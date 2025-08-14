from django import forms
from .models import Evaluation, ManagerEvaluation, ReviewCycle

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


class ManagerEvaluationForm(forms.ModelForm):
    # Hidden int field we control via the star widget in the template
    overall_rating = forms.IntegerField(
        required=False, min_value=1, max_value=5, widget=forms.HiddenInput()
    )

    class Meta:
        model = ManagerEvaluation
        fields = [
            # conditional section fields (we decide in __init__)
            "regular_evaluations",      # monthly only
            "performance_summary",      # quarterly only
            "annual_review",            # annual only
            # always present:
            "goals_achieved",
            "objectives_set",
            "strengths",
            "improvement_areas",
            "overall_rating",
            "supervisors_comments",     # keep as a free comment field for all cycles
        ]
        widgets = {
            "regular_evaluations":  forms.Textarea(attrs={"rows": 4, "class": "input-field"}),
            "performance_summary":  forms.Textarea(attrs={"rows": 4, "class": "input-field"}),
            "annual_review":        forms.Textarea(attrs={"rows": 4, "class": "input-field"}),
            "goals_achieved":       forms.Textarea(attrs={"rows": 3, "class": "input-field"}),
            "objectives_set":       forms.Textarea(attrs={"rows": 3, "class": "input-field"}),
            "strengths":            forms.Textarea(attrs={"rows": 3, "class": "input-field"}),
            "improvement_areas":    forms.Textarea(attrs={"rows": 3, "class": "input-field"}),
            "supervisors_comments": forms.Textarea(attrs={"rows": 3, "class": "input-field"}),
        }

    def __init__(self, *args, cycle: ReviewCycle = None, **kwargs):
        """
        Optionally accepts `cycle` kwarg for controlling which fields
        are visible/hidden. Falls back to instance.cycle if not provided.
        """
        super().__init__(*args, **kwargs)

        # If cycle not explicitly provided, use instance's cycle
        if cycle is None and hasattr(self.instance, "cycle"):
            cycle = self.instance.cycle

        # Default: all cycle-specific fields optional
        for fld in ["regular_evaluations", "performance_summary", "annual_review"]:
            self.fields[fld].required = False

        # Apply cycle-specific visibility
        if cycle:
            t = cycle.cycle_type
            if t == ReviewCycle.CycleType.MONTHLY:
                self.fields["performance_summary"].widget = forms.HiddenInput()
                self.fields["annual_review"].widget = forms.HiddenInput()
            elif t == ReviewCycle.CycleType.QUARTERLY:
                self.fields["regular_evaluations"].widget = forms.HiddenInput()
                self.fields["annual_review"].widget = forms.HiddenInput()
            elif t == ReviewCycle.CycleType.ANNUAL:
                self.fields["regular_evaluations"].widget = forms.HiddenInput()
                self.fields["performance_summary"].widget = forms.HiddenInput()

    def clean_overall_rating(self):
        """
        Ensure overall_rating is None instead of 0/empty for easier DB handling.
        """
        v = self.cleaned_data.get("overall_rating")
        return v or None
