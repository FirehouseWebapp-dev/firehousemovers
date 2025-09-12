from django import forms
from .models_dynamic import EvalForm, Question, QuestionChoice
from django.db.models import Max

class EvalFormForm(forms.ModelForm):
    EVALUATION_TYPE_CHOICES = [
        ('', '----'),
        ('Weekly Evaluation', 'Weekly Evaluation'),
        ('Monthly Evaluation', 'Monthly Evaluation'),
        ('Quarterly Evaluation', 'Quarterly Evaluation'),
        ('Annual Evaluation', 'Annual Evaluation'),
    ]
    
    name = forms.ChoiceField(
        choices=EVALUATION_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "input-field"}),
        label="Name"
    )
    
    class Meta:
        model = EvalForm
        fields = ["department", "name", "description"]
        widgets = {
            "department": forms.Select(attrs={"class": "input-field"}),
            "description": forms.TextInput(attrs={"class": "input-field"}),
        }
    
    

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "help_text", "qtype", "required", "min_value", "max_value", "order"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "input-field"}),
            "help_text": forms.TextInput(attrs={"class": "input-field"}),
            "qtype": forms.Select(attrs={"class": "input-field"}),
            "required": forms.CheckboxInput(attrs={"class": "h-4 w-4"}),
            "min_value": forms.NumberInput(attrs={"class": "input-field"}),
            "max_value": forms.NumberInput(attrs={"class": "input-field"}),
            "order": forms.NumberInput(attrs={"class": "input-field", "min": "0"}),
        }
    
    def __init__(self, *args, **kwargs):
        evaluation = kwargs.pop("evaluation", None)  # take evaluation from view
        super().__init__(*args, **kwargs)

        if not self.instance.pk and evaluation:
            # get max order for that evaluation only
            max_order = Question.objects.filter(form=evaluation).aggregate(Max("order"))["order__max"]
            next_order = 0 if max_order is None else max_order + 1
            self.fields["order"].initial = next_order
            self.fields["order"].widget.attrs["placeholder"] = str(next_order)

    def clean_min_value(self):
        """Validate min_value field individually."""
        min_value = self.cleaned_data.get('min_value')
        qtype = self.cleaned_data.get('qtype')
        
        # Validate that min_value cannot be negative for any question type that uses it
        numeric_qtypes = ['stars', 'emoji', 'rating', 'number']
        if qtype in numeric_qtypes and min_value is not None and min_value < 0:
            raise forms.ValidationError(f'Minimum value cannot be negative for {qtype} questions.')
        
        return min_value

class QuestionChoiceForm(forms.ModelForm):
    class Meta:
        model = QuestionChoice
        fields = ["value", "label"]
        widgets = {
            "value": forms.TextInput(attrs={"class": "input-field"}),
            "label": forms.TextInput(attrs={"class": "input-field"}),
        }
