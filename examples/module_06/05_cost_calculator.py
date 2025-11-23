#!/usr/bin/env python3
"""
Module 6: LLM Cost Calculator

Calculate costs for different LLM providers based on your usage patterns.
Helps you budget for production deployments.

THEORY CONNECTION:
- Module 6 Section: "Cost Considerations" (line 498+)
- Key Concept: Cost varies 100x between models
- What you'll learn: How to budget for LLM APIs

KEY INSIGHT: At scale, cost matters more than you think!
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class Provider(Enum):
    """LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass
class Model:
    """LLM model with pricing."""
    name: str
    provider: Provider
    context_window: int  # tokens
    input_price_per_1m: float  # USD per 1M input tokens
    output_price_per_1m: float  # USD per 1M output tokens


# Model catalog (prices as of 2024-2025)
MODELS = {
    # OpenAI
    "gpt-3.5-turbo": Model("GPT-3.5 Turbo", Provider.OPENAI, 16_000, 0.50, 1.50),
    "gpt-4-turbo": Model("GPT-4 Turbo", Provider.OPENAI, 128_000, 10.00, 30.00),
    "gpt-4": Model("GPT-4", Provider.OPENAI, 8_000, 30.00, 60.00),

    # Anthropic
    "claude-3-haiku": Model("Claude 3 Haiku", Provider.ANTHROPIC, 200_000, 0.25, 1.25),
    "claude-3-sonnet": Model("Claude 3 Sonnet", Provider.ANTHROPIC, 200_000, 3.00, 15.00),
    "claude-3.5-sonnet": Model("Claude 3.5 Sonnet", Provider.ANTHROPIC, 200_000, 3.00, 15.00),
    "claude-3-opus": Model("Claude 3 Opus", Provider.ANTHROPIC, 200_000, 15.00, 75.00),

    # Google
    "gemini-pro": Model("Gemini Pro", Provider.GOOGLE, 32_000, 0.50, 1.50),
    "gemini-1.5-pro": Model("Gemini 1.5 Pro", Provider.GOOGLE, 1_000_000, 3.50, 10.50),
}


@dataclass
class UsagePattern:
    """Expected usage pattern for cost estimation."""
    name: str
    requests_per_day: int
    avg_input_tokens: int
    avg_output_tokens: int


