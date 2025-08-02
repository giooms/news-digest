import os
import sys
import getpass
from sports_digest import SportsDigest

def test_sports_digest():
    """Test script to manually run the sports digest with user-provided credentials."""

    print("🏆 Sports Digest Testing Script")
    print("=" * 40)

    # Get Gemini API key
    print("\nEnter your Gemini API key:")
    gemini_key = getpass.getpass("Gemini API Key: ").strip()

    if not gemini_key:
        print("❌ Gemini API key is required!")
        return

    # Get Discord webhook URL
    print("\nEnter your Discord webhook URL:")
    discord_url = input("Discord Webhook URL: ").strip()

    if not discord_url:
        print("❌ Discord webhook URL is required!")
        return

    # Confirm before proceeding
    print(f"\n📋 Configuration:")
    print(f"Gemini API Key: {'*' * (len(gemini_key) - 4) + gemini_key[-4:]}")
    print(f"Discord Webhook: {discord_url[:50]}{'...' if len(discord_url) > 50 else ''}")

    confirm = input("\nProceed with test? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("Test cancelled.")
        return

    # Set environment variables temporarily
    os.environ['GEMINI_API_KEY'] = gemini_key
    os.environ['DISCORD_WEBHOOK_URL'] = discord_url

    try:
        print("\n🚀 Starting sports digest test...")
        print("-" * 40)

        # Create and run digest
        digest = SportsDigest()
        digest.run()

        print("\n✅ Test completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up environment variables
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        if 'DISCORD_WEBHOOK_URL' in os.environ:
            del os.environ['DISCORD_WEBHOOK_URL']

if __name__ == "__main__":
    test_sports_digest()
