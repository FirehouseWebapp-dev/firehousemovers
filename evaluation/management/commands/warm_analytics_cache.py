"""
Management command to warm up the analytics cache.
This can be run via cron job or scheduled task to pre-compute analytics data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from evaluation.views import senior_manager_analytics_dashboard
from evaluation.cache_utils import warm_analytics_cache
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Warm up the analytics cache by pre-computing dashboard data for all senior managers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Warm cache for a specific user ID only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cache warming even if cache already exists',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force = options.get('force', False)
        
        self.stdout.write(
            self.style.SUCCESS('Starting analytics cache warming...')
        )
        
        try:
            if user_id:
                # Warm cache for specific user
                self.warm_cache_for_user(user_id, force)
            else:
                # Warm cache for all senior managers
                warm_analytics_cache()
                
            self.stdout.write(
                self.style.SUCCESS('Analytics cache warming completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error warming analytics cache: {e}')
            )
            logger.error(f"Error in warm_analytics_cache command: {e}")
            raise

    def warm_cache_for_user(self, user_id, force=False):
        """
        Warm cache for a specific user.
        
        Args:
            user_id: ID of the user to warm cache for
            force: Whether to force cache warming even if cache exists
        """
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id, userprofile__role='senior_manager')
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {user_id} not found or is not a senior manager')
            )
            return
            
        factory = RequestFactory()
        
        try:
            # Create a mock request
            request = factory.get('/analytics/')
            request.user = user
            
            # Call the view to populate cache
            response = senior_manager_analytics_dashboard(request)
            
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS(f'Analytics cache warmed for user {user_id}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Failed to warm cache for user {user_id}: {response.status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error warming cache for user {user_id}: {e}')
            )
            logger.error(f"Error warming cache for user {user_id}: {e}")
