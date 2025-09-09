"""
Dynamic Weekly Evaluations Command v2

This command has been updated to work with the dynamic evaluation system:
- Uses EvalForm, DynamicEvaluation, and Answer models instead of legacy Evaluation
- Supports multiple evaluation types (Weekly, Monthly, Quarterly, Annual)
- Creates evaluations based on active forms per department
- Sends reminders for pending dynamic evaluations
- Links to dashboard2 for dynamic evaluation management

Key differences from v1:
- Removed legacy Evaluation model dependency
- Added --evaluation-type and --department filters
- Enhanced email reminders with department/form grouping
- Better error handling for missing departments/forms
"""

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail, get_connection
from django.conf import settings

from authentication.models import UserProfile
from django.db import transaction
from evaluation.models_dynamic import EvalForm, DynamicEvaluation, Answer, Question


class Command(BaseCommand):
    help = (
        "Mondays: create dynamic weekly evaluations for all employees who report to a manager.\n"
        "Fridays: email managers with any still-pending dynamic evaluations for the current week.\n"
        "You can force either path with --when monday|friday, dry-run with --dry-run, "
        "filter a single manager with --only-manager <email>, or send a test email with --test-email <to>.\n"
        "Emails will be printed to console in development mode.\n"
        "This v2 command focuses on the dynamic evaluation system with EvalForm and DynamicEvaluation models."
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
        parser.add_argument(
            "--evaluation-type",
            default="Weekly Evaluation",
            help="Type of evaluation to create (default: 'Weekly Evaluation'). Options: Weekly Evaluation, Monthly Evaluation, Quarterly Evaluation, Annual Evaluation",
        )
        parser.add_argument(
            "--department",
            help="Limit to a specific department ID (optional).",
        )

    # -----------------------------
    # Email helpers
    # -----------------------------

    def _log_mail_backend(self):
        backend = settings.EMAIL_BACKEND
        app_env = getattr(settings, "APP_ENV", "unknown")
        self.stdout.write(
            "📬 Email backend: {}\n"
            "   APP_ENV: {}".format(backend, app_env)
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
        Send email using Django's send_mail function.
        Returns True if sent, False otherwise.
        """
        if dry_run:
            self.stdout.write(f"(dry-run) Would email {to_addr} with subject '{subject}'")
            return True

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_addr],
                fail_silently=False,
            )
            self.stdout.write(f"📧 Email sent to {to_addr}")
            return True
        except Exception as e:
            self.stdout.write(f"❌ Email send failed: {e}")
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
        evaluation_type = options.get("evaluation_type", "Weekly Evaluation")
        department_id = options.get("department")

        if branch == "monday":
            self.stdout.write(f"🔨 Monday path: creating dynamic {evaluation_type.lower()} evaluations...")

            managers_qs = UserProfile.objects.filter(role="manager")
            if only_manager_email:
                managers_qs = managers_qs.filter(user__email__iexact=only_manager_email)

            managers = managers_qs.filter(team_members__isnull=False).distinct()

            created_count = 0
            skipped_count = 0
            
            for mgr in managers:
                team = UserProfile.objects.filter(manager=mgr).distinct()
                for emp in team:
                    dept = emp.department
                    if not dept:
                        if dry:
                            self.stdout.write(
                                f"(dry-run) Skipping emp={emp.user.email} - no department assigned"
                            )
                        skipped_count += 1
                        continue

                    # Filter by specific department if provided
                    if department_id and str(dept.id) != str(department_id):
                        continue

                    # Get all active evaluation forms for this department and type
                    active_forms = EvalForm.objects.filter(
                        department=dept, 
                        is_active=True,
                        name=evaluation_type
                    )

                    if not active_forms.exists():
                        if dry:
                            self.stdout.write(
                                f"(dry-run) Skipping emp={emp.user.email} dept={dept.title} - no active {evaluation_type.lower()} form"
                            )
                        skipped_count += 1
                        continue

                    # Create evaluations for each active form
                    for active_form in active_forms:
                        if dry:
                            self.stdout.write(
                                f"(dry-run) Would create DYNAMIC evaluation for mgr={mgr.user.email} emp={emp.user.email} "
                                f"dept={dept.title} form='{active_form.name}' week={this_monday}–{this_sunday}"
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
                                self.stdout.write(
                                    f"✅ Created evaluation for {emp.user.get_full_name() or emp.user.username} "
                                    f"({dept.title}) using form '{active_form.name}'"
                                )

            if not dry:
                self.stdout.write(
                    f"✅ Created {created_count} dynamic evaluations for week {this_monday}–{this_sunday}"
                )
                if skipped_count > 0:
                    self.stdout.write(f"⚠️ Skipped {skipped_count} employees (no department or active form)")
            else:
                self.stdout.write("✅ Dry-run complete (no DB writes).")

        elif branch == "friday":
            self.stdout.write(f"✉️ Friday path: sending pending {evaluation_type.lower()} reminders...")

            pending_qs = (
                DynamicEvaluation.objects
                .filter(
                    week_start=this_monday, 
                    week_end=this_sunday, 
                    status="pending",
                    form__name=evaluation_type
                )
                .select_related("manager__user", "employee__user", "form", "department")
            )
            if only_manager_email:
                pending_qs = pending_qs.filter(manager__user__email__iexact=only_manager_email)
            if department_id:
                pending_qs = pending_qs.filter(department_id=department_id)

            reminders = {}
            for ev in pending_qs:
                reminders.setdefault(ev.manager, []).append(ev)

            if not reminders:
                self.stdout.write(f"✅ No pending {evaluation_type.lower()} evaluations for this week. All set!")
                return

            sent_to = 0
            for mgr, evs in reminders.items():
                user = mgr.user
                email = user.email
                if not email:
                    self.stdout.write(f"⚠️ No email for manager {user.username}, skipping.")
                    continue

                subject = f"Reminder: Complete Pending {evaluation_type}s"
                lines = [
                    f"Hello {user.get_full_name() or user.username},",
                    "",
                    f"You have {len(evs)} {evaluation_type.lower()}(s) pending for the week {this_monday} to {this_sunday}:",
                    "",
                ]
                
                # Group by department and form for better organization
                by_dept_form = {}
                for ev in evs:
                    key = f"{ev.department.title} - {ev.form.name}"
                    if key not in by_dept_form:
                        by_dept_form[key] = []
                    by_dept_form[key].append(ev)
                
                for dept_form, evaluations in by_dept_form.items():
                    lines.append(f"📋 {dept_form}:")
                    for ev in evaluations:
                        emp_user = ev.employee.user
                        emp_name = emp_user.get_full_name() or emp_user.username
                        lines.append(f"  • {emp_name}")
                    lines.append("")
                
                lines += [
                    "Please complete these by Sunday. Your access may be restricted until all are submitted.",
                    "",
                    f"👉 {settings.BASE_URL}/evaluation/pending-v2/",
                ]
                body = "\n".join(lines)

                if self._send_with_fallback(subject, body, email, dry_run=dry):
                    sent_to += 1

            if not dry:
                self.stdout.write(f"✅ {evaluation_type} reminders sent to {sent_to} manager(s).")
            else:
                self.stdout.write("✅ Dry-run complete (no emails sent).")

        else:
            self.stdout.write("🛑 Not Monday or Friday – nothing to do. Use --when to force.")
