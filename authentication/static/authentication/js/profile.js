// Profile page JavaScript functionality

// Smooth scroll to profile section
function scrollToProfile() {
    const profileSection = document.getElementById('profile');
    if (profileSection) {
        profileSection.scrollIntoView({behavior: 'smooth'});
    }
}

// Initialize profile page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to edit profile button
    const editProfileBtn = document.getElementById('edit-profile-btn');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', scrollToProfile);
    }
    
    // Add any other profile-specific initialization here
    console.log('Profile page JavaScript loaded');
});
