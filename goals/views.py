from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import UserProfile
from .models import Goal
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
import json # Import json
from django.contrib.auth.decorators import login_required
from .forms import GoalForm
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.forms import modelformset_factory
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
# Define the formset for Goal model
GoalFormSet = modelformset_factory(Goal, form=GoalForm, extra=1, can_delete=True)


@login_required
def goals_management(request):
    """Main goals management page - lists all employees with goals"""
    user_profile = request.user.userprofile

    if user_profile.is_senior_management:
        scope = request.GET.get("scope", "all")
        if scope == 'team':
            employees = UserProfile.objects.filter(manager=user_profile).order_by('user__first_name', 'user__last_name')
        else:
            employees = UserProfile.objects.filter(is_employee=True).order_by('user__first_name', 'user__last_name')
    elif user_profile.is_manager:
        employees = UserProfile.objects.filter(manager=user_profile).order_by('user__first_name', 'user__last_name')
    else:
        employees = UserProfile.objects.filter(id=user_profile.id)

    for employee in employees:
        employee.goal_count = Goal.objects.filter(assigned_to=employee).count()
        employee.has_goals = employee.goal_count > 0
    
    filter_type = request.GET.get("filter", "all")
    role_filter = request.GET.get("role")
    scope = request.GET.get("scope", "all") if user_profile.is_senior_management else None
    # For view-only users, restrict goals to their own. For managers/seniors, show all.
    if user_profile.is_senior_management or user_profile.is_manager:
        goals = Goal.objects.all()
    else:
        goals = Goal.objects.filter(assigned_to=user_profile)

    if filter_type == "completed":
        goals = goals.filter(is_completed=True)
    elif filter_type == "incomplete":
        goals = goals.filter(is_completed=False)

    # Apply role filter for managers/senior only
    if (user_profile.is_senior_management or user_profile.is_manager) and role_filter and role_filter != 'all':
        employees = employees.filter(role=role_filter)


    context = {
        'employees': employees,
        'can_add_goals': user_profile.is_senior_management or user_profile.is_manager,
        'has_team_members': employees.exists() if user_profile.is_manager else True,
        'goals': goals,  
        'filter_type': filter_type,
        'role_filter': role_filter,
        'scope': scope,
    }

    return render(request, 'goals/goal_management.html', context)

@login_required
@require_POST
def toggle_goal_completion(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    user_profile = request.user.userprofile

    # Permission check: Only assigned user, manager, or senior management can toggle completion
    if not (user_profile.is_senior_management or user_profile.is_manager or goal.assigned_to == user_profile):
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
def add_goals(request, employee_id):
    """Add goals for a specific employee"""
    user_profile = request.user.userprofile
    employee = get_object_or_404(UserProfile, id=employee_id)

    # Check permissions
    if user_profile.is_senior_management:
        pass  # Senior management can add goals for any employee
    elif user_profile.is_manager:
        if employee.manager != user_profile:
            raise PermissionDenied("You can only add goals for your direct team members.")
    else:
        raise PermissionDenied("You don't have permission to add goals.")

    # Check if employee already has 10 goals
    existing_goals_count = Goal.objects.filter(assigned_to=employee).count()
    if existing_goals_count >= 10:
        messages.error(request, f"{employee} already has the maximum of 10 goals.")
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
            if created_goals:
                    send_mail(
                        subject="New Goal(s) Created. Check out.",
                        message=f"{len(created_goals)} new goal(s) have been created for {employee.user.get_full_name()}.",
                        from_email="noreply@example.com",   # dummy sender
                        recipient_list=["test@example.com"], # dummy recipient
                        fail_silently=False,
                    )
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
    }

    return render(request, 'goals/add_goals.html', context)


@login_required
def view_goals(request, employee_id):
    """View goals for a specific employee"""
    user_profile = request.user.userprofile
    employee = get_object_or_404(UserProfile, id=employee_id)

    if not (user_profile.is_senior_management or user_profile.is_manager) and user_profile.id != employee.id:
        raise PermissionDenied("You can only view your own goals.")

    # Full set for charts (unfiltered)
    all_goals_for_employee = Goal.objects.filter(assigned_to=employee)
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

    context = {
        'employee': employee,
        'goals': goals,
        'can_edit': user_profile.is_senior_management or user_profile.is_manager,
        'selected_goal_type': selected_goal_type,
        'selected_completion_status': selected_completion_status,
        # Chart data
        # Chart data (based on all goals for employee, not filtered list)
        'chart_total': all_goals_for_employee.count(),
        'chart_completion_completed': all_goals_for_employee.filter(is_completed=True).count(),
        'chart_completion_pending': all_goals_for_employee.filter(is_completed=False).count(),
        'chart_type_short': all_goals_for_employee.filter(goal_type='short_term').count(),
        'chart_type_long': all_goals_for_employee.filter(goal_type='long_term').count(),
    }
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
def edit_goal(request, goal_id):
    """Edit a specific goal"""
    user_profile = request.user.userprofile
    goal = get_object_or_404(Goal, id=goal_id)

    if not (user_profile.is_senior_management or user_profile.is_manager):
        raise PermissionDenied("You don't have permission to edit goals.")

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
def remove_goal(request, goal_id):
    """Remove a specific goal"""
    goal = get_object_or_404(Goal, id=goal_id)
    user_profile = request.user.userprofile

    # Only senior management or the creator can delete
    if not (user_profile.is_senior_management or goal.created_by == user_profile):
        raise PermissionDenied("You don't have permission to remove this goal.")

    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Goal removed successfully.")
        return redirect('goals:goal_management')

    return redirect('goals:goal_management')  # Fallback

@require_POST
def send_schedule_email(request):
    if request.method == "POST":
        try:
            send_mail(
                subject="New Meeting Scheduled",
                message="A user clicked Schedule Meeting on the website.",
                from_email="noreply@example.com",
                recipient_list= ["test@example.com"],# change this
                fail_silently=False,
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "invalid request"})
