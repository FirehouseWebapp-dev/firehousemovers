from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Max
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import json
from authentication.models import UserProfile, Department
from .models_dynamic import EvalForm, Question, QuestionChoice, DynamicEvaluation
from .forms_dynamic_admin import EvalFormForm, QuestionForm, QuestionChoiceForm
from .forms_dynamic import PreviewEvalForm, DynamicEvaluationForm
from django.utils.timezone import now
from datetime import timedelta

def _can_manage(user):
    """Check if user can manage evaluation forms globally (superusers and senior management only)."""
    if not user.is_authenticated:
        return False
    p = getattr(user, "userprofile", None)
    return (
        user.is_superuser
        or (p and p.role in {"admin", "vp", "ceo"})
    )

def _can_manage_department(user, department):
    """Check if user can manage evaluation forms for a specific department."""
    if not user.is_authenticated:
        return False
    p = getattr(user, "userprofile", None)
    if not p:
        return False
    
    # Superusers and global admins can manage any department
    if user.is_superuser or p.role in {"admin", "vp", "ceo"}:
        return True
    
    # Department managers can only manage their own department
    if p.role == "manager" and p.managed_department == department:
        return True
    
    return False


@login_required
def evalform_list(request):
    """List evaluation forms with department-specific permissions."""
    profile = request.user.userprofile
    
    # Get forms based on user permissions
    if _can_manage(request.user):
        # Global admins can see all forms
        forms = EvalForm.objects.select_related("department").order_by("-created_at")
        dept = request.GET.get("department")
        if dept and dept != "all":
            forms = forms.filter(department_id=dept)
    else:
        # Department managers can only see their own department's forms
        if profile.role == "manager" and profile.managed_department:
            forms = EvalForm.objects.filter(
                department=profile.managed_department
            ).select_related("department").order_by("-created_at")
        else:
            # No permission to view any forms
            forms = EvalForm.objects.none()
    
    return render(request, "evaluation/forms/list.html", {"forms": forms})

@login_required
def evalform_create(request):
    """Create evaluation form with department-specific permissions."""
    profile = request.user.userprofile
    
    if request.method == "POST":
        form = EvalFormForm(request.POST)
        if form.is_valid():
            # Check department permissions
            department = form.cleaned_data["department"]
            if not _can_manage_department(request.user, department):
                messages.error(request, "You don't have permission to create forms for this department.")
                return render(request, "evaluation/forms/create.html", {"form": form})
            
            try:
                with transaction.atomic():
                    # Deactivate any existing active forms of the same evaluation type for this department
                    EvalForm.objects.filter(
                        department=department, 
                        name=form.cleaned_data["name"],
                        is_active=True
                    ).update(is_active=False)
                    # Save the new form as active
                    obj = form.save()
                messages.success(request, "Form created.")
                return redirect("evaluation:evalform_detail", pk=obj.id)
            except IntegrityError as e:
                # If database constraint is violated, show only the custom message
                if 'uq_evalform_one_active_per_dept_per_type' in str(e):
                    from .messages import EVALUATION_ALREADY_EXISTS
                    messages.error(request, EVALUATION_ALREADY_EXISTS)
                else:
                    messages.error(request, "An error occurred while saving the form.")
                # Re-render the form to show the error message
                return render(request, "evaluation/forms/create.html", {"form": form})
    else:
        form = EvalFormForm()
        # Restrict department choices for non-global admins
        if profile.role == "manager" and profile.managed_department:
            form.fields['department'].queryset = Department.objects.filter(id=profile.managed_department.id)
            form.fields['department'].initial = profile.managed_department
    
    return render(request, "evaluation/forms/create.html", {"form": form})

