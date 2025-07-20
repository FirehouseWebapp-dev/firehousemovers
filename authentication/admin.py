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
        "start_date"
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "role",
        "phone_number"
    )
    list_filter = (
        "role",
        "start_date"
    )
    autocomplete_fields = ["user", "manager"]
    ordering = ("-start_date",)
    list_select_related = ("user", "manager")
    readonly_fields = ("profile_picture_preview",)

    fieldsets = (
        ("User Info", {
            "fields": ("user", "role", "manager")
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
        return obj.manager.user.username if obj.manager else "None"

    manager_display.short_description = "Manager"
