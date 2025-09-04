from django import forms
from django.utils import timezone
from .models import Goal
from .utils.validators import validate_future_date, validate_goal_title_length, validate_goal_description_length


class GoalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        today = timezone.now().date().isoformat()
        self.fields['due_date'].widget.attrs['min'] = today
    
    class Meta:
        model = Goal
        fields = ['title', 'description', 'due_date', 'goal_type', 'notes', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500', 'placeholder': 'Enter goal title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Detailed description of the goal'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Any notes or updates on the goal'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-red-600 rounded focus:ring-red-500'}),
            'goal_type': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            validate_goal_title_length(title)
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            validate_goal_description_length(description)
        return description
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            validate_future_date(due_date)
        return due_date


class GoalEditForm(forms.ModelForm):
    """Form for editing goals - excludes is_completed to prevent manipulation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        today = timezone.now().date().isoformat()
        self.fields['due_date'].widget.attrs['min'] = today
    
    class Meta:
        model = Goal
        fields = ['title', 'description', 'due_date', 'goal_type', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500', 'placeholder': 'Enter goal title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Detailed description of the goal'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Any notes or updates on the goal'}),
            'goal_type': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            validate_goal_title_length(title)
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            validate_goal_description_length(description)
        return description
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            validate_future_date(due_date)
        return due_date


class GoalFormSetForm(forms.ModelForm):
    """Form for formset that excludes the is_completed checkbox"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        today = timezone.now().date().isoformat()
        self.fields['due_date'].widget.attrs['min'] = today
    
    class Meta:
        model = Goal
        fields = ['title', 'description', 'due_date', 'goal_type', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500', 'placeholder': 'Enter goal title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Detailed description of the goal'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Any notes or updates on the goal'}),
            'goal_type': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-[#3a3a3a] border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            validate_goal_title_length(title)
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            validate_goal_description_length(description)
        return description
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            validate_future_date(due_date)
        return due_date
