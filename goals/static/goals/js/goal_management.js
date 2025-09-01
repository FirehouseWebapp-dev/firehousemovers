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
