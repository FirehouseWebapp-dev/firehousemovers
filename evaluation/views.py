from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Max, Count, Q, Avg , Min
from .models import Question
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import json
import logging
from django.core.cache import cache, caches
from datetime import datetime
from django.db.models import Prefetch
from django.utils import timezone
from .models import Answer
from django.http import HttpResponse
from io import BytesIO, StringIO
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
logger = logging.getLogger(__name__)

from authentication.models import UserProfile, Department
from .models import EvalForm, Question, DynamicEvaluation, DynamicManagerEvaluation
from .forms_dynamic_admin import EvalFormForm, QuestionForm, QuestionChoiceForm
from .forms import PreviewEvalForm, DynamicEvaluationForm
from .constants import EvaluationStatus
from django.utils.timezone import now
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from firehousemovers.utils.permissions import role_checker, require_management, require_admin_or_senior, ajax_require_management
from .decorators import (
    require_department_management, require_department_management_for_form, 
    ajax_require_department_management, 
    require_manager_access, require_senior_management_access, require_evaluation_access
)
from .utils import (
    activate_evalform_safely, deactivate_evalform_safely, get_role_checker,
    check_department_permission, process_form_creation_with_conflicts, 
    process_form_edit_with_conflicts, calculate_eval_stats, determine_status
)
from .evaluation_handlers import (
    handle_evaluation_submission, handle_evaluation_view, 
    handle_my_evaluations, handle_pending_evaluations,
    EMPLOYEE_EVALUATION_CONFIG, MANAGER_EVALUATION_CONFIG
)

# Permission checking functions moved to decorators.py



@login_required
def evalform_list(request):
    """List evaluation forms with department-specific permissions."""
    checker = get_role_checker(request.user)
    
    # Get forms based on user permissions
    from .decorators import _can_manage
    if _can_manage(request.user):
        # Global admins can see all forms
        forms = EvalForm.objects.select_related("department").order_by("-created_at")
        dept = request.GET.get("department")
        if dept and dept != "all":
            forms = forms.filter(department_id=dept)
    else:
        # Department managers can only see their own department's forms
        if checker.is_manager() and checker.user_profile and checker.user_profile.managed_department:
            forms = EvalForm.objects.filter(
                department=checker.user_profile.managed_department
            ).select_related("department").order_by("-created_at")
        else:
            # No permission to view any forms
            forms = EvalForm.objects.none()
    
    return render(request, "evaluation/forms/list.html", {"forms": forms})

@login_required
@require_department_management_for_form
def evalform_create(request):
    """Create evaluation form with department-specific permissions."""
    checker = get_role_checker(request.user)
    
    if request.method == "POST":
        try:
            form = EvalFormForm(request.POST)
            if form.is_valid():
                # Use consolidated form creation logic
                success, form_obj, error_response = process_form_creation_with_conflicts(form, request)
                
                if success:
                    return redirect("evaluation:evalform_detail", pk=form_obj.id)
                else:
                    return error_response
        except Exception as e:
            logger.exception("Failed to create evaluation form")
            messages.error(request, "An error occurred while creating the evaluation form. Please try again.")
            form = EvalFormForm(request.POST)
    else:
        form = EvalFormForm()
        # Restrict department choices for non-global admins
        if checker.is_manager() and checker.user_profile and checker.user_profile.managed_department:
            form.fields['department'].queryset = Department.objects.filter(id=checker.user_profile.managed_department.id)
            form.fields['department'].initial = checker.user_profile.managed_department
    
    return render(request, "evaluation/forms/create.html", {"form": form})

@login_required
@require_department_management
def evalform_edit(request, pk):
    """Edit evaluation form with department-specific permissions."""
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    checker = get_role_checker(request.user)
    
    if request.method == "POST":
        try:
            form = EvalFormForm(request.POST, instance=obj)
            if form.is_valid():
                # Check department permissions for the new department
                department = form.cleaned_data["department"]
                has_permission, error_msg = check_department_permission(
                    request.user, department, "move this form to"
                )
                if not has_permission:
                    messages.error(request, error_msg)
                    return render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": obj})
                
                # Use consolidated form edit logic
                success, error_response = process_form_edit_with_conflicts(form, obj, request)
                
                if success:
                    return redirect("evaluation:evalform_detail", pk=obj.id)
                else:
                    return error_response
        except Exception as e:
            logger.exception("Failed to edit evaluation form")
            messages.error(request, "An error occurred while updating the evaluation form. Please try again.")
            form = EvalFormForm(request.POST, instance=obj)
    else:
        form = EvalFormForm(instance=obj)
        # Restrict department choices for non-global admins
        if checker.is_manager() and checker.user_profile and checker.user_profile.managed_department:
            form.fields['department'].queryset = Department.objects.filter(id=checker.user_profile.managed_department.id)
    
    return render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": obj})

@login_required
@require_department_management
def evalform_detail(request, pk):
    """View evaluation form details with department-specific permissions."""
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    qs = obj.questions.prefetch_related("choices").order_by('order')
    return render(request, "evaluation/forms/detail.html", {"form_obj": obj, "questions": qs})

@login_required
@require_department_management
def evalform_preview(request, pk):
    """Preview evaluation form with department-specific permissions."""
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    form = PreviewEvalForm(eval_form=obj)
    return render(request, "evaluation/forms/preview.html", {"form_obj": obj, "preview_form": form})

@login_required
@require_department_management
def evalform_activate(request, pk):
    """Activate/deactivate evaluation form with department-specific permissions."""
    if request.method != "POST":
        return redirect("evaluation:evalform_detail", pk=pk)
    
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    # Check if the form has any questions
    question_count = obj.questions.count()
    if question_count == 0:
        messages.error(request, f"Cannot activate '{obj.name}' - it has no questions. Please add at least one question before activating.")
        return redirect("evaluation:evalform_detail", pk=pk)
    
    if obj.is_active:
        # Deactivate the form
        success, _ = deactivate_evalform_safely(obj, request)
    else:
        # Activate the form
        success, _ = activate_evalform_safely(obj, request)
    
    # Redirect back to forms list to show updated status
    return redirect("evaluation:evalform_list")

@login_required
@require_department_management
def evalform_delete(request, pk):
    """Delete evaluation form with department-specific permissions."""
    if request.method != "POST":
        return redirect("evaluation:evalform_list")
    
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    # Prevent deletion of active forms
    if obj.is_active:
        messages.error(request, f"Cannot delete '{obj.name}' - it is currently active. Please deactivate the form first.")
        return redirect("evaluation:evalform_list")
    
    form_name = obj.name
    
    try:
        with transaction.atomic():
            # Delete all questions first (which will cascade to choices)
            obj.questions.all().delete()
            # Then delete the form
            obj.delete()
        
        messages.success(request, f"Form '{form_name}' has been deleted successfully.")
    except Exception as e:
        logger.exception(f"Failed to delete evaluation form '{form_name}'")
        messages.error(request, f"Cannot delete '{form_name}' - it has associated evaluations. Please delete the evaluations first.")
    
    return redirect("evaluation:evalform_list")

