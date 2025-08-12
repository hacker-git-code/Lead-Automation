import os
import json
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Load environment variables
load_dotenv()

class SheetsService:
    """
    Service for interacting with Google Sheets API for lead storage and management
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.spreadsheet_id = os.environ.get('LEAD_SHEET_ID')
        self.credentials_file = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        self.service = None

        # Initialize Google Sheets API
        try:
            self._init_service()
        except Exception as e:
            self.logger.warning(f"Failed to initialize Google Sheets service: {str(e)}")

    def _init_service(self):
        """Initialize Google Sheets API service"""
        if not self.credentials_file or not self.spreadsheet_id:
            self.logger.warning("Google Sheets credentials or spreadsheet ID not set.")
            return

        try:
            # Scopes needed for Google Sheets
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES)

            # Build service
            self.service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Google Sheets API initialized successfully")

            # Ensure sheets exist
            self._ensure_sheets_exist()

        except Exception as e:
            self.logger.error(f"Error initializing Google Sheets service: {str(e)}")
            raise Exception(f"Failed to initialize Google Sheets: {str(e)}")

    def _ensure_sheets_exist(self):
        """Ensure required sheets exist in the spreadsheet"""
        required_sheets = [
            "US_Leads",
            "India_Leads",
            "Campaigns",
            "Analytics"
        ]

        try:
            # Get existing sheets
            result = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()

            existing_sheets = [sheet['properties']['title'] for sheet in result.get('sheets', [])]

            # Add missing sheets
            for sheet_name in required_sheets:
                if sheet_name not in existing_sheets:
                    self.logger.info(f"Creating sheet: {sheet_name}")

                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body={
                            "requests": [
                                {
                                    "addSheet": {
                                        "properties": {
                                            "title": sheet_name
                                        }
                                    }
                                }
                            ]
                        }
                    ).execute()

                    # Initialize headers
                    headers = [
                        "ID", "First Name", "Last Name", "Email", "Phone",
                        "LinkedIn URL", "Title", "Company", "Website",
                        "Industry", "Company Size", "Country",
                        "Estimated Revenue", "Status", "Source",
                        "Date Added", "Last Contact", "Notes"
                    ]

                    # Set headers
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{sheet_name}!A1:R1",
                        valueInputOption="RAW",
                        body={
                            "values": [headers]
                        }
                    ).execute()

        except Exception as e:
            self.logger.error(f"Error ensuring sheets exist: {str(e)}")

    def store_leads(self, leads):
        """
        Store leads in Google Sheets

        Args:
            leads (list): List of lead objects to store

        Returns:
            bool: Success status
        """
        if not self.service:
            self.logger.warning("Google Sheets service not initialized")
            return False

        if not leads:
            self.logger.warning("No leads to store")
            return False

        # Group leads by country
        us_leads = []
        india_leads = []

        for lead in leads:
            # Prepare row data
            row_data = [
                lead.get("id", ""),
                lead.get("first_name", ""),
                lead.get("last_name", ""),
                lead.get("email", ""),
                lead.get("phone", ""),
                lead.get("linkedin_url", ""),
                lead.get("title", ""),
                lead.get("company", ""),
                lead.get("company_website", ""),
                lead.get("industry", ""),
                lead.get("company_size", ""),
                lead.get("country", ""),
                lead.get("estimated_revenue", ""),
                lead.get("status", "New"),
                lead.get("source", "Apollo.io"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "",  # Last Contact
                lead.get("notes", "")
            ]

            # Add to appropriate country list
            if lead.get("country") == "US":
                us_leads.append(row_data)
            elif lead.get("country") == "IN":
                india_leads.append(row_data)

        try:
            # Store US leads
            if us_leads:
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range="US_Leads!A2",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={
                        "values": us_leads
                    }
                ).execute()
                self.logger.info(f"Stored {len(us_leads)} US leads in Google Sheets")

            # Store India leads
            if india_leads:
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range="India_Leads!A2",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={
                        "values": india_leads
                    }
                ).execute()
                self.logger.info(f"Stored {len(india_leads)} India leads in Google Sheets")

            return True

        except Exception as e:
            self.logger.error(f"Error storing leads in Google Sheets: {str(e)}")
            return False

    def get_leads(self, lead_ids=None, country=None, status=None):
        """
        Get leads from Google Sheets

        Args:
            lead_ids (list, optional): List of lead IDs to get
            country (str, optional): Country to filter (US or IN)
            status (str, optional): Status to filter

        Returns:
            list: List of lead objects
        """
        if not self.service:
            self.logger.warning("Google Sheets service not initialized")
            return []

        sheets_to_check = []

        if country == "US":
            sheets_to_check = ["US_Leads"]
        elif country == "IN":
            sheets_to_check = ["India_Leads"]
        else:
            # Check both sheets
            sheets_to_check = ["US_Leads", "India_Leads"]

        all_leads = []
        headers = [
            "id", "first_name", "last_name", "email", "phone",
            "linkedin_url", "title", "company", "company_website",
            "industry", "company_size", "country",
            "estimated_revenue", "status", "source",
            "date_added", "last_contact", "notes"
        ]

        try:
            for sheet_name in sheets_to_check:
                # Get all data from sheet
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1:R",
                ).execute()

                rows = result.get('values', [])
                if not rows or len(rows) <= 1:
                    continue

                # Skip header row and convert to list of dicts
                for row in rows[1:]:
                    # Pad row if needed
                    padded_row = row + [""] * (len(headers) - len(row))

                    # Create lead dict
                    lead = dict(zip(headers, padded_row))

                    # Apply filters
                    if lead_ids and lead["id"] not in lead_ids:
                        continue

                    if status and lead["status"] != status:
                        continue

                    # Infer country from sheet name if not set
                    if not lead["country"]:
                        lead["country"] = "US" if sheet_name == "US_Leads" else "IN"

                    all_leads.append(lead)

            return all_leads

        except Exception as e:
            self.logger.error(f"Error getting leads from Google Sheets: {str(e)}")
            return []

    def get_lead(self, lead_id):
        """
        Get a single lead by ID

        Args:
            lead_id (str): Lead ID to get

        Returns:
            dict: Lead object
        """
        leads = self.get_leads(lead_ids=[lead_id])
        return leads[0] if leads else None

    def update_lead(self, lead_id, status, notes=""):
        """
        Update lead status and notes

        Args:
            lead_id (str): Lead ID to update
            status (str): New status
            notes (str, optional): Notes to append

        Returns:
            bool: Success status
        """
        if not self.service or not lead_id:
            return False

        sheets_to_check = ["US_Leads", "India_Leads"]

        try:
            for sheet_name in sheets_to_check:
                # Get all data from sheet
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1:R",
                ).execute()

                rows = result.get('values', [])
                if not rows or len(rows) <= 1:
                    continue

                # Find lead
                for i, row in enumerate(rows[1:], start=2):  # start=2 to skip header and account for 1-indexing
                    if row[0] == lead_id:  # ID is in column A (index 0)
                        # Update status (column N, index 13)
                        self.service.spreadsheets().values().update(
                            spreadsheetId=self.spreadsheet_id,
                            range=f"{sheet_name}!N{i}",
                            valueInputOption="RAW",
                            body={
                                "values": [[status]]
                            }
                        ).execute()

                        # Get current notes
                        current_notes = row[17] if len(row) > 17 else ""

                        # Append new notes
                        if notes:
                            updated_notes = f"{current_notes}\n{datetime.now().strftime('%Y-%m-%d %H:%M')} - {notes}" if current_notes else f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {notes}"

                            # Update notes (column R, index 17)
                            self.service.spreadsheets().values().update(
                                spreadsheetId=self.spreadsheet_id,
                                range=f"{sheet_name}!R{i}",
                                valueInputOption="RAW",
                                body={
                                    "values": [[updated_notes]]
                                }
                            ).execute()

                        # Update last contact date (column Q, index 16)
                        self.service.spreadsheets().values().update(
                            spreadsheetId=self.spreadsheet_id,
                            range=f"{sheet_name}!Q{i}",
                            valueInputOption="RAW",
                            body={
                                "values": [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]
                            }
                        ).execute()

                        self.logger.info(f"Updated lead {lead_id} status to {status}")
                        return True

            self.logger.warning(f"Lead {lead_id} not found in sheets")
            return False

        except Exception as e:
            self.logger.error(f"Error updating lead in Google Sheets: {str(e)}")
            return False

    def get_analytics_data(self):
        """
        Get analytics data from Google Sheets

        Returns:
            dict: Analytics data
        """
        if not self.service:
            return {}

        analytics = {
            "us_leads": {
                "total": 0,
                "by_status": {}
            },
            "india_leads": {
                "total": 0,
                "by_status": {}
            },
            "overall_conversion_rate": 0,
            "recent_activities": []
        }

        try:
            # Get US leads statistics
            us_leads = self.get_leads(country="US")
            analytics["us_leads"]["total"] = len(us_leads)

            # Group by status
            for lead in us_leads:
                status = lead.get("status", "New")
                if status not in analytics["us_leads"]["by_status"]:
                    analytics["us_leads"]["by_status"][status] = 0
                analytics["us_leads"]["by_status"][status] += 1

            # Get India leads statistics
            india_leads = self.get_leads(country="IN")
            analytics["india_leads"]["total"] = len(india_leads)

            # Group by status
            for lead in india_leads:
                status = lead.get("status", "New")
                if status not in analytics["india_leads"]["by_status"]:
                    analytics["india_leads"]["by_status"][status] = 0
                analytics["india_leads"]["by_status"][status] += 1

            # Calculate overall conversion rate (if any payment made)
            total_leads = analytics["us_leads"]["total"] + analytics["india_leads"]["total"]
            paid_us = analytics["us_leads"]["by_status"].get("Payment Received", 0)
            paid_india = analytics["india_leads"]["by_status"].get("Payment Received", 0)
            total_paid = paid_us + paid_india

            if total_leads > 0:
                analytics["overall_conversion_rate"] = (total_paid / total_leads) * 100

            # Get recent activities (last 10 leads with updated status)
            all_leads = us_leads + india_leads
            sorted_leads = sorted(
                all_leads,
                key=lambda x: x.get("last_contact", ""),
                reverse=True
            )

            for lead in sorted_leads[:10]:
                analytics["recent_activities"].append({
                    "id": lead.get("id", ""),
                    "name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}",
                    "company": lead.get("company", ""),
                    "status": lead.get("status", ""),
                    "last_contact": lead.get("last_contact", ""),
                    "country": lead.get("country", "")
                })

            return analytics

        except Exception as e:
            self.logger.error(f"Error getting analytics data: {str(e)}")
            return analytics
