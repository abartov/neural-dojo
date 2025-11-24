#!/usr/bin/env python3
"""
Module 13 Deliverable: RAG vs Fine-tuning Decision Engine

A comprehensive CLI tool for analyzing AI customization strategies.
This deliverable combines the decision framework with detailed cost analysis
to provide actionable recommendations for production AI systems.

Features:
- Interactive use case analysis
- Multi-factor decision scoring
- Detailed cost projections (1 year, 3 year)
- Risk assessment
- Implementation roadmap
- JSON export for documentation

Usage:
    python deliverable_decision_engine.py demo1    # Customer support analysis
    python deliverable_decision_engine.py demo2    # Legal assistant analysis
    python deliverable_decision_engine.py demo3    # Cost comparison scenarios
    python deliverable_decision_engine.py demo4    # Interactive analysis
    python deliverable_decision_engine.py analyze  # Full interactive mode
    python deliverable_decision_engine.py help     # Show help

Author: Neural Dojo
Version: 1.0.0
"""

from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from enum import Enum
import json
import os
import sys
from datetime import datetime


# ============================================================================
# Configuration
# ============================================================================

STORAGE_DIR = ".decision_engine"
ANALYSIS_FILE = "analyses.json"

# 2025 Pricing
PRICING_2025 = {
    "gpt4o": {
        "input_per_million": 2.50,
        "output_per_million": 10.00,
        "finetuned_input_per_million": 3.75,
        "finetuned_output_per_million": 15.00,
        "training_per_million": 25.00,
    },
    "claude_sonnet": {
        "input_per_million": 3.00,
        "output_per_million": 15.00,
    },
    "claude_opus": {
        "input_per_million": 15.00,
        "output_per_million": 75.00,
    },
    "embedding": {
        "openai_per_million": 0.02,
        "voyage_per_million": 0.10,
    },
    "vector_db": {
        "free_tier": 0.0,
        "starter": 70.0,
        "standard": 150.0,
        "enterprise": 300.0,
    },
    "lora": {
        "base_cost": 50.0,
        "per_example": 0.10,
        "max_cost": 200.0,
    },
}


# ============================================================================
# Data Models
# ============================================================================

class KnowledgeFrequency(Enum):
    REALTIME = ("realtime", "Multiple times per day", 5)
    DAILY = ("daily", "Daily updates", 4)
    WEEKLY = ("weekly", "Weekly updates", 3)
    MONTHLY = ("monthly", "Monthly updates", 2)
    YEARLY = ("yearly", "Yearly or less", 1)
    STATIC = ("static", "Never changes", 0)

    def __init__(self, value: str, description: str, rag_score: int):
        self._value_ = value
        self.description = description
        self.rag_score = rag_score


class CitationNeed(Enum):
    REQUIRED = ("required", "Legal/compliance requirement", 5)
    IMPORTANT = ("important", "Important for trust", 3)
    PREFERRED = ("preferred", "Nice to have", 1)
    NOT_NEEDED = ("not_needed", "Not needed", 0)

    def __init__(self, value: str, description: str, rag_score: int):
        self._value_ = value
        self.description = description
        self.rag_score = rag_score


class StyleNeed(Enum):
    CRITICAL = ("critical", "Must match exact style", 5)
    IMPORTANT = ("important", "Style matters significantly", 3)
    MODERATE = ("moderate", "Style somewhat important", 2)
    MINIMAL = ("minimal", "Style not important", 0)

    def __init__(self, value: str, description: str, ft_score: int):
        self._value_ = value
        self.description = description
        self.ft_score = ft_score


class LatencyTolerance(Enum):
    STRICT = ("strict", "< 100ms required", -3)  # Negative = penalizes RAG
    MODERATE = ("moderate", "< 500ms acceptable", -1)
    FLEXIBLE = ("flexible", "< 2s acceptable", 0)
    RELAXED = ("relaxed", "> 2s acceptable", 1)

    def __init__(self, value: str, description: str, rag_modifier: int):
        self._value_ = value
        self.description = description
        self.rag_modifier = rag_modifier


