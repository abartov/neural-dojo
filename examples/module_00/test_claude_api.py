"""
Module 0: Test Claude API

Verifies that Claude API is configured and working.
"""
import os
import sys
from pathlib import Path

# Add project root to path to find .env
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables from project root
load_dotenv(project_root / ".env")


def test_claude_api():
    """Test Claude API with a simple call"""

    # Check API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("   Please add your API key to .env:")
        print("   ANTHROPIC_API_KEY=sk-ant-your-key-here")
        print(f"   Expected location: {project_root}/.env")
        return False

    print("✅ API key found")

    # Try to import anthropic
    try:
        from anthropic import Anthropic
    except ImportError:
        print("❌ anthropic package not installed")
        print("   Run: pip install anthropic")
        return False

    print("✅ anthropic package imported")

    # Make API call
    try:
        client = Anthropic(api_key=api_key)

        print("\n🤖 Making API call to Claude...")
        print("   (This will cost ~$0.001)")

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from Neural Dojo!' and nothing else."
                }
            ]
        )

        response_text = message.content[0].text
        print(f"\n📩 Claude says: {response_text}")

        # Check usage
        print(f"\n📊 Token usage:")
        print(f"   Input tokens: {message.usage.input_tokens}")
        print(f"   Output tokens: {message.usage.output_tokens}")

        return True

    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("\nCommon issues:")
        print("   - Check API key is correct (no extra spaces)")
        print("   - Verify API key hasn't expired")
        print("   - Check account has credits: https://console.anthropic.com/")
        return False


if __name__ == "__main__":
    print("🔍 Testing Claude API...\n")

    success = test_claude_api()

    if success:
        print("\n✅ Claude API working! You're ready to start Module 1.")
        sys.exit(0)
    else:
        print("\n❌ Claude API test failed. Check the errors above.")
        sys.exit(1)
