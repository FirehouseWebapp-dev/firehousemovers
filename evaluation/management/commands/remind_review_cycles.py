# evaluation/management/commands/remind_review_cycles.py
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Q, Count
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from datetime import timedelta

from evaluation.models import ReviewCycle, ManagerEvaluation

class BaseCommandError(Exception):
    pass

class Command(BaseCommand):
    help = "Run daily. For cycles ending in 2 days, email seniors who still have pending reviews in that cycle."

    def handle(self, *args, **kwargs):
        today = now().date()
        target_end = today + timedelta(days=2)

        cycles = ReviewCycle.objects.filter(period_end=target_end)
        if not cycles.exists():
            self.stdout.write("No cycles ending in 2 days; nothing to remind.")
            return

        total_sent = 0

        for cycle in cycles:
            # For each reviewer, do they have pending items in this cycle?
            by_reviewer = (
                ManagerEvaluation.objects
                .filter(cycle=cycle, status="pending")
                .values("reviewer_id",
                        "reviewer__user__first_name",
                        "reviewer__user__last_name",
                        "reviewer__user__email")
                .annotate(pending_count=Count("id"))
            )

            for row in by_reviewer:
                email = row["reviewer__user__email"]
                if not email:
                    continue
                try:
                    cycle_url = f"{settings.BASE_URL}{reverse('evaluation:cycle_assignments', args=[cycle.id])}"
                    ctx = {
                        "reviewer_name": f"{row['reviewer__user__first_name']} {row['reviewer__user__last_name']}".strip(),
                        "cycle": cycle,
                        "pending_count": row["pending_count"],
                        "cycle_url": cycle_url,
                    }
                    subject = f"Reminder: {cycle.get_cycle_type_display()} reviews due in 2 days ({cycle.period_end})"
                    text_body = render_to_string("evaluation/email/review_cycle_reminder.txt", ctx)
                    html_body = render_to_string("evaluation/email/review_cycle_reminder.html", ctx)
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                    )
                    msg.attach_alternative(html_body, "text/html")
                    msg.send()
                    total_sent += 1
                except Exception as e:
                    self.stdout.write(f"⚠️ Failed reminder to {email}: {e}")

        self.stdout.write(f"Sent {total_sent} reminder email(s).")
