import os
import logging
import stripe
import razorpay
import json
from datetime import datetime
from dotenv import load_dotenv

# Local imports
from services.sheets_service import SheetsService
from services.email_service import EmailService

# Load environment variables
load_dotenv()

class PaymentService:
    """
    Service for handling payments through Stripe (US) and Razorpay (India)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sheets_service = SheetsService()

        # Initialize Stripe
        self.stripe_api_key = os.environ.get('STRIPE_API_KEY')
        self.stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')

        if self.stripe_api_key:
            stripe.api_key = self.stripe_api_key
        else:
            self.logger.warning("Stripe API key not set. US payment functionality will be limited.")

        # Initialize Razorpay
        self.razorpay_key_id = os.environ.get('RAZORPAY_KEY_ID')
        self.razorpay_key_secret = os.environ.get('RAZORPAY_KEY_SECRET')

        if self.razorpay_key_id and self.razorpay_key_secret:
            self.razorpay_client = razorpay.Client(
                auth=(self.razorpay_key_id, self.razorpay_key_secret))
        else:
            self.logger.warning("Razorpay credentials not set. India payment functionality will be limited.")
            self.razorpay_client = None

    def create_payment_link(self, country, amount, lead):
        """
        Create payment link based on lead country

        Args:
            country (str): Lead country (US or IN)
            amount (float): Payment amount
            lead (dict): Lead data

        Returns:
            str: Payment link URL
        """
        if country == "US":
            return self._create_stripe_payment_link(amount, lead)
        else:
            return self._create_razorpay_payment_link(amount, lead)

    def _create_stripe_payment_link(self, amount, lead):
        """
        Create Stripe payment link for US leads

        Args:
            amount (float): Payment amount in USD
            lead (dict): Lead data

        Returns:
            str: Payment link URL
        """
        if not self.stripe_api_key:
            self.logger.error("Stripe API key not configured")
            return "#stripe-not-configured"

        try:
            # Convert amount to cents
            amount_cents = int(float(amount) * 100)

            # Create product for this specific service
            product = stripe.Product.create(
                name="Consulting Services for " + lead.get("company", "Your Business"),
                description="Custom business consulting services"
            )

            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=amount_cents,
                currency="usd",
                recurring=None,  # One-time payment
            )

            # Create payment link
            payment_link = stripe.PaymentLink.create(
                line_items=[{"price": price.id, "quantity": 1}],
                after_completion={"type": "redirect", "redirect": {"url": "https://yourdomain.com/thank-you"}},
                metadata={
                    "lead_id": lead.get("id", ""),
                    "company": lead.get("company", ""),
                    "email": lead.get("email", ""),
                    "country": "US"
                }
            )

            # Log and store payment link
            payment_url = payment_link.url
            self.logger.info(f"Created Stripe payment link for {lead.get('id')}: {payment_url}")

            # Store payment link in lead data
            self.sheets_service.update_lead(
                lead.get("id", ""),
                "Payment Link Created",
                f"Created Stripe payment link: {payment_url} for ${amount}"
            )

            return payment_url

        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe error: {str(e)}")
            return f"#stripe-error: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error creating Stripe payment link: {str(e)}")
            return "#payment-error"

    def _create_razorpay_payment_link(self, amount, lead):
        """
        Create Razorpay payment link for India leads

        Args:
            amount (float): Payment amount in INR
            lead (dict): Lead data

        Returns:
            str: Payment link URL
        """
        if not self.razorpay_client:
            self.logger.error("Razorpay client not configured")
            return "#razorpay-not-configured"

        try:
            # Round amount to nearest rupee
            amount_paise = int(float(amount) * 100)

            # Create customer
            customer = self.razorpay_client.customer.create({
                "name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}",
                "email": lead.get("email", ""),
                "contact": lead.get("phone", ""),
                "notes": {
                    "lead_id": lead.get("id", ""),
                    "company": lead.get("company", ""),
                }
            })

            # Create payment link
            payment_data = {
                "amount": amount_paise,
                "currency": "INR",
                "accept_partial": False,
                "description": f"Consulting Services for {lead.get('company', 'Your Business')}",
                "customer": {
                    "name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}",
                    "email": lead.get("email", ""),
                    "contact": lead.get("phone", "")
                },
                "notify": {
                    "email": True,
                    "sms": True
                },
                "notes": {
                    "lead_id": lead.get("id", ""),
                    "country": "IN"
                },
                "callback_url": "https://yourdomain.com/payment-success",
                "callback_method": "get"
            }

            # Create the payment link
            payment_link = self.razorpay_client.payment_link.create(payment_data)

            # Log and store payment link
            payment_url = payment_link['short_url']
            self.logger.info(f"Created Razorpay payment link for {lead.get('id')}: {payment_url}")

            # Store payment link in lead data
            self.sheets_service.update_lead(
                lead.get("id", ""),
                "Payment Link Created",
                f"Created Razorpay payment link: {payment_url} for ₹{int(amount)}"
            )

            return payment_url

        except Exception as e:
            self.logger.error(f"Error creating Razorpay payment link: {str(e)}")
            return "#payment-error"

    def handle_webhook(self, webhook_data):
        """
        Handle payment webhooks from Stripe/Razorpay

        Args:
            webhook_data (dict): Webhook data

        Returns:
            bool: Success status
        """
        try:
            # Determine webhook source
            source = webhook_data.get("source", "unknown")
            event_type = webhook_data.get("type", "")

            if source == "stripe":
                return self._handle_stripe_webhook(webhook_data)
            elif source == "razorpay":
                return self._handle_razorpay_webhook(webhook_data)
            else:
                self.logger.warning(f"Unknown webhook source: {source}")
                return False

        except Exception as e:
            self.logger.error(f"Error handling payment webhook: {str(e)}")
            return False

    def _handle_stripe_webhook(self, webhook_data):
        """
        Handle Stripe payment webhook

        Args:
            webhook_data (dict): Webhook data

        Returns:
            bool: Success status
        """
        try:
            event_type = webhook_data.get("type", "")

            # Check if this is a payment success event
            if event_type == "checkout.session.completed":
                session = webhook_data.get("data", {}).get("object", {})
                metadata = session.get("metadata", {})
                lead_id = metadata.get("lead_id", "")

                if not lead_id:
                    self.logger.warning("No lead_id in Stripe webhook metadata")
                    return False

                # Get payment amount
                amount = session.get("amount_total", 0) / 100  # Convert cents to dollars

                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "Payment Received",
                    f"Received Stripe payment of ${amount:.2f}"
                )

                # Get lead data for onboarding
                lead = self.sheets_service.get_lead(lead_id)

                # Handle onboarding (you'd implement this separately)
                self._send_onboarding_email(lead)

                return True

            return False

        except Exception as e:
            self.logger.error(f"Error handling Stripe webhook: {str(e)}")
            return False

    def _handle_razorpay_webhook(self, webhook_data):
        """
        Handle Razorpay payment webhook

        Args:
            webhook_data (dict): Webhook data

        Returns:
            bool: Success status
        """
        try:
            event_type = webhook_data.get("event", "")

            # Check if this is a payment success event
            if event_type == "payment.authorized":
                payload = webhook_data.get("payload", {})
                payment = payload.get("payment", {}).get("entity", {})
                notes = payment.get("notes", {})
                lead_id = notes.get("lead_id", "")

                if not lead_id:
                    self.logger.warning("No lead_id in Razorpay webhook notes")
                    return False

                # Get payment amount
                amount = payment.get("amount", 0) / 100  # Convert paise to rupees

                # Update lead status
                self.sheets_service.update_lead(
                    lead_id,
                    "Payment Received",
                    f"Received Razorpay payment of ₹{int(amount)}"
                )

                # Get lead data for onboarding
                lead = self.sheets_service.get_lead(lead_id)

                # Handle onboarding (you'd implement this separately)
                self._send_onboarding_email(lead)

                return True

            return False

        except Exception as e:
            self.logger.error(f"Error handling Razorpay webhook: {str(e)}")
            return False

    def _send_onboarding_email(self, lead):
        """
        Send onboarding email after payment

        Args:
            lead (dict): Lead data

        Returns:
            bool: Success status
        """
        try:
            from email_service import EmailService
            email_service = EmailService()

            country = lead.get("country", "US")
            email = lead.get("email", "")

            if not email:
                self.logger.warning(f"No email for lead {lead.get('id')}, cannot send onboarding email")
                return False

            # Determine email template based on country
            if country == "US":
                subject = f"Welcome onboard, {lead.get('first_name')}! Next steps for {lead.get('company')}"
                template = """
                <p>Hi {{first_name}},</p>
                <p>Thank you for your payment! We're excited to start working with {{company}}.</p>
                <p>Here are the next steps:</p>
                <ol>
                    <li>Complete our onboarding questionnaire: [LINK]</li>
                    <li>Schedule your kickoff call: [LINK]</li>
                    <li>Review our welcome packet: [LINK]</li>
                </ol>
                <p>Best regards,<br>Your Name</p>
                """
            else:
                subject = f"Welcome to our services, {lead.get('first_name')}! Next steps for {lead.get('company')}"
                template = """
                <p>Hello {{first_name}},</p>
                <p>Thank you for your payment! We're thrilled to begin working with {{company}}.</p>
                <p>Here's what happens next:</p>
                <ol>
                    <li>Fill out our onboarding form: [LINK]</li>
                    <li>Book your initial strategy call: [LINK]</li>
                    <li>Check out our welcome materials: [LINK]</li>
                </ol>
                <p>Regards,<br>Your Name</p>
                """

            # Personalize email
            body = email_service._personalize_template(template, lead)

            # Send email
            success = email_service._send_email(email, subject, body, country)

            if success:
                self.sheets_service.update_lead(
                    lead.get("id", ""),
                    "Onboarding",
                    "Sent onboarding email"
                )
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"Error sending onboarding email: {str(e)}")
            return False

    def suggest_pricing(self, lead):
        """
        Suggest pricing based on lead data

        Args:
            lead (dict): Lead data

        Returns:
            dict: Suggested pricing options
        """
        country = lead.get("country", "US")
        revenue = lead.get("estimated_revenue", 0)
        company_size = lead.get("company_size", 0)

        # Default pricing tiers
        if country == "US":
            pricing = {
                "standard": 2500,
                "premium": 3500,
                "enterprise": 5000
            }
        else:
            pricing = {
                "standard": 40000,
                "premium": 85000,
                "enterprise": 150000
            }

        # Adjust based on company size and revenue
        if isinstance(company_size, str):
            try:
                company_size = int(company_size)
            except:
                company_size = 0

        # Convert revenue to numeric if it's a string
        if isinstance(revenue, str):
            try:
                # Remove currency symbols and commas
                revenue = revenue.replace("$", "").replace("₹", "").replace(",", "")
                revenue = float(revenue)
            except:
                revenue = 0

        # Adjust pricing based on company size
        if company_size > 100:
            # Larger company - increase prices
            pricing = {k: v * 1.2 for k, v in pricing.items()}
        elif company_size < 10:
            # Small company - decrease prices slightly
            pricing = {k: v * 0.9 for k, v in pricing.items()}

        # Adjust pricing based on revenue
        if country == "US":
            if revenue > 10000000:  # $10M+
                pricing = {k: v * 1.3 for k, v in pricing.items()}
            elif revenue > 5000000:  # $5M+
                pricing = {k: v * 1.1 for k, v in pricing.items()}
        else:
            if revenue > 100000000:  # ₹10Cr+
                pricing = {k: v * 1.3 for k, v in pricing.items()}
            elif revenue > 50000000:  # ₹5Cr+
                pricing = {k: v * 1.1 for k, v in pricing.items()}

        # Format prices
        if country == "US":
            formatted_pricing = {
                k: f"${v:,.2f}" for k, v in pricing.items()
            }
        else:
            formatted_pricing = {
                k: f"₹{int(v):,}" for k, v in pricing.items()
            }

        return {
            "pricing": pricing,
            "formatted": formatted_pricing,
            "currency": "USD" if country == "US" else "INR"
        }
