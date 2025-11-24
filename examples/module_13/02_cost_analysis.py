#!/usr/bin/env python3
"""
Module 13: RAG vs Fine-tuning Cost Analysis

This example provides detailed cost calculations for different approaches
to help you make data-driven decisions.

Features:
- Detailed cost breakdown for RAG, fine-tuning, and hybrid
- Comparison across different scale levels
- Break-even analysis
- Cost optimization recommendations

Usage:
    python 02_cost_analysis.py [scenario]

    Scenarios:
    - startup: 10K queries/month
    - growth: 100K queries/month
    - scale: 1M queries/month
    - enterprise: 10M queries/month

Author: Neural Dojo
"""

from dataclasses import dataclass
from typing import Optional
import sys


# 2025 Pricing (update as needed)
PRICING = {
    # GPT-4o pricing
    "gpt4o_input": 2.50,       # Per 1M tokens
    "gpt4o_output": 10.00,     # Per 1M tokens

    # GPT-4o fine-tuned pricing
    "gpt4o_ft_training": 25.00,  # Per 1M training tokens
    "gpt4o_ft_input": 3.75,      # Per 1M tokens (1.5x base)
    "gpt4o_ft_output": 15.00,    # Per 1M tokens (1.5x base)

    # Claude 3.5 Sonnet pricing
    "claude_sonnet_input": 3.00,   # Per 1M tokens
    "claude_sonnet_output": 15.00, # Per 1M tokens

    # Claude 3 Opus pricing
    "claude_opus_input": 15.00,    # Per 1M tokens
    "claude_opus_output": 75.00,   # Per 1M tokens

    # Embedding pricing
    "openai_embedding": 0.02,      # Per 1M tokens
    "voyage_embedding": 0.10,      # Per 1M tokens (higher quality)

    # Vector database pricing (monthly)
    "pinecone_starter": 0.00,      # Free tier (limited)
    "pinecone_standard": 70.00,    # Standard tier
    "pinecone_enterprise": 300.00, # Enterprise tier
    "qdrant_cloud_free": 0.00,     # Free tier
    "qdrant_cloud_starter": 25.00, # Starter tier
    "qdrant_cloud_pro": 100.00,    # Pro tier

    # LoRA fine-tuning (estimated)
    "lora_training_base": 50.00,   # Base cost
    "lora_per_example": 0.10,      # Per training example
    "lora_hosting": 0.00,          # Self-hosted or merged into base
}


@dataclass
class CostEstimate:
    """Detailed cost estimate."""
    approach: str
    monthly_cost: float
    one_time_cost: float
    llm_cost: float
    embedding_cost: float
    vector_db_cost: float
    training_cost: float
    details: dict


def calculate_rag_cost(
    monthly_queries: int,
    avg_input_tokens: int = 800,
    avg_output_tokens: int = 200,
    model: str = "gpt4o"
) -> CostEstimate:
    """Calculate detailed RAG costs."""
    # LLM costs
    input_tokens_total = monthly_queries * avg_input_tokens
    output_tokens_total = monthly_queries * avg_output_tokens

    if model == "gpt4o":
        llm_input_cost = input_tokens_total / 1_000_000 * PRICING["gpt4o_input"]
        llm_output_cost = output_tokens_total / 1_000_000 * PRICING["gpt4o_output"]
    elif model == "claude_sonnet":
        llm_input_cost = input_tokens_total / 1_000_000 * PRICING["claude_sonnet_input"]
        llm_output_cost = output_tokens_total / 1_000_000 * PRICING["claude_sonnet_output"]
    else:
        llm_input_cost = input_tokens_total / 1_000_000 * PRICING["gpt4o_input"]
        llm_output_cost = output_tokens_total / 1_000_000 * PRICING["gpt4o_output"]

    llm_cost = llm_input_cost + llm_output_cost

    # Embedding costs (for query embedding)
    query_tokens = monthly_queries * 100  # ~100 tokens per query
    embedding_cost = query_tokens / 1_000_000 * PRICING["openai_embedding"]

    # Vector database costs (scale-based)
    if monthly_queries < 50_000:
        vector_db_cost = PRICING["qdrant_cloud_free"]
    elif monthly_queries < 500_000:
        vector_db_cost = PRICING["pinecone_standard"]
    else:
        vector_db_cost = PRICING["pinecone_enterprise"]

    total_monthly = llm_cost + embedding_cost + vector_db_cost

    return CostEstimate(
        approach="RAG",
        monthly_cost=total_monthly,
        one_time_cost=0.0,
        llm_cost=llm_cost,
        embedding_cost=embedding_cost,
        vector_db_cost=vector_db_cost,
        training_cost=0.0,
        details={
            "llm_input_cost": llm_input_cost,
            "llm_output_cost": llm_output_cost,
            "input_tokens_millions": input_tokens_total / 1_000_000,
            "output_tokens_millions": output_tokens_total / 1_000_000,
            "model": model,
        }
    )


