#!/usr/bin/env python3
"""
Module 7 Example 3: Multilingual Tokenization

This example demonstrates how tokenization differs across languages.
You'll learn:
- How different languages are tokenized
- Why non-English text uses more tokens
- The impact on API costs for multilingual applications
- How to handle multilingual tokenization

Prerequisites:
- pip install tiktoken

Author: Neural Dojo
Date: 2025-11-21
"""

import tiktoken
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class MultilingualAnalysis:
    """Represents tokenization analysis for multilingual text."""
    language: str
    text: str
    english_translation: str
    char_count: int
    token_count: int
    chars_per_token: float
    efficiency_vs_english: float


def analyze_text(text: str, language: str, translation: str, model: str = "gpt-4") -> MultilingualAnalysis:
    """
    Analyze tokenization efficiency for a given text.

    Args:
        text: The text to analyze
        language: Language name
        translation: English translation
        model: Model to use for tokenization

    Returns:
        MultilingualAnalysis with detailed metrics
    """
    encoding = tiktoken.encoding_for_model(model)

    tokens = encoding.encode(text)
    english_tokens = encoding.encode(translation)

    char_count = len(text)
    token_count = len(tokens)
    chars_per_token = char_count / token_count if token_count > 0 else 0

    # Efficiency vs English (ratio of tokens)
    efficiency_vs_english = (token_count / len(english_tokens)) if len(english_tokens) > 0 else 1.0

    return MultilingualAnalysis(
        language=language,
        text=text,
        english_translation=translation,
        char_count=char_count,
        token_count=token_count,
        chars_per_token=round(chars_per_token, 2),
        efficiency_vs_english=round(efficiency_vs_english, 2)
    )


def compare_greetings() -> None:
    """Compare 'Hello' across different languages."""

    greetings = {
        "English": ("Hello", "Hello"),
        "Spanish": ("Hola", "Hello"),
        "French": ("Bonjour", "Hello"),
        "German": ("Guten Tag", "Hello"),
        "Italian": ("Ciao", "Hello"),
        "Portuguese": ("Olá", "Hello"),
        "Russian": ("Привет", "Hello"),
        "Japanese": ("こんにちは", "Hello"),
        "Chinese": ("你好", "Hello"),
        "Korean": ("안녕하세요", "Hello"),
        "Arabic": ("مرحبا", "Hello"),
        "Hindi": ("नमस्ते", "Hello"),
        "Hebrew": ("שלום", "Hello"),
        "Thai": ("สวัสดี", "Hello"),
        "Turkish": ("Merhaba", "Hello"),
    }

    print(f"\n{'='*70}")
    print(f"GREETING TOKENIZATION ACROSS LANGUAGES")
    print(f"{'='*70}")
    print(f"\n{'Language':<15} {'Text':<15} {'Chars':<8} {'Tokens':<8} {'Chars/Token':<12} {'vs English'}")
    print("-"*70)

    results = []
    for language, (text, translation) in greetings.items():
        analysis = analyze_text(text, language, translation)
        results.append(analysis)

        efficiency_indicator = "🟢" if analysis.efficiency_vs_english <= 1.5 else "🟡" if analysis.efficiency_vs_english <= 2.5 else "🔴"

        print(f"{language:<15} {text:<15} {analysis.char_count:<8} {analysis.token_count:<8} "
              f"{analysis.chars_per_token:<12.2f} {efficiency_indicator} {analysis.efficiency_vs_english}x")

    print("-"*70)
    print("\nKey Insights:")
    print("  🟢 Efficient: ≤1.5x tokens vs English (European languages)")
    print("  🟡 Moderate: 1.5-2.5x tokens vs English (Cyrillic, some Asian)")
    print("  🔴 Inefficient: >2.5x tokens vs English (CJK, some scripts)")
    print("\n  Why? Models trained primarily on English tokenize it most efficiently.")


