"""
Payment Processing Module - Handles payments through Stripe and Razorpay
based on customer location.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import json

import stripe
import razorpay

from config import PaymentConfig
from modules.google_sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)

class StripePaymentProcessor:
    """Handle payments through Stripe (primarily for U.S. customers)."""

    def __init__(self, api_key: str = None):
        """
        Initialize with Stripe API key.

        Args:
            api_key: Stripe secret API key
        """
        self.api_key = api_key or PaymentConfig.STRIPE_SECRET_KEY

        if not self.api_key:
            raise ValueError("Stripe API key is required")

        # Configure Stripe
        stripe.api_key = self.api_key

    def create_product(self, name: str, description: str) -> str:
        """
        Create a product in Stripe.

        Args:
            name: Product name
            description: Product description

        Returns:
            Stripe product ID
        """
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
                active=True
            )

            logger.info(f"Created Stripe product: {name} ({product.id})")
            return product.id
        except Exception as e:
            logger.error(f"Error creating Stripe product: {str(e)}")
            raise

    def create_price(self, product_id: str, unit_amount: int, currency: str = "usd") -> str:
        """
        Create a price for a product.

        Args:
            product_id: Stripe product ID
            unit_amount: Price in cents (e.g., $25.00 = 2500)
            currency: 3-letter currency code

        Returns:
            Stripe price ID
        """
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=unit_amount,
                currency=currency.lower(),
                recurring=None  # One-time payment
            )

            logger.info(f"Created Stripe price: {unit_amount/100} {currency.upper()} ({price.id})")
            return price.id
        except Exception as e:
            logger.error(f"Error creating Stripe price: {str(e)}")
            raise

    def create_payment_link(self, price_id: str, customer_email: Optional[str] = None) -> str:
        """
        Create a payment link for a price.

        Args:
            price_id: Stripe price ID
            customer_email: Optional customer email to prefill

        Returns:
            Payment link URL
        """
        try:
            # Configure payment link options
            link_params = {
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1
                    }
                ],
                "allow_promotion_codes": True,
                "billing_address_collection": "required"
            }

            # Add customer email if provided
            if customer_email:
                link_params["customer_email"] = customer_email

            # Create the payment link
            payment_link = stripe.PaymentLink.create(**link_params)

            logger.info(f"Created Stripe payment link: {payment_link.url}")
            return payment_link.url
        except Exception as e:
            logger.error(f"Error creating Stripe payment link: {str(e)}")
            raise

    def create_checkout_session(self,
                                price_id: str,
                                customer_email: Optional[str] = None,
                                success_url: str = "https://example.com/success",
                                cancel_url: str = "https://example.com/cancel") -> str:
        """
        Create a checkout session.

        Args:
            price_id: Stripe price ID
            customer_email: Optional customer email to prefill
            success_url: URL to redirect to after successful payment
            cancel_url: URL to redirect to if checkout is cancelled

        Returns:
            Checkout session URL
        """
        try:
            # Configure checkout session options
            session_params = {
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1
                    }
                ],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "payment_method_types": ["card", "us_bank_account"],
                "billing_address_collection": "required"
            }

            # Add customer email if provided
            if customer_email:
                session_params["customer_email"] = customer_email

            # Create the checkout session
            session = stripe.checkout.Session.create(**session_params)

            logger.info(f"Created Stripe checkout session: {session.id}")
            return session.url
        except Exception as e:
            logger.error(f"Error creating Stripe checkout session: {str(e)}")
            raise

    def check_payment_status(self, session_id: str) -> Dict[str, Any]:
        """
        Check the status of a payment.

        Args:
            session_id: Stripe checkout session ID

        Returns:
            Dictionary with payment status information
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            payment_status = {
                "id": session.id,
                "status": session.payment_status,
                "amount_total": session.amount_total / 100,  # Convert cents to dollars
                "currency": session.currency.upper(),
                "customer_email": session.customer_details.email if session.customer_details else None,
                "payment_intent": session.payment_intent
            }

            logger.info(f"Checked payment status for session {session_id}: {payment_status['status']}")
            return payment_status
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")
            return {"status": "error", "error": str(e)}

