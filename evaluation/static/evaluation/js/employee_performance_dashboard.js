// Employee Performance Dashboard JavaScript
// This file contains all the chart initialization and dashboard functionality with lazy loading

// Chart instances for performance charts
let performanceCharts = {};

// Lazy loading state for performance charts
let performanceChartObserver = null;
let performanceChartsToLoad = new Set();

// Clean up function to reset state on page reload
function cleanupPerformanceCharts() {
    try {
        // Destroy existing chart instances
        Object.values(performanceCharts).forEach(chart => {
            try {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            } catch (error) {
                console.error('Error destroying chart:', error);
            }
        });
        
        // Clear chart instances
        performanceCharts = {};
        
        // Disconnect observer if it exists
        if (performanceChartObserver) {
            try {
                performanceChartObserver.disconnect();
                performanceChartObserver = null;
            } catch (error) {
                console.error('Error disconnecting observer:', error);
            }
        }
        
        // Clear charts to load set
        performanceChartsToLoad.clear();
        
        // Remove any existing loading placeholders
        try {
            document.querySelectorAll('.chart-loading-placeholder').forEach(placeholder => {
                try {
                    placeholder.remove();
                } catch (error) {
                    console.error('Error removing placeholder:', error);
                }
            });
        } catch (error) {
            console.error('Error querying loading placeholders:', error);
        }
    } catch (error) {
        console.error('Error in cleanupPerformanceCharts:', error);
    }
}

