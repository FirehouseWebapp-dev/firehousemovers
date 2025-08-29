from django import forms
from .models import Goal


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'due_date', 'goal_type', 'notes', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500', 'placeholder': 'Enter goal title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Detailed description of the goal'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none', 'placeholder': 'Any notes or updates on the goal'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-red-600 rounded focus:ring-red-500'}),
            'goal_type': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow empty goal_type in formsets so blank extra forms remain empty
        self.fields['goal_type'].required = False
        # Prepend a blank choice for goal_type so new extra forms are considered empty
        goal_type_field = self.fields['goal_type']
        if goal_type_field.choices and (goal_type_field.choices[0][0] != ''):
            goal_type_field.choices = [('', 'Select goal type')] + list(goal_type_field.choices)
        goal_type_field.initial = None
        # Add 'form-control' class to all fields for styling
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or isinstance(field.widget, forms.Textarea) or isinstance(field.widget, forms.DateInput) or isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] += ' form-control'
