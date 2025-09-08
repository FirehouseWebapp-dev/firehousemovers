from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch

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
            with transaction.atomic():
                if form.cleaned_data["is_active"]:
                    EvalForm.objects.filter(department=form.cleaned_data["department"], is_active=True).update(is_active=False)
                obj = form.save()
            messages.success(request, "Form created.")
            return redirect("evaluation:evalform_detail", pk=obj.id)
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
            with transaction.atomic():
                if form.cleaned_data["is_active"]:
                    EvalForm.objects.filter(department=form.cleaned_data["department"], is_active=True).exclude(pk=obj.pk).update(is_active=False)
                form.save()
            messages.success(request, "Form updated.")
            return redirect("evaluation:evalform_detail", pk=obj.id)
    else:
        form = EvalFormForm(instance=obj)
    return render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": obj})

@login_required
@user_passes_test(_can_manage)
def evalform_detail(request, pk):
    obj = get_object_or_404(EvalForm.objects.select_related("department"), pk=pk)
    qs = obj.questions.prefetch_related("choices").all()
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
    with transaction.atomic():
        EvalForm.objects.filter(department=obj.department, is_active=True).exclude(pk=obj.pk).update(is_active=False)
        if not obj.is_active:
            obj.is_active = True
            obj.save(update_fields=["is_active"])
    messages.success(request, f"‘{obj.name}’ is now active for {obj.department.title}.")
    return redirect("evaluation:evalform_detail", pk=obj.id)

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
