from django.core.management.base import BaseCommand
from authentication.models import Department, DepartmentQuiz


class Command(BaseCommand):
    help = 'Populate manager quiz questions for all departments'

    def handle(self, *args, **kwargs):
        manager_quiz_data = {
            'sales': [
                {
                    'question': "What's the best way to evaluate a salesperson's performance?",
                    'a': 'Number of calls made',
                    'b': 'Lead conversion rate and customer feedback',
                    'c': 'Hours spent online',
                    'd': 'Total messages sent',
                    'correct': 'B'
                },
                {
                    'question': 'When sales are declining, what should a manager review first?',
                    'a': 'Marketing budget',
                    'b': 'Quality of leads and follow-up process',
                    'c': 'Number of trucks',
                    'd': 'Employee attendance',
                    'correct': 'B'
                },
                {
                    'question': 'How can a manager improve lead-to-booking conversion?',
                    'a': 'Provide clear sales scripts and weekly coaching',
                    'b': 'Increase lead targets only',
                    'c': 'Reduce team size',
                    'd': 'Wait for seasonal improvement',
                    'correct': 'A'
                },
                {
                    'question': "What's the best metric to measure a top-performing salesperson?",
                    'a': 'Customer satisfaction + revenue generated',
                    'b': 'Number of leads',
                    'c': 'Calls made',
                    'd': 'Time on CRM',
                    'correct': 'A'
                },
                {
                    'question': 'What should a manager do if a team member consistently underperforms?',
                    'a': 'Ignore them',
                    'b': 'Replace immediately',
                    'c': 'Offer feedback and create an improvement plan',
                    'd': 'Assign fewer tasks',
                    'correct': 'C'
                },
            ],
            'accounting': [
                {
                    'question': "What's a key indicator of a well-managed accounting team?",
                    'a': 'Quick responses to emails',
                    'b': 'Low error rate and timely reconciliations',
                    'c': 'Number of invoices processed per day',
                    'd': 'Overtime hours worked',
                    'correct': 'B'
                },
                {
                    'question': 'How should discrepancies in customer payments be handled?',
                    'a': 'Escalate immediately and audit the transaction',
                    'b': 'Ignore until month-end',
                    'c': 'Ask the customer to resend',
                    'd': 'Delete and re-enter',
                    'correct': 'A'
                },
                {
                    'question': "What's the main purpose of internal audits?",
                    'a': 'To find who made mistakes',
                    'b': 'To ensure compliance and process accuracy',
                    'c': 'To increase workload',
                    'd': 'To improve customer communication',
                    'correct': 'B'
                },
                {
                    'question': 'How can managers reduce recurring accounting errors?',
                    'a': 'Weekly reviews and process checklists',
                    'b': 'Hiring more staff',
                    'c': 'Shortening deadlines',
                    'd': 'Ignoring small mistakes',
                    'correct': 'A'
                },
                {
                    'question': "What's the correct approach if a report doesn't balance?",
                    'a': 'Submit it anyway',
                    'b': 'Adjust numbers manually',
                    'c': 'Reconcile and identify the discrepancy',
                    'd': 'Delay submission indefinitely',
                    'correct': 'C'
                },
            ],
            'claims': [
                {
                    'question': "What's the first step in ensuring fair claim resolutions?",
                    'a': 'Collect proper documentation before deciding',
                    'b': 'Assume the customer is wrong',
                    'c': 'Reject all late claims',
                    'd': 'Base decisions on crew feedback only',
                    'correct': 'A'
                },
                {
                    'question': "What's the best KPI for claims handling?",
                    'a': 'Number of claims rejected',
                    'b': 'Resolution time and customer satisfaction',
                    'c': 'Number of emails sent',
                    'd': 'Total amount refunded',
                    'correct': 'B'
                },
                {
                    'question': 'If multiple claims come from the same crew, what should a manager do?',
                    'a': 'Ignore it',
                    'b': 'Investigate patterns and provide crew training',
                    'c': 'Reduce claims payouts',
                    'd': 'Reassign the claims team',
                    'correct': 'B'
                },
                {
                    'question': 'How should managers communicate with customers about claims?',
                    'a': 'Blame the crew',
                    'b': 'Stay professional and transparent',
                    'c': 'Be defensive',
                    'd': 'Avoid giving details',
                    'correct': 'B'
                },
                {
                    'question': "What's the ideal claim resolution timeline?",
                    'a': 'Within 30 days',
                    'b': '60 days',
                    'c': '90 days',
                    'd': 'No fixed time',
                    'correct': 'A'
                },
            ],
            'it': [
                {
                    'question': "What's the most important part of IT issue management?",
                    'a': 'Logging and prioritizing tickets',
                    'b': 'Replying casually',
                    'c': 'Deleting old logs',
                    'd': 'Focusing on one user only',
                    'correct': 'A'
                },
                {
                    'question': 'How can downtime be minimized in a moving company?',
                    'a': 'Preventive maintenance and system monitoring',
                    'b': 'Waiting for breakdowns',
                    'c': 'Blaming hardware vendors',
                    'd': 'Rebooting daily',
                    'correct': 'A'
                },
                {
                    'question': "What's the best way to evaluate IT staff performance?",
                    'a': 'Tickets resolved within SLA',
                    'b': 'Number of cables arranged',
                    'c': 'Hours online',
                    'd': 'Chat messages sent',
                    'correct': 'A'
                },
                {
                    'question': 'How should IT managers handle cybersecurity?',
                    'a': 'Regular audits and staff awareness',
                    'b': 'Ignore small threats',
                    'c': 'Use shared passwords',
                    'd': 'Disable antivirus',
                    'correct': 'A'
                },
                {
                    'question': "What's a critical metric for IT in logistics-based companies?",
                    'a': 'System uptime percentage',
                    'b': 'Number of team lunches',
                    'c': 'Amount of data used',
                    'd': 'Tickets opened',
                    'correct': 'A'
                },
            ],
            'operations': [
                {
                    'question': "What's the best way to track crew performance?",
                    'a': 'On-time move completion and damage rate',
                    'b': 'Number of trucks used',
                    'c': 'Number of calls made',
                    'd': 'Days worked',
                    'correct': 'A'
                },
                {
                    'question': 'When operations are delayed, what should a manager check first?',
                    'a': 'Scheduling and resource allocation',
                    'b': 'Sales report',
                    'c': 'Weather history',
                    'd': 'Claim records',
                    'correct': 'A'
                },
                {
                    'question': "What's an essential skill for an operations manager?",
                    'a': 'Resource planning and team coordination',
                    'b': 'Truck driving',
                    'c': 'Manual labor',
                    'd': 'Customer upselling',
                    'correct': 'A'
                },
                {
                    'question': 'How can managers prevent repeat move issues?',
                    'a': 'Weekly debriefs with crew and feedback analysis',
                    'b': 'Ignoring reports',
                    'c': 'Reassigning jobs randomly',
                    'd': 'Reducing jobs per day',
                    'correct': 'A'
                },
                {
                    'question': "What's the most important daily task?",
                    'a': 'Reviewing move logs and truck status',
                    'b': 'Reading emails',
                    'c': 'Checking social media',
                    'd': 'Preparing invoices',
                    'correct': 'A'
                },
            ],
            'warehouse': [
                {
                    'question': "What's the key to effective warehouse organization?",
                    'a': 'Clear labeling and storage mapping',
                    'b': 'Random stacking',
                    'c': 'Moving items daily',
                    'd': 'Ignoring damaged goods',
                    'correct': 'A'
                },
                {
                    'question': "What's a good KPI for warehouse efficiency?",
                    'a': 'Damage-free handling rate',
                    'b': 'Number of boxes',
                    'c': 'Employee count',
                    'd': 'Overtime hours',
                    'correct': 'A'
                },
                {
                    'question': 'How should managers ensure safety?',
                    'a': 'Conduct routine checks and enforce PPE rules',
                    'b': 'Rely on crew experience only',
                    'c': 'Skip morning briefings',
                    'd': 'Wait for incidents',
                    'correct': 'A'
                },
                {
                    'question': "What's the best way to reduce inventory errors?",
                    'a': 'Barcode scanning and double-checking',
                    'b': 'Manual counting only',
                    'c': 'Ignoring mismatches',
                    'd': 'Estimating by eye',
                    'correct': 'A'
                },
                {
                    'question': 'When storage is near capacity, what should be done?',
                    'a': 'Optimize existing space or schedule removals',
                    'b': 'Close operations',
                    'c': 'Move items randomly',
                    'd': 'Refuse all new jobs',
                    'correct': 'A'
                },
            ],
            'drivers': [
                {
                    'question': "What's the most important factor when assigning routes?",
                    'a': 'Distance and traffic conditions',
                    'b': 'Driver age',
                    'c': 'Random order',
                    'd': 'Truck color',
                    'correct': 'A'
                },
                {
                    'question': 'How can managers reduce delivery delays?',
                    'a': 'Plan routes and start times in advance',
                    'b': 'Add more breaks',
                    'c': 'Ignore GPS',
                    'd': 'Wait for customer calls',
                    'correct': 'A'
                },
                {
                    'question': 'How should managers handle driver fatigue?',
                    'a': 'Schedule rest breaks and rotate shifts',
                    'b': 'Encourage longer drives',
                    'c': 'Ignore signs',
                    'd': 'Offer bonuses only',
                    'correct': 'A'
                },
                {
                    'question': "What's a good KPI for driver performance?",
                    'a': 'On-time delivery rate',
                    'b': 'Total kilometers',
                    'c': 'Fuel cost',
                    'd': 'Break duration',
                    'correct': 'A'
                },
                {
                    'question': "What's the right response if a driver reports a vehicle issue?",
                    'a': 'Stop operations and send for inspection',
                    'b': 'Ignore and continue',
                    'c': 'Ask driver to fix it',
                    'd': 'Use another truck without checking',
                    'correct': 'A'
                },
            ],
        }

        created_count = 0
        for dept_slug, questions in manager_quiz_data.items():
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
                        order=idx,
                        audience='manager'
                    )
                    created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created {len(questions)} manager questions for {department.title}')
                )
            except Department.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Department with slug "{dept_slug}" not found. Skipping...')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created {created_count} manager quiz questions total!')
        )

