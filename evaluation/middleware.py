from django.shortcuts import redirect
from django.utils.timezone import now
from datetime import timedelta
from evaluation.models import Evaluation

class EvaluationLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If they're not logged in or not a manager, do nothing
        if not request.user.is_authenticated:
            return self.get_response(request)

        profile = getattr(request.user, "userprofile", None)
        if not profile or profile.role != "manager":
            return self.get_response(request)

        today = now().date()
        weekday = today.weekday()

        # Last week's Mon → Sun
        last_monday = today - timedelta(days=weekday + 7)
        last_sunday = last_monday + timedelta(days=6)

        # Any still-pending evals from last week?
        pending_qs = Evaluation.objects.filter(
            manager=profile,
            week_start=last_monday,
            week_end=last_sunday,
            status="pending",
        )

        if pending_qs.exists():
            # Allow the user to see only:
            #  • pending list  (/evaluation/pending/)
            #  • the evaluate form (/evaluation/evaluate/<id>/)
            #  • plus anything else you might need (e.g. logout, static files...)
            path = request.path
            if (
                not path.startswith("/evaluation/pending")
                and not path.startswith("/evaluation/evaluate")
            ):
                return redirect("evaluation:pending")

        return self.get_response(request)
