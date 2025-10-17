document.addEventListener('DOMContentLoaded', function() {
    const responseTextarea = document.querySelector('textarea[name="response_text"]');
    const charCountSpan = document.getElementById('charCount');
    const charCounterDiv = charCountSpan?.parentElement;
    const form = document.getElementById('responseForm');
    const maxLength = 5000;

    if (responseTextarea && charCountSpan) {
        // Update character count on input
        function updateCharCount() {
            const currentLength = responseTextarea.value.length;
            charCountSpan.textContent = currentLength;

            // Update styling based on character count
            if (currentLength >= maxLength) {
                charCounterDiv.classList.add('error');
                charCounterDiv.classList.remove('warning');
            } else if (currentLength >= maxLength * 0.9) {
                charCounterDiv.classList.add('warning');
                charCounterDiv.classList.remove('error');
            } else {
                charCounterDiv.classList.remove('warning', 'error');
            }
        }

        // Initialize count on page load
        updateCharCount();

        // Update count on input
        responseTextarea.addEventListener('input', updateCharCount);
    }

    // Confirm before submitting
    if (form) {
        form.addEventListener('submit', function(e) {
            const action = e.submitter?.value;
            
            if (action === 'submit') {
                const confirmed = confirm('Are you sure you want to submit this response? Once submitted, your manager will be notified.');
                if (!confirmed) {
                    e.preventDefault();
                }
            }
        });
    }

    // Auto-save draft functionality (optional)
    let autoSaveTimeout;
    if (responseTextarea) {
        responseTextarea.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(function() {
                // Optional: Implement auto-save draft via AJAX
                console.log('Auto-save draft (to be implemented if needed)');
            }, 3000);
        });
    }
});

