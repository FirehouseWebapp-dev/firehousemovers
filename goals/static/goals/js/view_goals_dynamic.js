document.addEventListener('DOMContentLoaded', function() {
    const goalTypeFilter = document.getElementById('goal-type-filter');
    const completionFilter = document.getElementById('completion-filter');
    const employeeId = goalTypeFilter ? goalTypeFilter.dataset.employeeId : (completionFilter ? completionFilter.dataset.employeeId : null);

    // Function to bind checkbox events
    function bindCompletionCheckboxes() {
        const csrfTokenInput = document.getElementById('csrf-token');
        const csrfToken = csrfTokenInput ? csrfTokenInput.value : getCookie("csrftoken");

        document.querySelectorAll(".goal-completion-checkbox").forEach(checkbox => {
            checkbox.addEventListener("change", function () {
                const goalId = this.dataset.goalId;
                const isCompleted = this.checked;
                const goalCard = document.getElementById(`goal-${goalId }`);
                
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
                            // Hide edit and delete buttons
                            const editButton = goalCard.querySelector('a[href*="edit_goal"]');
                            const deleteButton = goalCard.querySelector('.delete-goal-btn');
                            if (editButton) {
                                editButton.classList.add('hidden'); // Add hidden class
                            }
                            if (deleteButton) {
                                deleteButton.classList.add('hidden'); // Add hidden class
                            }
                        } else {
                            goalCard.classList.remove("opacity-60");
                            // Show edit and delete buttons
                            const editButton = goalCard.querySelector('a[href*="edit_goal"]');
                            const deleteButton = goalCard.querySelector('.delete-goal-btn');
                            if (editButton && editButton.dataset.canEdit === 'true') {
                                editButton.classList.remove('hidden'); // Remove hidden class
                            }
                            if (deleteButton && deleteButton.dataset.canDelete === 'true') {
                                deleteButton.classList.remove('hidden'); // Remove hidden class
                            }
                        }

                        // Refresh counts/charts
                        let countsUrl = new URL(window.location.origin + window.location.pathname);
                        countsUrl.searchParams.set('fragment', 'counts');
                        fetch(countsUrl.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                            .then(res => res.json())
                            .then(counts => { try { window.GoalsCharts && window.GoalsCharts.updateAll(counts); } catch(e){} });
                    } else {
                        alert("Error updating goal completion: " + data.error);
                        checkbox.checked = !isCompleted; // revert
                        // Keep line-through removed even if server update fails
                        goalCard.classList.remove("line-through");
                    }
                })
                .catch(err => {
                    console.error("Error:", err);
                    alert("An error occurred while updating goal completion.");
                    checkbox.checked = !isCompleted;
                    // Keep line-through removed even if there's an error
                    goalCard.classList.remove("line-through");
                });
            });
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

    // CSRF helper
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
  const notesEl = document.getElementById('modalGoalNotes');
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
