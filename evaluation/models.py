from django.db import models
from authentication.models import UserProfile

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
