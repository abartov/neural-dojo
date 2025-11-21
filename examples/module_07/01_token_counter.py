#!/usr/bin/env python3
"""
Module 7 Example 1: Token Counter Demonstration

This example demonstrates how to count tokens using tiktoken (OpenAI's tokenizer).
You'll learn:
- How to count tokens in text
- How different text types affect token counts
- Visualizing how text is split into tokens
- Practical token counting for API calls

Prerequisites:
- pip install tiktoken

Author: Neural Dojo
Date: 2025-11-21
"""

import tiktoken
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class TokenAnalysis:
    """Represents the analysis of tokenized text."""
    text: str
    token_count: int
    tokens: List[int]
    decoded_tokens: List[str]
    chars_per_token: float


def count_tokens(text: str, model: str = "gpt-4") -> TokenAnalysis:
    """
    Count tokens in text using tiktoken.

    Args:
        text: The text to tokenize
        model: The model to use for tokenization (default: gpt-4)

    Returns:
        TokenAnalysis with detailed token information

    Example:
        >>> analysis = count_tokens("Hello, world!")
        >>> print(f"Token count: {analysis.token_count}")
    """
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    decoded_tokens = [encoding.decode([t]) for t in tokens]

    chars_per_token = len(text) / len(tokens) if len(tokens) > 0 else 0

    return TokenAnalysis(
        text=text,
        token_count=len(tokens),
        tokens=tokens,
        decoded_tokens=decoded_tokens,
        chars_per_token=round(chars_per_token, 2)
    )


