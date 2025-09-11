from django.contrib import admin
from .models import Evaluation
from .models import ReviewCycle, ManagerEvaluation
from .models_dynamic import EvalForm, Question, QuestionChoice, DynamicEvaluation, Answer

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

class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "form", "qtype", "required", "order")
    list_filter  = ("qtype", "required", "form__department")
    search_fields = ("text", "form__name", "form__department__title")
    inlines = [QuestionChoiceInline]

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    show_change_link = True

@admin.register(EvalForm)
class EvalFormAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "is_active", "created_at")
    list_filter  = ("is_active", "department")
    search_fields = ("name", "department__title")
    inlines = [QuestionInline]

@admin.register(DynamicEvaluation)
class DynamicEvaluationAdmin(admin.ModelAdmin):
    list_display = ("employee", "manager", "department", "week_start", "status")
    list_filter  = ("status", "department", "form")
    search_fields = ("employee__user__username", "employee__user__first_name", "employee__user__last_name")
    date_hierarchy = "week_start"
    autocomplete_fields = ("employee", "manager", "form", "department")

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("instance", "question", "int_value", "choice_value")
    list_filter  = ("question__qtype", "instance__status", "instance__department")
