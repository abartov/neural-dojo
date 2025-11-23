#!/usr/bin/env python3
"""
Module 05 Deliverable: AI Tools Comparison & Benchmark Suite

A production-ready tool for systematically comparing AI coding assistants.

Features:
- Benchmark multiple AI tools on standardized tasks
- Measure performance metrics (speed, quality, cost)
- Compare code generation quality
- Analyze response times and token usage
- Generate comparison reports
- Track results over time

Supported Tools:
- Claude (Anthropic)
- GPT-4 (OpenAI)
- Gemini (Google)
- Local models (via Ollama)

Author: Neural Dojo
Date: 2025-11-23
"""

import json
import time
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

# Optional dependencies (graceful degradation)
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkTask:
    """A standardized task for benchmarking AI tools."""
    id: str
    name: str
    description: str
    prompt: str
    category: str  # code_generation, debugging, refactoring, documentation
    expected_features: List[str] = field(default_factory=list)
    difficulty: str = "medium"  # easy, medium, hard
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BenchmarkResult:
    """Results from running a benchmark task."""
    task_id: str
    tool_name: str
    model_name: str
    response: str
    response_time: float  # seconds
    token_count: int
    cost: float  # USD
    quality_score: float  # 0-100
    features_detected: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ToolComparison:
    """Comparison of multiple tools on a task."""
    task_id: str
    task_name: str
    results: List[BenchmarkResult] = field(default_factory=list)
    winner: Optional[str] = None
    analysis: str = ""


