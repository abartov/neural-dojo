#!/usr/bin/env python3
"""
Module 7 Example 2: Token Optimization Strategies

This example demonstrates practical token optimization techniques.
You'll learn:
- How to reduce token counts without losing meaning
- Before/after comparison of optimization strategies
- Cost savings from optimization
- When optimization makes sense

Prerequisites:
- pip install tiktoken

Author: Neural Dojo
Date: 2025-11-21
"""

import tiktoken
from typing import Tuple, List, Dict
from dataclasses import dataclass
import json


@dataclass
class OptimizationResult:
    """Represents the result of a prompt optimization."""
    original: str
    optimized: str
    original_tokens: int
    optimized_tokens: int
    tokens_saved: int
    percent_saved: float
    cost_saved_per_1k_requests: float


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def calculate_savings(original_tokens: int, optimized_tokens: int) -> Tuple[int, float, float]:
    """
    Calculate token savings and cost impact.

    Args:
        original_tokens: Original token count
        optimized_tokens: Optimized token count

    Returns:
        Tuple of (tokens_saved, percent_saved, cost_saved_per_1k_requests)
    """
    tokens_saved = original_tokens - optimized_tokens
    percent_saved = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0

    # Assuming GPT-4 pricing: $0.03 per 1K input tokens
    GPT4_INPUT_COST_PER_1K = 0.03
    cost_saved_per_1k_requests = (tokens_saved / 1000) * GPT4_INPUT_COST_PER_1K * 1000

    return tokens_saved, percent_saved, cost_saved_per_1k_requests


def optimize_and_compare(original: str, optimized: str, strategy: str) -> OptimizationResult:
    """
    Compare original and optimized prompts.

    Args:
        original: Original prompt
        optimized: Optimized prompt
        strategy: Description of optimization strategy used

    Returns:
        OptimizationResult with detailed comparison
    """
    original_tokens = count_tokens(original)
    optimized_tokens = count_tokens(optimized)
    tokens_saved, percent_saved, cost_saved = calculate_savings(original_tokens, optimized_tokens)

    print(f"\n{'='*70}")
    print(f"STRATEGY: {strategy}")
    print(f"{'='*70}")
    print(f"\nOriginal ({original_tokens} tokens):")
    print(f"  \"{original[:100]}{'...' if len(original) > 100 else ''}\"")
    print(f"\nOptimized ({optimized_tokens} tokens):")
    print(f"  \"{optimized[:100]}{'...' if len(optimized) > 100 else ''}\"")
    print(f"\nSavings:")
    print(f"  📊 Tokens saved: {tokens_saved} ({percent_saved:.1f}%)")
    print(f"  💰 Cost saved: ${cost_saved:.2f} per 1K requests")
    print(f"  📈 Annual savings (1M requests): ${cost_saved * 1000:,.2f}")

    return OptimizationResult(
        original=original,
        optimized=optimized,
        original_tokens=original_tokens,
        optimized_tokens=optimized_tokens,
        tokens_saved=tokens_saved,
        percent_saved=percent_saved,
        cost_saved_per_1k_requests=cost_saved
    )


def strategy_1_remove_verbosity() -> OptimizationResult:
    """Strategy 1: Remove unnecessary verbosity."""

    original = """
    Could you please help me by writing a Python function that takes a list of numbers
    as input and returns the sum of all the numbers in that list? I would really
    appreciate if you could help me with this task.
    """

    optimized = """
    Write a Python function that sums a list of numbers.
    """

    return optimize_and_compare(original, optimized, "Remove Verbosity")


def strategy_2_minimize_system_prompt() -> OptimizationResult:
    """Strategy 2: Minimize system prompts."""

    original = """
    You are a helpful AI assistant created by Anthropic. You should always be polite,
    respectful, and informative. When answering questions, provide clear and concise
    responses. Always maintain a professional tone and be helpful to the user.
    """

    optimized = """
    You are a helpful assistant.
    """

    return optimize_and_compare(original, optimized, "Minimize System Prompt")


def strategy_3_efficient_formatting() -> OptimizationResult:
    """Strategy 3: Use efficient formatting."""

    # Pretty-printed JSON vs minified
    data = {"name": "John Doe", "age": 30, "city": "New York", "skills": ["Python", "JavaScript", "SQL"]}

    original = json.dumps(data, indent=2)
    optimized = json.dumps(data, separators=(',', ':'))

    return optimize_and_compare(original, optimized, "Efficient Formatting (JSON)")


def strategy_4_abbreviations() -> OptimizationResult:
    """Strategy 4: Use abbreviations carefully."""

    original = """
    Please analyze the following document and provide a comprehensive summary
    including the main points, key arguments, supporting evidence, and conclusions.
    """

    optimized = """
    Analyze and summarize: main points, key arguments, evidence, conclusions.
    """

    return optimize_and_compare(original, optimized, "Careful Abbreviations")


