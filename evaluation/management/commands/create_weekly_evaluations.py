# evaluation/management/commands/create_weekly_evaluations.py

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from authentication.models import UserProfile
from evaluation.models import Evaluation
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Create weekly evaluation records for all employees under managers.'

    def handle(self, *args, **options):
        # today = date(2025, 8, 4)
        today = now().date()

        weekday = today.weekday()

        # This Monday
        week_start = today - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)

        managers = UserProfile.objects.filter(role='manager')
        count = 0

        for manager in managers:
            for employee in manager.team_members.all():
                # Check if evaluation for this week already exists
                exists = Evaluation.objects.filter(
                    employee=employee,
                    manager=manager,
                    week_start=week_start,
                    week_end=week_end,
                ).exists()

                if exists:
                    continue

                Evaluation.objects.create(
                    employee=employee,
                    manager=manager,
                    week_start=week_start,
                    week_end=week_end,
                    avg_customer_satisfaction_score=0,
                    five_star_reviews=0,
                    negative_reviews=0,
                    late_arrivals=0,
                    absences=0,
                    reliability_rating=0,
                    avg_move_completion_time=timedelta(hours=0),
                    moves_within_schedule=0,
                    avg_revenue_per_move=0.0,
                    damage_claims=0,
                    safety_incidents=0,
                    consecutive_damage_free_moves=0,
                    notes='',
                    status='pending',
                    submitted_at=None,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {count} evaluation record(s)."))