def compare_sentences() -> None:
    """Compare full sentences across languages."""

    sentences = {
        "English": (
            "The quick brown fox jumps over the lazy dog.",
            "The quick brown fox jumps over the lazy dog."
        ),
        "Spanish": (
            "El rápido zorro marrón salta sobre el perro perezoso.",
            "The quick brown fox jumps over the lazy dog."
        ),
        "French": (
            "Le rapide renard brun saute par-dessus le chien paresseux.",
            "The quick brown fox jumps over the lazy dog."
        ),
        "German": (
            "Der schnelle braune Fuchs springt über den faulen Hund.",
            "The quick brown fox jumps over the lazy dog."
        ),
        "Russian": (
            "Быстрая коричневая лиса прыгает через ленивую собаку.",
            "The quick brown fox jumps over the lazy dog."
        ),
        "Japanese": (
            "素早い茶色のキツネが怠け者の犬を飛び越える。",
            "The quick brown fox jumps over the lazy dog."
        ),
        "Chinese": (
            "敏捷的棕色狐狸跳过懒狗。",
            "The quick brown fox jumps over the lazy dog."
        ),
        "Korean": (
            "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
            "The quick brown fox jumps over the lazy dog."
        ),
        "Arabic": (
            "الثعلب البني السريع يقفز فوق الكلب الكسول.",
            "The quick brown fox jumps over the lazy dog."
        ),
    }

    print(f"\n{'='*70}")
    print(f"SENTENCE TOKENIZATION ACROSS LANGUAGES")
    print(f"{'='*70}")
    print(f"\n{'Language':<15} {'Chars':<8} {'Tokens':<8} {'Chars/Token':<12} {'vs English':<12} {'Cost Impact'}")
    print("-"*70)

    for language, (text, translation) in sentences.items():
        analysis = analyze_text(text, language, translation)

        efficiency_indicator = "🟢" if analysis.efficiency_vs_english <= 1.5 else "🟡" if analysis.efficiency_vs_english <= 2.5 else "🔴"
        cost_multiplier = f"{analysis.efficiency_vs_english}x"

        print(f"{language:<15} {analysis.char_count:<8} {analysis.token_count:<8} "
              f"{analysis.chars_per_token:<12.2f} {efficiency_indicator} {analysis.efficiency_vs_english:<10}x {cost_multiplier}")

    print("-"*70)
    print("\nCost Impact Example (GPT-4 at $0.03/1K input tokens):")
    print("  1M requests in English: $X")
    print("  1M requests in Japanese: $2-3X (2-3x the cost!)")
    print("  1M requests in Arabic: $2X (2x the cost!)")


def demonstrate_code_vs_multilingual() -> None:
    """Compare code tokenization with multilingual text."""

    examples = {
        "English comment": (
            "# This function calculates the sum of two numbers",
            "comment"
        ),
        "Spanish comment": (
            "# Esta función calcula la suma de dos números",
            "comment"
        ),
        "Japanese comment": (
            "# この関数は2つの数値の合計を計算します",
            "comment"
        ),
        "Python code": (
            "def add(a, b):\n    return a + b",
            "code"
        ),
        "JavaScript code": (
            "function add(a, b) { return a + b; }",
            "code"
        ),
    }

    print(f"\n{'='*70}")
    print(f"CODE VS MULTILINGUAL TEXT TOKENIZATION")
    print(f"{'='*70}")
    print(f"\n{'Description':<25} {'Chars':<8} {'Tokens':<8} {'Chars/Token':<12} {'Efficiency'}")
    print("-"*70)

    encoding = tiktoken.encoding_for_model("gpt-4")

    for description, (text, text_type) in examples.items():
        tokens = encoding.encode(text)
        char_count = len(text)
        token_count = len(tokens)
        chars_per_token = char_count / token_count if token_count > 0 else 0

        if chars_per_token >= 4:
            efficiency = "🟢 Good"
        elif chars_per_token >= 2.5:
            efficiency = "🟡 Average"
        else:
            efficiency = "🔴 Poor"

        print(f"{description:<25} {char_count:<8} {token_count:<8} {chars_per_token:<12.2f} {efficiency}")

    print("-"*70)
    print("\nKey Insight:")
    print("  Multilingual comments in code = double penalty!")
    print("  • Code already uses more tokens than prose")
    print("  • Non-English comments use even more tokens")
    print("  • Consider English for code comments to reduce API costs")


