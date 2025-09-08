// Drag and Drop functionality for questions
document.addEventListener('DOMContentLoaded', function() {
    const questionList = document.getElementById('q-list');
    
    if (!questionList) return;
    
    // Make questions sortable
    let draggedElement = null;
    
    // Add event listeners to all question items
    function addDragListeners() {
        const questionItems = questionList.querySelectorAll('.q-item');
        
        questionItems.forEach(item => {
            const dragHandle = item.querySelector('.drag');
            
            // Make the entire item draggable
            item.draggable = true;
            
            // Add visual feedback
            item.addEventListener('dragstart', function(e) {
                draggedElement = this;
                this.style.opacity = '0.5';
                this.classList.add('dragging');
                
                // Set drag data
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.outerHTML);
            });
            
            item.addEventListener('dragend', function(e) {
                this.style.opacity = '1';
                this.classList.remove('dragging');
                draggedElement = null;
            });
            
            item.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                
                // Add visual indicator
                this.classList.add('drag-over');
            });
            
            item.addEventListener('dragleave', function(e) {
                this.classList.remove('drag-over');
            });
            
            item.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                
                if (draggedElement && draggedElement !== this) {
                    // Get the position to insert
                    const rect = this.getBoundingClientRect();
                    const midpoint = rect.top + rect.height / 2;
                    const mouseY = e.clientY;
                    
                    if (mouseY < midpoint) {
                        // Insert before this element
                        questionList.insertBefore(draggedElement, this);
                    } else {
                        // Insert after this element
                        questionList.insertBefore(draggedElement, this.nextSibling);
                    }
                    
                    // Update question order in database
                    updateQuestionOrder();
                }
            });
        });
    }
    
    // Function to update question order in database
    function updateQuestionOrder() {
        const questionItems = questionList.querySelectorAll('.q-item');
        const questionIds = [];
        
        questionItems.forEach((item, index) => {
            // Extract question ID from the edit link
            const editLink = item.querySelector('a[href*="question_edit"]');
            if (editLink) {
                const href = editLink.getAttribute('href');
                const questionId = href.match(/question_edit\/(\d+)/);
                if (questionId) {
                    questionIds.push({
                        id: questionId[1],
                        order: index + 1
                    });
                }
            }
        });
        
        // Send AJAX request to update order
        fetch(window.location.href + 'update_order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                question_orders: questionIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Question order updated successfully');
                // Show success message
                showMessage('Question order updated successfully!', 'success');
            } else {
                console.error('Failed to update question order');
                showMessage('Failed to update question order', 'error');
            }
        })
        .catch(error => {
            console.error('Error updating question order:', error);
            showMessage('Error updating question order', 'error');
        });
    }
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Function to show messages
    function showMessage(message, type) {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
            type === 'success' ? 'bg-green-600' : 'bg-red-600'
        }`;
        messageDiv.textContent = message;
        
        // Add to page
        document.body.appendChild(messageDiv);
        
        // Remove after 3 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
    
    // Initialize drag and drop
    addDragListeners();
    
    // Re-initialize when new questions are added (if needed)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                addDragListeners();
            }
        });
    });
    
    observer.observe(questionList, {
        childList: true,
        subtree: true
    });
});
