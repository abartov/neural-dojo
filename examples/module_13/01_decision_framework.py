#!/usr/bin/env python3
"""
Module 13: RAG vs Fine-tuning Decision Framework

This example provides an interactive decision framework to help you
choose between RAG, fine-tuning, or a hybrid approach for your AI project.

The framework analyzes your specific use case and provides:
- Clear recommendation (RAG / Fine-tuning / Hybrid)
- Detailed reasoning
- Cost estimates
- Implementation suggestions

Usage:
    python 01_decision_framework.py

Author: Neural Dojo
"""

from dataclasses import dataclass, field
from typing import Literal
from enum import Enum


class KnowledgeUpdateFrequency(Enum):
    """How often does the knowledge change?"""
    REALTIME = "realtime"      # Changes multiple times per day
    DAILY = "daily"            # Changes daily
    WEEKLY = "weekly"          # Changes weekly
    MONTHLY = "monthly"        # Changes monthly
    YEARLY = "yearly"          # Changes yearly or less
    NEVER = "never"            # Static knowledge


class CitationRequirement(Enum):
    """Do you need to cite sources?"""
    REQUIRED = "required"      # Legal/compliance requirement
    PREFERRED = "preferred"    # Nice to have
    NOT_NEEDED = "not_needed"  # No citation needed


class StyleRequirement(Enum):
    """How important is specific style/behavior?"""
    CRITICAL = "critical"      # Must match exact style (brand voice, legal writing)
    IMPORTANT = "important"    # Style matters but flexible
    NICE_TO_HAVE = "nice"      # Would be nice but not required
    NOT_IMPORTANT = "none"     # No style requirements


class LatencyRequirement(Enum):
    """What's your latency tolerance?"""
    STRICT = "strict"          # < 100ms
    MODERATE = "moderate"      # < 500ms
    FLEXIBLE = "flexible"      # < 2s
    VERY_FLEXIBLE = "relaxed"  # > 2s is OK


@dataclass
class UseCase:
    """Represents a use case for AI customization."""
    name: str
    description: str
    knowledge_frequency: KnowledgeUpdateFrequency
    citation_requirement: CitationRequirement
    style_requirement: StyleRequirement
    latency_requirement: LatencyRequirement
    training_examples: int  # Number of high-quality examples available
    monthly_queries: int    # Expected queries per month
    corpus_size: int = 0    # Number of documents in knowledge base


@dataclass
class Recommendation:
    """Recommendation from the decision framework."""
    approach: Literal["RAG", "Fine-tuning", "Hybrid"]
    confidence: float  # 0.0 to 1.0
    reasoning: list[str]
    estimated_monthly_cost: float
    implementation_notes: list[str]
    risks: list[str]


@dataclass
class CostBreakdown:
    """Detailed cost breakdown."""
    llm_api_cost: float = 0.0
    embedding_cost: float = 0.0
    vector_db_cost: float = 0.0
    fine_tuning_cost: float = 0.0  # One-time
    fine_tuned_inference_cost: float = 0.0
    total_monthly: float = 0.0
    total_one_time: float = 0.0


def calculate_rag_cost(monthly_queries: int, avg_tokens: int = 1000) -> CostBreakdown:
    """Calculate costs for RAG approach."""
    # GPT-4o pricing (2025)
    llm_input_per_million = 2.50
    llm_output_per_million = 10.00
    embedding_per_million = 0.02

    # Assume 80% input, 20% output tokens
    input_tokens = monthly_queries * avg_tokens * 0.8
    output_tokens = monthly_queries * avg_tokens * 0.2

    llm_cost = (input_tokens / 1_000_000 * llm_input_per_million +
                output_tokens / 1_000_000 * llm_output_per_million)

    # Embedding cost (query embedding)
    embedding_tokens = monthly_queries * 100  # ~100 tokens per query
    embedding_cost = embedding_tokens / 1_000_000 * embedding_per_million

    # Vector DB (Pinecone starter)
    vector_db_cost = 70.0  # Monthly

    return CostBreakdown(
        llm_api_cost=llm_cost,
        embedding_cost=embedding_cost,
        vector_db_cost=vector_db_cost,
        total_monthly=llm_cost + embedding_cost + vector_db_cost,
        total_one_time=0.0
    )


