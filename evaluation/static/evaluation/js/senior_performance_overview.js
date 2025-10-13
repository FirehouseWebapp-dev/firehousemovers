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

// Setup lazy loading for Q1: Work Volume chart
function setupDeptQ1LazyLoading() {
    try {
        const canvas = document.getElementById('dept-q1-chart');
        if (!canvas) {
            console.log('Q1 chart canvas not found');
            return;
        }
        
        const container = canvas.parentElement;
        const loadingPlaceholder = document.createElement('div');
        loadingPlaceholder.className = 'chart-loading-placeholder';
        loadingPlaceholder.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading chart...</div>
        `;
        container.appendChild(loadingPlaceholder);
        canvas.style.display = 'none';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        initializeDeptQ1Chart();
                        loadingPlaceholder.classList.add('fade-out');
                        setTimeout(() => {
                            loadingPlaceholder.remove();
                            canvas.style.display = 'block';
                        }, 300);
                    }, 100);
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1, rootMargin: '50px' });
        
        observer.observe(container);
        console.log('Lazy loading setup complete for Q1 chart');
    } catch (error) {
        console.error('Error setting up Q1 lazy loading:', error);
    }
}

// Setup lazy loading for Q2: Quality/Timeliness chart
function setupDeptQ2LazyLoading() {
    try {
        const canvas = document.getElementById('dept-q2-chart');
        if (!canvas) {
            console.log('Q2 chart canvas not found');
            return;
        }
        
        const container = canvas.parentElement;
        const loadingPlaceholder = document.createElement('div');
        loadingPlaceholder.className = 'chart-loading-placeholder';
        loadingPlaceholder.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading chart...</div>
        `;
        container.appendChild(loadingPlaceholder);
        canvas.style.display = 'none';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        initializeDeptQ2Chart();
                        loadingPlaceholder.classList.add('fade-out');
                        setTimeout(() => {
                            loadingPlaceholder.remove();
                            canvas.style.display = 'block';
                        }, 300);
                    }, 100);
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1, rootMargin: '50px' });
        
        observer.observe(container);
        console.log('Lazy loading setup complete for Q2 chart');
    } catch (error) {
        console.error('Error setting up Q2 lazy loading:', error);
    }
}

// Setup lazy loading for Q3: 5-Star Rating chart
function setupDeptQ3LazyLoading() {
    try {
        const canvas = document.getElementById('dept-q3-chart');
        if (!canvas) {
            console.log('Q3 chart canvas not found');
            return;
        }
        
        const container = canvas.parentElement;
        const loadingPlaceholder = document.createElement('div');
        loadingPlaceholder.className = 'chart-loading-placeholder';
        loadingPlaceholder.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading chart...</div>
        `;
        container.appendChild(loadingPlaceholder);
        canvas.style.display = 'none';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        initializeDeptQ3Chart();
                        loadingPlaceholder.classList.add('fade-out');
                        setTimeout(() => {
                            loadingPlaceholder.remove();
                            canvas.style.display = 'block';
                        }, 300);
                    }, 100);
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1, rootMargin: '50px' });
        
        observer.observe(container);
        console.log('Lazy loading setup complete for Q3 chart');
    } catch (error) {
        console.error('Error setting up Q3 lazy loading:', error);
    }
}

// Setup lazy loading for Q4: Emoji Satisfaction chart
function setupDeptQ4LazyLoading() {
    try {
        const canvas = document.getElementById('dept-q4-chart');
        if (!canvas) {
            console.log('Q4 chart canvas not found');
            return;
        }
        
        const container = canvas.parentElement;
        const loadingPlaceholder = document.createElement('div');
        loadingPlaceholder.className = 'chart-loading-placeholder';
        loadingPlaceholder.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading chart...</div>
        `;
        container.appendChild(loadingPlaceholder);
        canvas.style.display = 'none';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        initializeDeptQ4Chart();
                        loadingPlaceholder.classList.add('fade-out');
                        setTimeout(() => {
                            loadingPlaceholder.remove();
                            canvas.style.display = 'block';
                        }, 300);
                    }, 100);
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1, rootMargin: '50px' });
        
        observer.observe(container);
        console.log('Lazy loading setup complete for Q4 chart');
    } catch (error) {
        console.error('Error setting up Q4 lazy loading:', error);
    }
}

