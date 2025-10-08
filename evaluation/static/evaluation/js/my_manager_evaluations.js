// My Manager Evaluations JavaScript

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
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
});
