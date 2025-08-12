// Dashboard functionality
window.loadDashboard = function() {
    // Load dashboard data
    loadDashboardData();

    // Set refresh interval (every 5 minutes)
    if (window.dashboardRefreshInterval) {
        clearInterval(window.dashboardRefreshInterval);
    }

    window.dashboardRefreshInterval = setInterval(loadDashboardData, 5 * 60 * 1000);
};

// Function to load dashboard data
async function loadDashboardData() {
    try {
        // Show loading indicators
        document.getElementById('recent-activities').innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;

        document.getElementById('suggestions').innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;

        // Fetch analytics data
        const analytics = await window.api.getAnalytics();

        if (!analytics || !analytics.data) {
            throw new Error('Failed to load analytics data');
        }

        // Update dashboard cards
        updateDashboardCards(analytics.data);

        // Update recent activities
        updateRecentActivities(analytics.data.recent_activities || []);

        // Update suggestions
        updateSuggestions(analytics.suggestions || []);

        // Update conversion chart
        updateConversionChart(analytics.data, analytics.metrics);

    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('error', 'Error loading dashboard data: ' + error.message);

        // Show error messages
        document.getElementById('recent-activities').innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-circle"></i> Error loading recent activities.
            </div>
        `;

        document.getElementById('suggestions').innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-circle"></i> Error loading suggestions.
            </div>
        `;
    }
}

// Update dashboard summary cards
function updateDashboardCards(data) {
    // Get US and India leads
    const usLeads = data.us_leads || { total: 0, by_status: {} };
    const indiaLeads = data.india_leads || { total: 0, by_status: {} };

    // Total leads
    const totalLeads = usLeads.total + indiaLeads.total;
    document.getElementById('total-leads-count').textContent = totalLeads;

    // Replies count
    const usReplies = (usLeads.by_status['Replied'] || 0) +
                      (usLeads.by_status['Call Requested'] || 0);
    const indiaReplies = (indiaLeads.by_status['Replied'] || 0) +
                         (indiaLeads.by_status['Call Requested'] || 0);
    const totalReplies = usReplies + indiaReplies;
    document.getElementById('replies-count').textContent = totalReplies;

    // Calls count
    const usCalls = (usLeads.by_status['Call Scheduled'] || 0) +
                    (usLeads.by_status['Call Completed'] || 0);
    const indiaCalls = (indiaLeads.by_status['Call Scheduled'] || 0) +
                       (indiaLeads.by_status['Call Completed'] || 0);
    const totalCalls = usCalls + indiaCalls;
    document.getElementById('calls-count').textContent = totalCalls;

    // Payments count
    const usPayments = (usLeads.by_status['Payment Received'] || 0) +
                       (usLeads.by_status['Onboarding'] || 0);
    const indiaPayments = (indiaLeads.by_status['Payment Received'] || 0) +
                          (indiaLeads.by_status['Onboarding'] || 0);
    const totalPayments = usPayments + indiaPayments;
    document.getElementById('payments-count').textContent = totalPayments;
}

// Update recent activities feed
function updateRecentActivities(activities) {
    const container = document.getElementById('recent-activities');

    if (!activities || activities.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-info-circle"></i> No recent activities to display.
            </div>
        `;
        return;
    }

    let html = '';

    activities.forEach(activity => {
        const countryFlag = activity.country === 'US' ? '🇺🇸' : '🇮🇳';
        html += `
            <div class="activity-item">
                <div class="d-flex justify-content-between">
                    <div><strong>${activity.name}</strong> (${activity.company})</div>
                    <div>${countryFlag}</div>
                </div>
                <div class="d-flex justify-content-between">
                    <div>${window.utils.createStatusBadge(activity.status)}</div>
                    <div class="activity-time">${activity.last_contact || 'N/A'}</div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Update suggestions for improvement
function updateSuggestions(suggestions) {
    const container = document.getElementById('suggestions');

    if (!suggestions || suggestions.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-info-circle"></i> No suggestions available at this time.
            </div>
        `;
        return;
    }

    let html = '';

    suggestions.forEach(suggestion => {
        html += `
            <div class="suggestion-item ${suggestion.priority}">
                <div class="suggestion-title">
                    <i class="fas fa-lightbulb"></i> ${suggestion.area}
                </div>
                <div>${suggestion.suggestion}</div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Update conversion rate chart
function updateConversionChart(data, metrics) {
    // Get context
    const ctx = document.getElementById('conversion-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (window.conversionChart) {
        window.conversionChart.destroy();
    }

    // Create data array
    const usMetrics = metrics.by_country.US || {};
    const indiaMetrics = metrics.by_country.India || {};

    // Create chart
    window.conversionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Reply Rate', 'Call Rate', 'Payment Rate', 'Conversion Rate'],
            datasets: [
                {
                    label: 'US',
                    data: [
                        usMetrics.reply_rate || 0,
                        usMetrics.call_rate || 0,
                        usMetrics.payment_rate || 0,
                        usMetrics.conversion_rate || 0
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'India',
                    data: [
                        indiaMetrics.reply_rate || 0,
                        indiaMetrics.call_rate || 0,
                        indiaMetrics.payment_rate || 0,
                        indiaMetrics.conversion_rate || 0
                    ],
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Overall',
                    data: [
                        metrics.overall.reply_rate || 0,
                        metrics.overall.call_rate || 0,
                        metrics.overall.payment_rate || 0,
                        metrics.overall.conversion_rate || 0
                    ],
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
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
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}
