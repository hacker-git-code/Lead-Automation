#!/usr/bin/env python3
"""
AI Sales Automation System - Main Entry Point

This script orchestrates the various modules to create a complete
AI sales automation workflow that includes lead generation, social outreach,
engagement, payment processing, and content marketing.
"""

import os
import time
import logging
import argparse
import schedule
from datetime import datetime, timedelta
import json
import threading
import subprocess
from typing import Dict, Any, List, Optional

# Import our modules
from modules.lead_generation import LeadManager
from modules.google_sheets import GoogleSheetsManager
from modules.social_outreach import SocialOutreachManager
from modules.payment_processing import PaymentManager
from modules.content_generation import SocialMediaPublisher

# Import configuration
from config import (
    GoogleSheetsConfig,
    OutreachConfig,
    ContentConfig
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/main.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SalesAutomationSystem:
    """Main class that orchestrates the AI sales automation workflow."""

    def __init__(self):
        """Initialize the automation system."""
        logger.info("Initializing AI Sales Automation System")

        # Create required directories
        self._create_directories()

        # Initialize managers
        try:
            self.sheets_manager = self._init_sheets_manager()
            logger.info("Google Sheets manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets manager: {str(e)}")
            self.sheets_manager = None

        try:
            self.lead_manager = LeadManager(sheets_manager=self.sheets_manager)
            logger.info("Lead manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize lead manager: {str(e)}")
            self.lead_manager = None

        try:
            self.outreach_manager = SocialOutreachManager(sheets_manager=self.sheets_manager)
            logger.info("Social outreach manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize social outreach manager: {str(e)}")
            self.outreach_manager = None

        try:
            self.payment_manager = PaymentManager(sheets_manager=self.sheets_manager)
            logger.info("Payment manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize payment manager: {str(e)}")
            self.payment_manager = None

        try:
            self.content_publisher = SocialMediaPublisher()
            logger.info("Content publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize content publisher: {str(e)}")
            self.content_publisher = None

        # Dashboard process
        self.dashboard_process = None

    def _create_directories(self):
        """Create necessary directories."""
        directories = [
            "logs",
            "data",
            "data/leads",
            "data/schedules",
            "assets",
            "assets/images",
            "credentials"
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _init_sheets_manager(self) -> GoogleSheetsManager:
        """
        Initialize the Google Sheets manager.

        Returns:
            Initialized GoogleSheetsManager instance
        """
        credentials_file = GoogleSheetsConfig.CREDENTIALS_FILE
        sheet_id = GoogleSheetsConfig.SHEET_ID

        # If credentials don't exist, create dummy
        if not credentials_file or not os.path.exists(credentials_file):
            logger.warning("Google Sheets credentials not found, using dummy")
            credentials_file = "credentials/google_sheets_credentials.json"

            if not os.path.exists(credentials_file):
                dummy_credentials = {
                    "type": "service_account",
                    "project_id": "example-project",
                    "private_key_id": "example-key-id",
                    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEpAIBAAKCAQEAxxx\n-----END PRIVATE KEY-----\n",
                    "client_email": "example@example.iam.gserviceaccount.com",
                    "client_id": "123456789",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/example%40example.iam.gserviceaccount.com"
                }

                with open(credentials_file, "w") as f:
                    json.dump(dummy_credentials, f)

        # Create dummy sheet ID if not provided
        if not sheet_id:
            sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"  # Example Google Sheet ID

        # Initialize and return the manager
        return GoogleSheetsManager(credentials_file=credentials_file, sheet_id=sheet_id)

    def generate_leads(self):
        """Generate leads from Apollo.io."""
        if not self.lead_manager:
            logger.error("Lead manager not initialized, skipping lead generation")
            return

        logger.info("Starting lead generation...")
        leads = self.lead_manager.find_and_store_leads()
        logger.info(f"Generated {len(leads)} leads")

    def execute_social_outreach(self):
        """Execute daily social outreach."""
        if not self.outreach_manager:
            logger.error("Social outreach manager not initialized, skipping outreach")
            return

        logger.info("Starting daily social outreach...")
        self.outreach_manager.execute_daily_outreach(
            limit_follows=OutreachConfig.MAX_DAILY_FOLLOWS,
            limit_dms=OutreachConfig.MAX_DAILY_DMS
        )
        logger.info("Daily social outreach completed")

    def check_lead_responses(self):
        """Check for responses from leads."""
        if not self.outreach_manager or not self.sheets_manager:
            logger.error("Required managers not initialized, skipping response check")
            return

        logger.info("Checking for lead responses...")

        # Get leads that have been contacted
        leads = self.sheets_manager.get_leads(filters={"Status": "Contacted"})

        response_count = 0
        for lead in leads:
            if "id" not in lead:
                continue

            # Check if lead has responded
            if self.outreach_manager.check_for_responses(lead):
                response_count += 1

        logger.info(f"Found {response_count} new responses")

    def generate_and_publish_content(self):
        """Generate and publish content to social media."""
        if not self.content_publisher:
            logger.error("Content publisher not initialized, skipping content publishing")
            return

        logger.info("Generating and publishing social media content...")
        result = self.content_publisher.generate_and_publish(
            platforms=["x", "instagram"]
        )

        if "error" in result:
            logger.error(f"Error publishing content: {result['error']}")
        else:
            logger.info(f"Published content in category: {result['category']}")

    def execute_scheduled_content(self):
        """Execute today's scheduled content."""
        if not self.content_publisher:
            logger.error("Content publisher not initialized, skipping scheduled content")
            return

        logger.info("Executing today's scheduled content...")
        result = self.content_publisher.execute_todays_schedule()

        if "error" in result:
            logger.error(f"Error executing scheduled content: {result['error']}")
        else:
            logger.info(f"Published scheduled content for {result['date']}")

    def schedule_content_for_week(self):
        """Schedule content for the upcoming week."""
        if not self.content_publisher:
            logger.error("Content publisher not initialized, skipping content scheduling")
            return

        logger.info("Scheduling content for the week...")
        content_plan = self.content_publisher.content_generator.generate_week_content()

        schedule = self.content_publisher.schedule_content(
            content_plan,
            platforms=["x", "instagram"],
            image_directory="assets/images"
        )

        logger.info(f"Scheduled {len(schedule)} posts for the week")

    def generate_payment_link(self, lead_id: str, package_id: str):
        """
        Generate a payment link for a lead.

        Args:
            lead_id: Lead ID
            package_id: Package ID
        """
        if not self.payment_manager or not self.sheets_manager:
            logger.error("Required managers not initialized, skipping payment link generation")
            return

        # Get lead information
        leads = self.sheets_manager.get_leads()
        lead = None

        for l in leads:
            if l.get("id") == lead_id:
                lead = l
                break

        if not lead:
            logger.error(f"Lead not found: {lead_id}")
            return

        # Get lead details
        customer_name = lead.get("name", "")
        customer_email = lead.get("email", "")
        country = lead.get("country", "United States")

        try:
            # Generate payment link
            payment_link = self.payment_manager.create_payment_link(
                lead_id=lead_id,
                package_id=package_id,
                customer_name=customer_name,
                customer_email=customer_email,
                country=country
            )

            logger.info(f"Generated payment link for lead {lead_id}, package {package_id}")
            return payment_link
        except Exception as e:
            logger.error(f"Error generating payment link: {str(e)}")
            return None

    def check_payment_status(self, payment_id: str, processor_name: str):
        """
        Check the status of a payment.

        Args:
            payment_id: Payment ID
            processor_name: Payment processor name
        """
        if not self.payment_manager:
            logger.error("Payment manager not initialized, skipping payment status check")
            return

        try:
            status = self.payment_manager.check_payment_status(payment_id, processor_name)
            logger.info(f"Payment status for {payment_id}: {status.get('status', 'unknown')}")
            return status
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")
            return {"error": str(e)}

    def start_dashboard(self, port: int = 5000):
        """
        Start the dashboard in a separate process.

        Args:
            port: Port number for the dashboard
        """
        logger.info(f"Starting dashboard on port {port}...")

        try:
            # Change to the dashboard directory and start the server
            dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard")

            # Create a new process for the dashboard
            cmd = [sys.executable, "run_dashboard.py"]
            env = os.environ.copy()
            env["PORT"] = str(port)

            self.dashboard_process = subprocess.Popen(
                cmd,
                cwd=dashboard_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"Dashboard started with PID {self.dashboard_process.pid}")
            logger.info(f"Dashboard available at http://localhost:{port}")

            return True
        except Exception as e:
            logger.error(f"Error starting dashboard: {str(e)}")
            return False

    def stop_dashboard(self):
        """Stop the dashboard process."""
        if self.dashboard_process:
            logger.info("Stopping dashboard...")
            self.dashboard_process.terminate()
            self.dashboard_process = None
            logger.info("Dashboard stopped")

    def run_scheduled_tasks(self):
        """Set up and run scheduled tasks."""
        logger.info("Setting up scheduled tasks...")

        # Schedule lead generation (weekly on Monday)
        schedule.every().monday.at("09:00").do(self.generate_leads)

        # Schedule daily outreach (every day at 10:00)
        schedule.every().day.at("10:00").do(self.execute_social_outreach)

        # Schedule response checking (every 3 hours during weekdays)
        for hour in [9, 12, 15, 18]:
            schedule.every().monday.at(f"{hour:02d}:00").do(self.check_lead_responses)
            schedule.every().tuesday.at(f"{hour:02d}:00").do(self.check_lead_responses)
            schedule.every().wednesday.at(f"{hour:02d}:00").do(self.check_lead_responses)
            schedule.every().thursday.at(f"{hour:02d}:00").do(self.check_lead_responses)
            schedule.every().friday.at(f"{hour:02d}:00").do(self.check_lead_responses)

        # Schedule content publishing (every day at 08:00)
        schedule.every().day.at("08:00").do(self.execute_scheduled_content)

        # Schedule weekly content planning (every Sunday at 18:00)
        schedule.every().sunday.at("18:00").do(self.schedule_content_for_week)

        logger.info("Starting scheduler...")

        # Run the scheduler in a loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Wait a minute before checking again

    def run_once(self, task: str = None):
        """
        Run a specific task once.

        Args:
            task: Task to run
        """
        if not task:
            logger.info("No task specified, running all tasks once")
            self.generate_leads()
            self.execute_social_outreach()
            self.check_lead_responses()
            self.schedule_content_for_week()
            self.generate_and_publish_content()
            return

        if task == "leads":
            self.generate_leads()
        elif task == "outreach":
            self.execute_social_outreach()
        elif task == "responses":
            self.check_lead_responses()
        elif task == "content":
            self.generate_and_publish_content()
        elif task == "schedule":
            self.schedule_content_for_week()
        else:
            logger.error(f"Unknown task: {task}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Sales Automation System")
    parser.add_argument("--schedule", action="store_true", help="Run the system with scheduled tasks")
    parser.add_argument("--task", type=str, help="Run a specific task once (leads, outreach, responses, content, schedule)")
    parser.add_argument("--dashboard", action="store_true", help="Start the dashboard web interface")
    parser.add_argument("--port", type=int, default=5000, help="Port for the dashboard (default: 5000)")

    args = parser.parse_args()

    # Create and initialize the system
    system = SalesAutomationSystem()

    # Start dashboard if requested
    if args.dashboard:
        system.start_dashboard(args.port)

    if args.schedule:
        # Run scheduled tasks
        try:
            system.run_scheduled_tasks()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            if args.dashboard:
                system.stop_dashboard()
    else:
        # Run once
        system.run_once(args.task)

        # Keep running if dashboard is active
        if args.dashboard:
            try:
                logger.info("Tasks completed. Dashboard is running. Press Ctrl+C to exit.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("System stopped by user")
                system.stop_dashboard()

if __name__ == "__main__":
    main()
