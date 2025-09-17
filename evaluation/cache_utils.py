"""
Cache utilities for evaluation analytics dashboard.
Provides cache invalidation when evaluation data changes.
"""

from django.core.cache import cache, caches
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def get_all_cache_aliases():
    """
    Get all configured cache aliases from settings.
    This ensures we clear all caches, including future ones.
    """
    try:
        return list(settings.CACHES.keys())
    except AttributeError:
        # Fallback to known aliases if settings not available
        return ['default', 'analytics']


def invalidate_analytics_cache():
    """
    Invalidate all analytics dashboard cache entries across all configured cache aliases.
    This should be called when evaluation data changes.
    """
    try:
        # Get all cache aliases dynamically from settings
        cache_aliases = get_all_cache_aliases()
        cleared_caches = []
        failed_caches = []
        
        for alias in cache_aliases:
            try:
                cache_instance = caches[alias]
                cache_instance.clear()
                cleared_caches.append(alias)
                logger.info(f"Cache '{alias}' cleared successfully")
            except Exception as alias_error:
                failed_caches.append(alias)
                logger.error(f"Error clearing cache '{alias}': {alias_error}")
        
        if cleared_caches:
            logger.info(f"Analytics caches cleared: {', '.join(cleared_caches)}")
        if failed_caches:
            logger.warning(f"Failed to clear caches: {', '.join(failed_caches)}")
            
        logger.info("Analytics cache invalidation completed")
        
    except Exception as e:
        logger.error(f"Error invalidating analytics cache: {e}")


def invalidate_user_analytics_cache(user_id=None):
    """
    Invalidate analytics cache for a specific user or all users across all cache aliases.
    
    Args:
        user_id: Specific user ID to invalidate cache for, or None for all users
    """
    try:
        if user_id:
            # Invalidate cache for specific user across all cache aliases
            today = timezone.now().date()
            cache_key = f"analytics_dashboard_{user_id}_{today}"
            
            cache_aliases = get_all_cache_aliases()
            deleted_from = []
            failed_from = []
            
            for alias in cache_aliases:
                try:
                    cache_instance = caches[alias]
                    cache_instance.delete(cache_key)
                    deleted_from.append(alias)
                except Exception as alias_error:
                    failed_from.append(alias)
                    logger.error(f"Error deleting cache key from '{alias}': {alias_error}")
            
            if deleted_from:
                logger.info(f"Analytics cache key '{cache_key}' deleted from: {', '.join(deleted_from)}")
            if failed_from:
                logger.warning(f"Failed to delete cache key from: {', '.join(failed_from)}")
        else:
            # Invalidate all analytics cache
            invalidate_analytics_cache()
            
    except Exception as e:
        logger.error(f"Error invalidating user analytics cache: {e}")


def serialize_evaluation_for_cache(evaluation):
    """
    Convert evaluation model instance to a lean dictionary for caching.
    Only includes essential fields needed for rendering.
    """
    try:
        return {
            'id': evaluation.id,
            'employee_name': evaluation.employee.user.get_full_name() if evaluation.employee else 'N/A',
            'employee_id': evaluation.employee.id if evaluation.employee else None,
            'manager_name': evaluation.manager.user.get_full_name() if evaluation.manager else 'N/A',
            'manager_id': evaluation.manager.id if evaluation.manager else None,
            'department': evaluation.employee.department.title if evaluation.employee and evaluation.employee.department else 'N/A',
            'status': evaluation.status,
            'submitted_at': evaluation.submitted_at.isoformat() if evaluation.submitted_at else None,
            'week_end': evaluation.week_end.isoformat() if hasattr(evaluation, 'week_end') and evaluation.week_end else None,
            'score': getattr(evaluation, 'score', None),  # If score field exists
        }
    except Exception as e:
        logger.error(f"Error serializing evaluation {evaluation.id}: {e}")
        return None


def serialize_manager_evaluation_for_cache(evaluation):
    """
    Convert manager evaluation model instance to a lean dictionary for caching.
    """
    try:
        return {
            'id': evaluation.id,
            'manager_name': evaluation.manager.user.get_full_name() if evaluation.manager else 'N/A',
            'manager_id': evaluation.manager.id if evaluation.manager else None,
            'senior_manager_name': evaluation.senior_manager.user.get_full_name() if evaluation.senior_manager else 'N/A',
            'senior_manager_id': evaluation.senior_manager.id if evaluation.senior_manager else None,
            'department': evaluation.manager.department.title if evaluation.manager and evaluation.manager.department else 'N/A',
            'status': evaluation.status,
            'submitted_at': evaluation.submitted_at.isoformat() if evaluation.submitted_at else None,
            'week_end': evaluation.week_end.isoformat() if hasattr(evaluation, 'week_end') and evaluation.week_end else None,
            'score': getattr(evaluation, 'score', None),
        }
    except Exception as e:
        logger.error(f"Error serializing manager evaluation {evaluation.id}: {e}")
        return None


