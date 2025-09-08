from django import forms
from .models_dynamic import EvalForm, Question, QuestionChoice

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
            "order": forms.NumberInput(attrs={"class": "input-field"}),
        }

class QuestionChoiceForm(forms.ModelForm):
    class Meta:
        model = QuestionChoice
        fields = ["value", "label"]
        widgets = {
            "value": forms.TextInput(attrs={"class": "input-field"}),
            "label": forms.TextInput(attrs={"class": "input-field"}),
        }
