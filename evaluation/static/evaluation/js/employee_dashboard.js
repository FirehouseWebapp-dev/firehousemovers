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

// Performance trends data from Django context
const performanceData = window.performanceData || {};

// Chart instances for trends
let trendsCharts = {};

// Initialize performance trends charts
function initializeTrendsCharts() {
    // Dynamically initialize charts for all questions with include_in_trends=True
    for (const [questionKey, chartData] of Object.entries(performanceData.chartData || {})) {
        const canvasId = `trends-chart-${questionKey.toLowerCase()}`;
        
        if (chartData) {
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
                case 'radar':
                    initializeTrendsRadarChart(canvasId, questionKey);
                    break;
                case 'gauge':
                    initializeTrendsGaugeChart(canvasId, questionKey);
                    break;
                default:
                    console.log(`Unknown chart type: ${chartData.type} for ${questionKey}`);
            }
        }
    }
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
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: '#3b82f6',
                borderWidth: 2,
                borderRadius: 6,
                borderSkipped: false,
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
                borderWidth: 3,
                borderColor: '#ffffff',
                hoverBorderWidth: 4,
                hoverBorderColor: '#ffffff'
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
    const canvas = document.getElementById(canvasId);
    const container = canvas.parentElement;
    container.innerHTML = '<div class="flex items-center justify-center h-full text-gray-400">No data available</div>';
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (performanceData && performanceData.chartData) {
        initializeTrendsCharts();
    }
});

// Update charts when window is resized
window.addEventListener('resize', function() {
    Object.values(trendsCharts).forEach(chart => {
        if (chart) chart.resize();
    });
});
