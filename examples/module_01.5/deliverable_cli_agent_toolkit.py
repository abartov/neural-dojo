"""
CLI AI Coding Agents Toolkit

A comprehensive toolkit for working with command-line AI coding agents.
Covers Claude Code, Aider, Goose with workflow automation, metrics tracking,
and multi-agent pipeline orchestration.

Features:
- Single-agent task execution with multiple CLI agents
- Multi-agent pipeline orchestration
- Automated code review workflow
- Usage metrics and cost tracking
- Configuration templates for each agent

Usage:
    python deliverable_cli_agent_toolkit.py demo1  # Single-agent tasks
    python deliverable_cli_agent_toolkit.py demo2  # Multi-agent pipeline
    python deliverable_cli_agent_toolkit.py demo3  # Code review workflow
    python deliverable_cli_agent_toolkit.py demo4  # Usage metrics
    python deliverable_cli_agent_toolkit.py help   # Show usage

Author: Neural Dojo
Module: 1.5 - CLI AI Coding Agents
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Callable


# ============================================================================
# Data Models
# ============================================================================

class AgentType(Enum):
    CLAUDE_CODE = "claude_code"
    AIDER = "aider"
    GOOSE = "goose"
    COPILOT_CLI = "copilot_cli"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentConfig:
    """Configuration for a CLI agent."""
    name: str
    agent_type: AgentType
    command: str
    available: bool
    env_vars: list[str]
    supports_non_interactive: bool
    supports_stdin: bool
    default_args: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of executing a task with an agent."""
    agent: str
    task: str
    status: TaskStatus
    duration_seconds: float
    output: str
    error: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0


@dataclass
class PipelineStep:
    """A step in a multi-agent pipeline."""
    name: str
    agent_type: AgentType
    prompt: str
    files: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    timeout_seconds: int = 120


@dataclass
class MetricsRecord:
    """Metrics for agent usage."""
    timestamp: str
    agent: str
    task_type: str
    duration_seconds: float
    tokens_used: int
    cost_usd: float
    success: bool


@dataclass
class AgentComparison:
    """Comparison result between agents."""
    task: str
    results: dict[str, TaskResult]
    winner: str
    reasoning: str


# ============================================================================
# Agent Detection & Configuration
# ============================================================================

