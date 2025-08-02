import os
import json
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import google.generativeai as genai

class SportsDigest:
    def __init__(self):
        # Validate API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

        if not self.discord_webhook_url:
            raise ValueError("DISCORD_WEBHOOK_URL environment variable is required")

        # Placeholder RSS feeds - replace with actual feeds
        self.rss_feeds = [
            "https://www.formula1.com/en/latest/all.xml",
            "https://www.espn.com/espn/rss/soccer/news",
            "https://cyclingnews.com/feeds/all",
            "https://www.tennis.com/rss",
            # Add your RSS feeds here
        ]

        self.preferences = """
        My sports preferences for ranking articles:

        Formula 1:
        - Priority teams: Ferrari, McLaren, RedBull, Mercedes
        - Priority drivers: Leclerc, Hamilton, Piastri, Verstappen, Norris, Russell, Antonelli

        Football:
        - Clubs: FC Barcelona, Standard de Liège, AC Milan, Chelsea FC, Belgium National Team
        - Competitions: UEFA Champion's League, Club World Cup, Country World Cup

        Cyclism:
        - Athletes: Van Aert, Evenepoel, Pogacar, Van der Poel
        - Competitions: Flemish Classics, Walloon Classics, Paris Roubaix, World Championships, Giro d'Italia, Tour de France, Vuelta a España, Olympics

        Tennis:
        - Only Grand Slam results or final-stage coverage
        """

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

        prompt = f"""
        You are a sports news curator. Below are sports articles from the last 24 hours.

        {self.preferences}

        Please:
        1. Select the 10 most relevant and interesting articles based on my preferences and general newsworthiness
        2. Ensure variety across different sports (don't pick 10 F1 articles)
        3. Summarize each selected article in 2-3 sentences

        Return ONLY a valid JSON object in this exact format, as plain text (not in code blocks or markdown):
        {{
            "articles": [
                {{
                    "sport_type": "Formula 1",
                    "title": "Article title",
                    "summary": "2-3 sentence summary of the article",
                    "link": "original article link"
                }}
            ]
        }}

        Articles to process:
        {articles_text}

        Return only the JSON, no other text.
        """

        try:
            response = self.model.generate_content(prompt)
            # Parse JSON response
            json_response = json.loads(response.text.strip())
            return json_response

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini: {str(e)}")
            print(f"Raw response: {response.text}")
            return {"articles": [], "error": f"Failed to parse JSON response: {str(e)}"}

        except Exception as e:
            print(f"Error processing with Gemini: {str(e)}")
            return {"articles": [], "error": f"Error processing articles: {str(e)}"}

    def format_digest_for_discord(self, gemini_response: Dict) -> str:
        """Format the structured response for Discord."""
        if "error" in gemini_response:
            return gemini_response["error"]

        articles = gemini_response.get("articles", [])
        if not articles:
            return "No relevant articles found based on your preferences."

        formatted_content = ""
        for article in articles:
            formatted_content += f"**[{article['sport_type']}]** {article['title']}\n"
            formatted_content += f"{article['summary']}\n"
            formatted_content += f"{article['link']}\n\n"

        return formatted_content.strip()

    def send_to_discord(self, articles: List[Dict]):
        """Send each article as a separate embedded message to Discord."""
        if not self.discord_webhook_url:
            print("Discord webhook URL not provided")
            return

        if not articles:
            # Send error message
            payload = {
                "content": "🏆 **Daily Sports Digest**\n\nNo relevant articles found based on your preferences."
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
            "content": f"🏆 **Daily Sports Digest** - {len(articles)} articles"
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
                "title": f"[{article['sport_type']}] {article['title']}",
                "description": article['summary'],
                "url": article['link'],
                "color": 0x00ff00  # Green color
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

    def run(self):
        """Main execution function."""
        print(f"Starting sports digest at {datetime.now()}")

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

        print("Sports digest completed successfully")

if __name__ == "__main__":
    digest = SportsDigest()
    digest.run()