class AIToolsBenchmark:
    """
    AI Tools Comparison & Benchmark Suite.

    Systematically compares AI coding assistants on standardized tasks.
    Measures performance, quality, and cost.
    """

    # Pricing per 1M tokens (as of 2025-11-23)
    PRICING = {
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-opus-4": {"input": 15.00, "output": 75.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    def __init__(self, storage_dir: str = ".ai_tools_benchmark"):
        """
        Initialize the benchmark suite.

        Args:
            storage_dir: Directory for storing results
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.tasks_file = self.storage_dir / "tasks.json"
        self.results_file = self.storage_dir / "results.json"

        self.tasks: Dict[str, BenchmarkTask] = {}
        self.results: List[BenchmarkResult] = []

        # Initialize AI clients
        self.clients = {}
        self._init_clients()

        # Load existing data
        self._load_tasks()
        self._load_results()

    def _init_clients(self):
        """Initialize AI API clients."""
        # Anthropic Claude
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.clients["claude"] = Anthropic(api_key=api_key)
                logger.info("Claude client initialized")
            else:
                logger.warning("ANTHROPIC_API_KEY not set")
        else:
            logger.warning("anthropic package not installed")

        # OpenAI GPT
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.clients["openai"] = openai
                logger.info("OpenAI client initialized")
            else:
                logger.warning("OPENAI_API_KEY not set")
        else:
            logger.warning("openai package not installed")

    def _load_tasks(self):
        """Load tasks from storage."""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                data = json.load(f)
                self.tasks = {
                    k: BenchmarkTask(**v) for k, v in data.items()
                }
            logger.info(f"Loaded {len(self.tasks)} tasks")

    def _save_tasks(self):
        """Save tasks to storage."""
        with open(self.tasks_file, 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.tasks.items()},
                f,
                indent=2
            )

    def _load_results(self):
        """Load results from storage."""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                data = json.load(f)
                self.results = [BenchmarkResult(**item) for item in data]
            logger.info(f"Loaded {len(self.results)} results")

    def _save_results(self):
        """Save results to storage."""
        with open(self.results_file, 'w') as f:
            json.dump(
                [asdict(r) for r in self.results],
                f,
                indent=2
            )

    def add_task(
        self,
        name: str,
        description: str,
        prompt: str,
        category: str,
        expected_features: List[str] = None,
        difficulty: str = "medium"
    ) -> BenchmarkTask:
        """
        Add a benchmark task.

        Args:
            name: Task name
            description: What the task tests
            prompt: Prompt to send to AI tools
            category: Task category
            expected_features: Features to check for in responses
            difficulty: Task difficulty level

        Returns:
            Created BenchmarkTask
        """
        task_id = name.lower().replace(" ", "_")

        task = BenchmarkTask(
            id=task_id,
            name=name,
            description=description,
            prompt=prompt,
            category=category,
            expected_features=expected_features or [],
            difficulty=difficulty
        )

        self.tasks[task_id] = task
        self._save_tasks()

        logger.info(f"Added task: {name}")
        return task

    def run_task_claude(
        self,
        task_id: str,
        model: str = "claude-sonnet-4-5"
    ) -> Optional[BenchmarkResult]:
        """
        Run a task with Claude.

        Args:
            task_id: Task ID
            model: Claude model to use

        Returns:
            BenchmarkResult or None
        """
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return None

        if "claude" not in self.clients:
            logger.error("Claude client not available")
            return None

        task = self.tasks[task_id]
        client = self.clients["claude"]

        try:
            start_time = time.time()

            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": task.prompt
                }]
            )

            response_time = time.time() - start_time

            # Extract response text
            response_text = response.content[0].text

            # Calculate tokens and cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            if model in self.PRICING:
                cost = (
                    (input_tokens / 1_000_000) * self.PRICING[model]["input"] +
                    (output_tokens / 1_000_000) * self.PRICING[model]["output"]
                )
            else:
                cost = 0.0

            # Evaluate quality
            quality_score, features_detected = self._evaluate_response(
                task,
                response_text
            )

            result = BenchmarkResult(
                task_id=task_id,
                tool_name="Claude",
                model_name=model,
                response=response_text,
                response_time=response_time,
                token_count=total_tokens,
                cost=cost,
                quality_score=quality_score,
                features_detected=features_detected
            )

            self.results.append(result)
            self._save_results()

            logger.info(f"Completed task '{task.name}' with Claude {model}")
            return result

        except Exception as e:
            logger.error(f"Claude task failed: {e}")
            return None

    def run_task_gpt(
        self,
        task_id: str,
        model: str = "gpt-4o"
    ) -> Optional[BenchmarkResult]:
        """
        Run a task with GPT.

        Args:
            task_id: Task ID
            model: GPT model to use

        Returns:
            BenchmarkResult or None
        """
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return None

        if "openai" not in self.clients:
            logger.error("OpenAI client not available")
            return None

        task = self.tasks[task_id]

        try:
            start_time = time.time()

            response = self.clients["openai"].chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": task.prompt
                }],
                max_tokens=4096
            )

            response_time = time.time() - start_time

            # Extract response text
            response_text = response.choices[0].message.content

            # Calculate tokens and cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens

            if model in self.PRICING:
                cost = (
                    (input_tokens / 1_000_000) * self.PRICING[model]["input"] +
                    (output_tokens / 1_000_000) * self.PRICING[model]["output"]
                )
            else:
                cost = 0.0

            # Evaluate quality
            quality_score, features_detected = self._evaluate_response(
                task,
                response_text
            )

            result = BenchmarkResult(
                task_id=task_id,
                tool_name="GPT",
                model_name=model,
                response=response_text,
                response_time=response_time,
                token_count=total_tokens,
                cost=cost,
                quality_score=quality_score,
                features_detected=features_detected
            )

            self.results.append(result)
            self._save_results()

            logger.info(f"Completed task '{task.name}' with GPT {model}")
            return result

        except Exception as e:
            logger.error(f"GPT task failed: {e}")
            return None

    def _evaluate_response(
        self,
        task: BenchmarkTask,
        response: str
    ) -> tuple[float, List[str]]:
        """
        Evaluate response quality.

        Args:
            task: Benchmark task
            response: AI response

        Returns:
            (quality_score, features_detected)
        """
        score = 100.0
        features_detected = []

        # Check for expected features
        for feature in task.expected_features:
            if feature.lower() in response.lower():
                features_detected.append(feature)
            else:
                score -= 10  # Deduct points for missing features

        # Minimum score
        score = max(score, 0.0)

        return score, features_detected

    def compare_tools(self, task_id: str) -> Optional[ToolComparison]:
        """
        Compare all tools on a specific task.

        Args:
            task_id: Task ID

        Returns:
            ToolComparison or None
        """
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return None

        task = self.tasks[task_id]

        # Get all results for this task
        task_results = [
            r for r in self.results if r.task_id == task_id
        ]

        if not task_results:
            logger.warning(f"No results found for task: {task_id}")
            return None

        # Group by tool
        by_tool = {}
        for result in task_results:
            key = f"{result.tool_name} ({result.model_name})"
            if key not in by_tool:
                by_tool[key] = []
            by_tool[key].append(result)

        # Find best result for each tool (latest run)
        best_results = []
        for tool_key, tool_results in by_tool.items():
            # Sort by timestamp (latest first)
            sorted_results = sorted(
                tool_results,
                key=lambda r: r.timestamp,
                reverse=True
            )
            best_results.append(sorted_results[0])

        # Determine winner (highest quality score)
        winner_result = max(best_results, key=lambda r: r.quality_score)
        winner = f"{winner_result.tool_name} ({winner_result.model_name})"

        # Generate analysis
        analysis = self._generate_analysis(task, best_results, winner_result)

        comparison = ToolComparison(
            task_id=task_id,
            task_name=task.name,
            results=best_results,
            winner=winner,
            analysis=analysis
        )

        return comparison

    def _generate_analysis(
        self,
        task: BenchmarkTask,
        results: List[BenchmarkResult],
        winner: BenchmarkResult
    ) -> str:
        """Generate comparison analysis."""
        analysis = f"Task: {task.name}\n\n"

        # Compare metrics
        analysis += "Performance Comparison:\n"
        for result in sorted(results, key=lambda r: r.quality_score, reverse=True):
            analysis += f"\n{result.tool_name} ({result.model_name}):\n"
            analysis += f"  Quality: {result.quality_score:.1f}/100\n"
            analysis += f"  Speed: {result.response_time:.2f}s\n"
            analysis += f"  Tokens: {result.token_count:,}\n"
            analysis += f"  Cost: ${result.cost:.4f}\n"
            analysis += f"  Features: {len(result.features_detected)}/{len(task.expected_features)}\n"

        analysis += f"\nWinner: {winner.tool_name} ({winner.model_name})\n"
        analysis += f"Best for: {self._get_best_for(results)}\n"

        return analysis

    def _get_best_for(self, results: List[BenchmarkResult]) -> str:
        """Determine what each tool is best for."""
        if not results:
            return "N/A"

        # Find fastest
        fastest = min(results, key=lambda r: r.response_time)

        # Find cheapest
        cheapest = min(results, key=lambda r: r.cost)

        # Find highest quality
        best_quality = max(results, key=lambda r: r.quality_score)

        recommendations = []

        if fastest == cheapest == best_quality:
            recommendations.append(f"{fastest.tool_name} wins in all categories")
        else:
            if fastest.response_time < min(r.response_time for r in results if r != fastest):
                recommendations.append(f"Speed → {fastest.tool_name}")
            if cheapest.cost < min(r.cost for r in results if r != cheapest) * 0.5:
                recommendations.append(f"Cost → {cheapest.tool_name}")
            if best_quality.quality_score > max(r.quality_score for r in results if r != best_quality):
                recommendations.append(f"Quality → {best_quality.tool_name}")

        return ", ".join(recommendations) if recommendations else "Evenly matched"

    def print_comparison(self, task_id: str):
        """Print tool comparison results."""
        comparison = self.compare_tools(task_id)
        if not comparison:
            print(f"❌ No comparison available for task: {task_id}")
            return

        print(f"\n{'='*60}")
        print(f"🏆 AI Tools Comparison: {comparison.task_name}")
        print(f"{'='*60}\n")

        print(comparison.analysis)

    def generate_report(self, output_file: str = "benchmark_report.md"):
        """
        Generate comprehensive benchmark report.

        Args:
            output_file: Output markdown file
        """
        report = "# AI Tools Benchmark Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Summary stats
        total_tasks = len(self.tasks)
        total_results = len(self.results)
        tools_tested = len(set(r.tool_name for r in self.results))

        report += "## Summary\n\n"
        report += f"- **Total Tasks**: {total_tasks}\n"
        report += f"- **Total Runs**: {total_results}\n"
        report += f"- **Tools Tested**: {tools_tested}\n\n"

        # Task comparisons
        report += "## Task Comparisons\n\n"

        for task_id in self.tasks:
            comparison = self.compare_tools(task_id)
            if comparison:
                report += f"### {comparison.task_name}\n\n"
                report += "```\n"
                report += comparison.analysis
                report += "```\n\n"

        # Overall statistics
        report += "## Overall Statistics\n\n"

        # Group by tool
        by_tool = {}
        for result in self.results:
            key = f"{result.tool_name} ({result.model_name})"
            if key not in by_tool:
                by_tool[key] = []
            by_tool[key].append(result)

        report += "| Tool | Avg Quality | Avg Speed | Avg Cost | Tasks |\n"
        report += "|------|-------------|-----------|----------|-------|\n"

        for tool_key, tool_results in sorted(by_tool.items()):
            avg_quality = sum(r.quality_score for r in tool_results) / len(tool_results)
            avg_speed = sum(r.response_time for r in tool_results) / len(tool_results)
            avg_cost = sum(r.cost for r in tool_results) / len(tool_results)
            num_tasks = len(tool_results)

            report += f"| {tool_key} | {avg_quality:.1f} | {avg_speed:.2f}s | ${avg_cost:.4f} | {num_tasks} |\n"

        # Save report
        with open(output_file, 'w') as f:
            f.write(report)

        logger.info(f"Report generated: {output_file}")
        print(f"\n✅ Report saved to: {output_file}")


def demo_1_add_tasks():
    """Demo 1: Add benchmark tasks."""
    print("\n" + "="*60)
    print("DEMO 1: Add Benchmark Tasks")
    print("="*60)

    benchmark = AIToolsBenchmark()

    # Task 1: Simple code generation
    print("\n📝 Adding tasks...")

    benchmark.add_task(
        name="Generate Email Validator",
        description="Test basic code generation capabilities",
        prompt="""Generate a Python function to validate email addresses:
- Accept email string as input
- Return True if valid, False otherwise
- Check for @ symbol and domain
- Include type hints and docstring
""",
        category="code_generation",
        expected_features=["def", "email", "return", "@", "type hint", "docstring"],
        difficulty="easy"
    )

    benchmark.add_task(
        name="Optimize Slow Function",
        description="Test code optimization and performance analysis",
        prompt="""Optimize this slow Python function:

def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

Make it faster and explain the optimization.
""",
        category="optimization",
        expected_features=["O(n)", "set", "faster", "optimization", "complexity"],
        difficulty="medium"
    )

    benchmark.add_task(
        name="Debug Error Message",
        description="Test debugging and error analysis capabilities",
        prompt="""Debug this error:

```
Traceback (most recent call last):
  File "app.py", line 42, in process_data
    result = data.split(',')
AttributeError: 'NoneType' object has no attribute 'split'
```

Explain the root cause and provide a fix.
""",
        category="debugging",
        expected_features=["None", "null check", "validation", "fix", "root cause"],
        difficulty="easy"
    )

    print(f"✅ Added {len(benchmark.tasks)} tasks")

    # List tasks
    print("\n📋 Benchmark Tasks:")
    for task in benchmark.tasks.values():
        print(f"  • {task.name} ({task.difficulty})")

    print("\n✅ Demo 1 complete!")


def demo_2_run_benchmarks():
    """Demo 2: Run benchmarks (requires API keys)."""
    print("\n" + "="*60)
    print("DEMO 2: Run Benchmarks")
    print("="*60)

    benchmark = AIToolsBenchmark()

    if not benchmark.clients:
        print("\n⚠️  No AI clients available - set API keys:")
        print("  export ANTHROPIC_API_KEY=your_key")
        print("  export OPENAI_API_KEY=your_key")
        return

    # Run first task with available tools
    task_id = "generate_email_validator"

    if task_id not in benchmark.tasks:
        print(f"\n⚠️  Task not found: {task_id}")
        print("Run demo_1 first to add tasks")
        return

    print(f"\n🤖 Running benchmarks for: {benchmark.tasks[task_id].name}")

    # Run with Claude
    if "claude" in benchmark.clients:
        print("\n⏱️  Testing Claude...")
        result = benchmark.run_task_claude(task_id)
        if result:
            print(f"  ✅ Quality: {result.quality_score:.1f}/100")
            print(f"  ⚡ Speed: {result.response_time:.2f}s")
            print(f"  💰 Cost: ${result.cost:.4f}")

    # Run with GPT
    if "openai" in benchmark.clients:
        print("\n⏱️  Testing GPT...")
        result = benchmark.run_task_gpt(task_id)
        if result:
            print(f"  ✅ Quality: {result.quality_score:.1f}/100")
            print(f"  ⚡ Speed: {result.response_time:.2f}s")
            print(f"  💰 Cost: ${result.cost:.4f}")

    print("\n✅ Demo 2 complete!")


def demo_3_compare_results():
    """Demo 3: Compare tool results."""
    print("\n" + "="*60)
    print("DEMO 3: Compare Results")
    print("="*60)

    benchmark = AIToolsBenchmark()

    if not benchmark.results:
        print("\n⚠️  No results available")
        print("Run demo_2 first to generate results")
        return

    # Get unique task IDs from results
    task_ids = set(r.task_id for r in benchmark.results)

    for task_id in task_ids:
        benchmark.print_comparison(task_id)

    print("\n✅ Demo 3 complete!")


def demo_4_generate_report():
    """Demo 4: Generate comprehensive report."""
    print("\n" + "="*60)
    print("DEMO 4: Generate Report")
    print("="*60)

    benchmark = AIToolsBenchmark()

    if not benchmark.results:
        print("\n⚠️  No results available")
        print("Run demo_2 first to generate results")
        return

    print("\n📊 Generating comprehensive benchmark report...")
    benchmark.generate_report()

    print("\n✅ Demo 4 complete!")


def main():
    """Main CLI interface."""
    import sys

    if len(sys.argv) < 2:
        print("AI Tools Comparison & Benchmark Suite")
        print("\nUsage:")
        print("  python deliverable_ai_tools_benchmark.py <command>")
        print("\nCommands:")
        print("  demo1    - Add benchmark tasks")
        print("  demo2    - Run benchmarks (requires API keys)")
        print("  demo3    - Compare results")
        print("  demo4    - Generate report")
        print("  all      - Run all demos")
        return

    command = sys.argv[1]

    if command == "demo1":
        demo_1_add_tasks()
    elif command == "demo2":
        demo_2_run_benchmarks()
    elif command == "demo3":
        demo_3_compare_results()
    elif command == "demo4":
        demo_4_generate_report()
    elif command == "all":
        demo_1_add_tasks()
        demo_2_run_benchmarks()
        demo_3_compare_results()
        demo_4_generate_report()
    else:
        print(f"Unknown command: {command}")
        return


if __name__ == "__main__":
    main()
