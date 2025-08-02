#!/usr/bin/env python3
"""
Generic News Digest Runner

This script can run different types of news digests (sports, finance, etc.)
Each digest type has its own configuration file and Discord webhook.

Usage:
    python main.py <digest_type>

Example:
    python main.py sports
    python main.py finance

Environment Variables Required:
- GEMINI_API_KEY: Your Google Gemini API key
- <DIGEST_TYPE>_DISCORD_WEBHOOK_URL: Discord webhook URL for each digest type
  (e.g., SPORTS_DISCORD_WEBHOOK_URL, FINANCE_DISCORD_WEBHOOK_URL)
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Type
from src.base_digest import BaseDigest
from src.digests.sports_digest import SportsDigest
from src.digests.finance_digest import FinanceDigest


# Registry of available digest types
DIGEST_REGISTRY: Dict[str, Type[BaseDigest]] = {
    'sports': SportsDigest,
    'finance': FinanceDigest,
}


def load_config(digest_type: str) -> Dict:
    """
    Load configuration for the specified digest type.

    Args:
        digest_type: The type of digest (e.g., 'sports', 'finance')

    Returns:
        Dictionary containing the configuration

    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the config file is not valid JSON
    """
    config_path = Path(__file__).parent / 'config' / f'{digest_type}_config.json'

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main entry point for the news digest runner."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <digest_type>")
        print(f"Available digest types: {', '.join(DIGEST_REGISTRY.keys())}")
        sys.exit(1)

    digest_type = sys.argv[1].lower()

    if digest_type not in DIGEST_REGISTRY:
        print(f"Unknown digest type: {digest_type}")
        print(f"Available digest types: {', '.join(DIGEST_REGISTRY.keys())}")
        sys.exit(1)

    try:
        # Load configuration
        config = load_config(digest_type)
        print(f"Loaded configuration for {digest_type} digest")

        # Create and run the digest
        digest_class = DIGEST_REGISTRY[digest_type]
        digest = digest_class(config)
        digest.run()

    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Environment variable error: {e}")
        print("\nRequired environment variables:")
        print("- GEMINI_API_KEY")
        if digest_type in DIGEST_REGISTRY:
            config = load_config(digest_type)
            webhook_env = config.get('discord_webhook_env', f'{digest_type.upper()}_DISCORD_WEBHOOK_URL')
            print(f"- {webhook_env}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running {digest_type} digest: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
