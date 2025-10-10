// Employee Evaluations List JavaScript
// Archive functionality and UI interactions

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
                               <p class="text-sm mt-2">This evaluation will be hidden from the main view but can be restored later.</p>`;
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
    
    // Reset modal state - find button with either class
    const confirmBtn = modal.querySelector('.modal-btn-archive, .btn-unarchive');
    if (confirmBtn) {
        confirmBtn.disabled = false;
        // Restore default state
        confirmBtn.classList.remove('btn-unarchive');
        confirmBtn.classList.add('modal-btn-archive');
    }
    
    // Clear current references
    currentEvaluationId = null;
    currentButton = null;
}

function confirmArchive() {
    if (!currentEvaluationId || !currentButton) return;
    
    const csrfToken = getCSRFToken();
    const modal = document.getElementById('archiveModal');
    const confirmBtn = modal.querySelector('.modal-btn-archive, .btn-unarchive');
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
    messageDiv.className = 'success-notification';
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.classList.add('fade-out');
        setTimeout(() => messageDiv.remove(), 300);
    }, 3000);
}

// Toggle show archived filter
function toggleShowArchived(checkbox) {
    const url = new URL(window.location.href);
    if (checkbox.checked) {
        url.searchParams.set('show_archived', 'true');
    } else {
        url.searchParams.delete('show_archived');
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

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set progress bar width from data attribute
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        const progress = progressFill.getAttribute('data-progress');
        if (progress) {
            progressFill.style.width = progress + '%';
        }
    }
    
    // Back button handler
    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', function() {
            history.back();
        });
    }
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.borderColor = '#ef4444';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.borderColor = '#374151';
        });
    });
    
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
    
    // Add event listener to confirm button - use modal footer to find it
    const modal = document.getElementById('archiveModal');
    if (modal) {
        const modalFooter = modal.querySelector('.modal-footer');
        if (modalFooter) {
            // Find the archive/confirm button (second button in footer)
            const buttons = modalFooter.querySelectorAll('button');
            if (buttons.length > 1) {
                buttons[1].addEventListener('click', confirmArchive);
            }
        }
    }
    
    // Add event listener to show archived toggle
    const showArchivedToggle = document.getElementById('showArchivedToggle');
    if (showArchivedToggle) {
        showArchivedToggle.addEventListener('change', function() {
            toggleShowArchived(this);
        });
    }
});