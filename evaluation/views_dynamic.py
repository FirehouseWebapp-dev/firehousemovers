from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Prefetch, Max
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from authentication.models import UserProfile
from .models_dynamic import EvalForm, Question, QuestionChoice
from .forms_dynamic_admin import EvalFormForm, QuestionForm, QuestionChoiceForm
from .forms_dynamic import PreviewEvalForm

def _can_manage(user):
    if not user.is_authenticated:
        return False
    p = getattr(user, "userprofile", None)
    return (
        user.is_superuser
        or (p and (p.is_senior_management or p.role in {"admin", "vp", "ceo"}))
    )

@login_required
@user_passes_test(_can_manage)
def evalform_list(request):
    dept = request.GET.get("department")
    forms = EvalForm.objects.select_related("department").order_by("-created_at")
    if dept and dept != "all":
        forms = forms.filter(department_id=dept)
    return render(request, "evaluation/forms/list.html", {"forms": forms})

@login_required
@user_passes_test(_can_manage)
def evalform_create(request):
    if request.method == "POST":
        form = EvalFormForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Deactivate any existing active forms of the same evaluation type for this department
                    EvalForm.objects.filter(
                        department=form.cleaned_data["department"], 
                        name=form.cleaned_data["name"],
                        is_active=True
                    ).update(is_active=False)
                    # Save the form with is_active=False by default
                    obj = form.save(commit=False)
                    obj.is_active = False
                    obj.save()
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
    return render(request, "evaluation/forms/create.html", {"form": form})

@login_required
@user_passes_test(_can_manage)
def evalform_edit(request, pk):
    obj = get_object_or_404(EvalForm, pk=pk)
    if request.method == "POST":
        form = EvalFormForm(request.POST, instance=obj)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Deactivate any existing active forms of the same evaluation type for this department
                    EvalForm.objects.filter(
                        department=form.cleaned_data["department"], 
                        name=form.cleaned_data["name"],
                        is_active=True
                    ).exclude(pk=obj.pk).update(is_active=False)
                    # Save the form with is_active=True
                    form_obj = form.save(commit=False)
                    form_obj.is_active = True
                    form_obj.save()
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
    return render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": obj})

@login_required
@user_passes_test(_can_manage)
def evalform_detail(request, pk):
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    qs = obj.questions.prefetch_related("choices").order_by('order')
    return render(request, "evaluation/forms/detail.html", {"form_obj": obj, "questions": qs})

@login_required
@user_passes_test(_can_manage)
def evalform_preview(request, pk):
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    form = PreviewEvalForm(eval_form=obj)
    return render(request, "evaluation/forms/preview.html", {"form_obj": obj, "preview_form": form})

@login_required
@user_passes_test(_can_manage)
def evalform_activate(request, pk):
    if request.method != "POST":
        return redirect("evaluation:evalform_detail", pk=pk)
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    
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
@user_passes_test(_can_manage)
def evalform_delete(request, pk):
    if request.method != "POST":
        return redirect("evaluation:evalform_list")
    
    obj = get_object_or_404(EvalForm, pk=pk)
    
    # Prevent deletion of active forms
    if obj.is_active:
        messages.error(request, f"Cannot delete '{obj.name}' - it is currently active. Please deactivate the form first.")
        return redirect("evaluation:evalform_list")
    
    form_name = obj.name
    obj.delete()
    
    messages.success(request, f"Form '{form_name}' has been deleted successfully.")
    return redirect("evaluation:evalform_list")

# ------- Questions -------
@login_required
@user_passes_test(_can_manage)
def question_add(request, form_id):
    ef = get_object_or_404(EvalForm, pk=form_id)
    if request.method == "POST":
        qf = QuestionForm(request.POST)
        if qf.is_valid():
            q = qf.save(commit=False)
            q.form = ef
            # Set order to be the next available order
            max_order = ef.questions.aggregate(max_order=Max('order'))['max_order'] or 0
            q.order = max_order + 1
            q.save()
            messages.success(request, "Question added.")
            return redirect("evaluation:evalform_detail", pk=ef.id)
    else:
        qf = QuestionForm()
    return render(request, "evaluation/forms/question_add.html", {"form": qf, "form_obj": ef})

@login_required
@user_passes_test(_can_manage)
def question_edit(request, question_id):
    q = get_object_or_404(Question, pk=question_id)
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
@user_passes_test(_can_manage)
def choice_add(request, question_id):
    q = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        cf = QuestionChoiceForm(request.POST)
        if cf.is_valid():
            c = cf.save(commit=False)
            c.question = q
            c.save()
            messages.success(request, "Choice added.")
            return redirect("evaluation:evalform_detail", pk=q.form_id)
    else:
        cf = QuestionChoiceForm()
    return render(request, "evaluation/forms/choice_add.html", {"form": cf, "question": q})


@login_required
@user_passes_test(_can_manage)
@require_http_methods(["POST"])
def update_question_order(request, pk):
    """Update the order of questions via AJAX"""
    try:
        form_obj = get_object_or_404(EvalForm, pk=pk)
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
@user_passes_test(_can_manage)
def question_delete(request, question_id):
    """Delete a question"""
    question = get_object_or_404(Question, id=question_id)
    form_obj = question.form
    
    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect("evaluation:evalform_detail", pk=form_obj.id)
    
    # If not POST, redirect to form detail
    return redirect("evaluation:evalform_detail", pk=form_obj.id)
