"""
Dashboard views for evaluation analytics.
Separate views file to keep dashboard functionality organized.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
    get_chart_type_for_qtype,
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
        # Fallback: try exact case-insensitive match first, then partial match
        exact_match = Department.objects.filter(title__iexact=department_slug).first()
        if exact_match:
            department = exact_match
        else:
            # Try partial match as last resort
            matching_departments = Department.objects.filter(title__icontains=department_slug)
            if matching_departments.count() == 1:
                department = matching_departments.first()
            elif matching_departments.count() > 1:
                # Multiple matches - return error to avoid ambiguity
                return render(request, 'evaluation/404.html', {
                    'message': f'Multiple departments found matching "{department_slug}". Please use exact department name.'
                })
            else:
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
    
    # Get completed evaluations that overlap with the date range
    # Include evaluations that start before end_date and end after start_date
    evaluations = DynamicEvaluation.objects.filter(
        department=department,
        week_start__lte=end_date,      # Evaluation starts before or on end_date
        week_end__gte=start_date,     # Evaluation ends after or on start_date
        status='completed'
    )
    
    if not evaluations.exists():
        return render(request, 'evaluation/404.html', {
            'message': f'No completed evaluations found for {department.title} in the selected date range'
        })
    
    # Get all forms used in the evaluations to handle form evolution
    forms_used = evaluations.values_list('form', flat=True).distinct()
    
    # Get questions from all forms, prioritizing the most recent form
    # This ensures we capture data even when forms change over time
    all_questions = Question.objects.filter(
        form__in=forms_used,
        include_in_trends=True
    ).order_by('order')
    
    # Group questions by order to handle form evolution
    # Questions with the same order across forms are considered equivalent
    questions_by_order = {}
    for question in all_questions:
        if question.order not in questions_by_order:
            questions_by_order[question.order] = []
        questions_by_order[question.order].append(question)
    
    # Use the most recent form's questions as the primary structure
    # but include data from all forms for comprehensive analytics
    eval_form = evaluations.order_by('-week_start').first().form
    questions = Question.objects.filter(
        form=eval_form,
        include_in_trends=True
    ).order_by('order')
    
    # Note: We now include ALL evaluations (not just same form) for comprehensive data
    # Filter by employee if specified
    if employee:
        evaluations = evaluations.filter(employee=employee)
    
    # Aggregate data for all questions at once to avoid N+1 queries
    chart_data = {}
    question_labels = get_question_labels(department.slug or department.title.lower())
    
    # Get all aggregated data in one call instead of looping through questions
    aggregated_data = aggregate_evaluation_data(
        evaluations, 
        questions, 
        granularity
    )
    
    # Process each question's data
    for question in questions:
        question_key = f"Q{question.order}"
        
        # Use qtype-based chart type selection
        chart_type = get_chart_type_for_qtype(question.qtype)
        
        chart_data[question_key] = {
            'type': chart_type,
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
        # Fallback: try exact case-insensitive match first, then partial match
        exact_match = Department.objects.filter(title__iexact=department_slug).first()
        if exact_match:
            department = exact_match
        else:
            # Try partial match as last resort
            matching_departments = Department.objects.filter(title__icontains=department_slug)
            if matching_departments.count() == 1:
                department = matching_departments.first()
            elif matching_departments.count() > 1:
                # Multiple matches - return error to avoid ambiguity
                return JsonResponse({
                    'error': f'Multiple departments found matching "{department_slug}". Please use exact department name.'
                }, status=400)
            else:
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
    
    # Get completed evaluations that overlap with the date range
    # Include evaluations that start before end_date and end after start_date
    evaluations = DynamicEvaluation.objects.filter(
        department=department,
        week_start__lte=end_date,      # Evaluation starts before or on end_date
        week_end__gte=start_date,     # Evaluation ends after or on start_date
        status='completed'
    )
    
    if not evaluations.exists():
        return JsonResponse({'error': 'No completed evaluations found in the selected date range'}, status=404)
    
    # Get all forms used in the evaluations to handle form evolution
    forms_used = evaluations.values_list('form', flat=True).distinct()
    
    # Get questions from all forms, prioritizing the most recent form
    # This ensures we capture data even when forms change over time
    all_questions = Question.objects.filter(
        form__in=forms_used,
        include_in_trends=True
    ).order_by('order')
    
    # Group questions by order to handle form evolution
    # Questions with the same order across forms are considered equivalent
    questions_by_order = {}
    for question in all_questions:
        if question.order not in questions_by_order:
            questions_by_order[question.order] = []
        questions_by_order[question.order].append(question)
    
    # Use the most recent form's questions as the primary structure
    # but include data from all forms for comprehensive analytics
    eval_form = evaluations.order_by('-week_start').first().form
    questions = Question.objects.filter(
        form=eval_form,
        include_in_trends=True
    ).order_by('order')
    
    # Note: We now include ALL evaluations (not just same form) for comprehensive data
    if employee:
        evaluations = evaluations.filter(employee=employee)
    
    # Aggregate data for all questions at once to avoid N+1 queries
    chart_data = {}
    question_labels = get_question_labels(department.slug or department.title.lower())
    
    # Get all aggregated data in one call instead of looping through questions
    aggregated_data = aggregate_evaluation_data(
        evaluations, 
        questions, 
        granularity
    )
    
    # Process each question's data
    for question in questions:
        question_key = f"Q{question.order}"
        
        # Use qtype-based chart type selection
        chart_type = get_chart_type_for_qtype(question.qtype)
        
        chart_data[question_key] = {
            'type': chart_type,
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
