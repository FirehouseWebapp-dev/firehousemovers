"""
Utilities package for the Goals app.

This package contains reusable utility functions, helpers, validators,
and permission checks to eliminate code duplication and improve maintainability.
"""

# Import commonly used utilities for easier access
from .permissions import role_checker, get_user_profile_safe
from .helpers import calculate_goal_progress_percentage, format_goal_status
from .validators import validate_future_date, validate_max_active_goals

__all__ = [
    'role_checker',
    'get_user_profile_safe', 
    'calculate_goal_progress_percentage',
    'format_goal_status',
    'validate_future_date',
    'validate_max_active_goals',
]