// Email Outreach functionality
window.loadEmailOutreach = function() {
    // Load email outreach HTML if not already loaded
    const emailOutreachSection = document.getElementById('email-outreach-section');

    if (!emailOutreachSection.innerHTML.trim()) {
        // Load initial HTML
        emailOutreachSection.innerHTML = `
            <div class="container-fluid">
                <h2>Email Outreach</h2>

                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    Email outreach functionality is managed automatically by the system.
                    You can view active campaigns and configure email templates.
                </div>

                <div class="card">
                    <div class="card-header">
                        Active Email Campaigns
                    </div>
                    <div class="card-body">
                        <p class="text-center">
                            <i class="fas fa-sync fa-spin"></i> Loading active campaigns...
                        </p>
                    </div>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        Email Templates
                    </div>
                    <div class="card-body">
                        <p class="text-center">
                            <i class="fas fa-sync fa-spin"></i> Loading email templates...
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    // In a future implementation, this would load active campaigns and templates
    setTimeout(() => {
        emailOutreachSection.querySelector('.card-body:first-of-type').innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                No active email campaigns.
            </div>
        `;

        emailOutreachSection.querySelector('.card-body:last-of-type').innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                Email templates configuration will be available in a future update.
            </div>
        `;
    }, 1000);
};
