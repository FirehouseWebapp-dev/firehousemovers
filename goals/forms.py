from django import forms
from .models import Goal


class GoalForm(forms.ModelForm):
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


class GoalFormSetForm(forms.ModelForm):
    """Form for formset that excludes the is_completed checkbox"""
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
