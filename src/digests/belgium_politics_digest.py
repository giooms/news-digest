from src.base_digest import BaseDigest
from typing import Dict


class BelgiumPoliticsDigest(BaseDigest):
    """Belgium politics news digest."""

    def get_digest_emoji(self) -> str:
        """Return the emoji to use in Discord messages."""
        return "🇧🇪"

    def get_curation_prompt(self, articles_text: str) -> str:
        """Generate the AI prompt for Belgium politics article curation."""
        return f"""
        You are a Belgian politics news curator. Below are political articles from the last 24 hours focusing on Belgium.

        {self.preferences}

        Please:
        1. Select the {self.max_articles} most relevant and interesting articles based on my preferences and general political newsworthiness
        2. Ensure variety across different political topics (government, parties, policies, social issues, etc.)
        3. Summarize each selected article in 2-3 sentences
        4. Focus on impactful political developments and policy changes

        IMPORTANT: Use only standard ASCII quotes (") and apostrophes (') in your response. Avoid smart quotes, curly quotes, or any special Unicode characters.

        Return ONLY a valid JSON object in this exact format, as plain text (not in code blocks or markdown):
        {{
            "articles": [
                {{
                    "category": "Government Policy",
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
