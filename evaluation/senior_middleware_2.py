from django.shortcuts import redirect, render
from django.utils.timezone import now
from evaluation.models_dynamic import DynamicManagerEvaluation
from django.contrib import messages
from firehousemovers.utils.permissions import role_checker

class OverdueManagerEvaluationLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If they're not logged in or not a senior manager, do nothing
        if not request.user.is_authenticated:
            return self.get_response(request)

        checker = role_checker(request.user)
        if not checker.is_admin_or_senior():
            return self.get_response(request)

        today = now().date()

        # Check for overdue manager evaluations - force fresh query
        overdue_manager_evaluations = DynamicManagerEvaluation.objects.filter(
            senior_manager=checker.user_profile,
            status="pending",
            period_end__lt=today,
        ).select_related()

        if overdue_manager_evaluations.exists():
            # Block access to everything except manager evaluation pages
            path = request.path
            allowed_paths = [
                "/evaluation/manager-evaluations/",
                "/evaluation/manager-evaluations/cards/",
                "/evaluation/manager-evaluations/evaluate/",
                "/evaluation/manager-evaluations/view/",
                "/evaluation/manager-evaluations/my/",
                "/evaluation/manager-evaluations/pending/",
                "/logout/",  # Allow logout
                "/login/",   # Allow login
            ]
            
            # Check if current path is allowed
            is_allowed = any(path.startswith(allowed_path) for allowed_path in allowed_paths)
            
            if not is_allowed:
                overdue_count = overdue_manager_evaluations.count()
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"You have {overdue_count} pending evaluation(s) to complete so you cannot access other pages.",
                    extra_tags="overdue-critical"
                )
                return redirect("/evaluation/manager-evaluations/")

        return self.get_response(request)
