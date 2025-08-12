"""
Social Media Outreach Module - Handles automated interactions on X (Twitter) and Instagram.
"""

import os
import time
import random
import logging
import string
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import tweepy
from instagrapi import Client as InstagrapiClient

from config import TwitterConfig, InstagramConfig, OutreachConfig, CalendlyConfig
from modules.google_sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)

class TwitterOutreach:
    """
    Handles automated interactions on Twitter/X.
    """

    def __init__(self,
                 api_key: str = None,
                 api_secret: str = None,
                 access_token: str = None,
                 access_token_secret: str = None,
                 bearer_token: str = None):
        """
        Initialize with Twitter API credentials.

        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
            bearer_token: Twitter bearer token
        """
        self.api_key = api_key or TwitterConfig.API_KEY
        self.api_secret = api_secret or TwitterConfig.API_SECRET
        self.access_token = access_token or TwitterConfig.ACCESS_TOKEN
        self.access_token_secret = access_token_secret or TwitterConfig.ACCESS_TOKEN_SECRET
        self.bearer_token = bearer_token or TwitterConfig.BEARER_TOKEN

        if not (self.api_key and self.api_secret and self.access_token and self.access_token_secret):
            raise ValueError("Twitter API credentials are incomplete")

        self.api = None
        self.client = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Twitter API."""
        try:
            # V1 Authentication for follow functionality
            auth = tweepy.OAuth1UserHandler(
                self.api_key, self.api_secret,
                self.access_token, self.access_token_secret
            )
            self.api = tweepy.API(auth)

            # V2 Authentication for dm functionality
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )

            logger.info("Successfully authenticated with Twitter API")
        except Exception as e:
            logger.error(f"Error authenticating with Twitter API: {str(e)}")
            raise

    def follow_user(self, username: str) -> bool:
        """
        Follow a user by username.

        Args:
            username: Twitter username (without @)

        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.api.get_user(screen_name=username)
            self.api.create_friendship(user_id=user.id)
            logger.info(f"Successfully followed Twitter user: @{username}")
            return True
        except tweepy.errors.TweepyException as e:
            if "You are unable to follow more people at this time" in str(e):
                logger.warning(f"Follow limit reached for Twitter. Try again later.")
            elif "You've already requested to follow" in str(e):
                logger.info(f"Already requested to follow @{username}")
                return True
            elif "You are blocking" in str(e) or "blocked you" in str(e):
                logger.warning(f"Cannot follow @{username} due to block")
            else:
                logger.error(f"Error following Twitter user @{username}: {str(e)}")
            return False

    def send_dm(self, username: str, message: str) -> bool:
        """
        Send a direct message to a user.

        Args:
            username: Twitter username (without @)
            message: Message content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user ID
            user = self.api.get_user(screen_name=username)
            user_id = user.id

            # Create DM
            self.client.create_direct_message(participant_id=user_id, text=message)

            logger.info(f"Successfully sent DM to Twitter user: @{username}")
            return True
        except tweepy.errors.TweepyException as e:
            if "You cannot send messages to this user" in str(e):
                logger.warning(f"Cannot send DM to @{username}: Not following you or DMs closed")
            else:
                logger.error(f"Error sending DM to Twitter user @{username}: {str(e)}")
            return False

    def check_for_replies(self, username: str, since_id: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check if a user has replied to your messages.

        Args:
            username: Twitter username (without @)
            since_id: Optional ID to check for messages since

        Returns:
            Tuple of (has_replied, replies)
        """
        try:
            # Get the authenticated user's ID
            me = self.api.verify_credentials()
            me_id = me.id

            # Get user ID
            user = self.api.get_user(screen_name=username)
            user_id = user.id

            # Search for mentions from this user
            mentions = self.api.get_mentions_timeline(since_id=since_id)

            # Filter mentions from the specified user
            replies_from_user = [
                {
                    "id": mention.id,
                    "text": mention.text,
                    "created_at": mention.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                for mention in mentions
                if mention.user.id == user_id
            ]

            return bool(replies_from_user), replies_from_user
        except tweepy.errors.TweepyException as e:
            logger.error(f"Error checking replies from Twitter user @{username}: {str(e)}")
            return False, []

class InstagramOutreach:
    """
    Handles automated interactions on Instagram.
    """

    def __init__(self, username: str = None, password: str = None):
        """
        Initialize with Instagram credentials.

        Args:
            username: Instagram username
            password: Instagram password
        """
        self.username = username or InstagramConfig.USERNAME
        self.password = password or InstagramConfig.PASSWORD

        if not (self.username and self.password):
            raise ValueError("Instagram credentials are incomplete")

        self.client = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Instagram."""
        try:
            # Create client
            self.client = InstagrapiClient()

            # Attempt to load session
            session_file = f"credentials/instagram_session_{self.username}.json"
            if os.path.exists(session_file):
                try:
                    self.client.load_settings(session_file)
                    self.client.get_timeline_feed()  # Test if the session is valid
                    logger.info(f"Loaded existing Instagram session for {self.username}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to use existing Instagram session: {str(e)}")

            # Login
            self.client.login(self.username, self.password)

            # Save session
            os.makedirs("credentials", exist_ok=True)
            self.client.dump_settings(session_file)

            logger.info(f"Successfully authenticated with Instagram as {self.username}")
        except Exception as e:
            logger.error(f"Error authenticating with Instagram: {str(e)}")
            raise

    def follow_user(self, username: str) -> bool:
        """
        Follow a user by username.

        Args:
            username: Instagram username

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user ID
            user_id = self.client.user_id_from_username(username)

            # Follow user
            result = self.client.user_follow(user_id)

            if result:
                logger.info(f"Successfully followed Instagram user: @{username}")
                return True
            else:
                logger.warning(f"Failed to follow Instagram user: @{username}")
                return False
        except Exception as e:
            if "User not found" in str(e):
                logger.warning(f"Instagram user not found: @{username}")
            elif "Please wait a few minutes" in str(e):
                logger.warning(f"Follow limit reached for Instagram. Try again later.")
            else:
                logger.error(f"Error following Instagram user @{username}: {str(e)}")
            return False

    def send_dm(self, username: str, message: str) -> bool:
        """
        Send a direct message to a user.

        Args:
            username: Instagram username
            message: Message content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user ID
            user_id = self.client.user_id_from_username(username)

            # Get or create thread
            threads = self.client.direct_threads()
            thread_id = None

            for thread in threads:
                if len(thread.users) == 1 and thread.users[0].pk == user_id:
                    thread_id = thread.id
                    break

            # Send message
            if thread_id:
                result = self.client.direct_send(message, thread_ids=[thread_id])
            else:
                result = self.client.direct_send(message, user_ids=[user_id])

            if result:
                logger.info(f"Successfully sent DM to Instagram user: @{username}")
                return True
            else:
                logger.warning(f"Failed to send DM to Instagram user: @{username}")
                return False
        except Exception as e:
            if "User not found" in str(e):
                logger.warning(f"Instagram user not found: @{username}")
            elif "Blocked from sending messages" in str(e):
                logger.warning(f"Blocked from sending messages to @{username}")
            else:
                logger.error(f"Error sending DM to Instagram user @{username}: {str(e)}")
            return False

    def check_for_replies(self, username: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check if a user has replied to your messages.

        Args:
            username: Instagram username

        Returns:
            Tuple of (has_replied, replies)
        """
        try:
            # Get user ID
            user_id = self.client.user_id_from_username(username)

            # Get threads
            threads = self.client.direct_threads()

            # Find thread with this user
            thread_with_user = None
            for thread in threads:
                if len(thread.users) == 1 and thread.users[0].pk == user_id:
                    thread_with_user = thread
                    break

            if not thread_with_user:
                return False, []

            # Get messages from the thread
            messages = self.client.direct_messages(thread_with_user.id)

            # Filter messages from the user
            replies_from_user = [
                {
                    "id": message.id,
                    "text": message.text,
                    "created_at": datetime.fromtimestamp(message.timestamp / 1000000).strftime("%Y-%m-%d %H:%M:%S")
                }
                for message in messages
                if message.user_id == user_id
            ]

            return bool(replies_from_user), replies_from_user
        except Exception as e:
            logger.error(f"Error checking replies from Instagram user @{username}: {str(e)}")
            return False, []

class SocialOutreachManager:
    """
    Manages social media outreach across multiple platforms.
    """

    def __init__(self,
                 sheets_manager: Optional[GoogleSheetsManager] = None,
                 twitter_api: Optional[TwitterOutreach] = None,
                 instagram_api: Optional[InstagramOutreach] = None):
        """
        Initialize outreach manager.

        Args:
            sheets_manager: Google Sheets manager
            twitter_api: Twitter API wrapper
            instagram_api: Instagram API wrapper
        """
        self.sheets_manager = sheets_manager

        # Initialize APIs if not provided
        try:
            self.twitter_api = twitter_api or TwitterOutreach()
        except Exception as e:
            logger.error(f"Twitter API initialization failed: {str(e)}")
            self.twitter_api = None

        try:
            self.instagram_api = instagram_api or InstagramOutreach()
        except Exception as e:
            logger.error(f"Instagram API initialization failed: {str(e)}")
            self.instagram_api = None

    def personalize_message(self, template: str, lead: Dict[str, Any]) -> str:
        """
        Personalize a message template for a specific lead.

        Args:
            template: Message template with placeholders
            lead: Lead information

        Returns:
            Personalized message
        """
        # Basic info
        first_name = lead.get("first_name", "").strip() or lead.get("name", "").split()[0] if lead.get("name") else ""
        industry = lead.get("industry", "").lower()
        target_type = lead.get("target_type", "").lower()
        company = lead.get("company", "")

        # Contextual variables
        business_type = company or industry or "business"

        # If target_type is empty, try to infer from title
        if not target_type and lead.get("title"):
            title = lead.get("title", "").lower()
            if "agency" in title:
                target_type = "digital agency owner"
            elif "saas" in title or "founder" in title or "ceo" in title:
                target_type = "saas founder"
            elif "coach" in title:
                target_type = "business coach"
            else:
                target_type = "business owner"

        # Industry context
        if "agency" in target_type:
            industry_context = f"running a {industry} agency"
        elif "saas" in target_type:
            industry_context = f"building a SaaS in the {industry} space"
        elif "coach" in target_type:
            industry_context = f"coaching clients in the {industry} industry"
        else:
            industry_context = f"working in the {industry} industry"

        # Format the message
        message = template.format(
            first_name=first_name,
            industry=industry,
            company=company,
            target_type=target_type,
            business_type=business_type,
            industry_context=industry_context,
            calendly_link=CalendlyConfig.MEETING_LINK
        )

        return message.strip()

    def follow_lead(self, lead: Dict[str, Any], platform: str) -> bool:
        """
        Follow a lead on the specified platform.

        Args:
            lead: Lead information
            platform: 'x' or 'instagram'

        Returns:
            True if successful, False otherwise
        """
        if platform.lower() == "x":
            if not self.twitter_api:
                logger.error("Twitter API not initialized")
                return False

            username = lead.get("x_username")
            if not username:
                logger.warning(f"No X username for lead: {lead.get('name')}")
                return False

            return self.twitter_api.follow_user(username)

        elif platform.lower() == "instagram":
            if not self.instagram_api:
                logger.error("Instagram API not initialized")
                return False

            username = lead.get("instagram_username")
            if not username:
                logger.warning(f"No Instagram username for lead: {lead.get('name')}")
                return False

            return self.instagram_api.follow_user(username)

        else:
            logger.error(f"Unsupported platform: {platform}")
            return False

    def send_initial_dm(self, lead: Dict[str, Any], platform: str) -> bool:
        """
        Send an initial DM to a lead.

        Args:
            lead: Lead information
            platform: 'x' or 'instagram'

        Returns:
            True if successful, False otherwise
        """
        # Personalize message
        message = self.personalize_message(OutreachConfig.INITIAL_DM_TEMPLATE, lead)

        # Send on appropriate platform
        result = False

        if platform.lower() == "x":
            if not self.twitter_api:
                logger.error("Twitter API not initialized")
                return False

            username = lead.get("x_username")
            if not username:
                logger.warning(f"No X username for lead: {lead.get('name')}")
                return False

            result = self.twitter_api.send_dm(username, message)

        elif platform.lower() == "instagram":
            if not self.instagram_api:
                logger.error("Instagram API not initialized")
                return False

            username = lead.get("instagram_username")
            if not username:
                logger.warning(f"No Instagram username for lead: {lead.get('name')}")
                return False

            result = self.instagram_api.send_dm(username, message)

        else:
            logger.error(f"Unsupported platform: {platform}")
            return False

        # Record outreach in Google Sheets
        if result and self.sheets_manager:
            self.sheets_manager.record_outreach(
                lead_id=lead.get("id"),
                platform=platform,
                action="initial_dm",
                message=message
            )

        return result

    def send_follow_up(self, lead: Dict[str, Any], platform: str, follow_up_count: int) -> bool:
        """
        Send a follow-up message to a lead.

        Args:
            lead: Lead information
            platform: 'x' or 'instagram'
            follow_up_count: Number of follow-ups already sent

        Returns:
            True if successful, False otherwise
        """
        # Check if we've reached the max follow-ups
        if follow_up_count >= OutreachConfig.MAX_FOLLOW_UPS:
            logger.info(f"Reached max follow-ups for lead: {lead.get('name')}")
            return False

        # Get follow-up template
        if follow_up_count < len(OutreachConfig.FOLLOW_UP_TEMPLATES):
            template = OutreachConfig.FOLLOW_UP_TEMPLATES[follow_up_count]
        else:
            template = OutreachConfig.FOLLOW_UP_TEMPLATES[-1]

        # Personalize message
        message = self.personalize_message(template, lead)

        # Send on appropriate platform
        result = False

        if platform.lower() == "x":
            if not self.twitter_api:
                logger.error("Twitter API not initialized")
                return False

            username = lead.get("x_username")
            if not username:
                logger.warning(f"No X username for lead: {lead.get('name')}")
                return False

            result = self.twitter_api.send_dm(username, message)

        elif platform.lower() == "instagram":
            if not self.instagram_api:
                logger.error("Instagram API not initialized")
                return False

            username = lead.get("instagram_username")
            if not username:
                logger.warning(f"No Instagram username for lead: {lead.get('name')}")
                return False

            result = self.instagram_api.send_dm(username, message)

        else:
            logger.error(f"Unsupported platform: {platform}")
            return False

        # Record outreach in Google Sheets
        if result and self.sheets_manager:
            self.sheets_manager.record_outreach(
                lead_id=lead.get("id"),
                platform=platform,
                action="follow_up",
                message=message
            )

        return result

    def check_for_responses(self, lead: Dict[str, Any]) -> bool:
        """
        Check if a lead has responded on any platform.

        Args:
            lead: Lead information

        Returns:
            True if lead has responded, False otherwise
        """
        has_responded = False

        # Check Twitter
        if self.twitter_api and lead.get("x_username"):
            has_replied, replies = self.twitter_api.check_for_replies(lead.get("x_username"))
            if has_replied:
                has_responded = True
                logger.info(f"Lead {lead.get('name')} has replied on Twitter")

                if self.sheets_manager:
                    # Record response in outreach sheet
                    self.sheets_manager.record_outreach(
                        lead_id=lead.get("id"),
                        platform="x",
                        action="received_reply",
                        message=replies[0].get("text", "")
                    )

                    # Update lead status
                    self.sheets_manager.update_lead_status(lead.get("id"), "Engaged")

        # Check Instagram
        if not has_responded and self.instagram_api and lead.get("instagram_username"):
            has_replied, replies = self.instagram_api.check_for_replies(lead.get("instagram_username"))
            if has_replied:
                has_responded = True
                logger.info(f"Lead {lead.get('name')} has replied on Instagram")

                if self.sheets_manager:
                    # Record response in outreach sheet
                    self.sheets_manager.record_outreach(
                        lead_id=lead.get("id"),
                        platform="instagram",
                        action="received_reply",
                        message=replies[0].get("text", "")
                    )

                    # Update lead status
                    self.sheets_manager.update_lead_status(lead.get("id"), "Engaged")

        return has_responded

    def send_positive_response(self, lead: Dict[str, Any], platform: str) -> bool:
        """
        Send a response when a lead shows interest.

        Args:
            lead: Lead information
            platform: 'x' or 'instagram'

        Returns:
            True if successful, False otherwise
        """
        # Personalize message
        message = self.personalize_message(OutreachConfig.POSITIVE_RESPONSE_TEMPLATE, lead)

        # Send on appropriate platform
        result = False

        if platform.lower() == "x":
            if not self.twitter_api:
                logger.error("Twitter API not initialized")
                return False

            username = lead.get("x_username")
            if not username:
                logger.warning(f"No X username for lead: {lead.get('name')}")
                return False

            result = self.twitter_api.send_dm(username, message)

        elif platform.lower() == "instagram":
            if not self.instagram_api:
                logger.error("Instagram API not initialized")
                return False

            username = lead.get("instagram_username")
            if not username:
                logger.warning(f"No Instagram username for lead: {lead.get('name')}")
                return False

            result = self.instagram_api.send_dm(username, message)

        else:
            logger.error(f"Unsupported platform: {platform}")
            return False

        # Record outreach in Google Sheets
        if result and self.sheets_manager:
            self.sheets_manager.record_outreach(
                lead_id=lead.get("id"),
                platform=platform,
                action="positive_response",
                message=message
            )

            # Update lead status
            self.sheets_manager.update_lead_status(lead.get("id"), "Opportunity")

        return result

    def execute_daily_outreach(self, limit_follows: int = None, limit_dms: int = None):
        """
        Execute the daily outreach workflow.

        Args:
            limit_follows: Maximum follows to perform
            limit_dms: Maximum DMs to send
        """
        if not limit_follows:
            limit_follows = OutreachConfig.MAX_DAILY_FOLLOWS

        if not limit_dms:
            limit_dms = OutreachConfig.MAX_DAILY_DMS

        if not self.sheets_manager:
            logger.error("Google Sheets manager not initialized")
            return

        # Count follows and DMs
        follows_count = 0
        dms_count = 0

        # Get leads for follow-up
        follow_up_leads = self.sheets_manager.get_leads_for_follow_up(
            days_since_last_contact=OutreachConfig.FOLLOW_UP_DAYS,
            max_follow_ups=OutreachConfig.MAX_FOLLOW_UPS
        )

        # Process follow-ups first
        for lead in follow_up_leads:
            # Check if lead has responded
            if self.check_for_responses(lead):
                # If responded, send the next stage message
                if lead.get("x_username"):
                    self.send_positive_response(lead, "x")
                elif lead.get("instagram_username"):
                    self.send_positive_response(lead, "instagram")
                continue

            # Send follow-up if needed
            follow_up_count = lead.get("follow_up_count", 0)

            if lead.get("x_username"):
                if self.send_follow_up(lead, "x", follow_up_count):
                    dms_count += 1
            elif lead.get("instagram_username"):
                if self.send_follow_up(lead, "instagram", follow_up_count):
                    dms_count += 1

            # Check DM limit
            if dms_count >= limit_dms:
                logger.info(f"Reached daily DM limit: {limit_dms}")
                break

            # Add delay
            time.sleep(OutreachConfig.DM_DELAY)

        # Get new leads if we haven't reached the DM limit
        if dms_count < limit_dms:
            # Get all leads
            all_leads = self.sheets_manager.get_leads(filters={"Status": "New"})

            # Process new leads
            for lead in all_leads:
                # Add lead ID if missing
                if "id" not in lead:
                    continue

                # Process X leads
                if lead.get("x_username") and follows_count < limit_follows:
                    # Follow user
                    if self.follow_lead(lead, "x"):
                        follows_count += 1

                        # Wait before sending DM
                        time.sleep(OutreachConfig.FOLLOW_DELAY)

                        # Send initial DM if we haven't reached the limit
                        if dms_count < limit_dms:
                            if self.send_initial_dm(lead, "x"):
                                dms_count += 1
                                # Update lead status
                                self.sheets_manager.update_lead_status(lead.get("id"), "Contacted")

                            # Wait before processing next lead
                            time.sleep(OutreachConfig.DM_DELAY)

                # Process Instagram leads
                elif lead.get("instagram_username") and follows_count < limit_follows:
                    # Follow user
                    if self.follow_lead(lead, "instagram"):
                        follows_count += 1

                        # Wait before sending DM
                        time.sleep(OutreachConfig.FOLLOW_DELAY)

                        # Send initial DM if we haven't reached the limit
                        if dms_count < limit_dms:
                            if self.send_initial_dm(lead, "instagram"):
                                dms_count += 1
                                # Update lead status
                                self.sheets_manager.update_lead_status(lead.get("id"), "Contacted")

                            # Wait before processing next lead
                            time.sleep(OutreachConfig.DM_DELAY)

                # Check if we've reached both limits
                if follows_count >= limit_follows and dms_count >= limit_dms:
                    logger.info(f"Reached daily limits: {follows_count} follows, {dms_count} DMs")
                    break

        logger.info(f"Daily outreach completed: {follows_count} follows, {dms_count} DMs")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/social_outreach.log"),
            logging.StreamHandler()
        ]
    )

    # Create dummy data directory for logs
    os.makedirs("logs", exist_ok=True)

    try:
        # Twitter API for testing
        twitter_api = TwitterOutreach()
        logger.info("Twitter API initialized successfully")
    except Exception as e:
        logger.error(f"Twitter API initialization failed: {str(e)}")
        twitter_api = None

    try:
        # Instagram API for testing
        instagram_api = InstagramOutreach()
        logger.info("Instagram API initialized successfully")
    except Exception as e:
        logger.error(f"Instagram API initialization failed: {str(e)}")
        instagram_api = None

    # Test outreach manager
    outreach_manager = SocialOutreachManager(
        twitter_api=twitter_api,
        instagram_api=instagram_api
    )

    # Test message personalization
    test_lead = {
        "name": "John Doe",
        "first_name": "John",
        "company": "Acme Inc",
        "industry": "Marketing",
        "target_type": "digital agency owner"
    }

    personalized_message = outreach_manager.personalize_message(
        OutreachConfig.INITIAL_DM_TEMPLATE,
        test_lead
    )

    print(f"Sample personalized message:\n{personalized_message}")