def calculate_finetuning_cost(monthly_queries: int, training_examples: int,
                               avg_tokens: int = 1000) -> CostBreakdown:
    """Calculate costs for fine-tuning approach."""
    # Fine-tuned models cost more per token
    finetuned_input_per_million = 12.00  # ~4-5x base model
    finetuned_output_per_million = 24.00

    # Training cost (one-time)
    training_tokens = training_examples * 500  # ~500 tokens per example
    training_cost = training_tokens / 1_000_000 * 25.0  # $25/million training tokens

    # Inference cost
    input_tokens = monthly_queries * avg_tokens * 0.8
    output_tokens = monthly_queries * avg_tokens * 0.2

    inference_cost = (input_tokens / 1_000_000 * finetuned_input_per_million +
                      output_tokens / 1_000_000 * finetuned_output_per_million)

    return CostBreakdown(
        fine_tuning_cost=training_cost,
        fine_tuned_inference_cost=inference_cost,
        total_monthly=inference_cost,
        total_one_time=training_cost
    )


def calculate_hybrid_cost(monthly_queries: int, training_examples: int,
                          avg_tokens: int = 1000) -> CostBreakdown:
    """Calculate costs for hybrid approach (RAG + LoRA)."""
    rag_cost = calculate_rag_cost(monthly_queries, avg_tokens)

    # LoRA fine-tuning is much cheaper
    lora_training_cost = 50.0 + (training_examples * 0.1)  # Base + per example
    lora_training_cost = min(lora_training_cost, 200.0)  # Cap at $200

    return CostBreakdown(
        llm_api_cost=rag_cost.llm_api_cost,
        embedding_cost=rag_cost.embedding_cost,
        vector_db_cost=rag_cost.vector_db_cost,
        fine_tuning_cost=lora_training_cost,
        total_monthly=rag_cost.total_monthly,
        total_one_time=lora_training_cost
    )


