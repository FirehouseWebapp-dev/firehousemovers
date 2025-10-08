"""
Example usage of the reusable analytics dashboard.

This file demonstrates how to use the dashboard for different departments
and provides example data structures.
"""

from django.shortcuts import render
from .dashboard_utils import get_question_labels, QUESTION_LABELS, CHART_TYPES

def example_usage():
    """
    Example of how to use the dashboard for different departments.
    """
    
    # Example 1: Sales Department Dashboard
    sales_labels = get_question_labels("sales")
    print("Sales Department Labels:")
    for key, label in sales_labels.items():
        print(f"  {key}: {label}")
    
    # Example 2: Drivers Department Dashboard  
    drivers_labels = get_question_labels("drivers")
    print("\nDrivers Department Labels:")
    for key, label in drivers_labels.items():
        print(f"  {key}: {label}")
    
    # Example 3: Chart Types
    print("\nChart Types:")
    for question, chart_type in CHART_TYPES.items():
        print(f"  {question}: {chart_type}")

def example_json_response():
    """
    Example JSON response structure that the API returns.
    """
    return {
        "chart_data": {
            "Q1": {
                "type": "line",
                "data": [
                    {"period": "2024-01-01", "value": 15.5, "count": 3},
                    {"period": "2024-01-02", "value": 18.2, "count": 2},
                    {"period": "2024-01-03", "value": 12.8, "count": 4}
                ],
                "label": "Leads Generated"
            },
            "Q2": {
                "type": "bar", 
                "data": [
                    {"period": "2024-01-01", "value": 85.0, "count": 3},
                    {"period": "2024-01-02", "value": 92.5, "count": 2},
                    {"period": "2024-01-03", "value": 78.3, "count": 4}
                ],
                "label": "Conversion Rate"
            },
            "Q3": {
                "type": "pie",
                "data": {
                    "😃": 12,
                    "😐": 8, 
                    "😞": 3
                },
                "label": "Customer Satisfaction"
            },
            "Q4": {
                "type": "radar",
                "data": [
                    {"period": "2024-01-01", "value": 4.2, "count": 3},
                    {"period": "2024-01-02", "value": 4.5, "count": 2},
                    {"period": "2024-01-03", "value": 3.8, "count": 4}
                ],
                "label": "Target Achievement"
            },
            "Q5": {
                "type": "gauge",
                "data": [
                    {"period": "2024-01-01", "value": 7.5, "count": 3},
                    {"period": "2024-01-02", "value": 8.2, "count": 2},
                    {"period": "2024-01-03", "value": 6.8, "count": 4}
                ],
                "label": "Future Confidence"
            }
        },
        "question_labels": {
            "Q1": "Leads Generated",
            "Q2": "Conversion Rate", 
            "Q3": "Customer Satisfaction",
            "Q4": "Target Achievement",
            "Q5": "Future Confidence"
        },
        "range_type": "weekly",
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "granularity": "daily"
    }

def example_django_view_context():
    """
    Example context data passed to the Django template.
    """
    return {
        'department': {
            'title': 'Sales',
            'slug': 'sales'
        },
        'employee': {
            'id': 123,
            'user': {
                'first_name': 'John',
                'last_name': 'Doe'
            }
        },
        'chart_data': {
            # Same structure as example_json_response() above
        },
        'question_labels': {
            'Q1': 'Leads Generated',
            'Q2': 'Conversion Rate',
            'Q3': 'Customer Satisfaction', 
            'Q4': 'Target Achievement',
            'Q5': 'Future Confidence'
        },
        'range_type': 'weekly',
        'start_date': '2024-01-01',
        'end_date': '2024-01-07',
        'granularity': 'daily',
        'total_evaluations': 25,
        'completion_rate': 85.5,
        'department_employees': [
            {'id': 123, 'user': {'first_name': 'John', 'last_name': 'Doe'}},
            {'id': 124, 'user': {'first_name': 'Jane', 'last_name': 'Smith'}}
        ],
        'chart_types': {
            'Q1': 'line',
            'Q2': 'bar', 
            'Q3': 'pie',
            'Q4': 'radar',
            'Q5': 'gauge'
        }
    }

# URL Examples:
"""
Dashboard URLs:

1. Department-wide dashboard:
   /evaluation/dashboard/sales/
   
2. Employee-specific dashboard:
   /evaluation/dashboard/sales/123/
   
3. With time range filters:
   /evaluation/dashboard/sales/?range=monthly
   /evaluation/dashboard/sales/123/?range=yearly
   
4. API endpoints (JSON responses):
   /evaluation/api/dashboard/sales/
   /evaluation/api/dashboard/sales/123/
"""

# Usage Examples:
"""
1. Sales Department Dashboard:
   - Q1: "Leads Generated" (Line Chart)
   - Q2: "Conversion Rate" (Bar Chart) 
   - Q3: "Customer Satisfaction" (Pie Chart - Emoji distribution)
   - Q4: "Target Achievement" (Radar Chart)
   - Q5: "Future Confidence" (Gauge Chart)

2. Drivers Department Dashboard:
   - Q1: "Moves Completed" (Line Chart)
   - Q2: "On-time %" (Bar Chart)
   - Q3: "Customer Satisfaction" (Pie Chart - Emoji distribution)
   - Q4: "Safety Rating" (Radar Chart)
   - Q5: "Future Confidence" (Gauge Chart)

3. Accounting Department Dashboard:
   - Q1: "Invoices Processed" (Line Chart)
   - Q2: "Accuracy Rate" (Bar Chart)
   - Q3: "Team Satisfaction" (Pie Chart - Emoji distribution)
   - Q4: "Target Achievement" (Radar Chart)
   - Q5: "Future Confidence" (Gauge Chart)
"""
