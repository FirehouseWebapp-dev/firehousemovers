"""
Custom validators for the Goals app.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date


def validate_future_date(value):
    """
    Validate that a date is in the future.
    
    Args:
        value: Date value to validate
        
    Raises:
        ValidationError: If date is not in the future
    """
    if value and value <= timezone.now().date():
        raise ValidationError("Due date must be in the future.")


def validate_goal_title_length(value):
    """
    Validate goal title has appropriate length.
    
    Args:
        value (str): Title string to validate
        
    Raises:
        ValidationError: If title is too short or too long
    """
    if len(value.strip()) < 3:
        raise ValidationError("Goal title must be at least 3 characters long.")
    if len(value.strip()) > 200:
        raise ValidationError("Goal title cannot exceed 200 characters.")


def validate_goal_description_length(value):
    """
    Validate goal description has appropriate length.
    
    Args:
        value (str): Description string to validate
        
    Raises:
        ValidationError: If description is too short or too long
    """
    if len(value.strip()) < 10:
        raise ValidationError("Goal description must be at least 10 characters long.")
    if len(value.strip()) > 1000:
        raise ValidationError("Goal description cannot exceed 1000 characters.")


def validate_max_active_goals(user_profile, exclude_goal_id=None):
    """
    Validate that user doesn't exceed maximum active goals limit.
    
    Args:
        user_profile: UserProfile instance
        exclude_goal_id (int, optional): Goal ID to exclude from count (for updates)
        
    Raises:
        ValidationError: If user would exceed the limit
    """
    from ..models import Goal  # Import here to avoid circular imports
    
    active_goals = Goal.objects.filter(
        assigned_to=user_profile,
        is_completed=False
    )
    
    if exclude_goal_id:
        active_goals = active_goals.exclude(id=exclude_goal_id)
    
    if active_goals.count() >= 10:
        raise ValidationError(
            f"{user_profile.user.get_full_name()} already has the maximum of 10 active goals."
        )