@login_required
@require_department_management
def question_add(request, form_id):
    """Add question to evaluation form with department-specific permissions."""
    ef = get_object_or_404(EvalForm, pk=form_id)

    if request.method == "POST":
        try:
            qf = QuestionForm(request.POST, evaluation=ef)
            if qf.is_valid():
                new_order = qf.cleaned_data.get("order", 0)
                q = qf.save(commit=False)
                q.form = ef

                with transaction.atomic():
                    q.save()  # Save once here

                    # Get all questions (id + order only for efficiency)
                    all_questions = list(
                        ef.questions.only("id", "order").order_by("order", "id")
                    )

                    # Remove the newly added question
                    all_questions = [question for question in all_questions if question.id != q.id]

                    # Clamp new_order to valid range [0, len(all_questions)]
                    max_order = len(all_questions)
                    clamped_order = max(0, min(new_order, max_order))

                    # Insert new question at its desired position
                    all_questions.insert(clamped_order, q)

                    # Reassign sequential order
                    for index, question in enumerate(all_questions):
                        question.order = index

                    # Bulk update (no N+1)
                    Question.objects.bulk_update(all_questions, ["order"])

                messages.success(request, "Question added successfully.")
                return redirect("evaluation:evalform_detail", pk=ef.id)
            # Invalid form → render again with errors
        except Exception as e:
            logger.exception("Failed to add question to evaluation form")
            messages.error(request, "An error occurred while adding the question. Please try again.")
            qf = QuestionForm(request.POST, evaluation=ef)
    else:
        qf = QuestionForm(evaluation=ef)

    return render(
        request,
        "evaluation/forms/question_add.html",
        {"form": qf, "form_obj": ef},
    )

@login_required
@require_department_management
def question_edit(request, question_id):
    """Edit question with department-specific permissions."""
    q = get_object_or_404(Question, pk=question_id)

    if request.method == "POST":
        qf = QuestionForm(request.POST, instance=q)
        if qf.is_valid():
            new_order = qf.cleaned_data.get("order", 0)

            # Save main edits first
            q = qf.save(commit=False)

            with transaction.atomic():
                # Get all questions ordered by current order
                all_questions = list(
                    q.form.questions.only("id", "order").order_by("order", "id")
                )

                # Remove the edited question
                all_questions = [question for question in all_questions if question.id != q.id]

                # Clamp new_order to valid range [0, len(all_questions)]
                max_order = len(all_questions)
                clamped_order = max(0, min(new_order, max_order))

                # Insert the edited one at its new position
                all_questions.insert(clamped_order, q)

                # Reorder sequentially
                for index, question in enumerate(all_questions):
                    question.order = index

                # Bulk update in one query
                Question.objects.bulk_update(all_questions, ["order"])

            messages.success(request, "Question updated successfully.")
            return redirect("evaluation:evalform_detail", pk=q.form_id)
        # Invalid form → fall through to render with errors
    else:
        qf = QuestionForm(instance=q)

    return render(
        request,
        "evaluation/forms/question_edit.html",
        {"form": qf, "question": q},
    )

@login_required
@require_department_management
def choice_add(request, question_id):
    """Add choice to question with department-specific permissions."""
    q = get_object_or_404(Question, pk=question_id)
    
    if request.method == "POST":
        try:
            cf = QuestionChoiceForm(request.POST)
            if cf.is_valid():
                cf.instance.question = q
                cf.save()
                messages.success(request, "Choice added.")
                return redirect("evaluation:evalform_detail", pk=q.form_id)
        except Exception as e:
            logger.exception("Failed to add choice to question")
            messages.error(request, "An error occurred while adding the choice. Please try again.")
            cf = QuestionChoiceForm(request.POST)
    else:
        cf = QuestionChoiceForm()
    return render(request, "evaluation/forms/choice_add.html", {"form": cf, "question": q})
@login_required
@require_http_methods(["POST"])
@ajax_require_department_management
def update_question_order(request, pk):
    """Update the order of questions via AJAX with department-specific permissions."""
    try:
        form_obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)

        data = json.loads(request.body)
        question_orders = data.get('question_orders', [])

        # Build a mapping of {id: order}
        order_map = {
            int(item["id"]): int(item["order"])
            for item in question_orders
            if item.get("id") and item.get("order") is not None
        }

        with transaction.atomic():
            # Fetch all questions in one go
            questions = list(
                Question.objects.filter(form=form_obj, id__in=order_map.keys())
            )

            # Update their order values
            for q in questions:
                q.order = order_map.get(q.id, q.order)

            # Bulk update in one query
            Question.objects.bulk_update(questions, ["order"])

        return JsonResponse({'success': True})

    except Exception as e:
        logger.exception("Failed to update question order via AJAX")
        return JsonResponse({'success': False, 'error': 'An error occurred while updating question order. Please try again.'})


@login_required
@require_department_management
def question_delete(request, question_id):
    """Delete a question with department-specific permissions."""
    question = get_object_or_404(Question, id=question_id)
    form_obj = question.form
    
    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect("evaluation:evalform_detail", pk=form_obj.id)
    
    # If not POST, redirect to form detail
    return redirect("evaluation:evalform_detail", pk=form_obj.id)


@login_required
@require_manager_access
def evaluation_dashboard(request):
    """
    Dashboard view: Alternative dashboard for managers showing dynamic evaluations.
    """
    checker = get_role_checker(request.user)
    
    today = now()  # Use timezone-aware datetime for precision
    today_date = today.date()  # Keep date for display purposes
    
    # Get manager's team dynamic evaluations with optimized stats calculation
    evaluations = (
        DynamicEvaluation.objects
        .filter(manager=checker.user_profile)
        .select_related("employee__user", "form", "department")
        .order_by("-week_start")
    )
    
    # Calculate all counts in a single optimized query using aggregation
    
    stats = calculate_eval_stats(evaluations, today_date, "week_end")
    # Rename keys to match original naming
    stats = {
        'pending_count': stats['pending'],
        'completed_count': stats['completed'],
        'overdue_count': stats['overdue']
    }
    
    pending_count = stats['pending_count']
    completed_count = stats['completed_count']
    overdue_count = stats['overdue_count']
    
    return render(request, "evaluation/dashboard.html", {
        "evaluations": evaluations,
        "today": today,
        "pending_count": pending_count,
        "completed_count": completed_count,
        "overdue_count": overdue_count,
    })