class RazorpayPaymentProcessor:
    """Handle payments through Razorpay (primarily for Indian customers)."""

    def __init__(self, key_id: str = None, key_secret: str = None):
        """
        Initialize with Razorpay credentials.

        Args:
            key_id: Razorpay key ID
            key_secret: Razorpay key secret
        """
        self.key_id = key_id or PaymentConfig.RAZORPAY_KEY_ID
        self.key_secret = key_secret or PaymentConfig.RAZORPAY_KEY_SECRET

        if not (self.key_id and self.key_secret):
            raise ValueError("Razorpay credentials are incomplete")

        # Configure Razorpay client
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_order(self, amount: int, currency: str = "INR", notes: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Create a payment order.

        Args:
            amount: Amount in paise (e.g., ₹100 = 10000)
            currency: Currency code
            notes: Additional notes for the order

        Returns:
            Order details
        """
        try:
            # Create order data
            data = {
                "amount": amount,
                "currency": currency,
                "receipt": f"receipt_{int(amount)}_{currency}",
                "partial_payment": False
            }

            # Add notes if provided
            if notes:
                data["notes"] = notes

            # Create the order
            order = self.client.order.create(data=data)

            logger.info(f"Created Razorpay order: {order['id']} for {amount/100} {currency}")
            return order
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            raise

    def generate_payment_link(self,
                              amount: int,
                              currency: str = "INR",
                              description: str = "AI Sales Automation Service",
                              customer_info: Dict[str, str] = None,
                              callback_url: str = None,
                              notes: Dict[str, str] = None) -> str:
        """
        Generate a payment link.

        Args:
            amount: Amount in paise (e.g., ₹100 = 10000)
            currency: Currency code
            description: Payment description
            customer_info: Customer details
            callback_url: URL to redirect after payment
            notes: Additional notes

        Returns:
            Payment link URL
        """
        try:
            # Configure payment link data
            data = {
                "amount": amount,
                "currency": currency,
                "accept_partial": False,
                "description": description,
                "expire_by": 0,  # Never expire
                "reference_id": f"ref_{int(amount)}_{currency}"
            }

            # Add customer info if provided
            if customer_info:
                data["customer"] = customer_info

            # Add callback URL if provided
            if callback_url:
                data["callback_url"] = callback_url
                data["callback_method"] = "get"

            # Add notes if provided
            if notes:
                data["notes"] = notes

            # Create the payment link
            payment_link = self.client.payment_link.create(data=data)

            logger.info(f"Created Razorpay payment link: {payment_link['id']}")
            return payment_link["short_url"]
        except Exception as e:
            logger.error(f"Error creating Razorpay payment link: {str(e)}")
            raise

    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Check the status of a payment.

        Args:
            payment_id: Razorpay payment ID

        Returns:
            Dictionary with payment status information
        """
        try:
            payment = self.client.payment.fetch(payment_id)

            payment_status = {
                "id": payment["id"],
                "status": payment["status"],
                "amount": payment["amount"] / 100,  # Convert paise to rupees
                "currency": payment["currency"],
                "email": payment.get("email"),
                "contact": payment.get("contact"),
                "method": payment.get("method"),
                "created_at": payment["created_at"]
            }

            logger.info(f"Checked payment status for payment {payment_id}: {payment_status['status']}")
            return payment_status
        except Exception as e:
            logger.error(f"Error checking Razorpay payment status: {str(e)}")
            return {"status": "error", "error": str(e)}

class PaymentManager:
    """
    Manage payments through various payment processors based on customer location.
    """

    def __init__(self,
                 sheets_manager: Optional[GoogleSheetsManager] = None,
                 stripe_processor: Optional[StripePaymentProcessor] = None,
                 razorpay_processor: Optional[RazorpayPaymentProcessor] = None):
        """
        Initialize payment manager.

        Args:
            sheets_manager: Google Sheets manager
            stripe_processor: Stripe payment processor
            razorpay_processor: Razorpay payment processor
        """
        self.sheets_manager = sheets_manager

        # Initialize payment processors if not provided
        try:
            self.stripe_processor = stripe_processor or StripePaymentProcessor()
        except Exception as e:
            logger.error(f"Stripe processor initialization failed: {str(e)}")
            self.stripe_processor = None

        try:
            self.razorpay_processor = razorpay_processor or RazorpayPaymentProcessor()
        except Exception as e:
            logger.error(f"Razorpay processor initialization failed: {str(e)}")
            self.razorpay_processor = None

        # Create product IDs for packages
        self.packages = self._setup_packages()

    def _setup_packages(self) -> Dict[str, Dict[str, Any]]:
        """
        Set up packages and pricing.

        Returns:
            Dictionary of package information
        """
        packages = {
            "basic": {
                "name": "Basic AI Sales Automation",
                "description": "AI-powered lead generation and outreach automation",
                "price_usd": 2500,  # $2,500
                "price_inr": 40000,  # ₹40,000
                "stripe_product_id": None,
                "stripe_price_id": None
            },
            "standard": {
                "name": "Standard AI Sales Automation",
                "description": "Complete AI sales automation with lead management and follow-ups",
                "price_usd": 3500,  # $3,500
                "price_inr": 80000,  # ₹80,000
                "stripe_product_id": None,
                "stripe_price_id": None
            },
            "premium": {
                "name": "Premium AI Sales Automation",
                "description": "Advanced AI sales automation with content generation and analytics",
                "price_usd": 5000,  # $5,000
                "price_inr": 150000,  # ₹150,000
                "stripe_product_id": None,
                "stripe_price_id": None
            }
        }

        # Create Stripe products and prices if Stripe is available
        if self.stripe_processor:
            try:
                for package_id, package in packages.items():
                    # Create product
                    product_id = self.stripe_processor.create_product(
                        name=package["name"],
                        description=package["description"]
                    )
                    packages[package_id]["stripe_product_id"] = product_id

                    # Create price
                    price_id = self.stripe_processor.create_price(
                        product_id=product_id,
                        unit_amount=package["price_usd"] * 100,  # Convert to cents
                        currency="usd"
                    )
                    packages[package_id]["stripe_price_id"] = price_id

                logger.info("Successfully set up Stripe products and prices")
            except Exception as e:
                logger.error(f"Error setting up Stripe products: {str(e)}")

        return packages

    def get_payment_processor_for_country(self, country: str) -> Tuple[str, Any]:
        """
        Get the appropriate payment processor for a country.

        Args:
            country: Country name

        Returns:
            Tuple of (processor_name, processor_instance)
        """
        country_lower = country.lower()

        # Check for India
        if "india" in country_lower:
            return "razorpay", self.razorpay_processor

        # Default to Stripe for other countries
        return "stripe", self.stripe_processor

    def get_price_for_package(self, package_id: str, country: str) -> Tuple[int, str]:
        """
        Get the price for a package based on the customer's country.

        Args:
            package_id: Package identifier
            country: Customer's country

        Returns:
            Tuple of (price, currency)
        """
        country_lower = country.lower()
        package = self.packages.get(package_id.lower())

        if not package:
            raise ValueError(f"Invalid package ID: {package_id}")

        # Check for India
        if "india" in country_lower:
            return package["price_inr"], "INR"

        # Default to USD for other countries
        return package["price_usd"], "USD"

    def create_payment_link(self,
                            lead_id: str,
                            package_id: str,
                            customer_name: str,
                            customer_email: str,
                            country: str,
                            note: str = None) -> str:
        """
        Create a payment link for a lead.

        Args:
            lead_id: Lead ID
            package_id: Package identifier
            customer_name: Customer's name
            customer_email: Customer's email
            country: Customer's country
            note: Optional note

        Returns:
            Payment link URL
        """
        # Get package
        package = self.packages.get(package_id.lower())
        if not package:
            raise ValueError(f"Invalid package ID: {package_id}")

        # Get appropriate processor and price
        processor_name, processor = self.get_payment_processor_for_country(country)
        price, currency = self.get_price_for_package(package_id, country)

        payment_link = None

        # Create payment link with appropriate processor
        if processor_name == "stripe" and processor:
            # Get Stripe price ID
            price_id = package["stripe_price_id"]
            if not price_id:
                raise ValueError(f"Stripe price ID not found for package: {package_id}")

            # Create payment link
            payment_link = processor.create_payment_link(
                price_id=price_id,
                customer_email=customer_email
            )

        elif processor_name == "razorpay" and processor:
            # Create customer info
            customer_info = {
                "name": customer_name,
                "email": customer_email,
                "contact": ""  # Phone would go here
            }

            # Create notes
            notes = {
                "lead_id": lead_id,
                "package": package_id
            }

            if note:
                notes["note"] = note

            # Create payment link
            payment_link = processor.generate_payment_link(
                amount=price * 100,  # Convert to paise/cents
                currency=currency,
                description=package["name"],
                customer_info=customer_info,
                notes=notes
            )

        else:
            raise ValueError(f"No payment processor available for {country}")

        # Record deal in Google Sheets
        if payment_link and self.sheets_manager:
            self.sheets_manager.record_deal(
                lead_id=lead_id,
                package=package["name"],
                price=price,
                currency=currency,
                payment_method=processor_name
            )

        return payment_link

    def get_payment_options(self, country: str) -> List[str]:
        """
        Get available payment methods for a country.

        Args:
            country: Country name

        Returns:
            List of payment method names
        """
        country_lower = country.lower()

        # Check for India
        if "india" in country_lower:
            return ["upi", "netbanking", "credit_card", "debit_card", "wallet"]

        # Default payment methods for other countries
        return ["credit_card", "debit_card", "paypal"]

    def check_payment_status(self, payment_id: str, processor_name: str) -> Dict[str, Any]:
        """
        Check the status of a payment.

        Args:
            payment_id: Payment ID
            processor_name: Name of the processor used for this payment

        Returns:
            Dictionary with payment status information
        """
        if processor_name.lower() == "stripe" and self.stripe_processor:
            return self.stripe_processor.check_payment_status(payment_id)

        elif processor_name.lower() == "razorpay" and self.razorpay_processor:
            return self.razorpay_processor.check_payment_status(payment_id)

        else:
            error_msg = f"Invalid payment processor: {processor_name}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

    def update_payment_status(self, lead_id: str, status: str) -> bool:
        """
        Update payment status in Google Sheets.

        Args:
            lead_id: Lead ID
            status: Payment status

        Returns:
            True if successful, False otherwise
        """
        if not self.sheets_manager:
            logger.error("Google Sheets manager not initialized")
            return False

        return self.sheets_manager.update_deal_status(lead_id, status)

# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/payment_processing.log"),
            logging.StreamHandler()
        ]
    )

    # Create dummy data directory for logs
    os.makedirs("logs", exist_ok=True)

    try:
        # Initialize payment manager
        payment_manager = PaymentManager()

        # Test getting payment options
        us_options = payment_manager.get_payment_options("United States")
        india_options = payment_manager.get_payment_options("India")

        print(f"US payment options: {us_options}")
        print(f"India payment options: {india_options}")

        # Test getting prices
        us_price, us_currency = payment_manager.get_price_for_package("standard", "United States")
        india_price, india_currency = payment_manager.get_price_for_package("standard", "India")

        print(f"US price: {us_price} {us_currency}")
        print(f"India price: {india_price} {india_currency}")

    except Exception as e:
        logger.error(f"Error in payment manager test: {str(e)}")
        print(f"Error: {str(e)}")
