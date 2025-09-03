/**
 * Frontend validation for goal description fields
 * Shows real-time validation messages for character count requirements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to validate description and show appropriate message
    function validateDescription(textarea) {
        const container = textarea.closest('div');
        const messageElement = container.querySelector('.description-validation-message');
        
        if (!messageElement) return;
        
        const value = textarea.value.trim();
        const length = value.length;
        
        // Clear previous message
        messageElement.style.display = 'none';
        messageElement.textContent = '';
        
        // Show validation messages
        if (length > 0 && length < 10) {
            messageElement.textContent = 'Goal description must be at least 10 characters long.';
            messageElement.style.display = 'block';
        } else if (length > 1000) {
            messageElement.textContent = 'Goal description cannot exceed 1000 characters.';
            messageElement.style.display = 'block';
        }
    }
    
    // Function to add validation to a textarea
    function addValidationToTextarea(textarea) {
        // Validate on input (real-time)
        textarea.addEventListener('input', function() {
            validateDescription(this);
        });
        
        // Validate on blur (when user leaves the field)
        textarea.addEventListener('blur', function() {
            validateDescription(this);
        });
        
        // Initial validation for pre-filled forms
        validateDescription(textarea);
    }
    
    // Initialize validation for existing description textareas
    function initializeExistingTextareas() {
        const textareas = document.querySelectorAll('textarea[name*="description"]');
        textareas.forEach(addValidationToTextarea);
    }
    
    // Initialize existing textareas
    initializeExistingTextareas();
    
    // Watch for dynamically added forms (for add_goals.html)
    const formContainer = document.getElementById('form-container');
    if (formContainer) {
        // Use MutationObserver to detect new forms
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if this is a form card or contains one
                        const formCard = node.classList && node.classList.contains('goal-form-card') ? node : node.querySelector('.goal-form-card');
                        if (formCard) {
                            const textarea = formCard.querySelector('textarea[name*="description"]');
                            if (textarea) {
                                addValidationToTextarea(textarea);
                            }
                        }
                    }
                });
            });
        });
        
        observer.observe(formContainer, {
            childList: true,
            subtree: true
        });
    }
});
