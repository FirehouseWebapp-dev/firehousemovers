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
        const includeInTrendsCheckbox = document.querySelector('input[name="include_in_trends"]');
        
        if (!qtypeSelect || !minValueInput || !maxValueInput) {
            console.warn('Question form elements not found');
            return;
        }

        // Define numeric question types that use min/max values
        this.numericTypes = ['stars', 'emoji', 'rating', 'number'];
        
        // Define question types that should be included in trends by default
        this.trendQtypes = ['stars', 'emoji', 'rating', 'number', 'bool'];
        
        // Define question types that should be disabled for trends
        this.disabledTrendQtypes = ['select', 'short', 'long', 'section'];
        
        // Bind the toggle function to the select change event
        qtypeSelect.addEventListener('change', () => {
            this.toggleMinMaxFields(qtypeSelect, minValueInput, maxValueInput);
            if (includeInTrendsCheckbox) {
                this.toggleIncludeInTrends(qtypeSelect, includeInTrendsCheckbox);
            }
        });
        
        // Initialize field states on page load
        this.toggleMinMaxFields(qtypeSelect, minValueInput, maxValueInput);
        if (includeInTrendsCheckbox) {
            this.toggleIncludeInTrends(qtypeSelect, includeInTrendsCheckbox);
        }
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

    /**
     * Toggle include_in_trends checkbox based on question type
     */
    toggleIncludeInTrends(qtypeSelect, includeInTrendsCheckbox) {
        const qtype = qtypeSelect.value;
        
        if (this.trendQtypes.includes(qtype)) {
            // Auto-check for trend-compatible question types
            includeInTrendsCheckbox.checked = true;
            includeInTrendsCheckbox.disabled = false;
            includeInTrendsCheckbox.classList.remove('disabled');
            includeInTrendsCheckbox.title = 'This question type is suitable for trend analysis';
        } else if (this.disabledTrendQtypes.includes(qtype)) {
            // Disable for non-trend question types
            includeInTrendsCheckbox.checked = false;
            includeInTrendsCheckbox.disabled = true;
            includeInTrendsCheckbox.classList.add('disabled');
            includeInTrendsCheckbox.title = `${qtype.charAt(0).toUpperCase() + qtype.slice(1)} questions cannot be included in trends as they are not suitable for chart analysis`;
        } else {
            // Default behavior for other types
            includeInTrendsCheckbox.disabled = false;
            includeInTrendsCheckbox.classList.remove('disabled');
            includeInTrendsCheckbox.title = 'Include this question in trend analysis charts';
        }
    }
}

// Initialize question form functionality
new QuestionForm();

// Export for potential use in other modules
window.QuestionForm = QuestionForm;
