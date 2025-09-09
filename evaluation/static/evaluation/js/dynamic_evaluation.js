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
                
                if (isSelected) {
                    star.classList.remove('text-gray-500');
                    star.classList.add('text-red-500');
                } else {
                    star.classList.remove('text-red-500');
                    star.classList.add('text-gray-500');
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
                // Add a subtle glow effect for filled stars
                label.style.textShadow = '0 0 8px rgba(239, 68, 68, 0.6)';
            } else {
                label.style.opacity = '0.4';
                label.style.transform = 'scale(1)';
                label.style.filter = 'grayscale(60%)';
                label.style.textShadow = 'none';
            }
        } else if (widgetType === 'emoji') {
            if (isSelected) {
                label.style.filter = 'none';
                label.style.textShadow = '0 0 20px rgba(255, 255, 0, 1), 0 0 30px rgba(255, 255, 0, 0.8), 0 0 40px rgba(255, 255, 0, 0.6)';
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