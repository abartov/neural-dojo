#!/usr/bin/env python3
"""
Module 19 Deliverable: AI Framework Selector Toolkit

A comprehensive toolkit for selecting and evaluating AI frameworks:
- Interactive questionnaire for framework recommendation
- Feature comparison matrix
- Use case matching
- Framework compatibility checker
- Project template generator

Helps teams make informed decisions about AI framework selection.

Usage:
    python deliverable_framework_selector.py recommend    # Interactive recommendation
    python deliverable_framework_selector.py compare      # Compare frameworks
    python deliverable_framework_selector.py analyze      # Analyze requirements
    python deliverable_framework_selector.py demo         # Run all demos
    python deliverable_framework_selector.py export       # Export comparison report

Author: Neural Dojo
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import sys


# =============================================================================
# Configuration
# =============================================================================

STORAGE_DIR = Path(".framework_selector")
RECOMMENDATIONS_FILE = STORAGE_DIR / "recommendations.json"


# =============================================================================
# Data Models
# =============================================================================

class UseCase(str, Enum):
    """Primary use cases for AI frameworks."""
    RAG = "rag"
    AGENTS = "agents"
    MULTI_AGENT = "multi_agent"
    CHATBOT = "chatbot"
    CODE_GEN = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    SEARCH = "search"
    GENERAL = "general"


class FrameworkCategory(str, Enum):
    """Categories of AI frameworks."""
    DATA_FRAMEWORK = "data_framework"
    ORCHESTRATION = "orchestration"
    MULTI_AGENT = "multi_agent"
    ENTERPRISE = "enterprise"
    RESEARCH = "research"


class Priority(str, Enum):
    """Priority levels for requirements."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Framework:
    """Definition of an AI framework."""
    name: str
    category: FrameworkCategory
    description: str
    strengths: List[str]
    weaknesses: List[str]
    use_cases: List[UseCase]
    learning_curve: str  # "low", "medium", "high"
    production_ready: bool
    community_size: str  # "small", "medium", "large"
    documentation_quality: str  # "poor", "good", "excellent"
    install_command: str
    website: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "use_cases": [uc.value for uc in self.use_cases],
            "learning_curve": self.learning_curve,
            "production_ready": self.production_ready,
            "community_size": self.community_size,
            "documentation_quality": self.documentation_quality,
            "install_command": self.install_command,
            "website": self.website
        }


@dataclass
class Requirement:
    """A project requirement for framework selection."""
    name: str
    description: str
    priority: Priority
    satisfied_by: List[str]  # Framework names


@dataclass
class Recommendation:
    """A framework recommendation."""
    framework: str
    score: float
    reasons: List[str]
    concerns: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProjectProfile:
    """Profile of a project for framework selection."""
    primary_use_case: UseCase
    secondary_use_cases: List[UseCase]
    team_size: str  # "solo", "small", "medium", "large"
    experience_level: str  # "beginner", "intermediate", "advanced"
    production_required: bool
    budget_constraints: bool
    timeline: str  # "asap", "weeks", "months"
    existing_stack: List[str]

    def to_dict(self) -> dict:
        return {
            "primary_use_case": self.primary_use_case.value,
            "secondary_use_cases": [uc.value for uc in self.secondary_use_cases],
            "team_size": self.team_size,
            "experience_level": self.experience_level,
            "production_required": self.production_required,
            "budget_constraints": self.budget_constraints,
            "timeline": self.timeline,
            "existing_stack": self.existing_stack
        }


# =============================================================================
# Framework Database
# =============================================================================

