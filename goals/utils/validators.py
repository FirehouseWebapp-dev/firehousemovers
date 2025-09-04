"""
Custom validators for the Goals app.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date


def validate_future_date(value):
    """
    Validate that a date is today or in the future (not in the past).
    
    Args:
        value: Date value to validate
        
    Raises:
        ValidationError: If date is in the past
    """
    if value and value < timezone.now().date():
        raise ValidationError("You cannot choose due date from the past")


def validate_goal_title_length(value):
    """
    Validate goal title has appropriate length.
    
    Args:
        value (str): Title string to validate
        
    Raises:
        ValidationError: If title is too short or too long
    """
    if not value:  # Handle None, empty string, etc.
        return  # Let required field validation handle empty values
    
    trimmed_value = value.strip()
    if len(trimmed_value) < 3:
        raise ValidationError("Goal title must be at least 3 characters long.")
    if len(trimmed_value) > 200:
        raise ValidationError("Goal title cannot exceed 200 characters.")


def validate_goal_description_length(value):
    """
    Validate goal description has appropriate length.
    
    Args:
        value (str): Description string to validate
        
    Raises:
        ValidationError: If description is too short or too long
    """
    if not value:  # Handle None, empty string, etc.
        return  # Let required field validation handle empty values
    
    trimmed_value = value.strip()
    if len(trimmed_value) < 10:
        raise ValidationError("Goal description must be at least 10 characters long.")
    if len(trimmed_value) > 1000:
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
