from django.shortcuts import redirect
from datetime import date
from evaluation.models import ReviewCycle, ManagerEvaluation
from django.contrib import messages
from django.shortcuts import redirect

class SeniorEvaluationLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow unauthenticated users (login/logout still needed)
        if not request.user.is_authenticated:
            return self.get_response(request)

        profile = getattr(request.user, "userprofile", None)
        if not profile or not profile.is_senior_management:  
            # Only lock seniors/admins
            return self.get_response(request)

        today = date.today()

        # Find all cycles that are closed (evaluation time ended)
        expired_cycles = ReviewCycle.objects.filter(
            is_open=True,
            period_end__lt=today,
        )

        for cycle in expired_cycles:
            pending = ManagerEvaluation.objects.filter(
                reviewer=profile,
                cycle=cycle,
                status="pending",
            )
            if pending.exists():
                # If not evaluation-related → redirect to pending reviews
                if (
                    not request.path.startswith("/evaluation/reviews/pending") 
                    and not request.path.startswith("/evaluation/reviews/evaluate")
                    ):
                        messages.warning (
                            request,
                            "You have pending evaluations to complete so you cannot access other pages."
                        )
                        return redirect("evaluation:senior_pending_reviews")

                break  # No need to check other cycles

        return self.get_response(request)
