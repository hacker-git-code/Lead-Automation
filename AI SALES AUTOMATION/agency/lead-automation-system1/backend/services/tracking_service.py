import os
import logging
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Local imports
from services.sheets_service import SheetsService

# Load environment variables
load_dotenv()

class TrackingService:
    """
    Service for tracking and optimizing the sales funnel
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sheets_service = SheetsService()

    def get_analytics(self):
        """
        Get sales funnel analytics data

        Returns:
            dict: Analytics data
        """
        try:
            # Get data from sheets service
            analytics_data = self.sheets_service.get_analytics_data()

            # Calculate additional metrics
            metrics = self._calculate_metrics(analytics_data)

            # Generate optimization suggestions
            suggestions = self._generate_suggestions(analytics_data, metrics)

            # Combine all data
            result = {
                "data": analytics_data,
                "metrics": metrics,
                "suggestions": suggestions,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return result

        except Exception as e:
            self.logger.error(f"Error getting analytics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def _calculate_metrics(self, analytics_data):
        """
        Calculate advanced metrics from analytics data

        Args:
            analytics_data (dict): Base analytics data

        Returns:
            dict: Calculated metrics
        """
        metrics = {
            "overall": {},
            "by_country": {
                "US": {},
                "India": {}
            }
        }

        try:
            # Extract data from analytics
            us_leads = analytics_data.get("us_leads", {})
            india_leads = analytics_data.get("india_leads", {})

            us_total = us_leads.get("total", 0)
            india_total = india_leads.get("total", 0)
            total_leads = us_total + india_total

            # Skip calculations if no leads
            if total_leads == 0:
                return metrics

            # Get status counts
            us_status = us_leads.get("by_status", {})
            india_status = india_leads.get("by_status", {})

            # US metrics
            if us_total > 0:
                metrics["by_country"]["US"]["reply_rate"] = self._calculate_percentage(
                    us_status.get("Replied", 0) + us_status.get("Call Requested", 0),
                    us_total
                )

                metrics["by_country"]["US"]["call_rate"] = self._calculate_percentage(
                    us_status.get("Call Requested", 0) + us_status.get("Call Scheduled", 0),
                    us_total
                )

                metrics["by_country"]["US"]["payment_rate"] = self._calculate_percentage(
                    us_status.get("Payment Link Sent", 0) + us_status.get("Payment Received", 0),
                    us_total
                )

                metrics["by_country"]["US"]["conversion_rate"] = self._calculate_percentage(
                    us_status.get("Payment Received", 0) + us_status.get("Onboarding", 0),
                    us_total
                )

            # India metrics
            if india_total > 0:
                metrics["by_country"]["India"]["reply_rate"] = self._calculate_percentage(
                    india_status.get("Replied", 0) + india_status.get("Call Requested", 0),
                    india_total
                )

                metrics["by_country"]["India"]["call_rate"] = self._calculate_percentage(
                    india_status.get("Call Requested", 0) + india_status.get("Call Scheduled", 0),
                    india_total
                )

                metrics["by_country"]["India"]["payment_rate"] = self._calculate_percentage(
                    india_status.get("Payment Link Sent", 0) + india_status.get("Payment Received", 0),
                    india_total
                )

                metrics["by_country"]["India"]["conversion_rate"] = self._calculate_percentage(
                    india_status.get("Payment Received", 0) + india_status.get("Onboarding", 0),
                    india_total
                )

            # Overall metrics
            overall_replied = (us_status.get("Replied", 0) + us_status.get("Call Requested", 0) +
                              india_status.get("Replied", 0) + india_status.get("Call Requested", 0))

            overall_calls = (us_status.get("Call Requested", 0) + us_status.get("Call Scheduled", 0) +
                            india_status.get("Call Requested", 0) + india_status.get("Call Scheduled", 0))

            overall_payments_sent = (us_status.get("Payment Link Sent", 0) + india_status.get("Payment Link Sent", 0))

            overall_payments_received = (us_status.get("Payment Received", 0) + us_status.get("Onboarding", 0) +
                                       india_status.get("Payment Received", 0) + india_status.get("Onboarding", 0))

            # Calculate overall rates
            metrics["overall"]["reply_rate"] = self._calculate_percentage(overall_replied, total_leads)
            metrics["overall"]["call_rate"] = self._calculate_percentage(overall_calls, total_leads)
            metrics["overall"]["payment_rate"] = self._calculate_percentage(overall_payments_sent, total_leads)
            metrics["overall"]["conversion_rate"] = self._calculate_percentage(overall_payments_received, total_leads)

            # Lead distribution
            metrics["overall"]["us_percentage"] = self._calculate_percentage(us_total, total_leads)
            metrics["overall"]["india_percentage"] = self._calculate_percentage(india_total, total_leads)

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            return metrics

    def _calculate_percentage(self, part, total):
        """Calculate percentage with two decimal places"""
        if total == 0:
            return 0.0
        return round((part / total) * 100, 2)

    def _generate_suggestions(self, analytics_data, metrics):
        """
        Generate suggestions for funnel optimization

        Args:
            analytics_data (dict): Analytics data
            metrics (dict): Calculated metrics

        Returns:
            list: Suggestions for optimization
        """
        suggestions = []

        try:
            # Overall conversion rate check
            overall_conversion = metrics.get("overall", {}).get("conversion_rate", 0)
            if overall_conversion < 5:
                suggestions.append({
                    "priority": "high",
                    "area": "Conversion",
                    "suggestion": "Your overall conversion rate is below 5%. Consider revising your entire funnel, starting with initial outreach messaging and call process."
                })

            # Check for country discrepancies
            us_conversion = metrics.get("by_country", {}).get("US", {}).get("conversion_rate", 0)
            india_conversion = metrics.get("by_country", {}).get("India", {}).get("conversion_rate", 0)

            conversion_difference = abs(us_conversion - india_conversion)
            if conversion_difference > 10:
                better_country = "US" if us_conversion > india_conversion else "India"
                worse_country = "India" if better_country == "US" else "US"

                suggestions.append({
                    "priority": "medium",
                    "area": "Regional Performance",
                    "suggestion": f"{better_country} leads are converting {conversion_difference}% better than {worse_country} leads. Review messaging and pricing strategy for {worse_country}."
                })

            # Email reply rate check
            overall_reply = metrics.get("overall", {}).get("reply_rate", 0)
            if overall_reply < 10:
                suggestions.append({
                    "priority": "high",
                    "area": "Email Engagement",
                    "suggestion": "Your email reply rate is below 10%. Test new subject lines and email content to increase engagement."
                })

            # Call booking rate
            overall_call = metrics.get("overall", {}).get("call_rate", 0)
            if overall_call < 5:
                suggestions.append({
                    "priority": "medium",
                    "area": "Call Booking",
                    "suggestion": "Your call booking rate is low. Consider making it easier to book calls or offer incentives for scheduling."
                })

            # Payment link to payment conversion
            us_payments_sent = analytics_data.get("us_leads", {}).get("by_status", {}).get("Payment Link Sent", 0)
            us_payments_received = analytics_data.get("us_leads", {}).get("by_status", {}).get("Payment Received", 0)

            india_payments_sent = analytics_data.get("india_leads", {}).get("by_status", {}).get("Payment Link Sent", 0)
            india_payments_received = analytics_data.get("india_leads", {}).get("by_status", {}).get("Payment Received", 0)

            total_sent = us_payments_sent + india_payments_sent
            total_received = us_payments_received + india_payments_received

            if total_sent > 0:
                payment_conversion = self._calculate_percentage(total_received, total_sent)

                if payment_conversion < 30:
                    suggestions.append({
                        "priority": "high",
                        "area": "Payment Process",
                        "suggestion": f"Only {payment_conversion}% of payment links are converting. Consider offering payment plans, different payment methods, or follow up personally after sending payment links."
                    })

            # Lead volume check
            us_total = analytics_data.get("us_leads", {}).get("total", 0)
            india_total = analytics_data.get("india_leads", {}).get("total", 0)

            if us_total < 20:
                suggestions.append({
                    "priority": "medium",
                    "area": "Lead Volume - US",
                    "suggestion": "You have fewer than 20 US leads. Increase your lead generation efforts for this market."
                })

            if india_total < 20:
                suggestions.append({
                    "priority": "medium",
                    "area": "Lead Volume - India",
                    "suggestion": "You have fewer than 20 India leads. Increase your lead generation efforts for this market."
                })

            # Check for recent activity
            recent = analytics_data.get("recent_activities", [])
            if len(recent) < 5:
                suggestions.append({
                    "priority": "low",
                    "area": "Activity Level",
                    "suggestion": "There seems to be low recent activity. Consider running a new lead generation campaign or follow-up sequence."
                })

            return suggestions

        except Exception as e:
            self.logger.error(f"Error generating suggestions: {str(e)}")
            return [{"priority": "high", "area": "System Error", "suggestion": "Error generating suggestions. Please check logs."}]

    def track_email_open(self, email_id, lead_id):
        """
        Track email open event

        Args:
            email_id (str): Email ID
            lead_id (str): Lead ID

        Returns:
            bool: Success status
        """
        try:
            # Get lead
            lead = self.sheets_service.get_lead(lead_id)

            if not lead:
                self.logger.warning(f"Cannot track email open for unknown lead: {lead_id}")
                return False

            # Update lead notes
            self.sheets_service.update_lead(
                lead_id,
                lead.get("status", "Contacted"),
                f"Email opened: {email_id} at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Error tracking email open: {str(e)}")
            return False

    def track_link_click(self, link_id, lead_id, link_type):
        """
        Track link click event

        Args:
            link_id (str): Link ID
            lead_id (str): Lead ID
            link_type (str): Link type (calendly, payment, etc.)

        Returns:
            bool: Success status
        """
        try:
            # Get lead
            lead = self.sheets_service.get_lead(lead_id)

            if not lead:
                self.logger.warning(f"Cannot track link click for unknown lead: {lead_id}")
                return False

            # Update lead notes based on link type
            if link_type == "calendly":
                self.sheets_service.update_lead(
                    lead_id,
                    "Call Link Clicked",
                    f"Calendly link clicked at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            elif link_type == "payment":
                self.sheets_service.update_lead(
                    lead_id,
                    "Payment Link Clicked",
                    f"Payment link clicked at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            else:
                self.sheets_service.update_lead(
                    lead_id,
                    lead.get("status", "Contacted"),
                    f"Link clicked: {link_id} ({link_type}) at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )

            return True

        except Exception as e:
            self.logger.error(f"Error tracking link click: {str(e)}")
            return False