// Setup lazy loading for Q5: Confidence Rating chart
function setupDeptQ5LazyLoading() {
    try {
        const canvas = document.getElementById('dept-q5-chart');
        if (!canvas) {
            console.log('Q5 chart canvas not found');
            return;
        }
        
        const container = canvas.parentElement;
        const loadingPlaceholder = document.createElement('div');
        loadingPlaceholder.className = 'chart-loading-placeholder';
        loadingPlaceholder.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading chart...</div>
        `;
        container.appendChild(loadingPlaceholder);
        canvas.style.display = 'none';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        initializeDeptQ5Chart();
                        loadingPlaceholder.classList.add('fade-out');
                        setTimeout(() => {
                            loadingPlaceholder.remove();
                            canvas.style.display = 'block';
                        }, 300);
                    }, 100);
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1, rootMargin: '50px' });
        
        observer.observe(container);
        console.log('Lazy loading setup complete for Q5 chart');
    } catch (error) {
        console.error('Error setting up Q5 lazy loading:', error);
    }
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

// Initialize Q1: Work Volume Bar Chart
function initializeDeptQ1Chart() {
    try {
        const canvas = document.getElementById('dept-q1-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = window.deptQ1WorkVolume;
        
        if (!chartData || !chartData.has_data) return;
        
        performanceCharts['dept-q1-chart'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Work Volume',
                    data: chartData.data,
                    backgroundColor: '#3b82f6',
                    borderColor: '#2563eb',
                    borderWidth: 2,
                    borderRadius: 6,
                    barThickness: 35,
                    maxBarThickness: 40,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        callbacks: {
                            label: (context) => `${context.label}: ${context.parsed.y.toFixed(0)} tasks`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#d1d5db' },
                        title: { display: true, text: 'Average Tasks Handled', color: '#e5e7eb' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#d1d5db', maxRotation: 45, minRotation: 45 }
                    }
                }
            }
        });
        console.log('Q1 Work Volume chart initialized');
    } catch (error) {
        console.error('Error initializing Q1 chart:', error);
    }
}

// Initialize Q2: Quality/Timeliness Bar Chart
function initializeDeptQ2Chart() {
    try {
        const canvas = document.getElementById('dept-q2-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = window.deptQ2Quality;
        
        if (!chartData || !chartData.has_data) return;
        
        performanceCharts['dept-q2-chart'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Quality %',
                    data: chartData.data,
                    backgroundColor: '#10b981',
                    borderColor: '#059669',
                    borderWidth: 2,
                    borderRadius: 6,
                    barThickness: 35,
                    maxBarThickness: 40,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        callbacks: {
                            label: (context) => `${context.label}: ${context.parsed.y.toFixed(1)}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#d1d5db', callback: (value) => value + '%' },
                        title: { display: true, text: 'Success Rate (%)', color: '#e5e7eb' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#d1d5db', maxRotation: 45, minRotation: 45 }
                    }
                }
            }
        });
        console.log('Q2 Quality chart initialized');
    } catch (error) {
        console.error('Error initializing Q2 chart:', error);
    }
}

// Initialize Q3: 5-Star Rating Line Chart
function initializeDeptQ3Chart() {
    try {
        const canvas = document.getElementById('dept-q3-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = window.deptQ3Rating;
        
        if (!chartData || !chartData.has_data) return;
        
        performanceCharts['dept-q3-chart'] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Expertise Rating',
                    data: chartData.data,
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderColor: '#f59e0b',
                    borderWidth: 3,
                    pointRadius: 6,
                    pointBackgroundColor: '#f59e0b',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        callbacks: {
                            label: (context) => `${context.label}: ${context.parsed.y.toFixed(2)} ⭐`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#d1d5db', stepSize: 1 },
                        title: { display: true, text: 'Average Rating (1-5)', color: '#e5e7eb' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#d1d5db', maxRotation: 45, minRotation: 45 }
                    }
                }
            }
        });
        console.log('Q3 Rating chart initialized');
    } catch (error) {
        console.error('Error initializing Q3 chart:', error);
    }
}

