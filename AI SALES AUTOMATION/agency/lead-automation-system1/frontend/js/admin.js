/**
 * Admin Dashboard JavaScript
 * Handles functionality for the admin dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    document.getElementById('sidebarCollapse').addEventListener('click', function() {
        document.getElementById('sidebar').classList.toggle('active');
        document.getElementById('content').classList.toggle('active');
    });

    // Navigation between sections
    document.querySelectorAll('#sidebar a[data-section]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Get the target section
            const sectionId = this.getAttribute('data-section');

            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });

            // Show target section
            document.getElementById(sectionId + '-section').classList.add('active');

            // Update active link in sidebar
            document.querySelectorAll('#sidebar li').forEach(item => {
                item.classList.remove('active');
            });
            this.parentElement.classList.add('active');

            // Load section content if needed
            loadSectionContent(sectionId);
        });
    });

    // Handle logout
    document.getElementById('logout-link').addEventListener('click', logout);
    document.getElementById('menu-logout-link').addEventListener('click', logout);

    // Initialize dashboard
    initializeDashboard();

    // System section event listeners
    document.getElementById('deploy-version-btn').addEventListener('click', function() {
        // Show deployment modal
        const deployModal = new bootstrap.Modal(document.getElementById('deployVersionModal'));
        deployModal.show();
    });

    document.getElementById('start-deployment').addEventListener('click', function() {
        // Start deployment process
        startDeployment();
    });

    // System quick actions
    document.getElementById('backup-db-btn').addEventListener('click', backupDatabase);
    document.getElementById('update-ssl-btn').addEventListener('click', updateSSLCertificate);
    document.getElementById('view-logs-btn').addEventListener('click', viewDetailedLogs);
    document.getElementById('purge-tmp-btn').addEventListener('click', purgeTempFiles);
    document.getElementById('restart-system-btn').addEventListener('click', restartServices);

    // User management
    document.getElementById('submit-new-user').addEventListener('click', addNewUser);

    // Update user name from auth
    updateUserInfo();
});

/**
 * Handle user logout
 */
function logout(e) {
    e.preventDefault();

    // Call auth service logout
    Auth.logout().then(result => {
        if (result.success) {
            // Redirect to login page
            window.location.href = '/login.html';
        } else {
            console.error('Logout failed:', result.error);
            alert('Logout failed: ' + result.error);
        }
    }).catch(error => {
        console.error('Logout error:', error);
        alert('Logout error: ' + error.message);
    });
}

/**
 * Initialize dashboard elements and data
 */
function initializeDashboard() {
    // Refresh dashboard data
    refreshDashboardData();

    // Set up refresh button
    document.getElementById('refresh-dashboard').addEventListener('click', refreshDashboardData);

    // Initialize charts
    initializeCharts();
}

/**
 * Refresh dashboard data from API
 */
async function refreshDashboardData() {
    try {
        // Show loading indicators
        setLoadingState(true);

        // Fetch dashboard data
        const dashboardData = await fetchDashboardData();

        // Update dashboard cards
        updateDashboardCards(dashboardData);

        // Update charts
        updateCharts(dashboardData);

        // Update activities and logs
        updateActivities(dashboardData.activities || []);
        updateSystemLogs(dashboardData.logs || []);

        // Hide loading indicators
        setLoadingState(false);
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
        alert('Error refreshing dashboard: ' + error.message);

        // Hide loading indicators
        setLoadingState(false);
    }
}

/**
 * Set loading state for dashboard elements
 */
function setLoadingState(isLoading) {
    // Add loading state to refresh button
    const refreshBtn = document.getElementById('refresh-dashboard');

    if (isLoading) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';
    } else {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Data';
    }
}

/**
 * Fetch dashboard data from API
 */
async function fetchDashboardData() {
    // For demo purposes, return mock data
    // In a real implementation, this would call the API
    return {
        usersCount: 25,
        leadsCount: 1863,
        systemStatus: 'Healthy',
        systemVersion: '1.0.1',
        activities: [
            { user: 'john.smith@example.com', action: 'User Login', time: '2023-07-20 15:42:30' },
            { user: 'admin@example.com', action: 'Added new user', time: '2023-07-20 14:35:22' },
            { user: 'sarah.jones@example.com', action: 'Updated lead status', time: '2023-07-20 14:12:05' },
            { user: 'admin@example.com', action: 'Sent payment link', time: '2023-07-20 13:58:41' },
            { user: 'john.smith@example.com', action: 'Imported leads', time: '2023-07-20 11:23:15' }
        ],
        logs: [
            { time: '2023-07-20 15:45:12', type: 'INFO', message: 'User john.smith@example.com logged in' },
            { time: '2023-07-20 15:42:30', type: 'INFO', message: 'Email sent to lead ID: 58921' },
            { time: '2023-07-20 15:40:18', type: 'WARNING', message: 'High CPU usage detected (78%)' },
            { time: '2023-07-20 15:38:52', type: 'ERROR', message: 'Failed to connect to payment gateway' },
            { time: '2023-07-20 15:37:41', type: 'INFO', message: 'Backup completed successfully' }
        ],
        userRegistration: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            data: [3, 5, 2, 4, 6, 3, 2]
        },
        leadDistribution: {
            labels: ['US', 'India', 'Other'],
            data: [65, 30, 5]
        },
        resources: {
            cpu: 23,
            memory: 45,
            disk: 38
        }
    };
}

