#!/usr/bin/env python3
"""
Module 3: API Client Generation

Demonstrates generating a complete API client with error handling and tests.

KEY INSIGHT: AI can generate production-ready API clients in minutes!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_api_client(specification: str) -> str:
    """Generate API client from specification."""
    prompt = f"""
You are an expert at building API clients.

{specification}

Requirements:
- Use requests library
- Include proper error handling (4xx, 5xx)
- Add timeout (default 10 seconds)
- Use type hints throughout
- Add comprehensive docstrings
- Include retry logic with exponential backoff
- Validate inputs
- Return proper data structures (dataclasses or dicts)

Return ONLY the code, no explanations.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def main():
    """Demonstrate API client generation."""
    print("=" * 60)
    print("MODULE 3: API CLIENT GENERATION")
    print("=" * 60)

    # Example 1: Simple REST API client
    print("\n📝 Example: JSONPlaceholder API Client")
    print("-" * 60)

    spec = """
Generate a Python client for JSONPlaceholder API (https://jsonplaceholder.typicode.com):

class JSONPlaceholderClient:
    Base URL: https://jsonplaceholder.typicode.com

    Methods:
    1. get_posts() -> List[Post]
       Get all posts

    2. get_post(post_id: int) -> Post
       Get single post by ID
       Raise ValueError if post_id < 1

    3. create_post(title: str, body: str, user_id: int) -> Post
       Create new post
       Validate: title and body not empty, user_id > 0

    4. update_post(post_id: int, title: str = None, body: str = None) -> Post
       Update existing post (partial update)

    5. delete_post(post_id: int) -> bool
       Delete post, return True if successful

Data Structures:
- Post: dataclass with fields (id: int, title: str, body: str, userId: int)

Error Handling:
- Handle HTTP 404 (raise PostNotFoundError)
- Handle HTTP 4xx (raise ClientError)
- Handle HTTP 5xx (raise ServerError)
- Handle network errors (ConnectionError)
- Retry on 5xx errors (max 3 times, exponential backoff)

Include:
- Custom exception classes
- Type hints everywhere
- Logging (use Python logging module)
- Request/response validation
"""

    print("Specification:")
    print(spec)

    print("\n🤖 Generating API client...")
    client_code = generate_api_client(spec)

    print("\n✨ Generated API Client:")
    print(client_code)

    # Now generate tests
    print("\n\n📝 Generating Tests for API Client")
    print("-" * 60)

    test_spec = f"""
Generate pytest tests for this API client:

{client_code}

Requirements:
- Use pytest framework
- Mock HTTP requests (use responses library or unittest.mock)
- Test all methods
- Test error cases (404, 500, network errors)
- Test retry logic
- Test input validation
- Use fixtures for common test data
- Aim for 100% coverage

Return ONLY the test code.
"""

    print("Generating tests...")
    test_prompt = f"""
You are an expert at writing API client tests.

{test_spec}

Return ONLY the code, no explanations.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{"role": "user", "content": test_prompt}]
    )

    tests = response.content[0].text

    print("\n✨ Generated Tests:")
    print(tests)

    # Lessons learned
    print("\n\n💡 LESSONS LEARNED:")
    print("=" * 60)
    print("1. Specify error handling explicitly:")
    print("   - Which errors to catch")
    print("   - What to do with them")
    print("   - Custom exception types")
    print("")
    print("2. Request production features:")
    print("   - Retry logic")
    print("   - Timeouts")
    print("   - Logging")
    print("   - Input validation")
    print("")
    print("3. Use type-safe data structures:")
    print("   - Dataclasses for responses")
    print("   - Type hints for clarity")
    print("   - Validation at boundaries")
    print("")
    print("4. Generate tests WITH the client:")
    print("   - Easier to verify correctness")
    print("   - Tests document usage")
    print("   - Catch bugs early")
    print("")
    print("5. API clients are perfect for AI generation:")
    print("   - Well-defined patterns")
    print("   - Standard error handling")
    print("   - Repetitive code structure")
    print("   - AI saves 4-6 hours per client!")
    print("")
    print("📦 NEXT STEPS:")
    print("   1. Save generated code to files")
    print("   2. pip install requests responses pytest")
    print("   3. Run tests: pytest test_api_client.py")
    print("   4. Try the client with real API")
    print("   5. Review and customize for your needs")


if __name__ == "__main__":
    main()
