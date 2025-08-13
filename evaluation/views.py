# evaluation/views.py

from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db.models import Avg, Sum, F, FloatField, ExpressionWrapper, Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction

from authentication.models import UserProfile
from .forms import EvaluationForm, ManagerEvaluationForm
from .models import Evaluation, ReviewCycle, ManagerEvaluation


# --------------------------------------------------------------------
# Employee weekly evaluations (manager -> employees)  [YOUR ORIGINALS]
# --------------------------------------------------------------------

@login_required
def evaluation_dashboard(request):
    """
    Dashboard view: managers see their team's evaluations; admins see all.
    Supports optional search by employee name/username.
    """
    query = request.GET.get("q", "")
    profile = request.user.userprofile
    today = now().date()

    if profile.role == "admin":
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
    pending_evaluations = stats_qs.filter(status="pending") \
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


@login_required
def analytics_dashboard(request):
    profile = request.user.userprofile
    is_manager = profile.role == "manager" or profile.role == "admin"
    is_employee = profile.role not in ["manager", "admin"]

    employees = (UserProfile.objects.exclude(role="admin").exclude(pk=profile.pk)
                 if profile.role == "admin"
                 else (UserProfile.objects.filter(manager=profile).exclude(pk=profile.pk) if is_manager else []))

    cards = [
        {"id": "stat-5stars",       "icon": "fas fa-star",         "label": "5★ Reviews",        "negative": False},
        {"id": "stat-satisfaction", "icon": "fas fa-smile",        "label": "Avg Satisfaction",  "negative": False},
        {"id": "stat-revenue",      "icon": "fas fa-dollar-sign",  "label": "Total Revenue",     "negative": False},
        {"id": "stat-moves",        "icon": "fas fa-truck-moving", "label": "Moves Completed",   "negative": False},
        {"id": "stat-negative",     "icon": "fas fa-frown",        "label": "Negative Reviews",  "negative": True},
    ]

    pies = [
        {"title": "Avg Satisfaction", "id": "satisfactionPie"},
        {"title": "Avg Reliability",  "id": "reliabilityPie"},
        {"title": "Moves Completed",  "id": "movesPie"},
        {"title": "Avg Revenue",      "id": "revenuePie"},
    ]

    return render(request, "evaluation/analytics.html", {
        "is_manager": is_manager,
        "is_employee": is_employee,
        "employees": employees,
        "cards": cards,
        "pies": pies,
    })


@login_required
def team_totals_api(request):
    profile = request.user.userprofile

    # managers get their team; admins get all; everyone else gets just their own evals
    if profile.role == "manager":
        qs = Evaluation.objects.filter(manager=profile)
    elif profile.role == "admin":
        qs = Evaluation.objects.all()
    else:
        qs = Evaluation.objects.filter(employee=profile)

    # include only submitted evaluations
    qs = qs.filter(status="completed")

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

    # managers see only their team's evaluations; admins see all; employees see only their own
    if profile.role == "manager":
        qs = Evaluation.objects.filter(manager=profile)
    elif profile.role == "admin":
        qs = Evaluation.objects.all()
    else:
        qs = Evaluation.objects.filter(employee=profile)

    # optional employee filter still works for managers
    emp = request.GET.get("employee_id")
    if emp and emp != "all":
        qs = qs.filter(employee_id=emp)

    # only submitted evaluations
    qs = qs.filter(status="completed")

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
              total_moves=Sum("moves_within_schedule"),
          )
          .order_by("week_start")
    )

    return JsonResponse({
        "labels":       [x["week_start"].isoformat() for x in data],
        "satisfaction": [float(x["avg_satisfaction"] or 0) for x in data],
        "reliability":  [float(x["avg_reliability"]  or 0) for x in data],
        "revenue":      [float(x["avg_revenue"]      or 0) for x in data],
        "moves":        [int(x["total_moves"]        or 0) for x in data],
    })


@login_required
def metrics_by_employee_api(request):
    profile = request.user.userprofile
    if profile.role not in ["manager", "admin"]:
        return HttpResponseForbidden()

    if profile.role == "manager":
        qs = Evaluation.objects.filter(manager=profile)
    else:  # admin
        qs = Evaluation.objects.all()

    # only submitted evaluations
    qs = qs.filter(status="completed")

    start, end = request.GET.get("start"), request.GET.get("end")
    if start:
        qs = qs.filter(week_start__gte=start)
    if end:
        qs = qs.filter(week_start__lte=end)

    data = (
        qs.values("employee_id", "employee__user__first_name", "employee__user__last_name")
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
        "reliability":  [float(x["avg_reliability"]  or 0) for x in data],
        "revenue":      [float(x["avg_revenue"]      or 0) for x in data],
        "moves":        [int(x["total_moves"]        or 0) for x in data],
    })


