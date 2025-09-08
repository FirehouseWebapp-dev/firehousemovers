from django.db import models
from authentication.models import UserProfile
from .models_dynamic import EvalForm, Question, QuestionChoice, DynamicEvaluation, Answer

class Evaluation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='evaluations')
    manager = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submitted_evaluations')
    week_start = models.DateField()
    week_end = models.DateField()

    # Customer Service Metrics
    avg_customer_satisfaction_score = models.PositiveSmallIntegerField()
    five_star_reviews = models.PositiveIntegerField()
    negative_reviews = models.PositiveIntegerField()

    # Attendance Metrics
    late_arrivals = models.PositiveIntegerField()
    absences = models.PositiveIntegerField()
    reliability_rating = models.PositiveSmallIntegerField()

    # Productivity Metrics
    avg_move_completion_time = models.DurationField()
    moves_within_schedule = models.PositiveIntegerField()
    avg_revenue_per_move = models.FloatField()

    # Safety Metrics
    damage_claims = models.PositiveIntegerField()
    safety_incidents = models.PositiveIntegerField()
    consecutive_damage_free_moves = models.PositiveIntegerField()

    # notes
    notes = models.TextField(blank=True, null=True)

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Submission details
    submitted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("employee", "week_start", "week_end")

    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.week_start} to {self.week_end}"


class ReviewCycle(models.Model):
    class CycleType(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"

    cycle_type = models.CharField(max_length=12, choices=CycleType.choices)
    period_start = models.DateField()
    period_end = models.DateField()
    is_open = models.BooleanField(default=True)  # can toggle when closed

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cycle_type", "period_start", "period_end")
        ordering = ["-period_start"]

    def __str__(self):
        return f"{self.get_cycle_type_display()} • {self.period_start} → {self.period_end}"


class ManagerEvaluation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
    ]

    cycle = models.ForeignKey(ReviewCycle, on_delete=models.CASCADE, related_name="manager_evaluations")

    # Who is being reviewed (must be a manager)
    subject_manager = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="received_manager_reviews"
    )

    # Who reviews (must be senior mgmt or admin)
    reviewer = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="authored_manager_reviews"
    )

    # Core fields you requested
    regular_evaluations = models.TextField(blank=True)  # “Regular Evaluations”
    performance_summary = models.TextField(blank=True)  # “Quarterly or monthly performance summaries”
    supervisors_comments = models.TextField(blank=True)  # “Supervisor’s comments and observations”
    annual_review = models.TextField(blank=True)  # “Annual Performance Review”
    goals_achieved = models.TextField(blank=True)  # “Goals achieved”
    objectives_set = models.TextField(blank=True)  # “Set objectives”
    strengths = models.TextField(blank=True)
    improvement_areas = models.TextField(blank=True)

    # Optional overall rating
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1–5

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    submitted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cycle", "subject_manager", "reviewer")
        ordering = ["subject_manager__user__last_name", "subject_manager__user__first_name"]

    def __str__(self):
        subj = self.subject_manager.user.get_full_name() or self.subject_manager.user.username
        return f"{self.cycle} • {subj} (by {self.reviewer.user.username})"