@dataclass
class UseCase:
    """Represents a use case for analysis."""
    name: str
    description: str
    knowledge_frequency: KnowledgeFrequency
    citation_need: CitationNeed
    style_need: StyleNeed
    latency_tolerance: LatencyTolerance
    training_examples: int
    monthly_queries: int
    corpus_size: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CostProjection:
    """Cost projection for an approach."""
    monthly: float
    yearly: float
    three_year: float
    one_time: float
    breakdown: dict = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Risk assessment for an approach."""
    level: Literal["Low", "Medium", "High"]
    factors: list[str] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)


@dataclass
class ImplementationStep:
    """A step in the implementation roadmap."""
    phase: int
    title: str
    description: str
    duration: str
    dependencies: list[str] = field(default_factory=list)


@dataclass
class Analysis:
    """Complete analysis result."""
    use_case: UseCase
    recommended_approach: Literal["RAG", "Fine-tuning", "Hybrid"]
    confidence: float
    reasoning: list[str]
    cost_projections: dict[str, CostProjection]
    risk_assessment: RiskAssessment
    implementation_roadmap: list[ImplementationStep]
    alternatives: list[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Decision Engine Core
# ============================================================================

class DecisionEngine:
    """Core decision engine for RAG vs Fine-tuning analysis."""

    def __init__(self):
        self.storage_dir = STORAGE_DIR
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure storage directory exists."""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _load_analyses(self) -> list[dict]:
        """Load saved analyses."""
        path = os.path.join(self.storage_dir, ANALYSIS_FILE)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return []

    def _save_analysis(self, analysis: Analysis) -> None:
        """Save an analysis to storage."""
        analyses = self._load_analyses()
        analyses.append(asdict(analysis))
        path = os.path.join(self.storage_dir, ANALYSIS_FILE)
        with open(path, "w") as f:
            json.dump(analyses, f, indent=2, default=str)

    def calculate_scores(self, use_case: UseCase) -> dict[str, float]:
        """Calculate approach scores based on use case factors."""
        scores = {"RAG": 0.0, "Fine-tuning": 0.0, "Hybrid": 0.0}

        # Knowledge frequency factor
        rag_knowledge_score = use_case.knowledge_frequency.rag_score
        scores["RAG"] += rag_knowledge_score * 1.5
        scores["Hybrid"] += rag_knowledge_score * 1.0
        scores["Fine-tuning"] += (5 - rag_knowledge_score) * 0.5

        # Citation factor
        citation_score = use_case.citation_need.rag_score
        scores["RAG"] += citation_score * 1.2
        scores["Hybrid"] += citation_score * 1.0
        if citation_score >= 3:
            scores["Fine-tuning"] -= 2.0  # Penalty

        # Style factor
        style_score = use_case.style_need.ft_score
        scores["Fine-tuning"] += style_score * 1.3
        scores["Hybrid"] += style_score * 1.2
        scores["RAG"] += (5 - style_score) * 0.3

        # Latency factor
        latency_mod = use_case.latency_tolerance.rag_modifier
        scores["RAG"] += latency_mod
        scores["Hybrid"] += latency_mod * 0.5

        # Training data factor
        if use_case.training_examples < 50:
            scores["RAG"] += 3.0
            scores["Fine-tuning"] -= 3.0
            scores["Hybrid"] += 1.0
        elif use_case.training_examples < 200:
            scores["Hybrid"] += 2.0
            scores["Fine-tuning"] += 1.0
        else:
            scores["Fine-tuning"] += 2.0
            scores["Hybrid"] += 2.0

        # Scale factor (high volume favors RAG due to cost)
        if use_case.monthly_queries > 500_000:
            scores["RAG"] += 2.0
            scores["Hybrid"] += 1.5

        # Normalize scores
        min_score = min(scores.values())
        if min_score < 0:
            for key in scores:
                scores[key] -= min_score

        return scores

    def calculate_costs(self, use_case: UseCase) -> dict[str, CostProjection]:
        """Calculate cost projections for all approaches."""
        projections = {}

        # Common calculations
        input_tokens_per_query = 800  # With context for RAG
        output_tokens_per_query = 200
        input_tokens_ft = 500  # Less context needed
        output_tokens_ft = 200

        # RAG costs
        monthly_input = use_case.monthly_queries * input_tokens_per_query
        monthly_output = use_case.monthly_queries * output_tokens_per_query

        rag_llm = (
            monthly_input / 1_000_000 * PRICING_2025["gpt4o"]["input_per_million"] +
            monthly_output / 1_000_000 * PRICING_2025["gpt4o"]["output_per_million"]
        )
        rag_embedding = use_case.monthly_queries * 100 / 1_000_000 * PRICING_2025["embedding"]["openai_per_million"]

        if use_case.monthly_queries < 50_000:
            rag_vectordb = PRICING_2025["vector_db"]["free_tier"]
        elif use_case.monthly_queries < 500_000:
            rag_vectordb = PRICING_2025["vector_db"]["starter"]
        else:
            rag_vectordb = PRICING_2025["vector_db"]["standard"]

        rag_monthly = rag_llm + rag_embedding + rag_vectordb
        projections["RAG"] = CostProjection(
            monthly=rag_monthly,
            yearly=rag_monthly * 12,
            three_year=rag_monthly * 36,
            one_time=0.0,
            breakdown={
                "llm_api": rag_llm,
                "embeddings": rag_embedding,
                "vector_db": rag_vectordb,
            }
        )

        # Fine-tuning costs
        ft_monthly_input = use_case.monthly_queries * input_tokens_ft
        ft_monthly_output = use_case.monthly_queries * output_tokens_ft

        ft_inference = (
            ft_monthly_input / 1_000_000 * PRICING_2025["gpt4o"]["finetuned_input_per_million"] +
            ft_monthly_output / 1_000_000 * PRICING_2025["gpt4o"]["finetuned_output_per_million"]
        )
        ft_training = use_case.training_examples * 500 / 1_000_000 * PRICING_2025["gpt4o"]["training_per_million"]

        projections["Fine-tuning"] = CostProjection(
            monthly=ft_inference,
            yearly=ft_inference * 12 + ft_training,
            three_year=ft_inference * 36 + ft_training,
            one_time=ft_training,
            breakdown={
                "inference": ft_inference,
                "training": ft_training,
            }
        )

        # Hybrid costs
        lora_training = min(
            PRICING_2025["lora"]["base_cost"] + use_case.training_examples * PRICING_2025["lora"]["per_example"],
            PRICING_2025["lora"]["max_cost"]
        )

        projections["Hybrid"] = CostProjection(
            monthly=rag_monthly,  # Uses base model pricing with RAG
            yearly=rag_monthly * 12 + lora_training,
            three_year=rag_monthly * 36 + lora_training,
            one_time=lora_training,
            breakdown={
                "llm_api": rag_llm,
                "embeddings": rag_embedding,
                "vector_db": rag_vectordb,
                "lora_training": lora_training,
            }
        )

        return projections

    def assess_risks(self, use_case: UseCase, approach: str) -> RiskAssessment:
        """Assess risks for the recommended approach."""
        factors = []
        mitigations = []

        if approach == "RAG":
            if use_case.latency_tolerance in [LatencyTolerance.STRICT, LatencyTolerance.MODERATE]:
                factors.append("Retrieval latency may impact response times")
                mitigations.append("Implement caching for common queries")

            if use_case.corpus_size > 100_000:
                factors.append("Large corpus may increase retrieval complexity")
                mitigations.append("Use hierarchical retrieval or query routing")

            if use_case.style_need in [StyleNeed.CRITICAL, StyleNeed.IMPORTANT]:
                factors.append("Style consistency may vary without fine-tuning")
                mitigations.append("Use detailed system prompts and few-shot examples")

        elif approach == "Fine-tuning":
            if use_case.training_examples < 100:
                factors.append("Limited training data may cause overfitting")
                mitigations.append("Use LoRA with careful validation")

            if use_case.knowledge_frequency in [KnowledgeFrequency.REALTIME, KnowledgeFrequency.DAILY]:
                factors.append("Frequent knowledge changes require retraining")
                mitigations.append("Consider hybrid approach or accept knowledge staleness")

            if use_case.citation_need in [CitationNeed.REQUIRED, CitationNeed.IMPORTANT]:
                factors.append("Citations not naturally supported")
                mitigations.append("Implement post-processing citation matching")

        else:  # Hybrid
            factors.append("More complex architecture to maintain")
            mitigations.append("Use well-documented, modular design")

            if use_case.monthly_queries > 1_000_000:
                factors.append("Multiple components increase operational complexity")
                mitigations.append("Implement robust monitoring and alerting")

        level = "Low" if len(factors) <= 1 else "Medium" if len(factors) <= 2 else "High"

        return RiskAssessment(level=level, factors=factors, mitigations=mitigations)

    def generate_roadmap(self, approach: str, use_case: UseCase) -> list[ImplementationStep]:
        """Generate implementation roadmap."""
        steps = []

        if approach == "RAG":
            steps = [
                ImplementationStep(
                    phase=1,
                    title="Document Processing Pipeline",
                    description="Set up document ingestion, chunking, and embedding generation",
                    duration="1-2 weeks",
                    dependencies=[]
                ),
                ImplementationStep(
                    phase=2,
                    title="Vector Database Setup",
                    description="Deploy and configure vector database (Qdrant/Pinecone)",
                    duration="3-5 days",
                    dependencies=["Document Processing Pipeline"]
                ),
                ImplementationStep(
                    phase=3,
                    title="Retrieval Pipeline",
                    description="Implement semantic search with reranking",
                    duration="1 week",
                    dependencies=["Vector Database Setup"]
                ),
                ImplementationStep(
                    phase=4,
                    title="RAG Integration",
                    description="Connect retrieval to LLM generation with prompt engineering",
                    duration="1 week",
                    dependencies=["Retrieval Pipeline"]
                ),
                ImplementationStep(
                    phase=5,
                    title="Evaluation & Optimization",
                    description="Measure retrieval quality and optimize chunking/prompts",
                    duration="1-2 weeks",
                    dependencies=["RAG Integration"]
                ),
            ]

        elif approach == "Fine-tuning":
            steps = [
                ImplementationStep(
                    phase=1,
                    title="Data Preparation",
                    description="Collect and format training examples",
                    duration="1-2 weeks",
                    dependencies=[]
                ),
                ImplementationStep(
                    phase=2,
                    title="Validation Split",
                    description="Create train/validation/test splits",
                    duration="2-3 days",
                    dependencies=["Data Preparation"]
                ),
                ImplementationStep(
                    phase=3,
                    title="LoRA Fine-tuning",
                    description="Fine-tune with LoRA/QLoRA on training data",
                    duration="3-5 days",
                    dependencies=["Validation Split"]
                ),
                ImplementationStep(
                    phase=4,
                    title="Evaluation",
                    description="Evaluate on held-out test set",
                    duration="2-3 days",
                    dependencies=["LoRA Fine-tuning"]
                ),
                ImplementationStep(
                    phase=5,
                    title="Deployment",
                    description="Deploy fine-tuned model to production",
                    duration="1 week",
                    dependencies=["Evaluation"]
                ),
            ]

        else:  # Hybrid
            steps = [
                ImplementationStep(
                    phase=1,
                    title="RAG Infrastructure",
                    description="Set up complete RAG pipeline (docs, vectors, retrieval)",
                    duration="2-3 weeks",
                    dependencies=[]
                ),
                ImplementationStep(
                    phase=2,
                    title="Style Data Collection",
                    description="Collect examples for behavior/style fine-tuning",
                    duration="1 week",
                    dependencies=[]
                ),
                ImplementationStep(
                    phase=3,
                    title="LoRA Fine-tuning",
                    description="Fine-tune for style/behavior (not knowledge)",
                    duration="1 week",
                    dependencies=["Style Data Collection"]
                ),
                ImplementationStep(
                    phase=4,
                    title="Integration",
                    description="Combine RAG retrieval with fine-tuned generation",
                    duration="1 week",
                    dependencies=["RAG Infrastructure", "LoRA Fine-tuning"]
                ),
                ImplementationStep(
                    phase=5,
                    title="End-to-End Testing",
                    description="Validate complete hybrid system",
                    duration="1-2 weeks",
                    dependencies=["Integration"]
                ),
            ]

        return steps

    def analyze(self, use_case: UseCase) -> Analysis:
        """Perform complete analysis of a use case."""
        # Calculate scores
        scores = self.calculate_scores(use_case)
        best_approach = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[best_approach] / total if total > 0 else 0.5

        # Generate reasoning
        reasoning = []
        if use_case.knowledge_frequency.rag_score >= 3:
            reasoning.append(f"Knowledge changes {use_case.knowledge_frequency.value} - RAG provides dynamic updates")
        if use_case.citation_need.rag_score >= 3:
            reasoning.append("Citations required/important - RAG enables natural source attribution")
        if use_case.style_need.ft_score >= 3:
            reasoning.append("Style requirements are significant - fine-tuning ensures consistency")
        if use_case.training_examples < 100:
            reasoning.append(f"Limited training data ({use_case.training_examples}) favors RAG")
        elif use_case.training_examples >= 200:
            reasoning.append(f"Sufficient training data ({use_case.training_examples}) enables effective fine-tuning")
        if use_case.latency_tolerance == LatencyTolerance.STRICT:
            reasoning.append("Strict latency requirements favor fine-tuning (no retrieval overhead)")

        # Calculate costs
        cost_projections = self.calculate_costs(use_case)

        # Assess risks
        risk_assessment = self.assess_risks(use_case, best_approach)

        # Generate roadmap
        roadmap = self.generate_roadmap(best_approach, use_case)

        # Generate alternatives
        sorted_approaches = sorted(scores.items(), key=lambda x: -x[1])
        alternatives = []
        for approach, score in sorted_approaches[1:]:
            diff = scores[best_approach] - score
            if diff < 3:
                alternatives.append(f"{approach} is also viable (score difference: {diff:.1f})")

        analysis = Analysis(
            use_case=use_case,
            recommended_approach=best_approach,
            confidence=confidence,
            reasoning=reasoning,
            cost_projections={k: v for k, v in cost_projections.items()},
            risk_assessment=risk_assessment,
            implementation_roadmap=roadmap,
            alternatives=alternatives,
        )

        # Save analysis
        self._save_analysis(analysis)

        return analysis


