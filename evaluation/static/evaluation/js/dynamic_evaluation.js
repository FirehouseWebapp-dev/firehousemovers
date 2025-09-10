/**
 * Dynamic Evaluation Form JavaScript
 * Handles interactive form widgets (stars, emojis, pills)
 * 
 * @author Firehouse Movers
 * @version 2.0.0
 */

class DynamicEvaluation {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            try {
                this.initializeEventListeners();
                this.initializeExistingValues();
            } catch (error) {
                console.error('Error initializing dynamic evaluation:', error);
            }
        });
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Handle radio button labels (new widget system)
        document.querySelectorAll('label[for]').forEach(label => {
            label.addEventListener('click', (event) => {
                this.handleLabelClick(event);
            });
        });

        // Handle legacy SVG stars and rating buttons
        document.querySelectorAll('[data-field][data-value]').forEach(element => {
            element.addEventListener('click', (event) => {
                this.handleLegacyClick(event);
            });
        });

        // Handle number input validation
        document.querySelectorAll('input[type="number"]').forEach(input => {
            input.addEventListener('input', (event) => {
                this.validateNumberInput(event);
            });
            input.addEventListener('blur', (event) => {
                this.validateNumberInput(event);
            });
        });
    }

    /**
     * Handle label clicks for radio button widgets
     */
    handleLabelClick(event) {
        try {
            const label = event.currentTarget;
            const input = document.getElementById(label.getAttribute('for'));
            
            if (!input || input.type !== 'radio') return;
            
            input.checked = true;
            this.updateWidgetGroup(input.name, input.value, label);
        } catch (error) {
            console.error('Error handling label click:', error);
        }
    }

    /**
     * Handle legacy SVG stars and rating buttons
     */
    handleLegacyClick(event) {
        try {
            const element = event.currentTarget;
            const fieldName = element.dataset.field;
            const value = element.dataset.value;
            
            if (!fieldName || !value) return;
            
            // Update hidden input if it exists
            const hiddenInput = document.getElementById(`${fieldName}_value`);
            if (hiddenInput) {
                hiddenInput.value = value;
            }
            
            // Update visual state
            if (element.classList.contains('star')) {
                this.updateLegacyStars(fieldName, parseInt(value, 10));
            } else {
                this.updateLegacyButtons(fieldName, value);
            }
        } catch (error) {
            console.error('Error handling legacy click:', error);
        }
    }

    /**
     * Update widget group visual state
     */
    updateWidgetGroup(fieldName, selectedValue, clickedLabel) {
        try {
            const inputs = document.querySelectorAll(`input[name="${fieldName}"]`);
            const widgetType = this.getWidgetType(clickedLabel);
            
            inputs.forEach(input => {
                const label = document.querySelector(`label[for="${input.id}"]`);
                if (!label) return;
                
                let isSelected;
                if (widgetType === 'star') {
                    // For stars, use cumulative selection (fill all stars up to selected one)
                    const inputValue = parseInt(input.value, 10);
                    const selectedValueInt = parseInt(selectedValue, 10);
                    isSelected = inputValue <= selectedValueInt;
                } else {
                    // For other widgets (emoji, pill), use exact selection
                    isSelected = input.value === selectedValue;
                }
                
                this.setWidgetState(label, widgetType, isSelected);
            });
        } catch (error) {
            console.error('Error updating widget group:', error);
        }
    }

    /**
     * Update legacy star group visual state
     */
    updateLegacyStars(fieldName, selectedValue) {
        try {
            const stars = document.querySelectorAll(`svg.star[data-field="${fieldName}"]`);
            stars.forEach(star => {
                const starValue = parseInt(star.dataset.value, 10);
                const isSelected = starValue <= selectedValue;
                
                // Use direct style manipulation like the original evaluation
                if (isSelected) {
                    star.style.fill = '#ef4444'; // text-red-500 equivalent
                } else {
                    star.style.fill = '#6b7280'; // text-gray-500 equivalent
                }
            });
        } catch (error) {
            console.error('Error updating legacy stars:', error);
        }
    }

    /**
     * Update legacy button group visual state
     */
    updateLegacyButtons(fieldName, selectedValue) {
        try {
            const buttons = document.querySelectorAll(`[data-field="${fieldName}"][data-value]`);
            buttons.forEach(button => {
                const isSelected = button.dataset.value === selectedValue;
                
                if (isSelected) {
                    button.classList.add('ring-4', 'ring-red-500', 'bg-red-800/30');
                    if (button.classList.contains('text-white')) {
                        button.classList.remove('text-white');
                        button.classList.add('text-red-400');
                    }
                } else {
                    button.classList.remove('ring-4', 'ring-red-500', 'bg-red-800/30');
                    if (button.classList.contains('text-red-400')) {
                        button.classList.remove('text-red-400');
                        button.classList.add('text-white');
                    }
                }
            });
        } catch (error) {
            console.error('Error updating legacy buttons:', error);
        }
    }

    /**
     * Set widget visual state
     */
    setWidgetState(label, widgetType, isSelected) {
        if (widgetType === 'star') {
            if (isSelected) {
                label.style.opacity = '1';
                label.style.transform = 'scale(1.06)';
                label.style.filter = 'none';
                // Remove glow effect for filled stars
            } else {
                label.style.opacity = '0.4';
                label.style.transform = 'scale(1)';
                label.style.filter = 'grayscale(60%)';
                label.style.textShadow = 'none';
            }
        } else if (widgetType === 'emoji') {
            if (isSelected) {
                label.style.filter = 'none';
                label.style.textShadow = 'none';
                label.style.opacity = '1';
            } else {
                label.style.filter = 'grayscale(40%) brightness(0.7)';
                label.style.textShadow = 'none';
                label.style.opacity = '0.7';
            }
        }
    }

    /**
     * Get widget type from label element
     */
    getWidgetType(label) {
        if (label.closest('.fh-star')) return 'star';
        if (label.closest('.fh-emoji')) return 'emoji';
        if (label.closest('.fh-pill')) return 'pill';
        return 'unknown';
    }

    /**
     * Validate number input against min/max constraints
     */
    validateNumberInput(event) {
        try {
            const input = event.currentTarget;
            const value = parseInt(input.value, 10);
            const min = parseInt(input.getAttribute('min'), 10) || 0;
            const max = parseInt(input.getAttribute('max'), 10);
            
            // Clear previous error styling
            input.classList.remove('border-red-500', 'bg-red-50');
            
            // Remove existing error message
            const existingError = input.parentNode.querySelector('.number-error-message');
            if (existingError) {
                existingError.remove();
            }
            
            // Validate if value is provided
            if (input.value && !isNaN(value)) {
                if (value < min) {
                    this.showNumberError(input, `Value must be at least ${min}.`);
                    return false;
                } else if (max && value > max) {
                    this.showNumberError(input, `Value cannot exceed ${max}.`);
                    return false;
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error validating number input:', error);
            return true;
        }
    }

    /**
     * Show error message for number input
     */
    showNumberError(input, message) {
        // Add error styling
        input.classList.add('border-red-500', 'bg-red-50');
        
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'number-error-message text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        
        // Insert error message after the input
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
    }

    /**
     * Initialize existing values for edit mode
     */
    initializeExistingValues() {
        setTimeout(() => {
            try {
                // Handle radio button widgets
                document.querySelectorAll('input[type="radio"]:checked').forEach(input => {
                    const label = document.querySelector(`label[for="${input.id}"]`);
                    if (label) {
                        this.updateWidgetGroup(input.name, input.value, label);
                    }
                });

                // Handle legacy hidden inputs
                document.querySelectorAll('input[type="hidden"][id$="_value"]').forEach(input => {
                    if (!input.value) return;
                    
                    const fieldName = input.name;
                    const value = input.value;
                    
                    // Check if it's a star field
                    const stars = document.querySelectorAll(`svg.star[data-field="${fieldName}"]`);
                    if (stars.length > 0) {
                        this.updateLegacyStars(fieldName, parseInt(value, 10));
                    } else {
                        this.updateLegacyButtons(fieldName, value);
                    }
                });
            } catch (error) {
                console.error('Error initializing existing values:', error);
            }
        }, 100);
    }
}

// Initialize dynamic evaluation functionality
new DynamicEvaluation();

// Export for potential use in other modules
window.DynamicEvaluation = DynamicEvaluation;