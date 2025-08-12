// Analytics functionality
window.loadAnalytics = function() {
    // Load analytics HTML if not already loaded
    const analyticsSection = document.getElementById('analytics-section');

    if (!analyticsSection.innerHTML.trim()) {
        // Load initial HTML
        analyticsSection.innerHTML = `
            <div class="container-fluid">
                <h2>Analytics</h2>

                <div class="row">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <span>Sales Funnel Overview</span>
                                <div>
                                    <button id="refresh-analytics-btn" class="btn btn-sm btn-outline-secondary">
                                        <i class="fas fa-sync-alt"></i> Refresh
                                    </button>
                                </div>
                            </div>
                            <div class="card-body">
                                <div id="funnel-chart-container">
                                    <canvas id="funnel-chart" height="300"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                US vs India Performance
                            </div>
                            <div class="card-body">
                                <canvas id="country-comparison-chart" height="250"></canvas>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                Email Performance
                            </div>
                            <div class="card-body">
                                <canvas id="email-performance-chart" height="250"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        document.getElementById('refresh-analytics-btn').addEventListener('click', loadAnalyticsData);
    }

    // Load analytics data
    loadAnalyticsData();
};

// Function to load analytics data
async function loadAnalyticsData() {
    try {
        // Fetch analytics data
        const analytics = await window.api.getAnalytics();

        if (!analytics.success) {
            throw new Error(analytics.error || 'Failed to load analytics data');
        }

        // Update charts with data
        updateFunnelChart(analytics.data, analytics.metrics);
        updateCountryComparisonChart(analytics.data, analytics.metrics);
        updateEmailPerformanceChart(analytics.data, analytics.metrics);

    } catch (error) {
        console.error('Error loading analytics data:', error);
        showNotification('error', 'Error loading analytics data: ' + error.message);
    }
}

// Function to update funnel chart
function updateFunnelChart(data, metrics) {
    const ctx = document.getElementById('funnel-chart').getContext('2d');

    // Example data - in a real implementation, this would use actual metrics
    const funnelData = {
        labels: ['Leads', 'Initial Contact', 'Replied', 'Call Booked', 'Payment Sent', 'Payment Received'],
        datasets: [{
            label: 'Conversion Funnel',
            data: [100, 80, 40, 25, 15, 10],
            backgroundColor: [
                'rgba(54, 162, 235, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)',
                'rgba(255, 99, 132, 0.6)'
            ],
            borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 1
        }]
    };

    if (window.funnelChart) {
        window.funnelChart.destroy();
    }

    window.funnelChart = new Chart(ctx, {
        type: 'bar',
        data: funnelData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Leads'
                    }
                }
            },
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: 'Sales Funnel Analysis'
                }
            }
        }
    });
}

// Function to update country comparison chart
function updateCountryComparisonChart(data, metrics) {
    const ctx = document.getElementById('country-comparison-chart').getContext('2d');

    // Example data - in a real implementation, this would use actual metrics
    const countryData = {
        labels: ['Reply Rate', 'Call Rate', 'Payment Rate', 'Conversion Rate'],
        datasets: [
            {
                label: 'US',
                data: [40, 25, 15, 10],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            },
            {
                label: 'India',
                data: [35, 20, 12, 8],
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }
        ]
    };

    if (window.countryChart) {
        window.countryChart.destroy();
    }

    window.countryChart = new Chart(ctx, {
        type: 'radar',
        data: countryData,
        options: {
            elements: {
                line: {
                    tension: 0.1
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 50
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'US vs India Performance'
                }
            }
        }
    });
}

// Function to update email performance chart
function updateEmailPerformanceChart(data, metrics) {
    const ctx = document.getElementById('email-performance-chart').getContext('2d');

    // Example data - in a real implementation, this would use actual metrics
    const emailData = {
        labels: ['Initial Email', 'Follow-up 1', 'Follow-up 2', 'Follow-up 3'],
        datasets: [
            {
                label: 'Open Rate',
                data: [80, 70, 60, 50],
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            },
            {
                label: 'Reply Rate',
                data: [15, 10, 8, 5],
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
            }
        ]
    };

    if (window.emailChart) {
        window.emailChart.destroy();
    }

    window.emailChart = new Chart(ctx, {
        type: 'line',
        data: emailData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Email Campaign Performance'
                }
            }
        }
    });
}
