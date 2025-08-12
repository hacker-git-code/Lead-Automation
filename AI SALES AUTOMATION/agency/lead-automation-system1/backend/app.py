import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import json
import logging

# Load environment variables
load_dotenv()

# Import services
from services.apollo_service import ApolloService
from services.email_service import EmailService
from services.sheets_service import SheetsService
from services.payment_service import PaymentService
from services.tracking_service import TrackingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
            static_folder='../frontend',
            template_folder='../frontend')
CORS(app)

# Initialize services
apollo_service = ApolloService()
email_service = EmailService()
sheets_service = SheetsService()
payment_service = PaymentService()
tracking_service = TrackingService()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# API Routes
@app.route('/api/leads/search', methods=['POST'])
def search_leads():
    """
    Search for leads on Apollo.io based on provided filters
    """
    try:
        data = request.json
        country = data.get('country', 'US')
        industry = data.get('industry', '')
        revenue = data.get('revenue', '')

        # Search leads through Apollo service
        leads = apollo_service.search_leads(country, industry, revenue)

        # Store leads in Google Sheets
        sheets_service.store_leads(leads)

        return jsonify({"success": True, "data": leads, "count": len(leads)})
    except Exception as e:
        logger.error(f"Error searching leads: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/outreach/start', methods=['POST'])
def start_outreach():
    """
    Start email outreach campaign for selected leads
    """
    try:
        data = request.json
        lead_ids = data.get('lead_ids', [])

        # Get leads from spreadsheet
        leads = sheets_service.get_leads(lead_ids)

        # Start outreach campaign
        results = email_service.start_campaign(leads)

        return jsonify({"success": True, "data": results})
    except Exception as e:
        logger.error(f"Error starting outreach: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/lead/update', methods=['POST'])
def update_lead():
    """
    Update lead status and information
    """
    try:
        data = request.json
        lead_id = data.get('lead_id')
        status = data.get('status')
        notes = data.get('notes', '')

        # Update lead in spreadsheet
        result = sheets_service.update_lead(lead_id, status, notes)

        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"Error updating lead: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/payment/create', methods=['POST'])
def create_payment():
    """
    Create a payment link based on lead location
    """
    try:
        data = request.json
        lead_id = data.get('lead_id')
        amount = data.get('amount')

        # Get lead data
        lead = sheets_service.get_lead(lead_id)
        country = lead.get('country', 'US')

        # Create payment link
        payment_link = payment_service.create_payment_link(country, amount, lead)

        # Update lead with payment link
        sheets_service.update_lead(lead_id, 'Payment Sent', f'Payment link: {payment_link}')

        return jsonify({"success": True, "payment_link": payment_link})
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analytics/get', methods=['GET'])
def get_analytics():
    """
    Get sales funnel analytics
    """
    try:
        analytics = tracking_service.get_analytics()
        return jsonify({"success": True, "data": analytics})
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/webhook/email', methods=['POST'])
def email_webhook():
    """
    Handle email reply webhooks
    """
    try:
        data = request.json
        email_service.handle_reply(data)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error handling email webhook: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/webhook/payment', methods=['POST'])
def payment_webhook():
    """
    Handle payment webhooks from Stripe/Razorpay
    """
    try:
        data = request.json
        payment_service.handle_webhook(data)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error handling payment webhook: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=os.environ.get('DEBUG', 'True') == 'True', host='0.0.0.0', port=port)