def calculate_multilingual_costs() -> None:
    """Calculate API costs for multilingual applications."""

    print(f"\n{'='*70}")
    print(f"MULTILINGUAL API COST CALCULATOR")
    print(f"{'='*70}")

    # Scenario: Customer support chatbot
    avg_message_english = "How can I help you today?"
    avg_response_english = "I'd be happy to help! Please describe your issue."

    languages = {
        "English": (avg_message_english, avg_response_english),
        "Spanish": ("¿Cómo puedo ayudarte hoy?", "¡Estaré encantado de ayudarte! Por favor describe tu problema."),
        "Japanese": ("今日はどのようにお手伝いできますか？", "喜んでお手伝いします！問題を説明してください。"),
        "Arabic": ("كيف يمكنني مساعدتك اليوم؟", "يسعدني المساعدة! يرجى وصف مشكلتك."),
    }

    encoding = tiktoken.encoding_for_model("gpt-4")
    GPT4_INPUT_COST = 0.03  # per 1K tokens
    GPT4_OUTPUT_COST = 0.06  # per 1K tokens
    REQUESTS_PER_MONTH = 1_000_000

    print(f"\nScenario: Customer support chatbot (1M requests/month)")
    print(f"\n{'Language':<15} {'Input Tokens':<15} {'Output Tokens':<15} {'Cost/Request':<15} {'Monthly Cost'}")
    print("-"*70)

    english_cost = None

    for language, (message, response) in languages.items():
        input_tokens = len(encoding.encode(message))
        output_tokens = len(encoding.encode(response))

        cost_per_request = (input_tokens / 1000 * GPT4_INPUT_COST) + (output_tokens / 1000 * GPT4_OUTPUT_COST)
        monthly_cost = cost_per_request * REQUESTS_PER_MONTH

        if language == "English":
            english_cost = monthly_cost

        cost_vs_english = f"(+{((monthly_cost / english_cost - 1) * 100):.0f}%)" if english_cost and language != "English" else ""

        print(f"{language:<15} {input_tokens:<15} {output_tokens:<15} ${cost_per_request:<14.6f} "
              f"${monthly_cost:>11,.2f} {cost_vs_english}")

    print("-"*70)
    print("\nKey Takeaway:")
    print("  Non-English languages cost 50-150% more due to tokenization!")
    print("  Budget accordingly for multilingual applications.")


def best_practices_multilingual() -> None:
    """Print best practices for handling multilingual tokenization."""

    print(f"\n{'='*70}")
    print(f"BEST PRACTICES FOR MULTILINGUAL TOKENIZATION")
    print(f"{'='*70}")

    practices = {
        "1. Budget Appropriately": [
            "Expect 1.5-3x token usage for non-English",
            "Test token counts in all target languages",
            "Consider language-specific pricing tiers",
        ],
        "2. Choose Right Models": [
            "Use multilingual models (e.g., Llama, mBERT) for non-English",
            "SentencePiece tokenizers are more language-agnostic",
            "Consider language-specific models for high-volume languages",
        ],
        "3. Optimize Prompts": [
            "Non-English prompts benefit MORE from optimization",
            "Use language-appropriate abbreviations",
            "Consider providing context in English when possible",
        ],
        "4. Monitor Usage": [
            "Track token usage per language",
            "Identify languages with highest token/char ratios",
            "Optimize highest-cost languages first",
        ],
        "5. Testing": [
            "Test tokenization in all target languages before launch",
            "Measure actual costs in production",
            "Have fallback strategies for expensive languages",
        ],
    }

    for category, tips in practices.items():
        print(f"\n{category}:")
        for tip in tips:
            print(f"  • {tip}")


