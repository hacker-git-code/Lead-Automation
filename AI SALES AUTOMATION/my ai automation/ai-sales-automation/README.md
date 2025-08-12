# AI Sales Automation System

A comprehensive Python-based AI sales automation system that helps grow your business from scratch.

## Overview

This system automates the entire sales workflow to help you acquire high-ticket clients:

1. **Find High-Paying Leads on X & Instagram**
   - Target digital agency owners, SaaS founders, and coaches in the U.S. & India
   - Use Apollo.io to find leads based on industry, revenue, and location
   - Extract active social media users and store in Google Sheets

2. **Automate Cold Outreach on X & Instagram**
   - Auto-follow target leads
   - Send personalized DMs with soft pitches
   - Send follow-ups every 3 days (max 3 times)
   - Stop messaging when they reply or book a call

3. **Engage & Convert Leads**
   - Offer quick calls via Calendly or send detailed emails
   - Track lead status in Google Sheets

4. **Close Sales & Automate Payments**
   - Location-based pricing (U.S. vs India)
   - Auto-send payment links (Stripe for U.S., Razorpay for India)
   - Multiple payment options

5. **Build Trust & Authority**
   - Auto-post valuable content daily to social media
   - Track engagement metrics
   - Showcase success stories and testimonials

## Prerequisites

- Python 3.8+
- Apollo.io API access
- X (Twitter) Developer Account and API keys
- Instagram account credentials
- Stripe account (for U.S. payments)
- Razorpay account (for India payments)
- Google Cloud account with Google Sheets API enabled

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-sales-automation.git
   cd ai-sales-automation
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

5. Set up credentials directories:
   ```bash
   mkdir -p credentials
   # Place your Google Sheets credentials in credentials/google_sheets_credentials.json
   ```

## Configuration

1. Edit the `config.py` file to customize:
   - Target lead parameters
   - Message templates
   - Follow-up schedules
   - Payment packages and pricing
   - Content posting frequency

2. Create directory structure for assets:
   ```bash
   mkdir -p assets/images
   # Add images for Instagram posts in assets/images/
   ```

## Usage

### Running the entire system with scheduling

```bash
python main.py --schedule
```

This will start the system with the following schedule:
- Lead generation: Every Monday at 9:00 AM
- Social outreach: Daily at 10:00 AM
- Response checking: Every 3 hours during weekdays
- Content publishing: Daily at 8:00 AM
- Content scheduling: Every Sunday at 6:00 PM

### Running specific tasks

```bash
# Generate leads
python main.py --task leads

# Execute social outreach
python main.py --task outreach

# Check for responses
python main.py --task responses

# Generate and publish content
python main.py --task content

# Schedule content for the week
python main.py --task schedule
```

### Run all tasks once

```bash
python main.py
```

## Module Breakdown

- **Lead Generation**: Uses Apollo.io to find high-quality leads
- **Google Sheets Manager**: Handles data storage and tracking
- **Social Outreach**: Manages X and Instagram interactions
- **Payment Processing**: Handles Stripe and Razorpay payments
- **Content Generation**: Creates and schedules social media content

## Data Storage

All data is stored in Google Sheets with the following structure:

1. **Leads Sheet**: Stores lead information
   - Name, company, location, contact details, social profiles

2. **Outreach Sheet**: Tracks all outreach activities
   - Messages sent, platforms used, follow-up counts, responses

3. **Deals Sheet**: Manages payment and deal information
   - Package details, pricing, payment status

## Customization

### Message Templates

Edit the message templates in `config.py` under `OutreachConfig`:

```python
INITIAL_DM_TEMPLATE = """
Hey {first_name}! I noticed you're {industry_context}. I help {target_type} automate sales & get more clients with AI. Want to see how?
"""
```

### Payment Packages

Edit the package definitions in `payment_processing.py`:

```python
packages = {
    "basic": {
        "name": "Basic AI Sales Automation",
        "description": "AI-powered lead generation and outreach automation",
        "price_usd": 2500,  # $2,500
        "price_inr": 40000,  # ₹40,000
    },
    # Add more packages as needed
}
```

### Content Templates

Add or modify content templates in `config.py` under `ContentConfig`:

```python
CONTENT_TEMPLATES = {
    "success_stories": [
        "How an agency saved 10+ hours/week with our AI automation system. #AIautomation #AgencyGrowth",
        # Add more templates
    ],
    # Add more categories
}
```

## Best Practices

1. **API Rate Limits**: Be mindful of API rate limits for X, Instagram, and Apollo.io
2. **Message Personalization**: Customize message templates for higher response rates
3. **Content Quality**: Create varied and valuable content for social media
4. **Payment Testing**: Test payment flows in sandbox mode before going live
5. **Regular Maintenance**: Update credentials and tokens as needed

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Check API credentials in `.env` file
2. **Rate Limiting**: Adjust delay parameters in `config.py`
3. **Instagram Blocks**: Use a proper delay between actions to avoid blocks
4. **Apollo.io Errors**: Verify query parameters in the lead generation module

### Logs

Check logs in the `logs/` directory:
- `logs/main.log`: Main system logs
- `logs/lead_generation.log`: Lead generation logs
- `logs/social_outreach.log`: Outreach logs
- `logs/payment_processing.log`: Payment processing logs
- `logs/content_generation.log`: Content generation logs

## Roadmap

- **Email Integration**: Add email outreach capabilities
- **AI Response Analysis**: Analyze lead responses to personalize follow-ups
- **CRM Integration**: Connect with popular CRM systems
- **Custom Analytics Dashboard**: Visualize performance metrics
- **Multi-user Support**: Enable team collaboration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational and ethical business development purposes only. It is the user's responsibility to comply with all applicable laws, terms of service for the platforms used, and data protection regulations. Always respect rate limits and use the system in a responsible manner.

## Support

For questions, issues, or feature requests, please open an issue on GitHub or contact support@yourdomain.com.
