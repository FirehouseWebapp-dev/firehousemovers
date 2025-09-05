// static/goals/js/delete_goal.js
document.addEventListener('DOMContentLoaded', function () {
  var modal = document.getElementById('deleteConfirmationModal');
  var confirmBtn = document.getElementById('confirmDeleteBtn');
  var cancelBtn = document.getElementById('cancelDeleteBtn');
  var form = document.getElementById('deleteGoalForm');
  var hiddenId = document.getElementById('deleteGoalId');
  var listContainer = document.getElementById('goals-list-container');

  // Required elements not present → do nothing
  if (!modal || !confirmBtn || !cancelBtn || !form || !hiddenId || !listContainer) return;

  // Delegate clicks from the list container (works after AJAX refreshes)
  listContainer.addEventListener('click', function (event) {
    var btn = event.target.closest('.delete-goal-btn');
    if (!btn) return;

    // If the card is visually marked as completed, ignore delete
    var card = btn.closest('.goal-card-item');
    if (card && card.classList.contains('opacity-60')) return;

    var goalId = btn.dataset.goalId;
    if (!goalId) return;

    // Set hidden input and form action explicitly every time
    hiddenId.value = goalId;
    var url = btn.dataset.url || ('/goals/remove/' + goalId + '/'); // prefers data-url from template
    form.setAttribute('action', url);

    // Show modal
    modal.classList.remove('hidden');
  });

  // Confirm deletion
  confirmBtn.addEventListener('click', function () {
    // Safety: ensure action targets /goals/remove/<id>/
    var action = form.getAttribute('action') || '';
    if (!/\/goals\/remove\/\d+\/$/.test(action)) {
      form.setAttribute('action', '/goals/remove/' + (hiddenId.value || '') + '/');
    }
    form.submit();
  });

  // Cancel deletion
  cancelBtn.addEventListener('click', function () {
    modal.classList.add('hidden');
    hiddenId.value = '';
    form.setAttribute('action', '');
  });

  // Close when clicking outside modal content
  modal.addEventListener('click', function (e) {
    if (e.target === modal) {
      cancelBtn.click();
    }
  });

  // Escape key closes modal
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      cancelBtn.click();
    }
  });
});
