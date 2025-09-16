"""
Cache utilities for evaluation analytics dashboard.
Provides cache invalidation when evaluation data changes.
"""

from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def invalidate_analytics_cache():
    """
    Invalidate all analytics dashboard cache entries.
    This should be called when evaluation data changes.
    """
    try:
        # Clear the entire cache to ensure all analytics data is fresh
        cache.clear()
        logger.info("Analytics cache invalidated due to evaluation data changes")
        
    except Exception as e:
        logger.error(f"Error invalidating analytics cache: {e}")


def invalidate_user_analytics_cache(user_id=None):
    """
    Invalidate analytics cache for a specific user or all users.
    
    Args:
        user_id: Specific user ID to invalidate cache for, or None for all users
    """
    try:
        if user_id:
            # Invalidate cache for specific user (try multiple date formats)
            today = timezone.now().date()
            cache_key = f"analytics_dashboard_{user_id}_{today}"
            cache.delete(cache_key)
            logger.info(f"Analytics cache invalidated for user {user_id}")
        else:
            # Invalidate all analytics cache
            invalidate_analytics_cache()
            
    except Exception as e:
        logger.error(f"Error invalidating user analytics cache: {e}")


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
