"""
Dashboard views for evaluation analytics.
Separate views file to keep dashboard functionality organized.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

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
    try:
        # Get department by slug
        try:
            department = Department.objects.get(slug=department_slug)
        except Department.DoesNotExist:
            return render(request, 'evaluation/404.html', {
                'message': f'Department "{department_slug}" not found. Please check the URL or contact your administrator.'
            })
    
        # Get employee if specified
        employee = None
        if employee_id:
            try:
                employee = UserProfile.objects.get(id=employee_id, department=department)
            except UserProfile.DoesNotExist:
                return render(request, 'evaluation/404.html', {'message': 'Employee not found'})
            except Exception as e:
                return render(request, 'evaluation/404.html', {'message': 'Error finding employee'})
        
        # Get range filter
        try:
            range_type = request.GET.get('range', 'weekly')
            start_date, end_date, granularity = get_date_range(range_type)
        except Exception as e:
            range_type = 'weekly'
            start_date, end_date, granularity = get_date_range('weekly')
        
        # Get pagination parameters
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        per_page = 20  # 20 evaluations per page
        offset = (page - 1) * per_page
    
        # Get total count for pagination
        try:
            total_evaluations_count = DynamicEvaluation.objects.filter(
                department=department,
                week_start__lte=end_date,
                week_end__gte=start_date,
                status='completed'
            ).count()
        except Exception as e:
            total_evaluations_count = 0
        
        # OPTIMIZED: Use select_related and prefetch_related to avoid N+1 queries
        try:
            evaluations = DynamicEvaluation.objects.filter(
                department=department,
                week_start__lte=end_date,      # Evaluation starts before or on end_date
                week_end__gte=start_date,     # Evaluation ends after or on start_date
                status='completed'
            ).select_related(
                'form', 
                'employee__user', 
                'manager__user', 
                'department'
            ).prefetch_related(
                'answers__question',  # Prefetch all answers and their questions
                'form__questions'     # Prefetch form questions
            ).order_by('-week_start')[offset:offset + per_page]  # Add pagination
        except Exception as e:
            return render(request, 'evaluation/404.html', {
                'message': f'Error loading evaluation data for {department.title}'
            })
        
        if not evaluations.exists():
            return render(request, 'evaluation/404.html', {
                'message': f'No completed evaluations found for {department.title} in the selected date range'
            })
        
        # Get all forms used in the evaluations to handle form evolution
        try:
            forms_used = evaluations.values_list('form', flat=True).distinct()
        except Exception as e:
            forms_used = []
        
        # Get questions from all forms, prioritizing the most recent form
        # This ensures we capture data even when forms change over time
        try:
            all_questions = Question.objects.filter(
                form__in=forms_used,
                include_in_trends=True
            ).order_by('order')
        except Exception as e:
            all_questions = Question.objects.none()
        
        # Group questions by order to handle form evolution
        # Questions with the same order across forms are considered equivalent
        questions_by_order = {}
        try:
            for question in all_questions:
                if question.order not in questions_by_order:
                    questions_by_order[question.order] = []
                questions_by_order[question.order].append(question)
        except Exception as e:
            pass
        
        # Use the most recent form's questions as the primary structure
        # but include data from all forms for comprehensive analytics
        # Get the most recent form from the already-loaded evaluations to avoid N+1
        try:
            most_recent_evaluation = evaluations.order_by('-week_start').first()
            if not most_recent_evaluation:
                return render(request, 'evaluation/404.html', {'message': 'No evaluations found'})
            
            eval_form = most_recent_evaluation.form
            questions = Question.objects.filter(
                form=eval_form,
                include_in_trends=True
            ).select_related('form').order_by('order')
        except Exception as e:
            return render(request, 'evaluation/404.html', {
                'message': 'Error processing evaluation data'
            })
    
        # Note: We now include ALL evaluations (not just same form) for comprehensive data
        # Filter by employee if specified
        if employee:
            try:
                evaluations = evaluations.filter(employee=employee)
            except Exception as e:
                pass
        
        # Aggregate data for all questions at once to avoid N+1 queries
        chart_data = {}
        try:
            question_labels = get_question_labels(department.slug or department.title.lower())
        except Exception as e:
            question_labels = {}
        
        # Get all aggregated data in one call instead of looping through questions
        try:
            aggregated_data = aggregate_evaluation_data(
                evaluations, 
                questions, 
                granularity
            )
        except Exception as e:
            aggregated_data = {}
        
        # Process each question's data
        try:
            for question in questions:
                question_key = f"Q{question.order}"
                
                # Use qtype-based chart type selection
                chart_type = get_chart_type_for_qtype(question.qtype)
                
                chart_data[question_key] = {
                    'type': chart_type,
                    'data': aggregated_data.get(question_key, []),
                    'label': question_labels.get(question_key, question.text)
                }
        except Exception as e:
            chart_data = {}
    
        # Calculate summary statistics efficiently with a single query
        try:
            from django.db.models import Count, Q
            evaluation_stats = evaluations.aggregate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed'))
            )
            total_evaluations = evaluation_stats['total']
            completed_evaluations = evaluation_stats['completed']
            completion_rate = round((completed_evaluations / total_evaluations) * 100, 1) if total_evaluations > 0 else 0
        except Exception as e:
            total_evaluations = 0
            completed_evaluations = 0
            completion_rate = 0
    
        # Get department employees for dropdown
        try:
            department_employees = UserProfile.objects.filter(
                department=department,
                is_employee=True
            ).select_related('user', 'department').order_by('user__first_name', 'user__last_name')
        except Exception as e:
            department_employees = UserProfile.objects.none()
        
        # Calculate pagination info
        try:
            total_pages = (total_evaluations_count + per_page - 1) // per_page
            has_next = page < total_pages
            has_previous = page > 1
        except Exception as e:
            total_pages = 1
            has_next = False
            has_previous = False
        
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
            'chart_types': CHART_TYPES,
            # Pagination info
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_count': total_evaluations_count,
                'per_page': per_page,
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page': page + 1 if has_next else None,
                'previous_page': page - 1 if has_previous else None,
            }
        }
        
        return render(request, 'evaluation/analytics_dashboard.html', context)
    
    except Exception as e:
        return render(request, 'evaluation/404.html', {
            'message': 'An unexpected error occurred. Please try again or contact support.'
        })

@login_required  
def analytics_dashboard_api(request, department_slug, employee_id=None):
    """
    API endpoint for dashboard data (JSON response).
    Useful for AJAX updates without page reload.
    """
    
    # Get department by slug
    try:
        department = Department.objects.get(slug=department_slug)
    except Department.DoesNotExist:
        return JsonResponse({
            'error': f'Department "{department_slug}" not found.'
        }, status=404)
    
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
    
    # Get pagination parameters for API
    page = int(request.GET.get('page', 1))
    per_page = 20  # 20 evaluations per page
    offset = (page - 1) * per_page
    
    # Get completed evaluations that overlap with the date range
    # Include evaluations that start before end_date and end after start_date
    evaluations = DynamicEvaluation.objects.filter(
        department=department,
        week_start__lte=end_date,      # Evaluation starts before or on end_date
        week_end__gte=start_date,     # Evaluation ends after or on start_date
        status='completed'
    ).select_related('form', 'employee__user', 'manager__user', 'department')[offset:offset + per_page]
    
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
    
    # Get total count for pagination
    total_count = DynamicEvaluation.objects.filter(
        department=department,
        week_start__lte=end_date,
        week_end__gte=start_date,
        status='completed'
    ).count()
    
    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page
    
    return JsonResponse({
        'chart_data': chart_data,
        'question_labels': question_labels,
        'range_type': range_type,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'granularity': granularity,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'total_count': total_count,
            'per_page': per_page,
            'has_next': page < total_pages,
            'has_previous': page > 1,
        }
    })

