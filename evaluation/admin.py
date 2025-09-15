from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models_dynamic import (
    EvalForm, Question, QuestionChoice, 
    DynamicEvaluation, Answer, 
    DynamicManagerEvaluation, ManagerAnswer
)


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 0
    fields = ('value', 'label')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'form', 'qtype', 'required', 'order', 'min_value', 'max_value')
    list_filter = ('qtype', 'required', 'form__department', 'form__name')
    search_fields = ('text', 'help_text', 'form__name')
    ordering = ('form', 'order', 'id')
    inlines = [QuestionChoiceInline]
    
    fieldsets = (
        (None, {
            'fields': ('form', 'text', 'help_text', 'qtype', 'required', 'order')
        }),
        ('Numeric Settings', {
            'fields': ('min_value', 'max_value'),
            'classes': ('collapse',)
        }),
    )


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('text', 'qtype', 'required', 'order')
    readonly_fields = ('order',)


@admin.register(EvalForm)
class EvalFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'is_active', 'created_by', 'created_at', 'question_count')
    list_filter = ('is_active', 'department', 'created_at')
    search_fields = ('name', 'description', 'department__title')
    ordering = ('-created_at',)
    inlines = [QuestionInline]
    
    fieldsets = (
        (None, {
            'fields': ('department', 'name', 'description', 'is_active', 'created_by')
        }),
    )
    
    def question_count(self, obj):
        count = obj.questions.count()
        if count > 0:
            url = reverse('admin:evaluation_question_changelist') + f'?form__id__exact={obj.id}'
            return format_html('<a href="{}">{} questions</a>', url, count)
        return "0 questions"
    question_count.short_description = "Questions"


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'int_value', 'text_value', 'choice_value')
    fields = ('question', 'int_value', 'text_value', 'choice_value')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DynamicEvaluation)
class DynamicEvaluationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'manager', 'form', 'week_start', 'week_end', 'status', 'submitted_at')
    list_filter = ('status', 'form__department', 'form__name', 'week_start', 'week_end')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 
                    'manager__user__first_name', 'manager__user__last_name',
                    'form__name')
    ordering = ('-week_start', '-submitted_at')
    readonly_fields = ('submitted_at',)
    inlines = [AnswerInline]
    
    fieldsets = (
        (None, {
            'fields': ('form', 'department', 'manager', 'employee', 'week_start', 'week_end', 'status')
        }),
        ('Submission', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )


class ManagerAnswerInline(admin.TabularInline):
    model = ManagerAnswer
    extra = 0
    readonly_fields = ('question', 'int_value', 'text_value', 'choice_value')
    fields = ('question', 'int_value', 'text_value', 'choice_value')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DynamicManagerEvaluation)
class DynamicManagerEvaluationAdmin(admin.ModelAdmin):
    list_display = ('manager', 'senior_manager', 'form', 'period_start', 'period_end', 'status', 'submitted_at')
    list_filter = ('status', 'form__department', 'form__name', 'period_start', 'period_end')
    search_fields = ('manager__user__first_name', 'manager__user__last_name',
                    'senior_manager__user__first_name', 'senior_manager__user__last_name',
                    'form__name')
    ordering = ('-period_start', '-submitted_at')
    readonly_fields = ('submitted_at',)
    inlines = [ManagerAnswerInline]
    
    fieldsets = (
        (None, {
            'fields': ('form', 'department', 'senior_manager', 'manager', 'period_start', 'period_end', 'status')
        }),
        ('Submission', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('instance', 'question', 'get_answer_display')
    list_filter = ('question__qtype', 'question__form__name', 'question__form__department')
    search_fields = ('instance__employee__user__first_name', 'instance__employee__user__last_name',
                    'question__text')
    ordering = ('-instance__week_start', 'question__order')
    
    def get_answer_display(self, obj):
        if obj.int_value is not None:
            return f"Number: {obj.int_value}"
        elif obj.text_value:
            preview = obj.text_value[:50] + "..." if len(obj.text_value) > 50 else obj.text_value
            return f"Text: {preview}"
        elif obj.choice_value:
            return f"Choice: {obj.choice_value}"
        return "No answer"
    get_answer_display.short_description = "Answer"


@admin.register(ManagerAnswer)
class ManagerAnswerAdmin(admin.ModelAdmin):
    list_display = ('instance', 'question', 'get_answer_display')
    list_filter = ('question__qtype', 'question__form__name', 'question__form__department')
    search_fields = ('instance__manager__user__first_name', 'instance__manager__user__last_name',
                    'question__text')
    ordering = ('-instance__period_start', 'question__order')
    
    def get_answer_display(self, obj):
        if obj.int_value is not None:
            return f"Number: {obj.int_value}"
        elif obj.text_value:
            preview = obj.text_value[:50] + "..." if len(obj.text_value) > 50 else obj.text_value
            return f"Text: {preview}"
        elif obj.choice_value:
            return f"Choice: {obj.choice_value}"
        return "No answer"
    get_answer_display.short_description = "Answer"


# Customize admin site header
admin.site.site_header = "Firehouse Movers Admin"
admin.site.site_title = "Firehouse Movers Admin Portal"
admin.site.index_title = "Welcome to Firehouse Movers Administration"
