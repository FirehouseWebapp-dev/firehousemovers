/**
 * Submit button control for goal forms
 * Provides real-time validation feedback and disables submit when errors exist
 * All validation logic remains in Django backend - this only provides UI feedback
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Validation functions that match Django backend validators exactly
    function validateTitle(value) {
        if (!value) return { isValid: false, message: 'Goal title is required.' };
        
        const trimmed = value.trim();
        if (trimmed.length === 0) return { isValid: false, message: 'Goal title is required.' };
        if (trimmed.length < 3) return { isValid: false, message: 'Goal title must be at least 3 characters long.' };
        if (trimmed.length > 200) return { isValid: false, message: 'Goal title cannot exceed 200 characters.' };
        
        return { isValid: true, message: '' };
    }
    
    function validateDescription(value) {
        if (!value) return { isValid: false, message: 'Goal description is required.' };
        
        const trimmed = value.trim();
        if (trimmed.length === 0) return { isValid: false, message: 'Goal description is required.' };
        if (trimmed.length < 10) return { isValid: false, message: 'Goal description must be at least 10 characters long.' };
        if (trimmed.length > 1000) return { isValid: false, message: 'Goal description cannot exceed 1000 characters.' };
        
        return { isValid: true, message: '' };
    }
    
    // Show/hide validation messages
    function showValidationMessage(field, message) {
        const container = field.closest('div');
        let messageElement = container.querySelector('.js-validation-message');
        
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.className = 'js-validation-message text-sm text-red-400 mt-1';
            container.appendChild(messageElement);
        }
        
        if (message) {
            messageElement.textContent = message;
            messageElement.style.display = 'block';
        } else {
            messageElement.style.display = 'none';
        }
    }
    
    // Validate form and control submit button
    function validateFormAndControlSubmit(form) {
        let hasErrors = false;
        
        // Check title fields
        const titleInputs = form.querySelectorAll('input[name*="title"]');
        titleInputs.forEach(input => {
            if (input.hasAttribute('required') || input.value.trim()) {
                const validation = validateTitle(input.value);
                showValidationMessage(input, validation.isValid ? '' : validation.message);
                if (!validation.isValid) hasErrors = true;
            }
        });
        
        // Check description fields
        const descriptionInputs = form.querySelectorAll('textarea[name*="description"]');
        descriptionInputs.forEach(textarea => {
            if (textarea.hasAttribute('required') || textarea.value.trim()) {
                const validation = validateDescription(textarea.value);
                showValidationMessage(textarea, validation.isValid ? '' : validation.message);
                if (!validation.isValid) hasErrors = true;
            }
        });
        
        // Control submit buttons
        const submitButtons = form.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            if (hasErrors) {
                button.disabled = true;
                button.classList.add('opacity-50', 'cursor-not-allowed');
                button.classList.remove('hover:bg-red-700');
            } else {
                button.disabled = false;
                button.classList.remove('opacity-50', 'cursor-not-allowed');
                button.classList.add('hover:bg-red-700');
            }
        });
        
        return !hasErrors;
    }
    
    // Add validation to a form
    function addSubmitControlToForm(form) {
        const inputs = form.querySelectorAll('input[name*="title"], textarea[name*="description"]');
        
        inputs.forEach(input => {
            ['input', 'blur', 'keyup'].forEach(eventType => {
                input.addEventListener(eventType, () => {
                    setTimeout(() => validateFormAndControlSubmit(form), 50);
                });
            });
        });
        
        // Prevent submission if validation fails (safety net)
        form.addEventListener('submit', function(event) {
            if (!validateFormAndControlSubmit(form)) {
                event.preventDefault();
                event.stopPropagation();
                
                // Scroll to first error
                const firstError = form.querySelector('.js-validation-message[style*="block"]');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                return false;
            }
        });
        
        // Initial validation
        validateFormAndControlSubmit(form);
    }
    
    // Initialize for existing forms
    function initializeForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const hasGoalFields = form.querySelector('input[name*="title"], textarea[name*="description"]');
            if (hasGoalFields) {
                addSubmitControlToForm(form);
            }
        });
    }
    
    // Initialize
    initializeForms();
    
    // Watch for dynamically added forms
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // Check for new forms
                    const forms = node.querySelectorAll ? node.querySelectorAll('form') : [];
                    forms.forEach(form => {
                        const hasGoalFields = form.querySelector('input[name*="title"], textarea[name*="description"]');
                        if (hasGoalFields) {
                            addSubmitControlToForm(form);
                        }
                    });
                    
                    // Check for new form cards in formsets
                    if (node.classList && node.classList.contains('goal-form-card')) {
                        const parentForm = node.closest('form');
                        if (parentForm) {
                            addSubmitControlToForm(parentForm);
                        }
                    }
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