def calculate_finetuning_cost(
    monthly_queries: int,
    training_examples: int,
    avg_input_tokens: int = 500,  # Typically shorter without retrieval context
    avg_output_tokens: int = 200,
    model: str = "gpt4o"
) -> CostEstimate:
    """Calculate detailed fine-tuning costs."""
    # Training cost (one-time)
    training_tokens = training_examples * 500  # ~500 tokens per example
    training_cost = training_tokens / 1_000_000 * PRICING["gpt4o_ft_training"]

    # Inference costs (fine-tuned models cost more)
    input_tokens_total = monthly_queries * avg_input_tokens
    output_tokens_total = monthly_queries * avg_output_tokens

    if model == "gpt4o":
        llm_input_cost = input_tokens_total / 1_000_000 * PRICING["gpt4o_ft_input"]
        llm_output_cost = output_tokens_total / 1_000_000 * PRICING["gpt4o_ft_output"]
    else:
        # Assume similar multiplier for other providers
        llm_input_cost = input_tokens_total / 1_000_000 * PRICING["gpt4o_ft_input"]
        llm_output_cost = output_tokens_total / 1_000_000 * PRICING["gpt4o_ft_output"]

    llm_cost = llm_input_cost + llm_output_cost

    return CostEstimate(
        approach="Fine-tuning",
        monthly_cost=llm_cost,
        one_time_cost=training_cost,
        llm_cost=llm_cost,
        embedding_cost=0.0,
        vector_db_cost=0.0,
        training_cost=training_cost,
        details={
            "llm_input_cost": llm_input_cost,
            "llm_output_cost": llm_output_cost,
            "training_tokens_millions": training_tokens / 1_000_000,
            "input_tokens_millions": input_tokens_total / 1_000_000,
            "output_tokens_millions": output_tokens_total / 1_000_000,
            "model": f"{model}_finetuned",
        }
    )


def calculate_hybrid_cost(
    monthly_queries: int,
    training_examples: int,
    avg_input_tokens: int = 800,  # With retrieval context
    avg_output_tokens: int = 200,
    model: str = "gpt4o",
    use_lora: bool = True
) -> CostEstimate:
    """Calculate detailed hybrid costs (RAG + LoRA)."""
    # RAG component (base model pricing, not fine-tuned)
    rag_cost = calculate_rag_cost(monthly_queries, avg_input_tokens, avg_output_tokens, model)

    # LoRA training (much cheaper than full fine-tuning)
    if use_lora:
        training_cost = PRICING["lora_training_base"] + (training_examples * PRICING["lora_per_example"])
        training_cost = min(training_cost, 200.0)  # Cap at $200 for reasonable datasets
    else:
        # Full fine-tuning
        training_tokens = training_examples * 500
        training_cost = training_tokens / 1_000_000 * PRICING["gpt4o_ft_training"]

    return CostEstimate(
        approach="Hybrid (RAG + LoRA)" if use_lora else "Hybrid (RAG + Full FT)",
        monthly_cost=rag_cost.monthly_cost,
        one_time_cost=training_cost,
        llm_cost=rag_cost.llm_cost,
        embedding_cost=rag_cost.embedding_cost,
        vector_db_cost=rag_cost.vector_db_cost,
        training_cost=training_cost,
        details={
            **rag_cost.details,
            "lora": use_lora,
            "training_method": "LoRA" if use_lora else "Full fine-tuning",
        }
    )


