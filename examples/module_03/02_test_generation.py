#!/usr/bin/env python3
"""
Module 3: Test Generation

Demonstrates generating comprehensive test suites for existing code.

KEY INSIGHT: AI excels at generating edge cases you might miss!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_tests(function_code: str, framework: str = "pytest") -> str:
    """Generate comprehensive test suite for given function."""
    prompt = f"""
You are an expert at writing comprehensive tests.

Generate a complete test suite for this function:

```python
{function_code}
```

Requirements:
- Use {framework} framework
- Cover happy path (normal usage)
- Cover edge cases (empty, null, boundaries, special chars)
- Cover error cases (invalid types, out of range)
- Use descriptive test names
- Add docstrings explaining what each test verifies
- Include fixtures for common test data
- Aim for 100% coverage

Return ONLY the test code, no explanations.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def main():
    """Demonstrate test generation."""
    print("=" * 60)
    print("MODULE 3: TEST GENERATION")
    print("=" * 60)

    # Example 1: Simple function
    print("\n📝 Example 1: Email Validator Tests")
    print("-" * 60)

    function1 = """
def validate_email(email: str) -> bool:
    '''Validate email format.'''
    if not email or not isinstance(email, str):
        return False

    if email.count('@') != 1:
        return False

    local, domain = email.split('@')

    if not local or not domain:
        return False

    if '.' not in domain:
        return False

    if len(email) > 254:
        return False

    return True
"""

    print("Function to test:")
    print(function1)

    tests1 = generate_tests(function1)
    print("\n✨ Generated Tests:")
    print(tests1)

    # Example 2: More complex function
    print("\n\n📝 Example 2: Data Filter Tests")
    print("-" * 60)

    function2 = """
from typing import List, Dict, Any

def filter_users(users: List[Dict[str, Any]], min_age: int = 18) -> List[Dict[str, Any]]:
    '''Filter users by minimum age and sort by name.'''
    if not users:
        return []

    filtered = []
    for user in users:
        if 'age' in user and user['age'] >= min_age:
            filtered.append(user)

    return sorted(filtered, key=lambda x: x.get('name', ''))
"""

    print("Function to test:")
    print(function2)

    tests2 = generate_tests(function2)
    print("\n✨ Generated Tests:")
    print(tests2)

    # Example 3: File operations
    print("\n\n📝 Example 3: File Reader Tests")
    print("-" * 60)

    function3 = """
import json
from pathlib import Path
from typing import Dict, Any

def read_config(filepath: str) -> Dict[str, Any]:
    '''Read JSON config file with error handling.'''
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {filepath}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    except UnicodeDecodeError:
        # Try with different encoding
        with open(path, 'r', encoding='latin-1') as f:
            config = json.load(f)

    return config
"""

    print("Function to test:")
    print(function3)

    tests3 = generate_tests(function3)
    print("\n✨ Generated Tests:")
    print(tests3)

    # Lessons learned
    print("\n\n💡 LESSONS LEARNED:")
    print("=" * 60)
    print("1. AI generates edge cases you might miss:")
    print("   - Empty strings, None, special characters")
    print("   - Boundary values (min/max)")
    print("   - Type errors")
    print("")
    print("2. Good test names are descriptive:")
    print("   - test_returns_true_for_valid_email")
    print("   - test_raises_error_for_missing_file")
    print("")
    print("3. Use fixtures for common test data:")
    print("   - Reduces duplication")
    print("   - Makes tests cleaner")
    print("   - Easier to maintain")
    print("")
    print("4. Always review generated tests:")
    print("   - Check they actually test what you want")
    print("   - Verify edge cases are comprehensive")
    print("   - Ensure assertions are correct")
    print("")
    print("5. Run tests to verify they work:")
    print("   - Generated tests might have bugs too!")
    print("   - Make sure they actually catch errors")
    print("   - Check coverage reports")


if __name__ == "__main__":
    main()
