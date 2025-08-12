from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "manager_display",
        "phone_number",
        "start_date",
        # new: quick flags overview
        "is_admin",
        "is_senior_management",
        "is_manager",
        "is_employee",
    )

    # new: allow toggling flags right from the list page
    list_editable = (
        "is_admin",
        "is_senior_management",
        "is_manager",
        "is_employee",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "role",
        "phone_number",
    )
    list_filter = (
        "role",
        "start_date",
        # new: filter by flags
        "is_admin",
        "is_senior_management",
        "is_manager",
        "is_employee",
    )
    autocomplete_fields = ["user", "manager"]
    ordering = ("-start_date",)
    list_select_related = ("user", "manager")
    readonly_fields = ("profile_picture_preview",)

    fieldsets = (
        ("User Info", {
            "fields": ("user", "role", "manager")
        }),
        ("Role Flags (manual override if needed)", {
            "fields": (
                "is_admin",
                "is_senior_management",
                "is_manager",
                "is_employee",
            )
        }),
        ("Contact", {
            "fields": ("phone_number", "location", "start_date")
        }),
        ("Profile Media", {
            "fields": ("profile_picture", "profile_picture_preview")
        }),
        ("Personal", {
            "fields": ("hobbies", "favourite_quote")
        }),
    )

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="100" style="border-radius: 8px;" />', obj.profile_picture.url)
        return "No picture"
    profile_picture_preview.short_description = "Preview"

    def manager_display(self, obj):
        if obj.manager and obj.manager.user:
            return obj.manager.user.get_full_name() or obj.manager.user.username
        return "None"
    manager_display.short_description = "Manager"
    manager_display.admin_order_field = "manager__user__username"

    def save_model(self, request, obj, form, change):
        """
        If an admin explicitly edits any of the flag checkboxes,
        save exactly what they set. Otherwise, let model.save() compute
        flags from role buckets (and Django user staff/superuser).
        """
        flag_fields = {"is_admin", "is_senior_management", "is_manager", "is_employee"}
        if change and any(field in form.changed_data for field in flag_fields):
            # Admin made an explicit choice; respect it.
            super().save_model(request, obj, form, change)
        else:
            # No manual change to flags; let model.save() recompute from role.
            obj.save()
