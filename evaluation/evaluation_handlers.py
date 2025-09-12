"""
Generic handlers for dynamic evaluations to eliminate duplication between
employee and manager evaluation views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

from .models_dynamic import DynamicEvaluation, DynamicManagerEvaluation
from .forms_dynamic import DynamicEvaluationForm
from .constants import EvaluationStatus


class EvaluationConfig:
    """Configuration class for different evaluation types."""
    
    def __init__(self, model_class, evaluator_field, evaluatee_field, 
                 period_start_field, period_end_field, detail_view_name,
                 email_template, email_subject_template):
        self.model_class = model_class
        self.evaluator_field = evaluator_field  # 'manager' or 'senior_manager'
        self.evaluatee_field = evaluatee_field  # 'employee' or 'manager'
        self.period_start_field = period_start_field  # 'week_start' or 'period_start'
        self.period_end_field = period_end_field  # 'week_end' or 'period_end'
        self.detail_view_name = detail_view_name
        self.email_template = email_template
        self.email_subject_template = email_subject_template


# Configuration for employee evaluations
EMPLOYEE_EVALUATION_CONFIG = EvaluationConfig(
    model_class=DynamicEvaluation,
    evaluator_field='manager',
    evaluatee_field='employee',
    period_start_field='week_start',
    period_end_field='week_end',
    detail_view_name='evaluation:view_dynamic_evaluation',
    email_template='evaluation/email/evaluation_submitted.html',
    email_subject_template='Your evaluation for {start}–{end} is ready'
)

# Configuration for manager evaluations
MANAGER_EVALUATION_CONFIG = EvaluationConfig(
    model_class=DynamicManagerEvaluation,
    evaluator_field='senior_manager',
    evaluatee_field='manager',
    period_start_field='period_start',
    period_end_field='period_end',
    detail_view_name='evaluation:view_manager_evaluation',
    email_template='evaluation/email/manager_evaluation_submitted.html',
    email_subject_template='Your evaluation for {start}–{end} is ready'
)


def handle_evaluation_submission(request, evaluation_id, config):
    """
    Generic handler for evaluation submission (both employee and manager evaluations).
    
    Args:
        request: Django request object
        evaluation_id: ID of the evaluation to submit
        config: EvaluationConfig instance
    
    Returns:
        HttpResponse: Redirect or render response
    """
    evaluation = get_object_or_404(config.model_class, pk=evaluation_id)
    
    # Check if evaluation is still editable
    period_end = getattr(evaluation, config.period_end_field)
    is_editable = (now().date() <= period_end)
    can_submit = is_editable or (evaluation.submitted_at is None)
    
    if request.method == "POST":
        try:
            form = DynamicEvaluationForm(request.POST, instance=evaluation)
            if form.is_valid() and can_submit:
                with transaction.atomic():
                    # Check if this is an update or new submission
                    was_completed = evaluation.status == EvaluationStatus.COMPLETED
                    
                    # Save the evaluation status
                    evaluation.status = EvaluationStatus.COMPLETED
                    evaluation.submitted_at = now()
                    evaluation.save()
                    
                    # Save the form data (answers)
                    form.save()
                    
                    # Send email notification (only for new submissions, not updates)
                    if not was_completed:
                        _send_evaluation_notification_email(evaluation, config)
                    
                    # Success message
                    evaluatee = getattr(evaluation, config.evaluatee_field)
                    if was_completed:
                        messages.success(request, f"Evaluation for {evaluatee.user.get_full_name()} has been updated successfully!")
                    else:
                        messages.success(request, f"Evaluation for {evaluatee.user.get_full_name()} has been submitted successfully!")
                    
                    # Redirect to appropriate dashboard
                    return redirect(_get_dashboard_url(config))
            # If form is invalid, it will be passed to the template with errors
        except Exception as e:
            logger.exception("Failed to submit evaluation")
            messages.error(request, "An error occurred while submitting the evaluation. Please try again.")
            form = DynamicEvaluationForm(request.POST, instance=evaluation)
    else:
        form = DynamicEvaluationForm(instance=evaluation)
    
    # Prepare template context
    evaluatee = getattr(evaluation, config.evaluatee_field)
    period_start = getattr(evaluation, config.period_start_field)
    period_end = getattr(evaluation, config.period_end_field)
    
    template_context = {
        "form": form,
        "evaluation": evaluation,
        "evaluatee": evaluatee,
        "period_start": period_start,
        "period_end": period_end,
        "is_editable": is_editable,
        "can_submit": can_submit,
    }
    
    return template_context


def handle_evaluation_view(request, evaluation_id, config):
    """
    Generic handler for viewing completed evaluations.
    
    Args:
        request: Django request object
        evaluation_id: ID of the evaluation to view
        config: EvaluationConfig instance
    
    Returns:
        HttpResponse: Render response
    """
    evaluation = get_object_or_404(
        config.model_class.objects.select_related('form', 'department', 
                                                  f'{config.evaluator_field}__user', 
                                                  f'{config.evaluatee_field}__user')
                                 .prefetch_related('form__questions__choices'),
        pk=evaluation_id
    )
    
    # Get all answers for this evaluation with optimized queries
    # prefetch_related('question__choices') optimizes rendering of SELECT question types
    answers = evaluation.answers.select_related('question').prefetch_related('question__choices').all()
    
    # Create a dictionary for easy template access
    answers_dict = {answer.question_id: answer for answer in answers}
    
    # Prepare template context
    evaluatee = getattr(evaluation, config.evaluatee_field)
    period_start = getattr(evaluation, config.period_start_field)
    period_end = getattr(evaluation, config.period_end_field)
    
    template_context = {
        "evaluation": evaluation,
        "evaluatee": evaluatee,
        "answers": answers_dict,
        "period_start": period_start,
        "period_end": period_end,
    }
    
    return template_context


def handle_my_evaluations(request, config, template_name):
    """
    Generic handler for "my evaluations" views.
    
    Args:
        request: Django request object
        config: EvaluationConfig instance
        template_name: Template to render
    
    Returns:
        HttpResponse: Render response
    """
    from .utils import get_role_checker
    
    checker = get_role_checker(request.user)
    today = now().date()
    
    # Get evaluations where user is the evaluatee
    evaluatee_field_filter = {config.evaluatee_field: checker.user_profile}
    evaluations = (
        config.model_class.objects
        .filter(**evaluatee_field_filter)
        .select_related(f"{config.evaluator_field}__user", "form", "department")
        .order_by(f"-{config.period_start_field}")
    )
    
    # Calculate all counts in a single optimized query using aggregation
    
    period_end_filter = {f"{config.period_end_field}__lt": today}
    
    stats = evaluations.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status=EvaluationStatus.COMPLETED)),
        pending=Count('id', filter=Q(status=EvaluationStatus.PENDING)),
        overdue=Count('id', filter=Q(status=EvaluationStatus.PENDING, **period_end_filter))
    )
    
    total = stats['total']
    completed = stats['completed']
    pending = stats['pending']
    overdue = stats['overdue']
    
    # Calculate percentage
    percent_complete = (completed / total * 100) if total > 0 else 0
    
    template_context = {
        "evaluations": evaluations,
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "percent_complete": percent_complete,
        "today": today,
    }
    
    return render(request, template_name, template_context)


def handle_pending_evaluations(request, config, template_name):
    """
    Generic handler for "pending evaluations" views.
    
    Args:
        request: Django request object
        config: EvaluationConfig instance
        template_name: Template to render
    
    Returns:
        HttpResponse: Render response
    """
    from .utils import get_role_checker
    
    checker = get_role_checker(request.user)
    today = now().date()
    
    # Get pending evaluations where user is the evaluator
    evaluator_field_filter = {config.evaluator_field: checker.user_profile}
    pending_evaluations = (
        config.model_class.objects
        .filter(**evaluator_field_filter, status=EvaluationStatus.PENDING)
        .select_related(f"{config.evaluatee_field}__user", "form", "department")
        .order_by(f"-{config.period_start_field}", f"{config.evaluatee_field}__user__first_name")
    )
    
    # Calculate all stats in a single optimized query using aggregation
    
    period_end_filter = {f"{config.period_end_field}__lt": today}
    
    # Get all evaluations for this evaluator to calculate total stats
    all_evaluations = config.model_class.objects.filter(**evaluator_field_filter)
    
    stats = all_evaluations.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status=EvaluationStatus.COMPLETED)),
        pending=Count('id', filter=Q(status=EvaluationStatus.PENDING)),
        overdue=Count('id', filter=Q(status=EvaluationStatus.PENDING, **period_end_filter))
    )
    
    total = stats['total']
    completed = stats['completed']
    pending = stats['pending']
    overdue = stats['overdue']
    
    percent_complete = (completed / total * 100) if total > 0 else 0
    
    template_context = {
        "pending_evaluations": pending_evaluations,
        "completed": completed,
        "total": total,
        "pending": pending,
        "overdue": overdue,
        "percent_complete": percent_complete,
        "today": today,
    }
    
    return render(request, template_name, template_context)


def _send_evaluation_notification_email(evaluation, config):
    """Send email notification for completed evaluation."""
    try:
        evaluatee = getattr(evaluation, config.evaluatee_field)
        period_start = getattr(evaluation, config.period_start_field)
        period_end = getattr(evaluation, config.period_end_field)
        
        detail_path = reverse(config.detail_view_name, args=[evaluation.id])
        evaluation_url = f"{settings.BASE_URL}{detail_path}"
        
        # Plain-text fallback
        evaluator = getattr(evaluation, config.evaluator_field)
        text_content = (
            f"Hi {evaluatee.user.get_full_name()},\n\n"
            f"Your {config.evaluator_field.replace('_', ' ')} {evaluator.user.get_full_name()} has submitted your evaluation "
            f"for the period {period_start} to {period_end}.\n"
            f"View your evaluations here: {evaluation_url}\n\n"
            "Thanks,"
        )
        
        # Render the HTML template
        html_content = render_to_string(
            config.email_template,
            {"ev": evaluation, "evaluation_url": evaluation_url}
        )
        
        send_mail(
            subject=config.email_subject_template.format(start=period_start, end=period_end),
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[evaluatee.user.email],
            html_message=html_content,
        )
    except Exception as e:
        # Log email errors but keep the saved evaluation
        logger.exception(f"Failed to send evaluation email to {evaluatee.user.email}")


def _get_dashboard_url(config):
    """Get the appropriate dashboard URL based on evaluation type."""
    if config == EMPLOYEE_EVALUATION_CONFIG:
        return "evaluation:dashboard2"
    else:  # MANAGER_EVALUATION_CONFIG
        return "evaluation:manager_evaluation_dashboard"
