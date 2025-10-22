# GitHub Actions Setup Guide

This guide will help you set up your Political News Digest system as a GitHub Action.

## Step 1: Push to GitHub

If you haven't already, push this repository to GitHub:

```bash
git init
git add .
git commit -m "Initial commit: Political news digest system with GitHub Actions"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/news-digest.git
git push -u origin main
```

## Step 2: Create Discord Webhooks

Create a Discord webhook for each political digest:

1. Go to your Discord server
2. Click on Server Settings (⚙️) → Integrations → Webhooks
3. Click "New Webhook"
4. Give it a name (e.g., "Belgium Politics Digest Bot")
5. Select the channel where you want the digest posted
6. Copy the webhook URL
7. Repeat for the world politics digest (can be same or different channel)

## Step 3: Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

## Step 4: Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click on **Settings** (top right)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the following secrets one by one:

   | Name | Value |
   |------|-------|
   | `GEMINI_API_KEY` | Your Google Gemini API key |
   | `BE_POLITICS_DISCORD_WEBHOOK_URL` | Your Belgium politics Discord webhook URL |
   | `WORLD_NEWS_DISCORD_WEBHOOK_URL` | Your world politics Discord webhook URL |

## Step 5: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. You should see the "Daily Political News Digest" workflow

## Step 6: Test the Workflow

Before waiting for the scheduled run, test the workflow manually:

1. Go to the **Actions** tab
2. Click on **Daily Political News Digest** workflow (left sidebar)
3. Click **Run workflow** (right side)
4. Select which digest to run (or "all" to test both)
5. Click **Run workflow**
6. Wait for the workflow to complete
7. Check your Discord channel for the digest

## Step 7: Customize (Optional)

### Change Schedule Times

Edit `.github/workflows/daily-digest.yml` to change when each digest runs.

The current schedule is:
- Belgium Politics: 7:00 AM UTC
- World Politics: 7:30 AM UTC

### Customize RSS Feeds and Preferences

Edit the JSON files in the `config/` directory:
- `config/belgium_politics_config.json`
- `config/world_politics_config.json`

You can:
- Add or remove RSS feeds
- Change the number of articles (`max_articles`)
- Customize AI curation preferences
- Change Discord embed colors

### Disable Specific Digests

If you only want one digest to run:

1. Go to `.github/workflows/daily-digest.yml`
2. Comment out or delete the corresponding job section
3. Commit and push the changes

## Troubleshooting

### Workflow fails immediately
- Check that all required secrets are set correctly
- Make sure the secret names match exactly (they are case-sensitive)

### No articles are posted
- Check the workflow logs in the Actions tab
- The digest might be filtering out all articles based on preferences
- RSS feeds might be temporarily unavailable

### Discord webhook errors
- Verify your webhook URL is correct
- Check that the webhook hasn't been deleted in Discord
- Make sure the bot has permissions to post in the channel

## Monitoring

- GitHub Actions will email you if a workflow fails
- You can view all workflow runs in the Actions tab
- Each run shows detailed logs for debugging

## Cost

- GitHub Actions is **free** for public repositories
- Private repositories get 2,000 minutes/month for free
- Each digest run takes approximately 1-2 minutes
- Running 2 digests daily = ~120 minutes/month (well within free tier)

## Support

If you encounter issues:
1. Check the workflow logs in the Actions tab
2. Review the error messages
3. Verify all secrets are set correctly
4. Test running locally first with `python main.py belgium_politics` or `python main.py world_politics`
