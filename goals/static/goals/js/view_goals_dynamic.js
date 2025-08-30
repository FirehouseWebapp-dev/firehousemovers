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
                const goalCard = document.getElementById(`goal-${goalId}`);

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
                            goalCard.classList.add("opacity-60", "line-through");
                        } else {
                            goalCard.classList.remove("opacity-60", "line-through");
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
                    }
                })
                .catch(err => {
                    console.error("Error:", err);
                    alert("An error occurred while updating goal completion.");
                    checkbox.checked = !isCompleted;
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
