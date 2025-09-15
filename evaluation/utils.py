"""
Utility functions for evaluation forms to handle race conditions and concurrent access.
"""

from django.db import transaction, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import EvalForm
from firehousemovers.utils.permissions import role_checker
import logging

logger = logging.getLogger(__name__)


def activate_evalform_safely(form_obj, request, success_message=None):
    """
    Safely activate an evaluation form with proper locking and error handling.
    
    Args:
        form_obj: EvalForm instance to activate
        request: Django request object for messages
        success_message: Custom success message (optional)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if success_message is None:
        success_message = f"'{form_obj.name}' is now active for {form_obj.department.title}."
    
    try:
        with transaction.atomic():
            # Lock the form and any conflicting forms
            locked_form = EvalForm.objects.select_for_update().get(pk=form_obj.pk)
            
            # Lock any other forms in the same department with the same name
            conflicting_forms = EvalForm.objects.select_for_update().filter(
                department=locked_form.department,
                name=locked_form.name,
                is_active=True
            ).exclude(pk=locked_form.pk)
            
            # Deactivate conflicting forms
            if conflicting_forms.exists():
                conflicting_forms.update(is_active=False)
                messages.info(request, f"Deactivated {conflicting_forms.count()} conflicting form(s) of the same type.")
            
            # Activate the form
            locked_form.is_active = True
            locked_form.save(update_fields=["is_active"])
            
            messages.success(request, success_message)
            return True, success_message
            
    except IntegrityError as e:
        logger.exception(f"Integrity error while activating evaluation form '{form_obj.name}'")
        if 'uq_evalform_one_active_per_dept_per_type' in str(e):
            error_msg = f"Cannot activate '{form_obj.name}' - another form of the same type is already active for {form_obj.department.title}."
            messages.error(request, error_msg)
            return False, error_msg
        else:
            error_msg = f"Database error while activating form. Please try again."
            messages.error(request, error_msg)
            return False, error_msg
    except Exception as e:
        logger.exception(f"Unexpected error while activating evaluation form '{form_obj.name}'")
        error_msg = f"An unexpected error occurred while activating the form. Please try again."
        messages.error(request, error_msg)
        return False, error_msg


def deactivate_evalform_safely(form_obj, request, success_message=None):
    """
    Safely deactivate an evaluation form with proper locking.
    
    Args:
        form_obj: EvalForm instance to deactivate
        request: Django request object for messages
        success_message: Custom success message (optional)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if success_message is None:
        success_message = f"'{form_obj.name}' has been deactivated."
    
    try:
        with transaction.atomic():
            # Lock the form
            locked_form = EvalForm.objects.select_for_update().get(pk=form_obj.pk)
            
            # Deactivate the form
            locked_form.is_active = False
            locked_form.save(update_fields=["is_active"])
            
            messages.success(request, success_message)
            return True, success_message
            
    except Exception as e:
        logger.exception(f"Error while deactivating evaluation form '{form_obj.name}'")
        error_msg = f"An error occurred while deactivating the form. Please try again."
        messages.error(request, error_msg)
        return False, error_msg


def get_active_forms_for_department_type(department, form_name):
    """
    Get active forms for a specific department and form type.
    
    Args:
        department: Department instance
        form_name: Name of the form type
    
    Returns:
        QuerySet of active forms
    """
    return EvalForm.objects.filter(
        department=department,
        name=form_name,
        is_active=True
    )


def check_form_activation_conflicts(form_obj, department, form_name):
    """
    Check if activating a form would create conflicts.
    
    Args:
        form_obj: EvalForm instance to check
        department: Department instance
        form_name: Name of the form type
    
    Returns:
        tuple: (has_conflicts: bool, conflicting_forms: QuerySet)
    """
    conflicting_forms = EvalForm.objects.filter(
        department=department,
        name=form_name,
        is_active=True
    ).exclude(pk=form_obj.pk)
    
    return conflicting_forms.exists(), conflicting_forms


# ============================================================================
# Permission Checking Utilities
# ============================================================================

def get_role_checker(user):
    """
    Get role checker for a user with consistent error handling.
    
    Args:
        user: Django User instance
    
    Returns:
        RoleChecker instance
    """
    return role_checker(user)


def check_department_permission(user, department, action_description="perform this action"):
    """
    Check if user can manage the specified department.
    
    Args:
        user: Django User instance
        department: Department instance
        action_description: Description of the action being attempted
    
    Returns:
        tuple: (has_permission: bool, error_message: str or None)
    """
    from .decorators import _can_manage_department
    
    if not _can_manage_department(user, department):
        error_msg = f"You don't have permission to {action_description} for {department.title}."
        return False, error_msg
    
    return True, None


def handle_department_permission_error(request, error_message, redirect_url="evaluation:evalform_list"):
    """
    Handle department permission errors consistently.
    
    Args:
        request: Django request object
        error_message: Error message to display
        redirect_url: URL to redirect to
    
    Returns:
        HttpResponse: Redirect response
    """
    messages.error(request, error_message)
    return redirect(redirect_url)


# ============================================================================
# Form Activation/Deactivation Utilities
# ============================================================================

def deactivate_conflicting_forms(department, form_name, exclude_form=None):
    """
    Deactivate any conflicting forms for the same department and type.
    
    WARNING: This function uses select_for_update() and MUST be called within
    a transaction.atomic() block to avoid database errors.
    
    Args:
        department: Department instance
        form_name: Name of the form type
        exclude_form: Form to exclude from deactivation (optional)
    
    Returns:
        int: Number of forms deactivated
        
    Raises:
        RuntimeError: If called outside of a transaction
    """
    from django.db import transaction
    
    # Ensure we're in a transaction
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError(
            "deactivate_conflicting_forms() must be called within a transaction.atomic() block"
        )
    
    queryset = EvalForm.objects.select_for_update().filter(
        department=department,
        name=form_name,
        is_active=True
    )
    
    if exclude_form:
        queryset = queryset.exclude(pk=exclude_form.pk)
    
    if queryset.exists():
        count = queryset.count()
        queryset.update(is_active=False)
        return count
    
    return 0