// Add CSS for loading placeholders (only if not already added)
try {
    if (!document.getElementById('employee-performance-dashboard-styles')) {
        const style = document.createElement('style');
        style.id = 'employee-performance-dashboard-styles';
        style.textContent = `
            .chart-loading-placeholder {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 300px;
                background: rgba(31, 41, 55, 0.5);
                border-radius: 8px;
                border: 1px solid rgba(75, 85, 99, 0.3);
            }
            
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 4px solid rgba(75, 85, 99, 0.3);
                border-top: 4px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 16px;
            }
            
            .loading-text {
                color: #9ca3af;
                font-size: 14px;
                font-weight: 500;
            }
            
            .chart-container {
                position: relative;
            }
            
            .fade-out {
                opacity: 0;
                transition: opacity 0.3s ease-out;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
} catch (error) {
    console.error('Error adding dashboard styles:', error);
}

// Initialize when DOM is ready and data is available
function initializeEmployeePerformanceDashboard() {
    try {
        // Clean up any existing charts first
        cleanupPerformanceCharts();
        
        // Wait for employee performance data to be available
        if (window.employeePerformanceData && Object.keys(window.employeePerformanceData).length > 0) {
            console.log('Initializing employee performance dashboard with data:', window.employeePerformanceData);
            setupPerformanceChartsLazyLoading();
            updateLastViewedTime();
        } else {
            // Retry after a short delay if data isn't ready yet
            console.log('Waiting for employee performance data...');
            setTimeout(initializeEmployeePerformanceDashboard, 100);
        }
    } catch (error) {
        console.error('Error initializing employee performance dashboard:', error);
        // Retry after a longer delay on error
        setTimeout(initializeEmployeePerformanceDashboard, 500);
    }
}

// Try to initialize immediately if DOM is already loaded
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeEmployeePerformanceDashboard);
    } else {
        // DOM is already loaded
        initializeEmployeePerformanceDashboard();
    }
} catch (error) {
    console.error('Error setting up DOM ready listener:', error);
}

// Handle page visibility changes to prevent issues on reload
document.addEventListener('visibilitychange', function() {
    try {
        if (document.hidden) {
            // Page is hidden, clean up resources
            if (performanceChartObserver) {
                performanceChartObserver.disconnect();
            }
        } else {
            // Page is visible again, reinitialize if needed
            if (Object.keys(performanceCharts).length === 0 && window.employeePerformanceData) {
                initializeEmployeePerformanceDashboard();
            }
        }
    } catch (error) {
        console.error('Error handling visibility change:', error);
    }
});

// Handle page unload to clean up
window.addEventListener('beforeunload', function() {
    try {
        cleanupPerformanceCharts();
    } catch (error) {
        console.error('Error during page unload cleanup:', error);
    }
});

function updateLastViewedTime() {
    try {
        const lastViewedElement = document.getElementById('last-viewed-time');
        if (lastViewedElement) {
            lastViewedElement.textContent = new Date().toLocaleString();
        }
    } catch (error) {
        console.error('Error updating last viewed time:', error);
    }
}

function setupPerformanceChartsLazyLoading() {
    try {
        console.log('Setting up employee performance charts with immediate loading for better UX');
        
        // For employee performance dashboards, load all charts immediately
        // This provides better user experience as users expect to see all charts at once
        loadAllPerformanceChartsImmediately();
        
    } catch (error) {
        console.error('Error setting up performance charts:', error);
        loadAllPerformanceChartsImmediately();
    }
}

// Note: setupChartLazyLoading function removed as we now load all charts immediately

function loadAllPerformanceChartsImmediately() {
    try {
        console.log('Loading all employee performance charts immediately');
        
        // Load charts with small delays to prevent blocking the UI
        // Initialize overall team performance chart first
        if (window.employeePerformanceData && window.employeePerformanceData.monthlyPerformance) {
            setTimeout(() => {
                console.log('Loading team overall chart');
                initializeTeamOverallChart();
            }, 100);
        }
        
        // Initialize overall department performance chart
        if (window.employeePerformanceData && window.employeePerformanceData.departmentMonthlyPerformance) {
            setTimeout(() => {
                console.log('Loading department overall chart');
                initializeDepartmentOverallChart();
            }, 200);
        }
        
        // Initialize individual employee charts
        if (window.employeePerformanceData && window.employeePerformanceData.employeeData) {
            setTimeout(() => {
                console.log('Loading employee bar charts');
                initializeEmployeeBarCharts();
            }, 300);
        }
        
        // Initialize individual department employee charts
        if (window.employeePerformanceData && window.employeePerformanceData.departmentEmployeeData) {
            setTimeout(() => {
                console.log('Loading department employee charts');
                initializeDepartmentEmployeeBarCharts();
            }, 400);
        }
        
    } catch (error) {
        console.error('Error in performance chart loading:', error);
    }
}

// Note: addPerformanceLoadingPlaceholder function removed as we now load all charts immediately

// Note: loadPerformanceChart function removed as we now call initialization functions directly

function initializeTeamOverallChart() {
    try {
        const canvasId = 'team-overall-chart';
        const canvas = document.getElementById(canvasId);
        
        if (!canvas) {
            console.error('Team overall chart canvas not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        const monthlyData = window.employeePerformanceData.monthlyPerformance;
        const months = window.employeePerformanceData.months;
        
        console.log('Team overall chart data:', { monthlyData, months });
        
        if (!monthlyData || !months) {
            console.error('Missing data for team overall chart');
            return;
        }
        
        // Extract star and emoji ratings for each month
        const starRatings = monthlyData.map(month => month.avg_star_rating || 0);
        const emojiRatings = monthlyData.map(month => month.avg_emoji_rating || 0);
        
        console.log('Team overall chart ratings:', { starRatings, emojiRatings });
        
        performanceCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Overall Star Rating',
                data: starRatings,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }, {
                label: 'Overall Satisfaction Rating',
                data: emojiRatings,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label;
                            const value = context.parsed.y;
                            return `${label}: ${value}/5`;
                        },
                        afterLabel: function(context) {
                            const monthData = monthlyData[context.dataIndex];
                            return `Evaluations: ${monthData.evaluation_count}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        stepSize: 1,
                        callback: function(value) {
                            return value + '/5';
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error('Error initializing team overall chart:', error);
        // Show error message on canvas if possible
        try {
            const canvasId = 'team-overall-chart';
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializeDepartmentOverallChart() {
    try {
        const canvasId = 'department-overall-chart';
        const canvas = document.getElementById(canvasId);
        
        if (!canvas) {
            console.error('Department overall chart canvas not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        const monthlyData = window.employeePerformanceData.departmentMonthlyPerformance;
        const months = window.employeePerformanceData.departmentMonths;
        
        if (!monthlyData || !months) {
            console.error('Missing data for department overall chart');
            return;
        }
        
        // Extract star and emoji ratings for each month
        const starRatings = monthlyData.map(month => month.avg_star_rating || 0);
        const emojiRatings = monthlyData.map(month => month.avg_emoji_rating || 0);
        
        performanceCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Overall Star Rating',
                data: starRatings,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                pointBackgroundColor: '#8b5cf6',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }, {
                label: 'Overall Satisfaction Rating',
                data: emojiRatings,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                pointBackgroundColor: '#f59e0b',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label;
                            const value = context.parsed.y;
                            return `${label}: ${value}/5`;
                        },
                        afterLabel: function(context) {
                            const monthData = monthlyData[context.dataIndex];
                            return `Evaluations: ${monthData.evaluation_count}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        stepSize: 1,
                        callback: function(value) {
                            return value + '/5';
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error('Error initializing department overall chart:', error);
        // Show error message on canvas if possible
        try {
            const canvasId = 'department-overall-chart';
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializeDepartmentEmployeeBarCharts() {
    try {
        const employeeData = window.employeePerformanceData.departmentEmployeeData;
        
        if (!employeeData) {
            console.error('No department employee data available');
            return;
        }
        
        console.log('Initializing department employee bar charts for', Object.keys(employeeData).length, 'employees');
        
        // Load all department employee charts with small delays to prevent UI blocking
        let delay = 0;
        for (const [employeeId, empData] of Object.entries(employeeData)) {
            try {
                const canvasId = `department-employee-chart-${employeeId}`;
                const canvas = document.getElementById(canvasId);
                
                if (canvas) {
                    setTimeout(() => {
                        try {
                            console.log('Loading department employee chart:', employeeId);
                            initializeDepartmentEmployeeBarChart(canvasId, empData);
                        } catch (error) {
                            console.error(`Error loading department employee chart ${employeeId}:`, error);
                        }
                    }, delay);
                    delay += 50; // 50ms delay between each chart
                }
            } catch (error) {
                console.error(`Error processing department employee ${employeeId}:`, error);
            }
        }
    } catch (error) {
        console.error('Error initializing department employee bar charts:', error);
    }
}

function initializeDepartmentEmployeeBarChart(canvasId, empData) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found for department employee chart: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        if (!empData) {
            console.error('No employee data provided for chart:', canvasId);
            return;
        }
        
        // Get weekly data
        const weeklyData = empData.weekly_data || [];
        const weeks = empData.weeks || [];
        
        // Check if we have any data
        if (weeklyData.length === 0) {
            ctx.fillStyle = '#9ca3af';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }
        
        // Extract star and emoji ratings for each week
        const starRatings = weeklyData.map(week => week.star_rating || 0);
        const emojiRatings = weeklyData.map(week => week.emoji_rating || 0);
        
        performanceCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Star Rating',
                data: starRatings,
                backgroundColor: 'rgba(139, 92, 246, 0.8)',
                borderColor: '#8b5cf6',
                borderWidth: 2,
                borderRadius: 4,
                barThickness: 20
            }, {
                label: 'Satisfaction Rating',
                data: emojiRatings,
                backgroundColor: 'rgba(245, 158, 11, 0.8)',
                borderColor: '#f59e0b',
                borderWidth: 2,
                borderRadius: 4,
                barThickness: 20
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label;
                            const value = context.parsed.y;
                            return `${label}: ${value}/5`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        stepSize: 1,
                        callback: function(value) {
                            return value + '/5';
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error(`Error initializing department employee bar chart ${canvasId}:`, error);
        // Show error message on canvas if possible
        try {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializeEmployeeBarCharts() {
    try {
        const employeeData = window.employeePerformanceData.employeeData;
        
        if (!employeeData) {
            console.error('No employee data available');
            return;
        }
        
        console.log('Initializing employee bar charts for', Object.keys(employeeData).length, 'employees');
        
        // Load all employee charts with small delays to prevent UI blocking
        let delay = 0;
        for (const [employeeId, empData] of Object.entries(employeeData)) {
            try {
                const canvasId = `employee-chart-${employeeId}`;
                const canvas = document.getElementById(canvasId);
                
                if (canvas) {
                    setTimeout(() => {
                        try {
                            console.log('Loading employee chart:', employeeId);
                            initializeEmployeeBarChart(canvasId, empData);
                        } catch (error) {
                            console.error(`Error loading employee chart ${employeeId}:`, error);
                        }
                    }, delay);
                    delay += 50; // 50ms delay between each chart
                }
            } catch (error) {
                console.error(`Error processing employee ${employeeId}:`, error);
            }
        }
    } catch (error) {
        console.error('Error initializing employee bar charts:', error);
    }
}

function initializeEmployeeBarChart(canvasId, empData) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found for employee chart: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        if (!empData) {
            console.error('No employee data provided for chart:', canvasId);
            return;
        }
        
        // Get weekly data
        const weeklyData = empData.weekly_data || [];
        const weeks = empData.weeks || [];
        
        // Check if we have any data
        if (weeklyData.length === 0) {
            ctx.fillStyle = '#9ca3af';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }
        
        // Extract star and emoji ratings for each week
        const starRatings = weeklyData.map(week => week.star_rating || 0);
        const emojiRatings = weeklyData.map(week => week.emoji_rating || 0);
        
        performanceCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Star Rating',
                data: starRatings,
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: '#3b82f6',
                borderWidth: 2,
                borderRadius: 4,
                barThickness: 20
            }, {
                label: 'Satisfaction Rating',
                data: emojiRatings,
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderColor: '#10b981',
                borderWidth: 2,
                borderRadius: 4,
                barThickness: 20
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label;
                            const value = context.parsed.y;
                            return `${label}: ${value}/5`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        stepSize: 1,
                        callback: function(value) {
                            return value + '/5';
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error(`Error initializing employee bar chart ${canvasId}:`, error);
        // Show error message on canvas if possible
        try {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializeCombinedBarChart(canvasId, chartInfo) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found for combined bar chart: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        if (!chartInfo) {
            console.error('No chart info provided for combined bar chart:', canvasId);
            return;
        }
        
        // Get star rating time series data and emoji distribution data
        const starData = chartInfo.star_data || [];
        const emojiData = chartInfo.emoji_data || {};
        
        if (!starData.length && Object.keys(emojiData).length === 0) {
            ctx.fillStyle = '#9ca3af';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }
    
    // Create a combined chart showing both star rating trend and emoji distribution
    const weeks = starData.map(item => {
        const date = new Date(item.period);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const starRatings = starData.map(item => item.value);
    
    // Calculate average emoji rating for display
    const emojiValues = Object.values(emojiData);
    const totalEmojis = emojiValues.reduce((sum, count) => sum + count, 0);
    const avgEmojiRating = totalEmojis > 0 ? 
        (emojiData['😞'] * 1 + emojiData['😕'] * 2 + emojiData['😐'] * 3 + emojiData['😊'] * 4 + emojiData['😍'] * 5) / totalEmojis : 0;
    
    // Create datasets
    const datasets = [];
    
    // Add star rating dataset if we have data
    if (starRatings.length > 0) {
        datasets.push({
            label: chartInfo.star_label || 'Star Rating',
            data: starRatings,
            backgroundColor: 'rgba(59, 130, 246, 0.8)',
            borderColor: '#3b82f6',
            borderWidth: 2,
            borderRadius: 4,
            yAxisID: 'y'
        });
    }
    
    // Add emoji satisfaction dataset (show as average line or bar)
    if (avgEmojiRating > 0) {
        datasets.push({
            label: chartInfo.emoji_label || 'Satisfaction Rating',
            data: new Array(weeks.length).fill(avgEmojiRating),
            backgroundColor: 'rgba(16, 185, 129, 0.8)',
            borderColor: '#10b981',
            borderWidth: 2,
            borderRadius: 4,
            yAxisID: 'y'
        });
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks.length > 0 ? weeks : ['Overall'],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            if (label.includes('Satisfaction')) {
                                return `${label}: ${value.toFixed(1)}/5 (${Object.entries(emojiData).map(([emoji, count]) => `${emoji}: ${count}`).join(', ')})`;
                            }
                            return `${label}: ${value}/5`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        stepSize: 1,
                        callback: function(value) {
                            return value + '/5';
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 }
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
    } catch (error) {
        console.error(`Error initializing combined bar chart ${canvasId}:`, error);
        // Show error message on canvas if possible
        try {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializeWeeklyBarChart(canvasId, chartInfo) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found for weekly bar chart: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        if (!chartInfo) {
            console.error('No chart info provided for weekly bar chart:', canvasId);
            return;
        }
        
        const data = chartInfo.data || [];
        
        if (!data || data.length === 0) {
            ctx.fillStyle = '#9ca3af';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }
    
    // Extract data for the chart
    const weeks = data.map(item => {
        // Format the week date for display
        const date = new Date(item.week);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const starRatings = data.map(item => item.star_rating);
    const emojiRatings = data.map(item => item.emoji_rating);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: [
                {
                    label: chartInfo.star_label || 'Star Rating',
                    data: starRatings,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    borderRadius: 4,
                    yAxisID: 'y'
                },
                {
                    label: chartInfo.emoji_label || 'Satisfaction Rating',
                    data: emojiRatings,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10b981',
                    borderWidth: 2,
                    borderRadius: 4,
                    yAxisID: 'y'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return `${label}: ${value}/5`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        stepSize: 1,
                        callback: function(value) {
                            return value + '/5';
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12 }
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
    } catch (error) {
        console.error(`Error initializing weekly bar chart ${canvasId}:`, error);
        // Show error message on canvas if possible
        try {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializeCombinedChart(canvasId, chartInfo) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found for combined chart: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        if (!chartInfo) {
            console.error('No chart info provided for combined chart:', canvasId);
            return;
        }
        
        // Create a combined chart showing both star rating trend and emoji distribution
        const starData = chartInfo.star_data || [];
        const emojiData = chartInfo.emoji_data || {};
    
    // Calculate average star rating
    const avgStarRating = starData.length > 0 
        ? starData.reduce((sum, item) => sum + item.value, 0) / starData.length 
        : 0;
    
    // Calculate emoji distribution percentages
    const totalEmojis = Object.values(emojiData).reduce((sum, count) => sum + count, 0);
    const emojiPercentages = {};
    for (const [emoji, count] of Object.entries(emojiData)) {
        emojiPercentages[emoji] = totalEmojis > 0 ? (count / totalEmojis) * 100 : 0;
    }
    
    // Create a doughnut chart showing the combined data
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Average Star Rating', 'Satisfaction Distribution'],
            datasets: [{
                data: [avgStarRating, 5 - avgStarRating],
                backgroundColor: [
                    '#10b981',  // Green for rating
                    '#374151'   // Gray for remaining
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        padding: 20,
                        generateLabels: function(chart) {
                            return [
                                {
                                    text: `Star Rating: ${avgStarRating.toFixed(1)}/5`,
                                    fillStyle: '#10b981',
                                    strokeStyle: '#10b981',
                                    lineWidth: 2,
                                    pointStyle: 'circle',
                                    hidden: false,
                                    index: 0
                                },
                                {
                                    text: `Emoji: ${Object.entries(emojiPercentages).map(([emoji, pct]) => `${emoji} ${pct.toFixed(0)}%`).join(', ')}`,
                                    fillStyle: '#374151',
                                    strokeStyle: '#374151',
                                    lineWidth: 2,
                                    pointStyle: 'circle',
                                    hidden: false,
                                    index: 1
                                }
                            ];
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            if (context.dataIndex === 0) {
                                return `Average Star Rating: ${avgStarRating.toFixed(1)}/5`;
                            } else {
                                return `Emoji Distribution: ${Object.entries(emojiPercentages).map(([emoji, pct]) => `${emoji} ${pct.toFixed(0)}%`).join(', ')}`;
                            }
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
    } catch (error) {
        console.error(`Error initializing combined chart ${canvasId}:`, error);
        // Show error message on canvas if possible
        try {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializeStandardChart(canvasId, chartInfo) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found for standard chart: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        if (!chartInfo) {
            console.error('No chart info provided for standard chart:', canvasId);
            return;
        }
        
        const data = chartInfo.data;
        
        if (!data || (Array.isArray(data) && data.length === 0)) {
            ctx.fillStyle = '#9ca3af';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }
    
    switch (chartInfo.type) {
        case 'pie':
            initializePieChart(ctx, data, chartInfo.label);
            break;
        case 'line':
            initializeLineChart(ctx, data, chartInfo.label);
            break;
        case 'bar':
            initializeBarChart(ctx, data, chartInfo.label);
            break;
        case 'doughnut':
            initializeDoughnutChart(ctx, data, chartInfo.label);
            break;
        default:
            initializeLineChart(ctx, data, chartInfo.label);
    }
    } catch (error) {
        console.error(`Error initializing standard chart ${canvasId}:`, error);
        // Show error message on canvas if possible
        try {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ef4444';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
            }
        } catch (displayError) {
            console.error('Error displaying error message:', displayError);
        }
    }
}

function initializePieChart(ctx, data, label) {
    try {
        if (!ctx || !data) {
            console.error('Invalid parameters for pie chart initialization');
            return;
        }
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#ef4444', '#f97316', '#f59e0b', '#3b82f6', '#10b981'
                ],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        padding: 20
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error('Error initializing pie chart:', error);
    }
}

function initializeLineChart(ctx, data, label) {
    try {
        if (!ctx || !data || !Array.isArray(data)) {
            console.error('Invalid parameters for line chart initialization');
            return;
        }
        
        const labels = data.map(item => item.period);
        const values = data.map(item => item.value);
        
        new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#9ca3af' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
    } catch (error) {
        console.error('Error initializing line chart:', error);
    }
}

function initializeBarChart(ctx, data, label) {
    try {
        if (!ctx || !data || !Array.isArray(data)) {
            console.error('Invalid parameters for bar chart initialization');
            return;
        }
        
        const labels = data.map(item => item.period);
        const values = data.map(item => item.value);
        
        new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: '#3b82f6',
                borderRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#9ca3af' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
    } catch (error) {
        console.error('Error initializing bar chart:', error);
    }
}

function initializeDoughnutChart(ctx, data, label) {
    try {
        if (!ctx || !data) {
            console.error('Invalid parameters for doughnut chart initialization');
            return;
        }
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#10b981', '#ef4444'
                ],
                borderWidth: 4,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 12 },
                        padding: 20
                    }
                }
            },
            cutout: '60%'
        }
    });
    } catch (error) {
        console.error('Error initializing doughnut chart:', error);
    }
}