@login_required
@require_evaluation_access
def evaluate_employee(request, evaluation_id):
    """
    Manager view: display & handle single dynamic evaluation form.
    """
    result = handle_evaluation_submission(request, evaluation_id, EMPLOYEE_EVALUATION_CONFIG)
    
    # If result is a redirect (success), return it
    if hasattr(result, 'status_code'):
        return result
    
    # Otherwise, result is template context - render the template
    return render(request, "evaluation/evaluate_employee.html", result)


@login_required
@require_evaluation_access
def view_evaluation(request, evaluation_id):
    """
    View completed dynamic evaluation (read-only).
    """
    template_context = handle_evaluation_view(request, evaluation_id, EMPLOYEE_EVALUATION_CONFIG)
    
    # Rename 'evaluatee' to 'employee' for template compatibility
    template_context['employee'] = template_context['evaluatee']
    
    return render(request, "evaluation/view_evaluation.html", template_context)


@login_required
@require_manager_access
def pending_evaluations(request):
    """
    Manager view: show progress & list of pending dynamic evaluations
    for last week and this week.
    """
    return handle_pending_evaluations(request, EMPLOYEE_EVALUATION_CONFIG, "evaluation/pending_evaluations.html")


@login_required
def my_evaluations_v2(request):
    """
    Employee view: show all dynamic evaluations for this employee.
    """
    return handle_my_evaluations(request, EMPLOYEE_EVALUATION_CONFIG, "evaluation/my_evaluations_v2.html")


# Manager Evaluation Views
@login_required
@require_senior_management_access
def manager_evaluation_dashboard(request):
    """
    Card-based dashboard for senior managers showing manager evaluations grouped by type.
    """
    checker = get_role_checker(request.user)
    
    today = now()  # Use timezone-aware datetime for precision
    today_date = today.date()  # Keep date for display purposes
    
    # Get manager evaluations assigned to this senior manager with optimized query
    evaluations = (
        DynamicManagerEvaluation.objects
        .filter(senior_manager=checker.user_profile)
        .select_related("manager__user", "form", "department")
        .order_by("-period_start")
    )
    
    # Group evaluations by type and period
    evaluation_cards = []
    
    # Get unique combinations of form name and period
    unique_periods = evaluations.values('form__name', 'period_start', 'period_end').distinct()
    
    # Pre-compute all stats to avoid database hits in loop
    period_stats_map = {}
    for eval in evaluations:
        key = (eval.form.name, eval.period_start, eval.period_end)
        if key not in period_stats_map:
            period_stats_map[key] = []
        period_stats_map[key].append(eval)
    
    for period_info in unique_periods:
        form_name = period_info['form__name']
        period_start = period_info['period_start']
        period_end = period_info['period_end']
        
        # Use pre-computed stats to avoid database hits
        period_evaluations = period_stats_map.get((form_name, period_start, period_end), [])
        period_stats = calculate_eval_stats(period_evaluations, today_date, "period_end")
        # Rename keys to match original naming
        period_stats = {
            'total_count': period_stats['total'],
            'pending_count': period_stats['pending'],
            'completed_count': period_stats['completed'],
            'overdue_count': period_stats['overdue']
        }
        
        total_count = period_stats['total_count']
        pending_count = period_stats['pending_count']
        completed_count = period_stats['completed_count']
        overdue_count = period_stats['overdue_count']
        
        # Determine status
        if overdue_count > 0:
            status = "Overdue"
        elif pending_count > 0:
            status = "Open"
        else:
            status = "Completed"
        
        # Get the actual evaluations for this period (needed for template display)
        period_evaluations = evaluations.filter(
            form__name=form_name,
            period_start=period_start,
            period_end=period_end
        )
        
        # Create card data
        card = {
            'form_name': form_name,
            'period_start': period_start,
            'period_end': period_end,
            'status': status,
            'total_count': total_count,
            'pending_count': pending_count,
            'completed_count': completed_count,
            'overdue_count': overdue_count,
            'evaluations': period_evaluations,
        }
        
        evaluation_cards.append(card)
    
    # Sort cards by period start (most recent first)
    evaluation_cards.sort(key=lambda x: x['period_start'], reverse=True)
    
    # Calculate totals for overview
    total_evaluations = len(evaluation_cards)
    total_completed = sum(card['completed_count'] for card in evaluation_cards)
    total_pending = sum(card['pending_count'] for card in evaluation_cards)
    total_overdue = sum(card['overdue_count'] for card in evaluation_cards)
    
    return render(request, "evaluation/manager_evaluation_cards.html", {
        "evaluation_cards": evaluation_cards,
        "today": today,
        "total_evaluations": total_evaluations,
        "total_completed": total_completed,
        "total_pending": total_pending,
        "total_overdue": total_overdue,
    })


@login_required
@require_senior_management_access
def manager_evaluation_cards_detail(request):
    """
    Detail view for a specific evaluation card showing all evaluations for that period and form.
    """
    checker = get_role_checker(request.user)
    
    today = now()  # Use timezone-aware datetime for precision
    today_date = today.date()  # Keep date for display purposes
    
    # Get filter parameters
    form_name = request.GET.get('form')
    period_start = request.GET.get('period_start')
    period_end = request.GET.get('period_end')
    
    if not all([form_name, period_start, period_end]):
        return redirect("evaluation:manager_evaluation_dashboard")
    
    # Parse dates
    try:
        period_start_date = datetime.strptime(period_start, '%Y-%m-%d').date()
        period_end_date = datetime.strptime(period_end, '%Y-%m-%d').date()
    except ValueError:
        return redirect("evaluation:manager_evaluation_dashboard")
    
    # Get evaluations for this specific period and form with optimized stats calculation
    evaluations = (
        DynamicManagerEvaluation.objects
        .filter(
            senior_manager=checker.user_profile,
            form__name=form_name,
            period_start=period_start_date,
            period_end=period_end_date
        )
        .select_related("manager__user", "form", "department")
        .order_by("manager__user__first_name", "manager__user__last_name")
    )
    
    # Calculate all stats in a single optimized query using aggregation
    
    stats = calculate_eval_stats(evaluations, today_date, "period_end")
    # Rename keys to match original naming
    stats = {
        'total_count': stats['total'],
        'pending_count': stats['pending'],
        'completed_count': stats['completed'],
        'overdue_count': stats['overdue']
    }
    
    total_count = stats['total_count']
    pending_count = stats['pending_count']
    completed_count = stats['completed_count']
    overdue_count = stats['overdue_count']
    
    # Determine overall status
    if overdue_count > 0:
        overall_status = "Overdue"
    elif pending_count > 0:
        overall_status = "Open"
    else:
        overall_status = "Completed"
    
    return render(request, "evaluation/manager_evaluation_cards_detail.html", {
        "evaluations": evaluations,
        "form_name": form_name,
        "period_start": period_start_date,
        "period_end": period_end_date,
        "today": today,
        "total_count": total_count,
        "pending_count": pending_count,
        "completed_count": completed_count,
        "overdue_count": overdue_count,
        "overall_status": overall_status,
    })


