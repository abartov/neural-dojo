#!/usr/bin/env python3
"""
Module 8 Example 2: Temperature Explorer

This example provides an interactive way to explore how temperature affects outputs.
You'll learn:
- Visual comparison of temperature effects
- Statistical analysis of variation
- How to choose optimal temperature for your use case

Prerequisites:
- pip install anthropic python-dotenv
- Set ANTHROPIC_API_KEY in .env file

Author: Neural Dojo
Date: 2025-11-21
"""

import anthropic
import os
from dotenv import load_dotenv
from typing import List, Dict
from collections import Counter
import time

# Load environment variables
load_dotenv()

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_multiple_samples(
    prompt: str,
    temperature: float,
    num_samples: int = 10,
    max_tokens: int = 100
) -> List[Dict]:
    """
    Generate multiple samples with the same temperature.

    Args:
        prompt: The prompt to use
        temperature: Temperature value
        num_samples: Number of samples to generate
        max_tokens: Maximum tokens per generation

    Returns:
        List of generation results
    """
    results = []

    print(f"\nGenerating {num_samples} samples with temperature={temperature}...")

    for i in range(num_samples):
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text
        results.append({
            "sample_num": i + 1,
            "text": text,
            "tokens": response.usage.output_tokens,
            "first_word": text.split()[0] if text else ""
        })

        # Show progress
        if (i + 1) % 5 == 0:
            print(f"  Generated {i + 1}/{num_samples}...")

    return results


def analyze_variation(results: List[Dict], temperature: float):
    """
    Analyze variation in generated samples.

    Args:
        results: List of generation results
        temperature: Temperature used
    """
    texts = [r["text"] for r in results]
    first_words = [r["first_word"] for r in results]

    # Count unique outputs
    unique_texts = len(set(texts))
    unique_first_words = len(set(first_words))

    # Count first word frequency
    first_word_counts = Counter(first_words)
    most_common = first_word_counts.most_common(3)

    print(f"\n{'='*70}")
    print(f"ANALYSIS: Temperature = {temperature}")
    print(f"{'='*70}")
    print(f"\nVariation metrics:")
    print(f"  Total samples: {len(results)}")
    print(f"  Unique full outputs: {unique_texts}/{len(results)} ({unique_texts/len(results)*100:.0f}%)")
    print(f"  Unique first words: {unique_first_words}/{len(results)} ({unique_first_words/len(results)*100:.0f}%)")

    print(f"\nMost common first words:")
    for word, count in most_common:
        percentage = count / len(results) * 100
        bar = "█" * int(percentage / 5)  # Visual bar (each █ = 5%)
        print(f"  '{word}': {count}/{len(results)} ({percentage:.0f}%) {bar}")

    # Variability rating
    if unique_texts == 1:
        rating = "⚪ No variation - Deterministic"
    elif unique_texts <= 3:
        rating = "🟡 Low variation - Very focused"
    elif unique_texts <= 7:
        rating = "🟢 Medium variation - Balanced"
    else:
        rating = "🔵 High variation - Creative"

    print(f"\nVariability: {rating}")

    # Show sample outputs
    print(f"\nSample outputs:")
    for i, result in enumerate(results[:3], 1):
        print(f"\n  Sample {i}:")
        text = result["text"][:150]
        print(f"  {text}{'...' if len(result['text']) > 150 else ''}")


def temperature_sweep(prompt: str, temperatures: List[float], num_samples: int = 10):
    """
    Test multiple temperatures and compare results.

    Args:
        prompt: The prompt to test
        temperatures: List of temperatures to test
        num_samples: Samples per temperature
    """
    print(f"\n{'='*70}")
    print(f"TEMPERATURE SWEEP")
    print(f"{'='*70}")
    print(f"\nPrompt: '{prompt}'")
    print(f"Testing {len(temperatures)} temperature values")
    print(f"{num_samples} samples per temperature")

    all_results = {}

    for temp in temperatures:
        results = generate_multiple_samples(prompt, temp, num_samples)
        all_results[temp] = results
        analyze_variation(results, temp)
        time.sleep(1)  # Be nice to API

    # Summary comparison
    print(f"\n{'='*70}")
    print(f"SUMMARY COMPARISON")
    print(f"{'='*70}\n")

    print(f"{'Temperature':<15} {'Unique Outputs':<20} {'Unique First Words':<25} {'Variability'}")
    print("-"*70)

    for temp, results in all_results.items():
        texts = [r["text"] for r in results]
        first_words = [r["first_word"] for r in results]

        unique_texts = len(set(texts))
        unique_first_words = len(set(first_words))

        if unique_texts == 1:
            variability = "⚪ Deterministic"
        elif unique_texts <= 3:
            variability = "🟡 Low"
        elif unique_texts <= 7:
            variability = "🟢 Medium"
        else:
            variability = "🔵 High"

        print(f"{temp:<15} {unique_texts}/{num_samples} ({unique_texts/num_samples*100:.0f}%)"
              f"{'':>6} {unique_first_words}/{num_samples} ({unique_first_words/num_samples*100:.0f}%)"
              f"{'':>10} {variability}")


