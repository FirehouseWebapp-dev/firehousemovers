"""
Dashboard utilities for evaluation analytics.
Contains department-specific question labels and aggregation helpers.
"""

from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

# Department-specific question labels based on actual questions
QUESTION_LABELS = {
    "sales": {
        "Q0": "New Leads Generated",
        "Q1": "Lead Conversion Effectiveness", 
        "Q2": "Customer Interaction Satisfaction",
        "Q3": "Sales Target Achievement",
        "Q4": "Future Deal Closing Confidence"
    },
    "drivers": {
        "Q0": "Moves & Deliveries Completed",
        "Q1": "On-Time Delivery Percentage",
        "Q2": "Safety & Compliance Rating", 
        "Q3": "Customer Professionalism Satisfaction",
        "Q4": "Complex Move Handling Confidence"
    },
    "accounting": {
        "Q0": "Invoices Processed",
        "Q1": "Processing Accuracy Rate",
        "Q2": "Team Collaboration Satisfaction",
        "Q3": "Target Achievement", 
        "Q4": "Future Performance Confidence"
    },
    "it": {
        "Q0": "Support Tickets Resolved",
        "Q1": "Issue Resolution Rate",
        "Q2": "User Satisfaction Rating",
        "Q3": "Technical Performance Rating",
        "Q4": "Future Problem-Solving Confidence"
    },
    "warehouse": {
        "Q0": "Orders Processed",
        "Q1": "Processing Accuracy Rate",
        "Q2": "Team Collaboration Satisfaction",
        "Q3": "Operational Efficiency Rating",
        "Q4": "Future Performance Confidence"
    },
    "marketing": {
        "Q0": "Campaigns Launched",
        "Q1": "Audience Engagement Rate",
        "Q2": "Team Collaboration Satisfaction", 
        "Q3": "ROI Achievement",
        "Q4": "Future Campaign Success Confidence"
    }
}

# Chart types based on question types (qtypes)
def get_chart_type_for_qtype(qtype):
    """
    Determine chart type based on question type (qtype).
    
    Args:
        qtype: The question type from Question.QType choices
        
    Returns:
        str: Chart type ('pie', 'line', 'bar', 'doughnut', 'radar', 'gauge')
    """
    chart_type_mapping = {
        'emoji': 'pie',      # Emoji satisfaction - Pie chart
        'stars': 'line',     # 5-star rating - Line chart  
        'number': 'bar',     # Number input - Bar chart
        'rating': 'bar',     # Plain rating - Bar chart
        'bool': 'doughnut',  # Yes/No - Doughnut chart
        'select': 'bar',     # Single select - Bar chart
        'short': 'bar',      # Short text - Bar chart
        'long': 'bar',       # Long text - Bar chart
        'section': 'bar'     # Section header - Bar chart (fallback)
    }
    
    return chart_type_mapping.get(qtype, 'line')  # Default to line chart

# Legacy chart types for backward compatibility (based on question position)
CHART_TYPES = {
    "Q0": "line",      # Performance/Quantity - Line chart
    "Q1": "bar",       # Accuracy - Bar chart  
    "Q2": "pie",       # Satisfaction - Pie chart (emoji distribution)
    "Q3": "radar",     # Targets - Radar chart
    "Q4": "gauge"      # Confidence - Gauge chart
}

def get_question_labels(department_slug):
    """Get question labels for a specific department."""
    if department_slug is None:
        return QUESTION_LABELS["sales"]
    return QUESTION_LABELS.get(department_slug.lower(), QUESTION_LABELS["sales"])

def get_date_range(range_type="monthly"):
    """
    Get date range based on filter type. Defaults to monthly.
    
    Args:
        range_type: "monthly" or other (defaults to monthly behavior)
        
    Returns:
        tuple: (start_date, end_date, granularity)
        - start_date: Beginning of the date range
        - end_date: End of the date range (includes 7-day buffer for overlapping evaluations)
        - granularity: "weekly" for UI display granularity (always weekly regardless of range_type)
    """
    now = timezone.now().date()
    
    if range_type == "monthly":
        # Last 4 weeks (28 days) + buffer for next week
        start_date = now - timedelta(days=35)  # 5 weeks to ensure we get 4 full weeks
        end_date = now + timedelta(days=7)     # Include evaluations that end in the next week
        return start_date, end_date, "weekly"
    else:
        # Default to monthly behavior
        start_date = now - timedelta(days=28)  # 4 weeks exactly
        end_date = now + timedelta(days=7)     # Include evaluations that end in the next week
        return start_date, end_date, "weekly"

def aggregate_evaluation_data(evaluations, questions, granularity="daily"):
    """
    Aggregate evaluation data by question and time period.
    
    Args:
        evaluations: QuerySet of DynamicEvaluation instances
        questions: QuerySet of Question instances  
        granularity: "daily", "weekly", or "monthly"
    
    Returns:
        dict: Aggregated data for each question
    """
    from .models import Answer
    
    # Get all answers for these evaluations
    answers = Answer.objects.filter(
        instance__in=evaluations,
        question__in=questions
    ).select_related('question', 'instance')
    
    # Group by question and time period
    data = defaultdict(lambda: defaultdict(list))
    
    for answer in answers:
        question = answer.question
        evaluation = answer.instance
        
        # Determine time period based on granularity
        if granularity == "daily":
            period = evaluation.week_start
        elif granularity == "weekly":
            # Group by week
            period = evaluation.week_start
        elif granularity == "monthly":
            # Group by month
            period = evaluation.week_start.replace(day=1)
        
        # Extract value based on question type
        value = None
        if answer.int_value is not None:
            value = answer.int_value
        elif answer.text_value:
            # For emoji questions, convert to numeric
            if question.qtype == "emoji":
                emoji_map = {"😞": 1, "😕": 2, "😐": 3, "😊": 4, "😍": 5}
                value = emoji_map.get(answer.text_value, 3)  # Default to neutral
            else:
                value = 0  # Default for text values
        
        if value is not None:
            data[question.order][period].append(value)
    
    # Calculate aggregations
    result = {}
    for question_order, periods in data.items():
        question_data = []
        
        for period, values in sorted(periods.items()):
            if values:
                avg_value = sum(values) / len(values)
                question_data.append({
                    'period': period.isoformat(),
                    'value': round(avg_value, 2),
                    'count': len(values)
                })
        
        result[f"Q{question_order}"] = question_data
    
    return result

def get_emoji_distribution(evaluations, question):
    """Get emoji distribution for satisfaction questions."""
    from .models import Answer
    
    answers = Answer.objects.filter(
        instance__in=evaluations,
        question=question
    )
    
    # 5-emoji scale for customer satisfaction
    distribution = {"😞": 0, "😕": 0, "😐": 0, "😊": 0, "😍": 0}
    
    for answer in answers:
        # Handle both text_value and int_value for emoji questions
        if answer.text_value and answer.text_value in distribution:
            distribution[answer.text_value] += 1
        elif answer.int_value is not None:
            # Convert integer emoji values to emoji (1-5 scale)
            emoji_map = {
                1: "😞",  # Very dissatisfied
                2: "😕",  # Dissatisfied  
                3: "😐",  # Neutral
                4: "😊",  # Satisfied
                5: "😍"   # Very satisfied
            }
            emoji = emoji_map.get(answer.int_value, "😐")
            if emoji in distribution:
                distribution[emoji] += 1
    
    return distribution
