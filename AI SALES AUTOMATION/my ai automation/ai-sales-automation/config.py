"""
Configuration settings for the AI Sales Automation System.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Credentials
class TwitterConfig:
    API_KEY = os.getenv("X_API_KEY")
    API_SECRET = os.getenv("X_API_SECRET")
    ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

class InstagramConfig:
    USERNAME = os.getenv("INSTAGRAM_USERNAME")
    PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

class ApolloConfig:
    API_KEY = os.getenv("APOLLO_API_KEY")
    BASE_URL = "https://api.apollo.io/v1"

    # Target parameters for lead generation
    TARGETS = [
        {
            "title": "Digital Agency Owner",
            "industry": "Marketing and Advertising",
            "locations": ["United States", "India"],
            "min_revenue": 500000,  # Annual revenue in USD
        },
        {
            "title": "SaaS Founder",
            "industry": "Software",
            "locations": ["United States", "India"],
            "min_revenue": 500000,
        },
        {
            "title": "Business Coach",
            "industry": "Professional Training & Coaching",
            "locations": ["United States", "India"],
            "min_revenue": 100000,
        }
    ]

class GoogleSheetsConfig:
    CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

    # Sheets and columns for tracking
    LEADS_SHEET = "Leads"
    LEADS_COLUMNS = [
        "Name", "Company", "Title", "Location", "Industry",
        "X_Username", "Instagram_Username", "Email", "Phone",
        "Source", "Status", "Last_Contact_Date", "Notes"
    ]

    OUTREACH_SHEET = "Outreach"
    OUTREACH_COLUMNS = [
        "Lead_ID", "Platform", "Action", "Message",
        "Date_Sent", "Response", "Follow_Up_Count"
    ]

    DEALS_SHEET = "Deals"
    DEALS_COLUMNS = [
        "Lead_ID", "Package", "Price", "Currency",
        "Payment_Method", "Status", "Close_Date"
    ]

class PaymentConfig:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

    # Pricing
    US_MIN_PRICE = int(os.getenv("US_MIN_PRICE", 2500))
    US_MAX_PRICE = int(os.getenv("US_MAX_PRICE", 5000))
    INDIA_MIN_PRICE = int(os.getenv("INDIA_MIN_PRICE", 40000))
    INDIA_MAX_PRICE = int(os.getenv("INDIA_MAX_PRICE", 150000))

    CURRENCY_BY_LOCATION = {
        "United States": "USD",
        "India": "INR",
        "default": "USD"
    }

    PAYMENT_METHODS = {
        "USD": ["credit_card", "paypal", "wire_transfer"],
        "INR": ["upi", "netbanking", "credit_card", "paypal"]
    }

class CalendlyConfig:
    API_KEY = os.getenv("CALENDLY_API_KEY")
    USER_URI = os.getenv("CALENDLY_USER_URI")
    MEETING_LINK = f"https://calendly.com/{os.getenv('CALENDLY_USER_URI')}/30min"

class OutreachConfig:
    FOLLOW_DELAY = int(os.getenv("FOLLOW_DELAY", 30))  # seconds
    DM_DELAY = int(os.getenv("DM_DELAY", 60))  # seconds
    MAX_DAILY_FOLLOWS = int(os.getenv("MAX_DAILY_FOLLOWS", 50))
    MAX_DAILY_DMS = int(os.getenv("MAX_DAILY_DMS", 30))
    FOLLOW_UP_DAYS = int(os.getenv("FOLLOW_UP_DAYS", 3))
    MAX_FOLLOW_UPS = int(os.getenv("MAX_FOLLOW_UPS", 3))

    # Message templates
    INITIAL_DM_TEMPLATE = """
    Hey {first_name}! I noticed you're {industry_context}. I help {target_type} automate sales & get more clients with AI. Want to see how?
    """

    FOLLOW_UP_TEMPLATES = [
        "Hi {first_name}, just checking in on my previous message. Would you be interested in learning more about how AI can help grow your {business_type}?",
        "Hey {first_name}, I thought you might find this case study interesting: one {target_type} saved 10+ hours/week with our AI automation. Let me know if you'd like to hear more!",
        "Final check-in {first_name} - I've helped {target_type}s like yours increase lead generation by 300%. Happy to share how if you're interested."
    ]

    POSITIVE_RESPONSE_TEMPLATE = """
    Great to hear from you, {first_name}! I'd be happy to share more details.

    Would you prefer:
    1. A quick 30-min call where I can show you a demo? Here's my calendar: {calendly_link}
    2. A detailed email with case studies similar to your business?

    Looking forward to your response!
    """

class ContentConfig:
    POST_FREQUENCY = {
        "X": 1,  # posts per day
        "Instagram": 1  # posts per day
    }

    CONTENT_CATEGORIES = [
        "success_stories",
        "client_results",
        "behind_the_scenes",
        "tips_and_tricks",
        "industry_insights"
    ]

    # Sample content templates
    CONTENT_TEMPLATES = {
        "success_stories": [
            "How an agency saved 10+ hours/week with our AI automation system. #AIautomation #AgencyGrowth",
            "Case study: How a {target_type} increased sales meetings by 45% with AI outreach. #SalesAutomation",
            "From struggling to thriving: How AI helped turn around a {industry} business in just 30 days."
        ],
        "client_results": [
            "Our client just landed 5 new high-ticket clients using our AI automation! Here's how: #ClientSuccess",
            "{target_type} using our system just reported a 300% ROI in the first month! #ROI #AITechnology",
            "Client spotlight: {first_name} from {location} used our AI to book 12 sales calls last week!"
        ],
        "behind_the_scenes": [
            "Here's how our AI identifies high-quality leads that are ready to buy: #BehindTheScenes",
            "This is what happens when our AI starts a conversation with your ideal clients: #AIinAction",
            "A peek at our dashboard showing how our AI automation works in real-time: #TechBehindTheScenes"
        ]
    }
