// Main JavaScript File
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    document.getElementById('sidebarCollapse').addEventListener('click', function() {
        document.getElementById('sidebar').classList.toggle('active');
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

    // API functions
    window.api = {
        // Base URL for API requests
        baseUrl: '/api',

        // Helper function for API calls
        async fetchAPI(endpoint, method = 'GET', body = null) {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (body) {
                options.body = JSON.stringify(body);
            }

            try {
                const response = await fetch(`${this.baseUrl}${endpoint}`, options);

                if (!response.ok) {
                    throw new Error(`API Error: ${response.status} ${response.statusText}`);
                }

                return await response.json();
            } catch (error) {
                console.error('API Error:', error);
                showNotification('error', 'API Error: ' + error.message);
                throw error;
            }
        },

        // API endpoint methods
        async searchLeads(filters) {
            return this.fetchAPI('/leads/search', 'POST', filters);
        },

        async getLeads(filters = {}) {
            const queryParams = new URLSearchParams(filters).toString();
            return this.fetchAPI(`/leads?${queryParams}`);
        },

        async startOutreach(leadIds) {
            return this.fetchAPI('/outreach/start', 'POST', { lead_ids: leadIds });
        },

        async updateLead(leadId, status, notes) {
            return this.fetchAPI('/lead/update', 'POST', {
                lead_id: leadId,
                status,
                notes
            });
        },

        async createPayment(leadId, amount) {
            return this.fetchAPI('/payment/create', 'POST', {
                lead_id: leadId,
                amount
            });
        },

        async getAnalytics() {
            return this.fetchAPI('/analytics/get');
        }
    };

    // Utility functions
    window.utils = {
        // Format date
        formatDate(dateString) {
            if (!dateString) return '';

            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        },

        // Format currency based on country
        formatCurrency(amount, country = 'US') {
            if (country === 'US') {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(amount);
            } else {
                return new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR'
                }).format(amount);
            }
        },

        // Create a status badge
        createStatusBadge(status) {
            const statusMap = {
                'New': 'status-new',
                'Initial Contact': 'status-contacted',
                'Follow-up': 'status-contacted',
                'Replied': 'status-replied',
                'Call Requested': 'status-replied',
                'Call Scheduled': 'status-meeting',
                'Call Completed': 'status-meeting',
                'Payment Link Sent': 'status-payment',
                'Payment Link Clicked': 'status-payment',
                'Payment Received': 'status-won',
                'Onboarding': 'status-won',
                'No Response': 'status-payment'
            };

            const className = statusMap[status] || 'status-new';

            return `<span class="status-badge ${className}">${status}</span>`;
        }
    };

    // Notification system
    window.showNotification = function(type, message) {
        // Check if notification container exists
        let container = document.getElementById('notification-container');

        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.role = 'alert';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Add to container
        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 150);
        }, 5000);
    };

    // Load section content
    function loadSectionContent(sectionId) {
        switch (sectionId) {
            case 'dashboard':
                if (window.loadDashboard) {
                    window.loadDashboard();
                }
                break;
            case 'lead-management':
                if (window.loadLeadManagement) {
                    window.loadLeadManagement();
                }
                break;
            case 'email-outreach':
                if (window.loadEmailOutreach) {
                    window.loadEmailOutreach();
                }
                break;
            case 'payments':
                if (window.loadPayments) {
                    window.loadPayments();
                }
                break;
            case 'analytics':
                if (window.loadAnalytics) {
                    window.loadAnalytics();
                }
                break;
            case 'settings':
                if (window.loadSettings) {
                    window.loadSettings();
                }
                break;
        }
    }

    // Load initial dashboard
    if (window.loadDashboard) {
        window.loadDashboard();
    }

    // Initialize search form
    const searchForm = document.getElementById('apollo-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const country = document.getElementById('country').value;
            const industry = document.getElementById('industry').value;
            const revenue = document.getElementById('revenue').value;

            if (!country) {
                showNotification('error', 'Please select a country');
                return;
            }

            // Show loading
            const searchResults = document.getElementById('search-results');
            searchResults.innerHTML = `
                <div class="text-center p-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Searching for leads. This may take a moment...</p>
                </div>
            `;

            // Call API
            window.api.searchLeads({
                country,
                industry,
                revenue
            }).then(result => {
                if (result.success && result.data) {
                    // Display results
                    displaySearchResults(result.data);
                } else {
                    throw new Error(result.error || 'Unknown error');
                }
            }).catch(error => {
                searchResults.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-circle"></i> ${error.message}
                    </div>
                `;
            });
        });
    }

    // Display search results
    function displaySearchResults(leads) {
        const searchResults = document.getElementById('search-results');

        if (!leads || leads.length === 0) {
            searchResults.innerHTML = `
                <div class="alert alert-info" role="alert">
                    <i class="fas fa-info-circle"></i> No leads found matching your criteria.
                </div>
            `;
            return;
        }

        // Build table
        let html = `
            <div class="d-flex justify-content-between mb-3">
                <h5>${leads.length} leads found</h5>
                <button id="start-outreach-btn" class="btn btn-success" disabled>
                    <i class="fas fa-envelope"></i> Start Outreach
                </button>
            </div>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th width="40">
                                <input type="checkbox" id="select-all-leads" class="form-check-input">
                            </th>
                            <th>Name</th>
                            <th>Company</th>
                            <th>Title</th>
                            <th>Email</th>
                            <th>Country</th>
                            <th>Industry</th>
                            <th>Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        // Add rows
        leads.forEach(lead => {
            html += `
                <tr>
                    <td>
                        <input type="checkbox" class="form-check-input lead-select-checkbox" data-id="${lead.id}">
                    </td>
                    <td>${lead.first_name} ${lead.last_name}</td>
                    <td>${lead.company || 'N/A'}</td>
                    <td>${lead.title || 'N/A'}</td>
                    <td>${lead.email || 'N/A'}</td>
                    <td>${lead.country}</td>
                    <td>${lead.industry || 'N/A'}</td>
                    <td>${lead.estimated_revenue || 'N/A'}</td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        searchResults.innerHTML = html;

        // Add event listeners
        document.getElementById('select-all-leads').addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.lead-select-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });

            updateOutreachButton();
        });

        document.querySelectorAll('.lead-select-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', updateOutreachButton);
        });

        document.getElementById('start-outreach-btn').addEventListener('click', startOutreach);

        function updateOutreachButton() {
            const selected = document.querySelectorAll('.lead-select-checkbox:checked').length;
            const button = document.getElementById('start-outreach-btn');

            button.disabled = selected === 0;
            button.innerHTML = `<i class="fas fa-envelope"></i> Start Outreach (${selected})`;
        }

        function startOutreach() {
            const selectedLeads = [];
            document.querySelectorAll('.lead-select-checkbox:checked').forEach(checkbox => {
                selectedLeads.push(checkbox.getAttribute('data-id'));
            });

            if (selectedLeads.length === 0) {
                showNotification('error', 'Please select at least one lead');
                return;
            }

            // Show confirmation
            if (!confirm(`Are you sure you want to start outreach to ${selectedLeads.length} leads?`)) {
                return;
            }

            // Disable button and show loading
            const button = document.getElementById('start-outreach-btn');
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;

            // Call API
            window.api.startOutreach(selectedLeads).then(result => {
                if (result.success) {
                    showNotification('success', `Outreach started for ${result.data.success} leads`);

                    // Reset checkboxes
                    document.querySelectorAll('.lead-select-checkbox:checked').forEach(checkbox => {
                        checkbox.checked = false;
                    });
                    document.getElementById('select-all-leads').checked = false;

                    // Reset button
                    button.innerHTML = originalText;
                    button.disabled = true;

                    // If any failed, show details
                    if (result.data.failed > 0) {
                        console.warn('Failed outreach:', result.data.leads.filter(l => l.status === 'Failed'));
                        showNotification('warning', `${result.data.failed} leads could not be processed`);
                    }
                } else {
                    throw new Error(result.error || 'Unknown error');
                }
            }).catch(error => {
                button.innerHTML = originalText;
                button.disabled = false;
                showNotification('error', error.message);
            });
        }
    }
});
