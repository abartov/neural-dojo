"""
Module 0: Test Google Gemini API (Optional)

Verifies that Google Gemini API is configured (optional alternative to Claude/OpenAI).
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


def test_gemini_api():
    """Test Google Gemini API with a simple call"""

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found - this is optional")
        print("   You can skip this if using Claude or OpenAI")
        print("   To use Gemini, add to .env:")
        print("   GOOGLE_API_KEY=your-key-here")
        print("\n   Get your API key:")
        print("   https://aistudio.google.com/app/apikey")
        return True  # Not a failure

    print("✅ API key found")

    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Run: pip install google-generativeai")
        return False

    print("✅ google-generativeai package imported")

    try:
        genai.configure(api_key=api_key)

        print("\n🤖 Making API call to Google Gemini...")
        print("   (Using gemini-1.5-flash, free tier available)")

        model = genai.GenerativeModel('gemini-1.5-flash')

        response = model.generate_content(
            "Say 'Hello from Neural Dojo!' and nothing else.",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100,
            )
        )

        response_text = response.text
        print(f"\n📩 Gemini says: {response_text}")

        # Gemini API provides usage metadata
        if hasattr(response, 'usage_metadata'):
            print(f"\n📊 Token usage:")
            print(f"   Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"   Completion tokens: {response.usage_metadata.candidates_token_count}")
            print(f"   Total tokens: {response.usage_metadata.total_token_count}")

        print(f"\n💡 Gemini Features:")
        print(f"   - Free tier: 15 requests/minute")
        print(f"   - Context: Up to 2M tokens (huge!)")
        print(f"   - Multimodal: Can process images, video, audio")
        print(f"   - Models: gemini-1.5-flash (fast), gemini-1.5-pro (quality)")

        return True

    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("\nCommon issues:")
        print("   - Check API key is correct")
        print("   - Get API key: https://aistudio.google.com/app/apikey")
        print("   - Verify API is enabled in Google Cloud Console")
        print("   - Check rate limits (15 req/min on free tier)")
        return False


if __name__ == "__main__":
    print("🔍 Testing Google Gemini API...\n")

    success = test_gemini_api()

    if success:
        print("\n✅ Google Gemini API working (or skipped)!")
        print("\n📝 Note: Gemini offers:")
        print("   - Free tier with generous limits")
        print("   - 2M token context window (vs 200K for Claude/GPT-4)")
        print("   - Multimodal capabilities")
        print("   - Great for large document analysis")
        sys.exit(0)
    else:
        print("\n❌ Google Gemini API test failed.")
        sys.exit(1)
