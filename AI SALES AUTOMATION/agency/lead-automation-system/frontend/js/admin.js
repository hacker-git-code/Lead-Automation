// Admin Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is admin
    const user = Auth.getCurrentUser();
    if (user && user.role !== 'admin') {
        window.location.href = 'index.html';
        return;
    }

    // Initialize charts
    initCharts();

    // Initialize event listeners
    initEventListeners();

    // Load dashboard data
    loadDashboardData();
});

// Initialize dashboard charts
function initCharts() {
    // Sales performance chart
    const salesCtx = document.getElementById('sales-chart').getContext('2d');
    window.salesChart = new Chart(salesCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'US Leads',
                data: [65, 78, 90, 85, 110, 125],
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }, {
                label: 'India Leads',
                data: [45, 58, 70, 75, 92, 108],
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                borderColor: 'rgba(25, 135, 84, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Lead sources chart
    const sourcesCtx = document.getElementById('sources-chart').getContext('2d');
    window.sourcesChart = new Chart(sourcesCtx, {
        type: 'doughnut',
        data: {
            labels: ['Apollo.io', 'LinkedIn', 'Website', 'Referral', 'Other'],
            datasets: [{
                label: 'Lead Sources',
                data: [45, 25, 15, 10, 5],
                backgroundColor: [
                    'rgba(13, 110, 253, 0.8)',
                    'rgba(25, 135, 84, 0.8)',
                    'rgba(13, 202, 240, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                borderColor: [
                    'rgba(13, 110, 253, 1)',
                    'rgba(25, 135, 84, 1)',
                    'rgba(13, 202, 240, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            },
            cutout: '70%'
        }
    });

    // API usage chart
    const apiUsageCtx = document.getElementById('api-usage-chart').getContext('2d');
    window.apiUsageChart = new Chart(apiUsageCtx, {
        type: 'bar',
        data: {
            labels: ['Apollo', 'Gmail', 'Outlook', 'Stripe', 'Razorpay', 'Sheets'],
            datasets: [{
                label: 'API Calls (Last 7 Days)',
                data: [580, 420, 320, 180, 140, 640],
                backgroundColor: [
                    'rgba(13, 110, 253, 0.7)',
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(13, 202, 240, 0.7)',
                    'rgba(25, 135, 84, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(108, 117, 125, 0.7)'
                ],
                borderColor: [
                    'rgba(13, 110, 253, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(13, 202, 240, 1)',
                    'rgba(25, 135, 84, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(108, 117, 125, 1)'
                ],
                borderWidth: 1
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

// Initialize event listeners
function initEventListeners() {
    // Period selector for sales chart
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active state
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Update chart data based on period selected
            const period = this.getAttribute('data-period');
            updateSalesChart(period);
        });
    });

    // Date range selector
    document.querySelectorAll('.date-range').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const days = parseInt(this.getAttribute('data-range'));
            document.getElementById('date-range-text').textContent = `Last ${days} Days`;
            loadDashboardData(days);
        });
    });

    // Custom date range
    document.getElementById('custom-date-range').addEventListener('click', function(e) {
        e.preventDefault();
        // In a real app, this would show a date picker
        alert('In a complete implementation, this would show a date range picker.');
    });

    // Refresh stats button
    document.getElementById('refresh-stats').addEventListener('click', function() {
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';

        // Simulate loading data
        setTimeout(() => {
            loadDashboardData();
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
        }, 1000);
    });

    // Add content button
    document.getElementById('add-content-btn').addEventListener('click', function() {
        // In a real app, this would show a modal or navigate to a content creation page
        alert('In a complete implementation, this would open a content creation form.');
    });

    // Navigation between sections - inherit from main script.js
}

// Update sales chart based on selected period
function updateSalesChart(period) {
    // This would fetch data from the API in a real application
    let labels, usData, indiaData;

    switch (period) {
        case 'daily':
            labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            usData = [12, 19, 15, 17, 14, 10, 8];
            indiaData = [8, 15, 12, 14, 10, 7, 5];
            break;
        case 'weekly':
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            usData = [52, 65, 58, 70];
            indiaData = [42, 48, 39, 55];
            break;
        case 'monthly':
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
            usData = [65, 78, 90, 85, 110, 125];
            indiaData = [45, 58, 70, 75, 92, 108];
            break;
    }

    // Update chart data
    window.salesChart.data.labels = labels;
    window.salesChart.data.datasets[0].data = usData;
    window.salesChart.data.datasets[1].data = indiaData;
    window.salesChart.update();
}

// Load dashboard data
function loadDashboardData(days = 7) {
    // In a real app, this would fetch data from an API
    // For demonstration, we'll use mock data

    // Update dashboard statistics with animated counting
    animateValue('total-users-count', 0, 12, 1000);
    animateValue('active-campaigns-count', 0, 8, 1000);
    animateValue('leads-count', 0, 468, 1000);

    // Conversion rate with percentage
    const conversionElement = document.getElementById('conversion-rate');
    const startValue = 0;
    const endValue = 5.7;
    const duration = 1000;
    const start = performance.now();

    const updateConversion = (timestamp) => {
        const elapsed = timestamp - start;
        const progress = Math.min(elapsed / duration, 1);
        const value = startValue + (endValue - startValue) * progress;

        conversionElement.textContent = value.toFixed(1) + '%';

        if (progress < 1) {
            window.requestAnimationFrame(updateConversion);
        }
    };

    window.requestAnimationFrame(updateConversion);

    // In a real app, this would update all charts with fresh data
}

// Animate counting for statistics
function animateValue(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    const range = end - start;
    const startTime = performance.now();

    const updateValue = (timestamp) => {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const value = Math.floor(start + (range * progress));

        element.textContent = value;

        if (progress < 1) {
            window.requestAnimationFrame(updateValue);
        }
    };

    window.requestAnimationFrame(updateValue);
}
