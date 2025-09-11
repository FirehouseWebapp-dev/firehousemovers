"""
Manager Evaluations Command

This command creates and manages manager evaluations:
- Mondays: Creates monthly/quarterly/annual evaluations for managers
- Fridays: Sends email reminders to senior managers with pending evaluations
- Uses the same dynamic evaluation system as employee evaluations
- Senior managers evaluate managers they supervise

Key features:
- Supports Monthly, Quarterly, and Annual evaluation types
- Creates evaluations based on active manager evaluation forms per department
- Sends reminders for pending manager evaluations
- Links to manager evaluation dashboard
"""

from datetime import timedelta, date
import logging
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail, get_connection
from django.conf import settings

from authentication.models import UserProfile
from django.db import transaction
from evaluation.models_dynamic import EvalForm, DynamicManagerEvaluation, ManagerAnswer, Question


class Command(BaseCommand):
    help = (
        "Mondays: create manager evaluations (monthly/quarterly/annual) for all managers.\n"
        "Fridays: email senior managers with any still-pending manager evaluations.\n"
        "You can force either path with --when monday|friday, dry-run with --dry-run, "
        "filter a single senior manager with --only-senior-manager <email>, or send a test email with --test-email <to>.\n"
        "Emails will be printed to console in development mode.\n"
        "This command focuses on the manager evaluation system with EvalForm and DynamicManagerEvaluation models."
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
            "--only-senior-manager",
            help="Limit actions to a single senior manager (by user email).",
        )
        parser.add_argument(
            "--test-email",
            help="Send a single test email to this address and exit (useful to verify Postmark wiring).",
        )
        parser.add_argument(
            "--evaluation-type",
            choices=["Monthly Evaluation", "Quarterly Evaluation", "Annual Evaluation"],
            default="Monthly Evaluation",
            help="Type of manager evaluation to create (default: 'Monthly Evaluation').",
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
            logging.error(f"Email connection initialization failed: {str(e)}", exc_info=True)

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
            logging.error(f"Failed to send email to {to_addr} with subject '{subject}': {str(e)}", exc_info=True)
            return False

    def _get_evaluation_period(self, evaluation_type: str, base_date: date = None):
        """Calculate the evaluation period based on the evaluation type."""
        if base_date is None:
            base_date = now().date()
        
        if evaluation_type == "Monthly Evaluation":
            # First day of current month to last day of current month
            period_start = base_date.replace(day=1)
            if base_date.month == 12:
                period_end = base_date.replace(year=base_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                period_end = base_date.replace(month=base_date.month + 1, day=1) - timedelta(days=1)
        
        elif evaluation_type == "Quarterly Evaluation":
            # Calculate quarter start and end
            quarter = (base_date.month - 1) // 3 + 1
            quarter_start_month = (quarter - 1) * 3 + 1
            period_start = base_date.replace(month=quarter_start_month, day=1)
            
            # Quarter end month
            quarter_end_month = quarter_start_month + 2
            if quarter_end_month == 12:
                period_end = base_date.replace(year=base_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                period_end = base_date.replace(month=quarter_end_month + 1, day=1) - timedelta(days=1)
        
        elif evaluation_type == "Annual Evaluation":
            # January 1st to December 31st of current year
            period_start = base_date.replace(month=1, day=1)
            period_end = base_date.replace(month=12, day=31)
        
        return period_start, period_end

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

        only_senior_manager_email = options.get("only_senior_manager")
        dry = options["dry_run"]
        evaluation_type = options.get("evaluation_type", "Monthly Evaluation")
        department_id = options.get("department")

        if branch == "monday":
            self.stdout.write(f"🔨 Monday path: creating {evaluation_type.lower()} evaluations for managers...")

            # Get all managers who need to be evaluated
            managers_qs = UserProfile.objects.filter(role="manager")
            if department_id:
                managers_qs = managers_qs.filter(department_id=department_id)

            managers = managers_qs.distinct()

            # Get all senior managers who can evaluate managers
            senior_managers_qs = UserProfile.objects.filter(
                role__in=["vp", "ceo", "admin"]
            )
            if only_senior_manager_email:
                senior_managers_qs = senior_managers_qs.filter(user__email__iexact=only_senior_manager_email)

            senior_managers = senior_managers_qs.distinct()

            created_count = 0
            skipped_count = 0
            
            # Calculate evaluation period
            period_start, period_end = self._get_evaluation_period(evaluation_type)
            
            for manager in managers:
                dept = getattr(manager, 'managed_department', None)
                
                if not dept:
                    if dry:
                        self.stdout.write(
                            f"(dry-run) Skipping manager={manager.user.email} - no managed department assigned"
                        )
                    skipped_count += 1
                    continue

                # Get all active manager evaluation forms for this department and type
                active_forms = EvalForm.objects.filter(
                    department=dept, 
                    is_active=True,
                    name=evaluation_type
                )

                if not active_forms.exists():
                    if dry:
                        self.stdout.write(
                            f"(dry-run) Skipping manager={manager.user.email} dept={dept.title} - no active {evaluation_type.lower()} form"
                        )
                    skipped_count += 1
                    continue

                # Create evaluations for each active form and each senior manager
                for active_form in active_forms:
                    for senior_manager in senior_managers:
                        if dry:
                            self.stdout.write(
                                f"(dry-run) Would create MANAGER evaluation for senior_mgr={senior_manager.user.email} "
                                f"mgr={manager.user.email} dept={dept.title} form='{active_form.name}' "
                                f"period={period_start}–{period_end}"
                            )
                            continue

                        with transaction.atomic():
                            inst, created = DynamicManagerEvaluation.objects.get_or_create(
                                form=active_form,
                                manager=manager,
                                period_start=period_start,
                                period_end=period_end,
                                defaults={
                                    "department": dept,
                                    "senior_manager": senior_manager,
                                    "status": "pending"
                                },
                            )
                            if created:
                                # scaffold answers for faster rendering (optional)
                                qids = list(active_form.questions.values_list("id", flat=True))
                                ManagerAnswer.objects.bulk_create(
                                    [ManagerAnswer(instance=inst, question_id=qid) for qid in qids],
                                    ignore_conflicts=True,
                                )
                                created_count += 1
                                self.stdout.write(
                                    f"✅ Created manager evaluation for {manager.user.get_full_name() or manager.user.username} "
                                    f"({dept.title}) by {senior_manager.user.get_full_name() or senior_manager.user.username} "
                                    f"using form '{active_form.name}'"
                                )

            if not dry:
                self.stdout.write(
                    f"✅ Created {created_count} manager evaluations for period {period_start}–{period_end}"
                )
                if skipped_count > 0:
                    self.stdout.write(f"⚠️ Skipped {skipped_count} managers (no department or active form)")
            else:
                self.stdout.write("✅ Dry-run complete (no DB writes).")

        elif branch == "friday":
            self.stdout.write(f"✉️ Friday path: sending pending {evaluation_type.lower()} reminders...")

            # Calculate the current evaluation period
            period_start, period_end = self._get_evaluation_period(evaluation_type)

            pending_qs = (
                DynamicManagerEvaluation.objects
                .filter(
                    period_start=period_start, 
                    period_end=period_end, 
                    status="pending",
                    form__name=evaluation_type
                )
                .select_related("senior_manager__user", "manager__user", "form", "department")
            )
            if only_senior_manager_email:
                pending_qs = pending_qs.filter(senior_manager__user__email__iexact=only_senior_manager_email)
            if department_id:
                pending_qs = pending_qs.filter(department_id=department_id)

            reminders = {}
            for ev in pending_qs:
                reminders.setdefault(ev.senior_manager, []).append(ev)

            if not reminders:
                self.stdout.write(f"✅ No pending {evaluation_type.lower()} evaluations for this period. All set!")
                return

            sent_to = 0
            for senior_mgr, evs in reminders.items():
                user = senior_mgr.user
                email = user.email
                if not email:
                    self.stdout.write(f"⚠️ No email for senior manager {user.username}, skipping.")
                    continue

                subject = f"Reminder: Complete Pending Manager {evaluation_type}s"
                lines = [
                    f"Hello {user.get_full_name() or user.username},",
                    "",
                    f"You have {len(evs)} pending manager {evaluation_type.lower()}(s) for the period {period_start} to {period_end}:",
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
                        mgr_user = ev.manager.user
                        mgr_name = mgr_user.get_full_name() or mgr_user.username
                        lines.append(f"  • {mgr_name}")
                    lines.append("")
                
                lines += [
                    "Please complete these evaluations. Your access may be restricted until all are submitted.",
                    "",
                    f"👉 {settings.BASE_URL}/evaluation/manager-evaluations/",
                ]
                body = "\n".join(lines)

                if self._send_with_fallback(subject, body, email, dry_run=dry):
                    sent_to += 1

            if not dry:
                self.stdout.write(f"✅ Manager {evaluation_type} reminders sent to {sent_to} senior manager(s).")
            else:
                self.stdout.write("✅ Dry-run complete (no emails sent).")

        else:
            self.stdout.write("🛑 Not Monday or Friday – nothing to do. Use --when to force.")
