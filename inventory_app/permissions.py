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
        if request.user.userprofile.role != "manager":
            return False

        return True