// Initialize Q4: Emoji Satisfaction Pie Chart
function initializeDeptQ4Chart() {
    try {
        const canvas = document.getElementById('dept-q4-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = window.deptQ4Satisfaction;
        
        if (!chartData || !chartData.has_data) return;
        
        const colors = [
            '#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', 
            '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
        ];
        
        const backgroundColors = chartData.labels.map((_, idx) => colors[idx % colors.length]);
        
        performanceCharts['dept-q4-chart'] = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 1.5,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            color: '#ffffff',
                            font: { size: 13, weight: '600' },
                            padding: 20,
                            generateLabels: (chart) => {
                                const data = chart.data;
                                return data.labels.map((label, i) => ({
                                    text: `${label}: ${data.datasets[0].data[i].toFixed(2)} 😊`,
                                    fillStyle: backgroundColors[i],
                                    hidden: false,
                                    index: i
                                }));
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value.toFixed(2)} 😊 (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        console.log('Q4 Satisfaction chart initialized');
    } catch (error) {
        console.error('Error initializing Q4 chart:', error);
    }
}

// Initialize Q5: Confidence Rating Bar Chart
function initializeDeptQ5Chart() {
    try {
        const canvas = document.getElementById('dept-q5-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = window.deptQ5Confidence;
        
        if (!chartData || !chartData.has_data) return;
        
        performanceCharts['dept-q5-chart'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Confidence Rating',
                    data: chartData.data,
                    backgroundColor: '#8b5cf6',
                    borderColor: '#7c3aed',
                    borderWidth: 2,
                    borderRadius: 6,
                    barThickness: 35,
                    maxBarThickness: 40,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        callbacks: {
                            label: (context) => `${context.label}: ${context.parsed.y.toFixed(2)}/10`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#d1d5db', stepSize: 1 },
                        title: { display: true, text: 'Confidence Level (1-10)', color: '#e5e7eb' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#d1d5db', maxRotation: 45, minRotation: 45 }
                    }
                }
            }
        });
        console.log('Q5 Confidence chart initialized');
    } catch (error) {
        console.error('Error initializing Q5 chart:', error);
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
    
    // Refresh button handler
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            location.reload();
        });
    }
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
        
        // Setup lazy loading for Q1-Q5 department charts
        if (window.deptQ1WorkVolume && window.deptQ1WorkVolume.has_data) {
            console.log('Setting up lazy loading for Q1 Work Volume chart');
            setupDeptQ1LazyLoading();
        } else {
            console.log('No Q1 Work Volume data available');
        }
        
        if (window.deptQ2Quality && window.deptQ2Quality.has_data) {
            console.log('Setting up lazy loading for Q2 Quality chart');
            setupDeptQ2LazyLoading();
        } else {
            console.log('No Q2 Quality data available');
        }
        
        if (window.deptQ3Rating && window.deptQ3Rating.has_data) {
            console.log('Setting up lazy loading for Q3 Rating chart');
            setupDeptQ3LazyLoading();
        } else {
            console.log('No Q3 Rating data available');
        }
        
        if (window.deptQ4Satisfaction && window.deptQ4Satisfaction.has_data) {
            console.log('Setting up lazy loading for Q4 Satisfaction chart');
            setupDeptQ4LazyLoading();
        } else {
            console.log('No Q4 Satisfaction data available');
        }
        
        if (window.deptQ5Confidence && window.deptQ5Confidence.has_data) {
            console.log('Setting up lazy loading for Q5 Confidence chart');
            setupDeptQ5LazyLoading();
        } else {
            console.log('No Q5 Confidence data available');
        }
        
        // Setup lazy loading for managers rating trends chart
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

