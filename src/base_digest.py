import os
import json
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from google import genai
from google.genai import types


class BaseDigest(ABC):
    """Base class for all news digest types."""

    def __init__(self, config: Dict):
        """
        Initialize the digest with configuration.

        Args:
            config: Dictionary containing digest configuration
        """
        # Validate API key - the new SDK will use GEMINI_API_KEY env var automatically
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # Create client using the new SDK
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.0-flash-exp'

        # Get Discord webhook URL from the environment variable specified in config
        discord_webhook_env = config.get('discord_webhook_env', 'DISCORD_WEBHOOK_URL')
        self.discord_webhook_url = os.getenv(discord_webhook_env)
        if not self.discord_webhook_url:
            raise ValueError(f"{discord_webhook_env} environment variable is required")

        self.config = config
        self.digest_type = config.get('digest_type', 'General')
        self.rss_feeds = config.get('rss_feeds', [])
        self.preferences = config.get('preferences', '')
        self.max_articles = config.get('max_articles', 15)

    def fetch_rss_articles(self) -> List[Dict]:
        """Fetch articles from all RSS feeds."""
        all_articles = []

        for feed_url in self.rss_feeds:
            try:
                print(f"Fetching from: {feed_url}")
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    # Filter articles from last 24 hours
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if datetime.now() - pub_date > timedelta(days=1):
                            continue

                    article = {
                        'title': entry.get('title', 'No title'),
                        'source': feed.feed.get('title', 'Unknown source'),
                        'link': entry.get('link', ''),
                        'description': entry.get('summary', entry.get('description', 'No description')),
                        'published': entry.get('published', 'Unknown date')
                    }
                    all_articles.append(article)

            except Exception as e:
                print(f"Error fetching from {feed_url}: {str(e)}")
                continue

        print(f"Total articles fetched: {len(all_articles)}")
        return all_articles

    @abstractmethod
    def get_curation_prompt(self, articles_text: str) -> str:
        """
        Generate the AI prompt for article curation.
        Must be implemented by subclasses.

        Args:
            articles_text: Formatted string of all articles

        Returns:
            Prompt string for the AI model
        """
        pass

    @abstractmethod
    def get_digest_emoji(self) -> str:
        """Return the emoji to use in Discord messages."""
        pass

    def process_with_gemini(self, articles: List[Dict]) -> Dict:
        """Send articles to Gemini for ranking and summarization."""
        if not articles:
            return {"articles": [], "error": "No articles found in the last 24 hours."}

        # Prepare articles data for Gemini
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"{i}. Source: {article['source']}\n"
            articles_text += f"Title: {article['title']}\n"
            articles_text += f"Description: {article['description'][:200]}...\n"
            articles_text += f"Link: {article['link']}\n\n"

        prompt = self.get_curation_prompt(articles_text)

        try:
            # Use the new SDK method
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            # Clean and parse JSON response
            cleaned_response = self._clean_json_response(response.text.strip())
            json_response = json.loads(cleaned_response)
            return json_response

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini: {str(e)}")
            print(f"Raw response: {response.text}")
            print(f"Cleaned response: {self._clean_json_response(response.text.strip())}")
            return {"articles": [], "error": f"Failed to parse JSON response: {str(e)}"}

        except Exception as e:
            print(f"Error processing with Gemini: {str(e)}")
            return {"articles": [], "error": f"Error processing articles: {str(e)}"}

    def send_to_discord(self, articles: List[Dict]):
        """Send each article as a separate embedded message to Discord."""
        if not self.discord_webhook_url:
            print("Discord webhook URL not provided")
            return

        digest_emoji = self.get_digest_emoji()

        if not articles:
            # Send error message
            payload = {
                "content": f"{digest_emoji} **Daily {self.digest_type} Digest**\n\nNo relevant articles found based on your preferences."
            }
            try:
                response = requests.post(self.discord_webhook_url, json=payload)
                response.raise_for_status()
                print("Successfully sent empty digest notification to Discord")
            except Exception as e:
                print(f"Error sending notification to Discord: {str(e)}")
            return

        # Send header message
        header_payload = {
            "content": f"{digest_emoji} **Daily {self.digest_type} Digest** - {len(articles)} articles"
        }
        try:
            response = requests.post(self.discord_webhook_url, json=header_payload)
            response.raise_for_status()
            print("Successfully sent header to Discord")
        except Exception as e:
            print(f"Error sending header to Discord: {str(e)}")

        # Send each article as separate embedded message
        for i, article in enumerate(articles, 1):
            embed = {
                "title": f"[{article.get('category', self.digest_type)}] {article['title']}",
                "description": article['summary'],
                "url": article['link'],
                "color": self.get_embed_color()
            }

            payload = {
                "embeds": [embed]
            }

            try:
                response = requests.post(self.discord_webhook_url, json=payload)
                response.raise_for_status()
                print(f"Successfully sent article {i}/{len(articles)} to Discord")

            except Exception as e:
                print(f"Error sending article {i} to Discord: {str(e)}")

    def get_embed_color(self) -> int:
        """Get the color for Discord embeds. Can be overridden by subclasses."""
        return int(self.config.get('embed_color', '0x00ff00'), 16)

    def _clean_json_response(self, response_text: str) -> str:
        """Clean the JSON response to handle problematic characters and markdown code blocks."""
        cleaned = response_text.strip()
        
        # Remove markdown code blocks if present
        if cleaned.startswith('```'):
            # Remove opening code block marker
            lines = cleaned.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]  # Remove first line (```json or ```)
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove last line (```)
            cleaned = '\n'.join(lines)
        
        # Replace ALL types of smart quotes and special characters with standard ones
        replacements = {
            # Single quotes
            "'": "'",  # Left single quotation mark
            "'": "'",  # Right single quotation mark
            "‚": "'",  # Single low-9 quotation mark
            "‛": "'",  # Single high-reversed-9 quotation mark
            "`": "'",  # Grave accent
            "´": "'",  # Acute accent
            # Double quotes
            """: '"',  # Left double quotation mark
            """: '"',  # Right double quotation mark
            "„": '"',  # Double low-9 quotation mark
            "‟": '"',  # Double high-reversed-9 quotation mark
            "«": '"',  # Left-pointing double angle quotation mark
            "»": '"',  # Right-pointing double angle quotation mark
            # Dashes
            "–": "-",  # En dash
            "—": "-",  # Em dash
            "−": "-",  # Minus sign
            # Other
            "…": "...",  # Horizontal ellipsis
        }

        for old_char, new_char in replacements.items():
            cleaned = cleaned.replace(old_char, new_char)

        return cleaned.strip()

    def run(self):
        """Main execution function."""
        print(f"Starting {self.digest_type.lower()} digest at {datetime.now()}")

        # Fetch articles
        articles = self.fetch_rss_articles()

        if not articles:
            print("No articles found, sending empty digest notification")
            self.send_to_discord([])
            return

        # Process with Gemini
        gemini_response = self.process_with_gemini(articles)

        # Handle errors
        if "error" in gemini_response:
            print(f"Error from Gemini: {gemini_response['error']}")
            self.send_to_discord([])
            return

        # Send articles directly to Discord
        processed_articles = gemini_response.get("articles", [])
        self.send_to_discord(processed_articles)

        print(f"{self.digest_type} digest completed successfully")