def practical_temperature_finder():
    """
    Help find the right temperature for different use cases.
    """
    print(f"\n{'='*70}")
    print(f"PRACTICAL TEMPERATURE FINDER")
    print(f"{'='*70}")

    test_cases = [
        {
            "name": "Code Generation",
            "prompt": "Write a Python function to check if a number is prime.",
            "recommended": 0.2,
            "alternatives": [0.0, 0.3, 0.5],
            "goal": "Consistent, correct code"
        },
        {
            "name": "Question Answering",
            "prompt": "What is the capital of France?",
            "recommended": 0.0,
            "alternatives": [0.3, 0.7],
            "goal": "Factual, consistent answers"
        },
        {
            "name": "Creative Story Opening",
            "prompt": "Write the first sentence of a mystery novel.",
            "recommended": 1.0,
            "alternatives": [0.7, 1.2],
            "goal": "Varied, interesting openings"
        },
    ]

    for test_case in test_cases:
        print(f"\n{'='*70}")
        print(f"Use Case: {test_case['name']}")
        print(f"{'='*70}")
        print(f"Goal: {test_case['goal']}")
        print(f"Recommended temperature: {test_case['recommended']}")
        print(f"\nTesting recommended temperature...")

        results = generate_multiple_samples(
            test_case["prompt"],
            test_case["recommended"],
            num_samples=5,
            max_tokens=100
        )

        print(f"\nSample outputs:")
        for i, result in enumerate(results, 1):
            text = result["text"][:100]
            print(f"  {i}. {text}{'...' if len(result['text']) > 100 else ''}")

        # Quick analysis
        unique_count = len(set(r["text"] for r in results))
        print(f"\nUnique outputs: {unique_count}/5")

        if test_case["name"] == "Code Generation":
            if unique_count <= 2:
                print("  ✅ Good! Low variation ensures consistent code.")
            else:
                print("  ⚠️  High variation - may want lower temperature")

        elif test_case["name"] == "Question Answering":
            if unique_count == 1:
                print("  ✅ Perfect! Deterministic factual answer.")
            else:
                print("  ⚠️  Variation in factual answer - use temperature=0.0")

        elif test_case["name"] == "Creative Story Opening":
            if unique_count >= 4:
                print("  ✅ Great! High variation for creativity.")
            elif unique_count >= 3:
                print("  🟢 Good variation - consider slightly higher temperature")
            else:
                print("  ⚠️  Low variation - increase temperature for more creativity")

        time.sleep(1)


def temperature_decision_tree():
    """
    Interactive decision tree for choosing temperature.
    """
    print(f"\n{'='*70}")
    print(f"TEMPERATURE DECISION TREE")
    print(f"{'='*70}\n")

    print("Answer these questions to find your optimal temperature:\n")

    questions = [
        {
            "q": "Do you need the same output every time?",
            "yes": {"temp": 0.0, "desc": "Deterministic - temperature = 0.0"},
            "no": "next"
        },
        {
            "q": "Is this for code generation or structured data?",
            "yes": {"temp": 0.2, "desc": "Low variance - temperature = 0.2-0.3"},
            "no": "next"
        },
        {
            "q": "Do you want creative, varied outputs?",
            "yes": {"temp": 1.0, "desc": "Creative - temperature = 0.9-1.2"},
            "no": {"temp": 0.7, "desc": "Balanced - temperature = 0.7"}
        },
    ]

    print("Decision Tree:")
    print("-" * 70)
    print()
    print("Q1: Do you need the same output every time?")
    print("    YES → Temperature = 0.0 (Deterministic)")
    print("    NO  → Q2")
    print()
    print("Q2: Is this for code generation or structured data?")
    print("    YES → Temperature = 0.2-0.3 (Low variance)")
    print("    NO  → Q3")
    print()
    print("Q3: Do you want creative, varied outputs?")
    print("    YES → Temperature = 0.9-1.2 (Creative)")
    print("    NO  → Temperature = 0.7 (Balanced)")
    print()
    print("-" * 70)

    print("\n\nCommon Use Cases → Recommended Temperatures:")
    print("-" * 70)

    use_cases = [
        ("Testing/QA", "0.0", "Need reproducible outputs"),
        ("JSON extraction", "0.0", "Need deterministic structured data"),
        ("Code generation", "0.2-0.3", "Need consistency with slight variation"),
        ("Translation", "0.3", "Need accuracy over creativity"),
        ("Summarization", "0.3-0.5", "Need focused, consistent summaries"),
        ("Chatbot responses", "0.7", "Balance natural variation with quality"),
        ("Content generation", "0.7-0.9", "Need variety but stay sensible"),
        ("Creative writing", "1.0-1.2", "Want surprising, creative outputs"),
        ("Brainstorming", "1.0-1.5", "Push creative boundaries"),
    ]

    for use_case, temp_range, reason in use_cases:
        print(f"\n  {use_case:<25} → T = {temp_range:<10} ({reason})")

    print("\n" + "-" * 70)


def main():
    """Run all temperature exploration demos."""

    print("\n🌡️ MODULE 8: TEMPERATURE EXPLORER")
    print("="*70)
    print("\nThis example helps you understand and choose the right temperature.")
    print("\n⚠️  Note: This uses the Claude API and will consume tokens!")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("   Please create a .env file with your API key:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        return

    # Demo 1: Temperature sweep
    prompt = "The most important skill for the future is"
    temperatures = [0.0, 0.3, 0.7, 1.0]
    temperature_sweep(prompt, temperatures, num_samples=10)

    # Demo 2: Practical temperature finder
    practical_temperature_finder()

    # Demo 3: Decision tree
    temperature_decision_tree()

    print("\n\n✅ TEMPERATURE EXPLORATION COMPLETE!")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Temperature = 0.0 → Always same output (deterministic)")
    print("  2. Temperature = 0.2-0.3 → Low variation (code, structured data)")
    print("  3. Temperature = 0.7 → Balanced (most chatbots)")
    print("  4. Temperature = 1.0+ → High variation (creative writing)")
    print("  5. There's no universal 'best' temperature - depends on use case!")
    print("\n💡 Pro Tip: Start with 0.7, then adjust based on results:")
    print("   • Too boring/repetitive? Increase temperature")
    print("   • Too random/weird? Decrease temperature")
    print("\n🥋 Neural Dojo - Find your perfect temperature! 🧠⚡")


if __name__ == "__main__":
    main()
