from django.db import models
from authentication.models import UserProfile


class Goal(models.Model):
    GOAL_TYPE_CHOICES = [
        ("short_term", "Short-Term"),
        ("long_term", "Long-Term"),
    ]

    title = models.CharField(max_length=200, help_text="Goal title")
    description = models.TextField(blank=True, help_text="Detailed description of the goal")
    assigned_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='goals')
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='created_goals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null =True, help_text="Any notes or updates on the goal")
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default="short_term")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Goal"
        verbose_name_plural = "Goals"
        ordering = ['due_date', 'title']

