from django import forms
from .models import EvalForm, Question, QuestionChoice
from django.db.models import Max
from django.utils.html import strip_tags
import re
import logging
from .constants import NUMERIC_QUESTION_TYPES

logger = logging.getLogger(__name__)

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
    
    def clean_description(self):
        """Sanitize description field."""
        description = self.cleaned_data.get('description', '')
        if description:
            # Strip HTML tags and limit length
            description = strip_tags(description).strip()
            if len(description) > 500:
                raise forms.ValidationError("Description cannot exceed 500 characters.")
        return description
    

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

    def clean_text(self):
        """Sanitize question text field."""
        text = self.cleaned_data.get('text', '')
        if text:
            # Strip HTML tags and limit length
            text = strip_tags(text).strip()
            if len(text) > 1000:
                raise forms.ValidationError("Question text cannot exceed 1000 characters.")
            if not text:
                raise forms.ValidationError("Question text cannot be empty.")
        return text
    
    def clean_help_text(self):
        """Sanitize help text field."""
        help_text = self.cleaned_data.get('help_text', '')
        if help_text:
            # Strip HTML tags and limit length
            help_text = strip_tags(help_text).strip()
            if len(help_text) > 500:
                raise forms.ValidationError("Help text cannot exceed 500 characters.")
        return help_text
    
    def clean_min_value(self):
        """Validate min_value field individually."""
        min_value = self.cleaned_data.get('min_value')
        qtype = self.cleaned_data.get('qtype')
        
        # Validate that min_value cannot be negative for any question type that uses it
        if qtype in NUMERIC_QUESTION_TYPES and min_value is not None and min_value < 0:
            raise forms.ValidationError(f'Minimum value cannot be negative for {qtype} questions.')
        
        return min_value
    
    def clean_max_value(self):
        """Validate max_value field individually."""
        max_value = self.cleaned_data.get('max_value')
        min_value = self.cleaned_data.get('min_value')
        qtype = self.cleaned_data.get('qtype')
        
        # Validate that max_value is greater than min_value for numeric question types
        if qtype in NUMERIC_QUESTION_TYPES and max_value is not None and min_value is not None:
            if max_value <= min_value:
                raise forms.ValidationError(f'Maximum value must be greater than minimum value for {qtype} questions.')
        
        return max_value

class QuestionChoiceForm(forms.ModelForm):
    class Meta:
        model = QuestionChoice
        fields = ["value", "label"]
        widgets = {
            "value": forms.TextInput(attrs={"class": "input-field"}),
            "label": forms.TextInput(attrs={"class": "input-field"}),
        }
    
    def clean_value(self):
        """Sanitize and validate choice value field."""
        value = self.cleaned_data.get('value', '')
        if value:
            # Strip HTML tags and limit length
            value = strip_tags(value).strip()
            if len(value) > 100:
                raise forms.ValidationError("Choice value cannot exceed 100 characters.")
            if not value:
                raise forms.ValidationError("Choice value cannot be empty.")
        return value
    
    def clean_label(self):
        """Sanitize and validate choice label field."""
        label = self.cleaned_data.get('label', '')
        if label:
            # Strip HTML tags and limit length
            label = strip_tags(label).strip()
            if len(label) > 200:
                raise forms.ValidationError("Choice label cannot exceed 200 characters.")
            if not label:
                raise forms.ValidationError("Choice label cannot be empty.")
        return label
    
    def clean(self):
        """Cross-field validation for choice form."""
        cleaned_data = super().clean()
        value = cleaned_data.get('value')
        label = cleaned_data.get('label')
        
        # Ensure both value and label are provided
        if not value and not label:
            raise forms.ValidationError("Both value and label are required.")
        
        return cleaned_data