FRAMEWORKS: Dict[str, Framework] = {
    "langchain": Framework(
        name="LangChain",
        category=FrameworkCategory.ORCHESTRATION,
        description="Composable building blocks for LLM applications",
        strengths=[
            "Highly flexible and composable",
            "Extensive tool integration",
            "Large community and ecosystem",
            "Good documentation",
            "Wide LLM provider support"
        ],
        weaknesses=[
            "Steeper learning curve",
            "Can be verbose for simple tasks",
            "Frequent breaking changes",
            "Abstraction overhead"
        ],
        use_cases=[UseCase.AGENTS, UseCase.CHATBOT, UseCase.RAG, UseCase.GENERAL],
        learning_curve="high",
        production_ready=True,
        community_size="large",
        documentation_quality="good",
        install_command="pip install langchain langchain-core",
        website="https://langchain.com"
    ),
    "langgraph": Framework(
        name="LangGraph",
        category=FrameworkCategory.ORCHESTRATION,
        description="Stateful, multi-actor applications with LLMs",
        strengths=[
            "Excellent state management",
            "Native cycle support",
            "Human-in-the-loop patterns",
            "Production-ready checkpointing",
            "Precise control over flow"
        ],
        weaknesses=[
            "Requires LangChain knowledge",
            "Higher complexity",
            "Newer, less mature"
        ],
        use_cases=[UseCase.AGENTS, UseCase.MULTI_AGENT],
        learning_curve="high",
        production_ready=True,
        community_size="medium",
        documentation_quality="good",
        install_command="pip install langgraph",
        website="https://langchain-ai.github.io/langgraph/"
    ),
    "llamaindex": Framework(
        name="LlamaIndex",
        category=FrameworkCategory.DATA_FRAMEWORK,
        description="Data framework for LLM applications",
        strengths=[
            "Excellent for RAG",
            "Simple API for indexing",
            "150+ data connectors",
            "Built-in query optimization",
            "Multiple index types"
        ],
        weaknesses=[
            "Less flexible for agents",
            "Smaller community than LangChain",
            "Limited workflow capabilities"
        ],
        use_cases=[UseCase.RAG, UseCase.SEARCH, UseCase.DATA_ANALYSIS],
        learning_curve="medium",
        production_ready=True,
        community_size="medium",
        documentation_quality="good",
        install_command="pip install llama-index",
        website="https://llamaindex.ai"
    ),
    "crewai": Framework(
        name="CrewAI",
        category=FrameworkCategory.MULTI_AGENT,
        description="Role-based multi-agent orchestration",
        strengths=[
            "Intuitive role-based design",
            "Easy to understand",
            "Quick to prototype",
            "Built-in collaboration",
            "Low learning curve"
        ],
        weaknesses=[
            "Less flexible than LangGraph",
            "Limited state management",
            "Newer framework",
            "Smaller community"
        ],
        use_cases=[UseCase.MULTI_AGENT, UseCase.AGENTS],
        learning_curve="low",
        production_ready=True,
        community_size="small",
        documentation_quality="good",
        install_command="pip install crewai",
        website="https://crewai.com"
    ),
    "autogen": Framework(
        name="AutoGen",
        category=FrameworkCategory.RESEARCH,
        description="Conversational multi-agent framework",
        strengths=[
            "Natural conversation flow",
            "Built-in code execution",
            "Strong human-in-the-loop",
            "Microsoft backing",
            "Research-grade design"
        ],
        weaknesses=[
            "Experimental status",
            "Higher complexity",
            "Less production focus",
            "Heavier dependencies"
        ],
        use_cases=[UseCase.MULTI_AGENT, UseCase.CODE_GEN],
        learning_curve="medium",
        production_ready=False,
        community_size="medium",
        documentation_quality="good",
        install_command="pip install autogen",
        website="https://microsoft.github.io/autogen/"
    ),
    "haystack": Framework(
        name="Haystack",
        category=FrameworkCategory.DATA_FRAMEWORK,
        description="Search-focused NLP framework",
        strengths=[
            "Excellent for search",
            "Strong pipeline architecture",
            "Good production tools",
            "NLP-focused features"
        ],
        weaknesses=[
            "Less general purpose",
            "Smaller LLM ecosystem",
            "Steeper learning for non-search"
        ],
        use_cases=[UseCase.SEARCH, UseCase.RAG],
        learning_curve="medium",
        production_ready=True,
        community_size="medium",
        documentation_quality="excellent",
        install_command="pip install haystack-ai",
        website="https://haystack.deepset.ai"
    ),
    "semantic_kernel": Framework(
        name="Semantic Kernel",
        category=FrameworkCategory.ENTERPRISE,
        description="Enterprise AI orchestration by Microsoft",
        strengths=[
            "Enterprise-ready",
            "Azure integration",
            "C# and Python support",
            "Plugin architecture",
            "Microsoft backing"
        ],
        weaknesses=[
            "Microsoft ecosystem bias",
            "Smaller open-source community",
            "Less flexible than alternatives"
        ],
        use_cases=[UseCase.AGENTS, UseCase.GENERAL],
        learning_curve="medium",
        production_ready=True,
        community_size="medium",
        documentation_quality="excellent",
        install_command="pip install semantic-kernel",
        website="https://learn.microsoft.com/semantic-kernel/"
    )
}


