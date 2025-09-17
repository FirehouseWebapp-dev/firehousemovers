from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EvalForm, Question, QuestionChoice, DynamicEvaluation, DynamicManagerEvaluation
from .cache_utils import invalidate_analytics_cache, invalidate_user_analytics_cache
import logging

logger = logging.getLogger(__name__)


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
            'qtype': Question.QType.LONG,
            'required': True,
            'order': 0,
        },
        {
            'text': 'Set Objectives',
            'qtype': Question.QType.LONG,
            'required': True,
            'order': 1,
        },
        {
            'text': 'Strengths',
            'qtype': Question.QType.LONG,
            'required': True,
            'order': 2,
        },
        {
            'text': 'Areas for Improvement',
            'qtype': Question.QType.LONG,
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
