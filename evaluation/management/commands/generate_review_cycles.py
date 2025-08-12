from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db import models
from datetime import date, timedelta

from evaluation.models import ReviewCycle, ManagerEvaluation
from authentication.models import UserProfile


def month_bounds(d: date):
    start = d.replace(day=1)
    # last day of month
    if start.month == 12:
        end = date(start.year, 12, 31)
    else:
        end = date(start.year, start.month + 1, 1) - timedelta(days=1)
    return start, end


def quarter_bounds(d: date):
    """Return start/end for the quarter that contains d."""
    q = (d.month - 1) // 3  # 0..3
    start_month = q * 3 + 1
    start = date(d.year, start_month, 1)
    last_month = start_month + 2
    if last_month == 12:
        end = date(d.year, 12, 31)
    else:
        end = date(d.year, last_month + 1, 1) - timedelta(days=1)
    return start, end


def year_bounds(d: date):
    return date(d.year, 1, 1), date(d.year, 12, 31)


class Command(BaseCommand):
    help = (
        "Run daily.\n"
        " • 15th: create Monthly cycle + assignments for that month.\n"
        " • Mar/Jun/Sep/Dec 15th: create Quarterly cycle + assignments for that quarter.\n"
        " • Dec 1st: create Annual cycle + assignments for the current year.\n"
        "Assignments are senior reviewers -> their direct-report managers only."
    )

    def handle(self, *args, **opts):
        today = now().date()

        did_anything = False
        log_lines = []

        # Seniors (NOT admins). Adjust this if you want admins included.
        seniors = (
            UserProfile.objects.filter(
                models.Q(is_senior_management=True) | models.Q(role__in=["ceo", "vp", "llc/owner"])
            )
            .exclude(role="admin")
            .distinct()
        )

        def ensure_cycle_and_assign_for_reviewer(cycle_type: str, start: date, end: date, reviewer: UserProfile):
            nonlocal did_anything
            cycle, created = ReviewCycle.objects.get_or_create(
                cycle_type=cycle_type, period_start=start, period_end=end
            )
            if created:
                did_anything = True
                log_lines.append(f"Created {cycle.get_cycle_type_display()} cycle: {start} → {end}")

            # Reviewer's direct reports who are MANAGERS
            directs = (
                UserProfile.objects
                .filter(manager=reviewer, role="manager")
                .distinct()
            )
            if not directs.exists():
                return 0

            created_count = 0
            for mgr in directs.exclude(pk=reviewer.pk):  # safety: no self-review
                _, was_created = ManagerEvaluation.objects.get_or_create(
                    cycle=cycle, reviewer=reviewer, subject_manager=mgr,
                    defaults={"status": "pending"},
                )
                if was_created:
                    created_count += 1
            return created_count

        plans = []

        # ---- TRIGGERS ----
        is_15th = (today.day == 15)
        is_quarter_end_month = today.month in (3, 6, 9, 12)
        is_dec_1 = (today.month == 12 and today.day == 1)

        # Monthly: 15th of every month
        if is_15th:
            m_start, m_end = month_bounds(today)
            plans.append(("monthly", m_start, m_end))

        # Quarterly: 15th of the LAST month in the quarter (Mar/Jun/Sep/Dec)
        if is_15th and is_quarter_end_month:
            q_start, q_end = quarter_bounds(today)
            plans.append(("quarterly", q_start, q_end))

        # Annual: Dec 1st
        if is_dec_1:
            y_start, y_end = year_bounds(today)
            plans.append(("annual", y_start, y_end))

        if not plans:
            self.stdout.write("Nothing to do today.")
            return

        for cycle_type, start, end in plans:
            cycle_total = 0
            for reviewer in seniors:
                cycle_total += ensure_cycle_and_assign_for_reviewer(cycle_type, start, end, reviewer)
            if cycle_total:
                did_anything = True
                log_lines.append(f"Assignments created for {cycle_type}: {cycle_total}")

        if not did_anything:
            log_lines.append("No new cycles or assignments created.")

        for line in log_lines:
            self.stdout.write(line)
