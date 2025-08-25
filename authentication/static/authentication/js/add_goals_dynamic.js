document.addEventListener('DOMContentLoaded', function() {
    const formContainer = document.getElementById('form-container');
    const addAnotherGoalBtn = document.getElementById('add-another-goal');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');
    const removeGoalModal = document.getElementById('removeGoalModal');
    const confirmRemoveGoalBtn = document.getElementById('confirmRemoveGoal');
    const cancelRemoveGoalBtn = document.getElementById('cancelRemoveGoal');
    const currentGoalCountSpan = document.getElementById('current-goal-count');

    let formIdx = parseInt(totalForms.value);
    let initialExistingGoals = parseInt(currentGoalCountSpan.textContent);
    let currentDisplayedGoals = formIdx; // Start with the number of forms loaded
    let formToRemove = null;

    // Function to update the displayed goal count
    function updateDisplayedGoalCount() {
        currentGoalCountSpan.textContent = currentDisplayedGoals;
    }

    // Function to update form indices
    function updateFormIndices() {
        Array.from(formContainer.children).forEach((card, index) => {
            card.querySelectorAll('input, select, textarea').forEach(element => {
                if (element.id) element.id = element.id.replace(/form-\d+/, `form-${index}`);
                if (element.name) element.name = element.name.replace(/form-\d+/, `form-${index}`);
            });
            // Update labels
            card.querySelectorAll('label').forEach(label => {
                if (label.htmlFor) label.htmlFor = label.htmlFor.replace(/form-\d+/, `form-${index}`);
            });
        });
    }

    // Initial display update
    updateDisplayedGoalCount();

    // Function to add a new form
    addAnotherGoalBtn.addEventListener('click', function() {
        if (currentDisplayedGoals >= 10) {
            alert('You can only add a maximum of 10 goals.');
            return;
        }

        const newFormHtml = `
            <div class="goal-form-card bg-[#2a2a2a] p-6 rounded-2xl shadow-lg mb-6 relative">
                <button type="button" class="remove-form-btn absolute top-4 right-4 text-gray-400 hover:text-red-500">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
                <div class="grid grid-cols-1 gap-6 mb-6">
                    <div>
                        <label for="id_form-${formIdx}-goal_type" class="block text-white font-semibold mb-2">Goal Type</label>
                        <select name="form-${formIdx}-goal_type" id="id_form-${formIdx}-goal_type" class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:border-red-500">
                            <option value="short_term">Short-Term</option>
                            <option value="long_term">Long-Term</option>
                        </select>
                    </div>
                    <div>
                        <label for="id_form-${formIdx}-title" class="block text-white font-semibold mb-2">Goal Title</label>
                        <input type="text" name="form-${formIdx}-title" id="id_form-${formIdx}-title" class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500" placeholder="Goal title">
                    </div>
                    <div>
                        <label for="id_form-${formIdx}-description" class="block text-white font-semibold mb-2">Goal Description</label>
                        <textarea name="form-${formIdx}-description" id="id_form-${formIdx}-description" rows="3" class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none" placeholder="Detailed description of the goal"></textarea>
                    </div>
                    <div>
                        <label for="id_form-${formIdx}-notes" class="block text-white font-semibold mb-2">Action Plans For Improvement</label>
                        <textarea name="form-${formIdx}-notes" id="id_form-${formIdx}-notes" rows="3" class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-red-500 resize-none" placeholder="Additional notes or comments"></textarea>
                    </div>
                    <input type="hidden" name="form-${formIdx}-DELETE" id="id_form-${formIdx}-DELETE" value="off">
                </div>
            </div>
        `;
        formContainer.insertAdjacentHTML('beforeend', newFormHtml);
        formIdx++;
        totalForms.value = formIdx;
        currentDisplayedGoals++;
        updateDisplayedGoalCount();
    });

    // Event delegation for removing forms
    formContainer.addEventListener('click', function(event) {
        if (event.target.closest('.remove-form-btn')) {
            formToRemove = event.target.closest('.goal-form-card');
            removeGoalModal.classList.remove('hidden');
        } else if (event.target.closest('.remove-goal-btn')) {
            formToRemove = event.target.closest('.goal-form-card');
            const goalId = event.target.closest('.remove-goal-btn').dataset.goalId;
            confirmRemoveGoalBtn.dataset.goalId = goalId; // Store goal ID for confirmation
            removeGoalModal.classList.remove('hidden');
        }
    });

    // Confirm removal
    confirmRemoveGoalBtn.addEventListener('click', function() {
        if (formToRemove) {
            const goalId = confirmRemoveGoalBtn.dataset.goalId;
            if (goalId) {
                // If it's an existing goal, submit a POST request to delete it
                fetch(`{% url 'authentication:remove_goal' 0 %}`.replace('0', goalId), {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        formToRemove.remove();
                        formIdx--;
                        totalForms.value = formIdx;
                        currentDisplayedGoals--; // Decrement displayed count for existing goal
                        updateFormIndices();
                        updateDisplayedGoalCount();
                        // Optionally, show a success message
                        // window.location.reload(); // Reload to update existing goals count
                    } else {
                        alert('Error removing goal.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error removing goal.');
                });

            } else {
                // If it's a new form, just remove it from the DOM
                formToRemove.remove();
                formIdx--;
                totalForms.value = formIdx;
                currentDisplayedGoals--; // Decrement displayed count for new form
                updateFormIndices();
                updateDisplayedGoalCount();
            }
            removeGoalModal.classList.add('hidden');
            formToRemove = null;
            confirmRemoveGoalBtn.removeAttribute('data-goal-id');
        }
    });

    // Cancel removal
    cancelRemoveGoalBtn.addEventListener('click', function() {
        removeGoalModal.classList.add('hidden');
        formToRemove = null;
        confirmRemoveGoalBtn.removeAttribute('data-goal-id');
    });

    // Initial setup for existing forms
    updateFormIndices();
});
