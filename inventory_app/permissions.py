from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Custom permission to allow access only to users with the 'manager' role.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user's role is 'manager'
        if request.user.is_superuser:
            return True

        userprofile = getattr(request.user, "userprofile", None)
        if not userprofile:
            return False
        role = getattr(userprofile, "role", None)
        return role in ["manager", "admin"] or userprofile.is_senior_management


from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def manager_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if not hasattr(request.user, "userprofile") or (request.user.userprofile.role not in ["manager", "admin"] and not request.user.userprofile.is_senior_management):
            messages.error(request, "You do not have permission to perform this action.")
            return redirect("awards:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
