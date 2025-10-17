// Handle acknowledgment deadline field visibility based on requires_acknowledgment checkbox

document.addEventListener('DOMContentLoaded', function() {
    const requiresAckCheckbox = document.querySelector('input[name="requires_acknowledgment"]');
    const deadlineContainer = document.getElementById('deadline-container');
    const deadlineField = document.querySelector('input[name="acknowledgment_deadline"]');
    
    if (requiresAckCheckbox && deadlineContainer && deadlineField) {
        // Function to toggle deadline field visibility
        function toggleDeadlineField() {
            if (requiresAckCheckbox.checked) {
                deadlineContainer.style.display = 'block';
                deadlineField.disabled = false;
            } else {
                deadlineContainer.style.display = 'none';
                deadlineField.disabled = true;
                deadlineField.value = ''; // Clear value when hidden
            }
        }
        
        // Set initial state
        toggleDeadlineField();
        
        // Listen for checkbox changes
        requiresAckCheckbox.addEventListener('change', toggleDeadlineField);
    }
});

