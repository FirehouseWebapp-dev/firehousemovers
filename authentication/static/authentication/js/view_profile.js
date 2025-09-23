// View Profile page JavaScript functionality

// Initialize view profile page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add any view profile specific functionality here
    console.log('View Profile page JavaScript loaded');
    
    // Add hover effects for profile images
    const profileImages = document.querySelectorAll('img[alt*="Picture"], img[alt*="Profile"]');
    profileImages.forEach(img => {
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});
