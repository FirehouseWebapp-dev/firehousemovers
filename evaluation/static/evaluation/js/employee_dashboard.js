// Update last viewed time
function updateLastViewedTime() {
    const now = new Date();
    const formatted = now.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('last-viewed-time').textContent = formatted;
}

// Performance trends data from Django context - will be set by inline script in HTML
let performanceData = {};

// Chart instances for trends
let trendsCharts = {};

// Lazy loading state for trends charts
let trendsChartObserver = null;
let trendsChartsToLoad = new Set();

// Add CSS animation for loading spinner
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Initialize performance trends charts with lazy loading
function setupTrendsLazyLoading() {
    try {
        // Check if IntersectionObserver is supported
        if (!window.IntersectionObserver) {
            loadAllTrendsChartsImmediately();
            return;
        }

        // Create intersection observer for lazy loading trends charts
        trendsChartObserver = new IntersectionObserver((entries) => {
            try {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const canvasId = entry.target.id;
                        const questionKey = canvasId.replace('trends-chart-', '').toUpperCase();
                        
                        // Only load chart if it hasn't been loaded yet
                        if (!trendsCharts[canvasId] && trendsChartsToLoad.has(questionKey)) {
                            loadTrendsChart(canvasId, questionKey);
                            trendsChartObserver.unobserve(entry.target);
                        }
                    }
                });
            } catch (error) {
                console.error('Error in trends intersection observer callback:', error);
            }
        }, {
            rootMargin: '100px 0px', // Start loading 100px before chart comes into view
            threshold: 0.1 // Load when 10% of chart is visible
        });
        
        // Set up lazy loading for all trends chart containers
        const chartData = performanceData.chartData || {};
        
        for (const [questionKey, chartInfo] of Object.entries(chartData)) {
            const canvasId = `trends-chart-${questionKey.toLowerCase()}`;
            const canvas = document.getElementById(canvasId);
            
            if (canvas) {
                // Add to charts to load set
                trendsChartsToLoad.add(questionKey);
                
                // Check if chart is already visible (above the fold)
                const rect = canvas.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                
                if (isVisible) {
                    // Load visible charts immediately
                    loadTrendsChart(canvasId, questionKey);
                } else {
                    // Add loading placeholder for hidden charts
                    addTrendsLoadingPlaceholder(canvas);
                    // Start observing the chart container for lazy loading
                    trendsChartObserver.observe(canvas);
                }
            }
        }
    } catch (error) {
        console.error('Error setting up trends lazy loading:', error);
        loadAllTrendsChartsImmediately();
    }
}

function loadAllTrendsChartsImmediately() {
    try {
        const chartData = performanceData.chartData || {};
        
        for (const [questionKey, chartInfo] of Object.entries(chartData)) {
            const canvasId = `trends-chart-${questionKey.toLowerCase()}`;
            const canvas = document.getElementById(canvasId);
            
            if (canvas && !trendsCharts[canvasId]) {
                loadTrendsChart(canvasId, questionKey);
            }
        }
    } catch (error) {
        console.error('Error in fallback trends chart loading:', error);
        showErrorMessage('Failed to load trends charts. Please refresh the page.');
    }
}

function addTrendsLoadingPlaceholder(canvas) {
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

function loadTrendsChart(canvasId, questionKey) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const container = canvas.parentElement;
    
    // Remove loading placeholder
    const placeholder = container.querySelector('.chart-loading-placeholder');
    if (placeholder) {
        placeholder.classList.add('fade-out');
        setTimeout(() => placeholder.remove(), 300);
    }
    
    // Get chart info and initialize
    const chartData = performanceData.chartData[questionKey];
    if (!chartData) return;
    
    // Use requestAnimationFrame for smoother loading
    requestAnimationFrame(() => {
        switch (chartData.type) {
            case 'line':
                initializeTrendsLineChart(canvasId, questionKey);
                break;
            case 'bar':
                initializeTrendsBarChart(canvasId, questionKey);
                break;
            case 'pie':
                initializeTrendsPieChart(canvasId, questionKey);
                break;
            case 'doughnut':
                initializeTrendsDoughnutChart(canvasId, questionKey);
                break;
            case 'radar':
                initializeTrendsRadarChart(canvasId, questionKey);
                break;
            case 'gauge':
                initializeTrendsGaugeChart(canvasId, questionKey);
                break;
            default:
        }
    });
}

function initializeTrendsLineChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = performanceData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showTrendsNoDataMessage(canvasId);
        return;
    }
    
    const labels = data.data.map(item => item.period);
    const values = data.data.map(item => item.value);
    
    trendsCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: data.label,
                data: values,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: {
                            size: 12
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
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function initializeTrendsBarChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = performanceData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showTrendsNoDataMessage(canvasId);
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
    
    trendsCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: data.label,
                data: values,
                backgroundColor: '#3b82f6',
                borderColor: '#3b82f6',
                barThickness: barWidth,
                maxBarThickness: maxBarWidth
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: {
                            size: 12
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
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function initializeTrendsPieChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = performanceData.chartData[questionKey];
    
    if (!data || !data.data) {
        showTrendsNoDataMessage(canvasId);
        return;
    }
    
    const emojiData = data.data;
    const labels = Object.keys(emojiData);
    const values = Object.values(emojiData);
    
    if (values.every(v => v === 0)) {
        showTrendsNoDataMessage(canvasId);
        return;
    }
    
    trendsCharts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#ef4444', // Red for 😞 (Very dissatisfied)
                    '#f97316', // Orange for 😕 (Dissatisfied)
                    '#f59e0b', // Yellow for 😐 (Neutral)
                    '#3b82f6', // Blue for 😊 (Satisfied)
                    '#10b981'  // Green for 😃 (Very satisfied)
                ],
                borderWidth: 1,
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
                        font: {
                            size: 18,
                            weight: 'bold'
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'line',
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
                    borderColor: '#000000',
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
            }
        }
    });
}

function initializeTrendsDoughnutChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = performanceData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showTrendsNoDataMessage(canvasId);
        return;
    }
    
    // For boolean data, we need to aggregate Yes/No responses
    let yesCount = 0;
    let noCount = 0;
    
    data.data.forEach(item => {
        if (item.value === 1 || item.value === true || item.value === 'Yes' || item.value === 'yes') {
            yesCount++;
        } else if (item.value === 0 || item.value === false || item.value === 'No' || item.value === 'no') {
            noCount++;
        }
    });
    
    // If no boolean data found, show no data message
    if (yesCount === 0 && noCount === 0) {
        showTrendsNoDataMessage(canvasId);
        return;
    }
    
    const total = yesCount + noCount;
    const yesPercentage = Math.round((yesCount / total) * 100);
    const noPercentage = Math.round((noCount / total) * 100);
    
    trendsCharts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Yes', 'No'],
            datasets: [{
                data: [yesCount, noCount],
                backgroundColor: [
                    '#10b981',  // Green for Yes
                    '#ef4444'   // Red for No
                ],
                borderWidth: 4,
                borderColor: '#ffffff',
                hoverBorderWidth: 6,
                hoverBorderColor: '#ffffff',
                hoverOffset: 15,
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                shadowBlur: 10,
                shadowOffsetY: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%', // Makes it a doughnut (hollow center)
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9ca3af',
                        font: {
                            size: 12,
                            weight: 'normal',
                            family: "'Inter', sans-serif"
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        boxWidth: 12,
                        boxHeight: 12,
                        borderWidth: 1,
                        borderColor: '#ffffff',
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const total = data.datasets[0].data.reduce((sum, val) => sum + val, 0);
                                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: 'transparent',
                                        strokeStyle: data.datasets[0].backgroundColor[i],
                                        lineWidth: 2,
                                        pointStyle: 'circle',
                                        hidden: false,
                                        index: i,
                                        fontColor: '#9ca3af'
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
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initializeTrendsRadarChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = performanceData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showTrendsNoDataMessage(canvasId);
        return;
    }
    
    const labels = data.data.map(item => item.period);
    const values = data.data.map(item => item.value);
    
    trendsCharts[canvasId] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: data.label,
                data: values,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderWidth: 3,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#000000',
                    borderWidth: 1,
                    cornerRadius: 8
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        lineWidth: 1
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        lineWidth: 1
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: {
                            size: 12
                        },
                        stepSize: 1
                    },
                    pointLabels: {
                        color: '#9ca3af',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

function initializeTrendsGaugeChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = performanceData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showTrendsNoDataMessage(canvasId);
        return;
    }
    
    // Calculate average value for gauge
    const values = data.data.map(item => item.value);
    const averageValue = values.reduce((sum, val) => sum + val, 0) / values.length;
    
    trendsCharts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [data.label],
            datasets: [{
                data: [averageValue, 10 - averageValue],
                backgroundColor: [
                    '#10b981',
                    '#374151'
                ],
                borderWidth: 0,
                hoverBorderWidth: 2,
                hoverBorderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
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
                                return `${data.label}: ${averageValue.toFixed(1)}/10`;
                            }
                            return '';
                        }
                    }
                }
            },
            cutout: '75%'
        }
    });
}

function showTrendsNoDataMessage(canvasId) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const container = canvas.parentElement;
        container.innerHTML = '<div class="flex items-center justify-center h-full text-gray-400">No data available</div>';
    } catch (error) {
        console.error(`Error showing trends no data message for ${canvasId}:`, error);
    }
}

function showErrorMessage(message) {
    try {
        console.error('Performance Dashboard Error:', message);
        
        // Create or update error notification
        let errorDiv = document.getElementById('trends-dashboard-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'trends-dashboard-error';
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

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Get performance data from window object set by inline script
        performanceData = window.performanceData || {};
        
        
        if (performanceData && performanceData.chartData) {
            setupTrendsLazyLoading();
        }
        setupEventListeners();
    } catch (error) {
        console.error('Error initializing performance dashboard:', error);
        showErrorMessage('Failed to initialize performance dashboard. Please refresh the page.');
    }
});

function setupEventListeners() {
    // Refresh button event listener
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDashboard);
    }
}

// Update charts when window is resized
window.addEventListener('resize', function() {
    Object.values(trendsCharts).forEach(chart => {
        if (chart) chart.resize();
    });
});

// Dashboard refresh function
function refreshDashboard() {
    try {
        updateLastViewedTime();
        
        // Clear existing charts and reset lazy loading state
        try {
            Object.values(trendsCharts).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
        } catch (error) {
            console.error('Error destroying trends charts:', error);
        }
        
        trendsCharts = {};
        trendsChartsToLoad.clear();
        
        // Disconnect observer if it exists
        if (trendsChartObserver) {
            try {
                trendsChartObserver.disconnect();
            } catch (error) {
                console.error('Error disconnecting trends observer:', error);
            }
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
