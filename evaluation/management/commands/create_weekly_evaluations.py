from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import get_connection
from django.conf import settings

from anymail.message import AnymailMessage
from anymail.exceptions import AnymailRequestsAPIError

from evaluation.models import Evaluation
from authentication.models import UserProfile
from django.db import transaction
from evaluation.models_dynamic import EvalForm, DynamicEvaluation, Answer, Question


class Command(BaseCommand):
    help = (
        "Mondays: create weekly evaluations for all employees who report to a manager.\n"
        "Fridays: email managers with any still-pending evaluations for the current week.\n"
        "You can force either path with --when monday|friday, dry-run with --dry-run, "
        "filter a single manager with --only-manager <email>, or send a test email with --test-email <to>."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--when",
            choices=["auto", "monday", "friday"],
            default="auto",
            help="Which branch to run (default: auto by weekday).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do everything except writing DB changes or sending emails.",
        )
        parser.add_argument(
            "--only-manager",
            help="Limit actions to a single manager (by user email).",
        )
        parser.add_argument(
            "--test-email",
            help="Send a single test email to this address and exit (useful to verify Postmark wiring).",
        )

    # -----------------------------
    # Email helpers
    # -----------------------------
    def _current_stream(self) -> str:
        """Pull the stream Anymail will use by default (from SEND_DEFAULTS)."""
        anymail = getattr(settings, "ANYMAIL", {})
        return anymail.get("SEND_DEFAULTS", {}).get("esp_extra", {}).get(
            "MessageStream",
            "outbound",  # default safety
        )

    def _log_mail_backend(self):
        backend = settings.EMAIL_BACKEND
        app_env = getattr(settings, "APP_ENV", "unknown")
        anymail = getattr(settings, "ANYMAIL", {})
        esp_extra = anymail.get("SEND_DEFAULTS", {}).get("esp_extra", {})
        stream = esp_extra.get("MessageStream", "(none)")
        token = anymail.get("POSTMARK_SERVER_TOKEN", "")
        token_hint = f"...{token[-6:]}" if token else "(missing)"
        sandbox = str(getattr(settings, "USE_POSTMARK_SANDBOX", False))
        self.stdout.write(
            "📬 Email backend: {}\n"
            "   APP_ENV: {}\n"
            "   MessageStream (default): {}\n"
            "   Using Sandbox: {}\n"
            "   Token_hint: {}".format(backend, app_env, stream, sandbox, token_hint)
        )
        # Try opening the backend connection early to fail fast:
        try:
            conn = get_connection()
            conn.open()
            self.stdout.write("   ✅ Email connection initialized.")
        except Exception as e:
            self.stdout.write(f"   ❌ Email connection failed: {e}")

    def _send_with_fallback(self, subject: str, body: str, to_addr: str, dry_run: bool = False) -> bool:
        """
        Send using AnymailMessage.
        1) Try the configured stream (from settings.ANYMAIL.SEND_DEFAULTS).
        2) If Postmark returns ErrorCode 1235 (stream not found), retry on 'outbound'.
        Returns True if sent, False otherwise.
        """
        if dry_run:
            self.stdout.write(f"(dry-run) Would email {to_addr} with subject '{subject}'")
            return True

        # Build a message; let SEND_DEFAULTS apply tags/metadata/stream by default.
        msg = AnymailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_addr],
        )

        try:
            sent = msg.send()  # raises on API errors
            self.stdout.write(f"✉️ Sent to {to_addr} (stream={self._current_stream()})")
            return bool(sent)
        except AnymailRequestsAPIError as e:
            # Inspect Postmark response for ErrorCode
            err_code = None
            try:
                data = e.response.json()
                err_code = data.get("ErrorCode")
            except Exception:
                pass

            if err_code == 1235:
                # Stream not found: retry once on 'outbound'
                self.stdout.write("⚠️ Postmark says this stream doesn't exist. Retrying on 'outbound'…")
                try:
                    msg = AnymailMessage(
                        subject=subject,
                        body=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[to_addr],
                    )
                    msg.esp_extra = {"MessageStream": "outbound"}
                    sent = msg.send()
                    self.stdout.write("✅ Fallback success on 'outbound'.")
                    return bool(sent)
                except Exception as e2:
                    self.stdout.write(f"❌ Fallback send failed: {e2}")
                    return False

            # Any other error: bubble up details
            self.stdout.write(f"❌ Postmark send failed: {e}")
            return False

    # -----------------------------
    # Main handler
    # -----------------------------
    def handle(self, *args, **options):
        # Quick one-off Postmark sanity test and exit
        test_to = options.get("test_email")
        self._log_mail_backend()
        if test_to:
            subject = f"[{getattr(settings, 'APP_ENV', 'unknown')}] Test mail"
            body = "If you see this in Postmark Activity, wiring works."
            ok = self._send_with_fallback(subject, body, test_to, dry_run=options["dry_run"])
            self.stdout.write(f"✉️ Test email sent: {ok}")
            return

        today = now().date()
        weekday = today.weekday()  # Monday=0 ... Sunday=6

        # Compute this Monday and Sunday of current week
        this_monday = today - timedelta(days=weekday)
        this_sunday = this_monday + timedelta(days=6)

        # Decide which branch to run
        when = options["when"]
        if when == "auto":
            if weekday == 0:
                branch = "monday"
            elif weekday == 4:
                branch = "friday"
            else:
                branch = "none"
        else:
            branch = when

        only_manager_email = options.get("only_manager")
        dry = options["dry_run"]

        if branch == "monday":
            self.stdout.write("🔨 Monday path: creating weekly evaluations...")

            managers_qs = UserProfile.objects.filter(role="manager")
            if only_manager_email:
                managers_qs = managers_qs.filter(user__email__iexact=only_manager_email)

            managers = managers_qs.filter(team_members__isnull=False).distinct()

            created_count = 0
            for mgr in managers:
                team = UserProfile.objects.filter(manager=mgr).distinct()
                for emp in team:
                    dept = emp.department
                    if dept:
                        active_form = EvalForm.objects.filter(department=dept, is_active=True).first()
                    else:
                        active_form = None

                    if active_form:
                        if dry:
                            self.stdout.write(
                                f"(dry-run) Would create DYNAMIC evaluation for mgr={mgr.user.email} emp={emp.user.email} "
                                f"dept={dept.title if dept else '-'} week={this_monday}–{this_sunday}"
                            )
                            continue

                        with transaction.atomic():
                            inst, created = DynamicEvaluation.objects.get_or_create(
                                form=active_form,
                                department=dept,
                                manager=mgr,
                                employee=emp,
                                week_start=this_monday,
                                week_end=this_sunday,
                                defaults={"status": "pending"},
                            )
                            if created:
                                # scaffold answers for faster rendering (optional)
                                qids = list(active_form.questions.values_list("id", flat=True))
                                Answer.objects.bulk_create(
                                    [Answer(instance=inst, question_id=qid) for qid in qids],
                                    ignore_conflicts=True,
                                )
                                created_count += 1
                    else:
                        # fallback to your existing legacy Evaluation creation
                        if dry:
                            self.stdout.write(
                                f"(dry-run) Would create legacy evaluation for mgr={mgr.user.email} emp={emp.user.email} "
                                f"week={this_monday}–{this_sunday}"
                            )
                            continue

                        ev, was_created = Evaluation.objects.get_or_create(
                            manager=mgr,
                            employee=emp,
                            week_start=this_monday,
                            week_end=this_sunday,
                            defaults={
                                "status": "pending",
                                "avg_customer_satisfaction_score": 0,
                                "five_star_reviews": 0,
                                "negative_reviews": 0,
                                "late_arrivals": 0,
                                "absences": 0,
                                "reliability_rating": 0,
                                "avg_move_completion_time": timedelta(),
                                "moves_within_schedule": 0,
                                "avg_revenue_per_move": 0.0,
                                "damage_claims": 0,
                                "safety_incidents": 0,
                                "consecutive_damage_free_moves": 0,
                            },
                        )
                        if was_created:
                            created_count += 1

            if not dry:
                self.stdout.write(
                    f"✅ Created {created_count} evaluations for week {this_monday}–{this_sunday}"
                )
            else:
                self.stdout.write("✅ Dry-run complete (no DB writes).")

        elif branch == "friday":
            self.stdout.write("✉️ Friday path: sending pending-eval reminders...")

            pending_qs = (
                Evaluation.objects
                .filter(week_start=this_monday, week_end=this_sunday, status="pending")
                .select_related("manager__user", "employee__user")
            )
            if only_manager_email:
                pending_qs = pending_qs.filter(manager__user__email__iexact=only_manager_email)

            reminders = {}
            for ev in pending_qs:
                reminders.setdefault(ev.manager, []).append(ev)

            if not reminders:
                self.stdout.write("✅ No pending evaluations for this week. All set!")
                return

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

                if self._send_with_fallback(subject, body, email, dry_run=dry):
                    sent_to += 1

            if not dry:
                self.stdout.write(f"✅ Reminders sent to {sent_to} manager(s).")
            else:
                self.stdout.write("✅ Dry-run complete (no emails sent).")

        else:
            self.stdout.write("🛑 Not Monday or Friday – nothing to do. Use --when to force.")
