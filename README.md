# News Digest System

A modular news digest system that can handle multiple types of news categories (sports, finance, etc.) and send curated summaries to different Discord channels.

## Features

- **Modular Architecture**: Easy to add new digest types
- **AI-Powered Curation**: Uses Google Gemini to rank and summarize articles
- **Multiple Discord Channels**: Each digest type can use its own Discord webhook
- **Configurable**: Each digest type has its own configuration file
- **RSS Feed Support**: Fetches articles from multiple RSS feeds
- **24-Hour Filtering**: Only processes articles from the last 24 hours

## Setup

### Prerequisites

1. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Discord Webhooks**: Create Discord webhooks for each digest type you want to use

### Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# Required for all digest types
GEMINI_API_KEY=your_gemini_api_key_here

# Discord webhooks for each digest type
SPORTS_DISCORD_WEBHOOK_URL=your_sports_discord_webhook_url
FINANCE_DISCORD_WEBHOOK_URL=your_finance_discord_webhook_url
```

### Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running Digest Types

Use the main entry point to run different digest types:

```bash
# Run sports digest
python main.py sports

# Run finance digest
python main.py finance
```

### Legacy Support

The original `sports_digest.py` is still available for backward compatibility:

```bash
python sports_digest.py
```

## Configuration

Each digest type has its own configuration file in the `config/` directory:

- `config/sports_config.json` - Sports digest configuration
- `config/finance_config.json` - Finance digest configuration

### Configuration Format

```json
{
    "digest_type": "Sports",
    "max_articles": 10,
    "rss_feeds": [
        "https://example.com/rss1",
        "https://example.com/rss2"
    ],
    "preferences": "Your detailed preferences for article curation...",
    "discord_webhook_env": "SPORTS_DISCORD_WEBHOOK_URL",
    "embed_color": "0x00ff00"
}
```

## Adding New Digest Types

To add a new digest type (e.g., technology):

1. **Create a configuration file**: `config/technology_config.json`
2. **Create a digest class**: `src/digests/technology_digest.py`
3. **Implement required methods**:
   - `get_curation_prompt()`: AI prompt for article curation
   - `get_digest_emoji()`: Emoji for Discord messages
4. **Register the class**: Add it to `DIGEST_REGISTRY` in `main.py`
5. **Set environment variable**: `TECHNOLOGY_DISCORD_WEBHOOK_URL`

### Example New Digest Class

```python
from src.base_digest import BaseDigest

class TechnologyDigest(BaseDigest):
    def get_curation_prompt(self, articles_text: str) -> str:
        return f"""
        You are a technology news curator...
        {self.preferences}

        Articles to process:
        {articles_text}
        """

    def get_digest_emoji(self) -> str:
        return "💻"
```

## Project Structure

```
sports-digest/
├── main.py                     # Main entry point
├── sports_digest.py           # Legacy sports digest runner
├── requirements.txt           # Python dependencies
├── config/                    # Configuration files
│   ├── sports_config.json    # Sports digest config
│   └── finance_config.json   # Finance digest config
├── src/                       # Source code
│   ├── __init__.py
│   ├── base_digest.py        # Base digest class
│   └── digests/              # Digest implementations
│       ├── __init__.py
│       ├── sports_digest.py  # Sports digest class
│       └── finance_digest.py # Finance digest class
└── tests/                     # Test files
```

## Scheduling

You can schedule the digests to run automatically using cron (Linux/Mac) or Task Scheduler (Windows):

### Cron Example

```bash
# Run sports digest daily at 8 AM
0 8 * * * cd /path/to/sports-digest && python main.py sports

# Run finance digest daily at 9 AM
0 9 * * * cd /path/to/sports-digest && python main.py finance
```

### Windows Task Scheduler

Create separate scheduled tasks for each digest type, running:

```bash
python C:\path\to\sports-digest\main.py sports
python C:\path\to\sports-digest\main.py finance
```

## Discord Output

Each digest sends:

1. A header message with the digest type and article count
2. Individual embedded messages for each article with:
   - Category/sport type
   - Article title
   - AI-generated summary
   - Link to original article
   - Color-coded embeds (configurable per digest type)

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY environment variable is required"**
   - Make sure you've set the `GEMINI_API_KEY` environment variable

2. **"Configuration file not found"**
   - Ensure the config file exists in the `config/` directory
   - Check the file name matches the pattern: `<digest_type>_config.json`

3. **"Discord webhook environment variable is required"**
   - Set the appropriate Discord webhook URL environment variable
   - Variable name is specified in the config file's `discord_webhook_env` field

4. **No articles found**
   - Check if RSS feeds are accessible
   - Verify articles are from the last 24 hours
   - Check if the AI curation preferences are too restrictive

## License

MIT License
