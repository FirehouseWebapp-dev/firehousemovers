// Dashboard data from Django context
const dashboardData = {
    chartData: window.dashboardData?.chartData || {},
    questionLabels: window.dashboardData?.questionLabels || {},
    rangeType: window.dashboardData?.rangeType || "monthly",
    startDate: window.dashboardData?.startDate || "",
    endDate: window.dashboardData?.endDate || "",
    granularity: window.dashboardData?.granularity || "weekly"
};

// Chart instances
let charts = {};

// Initialize all charts
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

function initializeCharts() {
    // Dynamically initialize charts for all questions with include_in_trends=True
    const chartData = dashboardData.chartData;
    
    for (const [questionKey, chartInfo] of Object.entries(chartData)) {
        const canvasId = `chart-${questionKey.toLowerCase()}`;
        const chartType = chartInfo.type;
        
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
                console.warn(`Unknown chart type: ${chartType} for ${questionKey}`);
        }
    }
}

function initializeLineChart(canvasId, questionKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = dashboardData.chartData[questionKey];
    
    if (!data || !data.data || data.data.length === 0) {
        showNoDataMessage(canvasId);
        return;
    }
    
    const labels = data.data.map(item => item.period);
    const values = data.data.map(item => item.value);
    
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
    const canvas = document.getElementById(canvasId);
    const container = canvas.parentElement;
    container.innerHTML = '<div class="no-data">No data available</div>';
}

function updateDashboard() {
    const range = document.getElementById('range-filter').value;
    const employee = document.getElementById('employee-filter') ? document.getElementById('employee-filter').value : '';
    
    let url = window.location.pathname;
    if (employee) {
        url = url.replace(/\/\d+\/$/, `/${employee}/`);
    }
    url += `?range=${range}`;
    
    window.location.href = url;
}

function refreshDashboard() {
    window.location.reload();
}

// Update charts when window is resized
window.addEventListener('resize', function() {
    Object.values(charts).forEach(chart => {
        if (chart) chart.resize();
    });
});
