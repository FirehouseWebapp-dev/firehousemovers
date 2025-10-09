// Toggle show archived filter for manager evaluation cards
function toggleShowArchived(checkbox) {
    const url = new URL(window.location.href);
    if (checkbox.checked) {
        url.searchParams.delete('show_archived'); // Default is true, so remove param
    } else {
        url.searchParams.set('show_archived', 'false');
    }
    window.location.href = url.toString();
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to show archived toggle
    const showArchivedToggle = document.getElementById('showArchivedToggle');
    if (showArchivedToggle) {
        showArchivedToggle.addEventListener('change', function() {
            toggleShowArchived(this);
        });
    }
    
    // Add event listeners to all evaluation cards
    document.querySelectorAll('.evaluation-card-clickable').forEach(card => {
        card.addEventListener('click', function() {
            const url = this.dataset.href;
            if (url) {
                window.location.href = url;
            }
        });
    });
});

