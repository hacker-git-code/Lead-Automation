import os
import logging
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PaymentService:
    """
    Service for processing payments through Stripe (US) and Razorpay (India)
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Stripe API keys (for US)
        self.stripe_api_key = os.environ.get("STRIPE_API_KEY")
        self.stripe_secret_key = os.environ.get("STRIPE_SECRET_KEY")

        # Razorpay API keys (for India)
        self.razorpay_key_id = os.environ.get("RAZORPAY_KEY_ID")
        self.razorpay_key_secret = os.environ.get("RAZORPAY_KEY_SECRET")

        # In a real implementation, this would be stored in a database
        # For demonstration, we'll use in-memory storage
        self.payments = []

    def create_payment_link(self, country, amount, lead):
        """
        Create a payment link based on lead location

        Args:
            country (str): Lead country (US or IN)
            amount (float): Payment amount
            lead (dict): Lead information

        Returns:
            str: Payment link URL
        """
        try:
            self.logger.info(f"Creating payment link for {lead.get('email')}: {country}, amount={amount}")

            # Generate payment ID
            payment_id = str(uuid.uuid4())

            # Format lead name
            lead_name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()

            # Create payment record
            payment = {
                "id": payment_id,
                "lead_id": lead.get("id"),
                "amount": amount,
                "currency": "USD" if country == "US" else "INR",
                "status": "created",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": f"Services for {lead.get('company', 'your business')}",
                "customer_name": lead_name,
                "customer_email": lead.get("email")
            }

            self.payments.append(payment)

            # In a real implementation, this would create a payment link via Stripe or Razorpay API
            # For demonstration, we'll create a mock link

            if country == "US":
                # Format amount for US leads
                formatted_amount = f"${amount}"
                payment_link = f"https://example.com/payment/{payment_id}?amount={amount}&currency=USD"

                self.logger.info(f"Created Stripe payment link for US lead: {payment_link}")
            else:
                # Format amount for India leads
                formatted_amount = f"₹{amount}"
                payment_link = f"https://example.com/payment/{payment_id}?amount={amount}&currency=INR"

                self.logger.info(f"Created Razorpay payment link for India lead: {payment_link}")

            return payment_link

        except Exception as e:
            self.logger.error(f"Error creating payment link: {str(e)}")
            raise

    def handle_webhook(self, data):
        """
        Handle payment webhook from Stripe or Razorpay

        Args:
            data (dict): Webhook data

        Returns:
            bool: Success status
        """
        try:
            self.logger.info(f"Handling payment webhook: {data}")

            # Extract payment data
            payment_id = data.get("payment_id")
            status = data.get("status")

            # Find and update payment
            payment = next((p for p in self.payments if p.get("id") == payment_id), None)

            if not payment:
                self.logger.warning(f"Payment not found: {payment_id}")
                return False

            # Update payment status
            payment["status"] = status
            payment["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.logger.info(f"Updated payment {payment_id} status to {status}")

            return True

        except Exception as e:
            self.logger.error(f"Error handling payment webhook: {str(e)}")
            return False

    def get_payment_details(self, payment_id):
        """
        Get payment details

        Args:
            payment_id (str): Payment ID

        Returns:
            dict: Payment details
        """
        try:
            # Find payment
            payment = next((p for p in self.payments if p.get("id") == payment_id), None)

            if not payment:
                self.logger.warning(f"Payment not found: {payment_id}")
                return None

            return payment

        except Exception as e:
            self.logger.error(f"Error getting payment details: {str(e)}")
            return None

    def get_lead_payments(self, lead_id):
        """
        Get all payments for a lead

        Args:
            lead_id (str): Lead ID

        Returns:
            list: Payment objects
        """
        try:
            # Find payments for lead
            payments = [p for p in self.payments if p.get("lead_id") == lead_id]

            return payments

        except Exception as e:
            self.logger.error(f"Error getting lead payments: {str(e)}")
            return []
