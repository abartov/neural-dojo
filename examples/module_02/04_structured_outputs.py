#!/usr/bin/env python3
"""
Module 2: Structured Outputs

Demonstrates how to get AI to return data in specific formats:
JSON, tables, code, markdown, etc.

KEY INSIGHT: Be explicit about format = consistent, parseable results!
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_json_output():
    """
    Request JSON format explicitly.
    """
    prompt = """
Analyze this code and return your analysis as JSON:

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

Return JSON with this structure:
{
    "function_name": "...",
    "purpose": "...",
    "time_complexity": "...",
    "space_complexity": "...",
    "algorithm_type": "...",
    "edge_cases": ["...", "..."],
    "improvements": ["...", "..."]
}

Return ONLY the JSON, no other text.
"""
    return prompt


def get_markdown_table():
    """
    Request markdown table format.
    """
    prompt = """
Compare these three sorting algorithms: Bubble Sort, Quick Sort, Merge Sort.

Return your comparison as a markdown table with these columns:
| Algorithm | Time (Best) | Time (Avg) | Time (Worst) | Space | Stable | When to Use |

Be concise in each cell (5-10 words max).
"""
    return prompt


def get_csv_format():
    """
    Request CSV format for data extraction.
    """
    prompt = """
Extract information about these Python packages and return as CSV:

Text: "We use FastAPI for the web framework, running on Python 3.11. For testing we use pytest version 7.4.0, and black 23.7.0 for code formatting. SQLAlchemy 2.0.19 handles database operations."

CSV format (no spaces after commas):
Package,Version,Purpose

Return ONLY the CSV data, no headers explanation.
"""
    return prompt


def get_code_only():
    """
    Request only code, no explanations.
    """
    prompt = """
Write a Python function that checks if a string is a palindrome.

Requirements:
- Ignore case
- Ignore spaces and punctuation
- Return boolean

Return ONLY the code, no explanations, no markdown.
"""
    return prompt


def get_xml_format():
    """
    Request XML format.
    """
    prompt = """
Convert this user data to XML:

Name: Alice Johnson
Email: alice@example.com
Age: 28
Roles: developer, admin
Active: true

Return as XML with proper structure and nesting.
"""
    return prompt


def run_prompt(prompt: str, label: str):
    """Execute a prompt and display results."""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"\nPrompt:\n{prompt[:200]}...")
    print(f"\n{'-'*60}\nResponse:")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(result)

    return result


def validate_json_output():
    """
    Get JSON and validate it's parseable.
    """
    print("\n" + "🔍"*30)
    print("VALIDATING JSON OUTPUT")
    print("🔍"*30)

    prompt = get_json_output()
    response_text = run_prompt(prompt, "📊 JSON FORMAT")

    # Try to parse the JSON
    print(f"\n{'-'*60}")
    print("Validation:")
    try:
        # Extract JSON from response (might have markdown backticks)
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()

        data = json.loads(json_text)
        print("✅ Valid JSON!")
        print(f"   Function name: {data.get('function_name')}")
        print(f"   Time complexity: {data.get('time_complexity')}")
        print(f"   Edge cases: {len(data.get('edge_cases', []))} found")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")


def demonstrate_format_examples():
    """
    Show multiple output formats.
    """
    print("\n" + "📋"*30)
    print("MULTIPLE FORMAT EXAMPLES")
    print("📋"*30)

    # Markdown table
    run_prompt(get_markdown_table(), "📊 MARKDOWN TABLE")

    # CSV
    run_prompt(get_csv_format(), "📄 CSV FORMAT")

    # Code only
    run_prompt(get_code_only(), "💻 CODE ONLY (No Explanation)")

    # XML
    run_prompt(get_xml_format(), "📝 XML FORMAT")


def demonstrate_nested_json():
    """
    Get complex nested JSON structure.
    """
    print("\n" + "🗂️"*30)
    print("COMPLEX NESTED JSON")
    print("🗂️"*30)

    prompt = """
Create a mock user profile as JSON with this exact structure:

