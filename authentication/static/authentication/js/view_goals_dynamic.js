document.addEventListener('DOMContentLoaded', function() {
    const goalTypeFilter = document.getElementById('goal-type-filter');
    const employeeId = goalTypeFilter.dataset.employeeId; // Get employeeId from data attribute

    // Handle goal type filter change
    goalTypeFilter.addEventListener('change', function() {
        const selectedGoalType = this.value;
        let url = `/goals/view/${employeeId}/`;
        if (selectedGoalType !== 'all') {
            url += `?goal_type=${selectedGoalType}`;
        }
        window.location.href = url;
    });

    // Handle goal completion checkbox change
    document.querySelectorAll('.goal-completion-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const goalId = this.dataset.goalId;
            const isCompleted = this.checked;
            const goalCard = document.getElementById(`goal-${goalId}`);

            // Fetch CSRF token from a hidden input or meta tag
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/goals/toggle-completion/${goalId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ is_completed: isCompleted })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.is_completed) {
                        goalCard.classList.add('opacity-60', 'line-through');
                    } else {
                        goalCard.classList.remove('opacity-60', 'line-through');
                    }
                    console.log('Goal completion status updated.');
                } else {
                    alert('Error updating goal completion: ' + data.error);
                    checkbox.checked = !isCompleted; // Revert checkbox state on error
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating goal completion.');
                checkbox.checked = !isCompleted; // Revert checkbox state on error
            });
        });
    });
});
