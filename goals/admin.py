from .models import Goal
from authentication.models import UserProfile
from django.contrib import admin

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "goal_type",
        "assigned_to",
        "created_by",
        "created_at",
        "is_completed",
    )
    
    list_filter = (
        "goal_type",
        "created_by",
        "created_at",
        "is_completed",
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
    
    def save_model(self, request, obj, form, change):
        if not change:  # new goal
            obj.created_by = request.user.userprofile
        super().save_model(request, obj, form, change)


# Register your models here.
