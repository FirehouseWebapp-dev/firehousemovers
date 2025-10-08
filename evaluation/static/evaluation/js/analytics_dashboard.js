// Dashboard data from Django context - will be set by inline script in HTML
let dashboardData = {};

// Chart instances
let charts = {};

// Lazy loading state
let chartObserver = null;
let chartsToLoad = new Set();

// Add CSS animation for loading spinner
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Initialize all charts with lazy loading
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Get dashboard data from window object set by inline script
        dashboardData = {
            chartData: window.dashboardData?.chartData || {},
            questionLabels: window.dashboardData?.questionLabels || {},
            rangeType: window.dashboardData?.rangeType || "monthly",
            startDate: window.dashboardData?.startDate || "",
            endDate: window.dashboardData?.endDate || "",
            granularity: window.dashboardData?.granularity || "weekly"
        };
        
        
        setupLazyLoading();
        setupEventListeners();
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showErrorMessage('Failed to initialize dashboard. Please refresh the page.');
    }
});

function setupLazyLoading() {
    try {
        // Check if IntersectionObserver is supported
        if (!window.IntersectionObserver) {
            loadAllChartsImmediately();
            return;
        }

        // Create intersection observer for lazy loading charts
        chartObserver = new IntersectionObserver((entries) => {
            try {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const canvasId = entry.target.id;
                        const questionKey = canvasId.replace('chart-', '').toUpperCase();
                        
                        // Only load chart if it hasn't been loaded yet
                        if (!charts[canvasId] && chartsToLoad.has(questionKey)) {
                            loadChart(canvasId, questionKey);
                            chartObserver.unobserve(entry.target);
                        }
                    }
                });
            } catch (error) {
                console.error('Error in intersection observer callback:', error);
            }
        }, {
            rootMargin: '100px 0px', // Start loading 100px before chart comes into view
            threshold: 0.1 // Load when 10% of chart is visible
        });
        
        // Set up lazy loading for all chart containers
        const chartData = dashboardData.chartData;
        
        for (const [questionKey, chartInfo] of Object.entries(chartData)) {
            const canvasId = `chart-${questionKey.toLowerCase()}`;
            const canvas = document.getElementById(canvasId);
            
            if (canvas) {
                // Add to charts to load set
                chartsToLoad.add(questionKey);
                
                // Check if chart is already visible (above the fold)
                const rect = canvas.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                
                if (isVisible) {
                    // Load visible charts immediately
                    loadChart(canvasId, questionKey);
                } else {
                    // Add loading placeholder for hidden charts
                    addLoadingPlaceholder(canvas);
                    // Start observing the chart container for lazy loading
                    chartObserver.observe(canvas);
                }
            }
        }
    } catch (error) {
        console.error('Error setting up lazy loading:', error);
        loadAllChartsImmediately();
    }
}

function loadAllChartsImmediately() {
    try {
        const chartData = dashboardData.chartData;
        
        for (const [questionKey, chartInfo] of Object.entries(chartData)) {
            const canvasId = `chart-${questionKey.toLowerCase()}`;
            const canvas = document.getElementById(canvasId);
            
            if (canvas && !charts[canvasId]) {
                loadChart(canvasId, questionKey);
            }
        }
    } catch (error) {
        console.error('Error in fallback chart loading:', error);
        showErrorMessage('Failed to load charts. Please refresh the page.');
    }
}

function addLoadingPlaceholder(canvas) {
    const container = canvas.parentElement;
    const placeholder = document.createElement('div');
    placeholder.className = 'chart-loading-placeholder';
    placeholder.innerHTML = `
        <div class="loading-spinner"></div>
        <div class="loading-text">Loading chart...</div>
    `;
    container.classList.add('chart-container');
    container.appendChild(placeholder);
}