# --------------------------------------------------------------------
# Senior‑management reviews of managers (monthly/quarterly/annual)
# --------------------------------------------------------------------

def _user_is_admin(profile: UserProfile) -> bool:
    return (getattr(profile, "is_admin", False)
            or profile.role == "admin"
            or profile.user.is_staff
            or profile.user.is_superuser)


def _user_is_senior(profile: UserProfile) -> bool:
    return (getattr(profile, "is_senior_management", False)
            or profile.role in {"llc/owner", "vp", "ceo"})


@login_required
def regular_reviews(request):
    """
    Senior/admin (reviewers): show cycles with count of THEIR assignments.
    Managers (subjects): show cycles with count of reviews ABOUT them.
    """
    profile = request.user.userprofile
    is_reviewer = _user_is_admin(profile) or _user_is_senior(profile)

    if is_reviewer:
        cycles = (
            ReviewCycle.objects.all()
            .annotate(
                my_items=Count(
                    "manager_evaluations",
                    filter=Q(manager_evaluations__reviewer=profile),
                ),
                my_pending=Count(
                    "manager_evaluations",
                    filter=Q(
                        manager_evaluations__reviewer=profile,
                        manager_evaluations__status="pending",
                    ),
                ),
            )
        )
    else:
        # Managers see cycles where they are the subject
        cycles = (
            ReviewCycle.objects.filter(manager_evaluations__subject_manager=profile)
            .distinct()
            .annotate(
                my_items=Count(
                    "manager_evaluations",
                    filter=Q(manager_evaluations__subject_manager=profile),
                ),
                my_pending=Count(
                    "manager_evaluations",
                    filter=Q(
                        manager_evaluations__subject_manager=profile,
                        manager_evaluations__status="pending",
                    ),
                ),
            )
        )

    return render(request, "evaluation/regular_reviews.html", {"cycles": cycles})


@login_required
def cycle_assignments(request, cycle_id: int):
    """
    Show assignments for a given cycle.
    Senior/admin (reviewers): see their assigned manager reviews.
    Managers: see reviews about them (read-only).
    """
    profile = request.user.userprofile
    cycle = get_object_or_404(ReviewCycle, pk=cycle_id)

    is_reviewer = _user_is_admin(profile) or _user_is_senior(profile)
    is_manager = getattr(profile, "is_manager", False) or profile.role == "manager"

    if is_reviewer:
        assignments = (ManagerEvaluation.objects
                       .filter(cycle=cycle, reviewer=profile)
                       .select_related("subject_manager__user")
                       .order_by("subject_manager__user__last_name"))
    else:
        assignments = (ManagerEvaluation.objects
                       .filter(cycle=cycle, subject_manager=profile)
                       .select_related("reviewer__user"))

    return render(request, "evaluation/cycle_assignments.html", {
        "cycle": cycle,
        "assignments": assignments,
        "is_reviewer": is_reviewer,
        "is_manager": is_manager,
    })



