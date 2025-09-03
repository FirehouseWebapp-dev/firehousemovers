"""
Custom template tags and filters for the goals app.
"""

from django import template
from ..utils.helpers import get_display_name, get_user_profile_display_name

register = template.Library()


@register.filter
def display_name(user):
    """
    Get a clean display name for a user.
    Usage: {{ user|display_name }}
    """
    try:
        return get_display_name(user)
    except (AttributeError, TypeError):
        return "Unknown User"


@register.filter
def profile_display_name(user_profile):
    """
    Get a clean display name for a user profile.
    Usage: {{ user_profile|profile_display_name }}
    """
    try:
        return get_user_profile_display_name(user_profile)
    except (AttributeError, TypeError):
        return "Unknown User"
