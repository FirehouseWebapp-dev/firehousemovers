from __future__ import annotations
from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import UserProfile, Department
from .constants import EvaluationStatus


class EvalForm(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="eval_forms")
    name = models.CharField(max_length=120, default="Weekly Evaluation")
    slug = models.SlugField(max_length=120, null=True, blank=True, help_text="URL-friendly identifier (not editable)")
    description = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Business rule: Only one active form per department per evaluation type
        # This is enforced by a unique partial index created in migration 0017
        indexes = [
            models.Index(fields=["department_id", "is_active"]),  # For department + active filtering
            models.Index(fields=["is_active"]),  # For active form queries
            models.Index(fields=["name", "department_id"]),  # For form name + department queries
        ]

    def __str__(self) -> str:
        dept_name = self.department.title if self.department else "Unknown Department"
        return f"{dept_name} • {self.name}{' (active)' if self.is_active else ''}"
    


class Question(models.Model):
    class QType(models.TextChoices):
        SECTION = "section", "Section header (no input)"   # ✅ NEW
        STARS  = "stars",  "Star rating (1–5)"
        EMOJI  = "emoji",  "Emoji satisfaction (1–5)"
        RATING = "rating", "Plain rating (1–5 or 0–10)"
        SHORT  = "short",  "Short text"
        LONG   = "long",   "Long text"
        NUMBER = "number", "Number"
        BOOL   = "bool",   "Yes/No"
        SELECT = "select", "Single select"

    form = models.ForeignKey(EvalForm, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=300)
    help_text = models.CharField(max_length=300, blank=True, default="")
    qtype = models.CharField(max_length=20, choices=QType.choices, default=QType.STARS)
    required = models.BooleanField(default=True)

    # For numeric scales
    min_value = models.IntegerField(null=True, blank=True, default=1)
    max_value = models.IntegerField(null=True, blank=True, default=5)

    order = models.PositiveIntegerField(default=0)
    include_in_trends = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]

    def clean(self):
        """Validate model-level constraints."""
        super().clean()
        
        # Enforce max_value limits based on question type
        if self.qtype in [self.QType.STARS, self.QType.EMOJI] and self.max_value is not None and self.max_value > 5:
            raise ValidationError({
                'max_value': 'Maximum value cannot exceed 5 for star and emoji rating questions.'
            })
        elif self.qtype == self.QType.RATING and self.max_value is not None and self.max_value > 10:
            raise ValidationError({
                'max_value': 'Maximum value cannot exceed 10 for plain rating questions.'
            })
        
        # Ensure min_value is not greater than max_value
        if (self.min_value is not None and self.max_value is not None and 
            self.min_value > self.max_value):
            raise ValidationError({
                'min_value': 'Minimum value cannot be greater than maximum value.'
            })
        
        # Ensure min_value is not negative for any question type that uses it
        numeric_qtypes = [self.QType.STARS, self.QType.EMOJI, self.QType.RATING, self.QType.NUMBER]
        if self.qtype in numeric_qtypes and self.min_value is not None and self.min_value < 0:
            raise ValidationError({
                'min_value': f'Minimum value cannot be negative for {self.qtype} questions.'
            })

    def save(self, *args, **kwargs):
        """Override save to run model validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"[{self.qtype}] {self.text[:50]}"


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    value = models.CharField(max_length=100)
    label = models.CharField(max_length=120)

    class Meta:
        unique_together = [("question", "value")]
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.label}"


class DynamicEvaluation(models.Model):
    STATUS = (
        (EvaluationStatus.PENDING, "Pending"), 
        (EvaluationStatus.COMPLETED, "Completed")
    )

    form = models.ForeignKey(EvalForm, on_delete=models.PROTECT, related_name="instances")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="dynamic_evaluations")
    manager = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name="dynamic_mgr_evaluations")
    employee = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name="dynamic_emp_evaluations")

    week_start = models.DateField()
    week_end   = models.DateField()

    status = models.CharField(max_length=10, choices=STATUS, default=EvaluationStatus.PENDING)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = [("employee", "week_start", "week_end", "form")]
        indexes = [
            models.Index(fields=["week_start", "week_end", "employee_id"]),
            models.Index(fields=["manager_id", "status"]),
            # Performance indexes for common filtering patterns
            models.Index(fields=["status"]),  # For status filtering
            models.Index(fields=["submitted_at"]),  # For recent activity queries
            models.Index(fields=["department_id", "status"]),  # For department + status filtering
            models.Index(fields=["employee_id", "status"]),  # For employee + status filtering
            models.Index(fields=["week_end", "status"]),  # For overdue calculations
            models.Index(fields=["submitted_at", "status"]),  # For recent completed evaluations
        ]

    def __str__(self) -> str:
        return f"{self.employee} • {self.week_start}–{self.week_end} ({self.form})"


class Answer(models.Model):
    instance = models.ForeignKey(DynamicEvaluation, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)

    int_value   = models.IntegerField(null=True, blank=True)   # rating/number/bool(0/1)
    text_value  = models.TextField(null=True, blank=True)      # short/long
    choice_value = models.CharField(max_length=100, null=True, blank=True)  # select

    class Meta:
        unique_together = [("instance", "question")]


# Manager Evaluation Models - Using same structure as employee evaluations
class DynamicManagerEvaluation(models.Model):
    """Dynamic evaluations for managers, evaluated by senior managers."""
    STATUS = (
        (EvaluationStatus.PENDING, "Pending"), 
        (EvaluationStatus.COMPLETED, "Completed")
    )

    form = models.ForeignKey(EvalForm, on_delete=models.PROTECT, related_name="manager_instances")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="dynamic_manager_evaluations")
    senior_manager = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name="dynamic_senior_evaluations")
    manager = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name="dynamic_manager_reviews")

    # Evaluation period (monthly, quarterly, annual)
    period_start = models.DateField()
    period_end = models.DateField()

    status = models.CharField(max_length=10, choices=STATUS, default=EvaluationStatus.PENDING)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = [("manager", "senior_manager", "period_start", "period_end", "form")]
        indexes = [
            models.Index(fields=["period_start", "period_end", "manager_id"]),
            models.Index(fields=["senior_manager_id", "status"]),
            # Performance indexes for common filtering patterns
            models.Index(fields=["status"]),  # For status filtering
            models.Index(fields=["submitted_at"]),  # For recent activity queries
            models.Index(fields=["department_id", "status"]),  # For department + status filtering
            models.Index(fields=["manager_id", "status"]),  # For manager + status filtering
            models.Index(fields=["period_end", "status"]),  # For overdue calculations
            models.Index(fields=["submitted_at", "status"]),  # For recent completed evaluations
        ]

    def __str__(self) -> str:
        return f"{self.manager} • {self.period_start}–{self.period_end} ({self.form})"


class ManagerAnswer(models.Model):
    """Answers for manager evaluations - reuses the same Question model."""
    instance = models.ForeignKey(DynamicManagerEvaluation, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)

    int_value   = models.IntegerField(null=True, blank=True)   # rating/number/bool(0/1)
    text_value  = models.TextField(null=True, blank=True)      # short/long
    choice_value = models.CharField(max_length=100, null=True, blank=True)  # select

    class Meta:
        unique_together = [("instance", "question")]


class ReportHistory(models.Model):
    """Track generated reports for senior management."""
    REPORT_TYPES = (
        ('employee', 'Employee Evaluation Report'),
        ('manager', 'Manager Evaluation Report'),
        ('trends', 'Performance Trends Report'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    date_from = models.DateField()
    date_to = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name_plural = 'Report Histories'
    
    def __str__(self):
        dept_name = self.department.title if self.department else "All Departments"
        return f"{self.get_report_type_display()} - {dept_name} ({self.generated_at.strftime('%Y-%m-%d %H:%M')})"