{
    "user": {
        "id": "uuid here",
        "name": "...",
        "email": "...",
        "profile": {
            "bio": "...",
            "avatar_url": "...",
            "social": {
                "github": "...",
                "twitter": "..."
            }
        },
        "settings": {
            "notifications": true,
            "theme": "dark",
            "language": "en"
        },
        "projects": [
            {
                "id": 1,
                "name": "...",
                "status": "active",
                "tags": ["tag1", "tag2"]
            }
        ]
    }
}

Make it realistic. Return ONLY the JSON.
"""

    run_prompt(prompt, "🗂️ NESTED JSON STRUCTURE")


def demonstrate_mixed_format():
    """
    Get structured output with sections.
    """
    print("\n" + "📑"*30)
    print("MIXED FORMAT OUTPUT")
    print("📑"*30)

    prompt = """
Analyze this code for bugs:

```python
def divide_numbers(a, b):
    result = a / b
    return result
```

Return your analysis in this EXACT format:

## Summary
[One sentence summary]

## Issues Found
1. [Issue]
2. [Issue]

## Severity
- Critical: [number]
- High: [number]
- Medium: [number]

## Fixed Code
```python
[corrected code here]
```

## Test Cases
```python
[test cases to verify fix]
```
"""

    run_prompt(prompt, "📑 MIXED FORMAT (Markdown + Code)")


def demonstrate_llm_friendly_formats():
    """
    Show formats that are easy for other tools to parse.
    """
    print("\n" + "🔧"*30)
    print("LLM-FRIENDLY FORMATS")
    print("🔧"*30)

    # Key-value pairs
    kv_prompt = """
Extract package dependencies from this requirements.txt:

fastapi==0.103.0
uvicorn==0.23.2
sqlalchemy==2.0.19

Return as simple key-value pairs (one per line):
PACKAGE=VERSION
"""

    run_prompt(kv_prompt, "🔑 KEY=VALUE FORMAT")

    # Delimited format
    delimited_prompt = """
List 5 Python design patterns with brief descriptions.

Return in this pipe-delimited format (one per line):
PatternName | Category | Description | Use Case

No headers, just data.
"""

    run_prompt(delimited_prompt, "➡️ PIPE-DELIMITED FORMAT")


def main():
    """
    Main demonstration of structured outputs.
    """
    print("\n" + "="*60)
    print("MODULE 2: STRUCTURED OUTPUTS")
    print("="*60)
    print("\nKEY INSIGHT: Specify format explicitly = parseable results!")
    print("="*60)

    # JSON validation
    validate_json_output()

    # Multiple formats
    demonstrate_format_examples()

    # Complex JSON
    demonstrate_nested_json()

    # Mixed format
    demonstrate_mixed_format()

    # LLM-friendly formats
    demonstrate_llm_friendly_formats()

    # Final insights
    print("\n" + "💡"*30)
    print("LESSONS LEARNED:")
    print("="*60)
    print("1. Always specify the format explicitly:")
    print("   - 'Return as JSON'")
    print("   - 'Format as markdown table'")
    print("   - 'CSV with headers: ...'")
    print("2. Provide format examples:")
    print("   - Show the exact structure you want")
    print("   - Use placeholders: {...} for JSON")
    print("3. Request 'ONLY' the format:")
    print("   - 'Return ONLY JSON, no explanations'")
    print("   - Prevents extra text that breaks parsing")
    print("4. Common formats:")
    print("   - JSON (most flexible, parseable)")
    print("   - Markdown tables (readable, structured)")
    print("   - CSV (simple data export)")
    print("   - XML (for legacy systems)")
    print("   - Code blocks (for implementations)")
    print("5. Validation is crucial:")
    print("   - Always validate AI output")
    print("   - Parse JSON with try/catch")
    print("   - Have fallback strategies")
    print("6. LLM-friendly formats:")
    print("   - Simple delimiters (|, =, :)")
    print("   - Line-based formats")
    print("   - Easy to parse with regex")
    print("7. Schema specification:")
    print("   - For JSON, show exact schema")
    print("   - Include data types")
    print("   - Specify required vs optional fields")
    print("="*60)

    print("\n🔧 Pro Tips:")
    print("   - JSON Schema: Use JSON Schema for validation")
    print("   - Pydantic: Create Python models for type safety")
    print("   - Templates: Store format templates in library")
    print("   - Fallbacks: Handle format violations gracefully")


if __name__ == "__main__":
    main()
