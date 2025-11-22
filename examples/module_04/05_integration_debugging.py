#!/usr/bin/env python3
"""
Module 4: Integration & API Debugging with AI
Shows how to debug external API calls and integrations.

AI Effectiveness: ⭐⭐⭐⭐ (Good with proper context!)
"""

import sys
import json
from typing import Dict


def example_1_auth_error():
    """Demonstrate fixing API authentication."""
    print("\n--- Example 1: API Authentication ---\n")

    print("❌ BUGGY CODE:")
    print("""
import requests
response = requests.post(
    "https://api.example.com/data",
    json={"key": "value"}
)
# Error: 401 Unauthorized
    """)

    print("\n🤖 AI Analysis:")
    print("   401 = Authentication required")
    print("   Fix: Add Authorization header or API key")

    print("\n✅ FIXED CODE:")
    print("""
headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.post(
    "https://api.example.com/data",
    headers=headers,
    json={"key": "value"}
)
    """)
    print("✓ Always check API docs for auth requirements!\n")


def example_2_json_parsing():
    """Demonstrate JSON parsing errors."""
    print("\n--- Example 2: JSON Parsing ---\n")

    print("❌ BUGGY:")
    bad_json = "{'key': 'value'}"  # Single quotes!
    print(f"json_str = {bad_json}")
    print("json.loads(json_str)  # JSONDecodeError!")

    print("\n🤖 AI Analysis:")
    print("   JSON requires double quotes")
    print("   Fix: Use proper JSON format")

    print("\n✅ FIXED:")
    good_json = '{"key": "value"}'
    result = json.loads(good_json)
    print(f"json_str = {good_json}")
    print(f"result = {result}")
    print("✓ Valid JSON parsed successfully!\n")


def example_3_timeout_handling():
    """Demonstrate timeout handling."""
    print("\n--- Example 3: Timeout Handling ---\n")

    print("❌ NO TIMEOUT (can hang forever):")
    print("""
response = requests.get("https://slow-api.com")
# May hang indefinitely!
    """)

    print("\n🤖 AI Analysis:")
    print("   Always set timeouts for external calls")
    print("   Fix: Add timeout parameter")

    print("\n✅ WITH TIMEOUT:")
    print("""
try:
    response = requests.get(
        "https://api.example.com",
        timeout=5  # 5 second timeout
    )
except requests.Timeout:
    print("Request timed out!")
    """)
    print("✓ Timeouts prevent hanging!\n")


def example_4_response_validation():
    """Demonstrate response validation."""
    print("\n--- Example 4: Response Validation ---\n")

    print("❌ ASSUMES SUCCESS:")
    print("""
response = requests.get(url)
data = response.json()  # Crashes if not JSON!
    """)

    print("\n🤖 AI Analysis:")
    print("   Check status code before parsing")
    print("   Handle non-JSON responses")

    print("\n✅ PROPER VALIDATION:")
    print("""
response = requests.get(url)
if response.status_code == 200:
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Response is not JSON")
else:
    print(f"Error: {response.status_code}")
    """)
    print("✓ Always validate responses!\n")


def main():
    """Run integration debugging examples."""
    print("=" * 60)
    print("  Integration & API Debugging with AI")
    print("=" * 60)
    print("\nCommon API debugging patterns:\n")

    example_1_auth_error()
    example_2_json_parsing()
    example_3_timeout_handling()
    example_4_response_validation()

    print("Key Takeaways:")
    print("1. AI is GREAT at debugging API errors with status codes")
    print("2. Always provide: status code, headers, request/response")
    print("3. Check API documentation")
    print("4. Add timeouts, validation, error handling")
    print("5. Test with curl/Postman first\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
