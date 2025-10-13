// Archived Manager and Employee Evaluations JavaScript
// Handles filtering and unarchive functionality for both manager and employee evaluations

let currentEvaluationId = null;
let currentButton = null;
let currentEvalType = null;

function openArchiveModal(button) {
    const evaluationId = button.dataset.evaluationId;
    const evalType = button.dataset.evalType;
    const name = button.dataset.name;
    const isArchived = button.dataset.isArchived === 'true';
    
    currentEvaluationId = evaluationId;
    currentButton = button;
    currentEvalType = evalType;
    
    const modal = document.getElementById('archiveModal');
    const modalTitle = modal.querySelector('.modal-header h3');
    const modalBody = modal.querySelector('.modal-body');
    const confirmBtn = modal.querySelector('.modal-btn-archive');
    const icon = modal.querySelector('.modal-header i');
    
    if (isArchived) {
        // Unarchive mode
        modalTitle.textContent = 'Unarchive Evaluation';
        modalBody.innerHTML = `<p>Are you sure you want to unarchive the evaluation for <strong>${name}</strong>?</p>
                               <p class="text-sm mt-2">This evaluation will become visible again.</p>`;
        confirmBtn.textContent = 'Unarchive';
        confirmBtn.classList.add('btn-unarchive');
        confirmBtn.classList.remove('modal-btn-archive');
        icon.className = 'fas fa-box-open';
    } else {
        // Archive mode
        modalTitle.textContent = 'Archive Evaluation';
        modalBody.innerHTML = `<p>Are you sure you want to archive the evaluation for <strong>${name}</strong>?</p>
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
    currentEvalType = null;
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
    
    // Determine the correct URL based on evaluation type
    let url;
    if (currentEvalType === 'employee') {
        url = `/evaluation/evaluation/${currentEvaluationId}/toggle-archive/`;
    } else {
        url = `/evaluation/manager-evaluation/${currentEvaluationId}/toggle-archive/`;
    }
    
    fetch(url, {
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
            
            // If unarchiving (moving from archived to active), remove the card from the page
            if (!newIsArchived) {
                // Find and remove the card
                const card = document.querySelector(`.evaluation-card[data-evaluation-id="${savedEvaluationId}"]`);
                if (card) {
                    // Add fade-out animation
                    card.style.transition = 'opacity 0.3s, transform 0.3s';
                    card.style.opacity = '0';
                    card.style.transform = 'translateX(20px)';
                    
                    setTimeout(() => {
                        card.remove();
                        
                        // Update the archive count
                        updateArchiveCount();
                        
                        // Update the dropdown filter count
                        const filterSelect = document.getElementById('evaluationTypeFilter');
                        if (filterSelect) {
                            const selectedOption = filterSelect.options[filterSelect.selectedIndex];
                            const currentCount = parseInt(selectedOption.textContent.match(/\((\d+)\)/)[1]);
                            const newCount = currentCount - 1;
                            const evalTypeText = currentEvalType === 'employee' ? 'Employee' : 'Manager';
                            selectedOption.textContent = `${evalTypeText} Evaluations (${newCount})`;
                        }
                        
                        // Check if there are any cards left
                        const remainingCards = document.querySelectorAll('.evaluation-card');
                        if (remainingCards.length === 0) {
                            // Show empty state
                            const evalList = document.querySelector('.evaluation-list');
                            const bottomNav = document.querySelector('.bottom-navigation');
                            if (evalList) evalList.remove();
                            if (bottomNav) bottomNav.remove();
                            
                            const pageContainer = document.querySelector('.pending-evaluations-page');
                            const evalTypeText = currentEvalType === 'employee' ? 'employee' : 'manager';
                            const emptyState = `
                                <div class="empty-state slide-in">
                                    <div class="empty-state-icon">
                                        <i class="fas fa-archive text-white text-xl"></i>
                                    </div>
                                    <h2 class="empty-state-title">No Archived Evaluations</h2>
                                    <p class="empty-state-description">No archived ${evalTypeText} evaluations found.</p>
                                    <a href="/evaluation/analytics/" class="btn-modern">
                                        <i class="fas fa-arrow-left"></i>
                                        Back to Dashboard
                                    </a>
                                </div>
                            `;
                            pageContainer.insertAdjacentHTML('beforeend', emptyState);
                        }
                    }, 300);
                }
            } else {
                // If archiving, update button state (shouldn't happen on this page, but keep for safety)
                const button = document.querySelector(`button[data-evaluation-id="${savedEvaluationId}"]`);
                if (button) {
                    button.dataset.isArchived = newIsArchived;
                    button.innerHTML = '<i class="fas fa-box-open mr-1"></i> Unarchive';
                    button.classList.add('archived');
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

function updateArchiveCount() {
    // Update the archive count in the summary
    const archiveCountEl = document.getElementById('archive-count');
    if (archiveCountEl) {
        const evalType = archiveCountEl.dataset.evalType || 'manager';
        const text = archiveCountEl.textContent.trim();
        const match = text.match(/^(\d+)/);
        if (match) {
            const currentCount = parseInt(match[1]);
            const newCount = Math.max(0, currentCount - 1);
            const evalTypeText = evalType === 'employee' ? 'employee' : 'manager';
            const pluralText = newCount === 1 ? 'evaluation' : 'evaluations';
            archiveCountEl.textContent = `${newCount} archived ${evalTypeText} ${pluralText}`;
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

// Filter change handler
function handleFilterChange(selectElement) {
    const evalType = selectElement.value;
    const url = new URL(window.location.href);
    url.searchParams.set('type', evalType);
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
    // Add event listeners to all unarchive buttons
    const unarchiveButtons = document.querySelectorAll('.btn-unarchive');
    unarchiveButtons.forEach(button => {
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
    
    // Add event listener to filter dropdown
    const filterSelect = document.getElementById('evaluationTypeFilter');
    if (filterSelect) {
        filterSelect.addEventListener('change', function(e) {
            handleFilterChange(this);
        });
    }
});