from django.contrib import admin
from .models import Evaluation

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

