"""
Manager Performance Views
Separate views file for manager performance dashboard functionality.
"""

import logging
from django.db.models import Avg, Count, Case, When, F, Value
from collections import defaultdict

from .models import DynamicManagerEvaluation, ManagerAnswer, Question
from .dashboard_utils import (
    get_chart_type_for_qtype,
    CHART_TYPES
)
from .utils import get_role_checker

logger = logging.getLogger(__name__)


def aggregate_manager_evaluation_data(evaluations, questions, granularity="daily"):
    """
    Aggregate manager evaluation data for charts.
    Optimized to prevent N+1 queries and handle large datasets efficiently.
    
    Args:
        evaluations: QuerySet of DynamicManagerEvaluation objects
        questions: QuerySet of Question objects
        granularity: Aggregation granularity (currently unused, defaults to monthly)
    
    Returns:
        dict: Aggregated data by question order
    """
    if not evaluations or not questions:
        return {}
    
    try:
        # Optimize query with select_related to prevent N+1 queries
        answers = ManagerAnswer.objects.filter(
            instance__in=evaluations,
            question__in=questions
        ).select_related('question', 'instance').only(
            'question__order', 'question__qtype', 'int_value', 'text_value',
            'instance__period_start'
        )
        
        answer_count = answers.count()
        logger.info(f"Aggregating {answer_count} manager answers across {len(questions)} questions")
        
        # For large datasets, use SQL aggregation for better performance
        if answer_count > 1000:
            logger.info(f"Using SQL aggregation for {answer_count} answers (threshold: 1000)")
            return _aggregate_with_sql(evaluations, questions, granularity)
        
        # In-memory aggregation for smaller datasets
        data = defaultdict(lambda: defaultdict(list))
        emoji_map = {"😞": 1, "😕": 2, "😐": 3, "😊": 4, "😍": 5}
        
        for answer in answers:
            question = answer.question
            period = answer.instance.period_start.replace(day=1)
            
            # Extract value based on question type
            value = None
            if answer.int_value is not None:
                value = answer.int_value
            elif answer.text_value and question.qtype == "emoji":
                value = emoji_map.get(answer.text_value, 3)
            
            if value is not None:
                data[question.order][period].append(value)
        
        # Calculate aggregations
        result = {}
        for question_order, periods in data.items():
            question_data = [
                {
                    'period': period.strftime('%b %d, %Y'),
                    'value': round(sum(values) / len(values), 2),
                    'count': len(values)
                }
                for period, values in sorted(periods.items()) if values
            ]
            result[f"Q{question_order}"] = question_data
        
        logger.info(f"Aggregated data for {len(result)} questions")
        return result
    
    except Exception as e:
        logger.error(f"Error in aggregate_manager_evaluation_data: {str(e)}", exc_info=True)
        return {}


def _aggregate_with_sql(evaluations, questions, granularity="daily"):
    """
    SQL-based aggregation method for large datasets.
    Uses database aggregation functions for better performance.
    
    Args:
        evaluations: QuerySet of DynamicManagerEvaluation objects
        questions: QuerySet of Question objects
        granularity: Aggregation granularity (currently unused)
    
    Returns:
        dict: Aggregated data by question order
    """
    try:
        # Use SQL aggregation for optimal performance with large datasets
        aggregated_data = ManagerAnswer.objects.filter(
            instance__in=evaluations,
            question__in=questions
        ).values(
            'question__order',
            'instance__period_start'
        ).annotate(
            avg_value=Avg(
                Case(
                    When(int_value__isnull=False, then=F('int_value')),
                    When(text_value__in=["😞", "😕", "😐", "😊", "😍"], 
                         then=Case(
                             When(text_value="😞", then=Value(1)),
                             When(text_value="😕", then=Value(2)),
                             When(text_value="😐", then=Value(3)),
                             When(text_value="😊", then=Value(4)),
                             When(text_value="😍", then=Value(5)),
                             default=Value(3)
                         )),
                    default=Value(0)
                )
            ),
            count=Count('id')
        ).order_by('question__order', 'instance__period_start')
        
        # Group results by question
        result = defaultdict(list)
        for item in aggregated_data:
            question_order = item['question__order']
            period = item['instance__period_start'].replace(day=1)
            
            result[f"Q{question_order}"].append({
                'period': period.strftime('%b %d, %Y'),
                'value': round(item['avg_value'], 2) if item['avg_value'] is not None else 0,
                'count': item['count']
            })
        
        logger.info(f"SQL aggregation completed for {len(result)} questions")
        return dict(result)
        
    except Exception as e:
        logger.error(f"Error in SQL aggregation: {str(e)}", exc_info=True)
        return {}


