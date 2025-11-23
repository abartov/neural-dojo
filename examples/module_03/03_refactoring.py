#!/usr/bin/env python3
"""
Module 3: Code Refactoring with AI

Demonstrates using AI to refactor and modernize legacy code.

KEY INSIGHT: AI can modernize old code (type hints, error handling, best practices)!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def refactor_code(legacy_code: str, improvements: str) -> str:
    """Refactor legacy code with specified improvements."""
    prompt = f"""
You are an expert Python developer specializing in code modernization.

Refactor this legacy code:

```python
{legacy_code}
```

Improvements to make:
{improvements}

Return ONLY the refactored code, no explanations.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def main():
    """Demonstrate code refactoring."""
    print("=" * 60)
    print("MODULE 3: CODE REFACTORING")
    print("=" * 60)

    # Example 1: Add type hints
    print("\n📝 Example 1: Modernize with Type Hints")
    print("-" * 60)

    legacy1 = """
def process_data(data, threshold):
    result = []
    for item in data:
        if item['value'] > threshold:
            result.append({
                'id': item['id'],
                'value': item['value'],
                'status': 'high'
            })
    return result
"""

    improvements1 = """
- Add complete type hints (typing.List, typing.Dict, typing.Any)
- Add docstring (Google style)
- Use more descriptive variable names if appropriate
- Keep functionality exactly the same
"""

    print("Legacy Code:")
    print(legacy1)
    print("\nImprovements requested:")
    print(improvements1)

    refactored1 = refactor_code(legacy1, improvements1)
    print("\n✨ Refactored Code:")
    print(refactored1)

    # Example 2: Add error handling
    print("\n\n📝 Example 2: Add Robust Error Handling")
    print("-" * 60)

    legacy2 = """
def read_user_data(filename):
    f = open(filename)
    content = f.read()
    f.close()
    return content.split('\n')
"""

    improvements2 = """
- Use context manager (with statement)
- Add proper error handling:
  - FileNotFoundError with clear message
  - UnicodeDecodeError (try utf-8, fallback to latin-1)
  - Handle empty file
- Add type hints
- Add docstring
- Use pathlib.Path for better path handling
"""

    print("Legacy Code:")
    print(legacy2)
    print("\nImprovements requested:")
    print(improvements2)

    refactored2 = refactor_code(legacy2, improvements2)
    print("\n✨ Refactored Code:")
    print(refactored2)

    # Example 3: Extract functions (improve readability)
    print("\n\n📝 Example 3: Extract Functions for Readability")
    print("-" * 60)

    legacy3 = """
def generate_report(users):
    # Filter active users
    active = [u for u in users if u['active']]

    # Calculate stats
    total = len(active)
    avg_age = sum(u['age'] for u in active) / total if total > 0 else 0

    # Format output
    output = f"Total Users: {total}\\n"
    output += f"Average Age: {avg_age:.1f}\\n"
    output += "\\nUser List:\\n"
    for u in sorted(active, key=lambda x: x['name']):
        output += f"- {u['name']} ({u['age']})\\n"

    return output
"""

    improvements3 = """
- Extract separate functions for:
  - Filtering active users
  - Calculating statistics
  - Formatting output
- Add type hints to all functions
- Add docstrings
- Make code more testable (single responsibility principle)
- Keep functionality exactly the same
"""

    print("Legacy Code:")
    print(legacy3)
    print("\nImprovements requested:")
    print(improvements3)

    refactored3 = refactor_code(legacy3, improvements3)
    print("\n✨ Refactored Code:")
    print(refactored3)

    # Example 4: Use modern Python features
    print("\n\n📝 Example 4: Use Modern Python Features")
    print("-" * 60)

    legacy4 = """
def merge_dicts(dict1, dict2):
    result = {}
    for key in dict1:
        result[key] = dict1[key]
    for key in dict2:
        result[key] = dict2[key]
    return result

def get_value(data, key, default):
    if key in data:
        return data[key]
    else:
        return default
"""

    improvements4 = """
- Use Python 3.9+ features:
  - Dictionary merge operator (|)
  - dict.get() method with default
- Simplify logic
- Add type hints
- Add docstrings
- Make more Pythonic
"""

    print("Legacy Code:")
    print(legacy4)
    print("\nImprovements requested:")
    print(improvements4)

    refactored4 = refactor_code(legacy4, improvements4)
    print("\n✨ Refactored Code:")
    print(refactored4)

    # Lessons learned
    print("\n\n💡 LESSONS LEARNED:")
    print("=" * 60)
    print("1. AI knows modern best practices:")
    print("   - Latest Python features")
    print("   - Type hints")
    print("   - Context managers")
    print("")
    print("2. Be specific about what to preserve:")
    print("   - 'Keep functionality exactly the same'")
    print("   - Prevents unintended changes")
    print("")
    print("3. Refactor in small steps:")
    print("   - One improvement at a time")
    print("   - Easier to verify correctness")
    print("   - Safer than big rewrites")
    print("")
    print("4. Always test after refactoring:")
    print("   - Run existing tests")
    print("   - Verify behavior unchanged")
    print("   - Check edge cases")
    print("")
    print("5. Good refactoring improves:")
    print("   - Readability (clear code)")
    print("   - Maintainability (easier to change)")
    print("   - Testability (smaller functions)")
    print("   - Correctness (proper error handling)")


if __name__ == "__main__":
    main()
