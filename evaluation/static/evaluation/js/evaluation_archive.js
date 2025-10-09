// Archive modal functionality for employee evaluations
let currentEvaluationId = null;
let currentButton = null;

function openArchiveModal(button) {
    const evaluationId = button.dataset.evaluationId;
    const employeeName = button.dataset.employeeName;
    const isArchived = button.dataset.isArchived === 'true';
    
    currentEvaluationId = evaluationId;
    currentButton = button;
    
    const modal = document.getElementById('archiveModal');
    const modalTitle = modal.querySelector('.modal-header h3');
    const modalBody = modal.querySelector('.modal-body');
    const confirmBtn = modal.querySelector('.modal-btn-archive');
    const icon = modal.querySelector('.modal-header i');
    
    if (isArchived) {
        // Unarchive mode
        modalTitle.textContent = 'Unarchive Evaluation';
        modalBody.innerHTML = `<p>Are you sure you want to unarchive the evaluation for <strong>${employeeName}</strong>?</p>
                               <p class="text-sm mt-2">This evaluation will become visible to the employee again.</p>`;
        confirmBtn.textContent = 'Unarchive';
        confirmBtn.classList.add('btn-unarchive');
        confirmBtn.classList.remove('modal-btn-archive');
        icon.className = 'fas fa-box-open';
    } else {
        // Archive mode
        modalTitle.textContent = 'Archive Evaluation';
        modalBody.innerHTML = `<p>Are you sure you want to archive the evaluation for <strong>${employeeName}</strong>?</p>
                               <p class="text-sm mt-2">This evaluation will be hidden from the employee and moved to your archived evaluations.</p>`;
        confirmBtn.textContent = 'Archive';
        confirmBtn.classList.remove('btn-unarchive');
        confirmBtn.classList.add('modal-btn-archive');
        icon.className = 'fas fa-archive';
    }
    
    modal.classList.add('show');
}

function closeArchiveModal() {
    const modal = document.getElementById('archiveModal');
    modal.classList.remove('show');
    
    // Reset modal state
    const confirmBtn = modal.querySelector('.modal-btn-archive');
    confirmBtn.disabled = false;
    
    // Clear current references
    currentEvaluationId = null;
    currentButton = null;
}

function confirmArchive() {
    if (!currentEvaluationId || !currentButton) return;
    
    const csrfToken = getCSRFToken();
    const modal = document.getElementById('archiveModal');
    const confirmBtn = modal.querySelector('.modal-btn-archive');
    const isArchived = currentButton.dataset.isArchived === 'true';
    
    // Disable button while processing
    confirmBtn.disabled = true;
    confirmBtn.textContent = isArchived ? 'Unarchiving...' : 'Archiving...';
    
    fetch(`/evaluation/evaluation/${currentEvaluationId}/toggle-archive/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const newIsArchived = data.is_archived;
            const savedEvaluationId = currentEvaluationId;
            
            // Close modal and clear references
            closeArchiveModal();
            
            // Update button state without page reload
            const button = document.querySelector(`button[data-evaluation-id="${savedEvaluationId}"]`);
            if (button) {
                button.dataset.isArchived = newIsArchived;
                
                if (newIsArchived) {
                    button.innerHTML = '<i class="fas fa-box-open"></i> Unarchive';
                    button.classList.add('archived');
                } else {
                    button.innerHTML = '<i class="fas fa-archive"></i> Archive';
                    button.classList.remove('archived');
                }
            }
            
            // Show success message
            showSuccessMessage(data.message);
        } else {
            alert(data.error || 'Failed to toggle archive status');
            confirmBtn.disabled = false;
            confirmBtn.textContent = isArchived ? 'Unarchive' : 'Archive';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        confirmBtn.disabled = false;
        confirmBtn.textContent = isArchived ? 'Unarchive' : 'Archive';
    });
}

function showSuccessMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 bg-green-600 text-white';
    messageDiv.style.animation = 'slideIn 0.3s ease-out';
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transition = 'opacity 0.3s';
        setTimeout(() => messageDiv.remove(), 300);
    }, 3000);
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('archiveModal');
    if (modal && event.target === modal) {
        closeArchiveModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeArchiveModal();
    }
});

// Toggle show archived filter
function toggleShowArchived(checkbox) {
    const url = new URL(window.location.href);
    if (checkbox.checked) {
        url.searchParams.delete('show_archived'); // Default is true, so remove param
    } else {
        url.searchParams.set('show_archived', 'false');
    }
    window.location.href = url.toString();
}

function getCSRFToken() {
    // Try to get from meta tag first
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.content;
    }
    
    // Fallback to cookie
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to all archive buttons
    document.querySelectorAll('.archive-btn').forEach(button => {
        button.addEventListener('click', function() {
            openArchiveModal(this);
        });
    });
    
    // Add event listener to cancel button
    const cancelBtn = document.querySelector('.modal-btn-cancel');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeArchiveModal);
    }
    
    // Add event listener to confirm button
    const confirmBtn = document.querySelector('.modal-btn-archive');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', confirmArchive);
    }
    
    // Add event listener to show archived toggle
    const showArchivedToggle = document.getElementById('showArchivedToggle');
    if (showArchivedToggle) {
        showArchivedToggle.addEventListener('change', function() {
            toggleShowArchived(this);
        });
    }
});