class CostCalculator:
    """Calculate costs for different usage patterns."""

    def calculate_daily_cost(
        self,
        model: Model,
        requests: int,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate daily cost for a model."""
        total_input_tokens = requests * input_tokens
        total_output_tokens = requests * output_tokens

        input_cost = (total_input_tokens / 1_000_000) * model.input_price_per_1m
        output_cost = (total_output_tokens / 1_000_000) * model.output_price_per_1m

        return input_cost + output_cost

    def calculate_monthly_cost(
        self,
        model: Model,
        requests: int,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate monthly cost (30 days)."""
        return self.calculate_daily_cost(model, requests, input_tokens, output_tokens) * 30

    def compare_models(
        self,
        usage: UsagePattern,
        models: List[str],
    ) -> Dict[str, Dict[str, float]]:
        """Compare costs across multiple models."""
        results = {}

        for model_name in models:
            if model_name not in MODELS:
                continue

            model = MODELS[model_name]

            daily_cost = self.calculate_daily_cost(
                model,
                usage.requests_per_day,
                usage.avg_input_tokens,
                usage.avg_output_tokens,
            )

            monthly_cost = daily_cost * 30
            yearly_cost = daily_cost * 365

            results[model_name] = {
                "daily": daily_cost,
                "monthly": monthly_cost,
                "yearly": yearly_cost,
                "context_window": model.context_window,
            }

        return results


def main():
    """Demonstrate cost calculation."""
    print("=" * 80)
    print("MODULE 6: LLM COST CALCULATOR")
    print("=" * 80)

    calculator = CostCalculator()

    # Use Case 1: Customer Support Chatbot
    print("\n📊 Use Case 1: Customer Support Chatbot")
    print("-" * 80)

    support_bot = UsagePattern(
        name="Support Chatbot",
        requests_per_day=10_000,  # 10K conversations/day
        avg_input_tokens=200,  # Question + history
        avg_output_tokens=150,  # Answer
    )

    print(f"Usage: {support_bot.requests_per_day:,} requests/day")
    print(f"Input: {support_bot.avg_input_tokens} tokens/request")
    print(f"Output: {support_bot.avg_output_tokens} tokens/request")

    models_to_compare = [
        "gpt-3.5-turbo",
        "gpt-4-turbo",
        "claude-3-haiku",
        "claude-3.5-sonnet",
        "gemini-pro",
    ]

    results = calculator.compare_models(support_bot, models_to_compare)

    print("\n💰 Cost Comparison:")
    print(f"{'Model':<25} {'Daily':<15} {'Monthly':<15} {'Yearly':<15}")
    print("-" * 80)

    for model_name, costs in sorted(results.items(), key=lambda x: x[1]['monthly']):
        print(
            f"{model_name:<25} "
            f"${costs['daily']:>7.2f}       "
            f"${costs['monthly']:>8,.2f}      "
            f"${costs['yearly']:>10,.2f}"
        )

    # Find cheapest and most expensive
    cheapest = min(results.items(), key=lambda x: x[1]['monthly'])
    expensive = max(results.items(), key=lambda x: x[1]['monthly'])

    print(f"\n🏆 Cheapest: {cheapest[0]} (${cheapest[1]['monthly']:.2f}/month)")
    print(f"💸 Most expensive: {expensive[0]} (${expensive[1]['monthly']:.2f}/month)")
    print(f"💡 Savings: ${expensive[1]['monthly'] - cheapest[1]['monthly']:.2f}/month")

    # Use Case 2: Code Assistant
    print("\n\n📊 Use Case 2: AI Code Assistant")
    print("-" * 80)

    code_assistant = UsagePattern(
        name="Code Assistant",
        requests_per_day=1_000,  # 1K code generations/day
        avg_input_tokens=500,  # Code context + instructions
        avg_output_tokens=800,  # Generated code
    )

    print(f"Usage: {code_assistant.requests_per_day:,} requests/day")
    print(f"Input: {code_assistant.avg_input_tokens} tokens/request")
    print(f"Output: {code_assistant.avg_output_tokens} tokens/request")

    results2 = calculator.compare_models(code_assistant, models_to_compare)

    print("\n💰 Cost Comparison:")
    print(f"{'Model':<25} {'Daily':<15} {'Monthly':<15}")
    print("-" * 80)

    for model_name, costs in sorted(results2.items(), key=lambda x: x[1]['monthly']):
        print(
            f"{model_name:<25} "
            f"${costs['daily']:>7.2f}       "
            f"${costs['monthly']:>8,.2f}"
        )

    # Use Case 3: Document Summarization (Long Context)
    print("\n\n📊 Use Case 3: Document Summarization (Long Context)")
    print("-" * 80)

    summarization = UsagePattern(
        name="Document Summarization",
        requests_per_day=100,  # 100 docs/day
        avg_input_tokens=50_000,  # Long documents!
        avg_output_tokens=500,  # Summary
    )

    print(f"Usage: {summarization.requests_per_day:,} requests/day")
    print(f"Input: {summarization.avg_input_tokens:,} tokens/request (long context!)")
    print(f"Output: {summarization.avg_output_tokens} tokens/request")

    # Filter models by context window
    long_context_models = [
        name for name in models_to_compare
        if MODELS[name].context_window >= summarization.avg_input_tokens
    ]

    print(f"\n⚠️  Only {len(long_context_models)} models support {summarization.avg_input_tokens:,} token context:")
    print(f"   {', '.join(long_context_models)}")

    results3 = calculator.compare_models(summarization, long_context_models)

    print("\n💰 Cost Comparison:")
    print(f"{'Model':<25} {'Daily':<15} {'Monthly':<15} {'Context Window':<20}")
    print("-" * 80)

    for model_name, costs in sorted(results3.items(), key=lambda x: x[1]['monthly']):
        print(
            f"{model_name:<25} "
            f"${costs['daily']:>7.2f}       "
            f"${costs['monthly']:>8,.2f}      "
            f"{costs['context_window']:>12,} tokens"
        )

    # Break-even analysis
    print("\n\n📈 BREAK-EVEN ANALYSIS: Self-hosting vs API")
    print("=" * 80)

    print("\nScenario: Running Llama 2 70B on your own infrastructure")
    print("")
    print("Hardware costs:")
    print("  - GPU: 4x A100 (80GB) = ~$40,000 one-time")
    print("  - Or cloud: ~$10/hour = ~$7,200/month")
    print("")
    print("API costs (Claude 3 Haiku at 10K requests/day):")

    haiku_monthly = results['claude-3-haiku']['monthly']
    print(f"  - API: ${haiku_monthly:.2f}/month")
    print("")
    print("Break-even analysis:")
    print(f"  - Cloud GPU: Break-even at ~{(7200 / haiku_monthly):.1f}x current volume")
    print(f"  - Own hardware: Pays off after {(40000 / haiku_monthly):.0f} months at current volume")

    # Key insights
    print("\n\n💡 KEY INSIGHTS:")
    print("=" * 80)
    print("1. Cost varies 100x between models:")
    print(f"   - Cheapest (Haiku): ${results['claude-3-haiku']['monthly']:.2f}/month")
    print(f"   - Most expensive (GPT-4): ${results.get('gpt-4', results['gpt-4-turbo'])['monthly']:.2f}/month")
    print("")
    print("2. Output tokens cost more:")
    print("   - Input: $0.25-30/1M tokens")
    print("   - Output: $1.25-75/1M tokens (up to 5x more!)")
    print("   - Tip: Be concise in responses!")
    print("")
    print("3. Long context is expensive:")
    print("   - 50K input tokens vs 500 tokens = 100x cost difference")
    print("   - Summarize when possible")
    print("   - Only include relevant context")
    print("")
    print("4. Volume matters:")
    print("   - <10K requests/day: Use APIs ($100-500/month)")
    print("   - 10K-100K/day: Still APIs, but optimize ($500-5K/month)")
    print("   - >100K/day: Consider self-hosting ($5K+/month)")
    print("")
    print("5. Smart routing saves money:")
    print("   - Simple queries → Haiku ($0.25/1M)")
    print("   - Complex reasoning → Sonnet ($3/1M)")
    print("   - Critical tasks → GPT-4 ($30/1M)")
    print("   - Save 50-80% with intelligent routing!")

    print("\n\n🎯 ACTION ITEMS:")
    print("=" * 80)
    print("1. Calculate YOUR actual usage:")
    print("   - How many requests/day?")
    print("   - Average input/output tokens?")
    print("   - Growth projections?")
    print("")
    print("2. Set cost budgets:")
    print("   - Alerts at 50%, 80%, 100% of budget")
    print("   - Track costs per user/feature")
    print("")
    print("3. Optimize:")
    print("   - Cache common responses")
    print("   - Use cheaper models when possible")
    print("   - Limit max tokens")
    print("   - Batch requests")
    print("")
    print("4. Monitor:")
    print("   - Daily spend")
    print("   - Cost per request")
    print("   - Anomalies (sudden spikes)")


if __name__ == "__main__":
    main()
