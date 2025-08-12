import os
import requests
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ApolloService:
    """
    Service for interacting with Apollo.io API for lead generation
    """

    def __init__(self):
        self.api_key = os.environ.get('APOLLO_API_KEY')
        self.base_url = 'https://api.apollo.io/v1'
        self.logger = logging.getLogger(__name__)

        if not self.api_key:
            self.logger.warning("Apollo API key not set. Lead generation functionality will be limited.")

    def search_leads(self, country, industry=None, revenue=None, limit=100):
        """
        Search for leads on Apollo.io based on provided filters

        Args:
            country (str): Country to target (US or IN)
            industry (str, optional): Industry to target
            revenue (str, optional): Revenue range to target
            limit (int, optional): Maximum number of leads to return

        Returns:
            list: List of lead data
        """
        self.logger.info(f"Searching leads in {country}, industry: {industry}, revenue: {revenue}")

        # Build search query
        query = {
            "api_key": self.api_key,
            "page": 1,
            "per_page": limit,
            "q_organization_country": country,
        }

        # Add optional filters
        if industry:
            query["q_organization_industry_tag"] = industry

        if revenue:
            # Convert revenue to Apollo format (e.g., "1M-10M")
            revenue_ranges = {
                "0-1M": {"min": 0, "max": 1000000},
                "1M-10M": {"min": 1000000, "max": 10000000},
                "10M-50M": {"min": 10000000, "max": 50000000},
                "50M+": {"min": 50000000, "max": None}
            }

            if revenue in revenue_ranges:
                r_range = revenue_ranges[revenue]
                if r_range["min"] is not None:
                    query["q_organization_estimated_annual_revenue_min"] = r_range["min"]
                if r_range["max"] is not None:
                    query["q_organization_estimated_annual_revenue_max"] = r_range["max"]

        # Add filter for business owners
        query["q_person_title_levels"] = ["owner"]

        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/mixed_people/search",
                json=query
            )

            # Check for errors
            response.raise_for_status()

            # Parse response
            data = response.json()

            if "people" not in data:
                self.logger.error(f"Invalid response from Apollo API: {data}")
                return []

            # Extract and format lead data
            leads = []
            for person in data["people"]:
                # Extract organization
                org = person.get("organization", {})

                # Create lead object
                lead = {
                    "id": person.get("id"),
                    "first_name": person.get("first_name", ""),
                    "last_name": person.get("last_name", ""),
                    "email": person.get("email", ""),
                    "phone": person.get("phone_number", ""),
                    "linkedin_url": person.get("linkedin_url", ""),
                    "title": person.get("title", ""),
                    "company": org.get("name", ""),
                    "company_website": org.get("website_url", ""),
                    "industry": org.get("industry", ""),
                    "company_size": org.get("employee_count", ""),
                    "country": country,
                    "estimated_revenue": org.get("estimated_annual_revenue", ""),
                    "status": "New",
                    "source": "Apollo.io",
                    "notes": ""
                }
                leads.append(lead)

            self.logger.info(f"Found {len(leads)} leads in {country}")
            return leads

        except requests.RequestException as e:
            self.logger.error(f"Error connecting to Apollo API: {str(e)}")
            raise Exception(f"Failed to connect to Apollo API: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error processing Apollo results: {str(e)}")
            raise Exception(f"Failed to process Apollo results: {str(e)}")

    def enrich_lead(self, email=None, linkedin_url=None):
        """
        Enrich a lead with additional data from Apollo.io

        Args:
            email (str, optional): Email to enrich
            linkedin_url (str, optional): LinkedIn URL to enrich

        Returns:
            dict: Enriched lead data
        """
        if not email and not linkedin_url:
            raise ValueError("Either email or LinkedIn URL is required for enrichment")

        query = {
            "api_key": self.api_key,
        }

        if email:
            query["email"] = email
        elif linkedin_url:
            query["linkedin_url"] = linkedin_url

        try:
            response = requests.post(
                f"{self.base_url}/people/match",
                json=query
            )

            response.raise_for_status()
            data = response.json()

            if "person" not in data:
                self.logger.warning(f"No enrichment data found: {data}")
                return None

            # Extract and return enriched data
            person = data["person"]
            org = person.get("organization", {})

            enriched_data = {
                "id": person.get("id"),
                "first_name": person.get("first_name", ""),
                "last_name": person.get("last_name", ""),
                "email": person.get("email", ""),
                "phone": person.get("phone_number", ""),
                "linkedin_url": person.get("linkedin_url", ""),
                "title": person.get("title", ""),
                "company": org.get("name", ""),
                "company_website": org.get("website_url", ""),
                "industry": org.get("industry", ""),
                "company_size": org.get("employee_count", ""),
                "country": person.get("country", ""),
                "estimated_revenue": org.get("estimated_annual_revenue", ""),
            }

            return enriched_data

        except requests.RequestException as e:
            self.logger.error(f"Error enriching lead: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing enrichment data: {str(e)}")
            return None