def strategy_5_batch_processing() -> OptimizationResult:
    """Strategy 5: Batch processing."""

    # Instead of 10 separate requests
    single_request_system = "You are a translator."  # 5 tokens
    single_request_user = "Translate to French: Hello"  # 5 tokens
    single_request_total = count_tokens(single_request_system + single_request_user)

    # Batch request
    batch_request = """You are a translator. Translate each to French:
1. Hello
2. Goodbye
3. Thank you
4. Please
5. Yes
6. No
7. Good morning
8. Good night
9. How are you?
10. See you later"""

    original_total_tokens = single_request_total * 10
    optimized_total_tokens = count_tokens(batch_request)

    print(f"\n{'='*70}")
    print(f"STRATEGY: Batch Processing")
    print(f"{'='*70}")
    print(f"\n10 Separate Requests:")
    print(f"  Each request: ~{single_request_total} tokens")
    print(f"  Total: {original_total_tokens} tokens")
    print(f"\n1 Batch Request:")
    print(f"  Total: {optimized_total_tokens} tokens")

    tokens_saved, percent_saved, cost_saved = calculate_savings(original_total_tokens, optimized_total_tokens)

    print(f"\nSavings:")
    print(f"  📊 Tokens saved: {tokens_saved} ({percent_saved:.1f}%)")
    print(f"  💰 Cost saved: ${cost_saved:.2f} per 1K requests")
    print(f"  📈 Annual savings (1M requests): ${cost_saved * 1000:,.2f}")

    return OptimizationResult(
        original=f"10 requests × {single_request_total} tokens",
        optimized=batch_request,
        original_tokens=original_total_tokens,
        optimized_tokens=optimized_total_tokens,
        tokens_saved=tokens_saved,
        percent_saved=percent_saved,
        cost_saved_per_1k_requests=cost_saved
    )


def strategy_6_remove_examples() -> OptimizationResult:
    """Strategy 6: Remove unnecessary examples when model can infer."""

    original = """
    Extract entities from the text. Return JSON with person, organization, and location.

    Examples:
    Input: "John works at Google in California"
    Output: {"person": ["John"], "organization": ["Google"], "location": ["California"]}

    Input: "Microsoft was founded by Bill Gates"
    Output: {"person": ["Bill Gates"], "organization": ["Microsoft"], "location": []}

    Now extract from: "Apple CEO Tim Cook announced new products in Cupertino."
    """

    optimized = """
    Extract entities (person, organization, location) as JSON:
    "Apple CEO Tim Cook announced new products in Cupertino."
    """

    return optimize_and_compare(original, optimized, "Remove Unnecessary Examples")


def demonstrate_real_world_optimization() -> None:
    """Demonstrate optimization on a real-world RAG prompt."""

    print(f"\n{'='*70}")
    print(f"REAL-WORLD EXAMPLE: RAG System Prompt Optimization")
    print(f"{'='*70}")

    original_rag_prompt = """
    You are an AI assistant that helps users by answering their questions based on
    the provided context. Please read the context carefully and provide accurate
    answers. If you cannot find the answer in the context, please say so honestly.
    Do not make up information that is not in the context.

    Context:
    {context}

    User Question:
    {question}

    Please provide your answer below:
    """

    optimized_rag_prompt = """
    Answer using only the context. If not found, say so.

    Context: {context}
    Question: {question}
    """

    # Simulate with actual context
    context = "Neural Dojo is a comprehensive AI curriculum. It covers LLMs, RAG, and deep learning."
    question = "What does Neural Dojo cover?"

    original_filled = original_rag_prompt.format(context=context, question=question)
    optimized_filled = optimized_rag_prompt.format(context=context, question=question)

    original_tokens = count_tokens(original_filled)
    optimized_tokens = count_tokens(optimized_filled)
    tokens_saved, percent_saved, cost_saved = calculate_savings(original_tokens, optimized_tokens)

    print(f"\nOriginal RAG prompt template: {count_tokens(original_rag_prompt)} tokens")
    print(f"Optimized RAG prompt template: {count_tokens(optimized_rag_prompt)} tokens")
    print(f"\nWith context filled in:")
    print(f"  Original: {original_tokens} tokens")
    print(f"  Optimized: {optimized_tokens} tokens")
    print(f"\nSavings per query:")
    print(f"  📊 Tokens saved: {tokens_saved} ({percent_saved:.1f}%)")
    print(f"  💰 Cost saved: ${(tokens_saved / 1000) * 0.03:.6f} per query")
    print(f"\nAt scale (1M queries/month):")
    print(f"  💰 Monthly savings: ${cost_saved * 1000:,.2f}")
    print(f"  💰 Annual savings: ${cost_saved * 12000:,.2f}")


