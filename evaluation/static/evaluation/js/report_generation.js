// Report Generation JavaScript

// Get CSRF token from meta tag or cookie
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    return getCookie('csrftoken');
}

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

// Show/hide custom date inputs based on date range selection
document.addEventListener('DOMContentLoaded', function() {
    // Employee report date range
    const empDateRange = document.getElementById('emp-date-range');
    const empCustomDates = document.getElementById('emp-custom-dates');
    
    if (empDateRange) {
        empDateRange.addEventListener('change', function() {
            if (this.value === 'custom') {
                empCustomDates.classList.remove('hidden');
            } else {
                empCustomDates.classList.add('hidden');
            }
        });
    }
    
    // Manager report date range
    const mgrDateRange = document.getElementById('mgr-date-range');
    const mgrCustomDates = document.getElementById('mgr-custom-dates');
    
    if (mgrDateRange) {
        mgrDateRange.addEventListener('change', function() {
            if (this.value === 'custom') {
                mgrCustomDates.classList.remove('hidden');
            } else {
                mgrCustomDates.classList.add('hidden');
            }
        });
    }
});

// Show loading modal
function showLoading() {
    const modal = document.getElementById('loading-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

// Hide loading modal
function hideLoading() {
    const modal = document.getElementById('loading-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Generate Employee Report
function generateEmployeeReport() {
    const form = document.getElementById('employee-report-form');
    const formData = new FormData(form);
    
    const department = formData.get('department');
    const dateRange = formData.get('date_range');
    const format = formData.get('format');
    
    let startDate = '';
    let endDate = '';
    
    if (dateRange === 'custom') {
        startDate = formData.get('start_date');
        endDate = formData.get('end_date');
        
        if (!startDate || !endDate) {
            alert('Please select both start and end dates for custom range.');
            return;
        }
    }
    
    // Build URL with parameters
    let url = '/evaluation/reports/employee-pdf/?';
    url += `department=${encodeURIComponent(department)}`;
    url += `&date_range=${encodeURIComponent(dateRange)}`;
    
    if (dateRange === 'custom') {
        url += `&start_date=${encodeURIComponent(startDate)}`;
        url += `&end_date=${encodeURIComponent(endDate)}`;
    }
    
    // Show loading
    showLoading();
    
    // Download PDF (currently only PDF is implemented)
    if (format === 'pdf') {
        // Open PDF in new window/download
        window.location.href = url;
        
        // Hide loading after a short delay
        setTimeout(() => {
            hideLoading();
        }, 1000);
    } else {
        hideLoading();
        alert(`${format.toUpperCase()} export format is not yet implemented. Currently only PDF is available.`);
    }
}

// Generate Manager Report
function generateManagerReport() {
    const form = document.getElementById('manager-report-form');
    const formData = new FormData(form);
    
    const department = formData.get('department');
    const dateRange = formData.get('date_range');
    const format = formData.get('format');
    
    let startDate = '';
    let endDate = '';
    
    if (dateRange === 'custom') {
        startDate = formData.get('start_date');
        endDate = formData.get('end_date');
        
        if (!startDate || !endDate) {
            alert('Please select both start and end dates for custom range.');
            return;
        }
    }
    
    // Build URL with parameters
    let url = '/evaluation/reports/manager-pdf/?';
    url += `department=${encodeURIComponent(department)}`;
    url += `&date_range=${encodeURIComponent(dateRange)}`;
    
    if (dateRange === 'custom') {
        url += `&start_date=${encodeURIComponent(startDate)}`;
        url += `&end_date=${encodeURIComponent(endDate)}`;
    }
    
    // Show loading
    showLoading();
    
    // Download PDF (currently only PDF is implemented)
    if (format === 'pdf') {
        // Open PDF in new window/download
        window.location.href = url;
        
        // Hide loading after a short delay
        setTimeout(() => {
            hideLoading();
        }, 1000);
    } else {
        hideLoading();
        alert(`${format.toUpperCase()} export format is not yet implemented. Currently only PDF is available.`);
    }
}

// Generate Performance Trends Report
function generateTrendsReport() {
    const form = document.getElementById('trends-report-form');
    const formData = new FormData(form);
    
    const department = formData.get('department');
    const period = formData.get('period');
    const format = formData.get('format');
    
    // Build URL with parameters
    let url = '/evaluation/reports/trends-pdf/?';
    url += `department=${encodeURIComponent(department)}`;
    url += `&period=${encodeURIComponent(period)}`;
    
    // Show loading
    showLoading();
    
    // Download PDF (currently only PDF is implemented)
    if (format === 'pdf') {
        // Open PDF in new window/download
        window.location.href = url;
        
        // Hide loading after a short delay
        setTimeout(() => {
            hideLoading();
        }, 1000);
    } else {
        hideLoading();
        alert(`${format.toUpperCase()} export format is not yet implemented. Currently only PDF is available.`);
    }
}


