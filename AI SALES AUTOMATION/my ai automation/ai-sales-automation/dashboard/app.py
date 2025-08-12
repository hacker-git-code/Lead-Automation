#!/usr/bin/env python3
"""
AI Sales Automation Dashboard
A simple web interface to monitor the AI sales automation system.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules from the main application
from modules.google_sheets import GoogleSheetsManager
from modules.lead_generation import LeadManager
from config import GoogleSheetsConfig

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("../logs/dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize the Google Sheets manager
try:
    sheets_manager = GoogleSheetsManager(
        credentials_file=GoogleSheetsConfig.CREDENTIALS_FILE,
        sheet_id=GoogleSheetsConfig.SHEET_ID
    )
    logger.info("Google Sheets manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Sheets manager: {str(e)}")
    # Create a dummy manager for demo purposes
    sheets_manager = None

# Sample data for demo purposes
def get_demo_data():
    return {
        "leads": [
            {"name": "John Doe", "company": "Tech Agency", "title": "CEO", "location": "United States", "status": "New", "x_username": "johndoe", "instagram_username": "johndoe_tech"},
            {"name": "Jane Smith", "company": "Digital Marketing Inc", "title": "Founder", "location": "United States", "status": "Contacted", "x_username": "janesmith", "instagram_username": "jane_digital"},
            {"name": "Raj Patel", "company": "WebSolution", "title": "CEO", "location": "India", "status": "Engaged", "x_username": "rajpatel", "instagram_username": "raj_websolution"},
            {"name": "Sarah Johnson", "company": "Growth Hackers", "title": "Founder", "location": "United States", "status": "Opportunity", "x_username": "sarahj", "instagram_username": "sarah_growth"},
            {"name": "Amit Kumar", "company": "CloudTech Solutions", "title": "Director", "location": "India", "status": "Deal Sent", "x_username": "amitkumar", "instagram_username": "amit_cloudtech"},
            {"name": "Mike Wilson", "company": "SaaS Platform", "title": "CEO", "location": "United States", "status": "Customer", "x_username": "mikewilson", "instagram_username": "mike_saas"},
        ],
        "outreach": [
            {"lead_id": "1", "platform": "x", "action": "follow", "date_sent": "2025-03-10", "response": ""},
            {"lead_id": "1", "platform": "x", "action": "initial_dm", "date_sent": "2025-03-10", "response": ""},
            {"lead_id": "2", "platform": "instagram", "action": "follow", "date_sent": "2025-03-10", "response": ""},
            {"lead_id": "2", "platform": "instagram", "action": "initial_dm", "date_sent": "2025-03-10", "response": ""},
            {"lead_id": "3", "platform": "x", "action": "follow", "date_sent": "2025-03-11", "response": ""},
            {"lead_id": "3", "platform": "x", "action": "initial_dm", "date_sent": "2025-03-11", "response": "Interested"},
            {"lead_id": "3", "platform": "x", "action": "positive_response", "date_sent": "2025-03-11", "response": ""},
            {"lead_id": "4", "platform": "instagram", "action": "follow", "date_sent": "2025-03-12", "response": ""},
            {"lead_id": "4", "platform": "instagram", "action": "initial_dm", "date_sent": "2025-03-12", "response": "Interested"},
            {"lead_id": "4", "platform": "instagram", "action": "positive_response", "date_sent": "2025-03-12", "response": ""},
            {"lead_id": "5", "platform": "x", "action": "follow", "date_sent": "2025-03-12", "response": ""},
            {"lead_id": "5", "platform": "x", "action": "initial_dm", "date_sent": "2025-03-12", "response": "Interested"},
            {"lead_id": "5", "platform": "x", "action": "positive_response", "date_sent": "2025-03-13", "response": ""},
        ],
        "deals": [
            {"lead_id": "5", "package": "Basic AI Sales Automation", "price": 40000, "currency": "INR", "status": "Pending", "payment_method": "razorpay"},
            {"lead_id": "6", "package": "Premium AI Sales Automation", "price": 5000, "currency": "USD", "status": "Completed", "payment_method": "stripe"},
        ],
        "content": [
            {"date": "2025-03-15", "platforms": ["x", "instagram"], "category": "success_stories", "content": "How an agency saved 10+ hours/week with our AI automation system. #AIautomation #AgencyGrowth"},
            {"date": "2025-03-16", "platforms": ["x", "instagram"], "category": "client_results", "content": "Our client just landed 5 new high-ticket clients using our AI automation! Here's how: #ClientSuccess"},
            {"date": "2025-03-17", "platforms": ["x"], "category": "behind_the_scenes", "content": "Here's how our AI identifies high-quality leads that are ready to buy: #BehindTheScenes"},
            {"date": "2025-03-18", "platforms": ["x", "instagram"], "category": "tips_and_tricks", "content": "3 ways to optimize your sales process with AI automation: 1) Lead qualification 2) Personalized outreach 3) Follow-up management #SalesTips"},
            {"date": "2025-03-19", "platforms": ["x", "instagram"], "category": "success_stories", "content": "Case study: How a digital agency increased sales meetings by 45% with AI outreach. #SalesAutomation"},
        ]
    }

@app.route('/')
def index():
    """Dashboard home page."""
    return render_template('index.html')

@app.route('/api/leads')
def get_leads():
    """Get lead data."""
    try:
        if sheets_manager:
            leads = sheets_manager.get_leads()
        else:
            leads = get_demo_data()["leads"]

        return jsonify({
            "success": True,
            "data": leads
        })
    except Exception as e:
        logger.error(f"Error getting leads: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/leads/stats')
def get_lead_stats():
    """Get lead statistics."""
    try:
        if sheets_manager:
            leads = sheets_manager.get_leads()
        else:
            leads = get_demo_data()["leads"]

        # Count leads by status
        status_counts = {}
        for lead in leads:
            status = lead.get("status", "New")
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1

        # Count leads by location
        location_counts = {}
        for lead in leads:
            location = lead.get("location", "Unknown")
            if "India" in location:
                location = "India"
            elif "United States" in location or "USA" in location:
                location = "United States"

            if location in location_counts:
                location_counts[location] += 1
            else:
                location_counts[location] = 1

        return jsonify({
            "success": True,
            "data": {
                "total_leads": len(leads),
                "status_counts": status_counts,
                "location_counts": location_counts
            }
        })
    except Exception as e:
        logger.error(f"Error getting lead stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/outreach')
def get_outreach():
    """Get outreach data."""
    try:
        if sheets_manager:
            outreach_worksheet = sheets_manager._get_worksheet(GoogleSheetsConfig.OUTREACH_SHEET, create_if_missing=False)
            if outreach_worksheet:
                outreach = outreach_worksheet.get_all_records()
            else:
                outreach = []
        else:
            outreach = get_demo_data()["outreach"]

        return jsonify({
            "success": True,
            "data": outreach
        })
    except Exception as e:
        logger.error(f"Error getting outreach data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/outreach/stats')
def get_outreach_stats():
    """Get outreach statistics."""
    try:
        if sheets_manager:
            outreach_worksheet = sheets_manager._get_worksheet(GoogleSheetsConfig.OUTREACH_SHEET, create_if_missing=False)
            if outreach_worksheet:
                outreach = outreach_worksheet.get_all_records()
            else:
                outreach = []
        else:
            outreach = get_demo_data()["outreach"]

        # Count actions
        action_counts = {}
        for record in outreach:
            action = record.get("action", "")
            if action in action_counts:
                action_counts[action] += 1
            else:
                action_counts[action] = 1

        # Count platforms
        platform_counts = {}
        for record in outreach:
            platform = record.get("platform", "")
            if platform in platform_counts:
                platform_counts[platform] += 1
            else:
                platform_counts[platform] = 1

        # Count response rate
        response_count = sum(1 for record in outreach if record.get("response", ""))

        return jsonify({
            "success": True,
            "data": {
                "total_outreach": len(outreach),
                "action_counts": action_counts,
                "platform_counts": platform_counts,
                "response_count": response_count,
                "response_rate": (response_count / len(outreach) * 100) if outreach else 0
            }
        })
    except Exception as e:
        logger.error(f"Error getting outreach stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/deals')
def get_deals():
    """Get deal data."""
    try:
        if sheets_manager:
            deals_worksheet = sheets_manager._get_worksheet(GoogleSheetsConfig.DEALS_SHEET, create_if_missing=False)
            if deals_worksheet:
                deals = deals_worksheet.get_all_records()
            else:
                deals = []
        else:
            deals = get_demo_data()["deals"]

        return jsonify({
            "success": True,
            "data": deals
        })
    except Exception as e:
        logger.error(f"Error getting deal data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/deals/stats')
def get_deal_stats():
    """Get deal statistics."""
    try:
        if sheets_manager:
            deals_worksheet = sheets_manager._get_worksheet(GoogleSheetsConfig.DEALS_SHEET, create_if_missing=False)
            if deals_worksheet:
                deals = deals_worksheet.get_all_records()
            else:
                deals = []
        else:
            deals = get_demo_data()["deals"]

        # Calculate total revenue
        usd_revenue = sum(deal.get("price", 0) for deal in deals if deal.get("currency") == "USD" and deal.get("status") == "Completed")
        inr_revenue = sum(deal.get("price", 0) for deal in deals if deal.get("currency") == "INR" and deal.get("status") == "Completed")

        # Count by status
        status_counts = {}
        for deal in deals:
            status = deal.get("status", "")
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1

        # Count by package
        package_counts = {}
        for deal in deals:
            package = deal.get("package", "")
            if package in package_counts:
                package_counts[package] += 1
            else:
                package_counts[package] = 1

        return jsonify({
            "success": True,
            "data": {
                "total_deals": len(deals),
                "completed_deals": status_counts.get("Completed", 0),
                "usd_revenue": usd_revenue,
                "inr_revenue": inr_revenue,
                "status_counts": status_counts,
                "package_counts": package_counts
            }
        })
    except Exception as e:
        logger.error(f"Error getting deal stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/content')
def get_content():
    """Get content schedule."""
    try:
        # Read content schedule from the most recent file
        schedule_dir = "../data/schedules"
        if os.path.exists(schedule_dir):
            schedule_files = [f for f in os.listdir(schedule_dir) if f.startswith("content_schedule_") and f.endswith(".json")]
            schedule_files.sort(reverse=True)  # Sort by filename (which includes date)

            if schedule_files:
                schedule_file = os.path.join(schedule_dir, schedule_files[0])
                with open(schedule_file, "r") as f:
                    schedule = json.load(f)

                # Convert to list of content items
                content = []
                for date, item in schedule.items():
                    content_item = {
                        "date": date,
                        "content": item.get("content", ""),
                        "platforms": item.get("platforms", []),
                        "image_path": item.get("image_path", "")
                    }
                    content.append(content_item)

                # Sort by date
                content.sort(key=lambda x: x["date"])
            else:
                content = []
        else:
            content = get_demo_data()["content"]

        return jsonify({
            "success": True,
            "data": content
        })
    except Exception as e:
        logger.error(f"Error getting content schedule: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": get_demo_data()["content"]  # Fallback to demo data
        })

@app.route('/api/content/stats')
def get_content_stats():
    """Get content statistics."""
    try:
        content = None

        # Read content schedule from the most recent file
        schedule_dir = "../data/schedules"
        if os.path.exists(schedule_dir):
            schedule_files = [f for f in os.listdir(schedule_dir) if f.startswith("content_schedule_") and f.endswith(".json")]
            schedule_files.sort(reverse=True)  # Sort by filename (which includes date)

            if schedule_files:
                schedule_file = os.path.join(schedule_dir, schedule_files[0])
                with open(schedule_file, "r") as f:
                    schedule = json.load(f)

                # Convert to list of content items
                content = []
                for date, item in schedule.items():
                    content_item = {
                        "date": date,
                        "content": item.get("content", ""),
                        "platforms": item.get("platforms", []),
                        "category": "unknown"  # We don't store category in the schedule
                    }
                    content.append(content_item)

        if not content:
            content = get_demo_data()["content"]

        # Count by platform
        platform_counts = {"x": 0, "instagram": 0}
        for item in content:
            for platform in item.get("platforms", []):
                if platform in platform_counts:
                    platform_counts[platform] += 1

        # Count by category if available
        category_counts = {}
        for item in content:
            category = item.get("category", "unknown")
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1

        return jsonify({
            "success": True,
            "data": {
                "total_content": len(content),
                "platform_counts": platform_counts,
                "category_counts": category_counts
            }
        })
    except Exception as e:
        logger.error(f"Error getting content stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/funnel')
def get_funnel():
    """Get sales funnel data."""
    try:
        if sheets_manager:
            leads = sheets_manager.get_leads()
        else:
            leads = get_demo_data()["leads"]

        # Count leads by status for funnel
        status_order = ["New", "Contacted", "Engaged", "Opportunity", "Deal Sent", "Customer"]
        funnel_data = []

        status_counts = {}
        for lead in leads:
            status = lead.get("status", "New")
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1

        for status in status_order:
            funnel_data.append({
                "status": status,
                "count": status_counts.get(status, 0)
            })

        return jsonify({
            "success": True,
            "data": funnel_data
        })
    except Exception as e:
        logger.error(f"Error getting funnel data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/overview')
def get_overview():
    """Get system overview stats."""
    try:
        # Get demo data for testing
        demo_data = get_demo_data()

        # Use real data if available
        if sheets_manager:
            leads = sheets_manager.get_leads()
            outreach_worksheet = sheets_manager._get_worksheet(GoogleSheetsConfig.OUTREACH_SHEET, create_if_missing=False)
            deals_worksheet = sheets_manager._get_worksheet(GoogleSheetsConfig.DEALS_SHEET, create_if_missing=False)

            if outreach_worksheet:
                outreach = outreach_worksheet.get_all_records()
            else:
                outreach = demo_data["outreach"]

            if deals_worksheet:
                deals = deals_worksheet.get_all_records()
            else:
                deals = demo_data["deals"]
        else:
            leads = demo_data["leads"]
            outreach = demo_data["outreach"]
            deals = demo_data["deals"]

        # Calculate conversion rates
        total_leads = len(leads)
        engaged_leads = sum(1 for lead in leads if lead.get("status") in ["Engaged", "Opportunity", "Deal Sent", "Customer"])
        customers = sum(1 for lead in leads if lead.get("status") == "Customer")

        engagement_rate = (engaged_leads / total_leads * 100) if total_leads > 0 else 0
        conversion_rate = (customers / total_leads * 100) if total_leads > 0 else 0

        # Calculate total revenue
        usd_revenue = sum(deal.get("price", 0) for deal in deals if deal.get("currency") == "USD" and deal.get("status") == "Completed")
        inr_revenue = sum(deal.get("price", 0) for deal in deals if deal.get("currency") == "INR" and deal.get("status") == "Completed")

        # Get recent activities
        recent_outreach = sorted(outreach, key=lambda x: x.get("date_sent", ""), reverse=True)[:5]

        return jsonify({
            "success": True,
            "data": {
                "total_leads": total_leads,
                "engaged_leads": engaged_leads,
                "customers": customers,
                "engagement_rate": engagement_rate,
                "conversion_rate": conversion_rate,
                "usd_revenue": usd_revenue,
                "inr_revenue": inr_revenue,
                "recent_outreach": recent_outreach
            }
        })
    except Exception as e:
        logger.error(f"Error getting overview data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
