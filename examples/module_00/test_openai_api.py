"""
Module 0: Test OpenAI API (Optional)

Verifies that OpenAI API is configured (optional - you can use Claude only).
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


def test_openai_api():
    """Test OpenAI API with a simple call"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found - this is optional")
        print("   You can skip this if using Claude only")
        print("   To use OpenAI, add to .env:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        return True  # Not a failure

    print("✅ API key found")

    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not installed")
        print("   Run: pip install openai")
        return False

    print("✅ openai package imported")

    try:
        client = OpenAI(api_key=api_key)

        print("\n🤖 Making API call to OpenAI...")
        print("   (Using gpt-4o-mini, costs ~$0.001)")

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model for testing
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from Neural Dojo!' and nothing else."
                }
            ]
        )

        response_text = response.choices[0].message.content
        print(f"\n📩 GPT says: {response_text}")

        print(f"\n📊 Token usage:")
        print(f"   Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   Completion tokens: {response.usage.completion_tokens}")
        print(f"   Total tokens: {response.usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("\nCommon issues:")
        print("   - Check API key is correct")
        print("   - Verify account has credits: https://platform.openai.com/")
        return False


if __name__ == "__main__":
    print("🔍 Testing OpenAI API...\n")

    success = test_openai_api()

    if success:
        print("\n✅ OpenAI API working (or skipped)!")
        sys.exit(0)
    else:
        print("\n❌ OpenAI API test failed.")
        sys.exit(1)
