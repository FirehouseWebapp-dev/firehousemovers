"""
Decorators for evaluation views to centralize permission checking logic.
"""

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from firehousemovers.utils.permissions import role_checker
import logging

logger = logging.getLogger(__name__)


def _is_ajax_request(request):
    """Check if the request is an AJAX request."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'


def _can_manage(user):
    """Check if user can manage evaluation forms globally (superusers and senior management only)."""
    if not user.is_authenticated:
        return False
    checker = role_checker(user)
    return checker.is_admin_or_senior()


def _can_manage_department(user, department):
    """Check if user can manage evaluation forms for a specific department."""
    if not user.is_authenticated:
        return False
    checker = role_checker(user)
    
    # Superusers and global admins can manage any department
    if checker.is_admin_or_senior():
        return True
    
    # Department managers can only manage their own department
    if checker.is_manager() and checker.user_profile.managed_department == department:
        return True
    
    return False


def require_department_management(view_func):
    """
    Decorator that checks if user can manage the department of an object.
    
    Expects the view to have either:
    1. A 'pk' parameter for an EvalForm object
    2. A 'form_id' parameter for an EvalForm object  
    3. A 'question_id' parameter for a Question object
    
    Automatically redirects to evalform_list with error message if permission denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import EvalForm, Question
        
        # Get the object to check permissions for
        obj = None
        department = None
        
        # Try to get the object based on URL parameters
        if 'pk' in kwargs:
            try:
                obj = EvalForm.objects.select_related("department").get(pk=kwargs['pk'])
                department = obj.department
            except EvalForm.DoesNotExist:
                messages.error(request, "Evaluation form not found.")
                return redirect("evaluation:evalform_list")
        
        elif 'form_id' in kwargs:
            try:
                obj = EvalForm.objects.select_related("department").get(pk=kwargs['form_id'])
                department = obj.department
            except EvalForm.DoesNotExist:
                messages.error(request, "Evaluation form not found.")
                return redirect("evaluation:evalform_list")
        
        elif 'question_id' in kwargs:
            try:
                obj = Question.objects.select_related("form__department").get(pk=kwargs['question_id'])
                department = obj.form.department
            except Question.DoesNotExist:
                messages.error(request, "Question not found.")
                return redirect("evaluation:evalform_list")
        
        # If no object found, this decorator can't be used
        if not department:
            messages.error(request, "Unable to determine department for permission check.")
            return redirect("evaluation:evalform_list")
        
        # Check department management permission
        if not _can_manage_department(request.user, department):
            if _is_ajax_request(request):
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            messages.error(request, "You don't have permission to manage this evaluation form.")
            return redirect("evaluation:evalform_list")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_department_management_for_form(view_func):
    """
    Decorator that checks department management permission for form-based operations.
    
    For POST requests, checks the department in the form data.
    For GET requests, checks if user has any department management permissions.
    
    Automatically redirects to evalform_list with error message if permission denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import EvalForm
        from authentication.models import Department
        
        if request.method == "POST":
            # For POST requests, check the department in the form data
            department_id = request.POST.get('department')
            if not department_id:
                messages.error(request, "Department not specified.")
                return redirect("evaluation:evalform_list")
            
            try:
                department = Department.objects.get(pk=department_id)
            except Department.DoesNotExist:
                messages.error(request, "Invalid department specified.")
                return redirect("evaluation:evalform_list")
            
            if not _can_manage_department(request.user, department):
                if _is_ajax_request(request):
                    return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
                messages.error(request, "You don't have permission to create forms for this department.")
                return redirect("evaluation:evalform_list")
        
        else:
            # For GET requests, check if user has any department management permissions
            checker = role_checker(request.user)
            if not checker.is_management():
                if _is_ajax_request(request):
                    return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
                messages.error(request, "You don't have permission to access this page.")
                return redirect("evaluation:evalform_list")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def ajax_require_department_management(view_func):
    """
    AJAX version of require_department_management decorator.
    
    Returns JSON error response instead of redirect if permission denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import EvalForm, Question
        
        # Get the object to check permissions for
        obj = None
        department = None
        
        # Try to get the object based on URL parameters
        if 'pk' in kwargs:
            try:
                obj = EvalForm.objects.select_related("department").get(pk=kwargs['pk'])
                department = obj.department
            except EvalForm.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Evaluation form not found'}, status=404)
        
        elif 'form_id' in kwargs:
            try:
                obj = EvalForm.objects.select_related("department").get(pk=kwargs['form_id'])
                department = obj.department
            except EvalForm.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Evaluation form not found'}, status=404)
        
        elif 'question_id' in kwargs:
            try:
                obj = Question.objects.select_related("form__department").get(pk=kwargs['question_id'])
                department = obj.form.department
            except Question.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Question not found'}, status=404)
        
        # If no object found, this decorator can't be used
        if not department:
            return JsonResponse({'success': False, 'error': 'Unable to determine department for permission check'}, status=400)
        
        # Check department management permission
        if not _can_manage_department(request.user, department):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_global_management(view_func):
    """
    Decorator that checks if user can manage evaluation forms globally.
    
    Only allows superusers and senior management.
    Automatically redirects to evalform_list with error message if permission denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _can_manage(request.user):
            if _is_ajax_request(request):
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            messages.error(request, "You don't have permission to perform this action.")
            return redirect("evaluation:evalform_list")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_manager_access(view_func):
    """
    Decorator that checks if user has manager access for dynamic evaluations.
    
    Only allows managers and above.
    Automatically redirects to main dashboard if permission denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        
        if not checker.is_manager():
            if _is_ajax_request(request):
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            return redirect("evaluation:dashboard")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_senior_management_access(view_func):
    """
    Decorator that checks if user has senior management access.
    
    Only allows admin or senior management.
    Automatically redirects to main dashboard if permission denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        checker = role_checker(request.user)
        
        if not checker.is_admin_or_senior():
            if _is_ajax_request(request):
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            return redirect("evaluation:dashboard")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_evaluation_access(view_func):
    """
    Decorator that checks if user can access a specific evaluation.
    
    Expects evaluation_id parameter and checks if user is either:
    1. The manager assigned to the evaluation
    2. The employee being evaluated
    3. Admin/senior management
    
    Automatically redirects to appropriate dashboard if permission denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import DynamicEvaluation, DynamicManagerEvaluation
        
        evaluation_id = kwargs.get('evaluation_id')
        if not evaluation_id:
            return redirect("evaluation:dashboard")
        
        checker = role_checker(request.user)
        
        # Try dynamic evaluation first
        try:
            evaluation = DynamicEvaluation.objects.select_related('manager', 'employee').get(pk=evaluation_id)
            
            # Allow access if user is the manager OR the employee being evaluated OR admin/senior
            if (evaluation.manager == checker.user_profile or 
                evaluation.employee == checker.user_profile or 
                checker.is_admin_or_senior()):
                return view_func(request, *args, **kwargs)
            
        except DynamicEvaluation.DoesNotExist:
            pass
        
        # Try manager evaluation
        try:
            evaluation = DynamicManagerEvaluation.objects.select_related('manager', 'senior_manager').get(pk=evaluation_id)
            
            # Allow access if user is the senior manager OR the manager being evaluated OR admin
            if (evaluation.senior_manager == checker.user_profile or 
                evaluation.manager == checker.user_profile or 
                checker.is_admin_or_senior()):
                return view_func(request, *args, **kwargs)
            
        except DynamicManagerEvaluation.DoesNotExist:
            pass
        
        # No access
        if _is_ajax_request(request):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        return redirect("evaluation:dashboard")
    
    return wrapper
