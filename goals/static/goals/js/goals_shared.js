(function(){
  function capitalizeFirstLetter(str) {
    if (!str) return str;
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function toTitleCase(str) {
    if (!str) return str;
    return str.replace(/\w\S*/g, function(txt){
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
  }

  function getEl(id) { return document.getElementById(id); }

  function populateModal(goalData) {
    var titleEl = getEl('modalTitle');
    var goalTypeEl = getEl('modalGoalType');
    var statusEl = getEl('modalStatus');
    var descEl = getEl('modalDescription');
    var notesEl = getEl('modalNotes');
    var notesSectionEl = getEl('modalNotesSection');
    var createdByEl = getEl('modalCreatedBy');
    var createdAtEl = getEl('modalCreatedAt');
    var updatedAtEl = getEl('modalUpdatedAt');
    var dueDateSection = getEl('modalDueDateSection');
    var dueDateEl = getEl('modalDueDate');
    var completedSection = getEl('modalCompletedSection');
    var completedAtEl = getEl('modalCompletedAt');

    if (titleEl) titleEl.textContent = toTitleCase(goalData.title);
    if (goalTypeEl) goalTypeEl.textContent = goalData.goal_type || '';
    if (descEl) descEl.textContent = capitalizeFirstLetter(goalData.description) || 'No description provided.';
    
    // Handle notes/action plans
    if (notesEl && notesSectionEl) {
      if (goalData.notes && goalData.notes.trim()) {
        notesEl.textContent = capitalizeFirstLetter(goalData.notes);
        notesSectionEl.style.display = 'block';
      } else {
        notesEl.textContent = 'No action plans specified.';
        notesSectionEl.style.display = 'block';
      }
    }
    
    if (createdByEl) createdByEl.textContent = toTitleCase(goalData.created_by || '');
    if (createdAtEl) createdAtEl.textContent = goalData.created_at || '';
    if (updatedAtEl) updatedAtEl.textContent = goalData.updated_at || '';

    if (statusEl) {
      if (goalData.is_completed) {
        statusEl.textContent = 'Completed';
        statusEl.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-green-600 text-white';
      } else {
        statusEl.textContent = 'Pending';
        statusEl.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-yellow-600 text-white';
      }
    }

    if (dueDateEl && dueDateSection) {
      if (goalData.due_date) {
        dueDateEl.textContent = goalData.due_date;
        dueDateSection.style.display = 'block';
      } else {
        dueDateEl.textContent = 'No due date set';
        dueDateSection.style.display = 'block';
      }
    }

    if (completedSection && completedAtEl) {
      if (goalData.is_completed && goalData.completed_at) {
        completedAtEl.textContent = goalData.completed_at;
        completedSection.classList.remove('hidden');
      } else {
        completedSection.classList.add('hidden');
      }
    }
  }

  function readGoalData(goalId) {
    var scriptEl = getEl('goal-data-' + goalId);
    if (!scriptEl) return null;
    try {
      return JSON.parse(scriptEl.textContent);
    } catch (e) {
      // JSON parsing error - return null to handle gracefully
      return null;
    }
  }

  function openGoalModal(goalId) {
    var data = typeof goalId === 'object' && goalId !== null ? goalId : readGoalData(goalId);
    if (!data) return;

    var modal = getEl('goalModal');
    if (!modal) return;

    populateModal(data);
    modal.classList.remove('hidden');
    try { document.body.style.overflow = 'hidden'; } catch(_){ }
  }

  function closeGoalModal() {
    var modal = getEl('goalModal');
    if (!modal) return;
    modal.classList.add('hidden');
    try { document.body.style.overflow = 'auto'; } catch(_){ }
  }

  function attachModalCloseHandlers() {
    var modal = getEl('goalModal');
    if (!modal) return;

    modal.addEventListener('click', function(e){
      if (e.target === modal) closeGoalModal();
    });

    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape') closeGoalModal();
    });
  }

  function attachCardClickHandlers() {
    var cards = document.querySelectorAll('.goal-card');
    if (!cards || !cards.length) return;
    cards.forEach(function(card){
      card.addEventListener('click', function(){
        var gid = card.getAttribute('data-goal-id');
        if (gid) openGoalModal(gid);
      });
    });
  }

  function calculateProgress() {
    var progressBar = getEl('progress-bar');
    var progressText = getEl('progress-text');
    var progressStats = getEl('progress-stats');

    if (!progressBar || !progressText || !progressStats) return;

    // Prefer server-provided percentage if available
    var datasetPercent = progressBar.dataset ? progressBar.dataset.progress : null;
    if (datasetPercent) {
      progressBar.style.width = datasetPercent + '%';
      progressText.textContent = datasetPercent + '%';
      return;
    }

    var cards = document.querySelectorAll('.goal-card');
    var total = cards.length;
    var completed = 0;
    cards.forEach(function(card){
      if (card.dataset && card.dataset.isCompleted === 'true') completed++;
    });

    var pct = total > 0 ? Math.round((completed / total) * 100) : 0;
    progressBar.style.width = pct + '%';
    progressText.textContent = pct + '%';
    if (progressStats) progressStats.textContent = completed + ' of ' + total + ' goals completed';
  }

  function init() {
    attachCardClickHandlers();
    attachModalCloseHandlers();
    calculateProgress();
  }

  // Expose API
  window.GoalsUI = {
    openGoalModal: openGoalModal,
    closeGoalModal: closeGoalModal,
    attachCardClickHandlers: attachCardClickHandlers,
    calculateProgress: calculateProgress,
    getCSRFToken: getCSRFToken,
    init: init
  };
  
  // CSRF helper - prioritizes meta tag over cookies
  function getCSRFToken() {
    // 1. Try meta tag first (preferred method)
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag && metaTag.content) {
      return metaTag.content;
    }
    
    // 2. Try hidden input as fallback
    const inputTag = document.getElementById('csrf-token');
    if (inputTag && inputTag.value) {
      return inputTag.value;
    }
    
    // 3. Finally try cookie (legacy fallback)
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === "csrftoken=") {
          return decodeURIComponent(cookie.substring(10));
        }
      }
    }
    return null;
  }

  document.addEventListener('DOMContentLoaded', init);
})();
