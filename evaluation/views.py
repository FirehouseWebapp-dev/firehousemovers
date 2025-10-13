from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Avg, Sum, Max
from .models import Question
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Import dashboard views
from .dashboard_views import analytics_dashboard, analytics_dashboard_api
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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors as pdf_colors

logger = logging.getLogger(__name__)

from authentication.models import UserProfile, Department
from .models import EvalForm, Question, DynamicEvaluation, DynamicManagerEvaluation, ManagerAnswer, ReportHistory
from .forms_dynamic_admin import EvalFormForm, QuestionForm, QuestionChoiceForm
from .forms import PreviewEvalForm, DynamicEvaluationForm
from .constants import EvaluationStatus
from django.utils.timezone import now
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from firehousemovers.utils.permissions import role_checker, require_management, require_admin_or_senior, ajax_require_management
from .decorators import (
    require_department_management, require_department_management_for_form, 
    ajax_require_department_management, 
    require_manager_access, require_senior_management_access, require_evaluation_access
)
from .utils import (
    activate_evalform_safely, deactivate_evalform_safely, get_role_checker,
    check_department_permission, process_form_creation_with_conflicts, 
    process_form_edit_with_conflicts, calculate_eval_stats, determine_status,
    get_user_profile_safely, toggle_archive_helper
)
from .manager_performance_views import manager_personal_performance_data
from .evaluation_handlers import (
    handle_evaluation_submission, handle_evaluation_view, 
    handle_my_evaluations, handle_pending_evaluations,
    EMPLOYEE_EVALUATION_CONFIG, MANAGER_EVALUATION_CONFIG
)
from .dashboard_utils import (
    get_question_labels, 
    get_date_range, 
    aggregate_evaluation_data,
    get_emoji_distribution,
    get_chart_type_for_qtype,
    CHART_TYPES
)
from .manager_performance_views import (
    aggregate_manager_evaluation_data,
    get_manager_emoji_distribution
)
from .report_utils import (
    get_pdf_styles,
    parse_date_range,
    get_department_info,
    create_summary_table,
    create_detail_table,
    create_chart_metrics_table,
    create_person_header,
    create_individual_question_table,
    save_report_history,
    create_question_paragraph
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
    Admins and superusers can see all evaluations.
    """
    checker = get_role_checker(request.user)
    
    today = now()  # Use timezone-aware datetime for precision
    today_date = today.date()  # Keep date for display purposes
    
    # Check if user wants to show archived evaluations (default: True)
    show_archived = request.GET.get('show_archived', 'true') == 'true'
    
    # Senior management and superusers see ALL evaluations, managers see only their team's
    if checker.is_senior_management() or request.user.is_superuser:
        evaluations = DynamicEvaluation.objects.select_related("employee__user", "manager__user", "form", "department")
        if not show_archived:
            evaluations = evaluations.filter(is_archived=False)
        evaluations = evaluations.order_by("-week_start")
    else:
        # Get manager's team dynamic evaluations with optimized stats calculation
        evaluations = DynamicEvaluation.objects.filter(manager=checker.user_profile).select_related("employee__user", "form", "department")
        if not show_archived:
            evaluations = evaluations.filter(is_archived=False)
        evaluations = evaluations.order_by("-week_start")
    
    # Calculate all counts in a single optimized query using aggregation (before pagination)
    all_evaluations = evaluations  # Keep reference for stats
    stats = calculate_eval_stats(all_evaluations, today_date, "week_end")
    # Rename keys to match original naming
    stats = {
        'pending_count': stats['pending'],
        'completed_count': stats['completed'],
        'overdue_count': stats['overdue']
    }
    
    pending_count = stats['pending_count']
    completed_count = stats['completed_count']
    overdue_count = stats['overdue_count']
    
    # Pagination - 10 evaluations per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(evaluations, 10)  # 10 items per page
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    return render(request, "evaluation/dashboard.html", {
        "evaluations": page_obj,
        "page_obj": page_obj,
        "is_paginated": paginator.num_pages > 1,
        "today": today,
        "pending_count": pending_count,
        "completed_count": completed_count,
        "overdue_count": overdue_count,
        "show_archived": show_archived,
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
    
    # Check if user wants to show archived evaluations (default: True)
    show_archived = request.GET.get('show_archived', 'true') == 'true'
    
    # Get manager evaluations assigned to this senior manager with optimized query
    evaluations = DynamicManagerEvaluation.objects.filter(senior_manager=checker.user_profile).select_related("manager__user", "form", "department")
    if not show_archived:
        evaluations = evaluations.filter(is_archived=False)
    evaluations = evaluations.order_by("-period_start")
    
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
        "show_archived": show_archived,
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
    
    # Check if user wants to show archived evaluations (default: True)
    show_archived = request.GET.get('show_archived', 'true') == 'true'
    
    # Get evaluations for this specific period and form with optimized stats calculation
    evaluations = DynamicManagerEvaluation.objects.filter(
        senior_manager=checker.user_profile,
        form__name=form_name,
        period_start=period_start_date,
        period_end=period_end_date
    )
    
    if not show_archived:
        evaluations = evaluations.filter(is_archived=False)
    
    evaluations = evaluations.select_related("manager__user", "form", "department").order_by("manager__user__first_name", "manager__user__last_name")
    
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
        "show_archived": show_archived,
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
    from datetime import datetime
    
    checker = get_role_checker(request.user)
    today = now()
    today_date = today.date()
    
    logger.info(f"Analytics dashboard accessed by user {request.user.id} ({request.user.username})")
    
    # Get and parse date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    start_date_obj = None
    end_date_obj = None
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid start_date format: {start_date}")
            start_date = None
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}")
            end_date = None
    
    if start_date_obj or end_date_obj:
        logger.info(f"Date filters applied: {start_date_obj} to {end_date_obj}")
    
    # Create cache key based on user, date, and filters
    cache_key = f"analytics_dashboard_{request.user.id}_{today_date}_{start_date}_{end_date}"
    
    # Skip cache if filters are applied to ensure fresh filtered data
    has_filters = bool(start_date or end_date)
    
    # Try to get cached data first from analytics cache
    analytics_cache = caches['analytics']
    cached_data = None
    if not has_filters:
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
    
    # Helper function to apply date filters (DRY principle)
    def apply_employee_date_filter(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(week_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj)
        return queryset
    
    def apply_manager_date_filter(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(period_start__lte=end_date_obj, period_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(period_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(period_start__lte=end_date_obj)
        return queryset
    
    # Optimized querysets with date filters
    employee_qs = apply_employee_date_filter(
        DynamicEvaluation.objects.only('id', 'status', 'week_end', 'week_start', 'department_id', 'employee_id')
    )
    manager_qs = apply_manager_date_filter(
        DynamicManagerEvaluation.objects.only('id', 'status', 'period_end', 'period_start', 'department_id', 'manager_id')
    )
    
    employee_prefetch = Prefetch('dynamic_evaluations', queryset=employee_qs)
    manager_prefetch = Prefetch('dynamic_manager_evaluations', queryset=manager_qs)
    
    departments = Department.objects.prefetch_related(
        employee_prefetch,
        manager_prefetch
    ).only('id', 'title').all()
    
    dept_count = len(departments)
    logger.info(f"Processing {dept_count} departments for analytics")
    
    # Optimized employee evaluations query with select_related to prevent N+1
    all_employee_evaluations = apply_employee_date_filter(
        DynamicEvaluation.objects.select_related(
        'employee__user', 'form', 'department'
    ).only(
            'id', 'status', 'week_end', 'week_start', 'submitted_at', 'employee_id', 'department_id', 
        'form_id', 'employee__user__first_name', 'employee__user__last_name',
        'department__title', 'form__name'
    )
    )
    
    # Optimized manager evaluations query with select_related to prevent N+1
    all_manager_evaluations = apply_manager_date_filter(
        DynamicManagerEvaluation.objects.select_related(
        'manager__user', 'form', 'department'
    ).only(
            'id', 'status', 'period_end', 'period_start', 'submitted_at', 'manager_id', 'department_id',
        'form_id', 'manager__user__first_name', 'manager__user__last_name',
        'department__title', 'form__name'
    )
    )
    
    emp_eval_count = all_employee_evaluations.count()
    mgr_eval_count = all_manager_evaluations.count()
    logger.info(f"Loaded {emp_eval_count} employee evaluations and {mgr_eval_count} manager evaluations")
    
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
    
    # Manager effectiveness analytics - optimize with prefetch and reuse filter functions
    mgr_eval_qs = apply_employee_date_filter(
        DynamicEvaluation.objects.only('id', 'status', 'week_end', 'week_start', 'employee_id', 'manager_id')
    )
    mgr_reviews_qs = apply_manager_date_filter(
        DynamicManagerEvaluation.objects.only('id', 'status', 'period_end', 'period_start', 'manager_id', 'senior_manager_id')
    )
    
    mgr_evaluations_prefetch = Prefetch('dynamic_mgr_evaluations', queryset=mgr_eval_qs)
    manager_reviews_prefetch = Prefetch('dynamic_manager_reviews', queryset=mgr_reviews_qs)
    team_members_prefetch = Prefetch(
        'team_members',
        queryset=UserProfile.objects.only('id', 'user__first_name', 'user__last_name', 'role')
    )
    
    managers = UserProfile.objects.filter(role='manager').select_related('user').prefetch_related(
        mgr_evaluations_prefetch,
        manager_reviews_prefetch,
        team_members_prefetch
    ).only('id', 'user__first_name', 'user__last_name', 'role')
    
    manager_count = managers.count()
    logger.info(f"Processing {manager_count} managers for effectiveness analytics")
    
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
    
    # Recent activity (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_employee_evals = all_employee_evaluations.filter(submitted_at__gte=thirty_days_ago)
    recent_manager_evals = all_manager_evaluations.filter(submitted_at__gte=thirty_days_ago)
    
    logger.info(f"Recent activity: {recent_employee_evals.count()} employee evals, {recent_manager_evals.count()} manager evals (last 30 days)")
    
    
    # Department comparison data (reuse already prefetched evaluations to avoid N+1)
    department_comparison = []
    for dept in departments:
        dept_employee_evals = dept.dynamic_evaluations.all()
        dept_manager_evals = dept.dynamic_manager_evaluations.all()
        
        dept_emp_completed = len([e for e in dept_employee_evals if e.status == EvaluationStatus.COMPLETED])
        dept_emp_total = len(dept_employee_evals)
        dept_emp_completion_rate = (dept_emp_completed / dept_emp_total * 100) if dept_emp_total > 0 else 0
        
        dept_mgr_completed = len([e for e in dept_manager_evals if e.status == EvaluationStatus.COMPLETED])
        dept_mgr_total = len(dept_manager_evals)
        dept_mgr_completion_rate = (dept_mgr_completed / dept_mgr_total * 100) if dept_mgr_total > 0 else 0
        
        # Calculate department average rating (only if needed)
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
    
    logger.info(f"Department comparison data compiled for {len(department_comparison)} departments")
    
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
        'start_date': start_date,  # Date filter
        'end_date': end_date,  # Date filter
    }
    
    # Cache the computed data for 30 minutes (1800 seconds) - skip caching if filters applied
    if not has_filters:
        analytics_cache.set(cache_key, context_data, timeout=1800)
        logger.info(f"Analytics dashboard data cached for user {request.user.id} (30 min TTL)")
    else:
        logger.info(f"Analytics dashboard data NOT cached (filters active) for user {request.user.id}")
    
    # Convert serialized data back to proper objects for template rendering
    context_data['today'] = today_date
    context_data['data_computed_at'] = current_time
    context_data['last_viewed_at'] = current_time
    
    logger.info(f"Analytics dashboard computed successfully for user {request.user.id}")
    return render(request, "evaluation/senior_manager_analytics_dashboard.html", context_data)


@login_required
@require_senior_management_access
def analytics_department_detail(request, department_id):
    """
    Detailed analytics view for a specific department.
    Optimized with select_related to prevent N+1 queries.
    """
    department = get_object_or_404(Department, id=department_id)
    today = now()
    today_date = today.date()
    
    logger.info(f"Department detail analytics accessed for department {department_id} ({department.title}) by user {request.user.id}")
    
    # Optimized employee evaluations query with select_related to prevent N+1
    dept_employee_evals = DynamicEvaluation.objects.filter(
        department=department
    ).select_related(
        'employee__user', 'form', 'manager__user'
    ).only(
        'id', 'status', 'week_end', 'submitted_at', 'employee_id', 'manager_id',
        'employee__user__first_name', 'employee__user__last_name',
        'manager__user__first_name', 'manager__user__last_name',
        'form__name'
    )
    
    # Optimized manager evaluations query with select_related to prevent N+1
    dept_manager_evals = DynamicManagerEvaluation.objects.filter(
        department=department
    ).select_related(
        'manager__user', 'form', 'senior_manager__user'
    ).only(
        'id', 'status', 'period_end', 'submitted_at', 'manager_id', 'senior_manager_id',
        'manager__user__first_name', 'manager__user__last_name',
        'senior_manager__user__first_name', 'senior_manager__user__last_name',
        'form__name'
    )
    
    emp_eval_count = dept_employee_evals.count()
    mgr_eval_count = dept_manager_evals.count()
    logger.info(f"Department {department.title}: {emp_eval_count} employee evals, {mgr_eval_count} manager evals")
    
    # Department statistics
    dept_stats = calculate_eval_stats(dept_employee_evals, today_date, "week_end")
    dept_completion_rate = (dept_stats['completed'] / dept_stats['total'] * 100) if dept_stats['total'] > 0 else 0
    
    logger.info(f"Department {department.title} completion rate: {dept_completion_rate:.1f}%")
    
    # Optimized employee query with select_related to prevent N+1
    employees = UserProfile.objects.filter(
        dynamic_emp_evaluations__department=department
    ).distinct().select_related('user').only(
        'id', 'user__first_name', 'user__last_name'
    )
    
    # Pre-group evaluations by employee to avoid N+1 queries
    employee_evaluations = {}
    for eval in dept_employee_evals:
        employee_id = eval.employee_id
        if employee_id not in employee_evaluations:
            employee_evaluations[employee_id] = []
        employee_evaluations[employee_id].append(eval)
    
    # Build employee performance data
    employee_performance = []
    for employee in employees:
        emp_evals = employee_evaluations.get(employee.id, [])
        emp_stats = calculate_eval_stats(emp_evals, today_date, "week_end")
        emp_completion_rate = (emp_stats['completed'] / emp_stats['total'] * 100) if emp_stats['total'] > 0 else 0
        emp_status = determine_status(emp_stats['total'], emp_stats['pending'], emp_stats['overdue'])
        
        employee_performance.append({
            'employee': employee,
            'stats': emp_stats,
            'completion_rate': round(emp_completion_rate, 1),
            'has_evaluations': emp_stats['total'] > 0,
            'emp_status': emp_status,
        })
    
    employee_performance.sort(key=lambda x: x['completion_rate'], reverse=True)
    logger.info(f"Processed {len(employee_performance)} employees for department {department.title}")
    
    # Recent evaluations in this department (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_evals = dept_employee_evals.filter(
        submitted_at__gte=thirty_days_ago
    ).order_by('-submitted_at')[:10]
    
    recent_evals_list = list(recent_evals)
    logger.info(f"Found {len(recent_evals_list)} recent evaluations (last 30 days) for department {department.title}")
    
    context = {
        'department': department,
        'dept_stats': dept_stats,
        'completion_rate': round(dept_completion_rate, 1),
        'employee_performance': employee_performance,
        'recent_evals': recent_evals_list,
        'recent_evals_count': len(recent_evals_list),
        'today': today_date,
    }
    
    logger.info(f"Department detail analytics completed successfully for {department.title}")
    return render(request, "evaluation/analytics_department_detail.html", context)


@login_required
@require_senior_management_access
def analytics_team_detail(request, team_leader_id):
    """
    Detailed analytics view for a specific team (managed by a team leader).
    Optimized with select_related and prefetch to prevent N+1 queries.
    """
    team_leader = get_object_or_404(UserProfile, id=team_leader_id, role='manager')
    today = now()
    today_date = today.date()
    
    team_leader_name = f"{team_leader.user.first_name} {team_leader.user.last_name}"
    logger.info(f"Team analytics accessed for team leader {team_leader_id} ({team_leader_name}) by user {request.user.id}")
    
    # Optimized team members query with select_related
    team_members = UserProfile.objects.filter(
        manager=team_leader
    ).select_related('user').only(
        'id', 'user__first_name', 'user__last_name', 'role'
    )
    
    team_size = team_members.count()
    logger.info(f"Team {team_leader_name}: {team_size} members")
    
    # Optimized employee evaluations with select_related to prevent N+1
    team_employee_evals = DynamicEvaluation.objects.filter(
        employee__in=team_members
    ).select_related(
        'employee__user', 'form', 'manager__user'
    ).only(
        'id', 'status', 'week_end', 'submitted_at', 'employee_id', 'manager_id',
        'employee__user__first_name', 'employee__user__last_name',
        'manager__user__first_name', 'manager__user__last_name',
        'form__name'
    )
    
    # Optimized manager evaluations with select_related to prevent N+1
    team_manager_evals = DynamicManagerEvaluation.objects.filter(
        manager=team_leader
    ).select_related(
        'manager__user', 'form', 'senior_manager__user'
    ).only(
        'id', 'status', 'period_end', 'submitted_at', 'manager_id', 'senior_manager_id',
        'manager__user__first_name', 'manager__user__last_name',
        'senior_manager__user__first_name', 'senior_manager__user__last_name',
        'form__name'
    )
    
    emp_eval_count = team_employee_evals.count()
    mgr_eval_count = team_manager_evals.count()
    logger.info(f"Team {team_leader_name}: {emp_eval_count} employee evals, {mgr_eval_count} manager evals")
    
    # Calculate team and manager statistics
    team_stats = calculate_eval_stats(team_employee_evals, today_date, "week_end")
    manager_stats = calculate_eval_stats(team_manager_evals, today_date, "period_end")
    
    team_completion_rate = (team_stats['completed'] / team_stats['total'] * 100) if team_stats['total'] > 0 else 0
    manager_completion_rate = (manager_stats['completed'] / manager_stats['total'] * 100) if manager_stats['total'] > 0 else 0
    
    logger.info(f"Team {team_leader_name} completion rates - Team: {team_completion_rate:.1f}%, Manager: {manager_completion_rate:.1f}%")
    
    # Pre-group evaluations by team member to avoid N+1 queries
    member_evaluations = {}
    for eval in team_employee_evals:
        member_id = eval.employee_id
        if member_id not in member_evaluations:
            member_evaluations[member_id] = []
        member_evaluations[member_id].append(eval)
    
    # Build member performance data
    member_performance = []
    for member in team_members:
        member_evals = member_evaluations.get(member.id, [])
        member_stats = calculate_eval_stats(member_evals, today_date, "week_end")
        member_completion_rate = (member_stats['completed'] / member_stats['total'] * 100) if member_stats['total'] > 0 else 0
        member_status = determine_status(member_stats['total'], member_stats['pending'], member_stats['overdue'])
        
        member_performance.append({
            'member': member,
            'stats': member_stats,
            'completion_rate': round(member_completion_rate, 1),
            'has_evaluations': member_stats['total'] > 0,
            'member_status': member_status,
        })
    
    member_performance.sort(key=lambda x: x['completion_rate'], reverse=True)
    logger.info(f"Processed {len(member_performance)} team members for team {team_leader_name}")
    
    # Recent evaluations in this team (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_evals = team_employee_evals.filter(
        submitted_at__gte=thirty_days_ago
    ).order_by('-submitted_at')[:10]
    
    recent_evals_list = list(recent_evals)
    team_members_list = list(team_members)
    
    logger.info(f"Found {len(recent_evals_list)} recent evaluations (last 30 days) for team {team_leader_name}")
    
    context = {
        'team_leader': team_leader,
        'team_members': team_members_list,
        'team_stats': team_stats,
        'manager_stats': manager_stats,
        'team_completion_rate': round(team_completion_rate, 1),
        'manager_completion_rate': round(manager_completion_rate, 1),
        'member_performance': member_performance,
        'recent_evals': recent_evals_list,
        'recent_evals_count': len(recent_evals_list),
        'today': today_date,
    }
    
    logger.info(f"Team analytics completed successfully for team {team_leader_name}")
    return render(request, "evaluation/analytics_team_detail.html", context)


@login_required
@require_senior_management_access
def employee_evaluations_list(request, employee_id):
    """
    View all evaluations for a specific employee (for senior managers).
    Shows both completed and pending evaluations with archive functionality.
    """
    employee = get_object_or_404(UserProfile.objects.select_related('user', 'department', 'manager'), id=employee_id)
    today = now().date()
    
    # Check if user wants to show archived evaluations (default: False)
    show_archived = request.GET.get('show_archived', 'false') == 'true'
    
    # Get all employee evaluations
    evaluations = DynamicEvaluation.objects.filter(
        employee=employee
    ).select_related(
        'form', 'department', 'manager__user'
    ).order_by('-week_start')
    
    # Filter by archive status
    if not show_archived:
        evaluations = evaluations.filter(is_archived=False)
    
    # Calculate stats (including archived for accurate counts)
    all_evaluations = DynamicEvaluation.objects.filter(employee=employee)
    total_evals = all_evaluations.count()
    completed_evals = all_evaluations.filter(status='completed').count()
    pending_evals = all_evaluations.filter(status='pending').count()
    overdue_evals = all_evaluations.filter(status='pending', week_end__lt=today).count()
    
    percent_complete = round((completed_evals / total_evals * 100) if total_evals > 0 else 0, 1)
    
    # Pagination - 10 evaluations per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(evaluations, 10)  # 10 items per page
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    context = {
        'employee': employee,
        'evaluations': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total': total_evals,
        'completed': completed_evals,
        'pending': pending_evals,
        'overdue': overdue_evals,
        'percent_complete': percent_complete,
        'today': today,
        'show_archived': show_archived,
    }
    
    return render(request, "evaluation/employee_evaluations_list.html", context)


@login_required
def employee_dashboard(request):
    """
    Employee dashboard with personal performance insights and evaluation history.
    Shows employee-specific data in senior manager dashboard style.
    Can be used by managers to view specific employee data via employee_id parameter.
    Optimized with select_related to prevent N+1 queries.
    """
    
    # Check if manager is viewing specific employee data
    employee_id = request.GET.get('employee_id')
    is_manager_view = employee_id is not None
    
    if is_manager_view:
        try:
            # Optimized: Use select_related to fetch related user in single query
            target_employee = UserProfile.objects.select_related('user', 'manager', 'department').get(id=employee_id)
            current_user_profile = get_user_profile_safely(request.user, request)
            
            if not current_user_profile:
                return redirect('authentication:login')
            
            checker = get_role_checker(request.user)
            has_permission = (
                target_employee.manager == current_user_profile or
                (hasattr(current_user_profile, 'managed_department') and 
                 current_user_profile.managed_department and 
                 target_employee.department == current_user_profile.managed_department) or
                checker.is_senior_management or
                checker.is_admin
            )
            
            if not has_permission:
                messages.error(request, "You don't have permission to view this employee's data.")
                return redirect('evaluation:manager_employee_dashboard')
            
            user_profile = target_employee
            logger.info(f"Manager {request.user.id} viewing employee dashboard for {employee_id} ({user_profile.user.get_full_name()})")
        except UserProfile.DoesNotExist:
            messages.error(request, "Employee not found.")
            logger.warning(f"Manager {request.user.id} attempted to view non-existent employee {employee_id}")
            return redirect('evaluation:manager_employee_dashboard')
    else:
        user_profile = get_user_profile_safely(request.user, request)
        if not user_profile:
            return redirect('authentication:login')
        logger.info(f"Employee dashboard accessed by user {request.user.id} ({user_profile.user.get_full_name()})")
    
    today = timezone.now().date()
    
    # Optimized: Get completed evaluations with select_related to prevent N+1
    employee_evaluations = DynamicEvaluation.objects.filter(
        employee=user_profile,
        status='completed'
    ).select_related('form', 'manager__user', 'department')
    
    # Optimized: Get pending evaluations with select_related to prevent N+1
    pending_evaluations = DynamicEvaluation.objects.filter(
        employee=user_profile,
        status='pending'
    ).select_related('form', 'manager__user')
    
    # Calculate stats efficiently
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_evaluations = employee_evaluations.count()
    pending_count = pending_evaluations.count()
    
    # Filter recent evaluations (exclude null submitted_at)
    recent_evaluations = employee_evaluations.filter(
        submitted_at__gte=thirty_days_ago
    ).exclude(submitted_at__isnull=True)
    recent_count = recent_evaluations.count()
    
    logger.info(f"Employee {user_profile.user.get_full_name()}: {total_evaluations} total, {recent_count} recent, {pending_count} pending")
    
    # Get performance trends data
    performance_data = {}
    question_labels = {}
    
    if user_profile.department:
        range_type = 'monthly'
        start_date, end_date, granularity = get_date_range(range_type)
        
        # Optimized: Get trend evaluations with select_related to prevent N+1
        trend_evaluations = DynamicEvaluation.objects.filter(
            employee=user_profile,
            department=user_profile.department,
            week_start__lte=end_date,
            week_end__gte=start_date,
            status='completed'
        ).select_related('manager__user', 'form', 'department', 'employee__user')
        
        trend_eval_count = trend_evaluations.count()
        
        if trend_eval_count == 0:
            logger.info(f"No trend evaluations found for employee {user_profile.user.get_full_name()}")
            performance_data = {}
            question_labels = {}
        else:
            logger.info(f"Processing {trend_eval_count} trend evaluations for employee {user_profile.user.get_full_name()}")
            
            # Get most recent evaluation to determine current form
            most_recent_evaluation = trend_evaluations.order_by('-week_start').first()
            
            if not most_recent_evaluation:
                performance_data = {}
                question_labels = {}
            else:
                eval_form = most_recent_evaluation.form
                
                # Optimized: Get questions with select_related to prevent N+1
                questions = Question.objects.filter(
                    form=eval_form,
                    include_in_trends=True
                ).select_related('form').order_by('order')
                
                chart_data = {}
                question_labels = get_question_labels(
                    user_profile.department.slug or user_profile.department.title.lower()
                )
                
                # Aggregate data for all questions
                aggregated_data = aggregate_evaluation_data(
                    trend_evaluations, 
                    questions, 
                    granularity
                )
                
                # Process each question's data
                for question in questions:
                    question_key = f"Q{question.order}"
                    chart_type = get_chart_type_for_qtype(question.qtype)
                    
                    # Use emoji distribution for emoji pie charts
                    if question.qtype == "emoji" and chart_type == "pie":
                        emoji_data = get_emoji_distribution(trend_evaluations, question)
                        chart_data[question_key] = {
                            'type': chart_type,
                            'data': emoji_data,
                            'label': question_labels.get(question_key, question.text)
                        }
                    else:
                        chart_data[question_key] = {
                            'type': chart_type,
                            'data': aggregated_data.get(question_key, []),
                            'label': question_labels.get(question_key, question.text)
                        }
                
                performance_data = {
                    'chart_data': chart_data,
                    'question_labels': question_labels,
                    'range_type': range_type,
                    'start_date': start_date,
                    'end_date': end_date,
                    'granularity': granularity,
                    'chart_types': CHART_TYPES
                }
    
                logger.info(f"Performance trends compiled for {len(chart_data)} questions")
    
    context = {
        'user_profile': user_profile,
        'today': today,
        'total_evaluations': total_evaluations,
        'recent_evaluations_count': recent_count,
        'pending_evaluations_count': pending_count,
        'recent_evaluations': recent_evaluations[:5],
        'pending_evaluations': pending_evaluations[:5],
        'last_viewed_at': timezone.now(),
        'performance_data': performance_data,
        'is_manager_view': is_manager_view,
        'viewing_employee_name': user_profile.user.get_full_name() if is_manager_view else None,
    }
    
    logger.info(f"Employee dashboard rendered successfully for {user_profile.user.get_full_name()}")
    return render(request, "evaluation/employee_dashboard.html", context)


@login_required
def manager_performance_dashboard(request):
    """
    Manager's own performance dashboard showing their evaluation trends.
    Senior managers can view other managers' performance by providing manager_id query parameter.
    Optimized with select_related to prevent N+1 queries.
    """
    period_type = request.GET.get('period', 'monthly')
    if period_type not in ['monthly', 'quarterly', 'annually']:
        period_type = 'monthly'
    
    checker = get_role_checker(request.user)
    
    # Check permissions
    if not (checker.is_manager() or checker.is_senior_management or checker.is_admin):
        logger.warning(f"User {request.user.id} denied access to manager performance dashboard")
        return redirect("evaluation:dashboard")
    
    # Determine target user profile
    manager_id = request.GET.get('manager_id')
    is_viewing_other = bool(manager_id and (checker.is_senior_management or checker.is_admin))
    
    if is_viewing_other:
        # Optimized: Use select_related to prevent N+1
        user_profile = get_object_or_404(
            UserProfile.objects.select_related('user', 'managed_department'),
            id=manager_id
        )
        logger.info(f"Senior manager {request.user.id} viewing performance dashboard for manager {manager_id} ({user_profile.user.get_full_name()})")
    else:
        user_profile = checker.user_profile
        logger.info(f"Manager {request.user.id} ({user_profile.user.get_full_name()}) accessing own performance dashboard")
    
    today = timezone.now().date()
    
    # Parse date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid start_date format: {start_date}")
            start_date = None
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}")
            end_date = None
    
    if start_date_obj or end_date_obj:
        logger.info(f"Date filters applied: {start_date_obj} to {end_date_obj}")
    
    # Optimized: Get completed evaluations with select_related to prevent N+1
    completed_evaluations = DynamicEvaluation.objects.filter(
        manager=user_profile,
        status='completed'
    ).select_related('form', 'employee__user', 'department')
    
    # Optimized: Get received evaluations with select_related to prevent N+1
    all_received_evaluations_unfiltered = DynamicManagerEvaluation.objects.filter(
        manager=user_profile,
        status='completed'
    ).select_related('form', 'senior_manager__user', 'department')
    
    # Helper function to apply date filters (DRY principle)
    def apply_date_filter_to_manager_evals(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(period_start__lte=end_date_obj, period_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(period_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(period_start__lte=end_date_obj)
        return queryset
    
    received_evaluations = apply_date_filter_to_manager_evals(all_received_evaluations_unfiltered)
    
    comp_eval_count = completed_evaluations.count()
    recv_eval_count = received_evaluations.count()
    logger.info(f"Manager {user_profile.user.get_full_name()}: {comp_eval_count} completed evals, {recv_eval_count} received evals")
    
    # Recent evaluations (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_evaluations = received_evaluations.filter(
        submitted_at__gte=thirty_days_ago
    ).exclude(submitted_at__isnull=True)
    
    # Calculate stats efficiently
    total_evaluations = received_evaluations.count()
    recent_count = recent_evaluations.count()
    
    logger.info(f"Manager {user_profile.user.get_full_name()}: {total_evaluations} total received, {recent_count} recent (last 30 days)")
    
    # Get performance trends data
    performance_data = {}
    
    if hasattr(user_profile, 'managed_department') and user_profile.managed_department:
        range_type = 'monthly'
        trend_start_date, trend_end_date, granularity = get_date_range(range_type)
        
        # Get trend evaluations
        trend_evaluations = received_evaluations.filter(
            period_start__lte=trend_end_date,
            period_end__gte=trend_start_date
        )
        
        trend_count = trend_evaluations.count()
        
        if trend_count > 0:
            logger.info(f"Processing {trend_count} trend evaluations for manager {user_profile.user.get_full_name()}")
            
            # Get most recent evaluation to determine form
            most_recent_evaluation = trend_evaluations.order_by('-period_start').first()
            
            if most_recent_evaluation:
                eval_form = most_recent_evaluation.form
                
                # Optimized: Get questions with select_related to prevent N+1
                questions = Question.objects.filter(
                    form=eval_form,
                    include_in_trends=True
                ).select_related('form').order_by('order')
                
                chart_data = {}
                
                # Aggregate data using manager-specific function
                aggregated_data = aggregate_manager_evaluation_data(
                    trend_evaluations, 
                    questions, 
                    granularity
                )
                
                # Process each question's data
                for question in questions:
                    question_key = f"Q{question.order}"
                    chart_type = get_chart_type_for_qtype(question.qtype)
                    
                    # Use emoji distribution for emoji pie charts
                    if question.qtype == "emoji" and chart_type == "pie":
                        emoji_data = get_manager_emoji_distribution(trend_evaluations, question)
                        chart_data[question_key] = {
                            'type': chart_type,
                            'data': emoji_data,
                            'label': question.text
                        }
                    else:
                        chart_data[question_key] = {
                            'type': chart_type,
                            'data': aggregated_data.get(question_key, []),
                            'label': question.text
                        }
                
                performance_data = {
                    'chart_data': chart_data,
                    'range_type': range_type,
                    'start_date': trend_start_date,
                    'end_date': trend_end_date,
                    'granularity': granularity,
                    'chart_types': CHART_TYPES
                }
                
                logger.info(f"Performance trends compiled for {len(chart_data)} questions")
        else:
            logger.info(f"No trend evaluations found for manager {user_profile.user.get_full_name()}")
    
    # Get manager's personal performance data (when they are being evaluated)
    personal_performance_data = manager_personal_performance_data(
        request, period_type, start_date_obj, end_date_obj, target_user_profile=user_profile
    )
    
    logger.info(f"Personal performance data retrieved for manager {user_profile.user.get_full_name()}")
    
    # Get senior manager from most recent evaluation (use unfiltered data)
    senior_manager = None
    if all_received_evaluations_unfiltered.exists():
        most_recent = all_received_evaluations_unfiltered.order_by('-submitted_at').first()
        if most_recent and most_recent.senior_manager:
            senior_manager = most_recent.senior_manager
            logger.info(f"Senior manager identified: {senior_manager.user.get_full_name()}")
    
    context = {
        'user_profile': user_profile,
        'today': today,
        'total_evaluations': total_evaluations,
        'recent_evaluations_count': recent_count,
        'recent_evaluations': recent_evaluations[:5],
        'last_viewed_at': timezone.now(),
        'performance_data': performance_data,
        'personal_performance_data': personal_performance_data,
        'period_type': period_type,
        'dashboard_type': 'manager_performance',
        'senior_manager': senior_manager,
        'start_date': start_date,
        'end_date': end_date,
        'manager_id': manager_id,
        'viewing_other_manager': is_viewing_other,
    }
    
    logger.info(f"Manager performance dashboard rendered successfully for {user_profile.user.get_full_name()}")
    return render(request, "evaluation/manager_performance_dashboard.html", context)


@login_required
@require_senior_management_access
def senior_manager_performance_overview(request):
    """
    Senior Manager Performance Overview - Shows department metrics and all managers rating trends.
    Only accessible to senior managers and admins.
    Optimized with prefetch_related to prevent N+1 queries.
    """
    checker = get_role_checker(request.user)
    
    logger.info(f"Senior manager performance overview accessed by user {request.user.id} ({request.user.username})")
    
    period_type = request.GET.get('period', 'monthly')
    if period_type not in ['monthly', 'quarterly', 'annually']:
        period_type = 'monthly'
    
    # Parse date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid start_date format: {start_date}")
            start_date = None
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}")
            end_date = None
    
    if start_date_obj or end_date_obj:
        logger.info(f"Date filters applied: {start_date_obj} to {end_date_obj}")
    
    # Optimized: Prefetch related data to prevent N+1 queries
    all_departments = Department.objects.all().prefetch_related(
        'members', 
        'eval_forms',
        'eval_forms__questions'
    )
    
    dept_count = all_departments.count()
    logger.info(f"Processing department metrics for {dept_count} departments")
    
    # Helper function to get default metric label (DRY principle)
    def get_default_metric_label(dept_title):
        if not dept_title:
            return "Performance Metric"
        
        dept_lower = dept_title.lower()
        if "sales" in dept_lower:
            return "Total Leads"
        elif any(x in dept_lower for x in ["driver", "field", "mover"]):
            return "Total Moves"
        elif "claims" in dept_lower:
            return "Total Claims Processed"
        elif "operation" in dept_lower:
            return "Total Moves Supervised"
        elif "it" in dept_lower:
            return "Total Support Requests Resolved"
        elif "warehouse" in dept_lower:
            return "Total Move-In/Out Tasks"
        elif "accounting" in dept_lower:
            return "Total Invoices Processed"
        elif "admin" in dept_lower:
            return "Total Tasks"
        return "Performance Metric"
    
    department_metrics = []
    for dept in all_departments:
        dept_employees = dept.members.filter(is_employee=True)
        employee_count = dept_employees.count()
        default_label = get_default_metric_label(dept.title)
        
        # Get active weekly form
        active_form = dept.eval_forms.filter(
            is_active=True,
            name__icontains='weekly'
        ).first()
        
        if not active_form:
            department_metrics.append({
                'department': dept,
                'employee_count': employee_count,
                'metric_value': 0,
                'metric_label': default_label,
            })
            continue
        
        # Get first question
        first_question = active_form.questions.order_by('order').first()
        
        if not first_question:
            department_metrics.append({
                'department': dept,
                'employee_count': employee_count,
                'metric_value': 0,
                'metric_label': default_label,
            })
            continue
        
        # Helper function to apply date filters (DRY principle - reuse from earlier)
        def apply_date_filter_to_evals(queryset):
            if start_date_obj and end_date_obj:
                return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
            elif start_date_obj:
                return queryset.filter(week_end__gte=start_date_obj)
            elif end_date_obj:
                return queryset.filter(week_start__lte=end_date_obj)
            return queryset
        
        # Get completed evaluations with date filters
        dept_evaluations = apply_date_filter_to_evals(
            DynamicEvaluation.objects.filter(department=dept, status='completed')
        )
        
        # Sum up the values from the first question across all evaluations
        if first_question.qtype in ['number', 'rating', 'stars']:
            total_value = Answer.objects.filter(
                instance__in=dept_evaluations,
                question=first_question,
                int_value__isnull=False
            ).aggregate(total=Sum('int_value'))['total'] or 0
        else:
            total_value = Answer.objects.filter(
                instance__in=dept_evaluations,
                question=first_question
            ).count()
        
        # Helper function to customize metric label (DRY principle)
        def customize_metric_label(dept_title, question_text):
            if not dept_title:
                return question_text
            
            dept_lower = dept_title.lower()
            q_lower = question_text.lower()
            
            if "sales" in dept_lower:
                if "lead" in q_lower:
                    return "Total Leads"
                elif "sale" in q_lower:
                    return "Total Sales"
            elif any(x in dept_lower for x in ["driver", "field", "mover"]):
                if "move" in q_lower:
                    return "Total Moves"
                elif "job" in q_lower:
                    return "Total Jobs"
            elif "claims" in dept_lower:
                if "claim" in q_lower or "process" in q_lower:
                    return "Total Claims Processed"
            elif "operation" in dept_lower:
                if "move" in q_lower or "supervis" in q_lower:
                    return "Total Moves Supervised"
            elif "it" in dept_lower:
                if "support" in q_lower or "request" in q_lower or "ticket" in q_lower:
                    return "Total Support Requests Resolved"
            elif "warehouse" in dept_lower:
                if "move" in q_lower or "task" in q_lower:
                    return "Total Move-In/Out Tasks"
            elif "accounting" in dept_lower:
                if "invoice" in q_lower or "bill" in q_lower:
                    return "Total Invoices Processed"
            
            return question_text
        
        metric_label = customize_metric_label(dept.title, first_question.text)
        
        department_metrics.append({
            'department': dept,
            'employee_count': employee_count,
            'metric_value': total_value,
            'metric_label': metric_label,
        })
    
    logger.info(f"Compiled metrics for {len(department_metrics)} departments")
    
    # Get all managers' rating trends
    managers_rating_trends = get_all_managers_rating_trends(period_type, start_date_obj, end_date_obj)
    managers_rating_trends_json = json.dumps(managers_rating_trends)
    
    # Get department comparisons for Q1-Q5 (weekly evaluation questions)
    # Q1: Work Volume (number) - Bar chart
    dept_q1_work_volume = get_department_question_comparison(
        question_order=0, chart_type='bar', 
        start_date_obj=start_date_obj, end_date_obj=end_date_obj
    )
    dept_q1_work_volume_json = json.dumps(dept_q1_work_volume)
    
    # Q2: Quality/Timeliness (numeric %) - Bar chart
    dept_q2_quality = get_department_question_comparison(
        question_order=1, chart_type='bar',
        start_date_obj=start_date_obj, end_date_obj=end_date_obj
    )
    dept_q2_quality_json = json.dumps(dept_q2_quality)
    
    # Q3: 5-Star Rating - Line chart
    dept_q3_rating = get_department_question_comparison(
        question_order=2, chart_type='line',
        start_date_obj=start_date_obj, end_date_obj=end_date_obj
    )
    dept_q3_rating_json = json.dumps(dept_q3_rating)
    
    # Q4: Emoji Satisfaction - Pie chart
    dept_q4_satisfaction = get_department_question_comparison(
        question_order=3, chart_type='pie',
        start_date_obj=start_date_obj, end_date_obj=end_date_obj
    )
    dept_q4_satisfaction_json = json.dumps(dept_q4_satisfaction)
    
    # Q5: Confidence Rating (1-10) - Bar chart
    dept_q5_confidence = get_department_question_comparison(
        question_order=4, chart_type='bar',
        start_date_obj=start_date_obj, end_date_obj=end_date_obj
    )
    dept_q5_confidence_json = json.dumps(dept_q5_confidence)
    
    context = {
        'department_metrics': department_metrics,
        'managers_rating_trends': managers_rating_trends,
        'managers_rating_trends_json': managers_rating_trends_json,
        'dept_q1_work_volume': dept_q1_work_volume,
        'dept_q1_work_volume_json': dept_q1_work_volume_json,
        'dept_q2_quality': dept_q2_quality,
        'dept_q2_quality_json': dept_q2_quality_json,
        'dept_q3_rating': dept_q3_rating,
        'dept_q3_rating_json': dept_q3_rating_json,
        'dept_q4_satisfaction': dept_q4_satisfaction,
        'dept_q4_satisfaction_json': dept_q4_satisfaction_json,
        'dept_q5_confidence': dept_q5_confidence,
        'dept_q5_confidence_json': dept_q5_confidence_json,
        'period_type': period_type,
        'start_date': start_date,
        'end_date': end_date,
        'last_viewed_at': timezone.now(),
    }
    
    logger.info(f"Senior manager performance overview rendered successfully with period_type={period_type}")
    return render(request, "evaluation/senior_manager_performance_overview.html", context)


def get_all_managers_rating_trends(period_type='monthly', start_date_obj=None, end_date_obj=None):
    """
    Get rating trends for all managers based on period type (monthly, quarterly, annually).
    Returns data formatted for line chart showing manager performance over time.
    Optimized with select_related to prevent N+1 queries.
    """
    # Optimized: Get evaluations with select_related to prevent N+1
    base_evaluations = DynamicManagerEvaluation.objects.filter(
        status='completed'
    ).select_related('manager__user', 'form')
    
    total_evals = base_evaluations.count()
    logger.info(f"get_all_managers_rating_trends - Total completed evaluations: {total_evals}, period={period_type}")
    
    # Helper function to apply date filters (DRY principle)
    def apply_date_filters(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(period_start__lte=end_date_obj, period_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(period_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(period_start__lte=end_date_obj)
        return queryset
    
    base_evaluations = apply_date_filters(base_evaluations)
    filtered_count = base_evaluations.count()
    logger.info(f"get_all_managers_rating_trends - After date filter: {filtered_count} evaluations")
    
    # Helper function to format period (DRY principle)
    def format_period(period_start, ptype):
        if ptype == "monthly":
            return period_start.strftime('%b %Y')
        elif ptype == "quarterly":
            quarter = (period_start.month - 1) // 3 + 1
            return f"Quarter {quarter} {period_start.year}"
        elif ptype == "annually":
            return str(period_start.year)
        return period_start.strftime('%b %Y')
    
    # Calculate average ratings per manager per period
    manager_trends = defaultdict(lambda: defaultdict(list))
    
    for evaluation in base_evaluations:
        # Check if evaluation period falls within date filter
        if start_date_obj and evaluation.period_start < start_date_obj:
            continue
        if end_date_obj and evaluation.period_start > end_date_obj:
            continue
        
        period = format_period(evaluation.period_start, period_type)
        
        # Optimized: Get Overall Rating question (already select_related on form)
        overall_rating_question = Question.objects.filter(
            form=evaluation.form,
            text__icontains="Overall Rating"
        ).first()
        
        if overall_rating_question:
            # Optimized: Get answer with select_related
            overall_rating_answer = ManagerAnswer.objects.filter(
                instance=evaluation,
                question=overall_rating_question,
                int_value__isnull=False
            ).select_related('question', 'instance').first()
            
            if overall_rating_answer and overall_rating_answer.int_value:
                manager_name = evaluation.manager.user.get_full_name() or evaluation.manager.user.username
                manager_trends[manager_name][period].append(overall_rating_answer.int_value)
            else:
                logger.debug(f"No overall rating answer for evaluation {evaluation.id}")
        else:
            logger.debug(f"No Overall Rating question for form {evaluation.form.name}")
    
    # If no data found, return empty structure
    if not manager_trends:
        logger.warning(f"get_all_managers_rating_trends - No manager trends data found for period_type: {period_type}")
        return {
            'labels': [],
            'datasets': []
        }
    
    manager_count = len(manager_trends)
    logger.info(f"get_all_managers_rating_trends - Found trends for {manager_count} managers")
    
    # Collect and sort periods
    periods = set()
    for manager_data in manager_trends.values():
        periods.update(manager_data.keys())
    
    # Helper function to sort periods (DRY principle)
    def sort_periods(period_list, ptype):
        if ptype == "monthly":
            return sorted(period_list, key=lambda x: datetime.strptime(x, '%b %Y'))
        elif ptype == "quarterly":
            return sorted(period_list, key=lambda x: (int(x.split()[2]), int(x.split()[1])))
        elif ptype == "annually":
            return sorted(period_list, key=lambda x: int(x))
        return sorted(period_list)
    
    periods = sort_periods(list(periods), period_type)
    
    chart_data = {
        'labels': periods,
        'datasets': []
    }
    
    # Create dataset for each manager
    colors = [
        '#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', 
        '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
    ]
    
    for idx, (manager_name, period_data) in enumerate(manager_trends.items()):
        data_points = []
        for period in periods:
            if period in period_data:
                avg = sum(period_data[period]) / len(period_data[period])
                data_points.append(round(avg, 2))
            else:
                data_points.append(None)
        
        chart_data['datasets'].append({
            'label': manager_name,
            'data': data_points,
            'borderColor': colors[idx % len(colors)],
            'backgroundColor': colors[idx % len(colors)] + '20',
            'tension': 0.4
        })
    
    dataset_count = len(chart_data['datasets'])
    period_count = len(chart_data['labels'])
    logger.info(f"get_all_managers_rating_trends - Returning chart data: {period_count} periods, {dataset_count} datasets")
    
    return chart_data


def _apply_date_filters(queryset, start_date_obj=None, end_date_obj=None):
    """Helper function to apply date filters to evaluation querysets."""
    if start_date_obj and end_date_obj:
        return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
    elif start_date_obj:
        return queryset.filter(week_end__gte=start_date_obj)
    elif end_date_obj:
        return queryset.filter(week_start__lte=end_date_obj)
    return queryset


def _get_department_evaluations_bulk(start_date_obj=None, end_date_obj=None):
    """
    Get all completed evaluations grouped by department in a single optimized query.
    Returns tuple: (dict mapping department_id to list of evaluation IDs, dict mapping eval_id to form_id)
    """
    evaluations_qs = DynamicEvaluation.objects.filter(status='completed').select_related('department')
    evaluations_qs = _apply_date_filters(evaluations_qs, start_date_obj, end_date_obj)
    
    # Group evaluations by department and build eval->form mapping
    dept_evaluations = defaultdict(list)
    eval_to_form = {}
    
    for eval_obj in evaluations_qs.only('id', 'department_id', 'form_id'):
        dept_evaluations[eval_obj.department_id].append(eval_obj.id)
        eval_to_form[eval_obj.id] = eval_obj.form_id
    
    logger.info(f"_get_department_evaluations_bulk - Found {len(eval_to_form)} evaluations for {len(dept_evaluations)} departments")
    return dept_evaluations, eval_to_form


def get_department_question_comparison(question_order, chart_type='bar', start_date_obj=None, end_date_obj=None):
    """
    Generic function to get question data across all departments by question order.
    Optimized to avoid N+1 queries.
    
    Args:
        question_order: The order number of the question (0-4 for Q1-Q5)
        chart_type: Type of chart ('bar', 'line', 'pie')
        start_date_obj: Start date filter
        end_date_obj: End date filter
    
    Returns:
        dict: Chart data with labels, data, question_text, chart_type, has_data
    """
    logger.info(f"get_department_question_comparison - Starting for Q{question_order + 1} (order={question_order})")
    
    # Get all departments
    departments = Department.objects.all().order_by('title')
    dept_count = departments.count()
    logger.info(f"Processing {dept_count} departments for Q{question_order + 1}")
    
    # Get all evaluations grouped by department (single query)
    dept_eval_ids, eval_to_form = _get_department_evaluations_bulk(start_date_obj, end_date_obj)
    
    if not dept_eval_ids:
        logger.warning(f"get_department_question_comparison Q{question_order + 1} - No evaluations found")
        return {
            'labels': [],
            'data': [],
            'question_text': '',
            'chart_type': chart_type,
            'has_data': False
        }
    
    # Get all relevant questions for this order across all forms (single query)
    all_eval_ids = [eid for eids in dept_eval_ids.values() for eid in eids]
    form_ids = set(eval_to_form.values())
    
    questions_by_form = {}
    for question in Question.objects.filter(form_id__in=form_ids, order=question_order).select_related('form'):
        questions_by_form[question.form_id] = question
    
    logger.info(f"Found {len(questions_by_form)} unique questions with order={question_order} across {len(form_ids)} forms")
    
    # Get all answers for relevant evaluations in bulk (single query)
    question_ids = list(questions_by_form.values())
    answers_data = Answer.objects.filter(
        instance_id__in=all_eval_ids,
        question__in=question_ids,
        int_value__isnull=False
    ).values('instance_id', 'instance__department_id', 'question_id', 'int_value')
    
    # Group answers by department
    dept_answer_sums = defaultdict(lambda: {'sum': 0, 'count': 0, 'question_id': None})
    
    for answer in answers_data:
        dept_id = answer['instance__department_id']
        dept_answer_sums[dept_id]['sum'] += answer['int_value']
        dept_answer_sums[dept_id]['count'] += 1
        if not dept_answer_sums[dept_id]['question_id']:
            dept_answer_sums[dept_id]['question_id'] = answer['question_id']
    
    logger.info(f"Calculated averages for {len(dept_answer_sums)} departments")
    
    # Build mapping of question_id to question object for faster lookup
    question_id_to_obj = {q.id: q for q in questions_by_form.values()}
    
    # Build department data
    department_data = []
    question_text = None
    
    for dept in departments:
        if dept.id not in dept_answer_sums or dept_answer_sums[dept.id]['count'] == 0:
            logger.debug(f"No answers for Q{question_order + 1} in {dept.title}")
            continue
        
        stats = dept_answer_sums[dept.id]
        avg_value = stats['sum'] / stats['count']
        question = question_id_to_obj.get(stats['question_id'])
        
        if not question_text and question:
            question_text = question.text
        
        department_data.append({
            'department': dept.title,
            'avg_value': round(avg_value, 2),
            'question_text': question.text if question else f'Question {question_order + 1}'
        })
        logger.debug(f"Department {dept.title}: avg Q{question_order + 1} = {avg_value:.2f} ({stats['count']} answers)")
    
    # Sort by department name
    department_data.sort(key=lambda x: x['department'])
    
    if not department_data:
        logger.warning(f"get_department_question_comparison Q{question_order + 1} - No data after processing")
        return {
            'labels': [],
            'data': [],
            'question_text': '',
            'chart_type': chart_type,
            'has_data': False
        }
    
    # Format data for chart
    chart_data = {
        'labels': [item['department'] for item in department_data],
        'data': [item['avg_value'] for item in department_data],
        'question_text': question_text or f'Question {question_order + 1}',
        'chart_type': chart_type,
        'has_data': True
    }
    
    logger.info(f"get_department_question_comparison Q{question_order + 1} - Returning data for {len(department_data)} departments")
    return chart_data


def get_department_customer_experience_comparison(start_date_obj=None, end_date_obj=None):
    """
    Calculate average customer satisfaction across all departments using emoji questions.
    Returns data formatted for pie chart showing department comparison.
    """
    logger.info("get_department_customer_experience_comparison - Starting calculation")
    
    # Helper function to apply date filters
    def apply_date_filters(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(week_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj)
        return queryset
    
    # Get all departments
    departments = Department.objects.all().prefetch_related('eval_forms', 'eval_forms__questions')
    
    department_data = []
    
    for dept in departments:
        logger.info(f"Processing department: {dept.title}")
        
        # Get completed evaluations for this department
        dept_evaluations = apply_date_filters(
            DynamicEvaluation.objects.filter(department=dept, status='completed')
        )
        
        eval_count = dept_evaluations.count()
        logger.info(f"Found {eval_count} completed evaluations for {dept.title}")
        
        if eval_count == 0:
            logger.warning(f"No completed evaluations for {dept.title}")
            continue
        
        # Get all forms used in these evaluations
        eval_form_ids = dept_evaluations.values_list('form_id', flat=True).distinct()
        
        # Look for emoji type questions in these forms
        emoji_question = Question.objects.filter(
            form_id__in=eval_form_ids,
            qtype='emoji'
        ).first()
        
        if not emoji_question:
            logger.warning(f"No emoji question found in completed evaluations for department {dept.title}")
            continue
        
        logger.info(f"Found emoji question in {dept.title}: {emoji_question.text}")
        
        # Calculate average rating for the emoji question from completed evaluations
        avg_rating = Answer.objects.filter(
            instance__in=dept_evaluations,
            question=emoji_question,
            int_value__isnull=False
        ).aggregate(avg=Avg('int_value'))['avg']
        
        if avg_rating:
            department_data.append({
                'department': dept.title,
                'avg_rating': round(avg_rating, 2)
            })
            logger.info(f"Department {dept.title}: avg customer satisfaction (emoji) = {avg_rating:.2f}")
        else:
            logger.warning(f"No emoji answers found for {dept.title}")
    
    # Sort by department name for consistency
    department_data.sort(key=lambda x: x['department'])
    
    # If no data found, return empty structure
    if not department_data:
        logger.warning("get_department_customer_experience_comparison - No data found for any department")
        return {
            'labels': [],
            'data': [],
            'has_data': False
        }
    
    # Format data for pie chart
    chart_data = {
        'labels': [item['department'] for item in department_data],
        'data': [item['avg_rating'] for item in department_data],
        'has_data': True
    }
    
    logger.info(f"get_department_customer_experience_comparison - Returning data for {len(department_data)} departments")
    return chart_data


def get_department_third_question_comparison(start_date_obj=None, end_date_obj=None):
    """
    Get 3rd question data from weekly evaluations across all departments.
    Returns data formatted for bar chart showing department comparison.
    """
    logger.info("get_department_third_question_comparison - Starting calculation")
    
    # Helper function to apply date filters
    def apply_date_filters(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(week_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj)
        return queryset
    
    # Get all departments
    departments = Department.objects.all().prefetch_related('eval_forms', 'eval_forms__questions')
    
    department_data = []
    question_text = None
    
    for dept in departments:
        logger.info(f"Processing 3rd question for department: {dept.title}")
        
        # Get completed evaluations for this department
        dept_evaluations = apply_date_filters(
            DynamicEvaluation.objects.filter(department=dept, status='completed')
        )
        
        eval_count = dept_evaluations.count()
        logger.info(f"Found {eval_count} completed evaluations for {dept.title}")
        
        if eval_count == 0:
            logger.warning(f"No completed evaluations for {dept.title}")
            continue
        
        # Get all forms used in these evaluations
        eval_form_ids = dept_evaluations.values_list('form_id', flat=True).distinct()
        
        # Find all questions with order=2 in these forms
        questions_order_2 = Question.objects.filter(
            form_id__in=eval_form_ids,
            order=2
        )
        
        if not questions_order_2.exists():
            logger.warning(f"No question with order=2 found in completed evaluations for department {dept.title}")
            continue
        
        # Find the most commonly used question by counting answers
        third_question = None
        max_answer_count = 0
        
        for q in questions_order_2:
            answer_count = Answer.objects.filter(
                instance__in=dept_evaluations,
                question=q,
                int_value__isnull=False
            ).count()
            if answer_count > max_answer_count:
                max_answer_count = answer_count
                third_question = q
        
        if not third_question:
            logger.warning(f"No answers found for any question with order=2 in {dept.title}")
            continue
        
        if not question_text:
            question_text = third_question.text
        
        logger.info(f"Found 3rd question in {dept.title}: {third_question.text} ({max_answer_count} answers)")
        
        # Calculate average for the 3rd question from completed evaluations
        avg_value = Answer.objects.filter(
            instance__in=dept_evaluations,
            question=third_question,
            int_value__isnull=False
        ).aggregate(avg=Avg('int_value'))['avg']
        
        if avg_value:
            department_data.append({
                'department': dept.title,
                'avg_value': round(avg_value, 2),
                'question_text': third_question.text
            })
            logger.info(f"Department {dept.title}: avg 3rd question value = {avg_value:.2f}")
        else:
            logger.warning(f"No answers found for 3rd question in {dept.title}")
    
    # Sort by department name for consistency
    department_data.sort(key=lambda x: x['department'])
    
    # If no data found, return empty structure
    if not department_data:
        logger.warning("get_department_third_question_comparison - No data found for any department")
        return {
            'labels': [],
            'data': [],
            'question_text': '',
            'has_data': False
        }
    
    # Format data for bar chart
    chart_data = {
        'labels': [item['department'] for item in department_data],
        'data': [item['avg_value'] for item in department_data],
        'question_texts': [item['question_text'] for item in department_data],
        'question_text': question_text or 'Question 3',
        'has_data': True
    }
    
    logger.info(f"get_department_third_question_comparison - Returning data for {len(department_data)} departments")
    return chart_data


def get_department_last_question_comparison(start_date_obj=None, end_date_obj=None):
    """
    Get last question (employee confidence) data from weekly evaluations across all departments.
    Returns data formatted for bar chart showing department comparison.
    """
    logger.info("get_department_last_question_comparison - Starting calculation")
    
    # Helper function to apply date filters
    def apply_date_filters(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(week_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj)
        return queryset
    
    # Get all departments
    departments = Department.objects.all().prefetch_related('eval_forms', 'eval_forms__questions')
    
    department_data = []
    question_text = None
    
    for dept in departments:
        logger.info(f"Processing last question for department: {dept.title}")
        
        # Get completed evaluations for this department
        dept_evaluations = apply_date_filters(
            DynamicEvaluation.objects.filter(department=dept, status='completed')
        )
        
        eval_count = dept_evaluations.count()
        logger.info(f"Found {eval_count} completed evaluations for {dept.title}")
        
        if eval_count == 0:
            logger.warning(f"No completed evaluations for {dept.title}")
            continue
        
        # Get all forms used in these evaluations
        eval_form_ids = dept_evaluations.values_list('form_id', flat=True).distinct()
        
        # Get the highest order number across all forms
        max_order = Question.objects.filter(
            form_id__in=eval_form_ids
        ).aggregate(max_order=Max('order'))['max_order']
        
        if max_order is None:
            logger.warning(f"No questions found in forms for department {dept.title}")
            continue
        
        # Find all questions with the highest order (last questions)
        last_questions = Question.objects.filter(
            form_id__in=eval_form_ids,
            order=max_order
        )
        
        if not last_questions.exists():
            logger.warning(f"No last question found in completed evaluations for department {dept.title}")
            continue
        
        # Find the most commonly used last question by counting answers
        last_question = None
        max_answer_count = 0
        
        for q in last_questions:
            answer_count = Answer.objects.filter(
                instance__in=dept_evaluations,
                question=q,
                int_value__isnull=False
            ).count()
            if answer_count > max_answer_count:
                max_answer_count = answer_count
                last_question = q
        
        if not last_question:
            logger.warning(f"No answers found for any last question in {dept.title}")
            continue
        
        if not question_text:
            question_text = last_question.text
        
        logger.info(f"Found last question in {dept.title}: {last_question.text} (order: {last_question.order}, {max_answer_count} answers)")
        
        # Calculate average for the last question from completed evaluations
        avg_value = Answer.objects.filter(
            instance__in=dept_evaluations,
            question=last_question,
            int_value__isnull=False
        ).aggregate(avg=Avg('int_value'))['avg']
        
        if avg_value:
            department_data.append({
                'department': dept.title,
                'avg_value': round(avg_value, 2),
                'question_text': last_question.text
            })
            logger.info(f"Department {dept.title}: avg last question value = {avg_value:.2f}")
        else:
            logger.warning(f"No answers found for last question in {dept.title}")
    
    # Sort by department name for consistency
    department_data.sort(key=lambda x: x['department'])
    
    # If no data found, return empty structure
    if not department_data:
        logger.warning("get_department_last_question_comparison - No data found for any department")
        return {
            'labels': [],
            'data': [],
            'question_text': '',
            'has_data': False
        }
    
    # Format data for bar chart
    chart_data = {
        'labels': [item['department'] for item in department_data],
        'data': [item['avg_value'] for item in department_data],
        'question_texts': [item['question_text'] for item in department_data],
        'question_text': question_text or 'Employee Confidence',
        'has_data': True
    }
    
    logger.info(f"get_department_last_question_comparison - Returning data for {len(department_data)} departments")
    return chart_data


def get_weekly_employee_data(evaluations, questions):
    """
    Get weekly data for an employee's star rating and emoji satisfaction.
    Returns data structured for bar charts showing weekly performance.
    """
    from .models import Answer
    from collections import defaultdict
    
    if not evaluations or not questions:
        return []
    
    # Get answers for these evaluations and questions
    answers = Answer.objects.filter(
        instance__in=evaluations,
        question__in=questions
    ).select_related('question', 'instance')
    
    # Group by week and question type
    weekly_data = defaultdict(lambda: {'star_rating': [], 'emoji_rating': []})
    
    for answer in answers:
        evaluation = answer.instance
        question = answer.question
        
        # Use week_start as the week identifier
        week_key = evaluation.week_start.strftime('%Y-%m-%d')
        
        if question.qtype == 'stars' and answer.int_value is not None:
            weekly_data[week_key]['star_rating'].append(answer.int_value)
        elif question.qtype == 'emoji':
            # Convert emoji to numeric value
            emoji_map = {"😞": 1, "😕": 2, "😐": 3, "😊": 4, "😍": 5}
            if answer.text_value and answer.text_value in emoji_map:
                weekly_data[week_key]['emoji_rating'].append(emoji_map[answer.text_value])
            elif answer.int_value is not None:
                weekly_data[week_key]['emoji_rating'].append(answer.int_value)
    
    # Convert to list format for charts
    chart_data = []
    for week_start, ratings in sorted(weekly_data.items()):
        week_label = week_start  # You can format this better if needed
        
        # Calculate averages
        avg_star = sum(ratings['star_rating']) / len(ratings['star_rating']) if ratings['star_rating'] else 0
        avg_emoji = sum(ratings['emoji_rating']) / len(ratings['emoji_rating']) if ratings['emoji_rating'] else 0
        
        chart_data.append({
            'week': week_label,
            'star_rating': round(avg_star, 1),
            'emoji_rating': round(avg_emoji, 1)
        })
    
    return chart_data

@login_required
@require_manager_access
def employee_performance_dashboard(request):
    """
    Manager's view of their employees' performance trends.
    Shows aggregated performance data for all employees under this manager.
    Optimized with select_related to prevent N+1 queries.
    """
    checker = get_role_checker(request.user)
    user_profile = checker.user_profile
    
    logger.info(f"Employee performance dashboard accessed by manager {request.user.id} ({user_profile.user.get_full_name()})")
    
    today = timezone.now().date()
    
    # Parse date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid start_date format: {start_date}")
            start_date = None
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}")
            end_date = None
    
    if start_date_obj or end_date_obj:
        logger.info(f"Date filters applied: {start_date_obj} to {end_date_obj}")
    
    # Helper function to apply date filters (DRY principle)
    def apply_eval_date_filter(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(week_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj)
        return queryset
    
    # Optimized: Get employees with select_related to prevent N+1
    managed_employees = UserProfile.objects.filter(
        manager=user_profile,
        is_employee=True
    ).select_related('user', 'department')
    
    managed_count = managed_employees.count()
    logger.info(f"Manager {user_profile.user.get_full_name()} has {managed_count} team members")
    
    department_members = UserProfile.objects.none()
    if hasattr(user_profile, 'managed_department') and user_profile.managed_department:
        department_members = UserProfile.objects.filter(
            department=user_profile.managed_department,
            is_employee=True
        ).select_related('user', 'department', 'manager__user')
        dept_count = department_members.count()
        logger.info(f"Manager's department has {dept_count} employees")
    
    # Optimized: Get evaluations with select_related
    employee_evaluations = apply_eval_date_filter(
        DynamicEvaluation.objects.filter(
            employee__in=managed_employees,
            status='completed'
        ).select_related('form', 'employee__user', 'manager__user', 'department')
    )
    
    # Get simple employee performance data for bar chart
    employee_performance_data = {}
    performance_data = {}
    
    if managed_employees.exists():
        # Optimized: Get all completed evaluations with date filter
        all_evaluations = apply_eval_date_filter(
            DynamicEvaluation.objects.filter(
                employee__in=managed_employees,
                status='completed'
            ).select_related('employee__user', 'form', 'department')
        )
        
        eval_count = all_evaluations.count()
        logger.info(f"Processing {eval_count} evaluations for team performance data")
        
        if all_evaluations.exists():
            # Get questions from the most recent form
            most_recent_evaluation = all_evaluations.order_by('-week_start').first()
            if most_recent_evaluation:
                eval_form = most_recent_evaluation.form
                questions = Question.objects.filter(
                    form=eval_form,
                    include_in_trends=True
                ).order_by('order')
                
                
                # Find star rating and emoji questions
                star_questions = questions.filter(qtype='stars')
                emoji_question = questions.filter(qtype='emoji').first()
                
                
                # Process each employee
                for employee in managed_employees:
                    emp_evaluations = all_evaluations.filter(employee=employee).order_by('week_start')
                    if emp_evaluations.exists():
                        
                        # Get questions from this employee's form (not the most recent form overall)
                        emp_most_recent = emp_evaluations.first()
                        emp_form = emp_most_recent.form
                        emp_questions = Question.objects.filter(
                            form=emp_form,
                            include_in_trends=True
                        ).order_by('order')
                        
                        # If no questions are marked for trends, use all questions from this employee's form
                        if not emp_questions.exists():
                            emp_questions = Question.objects.filter(form=emp_form).order_by('order')
                        
                        # Find star rating and emoji questions for this employee
                        emp_star_questions = emp_questions.filter(qtype='stars')
                        emp_emoji_question = emp_questions.filter(qtype='emoji').first()
                        
                        
                        # Get weekly data for the last 8 weeks
                        weekly_data = []
                        weeks = []
                        
                        # Get evaluations from the last 8 weeks
                        recent_evaluations = emp_evaluations[:8]
                        
                        for evaluation in recent_evaluations:
                            week_label = evaluation.week_start.strftime('%m/%d')
                            weeks.append(week_label)
                            
                            # Get star rating for this week (average of all star questions for this employee)
                            star_rating = 0
                            if emp_star_questions.exists():
                                star_answers = Answer.objects.filter(
                                    instance=evaluation,
                                    question__in=emp_star_questions,
                                    int_value__isnull=False
                                ).values_list('int_value', flat=True)
                                
                                if star_answers:
                                    star_rating = sum(star_answers) / len(star_answers)
                            
                            # Get emoji rating for this week
                            emoji_rating = 0
                            if emp_emoji_question:
                                emoji_answer = Answer.objects.filter(
                                    instance=evaluation,
                                    question=emp_emoji_question
                                ).first()
                                if emoji_answer:
                                    if emoji_answer.text_value:
                                        emoji_map = {"😞": 1, "😕": 2, "😐": 3, "😊": 4, "😍": 5}
                                        emoji_rating = emoji_map.get(emoji_answer.text_value, 0)
                                    elif emoji_answer.int_value is not None:
                                        emoji_rating = emoji_answer.int_value
                            
                            weekly_data.append({
                                'week': week_label,
                                'star_rating': star_rating,
                                'emoji_rating': emoji_rating
                            })
                        
                        # Calculate averages for summary
                        star_ratings = [week['star_rating'] for week in weekly_data if week['star_rating'] > 0]
                        emoji_ratings = [week['emoji_rating'] for week in weekly_data if week['emoji_rating'] > 0]
                        
                        avg_star_rating = sum(star_ratings) / len(star_ratings) if star_ratings else 0
                        avg_emoji_rating = sum(emoji_ratings) / len(emoji_ratings) if emoji_ratings else 0
                        
                        # Store employee data (serializable format)
                        employee_performance_data[employee.id] = {
                            'employee': {
                                'id': employee.id,
                                'name': employee.user.get_full_name() or employee.user.username,
                                'email': employee.user.email,
                                'department': employee.department.title if employee.department else 'No Department'
                            },
                            'avg_star_rating': round(avg_star_rating, 1),
                            'avg_emoji_rating': round(avg_emoji_rating, 1),
                            'total_evaluations': emp_evaluations.count(),
                            'weekly_data': weekly_data,
                            'weeks': weeks
                        }
                        
                
                # Calculate overall team performance by month
                team_monthly_data = {}
                
                # Get all evaluations for managed employees, ordered by week_start
                all_team_evaluations = all_evaluations.order_by('week_start')
                
                for evaluation in all_team_evaluations:
                    # Get month-year key
                    month_key = evaluation.week_start.strftime('%Y-%m')
                    
                    if month_key not in team_monthly_data:
                        team_monthly_data[month_key] = {
                            'month_label': evaluation.week_start.strftime('%b %Y'),
                            'star_ratings': [],
                            'emoji_ratings': [],
                            'evaluation_count': 0
                        }
                    
                    # Get star rating for this evaluation (average of all star questions)
                    star_rating = 0
                    if star_questions.exists():
                        star_answers = Answer.objects.filter(
                            instance=evaluation,
                            question__in=star_questions,
                            int_value__isnull=False
            ).values_list('int_value', flat=True)
            
                        if star_answers:
                            star_rating = sum(star_answers) / len(star_answers)
                    
                    # Get emoji rating for this evaluation
                    emoji_rating = 0
                    if emoji_question:
                        emoji_answer = Answer.objects.filter(
                            instance=evaluation,
                            question=emoji_question
                        ).first()
                        if emoji_answer:
                            if emoji_answer.text_value:
                                emoji_map = {"😞": 1, "😕": 2, "😐": 3, "😊": 4, "😍": 5}
                                emoji_rating = emoji_map.get(emoji_answer.text_value, 0)
                            elif emoji_answer.int_value is not None:
                                emoji_rating = emoji_answer.int_value
                    
                    # Add to monthly data
                    if star_rating > 0:
                        team_monthly_data[month_key]['star_ratings'].append(star_rating)
                    if emoji_rating > 0:
                        team_monthly_data[month_key]['emoji_ratings'].append(emoji_rating)
                    team_monthly_data[month_key]['evaluation_count'] += 1
                
                # Calculate monthly averages
                monthly_performance = []
                months = []
                for month_key in sorted(team_monthly_data.keys()):
                    month_data = team_monthly_data[month_key]
                    months.append(month_data['month_label'])
                    
                    # Calculate averages
                    avg_star = sum(month_data['star_ratings']) / len(month_data['star_ratings']) if month_data['star_ratings'] else 0
                    avg_emoji = sum(month_data['emoji_ratings']) / len(month_data['emoji_ratings']) if month_data['emoji_ratings'] else 0
                    
                    monthly_performance.append({
                        'month': month_data['month_label'],
                        'avg_star_rating': round(avg_star, 1),
                        'avg_emoji_rating': round(avg_emoji, 1),
                        'evaluation_count': month_data['evaluation_count']
                    })
                
                # Process department employee performance data
                department_performance_data = {}
                department_monthly_performance = []
                department_months = []
                
                # Get all completed evaluations for department members
                if department_members.exists():
                    # Optimized: Use helper function for date filtering
                    department_evaluations = apply_eval_date_filter(
                        DynamicEvaluation.objects.filter(
                            employee__in=department_members,
                            status='completed'
                        ).select_related('employee__user', 'form', 'department')
                    )
                    
                    dept_eval_count = department_evaluations.count()
                    logger.info(f"Processing {dept_eval_count} department evaluations")
                    
                    if department_evaluations.exists():
                        # Process each department employee
                        for dept_employee in department_members:
                            dept_emp_evaluations = department_evaluations.filter(employee=dept_employee).order_by('week_start')
                            if dept_emp_evaluations.exists():
                                # Get questions from this department employee's form
                                dept_emp_most_recent = dept_emp_evaluations.first()
                                dept_emp_form = dept_emp_most_recent.form
                                dept_emp_questions = Question.objects.filter(
                                    form=dept_emp_form,
                                    include_in_trends=True
                                ).order_by('order')
                                
                                # If no questions are marked for trends, use all questions from this employee's form
                                if not dept_emp_questions.exists():
                                    dept_emp_questions = Question.objects.filter(form=dept_emp_form).order_by('order')
                                
                                # Find star rating and emoji questions for this department employee
                                dept_emp_star_questions = dept_emp_questions.filter(qtype='stars')
                                dept_emp_emoji_question = dept_emp_questions.filter(qtype='emoji').first()
                                
                                # Get weekly data for the last 8 weeks
                                dept_weekly_data = []
                                dept_weeks = []
                                
                                # Get evaluations from the last 8 weeks
                                dept_recent_evaluations = dept_emp_evaluations[:8]
                                
                                for dept_evaluation in dept_recent_evaluations:
                                    dept_week_label = dept_evaluation.week_start.strftime('%m/%d')
                                    dept_weeks.append(dept_week_label)
                                    
                                    # Get star rating for this week (average of all star questions for this department employee)
                                    dept_star_rating = 0
                                    if dept_emp_star_questions.exists():
                                        dept_star_answers = Answer.objects.filter(
                                            instance=dept_evaluation,
                                            question__in=dept_emp_star_questions,
                                            int_value__isnull=False
                                        ).values_list('int_value', flat=True)
                                        
                                        if dept_star_answers:
                                            dept_star_rating = sum(dept_star_answers) / len(dept_star_answers)
                                    
                                    # Get emoji rating for this week
                                    dept_emoji_rating = 0
                                    if dept_emp_emoji_question:
                                        dept_emoji_answer = Answer.objects.filter(
                                            instance=dept_evaluation,
                                            question=dept_emp_emoji_question
                                        ).first()
                                        if dept_emoji_answer:
                                            if dept_emoji_answer.text_value:
                                                dept_emoji_map = {"😞": 1, "😕": 2, "😐": 3, "😊": 4, "😍": 5}
                                                dept_emoji_rating = dept_emoji_map.get(dept_emoji_answer.text_value, 0)
                                            elif dept_emoji_answer.int_value is not None:
                                                dept_emoji_rating = dept_emoji_answer.int_value
                                    
                                    dept_weekly_data.append({
                                        'week': dept_week_label,
                                        'star_rating': dept_star_rating,
                                        'emoji_rating': dept_emoji_rating
                                    })
                                
                                # Calculate averages for summary
                                dept_star_ratings = [week['star_rating'] for week in dept_weekly_data if week['star_rating'] > 0]
                                dept_emoji_ratings = [week['emoji_rating'] for week in dept_weekly_data if week['emoji_rating'] > 0]
                                
                                dept_avg_star_rating = sum(dept_star_ratings) / len(dept_star_ratings) if dept_star_ratings else 0
                                dept_avg_emoji_rating = sum(dept_emoji_ratings) / len(dept_emoji_ratings) if dept_emoji_ratings else 0
                                
                                # Store department employee data
                                department_performance_data[dept_employee.id] = {
                                    'employee': {
                                        'id': dept_employee.id,
                                        'name': dept_employee.user.get_full_name() or dept_employee.user.username,
                                        'email': dept_employee.user.email,
                                        'department': dept_employee.department.title if dept_employee.department else 'No Department',
                                        'manager': dept_employee.manager.user.get_full_name() if dept_employee.manager else 'No Manager'
                                    },
                                    'avg_star_rating': round(dept_avg_star_rating, 1),
                                    'avg_emoji_rating': round(dept_avg_emoji_rating, 1),
                                    'total_evaluations': dept_emp_evaluations.count(),
                                    'weekly_data': dept_weekly_data,
                                    'weeks': dept_weeks
                                }
                        
                        # Calculate overall department performance by month
                        dept_team_monthly_data = {}
                        
                        # Get all evaluations for department members, ordered by week_start
                        all_dept_team_evaluations = department_evaluations.order_by('week_start')
                        
                        for dept_evaluation in all_dept_team_evaluations:
                            # Get month-year key
                            dept_month_key = dept_evaluation.week_start.strftime('%Y-%m')
                            
                            if dept_month_key not in dept_team_monthly_data:
                                dept_team_monthly_data[dept_month_key] = {
                                    'month_label': dept_evaluation.week_start.strftime('%b %Y'),
                                    'star_ratings': [],
                                    'emoji_ratings': [],
                                    'evaluation_count': 0
                                }
                            
                            # Get questions from this evaluation's form
                            dept_eval_form = dept_evaluation.form
                            dept_eval_questions = Question.objects.filter(
                                form=dept_eval_form,
                                include_in_trends=True
                            ).order_by('order')
                            
                            if not dept_eval_questions.exists():
                                dept_eval_questions = Question.objects.filter(form=dept_eval_form).order_by('order')
                            
                            dept_eval_star_questions = dept_eval_questions.filter(qtype='stars')
                            dept_eval_emoji_question = dept_eval_questions.filter(qtype='emoji').first()
                            
                            # Get star rating for this evaluation (average of all star questions)
                            dept_star_rating = 0
                            if dept_eval_star_questions.exists():
                                dept_star_answers = Answer.objects.filter(
                                    instance=dept_evaluation,
                                    question__in=dept_eval_star_questions,
                                    int_value__isnull=False
                                ).values_list('int_value', flat=True)
                                
                                if dept_star_answers:
                                    dept_star_rating = sum(dept_star_answers) / len(dept_star_answers)
                            
                            # Get emoji rating for this evaluation
                            dept_emoji_rating = 0
                            if dept_eval_emoji_question:
                                dept_emoji_answer = Answer.objects.filter(
                                    instance=dept_evaluation,
                                    question=dept_eval_emoji_question
                                ).first()
                                if dept_emoji_answer:
                                    if dept_emoji_answer.text_value:
                                        dept_emoji_map = {"😞": 1, "😕": 2, "😐": 3, "😊": 4, "😍": 5}
                                        dept_emoji_rating = dept_emoji_map.get(dept_emoji_answer.text_value, 0)
                                    elif dept_emoji_answer.int_value is not None:
                                        dept_emoji_rating = dept_emoji_answer.int_value
                            
                            # Add to monthly data
                            if dept_star_rating > 0:
                                dept_team_monthly_data[dept_month_key]['star_ratings'].append(dept_star_rating)
                            if dept_emoji_rating > 0:
                                dept_team_monthly_data[dept_month_key]['emoji_ratings'].append(dept_emoji_rating)
                            dept_team_monthly_data[dept_month_key]['evaluation_count'] += 1
                        
                        # Calculate monthly averages for department
                        for dept_month_key in sorted(dept_team_monthly_data.keys()):
                            dept_month_data = dept_team_monthly_data[dept_month_key]
                            department_months.append(dept_month_data['month_label'])
                            
                            # Calculate averages
                            dept_avg_star = sum(dept_month_data['star_ratings']) / len(dept_month_data['star_ratings']) if dept_month_data['star_ratings'] else 0
                            dept_avg_emoji = sum(dept_month_data['emoji_ratings']) / len(dept_month_data['emoji_ratings']) if dept_month_data['emoji_ratings'] else 0
                            
                            department_monthly_performance.append({
                                'month': dept_month_data['month_label'],
                                'avg_star_rating': round(dept_avg_star, 1),
                                'avg_emoji_rating': round(dept_avg_emoji, 1),
                                'evaluation_count': dept_month_data['evaluation_count']
                            })

                performance_data = {
                    'employee_data': employee_performance_data,
                    'star_question_text': 'Star Rating (Average)' if star_questions.exists() else 'Star Rating',
                    'emoji_question_text': emoji_question.text if emoji_question else 'Satisfaction Rating',
                    'monthly_performance': monthly_performance,
                    'months': months,
                    'department_employee_data': department_performance_data,
                    'department_monthly_performance': department_monthly_performance,
                    'department_months': department_months
                }
                
                logger.info(f"Performance data compiled for {len(employee_performance_data)} employees")
    
    context = {
        'user_profile': user_profile,
        'managed_employees': managed_employees,
        'department_members': department_members,
        'today': today,
        'last_viewed_at': timezone.now(),
        'performance_data': performance_data,
        'dashboard_type': 'employee_performance',
        'start_date': start_date,
        'end_date': end_date
    }
    
    logger.info(f"Employee performance dashboard rendered successfully for manager {user_profile.user.get_full_name()}")
    return render(request, "evaluation/employee_performance_dashboard.html", context)


@login_required
@require_manager_access
def manager_employee_dashboard(request):
    """
    Employee dashboard for managers showing all their employees team-wise and department-wise,
    with evaluation statistics and status indicators (similar to senior managers dashboard).
    Optimized with select_related to prevent N+1 queries.
    """
    checker = get_role_checker(request.user)
    user_profile = checker.user_profile
    
    logger.info(f"Manager employee dashboard accessed by {request.user.id} ({user_profile.user.get_full_name()})")
    
    today = timezone.now()
    today_date = today.date()
    
    # Parse date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid start_date format: {start_date}")
            start_date = None
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}")
            end_date = None
    
    if start_date_obj or end_date_obj:
        logger.info(f"Date filters applied: {start_date_obj} to {end_date_obj}")
    
    # Helper function to apply date filters (DRY principle)
    def apply_mgr_eval_date_filter(queryset):
        if start_date_obj and end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj, week_end__gte=start_date_obj)
        elif start_date_obj:
            return queryset.filter(week_end__gte=start_date_obj)
        elif end_date_obj:
            return queryset.filter(week_start__lte=end_date_obj)
        return queryset
    
    # Optimized: Get team members with select_related
    team_members = UserProfile.objects.filter(
        manager=user_profile
    ).select_related('user', 'department', 'managed_department')
    
    team_count = team_members.count()
    logger.info(f"Manager has {team_count} team members")
    
    department_employees = UserProfile.objects.none()
    if hasattr(user_profile, 'managed_department') and user_profile.managed_department:
        department_employees = UserProfile.objects.filter(
            department=user_profile.managed_department
        ).exclude(
            id=user_profile.id
        ).select_related('user', 'manager', 'managed_department')
        dept_emp_count = department_employees.count()
        logger.info(f"Manager's department has {dept_emp_count} employees")
    
    # Optimized: Get all evaluations with date filter
    all_evaluations = apply_mgr_eval_date_filter(
        DynamicEvaluation.objects.filter(
            manager=user_profile
        ).select_related('employee__user', 'form', 'department').order_by('-week_start')
    )
    
    # Calculate evaluation stats efficiently
    total_evaluations = all_evaluations.count()
    completed_evaluations = all_evaluations.filter(status=EvaluationStatus.COMPLETED).count()
    pending_evaluations = all_evaluations.filter(status=EvaluationStatus.PENDING).count()
    overdue_evaluations = all_evaluations.filter(
        status=EvaluationStatus.PENDING,
        week_end__lt=today_date
    ).count()
    
    logger.info(f"Evaluation stats - Total: {total_evaluations}, Completed: {completed_evaluations}, Pending: {pending_evaluations}, Overdue: {overdue_evaluations}")
    
    # Recent activity (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_evaluations = all_evaluations.filter(week_start__gte=thirty_days_ago).count()
    
    completion_rate = round((completed_evaluations / total_evaluations * 100) if total_evaluations > 0 else 0, 1)
    logger.info(f"Overall completion rate: {completion_rate}%")
    
    # Team member statistics
    team_data = []
    for member in team_members:
        # Get evaluations for this team member
        member_evals = all_evaluations.filter(employee=member)
        member_total = member_evals.count()
        member_completed = member_evals.filter(status=EvaluationStatus.COMPLETED).count()
        member_pending = member_evals.filter(status=EvaluationStatus.PENDING).count()
        member_overdue = member_evals.filter(
            status=EvaluationStatus.PENDING,
            week_end__lt=today_date
        ).count()
        
        # Calculate completion rate
        member_completion_rate = round((member_completed / member_total * 100) if member_total > 0 else 0, 1)
        
        # Determine status
        if member_total == 0:
            member_status = 'awaiting'
        elif member_overdue > 0:
            member_status = 'critical'
        elif member_pending > member_completed:
            member_status = 'needs_attention'
        elif member_completion_rate >= 80:
            member_status = 'on_track'
        else:
            member_status = 'needs_attention'
        
        team_data.append({
            'employee': member,
            'stats': {
                'total': member_total,
                'completed': member_completed,
                'pending': member_pending,
                'overdue': member_overdue
            },
            'completion_rate': member_completion_rate,
            'status': member_status
        })
    
    # Department employee statistics
    department_data = []
    for member in department_employees:
        # Get evaluations for this department member
        dept_member_evals = all_evaluations.filter(employee=member)
        dept_member_total = dept_member_evals.count()
        dept_member_completed = dept_member_evals.filter(status=EvaluationStatus.COMPLETED).count()
        dept_member_pending = dept_member_evals.filter(status=EvaluationStatus.PENDING).count()
        dept_member_overdue = dept_member_evals.filter(
            status=EvaluationStatus.PENDING,
            week_end__lt=today_date
        ).count()
        
        # Calculate completion rate
        dept_member_completion_rate = round((dept_member_completed / dept_member_total * 100) if dept_member_total > 0 else 0, 1)
        
        # Determine status
        if dept_member_total == 0:
            dept_member_status = 'awaiting'
        elif dept_member_overdue > 0:
            dept_member_status = 'critical'
        elif dept_member_pending > dept_member_completed:
            dept_member_status = 'needs_attention'
        elif dept_member_completion_rate >= 80:
            dept_member_status = 'on_track'
        else:
            dept_member_status = 'needs_attention'
        
        department_data.append({
            'employee': member,
            'stats': {
                'total': dept_member_total,
                'completed': dept_member_completed,
                'pending': dept_member_pending,
                'overdue': dept_member_overdue
            },
            'completion_rate': dept_member_completion_rate,
            'status': dept_member_status
        })
    
    # Overall team status - calculate based on total completed / total evaluations
    team_total_count = sum([td['stats']['total'] for td in team_data])
    team_completed_count = sum([td['stats']['completed'] for td in team_data])
    team_overdue_count = sum([td['stats']['overdue'] for td in team_data])
    team_pending_count = sum([td['stats']['pending'] for td in team_data])
    
    team_completion_rate = round(
        (team_completed_count / team_total_count * 100) if team_total_count > 0 else 0, 
        1
    )
    
    # Status logic: overdue → critical, pending → needs_attention, all complete → on_track, no evals → awaiting
    if team_total_count == 0:
        overall_team_status = 'awaiting'
    elif team_overdue_count > 0:
        overall_team_status = 'critical'
    elif team_pending_count > 0:
        overall_team_status = 'needs_attention'
    else:
        overall_team_status = 'on_track'
    
    # Department overview statistics
    department_stats = None
    if hasattr(user_profile, 'managed_department') and user_profile.managed_department:
        dept = user_profile.managed_department
        dept_total_employees = department_employees.count()
        
        # Calculate department-level evaluation stats
        dept_evaluations = all_evaluations.filter(department=dept)
        dept_total_evals = dept_evaluations.count()
        dept_completed_evals = dept_evaluations.filter(status=EvaluationStatus.COMPLETED).count()
        dept_pending_evals = dept_evaluations.filter(status=EvaluationStatus.PENDING).count()
        dept_overdue_evals = dept_evaluations.filter(
            status=EvaluationStatus.PENDING,
            week_end__lt=today_date
        ).count()
        
        # Calculate department completion rate
        dept_completion_rate = round((dept_completed_evals / dept_total_evals * 100) if dept_total_evals > 0 else 0, 1)
        
        # Determine department status: overdue → critical, pending → needs_attention, all complete → on_track, no evals → awaiting
        if dept_total_evals == 0:
            dept_status = 'awaiting'
        elif dept_overdue_evals > 0:
            dept_status = 'critical'
        elif dept_pending_evals > 0:
            dept_status = 'needs_attention'
        else:
            dept_status = 'on_track'
        
        department_stats = {
            'department': dept,
            'total_employees': dept_total_employees,
            'total_evaluations': dept_total_evals,
            'completed': dept_completed_evals,
            'pending': dept_pending_evals,
            'overdue': dept_overdue_evals,
            'completion_rate': dept_completion_rate,
            'status': dept_status
        }
    
    logger.info(f"Processed {len(team_data)} team members and {len(department_data)} department employees")
    
    context = {
        'user_profile': user_profile,
        'team_members': team_data,
        'department_employees': department_data,
        'today': today_date,
        'last_viewed_at': today,
        'stats': {
            'total': total_evaluations,
            'completed': completed_evaluations,
            'pending': pending_evaluations,
            'overdue': overdue_evaluations,
            'recent': recent_evaluations,
            'completion_rate': completion_rate
        },
        'team_stats': {
            'size': len(team_data),
            'completion_rate': team_completion_rate,
            'status': overall_team_status
        },
        'department_stats': department_stats,
        'recent_evaluations': all_evaluations[:10],
        'start_date': start_date,
        'end_date': end_date
    }
    
    logger.info(f"Manager employee dashboard rendered successfully for {user_profile.user.get_full_name()}")
    return render(request, "evaluation/manager_employee_dashboard.html", context)


@login_required
@require_senior_management_access
def report_generation(request):
    """Report generation page for senior managers."""
    user_profile = get_user_profile_safely(request.user)
    
    # Get all departments for filtering
    departments = Department.objects.all().order_by('title')
    
    # Get date range options
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)
    last_6_months = today - relativedelta(months=6)
    last_year = today - relativedelta(years=1)
    
    # Get recent reports
    recent_reports = ReportHistory.objects.select_related('generated_by', 'department')[:10]
    
    context = {
        'user_profile': user_profile,
        'departments': departments,
        'date_ranges': {
            'last_30_days': last_30_days,
            'last_90_days': last_90_days,
            'last_6_months': last_6_months,
            'last_year': last_year,
            'today': today,
        },
        'recent_reports': recent_reports,
    }
    
    return render(request, "evaluation/report_generation.html", context)


@login_required
@require_senior_management_access
def generate_employee_report_pdf(request):
    """Generate PDF report for employee evaluations."""
    user_profile = get_user_profile_safely(request.user)
    
    # Get parameters
    department_id = request.GET.get('department', 'all')
    date_range = request.GET.get('date_range', '30')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    # Parse date range
    start_date, end_date = parse_date_range(date_range, start_date_str, end_date_str)
    
    # Get department name and object (avoid duplicate query)
    dept_name, dept_obj = get_department_info(department_id)
    
    logger.info(f"Generating employee report: dept={dept_name}, dates={start_date} to {end_date}, user={user_profile.user.get_full_name()}")
    
    # Build query with optimized select_related (avoid N+1 queries)
    evaluations = DynamicEvaluation.objects.filter(
        submitted_at__gte=start_date,
        submitted_at__lte=end_date
    ).select_related('employee__user', 'manager__user', 'department', 'form')
    
    if department_id != 'all':
        evaluations = evaluations.filter(department_id=department_id)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    elements = []
    styles, title_style, heading_style = get_pdf_styles()
    
    elements.append(Paragraph("Employee Evaluation Report", title_style))
    elements.append(Paragraph(f"Department: {dept_name}", styles['Normal']))
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Summary Statistics
    total_evals = evaluations.count()
    completed_evals = evaluations.filter(status=EvaluationStatus.COMPLETED).count()
    pending_evals = evaluations.filter(status=EvaluationStatus.PENDING).count()
    
    elements.append(Paragraph("Executive Summary", heading_style))
    
    summary_data = [
        ['Metric', 'Count'],
        ['Total Evaluations', str(total_evals)],
        ['Completed Evaluations', str(completed_evals)],
        ['Pending Evaluations', str(pending_evals)],
        ['Completion Rate', f'{(completed_evals/total_evals*100):.1f}%' if total_evals > 0 else 'N/A'],
    ]
    
    summary_table = create_summary_table(summary_data, [3*inch, 2*inch])
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Detailed Evaluations
    if total_evals > 0:
        elements.append(Paragraph("Evaluation Details", heading_style))
        
        # Add department column header when showing all departments
        if department_id == 'all':
            eval_data = [['Employee', 'Department', 'Manager', 'Week', 'Status', 'Submitted']]
        else:
            eval_data = [['Employee', 'Manager', 'Week', 'Status', 'Submitted']]
        
        for eval in evaluations[:100]:  # Increased to 100 for better coverage
            if department_id == 'all':
                eval_data.append([
                    eval.employee.user.get_full_name(),
                    eval.department.title,
                    eval.manager.user.get_full_name(),
                    f"{eval.week_start} to {eval.week_end}",
                    eval.status,
                    eval.submitted_at.strftime('%Y-%m-%d') if eval.submitted_at else 'N/A'
                ])
            else:
                eval_data.append([
                    eval.employee.user.get_full_name(),
                    eval.manager.user.get_full_name(),
                    f"{eval.week_start} to {eval.week_end}",
                    eval.status,
                    eval.submitted_at.strftime('%Y-%m-%d') if eval.submitted_at else 'N/A'
                ])
        
        # Adjust column widths based on whether department is shown
        if department_id == 'all':
            eval_table = Table(eval_data, colWidths=[1.3*inch, 1.2*inch, 1.3*inch, 1.3*inch, 0.8*inch, 0.8*inch])
        else:
            eval_table = Table(eval_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch, 1*inch])
        
        eval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#DC2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#D1D5DB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor('#F3F4F6')])
        ]))
        
        elements.append(eval_table)
        
        if total_evals > 100:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"Note: Showing first 100 of {total_evals} evaluations", styles['Italic']))
    else:
        elements.append(Paragraph("No evaluations found for the selected period.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Save report history
    save_report_history('employee', user_profile, dept_obj, start_date, end_date)
    
    # Return response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="employee_report_{start_date}_{end_date}.pdf"'
    
    return response


@login_required
@require_senior_management_access
def generate_manager_report_pdf(request):
    """Generate PDF report for manager evaluations."""
    user_profile = get_user_profile_safely(request.user)
    
    # Get parameters
    department_id = request.GET.get('department', 'all')
    date_range = request.GET.get('date_range', '30')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    # Parse date range
    start_date, end_date = parse_date_range(date_range, start_date_str, end_date_str)
    
    # Get department name and object
    dept_name, dept_obj = get_department_info(department_id)
    
    logger.info(f"Generating manager report: dept={dept_name}, dates={start_date} to {end_date}, user={user_profile.user.get_full_name()}")
    
    # Build query with optimized select_related (avoid N+1 queries)
    evaluations = DynamicManagerEvaluation.objects.filter(
        submitted_at__gte=start_date,
        submitted_at__lte=end_date
    ).select_related('manager__user', 'senior_manager__user', 'department', 'form')
    
    if department_id != 'all':
        evaluations = evaluations.filter(department_id=department_id)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    elements = []
    styles, title_style, heading_style = get_pdf_styles()
    
    elements.append(Paragraph("Manager Evaluation Report", title_style))
    elements.append(Paragraph(f"Department: {dept_name}", styles['Normal']))
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Summary Statistics
    total_evals = evaluations.count()
    completed_evals = evaluations.filter(status=EvaluationStatus.COMPLETED).count()
    pending_evals = evaluations.filter(status=EvaluationStatus.PENDING).count()
    
    elements.append(Paragraph("Executive Summary", heading_style))
    
    summary_data = [
        ['Metric', 'Count'],
        ['Total Evaluations', str(total_evals)],
        ['Completed Evaluations', str(completed_evals)],
        ['Pending Evaluations', str(pending_evals)],
        ['Completion Rate', f'{(completed_evals/total_evals*100):.1f}%' if total_evals > 0 else 'N/A'],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.HexColor('#F3F4F6')),
        ('GRID', (0, 0), (-1, -1), 1, pdf_colors.HexColor('#D1D5DB'))
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Detailed Evaluations
    if total_evals > 0:
        elements.append(Paragraph("Evaluation Details", heading_style))
        
        # Add department column header when showing all departments
        if department_id == 'all':
            eval_data = [['Manager', 'Department', 'Evaluator', 'Period', 'Status', 'Submitted']]
        else:
            eval_data = [['Manager', 'Evaluator', 'Period', 'Status', 'Submitted']]
        
        for eval in evaluations[:100]:  # Increased to 100 for better coverage
            if department_id == 'all':
                eval_data.append([
                    eval.manager.user.get_full_name(),
                    eval.department.title,
                    eval.senior_manager.user.get_full_name(),
                    f"{eval.period_start} to {eval.period_end}",
                    eval.status,
                    eval.submitted_at.strftime('%Y-%m-%d') if eval.submitted_at else 'N/A'
                ])
            else:
                eval_data.append([
                    eval.manager.user.get_full_name(),
                    eval.senior_manager.user.get_full_name(),
                    f"{eval.period_start} to {eval.period_end}",
                    eval.status,
                    eval.submitted_at.strftime('%Y-%m-%d') if eval.submitted_at else 'N/A'
                ])
        
        # Adjust column widths based on whether department is shown
        if department_id == 'all':
            eval_table = Table(eval_data, colWidths=[1.3*inch, 1.2*inch, 1.3*inch, 1.3*inch, 0.8*inch, 0.8*inch])
        else:
            eval_table = Table(eval_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch, 1*inch])
        
        eval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#DC2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#D1D5DB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor('#F3F4F6')])
        ]))
        
        elements.append(eval_table)
        
        if total_evals > 100:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"Note: Showing first 100 of {total_evals} evaluations", styles['Italic']))
    else:
        elements.append(Paragraph("No evaluations found for the selected period.", styles['Normal']))
    
    doc.build(elements)
    
    # Save report history
    save_report_history('manager', user_profile, dept_obj, start_date, end_date)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="manager_report_{start_date}_{end_date}.pdf"'
    
    return response


@login_required
@require_senior_management_access
def generate_trends_report_pdf(request):
    """Generate PDF report for performance trends."""
    user_profile = get_user_profile_safely(request.user)
    
    # Get parameters
    department_id = request.GET.get('department', 'all')
    period = int(request.GET.get('period', '90'))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period)
    
    # Get department name and object
    dept_name, dept_obj = get_department_info(department_id)
    
    logger.info(f"Generating trends report: dept={dept_name}, period={period} days, user={user_profile.user.get_full_name()}")
    
    # Get EMPLOYEE evaluations with answers (optimized to avoid N+1 queries)
    employee_evaluations = DynamicEvaluation.objects.filter(
        status=EvaluationStatus.COMPLETED,
        submitted_at__gte=start_date,
        submitted_at__lte=end_date
    ).select_related('employee__user', 'department', 'manager__user').prefetch_related(
        'answers__question__form'  # Prefetch question.form to avoid N+1 when accessing answer.question.form.name
    )
    
    # Get MANAGER evaluations with answers (optimized to avoid N+1 queries)
    manager_evaluations = DynamicManagerEvaluation.objects.filter(
        status=EvaluationStatus.COMPLETED,
        submitted_at__gte=start_date,
        submitted_at__lte=end_date
    ).select_related('manager__user', 'department', 'senior_manager__user').prefetch_related(
        'answers__question__form'  # Prefetch question.form to avoid N+1 when accessing answer.question.form.name
    )
    
    if department_id != 'all':
        employee_evaluations = employee_evaluations.filter(department_id=department_id)
        manager_evaluations = manager_evaluations.filter(department_id=department_id)
    
    logger.info(f"Fetched {employee_evaluations.count()} employee evals, {manager_evaluations.count()} manager evals")
    
    # Get questions marked for trends (include_in_trends=True)
    trend_questions = Question.objects.filter(include_in_trends=True).select_related('form')
    
    # Calculate performance by question for EMPLOYEES
    employee_question_performance = {}
    for question in trend_questions:
        question_key = f"{question.form.name} - {question.text}"
        employee_question_performance[question_key] = {
            'question': question,
            'responses': [],
            'response_count': 0
        }
    
    for eval in employee_evaluations:
        for answer in eval.answers.all():
            if answer.question.include_in_trends:
                question_key = f"{answer.question.form.name} - {answer.question.text}"
                if question_key in employee_question_performance:
                    if answer.int_value is not None:
                        employee_question_performance[question_key]['responses'].append(answer.int_value)
                        employee_question_performance[question_key]['response_count'] += 1
    
    # Calculate performance by question for MANAGERS
    manager_question_performance = {}
    for question in trend_questions:
        question_key = f"{question.form.name} - {question.text}"
        manager_question_performance[question_key] = {
            'question': question,
            'responses': [],
            'response_count': 0
        }
    
    for eval in manager_evaluations:
        for answer in eval.answers.all():
            if answer.question.include_in_trends:
                question_key = f"{answer.question.form.name} - {answer.question.text}"
                if question_key in manager_question_performance:
                    if answer.int_value is not None:
                        manager_question_performance[question_key]['responses'].append(answer.int_value)
                        manager_question_performance[question_key]['response_count'] += 1
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    elements = []
    styles, title_style, heading_style = get_pdf_styles()
    
    elements.append(Paragraph("Performance Trends Report", title_style))
    elements.append(Paragraph(f"Department: {dept_name}", styles['Normal']))
    elements.append(Paragraph(f"Period: Last {period} days ({start_date} to {end_date})", styles['Normal']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Overall Summary Statistics
    elements.append(Paragraph("Evaluation Summary", heading_style))
    
    summary_data = [
        ['Metric', 'Employee', 'Manager'],
        ['Completed Evaluations', str(employee_evaluations.count()), str(manager_evaluations.count())],
        ['Questions Tracked for Trends', str(len([q for q in employee_question_performance.values() if q['response_count'] > 0])), 
         str(len([q for q in manager_question_performance.values() if q['response_count'] > 0]))],
        ['Total Employees/Managers', str(employee_evaluations.values('employee').distinct().count()), 
         str(manager_evaluations.values('manager').distinct().count())],
    ]
    
    summary_table = create_summary_table(summary_data, [2.5*inch, 1.5*inch, 1.5*inch])
    # Override center alignment for columns 1 and 2
    summary_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Employee Question Performance (Chart Questions)
    if employee_question_performance:
        elements.append(Paragraph("Employee Performance by Question (Chart Metrics)", heading_style))
        
        emp_q_data = [['Question', 'Responses', 'Avg', '5⭐', '4⭐', '3⭐', '2⭐', '1⭐']]
        
        # Filter and process questions that have responses
        for question_key, data in sorted(employee_question_performance.items()):
            if data['response_count'] > 0:
                responses = data['responses']
                avg = sum(responses) / len(responses) if responses else 0
                
                # Count each star rating
                counts = {i: responses.count(i) for i in range(1, 6)}
                
                # Use helper for question paragraph
                question_para = create_question_paragraph(question_key)
                
                emp_q_data.append([
                    question_para,
                    str(data['response_count']),
                    f'{avg:.2f}',
                    str(counts.get(5, 0)),
                    str(counts.get(4, 0)),
                    str(counts.get(3, 0)),
                    str(counts.get(2, 0)),
                    str(counts.get(1, 0))
                ])
        
        if len(emp_q_data) > 1:  # Has data beyond header
            emp_q_table = create_chart_metrics_table(
                emp_q_data, 
                [3*inch, 0.7*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch]
            )
            elements.append(emp_q_table)
            elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("No employee questions marked for charts in this period.", styles['Normal']))
            elements.append(Spacer(1, 20))
    
    # Manager Question Performance (Chart Questions)
    if manager_question_performance:
        elements.append(Paragraph("Manager Performance by Question (Chart Metrics)", heading_style))
        
        mgr_q_data = [['Question', 'Responses', 'Avg', '5', '4', '3', '2', '1']]
        
        # Filter and process questions that have responses
        for question_key, data in sorted(manager_question_performance.items()):
            if data['response_count'] > 0:
                responses = data['responses']
                avg = sum(responses) / len(responses) if responses else 0
                
                # Count each star rating
                counts = {i: responses.count(i) for i in range(1, 6)}
                
                # Use helper for question paragraph
                question_para = create_question_paragraph(question_key)
                
                mgr_q_data.append([
                    question_para,
                    str(data['response_count']),
                    f'{avg:.2f}',
                    str(counts.get(5, 0)),
                    str(counts.get(4, 0)),
                    str(counts.get(3, 0)),
                    str(counts.get(2, 0)),
                    str(counts.get(1, 0))
                ])
        
        if len(mgr_q_data) > 1:  # Has data beyond header
            mgr_q_table = create_chart_metrics_table(
                mgr_q_data,
                [3*inch, 0.7*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch]
            )
            elements.append(mgr_q_table)
            elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("No manager questions marked for charts in this period.", styles['Normal']))
            elements.append(Spacer(1, 20))
    
    # Individual Employee Performance - Detailed by Person
    if employee_evaluations.exists():
        elements.append(Paragraph("Individual Employee Performance Details", heading_style))
        elements.append(Spacer(1, 10))
        
        # Collect individual employee data with question details including dates
        employee_individual_data = {}
        for eval in employee_evaluations:
            emp_name = eval.employee.user.get_full_name()
            if emp_name not in employee_individual_data:
                employee_individual_data[emp_name] = {
                    'department': eval.department.title,
                    'questions': {}
                }
            
            eval_date = eval.submitted_at.strftime('%Y-%m-%d') if eval.submitted_at else 'N/A'
            
            # Get responses for tracked questions only
            for answer in eval.answers.all():
                if answer.question.include_in_trends and answer.int_value is not None:
                    question_text = answer.question.text
                    question_type = answer.question.get_qtype_display()
                    
                    if question_text not in employee_individual_data[emp_name]['questions']:
                        employee_individual_data[emp_name]['questions'][question_text] = {
                            'type': question_type,
                            'responses': []
                        }
                    
                    employee_individual_data[emp_name]['questions'][question_text]['responses'].append({
                        'score': answer.int_value,
                        'date': eval_date
                    })
        
        # Create table for each employee
        for emp_name in sorted(employee_individual_data.keys()):
            data = employee_individual_data[emp_name]
            
            if data['questions']:  # Only show if they have tracked question responses
                # Employee header with red background
                emp_header = create_person_header(emp_name, data['department'])
                elements.append(emp_header)
                elements.append(Spacer(1, 8))
                
                # Questions table with dates
                emp_q_table_data = [['Question', 'Type', 'Score', 'Date']]
                
                for question_text, q_data in sorted(data['questions'].items()):
                    # Add each response as a separate row
                    for i, response in enumerate(q_data['responses']):
                        # Only show question text on first row for this question
                        question_display = create_question_paragraph(question_text) if i == 0 else ''
                        
                        emp_q_table_data.append([
                            question_display,
                            q_data['type'] if i == 0 else '',
                            str(response['score']),
                            response['date']
                        ])
                
                emp_q_table = create_individual_question_table(
                    emp_q_table_data, 
                    [2.6*inch, 1.4*inch, 0.7*inch, 1.1*inch]
                )
                elements.append(emp_q_table)
                elements.append(Spacer(1, 20))
    
    # Individual Manager Performance - Detailed by Person
    if manager_evaluations.exists():
        elements.append(Paragraph("Individual Manager Performance Details", heading_style))
        elements.append(Spacer(1, 10))
        
        # Collect individual manager data with question details including dates
        manager_individual_data = {}
        for eval in manager_evaluations:
            mgr_name = eval.manager.user.get_full_name()
            if mgr_name not in manager_individual_data:
                manager_individual_data[mgr_name] = {
                    'department': eval.department.title,
                    'questions': {}
                }
            
            eval_date = eval.submitted_at.strftime('%Y-%m-%d') if eval.submitted_at else 'N/A'
            
            # Get responses for tracked questions only
            for answer in eval.answers.all():
                if answer.question.include_in_trends and answer.int_value is not None:
                    question_text = answer.question.text
                    question_type = answer.question.get_qtype_display()
                    
                    if question_text not in manager_individual_data[mgr_name]['questions']:
                        manager_individual_data[mgr_name]['questions'][question_text] = {
                            'type': question_type,
                            'responses': []
                        }
                    
                    manager_individual_data[mgr_name]['questions'][question_text]['responses'].append({
                        'score': answer.int_value,
                        'date': eval_date
                    })
        
        # Create table for each manager
        for mgr_name in sorted(manager_individual_data.keys()):
            data = manager_individual_data[mgr_name]
            
            if data['questions']:  # Only show if they have tracked question responses
                # Manager header with red background
                mgr_header = create_person_header(mgr_name, data['department'])
                elements.append(mgr_header)
                elements.append(Spacer(1, 8))
                
                # Questions table with dates
                mgr_q_table_data = [['Question', 'Type', 'Score', 'Date']]
                
                for question_text, q_data in sorted(data['questions'].items()):
                    # Add each response as a separate row
                    for i, response in enumerate(q_data['responses']):
                        # Only show question text on first row for this question
                        question_display = create_question_paragraph(question_text) if i == 0 else ''
                        
                        mgr_q_table_data.append([
                            question_display,
                            q_data['type'] if i == 0 else '',
                            str(response['score']),
                            response['date']
                        ])
                
                mgr_q_table = create_individual_question_table(
                    mgr_q_table_data,
                    [2.6*inch, 1.4*inch, 0.7*inch, 1.1*inch]
                )
                elements.append(mgr_q_table)
                elements.append(Spacer(1, 20))
    
    doc.build(elements)
    
    # Save report history
    save_report_history('trends', user_profile, dept_obj, start_date, end_date)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="trends_report_{start_date}_{end_date}.pdf"'
    
    return response


# Archive/Unarchive functionality
@login_required
@require_http_methods(["POST"])
def toggle_evaluation_archive(request, evaluation_id):
    """Toggle archive status for employee evaluations (manager only)."""
    return toggle_archive_helper(
        request=request,
        evaluation_id=evaluation_id,
        model_class=DynamicEvaluation,
        owner_field='manager',
        target_field='employee',
        select_related_fields=['manager__user', 'employee__user']
    )


@login_required
@require_http_methods(["POST"])
def toggle_manager_evaluation_archive(request, evaluation_id):
    """Toggle archive status for manager evaluations (senior manager only)."""
    return toggle_archive_helper(
        request=request,
        evaluation_id=evaluation_id,
        model_class=DynamicManagerEvaluation,
        owner_field='senior_manager',
        target_field='manager',
        select_related_fields=['senior_manager__user', 'manager__user']
    )


@login_required
def archived_evaluations(request):
    """View archived employee evaluations for managers with pagination."""
    checker = get_role_checker(request.user)
    
    if not checker.is_manager() and not checker.is_senior_management():
        logger.warning(
            f"Permission denied: User {request.user.id} attempted to view archived evaluations "
            f"without proper permissions"
        )
        messages.error(request, "You don't have permission to view this page.")
        return redirect('evaluation:dashboard')
    
    # Senior managers can see ALL archived evaluations, regular managers see only their own
    if checker.is_senior_management():
        evaluations_list = (
            DynamicEvaluation.objects
            .filter(
                is_archived=True,
                answers__isnull=False  # Only evaluations that have been evaluated
            )
            .select_related('employee__user', 'manager__user', 'form', 'department')
            .distinct()  # Remove duplicates from the join
            .order_by('-submitted_at', '-week_end')
        )
    else:
        # Get archived evaluations that this manager has actually evaluated (has submitted answers)
        evaluations_list = (
            DynamicEvaluation.objects
            .filter(
                manager=checker.user_profile, 
                is_archived=True,
                answers__isnull=False  # Only evaluations that have been evaluated
            )
            .select_related('employee__user', 'manager__user', 'form', 'department')
            .distinct()  # Remove duplicates from the join
            .order_by('-submitted_at', '-week_end')
        )
    
    total_archived = evaluations_list.count()
    
    # Pagination - 10 items per page
    page = request.GET.get('page', 1)
    paginator = Paginator(evaluations_list, 10)  # 10 evaluations per page
    
    try:
        evaluations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        evaluations = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        evaluations = paginator.page(paginator.num_pages)
    
    logger.info(
        f"User {request.user.id} viewed page {evaluations.number} of {total_archived} archived employee evaluations"
    )
    
    context = {
        'evaluations': evaluations,
        'total_archived': total_archived
    }
    
    return render(request, 'evaluation/archived_evaluations.html', context)


@login_required
@require_senior_management_access
def archived_manager_evaluations(request):
    """View archived manager and employee evaluations for senior managers with filter and pagination."""
    checker = get_role_checker(request.user)
    
    # Get filter parameter (default to 'manager' for manager evaluations)
    eval_type = request.GET.get('type', 'manager')
    
    # Get archived manager evaluations for this senior manager with optimized query
    manager_evaluations = (
        DynamicManagerEvaluation.objects
        .filter(senior_manager=checker.user_profile, is_archived=True)
        .select_related('manager__user', 'senior_manager__user', 'form', 'department')
        .order_by('-submitted_at', '-period_end')
    )
    
    # Senior managers can see ALL archived employee evaluations
    if checker.is_senior_management():
        employee_evaluations = (
            DynamicEvaluation.objects
            .filter(is_archived=True)
            .select_related('employee__user', 'manager__user', 'form', 'department')
            .order_by('-week_end')
        )
    else:
        # Regular managers see only their own archived employee evaluations
        employee_evaluations = (
            DynamicEvaluation.objects
            .filter(manager=checker.user_profile, is_archived=True)
            .select_related('employee__user', 'manager__user', 'form', 'department')
            .order_by('-week_end')
        )
    
    # Get total counts before pagination
    manager_count = manager_evaluations.count()
    employee_count = employee_evaluations.count()
    
    # Set evaluations based on filter
    if eval_type == 'employee':
        evaluations_list = employee_evaluations
        total_archived = employee_count
    else:
        evaluations_list = manager_evaluations
        total_archived = manager_count
    
    # Pagination - 10 items per page
    page = request.GET.get('page', 1)
    paginator = Paginator(evaluations_list, 10)  # 10 evaluations per page
    
    try:
        evaluations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        evaluations = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        evaluations = paginator.page(paginator.num_pages)
    
    logger.info(
        f"User {request.user.id} viewed page {evaluations.number} of {total_archived} archived {eval_type} evaluations "
        f"(Manager count: {manager_count}, Employee count: {employee_count})"
    )
    
    context = {
        'evaluations': evaluations,
        'total_archived': total_archived,
        'eval_type': eval_type,
        'manager_count': manager_count,
        'employee_count': employee_count,
    }
    
    return render(request, 'evaluation/archived_manager_evaluations.html', context)


