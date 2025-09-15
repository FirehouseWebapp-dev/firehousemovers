from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Max, Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import json
import logging

logger = logging.getLogger(__name__)

from authentication.models import UserProfile, Department
from .models_dynamic import EvalForm, Question, DynamicEvaluation, DynamicManagerEvaluation
from .forms_dynamic_admin import EvalFormForm, QuestionForm, QuestionChoiceForm
from .forms_dynamic import PreviewEvalForm, DynamicEvaluationForm
from .constants import EvaluationStatus
from django.utils.timezone import now
from datetime import timedelta
from firehousemovers.utils.permissions import role_checker, require_management, require_admin_or_senior, ajax_require_management
from .decorators import (
    require_department_management, require_department_management_for_form, 
    ajax_require_department_management, 
    require_manager_access, require_senior_management_access, require_evaluation_access
)
from .utils import (
    activate_evalform_safely, deactivate_evalform_safely, get_role_checker,
    check_department_permission, process_form_creation_with_conflicts, 
    process_form_edit_with_conflicts
)
from .evaluation_handlers import (
    handle_evaluation_submission, handle_evaluation_view, 
    handle_my_evaluations, handle_pending_evaluations,
    EMPLOYEE_EVALUATION_CONFIG, MANAGER_EVALUATION_CONFIG
)

# Permission checking functions moved to decorators.py

@login_required
def evaluation_dashboard(request):
    """
    Dashboard view: managers see their team's evaluations; admins see all.
    Supports optional search by employee name/username.
    """
    query = request.GET.get("q", "")
    profile = request.user.userprofile
    today = now().date()

    if profile.is_admin:
        evaluations = (
            Evaluation.objects
            .select_related("employee__user")
            .order_by("-week_start")
        )
    else:
        evaluations = (
            Evaluation.objects
            .filter(manager=profile)
            .select_related("employee__user")
            .order_by("-week_start")
        )

    if query:
        evaluations = evaluations.filter(
            Q(employee__user__first_name__icontains=query) |
            Q(employee__user__last_name__icontains=query) |
            Q(employee__user__username__icontains=query)
        )

    return render(request, "evaluation/dashboard.html", {
        "evaluations": evaluations,
        "today": today,
    })



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
        if checker.is_manager() and checker.user_profile.managed_department:
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
        if checker.is_manager() and checker.user_profile.managed_department:
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
        if checker.is_manager() and checker.user_profile.managed_department:
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
def evaluation_dashboard2(request):
    """
    Dashboard 2 view: Alternative dashboard for managers showing dynamic evaluations.
    """
    checker = get_role_checker(request.user)
    
    today = now().date()
    
    # Get manager's team dynamic evaluations with optimized stats calculation
    evaluations = (
        DynamicEvaluation.objects
        .filter(manager=checker.user_profile)
        .select_related("employee__user", "form", "department")
        .order_by("-week_start")
    )
    
    # Calculate all counts in a single optimized query using aggregation
    
    stats = evaluations.aggregate(
        pending_count=Count('id', filter=Q(status=EvaluationStatus.PENDING)),
        completed_count=Count('id', filter=Q(status=EvaluationStatus.COMPLETED)),
        overdue_count=Count('id', filter=Q(status=EvaluationStatus.PENDING, week_end__lt=today))
    )
    
    pending_count = stats['pending_count']
    completed_count = stats['completed_count']
    overdue_count = stats['overdue_count']
    
    return render(request, "evaluation/dashboard2.html", {
        "evaluations": evaluations,
        "today": today,
        "pending_count": pending_count,
        "completed_count": completed_count,
        "overdue_count": overdue_count,
    })


@login_required
@require_evaluation_access
def evaluate_dynamic_employee(request, evaluation_id):
    """
    Manager view: display & handle single dynamic evaluation form.
    """
    result = handle_evaluation_submission(request, evaluation_id, EMPLOYEE_EVALUATION_CONFIG)
    
    # If result is a redirect (success), return it
    if hasattr(result, 'status_code'):
        return result
    
    # Otherwise, result is template context - render the template
    return render(request, "evaluation/evaluate_dynamic_employee.html", result)


@login_required
@require_evaluation_access
def view_dynamic_evaluation(request, evaluation_id):
    """
    View completed dynamic evaluation (read-only).
    """
    template_context = handle_evaluation_view(request, evaluation_id, EMPLOYEE_EVALUATION_CONFIG)
    
    # Rename 'evaluatee' to 'employee' for template compatibility
    template_context['employee'] = template_context['evaluatee']
    
    return render(request, "evaluation/view_dynamic_evaluation.html", template_context)


@login_required
@require_manager_access
def pending_evaluations_v2(request):
    """
    Manager view: show progress & list of pending dynamic evaluations
    for last week and this week.
    """
    return handle_pending_evaluations(request, EMPLOYEE_EVALUATION_CONFIG, "evaluation/pending_evaluations_v2.html")


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
    
    today = now().date()
    
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
    
    for period_info in unique_periods:
        form_name = period_info['form__name']
        period_start = period_info['period_start']
        period_end = period_info['period_end']
        
        # Calculate all stats in a single optimized query using aggregation
        
        stats = evaluations.filter(
            form__name=form_name,
            period_start=period_start,
            period_end=period_end
        ).aggregate(
            total_count=Count('id'),
            pending_count=Count('id', filter=Q(status=EvaluationStatus.PENDING)),
            completed_count=Count('id', filter=Q(status=EvaluationStatus.COMPLETED)),
            overdue_count=Count('id', filter=Q(status=EvaluationStatus.PENDING, period_end__lt=today))
        )
        
        total_count = stats['total_count']
        pending_count = stats['pending_count']
        completed_count = stats['completed_count']
        overdue_count = stats['overdue_count']
        
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
    
    today = now().date()
    
    # Get filter parameters
    form_name = request.GET.get('form')
    period_start = request.GET.get('period_start')
    period_end = request.GET.get('period_end')
    
    if not all([form_name, period_start, period_end]):
        return redirect("evaluation:manager_evaluation_dashboard")
    
    # Parse dates
    try:
        from datetime import datetime
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
    
    stats = evaluations.aggregate(
        total_count=Count('id'),
        pending_count=Count('id', filter=Q(status=EvaluationStatus.PENDING)),
        completed_count=Count('id', filter=Q(status=EvaluationStatus.COMPLETED)),
        overdue_count=Count('id', filter=Q(status=EvaluationStatus.PENDING, period_end__lt=today))
    )
    
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