def analyze_use_case(use_case: UseCase) -> Recommendation:
    """
    Analyze a use case and provide a recommendation.

    This is the core decision logic based on the framework from Module 13.
    """
    scores = {"RAG": 0.0, "Fine-tuning": 0.0, "Hybrid": 0.0}
    reasoning = []
    risks = []
    notes = []

    # Factor 1: Knowledge update frequency
    if use_case.knowledge_frequency in [KnowledgeUpdateFrequency.REALTIME,
                                        KnowledgeUpdateFrequency.DAILY,
                                        KnowledgeUpdateFrequency.WEEKLY]:
        scores["RAG"] += 3.0
        scores["Hybrid"] += 2.0
        reasoning.append(f"Knowledge changes {use_case.knowledge_frequency.value} - RAG provides dynamic updates")
    elif use_case.knowledge_frequency == KnowledgeUpdateFrequency.MONTHLY:
        scores["RAG"] += 1.5
        scores["Hybrid"] += 2.0
        scores["Fine-tuning"] += 1.0
        reasoning.append("Knowledge changes monthly - either approach viable")
    else:
        scores["Fine-tuning"] += 2.0
        scores["Hybrid"] += 1.5
        reasoning.append("Knowledge is stable - fine-tuning can encode it permanently")

    # Factor 2: Citation requirements
    if use_case.citation_requirement == CitationRequirement.REQUIRED:
        scores["RAG"] += 3.0
        scores["Hybrid"] += 2.5
        scores["Fine-tuning"] -= 1.0
        reasoning.append("Citations required - RAG provides natural source attribution")
        if scores["Fine-tuning"] > scores["RAG"]:
            risks.append("Fine-tuning alone cannot provide reliable citations!")
    elif use_case.citation_requirement == CitationRequirement.PREFERRED:
        scores["RAG"] += 1.5
        scores["Hybrid"] += 1.5
        reasoning.append("Citations preferred - RAG makes this easier")

    # Factor 3: Style requirements
    if use_case.style_requirement == StyleRequirement.CRITICAL:
        scores["Fine-tuning"] += 3.0
        scores["Hybrid"] += 3.0
        reasoning.append("Critical style requirements - fine-tuning ensures consistency")
        notes.append("Consider LoRA for cost-effective style adaptation")
    elif use_case.style_requirement == StyleRequirement.IMPORTANT:
        scores["Fine-tuning"] += 2.0
        scores["Hybrid"] += 2.5
        reasoning.append("Style is important - fine-tuning helps maintain voice")
    elif use_case.style_requirement == StyleRequirement.NICE_TO_HAVE:
        scores["RAG"] += 0.5
        scores["Fine-tuning"] += 1.0
        scores["Hybrid"] += 1.0
        reasoning.append("Style is nice-to-have - can achieve with good prompting")

    # Factor 4: Latency requirements
    if use_case.latency_requirement == LatencyRequirement.STRICT:
        scores["Fine-tuning"] += 2.5
        scores["RAG"] -= 1.0
        reasoning.append("Strict latency (<100ms) - fine-tuning avoids retrieval overhead")
        risks.append("RAG adds 100-500ms retrieval latency")
    elif use_case.latency_requirement == LatencyRequirement.MODERATE:
        scores["Fine-tuning"] += 1.0
        reasoning.append("Moderate latency requirements - both approaches viable")
    else:
        reasoning.append("Flexible latency - RAG overhead is acceptable")

    # Factor 5: Training data availability
    if use_case.training_examples < 50:
        scores["RAG"] += 2.0
        scores["Fine-tuning"] -= 2.0
        reasoning.append(f"Only {use_case.training_examples} examples - insufficient for fine-tuning")
        risks.append("Fine-tuning with <50 examples often fails to generalize")
    elif use_case.training_examples < 200:
        scores["Hybrid"] += 1.0
        reasoning.append(f"{use_case.training_examples} examples - suitable for LoRA fine-tuning")
        notes.append("Use LoRA/QLoRA for efficient fine-tuning with limited data")
    else:
        scores["Fine-tuning"] += 1.5
        scores["Hybrid"] += 1.5
        reasoning.append(f"{use_case.training_examples} examples - good for fine-tuning")

    # Calculate costs
    rag_cost = calculate_rag_cost(use_case.monthly_queries)
    ft_cost = calculate_finetuning_cost(use_case.monthly_queries, use_case.training_examples)
    hybrid_cost = calculate_hybrid_cost(use_case.monthly_queries, use_case.training_examples)

    # Factor 6: Cost consideration (significant impact)
    if ft_cost.total_monthly > rag_cost.total_monthly * 3:
        scores["RAG"] += 2.0
        scores["Hybrid"] += 2.0
        reasoning.append(f"Fine-tuning costs ${ft_cost.total_monthly:,.0f}/mo vs RAG ${rag_cost.total_monthly:,.0f}/mo")

    # Determine winner
    best_approach = max(scores, key=scores.get)
    total_score = sum(scores.values())
    confidence = scores[best_approach] / total_score if total_score > 0 else 0.5

    # Select appropriate cost
    if best_approach == "RAG":
        estimated_cost = rag_cost.total_monthly
    elif best_approach == "Fine-tuning":
        estimated_cost = ft_cost.total_monthly
    else:
        estimated_cost = hybrid_cost.total_monthly

    # Add implementation notes
    if best_approach == "RAG":
        notes.extend([
            "Use semantic chunking for better retrieval quality",
            "Consider hybrid search (semantic + keyword)",
            "Implement reranking for improved relevance",
        ])
    elif best_approach == "Fine-tuning":
        notes.extend([
            "Start with LoRA before full fine-tuning",
            "Validate on held-out test set",
            "Monitor for catastrophic forgetting",
        ])
    else:
        notes.extend([
            "Fine-tune for style, use RAG for knowledge",
            "Consider LoRA + vector database",
            "Separate concerns: behavior vs content",
        ])

    return Recommendation(
        approach=best_approach,
        confidence=confidence,
        reasoning=reasoning,
        estimated_monthly_cost=estimated_cost,
        implementation_notes=notes,
        risks=risks
    )