def optimization_best_practices() -> None:
    """Print best practices for token optimization."""

    print(f"\n{'='*70}")
    print(f"TOKEN OPTIMIZATION BEST PRACTICES")
    print(f"{'='*70}")

    practices = [
        ("✅ DO optimize", [
            "Remove unnecessary politeness ('please', 'could you')",
            "Use minimal system prompts",
            "Minify JSON/structured data",
            "Batch similar requests",
            "Remove redundant examples",
            "Use clear, concise language",
        ]),
        ("❌ DON'T optimize", [
            "Critical instructions or constraints",
            "Domain-specific terminology",
            "Examples that improve accuracy",
            "Context needed for correct answers",
            "When clarity would be sacrificed",
        ]),
        ("⚖️ BALANCE", [
            "Token savings vs model performance",
            "Cost reduction vs output quality",
            "Brevity vs clarity",
            "Optimization effort vs actual savings",
        ]),
    ]

    for category, items in practices:
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")


def calculate_project_savings() -> None:
    """Calculate potential savings for different project types."""

    print(f"\n{'='*70}")
    print(f"PROJECT-SPECIFIC SAVINGS CALCULATOR")
    print(f"{'='*70}")

    projects = {
        "Chatbot (high volume)": {
            "requests_per_month": 1_000_000,
            "avg_prompt_tokens": 150,
            "optimization_potential": 30,  # 30% reduction
        },
        "RAG System (medium volume)": {
            "requests_per_month": 100_000,
            "avg_prompt_tokens": 800,
            "optimization_potential": 20,  # 20% reduction
        },
        "Code Generation (low volume)": {
            "requests_per_month": 10_000,
            "avg_prompt_tokens": 300,
            "optimization_potential": 25,  # 25% reduction
        },
    }

    GPT4_INPUT_COST_PER_1K = 0.03

    print(f"\n{'Project':<30} {'Monthly Requests':<18} {'Savings/Month':<15} {'Savings/Year'}")
    print("-"*70)

    for project_name, config in projects.items():
        original_cost = (config["requests_per_month"] * config["avg_prompt_tokens"] / 1000) * GPT4_INPUT_COST_PER_1K
        tokens_saved = config["avg_prompt_tokens"] * (config["optimization_potential"] / 100)
        cost_saved_monthly = (config["requests_per_month"] * tokens_saved / 1000) * GPT4_INPUT_COST_PER_1K
        cost_saved_yearly = cost_saved_monthly * 12

        print(f"{project_name:<30} {config['requests_per_month']:>15,}  ${cost_saved_monthly:>12,.2f}  ${cost_saved_yearly:>12,.2f}")

    print("-"*70)
    print("\nKey Insight:")
    print("  Even modest optimization (20-30%) can save thousands annually!")


def main():
    """Run all optimization demonstrations."""

    print("\n⚡ MODULE 7: TOKEN OPTIMIZATION STRATEGIES")
    print("="*70)
    print("\nThis example demonstrates practical token optimization techniques.")
    print("Learn how to reduce costs without sacrificing quality!")

    # Run optimization strategies
    results = []

    print("\n\n📝 OPTIMIZATION STRATEGIES")
    results.append(strategy_1_remove_verbosity())
    results.append(strategy_2_minimize_system_prompt())
    results.append(strategy_3_efficient_formatting())
    results.append(strategy_4_abbreviations())
    results.append(strategy_5_batch_processing())
    results.append(strategy_6_remove_examples())

    # Summary
    print(f"\n\n{'='*70}")
    print(f"OPTIMIZATION SUMMARY")
    print(f"{'='*70}")

    total_original = sum(r.original_tokens for r in results)
    total_optimized = sum(r.optimized_tokens for r in results)
    total_saved = total_original - total_optimized
    total_percent_saved = (total_saved / total_original * 100) if total_original > 0 else 0

    print(f"\nTotal across all strategies:")
    print(f"  Original: {total_original} tokens")
    print(f"  Optimized: {total_optimized} tokens")
    print(f"  Saved: {total_saved} tokens ({total_percent_saved:.1f}%)")
    print(f"\nCost impact (GPT-4 pricing):")
    print(f"  💰 Saved per 1K requests: ${(total_saved / 1000) * 0.03 * 1000:.2f}")
    print(f"  💰 Saved per 1M requests: ${(total_saved / 1000) * 0.03 * 1_000_000:,.2f}")

    # Real-world example
    demonstrate_real_world_optimization()

    # Best practices
    optimization_best_practices()

    # Project savings
    calculate_project_savings()

    print("\n\n✅ OPTIMIZATION COMPLETE!")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Remove unnecessary verbosity (30-50% savings)")
    print("  2. Minimize system prompts (60-70% savings)")
    print("  3. Use efficient formatting (30-40% savings for JSON)")
    print("  4. Batch similar requests (massive savings)")
    print("  5. Balance optimization with quality")
    print("  6. At scale, even small savings = big $$$")
    print("\n🥋 Neural Dojo - Optimize like a pro! 🧠⚡")


if __name__ == "__main__":
    main()