def save_form_with_activation_check(form_obj, request, success_message=None):
    """
    Save a form with proper activation conflict checking.
    
    Args:
        form_obj: EvalForm instance to save
        request: Django request object for messages
        success_message: Custom success message (optional)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if success_message is None:
        success_message = "Form saved successfully."
    
    try:
        # If the form is being activated, check for conflicts
        if form_obj.is_active:
            try:
                form_obj.save(update_fields=["is_active"])
                messages.success(request, success_message)
                return True, success_message
            except IntegrityError as e:
                if 'uq_evalform_one_active_per_dept_per_type' in str(e):
                    # Another form was activated concurrently
                    form_obj.is_active = False
                    form_obj.save(update_fields=["is_active"])
                    error_msg = f"Form saved but not activated - another form of the same type is already active for {form_obj.department.title}."
                    messages.warning(request, error_msg)
                    return True, error_msg
                else:
                    raise
        else:
            form_obj.save()
            messages.success(request, success_message)
            return True, success_message
            
    except IntegrityError as e:
        logger.exception(f"Integrity error while saving evaluation form '{form_obj.name}'")
        if 'uq_evalform_one_active_per_dept_per_type' in str(e):
            error_msg = f"Cannot activate form - another form of the same type is already active for {form_obj.department.title}."
            messages.error(request, error_msg)
            return False, error_msg
        else:
            error_msg = f"Database error while saving form. Please try again."
            messages.error(request, error_msg)
            return False, error_msg
    except Exception as e:
        logger.exception(f"Error while saving evaluation form '{form_obj.name}'")
        error_msg = f"An error occurred while saving the form. Please try again."
        messages.error(request, error_msg)
        return False, error_msg


def process_form_creation_with_conflicts(form, request):
    """
    Process form creation with proper conflict resolution.
    
    Args:
        form: Validated EvalFormForm instance
        request: Django request object
    
    Returns:
        tuple: (success: bool, form_obj: EvalForm or None, error_response: HttpResponse or None)
    """
    department = form.cleaned_data["department"]
    
    try:
        with transaction.atomic():
            # Deactivate any existing conflicting forms
            deactivated_count = deactivate_conflicting_forms(
                department, 
                form.cleaned_data["name"]
            )
            
            if deactivated_count > 0:
                messages.info(request, f"Deactivated {deactivated_count} conflicting form(s) of the same type.")
            
            # Save the new form
            obj = form.save()
            
            # Handle activation conflicts if the form is active
            if obj.is_active:
                success, msg = save_form_with_activation_check(obj, request, "Form created and activated.")
                if not success:
                    return False, obj, render(request, "evaluation/forms/create.html", {"form": form})
            else:
                messages.success(request, "Form created.")
            
            return True, obj, None
            
    except IntegrityError as e:
        logger.exception("Integrity error while creating evaluation form")
        # Handle database constraint violations
        if 'uq_evalform_one_active_per_dept_per_type' in str(e):
            from .messages import EVALUATION_ALREADY_EXISTS
            messages.error(request, EVALUATION_ALREADY_EXISTS)
        else:
            messages.error(request, "An error occurred while saving the form. Please try again.")
        return False, None, render(request, "evaluation/forms/create.html", {"form": form})
    except Exception as e:
        logger.exception("Unexpected error while creating evaluation form")
        messages.error(request, "An unexpected error occurred while creating the form. Please try again.")
        return False, None, render(request, "evaluation/forms/create.html", {"form": form})


def process_form_edit_with_conflicts(form, form_obj, request):
    """
    Process form editing with proper conflict resolution.
    
    Args:
        form: Validated EvalFormForm instance
        form_obj: Existing EvalForm instance
        request: Django request object
    
    Returns:
        tuple: (success: bool, error_response: HttpResponse or None)
    """
    department = form.cleaned_data["department"]
    
    try:
        with transaction.atomic():
            # Lock the current form
            current_obj = EvalForm.objects.select_for_update().get(pk=form_obj.pk)
            
            # If this form is currently active or being activated, handle conflicts
            if current_obj.is_active or form.cleaned_data.get("is_active", False):
                deactivated_count = deactivate_conflicting_forms(
                    department,
                    form.cleaned_data["name"],
                    exclude_form=current_obj
                )
                
                if deactivated_count > 0:
                    messages.info(request, f"Deactivated {deactivated_count} conflicting form(s) of the same type.")
            
            # Save the form
            form.save()
            messages.success(request, "Form updated.")
            return True, None
            
    except IntegrityError as e:
        logger.exception("Integrity error while editing evaluation form")
        # Handle database constraint violations
        if 'uq_evalform_one_active_per_dept_per_type' in str(e):
            from .messages import EVALUATION_ALREADY_EXISTS
            messages.error(request, EVALUATION_ALREADY_EXISTS)
        else:
            messages.error(request, "An error occurred while saving the form. Please try again.")
        return False, render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": form_obj})
    except Exception as e:
        logger.exception("Unexpected error while editing evaluation form")
        messages.error(request, "An unexpected error occurred while updating the form. Please try again.")
        return False, render(request, "evaluation/forms/edit.html", {"form": form, "form_obj": form_obj})
