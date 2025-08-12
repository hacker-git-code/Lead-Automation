"""
Lead Generation Module - Uses Apollo.io API to find high-quality leads
matching our target criteria, and extracts active social media profiles.
"""

import os
import time
import json
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from config import ApolloConfig
from modules.google_sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)

class ApolloLeadFinder:
    """
    Uses Apollo.io API to find leads matching specified criteria and extracts
    social media profiles (X/Twitter and Instagram).
    """

    def __init__(self, api_key: str = None):
        """Initialize with Apollo.io API key."""
        self.api_key = api_key or ApolloConfig.API_KEY
        self.base_url = ApolloConfig.BASE_URL
        if not self.api_key:
            raise ValueError("Apollo.io API key is required")

        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

    def search_people(self,
                      title: str,
                      industry: str,
                      locations: List[str] = None,
                      min_revenue: int = None,
                      page: int = 1,
                      per_page: int = 100) -> Dict[str, Any]:
        """
        Search for people matching the given criteria.

        Args:
            title: Job title to search for (e.g., "Digital Agency Owner")
            industry: Industry sector (e.g., "Marketing and Advertising")
            locations: List of locations to search in
            min_revenue: Minimum annual revenue of the company
            page: Page number for pagination
            per_page: Number of results per page

        Returns:
            Dict containing search results
        """
        endpoint = f"{self.base_url}/people/search"

        # Build query
        query = {
            "api_key": self.api_key,
            "page": page,
            "per_page": per_page,
            "q_organization_domains": [],
            "person_titles": [title],
            "organization_industry_tagged_only": True,
            "organization_industries": [industry]
        }

        if locations:
            query["person_locations"] = locations

        if min_revenue:
            query["organization_estimated_annual_revenue_min"] = min_revenue

        try:
            response = requests.post(endpoint, headers=self.headers, json=query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Apollo.io: {str(e)}")
            return {"error": str(e)}

    def extract_social_profiles(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract people with social media profiles from Apollo response.

        Args:
            response_data: Response data from Apollo.io API

        Returns:
            List of leads with their details and social media profiles
        """
        leads = []

        if "people" not in response_data:
            logger.warning("No people found in Apollo response")
            return leads

        for person in response_data["people"]:
            # Extract basic info
            lead = {
                "name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                "first_name": person.get('first_name', ''),
                "email": person.get('email', ''),
                "phone": person.get('phone', ''),
                "title": person.get('title', ''),
                "location": person.get('city', '') + (f", {person.get('state', '')}" if person.get('state') else ''),
                "country": person.get('country', ''),
                "linkedin_url": person.get('linkedin_url', ''),
                "x_username": None,
                "instagram_username": None,
                "company": person.get('organization_name', ''),
                "industry": person.get('organization_industry', ''),
                "company_size": person.get('organization_size', ''),
                "company_website": person.get('organization_website', ''),
                "source": "Apollo.io",
                "found_date": datetime.now().strftime("%Y-%m-%d")
            }

            # Extract Twitter/X username
            if "twitter_url" in person and person["twitter_url"]:
                twitter_url = person["twitter_url"]
                try:
                    # Extract username from URL
                    x_username = twitter_url.split("/")[-1]
                    if x_username:
                        lead["x_username"] = x_username
                except:
                    pass

            # Check if lead has social media
            if lead["x_username"] or lead.get("instagram_username"):
                leads.append(lead)

        return leads

    def find_and_extract_leads(self, target_params: Dict[str, Any], max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Search for leads with the given parameters and extract their details.

        Args:
            target_params: Dictionary of search parameters
            max_pages: Maximum number of pages to retrieve

        Returns:
            List of leads with their details
        """
        all_leads = []

        # Extract parameters
        title = target_params.get("title")
        industry = target_params.get("industry")
        locations = target_params.get("locations")
        min_revenue = target_params.get("min_revenue")

        if not title or not industry:
            logger.error("Title and industry are required parameters")
            return all_leads

        for page in range(1, max_pages + 1):
            logger.info(f"Searching page {page} for {title} in {industry}")
            response_data = self.search_people(
                title=title,
                industry=industry,
                locations=locations,
                min_revenue=min_revenue,
                page=page
            )

            if "error" in response_data:
                logger.error(f"Error in Apollo search: {response_data['error']}")
                break

            leads = self.extract_social_profiles(response_data)
            all_leads.extend(leads)

            # Check if we reached the end of results
            if len(leads) == 0 or len(all_leads) >= response_data.get("pagination", {}).get("total", 0):
                break

            # Sleep to avoid rate limits
            time.sleep(1)

        return all_leads

    def save_leads_to_csv(self, leads: List[Dict[str, Any]], output_file: str) -> str:
        """
        Save leads to a CSV file.

        Args:
            leads: List of lead dictionaries
            output_file: Path to the output CSV file

        Returns:
            Path to the saved file
        """
        if not leads:
            logger.warning("No leads to save")
            return None

        try:
            df = pd.DataFrame(leads)
            df.to_csv(output_file, index=False)
            logger.info(f"Saved {len(leads)} leads to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving leads to CSV: {str(e)}")
            return None

    def find_leads_for_all_targets(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find leads for all target parameters defined in ApolloConfig.

        Returns:
            Dictionary mapping target types to lists of leads
        """
        all_target_leads = {}

        for target in ApolloConfig.TARGETS:
            target_type = target.get("title").replace(" ", "_").lower()
            logger.info(f"Finding leads for target: {target.get('title')}")

            leads = self.find_and_extract_leads(target)
            all_target_leads[target_type] = leads

            # Save to CSV
            output_dir = "data/leads"
            os.makedirs(output_dir, exist_ok=True)
            output_file = f"{output_dir}/{target_type}_{datetime.now().strftime('%Y%m%d')}.csv"
            self.save_leads_to_csv(leads, output_file)

            # Sleep between targets to avoid rate limits
            time.sleep(5)

        return all_target_leads

class LeadManager:
    """
    Manages lead data, integrating with Google Sheets and filtering for social presence.
    """

    def __init__(self, sheets_manager: Optional[GoogleSheetsManager] = None):
        """Initialize with optional GoogleSheetsManager."""
        self.apollo = ApolloLeadFinder()
        self.sheets_manager = sheets_manager

    def find_and_store_leads(self):
        """Find leads and store them in Google Sheets."""
        # Create output directory
        os.makedirs("data/leads", exist_ok=True)

        # Find leads from Apollo
        all_target_leads = self.apollo.find_leads_for_all_targets()

        # Flatten leads
        all_leads = []
        for target_type, leads in all_target_leads.items():
            for lead in leads:
                lead["target_type"] = target_type.replace("_", " ")
                all_leads.append(lead)

        # Store in Google Sheets if available
        if self.sheets_manager:
            self.sheets_manager.append_leads(all_leads)

        return all_leads

    def filter_leads_with_social(self, platform: str = "both") -> List[Dict[str, Any]]:
        """
        Filter leads that have social media presence.

        Args:
            platform: 'x', 'instagram', or 'both'

        Returns:
            Filtered list of leads
        """
        if self.sheets_manager:
            leads = self.sheets_manager.get_leads()
        else:
            # Read from the most recent CSV files
            leads = []
            lead_files = [f for f in os.listdir("data/leads") if f.endswith(".csv")]

            for file in lead_files:
                try:
                    df = pd.read_csv(f"data/leads/{file}")
                    leads.extend(df.to_dict("records"))
                except Exception as e:
                    logger.error(f"Error reading {file}: {str(e)}")

        # Filter based on platform
        if platform.lower() == "x":
            return [lead for lead in leads if lead.get("x_username")]
        elif platform.lower() == "instagram":
            return [lead for lead in leads if lead.get("instagram_username")]
        else:  # both
            return [lead for lead in leads if lead.get("x_username") or lead.get("instagram_username")]

# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/lead_generation.log"),
            logging.StreamHandler()
        ]
    )

    lead_manager = LeadManager()
    leads = lead_manager.find_and_store_leads()
    print(f"Found {len(leads)} leads with social media profiles")