@login_required
@require_evaluation_access
def evaluate_manager(request, evaluation_id):
    """
    Senior manager view: display & handle single manager evaluation form.
    """
    result = handle_evaluation_submission(request, evaluation_id, MANAGER_EVALUATION_CONFIG)
    
    # If result is a redirect (success), return it
    if hasattr(result, 'status_code'):
        return result
    
    # Otherwise, result is template context - rename 'evaluatee' to 'manager' for template compatibility
    result['manager'] = result['evaluatee']
    
    # Otherwise, result is template context - render the template
    return render(request, "evaluation/evaluate_manager.html", result)


@login_required
@require_evaluation_access
def view_manager_evaluation(request, evaluation_id):
    """
    View completed manager evaluation (read-only).
    """
    template_context = handle_evaluation_view(request, evaluation_id, MANAGER_EVALUATION_CONFIG)
    
    # Rename 'evaluatee' to 'manager' for template compatibility
    template_context['manager'] = template_context['evaluatee']
    
    return render(request, "evaluation/view_manager_evaluation.html", template_context)


@login_required
def my_manager_evaluations(request):
    """
    Manager view: show all evaluations for this manager.
    """
    return handle_my_evaluations(request, MANAGER_EVALUATION_CONFIG, "evaluation/my_manager_evaluations.html")


@login_required
@require_senior_management_access
def pending_manager_evaluations(request):
    """
    Senior manager view: show progress & list of pending manager evaluations.
    """
    return handle_pending_evaluations(request, MANAGER_EVALUATION_CONFIG, "evaluation/pending_manager_evaluations.html")


