#!/usr/bin/env python3
"""
Module 3: Basic Code Generation

Demonstrates generating functions from natural language specifications.

KEY INSIGHT: Clear specifications = quality code!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_code(specification: str) -> str:
    """Generate code from specification using Claude."""
    prompt = f"""
You are an expert Python developer. Generate clean, production-quality code.

{specification}

Requirements:
- Include type hints
- Add docstring (Google style)
- Handle edge cases
- Include error handling
- Follow PEP 8

Return ONLY the code, no explanations.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def main():
    """Demonstrate basic code generation."""
    print("=" * 60)
    print("MODULE 3: BASIC CODE GENERATION")
    print("=" * 60)

    # Example 1: Data validator
    print("\n📝 Example 1: Email Validator")
    print("-" * 60)

    spec1 = """
Generate a Python function validate_email(email: str) -> bool that:
- Returns True if email is valid, False otherwise
- Checks for @ symbol
- Checks for domain with TLD
- Handles None and empty strings
- Allows letters, numbers, dots, hyphens in local part
- Max length 254 characters
"""

    print("Specification:")
    print(spec1)

    code1 = generate_code(spec1)
    print("\n✨ Generated Code:")
    print(code1)

    # Example 2: Data processor
    print("\n\n📝 Example 2: Data Filter")
    print("-" * 60)

    spec2 = """
Generate a Python function filter_adults(users: List[Dict[str, Any]]) -> List[Dict[str, Any]] that:
- Takes list of user dictionaries
- Each dict has: name (str), age (int), email (str)
- Returns users where age >= 18
- Sorts result by name alphabetically
- Handles empty list
- Handles missing 'age' key (skip those users)
- Includes type hints
"""

    print("Specification:")
    print(spec2)

    code2 = generate_code(spec2)
    print("\n✨ Generated Code:")
    print(code2)

    # Example 3: File processor
    print("\n\n📝 Example 3: CSV Reader")
    print("-" * 60)

    spec3 = """
Generate a Python function read_csv_safe(filepath: str) -> List[Dict[str, str]] that:
- Reads CSV file and returns list of dictionaries
- First row is headers
- Handles file not found (raise FileNotFoundError with message)
- Handles encoding issues (try utf-8, then latin-1)
- Strips whitespace from values
- Returns empty list for empty file
- Uses csv module (not pandas)
"""

    print("Specification:")
    print(spec3)

    code3 = generate_code(spec3)
    print("\n✨ Generated Code:")
    print(code3)

    # Lessons learned
    print("\n\n💡 LESSONS LEARNED:")
    print("=" * 60)
    print("1. Specificity matters:")
    print("   - Clear inputs/outputs")
    print("   - Explicit edge cases")
    print("   - Define error handling")
    print("")
    print("2. Request best practices:")
    print("   - Type hints")
    print("   - Docstrings")
    print("   - Error handling")
    print("")
    print("3. Test generated code:")
    print("   - Never trust blindly")
    print("   - Run with edge cases")
    print("   - Review for security")
    print("")
    print("4. Iterate if needed:")
    print("   - First generation may need refinement")
    print("   - Adjust specification and regenerate")
    print("")
    print("5. Quality of spec = quality of code:")
    print("   - Vague spec → generic code")
    print("   - Detailed spec → production-ready code")


if __name__ == "__main__":
    main()
