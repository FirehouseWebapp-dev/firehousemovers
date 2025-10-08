from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import EvalForm, Question, QuestionChoice, DynamicEvaluation, DynamicManagerEvaluation
from .cache_utils import invalidate_analytics_cache, invalidate_user_analytics_cache
from authentication.models import Department
import logging

logger = logging.getLogger(__name__)

# Define default questions config centrally using slugs for robustness
# 
# IMPORTANT: Department slugs must match these exact values to generate correct questions:
#   - "sales"        → Sales department questions
#   - "accounting"   → Accounting department questions  
#   - "claims"       → Claims department questions
#   - "it"           → IT department questions
#   - "operations"   → Operations department questions
#   - "warehouse"    → Warehouse department questions
#   - "drivers"      → Drivers department questions
#
# When creating/editing departments, use these exact slug values.
DEFAULT_QUESTIONS = {
    # Manager Evaluations (using form slugs)
    ("monthly-evaluation", None): [
        {"text": "Goals Achieved", "qtype": Question.QType.LONG, "required": True, "order": 0, "include_in_trends": False},
        {"text": "Set Objectives", "qtype": Question.QType.LONG, "required": True, "order": 1, "include_in_trends": False},
        {"text": "Strengths", "qtype": Question.QType.LONG, "required": True, "order": 2, "include_in_trends": False},
        {"text": "Areas for Improvement", "qtype": Question.QType.LONG, "required": True, "order": 3, "include_in_trends": False},
        {"text": "Overall Rating", "qtype": Question.QType.STARS, "required": True, "order": 4, "min_value": 1, "max_value": 5, "include_in_trends": True},
    ],
    ("quarterly-evaluation", None): [
        {"text": "Goals Achieved", "qtype": Question.QType.LONG, "required": True, "order": 0, "include_in_trends": False},
        {"text": "Set Objectives", "qtype": Question.QType.LONG, "required": True, "order": 1, "include_in_trends": False},
        {"text": "Strengths", "qtype": Question.QType.LONG, "required": True, "order": 2, "include_in_trends": False},
        {"text": "Areas for Improvement", "qtype": Question.QType.LONG, "required": True, "order": 3, "include_in_trends": False},
        {"text": "Overall Rating", "qtype": Question.QType.STARS, "required": True, "order": 4, "min_value": 1, "max_value": 5, "include_in_trends": True},
    ],
    ("annual-evaluation", None): [
        {"text": "Goals Achieved", "qtype": Question.QType.LONG, "required": True, "order": 0, "include_in_trends": False},
        {"text": "Set Objectives", "qtype": Question.QType.LONG, "required": True, "order": 1, "include_in_trends": False},
        {"text": "Strengths", "qtype": Question.QType.LONG, "required": True, "order": 2, "include_in_trends": False},
        {"text": "Areas for Improvement", "qtype": Question.QType.LONG, "required": True, "order": 3, "include_in_trends": False},
        {"text": "Overall Rating", "qtype": Question.QType.STARS, "required": True, "order": 4, "min_value": 1, "max_value": 5, "include_in_trends": True},
    ],

    # Department Weekly Evaluations (using department slugs)
    ("weekly-evaluation", "sales"): [
        {"text": "How many new leads did the employee generate this week?", "qtype": Question.QType.NUMBER, "required": True, "order": 0, "min_value": 0, "include_in_trends": True},
        {"text": "How effectively did the employee convert leads into bookings?", "qtype": Question.QType.STARS, "required": True, "order": 1, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How satisfied are customers after interacting with this employee?", "qtype": Question.QType.EMOJI, "required": True, "order": 2, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How well does the employee meet or exceed sales targets?", "qtype": Question.QType.STARS, "required": True, "order": 3, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How confident are you in this employee's ability to close future deals?", "qtype": Question.QType.RATING, "required": True, "order": 4, "min_value": 1, "max_value": 10, "include_in_trends": True},
    ],
    ("weekly-evaluation", "accounting"): [
        {"text": "How many invoices did the employee process this week?", "qtype": Question.QType.NUMBER, "required": True, "order": 0, "min_value": 0, "include_in_trends": True},
        {"text": "What percentage of the employee's work was error-free?", "qtype": Question.QType.NUMBER, "required": True, "order": 1, "min_value": 0, "max_value": 100, "include_in_trends": True},
        {"text": "How accurate and detail-oriented is this employee?", "qtype": Question.QType.STARS, "required": True, "order": 2, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How timely is the employee in completing accounting tasks?", "qtype": Question.QType.EMOJI, "required": True, "order": 3, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How confident are you in this employee's ability to meet financial deadlines?", "qtype": Question.QType.RATING, "required": True, "order": 4, "min_value": 1, "max_value": 10, "include_in_trends": True},
    ],
    ("weekly-evaluation", "claims"): [
        {"text": "How many claims did the employee process this week?", "qtype": Question.QType.NUMBER, "required": True, "order": 0, "min_value": 0, "include_in_trends": True},
        {"text": "What percentage of the employee's claims were resolved within the standard timeframe?", "qtype": Question.QType.NUMBER, "required": True, "order": 1, "min_value": 0, "max_value": 100, "include_in_trends": True},
        {"text": "How well does this employee document and handle claim cases?", "qtype": Question.QType.STARS, "required": True, "order": 2, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How would you rate this employee's communication with customers during claims?", "qtype": Question.QType.EMOJI, "required": True, "order": 3, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How confident are you that this employee handles claims fairly and efficiently?", "qtype": Question.QType.RATING, "required": True, "order": 4, "min_value": 1, "max_value": 10, "include_in_trends": True},
    ],
    ("weekly-evaluation", "it"): [
        {"text": "How many IT support requests did the employee resolve this week?", "qtype": Question.QType.NUMBER, "required": True, "order": 0, "min_value": 0, "include_in_trends": True},
        {"text": "What percentage of issues were resolved within SLA by this employee?", "qtype": Question.QType.NUMBER, "required": True, "order": 1, "min_value": 0, "max_value": 100, "include_in_trends": True},
        {"text": "How reliable is the employee in maintaining system uptime and functionality?", "qtype": Question.QType.STARS, "required": True, "order": 2, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How would you rate employee satisfaction with the IT support this person provides?", "qtype": Question.QType.EMOJI, "required": True, "order": 3, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How confident are you in this employee's ability to keep systems secure and efficient?", "qtype": Question.QType.RATING, "required": True, "order": 4, "min_value": 1, "max_value": 10, "include_in_trends": True},
    ],
    ("weekly-evaluation", "operations"): [
        {"text": "How many moves were supervised or completed by this employee?", "qtype": Question.QType.NUMBER, "required": True, "order": 0, "min_value": 0, "include_in_trends": True},
        {"text": "What percentage of moves under this employee's supervision were damage-free?", "qtype": Question.QType.NUMBER, "required": True, "order": 1, "min_value": 0, "max_value": 100, "include_in_trends": True},
        {"text": "How efficient is this employee's teamwork and leadership during moves?", "qtype": Question.QType.STARS, "required": True, "order": 2, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How satisfied are customers with this employee's on-site service?", "qtype": Question.QType.EMOJI, "required": True, "order": 3, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How confident are you that this employee can handle future workloads effectively?", "qtype": Question.QType.RATING, "required": True, "order": 4, "min_value": 1, "max_value": 10, "include_in_trends": True},
    ],
    ("weekly-evaluation", "warehouse"): [
        {"text": "How many storage/move-in/move-out tasks did the employee handle?", "qtype": Question.QType.NUMBER, "required": True, "order": 0, "min_value": 0, "include_in_trends": True},
        {"text": "What percentage of items handled by this employee were damage-free?", "qtype": Question.QType.NUMBER, "required": True, "order": 1, "min_value": 0, "max_value": 100, "include_in_trends": True},
        {"text": "How accurate is this employee in managing inventory records?", "qtype": Question.QType.STARS, "required": True, "order": 2, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How would you rate this employee's efficiency in loading/unloading operations?", "qtype": Question.QType.EMOJI, "required": True, "order": 3, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How confident are you in this employee's ability to maintain warehouse safety and organization?", "qtype": Question.QType.RATING, "required": True, "order": 4, "min_value": 1, "max_value": 10, "include_in_trends": True},
    ],
    ("weekly-evaluation", "drivers"): [
        {"text": "How many moves/deliveries did the driver complete this week/month?", "qtype": Question.QType.NUMBER, "required": True, "order": 0, "min_value": 0, "include_in_trends": True},
        {"text": "What percentage of this driver's moves were completed on time?", "qtype": Question.QType.NUMBER, "required": True, "order": 1, "min_value": 0, "max_value": 100, "include_in_trends": True},
        {"text": "How safe and compliant was this driver in following traffic and company regulations?", "qtype": Question.QType.STARS, "required": True, "order": 2, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How would you rate customer satisfaction with this driver's professionalism and behavior?", "qtype": Question.QType.EMOJI, "required": True, "order": 3, "min_value": 1, "max_value": 5, "include_in_trends": True},
        {"text": "How confident are you in this driver's ability to handle long-distance or complex moves without issues?", "qtype": Question.QType.RATING, "required": True, "order": 4, "min_value": 1, "max_value": 10, "include_in_trends": True},
    ],
}


def invalidate_cache_for_instance(instance, action="updated"):
    """
    Helper function to invalidate analytics cache for evaluation-related changes.
    """
    logger.info(f"{instance.__class__.__name__} {action}: {instance.id}, invalidating analytics cache")
    invalidate_analytics_cache()

    # Invalidate related user caches if available
    for attr in ["manager", "senior_manager"]:
        if hasattr(instance, attr):
            obj = getattr(instance, attr)
            if obj and hasattr(obj, "user"):
                invalidate_user_analytics_cache(obj.user.id)




@receiver(post_save, sender=EvalForm)
def create_default_questions_for_evaluations(sender, instance, created, **kwargs):
    """
    Automatically create default questions for evaluation forms.
    """
    if not created or instance.questions.exists():
        return
    
    # Auto-populate slug if it's empty
    if not instance.slug:
        from django.utils.text import slugify
        instance.slug = slugify(instance.name)
        instance.save(update_fields=['slug'])
    
    # Use slugs for robust matching
    form_slug = instance.slug
    dept_slug = instance.department.slug if instance.department and instance.department.slug else None
    
    key = (form_slug, dept_slug)

    # Try department-specific or manager-type defaults
    default_questions = DEFAULT_QUESTIONS.get(key) or DEFAULT_QUESTIONS.get((form_slug, None))
    if not default_questions:
        return

    with transaction.atomic():
        Question.objects.bulk_create([
            Question(
                form=instance,
                text=q["text"],
                help_text=q.get("help_text", ""),
                qtype=q["qtype"],
                required=q["required"],
                order=q["order"],
                min_value=q.get("min_value"),
                max_value=q.get("max_value"),
                include_in_trends=q.get("include_in_trends", False),
            )
            for q in default_questions
        ])


# Cache Invalidation Signals
@receiver(post_save, sender=DynamicEvaluation)
def on_dynamic_evaluation_save(sender, instance, created, **kwargs):
    invalidate_cache_for_instance(instance, "created" if created else "updated")


@receiver(post_delete, sender=DynamicEvaluation)
def on_dynamic_evaluation_delete(sender, instance, **kwargs):
    invalidate_cache_for_instance(instance, "deleted")


@receiver(post_save, sender=DynamicManagerEvaluation)
def on_manager_evaluation_save(sender, instance, created, **kwargs):
    invalidate_cache_for_instance(instance, "created" if created else "updated")


@receiver(post_delete, sender=DynamicManagerEvaluation)
def on_manager_evaluation_delete(sender, instance, **kwargs):
    invalidate_cache_for_instance(instance, "deleted")


@receiver(post_save, sender=EvalForm)
def on_evalform_save(sender, instance, created, **kwargs):
    if not created:  # only updates
        invalidate_cache_for_instance(instance, "updated")


@receiver(post_delete, sender=EvalForm)
def on_evalform_delete(sender, instance, **kwargs):
    invalidate_cache_for_instance(instance, "deleted")