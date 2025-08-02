#!/usr/bin/env python3
"""
Legacy Sports Digest Runner

This file is kept for backward compatibility.
For new usage, please use: python main.py sports
"""

import json
from pathlib import Path
from src.digests.sports_digest import SportsDigest


def main():
    """Run the sports digest using the new modular structure."""
    print("Running legacy sports digest...")
    print("Note: Consider using 'python main.py sports' for the new interface")

    # Load sports configuration
    config_path = Path(__file__).parent / 'config' / 'sports_config.json'

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Create and run the sports digest
        digest = SportsDigest(config)
        digest.run()

    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        print("Please ensure config/sports_config.json exists")
    except Exception as e:
        print(f"Error running sports digest: {e}")


if __name__ == "__main__":
    main()
