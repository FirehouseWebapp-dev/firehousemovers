from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EvalForm, Question, QuestionChoice, DynamicEvaluation, DynamicManagerEvaluation
from .cache_utils import invalidate_analytics_cache, invalidate_user_analytics_cache
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=EvalForm)
def create_default_questions_for_evaluations(sender, instance, created, **kwargs):
    """
    Automatically create default questions for evaluation forms.
    This handles both manager evaluations and sales department weekly evaluations.
    """
    if not created:
        return
    
    # Check if questions already exist (prevent duplicates)
    if instance.questions.exists():
        return
    
    # Define default questions based on evaluation type and department
    default_questions = []
    
    # Manager evaluation types (Monthly, Quarterly, Annual)
    manager_evaluation_types = ['Monthly Evaluation', 'Quarterly Evaluation', 'Annual Evaluation']
    if instance.name in manager_evaluation_types:
        default_questions = [
            {
                'text': 'Goals Achieved',
                'qtype': Question.QType.LONG,
                'required': True,
                'order': 0,
                'include_in_trends': False,
            },
            {
                'text': 'Set Objectives',
                'qtype': Question.QType.LONG,
                'required': True,
                'order': 1,
                'include_in_trends': False,
            },
            {
                'text': 'Strengths',
                'qtype': Question.QType.LONG,
                'required': True,
                'order': 2,
                'include_in_trends': False,
            },
            {
                'text': 'Areas for Improvement',
                'qtype': Question.QType.LONG,
                'required': True,
                'order': 3,
                'include_in_trends': False,
            },
            {
                'text': 'Overall Rating',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 4,
                'include_in_trends': True,
            },
        ]
    
    # Sales department weekly evaluations
    elif (instance.name == 'Weekly Evaluation' and 
          instance.department.title.upper() == 'SALES'):
        default_questions = [
            {
                'text': 'How many new leads did the employee generate this week?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 0,
                'min_value': 0,
                'max_value': None,
                'include_in_trends': True,
            },
            {
                'text': 'How effectively did the employee convert leads into bookings?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 1,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How satisfied are customers after interacting with this employee?',
                'qtype': Question.QType.EMOJI,
                'required': True,
                'order': 2,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How well does the employee meet or exceed sales targets?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 3,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How confident are you in this employee\'s ability to close future deals?',
                'qtype': Question.QType.RATING,
                'required': True,
                'order': 4,
                'min_value': 1,
                'max_value': 10,
                'include_in_trends': True,
            },
        ]
    
    # Accounting department weekly evaluations
    elif (instance.name == 'Weekly Evaluation' and 
          instance.department.title.upper() == 'ACCOUNTING'):
        default_questions = [
            {
                'text': 'How many invoices did the employee process this week?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 0,
                'min_value': 0,
                'max_value': None,
                'include_in_trends': True,
            },
            {
                'text': 'What percentage of the employee\'s work was error-free?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 1,
                'min_value': 0,
                'max_value': 100,
                'include_in_trends': True,
            },
            {
                'text': 'How accurate and detail-oriented is this employee?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 2,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How timely is the employee in completing accounting tasks?',
                'qtype': Question.QType.EMOJI,
                'required': True,
                'order': 3,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How confident are you in this employee\'s ability to meet financial deadlines?',
                'qtype': Question.QType.RATING,
                'required': True,
                'order': 4,
                'min_value': 1,
                'max_value': 10,
                'include_in_trends': True,
            },
        ]
    
    # Claims department weekly evaluations
    elif (instance.name == 'Weekly Evaluation' and 
          instance.department.title.upper() == 'CLAIMS'):
        default_questions = [
            {
                'text': 'How many claims did the employee process this week?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 0,
                'min_value': 0,
                'max_value': None,
                'include_in_trends': True,
            },
            {
                'text': 'What percentage of the employee\'s claims were resolved within the standard timeframe?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 1,
                'min_value': 0,
                'max_value': 100,
                'include_in_trends': True,
            },
            {
                'text': 'How well does this employee document and handle claim cases?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 2,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How would you rate this employee\'s communication with customers during claims?',
                'qtype': Question.QType.EMOJI,
                'required': True,
                'order': 3,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How confident are you that this employee handles claims fairly and efficiently?',
                'qtype': Question.QType.RATING,
                'required': True,
                'order': 4,
                'min_value': 1,
                'max_value': 10,
                'include_in_trends': True,
            },
        ]
    
    # IT department weekly evaluations
    elif (instance.name == 'Weekly Evaluation' and 
          instance.department.title.upper() == 'IT'):
        default_questions = [
            {
                'text': 'How many IT support requests did the employee resolve this week?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 0,
                'min_value': 0,
                'max_value': None,
                'include_in_trends': True,
            },
            {
                'text': 'What percentage of issues were resolved within SLA by this employee?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 1,
                'min_value': 0,
                'max_value': 100,
                'include_in_trends': True,
            },
            {
                'text': 'How reliable is the employee in maintaining system uptime and functionality?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 2,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How would you rate employee satisfaction with the IT support this person provides?',
                'qtype': Question.QType.EMOJI,
                'required': True,
                'order': 3,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How confident are you in this employee\'s ability to keep systems secure and efficient?',
                'qtype': Question.QType.RATING,
                'required': True,
                'order': 4,
                'min_value': 1,
                'max_value': 10,
                'include_in_trends': True,
            },
        ]
    
    # Operations department weekly evaluations
    elif (instance.name == 'Weekly Evaluation' and 
          instance.department.title.upper() == 'OPERATIONS'):
        default_questions = [
            {
                'text': 'How many moves were supervised or completed by this employee?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 0,
                'min_value': 0,
                'max_value': None,
                'include_in_trends': True,
            },
            {
                'text': 'What percentage of moves under this employee\'s supervision were damage-free?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 1,
                'min_value': 0,
                'max_value': 100,
                'include_in_trends': True,
            },
            {
                'text': 'How efficient is this employee\'s teamwork and leadership during moves?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 2,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How satisfied are customers with this employee\'s on-site service?',
                'qtype': Question.QType.EMOJI,
                'required': True,
                'order': 3,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How confident are you that this employee can handle future workloads effectively?',
                'qtype': Question.QType.RATING,
                'required': True,
                'order': 4,
                'min_value': 1,
                'max_value': 10,
                'include_in_trends': True,
            },
        ]
    
    # Warehouse department weekly evaluations
    elif (instance.name == 'Weekly Evaluation' and 
          instance.department.title.upper() == 'WAREHOUSE'):
        default_questions = [
            {
                'text': 'How many storage/move-in/move-out tasks did the employee handle?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 0,
                'min_value': 0,
                'max_value': None,
                'include_in_trends': True,
            },
            {
                'text': 'What percentage of items handled by this employee were damage-free?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 1,
                'min_value': 0,
                'max_value': 100,
                'include_in_trends': True,
            },
            {
                'text': 'How accurate is this employee in managing inventory records?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 2,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How would you rate this employee\'s efficiency in loading/unloading operations?',
                'qtype': Question.QType.EMOJI,
                'required': True,
                'order': 3,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How confident are you in this employee\'s ability to maintain warehouse safety and organization?',
                'qtype': Question.QType.RATING,
                'required': True,
                'order': 4,
                'min_value': 1,
                'max_value': 10,
                'include_in_trends': True,
            },
        ]
    
    # Drivers department weekly evaluations
    elif (instance.name == 'Weekly Evaluation' and 
          instance.department.title.upper() == 'DRIVERS'):
        default_questions = [
            {
                'text': 'How many moves/deliveries did the driver complete this week/month?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 0,
                'min_value': 0,
                'max_value': None,
                'include_in_trends': True,
            },
            {
                'text': 'What percentage of this driver\'s moves were completed on time?',
                'qtype': Question.QType.NUMBER,
                'required': True,
                'order': 1,
                'min_value': 0,
                'max_value': 100,
                'include_in_trends': True,
            },
            {
                'text': 'How safe and compliant was this driver in following traffic and company regulations?',
                'qtype': Question.QType.STARS,
                'required': True,
                'order': 2,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How would you rate customer satisfaction with this driver\'s professionalism and behavior?',
                'qtype': Question.QType.EMOJI,
                'required': True,
                'order': 3,
                'min_value': 1,
                'max_value': 5,
                'include_in_trends': True,
            },
            {
                'text': 'How confident are you in this driver\'s ability to handle long-distance or complex moves without issues?',
                'qtype': Question.QType.RATING,
                'required': True,
                'order': 4,
                'min_value': 1,
                'max_value': 10,
                'include_in_trends': True,
            },
        ]
    
    # If no matching evaluation type, don't create questions
    if not default_questions:
        return
    
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
            min_value=question_data.get('min_value'),
            max_value=question_data.get('max_value'),
            include_in_trends=question_data.get('include_in_trends', False),
        )
        questions_to_create.append(question)
    
    # Bulk create all questions
    Question.objects.bulk_create(questions_to_create)


