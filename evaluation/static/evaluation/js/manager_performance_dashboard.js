// Manager Performance Dashboard JavaScript
// This file contains all the chart initialization and dashboard functionality with lazy loading

// Chart instances for manager performance charts
let managerCharts = {};

// Lazy loading state for manager performance charts
let managerChartObserver = null;
let managerChartsToLoad = new Set();

// Clean up function to reset state on page reload
function cleanupManagerCharts() {
    try {
        // Destroy existing chart instances
        Object.values(managerCharts).forEach(chart => {
            try {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            } catch (error) {
                console.error('Error destroying manager chart:', error);
            }
        });
        
        // Clear chart instances
        managerCharts = {};
        
        // Disconnect observer if it exists
        if (managerChartObserver) {
            try {
                managerChartObserver.disconnect();
                managerChartObserver = null;
            } catch (error) {
                console.error('Error disconnecting manager observer:', error);
            }
        }
        
        // Clear charts to load set
        managerChartsToLoad.clear();
        
        // Remove any existing loading placeholders
        try {
            document.querySelectorAll('.chart-loading-placeholder').forEach(placeholder => {
                try {
                    placeholder.remove();
                } catch (error) {
                    console.error('Error removing manager placeholder:', error);
                }
            });
        } catch (error) {
            console.error('Error querying manager loading placeholders:', error);
        }
    } catch (error) {
        console.error('Error in cleanupManagerCharts:', error);
    }
}

// Add CSS for loading placeholders (only if not already added)
try {
    if (!document.getElementById('manager-performance-dashboard-styles')) {
        const style = document.createElement('style');
        style.id = 'manager-performance-dashboard-styles';
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
    console.error('Error adding manager dashboard styles:', error);
}

// Initialize when DOM is ready and data is available
function initializeManagerPerformanceDashboard() {
    try {
        // Clean up any existing charts first
        cleanupManagerCharts();
        
        // Wait for manager performance data to be available
        if (window.managerPerformanceData && window.managerPerformanceData.chartData && Object.keys(window.managerPerformanceData.chartData).length > 0) {
            console.log('Initializing manager performance dashboard with data:', window.managerPerformanceData);
            setupManagerChartsLazyLoading();
            updateLastViewedTime();
            setupEventListeners();
            setupFilterButtons();
        } else {
            // Still set up other elements even if no personal performance data
            updateLastViewedTime();
            setupEventListeners();
            setupFilterButtons();
        }
    } catch (error) {
        console.error('Error initializing manager performance dashboard:', error);
        // Retry after a longer delay on error
        setTimeout(initializeManagerPerformanceDashboard, 500);
    }
}

function setupFilterButtons() {
    try {
        // Handle filter button clicks
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            try {
                button.addEventListener('click', function() {
                    try {
                        const period = this.getAttribute('data-period');
                        
                        // Update active button
                        filterButtons.forEach(btn => btn.classList.remove('active'));
                        this.classList.add('active');
                        
                        // Reload page with new period parameter
                        const url = new URL(window.location);
                        url.searchParams.set('period', period);
                        window.location.href = url.toString();
                    } catch (error) {
                        console.error('Error handling filter button click:', error);
                    }
                });
            } catch (error) {
                console.error('Error adding filter button event listener:', error);
            }
        });
    } catch (error) {
        console.error('Error setting up filter buttons:', error);
    }
}

// Try to initialize immediately if DOM is already loaded
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeManagerPerformanceDashboard);
    } else {
        // DOM is already loaded
        initializeManagerPerformanceDashboard();
    }
} catch (error) {
    console.error('Error setting up manager DOM ready listener:', error);
}

// Handle page visibility changes to prevent issues on reload
document.addEventListener('visibilitychange', function() {
    try {
        if (document.hidden) {
            // Page is hidden, clean up resources
            if (managerChartObserver) {
                managerChartObserver.disconnect();
            }
        } else {
            // Page is visible again, reinitialize if needed
            if (Object.keys(managerCharts).length === 0 && window.managerPerformanceData) {
                initializeManagerPerformanceDashboard();
            }
        }
    } catch (error) {
        console.error('Error handling manager visibility change:', error);
    }
});

// Handle page unload to clean up
window.addEventListener('beforeunload', function() {
    try {
        cleanupManagerCharts();
    } catch (error) {
        console.error('Error during manager page unload cleanup:', error);
    }
});

function updateLastViewedTime() {
    try {
        const lastViewedElement = document.getElementById('last-viewed-time');
        if (lastViewedElement) {
            lastViewedElement.textContent = new Date().toLocaleString();
        }
    } catch (error) {
        console.error('Error updating manager last viewed time:', error);
    }
}

