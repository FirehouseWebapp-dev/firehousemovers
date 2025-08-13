# evaluation/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.db.models import Avg, Sum, F, FloatField, ExpressionWrapper, Q
from datetime import timedelta
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse, HttpResponseForbidden
from authentication.models import UserProfile
from .models import Evaluation
from .forms import EvaluationForm

@login_required
def evaluation_dashboard(request):
    """
    Manager view: list all evaluations, with optional search.
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
    Manager view: display & handle single evaluation form.
    Sends email to the employee upon submission.
    """
    evaluation = get_object_or_404(Evaluation, pk=evaluation_id)
    manager = request.user.userprofile

    # only the assigned manager may access
    if evaluation.manager != manager:
        return redirect("evaluation:dashboard")

    # editable while within the week window
    is_editable = (now().date() <= evaluation.week_end)
    can_submit = is_editable or (evaluation.submitted_at is None)

    if request.method == "POST" and can_submit:
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.status = "completed"
            ev.submitted_at = now()
            ev.save()

            detail_path = reverse("evaluation:my_evaluation_detail", args=[ev.id])
            evaluation_url = f"{settings.BASE_URL}{detail_path}"

            # plain-text fallback
            text_content = (
                f"Hi {ev.employee.user.get_full_name()},\n\n"
                f"Your manager {ev.manager.user.get_full_name()} has submitted your evaluation "
                f"for the week {ev.week_start} to {ev.week_end}.\n"
                f"View it here: {evaluation_url}\n\n"
                "Thanks,"
            )

            # render the HTML template
            html_content = render_to_string(
                "evaluation/email/evaluation_submitted.html",
                {"ev": ev, "evaluation_url": evaluation_url}
            )

            # construct and send
            msg = EmailMultiAlternatives(
                subject=f"Your evaluation for {ev.week_start}–{ev.week_end} is ready",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[ev.employee.user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect("evaluation:dashboard")
    else:
        form = EvaluationForm(instance=evaluation)

    return render(request, "evaluation/evaluate_employee.html", {
        "form": form,
        "evaluation": evaluation,
        "employee": evaluation.employee,
        "week_start": evaluation.week_start,
        "week_end": evaluation.week_end,
        "is_editable": is_editable,
        "can_submit": can_submit,
    })


@login_required
def pending_evaluation_view(request):
    """
    Manager view: show progress & list of pending evaluations
    for last week and this week.
    """
    profile = request.user.userprofile
    today = now().date()
    weekday = today.weekday()

    # compute Mondays
    this_monday = today - timedelta(days=weekday)
    last_monday = this_monday - timedelta(days=7)

    # stats for both weeks
    stats_qs = Evaluation.objects.filter(
        manager=profile,
        week_start__in=[last_monday, this_monday],
    )
    total = stats_qs.count()
    completed = stats_qs.filter(status="completed").count()
    percent_complete = int((completed / total) * 100) if total else 100

    # list only those still pending
    pending_evaluations = stats_qs.filter(status="pending")\
        .order_by('-week_start', 'employee__user__last_name')

    return render(request, "evaluation/pending.html", {
        "pending_evaluations": pending_evaluations,
        "total": total,
        "completed": completed,
        "percent_complete": percent_complete,
    })


@login_required
def my_evaluations(request):
    """
    Employee view: list all completed evaluations for this user.
    """
    profile = request.user.userprofile
    evaluations = (
        Evaluation.objects
        .filter(employee=profile, status="completed")
        .select_related("manager__user")
        .order_by("-week_start")
    )
    return render(request, "evaluation/my_evaluations.html", {
        "evaluations": evaluations,
    })


@login_required
def evaluation_detail(request, evaluation_id):
    """
    Employee view: detail page for a single evaluation.
    """
    profile = request.user.userprofile
    evaluation = get_object_or_404(
        Evaluation,
        pk=evaluation_id,
        employee=profile,
    )
    return render(request, "evaluation/evaluation_detail.html", {
        "evaluation": evaluation,
    })

from django.shortcuts       import render
from django.contrib.auth.decorators import login_required
from django.http           import JsonResponse, HttpResponseForbidden
from django.db.models      import Avg, Sum, F, FloatField, ExpressionWrapper
from .models               import Evaluation
from authentication.models import UserProfile

@login_required
def analytics_dashboard(request):
   profile    = request.user.userprofile
    is_manager = profile.role == "manager"
    is_employee = profile.role != "manager"
    employees  = UserProfile.objects.filter(manager=profile) if is_manager else []

    cards = [
       {"id":"stat-5stars",      "icon":"fas fa-star",          "label":"5★ Reviews",       "negative":False},
        {"id":"stat-satisfaction","icon":"fas fa-smile",        "label":"Avg Satisfaction", "negative":False},
        {"id":"stat-revenue",     "icon":"fas fa-dollar-sign",  "label":"Total Revenue",    "negative":False},
        {"id":"stat-moves",       "icon":"fas fa-truck-moving", "label":"Moves Completed",  "negative":False},
        {"id":"stat-negative",    "icon":"fas fa-frown",        "label":"Negative Reviews","negative":True},
    ]

    pies = [
        {"title":"Avg Satisfaction","id":"satisfactionPie"},
        {"title":"Avg Reliability", "id":"reliabilityPie"},
        {"title":"Moves Completed", "id":"movesPie"},
        {"title":"Avg Revenue",     "id":"revenuePie"},
    ]

    return render(request, "evaluation/analytics.html", {
        "is_manager": is_manager,
        "is_employee": is_employee,
         "employees":  employees,
        "cards":      cards,
        "pies":       pies,
    })

@login_required
def team_totals_api(request):
    profile = request.user.userprofile

    # managers get their team; everyone else gets just their own evals
    if profile.role == "manager":
        qs = Evaluation.objects.filter(manager=profile)
    else:
        qs = Evaluation.objects.filter(employee=profile)
    # optional date filters
    start, end = request.GET.get("start"), request.GET.get("end")
    if start:
        qs = qs.filter(week_start__gte=start)
    if end:
        qs = qs.filter(week_start__lte=end)

    # aggregates
    total_5_star = qs.aggregate(sum=Sum("five_star_reviews"))["sum"] or 0
    avg_satisfaction = qs.aggregate(avg=Avg("avg_customer_satisfaction_score"))["avg"] or 0
    total_moves = qs.aggregate(sum=Sum("moves_within_schedule"))["sum"] or 0
    total_negative = qs.aggregate(sum=Sum("negative_reviews"))["sum"] or 0

    revenue_expr = ExpressionWrapper(
        F("avg_revenue_per_move") * F("moves_within_schedule"),
        output_field=FloatField()
    )
    total_revenue = qs.aggregate(sum=Sum(revenue_expr))["sum"] or 0

    return JsonResponse({
        "total_5_star":     total_5_star,
        "avg_satisfaction": round(avg_satisfaction, 2),
        "total_revenue":    round(total_revenue,    2),
        "total_moves":      total_moves,
        "total_negative":   total_negative,
    })


@login_required
def metrics_api(request):
    profile = request.user.userprofile

    # managers see only their team's evaluations,
    # employees see only their own
    if profile.role == "manager":
        qs = Evaluation.objects.filter(manager=profile)
    else:
        qs = Evaluation.objects.filter(employee=profile)

    # optional employee filter still works for managers
    emp = request.GET.get("employee_id")
    if emp and emp!="all":
        qs = qs.filter(employee_id=emp)

    # date filtering
    start, end = request.GET.get("start"), request.GET.get("end")
    if start:
        qs = qs.filter(week_start__gte=start)
    if end:
        qs = qs.filter(week_start__lte=end)

    # annotate & return
    data = (
        qs.values("week_start")
          .annotate(
              avg_satisfaction=Avg("avg_customer_satisfaction_score"),
              avg_reliability=Avg("reliability_rating"),
              avg_revenue=Avg("avg_revenue_per_move"),
              total_moves=  Sum("moves_within_schedule"),
          )
          .order_by("week_start")
    )

    return JsonResponse({
        "labels":       [x["week_start"].isoformat() for x in data],
        "satisfaction": [float(x["avg_satisfaction"] or 0) for x in data],
        "reliability":  [float(x["avg_reliability"]  or 0) for x in data],
        "revenue":      [float(x["avg_revenue"]      or 0) for x in data],
        "moves":        [int(x["total_moves"]       or 0) for x in data],
    })



@login_required
def metrics_by_employee_api(request):
    profile = request.user.userprofile
    if profile.role != "manager":
        return HttpResponseForbidden()
    qs = Evaluation.objects.filter(manager=profile)
    start, end = request.GET.get("start"), request.GET.get("end")
    if start: qs = qs.filter(week_start__gte=start)
    if end:   qs = qs.filter(week_start__lte=end)

    data = (
        qs.values("employee_id","employee__user__first_name","employee__user__last_name")
          .annotate(
              avg_satisfaction=Avg("avg_customer_satisfaction_score"),
              avg_reliability=Avg("reliability_rating"),
              avg_revenue=Avg("avg_revenue_per_move"),
              total_moves=Sum("moves_within_schedule"),
          )
          .order_by("employee__user__last_name")
    )

    labels = [
        f"{x['employee__user__first_name']} {x['employee__user__last_name']}"
        for x in data
    ]
    return JsonResponse({
        "labels":       labels,
        "satisfaction": [float(x["avg_satisfaction"] or 0) for x in data],
        "reliability":  [float(x["avg_reliability"] or 0)  for x in data],
        "revenue":      [float(x["avg_revenue"] or 0)      for x in data],
        "moves":        [int(x["total_moves"] or 0)        for x in data],
    })
