# Sports Digest

A daily sports news digest that automatically curates and summarizes relevant sports articles based on personal preferences.

## Setup

1. **Add RSS Feeds**: Edit the `rss_feeds` list in `sports_digest.py` with your preferred sports news RSS feeds.

2. **GitHub Secrets**: Add these secrets to your GitHub repository:
   - `GEMINI_API_KEY`: Your GEMINI API key
   - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL

3. **Discord Webhook**:
   - Go to your Discord server settings
   - Navigate to Integrations > Webhooks
   - Create a new webhook and copy the URL

## How it works

- Runs twice daily at 12PM and 8PM UTC+1
- Fetches articles from RSS feeds from the last 24 hours
- Uses Gemini to rank and select the 20 most relevant articles
- Summarizes each article in 2-3 sentences
- Sends the digest to Discord

## Manual Testing

You can manually trigger the workflow from the GitHub Actions tab or run locally:

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
export DISCORD_WEBHOOK_URL="your-webhook-url"
python sports_digest.py
```

## Customization

- Modify the `preferences` string in `sports_digest.py` to adjust content curation
- Add or remove RSS feeds in the `rss_feeds` list
- Adjust the schedule in `.github/workflows/sports_digest.yml`