function loadChart(canvasId, questionKey) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return;
        }
        
        const container = canvas.parentElement;
        
        // Remove loading placeholder
        const placeholder = container.querySelector('.chart-loading-placeholder');
        if (placeholder) {
            placeholder.classList.add('fade-out');
            setTimeout(() => placeholder.remove(), 300);
        }
        
        // Get chart info and initialize
        const chartInfo = dashboardData.chartData[questionKey];
        if (!chartInfo) {
            showNoDataMessage(canvasId);
            return;
        }
        
        const chartType = chartInfo.type;
        
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded');
            showErrorMessage(`Chart library not available for ${canvasId}`);
            return;
        }
        
        // Use requestAnimationFrame for smoother loading
        requestAnimationFrame(() => {
            try {
                switch (chartType) {
                    case 'line':
                        initializeLineChart(canvasId, questionKey);
                        break;
                    case 'bar':
                        initializeBarChart(canvasId, questionKey);
                        break;
                    case 'pie':
                        initializePieChart(canvasId, questionKey);
                        break;
                    case 'radar':
                        initializeRadarChart(canvasId, questionKey);
                        break;
                    case 'gauge':
                        initializeGaugeChart(canvasId, questionKey);
                        break;
                    default:
                        showErrorMessage(`Unsupported chart type: ${chartType}`);
                }
            } catch (error) {
                console.error(`Error initializing chart ${canvasId}:`, error);
                showErrorMessage(`Failed to load chart: ${questionKey}`);
            }
        });
    } catch (error) {
        console.error(`Error loading chart ${canvasId}:`, error);
        showErrorMessage(`Failed to load chart: ${questionKey}`);
    }
}

function setupEventListeners() {
    // Range filter event listener
    const rangeFilter = document.getElementById('range-filter');
    if (rangeFilter) {
        rangeFilter.addEventListener('change', updateDashboard);
    }
    
    // Employee filter event listener
    const employeeFilter = document.getElementById('employee-filter');
    if (employeeFilter) {
        employeeFilter.addEventListener('change', updateDashboard);
    }
    
    // Refresh button event listener
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDashboard);
    }
    
}


function initializeLineChart(canvasId, questionKey) {
    try {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const data = dashboardData.chartData[questionKey];
        
        if (!data || !data.data || data.data.length === 0) {
            showNoDataMessage(canvasId);
            return false;
        }
        
        const labels = data.data.map(item => item.period);
        const values = data.data.map(item => item.value);
        
        if (labels.length !== values.length) {
            showErrorMessage(`Data error for ${questionKey}`);
            return false;
        }
        
        charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: data.label,
                    data: values,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        return true;
    } catch (error) {
        console.error(`Error initializing line chart ${canvasId}:`, error);
        showErrorMessage(`Failed to create line chart for ${questionKey}`);
        return false;
    }
}

function initializeBarChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = dashboardData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showNoDataMessage(canvasId);
        return;
    }
    
    const labels = data.data.map(item => item.period);
    const values = data.data.map(item => item.value);
    
    // Calculate optimal bar width based on data length
    const maxBarWidth = 60; // Maximum width for a single bar
    const minBarWidth = 30; // Minimum width for bars
    const dataCount = labels.length;
    
    // For single data point, use a moderate width
    // For multiple data points, use proportional width
    const barWidth = dataCount === 1 ? 40 : Math.max(minBarWidth, Math.min(maxBarWidth, 280 / dataCount));
    
    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: data.label,
                data: values,
                backgroundColor: '#28a745',
                borderColor: '#1e7e34',
                borderWidth: 1,
                barThickness: barWidth,
                maxBarThickness: maxBarWidth,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    categoryPercentage: 0.6,
                    barPercentage: 0.8,
                    offset: true,
                    align: 'start'
                }
            }
        }
    });
}

function initializePieChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = dashboardData.chartData[questionKey];
    
    if (!data || !data.data) {
        showNoDataMessage(canvasId);
        return;
    }
    
    const emojiData = data.data;
    const labels = Object.keys(emojiData);
    const values = Object.values(emojiData);
    
    if (values.every(v => v === 0)) {
        showNoDataMessage(canvasId);
        return;
    }
    
    charts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#ef4444', // Red for 😞
                    '#f59e0b', // Yellow for 😐
                    '#10b981'  // Green for 😃
                ],
                borderWidth: 1,
                borderColor: '#ffffff',
                hoverBorderWidth: 2,
                hoverBorderColor: '#ffffff',
                hoverOffset: 8
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
}

function initializeRadarChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = dashboardData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showNoDataMessage(canvasId);
        return;
    }
    
    const labels = data.data.map(item => item.period);
    const values = data.data.map(item => item.value);
    
    charts[canvasId] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: data.label,
                data: values,
                borderColor: '#6f42c1',
                backgroundColor: 'rgba(111, 66, 193, 0.2)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5
                }
            }
        }
    });
}

function initializeGaugeChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = dashboardData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showNoDataMessage(canvasId);
        return;
    }
    
    // Calculate average value for gauge
    const values = data.data.map(item => item.value);
    const averageValue = values.reduce((sum, val) => sum + val, 0) / values.length;
    
    charts[canvasId] = new Chart(ctx, {
        type: 'gauge',
        data: {
            labels: [data.label],
            datasets: [{
                data: [averageValue],
                backgroundColor: ['#007bff'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            valueLabel: {
                display: true,
                fontSize: 20,
                color: '#000'
            },
            needle: {
                display: true,
                color: '#000'
            }
        }
    });
}

function showNoDataMessage(canvasId) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const container = canvas.parentElement;
        container.innerHTML = '<div class="no-data">No data available</div>';
    } catch (error) {
        console.error(`Error showing no data message for ${canvasId}:`, error);
    }
}

function showErrorMessage(message) {
    try {
        console.error('Dashboard Error:', message);
        
        // Create or update error notification
        let errorDiv = document.getElementById('dashboard-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'dashboard-error';
            errorDiv.className = 'dashboard-error';
            document.body.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = `
            <button class="close-btn" onclick="this.parentElement.remove()">&times;</button>
            <strong>Error:</strong> ${message}
        `;
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv && errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    } catch (error) {
        console.error('Error showing error message:', error);
    }
}

function updateDashboard() {
    try {
        const range = document.getElementById('range-filter')?.value;
        const employee = document.getElementById('employee-filter')?.value || '';
        
        if (!range) {
            showErrorMessage('Range filter not found');
            return;
        }
        
        let url = window.location.pathname;
        if (employee) {
            url = url.replace(/\/\d+\/$/, `/${employee}/`);
        }
        url += `?range=${range}`;
        
        // Clear existing charts and reset lazy loading state
        try {
            Object.values(charts).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
        } catch (error) {
            console.error('Error destroying charts:', error);
        }
        
        charts = {};
        chartsToLoad.clear();
        
        // Disconnect observer if it exists
        if (chartObserver) {
            try {
                chartObserver.disconnect();
            } catch (error) {
                console.error('Error disconnecting observer:', error);
            }
        }
        
        // Navigate to new URL with a small delay to ensure cleanup
        setTimeout(() => {
            window.location.href = url;
        }, 100);
    } catch (error) {
        console.error('Error updating dashboard:', error);
        showErrorMessage('Failed to update dashboard. Please try again.');
    }
}

function refreshDashboard() {
    try {
        // Clear existing charts and reset state
        Object.values(charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        charts = {};
        chartsToLoad.clear();
        
        // Disconnect observer if it exists
        if (chartObserver) {
            chartObserver.disconnect();
        }
        
        // Reload the page with a small delay to ensure cleanup
        setTimeout(() => {
            window.location.reload(true);
        }, 100);
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
        showErrorMessage('Failed to refresh dashboard. Please try again.');
    }
}

// Update charts when window is resized
window.addEventListener('resize', function() {
    try {
        Object.values(charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    } catch (error) {
        console.error('Error resizing charts:', error);
    }
});