def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    try:
        result = subprocess.run(
            ["which", command],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_env_var(var: str) -> bool:
    """Check if an environment variable is set."""
    return bool(os.environ.get(var))


def get_agent_configs() -> dict[AgentType, AgentConfig]:
    """Get configuration for all supported CLI agents."""

    configs = {
        AgentType.CLAUDE_CODE: AgentConfig(
            name="Claude Code",
            agent_type=AgentType.CLAUDE_CODE,
            command="claude",
            available=check_command_exists("claude"),
            env_vars=["ANTHROPIC_API_KEY"],
            supports_non_interactive=True,
            supports_stdin=True,
            default_args=["--print"],
        ),
        AgentType.AIDER: AgentConfig(
            name="Aider",
            agent_type=AgentType.AIDER,
            command="aider",
            available=check_command_exists("aider"),
            env_vars=["OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
            supports_non_interactive=True,
            supports_stdin=False,
            default_args=["--yes", "--no-git"],
        ),
        AgentType.GOOSE: AgentConfig(
            name="Goose",
            agent_type=AgentType.GOOSE,
            command="goose",
            available=check_command_exists("goose"),
            env_vars=["OPENAI_API_KEY"],
            supports_non_interactive=True,
            supports_stdin=False,
            default_args=[],
        ),
        AgentType.COPILOT_CLI: AgentConfig(
            name="GitHub Copilot CLI",
            agent_type=AgentType.COPILOT_CLI,
            command="gh",
            available=check_command_exists("gh"),
            env_vars=["GITHUB_TOKEN"],
            supports_non_interactive=True,
            supports_stdin=False,
            default_args=["copilot", "suggest"],
        ),
    }

    return configs


def detect_available_agents() -> list[AgentConfig]:
    """Detect which CLI agents are available."""
    configs = get_agent_configs()
    available = []

    for config in configs.values():
        if config.available:
            # Check if required env vars are set
            has_env = any(check_env_var(var) for var in config.env_vars)
            if has_env or not config.env_vars:
                available.append(config)

    return available


# ============================================================================
# Task Execution
# ============================================================================

def execute_with_agent(
    agent_config: AgentConfig,
    prompt: str,
    files: list[str] = None,
    timeout: int = 120,
    simulate: bool = True,
) -> TaskResult:
    """Execute a task with a specific CLI agent."""
    start_time = time.time()
    files = files or []

    if simulate:
        # Simulate execution for demo purposes
        time.sleep(0.5)  # Simulate some work
        duration = time.time() - start_time

        # Simulated responses based on agent type
        responses = {
            AgentType.CLAUDE_CODE: f"[Claude Code] Analyzed: {prompt[:50]}...\nSuggested changes applied.",
            AgentType.AIDER: f"[Aider] Committed changes for: {prompt[:50]}...\nGit commit: abc123",
            AgentType.GOOSE: f"[Goose] Executed toolkit for: {prompt[:50]}...\nTask complete.",
            AgentType.COPILOT_CLI: f"[Copilot] Suggested command for: {prompt[:50]}...",
        }

        return TaskResult(
            agent=agent_config.name,
            task=prompt[:100],
            status=TaskStatus.SUCCESS,
            duration_seconds=duration,
            output=responses.get(agent_config.agent_type, "Task completed"),
            tokens_used=len(prompt.split()) * 10,  # Rough estimate
            cost_usd=0.001 * len(prompt.split()),  # Rough estimate
        )

    # Real execution (when simulate=False)
    try:
        cmd = [agent_config.command] + agent_config.default_args

        if agent_config.agent_type == AgentType.CLAUDE_CODE:
            cmd.extend(["-p", prompt])
            if files:
                for f in files:
                    cmd.extend(["--file", f])

        elif agent_config.agent_type == AgentType.AIDER:
            cmd.extend(["--message", prompt])
            cmd.extend(files)

        elif agent_config.agent_type == AgentType.GOOSE:
            cmd.extend(["run", "--message", prompt])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        duration = time.time() - start_time

        return TaskResult(
            agent=agent_config.name,
            task=prompt[:100],
            status=TaskStatus.SUCCESS if result.returncode == 0 else TaskStatus.FAILED,
            duration_seconds=duration,
            output=result.stdout,
            error=result.stderr,
        )

    except subprocess.TimeoutExpired:
        return TaskResult(
            agent=agent_config.name,
            task=prompt[:100],
            status=TaskStatus.FAILED,
            duration_seconds=timeout,
            output="",
            error=f"Task timed out after {timeout} seconds",
        )
    except Exception as e:
        return TaskResult(
            agent=agent_config.name,
            task=prompt[:100],
            status=TaskStatus.FAILED,
            duration_seconds=time.time() - start_time,
            output="",
            error=str(e),
        )


# ============================================================================
# Pipeline Orchestration
# ============================================================================

def run_pipeline(
    steps: list[PipelineStep],
    simulate: bool = True,
) -> list[TaskResult]:
    """Run a multi-step pipeline with different agents."""
    configs = get_agent_configs()
    results = []
    completed_steps: dict[str, TaskResult] = {}

    print("\n🔄 Starting pipeline execution...")
    print("=" * 60)

    for i, step in enumerate(steps, 1):
        print(f"\n📍 Step {i}/{len(steps)}: {step.name}")

        # Check dependencies
        deps_met = all(
            dep in completed_steps and completed_steps[dep].status == TaskStatus.SUCCESS
            for dep in step.depends_on
        )

        if not deps_met:
            print(f"   ⏭️ Skipping: Dependencies not met ({step.depends_on})")
            result = TaskResult(
                agent=configs[step.agent_type].name,
                task=step.prompt[:100],
                status=TaskStatus.SKIPPED,
                duration_seconds=0,
                output="",
                error="Dependencies not met",
            )
            results.append(result)
            continue

        config = configs.get(step.agent_type)
        if not config:
            print(f"   ❌ Unknown agent type: {step.agent_type}")
            continue

        print(f"   🤖 Agent: {config.name}")
        print(f"   📝 Task: {step.prompt[:60]}...")

        result = execute_with_agent(
            config,
            step.prompt,
            step.files,
            step.timeout_seconds,
            simulate=simulate,
        )

        results.append(result)
        completed_steps[step.name] = result

        status_emoji = "✅" if result.status == TaskStatus.SUCCESS else "❌"
        print(f"   {status_emoji} Status: {result.status.value}")
        print(f"   ⏱️ Duration: {result.duration_seconds:.2f}s")

    return results


# ============================================================================
# Metrics & Storage
# ============================================================================

STORAGE_DIR = Path(".cli_agent_toolkit")


def ensure_storage() -> Path:
    """Ensure storage directory exists."""
    STORAGE_DIR.mkdir(exist_ok=True)
    return STORAGE_DIR


def save_metrics(record: MetricsRecord) -> None:
    """Append metrics record to storage."""
    ensure_storage()
    metrics_file = STORAGE_DIR / "metrics.jsonl"

    with open(metrics_file, "a") as f:
        f.write(json.dumps(asdict(record)) + "\n")


def load_metrics() -> list[MetricsRecord]:
    """Load all metrics records."""
    ensure_storage()
    metrics_file = STORAGE_DIR / "metrics.jsonl"

    if not metrics_file.exists():
        return []

    records = []
    with open(metrics_file) as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                records.append(MetricsRecord(**data))

    return records


def save_comparison(comparison: AgentComparison) -> Path:
    """Save agent comparison result."""
    ensure_storage()
    filename = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = STORAGE_DIR / filename

    data = {
        "task": comparison.task,
        "results": {k: asdict(v) for k, v in comparison.results.items()},
        "winner": comparison.winner,
        "reasoning": comparison.reasoning,
    }

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)

    return filepath


# ============================================================================
# Display Functions
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_agent_status(configs: dict[AgentType, AgentConfig]) -> None:
    """Print status of all CLI agents."""
    print_header("CLI Agent Status")

    for agent_type, config in configs.items():
        status = "✅ Available" if config.available else "❌ Not found"
        env_status = []
        for var in config.env_vars:
            if check_env_var(var):
                env_status.append(f"✅ {var}")
            else:
                env_status.append(f"❌ {var}")

        print(f"\n{config.name}")
        print(f"  Command: {config.command} {status}")
        print(f"  Environment: {', '.join(env_status) if env_status else 'None required'}")
        print(f"  Non-interactive: {'Yes' if config.supports_non_interactive else 'No'}")


def print_metrics_summary(records: list[MetricsRecord]) -> None:
    """Print summary of usage metrics."""
    print_header("Usage Metrics Summary")

    if not records:
        print("\n📊 No metrics recorded yet.")
        print("   Run some tasks to generate metrics!")
        return

    # Aggregate by agent
    by_agent: dict[str, list[MetricsRecord]] = {}
    for record in records:
        if record.agent not in by_agent:
            by_agent[record.agent] = []
        by_agent[record.agent].append(record)

    print(f"\n📊 Total tasks recorded: {len(records)}")
    print(f"📅 Date range: {records[0].timestamp[:10]} to {records[-1].timestamp[:10]}")

    print(f"\n{'Agent':<20} {'Tasks':<8} {'Success':<10} {'Avg Time':<12} {'Total Cost':<12}")
    print("-" * 70)

    for agent, agent_records in by_agent.items():
        total = len(agent_records)
        success = sum(1 for r in agent_records if r.success)
        avg_time = sum(r.duration_seconds for r in agent_records) / total
        total_cost = sum(r.cost_usd for r in agent_records)

        success_rate = (success / total * 100) if total > 0 else 0

        print(
            f"{agent:<20} {total:<8} {success_rate:<9.1f}% {avg_time:<11.2f}s ${total_cost:<11.4f}"
        )


def print_pipeline_results(results: list[TaskResult]) -> None:
    """Print pipeline execution results."""
    print_header("Pipeline Results Summary")

    success = sum(1 for r in results if r.status == TaskStatus.SUCCESS)
    failed = sum(1 for r in results if r.status == TaskStatus.FAILED)
    skipped = sum(1 for r in results if r.status == TaskStatus.SKIPPED)
    total_time = sum(r.duration_seconds for r in results)

    print(f"\n📊 Pipeline Statistics:")
    print(f"   Total steps: {len(results)}")
    print(f"   ✅ Success: {success}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏭️ Skipped: {skipped}")
    print(f"   ⏱️ Total time: {total_time:.2f}s")

    print(f"\n📋 Step Details:")
    for i, result in enumerate(results, 1):
        status_emoji = {"success": "✅", "failed": "❌", "skipped": "⏭️", "pending": "⏳", "running": "🔄"}
        emoji = status_emoji.get(result.status.value, "❓")
        print(f"   {i}. {emoji} [{result.agent}] {result.task[:40]}...")


# ============================================================================
# Demo Functions
# ============================================================================

def demo_1_single_agent() -> None:
    """Demo 1: Single-agent task execution."""
    print("\n🤖 DEMO 1: Single-Agent Task Execution")
    print("Demonstrating task execution with different CLI agents...\n")

    configs = get_agent_configs()
    print_agent_status(configs)

    # Define test tasks
    tasks = [
        ("Explain this code", "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)"),
        ("Add error handling", "Read a file and parse JSON from it"),
        ("Write tests", "Create unit tests for a User class with name and email"),
    ]

    print_header("Task Execution Results")

    for agent_type in [AgentType.CLAUDE_CODE, AgentType.AIDER, AgentType.GOOSE]:
        config = configs[agent_type]
        print(f"\n🔹 Testing {config.name}...")

        for task_name, task_detail in tasks[:2]:  # Just 2 tasks per agent for demo
            prompt = f"{task_name}: {task_detail}"
            result = execute_with_agent(config, prompt, simulate=True)

            status_emoji = "✅" if result.status == TaskStatus.SUCCESS else "❌"
            print(f"   {status_emoji} {task_name}: {result.duration_seconds:.2f}s")

            # Save metrics
            save_metrics(MetricsRecord(
                timestamp=datetime.now().isoformat(),
                agent=config.name,
                task_type=task_name,
                duration_seconds=result.duration_seconds,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                success=result.status == TaskStatus.SUCCESS,
            ))

    print("\n💾 Metrics saved to .cli_agent_toolkit/metrics.jsonl")


def demo_2_multi_agent_pipeline() -> None:
    """Demo 2: Multi-agent pipeline orchestration."""
    print("\n🔄 DEMO 2: Multi-Agent Pipeline Orchestration")
    print("Running a code improvement pipeline with multiple agents...\n")

    # Define a realistic pipeline
    pipeline = [
        PipelineStep(
            name="analyze",
            agent_type=AgentType.CLAUDE_CODE,
            prompt="Analyze this codebase for potential improvements. Focus on code quality, security, and performance.",
            files=["src/main.py"],
            timeout_seconds=60,
        ),
        PipelineStep(
            name="refactor",
            agent_type=AgentType.AIDER,
            prompt="Refactor the code based on the analysis. Apply clean code principles.",
            files=["src/main.py"],
            depends_on=["analyze"],
            timeout_seconds=120,
        ),
        PipelineStep(
            name="add_tests",
            agent_type=AgentType.AIDER,
            prompt="Write comprehensive unit tests for the refactored code.",
            files=["src/main.py", "tests/test_main.py"],
            depends_on=["refactor"],
            timeout_seconds=120,
        ),
        PipelineStep(
            name="document",
            agent_type=AgentType.CLAUDE_CODE,
            prompt="Generate documentation for the refactored code. Include docstrings and a README section.",
            files=["src/main.py"],
            depends_on=["refactor"],
            timeout_seconds=60,
        ),
        PipelineStep(
            name="security_review",
            agent_type=AgentType.CLAUDE_CODE,
            prompt="Perform a security review of all changes. Check for OWASP top 10 vulnerabilities.",
            files=["src/main.py"],
            depends_on=["refactor"],
            timeout_seconds=60,
        ),
    ]

    print("📋 Pipeline Steps:")
    for i, step in enumerate(pipeline, 1):
        deps = f" (depends: {step.depends_on})" if step.depends_on else ""
        print(f"   {i}. {step.name} [{step.agent_type.value}]{deps}")

    results = run_pipeline(pipeline, simulate=True)
    print_pipeline_results(results)


def demo_3_code_review() -> None:
    """Demo 3: Automated code review workflow."""
    print("\n🔍 DEMO 3: Automated Code Review Workflow")
    print("Simulating a comprehensive code review with multiple perspectives...\n")

    configs = get_agent_configs()

    # Simulated code to review
    code_sample = '''
def process_user_data(user_input):
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    result = db.execute(query)
    return eval(result[0])
'''

    print("📝 Code to Review:")
    print("-" * 50)
    print(code_sample)
    print("-" * 50)

    review_aspects = [
        ("Security Review", AgentType.CLAUDE_CODE, "Review for security vulnerabilities, especially injection attacks"),
        ("Performance Review", AgentType.CLAUDE_CODE, "Analyze performance implications and suggest optimizations"),
        ("Code Quality", AgentType.AIDER, "Review code style, readability, and best practices"),
    ]

    print("\n🔄 Running multi-aspect review...")
    all_results = []

    for aspect_name, agent_type, prompt in review_aspects:
        config = configs[agent_type]
        print(f"\n📋 {aspect_name} ({config.name}):")

        full_prompt = f"{prompt}\n\nCode:\n{code_sample}"
        result = execute_with_agent(config, full_prompt, simulate=True)
        all_results.append(result)

        print(f"   Status: {'✅ Complete' if result.status == TaskStatus.SUCCESS else '❌ Failed'}")
        print(f"   Time: {result.duration_seconds:.2f}s")

        # Simulated findings for demo
        if "Security" in aspect_name:
            print("   🚨 Findings:")
            print("      - SQL Injection vulnerability (line 2)")
            print("      - eval() on untrusted data (line 4)")
        elif "Performance" in aspect_name:
            print("   ⚡ Findings:")
            print("      - No prepared statements")
            print("      - Missing connection pooling")
        else:
            print("   📊 Findings:")
            print("      - Missing type hints")
            print("      - No error handling")

    print_header("Review Summary")
    print("\n🎯 Critical Issues Found: 2")
    print("⚠️ Warnings: 3")
    print("ℹ️ Suggestions: 2")
    print("\n📝 Recommended Actions:")
    print("   1. [CRITICAL] Fix SQL injection - use parameterized queries")
    print("   2. [CRITICAL] Remove eval() - use safe parsing")
    print("   3. [HIGH] Add input validation")
    print("   4. [MEDIUM] Add type hints")
    print("   5. [LOW] Add error handling")


def demo_4_metrics() -> None:
    """Demo 4: Usage metrics and reporting."""
    print("\n📊 DEMO 4: Usage Metrics and Reporting")
    print("Analyzing CLI agent usage patterns...\n")

    # Generate some sample metrics if none exist
    records = load_metrics()

    if len(records) < 5:
        print("📝 Generating sample metrics data...")
        sample_data = [
            ("Claude Code", "code_review", 5.2, 1500, 0.015, True),
            ("Claude Code", "refactor", 12.1, 3200, 0.032, True),
            ("Aider", "bug_fix", 8.7, 2100, 0.021, True),
            ("Aider", "add_tests", 15.3, 4500, 0.045, True),
            ("Goose", "automation", 6.4, 1800, 0.018, False),
            ("Claude Code", "explain", 3.1, 800, 0.008, True),
            ("Aider", "refactor", 18.2, 5200, 0.052, True),
            ("Claude Code", "security_scan", 7.5, 2000, 0.020, True),
        ]

        for agent, task, duration, tokens, cost, success in sample_data:
            save_metrics(MetricsRecord(
                timestamp=datetime.now().isoformat(),
                agent=agent,
                task_type=task,
                duration_seconds=duration,
                tokens_used=tokens,
                cost_usd=cost,
                success=success,
            ))

        records = load_metrics()

    print_metrics_summary(records)

    # Additional analysis
    print_header("Cost Analysis")

    total_cost = sum(r.cost_usd for r in records)
    total_tokens = sum(r.tokens_used for r in records)
    avg_cost_per_task = total_cost / len(records) if records else 0

    print(f"\n💰 Total cost: ${total_cost:.4f}")
    print(f"🎟️ Total tokens: {total_tokens:,}")
    print(f"📊 Average cost per task: ${avg_cost_per_task:.4f}")

    # Cost by agent
    print("\n📈 Cost by Agent:")
    by_agent: dict[str, float] = {}
    for record in records:
        by_agent[record.agent] = by_agent.get(record.agent, 0) + record.cost_usd

    for agent, cost in sorted(by_agent.items(), key=lambda x: -x[1]):
        pct = (cost / total_cost * 100) if total_cost > 0 else 0
        bar = "█" * int(pct / 5)
        print(f"   {agent:<15} ${cost:.4f} ({pct:.1f}%) {bar}")

    print_header("Recommendations")
    print("\n💡 Based on your usage patterns:")
    print("   1. Claude Code is most efficient for code review tasks")
    print("   2. Consider using Aider for larger refactoring (git integration)")
    print("   3. Goose had lower success rate - check toolkit configuration")
    print("   4. Average task cost is reasonable at ${:.4f}".format(avg_cost_per_task))


def show_help() -> None:
    """Show usage information."""
    print("""
CLI AI Coding Agents Toolkit
============================

A comprehensive toolkit for working with command-line AI coding agents.

Usage:
    python deliverable_cli_agent_toolkit.py <command>

Commands:
    demo1    Single-agent task execution
    demo2    Multi-agent pipeline orchestration
    demo3    Automated code review workflow
    demo4    Usage metrics and reporting
    help     Show this help message

Examples:
    python deliverable_cli_agent_toolkit.py demo1
    python deliverable_cli_agent_toolkit.py demo2

Supported Agents:
    • Claude Code - Anthropic's official CLI
    • Aider - Git-native AI pair programming
    • Goose - Block's extensible agent
    • GitHub Copilot CLI - Command suggestions

Configuration:
    Agents are auto-detected based on:
    1. Command availability in PATH
    2. Required environment variables

Data Storage:
    Metrics and results saved to .cli_agent_toolkit/

Environment Variables:
    ANTHROPIC_API_KEY - For Claude Code
    OPENAI_API_KEY - For Aider/Goose (depending on config)
    GITHUB_TOKEN - For GitHub Copilot CLI
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
        "demo1": demo_1_single_agent,
        "demo2": demo_2_multi_agent_pipeline,
        "demo3": demo_3_code_review,
        "demo4": demo_4_metrics,
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
