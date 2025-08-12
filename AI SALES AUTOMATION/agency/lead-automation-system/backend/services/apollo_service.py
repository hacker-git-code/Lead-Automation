import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ApolloService:
    """
    Service for interacting with Apollo.io API
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.environ.get("9VoVu59Q46dJoCCgYaseYQ")
        self.api_url = "https://api.apollo.io/v1"

    def search_leads(self, country, industry=None, revenue=None):
        """
        Search for leads on Apollo.io

        Args:
            country (str): Country code (US or IN)
            industry (str, optional): Industry type
            revenue (str, optional): Revenue range

        Returns:
            list: Leads that match the criteria
        """
        try:
            self.logger.info(f"Searching leads for country: {country}, industry: {industry}, revenue: {revenue}")

            # This is a simplified mock implementation
            # In a real application, this would make API calls to Apollo.io

            # Sample data for demonstration
            leads = self._get_sample_leads(country, industry, revenue)

            return leads

        except Exception as e:
            self.logger.error(f"Error searching leads: {str(e)}")
            raise

    def _get_sample_leads(self, country, industry, revenue):
        """Generate sample leads for demonstration"""
        if country == "US":
            return [
                {
                    "id": "US001",
                    "first_name": "John",
                    "last_name": "Smith",
                    "email": "john.smith@example.com",
                    "title": "CEO",
                    "company": "Digital Solutions Inc.",
                    "industry": industry or "SOFTWARE",
                    "estimated_revenue": revenue or "$1M-$10M",
                    "country": "US"
                },
                {
                    "id": "US002",
                    "first_name": "Jennifer",
                    "last_name": "Davis",
                    "email": "jennifer.davis@example.com",
                    "title": "Founder",
                    "company": "Growth Marketing Agency",
                    "industry": industry or "MARKETING",
                    "estimated_revenue": revenue or "$1M-$10M",
                    "country": "US"
                },
                {
                    "id": "US003",
                    "first_name": "Michael",
                    "last_name": "Johnson",
                    "email": "michael.j@example.com",
                    "title": "Director",
                    "company": "Tech Innovations LLC",
                    "industry": industry or "IT_SERVICES",
                    "estimated_revenue": revenue or "$10M-$50M",
                    "country": "US"
                }
            ]
        else:
            return [
                {
                    "id": "IN001",
                    "first_name": "Raj",
                    "last_name": "Patel",
                    "email": "raj.patel@example.com",
                    "title": "Founder & CEO",
                    "company": "CloudTech Solutions",
                    "industry": industry or "IT_SERVICES",
                    "estimated_revenue": revenue or "$0-$1M",
                    "country": "IN"
                },
                {
                    "id": "IN002",
                    "first_name": "Priya",
                    "last_name": "Sharma",
                    "email": "priya.sharma@example.com",
                    "title": "CTO",
                    "company": "DigiGrowth Technologies",
                    "industry": industry or "SOFTWARE",
                    "estimated_revenue": revenue or "$1M-$10M",
                    "country": "IN"
                },
                {
                    "id": "IN003",
                    "first_name": "Arjun",
                    "last_name": "Singh",
                    "email": "arjun.singh@example.com",
                    "title": "Managing Director",
                    "company": "Global Services Ltd",
                    "industry": industry or "CONSULTING",
                    "estimated_revenue": revenue or "$0-$1M",
                    "country": "IN"
                }
            ]