@login_required
def evalform_edit(request, pk):
    """Edit evaluation form with department-specific permissions."""
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    profile = request.user.userprofile
    
    # Check if user can edit this form
    if not _can_manage_department(request.user, obj.department):
        messages.error(request, "You don't have permission to edit this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    if request.method == "POST":
        form = EvalFormForm(request.POST, instance=obj)
        if form.is_valid():
            # Check department permissions for the new department
            department = form.cleaned_data["department"]
            if not _can_manage_department(request.user, department):
                messages.error(request, "You don't have permission to move this form to that department.")
                return render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": obj})
            
            try:
                with transaction.atomic():
                    # Only deactivate other forms if this form is currently active
                    # and we're changing to a different department/type combination
                    if obj.is_active:
                        EvalForm.objects.filter(
                            department=department, 
                            name=form.cleaned_data["name"],
                            is_active=True
                        ).exclude(pk=obj.pk).update(is_active=False)
                    
                    # Save the form preserving the existing is_active status
                    form.save()
                messages.success(request, "Form updated.")
                return redirect("evaluation:evalform_detail", pk=obj.id)
            except IntegrityError as e:
                # If database constraint is violated, show only the custom message
                if 'uq_evalform_one_active_per_dept_per_type' in str(e):
                    from .messages import EVALUATION_ALREADY_EXISTS
                    messages.error(request, EVALUATION_ALREADY_EXISTS)
                else:
                    messages.error(request, "An error occurred while saving the form.")
                # Re-render the form to show the error message
                return render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": obj})
    else:
        form = EvalFormForm(instance=obj)
        # Restrict department choices for non-global admins
        if profile.role == "manager" and profile.managed_department:
            form.fields['department'].queryset = Department.objects.filter(id=profile.managed_department.id)
    
    return render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": obj})

@login_required
def evalform_detail(request, pk):
    """View evaluation form details with department-specific permissions."""
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    # Check if user can view this form
    if not _can_manage_department(request.user, obj.department):
        messages.error(request, "You don't have permission to view this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    qs = obj.questions.prefetch_related("choices").order_by('order')
    return render(request, "evaluation/forms/detail.html", {"form_obj": obj, "questions": qs})

@login_required
def evalform_preview(request, pk):
    """Preview evaluation form with department-specific permissions."""
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    # Check if user can view this form
    if not _can_manage_department(request.user, obj.department):
        messages.error(request, "You don't have permission to preview this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    form = PreviewEvalForm(eval_form=obj)
    return render(request, "evaluation/forms/preview.html", {"form_obj": obj, "preview_form": form})

@login_required
def evalform_activate(request, pk):
    """Activate/deactivate evaluation form with department-specific permissions."""
    if request.method != "POST":
        return redirect("evaluation:evalform_detail", pk=pk)
    
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    # Check if user can manage this form
    if not _can_manage_department(request.user, obj.department):
        messages.error(request, "You don't have permission to activate/deactivate this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    # Check if the form has any questions
    question_count = obj.questions.count()
    if question_count == 0:
        messages.error(request, f"Cannot activate '{obj.name}' - it has no questions. Please add at least one question before activating.")
        return redirect("evaluation:evalform_detail", pk=pk)
    
    with transaction.atomic():
        if obj.is_active:
            # Deactivate the form
            obj.is_active = False
            obj.save(update_fields=["is_active"])
            messages.success(request, f"'{obj.name}' has been deactivated.")
        else:
            # Activate the form - first deactivate other forms of the same type
            EvalForm.objects.filter(
                department=obj.department, 
                name=obj.name,
                is_active=True
            ).exclude(pk=obj.pk).update(is_active=False)
            obj.is_active = True
            obj.save(update_fields=["is_active"])
            messages.success(request, f"'{obj.name}' is now active for {obj.department.title}.")
    
    # Redirect back to forms list to show updated status
    return redirect("evaluation:evalform_list")

@login_required
def evalform_delete(request, pk):
    """Delete evaluation form with department-specific permissions."""
    if request.method != "POST":
        return redirect("evaluation:evalform_list")
    
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
    # Check if user can manage this form
    if not _can_manage_department(request.user, obj.department):
        messages.error(request, "You don't have permission to delete this evaluation form.")
        return redirect("evaluation:evalform_list")
    
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
        messages.error(request, f"Cannot delete '{form_name}' - it has associated evaluations. Please delete the evaluations first.")
    
    return redirect("evaluation:evalform_list")

# ------- Questions -------
@login_required
def question_add(request, form_id):
    """Add question to evaluation form with department-specific permissions."""
    ef = get_object_or_404(EvalForm, pk=form_id)
    
    # Check if user can manage this form
    if not _can_manage_department(request.user, ef.department):
        messages.error(request, "You don't have permission to add questions to this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    if request.method == "POST":
        qf = QuestionForm(request.POST)
        if qf.is_valid():
            # Set order to be the next available order
            max_order = ef.questions.aggregate(max_order=Max('order'))['max_order'] or 0
            qf.instance.form = ef
            qf.instance.order = max_order + 1
            qf.save()
            messages.success(request, "Question added.")
            return redirect("evaluation:evalform_detail", pk=ef.id)
    else:
        qf = QuestionForm()
    return render(request, "evaluation/forms/question_add.html", {"form": qf, "form_obj": ef})

@login_required
def question_edit(request, question_id):
    """Edit question with department-specific permissions."""
    q = get_object_or_404(Question, pk=question_id)
    
    # Check if user can manage this form
    if not _can_manage_department(request.user, q.form.department):
        messages.error(request, "You don't have permission to edit questions in this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    if request.method == "POST":
        qf = QuestionForm(request.POST, instance=q)
        if qf.is_valid():
            qf.save()
            messages.success(request, "Question updated.")
            return redirect("evaluation:evalform_detail", pk=q.form_id)
    else:
        qf = QuestionForm(instance=q)
    return render(request, "evaluation/forms/question_edit.html", {"form": qf, "question": q})

@login_required
def choice_add(request, question_id):
    """Add choice to question with department-specific permissions."""
    q = get_object_or_404(Question, pk=question_id)
    
    # Check if user can manage this form
    if not _can_manage_department(request.user, q.form.department):
        messages.error(request, "You don't have permission to add choices to questions in this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    if request.method == "POST":
        cf = QuestionChoiceForm(request.POST)
        if cf.is_valid():
            cf.instance.question = q
            cf.save()
            messages.success(request, "Choice added.")
            return redirect("evaluation:evalform_detail", pk=q.form_id)
    else:
        cf = QuestionChoiceForm()
    return render(request, "evaluation/forms/choice_add.html", {"form": cf, "question": q})


@login_required
@require_http_methods(["POST"])
def update_question_order(request, pk):
    """Update the order of questions via AJAX with department-specific permissions."""
    try:
        form_obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
        
        # Check if user can manage this form
        if not _can_manage_department(request.user, form_obj.department):
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        data = json.loads(request.body)
        question_orders = data.get('question_orders', [])
        
        with transaction.atomic():
            for item in question_orders:
                question_id = item.get('id')
                order = item.get('order')
                
                if question_id and order:
                    question = get_object_or_404(Question, id=question_id, form=form_obj)
                    question.order = order
                    question.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def question_delete(request, question_id):
    """Delete a question with department-specific permissions."""
    question = get_object_or_404(Question, id=question_id)
    form_obj = question.form
    
    # Check if user can manage this form
    if not _can_manage_department(request.user, form_obj.department):
        messages.error(request, "You don't have permission to delete questions from this evaluation form.")
        return redirect("evaluation:evalform_list")
    
    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect("evaluation:evalform_detail", pk=form_obj.id)
    
    # If not POST, redirect to form detail
    return redirect("evaluation:evalform_detail", pk=form_obj.id)


@login_required
def evaluation_dashboard2(request):
    """
    Dashboard 2 view: Alternative dashboard for managers showing dynamic evaluations.
    """
    profile = request.user.userprofile
    
    # Only managers can access this dashboard
    if not (profile.role == "manager" or profile.is_manager):
        return redirect("evaluation:dashboard")
    
    today = now().date()
    
    # Get manager's team dynamic evaluations
    evaluations = (
        DynamicEvaluation.objects
        .filter(manager=profile)
        .select_related("employee__user", "form", "department")
        .order_by("-week_start")
    )
    
    # Calculate counts
    pending_count = evaluations.filter(status="pending").count()
    completed_count = evaluations.filter(status="completed").count()
    
    return render(request, "evaluation/dashboard2.html", {
        "evaluations": evaluations,
        "today": today,
        "pending_count": pending_count,
        "completed_count": completed_count,
    })


@login_required
def evaluate_dynamic_employee(request, evaluation_id):
    """
    Manager view: display & handle single dynamic evaluation form.
    """
    evaluation = get_object_or_404(DynamicEvaluation, pk=evaluation_id)
    manager = request.user.userprofile

    # only the assigned manager may access
    if evaluation.manager != manager:
        return redirect("evaluation:dashboard2")

    # editable while within the week window
    is_editable = (now().date() <= evaluation.week_end)
    can_submit = is_editable or (evaluation.submitted_at is None)

    if request.method == "POST" and can_submit:
        form = DynamicEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            with transaction.atomic():
                # Check if this is an update or new submission
                was_completed = evaluation.status == "completed"
                
                # Save the evaluation status
                evaluation.status = "completed"
                evaluation.submitted_at = now()
                evaluation.save()
                
                # Save the form data (answers)
                form.save()
                
                # Send email notification to employee (only for new submissions, not updates)
                if not was_completed:
                    try:
                        detail_path = reverse("evaluation:view_dynamic_evaluation", args=[evaluation.id])
                        evaluation_url = f"{settings.BASE_URL}{detail_path}"

                        # plain-text fallback
                        text_content = (
                            f"Hi {evaluation.employee.user.get_full_name()},\n\n"
                            f"Your manager {evaluation.manager.user.get_full_name()} has submitted your evaluation "
                            f"for the week {evaluation.week_start} to {evaluation.week_end}.\n"
                            f"View it here: {evaluation_url}\n\n"
                            "Thanks,"
                        )

                        # render the HTML template
                        html_content = render_to_string(
                            "evaluation/email/evaluation_submitted.html",
                            {"ev": evaluation, "evaluation_url": evaluation_url}
                        )

                      
                        send_mail(
                            subject=f"Your evaluation for {evaluation.week_start}–{evaluation.week_end} is ready",
                            message=text_content,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[evaluation.employee.user.email],
                            html_message=html_content,
                        )
                    except Exception:
                        # swallow email errors but keep the saved evaluation
                        pass
                
                if was_completed:
                    messages.success(request, f"Evaluation for {evaluation.employee.user.get_full_name()} has been updated successfully!")
                else:
                    messages.success(request, f"Evaluation for {evaluation.employee.user.get_full_name()} has been submitted successfully!")
                return redirect("evaluation:dashboard2")
    else:
        form = DynamicEvaluationForm(instance=evaluation)

    return render(request, "evaluation/evaluate_dynamic_employee.html", {
        "form": form,
        "evaluation": evaluation,
        "employee": evaluation.employee,
        "week_start": evaluation.week_start,
        "week_end": evaluation.week_end,
        "is_editable": is_editable,
        "can_submit": can_submit,
    })


@login_required
def view_dynamic_evaluation(request, evaluation_id):
    """
    View completed dynamic evaluation (read-only).
    """
    evaluation = get_object_or_404(
        DynamicEvaluation.objects.select_related('form', 'department', 'employee__user')
                                 .prefetch_related('form__questions__choices'),
        pk=evaluation_id
    )
    manager = request.user.userprofile

    # only the assigned manager may access
    if evaluation.manager != manager:
        return redirect("evaluation:dashboard2")

    # Get all answers for this evaluation with optimized queries
    answers = evaluation.answers.select_related('question').all()
    
    # Create a dictionary for easy template access
    answers_dict = {answer.question_id: answer for answer in answers}

    return render(request, "evaluation/view_dynamic_evaluation.html", {
        "evaluation": evaluation,
        "employee": evaluation.employee,
        "answers": answers_dict,
        "week_start": evaluation.week_start,
        "week_end": evaluation.week_end,
    })


@login_required
def pending_evaluations_v2(request):
    """
    Manager view: show progress & list of pending dynamic evaluations
    for last week and this week.
    """
    profile = request.user.userprofile
    today = now().date()
    weekday = today.weekday()

    # compute Mondays
    this_monday = today - timedelta(days=weekday)
    last_monday = this_monday - timedelta(days=7)

    # stats for both weeks
    stats_qs = DynamicEvaluation.objects.filter(
        manager=profile,
        week_start__in=[last_monday, this_monday],
    )

    total = stats_qs.count()
    completed = stats_qs.filter(status="completed").count()
    pending = stats_qs.filter(status="pending").count()
    
    percent_complete = (completed / total * 100) if total > 0 else 0

    # Get pending evaluations for both weeks
    pending_evaluations = DynamicEvaluation.objects.filter(
        manager=profile,
        week_start__in=[last_monday, this_monday],
        status="pending"
    ).select_related("employee__user", "form", "department").order_by("week_start", "employee__user__first_name")

    return render(request, "evaluation/pending_evaluations_v2.html", {
        "pending_evaluations": pending_evaluations,
        "completed": completed,
        "total": total,
        "pending": pending,
        "percent_complete": percent_complete,
    })
