document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('viewGoalModal');
  
  // Handle filter form submissions for My Goals section
  var goalTypeSelectMyGoals = document.getElementById('goalTypeSelectMyGoals');
  var filterSelectMyGoals = document.getElementById('filterSelectMyGoals');
  var filterFormMyGoals = document.getElementById('filterFormMyGoals');
  var closeGoalModalBtnMyGoals = document.getElementById('closeGoalModalBtnMyGoals');

  if (goalTypeSelectMyGoals && filterFormMyGoals) {
    goalTypeSelectMyGoals.addEventListener('change', function() {
      filterFormMyGoals.submit();
    });
  }

  if (filterSelectMyGoals && filterFormMyGoals) {
    filterSelectMyGoals.addEventListener('change', function() {
      filterFormMyGoals.submit();
    });
  }

  // Handle close modal button click for My Goals
  if (closeGoalModalBtnMyGoals && window.GoalsUI && window.GoalsUI.closeGoalModal) {
    closeGoalModalBtnMyGoals.addEventListener('click', function() {
      window.GoalsUI.closeGoalModal();
    });
  }

  // Original modal logic (if it exists)
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
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeModal();
    });
  }

  // Escape key to close
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
  });
});
