"""
General helper functions for the Goals app.
"""
from django.utils import timezone
from datetime import datetime, date


def calculate_goal_progress_percentage(completed_goals, total_goals):
    """
    Calculate goal completion percentage.
    
    Args:
        completed_goals (int): Number of completed goals
        total_goals (int): Total number of goals
        
    Returns:
        int: Percentage (0-100) rounded to nearest integer
    """
    if total_goals == 0:
        return 0
    return round((completed_goals / total_goals) * 100)


def is_goal_overdue(goal):
    """
    Check if a goal is overdue based on its due date.
    
    Args:
        goal: Goal instance with due_date field
        
    Returns:
        bool: True if goal is overdue, False otherwise
    """
    if not goal.due_date or goal.is_completed:
        return False
    
    today = timezone.now().date()
    return goal.due_date < today


def format_goal_status(goal):
    """
    Get a human-readable status string for a goal.
    
    Args:
        goal: Goal instance
        
    Returns:
        str: Status description
    """
    if goal.is_completed:
        return "Completed"
    elif is_goal_overdue(goal):
        return "Overdue"
    elif goal.due_date:
        days_left = (goal.due_date - timezone.now().date()).days
        if days_left <= 3:
            return f"Due in {days_left} day{'s' if days_left != 1 else ''}"
        else:
            return "In Progress"
    else:
        return "In Progress"


def get_goal_type_display_color(goal_type):
    """
    Get CSS color class for goal type display.
    
    Args:
        goal_type (str): Goal type value
        
    Returns:
        str: CSS class name for color
    """
    color_map = {
        'short_term': 'text-blue-400',
        'long_term': 'text-green-400',
        'performance': 'text-yellow-400',
        'development': 'text-purple-400',
        'behavioral': 'text-pink-400',
    }
    return color_map.get(goal_type, 'text-gray-400')


def get_display_name(user):
    """
    Get a clean display name for a user.
    Replaces the common pattern: user.get_full_name|default:user.username|capfirst
    
    Args:
        user: User instance
        
    Returns:
        str: Formatted display name
    """
    if user.get_full_name().strip():
        return user.get_full_name().strip()
    return user.username.capitalize() if user.username else "Unknown User"


def get_user_profile_display_name(user_profile):
    """
    Get display name from a UserProfile instance.
    
    Args:
        user_profile: UserProfile instance
        
    Returns:
        str: Formatted display name
    """
    return get_display_name(user_profile.user)


def get_goal_counts_summary(goal_count, max_goals=10):
    """
    Get a formatted goal count summary.
    
    Args:
        goal_count: Number of active goals
        max_goals: Maximum allowed goals (default: 10)
        
    Returns:
        str: Formatted count like "5/10 Active Goals"
    """
    return f"{goal_count or 0}/{max_goals} Active Goals"


def can_add_more_goals(existing_count, max_goals=10):
    """
    Check if more goals can be added.
    
    Args:
        existing_count: Current number of goals
        max_goals: Maximum allowed goals (default: 10)
        
    Returns:
        bool: True if more goals can be added
    """
    return (existing_count or 0) < max_goals


def get_goal_status_indicator(goal_count):
    """
    Get a status indicator message for goal count.
    
    Args:
        goal_count: Number of active goals
        
    Returns:
        str: Status message like "✓ Has 3 active goals"
    """
    count = goal_count or 0
    if count == 0:
        return "No active goals"
    elif count == 1:
        return f"✓ Has {count} active goal"
    else:
        return f"✓ Has {count} active goals"


def get_empty_state_message(role_checker, has_team_members=True):
    """
    Get appropriate empty state message based on user role.
    
    Args:
        role_checker: RoleChecker instance
        has_team_members: Whether user has team members
        
    Returns:
        str: Appropriate empty state message
    """
    if role_checker.is_manager() and not has_team_members:
        return "You have no team members assigned to you. Please add some."
    elif role_checker.is_senior_management():
        return "No employees with goals found. Add some team members or assign goals."
    else:
        return "No goals found."
