// Archive/Unarchive modal functionality for employee evaluations (same as main dashboard)
let currentEvaluationId = null;
let currentButton = null;
let currentCard = null;

function openArchiveModal(button) {
    const evaluationId = button.dataset.evaluationId;
    const employeeName = button.dataset.employeeName;
    const isArchived = button.dataset.isArchived === 'true';
    
    currentEvaluationId = evaluationId;
    currentButton = button;
    // Store card reference immediately
    currentCard = document.querySelector(`.evaluation-card[data-evaluation-id="${evaluationId}"]`);
    
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
    currentCard = null;
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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const newIsArchived = data.is_archived;
            
            // If we're on the archived page and just unarchived, remove the card instantly
            if (isArchived && !newIsArchived) {
                // Use stored card reference
                if (currentCard) {
                    currentCard.remove();
                    
                    // Close modal after removal
                    closeArchiveModal();
                    
                    // Show success message
                    showSuccessMessage(data.message);
                    
                    // Update the archive count
                    updateArchiveCount();
                    
                    // Check if there are no more evaluations
                    const remainingCards = document.querySelectorAll('.evaluation-card');
                    if (remainingCards.length === 0) {
                        location.reload();
                    }
                }
            } else {
                // Update button state without page reload (for non-archived pages)
                const buttonToUpdate = currentButton; // Save reference before clearing
                const savedEvalId = currentEvaluationId;
                
                // Close modal first
                closeArchiveModal();
                
                if (buttonToUpdate) {
                    buttonToUpdate.dataset.isArchived = newIsArchived;
                    
                    if (newIsArchived) {
                        buttonToUpdate.innerHTML = '<i class="fas fa-box-open"></i> Unarchive';
                        buttonToUpdate.classList.add('btn-unarchive');
                    } else {
                        buttonToUpdate.innerHTML = '<i class="fas fa-archive"></i> Archive';
                        buttonToUpdate.classList.remove('btn-unarchive');
                    }
                }
                
                // Show success message
                showSuccessMessage(data.message);
            }
        } else {
            alert(data.error || 'Failed to toggle archive status');
            confirmBtn.disabled = false;
            confirmBtn.textContent = isArchived ? 'Unarchive' : 'Archive';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred: ' + error.message);
        confirmBtn.disabled = false;
        confirmBtn.textContent = isArchived ? 'Unarchive' : 'Archive';
    });
}

function updateArchiveCount() {
    // Update the archive count in the summary
    const archiveCountEl = document.getElementById('archive-count');
    if (archiveCountEl) {
        const text = archiveCountEl.textContent.trim();
        const match = text.match(/^(\d+)/);
        if (match) {
            const currentCount = parseInt(match[1]);
            const newCount = Math.max(0, currentCount - 1);
            const pluralText = newCount === 1 ? 'evaluation' : 'evaluations';
            archiveCountEl.textContent = `${newCount} archived ${pluralText}`;
        }
    }
    
    // Update the pagination info
    const paginationInfoEl = document.getElementById('pagination-info');
    if (paginationInfoEl) {
        const text = paginationInfoEl.textContent.trim();
        const match = text.match(/^Showing (\d+) - (\d+) of (\d+)/);
        if (match) {
            const startIndex = parseInt(match[1]);
            let endIndex = parseInt(match[2]);
            const totalCount = parseInt(match[3]);
            
            const newTotal = Math.max(0, totalCount - 1);
            const newEnd = Math.max(0, endIndex - 1);
            const pluralText = newTotal === 1 ? 'evaluation' : 'evaluations';
            
            // Update the text
            if (newTotal > 0) {
                paginationInfoEl.textContent = `Showing ${startIndex} - ${newEnd} of ${newTotal} ${pluralText}`;
            }
        }
    }
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
    // Add event listeners to all unarchive buttons
    document.querySelectorAll('.btn-unarchive').forEach(button => {
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
});