# ============================================================================
# Output Formatting
# ============================================================================

def print_analysis(analysis: Analysis) -> None:
    """Pretty-print an analysis."""
    print("\n" + "=" * 80)
    print("  RAG vs FINE-TUNING DECISION ENGINE - ANALYSIS REPORT")
    print("=" * 80)

    # Use case summary
    uc = analysis.use_case
    print(f"\n  PROJECT: {uc.name}")
    print(f"  {uc.description}")
    print(f"\n  Parameters:")
    print(f"    - Monthly queries: {uc.monthly_queries:,}")
    print(f"    - Training examples: {uc.training_examples:,}")
    print(f"    - Knowledge updates: {uc.knowledge_frequency.description}")
    print(f"    - Citation need: {uc.citation_need.description}")
    print(f"    - Style need: {uc.style_need.description}")
    print(f"    - Latency tolerance: {uc.latency_tolerance.description}")

    # Recommendation
    emoji = {"RAG": "🔍", "Fine-tuning": "🎯", "Hybrid": "🔀"}[analysis.recommended_approach]
    print("\n" + "-" * 80)
    print(f"  RECOMMENDATION: {emoji} {analysis.recommended_approach.upper()}")
    print(f"  Confidence: {analysis.confidence:.0%}")
    print("-" * 80)

    # Reasoning
    print("\n  REASONING:")
    for i, reason in enumerate(analysis.reasoning, 1):
        print(f"    {i}. {reason}")

    # Cost projections
    print("\n  COST PROJECTIONS:")
    print(f"  {'Approach':<15} {'Monthly':>12} {'Year 1':>12} {'Year 3':>12} {'One-time':>12}")
    print("  " + "-" * 63)
    for approach, cost in analysis.cost_projections.items():
        print(f"  {approach:<15} ${cost.monthly:>10,.0f} ${cost.yearly:>10,.0f} ${cost.three_year:>10,.0f} ${cost.one_time:>10,.0f}")

    # Risk assessment
    print(f"\n  RISK ASSESSMENT: {analysis.risk_assessment.level}")
    if analysis.risk_assessment.factors:
        print("  Risk Factors:")
        for factor in analysis.risk_assessment.factors:
            print(f"    ⚠️  {factor}")
    if analysis.risk_assessment.mitigations:
        print("  Mitigations:")
        for mitigation in analysis.risk_assessment.mitigations:
            print(f"    ✓ {mitigation}")

    # Implementation roadmap
    print("\n  IMPLEMENTATION ROADMAP:")
    for step in analysis.implementation_roadmap:
        print(f"    Phase {step.phase}: {step.title} ({step.duration})")
        print(f"            {step.description}")

    # Alternatives
    if analysis.alternatives:
        print("\n  ALTERNATIVES:")
        for alt in analysis.alternatives:
            print(f"    • {alt}")

    print("\n" + "=" * 80)


