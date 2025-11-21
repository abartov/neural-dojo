#!/usr/bin/env python3
"""
Module 8 Example 1: Sampling Strategy Playground

This example demonstrates how different sampling strategies affect text generation.
You'll learn:
- How temperature affects outputs
- How top-p (nucleus sampling) works
- When to use different sampling configurations
- Real-world applications of sampling strategies

Prerequisites:
- pip install anthropic python-dotenv
- Set ANTHROPIC_API_KEY in .env file

Author: Neural Dojo
Date: 2025-11-21
"""

import anthropic
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from dataclasses import dataclass
import time

# Load environment variables
load_dotenv()

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    name: str
    temperature: float
    top_p: float
    max_tokens: int
    description: str


def generate_with_config(
    prompt: str,
    config: GenerationConfig,
    num_samples: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate multiple samples with the same configuration.

    Args:
        prompt: The prompt to use
        config: Generation configuration
        num_samples: Number of samples to generate

    Returns:
        List of generation results with metadata
    """
    results = []

    print(f"\n{'='*70}")
    print(f"Configuration: {config.name}")
    print(f"{'='*70}")
    print(f"Temperature: {config.temperature}")
    print(f"Top-p: {config.top_p}")
    print(f"Max tokens: {config.max_tokens}")
    print(f"Description: {config.description}")
    print(f"\nGenerating {num_samples} samples...\n")

    for i in range(num_samples):
        start_time = time.time()

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        elapsed = time.time() - start_time
        text = response.content[0].text

        result = {
            "config": config.name,
            "sample_num": i + 1,
            "text": text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "latency_ms": round(elapsed * 1000, 2)
        }

        results.append(result)

        print(f"Sample {i+1}:")
        print(f"  {text}")
        print(f"  (Tokens: {response.usage.output_tokens}, Latency: {elapsed*1000:.0f}ms)")
        print()

    return results


def demo_temperature_effect():
    """Demonstrate how temperature affects generation."""

    print("\n" + "="*70)
    print("DEMO 1: TEMPERATURE EFFECT")
    print("="*70)
    print("\nPrompt: 'Explain photosynthesis in one sentence.'")
    print("\nWe'll generate 3 samples at each temperature to see variation.")

    prompt = "Explain photosynthesis in one sentence."

    configs = [
        GenerationConfig(
            name="Deterministic (T=0.0)",
            temperature=0.0,
            top_p=1.0,
            max_tokens=100,
            description="Always picks highest probability - same output every time"
        ),
        GenerationConfig(
            name="Focused (T=0.3)",
            temperature=0.3,
            top_p=1.0,
            max_tokens=100,
            description="Very focused, minimal variation"
        ),
        GenerationConfig(
            name="Balanced (T=0.7)",
            temperature=0.7,
            top_p=1.0,
            max_tokens=100,
            description="Balanced creativity and consistency"
        ),
        GenerationConfig(
            name="Creative (T=1.0)",
            temperature=1.0,
            top_p=1.0,
            max_tokens=100,
            description="More creative and varied outputs"
        ),
    ]

    all_results = []
    for config in configs:
        results = generate_with_config(prompt, config, num_samples=3)
        all_results.extend(results)

    # Analyze variation
    print(f"\n{'='*70}")
    print("ANALYSIS: Variation by Temperature")
    print(f"{'='*70}\n")

    configs_dict = {}
    for result in all_results:
        config_name = result["config"]
        if config_name not in configs_dict:
            configs_dict[config_name] = []
        configs_dict[config_name].append(result["text"])

    for config_name, texts in configs_dict.items():
        unique_count = len(set(texts))
        print(f"{config_name}:")
        print(f"  Unique outputs: {unique_count}/3")
        if unique_count == 1:
            print(f"  ✅ Deterministic - same every time")
        elif unique_count == 2:
            print(f"  🟡 Low variation")
        else:
            print(f"  🟢 High variation - different outputs")
        print()


def demo_top_p_effect():
    """Demonstrate how top-p (nucleus sampling) affects generation."""

    print("\n" + "="*70)
    print("DEMO 2: TOP-P (NUCLEUS SAMPLING) EFFECT")
    print("="*70)
    print("\nPrompt: 'The weather today is'")
    print("\nWith temperature=1.0, varying top-p to see filtering effect.")

    prompt = "The weather today is"

    configs = [
        GenerationConfig(
            name="No filtering (top-p=1.0)",
            temperature=1.0,
            top_p=1.0,
            max_tokens=50,
            description="All tokens considered - can include unlikely ones"
        ),
        GenerationConfig(
            name="Moderate filtering (top-p=0.9)",
            temperature=1.0,
            top_p=0.9,
            max_tokens=50,
            description="Top 90% probability mass - filters out tail"
        ),
        GenerationConfig(
            name="Strong filtering (top-p=0.5)",
            temperature=1.0,
            top_p=0.5,
            max_tokens=50,
            description="Top 50% probability mass - very focused"
        ),
    ]

    for config in configs:
        generate_with_config(prompt, config, num_samples=3)


def demo_use_case_chatbot():
    """Demonstrate sampling configuration for chatbot responses."""

    print("\n" + "="*70)
    print("DEMO 3: USE CASE - CHATBOT RESPONSES")
    print("="*70)
    print("\nGoal: Natural, helpful, varied but sensible responses")

    prompt = """You are a helpful assistant. A user asks: "What's the best way to learn Python?"

Provide a concise, helpful response."""

    config = GenerationConfig(
        name="Chatbot (Balanced)",
        temperature=0.7,
        top_p=0.9,
        max_tokens=200,
        description="Natural variation without weirdness"
    )

    generate_with_config(prompt, config, num_samples=3)


def demo_use_case_code_generation():
    """Demonstrate sampling configuration for code generation."""

    print("\n" + "="*70)
    print("DEMO 4: USE CASE - CODE GENERATION")
    print("="*70)
    print("\nGoal: Correct, consistent code")

    prompt = """Write a Python function that calculates the factorial of a number using recursion.

Include docstring and type hints."""

    config = GenerationConfig(
        name="Code Generation (Focused)",
        temperature=0.2,
        top_p=0.5,
        max_tokens=300,
        description="High consistency, minimal variation"
    )

    generate_with_config(prompt, config, num_samples=3)

    print("\n💡 Note: Outputs are very similar! This ensures code correctness.")


def demo_use_case_creative_writing():
    """Demonstrate sampling configuration for creative writing."""

    print("\n" + "="*70)
    print("DEMO 5: USE CASE - CREATIVE WRITING")
    print("="*70)
    print("\nGoal: Interesting, surprising, varied narratives")

    prompt = """Write the opening sentence of a science fiction story about a robot who discovers emotions."""

    config = GenerationConfig(
        name="Creative Writing",
        temperature=1.0,
        top_p=0.95,
        max_tokens=150,
        description="Creative freedom with sensible filtering"
    )

    generate_with_config(prompt, config, num_samples=3)

    print("\n💡 Note: Each opening is unique and creative!")


def demo_use_case_json_extraction():
    """Demonstrate sampling configuration for structured data extraction."""

    print("\n" + "="*70)
    print("DEMO 6: USE CASE - JSON EXTRACTION")
    print("="*70)
    print("\nGoal: Valid JSON, consistent format")

    prompt = """Extract the person, organization, and location from this text as JSON:

"Apple CEO Tim Cook announced new products in Cupertino."

Return only the JSON, no explanation."""

    config = GenerationConfig(
        name="JSON Extraction (Deterministic)",
        temperature=0.0,
        top_p=1.0,
        max_tokens=200,
        description="Deterministic - critical for structured data!"
    )

    results = generate_with_config(prompt, config, num_samples=3)

    # Check if all outputs are identical
    texts = [r["text"] for r in results]
    if len(set(texts)) == 1:
        print("\n✅ Perfect! All 3 outputs are identical.")
        print("   This is crucial for structured data extraction.")
    else:
        print("\n⚠️  Warning: Outputs varied (unusual for temperature=0.0)")


def compare_configurations_side_by_side():
    """Compare different configurations side-by-side."""

    print("\n" + "="*70)
    print("DEMO 7: SIDE-BY-SIDE COMPARISON")
    print("="*70)
    print("\nPrompt: 'The benefits of artificial intelligence include'")

    prompt = "The benefits of artificial intelligence include"

    configs = [
        GenerationConfig("Deterministic (T=0.0)", 0.0, 1.0, 100, "Same every time"),
        GenerationConfig("Balanced (T=0.7)", 0.7, 0.9, 100, "Natural variation"),
        GenerationConfig("Creative (T=1.0)", 1.0, 0.95, 100, "Maximum creativity"),
    ]

    all_results = {}
    for config in configs:
        results = generate_with_config(prompt, config, num_samples=1)
        all_results[config.name] = results[0]["text"]

    print(f"\n{'='*70}")
    print("SIDE-BY-SIDE COMPARISON")
    print(f"{'='*70}\n")

    for config_name, text in all_results.items():
        print(f"{config_name}:")
        print(f"  {text[:200]}{'...' if len(text) > 200 else ''}")
        print()


def sampling_strategy_guide():
    """Print a guide for choosing sampling strategies."""

    print("\n" + "="*70)
    print("SAMPLING STRATEGY GUIDE")
    print("="*70)

    strategies = [
        {
            "use_case": "Code Generation",
            "temp": "0.2",
            "top_p": "0.5",
            "why": "Need consistency and correctness"
        },
        {
            "use_case": "JSON Extraction",
            "temp": "0.0",
            "top_p": "1.0",
            "why": "Need deterministic outputs"
        },
        {
            "use_case": "Chatbot",
            "temp": "0.7",
            "top_p": "0.9",
            "why": "Balance natural variation with quality"
        },
        {
            "use_case": "Creative Writing",
            "temp": "1.0",
            "top_p": "0.95",
            "why": "Want creativity, filter nonsense"
        },
        {
            "use_case": "Brainstorming",
            "temp": "1.2",
            "top_p": "0.95",
            "why": "Push into creative territory"
        },
        {
            "use_case": "Summarization",
            "temp": "0.3",
            "top_p": "0.7",
            "why": "Need focused, consistent summaries"
        },
        {
            "use_case": "Translation",
            "temp": "0.3",
            "top_p": "0.8",
            "why": "Need accuracy, minimal creativity"
        },
    ]

    print(f"\n{'Use Case':<20} {'Temp':<8} {'Top-p':<8} {'Why'}")
    print("-"*70)

    for strategy in strategies:
        print(f"{strategy['use_case']:<20} {strategy['temp']:<8} {strategy['top_p']:<8} {strategy['why']}")

    print("-"*70)
    print("\nKey Principles:")
    print("  • Lower temperature (0.0-0.3) = More consistent, focused")
    print("  • Medium temperature (0.5-0.8) = Balanced")
    print("  • Higher temperature (0.9-1.2) = More creative, varied")
    print("  • Top-p 0.9-0.95 is a good default (filters nonsense)")
    print("  • Use temperature=0.0 for deterministic outputs")


def main():
    """Run all sampling demonstrations."""

    print("\n🎲 MODULE 8: SAMPLING STRATEGY PLAYGROUND")
    print("="*70)
    print("\nThis example demonstrates how sampling strategies affect generation.")
    print("You'll see real outputs from Claude with different configurations.")
    print("\n⚠️  Note: This uses the Claude API and will consume tokens!")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("   Please create a .env file with your API key:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        return

    # Run demos
    demo_temperature_effect()
    demo_top_p_effect()
    demo_use_case_chatbot()
    demo_use_case_code_generation()
    demo_use_case_creative_writing()
    demo_use_case_json_extraction()
    compare_configurations_side_by_side()
    sampling_strategy_guide()

    print("\n\n✅ SAMPLING PLAYGROUND COMPLETE!")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Temperature controls creativity (0.0 = deterministic, 1.0+ = creative)")
    print("  2. Top-p filters unlikely tokens (0.9 is a good default)")
    print("  3. Different use cases need different strategies")
    print("  4. There's no one-size-fits-all configuration")
    print("  5. Experiment to find what works for your use case!")
    print("\n🥋 Neural Dojo - Master sampling, control generation! 🧠⚡")


if __name__ == "__main__":
    main()