function setupEventListeners() {
    try {
        // Add any additional event listeners here
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            try {
                refreshBtn.addEventListener('click', function() {
                    try {
                        window.location.reload();
                    } catch (error) {
                        console.error('Error reloading page:', error);
                    }
                });
            } catch (error) {
                console.error('Error adding refresh button event listener:', error);
            }
        }
    } catch (error) {
        console.error('Error setting up manager event listeners:', error);
    }
}

function setupManagerChartsLazyLoading() {
    try {
        // Check if IntersectionObserver is supported
        if (!window.IntersectionObserver) {
            console.log('IntersectionObserver not supported, loading all manager charts immediately');
            loadAllManagerChartsImmediately();
            return;
        }
        
        // Add a fallback timeout to ensure charts load even if lazy loading fails
        setTimeout(() => {
            console.log('Fallback: Loading any remaining manager charts after 3 seconds');
            loadAllManagerChartsImmediately();
        }, 3000);

        // Create intersection observer for lazy loading manager charts
        managerChartObserver = new IntersectionObserver((entries) => {
            try {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const canvasId = entry.target.id;
                        
                        // Only load chart if it hasn't been loaded yet
                        if (!managerCharts[canvasId] && managerChartsToLoad.has(canvasId)) {
                            loadManagerChart(canvasId);
                            managerChartObserver.unobserve(entry.target);
                        }
                    }
                });
            } catch (error) {
                console.error('Error in manager intersection observer callback:', error);
            }
        }, {
            rootMargin: '100px 0px', // Start loading 100px before chart comes into view
            threshold: 0.1 // Load when 10% of chart is visible
        });
        
        // Set up lazy loading for all manager performance charts
        const chartData = window.managerPerformanceData.chartData;
        
        for (const [questionKey, chartInfo] of Object.entries(chartData)) {
            const canvasId = `trends-chart-${questionKey.toLowerCase()}`;
            const canvas = document.getElementById(canvasId);
            
            if (canvas) {
                setupManagerChartLazyLoading(canvas, canvasId, chartInfo);
            }
        }
    } catch (error) {
        console.error('Error setting up manager charts lazy loading:', error);
        loadAllManagerChartsImmediately();
    }
}

function setupManagerChartLazyLoading(canvas, canvasId, chartInfo) {
    try {
        if (!canvas || !canvasId || !chartInfo) {
            console.error('Invalid parameters for manager chart lazy loading:', { canvas, canvasId, chartInfo });
            return;
        }
        
        // Add to charts to load set
        managerChartsToLoad.add(canvasId);
        
        // Check if chart is already visible (above the fold)
        const rect = canvas.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isVisible) {
            // Load visible charts immediately
            loadManagerChart(canvasId, chartInfo);
        } else {
            // Add loading placeholder for hidden charts
            addManagerLoadingPlaceholder(canvas);
            // Start observing the chart container for lazy loading
            if (managerChartObserver) {
                managerChartObserver.observe(canvas);
            }
        }
    } catch (error) {
        console.error('Error setting up manager chart lazy loading:', error);
    }
}

function loadAllManagerChartsImmediately() {
    try {
        const chartData = window.managerPerformanceData.chartData;
        
        for (const [questionKey, chartInfo] of Object.entries(chartData)) {
            const canvasId = `trends-chart-${questionKey.toLowerCase()}`;
            const canvas = document.getElementById(canvasId);
            
            if (canvas && !managerCharts[canvasId]) {
                initializeStandardChart(canvasId, chartInfo);
            }
        }
    } catch (error) {
        console.error('Error in fallback manager chart loading:', error);
    }
}