# ============================================================================
# Demo Functions
# ============================================================================

def demo_customer_support() -> None:
    """Demo 1: Customer support chatbot analysis."""
    print("\n" + "=" * 80)
    print("  DEMO 1: Customer Support Chatbot")
    print("=" * 80)

    engine = DecisionEngine()
    use_case = UseCase(
        name="Customer Support Chatbot",
        description="AI assistant for SaaS product with 500+ help articles",
        knowledge_frequency=KnowledgeFrequency.WEEKLY,
        citation_need=CitationNeed.PREFERRED,
        style_need=StyleNeed.MODERATE,
        latency_tolerance=LatencyTolerance.FLEXIBLE,
        training_examples=75,
        monthly_queries=100_000,
        corpus_size=500,
    )

    analysis = engine.analyze(use_case)
    print_analysis(analysis)


def demo_legal_assistant() -> None:
    """Demo 2: Legal research assistant analysis."""
    print("\n" + "=" * 80)
    print("  DEMO 2: Legal Research Assistant")
    print("=" * 80)

    engine = DecisionEngine()
    use_case = UseCase(
        name="Legal Research Assistant",
        description="Research case law and draft legal documents with citations",
        knowledge_frequency=KnowledgeFrequency.WEEKLY,
        citation_need=CitationNeed.REQUIRED,
        style_need=StyleNeed.CRITICAL,
        latency_tolerance=LatencyTolerance.FLEXIBLE,
        training_examples=1000,
        monthly_queries=50_000,
        corpus_size=100_000,
    )

    analysis = engine.analyze(use_case)
    print_analysis(analysis)


