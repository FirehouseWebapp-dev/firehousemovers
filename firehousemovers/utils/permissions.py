"""
Global role-based permission utilities for the Firehouse Movers project.
Contains only basic user profile role checks.
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect


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
    Provides clean, readable methods for basic role checks.
    """
    
    def __init__(self, user_profile):
        self.user_profile = user_profile
    
    # Basic role checks
    def is_admin(self):
        """Check if user is admin (by role or Django admin)"""
        if not self.user_profile:
            return False
        return (self.user_profile.is_admin or 
                self.user_profile.user.is_staff or 
                self.user_profile.user.is_superuser)
    
    def is_senior_management(self):
        """Check if user is senior management (VP, CEO, LLC/Owner)"""
        return self.user_profile and self.user_profile.is_senior_management
    
    def is_manager(self):
        """Check if user is manager"""
        return self.user_profile and self.user_profile.is_manager
    
    def is_employee(self):
        """Check if user is employee (non-management)"""
        return self.user_profile and self.user_profile.is_employee
    
    # Specific role checks
    def is_llc_owner(self):
        """Check if user is LLC/Owner"""
        return self.user_profile and self.user_profile.role == "llc/owner"
    
    def is_vp(self):
        """Check if user is VP"""
        return self.user_profile and self.user_profile.role == "vp"
    
    def is_ceo(self):
        """Check if user is CEO"""
        return self.user_profile and self.user_profile.role == "ceo"
    
    def is_driver(self):
        """Check if user is driver"""
        return self.user_profile and self.user_profile.role == "driver"
    
    def is_mover(self):
        """Check if user is mover"""
        return self.user_profile and self.user_profile.role == "mover"
    
    def is_technician(self):
        """Check if user is technician"""
        return self.user_profile and self.user_profile.role == "technician"
    
    def is_warehouse(self):
        """Check if user is warehouse staff"""
        return self.user_profile and self.user_profile.role == "warehouse"
    
    def is_sales(self):
        """Check if user is sales staff"""
        return self.user_profile and self.user_profile.role == "sales"
    
    def is_field(self):
        """Check if user is field staff"""
        return self.user_profile and self.user_profile.role == "field"
    
    def is_rwh(self):
        """Check if user is RWH staff"""
        return self.user_profile and self.user_profile.role == "rwh"
    
    # Composite role checks
    def is_management(self):
        """Check if user is any type of management (admin, senior, or manager)"""
        return self.is_admin() or self.is_senior_management() or self.is_manager()
    
    def is_admin_or_senior(self):
        """Check if user is admin or senior management"""
        return self.is_admin() or self.is_senior_management()
    
    def is_manager_or_above(self):
        """Check if user is manager, senior management, or admin"""
        return self.is_manager() or self.is_admin_or_senior()
    
    def is_executive(self):
        """Check if user is executive level (CEO, VP, LLC/Owner)"""
        return self.is_ceo() or self.is_vp() or self.is_llc_owner()


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


def require_admin(view_func):
    """
    Decorator requiring admin role.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_admin():
            raise PermissionDenied("Admin access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_executive(view_func):
    """
    Decorator requiring executive role (CEO, VP, LLC/Owner).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_executive():
            raise PermissionDenied("Executive access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


# AJAX decorators (return JSON instead of raising exceptions)
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


def ajax_require_admin_or_senior(view_func):
    """
    Decorator for AJAX views requiring admin or senior management role.
    Returns JSON error instead of raising PermissionDenied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_admin_or_senior():
            return JsonResponse({
                'success': False, 
                'error': 'Admin or senior management access required.'
            }, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


# Redirect-based decorators (for views that should redirect instead of raise exceptions)
def redirect_require_management(view_func):
    """
    Decorator requiring management role with redirect on failure.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_management():
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('authentication:login')  # Adjust redirect as needed
        return view_func(request, *args, **kwargs)
    return wrapper


def redirect_require_admin_or_senior(view_func):
    """
    Decorator requiring admin or senior management role with redirect on failure.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        if not checker.is_admin_or_senior():
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('authentication:login')  # Adjust redirect as needed
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


# Django REST Framework permissions
try:
    from rest_framework import permissions
    
    class IsManagement(permissions.BasePermission):
        """
        Custom permission to allow access only to management users.
        """
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            checker = role_checker(request.user)
            return checker.is_management()


    class IsAdminOrSenior(permissions.BasePermission):
        """
        Custom permission to allow access only to admin or senior management users.
        """
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            checker = role_checker(request.user)
            return checker.is_admin_or_senior()


    class IsAdmin(permissions.BasePermission):
        """
        Custom permission to allow access only to admin users.
        """
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            checker = role_checker(request.user)
            return checker.is_admin()


    class IsExecutive(permissions.BasePermission):
        """
        Custom permission to allow access only to executive users (CEO, VP, LLC/Owner).
        """
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            checker = role_checker(request.user)
            return checker.is_executive()

except ImportError:
    # DRF not available, define dummy permissions
    class permissions:
        class BasePermission:
            pass