@login_required
@require_senior_management_access
def senior_manager_analytics_dashboard(request):
    """
    Senior manager analytics dashboard with comprehensive organizational insights.
    Cached for 30 minutes to improve performance for senior-only view.
    """
    checker = get_role_checker(request.user)
    today = now()  # Use timezone-aware datetime for precision
    today_date = today.date()  # Keep date for display purposes
    
    # Create cache key based on user and date
    cache_key = f"analytics_dashboard_{request.user.id}_{today_date}"
    
    # Try to get cached data first from analytics cache
    analytics_cache = caches['analytics']
    cached_data = analytics_cache.get(cache_key)
    if cached_data:
        logger.info(f"Analytics dashboard cache hit for user {request.user.id}")
        # Update the last viewed timestamp to current time
        current_time = timezone.now()
        cached_data['last_viewed_at'] = current_time.isoformat()
        # Update cache with new timestamp
        analytics_cache.set(cache_key, cached_data, timeout=1800)
        
        # Convert serialized dates back to proper objects for template rendering
        from datetime import datetime
        cached_data['today'] = datetime.fromisoformat(cached_data['today']).date()
        cached_data['data_computed_at'] = datetime.fromisoformat(cached_data['data_computed_at'])
        cached_data['last_viewed_at'] = current_time  # Use current time object for display
        
        return render(request, "evaluation/senior_manager_analytics_dashboard.html", cached_data)
    
    logger.info(f"Analytics dashboard cache miss for user {request.user.id}, computing data...")
    
    # Get all departments for senior managers with optimized prefetched evaluations
    
    # Prefetch all evaluations for department stats (need total counts)
    employee_prefetch = Prefetch(
        'dynamic_evaluations',
        queryset=DynamicEvaluation.objects.only('id', 'status', 'week_end', 'department_id', 'employee_id')
    )
    manager_prefetch = Prefetch(
        'dynamic_manager_evaluations', 
        queryset=DynamicManagerEvaluation.objects.only('id', 'status', 'period_end', 'department_id', 'manager_id')
    )
    
    departments = Department.objects.prefetch_related(
        employee_prefetch,
        manager_prefetch
    ).only('id', 'title').all()
    
    # Calculate overall organizational metrics - optimize for summary data
    all_employee_evaluations = DynamicEvaluation.objects.select_related(
        'employee__user', 'form', 'department'
    ).only(
        'id', 'status', 'week_end', 'submitted_at', 'employee_id', 'department_id', 
        'form_id', 'employee__user__first_name', 'employee__user__last_name',
        'department__title', 'form__name'
    ).all()
    
    all_manager_evaluations = DynamicManagerEvaluation.objects.select_related(
        'manager__user', 'form', 'department'
    ).only(
        'id', 'status', 'period_end', 'submitted_at', 'manager_id', 'department_id',
        'form_id', 'manager__user__first_name', 'manager__user__last_name',
        'department__title', 'form__name'
    ).all()
    
    # Overall completion rates
    employee_stats = calculate_eval_stats(all_employee_evaluations, today_date, "week_end")
    # Rename keys to match original naming
    employee_stats = {
        'total_employee_evals': employee_stats['total'],
        'completed_employee_evals': employee_stats['completed'],
        'pending_employee_evals': employee_stats['pending'],
        'overdue_employee_evals': employee_stats['overdue']
    }
    
    manager_stats = calculate_eval_stats(all_manager_evaluations, today_date, "period_end")
    # Rename keys to match original naming
    manager_stats = {
        'total_manager_evals': manager_stats['total'],
        'completed_manager_evals': manager_stats['completed'],
        'pending_manager_evals': manager_stats['pending'],
        'overdue_manager_evals': manager_stats['overdue']
    }
    
    # Department performance analytics
    department_analytics = []
    for dept in departments:
        # Use prefetched evaluations to avoid N+1 queries
        dept_employee_evals = dept.dynamic_evaluations.all()
        dept_manager_evals = dept.dynamic_manager_evaluations.all()
        
        dept_employee_stats = calculate_eval_stats(dept_employee_evals, today_date, "week_end")
        dept_manager_stats = calculate_eval_stats(dept_manager_evals, today_date, "period_end")
        
        # Calculate completion rates
        employee_completion_rate = (dept_employee_stats['completed'] / dept_employee_stats['total'] * 100) if dept_employee_stats['total'] > 0 else 0
        manager_completion_rate = (dept_manager_stats['completed'] / dept_manager_stats['total'] * 100) if dept_manager_stats['total'] > 0 else 0
        
        # Determine if department has no evaluations (not started)
        has_employee_evals = dept_employee_stats['total'] > 0
        has_manager_evals = dept_manager_stats['total'] > 0
        
        # Determine employee status based on pending/overdue logic
        employee_status = determine_status(dept_employee_stats['total'], dept_employee_stats['pending'], dept_employee_stats['overdue'])
            
        # Determine manager status based on pending/overdue logic
        manager_status = determine_status(dept_manager_stats['total'], dept_manager_stats['pending'], dept_manager_stats['overdue'])
        
        department_analytics.append({
            'department': dept,
            'employee_stats': dept_employee_stats,
            'manager_stats': dept_manager_stats,
            'employee_completion_rate': round(employee_completion_rate, 1),
            'manager_completion_rate': round(manager_completion_rate, 1),
            'has_employee_evals': has_employee_evals,
            'has_manager_evals': has_manager_evals,
            'employee_status': employee_status,
            'manager_status': manager_status,
        })
    
    # Sort departments by employee completion rate
    department_analytics.sort(key=lambda x: x['employee_completion_rate'], reverse=True)
    
    # Manager effectiveness analytics - optimize with prefetch
    # Prefetch all evaluations for manager stats (need total counts)
    mgr_evaluations_prefetch = Prefetch(
        'dynamic_mgr_evaluations',
        queryset=DynamicEvaluation.objects.only('id', 'status', 'week_end', 'employee_id', 'manager_id')
    )
    manager_reviews_prefetch = Prefetch(
        'dynamic_manager_reviews',
        queryset=DynamicManagerEvaluation.objects.only('id', 'status', 'period_end', 'manager_id', 'senior_manager_id')
    )
    team_members_prefetch = Prefetch(
        'team_members',
        queryset=UserProfile.objects.only('id', 'user__first_name', 'user__last_name', 'role')
    )
    
    managers = UserProfile.objects.filter(role='manager').select_related('user').prefetch_related(
        mgr_evaluations_prefetch,
        manager_reviews_prefetch,
        team_members_prefetch
    ).only('id', 'user__first_name', 'user__last_name', 'role')
    manager_effectiveness = []
    
    for manager in managers:
        # Use prefetched evaluations to avoid N+1 queries
        manager_team_evals = manager.dynamic_mgr_evaluations.all()
        manager_self_evals = manager.dynamic_manager_reviews.all()
        
        team_stats = calculate_eval_stats(manager_team_evals, today_date, "week_end")
        self_stats = calculate_eval_stats(manager_self_evals, today_date, "period_end")
        
        team_completion_rate = (team_stats['completed'] / team_stats['total'] * 100) if team_stats['total'] > 0 else 0
        self_completion_rate = (self_stats['completed'] / self_stats['total'] * 100) if self_stats['total'] > 0 else 0
        
        # Determine manager team status based on pending/overdue logic
        team_status = determine_status(team_stats['total'], team_stats['pending'], team_stats['overdue'])
        
        # Get the senior manager who manages this manager
        senior_manager = manager.manager if hasattr(manager, 'manager') and manager.manager else None
        
        manager_effectiveness.append({
            'manager': manager,
            'senior_manager': senior_manager,
            'team_stats': team_stats,
            'self_stats': self_stats,
            'team_completion_rate': round(team_completion_rate, 1),
            'self_completion_rate': round(self_completion_rate, 1),
            'team_status': team_status,
        })
    
    # Sort managers by team completion rate
    manager_effectiveness.sort(key=lambda x: x['team_completion_rate'], reverse=True)
    
    # Teams performance analytics (grouped by manager/team leader)
    # Pre-compute team member evaluations to avoid database hits
    team_member_evaluations = {}
    for eval in all_employee_evaluations:
        employee_id = eval.employee_id
        if employee_id not in team_member_evaluations:
            team_member_evaluations[employee_id] = []
        team_member_evaluations[employee_id].append(eval)
    
    teams_analytics = []
    for manager in managers:
        # Use prefetched team members to avoid N+1 queries
        team_members = list(manager.team_members.all())
        
        # Get evaluations for all team members using pre-computed data
        team_employee_evals = []
        for member in team_members:
            team_employee_evals.extend(team_member_evaluations.get(member.id, []))
        team_manager_evals = list(manager.dynamic_manager_reviews.all())
        
        team_employee_stats = calculate_eval_stats(team_employee_evals, today_date, "week_end")
        team_manager_stats = calculate_eval_stats(team_manager_evals, today_date, "period_end")
        
        # Calculate completion rates
        team_employee_completion_rate = (team_employee_stats['completed'] / team_employee_stats['total'] * 100) if team_employee_stats['total'] > 0 else 0
        team_manager_completion_rate = (team_manager_stats['completed'] / team_manager_stats['total'] * 100) if team_manager_stats['total'] > 0 else 0
        
        # Determine if team has no evaluations (not started)
        has_employee_evals = team_employee_stats['total'] > 0
        has_manager_evals = team_manager_stats['total'] > 0
        
        # Determine team status based on pending/overdue logic
        # Use the more critical status between employee and manager evaluations
        employee_status = determine_status(team_employee_stats['total'], team_employee_stats['pending'], team_employee_stats['overdue'])
        manager_status = determine_status(team_manager_stats['total'], team_manager_stats['pending'], team_manager_stats['overdue'])
        
        # If either is critical, team is critical; if either needs attention, team needs attention
        if employee_status == 'critical' or manager_status == 'critical':
            team_status = 'critical'
        elif employee_status == 'needs_attention' or manager_status == 'needs_attention':
            team_status = 'needs_attention'
        elif employee_status == 'awaiting' and manager_status == 'awaiting':
            team_status = 'awaiting'
        else:
            team_status = 'on_track'
        
        # Get team size (use len() to avoid DB hit on prefetched data)
        team_size = len(team_members)
        
        teams_analytics.append({
            'manager': manager,
            'team_members': team_members,
            'team_size': team_size,
            'employee_stats': team_employee_stats,
            'manager_stats': team_manager_stats,
            'employee_completion_rate': round(team_employee_completion_rate, 1),
            'manager_completion_rate': round(team_manager_completion_rate, 1),
            'has_employee_evals': has_employee_evals,
            'has_manager_evals': has_manager_evals,
            'team_status': team_status,
        })
    
    # Sort teams by employee completion rate
    teams_analytics.sort(key=lambda x: x['employee_completion_rate'], reverse=True)
    
    # Calculate overall completion rates
    total_employee_evals = employee_stats['total_employee_evals']
    total_manager_evals = manager_stats['total_manager_evals']
    
    overall_employee_completion_rate = (employee_stats['completed_employee_evals'] / total_employee_evals * 100) if total_employee_evals > 0 else 0
    overall_manager_completion_rate = (manager_stats['completed_manager_evals'] / total_manager_evals * 100) if total_manager_evals > 0 else 0
    
    # Recent activity (last 30 days) - use timezone-aware datetime for precision
    thirty_days_ago = today - timedelta(days=30)
    recent_employee_evals = all_employee_evaluations.filter(submitted_at__gte=thirty_days_ago)
    recent_manager_evals = all_manager_evaluations.filter(submitted_at__gte=thirty_days_ago)
    
    
    # Department comparison data
    department_comparison = []
    for dept in departments:
        # Use prefetched evaluations to avoid N+1 queries
        dept_employee_evals = dept.dynamic_evaluations.all()
        dept_manager_evals = dept.dynamic_manager_evaluations.all()
        
        dept_emp_completed = len([e for e in dept_employee_evals if e.status == EvaluationStatus.COMPLETED])
        dept_emp_total = len(dept_employee_evals)
        dept_emp_completion_rate = (dept_emp_completed / dept_emp_total * 100) if dept_emp_total > 0 else 0
        
        dept_mgr_completed = len([e for e in dept_manager_evals if e.status == EvaluationStatus.COMPLETED])
        dept_mgr_total = len(dept_manager_evals)
        dept_mgr_completion_rate = (dept_mgr_completed / dept_mgr_total * 100) if dept_mgr_total > 0 else 0
        
        # Calculate department average rating
        dept_avg_rating = 0
        if dept_emp_completed > 0:

            dept_ratings = Answer.objects.filter(
                instance__in=dept_employee_evals.filter(status=EvaluationStatus.COMPLETED),
                question__qtype='rating'
            ).aggregate(avg_rating=Avg('int_value'))['avg_rating'] or 0
            dept_avg_rating = round(dept_ratings, 1)
        
        department_comparison.append({
            'department_name': dept.title,
            'employee_completion_rate': round(dept_emp_completion_rate, 1),
            'manager_completion_rate': round(dept_mgr_completion_rate, 1),
            'average_rating': dept_avg_rating,
            'total_evaluations': dept_emp_total + dept_mgr_total,
            'completed_evaluations': dept_emp_completed + dept_mgr_completed
        })
    
    # Prepare context data with current time
    current_time = timezone.now()
    
    # Serialize departments to avoid caching ORM objects
    departments_data = [
        {
            'id': dept.id,
            'title': dept.title,
        }
        for dept in departments
    ]
    
    # Serialize recent evaluations to avoid caching ORM objects
    recent_employee_evals_data = [
        {
            'id': eval.id,
            'employee_name': f"{eval.employee.user.first_name} {eval.employee.user.last_name}",
            'department_name': eval.department.title,
            'form_name': eval.form.name,
            'status': eval.status,
            'week_end': eval.week_end.isoformat() if eval.week_end else None,
            'submitted_at': eval.submitted_at.isoformat() if eval.submitted_at else None,
        }
        for eval in recent_employee_evals
    ]
    
    recent_manager_evals_data = [
        {
            'id': eval.id,
            'manager_name': f"{eval.manager.user.first_name} {eval.manager.user.last_name}",
            'department_name': eval.department.title,
            'form_name': eval.form.name,
            'status': eval.status,
            'period_end': eval.period_end.isoformat() if eval.period_end else None,
            'submitted_at': eval.submitted_at.isoformat() if eval.submitted_at else None,
        }
        for eval in recent_manager_evals
    ]
    
    context_data = {
        'departments': departments_data,
        'department_analytics': department_analytics,
        'teams_analytics': teams_analytics,
        'manager_effectiveness': manager_effectiveness,
        'employee_stats': employee_stats,
        'manager_stats': manager_stats,
        'overall_employee_completion_rate': round(overall_employee_completion_rate, 1),
        'overall_manager_completion_rate': round(overall_manager_completion_rate, 1),
        'recent_employee_evals': recent_employee_evals_data,
        'recent_manager_evals': recent_manager_evals_data,
        'recent_employee_evals_count': len(recent_employee_evals),  # Pre-computed count
        'recent_manager_evals_count': len(recent_manager_evals),    # Pre-computed count
        'today': today_date.isoformat(),  # Serialize date
        'department_comparison': department_comparison,
        'data_computed_at': current_time.isoformat(),  # Serialize datetime
        'last_viewed_at': current_time.isoformat(),    # Serialize datetime
    }
    
    # Cache the computed data for 30 minutes (1800 seconds)
    analytics_cache.set(cache_key, context_data, timeout=1800)
    logger.info(f"Analytics dashboard data cached for user {request.user.id}")
    
    # Convert serialized data back to proper objects for template rendering
    context_data['today'] = today_date  # Use original date object
    context_data['data_computed_at'] = current_time  # Use original datetime object
    context_data['last_viewed_at'] = current_time  # Use original datetime object
    
    return render(request, "evaluation/senior_manager_analytics_dashboard.html", context_data)


