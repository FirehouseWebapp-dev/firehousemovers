from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from datetime import date, timedelta

from evaluation.models import ReviewCycle, ManagerEvaluation
from authentication.models import UserProfile


def month_bounds(d: date):
    start = d.replace(day=1)
    if start.month == 12:
        end = date(start.year, 12, 31)
    else:
        end = date(start.year, start.month + 1, 1) - timedelta(days=1)
    return start, end

def quarter_bounds(d: date):
    q = (d.month - 1) // 3
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
        "Also sends reminder emails 2 days before cycle period_end to seniors with pending items.\n"
        "Assignments are senior reviewers -> their direct-report managers only."
    )

    def handle(self, *args, **opts):
        today = now().date()
        log_lines = []
        did_anything = False

        seniors = (
            UserProfile.objects.filter(
                models.Q(is_senior_management=True) | models.Q(role__in=["ceo", "vp", "llc/owner"])
            )
            .exclude(role="admin")
            .distinct()
        )

        def ensure_cycle_and_assign_for_reviewer(cycle_type: str, start: date, end: date, reviewer: UserProfile) -> int:
            """Create (or get) the cycle and ensure assignments for this reviewer’s direct-report managers.
               Returns number of NEW assignments created."""
            nonlocal did_anything
            cycle, created = ReviewCycle.objects.get_or_create(
                cycle_type=cycle_type, period_start=start, period_end=end
            )
            if created:
                did_anything = True
                log_lines.append(f"Created {cycle.get_cycle_type_display()} cycle: {start} → {end}")

            directs = (
                UserProfile.objects
                .filter(manager=reviewer, role="manager")
                .distinct()
            )
            if not directs.exists():
                return 0

            created_count = 0
            for mgr in directs.exclude(pk=reviewer.pk):
                _, was_created = ManagerEvaluation.objects.get_or_create(
                    cycle=cycle, reviewer=reviewer, subject_manager=mgr,
                    defaults={"status": "pending"},
                )
                if was_created:
                    created_count += 1
            return created_count

        # --- Creation triggers -------------------------------------------------
        is_15th = (today.day == 15)
        is_quarter_end_month = today.month in (3, 6, 9, 12)
        is_dec_1 = (today.month == 12 and today.day == 1)

        plans = []
        # Always keep monthly up to date (so you can run daily without waiting for 15th)
        m_start, m_end = month_bounds(today)
        plans.append(("monthly", m_start, m_end))

        if is_15th and is_quarter_end_month:
            q_start, q_end = quarter_bounds(today)
            plans.append(("quarterly", q_start, q_end))
        if is_dec_1:
            y_start, y_end = year_bounds(today)
            plans.append(("annual", y_start, y_end))

        if not plans:
            self.stdout.write("Nothing to do today (no cycles to create).")

        # Create assignments + notify reviewers who just got NEW items
        for cycle_type, start, end in plans:
            total_new_for_cycle = 0
            for reviewer in seniors:
                new_count = ensure_cycle_and_assign_for_reviewer(cycle_type, start, end, reviewer)
                total_new_for_cycle += new_count

                if new_count and reviewer.user.email:
                    cycle = ReviewCycle.objects.get(cycle_type=cycle_type, period_start=start, period_end=end)
                    list_url = f"{settings.BASE_URL}{reverse('evaluation:cycle_assignments', args=[cycle.id])}"
                    ctx = {
                        "reviewer_name": reviewer.user.get_full_name() or reviewer.user.username,
                        "cycle": cycle,
                        "new_count": new_count,
                        "list_url": list_url,
                    }
                    txt = render_to_string("evaluation/email/reviewer_assignments_created.txt", ctx)
                    html = render_to_string("evaluation/email/reviewer_assignments_created.html", ctx)
                    msg = EmailMultiAlternatives(
                        subject=f"{cycle.get_cycle_type_display()} reviews assigned ({new_count})",
                        body=txt,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[reviewer.user.email],
                    )
                    msg.attach_alternative(html, "text/html")
                    msg.send()

            if total_new_for_cycle:
                did_anything = True
                log_lines.append(f"Assignments created for {cycle_type}: {total_new_for_cycle}")

        # --- Reminder block: 2 days before deadline ---------------------------
        reminder_target = today + timedelta(days=2)
        # Recommended (prevents spamming all cycles):
        # cycles_due_soon = ReviewCycle.objects.filter(period_end=reminder_target)
        cycles_due_soon = ReviewCycle.objects.all()

        total_reminders_sent = 0  # <-- ADDED

        for cycle in cycles_due_soon:
            sent_for_cycle = 0           # <-- ADDED
            recipients_for_cycle = []    # <-- ADDED

            # Aggregate pending counts per reviewer for this cycle
            pending_q = (
                ManagerEvaluation.objects.filter(
                    cycle=cycle,
                    status__in=["pending"]  # add "in_progress" if you want to nudge those too
                ).values("reviewer").annotate(pending_count=models.Count("id"))
            )
            reviewers_with_pending = pending_q.count()  # <-- ADDED (safe vs truthiness)

            for row in pending_q:
                try:
                    reviewer = UserProfile.objects.get(pk=row["reviewer"])
                except UserProfile.DoesNotExist:
                    continue
                if not reviewer.user.email:
                    continue

                pending_count = row["pending_count"]
                if pending_count <= 0:
                    continue

                list_url = f"{settings.BASE_URL}{reverse('evaluation:cycle_assignments', args=[cycle.id])}"
                ctx = {
                    "reviewer_name": reviewer.user.get_full_name() or reviewer.user.username,
                    "cycle": cycle,
                    "pending_count": pending_count,
                    "deadline": cycle.period_end,
                    "list_url": list_url,
                }
                txt = render_to_string("evaluation/email/review_cycle_reminder.txt", ctx)
                html = render_to_string("evaluation/email/review_cycle_reminder.html", ctx)
                msg = EmailMultiAlternatives(
                    subject=f"Reminder: {pending_count} {cycle.get_cycle_type_display()} review(s) due by {cycle.period_end:%b %d}",
                    body=txt,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[reviewer.user.email],
                )
                msg.attach_alternative(html, "text/html")
                msg.send()

                did_anything = True
                sent_for_cycle += 1                 # <-- ADDED
                total_reminders_sent += 1           # <-- ADDED
                recipients_for_cycle.append(reviewer.user.email)

            # Debug/logging ---------------------------------------------
            if sent_for_cycle:
                log_lines.append(
                    f"Sent {sent_for_cycle} reminder email(s) for "
                    f"{cycle.get_cycle_type_display()} ({cycle.period_start} → {cycle.period_end}). "
                    f"Recipients: {', '.join(recipients_for_cycle)}"
                )
            elif reviewers_with_pending:
                log_lines.append(
                    f"{reviewers_with_pending} reviewer(s) had pending items for "
                    f"{cycle.get_cycle_type_display()} ({cycle.period_start} → {cycle.period_end}), "
                    f"but 0 emails were sent (likely missing email addresses)."
                )
            else:
                log_lines.append(
                    f"No pending items to remind for {cycle.get_cycle_type_display()} "
                    f"({cycle.period_start} → {cycle.period_end})."
                )

        # Final summary line
        log_lines.append(f"Total reminder emails sent today: {total_reminders_sent}")  # <-- ADDED


        if not did_anything:
            log_lines.append("No new cycles/assignments created and no reminders to send today.")

        for line in log_lines:
            self.stdout.write(line)
