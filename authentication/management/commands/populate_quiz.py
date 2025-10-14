from django.core.management.base import BaseCommand
from authentication.models import Department, DepartmentQuiz


class Command(BaseCommand):
    help = 'Populate quiz questions for all departments'

    def handle(self, *args, **kwargs):
        # Clear existing quiz questions
        DepartmentQuiz.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing quiz questions'))

        quiz_data = {
            'sales': [
                {
                    'question': 'What is the first step in converting a lead into a booking?',
                    'a': 'Send an invoice',
                    'b': 'Contact the customer and understand their needs',
                    'c': 'Schedule the truck',
                    'd': 'Confirm payment',
                    'correct': 'B'
                },
                {
                    'question': "What's most important when following up with a potential customer?",
                    'a': 'Timing and clear communication',
                    'b': 'Talking fast',
                    'c': 'Sending long emails',
                    'd': 'Ignoring objections',
                    'correct': 'A'
                },
                {
                    'question': 'Which of the following best represents a "qualified lead"?',
                    'a': 'Random website visitor',
                    'b': 'A friend of a mover',
                    'c': 'Someone who requested a quote',
                    'd': 'Social media follower',
                    'correct': 'C'
                },
                {
                    'question': "What should you do if a customer requests a service that's not available?",
                    'a': 'Say no immediately',
                    'b': 'Recommend alternatives or schedule later',
                    'c': 'Ignore it',
                    'd': 'Offer a discount',
                    'correct': 'B'
                },
                {
                    'question': 'What tool is best for tracking leads and follow-ups?',
                    'a': 'Notebook',
                    'b': 'CRM system',
                    'c': 'Text messages',
                    'd': 'Social media',
                    'correct': 'B'
                },
            ],
            'accounting': [
                {
                    'question': 'What is the purpose of reconciling accounts?',
                    'a': 'To match bank and company records',
                    'b': 'To approve overtime',
                    'c': 'To schedule jobs',
                    'd': 'To call clients',
                    'correct': 'A'
                },
                {
                    'question': 'An invoice should be sent:',
                    'a': 'Before the move starts',
                    'b': 'After payment',
                    'c': 'Once the job is confirmed',
                    'd': 'Anytime during the month',
                    'correct': 'C'
                },
                {
                    'question': 'What does an error-free report indicate?',
                    'a': 'Strong accuracy',
                    'b': 'Poor performance',
                    'c': 'Delayed entries',
                    'd': 'Random entries',
                    'correct': 'A'
                },
                {
                    'question': "If you find a discrepancy in billing, what's the first step?",
                    'a': 'Ignore it',
                    'b': 'Notify your manager',
                    'c': 'Delete the entry',
                    'd': 'Re-invoice the client',
                    'correct': 'B'
                },
                {
                    'question': 'What is the most important trait for an accounting employee?',
                    'a': 'Speed',
                    'b': 'Accuracy',
                    'c': 'Friendliness',
                    'd': 'Multitasking',
                    'correct': 'B'
                },
            ],
            'claims': [
                {
                    'question': 'What is the first step when a claim is reported?',
                    'a': 'Close it immediately',
                    'b': 'Document and acknowledge receipt',
                    'c': 'Delay response',
                    'd': 'Ask the driver',
                    'correct': 'B'
                },
                {
                    'question': 'When reviewing a claim, which factor matters most?',
                    'a': 'Claim value',
                    'b': 'Proper documentation',
                    'c': 'Claim date',
                    'd': 'Claim type',
                    'correct': 'B'
                },
                {
                    'question': 'How should customer communication during a claim be handled?',
                    'a': 'Professionally and transparently',
                    'b': 'Brief and dismissive',
                    'c': 'Casual',
                    'd': 'Only by email',
                    'correct': 'A'
                },
                {
                    'question': "What's a sign of a valid claim?",
                    'a': 'No documentation',
                    'b': 'Clear proof of damage',
                    'c': 'Verbal complaint only',
                    'd': 'Late submission',
                    'correct': 'B'
                },
                {
                    'question': 'Why is claim resolution speed important?',
                    'a': 'Increases customer trust',
                    'b': 'Reduces paperwork',
                    'c': 'Improves ad campaigns',
                    'd': 'None of the above',
                    'correct': 'A'
                },
            ],
            'drivers': [
                {
                    'question': "What's the most important safety check before a trip?",
                    'a': 'Checking truck condition',
                    'b': 'Loading furniture',
                    'c': 'Adjusting music',
                    'd': 'Checking emails',
                    'correct': 'A'
                },
                {
                    'question': 'What does "on-time delivery" mainly depend on?',
                    'a': 'Driver punctuality and route planning',
                    'b': 'Customer response time',
                    'c': 'Fuel prices',
                    'd': 'Paperwork',
                    'correct': 'A'
                },
                {
                    'question': 'How should fragile items be handled?',
                    'a': 'Stack on top',
                    'b': 'Load last and secure',
                    'c': 'Place under heavy boxes',
                    'd': 'Pack loosely',
                    'correct': 'B'
                },
                {
                    'question': "What's the correct behavior if an accident occurs?",
                    'a': 'Leave immediately',
                    'b': 'Report to dispatch and follow safety protocol',
                    'c': 'Hide damage',
                    'd': 'Argue with others',
                    'correct': 'B'
                },
                {
                    'question': "What's the best way to improve fuel efficiency?",
                    'a': 'Drive steadily and avoid idling',
                    'b': 'Speed up often',
                    'c': 'Use air conditioning at max',
                    'd': 'Ignore tire pressure',
                    'correct': 'A'
                },
            ],
            'it': [
                {
                    'question': "What's the first step when troubleshooting a system issue?",
                    'a': 'Restart the system',
                    'b': 'Panic',
                    'c': 'Report immediately',
                    'd': 'Reinstall OS',
                    'correct': 'A'
                },
                {
                    'question': "What's the purpose of regular system updates?",
                    'a': 'Add games',
                    'b': 'Improve security and performance',
                    'c': 'Slow down PCs',
                    'd': 'Increase storage',
                    'correct': 'B'
                },
                {
                    'question': "What's the best way to handle repeated IT requests?",
                    'a': 'Create a support ticket system',
                    'b': 'Ignore them',
                    'c': 'Ask by phone only',
                    'd': 'Post on chat',
                    'correct': 'A'
                },
                {
                    'question': "What's the most important cybersecurity rule?",
                    'a': "Don't share passwords",
                    'b': 'Use personal email',
                    'c': 'Click all links',
                    'd': 'Save passwords in notes',
                    'correct': 'A'
                },
                {
                    'question': "What's the ideal response time for IT issues under SLA?",
                    'a': 'Within 24–48 hours',
                    'b': 'Within a week',
                    'c': 'Anytime',
                    'd': 'When manager asks',
                    'correct': 'A'
                },
            ],
            'operations': [
                {
                    'question': "What's the top priority during a move?",
                    'a': 'Completing on time without damage',
                    'b': 'Speed only',
                    'c': 'Customer talk',
                    'd': 'Rest breaks',
                    'correct': 'A'
                },
                {
                    'question': 'Who ensures all crew members follow the SOP?',
                    'a': 'Operations Manager',
                    'b': 'Driver',
                    'c': 'Accountant',
                    'd': 'Sales Rep',
                    'correct': 'A'
                },
                {
                    'question': "What's a sign of efficient teamwork?",
                    'a': 'Smooth coordination and task handover',
                    'b': 'Everyone working alone',
                    'c': 'Repeated confusion',
                    'd': 'Late starts',
                    'correct': 'A'
                },
                {
                    'question': 'What should be done before starting a move?',
                    'a': 'Confirm checklist and crew readiness',
                    'b': "Wait for client's call",
                    'c': 'Skip inspection',
                    'd': 'Load immediately',
                    'correct': 'A'
                },
                {
                    'question': 'How can move-related delays be reduced?',
                    'a': 'Route planning and early dispatch',
                    'b': 'Guessing time',
                    'c': 'Ignoring updates',
                    'd': 'Overloading trucks',
                    'correct': 'A'
                },
            ],
            'warehouse': [
                {
                    'question': "What's the first step in receiving inventory?",
                    'a': 'Verify and record incoming items',
                    'b': 'Store anywhere',
                    'c': 'Skip labeling',
                    'd': 'Wait for instructions',
                    'correct': 'A'
                },
                {
                    'question': 'How can warehouse damage be minimized?',
                    'a': 'Proper stacking and safe handling',
                    'b': 'Rushing',
                    'c': 'Ignoring heavy labels',
                    'd': 'Random storage',
                    'correct': 'A'
                },
                {
                    'question': "What's a good indicator of warehouse efficiency?",
                    'a': 'Organized storage',
                    'b': 'Empty shelves',
                    'c': 'Noise level',
                    'd': 'Speed of loading',
                    'correct': 'A'
                },
                {
                    'question': 'What should be done before dispatching an item?',
                    'a': 'Verify item and documentation',
                    'b': 'Load anything',
                    'c': 'Wait for end of shift',
                    'd': 'Skip paperwork',
                    'correct': 'A'
                },
                {
                    'question': "What's key to maintaining safety in the warehouse?",
                    'a': 'Clear aisles and proper gear',
                    'b': 'Music',
                    'c': 'Open boxes',
                    'd': 'Faster shifts',
                    'correct': 'A'
                },
            ],
        }

        created_count = 0
        for dept_slug, questions in quiz_data.items():
            try:
                department = Department.objects.get(slug=dept_slug)
                
                for idx, q in enumerate(questions, start=1):
                    DepartmentQuiz.objects.create(
                        department=department,
                        question_text=q['question'],
                        option_a=q['a'],
                        option_b=q['b'],
                        option_c=q['c'],
                        option_d=q['d'],
                        correct_answer=q['correct'],
                        order=idx
                    )
                    created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created {len(questions)} questions for {department.title}')
                )
            except Department.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Department with slug "{dept_slug}" not found. Skipping...')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created {created_count} quiz questions total!')
        )