@login_required
@require_senior_management_access
def analytics_department_detail(request, department_id):
    """
    Detailed analytics view for a specific department.
    """
    department = get_object_or_404(Department, id=department_id)
    today = now()  # Use timezone-aware datetime for precision
    today_date = today.date()  # Keep date for display purposes
    
    # Get department-specific evaluations - optimize for detail page
    dept_employee_evals = DynamicEvaluation.objects.filter(department=department).select_related(
        'employee__user', 'form', 'manager__user'
    ).only(
        'id', 'status', 'week_end', 'submitted_at', 'employee_id', 'manager_id',
        'employee__user__first_name', 'employee__user__last_name',
        'manager__user__first_name', 'manager__user__last_name',
        'form__name'
    )
    
    dept_manager_evals = DynamicManagerEvaluation.objects.filter(department=department).select_related(
        'manager__user', 'form', 'senior_manager__user'
    ).only(
        'id', 'status', 'period_end', 'submitted_at', 'manager_id', 'senior_manager_id',
        'manager__user__first_name', 'manager__user__last_name',
        'senior_manager__user__first_name', 'senior_manager__user__last_name',
        'form__name'
    )
    
    # Department statistics
    dept_stats = calculate_eval_stats(dept_employee_evals, today_date, "week_end")
    
    # Calculate completion rate
    completion_rate = (dept_stats['completed'] / dept_stats['total'] * 100) if dept_stats['total'] > 0 else 0
    
    # Employee performance in this department - pre-compute all stats to avoid N+1 queries
    employees = UserProfile.objects.filter(
        dynamic_emp_evaluations__department=department
    ).distinct().select_related('user')
    
    # Group evaluations by employee to avoid N+1 queries
    employee_evaluations = {}
    for eval in dept_employee_evals:
        employee_id = eval.employee_id
        if employee_id not in employee_evaluations:
            employee_evaluations[employee_id] = []
        employee_evaluations[employee_id].append(eval)
    
    employee_performance = []
    for employee in employees:
        emp_evals = employee_evaluations.get(employee.id, [])
        emp_stats = calculate_eval_stats(emp_evals, today_date, "week_end")
        
        completion_rate = (emp_stats['completed'] / emp_stats['total'] * 100) if emp_stats['total'] > 0 else 0
        
        # Determine employee status based on pending/overdue logic
        emp_status = determine_status(emp_stats['total'], emp_stats['pending'], emp_stats['overdue'])
        
        employee_performance.append({
            'employee': employee,
            'stats': emp_stats,
            'completion_rate': round(completion_rate, 1),
            'has_evaluations': emp_stats['total'] > 0,
            'emp_status': emp_status,
        })
    
    # Sort by completion rate
    employee_performance.sort(key=lambda x: x['completion_rate'], reverse=True)
    
    # Recent evaluations in this department - use timezone-aware datetime for precision
    thirty_days_ago = today - timedelta(days=30)
    recent_evals = dept_employee_evals.filter(submitted_at__gte=thirty_days_ago).order_by('-submitted_at')[:10]
    
    return render(request, "evaluation/analytics_department_detail.html", {
        'department': department,
        'dept_stats': dept_stats,
        'completion_rate': round(completion_rate, 1),
        'employee_performance': employee_performance,
        'recent_evals': list(recent_evals),  # Convert to list to avoid accidental queries
        'recent_evals_count': len(recent_evals),  # Pre-computed count
        'today': today_date,
    })


