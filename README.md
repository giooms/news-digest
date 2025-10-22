# Political News Digest System

A political news digest system that delivers AI-curated summaries of Belgium and international political news to Discord channels. Designed to run as a GitHub Action for automated daily political news digests.

## Features

- **AI-Powered Curation**: Uses Google Gemini to rank and summarize political articles
- **Multiple Focus Areas**: Separate digests for Belgium politics and world politics
- **Discord Integration**: Each digest uses its own Discord webhook
- **Configurable**: Customize RSS feeds and curation preferences
- **GitHub Actions**: Automated daily digests with scheduled workflows
- **Manual Triggers**: Run specific digests on-demand from GitHub UI

## Available Digest Types

- **Belgium Politics** (`belgium_politics`) - Belgian political news and developments 🇧🇪
- **World Politics** (`world_politics`) - International politics and world news 🌍

## Setup

### For GitHub Actions (Recommended)

1. **Fork or clone this repository** to your GitHub account

2. **Set up GitHub Secrets**:
   - Go to your repository on GitHub
   - Navigate to Settings > Secrets and variables > Actions
   - Add the following secrets:
     - `GEMINI_API_KEY` - Your Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
     - `BE_POLITICS_DISCORD_WEBHOOK_URL` - Discord webhook for Belgium politics digest
     - `WORLD_NEWS_DISCORD_WEBHOOK_URL` - Discord webhook for world politics digest

3. **Enable GitHub Actions**:
   - Go to the Actions tab in your repository
   - Enable workflows if prompted

4. **Customize schedules** (optional):
   - Edit `.github/workflows/daily-digest.yml` to change when each digest runs
   - Current schedule (UTC times):
     - Belgium Politics: 7:00 AM UTC
     - World Politics: 7:30 AM UTC

5. **Customize digest preferences**:
   - Edit the JSON files in the `config/` directory to customize RSS feeds and preferences for each digest type

### For Local Development

#### Prerequisites

1. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Discord Webhooks**: Create Discord webhooks for each digest type you want to use

#### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Then fill in your actual values:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
BE_POLITICS_DISCORD_WEBHOOK_URL=your_belgium_politics_discord_webhook_url
WORLD_NEWS_DISCORD_WEBHOOK_URL=your_world_news_discord_webhook_url
```

#### Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running with GitHub Actions

The workflows run automatically on schedule, but you can also trigger them manually:

1. Go to the **Actions** tab in your GitHub repository
2. Select **Daily News Digest** workflow
3. Click **Run workflow**
4. Choose which digest to run (or select "all" to run all digests)
5. Click **Run workflow**

### Running Locally

Use the main entry point to run different digest types:

```bash
# Run Belgium politics digest
python main.py belgium_politics

# Run world politics digest
python main.py world_politics
```

## Configuration

Each digest type has its own configuration file in the `config/` directory:

- `config/belgium_politics_config.json` - Belgium politics digest configuration
- `config/world_politics_config.json` - World politics digest configuration

### Configuration Format

```json
{
    "digest_type": "Sports",
    "max_articles": 15,
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

To add a new political digest type (e.g., EU politics):

1. **Create a configuration file**: `config/eu_politics_config.json`
2. **Create a digest class**: `src/digests/eu_politics_digest.py`
3. **Implement required methods**:
   - `get_curation_prompt()`: AI prompt for article curation
   - `get_digest_emoji()`: Emoji for Discord messages
4. **Register the class**: Add it to `DIGEST_REGISTRY` in `main.py`
5. **Set environment variable**: `EU_POLITICS_DISCORD_WEBHOOK_URL`
6. **Add to GitHub Actions**: Add a job in `.github/workflows/daily-digest.yml`

### Example New Digest Class

```python
from src.base_digest import BaseDigest

class EUPoliticsDigest(BaseDigest):
    def get_curation_prompt(self, articles_text: str) -> str:
        return f"""
        You are an EU politics news curator...
        {self.preferences}

        Articles to process:
        {articles_text}
        """

    def get_digest_emoji(self) -> str:
        return "🇪🇺"
```

## Project Structure

```
news-digest/
├── .github/
│   └── workflows/
│       └── daily-digest.yml      # GitHub Actions workflow
├── main.py                        # Main entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── config/                        # Configuration files
│   ├── belgium_politics_config.json
│   └── world_politics_config.json
└── src/                           # Source code
    ├── __init__.py
    ├── base_digest.py             # Base digest class
    └── digests/                   # Digest implementations
        ├── __init__.py
        ├── belgium_politics_digest.py
        └── world_politics_digest.py
```

## Scheduling

### With GitHub Actions (Recommended)

The GitHub Actions workflow automatically runs your digests on schedule. The current schedule is:

- **Belgium Politics**: Daily at 7:00 AM UTC
- **World Politics**: Daily at 7:30 AM UTC

To change the schedule, edit `.github/workflows/daily-digest.yml` and modify the cron expressions.

### With Cron (Linux/Mac)

You can also schedule the digests locally using cron:

```bash
# Run Belgium politics digest daily at 8 AM
0 8 * * * cd /path/to/news-digest && python main.py belgium_politics

# Run world politics digest daily at 9 AM
0 9 * * * cd /path/to/news-digest && python main.py world_politics
```

### With Windows Task Scheduler

Create separate scheduled tasks for each digest type:

```bash
python C:\path\to\news-digest\main.py belgium_politics
python C:\path\to\news-digest\main.py world_politics
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
   - Check if the AI curation preferences are too restrictive

## License

MIT License
