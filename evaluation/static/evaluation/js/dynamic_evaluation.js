/**
 * Dynamic Evaluation Form JavaScript
 * Handles clickable star interactions without radio buttons
 * 
 * @author Firehouse Movers
 * @version 1.0.0
 */

class DynamicEvaluation {
    constructor() {
        this.init();
    }

    /**
     * Initialize the dynamic evaluation functionality
     */
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            try {
                this.initializeClickableStars();
                
                // Initialize existing star values (for edit mode) with delay
                setTimeout(() => {
                    this.initializeExistingStarValues();
                }, 100);
            } catch (error) {
                console.error('Error initializing dynamic evaluation:', error);
            }
        });
    }

    /**
     * Initialize clickable star and rating interactions
     */
    initializeClickableStars() {
        try {
            // Handle star clicks
            const stars = document.querySelectorAll('svg.star[data-field]');
            stars.forEach(star => {
                star.addEventListener('click', (event) => {
                    this.handleStarClick(event);
                });
            });
            
            // Handle emoji/rating button clicks
            const ratingButtons = document.querySelectorAll('[data-field][data-value]');
            ratingButtons.forEach(button => {
                if (!button.classList.contains('star')) {
                    button.addEventListener('click', (event) => {
                        this.handleRatingButtonClick(event);
                    });
                }
            });
            
            // Handle emoji label clicks
            const emojiLabels = document.querySelectorAll('.fh-emoji label[data-field]');
            emojiLabels.forEach(label => {
                label.addEventListener('click', (event) => {
                    // Find the associated radio input and trigger it
                    const radioId = label.getAttribute('for');
                    const radioInput = document.getElementById(radioId);
                    if (radioInput) {
                        radioInput.checked = true;
                        // Trigger the rating button click handler
                        this.handleRatingButtonClick({
                            currentTarget: label
                        });
                    }
                });
            });
        } catch (error) {
            console.error('Error initializing clickable stars:', error);
        }
    }

    /**
     * Handle star click events
     * @param {Event} event - The click event
     */
    handleStarClick(event) {
        try {
            const star = event.currentTarget;
            const fieldName = star.dataset.field;
            const selectedValue = parseInt(star.dataset.value, 10);
            
            if (!fieldName || isNaN(selectedValue)) {
                console.warn('Invalid star data:', { fieldName, selectedValue });
                return;
            }
            
            // Update hidden input value
            this.updateHiddenInput(fieldName, selectedValue);
            
            // Update visual state of all stars in this group
            this.updateStarGroup(fieldName, selectedValue);
        } catch (error) {
            console.error('Error handling star click:', error);
        }
    }

    /**
     * Handle rating button click events
     * @param {Event} event - The click event
     */
    handleRatingButtonClick(event) {
        try {
            const button = event.currentTarget;
            const fieldName = button.dataset.field;
            const selectedValue = button.dataset.value;
            
            if (!fieldName || !selectedValue) {
                console.warn('Invalid rating button data:', { fieldName, selectedValue });
                return;
            }
            
            // Update hidden input value
            this.updateHiddenInput(fieldName, selectedValue);
            
            // Update visual state of all buttons in this group
            this.updateRatingGroup(fieldName, selectedValue);
        } catch (error) {
            console.error('Error handling rating button click:', error);
        }
    }

    /**
     * Update hidden input value
     * @param {string} fieldName - The field name
     * @param {string|number} value - The value to set
     */
    updateHiddenInput(fieldName, value) {
        const hiddenInput = document.getElementById(`${fieldName}_value`);
        if (hiddenInput) {
            hiddenInput.value = value;
        } else {
            console.warn(`Hidden input not found for field: ${fieldName}`);
        }
    }

    /**
     * Update star group visual state
     * @param {string} fieldName - The field name
     * @param {number} selectedValue - The selected star value
     */
    updateStarGroup(fieldName, selectedValue) {
        try {
            const stars = document.querySelectorAll(`svg.star[data-field="${fieldName}"]`);
            stars.forEach(star => {
                const starValue = parseInt(star.dataset.value, 10);
                if (isNaN(starValue)) {
                    console.warn(`Invalid star value for field ${fieldName}:`, star.dataset.value);
                    return;
                }
                
                if (starValue <= selectedValue) {
                    star.classList.remove('text-gray-500');
                    star.classList.add('text-red-500');
                } else {
                    star.classList.remove('text-red-500');
                    star.classList.add('text-gray-500');
                }
            });
        } catch (error) {
            console.error('Error updating star group:', error);
        }
    }

    /**
     * Update rating group visual state (for emoji/rating buttons)
     * @param {string} fieldName - The field name
     * @param {string} selectedValue - The selected value
     */
    updateRatingGroup(fieldName, selectedValue) {
        try {
            const buttons = document.querySelectorAll(`[data-field="${fieldName}"][data-value]`);
            buttons.forEach(button => {
                if (button.dataset.value === selectedValue) {
                    // Selected button
                    button.classList.add('ring-4', 'ring-red-500', 'bg-red-800/30');
                    if (button.classList.contains('text-white')) {
                        button.classList.remove('text-white');
                        button.classList.add('text-red-400');
                    }
                } else {
                    // Unselected buttons
                    button.classList.remove('ring-4', 'ring-red-500', 'bg-red-800/30');
                    if (button.classList.contains('text-red-400')) {
                        button.classList.remove('text-red-400');
                        button.classList.add('text-white');
                    }
                }
            });
        } catch (error) {
            console.error('Error updating rating group:', error);
        }
    }

    /**
     * Initialize existing star values for edit mode
     */
    initializeExistingStarValues() {
        try {
            const hiddenInputs = document.querySelectorAll('input[type="hidden"][id$="_value"]');
            hiddenInputs.forEach(input => {
                const fieldName = input.name;
                const value = input.value;
                
                if (value) {
                    // Check if this is a star field
                    const stars = document.querySelectorAll(`svg.star[data-field="${fieldName}"]`);
                    if (stars.length > 0) {
                        // It's a star field
                        this.updateStarGroup(fieldName, parseInt(value, 10));
                    } else {
                        // It's an emoji/rating field
                        this.updateRatingGroup(fieldName, value);
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing existing star values:', error);
        }
    }
}

// Initialize dynamic evaluation functionality
new DynamicEvaluation();

// Export for potential use in other modules
window.DynamicEvaluation = DynamicEvaluation;