@login_required
@require_senior_management_access
def analytics_team_detail(request, team_leader_id):
    """
    Detailed analytics view for a specific team (managed by a team leader).
    """
    team_leader = get_object_or_404(UserProfile, id=team_leader_id, role='manager')
    today = now()  # Use timezone-aware datetime for precision
    today_date = today.date()  # Keep date for display purposes
    
    # Get team members - optimize for detail page
    team_members = UserProfile.objects.filter(manager=team_leader).select_related('user').only(
        'id', 'user__first_name', 'user__last_name', 'role'
    )
    
    # Get team-specific evaluations - optimize for detail page
    team_employee_evals = DynamicEvaluation.objects.filter(employee__in=team_members).select_related(
        'employee__user', 'form', 'manager__user'
    ).only(
        'id', 'status', 'week_end', 'submitted_at', 'employee_id', 'manager_id',
        'employee__user__first_name', 'employee__user__last_name',
        'manager__user__first_name', 'manager__user__last_name',
        'form__name'
    )
    
    team_manager_evals = DynamicManagerEvaluation.objects.filter(manager=team_leader).select_related(
        'manager__user', 'form', 'senior_manager__user'
    ).only(
        'id', 'status', 'period_end', 'submitted_at', 'manager_id', 'senior_manager_id',
        'manager__user__first_name', 'manager__user__last_name',
        'senior_manager__user__first_name', 'senior_manager__user__last_name',
        'form__name'
    )
    
    # Team statistics
    team_stats = calculate_eval_stats(team_employee_evals, today_date, "week_end")
    
    # Manager self-evaluation statistics
    manager_stats = calculate_eval_stats(team_manager_evals, today_date, "period_end")
    
    # Calculate completion rates
    team_completion_rate = (team_stats['completed'] / team_stats['total'] * 100) if team_stats['total'] > 0 else 0
    manager_completion_rate = (manager_stats['completed'] / manager_stats['total'] * 100) if manager_stats['total'] > 0 else 0
    
    # Team member performance - pre-compute all stats to avoid N+1 queries
    # Group evaluations by team member to avoid N+1 queries
    member_evaluations = {}
    for eval in team_employee_evals:
        member_id = eval.employee_id
        if member_id not in member_evaluations:
            member_evaluations[member_id] = []
        member_evaluations[member_id].append(eval)
    
    member_performance = []
    for member in team_members:
        member_evals = member_evaluations.get(member.id, [])
        member_stats = calculate_eval_stats(member_evals, today_date, "week_end")
        
        completion_rate = (member_stats['completed'] / member_stats['total'] * 100) if member_stats['total'] > 0 else 0
        
        # Determine member status
        member_status = determine_status(member_stats['total'], member_stats['pending'], member_stats['overdue'])
        
        member_performance.append({
            'member': member,
            'stats': member_stats,
            'completion_rate': round(completion_rate, 1),
            'has_evaluations': member_stats['total'] > 0,
            'member_status': member_status,
        })
    
    # Sort by completion rate
    member_performance.sort(key=lambda x: x['completion_rate'], reverse=True)
    
    # Recent evaluations in this team - use timezone-aware datetime for precision
    thirty_days_ago = today - timedelta(days=30)
    recent_evals = team_employee_evals.filter(submitted_at__gte=thirty_days_ago).order_by('-submitted_at')[:10]
    
    return render(request, "evaluation/analytics_team_detail.html", {
        'team_leader': team_leader,
        'team_members': list(team_members),  # Convert to list to avoid accidental queries
        'team_stats': team_stats,
        'manager_stats': manager_stats,
        'team_completion_rate': round(team_completion_rate, 1),
        'manager_completion_rate': round(manager_completion_rate, 1),
        'member_performance': member_performance,
        'recent_evals': list(recent_evals),  # Convert to list to avoid accidental queries
        'recent_evals_count': len(recent_evals),  # Pre-computed count
        'today': today_date,
    })


@login_required
@require_senior_management_access
def analytics_export(request):
    """Export analytics data as PDF or Excel."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    format_type = request.POST.get('format', 'pdf').lower()
    
    try:
        if format_type == 'pdf':
            return export_analytics_pdf(request)
        elif format_type == 'excel':
            return export_analytics_excel(request)
        else:
            return JsonResponse({'error': 'Invalid format'}, status=400)
    except Exception as e:
        logger.exception("Analytics export failed")
        return JsonResponse({'error': 'Export failed'}, status=500)


def export_analytics_pdf(request):
    """Generate PDF report of analytics data."""
    try:
        # Try to import reportlab for PDF generation
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add content to PDF
        p.drawString(100, 750, "Analytics Report")
        p.drawString(100, 730, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        p.drawString(100, 710, "Evaluation Analytics Dashboard Export")
        
        # Add basic analytics data (you can expand this)
        p.drawString(100, 680, "Summary:")
        p.drawString(120, 660, "• Total Evaluations: [Dynamic data would go here]")
        p.drawString(120, 640, "• Completion Rate: [Dynamic data would go here]")
        p.drawString(120, 620, "• Overdue Evaluations: [Dynamic data would go here]")
        
        p.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="analytics_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
        return response
        
    except ImportError:
        # Fallback if reportlab is not installed
        response = HttpResponse("PDF export requires reportlab library", content_type='text/plain')
        response.status_code = 500
        return response


def export_analytics_excel(request):
    """Generate Excel report of analytics data."""
    
    # Create CSV content (simpler fallback for Excel)
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Analytics Report', f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M")}'])
    writer.writerow([])  # Empty row
    writer.writerow(['Metric', 'Value'])
    
    # Add sample data (you can expand this with real analytics data)
    writer.writerow(['Total Evaluations', 'Dynamic data would go here'])
    writer.writerow(['Completion Rate', 'Dynamic data would go here'])
    writer.writerow(['Overdue Evaluations', 'Dynamic data would go here'])
    writer.writerow(['Recent Activity', 'Dynamic data would go here'])
    
    output.seek(0)
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_report_{timezone.now().strftime("%Y%m%d")}.csv"'
    return response


@login_required
@require_senior_management_access
def analytics_trends(request):
    """Analytics trends page."""
    return render(request, "evaluation/analytics_trends.html", {
        'title': 'Performance Trends',
        'today': timezone.now().date(),
    })


@login_required
@require_senior_management_access
def analytics_alerts(request):
    """Get analytics alerts data."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON data for AJAX requests
        alerts_data = {
            'alerts': [
                {
                    'id': 1,
                    'severity': 'critical',
                    'icon': 'exclamation-triangle',
                    'message': 'Department A has 15 overdue evaluations',
                    'timestamp': '2 hours ago'
                },
                {
                    'id': 2,
                    'severity': 'warning',
                    'icon': 'clock',
                    'message': 'Manager evaluations due in 24 hours',
                    'timestamp': '4 hours ago'
                },
                {
                    'id': 3,
                    'severity': 'critical',
                    'icon': 'user-times',
                    'message': '5 employees have not started evaluations',
                    'timestamp': '6 hours ago'
                },
                {
                    'id': 4,
                    'severity': 'warning',
                    'icon': 'chart-line',
                    'message': 'Performance trend declining in Department B',
                    'timestamp': '1 day ago'
                }
            ]
        }
        return JsonResponse(alerts_data)
    
    # Return HTML page for direct access
    return render(request, "evaluation/analytics_alerts.html", {
        'title': 'Risk Alerts',
        'today': timezone.now().date(),
    })


