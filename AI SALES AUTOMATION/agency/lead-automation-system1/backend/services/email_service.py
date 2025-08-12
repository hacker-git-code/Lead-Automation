import os
import smtplib
import logging
import json
import time
import schedule
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Local imports
from services.sheets_service import SheetsService

# Load environment variables
load_dotenv()

class EmailService:
    """
    Service for handling automated email outreach to leads
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sheets_service = SheetsService()

        # Email credentials
        self.gmail_username = os.environ.get('GMAIL_USERNAME')
        self.gmail_password = os.environ.get('GMAIL_PASSWORD')
        self.outlook_email = os.environ.get('OUTLOOK_EMAIL')
        self.outlook_password = os.environ.get('OUTLOOK_PASSWORD')

        # Calendly link
        self.calendly_link = os.environ.get('CALENDLY_LINK', 'https://calendly.com/yourusername')

        # Campaign tracking
        self.active_campaigns = {}
        self.follow_up_thread = None

        # Start follow-up scheduler
        self._start_follow_up_scheduler()

    def _start_follow_up_scheduler(self):
        """Start the scheduler for follow-up emails"""
        def run_scheduler():
            # Schedule follow-ups to run every day at 10 AM
            schedule.every().day.at("10:00").do(self._process_follow_ups)

            while True:
                schedule.run_pending()
                time.sleep(60)

        # Start scheduler in a separate thread
        self.follow_up_thread = threading.Thread(target=run_scheduler)
        self.follow_up_thread.daemon = True
        self.follow_up_thread.start()
        self.logger.info("Follow-up scheduler started")

    def _get_smtp_connection(self, country):
        """
        Get SMTP connection based on lead country

        Args:
            country (str): Lead country (US or IN)

        Returns:
            tuple: (smtp_server, username, password)
        """
        if country == "US":
            # Use Outlook for US leads
            return {
                "server": "smtp-mail.outlook.com",
                "port": 587,
                "username": self.outlook_email,
                "password": self.outlook_password
            }
        else:
            # Use Gmail for India leads
            return {
                "server": "smtp.gmail.com",
                "port": 587,
                "username": self.gmail_username,
                "password": self.gmail_password
            }

    def _send_email(self, to_email, subject, html_content, country):
        """
        Send an email

        Args:
            to_email (str): Recipient email
            subject (str): Email subject
            html_content (str): Email HTML content
            country (str): Lead country (US or IN)

        Returns:
            bool: Success status
        """
        # Get SMTP connection based on country
        smtp_config = self._get_smtp_connection(country)

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_config["username"]
        msg['To'] = to_email

        # Add HTML content
        msg.attach(MIMEText(html_content, 'html'))

        try:
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_config["server"], smtp_config["port"])
            server.starttls()
            server.login(smtp_config["username"], smtp_config["password"])

            # Send email
            server.sendmail(smtp_config["username"], to_email, msg.as_string())
            server.quit()

            self.logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False

    def _get_email_templates(self, sequence_type):
        """
        Get email templates for a sequence

        Args:
            sequence_type (str): Sequence type (initial, follow_up_1, etc.)

        Returns:
            dict: Template data with subject and body
        """
        # These would typically be loaded from a database or template files
        # For simplicity, we'll define them here
        templates = {
            "initial": {
                "us": {
                    "subject": "Quick question about {{company}}",
                    "body": """
                    <p>Hi {{first_name}},</p>
                    <p>I noticed you're the owner of {{company}} and I wanted to reach out.</p>
                    <p>We've been helping {{business_type}} like yours streamline their operations and increase revenue.</p>
                    <p>Would you be interested in a quick 15-minute chat to see if we could help you too?</p>
                    <p>Best regards,<br>Your Name</p>
                    """
                },
                "india": {
                    "subject": "Regarding your business: {{company}}",
                    "body": """
                    <p>Hello {{first_name}},</p>
                    <p>I came across {{company}} while researching leading {{business_type}} in {{country}}.</p>
                    <p>Our company specializes in helping businesses like yours increase efficiency and growth.</p>
                    <p>Would you be open to a brief conversation about how we might help your business?</p>
                    <p>Regards,<br>Your Name</p>
                    """
                }
            },
            "follow_up_1": {
                "us": {
                    "subject": "Following up: {{company}}",
                    "body": """
                    <p>Hi {{first_name}},</p>
                    <p>I wanted to follow up on my previous email about how we could help {{company}}.</p>
                    <p>Many {{business_type}} owners we work with have seen significant improvements in just a few weeks.</p>
                    <p>Would you be available for a quick call this week?</p>
                    <p>Best regards,<br>Your Name</p>
                    """
                },
                "india": {
                    "subject": "Quick follow-up: {{company}}",
                    "body": """
                    <p>Hello {{first_name}},</p>
                    <p>I'm following up on my previous message regarding {{company}}.</p>
                    <p>We've helped several {{business_type}} in India achieve remarkable results recently.</p>
                    <p>Would you like to schedule a short call to discuss how we could help you too?</p>
                    <p>Regards,<br>Your Name</p>
                    """
                }
            },
            "follow_up_2": {
                "us": {
                    "subject": "One more thing about {{company}}",
                    "body": """
                    <p>Hi {{first_name}},</p>
                    <p>I thought I'd share that we recently helped a {{business_type}} similar to {{company}} increase their revenue by 30%.</p>
                    <p>I'd love to show you how we did it in a quick call.</p>
                    <p>Let me know if you're interested!</p>
                    <p>Best regards,<br>Your Name</p>
                    """
                },
                "india": {
                    "subject": "Case study for {{company}}",
                    "body": """
                    <p>Hello {{first_name}},</p>
                    <p>I wanted to share a case study about how we helped a {{business_type}} in India similar to {{company}}.</p>
                    <p>They were facing challenges with growth, and we helped them implement solutions that increased their revenue.</p>
                    <p>Would you like to see how we could apply similar strategies to your business?</p>
                    <p>Regards,<br>Your Name</p>
                    """
                }
            },
            "follow_up_3": {
                "us": {
                    "subject": "Final thoughts for {{company}}",
                    "body": """
                    <p>Hi {{first_name}},</p>
                    <p>I've reached out a few times about how we could help {{company}} grow as a {{business_type}}.</p>
                    <p>I understand you might be busy, so this will be my last email for now.</p>
                    <p>If you'd like to explore how we could work together in the future, please feel free to reach out.</p>
                    <p>Best regards,<br>Your Name</p>
                    """
                },
                "india": {
                    "subject": "Last message regarding {{company}}",
                    "body": """
                    <p>Hello {{first_name}},</p>
                    <p>I've sent a few messages about how we could support {{company}} as a growing {{business_type}} in India.</p>
                    <p>This will be my last email, but please know my offer to help still stands.</p>
                    <p>Whenever you're ready to discuss, I'm here to help.</p>
                    <p>Regards,<br>Your Name</p>
                    """
                }
            },
            "call_invite": {
                "us": {
                    "subject": "Call details for our discussion",
                    "body": """
                    <p>Hi {{first_name}},</p>
                    <p>Thank you for your interest in discussing how we can help {{company}}.</p>
                    <p>You can book a time on my calendar here: <a href="{{calendly_link}}">Schedule a Call</a></p>
                    <p>I look forward to our conversation!</p>
                    <p>Best regards,<br>Your Name</p>
                    """
                },
                "india": {
                    "subject": "Schedule our call",
                    "body": """
                    <p>Hello {{first_name}},</p>
                    <p>Thanks for your interest in exploring how we can help {{company}} grow.</p>
                    <p>Please use this link to book a time that works for you: <a href="{{calendly_link}}">Book a Call</a></p>
                    <p>I'm looking forward to our discussion!</p>
                    <p>Regards,<br>Your Name</p>
                    """
                }
            },
            "pricing_info": {
                "us": {
                    "subject": "Investment details for {{company}}",
                    "body": """
                    <p>Hi {{first_name}},</p>
                    <p>Thank you for your interest in our services for {{company}}.</p>
                    <p>Based on our discussion, the investment for our solution would be ${{price}}.</p>
                    <p>You can make the payment securely through this link: <a href="{{payment_link}}">Make Payment</a></p>
                    <p>Once the payment is confirmed, we'll begin the onboarding process right away.</p>
                    <p>Best regards,<br>Your Name</p>
                    """
                },
                "india": {
                    "subject": "Pricing information for {{company}}",
                    "body": """
                    <p>Hello {{first_name}},</p>
                    <p>Thank you for considering our services for {{company}}.</p>
                    <p>The investment for our solution would be ₹{{price}}.</p>
                    <p>You can complete the payment through this secure link: <a href="{{payment_link}}">Make Payment</a></p>
                    <p>After payment confirmation, we'll start the onboarding process immediately.</p>
                    <p>Regards,<br>Your Name</p>
                    """
                }
            }
        }

        return templates.get(sequence_type, templates["initial"])

    def _personalize_template(self, template, lead):
        """
        Personalize an email template with lead data

        Args:
            template (str): Email template
            lead (dict): Lead data

        Returns:
            str: Personalized template
        """
        # Determine business type based on industry
        business_type = lead.get("industry", "business")
        if not business_type or business_type.lower() == "n/a":
            if "agency" in lead.get("company", "").lower():
                business_type = "digital agency"
            elif "coach" in lead.get("title", "").lower():
                business_type = "coaching business"
            elif "consult" in lead.get("title", "").lower():
                business_type = "consulting business"
            else:
                business_type = "business"

        # Replacements
        replacements = {
            "{{first_name}}": lead.get("first_name", "there"),
            "{{last_name}}": lead.get("last_name", ""),
            "{{company}}": lead.get("company", "your business"),
            "{{business_type}}": business_type,
            "{{country}}": "the United States" if lead.get("country") == "US" else "India",
            "{{calendly_link}}": self.calendly_link,
            "{{payment_link}}": lead.get("payment_link", "#")
        }

        # Apply replacements
        personalized = template
        for key, value in replacements.items():
            personalized = personalized.replace(key, value)

        return personalized

    def start_campaign(self, leads):
        """
        Start email outreach campaign for leads

        Args:
            leads (list): List of lead objects

        Returns:
            dict: Campaign results
        """
        results = {
            "success": 0,
            "failed": 0,
            "leads": []
        }

        for lead in leads:
            lead_id = lead.get("id")
            email = lead.get("email")
            country = lead.get("country")

            if not email:
                self.logger.warning(f"No email for lead {lead_id}, skipping")
                results["failed"] += 1
                results["leads"].append({
                    "id": lead_id,
                    "status": "Failed",
                    "reason": "No email address"
                })
                continue

            # Determine country template set
            country_code = "us" if country == "US" else "india"

            # Get email template
            templates = self._get_email_templates("initial")
            template_data = templates.get(country_code, templates["us"])

            # Personalize subject and body
            subject = self._personalize_template(template_data["subject"], lead)
            body = self._personalize_template(template_data["body"], lead)

            # Send email
            success = self._send_email(email, subject, body, country)

            if success:
                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "Initial Contact",
                    "Initial email sent"
                )

                # Add to active campaigns
                self.active_campaigns[lead_id] = {
                    "lead": lead,
                    "sequence": "initial",
                    "last_contact": datetime.now(),
                    "follow_up_count": 0,
                    "max_follow_ups": 3,
                    "next_follow_up": datetime.now() + timedelta(days=3)
                }

                results["success"] += 1
                results["leads"].append({
                    "id": lead_id,
                    "status": "Success",
                    "next_follow_up": self.active_campaigns[lead_id]["next_follow_up"].strftime("%Y-%m-%d")
                })
            else:
                results["failed"] += 1
                results["leads"].append({
                    "id": lead_id,
                    "status": "Failed",
                    "reason": "Email sending failed"
                })

        return results

    def _process_follow_ups(self):
        """Process follow-up emails for active campaigns"""
        now = datetime.now()
        leads_to_update = []

        for lead_id, campaign in list(self.active_campaigns.items()):
            # Skip if not time for follow-up yet
            if campaign["next_follow_up"] > now:
                continue

            # Skip if max follow-ups reached
            if campaign["follow_up_count"] >= campaign["max_follow_ups"]:
                # Close campaign
                del self.active_campaigns[lead_id]

                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "No Response",
                    f"Completed {campaign['follow_up_count']} follow-ups with no response"
                )
                continue

            # Determine next follow-up template
            campaign["follow_up_count"] += 1
            sequence_type = f"follow_up_{campaign['follow_up_count']}"

            lead = campaign["lead"]
            country = lead.get("country")
            email = lead.get("email")

            # Determine country template set
            country_code = "us" if country == "US" else "india"

            # Get email template
            templates = self._get_email_templates(sequence_type)
            template_data = templates.get(country_code, templates["us"])

            # Personalize subject and body
            subject = self._personalize_template(template_data["subject"], lead)
            body = self._personalize_template(template_data["body"], lead)

            # Send email
            success = self._send_email(email, subject, body, country)

            if success:
                # Update campaign status
                campaign["last_contact"] = now
                campaign["next_follow_up"] = now + timedelta(days=3)

                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "Follow-up",
                    f"Follow-up email #{campaign['follow_up_count']} sent"
                )

                self.logger.info(f"Sent follow-up #{campaign['follow_up_count']} to {email}")
            else:
                # Log failure
                self.logger.error(f"Failed to send follow-up to {email}")

    def handle_reply(self, email_data):
        """
        Handle email reply webhook

        Args:
            email_data (dict): Email webhook data

        Returns:
            bool: Success status
        """
        try:
            from_email = email_data.get("from", "")
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")

            # Find lead by email
            leads = self.sheets_service.get_leads()
            matching_leads = [lead for lead in leads if lead.get("email") == from_email]

            if not matching_leads:
                self.logger.warning(f"Reply from unknown email: {from_email}")
                return False

            lead = matching_leads[0]
            lead_id = lead.get("id")

            # Remove from active campaigns if exists
            if lead_id in self.active_campaigns:
                del self.active_campaigns[lead_id]

            # Check for keywords indicating interest in a call
            call_keywords = ["call", "meeting", "schedule", "calendly", "available", "time"]
            wants_call = any(keyword in body.lower() for keyword in call_keywords)

            if wants_call:
                # Send calendly link
                country = lead.get("country")
                country_code = "us" if country == "US" else "india"

                # Get template
                templates = self._get_email_templates("call_invite")
                template_data = templates.get(country_code, templates["us"])

                # Personalize
                email_subject = self._personalize_template(template_data["subject"], lead)
                email_body = self._personalize_template(template_data["body"], lead)

                # Send email
                self._send_email(from_email, email_subject, email_body, country)

                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "Call Requested",
                    "Lead requested a call, sent Calendly link"
                )
            else:
                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "Replied",
                    f"Lead replied: {subject}"
                )

            return True

        except Exception as e:
            self.logger.error(f"Error handling email reply: {str(e)}")
            return False

    def send_payment_link(self, lead, amount):
        """
        Send payment link email

        Args:
            lead (dict): Lead data
            amount (float): Payment amount

        Returns:
            bool: Success status
        """
        try:
            lead_id = lead.get("id")
            email = lead.get("email")
            country = lead.get("country")

            if not email:
                self.logger.warning(f"No email for lead {lead_id}, cannot send payment link")
                return False

            # Format price based on country
            if country == "US":
                formatted_price = f"{amount:,.2f}"
            else:
                formatted_price = f"{int(amount):,}"

            # Add payment info to lead
            lead["price"] = formatted_price

            # Get country template
            country_code = "us" if country == "US" else "india"

            # Get template
            templates = self._get_email_templates("pricing_info")
            template_data = templates.get(country_code, templates["us"])

            # Personalize
            email_subject = self._personalize_template(template_data["subject"], lead)
            email_body = self._personalize_template(template_data["body"], lead)

            # Send email
            success = self._send_email(email, email_subject, email_body, country)

            if success:
                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "Payment Link Sent",
                    f"Sent payment link for {formatted_price}"
                )

                # Remove from active campaigns if exists
                if lead_id in self.active_campaigns:
                    del self.active_campaigns[lead_id]

                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"Error sending payment link: {str(e)}")
            return False
