document.addEventListener('DOMContentLoaded', function() {
    const acknowledgeBtn = document.getElementById('acknowledge-btn');
    
    if (acknowledgeBtn) {
        acknowledgeBtn.addEventListener('click', function() {
            const logId = this.dataset.logId;
            
            // Get CSRF token
            function getCsrfToken() {
                const metaTag = document.querySelector('meta[name="csrf-token"]');
                if (metaTag) {
                    return metaTag.getAttribute('content');
                }
                
                const cookieValue = document.cookie
                    .split('; ')
                    .find(row => row.startsWith('csrftoken='));
                return cookieValue ? cookieValue.split('=')[1] : '';
            }
            
            // Disable button
            acknowledgeBtn.disabled = true;
            acknowledgeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            
            // Send AJAX request
            fetch(`/communication/logs/${logId}/acknowledge/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    acknowledgeBtn.innerHTML = '<i class="fas fa-check-circle mr-2"></i>Acknowledged!';
                    acknowledgeBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
                    acknowledgeBtn.classList.add('bg-gray-600');
                    
                    // Show success message
                    const successDiv = document.createElement('div');
                    successDiv.className = 'mt-4 p-4 bg-green-500 bg-opacity-20 border border-green-500 rounded-lg text-green-500';
                    successDiv.innerHTML = `<i class="fas fa-check-circle mr-2"></i>Successfully acknowledged on ${data.acknowledged_at}`;
                    acknowledgeBtn.parentElement.appendChild(successDiv);
                    
                    // Reload page after 2 seconds
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    throw new Error(data.error || 'Failed to acknowledge');
                }
            })
            .catch(error => {
                acknowledgeBtn.disabled = false;
                acknowledgeBtn.innerHTML = '<i class="fas fa-check-circle mr-2"></i>Acknowledge This Communication';
                
                // Show error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'mt-4 p-4 bg-red-500 bg-opacity-20 border border-red-500 rounded-lg text-red-500';
                errorDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-2"></i>${error.message}`;
                acknowledgeBtn.parentElement.appendChild(errorDiv);
                
                // Remove error after 5 seconds
                setTimeout(() => {
                    errorDiv.remove();
                }, 5000);
            });
        });
    }
});