/**
 * Update dashboard summary cards
 */
function updateDashboardCards(data) {
    document.getElementById('total-users').textContent = data.usersCount;
    document.getElementById('total-leads').textContent = data.leadsCount;
    document.getElementById('system-status').textContent = data.systemStatus;
    document.getElementById('system-version').textContent = data.systemVersion;

    // Update system info
    document.getElementById('info-version').textContent = data.systemVersion;
    document.getElementById('info-server-time').textContent = new Date().toLocaleString();
    document.getElementById('info-last-deployment').textContent = '2023-07-15 09:23:45';

    // Update resource usage
    updateResourceUsage(data.resources);
}

/**
 * Update resource usage bars
 */
function updateResourceUsage(resources) {
    // CPU usage
    document.getElementById('cpu-usage-percent').textContent = resources.cpu + '%';
    document.getElementById('cpu-usage-bar').style.width = resources.cpu + '%';
    document.getElementById('cpu-usage-bar').setAttribute('aria-valuenow', resources.cpu);

    // Memory usage
    document.getElementById('memory-usage-percent').textContent = resources.memory + '%';
    document.getElementById('memory-usage-bar').style.width = resources.memory + '%';
    document.getElementById('memory-usage-bar').setAttribute('aria-valuenow', resources.memory);

    // Disk usage
    document.getElementById('disk-usage-percent').textContent = resources.disk + '%';
    document.getElementById('disk-usage-bar').style.width = resources.disk + '%';
    document.getElementById('disk-usage-bar').setAttribute('aria-valuenow', resources.disk);

    // Set colors based on usage
    setProgressBarColor('cpu-usage-bar', resources.cpu);
    setProgressBarColor('memory-usage-bar', resources.memory);
    setProgressBarColor('disk-usage-bar', resources.disk);
}

/**
 * Set progress bar color based on value
 */
function setProgressBarColor(elementId, value) {
    const element = document.getElementById(elementId);

    if (value < 50) {
        element.classList.remove('bg-warning', 'bg-danger');
        element.classList.add('bg-success');
    } else if (value < 80) {
        element.classList.remove('bg-success', 'bg-danger');
        element.classList.add('bg-warning');
    } else {
        element.classList.remove('bg-success', 'bg-warning');
        element.classList.add('bg-danger');
    }
}

/**
 * Update recent activities table
 */
function updateActivities(activities) {
    const container = document.getElementById('recent-activities');

    if (!activities || activities.length === 0) {
        container.innerHTML = '<tr><td colspan="3" class="text-center">No recent activities</td></tr>';
        return;
    }

    let html = '';

    activities.forEach(activity => {
        html += `
            <tr>
                <td>${activity.user}</td>
                <td>${activity.action}</td>
                <td>${activity.time}</td>
            </tr>
        `;
    });

    container.innerHTML = html;
}

/**
 * Update system logs table
 */
function updateSystemLogs(logs) {
    const container = document.getElementById('system-logs');

    if (!logs || logs.length === 0) {
        container.innerHTML = '<tr><td colspan="3" class="text-center">No system logs</td></tr>';
        return;
    }

    let html = '';

    logs.forEach(log => {
        // Set badge class based on log type
        let badgeClass = 'bg-info';
        if (log.type === 'WARNING') badgeClass = 'bg-warning';
        if (log.type === 'ERROR') badgeClass = 'bg-danger';

        html += `
            <tr>
                <td>${log.time}</td>
                <td><span class="badge ${badgeClass}">${log.type}</span></td>
                <td>${log.message}</td>
            </tr>
        `;
    });

    container.innerHTML = html;
}

/**
 * Initialize charts on the dashboard
 */
