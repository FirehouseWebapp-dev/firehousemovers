document.addEventListener('DOMContentLoaded', function() {
  // Enable all form fields
  const formFields = document.querySelectorAll('input, textarea, select');
  
  formFields.forEach(function(field) {
    // Remove disabled attribute if present
    field.removeAttribute('disabled');
    field.removeAttribute('readonly');
    
    // Add focus styling
    field.addEventListener('focus', function() {
      this.style.borderColor = '#ef4444';
    });
    
    field.addEventListener('blur', function() {
      this.style.borderColor = '#2b2b2b';
      this.style.boxShadow = 'none';
    });
  });
  
  // Handle Yes/No button clicks for boolean fields
  const boolContainers = document.querySelectorAll('.fh-bool');
  
  boolContainers.forEach(function(container) {
    const radioInputs = container.querySelectorAll('input[type="radio"]');
    
    radioInputs.forEach(function(radio) {
      radio.addEventListener('change', function() {
        // Visual feedback for selection
        const labels = container.querySelectorAll('label');
        labels.forEach(label => {
          label.style.background = 'transparent';
          label.style.color = '#ef4444';
          label.style.borderStyle = 'dashed';
        });
        
        const selectedLabel = this.nextElementSibling;
        selectedLabel.style.background = '#ef4444';
        selectedLabel.style.color = 'white';
        selectedLabel.style.borderStyle = 'solid';
      });
    });
  });
});
