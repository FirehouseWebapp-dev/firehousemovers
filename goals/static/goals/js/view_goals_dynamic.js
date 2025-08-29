document.addEventListener('DOMContentLoaded', function() {
    const goalTypeFilter = document.getElementById('goal-type-filter');
    const completionFilter = document.getElementById('completion-filter');
    const employeeId = goalTypeFilter ? goalTypeFilter.dataset.employeeId : (completionFilter ? completionFilter.dataset.employeeId : null);

    if (employeeId) {
        // Function to update the URL based on selected filters
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
                    if (container) container.innerHTML = html;
                })
                .catch(err => console.error('Filter update error:', err));

            // Also refresh counts for charts
            let countsUrl = new URL(window.location.origin + window.location.pathname);
            if (selectedGoalType && selectedGoalType !== 'all') countsUrl.searchParams.set('goal_type', selectedGoalType);
            if (selectedCompletionStatus && selectedCompletionStatus !== 'all') countsUrl.searchParams.set('completion_status', selectedCompletionStatus);
            countsUrl.searchParams.set('fragment', 'counts');
            fetch(countsUrl.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(res => res.json())
                .then(data => { try { window.GoalsCharts && window.GoalsCharts.updateAll(data); } catch(e){} })
                .catch(err => console.error('Counts update error:', err));
        }

        // Event listeners for filter changes
        if (goalTypeFilter) {
            goalTypeFilter.addEventListener('change', updateListAjax);
        }
        if (completionFilter) {
            completionFilter.addEventListener('change', updateListAjax);
        }
    }

    // Function to read CSRF token from hidden input or cookies
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
const csrfTokenInput = document.getElementById('csrf-token');
const csrfToken = csrfTokenInput ? csrfTokenInput.value : getCookie("csrftoken");

// Handle goal completion checkbox change
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
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                if (data.is_completed) {
                    goalCard.classList.add("opacity-60", "line-through");
                } else {
                    goalCard.classList.remove("opacity-60", "line-through");
                }
                // Update completion donuts in real-time without reload
                // Refresh counts and charts after toggle
                try {
                    let countsUrl = new URL(window.location.origin + window.location.pathname);
                    countsUrl.searchParams.set('fragment', 'counts');
                    fetch(countsUrl.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                        .then(res => res.json())
                        .then(counts => { try { window.GoalsCharts && window.GoalsCharts.updateAll(counts); } catch(e){} });
                } catch (e) {}
            } else {
                alert("Error updating goal completion: " + data.error);
                checkbox.checked = !isCompleted; // revert
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while updating goal completion.");
            checkbox.checked = !isCompleted; // revert
        });
    });
});
});
