"""
Dashboard views for evaluation analytics.
Separate views file to keep dashboard functionality organized.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from authentication.models import Department, UserProfile
from .models import EvalForm, DynamicEvaluation, Question
from .dashboard_utils import (
    get_question_labels, 
    get_date_range, 
    aggregate_evaluation_data,
    get_emoji_distribution,
    CHART_TYPES
)

@login_required
def analytics_dashboard(request, department_slug, employee_id=None):
    """
    Main analytics dashboard for department/employee evaluations.
    
    URL: /dashboard/<department_slug>/<employee_id>/
    Query params: ?range=weekly|monthly|yearly
    """
    
    # Get department
    try:
        department = Department.objects.get(slug=department_slug)
    except Department.DoesNotExist:
        department = Department.objects.filter(title__icontains=department_slug).first()
        if not department:
            return render(request, 'evaluation/404.html', {'message': 'Department not found'})
    
    # Get employee if specified
    employee = None
    if employee_id:
        try:
            employee = UserProfile.objects.get(id=employee_id, department=department)
        except UserProfile.DoesNotExist:
            return render(request, 'evaluation/404.html', {'message': 'Employee not found'})
    
    # Get range filter
    range_type = request.GET.get('range', 'weekly')
    start_date, end_date, granularity = get_date_range(range_type)
    
    # Get active evaluation form for this department
    try:
        eval_form = EvalForm.objects.get(
            department=department, 
            is_active=True
        )
    except EvalForm.DoesNotExist:
        return render(request, 'evaluation/404.html', {
            'message': f'No active evaluation form found for {department.title}'
        })
    
    # Get questions (Q1-Q5) ordered by position
    questions = Question.objects.filter(
        form=eval_form,
        order__in=[1, 2, 3, 4, 5]
    ).order_by('order')
    
    # Get evaluations in date range
    evaluations = DynamicEvaluation.objects.filter(
        form=eval_form,
        department=department,
        week_start__gte=start_date,
        week_end__lte=end_date,
        status='completed'
    )
    
    # Filter by employee if specified
    if employee:
        evaluations = evaluations.filter(employee=employee)
    
    # Aggregate data for each question
    chart_data = {}
    question_labels = get_question_labels(department.slug or department.title.lower())
    
    for question in questions:
        question_key = f"Q{question.order}"
        
        # Get aggregated data for this question
        question_evaluations = evaluations.filter(
            answers__question=question
        ).distinct()
        
        if question.qtype == "emoji":
            # Special handling for emoji questions (Q3)
            emoji_data = get_emoji_distribution(question_evaluations, question)
            chart_data[question_key] = {
                'type': 'pie',
                'data': emoji_data,
                'label': question_labels.get(question_key, question.text)
            }
        else:
            # Numeric aggregation
            aggregated_data = aggregate_evaluation_data(
                question_evaluations, 
                [question], 
                granularity
            )
            
            chart_data[question_key] = {
                'type': CHART_TYPES.get(question_key, 'line'),
                'data': aggregated_data.get(question_key, []),
                'label': question_labels.get(question_key, question.text)
            }
    
    # Calculate summary statistics
    total_evaluations = evaluations.count()
    completion_rate = 0
    if total_evaluations > 0:
        completed_evaluations = evaluations.filter(status='completed').count()
        completion_rate = round((completed_evaluations / total_evaluations) * 100, 1)
    
    # Get department employees for dropdown
    department_employees = UserProfile.objects.filter(
        department=department,
        is_employee=True
    ).order_by('user__first_name', 'user__last_name')
    
    context = {
        'department': department,
        'employee': employee,
        'eval_form': eval_form,
        'chart_data': chart_data,
        'question_labels': question_labels,
        'range_type': range_type,
        'start_date': start_date,
        'end_date': end_date,
        'granularity': granularity,
        'total_evaluations': total_evaluations,
        'completion_rate': completion_rate,
        'department_employees': department_employees,
        'chart_types': CHART_TYPES
    }
    
    return render(request, 'evaluation/analytics_dashboard.html', context)

@login_required  
def analytics_dashboard_api(request, department_slug, employee_id=None):
    """
    API endpoint for dashboard data (JSON response).
    Useful for AJAX updates without page reload.
    """
    
    # Get department
    try:
        department = Department.objects.get(slug=department_slug)
    except Department.DoesNotExist:
        department = Department.objects.filter(title__icontains=department_slug).first()
        if not department:
            return JsonResponse({'error': 'Department not found'}, status=404)
    
    # Get employee if specified
    employee = None
    if employee_id:
        try:
            employee = UserProfile.objects.get(id=employee_id, department=department)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)
    
    # Get range filter
    range_type = request.GET.get('range', 'weekly')
    start_date, end_date, granularity = get_date_range(range_type)
    
    # Get active evaluation form
    try:
        eval_form = EvalForm.objects.get(department=department, is_active=True)
    except EvalForm.DoesNotExist:
        return JsonResponse({'error': 'No active evaluation form found'}, status=404)
    
    # Get questions and evaluations
    questions = Question.objects.filter(
        form=eval_form,
        order__in=[1, 2, 3, 4, 5]
    ).order_by('order')
    
    evaluations = DynamicEvaluation.objects.filter(
        form=eval_form,
        department=department,
        week_start__gte=start_date,
        week_end__lte=end_date,
        status='completed'
    )
    
    if employee:
        evaluations = evaluations.filter(employee=employee)
    
    # Aggregate data
    chart_data = {}
    question_labels = get_question_labels(department.slug or department.title.lower())
    
    for question in questions:
        question_key = f"Q{question.order}"
        question_evaluations = evaluations.filter(
            answers__question=question
        ).distinct()
        
        if question.qtype == "emoji":
            emoji_data = get_emoji_distribution(question_evaluations, question)
            chart_data[question_key] = {
                'type': 'pie',
                'data': emoji_data,
                'label': question_labels.get(question_key, question.text)
            }
        else:
            aggregated_data = aggregate_evaluation_data(
                question_evaluations, 
                [question], 
                granularity
            )
            chart_data[question_key] = {
                'type': CHART_TYPES.get(question_key, 'line'),
                'data': aggregated_data.get(question_key, []),
                'label': question_labels.get(question_key, question.text)
            }
    
    return JsonResponse({
        'chart_data': chart_data,
        'question_labels': question_labels,
        'range_type': range_type,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'granularity': granularity
    })