# =============================================================================
# Scoring Engine
# =============================================================================

class FrameworkScorer:
    """Scores frameworks based on project requirements."""

    def __init__(self):
        self.weights = {
            "use_case_match": 0.30,
            "experience_fit": 0.20,
            "production_need": 0.20,
            "timeline_fit": 0.15,
            "community": 0.15
        }

    def score_framework(self, framework: Framework, profile: ProjectProfile) -> Tuple[float, List[str], List[str]]:
        """Score a framework against a project profile."""
        score = 0.0
        reasons = []
        concerns = []

        # Use case match (30%)
        use_case_score = 0.0
        if profile.primary_use_case in framework.use_cases:
            use_case_score += 0.7
            reasons.append(f"Strong match for {profile.primary_use_case.value}")
        else:
            concerns.append(f"Not optimized for {profile.primary_use_case.value}")

        for secondary in profile.secondary_use_cases:
            if secondary in framework.use_cases:
                use_case_score += 0.15
                reasons.append(f"Supports {secondary.value}")

        score += min(1.0, use_case_score) * self.weights["use_case_match"]

        # Experience fit (20%)
        exp_map = {"beginner": "low", "intermediate": "medium", "advanced": "high"}
        target_curve = exp_map.get(profile.experience_level, "medium")

        if framework.learning_curve == target_curve:
            score += 1.0 * self.weights["experience_fit"]
            reasons.append(f"Good fit for {profile.experience_level} team")
        elif framework.learning_curve == "low":
            score += 0.8 * self.weights["experience_fit"]
            reasons.append("Easy to learn")
        elif framework.learning_curve == "high" and profile.experience_level == "beginner":
            score += 0.3 * self.weights["experience_fit"]
            concerns.append("Steep learning curve for beginners")
        else:
            score += 0.6 * self.weights["experience_fit"]

        # Production need (20%)
        if profile.production_required:
            if framework.production_ready:
                score += 1.0 * self.weights["production_need"]
                reasons.append("Production-ready")
            else:
                score += 0.2 * self.weights["production_need"]
                concerns.append("Not production-ready")
        else:
            score += 0.8 * self.weights["production_need"]

        # Timeline fit (15%)
        if profile.timeline == "asap":
            if framework.learning_curve == "low":
                score += 1.0 * self.weights["timeline_fit"]
                reasons.append("Quick to get started")
            else:
                score += 0.5 * self.weights["timeline_fit"]
                concerns.append("May slow initial development")
        else:
            score += 0.7 * self.weights["timeline_fit"]

        # Community (15%)
        community_scores = {"large": 1.0, "medium": 0.7, "small": 0.4}
        score += community_scores.get(framework.community_size, 0.5) * self.weights["community"]
        if framework.community_size == "large":
            reasons.append("Large helpful community")
        elif framework.community_size == "small":
            concerns.append("Smaller community for support")

        # Add framework-specific strengths
        reasons.extend(framework.strengths[:2])

        return score, reasons, concerns

    def get_recommendations(self, profile: ProjectProfile, top_n: int = 3) -> List[Recommendation]:
        """Get top framework recommendations for a profile."""
        scored = []

        for name, framework in FRAMEWORKS.items():
            score, reasons, concerns = self.score_framework(framework, profile)
            scored.append((name, score, reasons, concerns))

        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for name, score, reasons, concerns in scored[:top_n]:
            recommendations.append(Recommendation(
                framework=name,
                score=score,
                reasons=reasons[:5],
                concerns=concerns[:3]
            ))

        return recommendations


# =============================================================================
# Framework Selector
# =============================================================================

