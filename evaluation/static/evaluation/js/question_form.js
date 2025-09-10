/**
 * Question Form JavaScript
 * Handles dynamic enabling/disabling of min_value and max_value fields
 * based on question type selection.
 * 
 * @author Firehouse Movers
 * @version 1.0.0
 */

class QuestionForm {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            try {
                this.initializeFieldToggling();
            } catch (error) {
                console.error('Error initializing question form:', error);
            }
        });
    }

    /**
     * Initialize field toggling functionality
     */
    initializeFieldToggling() {
        const qtypeSelect = document.querySelector('select[name="qtype"]');
        const minValueInput = document.querySelector('input[name="min_value"]');
        const maxValueInput = document.querySelector('input[name="max_value"]');
        
        if (!qtypeSelect || !minValueInput || !maxValueInput) {
            console.warn('Question form elements not found');
            return;
        }

        // Define numeric question types that use min/max values
        this.numericTypes = ['stars', 'emoji', 'rating', 'number'];
        
        // Bind the toggle function to the select change event
        qtypeSelect.addEventListener('change', () => {
            this.toggleMinMaxFields(qtypeSelect, minValueInput, maxValueInput);
        });
        
        // Initialize field states on page load
        this.toggleMinMaxFields(qtypeSelect, minValueInput, maxValueInput);
    }

    /**
     * Toggle min/max value fields based on question type
     */
    toggleMinMaxFields(qtypeSelect, minValueInput, maxValueInput) {
        const qtype = qtypeSelect.value;
        const isNumericType = this.numericTypes.includes(qtype);
        
        if (isNumericType) {
            this.enableFields(minValueInput, maxValueInput);
        } else {
            this.disableFields(minValueInput, maxValueInput);
        }
    }

    /**
     * Enable min/max value fields
     */
    enableFields(minValueInput, maxValueInput) {
        minValueInput.disabled = false;
        maxValueInput.disabled = false;
        minValueInput.classList.remove('disabled');
        maxValueInput.classList.remove('disabled');
    }

    /**
     * Disable min/max value fields and clear their values
     */
    disableFields(minValueInput, maxValueInput) {
        minValueInput.disabled = true;
        maxValueInput.disabled = true;
        minValueInput.classList.add('disabled');
        maxValueInput.classList.add('disabled');
        
        // Clear values when disabled
        minValueInput.value = '';
        maxValueInput.value = '';
    }
}

// Initialize question form functionality
new QuestionForm();

// Export for potential use in other modules
window.QuestionForm = QuestionForm;
