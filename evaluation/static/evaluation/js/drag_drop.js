// Drag and Drop functionality for questions
document.addEventListener('DOMContentLoaded', function() {
    const questionList = document.getElementById('q-list');
    if (!questionList) return;

    let draggedElement = null;
    let orderUpdateTimeout = null; // debounce timer

    // Add event listeners to all question items
    function addDragListeners() {
        const questionItems = questionList.querySelectorAll('.q-item');

        questionItems.forEach(item => {
            item.draggable = true;

            item.addEventListener('dragstart', function(e) {
                draggedElement = this;
                this.style.opacity = '0.5';
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.outerHTML);
            });

            item.addEventListener('dragend', function() {
                this.style.opacity = '1';
                this.classList.remove('dragging');
                draggedElement = null;
            });

            item.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
            });

            item.addEventListener('dragleave', function() {
                this.classList.remove('drag-over');
            });

            item.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');

                if (draggedElement && draggedElement !== this) {
                    const rect = this.getBoundingClientRect();
                    const midpoint = rect.top + rect.height / 2;
                    const mouseY = e.clientY;

                    if (mouseY < midpoint) {
                        questionList.insertBefore(draggedElement, this);
                    } else {
                        questionList.insertBefore(draggedElement, this.nextSibling);
                    }

                    // Debounced order update
                    scheduleUpdateOrder();
                }
            });
        });
    }

    // Debounce wrapper
    function scheduleUpdateOrder() {
        if (orderUpdateTimeout) clearTimeout(orderUpdateTimeout);
        orderUpdateTimeout = setTimeout(() => {
            updateQuestionOrder();
        }, 400); // wait 400ms after last drag
    }

    // Function to update question order in database
    function updateQuestionOrder() {
        const questionItems = questionList.querySelectorAll('.q-item');
        const questionIds = [];

        questionItems.forEach((item, index) => {
            let editLink = item.querySelector('a[title="Edit Question"]')
                || item.querySelector('a[href*="question_edit"]')
                || item.querySelector('a[href*="/edit/"]');

            if (editLink) {
                const href = editLink.getAttribute('href');
                let questionId = href.match(/questions\/(\d+)\/edit/)
                    || href.match(/question_edit\/(\d+)/)
                    || href.match(/\/(\d+)\/edit/);

                if (questionId) {
                    questionIds.push({
                        id: questionId[1],
                        order: index
                    });

                    const orderInput = item.querySelector('input[name*="order"]');
                    if (orderInput) orderInput.value = index;
                }
            }
        });

        fetch(window.location.href + 'update_order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ question_orders: questionIds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Question order updated successfully!', 'success');
            } else {
                showMessage('Failed to update question order: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(() => {
            showMessage('Error updating question order', 'error');
        });
    }

    // Helper: Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Helper: Show message
    function showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
            type === 'success' ? 'bg-green-600' : 'bg-red-600'
        }`;
        messageDiv.textContent = message;
        document.body.appendChild(messageDiv);
        setTimeout(() => messageDiv.remove(), 3000);
    }

    // Initialize
    addDragListeners();

    // Re-initialize when new questions are added dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(mutation => {
            if (mutation.type === 'childList') {
                addDragListeners();
            }
        });
    });

    observer.observe(questionList, { childList: true, subtree: true });
});
