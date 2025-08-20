from django.contrib import admin
from .models import Evaluation
from .models import ReviewCycle, ManagerEvaluation

@admin.register(ReviewCycle)
class ReviewCycleAdmin(admin.ModelAdmin):
    list_display = ("cycle_type", "period_start", "period_end", "is_open", "created_at")
    list_filter = ("cycle_type", "is_open")
    ordering = ("-period_start",)
    search_fields = ("period_start", "period_end")


@admin.register(ManagerEvaluation)
class ManagerEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "cycle",
        "subject_manager",
        "reviewer",
        "status",
        "overall_rating",
        "submitted_at",
    )
    list_filter = ("status", "cycle__cycle_type")
    search_fields = (
        "subject_manager__user__first_name",
        "subject_manager__user__last_name",
        "reviewer__user__first_name",
        "reviewer__user__last_name",
    )
    autocomplete_fields = ("cycle", "subject_manager", "reviewer")


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'manager',
        'week_start',
        'customer_satisfaction_display',
        'status',
        'submitted_at',
    )

    EMOJI_MAP = {
        1: "😡",
        2: "😕",
        3: "😐",
        4: "🙂",
        5: "😍",
    }

    @admin.display(description="Customer Satisfaction")
    def customer_satisfaction_display(self, obj):
        return self.EMOJI_MAP.get(obj.avg_customer_satisfaction_score, "-")

