from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings

from evaluation.models import Evaluation
from authentication.models import UserProfile


class Command(BaseCommand):
    help = (
        "Mondays: create weekly evaluations for all employees who report to a manager. "
        "Fridays: email managers with any still-pending evaluations for the current week."
    )

    def handle(self, *args, **options):
        today = now().date()
        weekday = today.weekday()  # Monday=0 ... Sunday=6

        # Compute this Monday and Sunday of current week
        this_monday = today - timedelta(days=weekday)
        this_sunday = this_monday + timedelta(days=6)

        # --- MONDAY: create evals ---
        if weekday == 0:
            self.stdout.write("🔨 Monday: creating weekly evaluations...")
            created_count = 0

            # Managers who actually manage someone (role=manager AND have team members)
            managers = (
                UserProfile.objects
                .filter(role="manager", team_members__isnull=False)
                .distinct()
            )

            for mgr in managers:
                # All direct reports of this manager (any role)
                team = UserProfile.objects.filter(manager=mgr).distinct()
                for emp in team:
                    ev, was_created = Evaluation.objects.get_or_create(
                        manager=mgr,
                        employee=emp,
                        week_start=this_monday,
                        week_end=this_sunday,
                        defaults={
                            "status": "pending",
                            # safe defaults for NOT NULL model fields
                            "avg_customer_satisfaction_score": 0,
                            "five_star_reviews": 0,
                            "negative_reviews": 0,
                            "late_arrivals": 0,
                            "absences": 0,
                            "reliability_rating": 0,
                            "avg_move_completion_time": timedelta(),  # 0:00:00
                            "moves_within_schedule": 0,
                            "avg_revenue_per_move": 0.0,
                            "damage_claims": 0,
                            "safety_incidents": 0,
                            "consecutive_damage_free_moves": 0,
                        },
                    )
                    if was_created:
                        created_count += 1

            self.stdout.write(
                f"✅ Created {created_count} evaluations for week {this_monday}–{this_sunday}"
            )

        # --- FRIDAY: send reminders ---
        elif weekday == 4:
            self.stdout.write("✉️ Friday: sending pending‑eval reminders...")

            pending_qs = (
                Evaluation.objects
                .filter(week_start=this_monday, week_end=this_sunday, status="pending")
                .select_related("manager__user", "employee__user")
            )

            # Group by manager
            reminders = {}
            for ev in pending_qs:
                reminders.setdefault(ev.manager, []).append(ev)

            sent_to = 0
            for mgr, evs in reminders.items():
                user = mgr.user
                email = user.email
                if not email:
                    self.stdout.write(f"⚠️ No email for manager {user.username}, skipping.")
                    continue

                subject = "Reminder: Complete Pending Evaluations"
                lines = [
                    f"Hello {user.get_full_name() or user.username},",
                    "",
                    f"You have {len(evs)} evaluation(s) pending for the week {this_monday} to {this_sunday}:",
                    "",
                ]
                for ev in evs:
                    emp_user = ev.employee.user
                    emp_name = emp_user.get_full_name() or emp_user.username
                    lines.append(f"  • {emp_name}")
                lines += [
                    "",
                    "Please complete these by Sunday. Your access may be restricted until all are submitted.",
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
                sent_to += 1
                self.stdout.write(f"✉️ Sent reminder to {email}")

            if sent_to == 0:
                self.stdout.write("✅ No pending evaluations for this week. All set!")

        else:
            self.stdout.write("🛑 Not Monday or Friday – nothing to do.")
