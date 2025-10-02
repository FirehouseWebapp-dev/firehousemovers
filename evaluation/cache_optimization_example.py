"""
Example of how to optimize the senior manager analytics dashboard 
to use lean caching instead of full model instances.

This demonstrates the before/after approach for memory-efficient caching.
"""

from django.core.cache import caches
from django.utils import timezone
from datetime import timedelta
from .cache_utils import get_cached_recent_evaluations, cache_recent_evaluations

def senior_manager_analytics_dashboard_optimized(request):
    """
    OPTIMIZED version of the analytics dashboard that uses lean caching.
    """
    # ... existing code for permissions, date setup, etc. ...
    
    today = timezone.now()
    today_date = today.date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Create cache key based on user and date
    cache_key = f"analytics_dashboard_{request.user.id}_{today_date}"
    
    # Try to get cached data first
    analytics_cache = caches['analytics']
    cached_data = analytics_cache.get(cache_key)
    
    if cached_data:
        # Use cached data but get fresh recent evaluations using lean caching
        recent_employee_key = f"recent_employee_evals_{today_date}"
        recent_manager_key = f"recent_manager_evals_{today_date}"
        
        # Get lean recent evaluations (only essential data)
        recent_employee_data = get_cached_recent_evaluations(
            recent_employee_key, 
            fallback_queryset=None,  # Will be computed if needed
            evaluation_type='employee'
        )
        
        recent_manager_data = get_cached_recent_evaluations(
            recent_manager_key,
            fallback_queryset=None,
            evaluation_type='manager'
        )
        
        # Update cached data with fresh recent evaluations
        cached_data.update({
            'recent_employee_evals': recent_employee_data['items'],
            'recent_manager_evals': recent_manager_data['items'],
            'recent_employee_evals_count': recent_employee_data['count'],
            'recent_manager_evals_count': recent_manager_data['count'],
            'last_viewed_at': timezone.now(),
        })
        
        return render(request, "evaluation/senior_manager_analytics_dashboard.html", cached_data)
    
    # Cache miss - compute fresh data with lean recent evaluations
    
    # ... existing code for computing stats, department analytics, etc. ...
    
    # BEFORE (memory-intensive):
    # recent_employee_evals = all_employee_evaluations.filter(submitted_at__gte=thirty_days_ago)
    # recent_manager_evals = all_manager_evaluations.filter(submitted_at__gte=thirty_days_ago)
    # context = {
    #     'recent_employee_evals': list(recent_employee_evals),  # Full model instances!
    #     'recent_manager_evals': list(recent_manager_evals),    # Full model instances!
    # }
    
    # AFTER (lean caching):
    recent_employee_key = f"recent_employee_evals_{today_date}"
    recent_manager_key = f"recent_manager_evals_{today_date}"
    
    # Get recent evaluations as lean data
    recent_employee_qs = all_employee_evaluations.filter(submitted_at__gte=thirty_days_ago)
    recent_manager_qs = all_manager_evaluations.filter(submitted_at__gte=thirty_days_ago)
    
    recent_employee_data = cache_recent_evaluations(
        recent_employee_key, 
        recent_employee_qs, 
        'employee'
    )
    
    recent_manager_data = cache_recent_evaluations(
        recent_manager_key, 
        recent_manager_qs, 
        'manager'
    )
    
    context_data = {
        # ... other analytics data ...
        
        # Lean recent evaluations (only essential fields)
        'recent_employee_evals': recent_employee_data['items'],
        'recent_manager_evals': recent_manager_data['items'],
        'recent_employee_evals_count': recent_employee_data['count'],
        'recent_manager_evals_count': recent_manager_data['count'],
        
        # ... rest of context ...
        'today': today_date,
        'last_viewed_at': timezone.now(),
        'data_computed_at': timezone.now(),
    }
    
    # Cache the main dashboard data (without full model instances)
    analytics_cache.set(cache_key, context_data, timeout=1800)
    
    return render(request, "evaluation/senior_manager_analytics_dashboard.html", context_data)


# Template usage example - how to handle lean data in templates
TEMPLATE_USAGE_EXAMPLE = """
<!-- BEFORE: Using full model instances -->
{% for eval in recent_employee_evals %}
    <div>{{ eval.employee.user.get_full_name }} - {{ eval.status }}</div>
{% endfor %}

<!-- AFTER: Using lean cached data -->
{% for eval in recent_employee_evals %}
    <div>{{ eval.employee_name }} - {{ eval.status }}</div>
{% endfor %}

<!-- Benefits of lean caching: -->
<!-- 1. Much smaller memory footprint -->
<!-- 2. No accidental N+1 queries in templates -->
<!-- 3. Faster serialization/deserialization -->
<!-- 4. More predictable performance -->
"""


def get_evaluation_details_on_demand(evaluation_id):
    """
    Example of how to fetch full evaluation details only when needed.
    This can be called via AJAX or when user clicks "View Details".
    """
    from .models import DynamicEvaluation
    
    try:
        # Only fetch full details when explicitly requested
        evaluation = DynamicEvaluation.objects.select_related(
            'employee__user', 'employee__department',
            'manager__user', 'manager__department'
        ).get(id=evaluation_id)
        
        return {
            'id': evaluation.id,
            'employee': {
                'name': evaluation.employee.user.get_full_name(),
                'department': evaluation.employee.department.title,
                'email': evaluation.employee.user.email,
            },
            'manager': {
                'name': evaluation.manager.user.get_full_name(),
                'department': evaluation.manager.department.title,
            },
            'status': evaluation.status,
            'submitted_at': evaluation.submitted_at,
            'week_end': evaluation.week_end,
            'responses': evaluation.responses,  # Full response data
            # ... other detailed fields as needed
        }
    except DynamicEvaluation.DoesNotExist:
        return None


# Memory usage comparison example
MEMORY_COMPARISON = """
BEFORE (Full Model Instances):
- Each evaluation: ~2-5KB (with related objects)
- 100 recent evaluations: ~200-500KB
- Plus Django ORM overhead: ~50-100KB
- Total per cache entry: ~250-600KB

AFTER (Lean Dictionaries):
- Each evaluation: ~200-500 bytes (essential fields only)
- 100 recent evaluations: ~20-50KB  
- No ORM overhead in cache
- Total per cache entry: ~20-50KB

Memory savings: 80-90% reduction!
"""
