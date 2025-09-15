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
from evaluation.models import EvalForm, DynamicManagerEvaluation, ManagerAnswer, Question


class Command(BaseCommand):
    help = (
        "Daily: create manager evaluations (monthly/quarterly/annual) for all managers based on active forms.\n"
        "Last Friday of month/quarter/year: email senior managers with any still-pending manager evaluations.\n"
        "You can force creation with --create-evaluations, force reminders with --send-reminders, "
        "dry-run with --dry-run, filter a single senior manager with --only-senior-manager <email>, "
        "or send a test email with --test-email <to>.\n"
        "Emails will be printed to console in development mode.\n"
        "This command focuses on the manager evaluation system with EvalForm and DynamicManagerEvaluation models."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-evaluations",
            action="store_true",
            help="Force creation of manager evaluations (can be run any day).",
        )
        parser.add_argument(
            "--send-reminders",
            action="store_true",
            help="Force sending of reminder emails (typically run on last Friday).",
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
        try:
            conn = get_connection()
            conn.open()
            self.stdout.write("   ✅ Email connection initialized.")
        except Exception as e:
            self.stdout.write(f"   ❌ Email connection failed: {e}")
            logging.error(f"Email connection initialization failed: {str(e)}", exc_info=True)

    def _send_with_fallback(self, subject: str, body: str, to_addr: str, dry_run: bool = False) -> bool:
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

    def _month_bounds(self, d: date):
        """Calculate month start and end dates - same logic as generate_review_cycles.py"""
        start = d.replace(day=1)
        if start.month == 12:
            end = date(start.year, 12, 31)
        else:
            end = date(start.year, start.month + 1, 1) - timedelta(days=1)
        return start, end

    def _quarter_bounds(self, d: date):
        """Calculate quarter start and end dates - same logic as generate_review_cycles.py"""
        q = (d.month - 1) // 3
        start_month = q * 3 + 1
        start = date(d.year, start_month, 1)
        last_month = start_month + 2
        if last_month == 12:
            end = date(d.year, 12, 31)
        else:
            end = date(d.year, last_month + 1, 1) - timedelta(days=1)
        return start, end

    def _year_bounds(self, d: date):
        """Calculate year start and end dates - same logic as generate_review_cycles.py"""
        return date(d.year, 1, 1), date(d.year, 12, 31)

    def _get_evaluation_period(self, evaluation_type: str, base_date: date = None):
        """Get evaluation period using the same logic as generate_review_cycles.py"""
        if base_date is None:
            base_date = now().date()
        
        if evaluation_type == "Monthly Evaluation":
            return self._month_bounds(base_date)
        elif evaluation_type == "Quarterly Evaluation":
            return self._quarter_bounds(base_date)
        elif evaluation_type == "Annual Evaluation":
            return self._year_bounds(base_date)
        
        # Fallback for unknown types
        return base_date, base_date

    def _is_last_friday_of_period(self, evaluation_type: str, base_date: date = None):
        """Check if the given date is the last Friday of the month/quarter/year for the given evaluation type."""
        if base_date is None:
            base_date = now().date()
        
        # Check if it's a Friday
        if base_date.weekday() != 4:  # Friday is 4
            return False
        
        # Get the period end date using the same logic as generate_review_cycles.py
        if evaluation_type == "Monthly Evaluation":
            _, period_end = self._month_bounds(base_date)
        elif evaluation_type == "Quarterly Evaluation":
            _, period_end = self._quarter_bounds(base_date)
        elif evaluation_type == "Annual Evaluation":
            _, period_end = self._year_bounds(base_date)
        else:
            return False
        
        # Find the last Friday of the period
        last_friday = period_end
        while last_friday.weekday() != 4:  # While not Friday
            last_friday -= timedelta(days=1)
        
        return base_date == last_friday

    # -----------------------------
    # Main handler
    # -----------------------------
    def handle(self, *args, **options):
        test_to = options.get("test_email")
        self._log_mail_backend()
        
        if test_to:
            subject = f"[{getattr(settings, 'APP_ENV', 'unknown')}] Test mail"
            body = "If you see this in Postmark Activity, wiring works."
            ok = self._send_with_fallback(subject, body, test_to, dry_run=options["dry_run"])
            self.stdout.write(f"✉️ Test email sent: {ok}")
            return

        today = now().date()
        only_senior_manager_email = options.get("only_senior_manager")
        dry = options["dry_run"]
        department_id = options.get("department")
        
        # Always calculate date triggers (needed for both automatic and forced creation)
        is_15th = (today.day == 15)
        is_quarter_end_month = today.month in (3, 6, 9, 12)
        is_dec_15 = (today.month == 12 and today.day == 15)
        
        # Determine what actions to take
        create_evaluations = options.get("create_evaluations", False)
        send_reminders = options.get("send_reminders", False)
        
        # If no specific action is requested, determine automatically
        if not create_evaluations and not send_reminders:
            # Check if we should create evaluations based on date triggers
            if is_15th:
                create_evaluations = True
                self.stdout.write(f"📅 15th of month detected - creating evaluations")
            
            # Check if we should send reminders (last Friday of period)
            active_forms = EvalForm.objects.filter(is_active=True).values_list('name', flat=True).distinct()
            for evaluation_type in active_forms:
                if self._is_last_friday_of_period(evaluation_type, today):
                    send_reminders = True
                    self.stdout.write(f"📧 Last Friday of {evaluation_type.lower()} period detected - sending reminders")
                    break

        # -----------------------------
        # Create Evaluations (based on date triggers or force)
        # -----------------------------
        if create_evaluations:
            # Determine which evaluation types to create
            eval_types_to_create = []
            
            # Check if this is forced creation (not automatic)
            is_forced = options.get("create_evaluations", False)
            
            if is_forced:
                # Force creation: create all active evaluation types
                self.stdout.write("🔨 Force creating manager evaluations for all active forms...")
                active_forms = EvalForm.objects.filter(is_active=True).values_list('name', flat=True).distinct()
                eval_types_to_create = list(active_forms)
            else:
                # Automatic creation: only create based on date triggers
                self.stdout.write("🔨 Creating manager evaluations based on date triggers...")
                
                if is_15th:
                    # Always create monthly on 15th
                    eval_types_to_create.append("Monthly Evaluation")
                    
                    # Create quarterly if it's a quarter-end month (Mar, Jun, Sep, Dec)
                    if is_quarter_end_month:
                        eval_types_to_create.append("Quarterly Evaluation")
                    
                    # Create annual if it's December 15th
                    if is_dec_15:
                        eval_types_to_create.append("Annual Evaluation")
            
            if not eval_types_to_create:
                self.stdout.write("⚠️ No evaluation types to create based on current date.")
                return
            
            self.stdout.write(f"Creating evaluation types: {', '.join(eval_types_to_create)}")

            for evaluation_type in eval_types_to_create:
                # Check if this evaluation type has active forms
                active_forms = EvalForm.objects.filter(is_active=True, name=evaluation_type)
                if not active_forms.exists():
                    self.stdout.write(f"⚠️ No active forms found for {evaluation_type}. Skipping.")
                    continue
                
                self.stdout.write(f"   Creating {evaluation_type.lower()} evaluations...")

                # Managers
                managers_qs = UserProfile.objects.filter(role="manager")
                if department_id:
                    managers_qs = managers_qs.filter(department_id=department_id)
                managers = managers_qs.distinct()

                # Senior Managers
                senior_managers_qs = UserProfile.objects.filter(role__in=UserProfile.SENIOR_MANAGEMENT_ROLES)
                if only_senior_manager_email:
                    senior_managers_qs = senior_managers_qs.filter(user__email__iexact=only_senior_manager_email)
                senior_managers = senior_managers_qs.distinct()

                created_count = 0
                skipped_count = 0
                period_start, period_end = self._get_evaluation_period(evaluation_type)

                for manager in managers:
                    dept = getattr(manager, 'managed_department', None)
                    if not dept:
                        if dry:
                            self.stdout.write(f"(dry-run) Skipping manager={manager.user.email} - no department assigned")
                        skipped_count += 1
                        continue

                    active_forms = EvalForm.objects.filter(department=dept, is_active=True, name=evaluation_type)
                    if not active_forms.exists():
                        if dry:
                            self.stdout.write(f"(dry-run) Skipping manager={manager.user.email} dept={dept.title} - no active form")
                        skipped_count += 1
                        continue

                    for active_form in active_forms:
                        for senior_manager in senior_managers:
                            if dry:
                                self.stdout.write(f"(dry-run) Would create evaluation: senior_mgr={senior_manager.user.email}, manager={manager.user.email}, form={active_form.name}, period={period_start}–{period_end}")
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
                                    qids = list(active_form.questions.values_list("id", flat=True))
                                    ManagerAnswer.objects.bulk_create(
                                        [ManagerAnswer(instance=inst, question_id=qid) for qid in qids],
                                        ignore_conflicts=True,
                                    )
                                    created_count += 1
                                    self.stdout.write(f"✅ Created {evaluation_type.lower()} for manager {manager.user.username} by {senior_manager.user.username}")

                if not dry:
                    self.stdout.write(f"✅ Created {created_count} {evaluation_type.lower()} evaluations for period {period_start}–{period_end}")
                    if skipped_count > 0:
                        self.stdout.write(f"⚠️ Skipped {skipped_count} managers (no department or active form)")
                else:
                    self.stdout.write(f"✅ Dry-run complete for {evaluation_type.lower()}")

        # -----------------------------
        # Send Reminders (last Friday of period)
        # -----------------------------
        if send_reminders:
            self.stdout.write("✉️ Sending pending manager evaluation reminders (last Friday of period)...")

            # Get all active evaluation forms to determine which types to check
            active_forms = EvalForm.objects.filter(is_active=True).values_list('name', flat=True).distinct()
            eval_types = list(active_forms)
            
            if not eval_types:
                self.stdout.write("⚠️ No active evaluation forms found. Nothing to remind about.")
            else:
                self.stdout.write(f"Checking reminders for active evaluation types: {', '.join(eval_types)}")
                sent_to_total = 0

                for evaluation_type in eval_types:
                    # Only send reminders for evaluation types where today is the last Friday
                    if not self._is_last_friday_of_period(evaluation_type, today):
                        self.stdout.write(f"⏭️ Skipping {evaluation_type.lower()} reminders - not last Friday of period")
                        continue
                    
                    self.stdout.write(f"📧 Sending {evaluation_type.lower()} reminders...")
                    
                    period_start, period_end = self._get_evaluation_period(evaluation_type)
                    pending_qs = DynamicManagerEvaluation.objects.filter(
                        period_start=period_start,
                        period_end=period_end,
                        status="pending",
                        form__name=evaluation_type
                    ).select_related("senior_manager__user", "manager__user", "form", "department")

                    if only_senior_manager_email:
                        pending_qs = pending_qs.filter(senior_manager__user__email__iexact=only_senior_manager_email)
                    if department_id:
                        pending_qs = pending_qs.filter(department_id=department_id)

                    reminders = {}
                    for ev in pending_qs:
                        reminders.setdefault(ev.senior_manager, []).append(ev)

                    if not reminders:
                        self.stdout.write(f"✅ No pending {evaluation_type.lower()} evaluations for this period.")
                        continue

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

                        by_dept_form = {}
                        for ev in evs:
                            key = f"{ev.department.title} - {ev.form.name}"
                            by_dept_form.setdefault(key, []).append(ev)

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

                    sent_to_total += sent_to
                    self.stdout.write(f"✅ Reminders for {evaluation_type.lower()} sent to {sent_to} senior manager(s).")

                if sent_to_total == 0 and dry:
                    self.stdout.write("✅ Dry-run complete (no emails sent).")

        # Summary
        if not create_evaluations and not send_reminders:
            self.stdout.write("🛑 No actions specified. Use --create-evaluations or --send-reminders to force actions.")
