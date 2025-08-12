"""
Content Generation Module - Handles automated content posting to build authority.
"""

import os
import time
import logging
import random
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

import tweepy
from instagrapi import Client as InstagrapiClient

from config import TwitterConfig, InstagramConfig, ContentConfig
from modules.social_outreach import TwitterOutreach, InstagramOutreach

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generate content for social media posts."""

    def __init__(self):
        """Initialize the content generator."""
        self.content_categories = ContentConfig.CONTENT_CATEGORIES
        self.content_templates = ContentConfig.CONTENT_TEMPLATES

    def pick_random_template(self, category: str) -> str:
        """
        Pick a random template from a category.

        Args:
            category: Content category

        Returns:
            Template string
        """
        templates = self.content_templates.get(category, [])
        if not templates:
            # Fallback to a generic template
            return "Check out how our AI sales automation can help grow your business. #AIautomation"

        return random.choice(templates)

    def personalize_template(self, template: str, **kwargs) -> str:
        """
        Personalize a content template.

        Args:
            template: Template string
            **kwargs: Variables to substitute

        Returns:
            Personalized content
        """
        try:
            personalized = template.format(**kwargs)
            return personalized
        except KeyError as e:
            logger.warning(f"Missing key in template: {e}")
            return template

    def generate_content(self, category: Optional[str] = None, **kwargs) -> Tuple[str, str]:
        """
        Generate content for a post.

        Args:
            category: Content category (random if not specified)
            **kwargs: Variables to substitute

        Returns:
            Tuple of (category, content)
        """
        # Pick a category if not specified
        if not category:
            category = random.choice(self.content_categories)

        # Get template
        template = self.pick_random_template(category)

        # Personalize template
        content = self.personalize_template(template, **kwargs)

        return category, content

    def generate_week_content(self, variables: Dict[str, Any] = None) -> Dict[str, List[str]]:
        """
        Generate content for a week.

        Args:
            variables: Variables to substitute in templates

        Returns:
            Dictionary mapping dates to content
        """
        if not variables:
            variables = {}

        # Default variables
        defaults = {
            "target_type": "agency",
            "industry": "marketing",
            "first_name": "our client",
            "location": "the US",
            "business_type": "agency"
        }

        # Merge with provided variables
        for key, value in defaults.items():
            if key not in variables:
                variables[key] = value

        # Generate content for each day
        content_plan = {}
        today = datetime.now()

        # Generate content for each category
        for i in range(7):
            day = today + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")

            # For variety, pick a different category each day
            category = self.content_categories[i % len(self.content_categories)]

            _, content = self.generate_content(category, **variables)
            content_plan[day_str] = content

        return content_plan

class SocialMediaPublisher:
    """Publish content to social media platforms."""

    def __init__(self,
                 twitter_api: Optional[TwitterOutreach] = None,
                 instagram_api: Optional[InstagramOutreach] = None):
        """
        Initialize with social media APIs.

        Args:
            twitter_api: Twitter API wrapper
            instagram_api: Instagram API wrapper
        """
        self.twitter_api = twitter_api
        self.instagram_api = instagram_api

        # Initialize APIs if not provided
        if not self.twitter_api:
            try:
                self.twitter_api = TwitterOutreach()
            except Exception as e:
                logger.error(f"Twitter API initialization failed: {str(e)}")
                self.twitter_api = None

        if not self.instagram_api:
            try:
                self.instagram_api = InstagramOutreach()
            except Exception as e:
                logger.error(f"Instagram API initialization failed: {str(e)}")
                self.instagram_api = None

        # Initialize the content generator
        self.content_generator = ContentGenerator()

    def post_to_twitter(self, content: str) -> bool:
        """
        Post content to Twitter/X.

        Args:
            content: Tweet content

        Returns:
            True if successful, False otherwise
        """
        if not self.twitter_api or not self.twitter_api.api:
            logger.error("Twitter API not initialized")
            return False

        try:
            # Post tweet
            tweet = self.twitter_api.api.update_status(content)
            logger.info(f"Posted to Twitter: {content[:50]}...")
            return True
        except tweepy.errors.TweepyException as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            return False

    def post_to_instagram(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Post content to Instagram.

        Args:
            content: Caption content
            image_path: Path to image file (required for Instagram)

        Returns:
            True if successful, False otherwise
        """
        if not self.instagram_api or not self.instagram_api.client:
            logger.error("Instagram API not initialized")
            return False

        if not image_path:
            # Use a default image if none provided
            default_images_dir = "assets/images"
            os.makedirs(default_images_dir, exist_ok=True)

            default_images = [f for f in os.listdir(default_images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

            if not default_images:
                logger.error("No default images found for Instagram post")
                return False

            image_path = os.path.join(default_images_dir, random.choice(default_images))

        try:
            # Post to Instagram
            media = self.instagram_api.client.photo_upload(
                image_path,
                caption=content
            )
            logger.info(f"Posted to Instagram: {content[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error posting to Instagram: {str(e)}")
            return False

    def publish_content(self, content: str, platforms: List[str] = None, image_path: Optional[str] = None) -> Dict[str, bool]:
        """
        Publish content to specified platforms.

        Args:
            content: Content to publish
            platforms: List of platforms to publish to ("x", "instagram")
            image_path: Path to image file (required for Instagram)

        Returns:
            Dictionary mapping platforms to success status
        """
        if not platforms:
            platforms = ["x", "instagram"]

        results = {}

        for platform in platforms:
            if platform.lower() == "x" or platform.lower() == "twitter":
                results["x"] = self.post_to_twitter(content)

            elif platform.lower() == "instagram":
                results["instagram"] = self.post_to_instagram(content, image_path)

        return results

    def generate_and_publish(self, category: Optional[str] = None, platforms: List[str] = None, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate and publish content.

        Args:
            category: Content category
            platforms: List of platforms to publish to
            image_path: Path to image file (for Instagram)

        Returns:
            Dictionary with results
        """
        # Generate content
        category, content = self.content_generator.generate_content(category)

        # Publish content
        publish_results = self.publish_content(content, platforms, image_path)

        return {
            "category": category,
            "content": content,
            "results": publish_results
        }

    def schedule_content(self, content_plan: Dict[str, str], platforms: List[str] = None, image_directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Schedule content for publishing.

        Note: This doesn't actually schedule via the APIs (most don't support it).
        Instead, it creates a schedule plan that can be executed by the main scheduler.

        Args:
            content_plan: Dictionary mapping dates to content
            platforms: List of platforms to publish to
            image_directory: Directory containing images for Instagram posts

        Returns:
            Dictionary with scheduled content
        """
        if not platforms:
            platforms = ["x", "instagram"]

        scheduled = {}

        for date_str, content in content_plan.items():
            image_path = None

            # If Instagram is included and we have an image directory, pick a random image
            if "instagram" in platforms and image_directory:
                images = [f for f in os.listdir(image_directory) if f.endswith(('.jpg', '.jpeg', '.png'))]
                if images:
                    image_path = os.path.join(image_directory, random.choice(images))

            scheduled[date_str] = {
                "content": content,
                "platforms": platforms,
                "image_path": image_path
            }

        # Save schedule to file
        os.makedirs("data/schedules", exist_ok=True)
        schedule_file = f"data/schedules/content_schedule_{datetime.now().strftime('%Y%m%d')}.json"

        with open(schedule_file, "w") as f:
            json.dump(scheduled, f, indent=2)

        logger.info(f"Scheduled {len(scheduled)} posts and saved to {schedule_file}")

        return scheduled

    def execute_todays_schedule(self) -> Dict[str, Any]:
        """
        Execute today's scheduled content.

        Returns:
            Dictionary with results
        """
        today = datetime.now().strftime("%Y-%m-%d")
        schedule_dir = "data/schedules"

        if not os.path.exists(schedule_dir):
            logger.warning(f"Schedule directory not found: {schedule_dir}")
            return {"error": "Schedule directory not found"}

        # Find the most recent schedule file
        schedule_files = [f for f in os.listdir(schedule_dir) if f.startswith("content_schedule_") and f.endswith(".json")]
        schedule_files.sort(reverse=True)  # Sort by filename (which includes date)

        if not schedule_files:
            logger.warning("No schedule files found")
            return {"error": "No schedule files found"}

        schedule_file = os.path.join(schedule_dir, schedule_files[0])

        try:
            with open(schedule_file, "r") as f:
                schedule = json.load(f)

            # Check if today is in the schedule
            if today not in schedule:
                logger.warning(f"No content scheduled for today ({today})")
                return {"error": "No content scheduled for today"}

            # Get today's schedule
            todays_schedule = schedule[today]

            # Publish content
            results = self.publish_content(
                content=todays_schedule["content"],
                platforms=todays_schedule.get("platforms", ["x", "instagram"]),
                image_path=todays_schedule.get("image_path")
            )

            return {
                "date": today,
                "content": todays_schedule["content"],
                "results": results
            }

        except Exception as e:
            logger.error(f"Error executing today's schedule: {str(e)}")
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/content_generation.log"),
            logging.StreamHandler()
        ]
    )

    # Create dummy data directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("assets/images", exist_ok=True)

    # Create example image for demonstration
    try:
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont

        # Create a simple image for demonstration
        img = Image.new('RGB', (1080, 1080), color=(53, 56, 57))
        d = ImageDraw.Draw(img)
        d.rectangle([(100, 100), (980, 980)], fill=(45, 45, 45), outline=(200, 200, 200))
        d.text((540, 540), "AI Sales Automation", fill=(255, 255, 255), anchor="mm")

        img.save("assets/images/sample_post.jpg")
        logger.info("Created sample image for Instagram posts")
    except ImportError:
        logger.warning("PIL not installed, skipping sample image creation")

    # Test content generator
    content_generator = ContentGenerator()
    category, content = content_generator.generate_content(
        category="success_stories",
        target_type="digital agency owner",
        industry="marketing"
    )

    print(f"Generated {category} content: {content}")

    # Generate a week's worth of content
    content_plan = content_generator.generate_week_content()
    print("\nContent plan for the week:")
    for date, post in content_plan.items():
        print(f"{date}: {post}")

    # Test publisher if API credentials are available
    try:
        publisher = SocialMediaPublisher()

        # Schedule content
        schedule = publisher.schedule_content(
            content_plan,
            platforms=["x", "instagram"],
            image_directory="assets/images"
        )

        print(f"\nScheduled {len(schedule)} posts")

    except Exception as e:
        logger.error(f"Error in publisher test: {str(e)}")
        print(f"Error: {str(e)}")