def demo_cost_scenarios() -> None:
    """Demo 3: Cost comparison across different scales."""
    print("\n" + "=" * 80)
    print("  DEMO 3: Cost Comparison Across Scales")
    print("=" * 80)

    engine = DecisionEngine()
    scenarios = [
        ("Startup", 10_000, 100),
        ("Growth", 100_000, 500),
        ("Scale", 1_000_000, 2000),
    ]

    print("\n  Cost comparison for a typical use case at different scales:\n")
    print(f"  {'Scale':<12} {'Queries/Mo':>12} {'RAG (Y1)':>15} {'FT (Y1)':>15} {'Hybrid (Y1)':>15} {'Winner':>10}")
    print("  " + "-" * 79)

    for name, queries, examples in scenarios:
        use_case = UseCase(
            name=name,
            description="Cost scenario",
            knowledge_frequency=KnowledgeFrequency.WEEKLY,
            citation_need=CitationNeed.PREFERRED,
            style_need=StyleNeed.MODERATE,
            latency_tolerance=LatencyTolerance.FLEXIBLE,
            training_examples=examples,
            monthly_queries=queries,
        )

        costs = engine.calculate_costs(use_case)
        rag_y1 = costs["RAG"].yearly
        ft_y1 = costs["Fine-tuning"].yearly
        hybrid_y1 = costs["Hybrid"].yearly

        winner = min([("RAG", rag_y1), ("FT", ft_y1), ("Hybrid", hybrid_y1)], key=lambda x: x[1])[0]

        print(f"  {name:<12} {queries:>12,} ${rag_y1:>13,.0f} ${ft_y1:>13,.0f} ${hybrid_y1:>13,.0f} {winner:>10}")

    print("\n  Key Insight: RAG and Hybrid are consistently more cost-effective due to")
    print("  lower per-token costs. Fine-tuning only wins on latency-critical workloads.")


