"""
Management command to manage analytics cache.
Provides operations to clear, warm, and inspect analytics cache.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth import get_user_model
from evaluation.cache_utils import invalidate_analytics_cache, warm_analytics_cache
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage analytics cache operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['clear', 'warm', 'status'],
            help='Action to perform: clear, warm, or status'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Target specific user ID (for warm/status actions)',
        )

    def handle(self, *args, **options):
        action = options['action']
        user_id = options.get('user_id')
        
        if action == 'clear':
            self.clear_cache()
        elif action == 'warm':
            self.warm_cache(user_id)
        elif action == 'status':
            self.show_cache_status(user_id)

    def clear_cache(self):
        """Clear all analytics cache."""
        self.stdout.write('Clearing analytics cache...')
        
        try:
            invalidate_analytics_cache()
            self.stdout.write(
                self.style.SUCCESS('Analytics cache cleared successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing cache: {e}')
            )
            logger.error(f"Error clearing analytics cache: {e}")

    def warm_cache(self, user_id=None):
        """Warm analytics cache."""
        if user_id:
            self.stdout.write(f'Warming analytics cache for user {user_id}...')
        else:
            self.stdout.write('Warming analytics cache for all senior managers...')
        
        try:
            if user_id:
                from django.test import RequestFactory
                from evaluation.views import senior_manager_analytics_dashboard
                
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id, userprofile__role='senior_manager')
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'User {user_id} not found or is not a senior manager')
                    )
                    return
                
                factory = RequestFactory()
                request = factory.get('/analytics/')
                request.user = user
                
                response = senior_manager_analytics_dashboard(request)
                
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS(f'Analytics cache warmed for user {user_id}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to warm cache for user {user_id}: {response.status_code}')
                    )
            else:
                warm_analytics_cache()
                self.stdout.write(
                    self.style.SUCCESS('Analytics cache warmed for all senior managers!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error warming cache: {e}')
            )
            logger.error(f"Error warming analytics cache: {e}")

    def show_cache_status(self, user_id=None):
        """Show cache status information."""
        self.stdout.write('Analytics Cache Status:')
        self.stdout.write('=' * 50)
        
        try:
            # Show cache backend info
            cache_backend = cache.__class__.__name__
            self.stdout.write(f'Cache Backend: {cache_backend}')
            
            # Show cache configuration
            if hasattr(cache, '_cache'):
                cache_config = getattr(cache._cache, 'params', {})
                self.stdout.write(f'Cache Configuration: {cache_config}')
            
            # Show cache statistics (if available)
            if hasattr(cache, 'get_stats'):
                stats = cache.get_stats()
                if stats:
                    self.stdout.write('Cache Statistics:')
                    for key, value in stats.items():
                        self.stdout.write(f'  {key}: {value}')
            
            # Test cache functionality
            test_key = 'analytics_cache_test'
            test_value = 'test_data'
            
            # Set test value
            cache.set(test_key, test_value, timeout=60)
            
            # Get test value
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                self.stdout.write(
                    self.style.SUCCESS('Cache is working correctly')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Cache is not working correctly')
                )
            
            # Clean up test value
            cache.delete(test_key)
            
            # Show senior managers count
            User = get_user_model()
            senior_managers_count = User.objects.filter(
                userprofile__role='senior_manager'
            ).count()
            
            self.stdout.write(f'Senior Managers: {senior_managers_count}')
            
            if user_id:
                try:
                    user = User.objects.get(id=user_id, userprofile__role='senior_manager')
                    self.stdout.write(f'Target User: {user.get_full_name()} (ID: {user_id})')
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'User {user_id} not found or is not a senior manager')
                    )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking cache status: {e}')
            )
            logger.error(f"Error checking cache status: {e}")
