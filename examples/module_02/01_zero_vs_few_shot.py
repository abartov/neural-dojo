#!/usr/bin/env python3
"""
Module 2: Zero-Shot vs Few-Shot Prompting

Demonstrates the dramatic difference between zero-shot (no examples)
and few-shot (with examples) prompting.

KEY INSIGHT: 2-3 examples can improve accuracy from ~60% to ~95%!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def zero_shot_prompt():
    """
    Zero-Shot: Ask the AI to perform a task with NO examples.

    Relies entirely on the model's training data.
    """
    prompt = """
    Extract the sentiment from this movie review as: Positive, Negative, or Neutral

    Review: "This film was a masterpiece! The cinematography was breathtaking and the story kept me engaged until the very end. A must-watch!"

    Sentiment:
    """

    return prompt


def few_shot_prompt():
    """
    Few-Shot: Provide 2-3 examples, then ask for a new one.

    The AI learns the pattern from examples!
    """
    prompt = """
    Extract the sentiment from movie reviews. Format: Review → Sentiment

    Review: "Absolutely loved it! Best movie of the year!"
    Sentiment: Positive

    Review: "Terrible waste of time. Poor acting and boring plot."
    Sentiment: Negative

    Review: "It was okay. Nothing special but not terrible either."
    Sentiment: Neutral

    Review: "This film was a masterpiece! The cinematography was breathtaking and the story kept me engaged until the very end. A must-watch!"
    Sentiment:
    """

    return prompt


def run_prompt(prompt: str, label: str):
    """Execute a prompt and display results."""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"\nPrompt:\n{prompt}")
    print(f"\n{'-'*60}")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(f"Response: {result}")

    return result


def demonstrate_extraction_task():
    """
    Demonstrate zero-shot vs few-shot on structured data extraction.

    Task: Extract name, email, phone from text.
    """
    print("\n" + "🔥"*30)
    print("TASK: Structured Data Extraction")
    print("🔥"*30)

    # Zero-shot version
    zero_shot = """
    Extract the person's name, email, and phone number from this text:

    "Hi, I'm Sarah Johnson. You can reach me at sarah.j@example.com or call me at 555-0123."

    Format as JSON.
    """

    # Few-shot version
    few_shot = """
    Extract contact information as JSON.

    Example 1:
    Text: "I'm John Doe, email: john@test.com, phone: 555-1234"
    Output: {"name": "John Doe", "email": "john@test.com", "phone": "555-1234"}

    Example 2:
    Text: "Contact Alice Smith at alice.smith@demo.org or 555-5678"
    Output: {"name": "Alice Smith", "email": "alice.smith@demo.org", "phone": "555-5678"}

    Now extract from:
    Text: "Hi, I'm Sarah Johnson. You can reach me at sarah.j@example.com or call me at 555-0123."
    Output:
    """

    run_prompt(zero_shot, "❌ ZERO-SHOT (No Examples)")
    run_prompt(few_shot, "✅ FEW-SHOT (With Examples)")


def demonstrate_format_consistency():
    """
    Show how few-shot ensures consistent output format.
    """
    print("\n" + "🔥"*30)
    print("TASK: Format Consistency")
    print("🔥"*30)

    # Zero-shot (format may vary)
    zero_shot = """
    List 3 programming languages and their primary use cases.
    """

    # Few-shot (format is consistent)
    few_shot = """
    List programming languages with their primary use cases.

    Language: Python | Use Case: Data science, web development, scripting
    Language: JavaScript | Use Case: Web frontend, Node.js backend, mobile apps
    Language: Rust | Use Case: Systems programming, performance-critical applications

    Now add 2 more languages following the same format.
    """

    run_prompt(zero_shot, "❌ ZERO-SHOT (Unpredictable Format)")
    run_prompt(few_shot, "✅ FEW-SHOT (Consistent Format)")


def main():
    """
    Main demonstration of zero-shot vs few-shot prompting.
    """
    print("\n" + "="*60)
    print("MODULE 2: ZERO-SHOT VS FEW-SHOT PROMPTING")
    print("="*60)
    print("\nKEY INSIGHT: Examples teach the AI your desired pattern!")
    print("="*60)

    # Basic sentiment analysis
    run_prompt(zero_shot_prompt(), "❌ ZERO-SHOT (No Examples)")
    run_prompt(few_shot_prompt(), "✅ FEW-SHOT (With Examples)")

    # Structured data extraction
    demonstrate_extraction_task()

    # Format consistency
    demonstrate_format_consistency()

    # Final insights
    print("\n" + "💡"*30)
    print("LESSONS LEARNED:")
    print("="*60)
    print("1. Zero-shot works for simple, common tasks")
    print("2. Few-shot ensures:")
    print("   - Consistent format")
    print("   - Better accuracy")
    print("   - Desired output structure")
    print("3. Sweet spot: 2-3 examples")
    print("4. More examples ≠ always better (diminishing returns)")
    print("="*60)


if __name__ == "__main__":
    main()
