from .models import Goal
from authentication.models import UserProfile
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Q 
from django.contrib.auth import get_user_model
from .utils.permissions import role_checker, get_user_profile_safe

User = get_user_model()

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "goal_type",
        "assigned_to",
        "created_by",
        "created_at",
        "is_completed",
        "completed_at",
        "due_date"
    )

    list_filter = (
        "goal_type",
        "created_by",
        "created_at",
        "is_completed",
        "completed_at",
        "due_date"
    )
    
    search_fields = (
        "title",
        "description",
        "notes",
        "assigned_to__user__username",
        "assigned_to__user__first_name",
        "assigned_to__user__last_name",
        "created_by__user__username",
        "created_by__user__first_name",
        "created_by__user__last_name",
    )
    
    autocomplete_fields = ["assigned_to", "created_by"]
    
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Goal Information", {
            "fields": ("title", "goal_type", "description", "notes", "is_completed")
        }),
        ("Assignment", {
            "fields": ("assigned_to", "created_by")
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def _can_manage_goals(self, request):
        """
        Helper method to check if user can manage goals (add/change/delete).
        Centralizes the permission logic to avoid duplication.
        """
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        
        checker = role_checker(request.user)
        return checker.is_manager_or_above()
    
    def has_module_permission(self, request):
        return request.user.is_authenticated
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated
    
    def has_add_permission(self, request):
        return self._can_manage_goals(request)
    
    def has_change_permission(self, request, obj=None):
        return self._can_manage_goals(request)
    
    def has_delete_permission(self, request, obj=None):
        return self._can_manage_goals(request)
    
    def get_queryset(self, request):
        # Optimize queryset with select_related to prevent N+1 queries
        qs = super().get_queryset(request).select_related(
            'assigned_to__user', 
            'assigned_to__manager', 
            'created_by__user'
        )
        
        if request.user.is_superuser:
            return qs
        if not request.user.is_authenticated:
            return qs.none()
        
        user_profile = get_user_profile_safe(request.user)
        if not user_profile:
            return qs.none()
            
        checker = role_checker(request.user)
        if checker.is_manager_or_above():
            return qs
        else:
            # Regular employees only see their own goals
            return qs.filter(assigned_to=user_profile)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Custom dropdown filters for admin site with optimized queries:
        - assigned_to: exclude logged-in user
        - created_by: only managers / senior management (with team) + admins
        """
        current_profile = get_user_profile_safe(request.user)
        
        # For assigned_to → exclude logged-in user and optimize with select_related
        if db_field.name == "assigned_to":
            queryset = UserProfile.objects.select_related('user', 'department')
            if current_profile:
                queryset = queryset.exclude(id=current_profile.id)
            kwargs["queryset"] = queryset

        # For created_by → only managers with team OR senior management OR admins
        if db_field.name == "created_by":
            kwargs["queryset"] = UserProfile.objects.select_related('user', 'department').filter(
                Q(is_manager=True) |                    # All managers
                Q(is_senior_management=True) |           # Senior management
                Q(is_admin=True)                         # Admins
            ).distinct()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Prevent assigning a goal to yourself.
        """
        current_profile = get_user_profile_safe(request.user)
        if obj.assigned_to and current_profile and obj.assigned_to == current_profile:
            raise ValidationError("You cannot assign a goal to yourself.")

        super().save_model(request, obj, form, change)

# Register your models here.
