# evaluation/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Q
from datetime import timedelta

from .models import Evaluation
from .forms import EvaluationForm

@login_required
def evaluation_dashboard(request):
    """
    Show all evaluations for this manager, with optional search.
    """
    query = request.GET.get("q", "")
    manager = request.user.userprofile
    today = now().date()

    evaluations = (
        Evaluation.objects
        .filter(manager=manager)
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
def evaluate_employee(request, evaluation_id):
    """
    Display & handle the evaluation form.
    Only the assigned manager may access.
    Submission is allowed only if evaluation.submitted_at is still None.
    """
    evaluation = get_object_or_404(Evaluation, pk=evaluation_id)
    manager = request.user.userprofile

    # Block anyone but the assigned manager
    if evaluation.manager != manager:
        return redirect("evaluation:dashboard")

    # Only allow edits/submission if never submitted
    can_submit = evaluation.submitted_at is None

    if request.method == "POST" and can_submit:
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.status = "completed"
            ev.submitted_at = now()
            ev.save()
            return redirect("evaluation:dashboard")
    else:
        form = EvaluationForm(instance=evaluation)

    return render(request, "evaluation/evaluate_employee.html", {
        "form": form,
        "evaluation": evaluation,
        "employee": evaluation.employee,
        "week_start": evaluation.week_start,
        "week_end": evaluation.week_end,
        "can_submit": can_submit,
    })


@login_required
def pending_evaluation_view(request):
    profile = request.user.userprofile
    today = now().date()
    weekday = today.weekday()

    # Compute this week’s and last week’s Mondays
    this_monday = today - timedelta(days=weekday)
    last_monday = this_monday - timedelta(days=7)

    # For the progress bar: all tasks in those two weeks
    stats_qs = Evaluation.objects.filter(
        manager=profile,
        week_start__in=[last_monday, this_monday],
    )
    total = stats_qs.count()
    completed = stats_qs.filter(status="completed").count()
    percent_complete = int((completed / total) * 100) if total else 100

    # But the list itself is *only* the pending ones
    pending_evaluations = stats_qs.filter(status="pending")\
        .order_by('-week_start', 'employee__user__last_name')

    return render(request, "evaluation/pending.html", {
        "pending_evaluations": pending_evaluations,
        "total": total,
        "completed": completed,
        "percent_complete": percent_complete,
    })