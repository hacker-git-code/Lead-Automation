// Payments functionality
window.loadPayments = function() {
    // Load payments HTML if not already loaded
    const paymentsSection = document.getElementById('payments-section');

    if (!paymentsSection.innerHTML.trim()) {
        // Load initial HTML
        paymentsSection.innerHTML = `
            <div class="container-fluid">
                <h2>Payments</h2>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                Send Payment Link
                            </div>
                            <div class="card-body">
                                <form id="payment-form">
                                    <div class="mb-3">
                                        <label for="lead-select" class="form-label">Select Lead</label>
                                        <select class="form-select" id="lead-select" required>
                                            <option value="">Select a lead</option>
                                            <!-- Options will be loaded dynamically -->
                                        </select>
                                    </div>

                                    <div id="lead-info">
                                        <!-- Lead info will be displayed here -->
                                    </div>

                                    <div class="mb-3">
                                        <label for="payment-amount" class="form-label">Payment Amount</label>
                                        <div class="input-group">
                                            <span class="input-group-text" id="currency-symbol">$</span>
                                            <input type="number" class="form-control" id="payment-amount" placeholder="Enter amount" step="0.01" required>
                                        </div>
                                        <div class="form-text" id="pricing-suggestions">
                                            <!-- Pricing suggestions will be displayed here -->
                                        </div>
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-primary" id="send-payment-btn">
                                            <i class="fas fa-paper-plane"></i> Send Payment Link
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                Recent Payments
                            </div>
                            <div class="card-body">
                                <div id="recent-payments">
                                    <div class="text-center">
                                        <div class="spinner-border text-primary" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                        <p>Loading payment history...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        document.getElementById('payment-form').addEventListener('submit', sendPaymentLink);
        document.getElementById('lead-select').addEventListener('change', loadLeadInfo);
    }

    // Load leads for the dropdown
    loadLeadsForPayment();

    // Load payment history
    loadPaymentHistory();

    // Check if a lead was pre-selected from another section
    if (window.selectedLeadId) {
        const leadSelect = document.getElementById('lead-select');
        if (leadSelect.querySelector(`option[value="${window.selectedLeadId}"]`)) {
            leadSelect.value = window.selectedLeadId;
            loadLeadInfo();
        }

        // Clear the stored lead ID
        window.selectedLeadId = null;
    }
};

// Function to load leads for the payment dropdown
async function loadLeadsForPayment() {
    const leadSelect = document.getElementById('lead-select');

    try {
        // Fetch leads that are ready for payment
        // We'll focus on leads that have status: Call Completed, Replied, etc.
        const response = await window.api.getLeads();

        if (!response.success) {
            throw new Error(response.error || 'Failed to load leads');
        }

        const leads = response.data || [];

        // Filter leads
        const eligibleLeads = leads.filter(lead => {
            // Include leads that have had meaningful interaction
            const eligibleStatuses = [
                'Call Completed',
                'Call Scheduled',
                'Replied',
                'Call Requested',
                'Payment Link Sent'
            ];
            return eligibleStatuses.includes(lead.status);
        });

        // Clear existing options except the first one
        while (leadSelect.options.length > 1) {
            leadSelect.remove(1);
        }

        // Add options for each lead
        eligibleLeads.forEach(lead => {
            const option = document.createElement('option');
            option.value = lead.id;
            option.textContent = `${lead.first_name} ${lead.last_name} - ${lead.company || 'N/A'} (${lead.country})`;
            option.dataset.country = lead.country;
            leadSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading leads for payment:', error);
        showNotification('error', 'Error loading leads: ' + error.message);
    }
}

// Function to load lead info when selected
async function loadLeadInfo() {
    const leadSelect = document.getElementById('lead-select');
    const leadInfo = document.getElementById('lead-info');
    const pricingSuggestions = document.getElementById('pricing-suggestions');
    const currencySymbol = document.getElementById('currency-symbol');

    // Clear lead info
    leadInfo.innerHTML = '';
    pricingSuggestions.innerHTML = '';

    if (!leadSelect.value) {
        return;
    }

    try {
        // Get lead details
        const response = await window.api.getLeads({ lead_ids: [leadSelect.value] });

        if (!response.success || !response.data || response.data.length === 0) {
            throw new Error('Failed to load lead details');
        }

        const lead = response.data[0];

        // Set currency symbol based on country
        currencySymbol.textContent = lead.country === 'US' ? '$' : '₹';

        // Display lead info
        leadInfo.innerHTML = `
            <div class="alert alert-info mb-3">
                <div class="d-flex justify-content-between">
                    <strong>${lead.first_name} ${lead.last_name}</strong>
                    <span>${lead.country === 'US' ? '🇺🇸 United States' : '🇮🇳 India'}</span>
                </div>
                <div>Company: ${lead.company || 'N/A'}</div>
                <div>Email: ${lead.email || 'N/A'}</div>
                <div>Status: ${window.utils.createStatusBadge(lead.status)}</div>
            </div>
        `;

        // Get pricing suggestions based on lead data
        // This would typically come from API but we'll simulate it here
        let suggestedPricing;

        if (lead.country === 'US') {
            suggestedPricing = {
                standard: 2500,
                premium: 3500,
                enterprise: 5000
            };

            // Adjust based on company size
            const companySize = parseInt(lead.company_size || '0');
            if (companySize > 100) {
                suggestedPricing = {
                    standard: 3000,
                    premium: 4200,
                    enterprise: 6000
                };
            }
        } else {
            // India pricing in INR
            suggestedPricing = {
                standard: 40000,
                premium: 85000,
                enterprise: 150000
            };

            // Adjust based on company size
            const companySize = parseInt(lead.company_size || '0');
            if (companySize > 100) {
                suggestedPricing = {
                    standard: 50000,
                    premium: 100000,
                    enterprise: 180000
                };
            }
        }

        // Display pricing suggestions
        pricingSuggestions.innerHTML = `
            <div class="mt-2">Suggested pricing:</div>
            <div class="d-flex justify-content-between">
                <button type="button" class="btn btn-sm btn-outline-primary pricing-btn" data-amount="${suggestedPricing.standard}">
                    Standard: ${lead.country === 'US' ? '$' : '₹'}${suggestedPricing.standard.toLocaleString()}
                </button>
                <button type="button" class="btn btn-sm btn-outline-primary pricing-btn" data-amount="${suggestedPricing.premium}">
                    Premium: ${lead.country === 'US' ? '$' : '₹'}${suggestedPricing.premium.toLocaleString()}
                </button>
                <button type="button" class="btn btn-sm btn-outline-primary pricing-btn" data-amount="${suggestedPricing.enterprise}">
                    Enterprise: ${lead.country === 'US' ? '$' : '₹'}${suggestedPricing.enterprise.toLocaleString()}
                </button>
            </div>
        `;

        // Add event listeners to pricing buttons
        document.querySelectorAll('.pricing-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('payment-amount').value = btn.getAttribute('data-amount');
            });
        });

    } catch (error) {
        console.error('Error loading lead info:', error);
        leadInfo.innerHTML = `
            <div class="alert alert-danger mb-3">
                Error loading lead info: ${error.message}
            </div>
        `;
    }
}

// Function to send payment link
async function sendPaymentLink(e) {
    e.preventDefault();

    const leadId = document.getElementById('lead-select').value;
    const amount = document.getElementById('payment-amount').value;

    if (!leadId) {
        showNotification('error', 'Please select a lead');
        return;
    }

    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
        showNotification('error', 'Please enter a valid amount');
        return;
    }

    // Show loading state
    const submitButton = document.getElementById('send-payment-btn');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Creating payment link...
    `;

    try {
        // Call API to create payment link
        const response = await window.api.createPayment(leadId, parseFloat(amount));

        if (!response.success) {
            throw new Error(response.error || 'Failed to create payment link');
        }

        // Success
        showNotification('success', 'Payment link sent successfully!');

        // Reset form
        document.getElementById('payment-form').reset();
        document.getElementById('lead-info').innerHTML = '';
        document.getElementById('pricing-suggestions').innerHTML = '';

        // Refresh payment history
        loadPaymentHistory();

    } catch (error) {
        console.error('Error sending payment link:', error);
        showNotification('error', 'Error sending payment link: ' + error.message);
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }
}

// Function to load payment history
async function loadPaymentHistory() {
    const container = document.getElementById('recent-payments');

    try {
        // Fetch leads with payment status
        const response = await window.api.getLeads({
            status: ['Payment Link Sent', 'Payment Link Clicked', 'Payment Received', 'Onboarding']
        });

        if (!response.success) {
            throw new Error(response.error || 'Failed to load payment history');
        }

        const paymentLeads = response.data || [];

        if (paymentLeads.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info" role="alert">
                    <i class="fas fa-info-circle"></i> No payment history available.
                </div>
            `;
            return;
        }

        // Sort by most recent
        paymentLeads.sort((a, b) => {
            return new Date(b.last_contact || 0) - new Date(a.last_contact || 0);
        });

        // Display payment history
        let html = `
            <div class="list-group">
        `;

        paymentLeads.forEach(lead => {
            const countryFlag = lead.country === 'US' ? '🇺🇸' : '🇮🇳';

            // Extract payment amount from notes (this would be better stored in a dedicated field)
            let paymentAmount = 'N/A';
            if (lead.notes && lead.notes.includes('payment link:')) {
                const match = lead.notes.match(/for (\$|₹)([0-9,.]+)/);
                if (match) {
                    paymentAmount = match[1] + match[2];
                }
            }

            // Get status icon
            let statusIcon = 'fa-paper-plane';
            if (lead.status === 'Payment Link Clicked') {
                statusIcon = 'fa-mouse-pointer';
            } else if (lead.status === 'Payment Received') {
                statusIcon = 'fa-check-circle';
            } else if (lead.status === 'Onboarding') {
                statusIcon = 'fa-user-plus';
            }

            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas ${statusIcon} me-2"></i>
                            <strong>${lead.first_name} ${lead.last_name}</strong>
                        </div>
                        <div>${countryFlag}</div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-1">
                        <div>${lead.company || 'N/A'}</div>
                        <div>${paymentAmount}</div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-1">
                        <div>${window.utils.createStatusBadge(lead.status)}</div>
                        <small>${lead.last_contact || 'N/A'}</small>
                    </div>
                </div>
            `;
        });

        html += `
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading payment history:', error);
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-circle"></i> Error loading payment history: ${error.message}
            </div>
        `;
    }
}