def demo_interactive() -> None:
    """Demo 4: Interactive analysis mode."""
    print("\n" + "=" * 80)
    print("  DEMO 4: Interactive Analysis")
    print("=" * 80)

    engine = DecisionEngine()

    print("\n  Let's analyze your specific use case!\n")

    name = input("  Project name: ")
    description = input("  Brief description: ")

    print("\n  How often does your knowledge change?")
    for i, freq in enumerate(KnowledgeFrequency, 1):
        print(f"    {i}. {freq.description}")
    freq_choice = int(input("  Choice (1-6): "))
    knowledge_freq = list(KnowledgeFrequency)[freq_choice - 1]

    print("\n  Do you need to cite sources?")
    for i, cite in enumerate(CitationNeed, 1):
        print(f"    {i}. {cite.description}")
    cite_choice = int(input("  Choice (1-4): "))
    citation_need = list(CitationNeed)[cite_choice - 1]

    print("\n  How important is specific style/behavior?")
    for i, style in enumerate(StyleNeed, 1):
        print(f"    {i}. {style.description}")
    style_choice = int(input("  Choice (1-4): "))
    style_need = list(StyleNeed)[style_choice - 1]

    print("\n  What's your latency tolerance?")
    for i, lat in enumerate(LatencyTolerance, 1):
        print(f"    {i}. {lat.description}")
    lat_choice = int(input("  Choice (1-4): "))
    latency_tolerance = list(LatencyTolerance)[lat_choice - 1]

    training_examples = int(input("\n  Number of training examples available: "))
    monthly_queries = int(input("  Expected monthly queries: "))

    use_case = UseCase(
        name=name,
        description=description,
        knowledge_frequency=knowledge_freq,
        citation_need=citation_need,
        style_need=style_need,
        latency_tolerance=latency_tolerance,
        training_examples=training_examples,
        monthly_queries=monthly_queries,
    )

    print("\n  Analyzing...")
    analysis = engine.analyze(use_case)
    print_analysis(analysis)

    # Offer to export
    export = input("\n  Export analysis to JSON? (y/n): ")
    if export.lower() == "y":
        filename = f"analysis_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(asdict(analysis), f, indent=2, default=str)
        print(f"  ✅ Exported to {filename}")


