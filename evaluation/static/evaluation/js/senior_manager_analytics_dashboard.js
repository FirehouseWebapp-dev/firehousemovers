// Update last viewed time to current local time
function updateLastViewedTime() {
    const now = new Date();
    const timeElement = document.getElementById('last-viewed-time');
    if (timeElement) {
        // Format: "Sep 17, 2025 01:31"
        const options = { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        };
        const formattedTime = now.toLocaleDateString('en-US', options);
        timeElement.textContent = formattedTime;
    }
}

// View team trend - shows manager's performance dashboard
function viewTeamTrend(managerId) {
    window.location.href = `/evaluation/manager-performance/?manager_id=${managerId}`;
}

// Update time on page load to show current local time
document.addEventListener('DOMContentLoaded', function() {
    updateLastViewedTime();
});