def print_recommendation(use_case: UseCase, rec: Recommendation) -> None:
    """Pretty-print a recommendation."""
    print("\n" + "=" * 70)
    print(f"  ANALYSIS: {use_case.name}")
    print("=" * 70)

    print(f"\n  {use_case.description}\n")

    # Recommendation
    emoji = {"RAG": "🔍", "Fine-tuning": "🎯", "Hybrid": "🔀"}[rec.approach]
    print(f"  RECOMMENDATION: {emoji} {rec.approach.upper()}")
    print(f"  Confidence: {rec.confidence:.0%}")
    print(f"  Estimated Monthly Cost: ${rec.estimated_monthly_cost:,.2f}")

    # Reasoning
    print("\n  REASONING:")
    for i, reason in enumerate(rec.reasoning, 1):
        print(f"    {i}. {reason}")

    # Implementation notes
    if rec.implementation_notes:
        print("\n  IMPLEMENTATION NOTES:")
        for note in rec.implementation_notes:
            print(f"    • {note}")

    # Risks
    if rec.risks:
        print("\n  ⚠️  RISKS:")
        for risk in rec.risks:
            print(f"    • {risk}")

    print("\n" + "=" * 70)


def demo_customer_support() -> None:
    """Demo: Customer support chatbot."""
    use_case = UseCase(
        name="Customer Support Chatbot",
        description="Build a support bot for a SaaS product with 500+ help articles",
        knowledge_frequency=KnowledgeUpdateFrequency.WEEKLY,
        citation_requirement=CitationRequirement.PREFERRED,
        style_requirement=StyleRequirement.IMPORTANT,
        latency_requirement=LatencyRequirement.FLEXIBLE,
        training_examples=50,
        monthly_queries=100_000,
        corpus_size=500
    )

    rec = analyze_use_case(use_case)
    print_recommendation(use_case, rec)


def demo_brand_copywriter() -> None:
    """Demo: Brand voice copywriter."""
    use_case = UseCase(
        name="Brand Copywriter",
        description="Generate marketing copy in a specific brand voice",
        knowledge_frequency=KnowledgeUpdateFrequency.NEVER,
        citation_requirement=CitationRequirement.NOT_NEEDED,
        style_requirement=StyleRequirement.CRITICAL,
        latency_requirement=LatencyRequirement.MODERATE,
        training_examples=500,
        monthly_queries=10_000,
        corpus_size=0
    )

    rec = analyze_use_case(use_case)
    print_recommendation(use_case, rec)


def demo_legal_research() -> None:
    """Demo: Legal research assistant."""
    use_case = UseCase(
        name="Legal Research Assistant",
        description="Research case law and draft legal documents with citations",
        knowledge_frequency=KnowledgeUpdateFrequency.WEEKLY,
        citation_requirement=CitationRequirement.REQUIRED,
        style_requirement=StyleRequirement.CRITICAL,
        latency_requirement=LatencyRequirement.FLEXIBLE,
        training_examples=1000,
        monthly_queries=50_000,
        corpus_size=100_000
    )

    rec = analyze_use_case(use_case)
    print_recommendation(use_case, rec)


def demo_realtime_trading() -> None:
    """Demo: Real-time trading assistant."""
    use_case = UseCase(
        name="Trading Assistant",
        description="Provide real-time market analysis and trading signals",
        knowledge_frequency=KnowledgeUpdateFrequency.REALTIME,
        citation_requirement=CitationRequirement.REQUIRED,
        style_requirement=StyleRequirement.NICE_TO_HAVE,
        latency_requirement=LatencyRequirement.STRICT,
        training_examples=200,
        monthly_queries=500_000,
        corpus_size=10_000
    )

    rec = analyze_use_case(use_case)
    print_recommendation(use_case, rec)


