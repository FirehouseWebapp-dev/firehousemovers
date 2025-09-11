from django.shortcuts import redirect
from django.utils.timezone import now
from evaluation.models_dynamic import DynamicEvaluation
from django.contrib import messages
from firehousemovers.utils.permissions import role_checker

class OverdueEvaluationLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If they're not logged in or not a manager, do nothing
        if not request.user.is_authenticated:
            return self.get_response(request)

        checker = role_checker(request.user)
        if not checker.is_manager():
            return self.get_response(request)

        today = now().date()

        # Check for overdue dynamic evaluations
        overdue_dynamic_qs = DynamicEvaluation.objects.filter(
            manager=checker.user_profile,
            status="pending",
            week_end__lt=today,
        )

        if overdue_dynamic_qs.exists():
            # Block access to everything except overdue evaluations
            path = request.path
            if (
                not path.startswith("/evaluation/pending-v2")
                and not path.startswith("/evaluation/evaluate-dynamic")
                and not path.startswith("/evaluation/dynamic-evaluation")
            ):
                messages.error(
                    request,
                    f"You have {overdue_dynamic_qs.count()} overdue evaluation(s) that must be completed before accessing other pages."
                )
                return redirect("evaluation:pending_v2")

        return self.get_response(request)