class FrameworkSelector:
    """Main framework selection toolkit."""

    def __init__(self):
        self.scorer = FrameworkScorer()
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure storage directory exists."""
        STORAGE_DIR.mkdir(exist_ok=True)

    def interactive_questionnaire(self) -> ProjectProfile:
        """Run interactive questionnaire to build project profile."""
        print("\n" + "="*60)
        print("AI Framework Selection Questionnaire")
        print("="*60)

        print("\nAnswer the following questions to get personalized recommendations.\n")

        # Primary use case
        print("1. What is your PRIMARY use case?")
        use_cases = list(UseCase)
        for i, uc in enumerate(use_cases, 1):
            print(f"   {i}. {uc.value.replace('_', ' ').title()}")
        try:
            choice = int(input("\n   Enter number (1-8): ")) - 1
            primary = use_cases[choice] if 0 <= choice < len(use_cases) else UseCase.GENERAL
        except (ValueError, IndexError):
            primary = UseCase.GENERAL

        # Secondary use cases
        print("\n2. Any SECONDARY use cases? (comma-separated numbers, or press Enter to skip)")
        secondary = []
        try:
            choices = input("   Enter numbers: ").strip()
            if choices:
                for c in choices.split(","):
                    idx = int(c.strip()) - 1
                    if 0 <= idx < len(use_cases) and use_cases[idx] != primary:
                        secondary.append(use_cases[idx])
        except (ValueError, IndexError):
            pass

        # Team size
        print("\n3. What is your team size?")
        print("   1. Solo developer")
        print("   2. Small team (2-5)")
        print("   3. Medium team (6-15)")
        print("   4. Large team (15+)")
        try:
            choice = int(input("\n   Enter number: "))
            team_size = ["solo", "small", "medium", "large"][choice - 1]
        except (ValueError, IndexError):
            team_size = "small"

        # Experience level
        print("\n4. What is your team's AI/ML experience level?")
        print("   1. Beginner (new to AI frameworks)")
        print("   2. Intermediate (some experience)")
        print("   3. Advanced (significant experience)")
        try:
            choice = int(input("\n   Enter number: "))
            experience = ["beginner", "intermediate", "advanced"][choice - 1]
        except (ValueError, IndexError):
            experience = "intermediate"

        # Production required
        print("\n5. Do you need production-ready capabilities?")
        prod_input = input("   (y/n): ").strip().lower()
        production = prod_input == "y"

        # Budget constraints
        print("\n6. Do you have budget constraints (prefer free/open-source)?")
        budget_input = input("   (y/n): ").strip().lower()
        budget = budget_input == "y"

        # Timeline
        print("\n7. What is your timeline?")
        print("   1. ASAP (need it working quickly)")
        print("   2. Weeks (have some time)")
        print("   3. Months (can invest in learning)")
        try:
            choice = int(input("\n   Enter number: "))
            timeline = ["asap", "weeks", "months"][choice - 1]
        except (ValueError, IndexError):
            timeline = "weeks"

        # Existing stack
        print("\n8. What's in your existing tech stack? (comma-separated, or Enter to skip)")
        print("   Examples: python, typescript, azure, aws, docker")
        stack_input = input("   Enter stack: ").strip()
        stack = [s.strip().lower() for s in stack_input.split(",")] if stack_input else []

        return ProjectProfile(
            primary_use_case=primary,
            secondary_use_cases=secondary,
            team_size=team_size,
            experience_level=experience,
            production_required=production,
            budget_constraints=budget,
            timeline=timeline,
            existing_stack=stack
        )

    def get_recommendations(self, profile: ProjectProfile) -> List[Recommendation]:
        """Get framework recommendations for a profile."""
        return self.scorer.get_recommendations(profile)

    def display_recommendations(self, recommendations: List[Recommendation]):
        """Display recommendations in a nice format."""
        print("\n" + "="*60)
        print("Framework Recommendations")
        print("="*60)

        for i, rec in enumerate(recommendations, 1):
            framework = FRAMEWORKS[rec.framework]
            score_pct = rec.score * 100

            print(f"\n{'='*60}")
            print(f"#{i} {framework.name} (Score: {score_pct:.0f}%)")
            print(f"{'='*60}")
            print(f"\nDescription: {framework.description}")

            print(f"\nWhy this framework:")
            for reason in rec.reasons:
                print(f"  + {reason}")

            if rec.concerns:
                print(f"\nConsiderations:")
                for concern in rec.concerns:
                    print(f"  - {concern}")

            print(f"\nQuick Start:")
            print(f"  {framework.install_command}")
            print(f"  Website: {framework.website}")

    def compare_frameworks(self, framework_names: List[str] = None):
        """Compare specified frameworks or all frameworks."""
        if framework_names is None:
            framework_names = list(FRAMEWORKS.keys())

        frameworks = [FRAMEWORKS[name] for name in framework_names if name in FRAMEWORKS]

        print("\n" + "="*60)
        print("Framework Comparison")
        print("="*60)

        # Header
        print(f"\n{'Feature':<25}", end="")
        for fw in frameworks:
            print(f"{fw.name:<15}", end="")
        print()
        print("-" * (25 + 15 * len(frameworks)))

        # Category
        print(f"{'Category':<25}", end="")
        for fw in frameworks:
            print(f"{fw.category.value:<15}", end="")
        print()

        # Learning Curve
        print(f"{'Learning Curve':<25}", end="")
        for fw in frameworks:
            print(f"{fw.learning_curve:<15}", end="")
        print()

        # Production Ready
        print(f"{'Production Ready':<25}", end="")
        for fw in frameworks:
            status = "Yes" if fw.production_ready else "No"
            print(f"{status:<15}", end="")
        print()

        # Community
        print(f"{'Community Size':<25}", end="")
        for fw in frameworks:
            print(f"{fw.community_size:<15}", end="")
        print()

        # Documentation
        print(f"{'Documentation':<25}", end="")
        for fw in frameworks:
            print(f"{fw.documentation_quality:<15}", end="")
        print()

        # Use Cases
        print(f"\n{'Use Cases':<25}")
        for fw in frameworks:
            use_cases = ", ".join([uc.value for uc in fw.use_cases[:3]])
            print(f"  {fw.name}: {use_cases}")

    def export_report(self, profile: ProjectProfile, recommendations: List[Recommendation],
                     filename: str = "framework_report.md"):
        """Export a detailed markdown report."""
        report = []
        report.append("# AI Framework Selection Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

        report.append("## Project Profile\n")
        report.append(f"- **Primary Use Case**: {profile.primary_use_case.value}")
        report.append(f"- **Team Size**: {profile.team_size}")
        report.append(f"- **Experience Level**: {profile.experience_level}")
        report.append(f"- **Production Required**: {'Yes' if profile.production_required else 'No'}")
        report.append(f"- **Timeline**: {profile.timeline}")

        report.append("\n## Recommendations\n")

        for i, rec in enumerate(recommendations, 1):
            fw = FRAMEWORKS[rec.framework]
            report.append(f"### {i}. {fw.name} (Score: {rec.score*100:.0f}%)\n")
            report.append(f"**Description**: {fw.description}\n")
            report.append(f"**Install**: `{fw.install_command}`\n")

            report.append("**Reasons**:")
            for reason in rec.reasons:
                report.append(f"- {reason}")

            if rec.concerns:
                report.append("\n**Concerns**:")
                for concern in rec.concerns:
                    report.append(f"- {concern}")

            report.append("")

        report.append("## Framework Comparison Matrix\n")
        report.append("| Framework | Category | Learning | Production | Community |")
        report.append("|-----------|----------|----------|------------|-----------|")
        for name in [r.framework for r in recommendations]:
            fw = FRAMEWORKS[name]
            prod = "Yes" if fw.production_ready else "No"
            report.append(f"| {fw.name} | {fw.category.value} | {fw.learning_curve} | {prod} | {fw.community_size} |")

        # Write report
        output_path = STORAGE_DIR / filename
        with open(output_path, 'w') as f:
            f.write("\n".join(report))

        print(f"\n  Report exported to: {output_path}")
        return output_path


# =============================================================================
# Demo Functions
# =============================================================================

def demo_interactive():
    """Demo the interactive questionnaire."""
    print("\n" + "="*60)
    print("Demo: Interactive Framework Selection")
    print("="*60)

    selector = FrameworkSelector()

    # Run questionnaire
    profile = selector.interactive_questionnaire()

    print("\n" + "-"*40)
    print("Your Project Profile:")
    print(json.dumps(profile.to_dict(), indent=2))

    # Get recommendations
    recommendations = selector.get_recommendations(profile)
    selector.display_recommendations(recommendations)

    # Export report
    selector.export_report(profile, recommendations)


def demo_comparison():
    """Demo framework comparison."""
    print("\n" + "="*60)
    print("Demo: Framework Comparison")
    print("="*60)

    selector = FrameworkSelector()

    # Compare main frameworks
    print("\n  Comparing: LangChain, LlamaIndex, CrewAI, LangGraph")
    selector.compare_frameworks(["langchain", "llamaindex", "crewai", "langgraph"])

    # Use case analysis
    print("\n" + "-"*40)
    print("Use Case → Framework Mapping:")
    print("-"*40)

    use_case_map = {
        UseCase.RAG: "llamaindex",
        UseCase.AGENTS: "langchain",
        UseCase.MULTI_AGENT: "crewai",
        UseCase.CODE_GEN: "autogen",
        UseCase.SEARCH: "haystack",
    }

    for use_case, framework in use_case_map.items():
        fw = FRAMEWORKS[framework]
        print(f"\n  {use_case.value.upper()} → {fw.name}")
        print(f"    {fw.description}")


def demo_quick_analysis():
    """Demo quick requirement analysis."""
    print("\n" + "="*60)
    print("Demo: Quick Requirement Analysis")
    print("="*60)

    selector = FrameworkSelector()

    # Sample profiles
    profiles = [
        ProjectProfile(
            primary_use_case=UseCase.RAG,
            secondary_use_cases=[],
            team_size="small",
            experience_level="beginner",
            production_required=True,
            budget_constraints=True,
            timeline="asap",
            existing_stack=["python"]
        ),
        ProjectProfile(
            primary_use_case=UseCase.MULTI_AGENT,
            secondary_use_cases=[UseCase.CODE_GEN],
            team_size="medium",
            experience_level="advanced",
            production_required=True,
            budget_constraints=False,
            timeline="months",
            existing_stack=["python", "docker", "aws"]
        )
    ]

    for i, profile in enumerate(profiles, 1):
        print(f"\n{'='*40}")
        print(f"Scenario {i}: {profile.primary_use_case.value} application")
        print(f"Team: {profile.team_size}, Experience: {profile.experience_level}")
        print(f"{'='*40}")

        recommendations = selector.get_recommendations(profile, top_n=2)

        for rec in recommendations:
            fw = FRAMEWORKS[rec.framework]
            print(f"\n  Recommended: {fw.name} ({rec.score*100:.0f}%)")
            print(f"    {rec.reasons[0]}")


def demo_all():
    """Run all demos."""
    print("="*60)
    print("Framework Selector - Full Demo")
    print("="*60)

    demo_comparison()
    demo_quick_analysis()

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("""
    The Framework Selector helps you choose:

    1. LLAMAINDEX for RAG-focused applications
       - Simple API, great indexing
       - 150+ data connectors

    2. LANGCHAIN for flexible LLM applications
       - Maximum flexibility
       - Large ecosystem

    3. LANGGRAPH for stateful agent workflows
       - Production-ready
       - Complex state management

    4. CREWAI for role-based multi-agent
       - Easy to understand
       - Quick prototypes

    5. AUTOGEN for conversational research
       - Code execution built-in
       - Human-in-the-loop

    Run 'recommend' for personalized recommendations!
    """)


def print_usage():
    """Print usage information."""
    print("""
Framework Selector Toolkit - Module 19 Deliverable
===================================================

Helps you choose the right AI framework for your project.

Usage:
    python deliverable_framework_selector.py <command>

Commands:
    recommend   - Interactive questionnaire for recommendations
    compare     - Compare frameworks side-by-side
    analyze     - Quick requirement analysis with sample profiles
    demo        - Run all demonstrations
    export      - Export comparison report (requires recommend first)
    help        - Show this help message

Features:
    - Interactive questionnaire
    - Scoring based on requirements
    - Framework comparison matrix
    - Export recommendations to markdown
    - Use case matching

Frameworks Covered:
    - LangChain & LangGraph
    - LlamaIndex
    - CrewAI
    - AutoGen
    - Haystack
    - Semantic Kernel
""")


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == "recommend":
        demo_interactive()
    elif command == "compare":
        demo_comparison()
    elif command == "analyze":
        demo_quick_analysis()
    elif command == "demo":
        demo_all()
    elif command == "export":
        print("Run 'recommend' first to generate a profile, then export.")
    elif command == "help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
