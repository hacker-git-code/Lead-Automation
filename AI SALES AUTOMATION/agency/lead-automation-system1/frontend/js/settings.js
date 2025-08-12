// Settings functionality
window.loadSettings = function() {
    // Load settings HTML if not already loaded
    const settingsSection = document.getElementById('settings-section');

    if (!settingsSection.innerHTML.trim()) {
        // Load initial HTML
        settingsSection.innerHTML = `
            <div class="container-fluid">
                <h2>Settings</h2>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                API Credentials
                            </div>
                            <div class="card-body">
                                <form id="api-credentials-form">
                                    <div class="mb-3">
                                        <label for="apollo-api-key" class="form-label">Apollo.io API Key</label>
                                        <input type="password" class="form-control" id="apollo-api-key" placeholder="Enter API key">
                                    </div>

                                    <h5 class="mt-4">Email Integration</h5>

                                    <div class="mb-3">
                                        <label for="gmail-username" class="form-label">Gmail Username (for India leads)</label>
                                        <input type="email" class="form-control" id="gmail-username" placeholder="Enter Gmail address">
                                    </div>

                                    <div class="mb-3">
                                        <label for="gmail-password" class="form-label">Gmail App Password</label>
                                        <input type="password" class="form-control" id="gmail-password" placeholder="Enter app password">
                                        <div class="form-text">
                                            <a href="https://support.google.com/accounts/answer/185833" target="_blank">
                                                How to create an app password
                                            </a>
                                        </div>
                                    </div>

                                    <div class="mb-3">
                                        <label for="outlook-email" class="form-label">Outlook Email (for US leads)</label>
                                        <input type="email" class="form-control" id="outlook-email" placeholder="Enter Outlook address">
                                    </div>

                                    <div class="mb-3">
                                        <label for="outlook-password" class="form-label">Outlook App Password</label>
                                        <input type="password" class="form-control" id="outlook-password" placeholder="Enter app password">
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-primary">
                                            <i class="fas fa-save"></i> Save API Credentials
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                Payment Gateway Settings
                            </div>
                            <div class="card-body">
                                <form id="payment-gateway-form">
                                    <h5>Stripe (US Payments)</h5>

                                    <div class="mb-3">
                                        <label for="stripe-api-key" class="form-label">Stripe API Key</label>
                                        <input type="password" class="form-control" id="stripe-api-key" placeholder="Enter Stripe API key">
                                    </div>

                                    <div class="mb-3">
                                        <label for="stripe-secret-key" class="form-label">Stripe Secret Key</label>
                                        <input type="password" class="form-control" id="stripe-secret-key" placeholder="Enter Stripe secret key">
                                    </div>

                                    <h5 class="mt-4">Razorpay (India Payments)</h5>

                                    <div class="mb-3">
                                        <label for="razorpay-key-id" class="form-label">Razorpay Key ID</label>
                                        <input type="password" class="form-control" id="razorpay-key-id" placeholder="Enter Razorpay key ID">
                                    </div>

                                    <div class="mb-3">
                                        <label for="razorpay-key-secret" class="form-label">Razorpay Key Secret</label>
                                        <input type="password" class="form-control" id="razorpay-key-secret" placeholder="Enter Razorpay key secret">
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-primary">
                                            <i class="fas fa-save"></i> Save Payment Settings
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>

                        <div class="card mt-4">
                            <div class="card-header">
                                Other Settings
                            </div>
                            <div class="card-body">
                                <form id="other-settings-form">
                                    <div class="mb-3">
                                        <label for="calendly-link" class="form-label">Calendly Link</label>
                                        <input type="url" class="form-control" id="calendly-link" placeholder="https://calendly.com/yourusername">
                                    </div>

                                    <div class="mb-3">
                                        <label for="follow-up-days" class="form-label">Follow-up Interval (Days)</label>
                                        <input type="number" class="form-control" id="follow-up-days" min="1" max="14" value="3">
                                    </div>

                                    <div class="mb-3">
                                        <label for="max-follow-ups" class="form-label">Maximum Follow-ups</label>
                                        <input type="number" class="form-control" id="max-follow-ups" min="1" max="10" value="4">
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-primary">
                                            <i class="fas fa-save"></i> Save Other Settings
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners to forms
        document.getElementById('api-credentials-form').addEventListener('submit', handleApiCredentialsForm);
        document.getElementById('payment-gateway-form').addEventListener('submit', handlePaymentGatewayForm);
        document.getElementById('other-settings-form').addEventListener('submit', handleOtherSettingsForm);
    }

    // Load existing settings
    loadExistingSettings();
};

// Function to load existing settings
function loadExistingSettings() {
    // This would fetch settings from the server API in a real implementation
    // For now, we'll just show a notification
    setTimeout(() => {
        showNotification('info', 'Settings loaded successfully');
    }, 500);
}

// Function to handle API credentials form submission
function handleApiCredentialsForm(e) {
    e.preventDefault();

    // Get form values
    const apolloApiKey = document.getElementById('apollo-api-key').value;
    const gmailUsername = document.getElementById('gmail-username').value;
    const gmailPassword = document.getElementById('gmail-password').value;
    const outlookEmail = document.getElementById('outlook-email').value;
    const outlookPassword = document.getElementById('outlook-password').value;

    // Validate the form
    if (!apolloApiKey) {
        showNotification('error', 'Apollo API Key is required');
        return;
    }

    if (!gmailUsername || !gmailPassword) {
        showNotification('error', 'Gmail credentials are required for India leads');
        return;
    }

    if (!outlookEmail || !outlookPassword) {
        showNotification('error', 'Outlook credentials are required for US leads');
        return;
    }

    // In a real implementation, this would send the data to the server
    // For now, just show a success notification
    showNotification('success', 'API credentials saved successfully');
}

// Function to handle payment gateway form submission
function handlePaymentGatewayForm(e) {
    e.preventDefault();

    // Get form values
    const stripeApiKey = document.getElementById('stripe-api-key').value;
    const stripeSecretKey = document.getElementById('stripe-secret-key').value;
    const razorpayKeyId = document.getElementById('razorpay-key-id').value;
    const razorpayKeySecret = document.getElementById('razorpay-key-secret').value;

    // Validate the form
    if (!stripeApiKey || !stripeSecretKey) {
        showNotification('error', 'Stripe credentials are required for US payments');
        return;
    }

    if (!razorpayKeyId || !razorpayKeySecret) {
        showNotification('error', 'Razorpay credentials are required for India payments');
        return;
    }

    // In a real implementation, this would send the data to the server
    // For now, just show a success notification
    showNotification('success', 'Payment gateway settings saved successfully');
}

// Function to handle other settings form submission
function handleOtherSettingsForm(e) {
    e.preventDefault();

    // Get form values
    const calendlyLink = document.getElementById('calendly-link').value;
    const followUpDays = document.getElementById('follow-up-days').value;
    const maxFollowUps = document.getElementById('max-follow-ups').value;

    // Validate the form
    if (!calendlyLink) {
        showNotification('error', 'Calendly link is required');
        return;
    }

    // In a real implementation, this would send the data to the server
    // For now, just show a success notification
    showNotification('success', 'Other settings saved successfully');
}
