"""
Role-based permission utilities for the Goals app.
Eliminates repetitive role checking code throughout views and templates.
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def get_user_profile_safe(user):
    """
    Safely get user profile with None fallback.
    
    Args:
        user: Django User instance
        
    Returns:
        UserProfile instance or None if not found
    """
    return getattr(user, 'userprofile', None)


class RoleChecker:
    """
    Centralized role checking utility class.
    Provides clean, readable methods for all permission scenarios.
    """
    
    def __init__(self, user_profile):
        self.user_profile = user_profile
    
    # Basic role checks
    def is_admin(self):
        """Check if user is admin (by role)"""
        return self.user_profile and self.user_profile.is_admin
    
    def is_senior_management(self):
        """Check if user is senior management"""
        return self.user_profile and self.user_profile.is_senior_management
    
    def is_manager(self):
        """Check if user is manager"""
        return self.user_profile and self.user_profile.is_manager
    
    def is_employee(self):
        """Check if user is employee (non-management)"""
        return self.user_profile and self.user_profile.is_employee
    
    # Composite role checks (common patterns)
    def is_management(self):
        """Check if user is any type of management (admin, senior, or manager)"""
        return self.is_admin() or self.is_senior_management() or self.is_manager()
    
    def is_admin_or_senior(self):
        """Check if user is admin or senior management"""
        return self.is_admin() or self.is_senior_management()
    
    def is_manager_or_above(self):
        """Check if user is manager, senior management, or admin"""
        return self.is_manager() or self.is_admin_or_senior()
    
    # Goal-specific permission checks
    def can_manage_goals(self):
        """Check if user can manage goals (add, edit, delete for others)"""
        return self.is_management()
    
    def can_view_all_employees(self):
        """Check if user can view all employees (not just their team)"""
        return self.is_admin_or_senior()
    
    def can_add_goals_for(self, target_user_profile):
        """
        Check if user can add goals for target user.
        
        Args:
            target_user_profile: UserProfile of the target user
            
        Returns:
            bool: True if permission granted
        """
        if not self.user_profile or not target_user_profile:
            return False
            
        # Can't add goals for admins or senior management
        if target_user_profile.role == "admin" or target_user_profile.is_senior_management:
            return False
            
        # Admin can add for anyone (except other admins/senior)
        if self.is_admin():
            return True
            
        # Senior management can add for anyone (except other admins/senior)
        if self.is_senior_management():
            return True
            
        # Managers can only add for their direct reports
        if self.is_manager():
            return target_user_profile.manager_id == self.user_profile.id
            
        return False
    
    def can_edit_goal(self, goal):
        """
        Check if user can edit a specific goal.
        
        Args:
            goal: Goal instance
            
        Returns:
            bool: True if permission granted
        """
        if not self.user_profile:
            return False
            
        # Admin or senior management can edit any goal
        if self.is_admin_or_senior():
            return True
            
        # Managers can edit goals for their direct reports
        if self.is_manager() and goal.assigned_to.manager_id == self.user_profile.id:
            return True
            
        return False
    
    def can_delete_goal(self, goal):
        """
        Check if user can delete a specific goal.
        Same logic as edit for now.
        
        Args:
            goal: Goal instance
            
        Returns:
            bool: True if permission granted
        """
        return self.can_edit_goal(goal)
    
    def can_toggle_goal_completion(self, goal):
        """
        Check if user can toggle goal completion status.
        Users cannot complete their own goals - only managers can complete their team's goals.
        
        Args:
            goal: Goal instance
            
        Returns:
            bool: True if permission granted
        """
        if not self.user_profile:
            return False
            
        # Users cannot toggle their own goals
        if goal.assigned_to == self.user_profile:
            return False
            
        # Managers can toggle for their team
        if self.is_manager() and goal.assigned_to.manager_id == self.user_profile.id:
            return True
            
        # Senior management can toggle any goal
        if self.is_senior_management():
            return True
            
        return False


def role_checker(user):
    """
    Factory function to create RoleChecker instance.
    
    Args:
        user: Django User instance
        
    Returns:
        RoleChecker instance
    """
    user_profile = get_user_profile_safe(user)
    return RoleChecker(user_profile)


# Decorators for view-level permission checking
def require_management(view_func):
    """
    Decorator requiring management role (admin, senior, or manager).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_management():
            raise PermissionDenied("Management access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_manager_or_above(view_func):
    """
    Decorator requiring manager role or above.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_manager_or_above():
            raise PermissionDenied("Manager access or above required.")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_admin_or_senior(view_func):
    """
    Decorator requiring admin or senior management role.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_admin_or_senior():
            raise PermissionDenied("Admin or senior management access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


def ajax_require_management(view_func):
    """
    Decorator for AJAX views requiring management role.
    Returns JSON error instead of raising PermissionDenied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_management():
            return JsonResponse({
                'success': False, 
                'error': 'Management access required.'
            }, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


# Template context processor helper
def role_context(request):
    """
    Context processor to add role checking to templates.
    Usage in templates: {% if role.is_manager %}...{% endif %}
    """
    if request.user.is_authenticated:
        return {'role': role_checker(request.user)}
    return {'role': RoleChecker(None)}
