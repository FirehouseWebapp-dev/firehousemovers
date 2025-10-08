// Senior Manager Performance Overview JavaScript
// Chart initialization for department metrics and all managers rating trends

// Chart instances
let performanceCharts = {};

// Lazy loading state
let chartObserver = null;

// Clean up function
function cleanupPerformanceCharts() {
    try {
        Object.values(performanceCharts).forEach(chart => {
            try {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            } catch (error) {
                console.error('Error destroying chart:', error);
            }
        });
        
        performanceCharts = {};
        
        if (chartObserver) {
            try {
                chartObserver.disconnect();
                chartObserver = null;
            } catch (error) {
                console.error('Error disconnecting observer:', error);
            }
        }
        
        document.querySelectorAll('.chart-loading-placeholder').forEach(placeholder => {
            try {
                placeholder.remove();
            } catch (error) {
                console.error('Error removing placeholder:', error);
            }
        });
    } catch (error) {
        console.error('Error in cleanupPerformanceCharts:', error);
    }
}

// Add CSS for loading placeholders
if (!document.getElementById('performance-overview-styles')) {
    const style = document.createElement('style');
    style.id = 'performance-overview-styles';
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

// Setup lazy loading for managers rating trends chart
function setupManagersRatingTrendsLazyLoading() {
    try {
        const canvas = document.getElementById('managers-rating-trends-chart');
        if (!canvas) {
            console.log('Managers rating trends chart canvas not found');
            return;
        }
        
        // Add loading placeholder
        const container = canvas.parentElement;
        const loadingPlaceholder = document.createElement('div');
        loadingPlaceholder.className = 'chart-loading-placeholder';
        loadingPlaceholder.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading chart...</div>
        `;
        container.appendChild(loadingPlaceholder);
        canvas.style.display = 'none';
        
        // Create intersection observer for lazy loading
        chartObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        initializeManagersRatingTrendsChart();
                        
                        // Remove loading placeholder with fade effect
                        loadingPlaceholder.classList.add('fade-out');
                        setTimeout(() => {
                            loadingPlaceholder.remove();
                            canvas.style.display = 'block';
                        }, 300);
                    }, 100);
                    
                    chartObserver.disconnect();
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        chartObserver.observe(container);
        
        console.log('Lazy loading setup complete for managers rating trends chart');
    } catch (error) {
        console.error('Error setting up lazy loading:', error);
    }
}

// Initialize managers rating trends chart
function initializeManagersRatingTrendsChart() {
    try {
        const canvas = document.getElementById('managers-rating-trends-chart');
        if (!canvas) {
            console.log('Chart canvas not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        const chartData = window.managersRatingTrends;
        
        if (!chartData || !chartData.datasets || chartData.datasets.length === 0) {
            console.log('No chart data available');
            return;
        }
        
        performanceCharts['managers-rating-trends-chart'] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: chartData.datasets.map(dataset => ({
                    ...dataset,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: dataset.borderColor,
                    pointBorderColor: 'transparent',
                    pointBorderWidth: 0,
                    pointHoverBackgroundColor: dataset.borderColor,
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 2
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            color: '#e5e7eb',
                            font: { 
                                size: 14,
                                weight: '500'
                            },
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            boxWidth: 12,
                            boxHeight: 12,
                            useBorderRadius: true,
                            borderRadius: 6
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#ef4444',
                        borderWidth: 2,
                        cornerRadius: 8,
                        padding: 12,
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} ⭐`;
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
                            lineWidth: 1
                        },
                        ticks: { 
                            color: '#d1d5db',
                            stepSize: 1,
                            font: {
                                size: 12
                            }
                        },
                        title: {
                            display: true,
                            text: 'Average Rating',
                            color: '#e5e7eb',
                            font: {
                                size: 14,
                                weight: '600'
                            }
                        }
                    },
                    x: {
                        grid: { 
                            color: 'rgba(255, 255, 255, 0.1)',
                            lineWidth: 1
                        },
                        ticks: { 
                            color: '#d1d5db',
                            font: {
                                size: 12
                            }
                        },
                        title: {
                            display: true,
                            text: 'Period',
                            color: '#e5e7eb',
                            font: {
                                size: 14,
                                weight: '600'
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
        
        console.log('Managers rating trends chart initialized successfully');
    } catch (error) {
        console.error('Error initializing chart:', error);
    }
}

// Update last viewed time
function updateLastViewedTime() {
    const now = new Date();
    const timeElement = document.getElementById('last-viewed-time');
    if (timeElement) {
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

// Setup filter buttons
function setupFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const period = this.dataset.period;
            const currentUrl = new URL(window.location.href);
            
            // Set the new period
            currentUrl.searchParams.set('period', period);
            
            // Preserve existing date filters if they exist
            const startDateInput = document.getElementById('start_date');
            const endDateInput = document.getElementById('end_date');
            
            if (startDateInput && startDateInput.value) {
                currentUrl.searchParams.set('start_date', startDateInput.value);
            }
            if (endDateInput && endDateInput.value) {
                currentUrl.searchParams.set('end_date', endDateInput.value);
            }
            
            window.location.href = currentUrl.toString();
        });
    });
}

// Initialize everything on page load
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Clean up any existing charts
        cleanupPerformanceCharts();
        
        // Update last viewed time
        updateLastViewedTime();
        
        // Setup filter buttons
        setupFilterButtons();
        
        // Initialize chart if data exists
        if (window.managersRatingTrends && window.managersRatingTrends.labels && window.managersRatingTrends.labels.length > 0) {
            console.log('Setting up lazy loading for managers rating trends chart');
            setupManagersRatingTrendsLazyLoading();
        } else {
            console.log('No managers rating trends data available');
        }
    } catch (error) {
        console.error('Error initializing performance overview:', error);
    }
});

