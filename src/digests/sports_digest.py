from src.base_digest import BaseDigest
from typing import Dict


class SportsDigest(BaseDigest):
    """Sports-specific news digest."""

    def get_digest_emoji(self) -> str:
        """Return the emoji to use in Discord messages."""
        return "🏆"

    def get_curation_prompt(self, articles_text: str) -> str:
        """Generate the AI prompt for sports article curation."""
        return f"""
        You are a sports news curator. Below are sports articles from the last 24 hours.

        {self.preferences}

        Please:
        1. Select the {self.max_articles} most relevant and interesting articles based on my preferences and general newsworthiness
        2. Ensure variety across different sports (don't pick {self.max_articles} articles from the same sport)
        3. Summarize each selected article in 2-3 sentences

        Return ONLY a valid JSON object in this exact format, as plain text (not in code blocks or markdown):
        {{
            "articles": [
                {{
                    "category": "Formula 1",
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
