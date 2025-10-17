from django.core.management.base import BaseCommand
from communication.models import LogType


class Command(BaseCommand):
    help = 'Create initial communication log types'

    def handle(self, *args, **options):
        log_types = [
            {
                'name': 'Positive Feedback',
                'icon': 'fa-thumbs-up',
                'color': 'green',
                'description': 'Positive reinforcement and praise'
            },
            {
                'name': 'Constructive Feedback',
                'icon': 'fa-comment-dots',
                'color': 'yellow',
                'description': 'Areas for improvement and development'
            },
            {
                'name': 'Performance Discussion',
                'icon': 'fa-chart-line',
                'color': 'blue',
                'description': 'Performance review and goals discussion'
            },
            {
                'name': 'Instructions/Directives',
                'icon': 'fa-clipboard-list',
                'color': 'indigo',
                'description': 'Task assignments and procedural guidance'
            },
            {
                'name': 'Safety Concern',
                'icon': 'fa-exclamation-triangle',
                'color': 'red',
                'description': 'Safety-related communications'
            },
            {
                'name': 'Incident Discussion',
                'icon': 'fa-fire-extinguisher',
                'color': 'orange',
                'description': 'Discussion about specific events or incidents'
            },
            {
                'name': 'Training & Development',
                'icon': 'fa-graduation-cap',
                'color': 'purple',
                'description': 'Skill development and training discussions'
            },
            {
                'name': 'General Note',
                'icon': 'fa-sticky-note',
                'color': 'gray',
                'description': 'Miscellaneous documentation'
            },
        ]

        created_count = 0
        for log_type_data in log_types:
            log_type, created = LogType.objects.get_or_create(
                name=log_type_data['name'],
                defaults={
                    'icon': log_type_data['icon'],
                    'color': log_type_data['color'],
                    'description': log_type_data['description']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created log type: {log_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Log type already exists: {log_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new log types')
        )