def print_cost_comparison(
    monthly_queries: int,
    training_examples: int,
    title: str = "Cost Comparison"
) -> None:
    """Print a detailed cost comparison."""
    rag = calculate_rag_cost(monthly_queries)
    ft = calculate_finetuning_cost(monthly_queries, training_examples)
    hybrid = calculate_hybrid_cost(monthly_queries, training_examples)

    print("\n" + "=" * 80)
    print(f"  {title}")
    print(f"  {monthly_queries:,} queries/month | {training_examples:,} training examples")
    print("=" * 80)

    # Table header
    print(f"\n  {'Approach':<25} {'Monthly':>12} {'One-time':>12} {'Year 1 Total':>15}")
    print("  " + "-" * 66)

    # Calculate year 1 totals
    for cost in [rag, ft, hybrid]:
        year_1 = (cost.monthly_cost * 12) + cost.one_time_cost
        print(f"  {cost.approach:<25} ${cost.monthly_cost:>10,.2f} ${cost.one_time_cost:>10,.2f} ${year_1:>13,.2f}")

    print("  " + "-" * 66)

    # Winner
    costs = [rag, ft, hybrid]
    year_1_costs = [(c.monthly_cost * 12) + c.one_time_cost for c in costs]
    winner = costs[year_1_costs.index(min(year_1_costs))]

    print(f"\n  Winner (Year 1): {winner.approach}")
    savings = max(year_1_costs) - min(year_1_costs)
    print(f"  Potential Savings: ${savings:,.2f}/year")

    # Detailed breakdown
    print("\n" + "-" * 80)
    print("  DETAILED BREAKDOWN")
    print("-" * 80)

    for cost in [rag, ft, hybrid]:
        print(f"\n  {cost.approach}:")
        print(f"    LLM API:      ${cost.llm_cost:>10,.2f}/month")
        if cost.embedding_cost > 0:
            print(f"    Embeddings:   ${cost.embedding_cost:>10,.2f}/month")
        if cost.vector_db_cost > 0:
            print(f"    Vector DB:    ${cost.vector_db_cost:>10,.2f}/month")
        if cost.training_cost > 0:
            print(f"    Training:     ${cost.training_cost:>10,.2f} (one-time)")

    print("\n" + "=" * 80)


def break_even_analysis(training_examples: int) -> None:
    """Find the break-even point between approaches."""
    print("\n" + "=" * 80)
    print("  BREAK-EVEN ANALYSIS")
    print(f"  Training examples: {training_examples:,}")
    print("=" * 80)

    print(f"\n  Finding query volume where RAG becomes more cost-effective than fine-tuning...")

    # Test different query volumes
    query_volumes = [1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000]

    print(f"\n  {'Queries/Month':>15} {'RAG (Year 1)':>15} {'FT (Year 1)':>15} {'Winner':>10}")
    print("  " + "-" * 57)

    for queries in query_volumes:
        rag = calculate_rag_cost(queries)
        ft = calculate_finetuning_cost(queries, training_examples)

        rag_year1 = (rag.monthly_cost * 12)
        ft_year1 = (ft.monthly_cost * 12) + ft.one_time_cost

        winner = "RAG" if rag_year1 < ft_year1 else "FT"
        print(f"  {queries:>15,} ${rag_year1:>13,.2f} ${ft_year1:>13,.2f} {winner:>10}")

    print("\n  Note: Fine-tuned models have higher per-token costs but no retrieval overhead.")
    print("  RAG has lower per-token costs but adds embedding + vector DB costs.")
    print("=" * 80)