def get_lean_recent_evaluations(evaluation_queryset, evaluation_type='employee'):
    """
    Get recent evaluations as lean dictionaries instead of full model instances.
    
    Args:
        evaluation_queryset: Django queryset of evaluations
        evaluation_type: 'employee' or 'manager' for proper serialization
    
    Returns:
        dict: Contains 'items' (list of dicts), 'count', and 'ids'
    """
    try:
        # Limit to reasonable number and select only needed fields
        evaluations = evaluation_queryset.select_related(
            'employee__user', 'employee__department', 'manager__user', 'manager__department'
        ).order_by('-submitted_at')[:20]  # Limit to 20 most recent
        
        serializer = (serialize_evaluation_for_cache if evaluation_type == 'employee' 
                     else serialize_manager_evaluation_for_cache)
        
        serialized_items = []
        evaluation_ids = []
        
        for eval_obj in evaluations:
            serialized = serializer(eval_obj)
            if serialized:
                serialized_items.append(serialized)
                evaluation_ids.append(eval_obj.id)
        
        return {
            'items': serialized_items,
            'count': len(serialized_items),
            'ids': evaluation_ids,
            'cached_at': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting lean recent evaluations: {e}")
        return {'items': [], 'count': 0, 'ids': [], 'cached_at': timezone.now().isoformat()}


def warm_analytics_cache():
    """
    Warm up the analytics cache by pre-computing dashboard data.
    This can be called via management command or scheduled task.
    """
    try:
        from .views import senior_manager_analytics_dashboard
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory
        
        User = get_user_model()
        
        # Get all senior managers
        senior_managers = User.objects.filter(
            userprofile__role='senior_manager'
        ).select_related('userprofile')
        
        factory = RequestFactory()
        
        for user in senior_managers:
            try:
                # Create a mock request
                request = factory.get('/analytics/')
                request.user = user
                
                # Call the view to populate cache
                response = senior_manager_analytics_dashboard(request)
                
                if response.status_code == 200:
                    logger.info(f"Analytics cache warmed for user {user.id}")
                else:
                    logger.warning(f"Failed to warm cache for user {user.id}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error warming cache for user {user.id}: {e}")
                
        logger.info("Analytics cache warming completed")
        
    except Exception as e:
        logger.error(f"Error warming analytics cache: {e}")


def cache_recent_evaluations(cache_key, evaluation_queryset, evaluation_type='employee', timeout=1800, user_id=None):
    """
    Cache recent evaluations as lean data structures with user-specific keys.
    
    Args:
        cache_key: Base cache key to store under
        evaluation_queryset: Django queryset
        evaluation_type: 'employee' or 'manager'
        timeout: Cache timeout in seconds (default 30 minutes)
        user_id: User ID for permission-specific caching (SECURITY CRITICAL)
    """
    try:
        from django.core.cache import caches
        
        # Use analytics cache for better organization
        analytics_cache = caches['analytics']
        
        # SECURITY: Make cache key user-specific to prevent data leakage
        if user_id:
            secure_cache_key = f"{cache_key}_user_{user_id}"
        else:
            logger.warning(f"No user_id provided for cache key '{cache_key}' - potential security risk!")
            secure_cache_key = cache_key
        
        lean_data = get_lean_recent_evaluations(evaluation_queryset, evaluation_type)
        analytics_cache.set(secure_cache_key, lean_data, timeout)
        
        logger.info(f"Cached {lean_data['count']} recent {evaluation_type} evaluations under key '{secure_cache_key}'")
        return lean_data
        
    except Exception as e:
        logger.error(f"Error caching recent evaluations: {e}")
        return None


def get_cached_recent_evaluations(cache_key, fallback_queryset=None, evaluation_type='employee', user_id=None):
    """
    Get recent evaluations from cache or compute if not cached.
    
    Args:
        cache_key: Base cache key to look up
        fallback_queryset: Queryset to use if cache miss
        evaluation_type: 'employee' or 'manager'
        user_id: User ID for permission-specific caching (SECURITY CRITICAL)
    
    Returns:
        dict: Lean evaluation data or empty structure
    """
    try:
        from django.core.cache import caches
        
        analytics_cache = caches['analytics']
        
        # SECURITY: Make cache key user-specific to prevent data leakage
        if user_id:
            secure_cache_key = f"{cache_key}_user_{user_id}"
        else:
            logger.warning(f"No user_id provided for cache key '{cache_key}' - potential security risk!")
            secure_cache_key = cache_key
        
        cached_data = analytics_cache.get(secure_cache_key)
        
        if cached_data:
            logger.debug(f"Cache hit for recent evaluations: {secure_cache_key}")
            return cached_data
            
        if fallback_queryset is not None:
            logger.debug(f"Cache miss for recent evaluations: {secure_cache_key}, computing...")
            return cache_recent_evaluations(cache_key, fallback_queryset, evaluation_type, user_id=user_id)
            
        # Return empty structure if no fallback
        return {'items': [], 'count': 0, 'ids': [], 'cached_at': timezone.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Error getting cached recent evaluations: {e}")
        return {'items': [], 'count': 0, 'ids': [], 'cached_at': timezone.now().isoformat()}