# Cache Invalidation Signals
# These signals ensure that analytics cache is invalidated when evaluation data changes

@receiver(post_save, sender=DynamicEvaluation)
def invalidate_cache_on_evaluation_save(sender, instance, created, **kwargs):
    """
    Invalidate analytics cache when an employee evaluation is created or updated.
    This ensures the dashboard shows fresh data.
    """
    try:
        action = "created" if created else "updated"
        logger.info(f"DynamicEvaluation {action}: {instance.id}, invalidating analytics cache")
        
        # Invalidate cache for all users since analytics may be affected
        invalidate_analytics_cache()
        
        # Also invalidate specific user caches if we have manager/senior manager info
        if hasattr(instance, 'manager') and instance.manager:
            invalidate_user_analytics_cache(instance.manager.user.id)
            
    except Exception as e:
        logger.error(f"Error invalidating cache after DynamicEvaluation save: {e}")


@receiver(post_delete, sender=DynamicEvaluation)
def invalidate_cache_on_evaluation_delete(sender, instance, **kwargs):
    """
    Invalidate analytics cache when an employee evaluation is deleted.
    """
    try:
        logger.info(f"DynamicEvaluation deleted: {instance.id}, invalidating analytics cache")
        
        # Invalidate cache for all users since analytics counts will change
        invalidate_analytics_cache()
        
        # Also invalidate specific user caches if we have manager/senior manager info
        if hasattr(instance, 'manager') and instance.manager:
            invalidate_user_analytics_cache(instance.manager.user.id)
            
    except Exception as e:
        logger.error(f"Error invalidating cache after DynamicEvaluation delete: {e}")