function initializeCharts() {
    // User Registration Chart
    const userCtx = document.getElementById('userRegistrationChart').getContext('2d');
    window.userChart = new Chart(userCtx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            datasets: [{
                label: 'New Users',
                data: [3, 5, 2, 4, 6, 3, 2],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'User Registrations by Month'
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Lead Distribution Chart
    const leadCtx = document.getElementById('leadDistributionChart').getContext('2d');
    window.leadChart = new Chart(leadCtx, {
        type: 'pie',
        data: {
            labels: ['US', 'India', 'Other'],
            datasets: [{
                label: 'Leads',
                data: [65, 30, 5],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(255, 205, 86, 0.5)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 205, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Lead Distribution by Country'
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Update charts with new data
 */
function updateCharts(data) {
    // Update User Registration Chart
    if (window.userChart && data.userRegistration) {
        window.userChart.data.labels = data.userRegistration.labels;
        window.userChart.data.datasets[0].data = data.userRegistration.data;
        window.userChart.update();
    }

    // Update Lead Distribution Chart
    if (window.leadChart && data.leadDistribution) {
        window.leadChart.data.labels = data.leadDistribution.labels;
        window.leadChart.data.datasets[0].data = data.leadDistribution.data;
        window.leadChart.update();
    }
}

/**
 * Load content for a specific section
 */
function loadSectionContent(sectionId) {
    switch (sectionId) {
        case 'users':
            loadUsers();
            break;
        case 'leads':
            loadLeads();
            break;
        case 'email-templates':
            loadEmailTemplates();
            break;
        case 'payment-settings':
            loadPaymentSettings();
            break;
        case 'reports':
            loadReports();
            break;
        case 'system':
            // System section is pre-loaded
            updateSystemInfo();
            break;
    }
}

/**
 * Load users for user management section
 */
async function loadUsers() {
    try {
        // In a real implementation, this would call the API
        const users = [
            { id: 1, name: 'John Smith', email: 'john.smith@example.com', role: 'User', lastLogin: '2023-07-20 15:42:30', status: 'Active' },
            { id: 2, name: 'Sarah Jones', email: 'sarah.jones@example.com', role: 'User', lastLogin: '2023-07-20 14:12:05', status: 'Active' },
            { id: 3, name: 'Admin User', email: 'admin@example.com', role: 'Admin', lastLogin: '2023-07-20 13:58:41', status: 'Active' },
            { id: 4, name: 'Mike Wilson', email: 'mike.wilson@example.com', role: 'User', lastLogin: '2023-07-19 09:30:22', status: 'Inactive' }
        ];

        // Update user table
        const tableBody = document.querySelector('#users-table tbody');

        let html = '';
        users.forEach(user => {
            const statusBadge = user.status === 'Active' ?
                '<span class="badge bg-success">Active</span>' :
                '<span class="badge bg-secondary">Inactive</span>';

            html += `
                <tr>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.role}</td>
                    <td>${user.lastLogin}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary edit-user-btn" data-id="${user.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-user-btn" data-id="${user.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        tableBody.innerHTML = html;

        // Add event listeners to buttons
        document.querySelectorAll('.edit-user-btn').forEach(btn => {
            btn.addEventListener('click', () => editUser(btn.getAttribute('data-id')));
        });

        document.querySelectorAll('.delete-user-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteUser(btn.getAttribute('data-id')));
        });

    } catch (error) {
        console.error('Error loading users:', error);
        alert('Error loading users: ' + error.message);
    }
}

/**
 * Add a new user
 */
function addNewUser() {
    // Get form values
    const name = document.getElementById('new-user-name').value;
    const email = document.getElementById('new-user-email').value;
    const role = document.getElementById('new-user-role').value;
    const password = document.getElementById('new-user-password').value;

    // Validate form
    if (!name || !email || !role || !password) {
        alert('Please fill in all fields');
        return;
    }

    // In a real implementation, this would call the API
    // For now, just show a success message and close the modal
    alert(`User ${name} (${email}) added successfully with role: ${role}`);

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('addUserModal'));
    modal.hide();

    // Refresh user list
    loadUsers();
}

/**
 * Edit an existing user
 */
function editUser(userId) {
    // In a real implementation, this would open a modal and load user data
    alert(`Edit user with ID: ${userId}`);
}

/**
 * Delete a user
 */
function deleteUser(userId) {
    // In a real implementation, this would show a confirmation dialog
    if (confirm(`Are you sure you want to delete user with ID: ${userId}?`)) {
        // Delete user
        alert(`User with ID: ${userId} deleted successfully`);

        // Refresh user list
        loadUsers();
    }
}

/**
 * Start the deployment process
 */
function startDeployment() {
    // Get form values
    const version = document.getElementById('version-number').value;
    const notes = document.getElementById('version-notes').value;
    const confirmed = document.getElementById('confirm-deployment').checked;

    // Validate form
    if (!version || !notes || !confirmed) {
        alert('Please fill in all fields and confirm deployment');
        return;
    }

    // Show deployment status
    document.getElementById('deployment-status').style.display = 'block';
    document.getElementById('deploy-version-form').style.display = 'none';
    document.getElementById('start-deployment').style.display = 'none';
    document.getElementById('cancel-deployment').textContent = 'Close';

    // Simulate deployment progress
    simulateDeployment();
}

/**
 * Simulate deployment progress
 */
function simulateDeployment() {
    const progressBar = document.getElementById('deployment-progress');
    const log = document.getElementById('deployment-log');
    let progress = 0;

    const interval = setInterval(() => {
        progress += 5;
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);

        // Add log message
        addDeploymentLog(progress, log);

        if (progress >= 100) {
            clearInterval(interval);

            // Complete deployment
            addDeploymentLog(100, log, true);

            // Update version
            document.getElementById('system-version').textContent = document.getElementById('version-number').value;
            document.getElementById('info-version').textContent = document.getElementById('version-number').value;
        }
    }, 500);
}

/**
 * Add a log message to the deployment log
 */
function addDeploymentLog(progress, logElement, isComplete = false) {
    const now = new Date().toLocaleTimeString();
    let message = '';

    if (isComplete) {
        message = `<div class="text-success">[${now}] Deployment completed successfully!</div>`;
    } else if (progress === 0) {
        message = `<div>[${now}] Starting deployment...</div>`;
    } else if (progress === 5) {
        message = `<div>[${now}] Backing up database...</div>`;
    } else if (progress === 20) {
        message = `<div>[${now}] Database backup complete.</div>`;
    } else if (progress === 25) {
        message = `<div>[${now}] Pulling latest code from repository...</div>`;
    } else if (progress === 40) {
        message = `<div>[${now}] Code updated successfully.</div>`;
    } else if (progress === 45) {
        message = `<div>[${now}] Installing dependencies...</div>`;
    } else if (progress === 60) {
        message = `<div>[${now}] Dependencies installed.</div>`;
    } else if (progress === 65) {
        message = `<div>[${now}] Running database migrations...</div>`;
    } else if (progress === 80) {
        message = `<div>[${now}] Migrations completed.</div>`;
    } else if (progress === 85) {
        message = `<div>[${now}] Restarting services...</div>`;
    } else if (progress === 95) {
        message = `<div>[${now}] Services restarted successfully.</div>`;
    }

    if (message) {
        logElement.innerHTML += message;
        // Scroll to bottom
        logElement.parentElement.scrollTop = logElement.parentElement.scrollHeight;
    }
}

/**
 * Update system information
 */
function updateSystemInfo() {
    // In a real implementation, this would call the API
    // For now, just update the server time
    document.getElementById('info-server-time').textContent = new Date().toLocaleString();
}

/**
 * Update user information from auth
 */
function updateUserInfo() {
    // Get user from auth
    const user = Auth.getCurrentUser();

    if (user) {
        // Update user name in navbar
        document.getElementById('user-name').textContent = user.full_name || user.email;
    }
}

// Quick action functions
function backupDatabase() {
    alert('Database backup started. This may take a few minutes.');
    // In a real implementation, this would call the API
}

function updateSSLCertificate() {
    alert('SSL certificate update started. This may take a few minutes.');
    // In a real implementation, this would call the API
}

function viewDetailedLogs() {
    alert('Detailed logs will open in a new window.');
    // In a real implementation, this would open a new window with logs
}

function purgeTempFiles() {
    alert('Temporary files purge started.');
    // In a real implementation, this would call the API
}

function restartServices() {
    if (confirm('Are you sure you want to restart all services? This will temporarily disrupt service for users.')) {
        alert('Services restart initiated. This may take a few minutes.');
        // In a real implementation, this would call the API
    }
}

// Placeholder functions for other sections
function loadLeads() {
    // In a real implementation, this would load leads
    document.getElementById('leads-section').innerHTML = `
        <div class="container-fluid">
            <h2>Lead Management</h2>
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                This section will be implemented in a future update.
            </div>
        </div>
    `;
}

function loadEmailTemplates() {
    // In a real implementation, this would load email templates
    document.getElementById('email-templates-section').innerHTML = `
        <div class="container-fluid">
            <h2>Email Templates</h2>
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                This section will be implemented in a future update.
            </div>
        </div>
    `;
}

function loadPaymentSettings() {
    // In a real implementation, this would load payment settings
    document.getElementById('payment-settings-section').innerHTML = `
        <div class="container-fluid">
            <h2>Payment Settings</h2>
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                This section will be implemented in a future update.
            </div>
        </div>
    `;
}

function loadReports() {
    // In a real implementation, this would load reports
    document.getElementById('reports-section').innerHTML = `
        <div class="container-fluid">
            <h2>Reports</h2>
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                This section will be implemented in a future update.
            </div>
        </div>
    `;
}