def optimization_recommendations(monthly_queries: int, training_examples: int) -> None:
    """Provide cost optimization recommendations."""
    print("\n" + "=" * 80)
    print("  COST OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)

    rag = calculate_rag_cost(monthly_queries)
    ft = calculate_finetuning_cost(monthly_queries, training_examples)
    hybrid = calculate_hybrid_cost(monthly_queries, training_examples)

    print("\n  General Recommendations:")

    # Model selection
    print("""
  1. MODEL SELECTION
     • Use GPT-4o or Claude 3.5 Sonnet for best cost/quality ratio
     • Avoid GPT-4 Turbo (3x more expensive, similar quality)
     • Consider Llama 3.1 70B for self-hosted (higher upfront, lower per-query)
    """)

    # RAG optimization
    if rag.monthly_cost > 1000:
        print("""
  2. RAG OPTIMIZATION
     • Cache common queries (can reduce costs 30-50%)
     • Use smaller embedding models (all-MiniLM-L6-v2 is free!)
     • Implement semantic caching (same question = same embedding)
     • Reduce chunk size to minimize context tokens
    """)

    # Fine-tuning optimization
    if ft.one_time_cost > 100:
        print("""
  3. FINE-TUNING OPTIMIZATION
     • Use LoRA instead of full fine-tuning (90% cost reduction)
     • Start with fewer examples, validate, then scale
     • Use QLoRA for even cheaper training
     • Consider open-source models (Llama, Mistral) for no training fees
    """)

    # Hybrid optimization
    print("""
  4. HYBRID OPTIMIZATION
     • Fine-tune only for style, use RAG for all knowledge
     • Use LoRA adapters (merge into base model for free inference)
     • Separate behavior training from knowledge retrieval
    """)

    # Scale-specific
    if monthly_queries > 500_000:
        print("""
  5. HIGH-VOLUME OPTIMIZATION
     • Negotiate enterprise pricing (can be 40-60% discount)
     • Consider batching requests for better throughput
     • Implement aggressive caching strategies
     • Explore self-hosted options (break-even at ~1M queries/month)
    """)

    print("=" * 80)


def scenario_startup() -> None:
    """Startup scenario: 10K queries/month."""
    print_cost_comparison(
        monthly_queries=10_000,
        training_examples=100,
        title="STARTUP SCENARIO"
    )


def scenario_growth() -> None:
    """Growth scenario: 100K queries/month."""
    print_cost_comparison(
        monthly_queries=100_000,
        training_examples=500,
        title="GROWTH SCENARIO"
    )


def scenario_scale() -> None:
    """Scale scenario: 1M queries/month."""
    print_cost_comparison(
        monthly_queries=1_000_000,
        training_examples=2000,
        title="SCALE SCENARIO"
    )


def scenario_enterprise() -> None:
    """Enterprise scenario: 10M queries/month."""
    print_cost_comparison(
        monthly_queries=10_000_000,
        training_examples=10000,
        title="ENTERPRISE SCENARIO"
    )


def main():
    """Run cost analysis."""
    print("\n" + "=" * 80)
    print("  MODULE 13: RAG vs FINE-TUNING COST ANALYSIS")
    print("=" * 80)
    print("""
  This tool calculates and compares costs for different AI customization
  approaches at various scale levels.

  Pricing based on 2025 rates:
  • GPT-4o: $2.50/1M input, $10/1M output
  • GPT-4o Fine-tuned: $3.75/1M input, $15/1M output
  • Embeddings: $0.02/1M tokens
  • Vector DB: $0-300/month (scale-dependent)
    """)

    # Check for scenario argument
    if len(sys.argv) > 1:
        scenario = sys.argv[1].lower()
        if scenario == "startup":
            scenario_startup()
        elif scenario == "growth":
            scenario_growth()
        elif scenario == "scale":
            scenario_scale()
        elif scenario == "enterprise":
            scenario_enterprise()
        elif scenario == "all":
            scenario_startup()
            scenario_growth()
            scenario_scale()
            scenario_enterprise()
        else:
            print(f"Unknown scenario: {scenario}")
            print("Available: startup, growth, scale, enterprise, all")
    else:
        # Run all scenarios
        scenario_startup()
        scenario_growth()
        scenario_scale()

        # Break-even analysis
        break_even_analysis(training_examples=500)

        # Optimization recommendations
        optimization_recommendations(
            monthly_queries=100_000,
            training_examples=500
        )

    print("\n  Run with specific scenario:")
    print("    python 02_cost_analysis.py startup")
    print("    python 02_cost_analysis.py growth")
    print("    python 02_cost_analysis.py scale")
    print("    python 02_cost_analysis.py enterprise")
    print("    python 02_cost_analysis.py all")


if __name__ == "__main__":
    main()
