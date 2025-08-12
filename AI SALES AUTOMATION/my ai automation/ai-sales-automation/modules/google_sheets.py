"""
Google Sheets Manager - Handles interactions with Google Sheets for lead storage and tracking.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

from config import GoogleSheetsConfig

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """
    Manages interactions with Google Sheets for lead storage and tracking.
    """

    def __init__(self, credentials_file: str = None, sheet_id: str = None):
        """
        Initialize the Google Sheets manager.

        Args:
            credentials_file: Path to the Google Sheets credentials JSON file
            sheet_id: Google Sheet ID
        """
        self.credentials_file = credentials_file or GoogleSheetsConfig.CREDENTIALS_FILE
        self.sheet_id = sheet_id or GoogleSheetsConfig.SHEET_ID

        if not self.credentials_file or not os.path.exists(self.credentials_file):
            raise ValueError(f"Google Sheets credentials file not found: {self.credentials_file}")

        if not self.sheet_id:
            raise ValueError("Google Sheet ID is required")

        self.scope = ['https://spreadsheets.google.com/feeds',
                       'https://www.googleapis.com/auth/drive']

        self.client = None
        self.sheet = None

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, self.scope)
            self.client = gspread.authorize(credentials)
            self.sheet = self.client.open_by_key(self.sheet_id)
            logger.info("Successfully authenticated with Google Sheets")
        except Exception as e:
            logger.error(f"Error authenticating with Google Sheets: {str(e)}")
            raise

    def _get_worksheet(self, sheet_name: str, create_if_missing: bool = True) -> Optional[gspread.Worksheet]:
        """
        Get a worksheet by name, creating it if it doesn't exist.

        Args:
            sheet_name: Name of the worksheet
            create_if_missing: Whether to create the worksheet if it doesn't exist

        Returns:
            gspread.Worksheet or None if worksheet doesn't exist and create_if_missing is False
        """
        try:
            return self.sheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            if create_if_missing:
                logger.info(f"Creating new worksheet: {sheet_name}")
                return self.sheet.add_worksheet(title=sheet_name, rows=1000, cols=26)
            else:
                logger.warning(f"Worksheet not found: {sheet_name}")
                return None

    def _ensure_headers(self, worksheet: gspread.Worksheet, headers: List[str]):
        """
        Ensure the worksheet has the required headers.

        Args:
            worksheet: Worksheet to check
            headers: List of header names
        """
        # Get current headers
        try:
            current_headers = worksheet.row_values(1)

            # If no headers, add them
            if not current_headers:
                worksheet.append_row(headers)
                logger.info(f"Added headers to {worksheet.title}")
            # If headers don't match, update them
            elif set(current_headers) != set(headers):
                # Find headers that need to be added
                new_headers = [h for h in headers if h not in current_headers]

                if new_headers:
                    # Get all current data
                    all_data = worksheet.get_all_records()

                    # Update headers
                    worksheet.clear()
                    worksheet.append_row(headers)

                    # Add back the data with new columns as empty
                    for row in all_data:
                        row_data = [row.get(h, "") for h in headers]
                        worksheet.append_row(row_data)

                    logger.info(f"Updated headers in {worksheet.title}")
        except Exception as e:
            logger.error(f"Error ensuring headers: {str(e)}")
            # Fallback: clear and re-add headers
            worksheet.clear()
            worksheet.append_row(headers)

    def append_leads(self, leads: List[Dict[str, Any]]) -> bool:
        """
        Append leads to the leads worksheet.

        Args:
            leads: List of lead dictionaries

        Returns:
            True if successful, False otherwise
        """
        if not leads:
            logger.warning("No leads to append")
            return False

        try:
            # Get the leads worksheet
            leads_worksheet = self._get_worksheet(GoogleSheetsConfig.LEADS_SHEET)

            # Ensure headers
            self._ensure_headers(leads_worksheet, GoogleSheetsConfig.LEADS_COLUMNS)

            # Prepare data for appending
            rows_to_append = []
            for lead in leads:
                # Prepare row data in the correct column order
                row = [lead.get(col.lower(), "") for col in GoogleSheetsConfig.LEADS_COLUMNS]
                rows_to_append.append(row)

            # Append the rows
            leads_worksheet.append_rows(rows_to_append)
            logger.info(f"Added {len(leads)} leads to Google Sheets")

            return True
        except Exception as e:
            logger.error(f"Error appending leads to Google Sheets: {str(e)}")
            return False

    def get_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get leads from the leads worksheet with optional filtering.

        Args:
            filters: Dictionary of column-value pairs to filter by

        Returns:
            List of lead dictionaries
        """
        try:
            # Get the leads worksheet
            leads_worksheet = self._get_worksheet(GoogleSheetsConfig.LEADS_SHEET, create_if_missing=False)

            if not leads_worksheet:
                logger.warning("Leads worksheet not found")
                return []

            # Get all leads
            leads = leads_worksheet.get_all_records()

            # Apply filters if provided
            if filters:
                filtered_leads = []
                for lead in leads:
                    match = True
                    for key, value in filters.items():
                        if lead.get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_leads.append(lead)
                return filtered_leads

            return leads
        except Exception as e:
            logger.error(f"Error getting leads from Google Sheets: {str(e)}")
            return []

    def update_lead_status(self, lead_id: str, status: str) -> bool:
        """
        Update the status of a lead.

        Args:
            lead_id: ID of the lead (typically the row number)
            status: New status value

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the leads worksheet
            leads_worksheet = self._get_worksheet(GoogleSheetsConfig.LEADS_SHEET, create_if_missing=False)

            if not leads_worksheet:
                logger.warning("Leads worksheet not found")
                return False

            # Find the status column
            headers = leads_worksheet.row_values(1)
            status_col = headers.index("Status") + 1  # 1-indexed
            last_contact_col = headers.index("Last_Contact_Date") + 1  # 1-indexed

            # Find the lead row
            lead_row = int(lead_id)

            # Update the status
            leads_worksheet.update_cell(lead_row, status_col, status)
            leads_worksheet.update_cell(lead_row, last_contact_col, datetime.now().strftime("%Y-%m-%d"))

            logger.info(f"Updated lead {lead_id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating lead status: {str(e)}")
            return False

    def record_outreach(self, lead_id: str, platform: str, action: str, message: str) -> bool:
        """
        Record an outreach action.

        Args:
            lead_id: ID of the lead
            platform: Platform used (X, Instagram)
            action: Action taken (follow, dm, reply)
            message: Content of the message

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the outreach worksheet
            outreach_worksheet = self._get_worksheet(GoogleSheetsConfig.OUTREACH_SHEET)

            # Ensure headers
            self._ensure_headers(outreach_worksheet, GoogleSheetsConfig.OUTREACH_COLUMNS)

            # Prepare data
            outreach = {
                "Lead_ID": lead_id,
                "Platform": platform,
                "Action": action,
                "Message": message,
                "Date_Sent": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Response": "",
                "Follow_Up_Count": 0
            }

            # Append the outreach record
            row = [outreach.get(col, "") for col in GoogleSheetsConfig.OUTREACH_COLUMNS]
            outreach_worksheet.append_row(row)

            logger.info(f"Recorded {action} outreach to lead {lead_id} on {platform}")
            return True
        except Exception as e:
            logger.error(f"Error recording outreach: {str(e)}")
            return False

    def get_leads_for_follow_up(self, days_since_last_contact: int = 3, max_follow_ups: int = 3) -> List[Dict[str, Any]]:
        """
        Get leads that need follow-up.

        Args:
            days_since_last_contact: Number of days since last contact
            max_follow_ups: Maximum number of follow-ups

        Returns:
            List of leads needing follow-up
        """
        try:
            # Get all outreach records
            outreach_worksheet = self._get_worksheet(GoogleSheetsConfig.OUTREACH_SHEET, create_if_missing=False)

            if not outreach_worksheet:
                logger.warning("Outreach worksheet not found")
                return []

            outreach_records = outreach_worksheet.get_all_records()

            # Group by lead_id and find those needing follow-up
            lead_outreach = {}
            for record in outreach_records:
                lead_id = record.get("Lead_ID")
                follow_up_count = record.get("Follow_Up_Count", 0)
                date_sent = record.get("Date_Sent")
                response = record.get("Response", "")

                if not lead_id or not date_sent:
                    continue

                # Parse date
                try:
                    date_sent = datetime.strptime(date_sent, "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        date_sent = datetime.strptime(date_sent, "%Y-%m-%d")
                    except:
                        continue

                # Calculate days since
                days_since = (datetime.now() - date_sent).days

                # Update lead outreach data
                if lead_id not in lead_outreach or date_sent > lead_outreach[lead_id]["date_sent"]:
                    lead_outreach[lead_id] = {
                        "date_sent": date_sent,
                        "days_since": days_since,
                        "follow_up_count": follow_up_count,
                        "has_response": bool(response.strip())
                    }

            # Get the leads worksheet
            leads_worksheet = self._get_worksheet(GoogleSheetsConfig.LEADS_SHEET, create_if_missing=False)

            if not leads_worksheet:
                logger.warning("Leads worksheet not found")
                return []

            all_leads = leads_worksheet.get_all_records()

            # Filter leads for follow-up
            leads_for_follow_up = []

            for i, lead in enumerate(all_leads, start=2):  # Start from 2 to account for headers
                lead_id = str(i)

                # Skip leads without social profiles
                if not lead.get("X_Username") and not lead.get("Instagram_Username"):
                    continue

                # Skip leads that have been fully followed up or have responded
                outreach_data = lead_outreach.get(lead_id, {})
                if (outreach_data.get("has_response", False) or
                    outreach_data.get("follow_up_count", 0) >= max_follow_ups):
                    continue

                # Check if it's time for follow-up
                if (not outreach_data or  # No outreach yet
                    outreach_data.get("days_since", 0) >= days_since_last_contact):

                    # Add lead ID to the lead dictionary
                    lead["id"] = lead_id
                    lead["follow_up_count"] = outreach_data.get("follow_up_count", 0)
                    leads_for_follow_up.append(lead)

            return leads_for_follow_up
        except Exception as e:
            logger.error(f"Error getting leads for follow-up: {str(e)}")
            return []

    def record_deal(self, lead_id: str, package: str, price: float, currency: str, payment_method: str) -> bool:
        """
        Record a deal.

        Args:
            lead_id: ID of the lead
            package: Package name
            price: Price amount
            currency: Currency code (USD, INR)
            payment_method: Payment method

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the deals worksheet
            deals_worksheet = self._get_worksheet(GoogleSheetsConfig.DEALS_SHEET)

            # Ensure headers
            self._ensure_headers(deals_worksheet, GoogleSheetsConfig.DEALS_COLUMNS)

            # Prepare data
            deal = {
                "Lead_ID": lead_id,
                "Package": package,
                "Price": price,
                "Currency": currency,
                "Payment_Method": payment_method,
                "Status": "Pending",
                "Close_Date": datetime.now().strftime("%Y-%m-%d")
            }

            # Append the deal record
            row = [deal.get(col, "") for col in GoogleSheetsConfig.DEALS_COLUMNS]
            deals_worksheet.append_row(row)

            # Update lead status
            self.update_lead_status(lead_id, "Deal Sent")

            logger.info(f"Recorded deal for lead {lead_id}: {package} for {price} {currency}")
            return True
        except Exception as e:
            logger.error(f"Error recording deal: {str(e)}")
            return False

    def update_deal_status(self, lead_id: str, status: str) -> bool:
        """
        Update the status of a deal.

        Args:
            lead_id: ID of the lead
            status: New status value

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the deals worksheet
            deals_worksheet = self._get_worksheet(GoogleSheetsConfig.DEALS_SHEET, create_if_missing=False)

            if not deals_worksheet:
                logger.warning("Deals worksheet not found")
                return False

            # Find all deals for this lead
            deals = deals_worksheet.get_all_records()

            found = False
            for i, deal in enumerate(deals, start=2):  # Start from 2 to account for headers
                if str(deal.get("Lead_ID")) == str(lead_id):
                    # Find the status column
                    headers = deals_worksheet.row_values(1)
                    status_col = headers.index("Status") + 1  # 1-indexed

                    # Update the status
                    deals_worksheet.update_cell(i, status_col, status)
                    found = True

                    # If deal is completed, update lead status
                    if status == "Completed":
                        self.update_lead_status(lead_id, "Customer")

            if found:
                logger.info(f"Updated deal status for lead {lead_id} to {status}")
                return True
            else:
                logger.warning(f"No deals found for lead {lead_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating deal status: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/google_sheets.log"),
            logging.StreamHandler()
        ]
    )

    # Create dummy data directory for credentials
    os.makedirs("credentials", exist_ok=True)

    # Example dummy credentials file
    if not os.path.exists("credentials/google_sheets_credentials.json"):
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

        with open("credentials/google_sheets_credentials.json", "w") as f:
            json.dump(dummy_credentials, f)

        print("Created dummy credentials file. Replace with real credentials before using.")