def demonstrate_emoji_and_special_chars() -> None:
    """Demonstrate tokenization of emoji and special characters."""

    print(f"\n{'='*70}")
    print(f"EMOJI & SPECIAL CHARACTER TOKENIZATION")
    print(f"{'='*70}")

    examples = {
        "Simple emoji": "😀",
        "Emoji sequence": "😀🌍🚀",
        "Emoji in text": "Hello 😀 World 🌍",
        "Flag (simple)": "🇺🇸",
        "Flag (complex)": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "Skin tone": "👋🏽",
        "ZWJ sequence": "👨‍👩‍👧‍👦",
        "Special chars": "© ® ™ € £ ¥",
        "Math symbols": "∑ ∫ ∂ ∇ ∞",
        "Arrows": "→ ← ↑ ↓ ⇒ ⇐",
    }

    encoding = tiktoken.encoding_for_model("gpt-4")

    print(f"\n{'Description':<20} {'Text':<20} {'Chars':<8} {'Tokens':<8} {'Chars/Token':<12} {'Efficiency'}")
    print("-"*70)

    for description, text in examples.items():
        tokens = encoding.encode(text)
        char_count = len(text)
        token_count = len(tokens)
        chars_per_token = char_count / token_count if token_count > 0 else 0

        efficiency = "🔴 Expensive!" if chars_per_token < 1.5 else "🟡 Moderate" if chars_per_token < 3 else "🟢 Good"

        print(f"{description:<20} {text:<20} {char_count:<8} {token_count:<8} {chars_per_token:<12.2f} {efficiency}")

    print("-"*70)
    print("\nKey Insight:")
    print("  Emoji can be VERY expensive in tokens!")
    print("  • Simple emoji: 1-2 tokens (moderate)")
    print("  • Complex emoji (flags, ZWJ): 5-10 tokens (expensive!)")
    print("  • Consider limiting emoji in high-volume applications")


def main():
    """Run all multilingual tokenization demonstrations."""

    print("\n🌍 MODULE 7: MULTILINGUAL TOKENIZATION")
    print("="*70)
    print("\nThis example demonstrates how tokenization differs across languages")
    print("and the cost implications for multilingual applications.")

    # Compare greetings
    print("\n\n👋 EXAMPLE 1: Greeting Tokenization")
    compare_greetings()

    # Compare sentences
    print("\n\n📝 EXAMPLE 2: Sentence Tokenization")
    compare_sentences()

    # Code vs multilingual
    print("\n\n💻 EXAMPLE 3: Code with Multilingual Comments")
    demonstrate_code_vs_multilingual()

    # Cost calculator
    print("\n\n💰 EXAMPLE 4: Multilingual Cost Analysis")
    calculate_multilingual_costs()

    # Emoji and special characters
    print("\n\n😀 EXAMPLE 5: Emoji & Special Characters")
    demonstrate_emoji_and_special_chars()

    # Best practices
    best_practices_multilingual()

    print("\n\n✅ MULTILINGUAL ANALYSIS COMPLETE!")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Non-English languages use 1.5-3x more tokens")
    print("  2. CJK languages (Chinese, Japanese, Korean) are least efficient")
    print("  3. European languages are moderately efficient")
    print("  4. Budget 2-3x API costs for multilingual apps")
    print("  5. Use multilingual models (Llama, mBERT) when possible")
    print("  6. Emoji can be surprisingly expensive (1-10 tokens!)")
    print("  7. Test tokenization in ALL target languages before launch")
    print("\n🥋 Neural Dojo - Think globally, tokenize locally! 🧠⚡")


if __name__ == "__main__":
    main()
