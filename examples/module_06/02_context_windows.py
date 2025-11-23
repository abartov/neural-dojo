#!/usr/bin/env python3
"""
Module 6: Context Window Experiments

Demonstrates how different context window sizes affect model performance.

THEORY CONNECTION:
- Module 6 Section: "Context Windows" (line 373+)
- Key Concept: Models have limited memory (context window)
- What you'll learn: When to use RAG vs long context

KEY INSIGHT: Larger context ≠ always better. Models can "get lost" in middle!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def test_with_context_size(context_text: str, question: str, model: str = "claude-sonnet-4-5-20250929"):
    """Test model with specific context size."""
    prompt = f"""
{context_text}

Question: {question}
Answer based ONLY on the context above.
"""

    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def generate_filler_text(size_kb: int) -> str:
    """Generate filler text of approximate size."""
    # 1 KB ≈ 750 tokens ≈ 1000 characters
    base_text = "The quick brown fox jumps over the lazy dog. " * 100
    return (base_text * (size_kb * 20))[:size_kb * 1000]


def main():
    """Demonstrate context window experiments."""
    print("=" * 60)
    print("MODULE 6: CONTEXT WINDOW EXPERIMENTS")
    print("=" * 60)

    # Experiment 1: Small context (easy)
    print("\n📝 Experiment 1: Small Context (2KB)")
    print("-" * 60)

    small_context = """
    Company: Acme Corp
    Founded: 2020
    CEO: Jane Smith
    Revenue: $50M
    Employees: 200
    """

    question1 = "Who is the CEO of Acme Corp?"

    answer1 = test_with_context_size(small_context, question1)
    print(f"Context size: ~0.2 KB")
    print(f"Question: {question1}")
    print(f"Answer: {answer1}")
    print("✅ Small context = Easy to answer")

    # Experiment 2: Medium context with info at beginning
    print("\n\n📝 Experiment 2: Medium Context - Info at Beginning")
    print("-" * 60)

    important_info_start = "The secret code is: ALPHA-2024."
    filler = generate_filler_text(10)  # 10 KB filler
    medium_context_start = important_info_start + "\n\n" + filler

    question2 = "What is the secret code?"

    print(f"Context size: ~10 KB")
    print(f"Important info: At the START")
    print(f"Question: {question2}")

    answer2 = test_with_context_size(medium_context_start, question2)
    print(f"Answer: {answer2}")
    print("✅ Info at start = Easy to retrieve (recency bias)")

    # Experiment 3: Medium context with info at end
    print("\n\n📝 Experiment 3: Medium Context - Info at End")
    print("-" * 60)

    important_info_end = "The secret code is: BETA-2024."
    medium_context_end = filler + "\n\n" + important_info_end

    print(f"Context size: ~10 KB")
    print(f"Important info: At the END")
    print(f"Question: {question2}")

    answer3 = test_with_context_size(medium_context_end, question2)
    print(f"Answer: {answer3}")
    print("✅ Info at end = Also easy to retrieve (recency bias)")

    # Experiment 4: Large context with info in middle (THE HARD ONE!)
    print("\n\n📝 Experiment 4: Large Context - Info in MIDDLE")
    print("-" * 60)

    filler_before = generate_filler_text(20)  # 20 KB before
    important_info_middle = "The secret code is: GAMMA-2024."
    filler_after = generate_filler_text(20)  # 20 KB after

    large_context_middle = filler_before + "\n\n" + important_info_middle + "\n\n" + filler_after

    print(f"Context size: ~40 KB")
    print(f"Important info: In the MIDDLE (buried!)")
    print(f"Question: {question2}")

    answer4 = test_with_context_size(large_context_middle, question2)
    print(f"Answer: {answer4}")
    print("⚠️  Info in middle = Harder to retrieve (lost in the middle)")

    # Summary and lessons
    print("\n\n💡 KEY INSIGHTS:")
    print("=" * 60)
    print("1. Position Matters:")
    print("   - Start: ✅ Easy to find (primacy effect)")
    print("   - End: ✅ Easy to find (recency effect)")
    print("   - Middle: ⚠️ Can get lost!")
    print("")
    print("2. 'Lost in the Middle' Problem:")
    print("   - Paper: Liu et al. (2023)")
    print("   - Models pay less attention to middle of context")
    print("   - Even with 200K context window!")
    print("")
    print("3. Implications for RAG:")
    print("   - Put most relevant docs at START and END")
    print("   - Don't just dump everything in middle")
    print("   - Rank by relevance, place strategically")
    print("")
    print("4. Context Size Trade-offs:")
    print("   - Larger context = More cost")
    print("   - Larger context = Slower response")
    print("   - Larger context ≠ Better answers")
    print("")
    print("5. Best Practice:")
    print("   - Use ONLY as much context as needed")
    print("   - Put critical info at start or end")
    print("   - Summarize when possible")

    # Context window sizes comparison
    print("\n\n📊 CONTEXT WINDOW SIZES (2024-2025):")
    print("=" * 60)
    print("GPT-3.5:          16K tokens  (~12,000 words)")
    print("GPT-4:            128K tokens (~96,000 words)")
    print("Claude 3.5:       200K tokens (~150,000 words)")
    print("Gemini 1.5:       1M tokens   (~750,000 words)")
    print("Llama 2:          4K tokens   (~3,000 words)")
    print("")
    print("📖 1 token ≈ 0.75 words (English)")
    print("📖 Harry Potter Book 1: 77K words = ~100K tokens")
    print("📖 This Python file: ~5KB = ~4K tokens")

    print("\n\n🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Try changing the context sizes")
    print("2. Test with different models (GPT vs Claude)")
    print("3. Measure how answer quality degrades")
    print("4. Apply to your RAG system design")
    print("")
    print("📚 Read the paper:")
    print("   'Lost in the Middle' (Liu et al., 2023)")
    print("   https://arxiv.org/abs/2307.03172")


if __name__ == "__main__":
    main()