@login_required
def evaluate_manager(request, evaluation_id: int):
    ev = get_object_or_404(ManagerEvaluation, pk=evaluation_id)
    profile = request.user.userprofile

    if not (_user_is_admin(profile) or _user_is_senior(profile)):
        return redirect("evaluation:regular_reviews")
    if ev.reviewer != profile:
        return redirect("evaluation:regular_reviews")

    # If cycle closed and not already completed, block access
    if not ev.cycle.is_open and ev.status != "completed":
        return redirect("evaluation:cycle_assignments", cycle_id=ev.cycle_id)

    # If already completed and no ?edit=1, show read-only
    if request.method == "GET" and ev.status == "completed" and request.GET.get("edit") != "1":
        return render(request, "evaluation/manager_review_detail.html", {
            "evaluation": ev,
            "cycle": ev.cycle,
            "subject": ev.subject_manager,
            "can_edit": ev.cycle.is_open,  # allow edit button if cycle still open
        })

    # If POST, also block edits when cycle is closed
    if request.method == "POST" and not ev.cycle.is_open:
        return redirect("evaluation:cycle_assignments", cycle_id=ev.cycle_id)

    if request.method == "POST":
        form = ManagerEvaluationForm(request.POST, instance=ev, cycle=ev.cycle)
        if form.is_valid():
            with transaction.atomic():
                obj = form.save(commit=False)
                obj.status = "completed"
                obj.submitted_at = now()
                obj.save()

                # Notify the subject manager
                try:
                    detail_url = f"{settings.BASE_URL}{reverse('evaluation:manager_review_detail', args=[obj.id])}"
                    ctx = {
                        "subject_name": obj.subject_manager.user.get_full_name() or obj.subject_manager.user.username,
                        "reviewer_name": obj.reviewer.user.get_full_name() or obj.reviewer.user.username,
                        "cycle": obj.cycle,
                        "detail_url": detail_url,
                    }
                    txt = render_to_string("evaluation/email/manager_review_submitted.txt", ctx)
                    html = render_to_string("evaluation/email/manager_review_submitted.html", ctx)
                    to_addr = obj.subject_manager.user.email
                    if to_addr:
                        msg = EmailMultiAlternatives(
                            subject=f"Your {obj.cycle.get_cycle_type_display()} review was submitted",
                            body=txt,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[to_addr],
                        )
                        msg.attach_alternative(html, "text/html")
                        msg.send()
                except Exception:
                    # swallow email errors but keep the saved review
                    pass

            messages.success(request, "Review submitted.")
            return redirect("evaluation:evaluate_manager", evaluation_id=obj.id)
    else:
        form = ManagerEvaluationForm(instance=ev, cycle=ev.cycle)

    return render(request, "evaluation/evaluate_manager.html", {
        "form": form,
        "evaluation": ev,
        "cycle": ev.cycle,
        "subject": ev.subject_manager,
    })



@login_required
def manager_review_detail(request, evaluation_id: int):
    """
    Explicit read-only detail route (in case you want to link to it elsewhere).
    """
    ev = get_object_or_404(ManagerEvaluation, pk=evaluation_id)
    profile = request.user.userprofile

    # Reviewer or subject manager can view
    if not (
        (_user_is_admin(profile) or _user_is_senior(profile)) and ev.reviewer == profile
        or ev.subject_manager == profile
    ):
        return redirect("evaluation:regular_reviews")

    return render(request, "evaluation/manager_review_detail.html", {
        "evaluation": ev,
        "cycle": ev.cycle,
        "subject": ev.subject_manager,
        "can_edit": (_user_is_admin(profile) or _user_is_senior(profile)) and ev.reviewer == profile and ev.cycle.is_open,
    })



@login_required
def my_manager_reviews(request):
    """
    Managers see reviews they've received (completed only), compact list with pagination.
    """
    profile = request.user.userprofile
    qs = (
        ManagerEvaluation.objects
        .filter(subject_manager=profile, status="completed")
        .select_related("cycle", "reviewer__user")
        .only(
            "id", "overall_rating", "submitted_at", "subject_manager_id",
            "cycle__cycle_type", "cycle__period_start", "cycle__period_end",
            "reviewer__user__first_name", "reviewer__user__last_name", "reviewer__user__username",
        )
        .order_by("-cycle__period_start", "-submitted_at")
    )

    paginator = Paginator(qs, 10)  # 10 per page
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(request, "evaluation/my_manager_reviews.html", {"page_obj": page_obj})

@login_required
def senior_pending_reviews(request):
    """
    Senior management dashboard of pending ManagerEvaluations they must complete,
    with per-cycle progress.
    """
    profile = request.user.userprofile
    if not (_user_is_senior(profile) or _user_is_admin(profile)):  # if admins shouldn't see it, drop _user_is_admin
        return redirect("evaluation:regular_reviews")

    # Per-cycle progress for THIS reviewer
    cycles = (
        ReviewCycle.objects
        .filter(manager_evaluations__reviewer=profile)
        .distinct()
        .annotate(
            total=Count("manager_evaluations", filter=Q(manager_evaluations__reviewer=profile)),
            done=Count("manager_evaluations", filter=Q(manager_evaluations__reviewer=profile, manager_evaluations__status="completed")),
            pending=Count("manager_evaluations", filter=Q(manager_evaluations__reviewer=profile, manager_evaluations__status="pending")),
        )
        .order_by("-period_start")
    )

    # Flat list of pending items to act on
    pending_items = (
        ManagerEvaluation.objects
        .filter(reviewer=profile, status="pending")
        .select_related("subject_manager__user", "cycle")
        .order_by("-cycle__period_start", "subject_manager__user__last_name")
    )

    return render(request, "evaluation/senior_pending.html", {
        "cycles": cycles,
        "pending_items": pending_items,
    })
