// Lead Management functionality
window.loadLeadManagement = function() {
    // Load lead management HTML if not already loaded
    const leadManagementSection = document.getElementById('lead-management-section');

    if (!leadManagementSection.innerHTML.trim()) {
        // Load initial HTML
        leadManagementSection.innerHTML = `
            <div class="container-fluid">
                <h2>Lead Management</h2>

                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>Lead List</span>
                        <div>
                            <button id="refresh-leads-btn" class="btn btn-sm btn-outline-secondary me-2">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                            <select id="lead-filter" class="form-select form-select-sm d-inline-block w-auto">
                                <option value="">All Leads</option>
                                <option value="US">US Leads</option>
                                <option value="IN">India Leads</option>
                                <option value="New">New Leads</option>
                                <option value="Initial Contact">Contacted</option>
                                <option value="Replied">Replied</option>
                                <option value="Call">Call Scheduled</option>
                                <option value="Payment">Payment Stage</option>
                            </select>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="lead-list-container">
                            <div class="text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p>Loading leads...</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Lead Details Modal -->
                <div class="modal fade" id="leadDetailsModal" tabindex="-1" aria-labelledby="leadDetailsModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="leadDetailsModalLabel">Lead Details</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body" id="lead-details-content">
                                <div class="text-center">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-primary" id="update-lead-btn">Update Lead</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners after HTML is loaded
        document.getElementById('refresh-leads-btn').addEventListener('click', loadLeads);
        document.getElementById('lead-filter').addEventListener('change', loadLeads);
        document.getElementById('update-lead-btn').addEventListener('click', updateLead);
    }

    // Load leads
    loadLeads();
};

// Function to load leads
async function loadLeads() {
    const container = document.getElementById('lead-list-container');
    const filterValue = document.getElementById('lead-filter').value;

    // Show loading
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading leads...</p>
        </div>
    `;

    try {
        // Build filter object
        const filters = {};

        if (filterValue === 'US' || filterValue === 'IN') {
            filters.country = filterValue;
        } else if (filterValue) {
            filters.status = filterValue;
        }

        // Fetch leads
        const response = await window.api.getLeads(filters);

        if (!response.success) {
            throw new Error(response.error || 'Failed to load leads');
        }

        const leads = response.data || [];

        // Display leads
        displayLeads(leads, container);

    } catch (error) {
        console.error('Error loading leads:', error);

        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-circle"></i> Error loading leads: ${error.message}
                <button class="btn btn-sm btn-outline-danger ms-3" onclick="loadLeads()">Try Again</button>
            </div>
        `;
    }
}

// Function to display leads
function displayLeads(leads, container) {
    if (!leads || leads.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-info-circle"></i> No leads found matching your criteria.
            </div>
        `;
        return;
    }

    // Create HTML table
    let html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Company</th>
                        <th>Country</th>
                        <th>Status</th>
                        <th>Last Contact</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    // Add rows
    leads.forEach(lead => {
        const countryFlag = lead.country === 'US' ? '🇺🇸' : '🇮🇳';

        html += `
            <tr>
                <td>${lead.first_name} ${lead.last_name}</td>
                <td>${lead.company || 'N/A'}</td>
                <td>${countryFlag} ${lead.country}</td>
                <td>${window.utils.createStatusBadge(lead.status)}</td>
                <td>${lead.last_contact || 'Never'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary view-lead-btn" data-id="${lead.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success send-email-btn" data-id="${lead.id}">
                        <i class="fas fa-envelope"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning payment-btn" data-id="${lead.id}">
                        <i class="fas fa-dollar-sign"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;

    // Add event listeners
    document.querySelectorAll('.view-lead-btn').forEach(btn => {
        btn.addEventListener('click', () => viewLeadDetails(btn.getAttribute('data-id')));
    });

    document.querySelectorAll('.send-email-btn').forEach(btn => {
        btn.addEventListener('click', () => sendEmailToLead(btn.getAttribute('data-id')));
    });

    document.querySelectorAll('.payment-btn').forEach(btn => {
        btn.addEventListener('click', () => sendPaymentLink(btn.getAttribute('data-id')));
    });
}

// Function to view lead details
async function viewLeadDetails(leadId) {
    // Get modal elements
    const modal = new bootstrap.Modal(document.getElementById('leadDetailsModal'));
    const modalTitle = document.getElementById('leadDetailsModalLabel');
    const modalContent = document.getElementById('lead-details-content');

    // Show loading in modal
    modalContent.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading lead details...</p>
        </div>
    `;

    // Show modal
    modal.show();

    try {
        // Fetch lead details
        const response = await window.api.getLeads({ lead_ids: [leadId] });

        if (!response.success || !response.data || response.data.length === 0) {
            throw new Error('Failed to load lead details');
        }

        const lead = response.data[0];

        // Update modal title
        modalTitle.textContent = `${lead.first_name} ${lead.last_name} - ${lead.company || 'N/A'}`;

        // Display lead details
        modalContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Contact Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <th>Name</th>
                            <td>${lead.first_name} ${lead.last_name}</td>
                        </tr>
                        <tr>
                            <th>Email</th>
                            <td>${lead.email || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Phone</th>
                            <td>${lead.phone || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>LinkedIn</th>
                            <td>
                                ${lead.linkedin_url ?
                                    `<a href="${lead.linkedin_url}" target="_blank">${lead.linkedin_url}</a>` :
                                    'N/A'}
                            </td>
                        </tr>
                        <tr>
                            <th>Title</th>
                            <td>${lead.title || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Country</th>
                            <td>${lead.country === 'US' ? '🇺🇸 United States' : '🇮🇳 India'}</td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Company Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <th>Company</th>
                            <td>${lead.company || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Website</th>
                            <td>
                                ${lead.company_website ?
                                    `<a href="${lead.company_website}" target="_blank">${lead.company_website}</a>` :
                                    'N/A'}
                            </td>
                        </tr>
                        <tr>
                            <th>Industry</th>
                            <td>${lead.industry || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Company Size</th>
                            <td>${lead.company_size || 'N/A'} employees</td>
                        </tr>
                        <tr>
                            <th>Revenue</th>
                            <td>${lead.estimated_revenue || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Lead Source</th>
                            <td>${lead.source || 'N/A'}</td>
                        </tr>
                    </table>
                </div>
            </div>

            <div class="row mt-3">
                <div class="col-12">
                    <h6>Lead Status</h6>
                    <div class="d-flex align-items-center">
                        <div class="me-3">Current Status:</div>
                        <div>${window.utils.createStatusBadge(lead.status)}</div>
                    </div>

                    <div class="mt-3">
                        <label for="lead-status-select" class="form-label">Update Status</label>
                        <select class="form-select" id="lead-status-select">
                            <option value="">Select Status</option>
                            <option value="New">New</option>
                            <option value="Initial Contact">Initial Contact</option>
                            <option value="Follow-up">Follow-up</option>
                            <option value="Replied">Replied</option>
                            <option value="Call Requested">Call Requested</option>
                            <option value="Call Scheduled">Call Scheduled</option>
                            <option value="Call Completed">Call Completed</option>
                            <option value="Payment Link Sent">Payment Link Sent</option>
                            <option value="Payment Received">Payment Received</option>
                            <option value="Onboarding">Onboarding</option>
                            <option value="No Response">No Response</option>
                        </select>
                    </div>

                    <div class="mt-3">
                        <label for="lead-notes-input" class="form-label">Notes</label>
                        <textarea class="form-control" id="lead-notes-input" rows="4">${lead.notes || ''}</textarea>
                    </div>
                </div>
            </div>

            <input type="hidden" id="current-lead-id" value="${lead.id}">
        `;

    } catch (error) {
        console.error('Error loading lead details:', error);

        modalContent.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-circle"></i> Error loading lead details: ${error.message}
            </div>
        `;
    }
}

// Function to update lead
async function updateLead() {
    const leadId = document.getElementById('current-lead-id').value;
    const status = document.getElementById('lead-status-select').value;
    const notes = document.getElementById('lead-notes-input').value;

    if (!leadId) {
        showNotification('error', 'Lead ID is missing');
        return;
    }

    if (!status) {
        showNotification('error', 'Please select a status');
        return;
    }

    // Show loading
    const updateBtn = document.getElementById('update-lead-btn');
    const originalText = updateBtn.textContent;
    updateBtn.disabled = true;
    updateBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...`;

    try {
        // Call API to update lead
        const response = await window.api.updateLead(leadId, status, notes);

        if (!response.success) {
            throw new Error(response.error || 'Failed to update lead');
        }

        // Success
        showNotification('success', 'Lead updated successfully');

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('leadDetailsModal'));
        modal.hide();

        // Refresh leads
        loadLeads();

    } catch (error) {
        console.error('Error updating lead:', error);
        showNotification('error', 'Error updating lead: ' + error.message);
    } finally {
        // Reset button
        updateBtn.disabled = false;
        updateBtn.textContent = originalText;
    }
}

// Function to send email to lead
function sendEmailToLead(leadId) {
    // Navigate to email outreach section and pre-select this lead
    const emailLink = document.querySelector('#sidebar a[data-section="email-outreach"]');
    if (emailLink) {
        emailLink.click();

        // Store lead ID for email section to use
        window.selectedLeadId = leadId;
    } else {
        showNotification('error', 'Email outreach section not found');
    }
}

// Function to send payment link
function sendPaymentLink(leadId) {
    // Navigate to payments section and pre-select this lead
    const paymentsLink = document.querySelector('#sidebar a[data-section="payments"]');
    if (paymentsLink) {
        paymentsLink.click();

        // Store lead ID for payments section to use
        window.selectedLeadId = leadId;
    } else {
        showNotification('error', 'Payments section not found');
    }
}
