import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    """
    Service for sending and managing email outreach
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Gmail credentials (for India leads)
        self.gmail_username = os.environ.get("GMAIL_USERNAME")
        self.gmail_password = os.environ.get("GMAIL_PASSWORD")

        # Outlook credentials (for US leads)
        self.outlook_email = os.environ.get("OUTLOOK_EMAIL")
        self.outlook_password = os.environ.get("OUTLOOK_PASSWORD")

        # Email templates
        self.templates = {
            "initial": {
                "subject": "Let's talk about boosting {company}'s growth",
                "body": """
                Hello {first_name},

                I noticed {company} has been making some impressive moves in the {industry} space.

                We specialize in helping {industry} companies like yours achieve significant growth through our specialized lead generation services.

                Would you be interested in a 15-minute call to discuss how we might help {company} reach its growth goals this quarter?

                Best regards,
                {sender_name}
                """
            },
            "follow_up_1": {
                "subject": "Following up on my message to {first_name}",
                "body": """
                Hi {first_name},

                I wanted to follow up on my previous message about helping {company} scale its customer acquisition.

                Our clients in the {industry} sector typically see a 30-40% increase in qualified leads within the first 60 days.

                I'd love to share some specific ideas for {company} - are you available for a quick call this week?

                Best,
                {sender_name}
                """
            },
            "follow_up_2": {
                "subject": "Ideas for {company}'s growth strategy",
                "body": """
                Hi {first_name},

                I've been thinking about {company}'s positioning in the {industry} market, and I have a few specific ideas that might help you attract more high-value clients.

                I've helped similar companies implement these strategies with great success.

                Would a 15-minute call next week work for you?

                Regards,
                {sender_name}
                """
            },
            "follow_up_3": {
                "subject": "One last message for {first_name}",
                "body": """
                Hi {first_name},

                I've reached out a few times about helping {company} with its growth strategy.

                If you're interested in learning how we've helped other {industry} businesses increase their qualified leads by 30-40%, just reply to this email or book a call here: {calendly_link}

                I won't bother you again, but I'm here if you need any assistance in the future.

                Best regards,
                {sender_name}
                """
            }
        }

        # In a real implementation, this would track email campaigns in a database
        # For demonstration, we'll use in-memory storage
        self.campaigns = []

    def start_campaign(self, leads):
        """
        Start an email outreach campaign for a list of leads

        Args:
            leads (list): List of lead objects

        Returns:
            dict: Campaign results
        """
        try:
            self.logger.info(f"Starting email campaign for {len(leads)} leads")

            results = {
                "success": 0,
                "failed": 0,
                "leads": []
            }

            for lead in leads:
                try:
                    # Send initial email
                    email_sent = self._send_email(
                        lead,
                        self.templates["initial"]["subject"],
                        self.templates["initial"]["body"],
                        "initial"
                    )

                    lead_result = {
                        "id": lead.get("id"),
                        "email": lead.get("email"),
                        "name": f"{lead.get('first_name')} {lead.get('last_name')}",
                        "status": "Success" if email_sent else "Failed"
                    }

                    if email_sent:
                        results["success"] += 1

                        # Create campaign entry
                        campaign = {
                            "lead_id": lead.get("id"),
                            "stage": "initial",
                            "last_contact": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "replies": 0,
                            "status": "Active"
                        }
                        self.campaigns.append(campaign)
                    else:
                        results["failed"] += 1

                    results["leads"].append(lead_result)

                except Exception as e:
                    self.logger.error(f"Error sending email to {lead.get('email')}: {str(e)}")
                    results["failed"] += 1
                    results["leads"].append({
                        "id": lead.get("id"),
                        "email": lead.get("email"),
                        "name": f"{lead.get('first_name')} {lead.get('last_name')}",
                        "status": "Failed",
                        "error": str(e)
                    })

            return results

        except Exception as e:
            self.logger.error(f"Error starting email campaign: {str(e)}")
            raise

    def handle_reply(self, data):
        """
        Handle email reply webhook

        Args:
            data (dict): Webhook data

        Returns:
            bool: Success status
        """
        try:
            self.logger.info(f"Handling email reply: {data}")

            # Extract email data
            email_id = data.get("email_id")
            lead_id = data.get("lead_id")

            # Update campaign status
            campaign = next((c for c in self.campaigns if c.get('lead_id') == lead_id), None)

            if campaign:
                campaign["replies"] += 1
                campaign["status"] = "Replied"
                campaign["last_contact"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return True

        except Exception as e:
            self.logger.error(f"Error handling email reply: {str(e)}")
            return False

    def _send_email(self, lead, subject_template, body_template, stage):
        """
        Send an email to a lead

        Args:
            lead (dict): Lead object
            subject_template (str): Email subject template
            body_template (str): Email body template
            stage (str): Campaign stage

        Returns:
            bool: Success status
        """
        try:
            # Determine which email provider to use based on lead country
            if lead.get("country") == "US":
                sender_email = self.outlook_email
                sender_name = "Lead Automation US Team"
                password = self.outlook_password
                smtp_server = "smtp-mail.outlook.com"
                port = 587
            else:
                sender_email = self.gmail_username
                sender_name = "Lead Automation India Team"
                password = self.gmail_password
                smtp_server = "smtp.gmail.com"
                port = 587

            # Prepare recipient
            recipient_email = lead.get("email")

            if not recipient_email:
                self.logger.warning(f"No email address for lead {lead.get('id')}")
                return False

            # Prepare email content
            subject = subject_template.format(
                first_name=lead.get("first_name", "there"),
                company=lead.get("company", "your company"),
                industry=lead.get("industry", "your industry")
            )

            # Format body
            body = body_template.format(
                first_name=lead.get("first_name", "there"),
                company=lead.get("company", "your company"),
                industry=lead.get("industry", "your industry"),
                sender_name=sender_name,
                calendly_link=os.environ.get("CALENDLY_LINK", "https://calendly.com/example")
            )

            # Create message
            message = MIMEMultipart()
            message["From"] = f"{sender_name} <{sender_email}>"
            message["To"] = recipient_email
            message["Subject"] = subject

            # Attach body
            message.attach(MIMEText(body, "plain"))

            # In a real implementation, this would send the email
            # For demonstration, we'll just log it
            self.logger.info(f"Sending {stage} email to {recipient_email}: {subject}")

            # Simulate successful sending
            return True

        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
