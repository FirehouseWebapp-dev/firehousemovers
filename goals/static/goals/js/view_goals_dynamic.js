document.addEventListener('DOMContentLoaded', function() {
    // Handle filter form submissions (from view_goals.js)
    var goalTypeSelect = document.getElementById('goalTypeSelect');
    var completionStatusSelect = document.getElementById('completionStatusSelect');
    var filterForm = document.getElementById('filterForm');
    var closeGoalModalBtn = document.getElementById('closeGoalModalBtn');

    if (goalTypeSelect && filterForm) {
        goalTypeSelect.addEventListener('change', function() {
            filterForm.submit();
        });
    }

    if (completionStatusSelect && filterForm) {
        completionStatusSelect.addEventListener('change', function() {
            filterForm.submit();
        });
    }

    // Handle close modal button click (from view_goals.js)
    if (closeGoalModalBtn && window.GoalsUI && window.GoalsUI.closeGoalModal) {
        closeGoalModalBtn.addEventListener('click', function() {
            window.GoalsUI.closeGoalModal();
        });
    }

    // Original dynamic functionality
    const goalTypeFilter = document.getElementById('goal-type-filter');
    const completionFilter = document.getElementById('completion-filter');
    const employeeId = goalTypeFilter ? goalTypeFilter.dataset.employeeId : (completionFilter ? completionFilter.dataset.employeeId : null);

    // Function to bind checkbox events
    function bindCompletionCheckboxes() {
        const csrfToken = window.GoalsUI && window.GoalsUI.getCSRFToken ? window.GoalsUI.getCSRFToken() : getCSRFToken();

        document.querySelectorAll(".goal-completion-checkbox").forEach(checkbox => {
            // Disable checkboxes for already completed goals and hide edit/delete buttons
            if (checkbox.checked) {
                checkbox.disabled = true;
                checkbox.classList.add('pointer-events-none', 'cursor-not-allowed', 'opacity-50');
                
                // Hide edit and delete buttons for already completed goals on page load
                const goalId = checkbox.dataset.goalId;
                const goalCard = document.getElementById(`goal-${goalId}`);
                if (goalCard) {
                    const editButton = goalCard.querySelector('a[data-can-edit="true"]');
                    const deleteButton = goalCard.querySelector('.delete-goal-btn');
                    if (editButton) {
                        editButton.classList.add('hidden');
                        editButton.style.display = 'none';
                    }
                    if (deleteButton) {
                        deleteButton.classList.add('hidden');
                        deleteButton.style.display = 'none';
                    }
                }
                return;
            }
            
            // Add pointer cursor for enabled checkboxes
            checkbox.style.cursor = 'pointer';
            
            checkbox.addEventListener("change", function () {
                const goalId = this.dataset.goalId;
                const isCompleted = this.checked;
                const goalCard = document.getElementById(`goal-${goalId }`);
                
                // Only allow marking as completed, not unchecking
                if (isCompleted) {
                    // Revert checkbox state temporarily
                    this.checked = false;
                    
                    // Show confirmation modal
                    const modal = document.getElementById('completionConfirmationModal');
                    const confirmBtn = document.getElementById('confirmCompletionBtn');
                    const cancelBtn = document.getElementById('cancelCompletionBtn');
                    
                    if (modal && confirmBtn && cancelBtn) {
                        modal.classList.remove('hidden');
                        
                        // Handle confirmation
                        const handleConfirm = () => {
                            modal.classList.add('hidden');
                            this.checked = true;
                            processGoalCompletion(goalId, true, goalCard, this);
                            confirmBtn.removeEventListener('click', handleConfirm);
                            cancelBtn.removeEventListener('click', handleCancel);
                        };
                        
                        // Handle cancellation
                        const handleCancel = () => {
                            modal.classList.add('hidden');
                            this.checked = false;
                            confirmBtn.removeEventListener('click', handleConfirm);
                            cancelBtn.removeEventListener('click', handleCancel);
                        };
                        
                        confirmBtn.addEventListener('click', handleConfirm);
                        cancelBtn.addEventListener('click', handleCancel);
                    }
                }
            });
        });
    }

    // Separate function to handle the actual completion processing
    function processGoalCompletion(goalId, isCompleted, goalCard, checkbox) {
        const csrfToken = window.GoalsUI && window.GoalsUI.getCSRFToken ? window.GoalsUI.getCSRFToken() : getCSRFToken();
        
        // Remove line-through immediately when checkbox is clicked
        goalCard.classList.remove("line-through");

        fetch(`/goals/toggle-completion/${goalId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ is_completed: isCompleted }),
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (data.is_completed) {
                    goalCard.classList.add("opacity-60");
                    // Only disable the checkbox visually/interaction-wise
                    checkbox.classList.add('cursor-not-allowed');
                    checkbox.style.cursor = 'not-allowed';
                    // Hide edit and delete buttons
                    // Try multiple selectors to ensure we find the edit button
                    const editButton = goalCard.querySelector('a[data-can-edit="true"]') || 
                                     goalCard.querySelector('a[href*="edit_goal"]') ||
                                     goalCard.querySelector('a[href*="/edit/"]');
                    const deleteButton = goalCard.querySelector('.delete-goal-btn');
                    
                    // Hide edit/delete buttons for completed goals
                    
                    if (editButton) {
                        editButton.classList.add('hidden'); // Add hidden class
                        editButton.style.display = 'none'; // Ensure it's hidden
                        editButton.style.visibility = 'hidden'; // Additional hiding
                    }
                    
                    if (deleteButton) {
                        deleteButton.classList.add('hidden'); // Add hidden class
                        deleteButton.style.display = 'none'; // Ensure it's hidden
                        deleteButton.style.visibility = 'hidden'; // Additional hiding
                    }
                    // Disable the checkbox so it cannot be unchecked
                    checkbox.disabled = true;
                    checkbox.classList.add('cursor-not-allowed', 'opacity-50');
                }

                // Refresh counts/charts
                let countsUrl = new URL(window.location.origin + window.location.pathname);
                countsUrl.searchParams.set('fragment', 'counts');
                fetch(countsUrl.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(res => res.json())
                    .then(counts => { try { window.GoalsCharts && window.GoalsCharts.updateAll(counts); } catch(e){} });
            } else {
                // Show user-friendly error message
                const errorMsg = data.error || "Unknown error occurred";
                // Could use a toast notification system here instead
                alert("Error updating goal completion: " + errorMsg);
                checkbox.checked = !isCompleted; // revert
                // Keep line-through removed even if server update fails
                goalCard.classList.remove("line-through");
            }
        })
        .catch(err => {
            // Network or parsing error - log to browser console for debugging
            alert("An error occurred while updating goal completion.");
            checkbox.checked = !isCompleted;
            // Keep line-through removed even if there's an error
            goalCard.classList.remove("line-through");
        });
    }

    // Function to update list via AJAX
    function updateListAjax() {
        let url = new URL(window.location.origin + window.location.pathname);
        const selectedGoalType = goalTypeFilter ? goalTypeFilter.value : 'all';
        const selectedCompletionStatus = completionFilter ? completionFilter.value : 'all';
        if (selectedGoalType && selectedGoalType !== 'all') url.searchParams.set('goal_type', selectedGoalType);
        if (selectedCompletionStatus && selectedCompletionStatus !== 'all') url.searchParams.set('completion_status', selectedCompletionStatus);
        url.searchParams.set('fragment', 'list');

        fetch(url.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(res => res.text())
            .then(html => {
                const container = document.getElementById('goals-list-container');
                if (container) {
                    container.innerHTML = html;
                    bindCompletionCheckboxes(); // rebind checkboxes after list update
                }
            });
    }

    // Listen for filter changes
    if (goalTypeFilter) goalTypeFilter.addEventListener('change', updateListAjax);
    if (completionFilter) completionFilter.addEventListener('change', updateListAjax);

    // CSRF helper - prioritizes meta tag over cookies
    function getCSRFToken() {
        // 1. Try meta tag first (preferred method)
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag && metaTag.content) {
            return metaTag.content;
        }
        
        // 2. Try hidden input as fallback
        const inputTag = document.getElementById('csrf-token');
        if (inputTag && inputTag.value) {
            return inputTag.value;
        }
        
        // 3. Finally try cookie (legacy fallback)
        return getCookie('csrftoken');
    }
    
    // Cookie helper (used as last resort)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initial bind
    bindCompletionCheckboxes();
});

document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('viewGoalModal');
  if (!modal) return;

  const titleEl = document.getElementById('modalGoalTitle');
  const descEl = document.getElementById('modalGoalDescription');
  const notesEl = document.getElementById('modalNotes');
  const createdByEl = document.getElementById('modalGoalCreatedBy');
  const createdAtEl = document.getElementById('modalGoalCreatedAt');
  const updatedAtEl = document.getElementById('modalGoalUpdatedAt');
  const closeBtn = document.getElementById('closeViewGoalModal');

  function openModal() {
    modal.classList.remove('hidden');
  }

  function closeModal() {
    modal.classList.add('hidden');
  }

  document.body.addEventListener('click', function(e) {
    const btn = e.target.closest('.view-goal-btn');
    if (btn) {
      titleEl.textContent = btn.dataset.goalTitle || 'Goal';
      descEl.textContent = btn.dataset.goalDescription || '—';
      notesEl.textContent = btn.dataset.goalNotes || '—';
      createdByEl.textContent = btn.dataset.goalCreatedBy || '—';
      createdAtEl.textContent = btn.dataset.goalCreatedAt || '—';
      updatedAtEl.textContent = btn.dataset.goalUpdatedAt || '—';
      openModal();
    }
  });

  closeBtn && closeBtn.addEventListener('click', closeModal);

  // Close when clicking outside the modal content
  modal.addEventListener('click', function(e) {
    if (e.target === modal) closeModal();
  });

  // Escape key to close
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
  });
});