@login_required
def employee_dashboard(request):
    """
    Employee dashboard with personal performance insights and evaluation history.
    Shows employee-specific data in senior manager dashboard style.
    """
    from django.db.models import Avg, Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    user_profile = request.user.userprofile
    today = timezone.now().date()
    
    # Get employee's evaluation history
    employee_evaluations = DynamicEvaluation.objects.filter(
        employee=user_profile,
        status='completed'
    ).select_related('form', 'manager__user', 'department')
    
    # Recent evaluations (last 30 days)
    recent_evaluations = employee_evaluations.filter(
        submitted_at__gte=timezone.now() - timedelta(days=30)
    )
    
    # Pending evaluations
    pending_evaluations = DynamicEvaluation.objects.filter(
        employee=user_profile,
        status='pending'
    ).select_related('form', 'manager__user')
    
    # Calculate overall stats
    total_evaluations = employee_evaluations.count()
    recent_count = recent_evaluations.count()
    pending_count = pending_evaluations.count()
    
    
    # Team and Department Analytics
    manager = user_profile.manager  # Direct manager (team manager)
    department = user_profile.department
    
    # Get department manager
    department_manager = None
    if department:
        department_manager = department.manager
    
    # Get team members (colleagues under same manager)
    team_members = []
    team_size = 0
    if manager:
        team_members = UserProfile.objects.filter(manager=manager).exclude(id=user_profile.id)
        team_size = team_members.count() + 1  # +1 for the employee themselves
    
    # Department stats
    dept_employees_count = 0
    if department:
        dept_employees_count = UserProfile.objects.filter(department=department).count()
    
    # Get department performance comparison (if department exists)
    dept_performance_data = []
    if department:
        dept_evaluations = DynamicEvaluation.objects.filter(
            department=department,
            status='completed',
            submitted_at__gte=timezone.now() - timedelta(days=90)  # Last 3 months
        ).select_related('employee__user', 'form').prefetch_related(
            Prefetch(
                'answers',
                queryset=Answer.objects.filter(
                    question__qtype__in=['stars', 'emoji', 'rating', 'number'],
                    int_value__isnull=False
                ).select_related('question'),
                to_attr='numeric_answers'
            )
        )
        
        # Group by employee for department comparison
        employee_scores = {}
        for eval_instance in dept_evaluations:
            answers = eval_instance.numeric_answers
        
            if answers:
                total_score = 0
                count = 0
                for answer in answers:
                    if answer.question.qtype in ['stars', 'emoji']:
                        normalized = (answer.int_value - 1) * 25
                    elif answer.question.qtype == 'rating':
                        max_val = answer.question.max_value or 10
                        normalized = ((answer.int_value - 1) / (max_val - 1)) * 100
                    else:
                        normalized = answer.int_value
                    
                    total_score += normalized
                    count += 1
                
                if count > 0:
                    emp_id = eval_instance.employee.id
                    emp_name = eval_instance.employee.user.get_full_name() or eval_instance.employee.user.username
                    if emp_id not in employee_scores:
                        employee_scores[emp_id] = {'name': emp_name, 'scores': []}
                    employee_scores[emp_id]['scores'].append(total_score / count)
        
        # Calculate average for each employee
        for emp_id, data in employee_scores.items():
            if data['scores']:
                avg_score = sum(data['scores']) / len(data['scores'])
                is_current_user = (emp_id == user_profile.id)
                dept_performance_data.append({
                    'name': data['name'],
                    'score': round(avg_score, 1),
                    'is_current_user': is_current_user
                })
        
        # Sort by score descending
        dept_performance_data.sort(key=lambda x: x['score'], reverse=True)
    
    # Recent team activity (if manager exists)
    team_recent_activity = []
    if manager:
        team_recent_evals = DynamicEvaluation.objects.filter(
            manager=manager,
            status='completed',
            submitted_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('employee__user', 'form').order_by('-submitted_at')[:10]
        
        for eval_instance in team_recent_evals:
            team_recent_activity.append({
                'employee_name': eval_instance.employee.user.get_full_name() or eval_instance.employee.user.username,
                'form_name': eval_instance.form.name,
                'date': eval_instance.submitted_at,
                'is_current_user': eval_instance.employee.id == user_profile.id
            })
    
    context = {
        'user_profile': user_profile,
        'today': today,
        'total_evaluations': total_evaluations,
        'recent_evaluations_count': recent_count,
        'pending_evaluations_count': pending_count,
        'recent_evaluations': recent_evaluations[:5],  # Show last 5
        'pending_evaluations': pending_evaluations[:5],  # Show first 5 pending
        'last_viewed_at': timezone.now(),
        
        # Team & Department Info
        'manager': manager,  # Direct manager (team manager)
        'department': department,
        'department_manager': department_manager,
        'team_members': team_members[:5],  # Show first 5 team members
        'team_size': team_size,
        'dept_employees_count': dept_employees_count,
        'dept_performance_data': dept_performance_data[:10],  # Top 10 performers
        'team_recent_activity': team_recent_activity,
    }
    
    return render(request, "evaluation/employee_dashboard.html", context)
