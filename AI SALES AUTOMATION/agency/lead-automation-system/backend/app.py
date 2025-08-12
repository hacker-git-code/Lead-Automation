import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import json
import logging
from functools import wraps

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

# Authentication middleware
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get authorization header
        auth_header = request.headers.get('Authorization')

        # In a real app, this would verify the JWT token
        # For demonstration, we'll check for a dummy token
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "error": "Authentication required"}), 401

        token = auth_header.replace('Bearer ', '')

        # Check if token is valid (in a real app, this would use JWT verification)
        if token != 'admin-token':
            return jsonify({"success": False, "error": "Admin access required"}), 403

        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

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

# Admin API Routes
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    """
    Get system statistics for admin dashboard
    """
    try:
        # In a real app, this would fetch actual statistics
        # For demonstration, we'll return mock data
        stats = {
            "users": {
                "total": 12,
                "growth": 5,
                "active": 10
            },
            "campaigns": {
                "total": 15,
                "active": 8,
                "growth": -2
            },
            "leads": {
                "total": 468,
                "growth": 12,
                "by_country": {
                    "US": 285,
                    "India": 183
                },
                "by_source": {
                    "Apollo": 210,
                    "LinkedIn": 117,
                    "Website": 70,
                    "Referral": 47,
                    "Other": 24
                }
            },
            "conversions": {
                "rate": 5.7,
                "growth": 0.8,
                "by_campaign": {
                    "SaaS Founders": 12.4,
                    "Agency Owners": 9.6,
                    "Tech Startups": 7.2,
                    "E-commerce": 6.8,
                    "Healthcare": 5.2
                }
            },
            "ai_performance": {
                "email_response_rate": 92,
                "personalization_accuracy": 87,
                "lead_qualification_accuracy": 78,
                "content_generation_quality": 83,
                "api_call_success_rate": 95
            },
            "api_usage": {
                "Apollo": 580,
                "Gmail": 420,
                "Outlook": 320,
                "Stripe": 180,
                "Razorpay": 140,
                "Sheets": 640
            },
            "system_health": {
                "server_status": "Online",
                "database_status": "Healthy",
                "api_services_status": "Operational",
                "storage_usage": 42,
                "storage_free": "8.4 GB",
                "last_backup": "June 20, 2023 (04:30 AM)"
            }
        }

        return jsonify({"success": True, "data": stats})
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get all users (admin only)
    """
    try:
        # In a real app, this would fetch from the database
        # For demonstration, we'll return mock data
        users = [
            {
                "id": "1",
                "email": "admin@example.com",
                "name": "Admin User",
                "role": "admin",
                "lastLogin": "2023-06-22T14:35:12Z",
                "status": "active"
            },
            {
                "id": "2",
                "email": "sarah@example.com",
                "name": "Sarah Johnson",
                "role": "user",
                "lastLogin": "2023-06-22T10:12:45Z",
                "status": "active"
            },
            {
                "id": "3",
                "email": "mike@example.com",
                "name": "Mike Davis",
                "role": "user",
                "lastLogin": "2023-06-21T16:42:19Z",
                "status": "active"
            }
        ]

        return jsonify({"success": True, "data": users})
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/content/schedule', methods=['GET'])
@admin_required
def get_content_schedule():
    """
    Get upcoming content schedule (admin only)
    """
    try:
        # In a real app, this would fetch from the database
        # For demonstration, we'll return mock data
        schedule = [
            {
                "id": "1",
                "type": "Email Sequence",
                "campaign": "Tech Startup Outreach",
                "scheduled_date": "2023-06-25",
                "status": "Pending",
                "creator": "AI Assistant"
            },
            {
                "id": "2",
                "type": "LinkedIn Post",
                "campaign": "Agency Growth 2023",
                "scheduled_date": "2023-06-26",
                "status": "Approved",
                "creator": "AI Assistant"
            },
            {
                "id": "3",
                "type": "Follow-up Email",
                "campaign": "SaaS Founders",
                "scheduled_date": "2023-06-27",
                "status": "Drafting",
                "creator": "AI Assistant"
            },
            {
                "id": "4",
                "type": "Sales Call Script",
                "campaign": "E-commerce Solutions",
                "scheduled_date": "2023-06-28",
                "status": "In Review",
                "creator": "Sarah J."
            },
            {
                "id": "5",
                "type": "Case Study",
                "campaign": "Healthcare Tech",
                "scheduled_date": "2023-06-30",
                "status": "In Progress",
                "creator": "AI Assistant"
            }
        ]

        return jsonify({"success": True, "data": schedule})
    except Exception as e:
        logger.error(f"Error getting content schedule: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/system/logs', methods=['GET'])
@admin_required
def get_system_logs():
    """
    Get system activity logs (admin only)
    """
    try:
        # In a real app, this would read from log files
        # For demonstration, we'll return mock data
        logs = [
            {
                "id": "1",
                "timestamp": "2023-06-22T15:15:32Z",
                "type": "user_creation",
                "description": "New user registered: Sarah Johnson (sarah@example.com)",
                "level": "info"
            },
            {
                "id": "2",
                "timestamp": "2023-06-22T14:30:12Z",
                "type": "campaign_creation",
                "description": "Campaign created: Tech Startup Outreach 2023",
                "level": "info"
            },
            {
                "id": "3",
                "timestamp": "2023-06-22T13:02:45Z",
                "type": "api_update",
                "description": "Apollo.io API configuration updated",
                "level": "info"
            },
            {
                "id": "4",
                "timestamp": "2023-06-22T09:23:18Z",
                "type": "template_update",
                "description": "Email template modified: Follow-up #2 for Marketing Agencies",
                "level": "info"
            },
            {
                "id": "5",
                "timestamp": "2023-06-21T04:30:02Z",
                "type": "system_backup",
                "description": "Full database backup completed (3.2 GB)",
                "level": "info"
            }
        ]

        return jsonify({"success": True, "data": logs})
    except Exception as e:
        logger.error(f"Error getting system logs: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/sales-performance', methods=['GET'])
@admin_required
def get_sales_performance():
    """
    Get sales performance data (admin only)
    """
    try:
        period = request.args.get('period', 'monthly')

        # In a real app, this would fetch from a database
        # For demonstration, we'll return mock data
        if period == 'daily':
            data = {
                "labels": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                "us_data": [12, 19, 15, 17, 14, 10, 8],
                "india_data": [8, 15, 12, 14, 10, 7, 5]
            }
        elif period == 'weekly':
            data = {
                "labels": ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                "us_data": [52, 65, 58, 70],
                "india_data": [42, 48, 39, 55]
            }
        else:  # monthly
            data = {
                "labels": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                "us_data": [65, 78, 90, 85, 110, 125],
                "india_data": [45, 58, 70, 75, 92, 108]
            }

        return jsonify({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Error getting sales performance data: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=os.environ.get('DEBUG', 'True') == 'True', host='0.0.0.0', port=port)
