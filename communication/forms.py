from django import forms
from .models import CommunicationLog, LogResponse, LogType
from authentication.models import UserProfile
from datetime import date, timedelta


class CommunicationLogForm(forms.ModelForm):
    """Form for creating communication logs"""
    
    class Meta:
        model = CommunicationLog
        fields = ['employee', 'log_type', 'subject', 'content', 'visibility', 'week_start', 'week_end']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
            }),
            'log_type': forms.Select(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
                'placeholder': 'Enter subject...',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
                'rows': 6,
                'placeholder': 'Enter detailed notes...',
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
            }),
            'week_start': forms.DateInput(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
                'type': 'date',
            }),
            'week_end': forms.DateInput(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
                'type': 'date',
            }),
        }
        labels = {
            'employee': 'Employee',
            'log_type': 'Log type',
            'subject': 'Subject',
            'content': 'Notes',
            'visibility': 'Visibility',
            'week_start': 'Week start',
            'week_end': 'Week end',
        }

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        
        if manager:
            choices = []
            
            # For Senior Managers: Include managers they can create logs for
            if manager.is_senior_management or manager.is_admin:
                # Get all managers in the organization
                all_managers = UserProfile.objects.filter(
                    is_manager=True
                ).exclude(id=manager.id).order_by('user__first_name', 'user__last_name')
                
                if all_managers.exists():
                    manager_choices = [
                        (mgr.id, f"{mgr.user.get_full_name()} ({mgr.role})")
                        for mgr in all_managers
                    ]
                    choices.append(('Managers', manager_choices))
            
            # Get team members (direct reports) - includes both employees and managers
            team_members = manager.team_members.filter(is_employee=True)
            
            # Get department members (same department) - employees only
            department_members = UserProfile.objects.none()
            if manager.department:
                department_members = manager.department.members.filter(
                    is_employee=True
                ).exclude(id=manager.id)
            
            # Combine and remove duplicates
            available_employees = (team_members | department_members).distinct().order_by('user__first_name', 'user__last_name')
            
            # Team Members (employees)
            team_ids = set(team_members.values_list('id', flat=True))
            team_choices = [
                (emp.id, f"{emp.user.get_full_name()} ({emp.role})")
                for emp in available_employees if emp.id in team_ids
            ]
            if team_choices:
                choices.append(('Team Members', team_choices))
            
            # Department Members (not in team, employees only)
            dept_choices = [
                (emp.id, f"{emp.user.get_full_name()} ({emp.role})")
                for emp in available_employees if emp.id not in team_ids
            ]
            if dept_choices:
                choices.append(('Department Members', dept_choices))
            
            self.fields['employee'].choices = [('', '---------')] + choices
        
        # Set default dates to current week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday
        
        if not self.instance.pk:
            self.initial['week_start'] = week_start
            self.initial['week_end'] = week_end


class LogResponseForm(forms.ModelForm):
    """Form for employees to respond to logs"""
    
    class Meta:
        model = LogResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={
                'class': 'form-input w-full bg-[#2a2a2a] border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-red-500 focus:outline-none',
                'rows': 4,
                'placeholder': 'Enter your response...',
            }),
        }
        labels = {
            'response_text': 'Your response',
        }

