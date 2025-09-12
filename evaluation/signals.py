from django.db.models.signals import post_save
from django.dispatch import receiver
from .models_dynamic import EvalForm, Question, QuestionChoice


@receiver(post_save, sender=EvalForm)
def create_default_questions_for_manager_evaluations(sender, instance, created, **kwargs):
    """
    Automatically create default questions for manager evaluation forms.
    This only runs when a new EvalForm is created and it's a manager evaluation type.
    """
    if not created:
        return
    
    # Only create default questions for manager evaluation types
    manager_evaluation_types = ['Monthly Evaluation', 'Quarterly Evaluation', 'Annual Evaluation']
    
    if instance.name not in manager_evaluation_types:
        return
    
    # Check if questions already exist (prevent duplicates)
    if instance.questions.exists():
        return
    
    # Define default questions for manager evaluations
    default_questions = [
        {
            'text': 'Goals Achieved',
            'qtype': Question.QType.SHORT,
            'required': True,
            'order': 0,
        },
        {
            'text': 'Set Objectives',
            'qtype': Question.QType.SHORT,
            'required': True,
            'order': 1,
        },
        {
            'text': 'Strengths',
            'qtype': Question.QType.SHORT,
            'required': True,
            'order': 2,
        },
        {
            'text': 'Areas for Improvement',
            'qtype': Question.QType.SHORT,
            'required': True,
            'order': 3,
        },
        {
            'text': 'Overall Rating',
            'qtype': Question.QType.STARS,
            'required': True,
            'order': 4,
        },
    ]
    
    # Create the questions
    questions_to_create = []
    for question_data in default_questions:
        question = Question(
            form=instance,
            text=question_data['text'],
            help_text=question_data.get('help_text', ''),
            qtype=question_data['qtype'],
            required=question_data['required'],
            order=question_data['order'],
            min_value=1 if question_data['qtype'] == Question.QType.STARS else None,
            max_value=5 if question_data['qtype'] == Question.QType.STARS else None,
        )
        questions_to_create.append(question)
    
    # Bulk create all questions
    Question.objects.bulk_create(questions_to_create)