def get_manager_emoji_distribution(evaluations, question):
    """
    Get emoji distribution for manager evaluation satisfaction questions.
    Uses database aggregation for optimal performance.
    
    Args:
        evaluations: QuerySet of DynamicManagerEvaluation objects
        question: Question object
    
    Returns:
        dict: Distribution of emoji responses
    """
    if not evaluations or not question:
        return {"😞": 0, "😕": 0, "😐": 0, "😊": 0, "😍": 0}
    
    try:
        distribution = {"😞": 0, "😕": 0, "😐": 0, "😊": 0, "😍": 0}
        int_to_emoji_map = {1: "😞", 2: "😕", 3: "😐", 4: "😊", 5: "😍"}
        
        # Use database aggregation for emoji counting
        text_emoji_counts = ManagerAnswer.objects.filter(
            instance__in=evaluations,
            question=question,
            text_value__in=list(distribution.keys())
        ).values('text_value').annotate(count=Count('id'))
        
        for item in text_emoji_counts:
            distribution[item['text_value']] += item['count']
        
        # Count and convert integer values to emojis
        int_emoji_counts = ManagerAnswer.objects.filter(
            instance__in=evaluations,
            question=question,
            int_value__in=[1, 2, 3, 4, 5]
        ).values('int_value').annotate(count=Count('id'))
        
        for item in int_emoji_counts:
            emoji = int_to_emoji_map.get(item['int_value'])
            if emoji:
                distribution[emoji] += item['count']
        
        total_count = sum(distribution.values())
        logger.info(f"Emoji distribution for question {question.id}: {total_count} responses")
        
        return distribution
        
    except Exception as e:
        logger.error(f"Error getting emoji distribution: {str(e)}", exc_info=True)
        return {"😞": 0, "😕": 0, "😐": 0, "😊": 0, "😍": 0}


def manager_personal_performance_data(request, period_type="monthly", start_date_obj=None, end_date_obj=None, target_user_profile=None):
    """
    Get manager's personal performance data (when they are being evaluated).
    Returns JSON data for charts based on the specified period type.
    
    Args:
        request: HTTP request object (or None if target_user_profile is provided)
        period_type: "monthly", "quarterly", or "annually"
        start_date_obj: Start date filter (datetime.date object)
        end_date_obj: End date filter (datetime.date object)
        target_user_profile: Optional UserProfile to get data for (for senior managers viewing other managers)
    
    Returns:
        dict: Performance data structured for chart rendering
    """
    # Determine target user profile
    if target_user_profile:
        user_profile = target_user_profile
    else:
        checker = get_role_checker(request.user)
        user_profile = checker.user_profile
    
    logger.info(f"Fetching performance data for manager {user_profile.id}, period: {period_type}")
    
    # Get manager's evaluations with optimized query
    base_evaluations = DynamicManagerEvaluation.objects.filter(
        manager=user_profile,
        status='completed'
    ).select_related('form', 'department').only(
        'id', 'period_start', 'period_end', 'form__id', 'form__name', 'department__id'
    )
    
    # Apply date filters using overlap logic
    if start_date_obj and end_date_obj:
        base_evaluations = base_evaluations.filter(
            period_start__lte=end_date_obj,
            period_end__gte=start_date_obj
        )
    elif start_date_obj:
        base_evaluations = base_evaluations.filter(period_end__gte=start_date_obj)
    elif end_date_obj:
        base_evaluations = base_evaluations.filter(period_start__lte=end_date_obj)
    
    # Filter by period type
    period_filters = {
        "monthly": "monthly",
        "quarterly": "quarterly",
        "annually": "annual"
    }
    if period_type in period_filters:
        manager_evaluations = base_evaluations.filter(form__name__icontains=period_filters[period_type])
    else:
        manager_evaluations = base_evaluations
    
    eval_count = manager_evaluations.count()
    logger.info(f"Found {eval_count} evaluations for manager {user_profile.id}")
    
    # Build performance data
    performance_data = {}
    
    if hasattr(user_profile, 'managed_department') and user_profile.managed_department and eval_count > 0:
        trend_evaluations = manager_evaluations.filter(
            department=user_profile.managed_department
        ).order_by('period_start')
        
        if trend_evaluations.exists():
            # Get date range from evaluations
            first_eval = trend_evaluations.first()
            last_eval = trend_evaluations.last()
            start_date = first_eval.period_start
            end_date = last_eval.period_end
            
            # Get questions from the most recent form
            most_recent_evaluation = trend_evaluations.order_by('-period_start').first()
            eval_form = most_recent_evaluation.form
            
            questions = Question.objects.filter(
                form=eval_form,
                include_in_trends=True
            ).only('id', 'order', 'text', 'qtype').order_by('order')
            
            question_count = questions.count()
            logger.info(f"Processing {question_count} questions for manager performance")
            
            # Aggregate data
            aggregated_data = aggregate_manager_evaluation_data(
                trend_evaluations, 
                questions, 
                'monthly'
            )
            
            # Build chart data
            chart_data = {}
            for question in questions:
                question_key = f"Q{question.order}"
                chart_type = get_chart_type_for_qtype(question.qtype)
                
                if question.qtype == "emoji" and chart_type == "pie":
                    emoji_data = get_manager_emoji_distribution(trend_evaluations, question)
                    chart_data[question_key] = {
                        'type': chart_type,
                        'data': emoji_data,
                        'label': question.text
                    }
                else:
                    chart_data[question_key] = {
                        'type': chart_type,
                        'data': aggregated_data.get(question_key, []),
                        'label': question.text
                    }
            
            performance_data = {
                'chart_data': chart_data,
                'range_type': 'monthly',
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'granularity': 'monthly',
                'chart_types': CHART_TYPES
            }
            
            logger.info(f"Returning performance data with {len(chart_data)} charts for manager {user_profile.id}")
    
    return performance_data
