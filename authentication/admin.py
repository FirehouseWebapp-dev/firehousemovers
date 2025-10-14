from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Department, DepartmentQuiz, QuizAttempt

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description", "manager")
    # ✅ REQUIRED for other admins' autocomplete_fields to work
    search_fields = (
        "title",
        "slug",
        "description",
        "manager__user__first_name",
        "manager__user__last_name",
        "manager__user__username",
        "manager__user__email",
    )
    list_select_related = ("manager__user",)

    def has_module_permission(self, request):
        """Show Department section only for senior management/admins."""
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.is_senior_management
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "manager_display",
        "start_date",
        "department",
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
        "department__title",
    )
    list_filter = (
        "role",
        "start_date",
        "department",
        "is_admin",
        "is_senior_management",
        "is_manager",
        "is_employee",
    )
    autocomplete_fields = ["user", "manager"]
    ordering = ("-start_date",)
    list_select_related = ("user", "manager__user", "department")
    readonly_fields = ("profile_picture_preview",)

    fieldsets = (
        ("User Info", {
            "fields": ("user", "role", "department", "manager")
        }),
        ("Role Flags (manual override if needed)", {
            "fields": ("is_admin", "is_senior_management", "is_manager", "is_employee")
        }),
        ("Contact", {
            "fields": ("phone_number",)
        }),
        ("Media", {
            "fields": ("profile_picture", "profile_picture_preview")
        }),
        ("Dates", {
            "fields": ("start_date",)
        }),
    )

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="100" style="border-radius: 8px;" />', obj.profile_picture.url)
        return "No picture"
    profile_picture_preview.short_description = "Preview"

    def manager_display(self, obj):
        if obj.manager and obj.manager.user:
            name = obj.manager.user.get_full_name() or obj.manager.user.username
            return format_html('<a href="/admin/authentication/userprofile/{}/change/">{}</a>', obj.manager.id, name)
        return "—"
    manager_display.short_description = "Manager"


@admin.register(DepartmentQuiz)
class DepartmentQuizAdmin(admin.ModelAdmin):
    list_display = ("department", "audience", "order", "question_preview", "correct_answer")
    list_filter = ("department", "audience")
    search_fields = ("question_text", "department__title")
    ordering = ("department", "audience", "order")
    list_editable = ("order",)
    
    fieldsets = (
        ("Question Info", {
            "fields": ("department", "audience", "question_text", "order")
        }),
        ("Answer Options", {
            "fields": ("option_a", "option_b", "option_c", "option_d", "correct_answer")
        }),
    )
    
    def question_preview(self, obj):
        return obj.question_text[:60] + "..." if len(obj.question_text) > 60 else obj.question_text
    question_preview.short_description = "Question"


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "quiz_type", "score", "total_questions", "percentage", "completed_at")
    list_filter = ("department", "quiz_type", "completed_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "department__title")
    readonly_fields = ("user", "department", "quiz_type", "score", "total_questions", "completed_at", "percentage")
    ordering = ("-completed_at",)
    
    def has_add_permission(self, request):
        return False