from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from evaluation.models import Evaluation
from authentication.models import UserProfile

class Command(BaseCommand):
    help = (
        "Mondays: create weekly evaluations for all employees.  "
        "Fridays: email managers with any still-pending evaluations."
    )

    def handle(self, *args, **options):
        today = now().date()
        weekday = today.weekday()  # Monday=0 ... Friday=4

        # Compute this Monday and Sunday
        this_monday = today - timedelta(days=weekday)
        this_sunday = this_monday + timedelta(days=6)

        # --- MONDAY: create evals ---
        if weekday == 1:
            self.stdout.write("🔨 Monday: creating weekly evaluations...")
            created_count = 0

            # For each manager, create one Evaluation per direct report
            managers = UserProfile.objects.filter(role="manager")
            for mgr in managers:
                team = UserProfile.objects.filter(manager=mgr)
                for emp in team:
                    ev, was_created = Evaluation.objects.get_or_create(
                        manager=mgr,
                        employee=emp,
                        week_start=this_monday,
                        week_end=this_sunday,
                        defaults={"status": "pending"},
                    )
                    if was_created:
                        created_count += 1

            self.stdout.write(f"✅ Created {created_count} evaluations for week {this_monday}–{this_sunday}")

        # --- FRIDAY: send reminders ---
        elif weekday == 4:
            self.stdout.write("✉️ Friday: sending pending‐eval reminders...")
            # Find all pending evals for THIS week
            pending_qs = Evaluation.objects.filter(
                week_start=this_monday,
                status="pending"
            ).select_related("manager__user", "employee__user")

            # Group by manager
            reminders = {}
            for ev in pending_qs:
                mgr = ev.manager
                reminders.setdefault(mgr, []).append(ev)

            for mgr, evs in reminders.items():
                user = mgr.user
                email = user.email
                if not email:
                    self.stdout.write(f"⚠️ No email for manager {user.username}, skipping.")
                    continue

                # Build email
                subject = "Reminder: Complete Pending Evaluations"
                lines = [
                    f"Hello {user.get_full_name()},",
                    "",
                    f"You have {len(evs)} evaluation(s) still pending for the week {this_monday} to {this_sunday}:",
                    "",
                ]
                for ev in evs:
                    emp_name = ev.employee.user.get_full_name()
                    lines.append(f"  • {emp_name}")
                lines += [
                    "",
                    "Please complete these by Sunday, otherwise your access to the platform may be restricted until you submit all the pending evaluations.",
                    "",
                    f"👉 {settings.BASE_URL}/evaluation/pending/",
                ]
                body = "\n".join(lines)

                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                self.stdout.write(f"✉️ Sent reminder to {email}")

        else:
            self.stdout.write("🛑 Not Monday or Friday – nothing to do.")
