from .models import Goal
from authentication.models import UserProfile
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Q 
from django.contrib.auth import get_user_model

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
    
    def has_module_permission(self, request):
        return request.user.is_authenticated
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        try:
            user_profile = request.user.userprofile
            return user_profile.is_senior_management or user_profile.is_manager
        except UserProfile.DoesNotExist:
            return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        try:
            user_profile = request.user.userprofile
            return user_profile.is_senior_management or user_profile.is_manager
        except UserProfile.DoesNotExist:
            return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        try:
            user_profile = request.user.userprofile
            return user_profile.is_senior_management or user_profile.is_manager
        except UserProfile.DoesNotExist:
            return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if not request.user.is_authenticated:
            return qs.none()
        try:
            user_profile = request.user.userprofile
            if user_profile.is_senior_management or user_profile.is_manager:
                return qs
            else:
                return qs.filter(assigned_to=user_profile)
        except UserProfile.DoesNotExist:
            return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Custom dropdown filters for admin site:
        - assigned_to: exclude logged-in user
        - created_by: only managers / senior management (with team) + admins
        """
        try:
            current_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            current_profile = None
        # For assigned_to → exclude logged-in user
        if db_field.name == "assigned_to" and current_profile:
            kwargs["queryset"] = UserProfile.objects.exclude(id=current_profile.id)

        # For created_by → only managers with team OR senior management OR admins
        if db_field.name == "created_by":
            kwargs["queryset"] = UserProfile.objects.filter(
                Q(is_manager=True) |                    # All managers
                Q(is_senior_management=True) |           # Senior management
                Q(is_admin=True)                         # Admins
            ).distinct()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Prevent assigning a goal to yourself.
        """
        try:
            if obj.assigned_to and request.user.userprofile and obj.assigned_to == request.user.userprofile:
                raise ValidationError("You cannot assign a goal to yourself.")
        except UserProfile.DoesNotExist:
            # Superuser or user without UserProfile - skip the validation
            pass

        super().save_model(request, obj, form, change)

# Register your models here.