def visualize_tokens(text: str, model: str = "gpt-4") -> None:
    """
    Visualize how text is split into tokens.

    Args:
        text: The text to visualize
        model: The model to use for tokenization
    """
    analysis = count_tokens(text, model)

    print(f"\n{'='*70}")
    print(f"TEXT: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"{'='*70}")
    print(f"Token count: {analysis.token_count}")
    print(f"Character count: {len(text)}")
    print(f"Chars per token: {analysis.chars_per_token}")
    print(f"\nToken breakdown:")
    print("-" * 70)

    for i, (token_id, token_str) in enumerate(zip(analysis.tokens, analysis.decoded_tokens), 1):
        # Show token with visible whitespace
        display_str = token_str.replace(' ', '·').replace('\n', '↵').replace('\t', '→')
        print(f"  {i:3d}. [{token_id:5d}] '{display_str}'")

    print("-" * 70)


def compare_text_types() -> None:
    """Compare token counts across different text types."""

    examples = {
        "Simple English": "Hello, world!",
        "Longer sentence": "The quick brown fox jumps over the lazy dog.",
        "Repeated words": "Hello hello hello hello hello",
        "Repeated chars": "Hellooooooooooo",
        "Code snippet": "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "JSON data": '{"name": "John", "age": 30, "city": "New York"}',
        "Minified JSON": '{"name":"John","age":30,"city":"New York"}',
        "Numbers": "123456789 987654321 456789123",
        "Emoji": "Hello 😀 🌍 🚀",
        "Mixed case": "HELLO hello HeLLo",
    }

    print("\n" + "="*70)
    print("COMPARING TOKEN COUNTS ACROSS TEXT TYPES")
    print("="*70)
    print(f"{'Text Type':<20} {'Chars':<8} {'Tokens':<8} {'Chars/Token':<12} {'Efficiency'}")
    print("-"*70)

    results = []
    for name, text in examples.items():
        analysis = count_tokens(text)
        efficiency = "🟢 Good" if analysis.chars_per_token >= 4 else "🟡 Average" if analysis.chars_per_token >= 3 else "🔴 Poor"
        results.append((name, len(text), analysis.token_count, analysis.chars_per_token, efficiency))
        print(f"{name:<20} {len(text):<8} {analysis.token_count:<8} {analysis.chars_per_token:<12.2f} {efficiency}")

    print("-"*70)
    print("\nKey Insights:")
    print("  🟢 Good efficiency: ≥4 chars/token (typical for English prose)")
    print("  🟡 Average efficiency: 3-4 chars/token (code, special chars)")
    print("  🔴 Poor efficiency: <3 chars/token (emoji, repeated chars, some code)")


def estimate_api_cost(text: str, model: str = "gpt-4") -> Dict[str, float]:
    """
    Estimate API costs for a given text.

    Args:
        text: The text to analyze
        model: The model to use

    Returns:
        Dictionary with cost estimates for different models
    """
    analysis = count_tokens(text, model)

    # API pricing (as of 2024, per 1K tokens)
    pricing = {
        "GPT-3.5 Turbo": {"input": 0.0015, "output": 0.002},
        "GPT-4": {"input": 0.03, "output": 0.06},
        "GPT-4 Turbo": {"input": 0.01, "output": 0.03},
    }

    print(f"\n{'='*70}")
    print(f"API COST ESTIMATION")
    print(f"{'='*70}")
    print(f"Text: {text[:60]}{'...' if len(text) > 60 else ''}")
    print(f"Tokens: {analysis.token_count}")
    print(f"\nCost per request:")
    print("-"*70)
    print(f"{'Model':<20} {'Input Cost':<15} {'Output Cost':<15} {'Total (1:1)'}")
    print("-"*70)

    for model_name, costs in pricing.items():
        input_cost = (analysis.token_count / 1000) * costs["input"]
        output_cost = (analysis.token_count / 1000) * costs["output"]
        total_cost = input_cost + output_cost

        print(f"{model_name:<20} ${input_cost:>12.6f}  ${output_cost:>12.6f}  ${total_cost:>12.6f}")

    print("-"*70)
    print("\nCost at scale (1M requests/month):")
    print("-"*70)

    for model_name, costs in pricing.items():
        monthly_cost = ((analysis.token_count / 1000) * (costs["input"] + costs["output"]) * 1_000_000)
        print(f"  {model_name:<20} ${monthly_cost:>12,.2f}/month")

    print("-"*70)

    return pricing


def demonstrate_context_window_limits() -> None:
    """Demonstrate how token counting relates to context windows."""

    # Simulate a long document
    paragraph = """
    Large Language Models (LLMs) have revolutionized the field of natural language processing.
    These models, trained on vast amounts of text data, can generate human-like text, answer questions,
    translate languages, and perform a wide variety of other tasks. Understanding how tokens work
    is crucial for working effectively with LLMs.
    """

    context_windows = {
        "GPT-3.5": 16_000,
        "GPT-4": 8_000,
        "GPT-4 32K": 32_000,
        "GPT-4 Turbo": 128_000,
        "Claude 3.5 Sonnet": 200_000,
        "Gemini 1.5 Pro": 1_000_000,
    }

    analysis = count_tokens(paragraph * 100)  # Simulate a long document

    print(f"\n{'='*70}")
    print(f"CONTEXT WINDOW ANALYSIS")
    print(f"{'='*70}")
    print(f"Document tokens: {analysis.token_count:,}")
    print(f"\nHow many copies fit in each model's context window?")
    print("-"*70)
    print(f"{'Model':<25} {'Context Window':<15} {'Copies':<10} {'Usage %'}")
    print("-"*70)

    for model_name, window_size in context_windows.items():
        copies = window_size // analysis.token_count
        usage_pct = (analysis.token_count / window_size) * 100

        if usage_pct > 100:
            print(f"{model_name:<25} {window_size:>13,}  {'TOO BIG!':<10} {usage_pct:>6.1f}%")
        else:
            print(f"{model_name:<25} {window_size:>13,}  {copies:>8,}  {usage_pct:>6.1f}%")

    print("-"*70)
    print("\nKey Insight:")
    print("  Context window size dramatically affects what you can fit:")
    print(f"  - This {analysis.token_count:,}-token document fits {context_windows['GPT-4']//analysis.token_count}x in GPT-4")
    print(f"  - But {context_windows['Gemini 1.5 Pro']//analysis.token_count}x in Gemini 1.5 Pro!")


def main():
    """Run all token counting demonstrations."""

    print("\n🔢 MODULE 7: TOKEN COUNTER DEMONSTRATION")
    print("="*70)
    print("\nThis example demonstrates token counting with tiktoken.")
    print("You'll see how different texts are tokenized and learn to")
    print("estimate API costs and context window usage.")

    # Example 1: Basic token counting
    print("\n\n📝 EXAMPLE 1: Basic Token Counting")
    visualize_tokens("Hello, world!")

    # Example 2: Code tokenization
    print("\n\n💻 EXAMPLE 2: Code Tokenization")
    code = """def greet(name: str) -> str:
    return f"Hello, {name}!\""""
    visualize_tokens(code)

    # Example 3: Compare text types
    print("\n\n📊 EXAMPLE 3: Token Efficiency Comparison")
    compare_text_types()

    # Example 4: API cost estimation
    print("\n\n💰 EXAMPLE 4: API Cost Estimation")
    sample_prompt = """
    Analyze the following code and suggest improvements:

    def process_data(data):
        result = []
        for item in data:
            if item > 0:
                result.append(item * 2)
        return result
    """
    estimate_api_cost(sample_prompt)

    # Example 5: Context window analysis
    print("\n\n🪟 EXAMPLE 5: Context Window Limits")
    demonstrate_context_window_limits()

    print("\n\n✅ TOKEN COUNTING COMPLETE!")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Tokens ≠ words: 1 token ≈ 0.75 words (English)")
    print("  2. Code uses 3-4x more tokens than prose")
    print("  3. Token counting is essential for cost optimization")
    print("  4. Context windows vary dramatically (8K → 1M tokens)")
    print("  5. Always count tokens before making API calls!")
    print("\n🥋 Neural Dojo - Master the fundamentals! 🧠⚡")


if __name__ == "__main__":
    main()