def show_help() -> None:
    """Show help information."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║          RAG vs FINE-TUNING DECISION ENGINE - Help                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Usage:                                                                      ║
║    python deliverable_decision_engine.py [command]                           ║
║                                                                              ║
║  Commands:                                                                   ║
║    demo1     Customer support chatbot analysis                               ║
║    demo2     Legal research assistant analysis                               ║
║    demo3     Cost comparison across scales                                   ║
║    demo4     Interactive analysis mode                                       ║
║    analyze   Full interactive analysis (same as demo4)                       ║
║    help      Show this help message                                          ║
║                                                                              ║
║  Examples:                                                                   ║
║    python deliverable_decision_engine.py demo1                               ║
║    python deliverable_decision_engine.py analyze                             ║
║                                                                              ║
║  Key Insight:                                                                ║
║    RAG = Dynamic Knowledge (facts that change)                               ║
║    Fine-tuning = Behavior Modification (style, reasoning)                    ║
║    Hybrid = Best of both worlds (recommended for production)                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("\n  Running all demos...\n")
        demo_customer_support()
        demo_legal_assistant()
        demo_cost_scenarios()
        print("\n  Run 'python deliverable_decision_engine.py demo4' for interactive mode")
        print("  Run 'python deliverable_decision_engine.py help' for more options")
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_customer_support()
    elif command == "demo2":
        demo_legal_assistant()
    elif command == "demo3":
        demo_cost_scenarios()
    elif command == "demo4" or command == "analyze":
        demo_interactive()
    elif command == "help":
        show_help()
    else:
        print(f"  Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
