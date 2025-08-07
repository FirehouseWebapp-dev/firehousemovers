from django import forms
from .models import Evaluation

EMOJI_CHOICES = [
    (1, "😡"),  # Very Dissatisfied
    (2, "😕"),  # Dissatisfied
    (3, "😐"),  # Neutral
    (4, "🙂"),  # Satisfied
    (5, "😍"),  # Very Satisfied
]

STAR_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
]

class EvaluationForm(forms.ModelForm):
    avg_customer_satisfaction_score = forms.ChoiceField(
        choices=EMOJI_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'sr-only'}),
        required=True,
        label="Avg customer satisfaction score"
    )
    reliability_rating = forms.ChoiceField(
        choices=STAR_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Reliability"
    )

    class Meta:
        model = Evaluation
        fields = [
            'avg_customer_satisfaction_score',
            'five_star_reviews',
            'negative_reviews',
            'late_arrivals',
            'absences',
            'reliability_rating',
            'avg_move_completion_time',
            'moves_within_schedule',
            'avg_revenue_per_move',
            'damage_claims',
            'safety_incidents',
            'consecutive_damage_free_moves',
            'notes',
        ]
        widgets = {
            'avg_move_completion_time': forms.TextInput(attrs={
                'placeholder': 'e.g. 01:30:00 (HH:MM:SS)',
                'class': 'input-field',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.setdefault('class', 'input-field')
