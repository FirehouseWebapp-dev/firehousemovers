import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from authentication.models import UserProfile
from .models import CommunicationLog, LogType, LogResponse
from .forms import CommunicationLogForm, LogResponseForm
from authentication.mailer import send_communication_log_email

logger = logging.getLogger(__name__)


def get_user_profile(user):
    """Helper to get user profile"""
    try:
        return user.userprofile
    except AttributeError:
        logger.warning(f"User {user.id} ({user.username}) has no profile")
        return None


def is_manager_or_admin(user_profile):
    """Check if user has manager/admin privileges"""
    return user_profile.is_manager or user_profile.is_senior_management or user_profile.is_admin


def get_optimized_logs_queryset():
    """Get base queryset with optimized select/prefetch for all related objects"""
    return CommunicationLog.objects.select_related(
        'created_by__user',
        'employee__user',
        'log_type'
    ).prefetch_related(
        Prefetch(
            'responses',
            queryset=LogResponse.objects.select_related('responder__user')
        )
    )


def get_shared_employee_logs_base(user_profile):
    """Get base queryset for logs received by employee (shared only)"""
    return get_optimized_logs_queryset().filter(
        employee=user_profile,
        visibility='shared'
    )


def get_created_logs_base(user_profile):
    """Get base queryset for logs created by manager"""
    return get_optimized_logs_queryset().filter(created_by=user_profile)


def calculate_log_stats(queryset, is_shared_filter=True):
    """Calculate statistics for a log queryset"""
    stats = {
        'total': queryset.count(),
    }
    
    if is_shared_filter:
        shared_queryset = queryset.filter(visibility='shared')
        stats['unacknowledged'] = shared_queryset.filter(is_acknowledged=False).count()
        stats['acknowledged'] = shared_queryset.filter(is_acknowledged=True).count()
    else:
        stats['unacknowledged'] = queryset.filter(is_acknowledged=False).count()
        stats['acknowledged'] = queryset.filter(is_acknowledged=True).count()
    
    return stats


def check_log_view_permission(log, user_profile):
    """Check if user can view a log"""
    return (
        log.created_by == user_profile or
        (log.employee == user_profile and log.visibility == 'shared') or
        user_profile.is_admin or
        user_profile.is_senior_management
    )


