document.addEventListener('DOMContentLoaded', function() {
  var deleteConfirmationModal = document.getElementById('deleteConfirmationModal');
  var confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  var cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
  var deleteGoalForm = document.getElementById('deleteGoalForm');
  var deleteGoalIdInput = document.getElementById('deleteGoalId');
  var goalsListContainer = document.getElementById('goals-list-container');

  if (!goalsListContainer || !deleteConfirmationModal || !deleteGoalForm) return;

  goalsListContainer.addEventListener('click', function(event) {
    var deleteButton = event.target.closest('.delete-goal-btn');
    if (deleteButton) {
      var goalCard = deleteButton.closest('.goal-card-item');
      if (goalCard && goalCard.classList.contains('opacity-60')) {
        return;
      }
      var goalId = deleteButton.dataset.goalId;
      deleteGoalIdInput.value = goalId;
      deleteGoalForm.action = deleteGoalForm.action || window.location.origin + '/goals/remove/' + goalId + '/';
      deleteConfirmationModal.classList.remove('hidden');
    }
  });

  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', function() {
      deleteGoalForm.submit();
    });
  }

  if (cancelDeleteBtn) {
    cancelDeleteBtn.addEventListener('click', function() {
      deleteConfirmationModal.classList.add('hidden');
      deleteGoalIdInput.value = '';
    });
  }
});
