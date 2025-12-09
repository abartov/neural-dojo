"""
Agent-First IDE Comparison Toolkit

A comprehensive toolkit for comparing and benchmarking modern AI-powered IDEs.
Covers Google Antigravity, Windsurf, Cline, and Cursor with feature matrices,
task suitability analysis, and configuration recommendations.

Features:
- Feature comparison matrix across all major agent-first IDEs
- Task complexity analysis and IDE recommendations
- Cost analysis for different usage patterns
- Configuration templates and best practices
- Decision tree for IDE selection

Usage:
    python deliverable_ide_comparison_toolkit.py demo1  # Feature comparison
    python deliverable_ide_comparison_toolkit.py demo2  # Task suitability
    python deliverable_ide_comparison_toolkit.py demo3  # Cost analysis
    python deliverable_ide_comparison_toolkit.py demo4  # Decision helper
    python deliverable_ide_comparison_toolkit.py help   # Show usage

Author: Neural Dojo
Module: 1.4 - Agent-First IDEs
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


# ============================================================================
# Data Models
# ============================================================================

class PricingTier(Enum):
    FREE = "free"
    FREEMIUM = "freemium"
    PAID = "paid"
    ENTERPRISE = "enterprise"


class AgentCapability(Enum):
    AUTOCOMPLETE = "autocomplete"
    CHAT = "chat"
    MULTI_FILE = "multi_file"
    AUTONOMOUS = "autonomous"
    MULTI_AGENT = "multi_agent"
    BROWSER_CONTROL = "browser_control"
    MEMORY = "memory"
    VOICE = "voice"


class TaskComplexity(Enum):
    SIMPLE = "simple"          # Single file, quick fix
    MODERATE = "moderate"      # Multi-file, clear scope
    COMPLEX = "complex"        # Architecture changes, planning needed
    AUTONOMOUS = "autonomous"  # Full feature implementation


@dataclass
class IDEFeature:
    """Represents a single IDE feature."""
    name: str
    supported: bool
    quality: int  # 1-5 rating
    notes: str = ""


@dataclass
class IDEProfile:
    """Complete profile of an agent-first IDE."""
    name: str
    vendor: str
    base_editor: str
    release_date: str
    pricing_tier: PricingTier
    monthly_cost_usd: float
    capabilities: list[AgentCapability]
    features: dict[str, IDEFeature]
    supported_models: list[str]
    extensibility: str
    strengths: list[str]
    weaknesses: list[str]
    best_for: list[str]
    website: str


@dataclass
class TaskRecommendation:
    """Recommendation for which IDE to use for a task."""
    task_type: str
    complexity: TaskComplexity
    recommended_ide: str
    alternatives: list[str]
    reasoning: str


@dataclass
class CostAnalysis:
    """Cost analysis for IDE usage."""
    ide_name: str
    monthly_base: float
    api_cost_estimate: float
    total_monthly: float
    cost_per_task: float
    notes: str


@dataclass
class ComparisonResult:
    """Result of comparing IDEs."""
    timestamp: str
    profiles: list[dict]
    feature_matrix: dict[str, dict[str, bool]]
    recommendations: list[dict]
    cost_analyses: list[dict]


# ============================================================================
# IDE Database
# ============================================================================

def get_ide_profiles() -> list[IDEProfile]:
    """Get comprehensive profiles for all agent-first IDEs."""

    profiles = [
        IDEProfile(
            name="Google Antigravity",
            vendor="Google",
            base_editor="VS Code Fork",
            release_date="2025-11",
            pricing_tier=PricingTier.FREEMIUM,
            monthly_cost_usd=0.0,  # Free with API costs
            capabilities=[
                AgentCapability.AUTOCOMPLETE,
                AgentCapability.CHAT,
                AgentCapability.MULTI_FILE,
                AgentCapability.AUTONOMOUS,
                AgentCapability.MULTI_AGENT,
                AgentCapability.BROWSER_CONTROL,
            ],
            features={
                "multi_agent": IDEFeature("Multi-Agent System", True, 5, "Mission Control orchestrates specialized agents"),
                "browser_control": IDEFeature("Browser Automation", True, 5, "Chrome extension for web interaction"),
                "artifacts": IDEFeature("Rich Artifacts", True, 4, "Interactive previews, diagrams"),
                "memory": IDEFeature("Session Memory", True, 3, "Context within session"),
                "mcp_support": IDEFeature("MCP Support", True, 4, "Tool extensibility"),
                "voice_input": IDEFeature("Voice Input", False, 0, "Not supported"),
                "local_models": IDEFeature("Local Models", False, 0, "Gemini only"),
                "git_integration": IDEFeature("Git Integration", True, 4, "Standard VS Code git"),
            },
            supported_models=["Gemini 2.0 Flash", "Gemini 2.0 Pro"],
            extensibility="MCP servers, VS Code extensions",
            strengths=[
                "Multi-agent orchestration (Mission Control)",
                "Browser automation for testing",
                "Rich artifact rendering",
                "Free tier with generous limits",
                "Google ecosystem integration",
            ],
            weaknesses=[
                "Gemini models only",
                "New, less battle-tested",
                "Limited customization",
                "No local model support",
            ],
            best_for=[
                "Full-stack web development",
                "Projects needing browser automation",
                "Google Cloud deployments",
                "Teams wanting multi-agent capabilities",
            ],
            website="https://idx.google.com/antigravity",
        ),
        IDEProfile(
            name="Windsurf",
            vendor="Codeium",
            base_editor="VS Code Fork",
            release_date="2024-11",
            pricing_tier=PricingTier.FREEMIUM,
            monthly_cost_usd=15.0,  # Pro tier
            capabilities=[
                AgentCapability.AUTOCOMPLETE,
                AgentCapability.CHAT,
                AgentCapability.MULTI_FILE,
                AgentCapability.AUTONOMOUS,
                AgentCapability.MEMORY,
            ],
            features={
                "multi_agent": IDEFeature("Multi-Agent System", False, 0, "Single Cascade agent"),
                "browser_control": IDEFeature("Browser Automation", False, 0, "Not supported"),
                "artifacts": IDEFeature("Rich Artifacts", True, 3, "Code previews"),
                "memory": IDEFeature("Session Memory", True, 5, "Flows - persistent memory across sessions"),
                "mcp_support": IDEFeature("MCP Support", True, 4, "Tool extensibility"),
                "voice_input": IDEFeature("Voice Input", False, 0, "Not supported"),
                "local_models": IDEFeature("Local Models", False, 0, "Cloud models only"),
                "git_integration": IDEFeature("Git Integration", True, 4, "Enhanced git features"),
            },
            supported_models=["GPT-4o", "Claude 3.5 Sonnet", "Codeium models"],
            extensibility="MCP servers, Flows customization",
            strengths=[
                "Flows - persistent memory system",
                "Cascade for autonomous coding",
                "Multiple model support",
                "Generous free tier",
                "Fast autocomplete",
            ],
            weaknesses=[
                "No multi-agent orchestration",
                "No browser automation",
                "Limited artifact types",
                "Newer than Cursor",
            ],
            best_for=[
                "Long-running projects needing memory",
                "Developers wanting model flexibility",
                "Budget-conscious teams",
                "Codeium ecosystem users",
            ],
            website="https://codeium.com/windsurf",
        ),
        IDEProfile(
            name="Cline",
            vendor="Cline (Open Source)",
            base_editor="VS Code Extension",
            release_date="2024-06",
            pricing_tier=PricingTier.FREE,
            monthly_cost_usd=0.0,  # Open source, pay for API
            capabilities=[
                AgentCapability.AUTOCOMPLETE,
                AgentCapability.CHAT,
                AgentCapability.MULTI_FILE,
                AgentCapability.AUTONOMOUS,
            ],
            features={
                "multi_agent": IDEFeature("Multi-Agent System", False, 0, "Single agent"),
                "browser_control": IDEFeature("Browser Automation", True, 3, "Via MCP tools"),
                "artifacts": IDEFeature("Rich Artifacts", False, 0, "Limited"),
                "memory": IDEFeature("Session Memory", True, 3, "Context within session"),
                "mcp_support": IDEFeature("MCP Support", True, 5, "First-class MCP support"),
                "voice_input": IDEFeature("Voice Input", False, 0, "Not built-in"),
                "local_models": IDEFeature("Local Models", True, 5, "Full Ollama support"),
                "git_integration": IDEFeature("Git Integration", True, 3, "Basic git operations"),
            },
            supported_models=["Any OpenAI-compatible", "Claude", "Ollama", "OpenRouter"],
            extensibility="MCP servers, open source customization",
            strengths=[
                "Fully open source",
                "Model agnostic",
                "Local model support",
                "MCP extensibility",
                "No vendor lock-in",
                "Active community",
            ],
            weaknesses=[
                "Requires configuration",
                "No built-in memory persistence",
                "Less polished UX",
                "Single agent only",
            ],
            best_for=[
                "Privacy-conscious developers",
                "Local model enthusiasts",
                "Developers wanting customization",
                "Open source advocates",
            ],
            website="https://github.com/cline/cline",
        ),
        IDEProfile(
            name="Cursor",
            vendor="Anysphere",
            base_editor="VS Code Fork",
            release_date="2023-03",
            pricing_tier=PricingTier.FREEMIUM,
            monthly_cost_usd=20.0,  # Pro tier
            capabilities=[
                AgentCapability.AUTOCOMPLETE,
                AgentCapability.CHAT,
                AgentCapability.MULTI_FILE,
                AgentCapability.AUTONOMOUS,
            ],
            features={
                "multi_agent": IDEFeature("Multi-Agent System", False, 0, "Single Composer agent"),
                "browser_control": IDEFeature("Browser Automation", False, 0, "Not supported"),
                "artifacts": IDEFeature("Rich Artifacts", True, 4, "Code diffs, previews"),
                "memory": IDEFeature("Session Memory", True, 3, "Chat history"),
                "mcp_support": IDEFeature("MCP Support", False, 0, "Not supported"),
                "voice_input": IDEFeature("Voice Input", False, 0, "Not supported"),
                "local_models": IDEFeature("Local Models", True, 3, "Limited support"),
                "git_integration": IDEFeature("Git Integration", True, 5, "Excellent git features"),
            },
            supported_models=["GPT-4o", "Claude 3.5 Sonnet", "cursor-small"],
            extensibility="VS Code extensions only",
            strengths=[
                "Most mature product",
                "Excellent UX/polish",
                "Strong Composer mode",
                "Good model selection",
                "Large user community",
            ],
            weaknesses=[
                "No MCP support",
                "No multi-agent",
                "Higher price point",
                "Less extensible",
            ],
            best_for=[
                "Developers wanting polish",
                "Teams needing stability",
                "Quick adoption needs",
                "VS Code power users",
            ],
            website="https://cursor.com",
        ),
    ]

    return profiles


# ============================================================================
# Analysis Functions
# ============================================================================

def generate_feature_matrix(profiles: list[IDEProfile]) -> dict[str, dict[str, bool]]:
    """Generate a feature comparison matrix."""
    features = [
        "multi_agent",
        "browser_control",
        "artifacts",
        "memory",
        "mcp_support",
        "voice_input",
        "local_models",
        "git_integration",
    ]

    matrix = {}
    for feature in features:
        matrix[feature] = {}
        for profile in profiles:
            if feature in profile.features:
                matrix[feature][profile.name] = profile.features[feature].supported
            else:
                matrix[feature][profile.name] = False

    return matrix


def get_task_recommendations() -> list[TaskRecommendation]:
    """Get IDE recommendations for different task types."""

    recommendations = [
        TaskRecommendation(
            task_type="Quick bug fix",
            complexity=TaskComplexity.SIMPLE,
            recommended_ide="Cursor",
            alternatives=["Windsurf", "Cline"],
            reasoning="Cursor's polished UX makes quick fixes efficient",
        ),
        TaskRecommendation(
            task_type="Multi-file refactoring",
            complexity=TaskComplexity.MODERATE,
            recommended_ide="Cursor",
            alternatives=["Windsurf", "Antigravity"],
            reasoning="Composer mode excels at coordinated multi-file changes",
        ),
        TaskRecommendation(
            task_type="Full feature implementation",
            complexity=TaskComplexity.COMPLEX,
            recommended_ide="Google Antigravity",
            alternatives=["Windsurf"],
            reasoning="Multi-agent orchestration handles complex planning",
        ),
        TaskRecommendation(
            task_type="Web app with testing",
            complexity=TaskComplexity.COMPLEX,
            recommended_ide="Google Antigravity",
            alternatives=["Cursor"],
            reasoning="Browser automation enables end-to-end testing",
        ),
        TaskRecommendation(
            task_type="Long-running project",
            complexity=TaskComplexity.COMPLEX,
            recommended_ide="Windsurf",
            alternatives=["Antigravity"],
            reasoning="Flows memory maintains context across sessions",
        ),
        TaskRecommendation(
            task_type="Privacy-sensitive work",
            complexity=TaskComplexity.MODERATE,
            recommended_ide="Cline",
            alternatives=[],
            reasoning="Local models keep code on your machine",
        ),
        TaskRecommendation(
            task_type="Custom tool integration",
            complexity=TaskComplexity.COMPLEX,
            recommended_ide="Cline",
            alternatives=["Antigravity", "Windsurf"],
            reasoning="Full MCP support for custom tools",
        ),
        TaskRecommendation(
            task_type="Learning/exploration",
            complexity=TaskComplexity.SIMPLE,
            recommended_ide="Cursor",
            alternatives=["Windsurf"],
            reasoning="Best UX for beginners, good documentation",
        ),
    ]

    return recommendations


def calculate_cost_analysis(
    profiles: list[IDEProfile],
    tasks_per_month: int = 100,
    avg_tokens_per_task: int = 5000,
) -> list[CostAnalysis]:
    """Calculate cost analysis for each IDE."""

    # Approximate API costs per 1M tokens
    api_costs = {
        "Google Antigravity": 0.15,  # Gemini pricing
        "Windsurf": 0.0,  # Included in subscription
        "Cline": 3.0,  # Claude pricing (user pays API)
        "Cursor": 0.0,  # Included in subscription
    }

    analyses = []
    for profile in profiles:
        api_cost = api_costs.get(profile.name, 0.0)
        tokens_used = tasks_per_month * avg_tokens_per_task
        monthly_api = (tokens_used / 1_000_000) * api_cost
        total = profile.monthly_cost_usd + monthly_api

        notes = ""
        if profile.name == "Cline":
            notes = "API costs vary by model choice. Local models = $0"
        elif profile.name == "Google Antigravity":
            notes = "Free tier generous; costs only at scale"
        elif profile.name == "Windsurf":
            notes = "API included; 500 premium requests/month"
        elif profile.name == "Cursor":
            notes = "API included; 500 fast requests/month"

        analyses.append(CostAnalysis(
            ide_name=profile.name,
            monthly_base=profile.monthly_cost_usd,
            api_cost_estimate=monthly_api,
            total_monthly=total,
            cost_per_task=total / tasks_per_month if tasks_per_month > 0 else 0,
            notes=notes,
        ))

    return analyses


# ============================================================================
# Storage
# ============================================================================

STORAGE_DIR = Path(".ide_comparison")


def ensure_storage() -> Path:
    """Ensure storage directory exists."""
    STORAGE_DIR.mkdir(exist_ok=True)
    return STORAGE_DIR


def save_comparison(result: ComparisonResult) -> Path:
    """Save comparison result to JSON."""
    ensure_storage()
    filename = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = STORAGE_DIR / filename

    with open(filepath, "w") as f:
        json.dump(asdict(result), f, indent=2, default=str)

    return filepath


def load_latest_comparison() -> Optional[ComparisonResult]:
    """Load the most recent comparison."""
    ensure_storage()
    files = sorted(STORAGE_DIR.glob("comparison_*.json"), reverse=True)

    if not files:
        return None

    with open(files[0]) as f:
        data = json.load(f)

    return data  # Return as dict for simplicity


# ============================================================================
# Display Functions
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_feature_matrix(matrix: dict[str, dict[str, bool]], profiles: list[IDEProfile]) -> None:
    """Print the feature comparison matrix."""
    print_header("Feature Comparison Matrix")

    # Header
    ide_names = [p.name for p in profiles]
    header = f"{'Feature':<25}"
    for name in ide_names:
        short_name = name[:12]
        header += f" {short_name:^12}"
    print(header)
    print("-" * 70)

    # Feature labels for display
    feature_labels = {
        "multi_agent": "Multi-Agent System",
        "browser_control": "Browser Automation",
        "artifacts": "Rich Artifacts",
        "memory": "Persistent Memory",
        "mcp_support": "MCP Support",
        "voice_input": "Voice Input",
        "local_models": "Local Models",
        "git_integration": "Git Integration",
    }

    for feature, ide_support in matrix.items():
        label = feature_labels.get(feature, feature)
        row = f"{label:<25}"
        for name in ide_names:
            supported = ide_support.get(name, False)
            symbol = "✅" if supported else "❌"
            row += f" {symbol:^12}"
        print(row)


def print_ide_profiles(profiles: list[IDEProfile]) -> None:
    """Print detailed IDE profiles."""
    print_header("IDE Profiles")

    for profile in profiles:
        print(f"\n{'─' * 50}")
        print(f"📦 {profile.name}")
        print(f"{'─' * 50}")
        print(f"  Vendor: {profile.vendor}")
        print(f"  Base: {profile.base_editor}")
        print(f"  Released: {profile.release_date}")
        print(f"  Pricing: {profile.pricing_tier.value} (${profile.monthly_cost_usd}/mo)")
        print(f"  Website: {profile.website}")

        print(f"\n  Supported Models:")
        for model in profile.supported_models:
            print(f"    • {model}")

        print(f"\n  Strengths:")
        for strength in profile.strengths[:3]:
            print(f"    ✅ {strength}")

        print(f"\n  Weaknesses:")
        for weakness in profile.weaknesses[:3]:
            print(f"    ⚠️ {weakness}")

        print(f"\n  Best For:")
        for use_case in profile.best_for[:3]:
            print(f"    🎯 {use_case}")


def print_recommendations(recommendations: list[TaskRecommendation]) -> None:
    """Print task-based recommendations."""
    print_header("Task-Based Recommendations")

    for rec in recommendations:
        complexity_emoji = {
            TaskComplexity.SIMPLE: "🟢",
            TaskComplexity.MODERATE: "🟡",
            TaskComplexity.COMPLEX: "🔴",
            TaskComplexity.AUTONOMOUS: "🟣",
        }

        emoji = complexity_emoji.get(rec.complexity, "⚪")
        print(f"\n{emoji} {rec.task_type} ({rec.complexity.value})")
        print(f"   Recommended: {rec.recommended_ide}")
        if rec.alternatives:
            print(f"   Alternatives: {', '.join(rec.alternatives)}")
        print(f"   Why: {rec.reasoning}")


def print_cost_analysis(analyses: list[CostAnalysis]) -> None:
    """Print cost analysis table."""
    print_header("Cost Analysis (100 tasks/month estimate)")

    print(f"\n{'IDE':<20} {'Base':<10} {'API Est.':<12} {'Total':<10} {'Per Task':<10}")
    print("-" * 70)

    for analysis in sorted(analyses, key=lambda x: x.total_monthly):
        print(
            f"{analysis.ide_name:<20} "
            f"${analysis.monthly_base:<9.2f} "
            f"${analysis.api_cost_estimate:<11.2f} "
            f"${analysis.total_monthly:<9.2f} "
            f"${analysis.cost_per_task:<9.4f}"
        )
        if analysis.notes:
            print(f"   ℹ️ {analysis.notes}")


def print_decision_tree() -> None:
    """Print an interactive decision helper."""
    print_header("IDE Selection Decision Tree")

    tree = """
    Start Here: What's your priority?
    │
    ├─► Privacy/Local Models → Cline
    │   "Keep code on your machine with Ollama"
    │
    ├─► Multi-Agent/Complex Tasks → Google Antigravity
    │   "Mission Control orchestrates specialized agents"
    │
    ├─► Long-Running Projects → Windsurf
    │   "Flows memory remembers context across sessions"
    │
    ├─► Polish/Stability → Cursor
    │   "Most mature, excellent UX"
    │
    └─► Budget Conscious?
        │
        ├─► Yes, want features → Windsurf Free / Cline
        │
        └─► Yes, Google ecosystem → Antigravity (free tier)
    """
    print(tree)

    print("\n📋 Quick Selection Guide:")
    print("  • Need browser testing? → Antigravity")
    print("  • Need MCP tools? → Cline or Antigravity")
    print("  • Need persistent memory? → Windsurf")
    print("  • Need stability? → Cursor")
    print("  • Need local models? → Cline")
    print("  • Need multi-agent? → Antigravity")


# ============================================================================
# Demo Functions
# ============================================================================

def demo_1_feature_comparison() -> None:
    """Demo 1: Feature comparison matrix."""
    print("\n🔬 DEMO 1: Feature Comparison Matrix")
    print("Comparing features across all agent-first IDEs...\n")

    profiles = get_ide_profiles()
    matrix = generate_feature_matrix(profiles)

    print_feature_matrix(matrix, profiles)
    print_ide_profiles(profiles)

    # Save results
    result = ComparisonResult(
        timestamp=datetime.now().isoformat(),
        profiles=[asdict(p) for p in profiles],
        feature_matrix=matrix,
        recommendations=[],
        cost_analyses=[],
    )
    filepath = save_comparison(result)
    print(f"\n💾 Results saved to: {filepath}")


def demo_2_task_suitability() -> None:
    """Demo 2: Task suitability analysis."""
    print("\n🎯 DEMO 2: Task Suitability Analysis")
    print("Which IDE is best for which tasks?\n")

    recommendations = get_task_recommendations()
    print_recommendations(recommendations)

    print("\n" + "=" * 70)
    print("📊 Summary by Complexity Level:")
    print("=" * 70)

    for complexity in TaskComplexity:
        matching = [r for r in recommendations if r.complexity == complexity]
        if matching:
            print(f"\n{complexity.value.upper()} tasks:")
            ide_counts: dict[str, int] = {}
            for rec in matching:
                ide_counts[rec.recommended_ide] = ide_counts.get(rec.recommended_ide, 0) + 1
            for ide, count in sorted(ide_counts.items(), key=lambda x: -x[1]):
                print(f"  • {ide}: {count} task types")


def demo_3_cost_analysis() -> None:
    """Demo 3: Cost analysis."""
    print("\n💰 DEMO 3: Cost Analysis")
    print("Estimating monthly costs for different usage patterns...\n")

    profiles = get_ide_profiles()

    # Light usage
    print("📉 Light Usage (50 tasks/month, 3k tokens each):")
    light = calculate_cost_analysis(profiles, tasks_per_month=50, avg_tokens_per_task=3000)
    print_cost_analysis(light)

    # Heavy usage
    print("\n📈 Heavy Usage (200 tasks/month, 8k tokens each):")
    heavy = calculate_cost_analysis(profiles, tasks_per_month=200, avg_tokens_per_task=8000)
    print_cost_analysis(heavy)

    print("\n💡 Cost Optimization Tips:")
    print("  1. Use Cline with local models for $0 API costs")
    print("  2. Antigravity free tier is generous for most developers")
    print("  3. Windsurf/Cursor subscriptions include API - good value for heavy users")
    print("  4. Mix IDEs: Cline for bulk work, paid IDE for complex tasks")


def demo_4_decision_helper() -> None:
    """Demo 4: Interactive decision helper."""
    print("\n🧭 DEMO 4: IDE Selection Decision Helper")
    print("Find the right IDE for your needs...\n")

    print_decision_tree()

    print("\n" + "=" * 70)
    print("🏆 Winner by Category:")
    print("=" * 70)

    categories = [
        ("Best for Beginners", "Cursor", "Polished UX, great documentation"),
        ("Best for Privacy", "Cline", "Local models, open source"),
        ("Best for Complex Tasks", "Google Antigravity", "Multi-agent orchestration"),
        ("Best for Long Projects", "Windsurf", "Flows persistent memory"),
        ("Best Free Option", "Cline", "Open source, pay only for API"),
        ("Best Value", "Windsurf", "Good free tier, reasonable pro"),
        ("Most Extensible", "Cline", "Full MCP + open source"),
        ("Most Stable", "Cursor", "Longest track record"),
    ]

    for category, winner, reason in categories:
        print(f"\n  {category}: {winner}")
        print(f"    └─ {reason}")


def show_help() -> None:
    """Show usage information."""
    print("""
Agent-First IDE Comparison Toolkit
==================================

A comprehensive toolkit for comparing modern AI-powered IDEs.

Usage:
    python deliverable_ide_comparison_toolkit.py <command>

Commands:
    demo1    Feature comparison matrix across all IDEs
    demo2    Task suitability analysis and recommendations
    demo3    Cost analysis for different usage patterns
    demo4    Interactive decision helper for IDE selection
    help     Show this help message

Examples:
    python deliverable_ide_comparison_toolkit.py demo1
    python deliverable_ide_comparison_toolkit.py demo3

IDEs Covered:
    • Google Antigravity - Multi-agent with browser control
    • Windsurf - Cascade + Flows memory system
    • Cline - Open source, model agnostic
    • Cursor - Most polished, Composer mode

Data Storage:
    Results are saved to .ide_comparison/ directory
""")


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "demo1": demo_1_feature_comparison,
        "demo2": demo_2_task_suitability,
        "demo3": demo_3_cost_analysis,
        "demo4": demo_4_decision_helper,
        "help": show_help,
        "--help": show_help,
        "-h": show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
