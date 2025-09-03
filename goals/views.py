from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import UserProfile
from .models import Goal
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
import json # Import json
import os
import logging
from django.contrib.auth.decorators import login_required

# Configure logger for goals app
logger = logging.getLogger(__name__)


from .forms import GoalForm, GoalFormSetForm
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.forms import modelformset_factory
from django.db import transaction
from django.views.decorators.http import require_POST
from .utils.permissions import (
    role_checker, get_user_profile_safe, require_management, 
    require_manager_or_above, ajax_require_management
)
from .utils.helpers import (
    get_display_name, get_user_profile_display_name, get_goal_counts_summary, 
    can_add_more_goals, get_goal_status_indicator, get_empty_state_message
)
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
# Define the formset for Goal model
GoalFormSet = modelformset_factory(Goal, form=GoalFormSetForm, extra=1, can_delete=True)


@login_required
def goals_management(request):
    user_profile = get_user_profile_safe(request.user)
    if not user_profile:
        raise PermissionDenied("User profile not found for current user.")
    
    checker = role_checker(request.user)

    # Base queryset based on user role
    if checker.is_admin_or_senior():
        scope = request.GET.get("scope", "all")
        if scope == "team" and checker.is_senior_management():
            # My Team: show users assigned to this senior manager's team, excluding admins and other senior managers
            employees = UserProfile.objects.select_related('user', 'department', 'manager__user').filter(
                manager=user_profile
            ).exclude(
                role="admin"
            ).exclude(
                is_senior_management=True
            )
        else:
            # All Employees: show everyone except other senior management and users with role 'admin'
            employees = UserProfile.objects.select_related('user', 'department', 'manager__user').exclude(
                is_senior_management=True
            ).exclude(
                role="admin"
            )

    elif checker.is_manager():
        # Managers only see their direct reports - STRICTLY ENFORCED
        employees = UserProfile.objects.select_related('user', 'department', 'manager__user').filter(
            manager=user_profile  # Only users who have this manager assigned
        )

    else:
        # Regular employees can only see themselves
        employees = UserProfile.objects.select_related('user', 'department', 'manager__user').filter(id=user_profile.id)

    # Apply role filter
    role_filter = request.GET.get("role", "all")
    if role_filter != "all" and checker.is_management():
        employees = employees.filter(role=role_filter)

    # Optimize database queries and annotate goal counts
    # Only count active (non-completed) goals for the limit and has_goals check
    employees = employees.select_related('user', 'department', 'manager__user').annotate(
        goal_count=Count('goals', filter=Q(goals__is_completed=False))
        # total_goal_count=Count('goals')  # Removed - not used anywhere
    )
    
    # Add computed attributes using helper functions
    for e in employees:
        e.has_goals = e.goal_count > 0  # Based on active goals only
        e.display_name = get_user_profile_display_name(e)
        e.goal_count_summary = get_goal_counts_summary(e.goal_count)
        e.can_add_more_goals = can_add_more_goals(e.goal_count)
        e.goal_status_indicator = get_goal_status_indicator(e.goal_count)

    # Handle goals for view-only users
    filter_type = request.GET.get("filter", "all")
    goal_type_filter = request.GET.get("goal_type", "all")
    scope = request.GET.get("scope", "all") if checker.is_senior_management() else None
    if checker.is_manager_or_above():
        goals = Goal.objects.select_related('assigned_to__user', 'assigned_to__manager', 'created_by__user').all()
    else:
        goals = Goal.objects.select_related('assigned_to__user', 'assigned_to__manager', 'created_by__user').filter(assigned_to=user_profile)

    if filter_type == "completed":
        goals = goals.filter(is_completed=True)
    elif filter_type == "incomplete":
        goals = goals.filter(is_completed=False)
    
    # Apply goal type filter
    if goal_type_filter and goal_type_filter != "all":
        goals = goals.filter(goal_type=goal_type_filter)

    context = {
        'employees': employees,
        'can_add_goals': checker.can_manage_goals(),
        'has_team_members': employees.exists() if user_profile.is_manager else True,
        'goals': goals,  
        'filter_type': filter_type,
        'goal_type_filter': goal_type_filter,
        'role_filter': role_filter,
        'scope': scope,
        'EMPLOYEE_CHOICES': UserProfile.EMPLOYEE_CHOICES,
        # Clean context flags
        'is_manager': checker.is_manager(),
        'is_senior_manager': checker.is_senior_management(),
        'is_admin': checker.is_admin(),
        'is_management': checker.is_management(),
        'current_user_display_name': get_user_profile_display_name(user_profile),
        'empty_state_message': get_empty_state_message(checker, employees.exists() if user_profile.is_manager else True),
    }

    return render(request, 'goals/goal_management.html', context)

