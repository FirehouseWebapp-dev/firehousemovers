document.addEventListener('DOMContentLoaded', function() {
    const formContainer = document.getElementById('form-container');
    const addAnotherGoalBtn = document.getElementById('add-another-goal');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');
    const removeGoalModal = document.getElementById('removeGoalModal');
    const confirmRemoveGoalBtn = document.getElementById('confirmRemoveGoal');
    const cancelRemoveGoalBtn = document.getElementById('cancelRemoveGoal');
    const currentGoalCountSpan = document.getElementById('current-goal-count');
    const emptyFormDiv = document.getElementById('empty-form'); // hidden template

    // Early exit if critical elements are missing
    if (!formContainer || !addAnotherGoalBtn || !totalForms || !currentGoalCountSpan || !emptyFormDiv) {
        // Critical DOM elements not found - cannot initialize dynamic forms
        return;
    }

    // Get the initial count of existing goals from the Django template
    let existingGoalsCount = parseInt(currentGoalCountSpan.textContent);
    let formToRemove = null;
    // Get current form count from DOM (single source of truth)
    function getCurrentFormCount() {
        const allCards = formContainer.querySelectorAll('.goal-form-card');
        const visibleCards = Array.from(allCards).filter(card => card.style.display !== 'none');
        return visibleCards.length;
    }

    // Update displayed goal count and disable add button if max reached
    function updateDisplayedGoalCount() {
        const currentForms = getCurrentFormCount();
        const totalCount = existingGoalsCount + currentForms;
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

    // Update form indices for Django (single source of truth)
    function updateFormIndices() {
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
        // Update TOTAL_FORMS to reflect the number of currently visible forms (single source of truth)
        totalForms.value = visibleForms.length;
    }

    // Fix initial form prefix issues first - this is critical!
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
    
    // Also fix any remaining __prefix__ in the entire container
    formContainer.querySelectorAll('*[name*="__prefix__"], *[id*="__prefix__"], *[for*="__prefix__"]').forEach(element => {
        if (element.name && element.name.includes('__prefix__')) {
            element.name = element.name.replace(/__prefix__/g, '0');
        }
        if (element.id && element.id.includes('__prefix__')) {
            element.id = element.id.replace(/__prefix__/g, '0');
        }
        if (element.htmlFor && element.htmlFor.includes('__prefix__')) {
            element.htmlFor = element.htmlFor.replace(/__prefix__/g, '0');
        }
    });
    
    updateDisplayedGoalCount();
    updateFormIndices();

    //  Add another goal
    addAnotherGoalBtn.addEventListener('click', function() {
        // Check against the sum of existing and current forms
        const currentForms = getCurrentFormCount();
        if (existingGoalsCount + currentForms >= 10) {
            // Show user-friendly error message
            alert('You can only have a maximum of 10 goals.');
            return;
        }

        // Use current form count as the next index (single source of truth)
        const nextFormIndex = currentForms;
        const newFormHtml = emptyFormDiv.innerHTML.replace(/__prefix__/g, nextFormIndex);
        formContainer.insertAdjacentHTML('beforeend', newFormHtml);
        
        // Update indices and counts - DOM is now the single source of truth
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
            } else {
                // Existing goal form - mark for deletion
                deleteInput.value = "on";
                formToRemove.style.display = "none";
            }
            
            // Update everything - DOM count is single source of truth
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

    // Handle form submission with validation
    document.getElementById('goalsForm').addEventListener('submit', function(e) {
        // Check if at least one form has data
        const formCards = formContainer.querySelectorAll('.goal-form-card:not([style*="display: none"])');
        let hasValidForm = false;
        
        for (let card of formCards) {
            const titleInput = card.querySelector('input[name$="-title"]');
            const descriptionInput = card.querySelector('textarea[name$="-description"]');
            
            if (titleInput && titleInput.value.trim() && descriptionInput && descriptionInput.value.trim()) {
                hasValidForm = true;
                break;
            }
        }
        
        if (!hasValidForm) {
            e.preventDefault();
            // Show validation error to user
            alert('Please fill in at least one goal with both title and description.');
            return false;
        }
        
        // Update form indices one final time before submission
        updateFormIndices();
        
        // Let the form submit normally
        return true;
    });
});