def interactive_analysis() -> None:
    """Interactive mode for custom use cases."""
    print("\n" + "=" * 70)
    print("  RAG vs FINE-TUNING DECISION FRAMEWORK")
    print("  Interactive Analysis Mode")
    print("=" * 70)

    name = input("\n  Project name: ")
    description = input("  Brief description: ")

    print("\n  How often does your knowledge change?")
    print("    1. Real-time (multiple times per day)")
    print("    2. Daily")
    print("    3. Weekly")
    print("    4. Monthly")
    print("    5. Yearly or less")
    print("    6. Never (static)")
    freq_choice = input("  Choice (1-6): ")
    freq_map = {
        "1": KnowledgeUpdateFrequency.REALTIME,
        "2": KnowledgeUpdateFrequency.DAILY,
        "3": KnowledgeUpdateFrequency.WEEKLY,
        "4": KnowledgeUpdateFrequency.MONTHLY,
        "5": KnowledgeUpdateFrequency.YEARLY,
        "6": KnowledgeUpdateFrequency.NEVER,
    }
    knowledge_freq = freq_map.get(freq_choice, KnowledgeUpdateFrequency.WEEKLY)

    print("\n  Do you need to cite sources?")
    print("    1. Required (legal/compliance)")
    print("    2. Preferred (nice to have)")
    print("    3. Not needed")
    cite_choice = input("  Choice (1-3): ")
    cite_map = {
        "1": CitationRequirement.REQUIRED,
        "2": CitationRequirement.PREFERRED,
        "3": CitationRequirement.NOT_NEEDED,
    }
    citation_req = cite_map.get(cite_choice, CitationRequirement.PREFERRED)

    print("\n  How important is specific style/behavior?")
    print("    1. Critical (must match exact style)")
    print("    2. Important (style matters)")
    print("    3. Nice to have")
    print("    4. Not important")
    style_choice = input("  Choice (1-4): ")
    style_map = {
        "1": StyleRequirement.CRITICAL,
        "2": StyleRequirement.IMPORTANT,
        "3": StyleRequirement.NICE_TO_HAVE,
        "4": StyleRequirement.NOT_IMPORTANT,
    }
    style_req = style_map.get(style_choice, StyleRequirement.IMPORTANT)

    print("\n  What's your latency requirement?")
    print("    1. Strict (< 100ms)")
    print("    2. Moderate (< 500ms)")
    print("    3. Flexible (< 2s)")
    print("    4. Very flexible (> 2s OK)")
    latency_choice = input("  Choice (1-4): ")
    latency_map = {
        "1": LatencyRequirement.STRICT,
        "2": LatencyRequirement.MODERATE,
        "3": LatencyRequirement.FLEXIBLE,
        "4": LatencyRequirement.VERY_FLEXIBLE,
    }
    latency_req = latency_map.get(latency_choice, LatencyRequirement.FLEXIBLE)

    training_examples = int(input("\n  How many training examples do you have? "))
    monthly_queries = int(input("  Expected monthly queries? "))

    use_case = UseCase(
        name=name,
        description=description,
        knowledge_frequency=knowledge_freq,
        citation_requirement=citation_req,
        style_requirement=style_req,
        latency_requirement=latency_req,
        training_examples=training_examples,
        monthly_queries=monthly_queries
    )

    rec = analyze_use_case(use_case)
    print_recommendation(use_case, rec)


def main():
    """Run decision framework demos."""
    print("\n" + "=" * 70)
    print("  MODULE 13: RAG vs FINE-TUNING DECISION FRAMEWORK")
    print("=" * 70)
    print("""
  This framework helps you decide between RAG, fine-tuning, or hybrid
  approaches for your AI project.

  The key insight:
  - RAG  = Dynamic knowledge (facts that change)
  - Fine-tuning = Behavior modification (style, reasoning)
  - Hybrid = Best of both worlds

  Running example scenarios...
    """)

    # Run demos
    print("\n" + "-" * 70)
    print("  SCENARIO 1: Customer Support Chatbot")
    print("-" * 70)
    demo_customer_support()

    print("\n" + "-" * 70)
    print("  SCENARIO 2: Brand Copywriter")
    print("-" * 70)
    demo_brand_copywriter()

    print("\n" + "-" * 70)
    print("  SCENARIO 3: Legal Research Assistant")
    print("-" * 70)
    demo_legal_research()

    print("\n" + "-" * 70)
    print("  SCENARIO 4: Real-time Trading Assistant")
    print("-" * 70)
    demo_realtime_trading()

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY: WHEN TO USE WHAT")
    print("=" * 70)
    print("""
  🔍 RAG - Use when:
     • Knowledge changes frequently
     • Citations are required
     • Large document corpus
     • Limited training data

  🎯 FINE-TUNING - Use when:
     • Specific style/behavior is critical
     • Knowledge is static
     • Latency is strict
     • Good training data available

  🔀 HYBRID - Use when:
     • Need both dynamic knowledge AND specific behavior
     • Building production systems
     • Want best quality at reasonable cost

  Try interactive mode:
     python 01_decision_framework.py --interactive
    """)

    # Check for interactive flag
    import sys
    if "--interactive" in sys.argv:
        interactive_analysis()


if __name__ == "__main__":
    main()