@login_required
@require_POST
def toggle_goal_completion(request, goal_id):
    goal = get_object_or_404(Goal.objects.select_related('assigned_to__user', 'assigned_to__manager', 'created_by__user'), id=goal_id)
    user_profile = get_user_profile_safe(request.user)
    if not user_profile:
        return JsonResponse({'success': False, 'error': 'User profile not found.'}, status=403)

    # Permission check using new utility
    checker = role_checker(request.user)
    if not checker.can_toggle_goal_completion(goal):
        return JsonResponse({'success': False, 'error': 'You don\'t have permission to modify this goal.'}, status=403)

    try:
        # Parse the JSON body from the request
        data = json.loads(request.body)
        is_completed = data.get('is_completed')

        if is_completed is None:
            return JsonResponse({'success': False, 'error': 'Invalid request data: is_completed is missing.'}, status=400)

        goal.is_completed = is_completed
        goal.save()
        return JsonResponse({'success': True, 'is_completed': goal.is_completed})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_management
def add_goals(request, employee_id):
    """Add goals for a specific employee"""
    user_profile = get_user_profile_safe(request.user)
    if not user_profile:
        raise PermissionDenied("User profile not found for current user.")
    employee = get_object_or_404(UserProfile.objects.select_related('user', 'manager__user'), id=employee_id)

    # Permission check using new utility
    checker = role_checker(request.user)
    if not checker.can_add_goals_for(employee):
        if employee.role == "admin" or employee.is_senior_management:
            raise PermissionDenied("Cannot add goals for admins or senior management.")
        else:
            raise PermissionDenied(f"You can only add goals for your direct team members. {employee.user.get_full_name()} is not your direct report.")

    # Check if employee already has 10 active goals
    existing_goals_count = Goal.objects.filter(assigned_to=employee, is_completed=False).count()
    if existing_goals_count >= 10:
        messages.error(request, f"{employee} already has the maximum of 10 active goals.")
        return redirect('goals:goal_management')

    remaining_goals = 10 - existing_goals_count

    if request.method == 'POST':
        formset = GoalFormSet(request.POST, queryset=Goal.objects.none())
        if formset.is_valid():
            with transaction.atomic():
                created_goals = []
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        goal = form.save(commit=False)
                        goal.assigned_to = employee
                        goal.created_by = user_profile
                        goal.save()
                        created_goals.append(goal)
                # Send email notification
                if created_goals:
                    try:
                        default_email = os.getenv("DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)
                        recipient_email = getattr(employee.user, "email", None) or default_email
                        send_mail(
                            subject="New Goal(s) Created. Check out.",
                            message=f"{len(created_goals)} new goal(s) have been created for {employee.user.get_full_name()}.",
                            from_email=default_email,
                            recipient_list=[recipient_email],
                            fail_silently=True,  # This prevents email errors from blocking form submission
                        )
                        logger.info(f"Email notification sent successfully to {recipient_email}")
                    except Exception as e:
                        # Log the error but don't let it prevent goal creation
                        logger.error(f"Email sending failed: {e}")
                        pass
                messages.success(request, f"Goals added successfully for {employee}.")
                return redirect('goals:goal_management')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        formset = GoalFormSet(queryset=Goal.objects.none())

    context = {
        'employee': employee,
        'existing_goals_count': existing_goals_count,
        'remaining_goals': remaining_goals,
        'formset': formset,
        # Clean context flags  
        'employee_display_name': get_user_profile_display_name(employee),
        'current_user_display_name': get_user_profile_display_name(user_profile),
        'is_manager': checker.is_manager(),
        'is_senior_manager': checker.is_senior_management(),
    }

    return render(request, 'goals/add_goals.html', context)


@login_required
def view_goals(request, employee_id):
    """View goals for a specific employee"""
    user_profile = get_user_profile_safe(request.user)
    if not user_profile:
        raise PermissionDenied("User profile not found for current user.")
    employee = get_object_or_404(UserProfile.objects.select_related('user', 'manager__user'), id=employee_id)

    # Permission check: users can view their own goals, managers/senior management can view anyone's
    checker = role_checker(request.user)
    if not checker.is_manager_or_above() and user_profile.id != employee.id:
        raise PermissionDenied("You can only view your own goals.")

    # Full set for charts (unfiltered)
    all_goals_for_employee = Goal.objects.select_related('assigned_to__user', 'assigned_to__manager', 'created_by__user').filter(assigned_to=employee)
    # List view (filterable)
    goals = all_goals_for_employee

    # Apply goal type filter
    selected_goal_type = request.GET.get('goal_type')
    selected_completion_status = request.GET.get('completion_status')

    if selected_goal_type and selected_goal_type != 'all':
        goals = goals.filter(goal_type=selected_goal_type)

    if selected_completion_status and selected_completion_status != 'all':
        if selected_completion_status == 'completed':
            goals = goals.filter(is_completed=True)
        elif selected_completion_status == 'pending':
            goals = goals.filter(is_completed=False)

    goals = goals.order_by('is_completed', '-created_at') # Order by completion status then creation date

    # Calculate all goal stats using aggregate (single query)
    goal_stats = all_goals_for_employee.aggregate(
        total_goals=Count('id'),
        completed_goals=Count('id', filter=Q(is_completed=True)),
        pending_goals=Count('id', filter=Q(is_completed=False)),
        short_term_goals=Count('id', filter=Q(goal_type='short_term')),
        long_term_goals=Count('id', filter=Q(goal_type='long_term'))
    )
    total_goals_for_employee = goal_stats['total_goals']
    completed_goals_for_employee = goal_stats['completed_goals']
    goal_completion_percentage = 0
    if total_goals_for_employee > 0:
        goal_completion_percentage = round((completed_goals_for_employee / total_goals_for_employee) * 100)

    # Determine if progress bar should be shown instead of charts/Calendly
    show_progress_bar = not checker.is_management()

    # Create a mock goal for permission checking (we need the assigned_to field)
    mock_goal = type('MockGoal', (), {'assigned_to': employee})()

    context = {
        'employee': employee,
        'goals': goals,
        'can_edit': checker.can_edit_goal(mock_goal),
        'can_delete_goal': checker.can_delete_goal(mock_goal),
        'selected_goal_type': selected_goal_type,
        'selected_completion_status': selected_completion_status,
        'show_progress_bar': show_progress_bar,
        # Clean context flags
        'employee_display_name': get_user_profile_display_name(employee),
        'is_manager': checker.is_manager(),
        'is_senior_manager': checker.is_senior_management(),
        'is_self': user_profile.id == employee.id,
        'current_user_display_name': get_user_profile_display_name(user_profile),
    }

    if show_progress_bar:
        context.update({
            'total_goals': total_goals_for_employee,
            'completed_goals': completed_goals_for_employee,
            'goal_completion_percentage': goal_completion_percentage,
        })
    else:
        # Use already calculated stats from the single aggregate query
        context.update({
            'chart_total': total_goals_for_employee,
            'chart_completion_completed': completed_goals_for_employee,
            'chart_completion_pending': goal_stats['pending_goals'],
            'chart_type_short': goal_stats['short_term_goals'],
            'chart_type_long': goal_stats['long_term_goals'],
        })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        fragment = request.GET.get('fragment')
        if fragment == 'list':
            return render(request, 'goals/_goals_list.html', context)
        if fragment == 'counts':
            return JsonResponse({
                'total': context['chart_total'] if not show_progress_bar else context['total_goals'],
                'completed': context['chart_completion_completed'] if not show_progress_bar else context['completed_goals'],
                'pending': context['chart_completion_pending'] if not show_progress_bar else (context['total_goals'] - context['completed_goals']),
                'short_term': context['chart_type_short'] if not show_progress_bar else 0, # Assuming no short/long term breakdown for progress bar
                'long_term': context['chart_type_long'] if not show_progress_bar else 0, # Assuming no short/long term breakdown for progress bar
            })
    return render(request, 'goals/view_goals.html', context)


@login_required
def edit_goal(request, goal_id):
    """Edit a specific goal"""
    user_profile = get_user_profile_safe(request.user)
    if not user_profile:
        raise PermissionDenied("User profile not found for current user.")
    goal = get_object_or_404(Goal.objects.select_related('assigned_to__user', 'assigned_to__manager', 'created_by__user'), id=goal_id)

    if goal.is_completed: # New check for completed goals
        messages.error(request, "Completed goals cannot be edited.")
        return redirect('goals:view_goals', employee_id=goal.assigned_to.id)

    # Permission check using new utility
    checker = role_checker(request.user)
    if not checker.can_edit_goal(goal):
        raise PermissionDenied("You don't have permission to edit this goal.")

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Goal updated successfully.")
            return redirect('goals:view_goals', employee_id=goal.assigned_to.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = GoalForm(instance=goal)

    context = {
        'goal': goal,
        'form': form,
    }

    return render(request, 'goals/edit_goal.html', context)

@login_required
@require_manager_or_above
def my_goals(request):
    """View goals assigned to the current manager/admin/senior management"""
    user_profile = get_user_profile_safe(request.user)
    if not user_profile:
        raise PermissionDenied("User profile not found for current user.")

    # This view is for the logged-in manager/admin/senior management to view their own goals
    employee = user_profile  # The employee whose goals are being viewed is the current user

    # Full set for charts (unfiltered)
    all_goals_for_employee = Goal.objects.select_related('assigned_to__user', 'assigned_to__manager', 'created_by__user').filter(assigned_to=employee)
    # List view (filterable)
    goals = all_goals_for_employee

    # Apply goal type filter
    selected_goal_type = request.GET.get('goal_type')
    selected_completion_status = request.GET.get('completion_status')

    if selected_goal_type and selected_goal_type != 'all':
        goals = goals.filter(goal_type=selected_goal_type)

    if selected_completion_status and selected_completion_status != 'all':
        if selected_completion_status == 'completed':
            goals = goals.filter(is_completed=True)
        elif selected_completion_status == 'pending':
            goals = goals.filter(is_completed=False)

    goals = goals.order_by('is_completed', '-created_at') # Order by completion status then creation date

    # Managers should see the progress bar in this view
    checker = role_checker(request.user)
    show_progress_bar = checker.is_manager()

    # Get all goal stats in single aggregate query
    goal_stats = all_goals_for_employee.aggregate(
        total_goals=Count('id'),
        completed_goals=Count('id', filter=Q(is_completed=True)),
        pending_goals=Count('id', filter=Q(is_completed=False)),
        short_term_goals=Count('id', filter=Q(goal_type='short_term')),
        long_term_goals=Count('id', filter=Q(goal_type='long_term'))
    )
    total_goals = goal_stats['total_goals']
    completed_goals = goal_stats['completed_goals']
    goal_completion_percentage = 0
    if total_goals > 0:
        goal_completion_percentage = round((completed_goals / total_goals) * 100)

    context = {
        'employee': employee,
        'goals': goals,
        'can_edit': False,
        'can_delete_goal': False,
        'selected_goal_type': selected_goal_type,
        'selected_completion_status': selected_completion_status,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'goal_completion_percentage': goal_completion_percentage,
        'show_progress_bar': show_progress_bar,
        # Clean context flags
        'employee_display_name': get_user_profile_display_name(employee),
        'current_user_display_name': get_user_profile_display_name(employee),  # Same as employee since it's my_goals
        'is_manager': True,  # This view is only for managers
        'is_self': True,     # Always viewing own goals
    }

    # Provide chart values if charts are being shown in this view
    if not show_progress_bar:
        # Use already calculated stats from the single aggregate query
        context.update({
            'chart_total': total_goals,
            'chart_completion_completed': completed_goals,
            'chart_completion_pending': goal_stats['pending_goals'],
            'chart_type_short': goal_stats['short_term_goals'],
            'chart_type_long': goal_stats['long_term_goals'],
        })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        fragment = request.GET.get('fragment')
        if fragment == 'list':
            return render(request, 'goals/_goals_list.html', context)
        if fragment == 'counts':
            return JsonResponse({
                'total': context['chart_total'],
                'completed': context['chart_completion_completed'],
                'pending': context['chart_completion_pending'],
                'short_term': context['chart_type_short'],
                'long_term': context['chart_type_long'],
            })
    return render(request, 'goals/view_goals.html', context)

@login_required
def remove_goal(request, goal_id):
    """Remove a specific goal"""
    goal = get_object_or_404(Goal.objects.select_related('assigned_to__user', 'assigned_to__manager', 'created_by__user'), id=goal_id)
    user_profile = get_user_profile_safe(request.user)
    if not user_profile:
        raise PermissionDenied("User profile not found for current user.")

    if goal.is_completed: # New check for completed goals
        messages.error(request, "Completed goals cannot be deleted.")
        return redirect('goals:view_goals', employee_id=goal.assigned_to.id)

    # Permission check using new utility
    checker = role_checker(request.user)
    if not checker.can_delete_goal(goal):
        raise PermissionDenied("You don't have permission to remove this goal.")

    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Goal removed successfully.")
        return redirect('goals:view_goals', employee_id=goal.assigned_to.id)

    return redirect('goals:view_goals', employee_id=goal.assigned_to.id)  # Fallback for GET request

@login_required
@require_POST
def send_schedule_email(request):
    try:
        default_email = os.getenv("DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)
        recipient_email = getattr(request.user, "email", None) or default_email
        send_mail(
            subject="New Meeting Scheduled",
            message="A user clicked Schedule Meeting on the website.",
            from_email=default_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

