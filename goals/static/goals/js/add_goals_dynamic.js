document.addEventListener('DOMContentLoaded', function() {
    const formContainer = document.getElementById('form-container');
    const addAnotherGoalBtn = document.getElementById('add-another-goal');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');
    const removeGoalModal = document.getElementById('removeGoalModal');
    const confirmRemoveGoalBtn = document.getElementById('confirmRemoveGoal');
    const cancelRemoveGoalBtn = document.getElementById('cancelRemoveGoal');
    const currentGoalCountSpan = document.getElementById('current-goal-count');
    const emptyFormDiv = document.getElementById('empty-form'); // hidden template

    // Initialize formIdx based on the total forms reported by Django management form
    let formIdx = parseInt(totalForms.value);
    // Get the initial count of existing goals from the Django template
    let existingGoalsCount = parseInt(currentGoalCountSpan.textContent);
    let newGoalsCount = formContainer.querySelectorAll('.goal-form-card').length; // This will track all new goals forms on the page, including the default empty one
    let formToRemove = null;
    // Update displayed goal count and disable add button if max reached
    function updateDisplayedGoalCount() {
        // Total count is existing goals from DB + newly added forms
        const totalCount = existingGoalsCount + newGoalsCount;
        currentGoalCountSpan.textContent = totalCount;

        if (totalCount >= 10) {
            addAnotherGoalBtn.disabled = true;
            addAnotherGoalBtn.classList.add('opacity-50', 'cursor-not-allowed');
            addAnotherGoalBtn.textContent = 'Maximum Goals Reached (10)';
        } else {
            addAnotherGoalBtn.disabled = false;
            addAnotherGoalBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            addAnotherGoalBtn.textContent = 'Add Another Goal';
        }
    }

    // Update form indices for Django
    function updateFormIndices() {
        // Only consider visible (not deleted) forms for re-indexing
        const visibleForms = Array.from(formContainer.querySelectorAll('.goal-form-card')).filter(card => card.style.display !== 'none');
        visibleForms.forEach((card, index) => {
            card.querySelectorAll('input, select, textarea, input[type="hidden"]').forEach(element => {
                if (element.id) element.id = element.id.replace(/form-\d+/, `form-${index}`);
                if (element.name) element.name = element.name.replace(/form-\d+/, `form-${index}`);
            });
            card.querySelectorAll('label').forEach(label => {
                if (label.htmlFor) label.htmlFor = label.htmlFor.replace(/form-\d+/, `form-${index}`);
            });
        });
        // Update TOTAL_FORMS to reflect the number of currently visible forms
        totalForms.value = visibleForms.length;
    }

    updateDisplayedGoalCount();
    updateFormIndices();
    
    // Ensure the initial form has proper indices
    const initialForms = formContainer.querySelectorAll('.goal-form-card');
    if (initialForms.length > 0) {
        initialForms.forEach((card, index) => {
            card.querySelectorAll('input, select, textarea, input[type="hidden"]').forEach(element => {
                if (element.name && element.name.includes('__prefix__')) {
                    element.name = element.name.replace(/__prefix__/g, index);
                }
                if (element.id && element.id.includes('__prefix__')) {
                    element.id = element.id.replace(/__prefix__/g, index);
                }
            });
            card.querySelectorAll('label').forEach(label => {
                if (label.htmlFor && label.htmlFor.includes('__prefix__')) {
                    label.htmlFor = label.htmlFor.replace(/__prefix__/g, index);
                }
            });
        });
    }

    //  Add another goal
    addAnotherGoalBtn.addEventListener('click', function() {
        // Check against the sum of existing and newly added goals
        if (existingGoalsCount + newGoalsCount >= 10) {
            alert('You can only have a maximum of 10 goals.');
            return;
        }

        const newFormHtml = emptyFormDiv.innerHTML.replace(/__prefix__/g, formIdx);
        formContainer.insertAdjacentHTML('beforeend', newFormHtml);
        
        // Update the total forms count for Django
        totalForms.value = parseInt(totalForms.value) + 1;

        formIdx++; // Increment formIdx for the next new form
        newGoalsCount++; // Only increment newGoalsCount for forms added via button
        updateFormIndices();
        updateDisplayedGoalCount();
    });

    //Handle clicks on remove buttons (delegated)
    formContainer.addEventListener('click', function(event) {
        if (event.target.closest('.remove-form-btn')) {
            formToRemove = event.target.closest('.goal-form-card');
            removeGoalModal.classList.remove('hidden');
        } else if (event.target.closest('.remove-goal-btn')) {
            formToRemove = event.target.closest('.goal-form-card');
            const goalId = event.target.closest('.remove-goal-btn').dataset.goalId;
            confirmRemoveGoalBtn.dataset.goalId = goalId;
            removeGoalModal.classList.remove('hidden');
        }
    });

    // Confirm removal
    confirmRemoveGoalBtn.addEventListener('click', function() {
        if (formToRemove) {
            const deleteInput = formToRemove.querySelector('input[name$="-DELETE"]');
            const idInput = formToRemove.querySelector('input[name$="-id"]');

            // If there's no ID input or it's empty, it's a newly added form
            if (!idInput || !idInput.value) {
                formToRemove.remove();
                newGoalsCount--; // Decrement new goal count
                formIdx--; // Also decrement formIdx if a new form is removed
            } else { // This case should ideally not happen on this page if existing goals are not rendered
                // However, for robustness, if an existing goal form were to be here and removed
                // we would mark it for deletion and decrement existingGoalsCount.
                deleteInput.value = "on";
                formToRemove.style.display = "none";
                // existingGoalsCount--; // This would be done if we were displaying existing goals.
            }
            updateFormIndices();
            updateDisplayedGoalCount();
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
});

// Handle form submission - simplified version
document.getElementById('goalsForm').addEventListener('submit', function(e) {
    // Just let the form submit normally, Django will handle validation
});