@login_required
def log_list(request):
    """List all communication logs based on user role"""
    user_profile = get_user_profile(request.user)
    
    if not user_profile:
        logger.error(f"User {request.user.id} attempted to access log_list without profile")
        messages.error(request, "User profile not found.")
        return redirect('authentication:profile')
    
    # Managers and Senior Management see logs they created AND logs they received
    if is_manager_or_admin(user_profile):
        view_type = request.GET.get('view', 'created')
        logger.debug(f"Manager {user_profile.user.username} viewing {view_type} logs")
        
        if view_type == 'received':
            # Show logs this manager has received from senior management
            base_logs = get_shared_employee_logs_base(user_profile)
            logs = base_logs
            
            stats = calculate_log_stats(base_logs, is_shared_filter=False)
            context = {
                'logs': logs,
                'is_manager': False,  # Use employee view template
                'view_type': 'received',
                'unread_count': stats['unacknowledged'],
                'acknowledged_count': stats['acknowledged'],
            }
            template = 'communication/employee_log_list.html'
        else:
            # Show logs this manager has created (default)
            logs = get_created_logs_base(user_profile)
            
            # Apply filters
            employee_filter = request.GET.get('employee')
            log_type_filter = request.GET.get('log_type')
            status_filter = request.GET.get('status')
            
            if employee_filter:
                logs = logs.filter(employee_id=employee_filter)
                logger.debug(f"Filtering by employee: {employee_filter}")
            if log_type_filter:
                logs = logs.filter(log_type_id=log_type_filter)
                logger.debug(f"Filtering by log_type: {log_type_filter}")
            if status_filter == 'acknowledged':
                logs = logs.filter(is_acknowledged=True)
            elif status_filter == 'pending':
                logs = logs.filter(is_acknowledged=False)
            
            # Get filter options
            team_members = user_profile.team_members.all()
            department_members = UserProfile.objects.none()
            if user_profile.department:
                department_members = user_profile.department.members.exclude(id=user_profile.id)
            employees = (team_members | department_members).distinct()
            
            context = {
                'logs': logs,
                'is_manager': True,
                'view_type': 'created',
                'employees': employees,
                'log_types': LogType.objects.filter(is_active=True),
            }
            template = 'communication/manager_log_list.html'
    
    # Regular Employees see logs about them (shared only)
    else:
        logger.debug(f"Employee {user_profile.user.username} viewing received logs")
        base_logs = get_shared_employee_logs_base(user_profile)
        logs = base_logs
        
        # Filter by acknowledged status
        status_filter = request.GET.get('status')
        if status_filter == 'acknowledged':
            logs = logs.filter(is_acknowledged=True)
        elif status_filter == 'unread':
            logs = logs.filter(is_acknowledged=False)
        
        # Calculate counts from base queryset (before filtering)
        stats = calculate_log_stats(base_logs, is_shared_filter=False)
        
        context = {
            'logs': logs,
            'is_manager': False,
            'unread_count': stats['unacknowledged'],
            'acknowledged_count': stats['acknowledged'],
        }
        template = 'communication/employee_log_list.html'
    
    # Pagination
    paginator = Paginator(logs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    
    logger.info(f"User {user_profile.user.username} accessed log_list, {logs.count()} logs returned")
    return render(request, template, context)


@login_required
def create_log(request):
    """Create a new communication log (managers and senior management)"""
    user_profile = get_user_profile(request.user)
    
    if not user_profile or not is_manager_or_admin(user_profile):
        logger.warning(f"User {request.user.username} denied permission to create communication log")
        messages.error(request, "You do not have permission to create communication logs.")
        return redirect('communication:log_list')
    
    if request.method == 'POST':
        form = CommunicationLogForm(request.POST, manager=user_profile)
        if form.is_valid():
            log = form.save(commit=False)
            log.created_by = user_profile
            log.save()
            
            logger.info(
                f"Communication log {log.id} created by {user_profile.user.username} "
                f"for {log.employee.user.username} - Type: {log.log_type}, "
                f"Visibility: {log.visibility}"
            )
            
            # Send email notification if shared
            if log.visibility == 'shared':
                try:
                    send_communication_log_email(
                        email=log.employee.user.email,
                        employee_name=log.employee.user.get_full_name(),
                        manager_name=user_profile.user.get_full_name(),
                        subject=log.subject,
                        content=log.content,
                        log_type=log.log_type.name if log.log_type else 'Communication',
                        log_id=log.id
                    )
                    logger.info(f"Email notification sent for log {log.id} to {log.employee.user.email}")
                except Exception as e:
                    logger.error(f"Email notification failed for log {log.id}: {str(e)}", exc_info=True)
                    messages.warning(request, f"Log created but email notification failed: {str(e)}")
            
            messages.success(request, "Communication log created successfully!")
            return redirect('communication:log_detail', pk=log.id)
        else:
            logger.warning(f"Invalid form submission by {user_profile.user.username}: {form.errors}")
    else:
        form = CommunicationLogForm(manager=user_profile)
    
    context = {
        'form': form,
        'log_types': LogType.objects.filter(is_active=True),
    }
    return render(request, 'communication/create_log.html', context)


@login_required
def log_detail(request, pk):
    """View details of a communication log"""
    user_profile = get_user_profile(request.user)
    log = get_object_or_404(
        get_optimized_logs_queryset(),
        pk=pk
    )
    
    # Check permissions
    can_view = check_log_view_permission(log, user_profile)
    
    if not can_view:
        logger.warning(
            f"User {user_profile.user.username} denied access to log {pk} "
            f"(creator: {log.created_by.user.username}, employee: {log.employee.user.username})"
        )
        messages.error(request, "You do not have permission to view this log.")
        return redirect('communication:log_list')
    
    logger.debug(f"User {user_profile.user.username} viewing log {pk}")
    
    # Check if user can respond (employee/manager who received the log)
    can_respond = log.employee == user_profile and log.visibility == 'shared'
    is_creator = log.created_by == user_profile
    
    # Handle response form
    response_form = None
    if can_respond:
        if request.method == 'POST':
            response_form = LogResponseForm(request.POST)
            if response_form.is_valid():
                response = response_form.save(commit=False)
                response.communication_log = log
                response.responder = user_profile
                response.save()
                
                logger.info(
                    f"Response added to log {pk} by {user_profile.user.username} "
                    f"(response id: {response.id})"
                )
                messages.success(request, "Response added successfully!")
                return redirect('communication:log_detail', pk=log.id)
            else:
                logger.warning(f"Invalid response form by {user_profile.user.username}: {response_form.errors}")
        else:
            response_form = LogResponseForm()
    
    context = {
        'log': log,
        'response_form': response_form,
        'responses': log.responses.all(),  # Already prefetched with select_related
        'can_respond': can_respond,
        'is_creator': is_creator,
    }
    return render(request, 'communication/log_detail.html', context)


@login_required
@require_http_methods(["POST"])
def acknowledge_log(request, pk):
    """Acknowledge a communication log"""
    user_profile = get_user_profile(request.user)
    log = get_object_or_404(CommunicationLog, pk=pk)
    
    # Only the employee can acknowledge their log
    if log.employee != user_profile:
        logger.warning(
            f"User {user_profile.user.username} denied permission to acknowledge log {pk} "
            f"(employee: {log.employee.user.username})"
        )
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    if log.visibility != 'shared':
        logger.warning(f"User {user_profile.user.username} attempted to acknowledge private log {pk}")
        return JsonResponse({'success': False, 'error': 'Cannot acknowledge private log'}, status=400)
    
    log.acknowledge()
    logger.info(f"Log {pk} acknowledged by {user_profile.user.username}")
    
    return JsonResponse({
        'success': True,
        'acknowledged_at': log.acknowledged_at.strftime('%B %d, %Y at %I:%M %p')
    })


@login_required
def dashboard(request):
    """Communication dashboard"""
    user_profile = get_user_profile(request.user)
    
    if is_manager_or_admin(user_profile):
        # Manager/Senior dashboard with view filter
        # Default to 'employee_logs' for pure senior management, 'my_logs' for managers
        default_view = 'employee_logs' if (user_profile.is_senior_management and not user_profile.is_manager) else 'my_logs'
        view_type = request.GET.get('view', default_view)
        
        logger.debug(f"Manager {user_profile.user.username} viewing {view_type} dashboard")
        
        if view_type == 'employee_logs':
            # Stats for logs created by manager (for employees)
            base_queryset = get_created_logs_base(user_profile)
            stats = calculate_log_stats(base_queryset, is_shared_filter=True)
            recent_logs = base_queryset[:5]
            
            # Stats by log type
            log_type_stats = base_queryset.values('log_type__name').annotate(
                count=Count('id')
            ).order_by('-count')
        else:
            # Default: Stats for logs received by manager (my logs)
            base_queryset = get_shared_employee_logs_base(user_profile)
            stats = calculate_log_stats(base_queryset, is_shared_filter=False)
            recent_logs = base_queryset[:5]
            
            # Stats by log type
            log_type_stats = base_queryset.values('log_type__name').annotate(
                count=Count('id')
            ).order_by('-count')
        
        context = {
            'is_manager': True,
            'view_type': view_type,
            'total_logs': stats['total'],
            'unacknowledged': stats['unacknowledged'],
            'acknowledged': stats['acknowledged'],
            'recent_logs': recent_logs,
            'log_type_stats': log_type_stats,
        }
    else:
        # Employee dashboard
        logger.debug(f"Employee {user_profile.user.username} viewing dashboard")
        base_queryset = get_shared_employee_logs_base(user_profile)
        stats = calculate_log_stats(base_queryset, is_shared_filter=False)
        recent_logs = base_queryset[:5]
        
        context = {
            'is_manager': False,
            'total_logs': stats['total'],
            'unread_logs': stats['unacknowledged'],
            'acknowledged_logs': stats['acknowledged'],
            'recent_logs': recent_logs,
        }
    
    logger.info(f"User {user_profile.user.username} accessed dashboard")
    return render(request, 'communication/dashboard.html', context)
