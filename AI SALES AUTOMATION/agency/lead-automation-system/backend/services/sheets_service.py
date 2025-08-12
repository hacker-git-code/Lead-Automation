import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SheetsService:
    """
    Service for interacting with Google Sheets to store and retrieve lead data
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # In a real implementation, this would use Google Sheets API
        # For demonstration, we'll use in-memory storage
        self.leads_store = []
        self.lead_counter = 0

    def store_leads(self, leads):
        """
        Store leads in the spreadsheet

        Args:
            leads (list): List of lead objects

        Returns:
            bool: Success status
        """
        try:
            self.logger.info(f"Storing {len(leads)} leads")

            # In a real implementation, this would add data to Google Sheets
            # For demonstration, we'll add to in-memory store
            for lead in leads:
                # Check if lead already exists
                existing_lead = next((l for l in self.leads_store if l.get('id') == lead.get('id')), None)

                if existing_lead:
                    # Update existing lead
                    existing_lead.update(lead)
                    existing_lead['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # Add new lead
                    lead['status'] = 'New'
                    lead['added_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    lead['updated_at'] = lead['added_at']
                    lead['notes'] = ''
                    self.leads_store.append(lead)

            return True

        except Exception as e:
            self.logger.error(f"Error storing leads: {str(e)}")
            return False

    def get_leads(self, lead_ids=None):
        """
        Get leads from the spreadsheet

        Args:
            lead_ids (list, optional): List of lead IDs to fetch. If None, returns all leads.

        Returns:
            list: Lead objects
        """
        try:
            self.logger.info(f"Fetching leads: {lead_ids if lead_ids else 'all'}")

            if not lead_ids:
                return self.leads_store

            # Filter leads by ID
            return [lead for lead in self.leads_store if lead.get('id') in lead_ids]

        except Exception as e:
            self.logger.error(f"Error getting leads: {str(e)}")
            return []

    def get_lead(self, lead_id):
        """
        Get a single lead by ID

        Args:
            lead_id (str): Lead ID

        Returns:
            dict: Lead object or None if not found
        """
        try:
            self.logger.info(f"Fetching lead: {lead_id}")

            # Find lead by ID
            lead = next((l for l in self.leads_store if l.get('id') == lead_id), None)

            return lead

        except Exception as e:
            self.logger.error(f"Error getting lead: {str(e)}")
            return None

    def update_lead(self, lead_id, status, notes=None):
        """
        Update lead status and notes

        Args:
            lead_id (str): Lead ID
            status (str): New status
            notes (str, optional): Additional notes

        Returns:
            bool: Success status
        """
        try:
            self.logger.info(f"Updating lead {lead_id}: status={status}, notes={notes}")

            # Find lead by ID
            lead = next((l for l in self.leads_store if l.get('id') == lead_id), None)

            if not lead:
                self.logger.warning(f"Lead not found: {lead_id}")
                return False

            # Update lead
            lead['status'] = status
            lead['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if notes:
                if lead.get('notes'):
                    lead['notes'] += f"\n{notes}"
                else:
                    lead['notes'] = notes

            return True

        except Exception as e:
            self.logger.error(f"Error updating lead: {str(e)}")
            return False

    def get_analytics_data(self):
        """
        Get analytics data from the stored leads

        Returns:
            dict: Analytics data
        """
        try:
            self.logger.info("Generating analytics data")

            # Default structure
            analytics = {
                "us_leads": {
                    "total": 0,
                    "by_status": {}
                },
                "india_leads": {
                    "total": 0,
                    "by_status": {}
                },
                "recent_activities": []
            }

            # Process leads
            for lead in self.leads_store:
                # Determine country category
                if lead.get('country') == 'US':
                    analytics["us_leads"]["total"] += 1

                    # Count by status
                    status = lead.get('status', 'New')
                    analytics["us_leads"]["by_status"][status] = analytics["us_leads"]["by_status"].get(status, 0) + 1
                else:
                    analytics["india_leads"]["total"] += 1

                    # Count by status
                    status = lead.get('status', 'New')
                    analytics["india_leads"]["by_status"][status] = analytics["india_leads"]["by_status"].get(status, 0) + 1

                # Add to recent activities if updated recently
                if lead.get('updated_at'):
                    activity = {
                        "id": lead.get('id'),
                        "name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}",
                        "company": lead.get('company', 'N/A'),
                        "status": lead.get('status', 'New'),
                        "country": lead.get('country', 'N/A'),
                        "last_contact": lead.get('updated_at')
                    }
                    analytics["recent_activities"].append(activity)

            # Sort recent activities by date (newest first)
            analytics["recent_activities"].sort(key=lambda x: x.get('last_contact', ''), reverse=True)

            # Limit to 10 most recent
            analytics["recent_activities"] = analytics["recent_activities"][:10]

            return analytics

        except Exception as e:
            self.logger.error(f"Error generating analytics: {str(e)}")
            return {
                "us_leads": {"total": 0, "by_status": {}},
                "india_leads": {"total": 0, "by_status": {}},
                "recent_activities": []
            }
