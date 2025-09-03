from django.db import models
from authentication.models import UserProfile
from django.utils import timezone
from django.core.exceptions import ValidationError
from .utils.validators import validate_future_date, validate_goal_title_length, validate_goal_description_length, validate_max_active_goals

class Goal(models.Model):
    GOAL_TYPE_CHOICES = [
        ("short_term", "Short-Term"),
        ("long_term", "Long-Term"),
    ]

    title = models.CharField(max_length=200, help_text="Goal title", validators=[validate_goal_title_length])
    description = models.TextField(blank=False, help_text="Detailed description of the goal", validators=[validate_goal_description_length])
    assigned_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='goals')
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='created_goals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True, help_text="Due date for the goal", validators=[validate_future_date])
    completed_at = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null =True, help_text="Any notes or updates on the goal")
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default="short_term")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track original completion status to prevent unauthorized changes
        self._original_is_completed = self.is_completed


    def clean(self):
        """Custom validation for the Goal model"""
        super().clean()
        
        # Validate title length
        if self.title:
            validate_goal_title_length(self.title)
        
        # Validate description length  
        if self.description:
            validate_goal_description_length(self.description)
        
        # Validate due date is not in the past
        if self.due_date:
            validate_future_date(self.due_date)
        
        # Validate completion status changes (prevent uncompleting goals)
        if hasattr(self, '_original_is_completed') and self._original_is_completed and not self.is_completed:
            raise ValidationError("Completed goals cannot be marked as incomplete.")

        # For new goals, this validation is handled in the view after assigned_to is set
        if (not self.is_completed and 
            self.pk and  # Only for existing goals being updated
            hasattr(self, 'assigned_to') and self.assigned_to):
            exclude_id = self.pk
            validate_max_active_goals(self.assigned_to, exclude_goal_id=exclude_id)

    def save(self, *args, **kwargs):
        # call full_clean() so clean() always runs
        self.full_clean()

        # completion timestamp logic
        if self.is_completed and self.completed_at is None:
            self.completed_at = timezone.now().date()
        elif not self.is_completed:
            self.completed_at = None

        super().save(*args, **kwargs)
        
        # Update tracked completion status after save
        self._original_is_completed = self.is_completed
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "Goal"
        verbose_name_plural = "Goals"
        ordering = ['due_date', 'title']