@receiver(post_save, sender=DynamicManagerEvaluation)
def invalidate_cache_on_manager_evaluation_save(sender, instance, created, **kwargs):
    """
    Invalidate analytics cache when a manager evaluation is created or updated.
    """
    try:
        action = "created" if created else "updated"
        logger.info(f"DynamicManagerEvaluation {action}: {instance.id}, invalidating analytics cache")
        
        # Invalidate cache for all users since manager analytics may be affected
        invalidate_analytics_cache()
        
        # Also invalidate specific user caches for the senior manager
        if hasattr(instance, 'senior_manager') and instance.senior_manager:
            invalidate_user_analytics_cache(instance.senior_manager.user.id)
            
        # And for the manager being evaluated
        if hasattr(instance, 'manager') and instance.manager:
            invalidate_user_analytics_cache(instance.manager.user.id)
            
    except Exception as e:
        logger.error(f"Error invalidating cache after DynamicManagerEvaluation save: {e}")


@receiver(post_delete, sender=DynamicManagerEvaluation)
def invalidate_cache_on_manager_evaluation_delete(sender, instance, **kwargs):
    """
    Invalidate analytics cache when a manager evaluation is deleted.
    """
    try:
        logger.info(f"DynamicManagerEvaluation deleted: {instance.id}, invalidating analytics cache")
        
        # Invalidate cache for all users since manager analytics counts will change
        invalidate_analytics_cache()
        
        # Also invalidate specific user caches for the senior manager
        if hasattr(instance, 'senior_manager') and instance.senior_manager:
            invalidate_user_analytics_cache(instance.senior_manager.user.id)
            
        # And for the manager being evaluated
        if hasattr(instance, 'manager') and instance.manager:
            invalidate_user_analytics_cache(instance.manager.user.id)
            
    except Exception as e:
        logger.error(f"Error invalidating cache after DynamicManagerEvaluation delete: {e}")


@receiver(post_save, sender=EvalForm)
def invalidate_cache_on_evalform_change(sender, instance, created, **kwargs):
    """
    Invalidate analytics cache when evaluation forms are modified.
    This affects which evaluations are active and visible.
    """
    try:
        if not created:  # Only invalidate on updates, not creation
            logger.info(f"EvalForm updated: {instance.id}, invalidating analytics cache")
            invalidate_analytics_cache()
            
    except Exception as e:
        logger.error(f"Error invalidating cache after EvalForm save: {e}")


@receiver(post_delete, sender=EvalForm)
def invalidate_cache_on_evalform_delete(sender, instance, **kwargs):
    """
    Invalidate analytics cache when evaluation forms are deleted.
    """
    try:
        logger.info(f"EvalForm deleted: {instance.id}, invalidating analytics cache")
        invalidate_analytics_cache()
        
    except Exception as e:
        logger.error(f"Error invalidating cache after EvalForm delete: {e}")
