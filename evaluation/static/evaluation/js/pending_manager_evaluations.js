// Pending Manager Evaluations JavaScript

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Set progress bar width from data attribute
  const progressFill = document.querySelector('.progress-fill');
  if (progressFill) {
    const progress = progressFill.getAttribute('data-progress');
    if (progress) {
      progressFill.style.width = progress + '%';
    }
  }
  
  // Add hover effects to cards
  const cards = document.querySelectorAll('.card-hover');
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.borderColor = '#ef4444';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.borderColor = '#374151';
    });
  });
  
  // Add urgency animation for overdue items
  const overdueCards = document.querySelectorAll('.overdue-card');
  overdueCards.forEach(card => {
    card.style.animation = 'pulse 2s infinite';
  });
});