function addManagerLoadingPlaceholder(canvas) {
    try {
        if (!canvas) {
            console.error('Canvas not provided for manager loading placeholder');
            return;
        }
        
        const container = canvas.parentElement;
        if (!container) {
            console.error('Canvas parent element not found for manager loading placeholder');
            return;
        }
        
        const placeholder = document.createElement('div');
        placeholder.className = 'chart-loading-placeholder';
        placeholder.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading chart...</div>
        `;
        container.classList.add('chart-container');
        container.appendChild(placeholder);
    } catch (error) {
        console.error('Error adding manager loading placeholder:', error);
    }
}

function loadManagerChart(canvasId, chartInfo = null) {
    try {
        if (!canvasId) {
            console.error('Canvas ID not provided for manager chart loading');
            return;
        }
        
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Manager chart canvas not found: ${canvasId}`);
            return;
        }
        
        // Check if chart already exists
        if (managerCharts[canvasId]) {
            console.log('Manager chart already exists:', canvasId);
            return;
        }
        
        const container = canvas.parentElement;
        
        // Remove loading placeholder
        if (container) {
            const placeholder = container.querySelector('.chart-loading-placeholder');
            if (placeholder) {
                placeholder.classList.add('fade-out');
                setTimeout(() => {
                    try {
                        placeholder.remove();
                    } catch (error) {
                        console.error('Error removing manager placeholder:', error);
                    }
                }, 300);
            }
        }
        
        // Get chart info if not provided
        if (!chartInfo) {
            const questionKey = canvasId.replace('trends-chart-', '').toUpperCase();
            chartInfo = window.managerPerformanceData?.chartData?.[questionKey];
        }
        
        // Use requestAnimationFrame for smoother loading
        requestAnimationFrame(() => {
            try {
                if (chartInfo) {
                    initializeStandardChart(canvasId, chartInfo);
                } else {
                    console.error(`No chart info available for manager chart: ${canvasId}`);
                }
            } catch (error) {
                console.error(`Error in manager chart requestAnimationFrame: ${canvasId}`, error);
            }
        });
    } catch (error) {
        console.error(`Error loading manager chart ${canvasId}:`, error);
    }
}

function initializeStandardChart(canvasId, chartInfo) {
    try {
        if (!canvasId || !chartInfo) {
            console.error('Invalid parameters for manager standard chart initialization:', { canvasId, chartInfo });
            return;
        }
        
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Manager chart canvas not found: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
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
                managerCharts[canvasId] = initializePieChart(ctx, data, chartInfo.label);
                break;
            case 'line':
                managerCharts[canvasId] = initializeLineChart(ctx, data, chartInfo.label);
                break;
            case 'bar':
                managerCharts[canvasId] = initializeBarChart(ctx, data, chartInfo.label);
                break;
            case 'doughnut':
                managerCharts[canvasId] = initializeDoughnutChart(ctx, data, chartInfo.label);
                break;
            default:
                managerCharts[canvasId] = initializeLineChart(ctx, data, chartInfo.label);
        }
    } catch (error) {
        console.error(`Error initializing manager standard chart ${canvasId}:`, error);
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
            console.error('Error displaying manager error message:', displayError);
        }
    }
}

function initializePieChart(ctx, data, label) {
    try {
        if (!ctx || !data) {
            console.error('Invalid parameters for manager pie chart initialization');
            return null;
        }
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#ef4444', '#f97316', '#f59e0b', '#3b82f6', '#10b981'
                ],
                // borderWidth: 3,
                // borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'line',
                        padding: 20,
                        font: {
                            size: 20,
                            weight: '500'
                        },
                        color: '#ffffff',
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const meta = chart.getDatasetMeta(0);
                                    const style = meta.controller.getStyle(i);
                                    return {
                                        text: label,
                                        fillStyle: 'transparent',
                                        strokeStyle: style.backgroundColor,
                                        lineWidth: 2,
                                        pointStyle: 'line',
                                        hidden: isNaN(data.datasets[0].data[i]) || meta.data[i].hidden,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000
            }
        }
    });
    } catch (error) {
        console.error('Error initializing manager pie chart:', error);
        return null;
    }
}

function initializeLineChart(ctx, data, label) {
    try {
        if (!ctx || !data || !Array.isArray(data)) {
            console.error('Invalid parameters for manager line chart initialization');
            return null;
        }
        
        const labels = data.map(item => item.period);
        const values = data.map(item => item.value);
        
        return new Chart(ctx, {
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
        console.error('Error initializing manager line chart:', error);
        return null;
    }
}

function initializeBarChart(ctx, data, label) {
    try {
        if (!ctx || !data || !Array.isArray(data)) {
            console.error('Invalid parameters for manager bar chart initialization');
            return null;
        }
        
        const labels = data.map(item => item.period);
        const values = data.map(item => item.value);
        
        // Use fixed bar thickness instead of percentages to avoid conflicts
        const barThickness = 60;
        
        return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: '#3b82f6',
                borderRadius: 0,
                barThickness: barThickness
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
        console.error('Error initializing manager bar chart:', error);
        return null;
    }
}

function initializeDoughnutChart(ctx, data, label) {
    try {
        if (!ctx || !data) {
            console.error('Invalid parameters for manager doughnut chart initialization');
            return null;
        }
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        return new Chart(ctx, {
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
                        font: { size: 18 },
                        padding: 20
                    }
                }
            },
            cutout: '60%'
        }
    });
    } catch (error) {
        console.error('Error initializing manager doughnut chart:', error);
        return null;
    }
}
