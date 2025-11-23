#!/usr/bin/env python3
"""
Module 06 Deliverable: Model Comparison Benchmark Suite

Deep benchmarking tool for comparing LLM models on various dimensions.

Features:
- Test multiple models from same/different providers
- Comprehensive quality scoring
- Task-specific performance analysis
- Cost/speed/quality tradeoff visualization
- Model recommendation engine

Author: Neural Dojo
Date: 2025-11-23
"""

import json
import time
import statistics
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

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


@dataclass
class ModelConfig:
    """Model configuration."""
    provider: str  # anthropic, openai
    name: str  # claude-sonnet-4-5, gpt-4o
    display_name: str
    cost_per_1m_input: float
    cost_per_1m_output: float
    max_tokens: int


@dataclass
class BenchmarkResult:
    """Single benchmark result."""
    model: str
    task: str
    response: str
    latency: float
    tokens_in: int
    tokens_out: int
    cost: float
    quality_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ModelBenchmark:
    """Model comparison benchmark suite."""

    MODELS = {
        "claude-sonnet-4-5": ModelConfig(
            provider="anthropic",
            name="claude-sonnet-4-5",
            display_name="Claude Sonnet 4.5",
            cost_per_1m_input=3.00,
            cost_per_1m_output=15.00,
            max_tokens=8192
        ),
        "claude-opus-4": ModelConfig(
            provider="anthropic",
            name="claude-opus-4",
            display_name="Claude Opus 4",
            cost_per_1m_input=15.00,
            cost_per_1m_output=75.00,
            max_tokens=8192
        ),
        "gpt-4o": ModelConfig(
            provider="openai",
            name="gpt-4o",
            display_name="GPT-4o",
            cost_per_1m_input=5.00,
            cost_per_1m_output=15.00,
            max_tokens=4096
        ),
        "gpt-3.5-turbo": ModelConfig(
            provider="openai",
            name="gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo",
            cost_per_1m_input=0.50,
            cost_per_1m_output=1.50,
            max_tokens=4096
        ),
    }

    TASKS = {
        "simple_function": {
            "name": "Simple Function",
            "prompt": "Write a Python function to calculate factorial of a number. Include type hints and docstring.",
            "expected_keywords": ["def", "factorial", "int", "return", "docstring"]
        },
        "complex_algorithm": {
            "name": "Complex Algorithm",
            "prompt": "Implement a LRU cache in Python with O(1) get and put operations. Use OrderedDict or implement from scratch.",
            "expected_keywords": ["class", "LRU", "OrderedDict", "O(1)", "__init__", "get", "put"]
        },
        "code_explanation": {
            "name": "Code Explanation",
            "prompt": "Explain how binary search works and why it's O(log n). Include pseudocode.",
            "expected_keywords": ["binary search", "O(log n)", "divide", "logarithmic", "pseudocode"]
        },
        "debugging": {
            "name": "Debugging",
            "prompt": "Find and fix the bug in this code:\n\ndef avg(nums):\n    return sum(nums) / len(nums)\n\nresult = avg([])",
            "expected_keywords": ["empty", "zero", "check", "if", "exception", "validation"]
        },
        "optimization": {
            "name": "Code Optimization",
            "prompt": "Optimize this O(n²) code to O(n):\n\ndef has_duplicates(arr):\n    for i in range(len(arr)):\n        for j in range(i+1, len(arr)):\n            if arr[i] == arr[j]:\n                return True\n    return False",
            "expected_keywords": ["set", "O(n)", "hash", "seen", "linear"]
        }
    }

    def __init__(self, storage_dir: str = ".model_benchmark"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.results_file = self.storage_dir / "results.json"
        self.results: List[BenchmarkResult] = []

        # Init clients
        import os
        self.anthropic_client = None
        self.openai_client = None

        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = openai

        self._load_results()

    def _load_results(self):
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                data = json.load(f)
                self.results = [BenchmarkResult(**r) for r in data]

    def _save_results(self):
        with open(self.results_file, 'w') as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)

    def _calculate_quality(self, response: str, expected_keywords: List[str]) -> float:
        """Simple keyword-based quality scoring."""
        score = 0.0
        response_lower = response.lower()
        for keyword in expected_keywords:
            if keyword.lower() in response_lower:
                score += 100.0 / len(expected_keywords)
        return min(score, 100.0)

    def benchmark_model(self, model_key: str, task_key: str) -> Optional[BenchmarkResult]:
        """Run single model on single task."""
        if model_key not in self.MODELS:
            print(f"❌ Unknown model: {model_key}")
            return None

        if task_key not in self.TASKS:
            print(f"❌ Unknown task: {task_key}")
            return None

        model_config = self.MODELS[model_key]
        task = self.TASKS[task_key]

        # Route to correct provider
        if model_config.provider == "anthropic":
            if not self.anthropic_client:
                print(f"⚠️  Anthropic client not available")
                return None
            return self._benchmark_anthropic(model_config, task_key, task)
        elif model_config.provider == "openai":
            if not self.openai_client:
                print(f"⚠️  OpenAI client not available")
                return None
            return self._benchmark_openai(model_config, task_key, task)

        return None

    def _benchmark_anthropic(self, model: ModelConfig, task_key: str, task: Dict) -> BenchmarkResult:
        """Benchmark Anthropic model."""
        start = time.time()
        response = self.anthropic_client.messages.create(
            model=model.name,
            max_tokens=model.max_tokens,
            messages=[{"role": "user", "content": task["prompt"]}]
        )
        latency = time.time() - start

        text = response.content[0].text
        tokens_in = response.usage.input_tokens
        tokens_out = response.usage.output_tokens
        cost = (tokens_in / 1_000_000) * model.cost_per_1m_input + (tokens_out / 1_000_000) * model.cost_per_1m_output
        quality = self._calculate_quality(text, task["expected_keywords"])

        result = BenchmarkResult(
            model=model.name,
            task=task_key,
            response=text,
            latency=latency,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            quality_score=quality
        )

        self.results.append(result)
        self._save_results()
        return result

    def _benchmark_openai(self, model: ModelConfig, task_key: str, task: Dict) -> BenchmarkResult:
        """Benchmark OpenAI model."""
        start = time.time()
        response = self.openai_client.chat.completions.create(
            model=model.name,
            max_tokens=model.max_tokens,
            messages=[{"role": "user", "content": task["prompt"]}]
        )
        latency = time.time() - start

        text = response.choices[0].message.content
        tokens_in = response.usage.prompt_tokens
        tokens_out = response.usage.completion_tokens
        cost = (tokens_in / 1_000_000) * model.cost_per_1m_input + (tokens_out / 1_000_000) * model.cost_per_1m_output
        quality = self._calculate_quality(text, task["expected_keywords"])

        result = BenchmarkResult(
            model=model.name,
            task=task_key,
            response=text,
            latency=latency,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            quality_score=quality
        )

        self.results.append(result)
        self._save_results()
        return result

    def benchmark_all(self, models: List[str] = None):
        """Benchmark all models on all tasks."""
        if models is None:
            models = list(self.MODELS.keys())

        print(f"\n🚀 Benchmarking {len(models)} models on {len(self.TASKS)} tasks...")

        for model_key in models:
            for task_key in self.TASKS:
                print(f"\n⏱️  {self.MODELS[model_key].display_name} → {self.TASKS[task_key]['name']}")
                result = self.benchmark_model(model_key, task_key)
                if result:
                    print(f"  Quality: {result.quality_score:.1f}/100 | Latency: {result.latency:.2f}s | Cost: ${result.cost:.4f}")

    def generate_report(self) -> str:
        """Generate comparison report."""
        if not self.results:
            return "No results available."

        report = "# Model Comparison Report\n\n"

        # Group by task
        by_task = {}
        for r in self.results:
            if r.task not in by_task:
                by_task[r.task] = []
            by_task[r.task].append(r)

        for task_key, task_results in by_task.items():
            task_name = self.TASKS[task_key]["name"]
            report += f"## {task_name}\n\n"
            report += "| Model | Quality | Latency | Cost | Tokens |\n"
            report += "|-------|---------|---------|------|--------|\n"

            for r in sorted(task_results, key=lambda x: x.quality_score, reverse=True):
                model_name = self.MODELS[r.model].display_name
                report += f"| {model_name} | {r.quality_score:.1f}/100 | {r.latency:.2f}s | ${r.cost:.4f} | {r.tokens_in + r.tokens_out} |\n"

            # Winner
            winner = max(task_results, key=lambda x: x.quality_score)
            report += f"\n**Winner**: {self.MODELS[winner.model].display_name}\n\n"

        # Overall stats
        report += "## Overall Summary\n\n"
        by_model = {}
        for r in self.results:
            if r.model not in by_model:
                by_model[r.model] = []
            by_model[r.model].append(r)

        report += "| Model | Avg Quality | Avg Latency | Avg Cost |\n"
        report += "|-------|-------------|-------------|----------|\n"

        for model_key, model_results in by_model.items():
            avg_quality = statistics.mean(r.quality_score for r in model_results)
            avg_latency = statistics.mean(r.latency for r in model_results)
            avg_cost = statistics.mean(r.cost for r in model_results)
            model_name = self.MODELS[model_key].display_name
            report += f"| {model_name} | {avg_quality:.1f}/100 | {avg_latency:.2f}s | ${avg_cost:.4f} |\n"

        return report


def demo_1_list_models():
    """Demo 1: List available models."""
    print("\n" + "="*60)
    print("DEMO 1: Available Models")
    print("="*60)

    benchmark = ModelBenchmark()

    print("\n📋 Models:")
    for key, model in benchmark.MODELS.items():
        print(f"\n  {model.display_name} ({key})")
        print(f"    Provider: {model.provider}")
        print(f"    Cost: ${model.cost_per_1m_input}/M in, ${model.cost_per_1m_output}/M out")
        print(f"    Max Tokens: {model.max_tokens:,}")

    print(f"\n📋 Tasks: {len(benchmark.TASKS)}")
    for key, task in benchmark.TASKS.items():
        print(f"  • {task['name']}")

    print("\n✅ Demo 1 complete!")


def demo_2_single_benchmark():
    """Demo 2: Single model benchmark."""
    print("\n" + "="*60)
    print("DEMO 2: Single Model Benchmark")
    print("="*60)

    benchmark = ModelBenchmark()

    if not (benchmark.anthropic_client or benchmark.openai_client):
        print("\n⚠️  No API clients available")
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
        return

    # Benchmark one model on one task
    model_key = "claude-sonnet-4-5" if benchmark.anthropic_client else "gpt-4o"
    task_key = "simple_function"

    print(f"\n🧪 Testing {benchmark.MODELS[model_key].display_name}...")
    print(f"Task: {benchmark.TASKS[task_key]['name']}\n")

    result = benchmark.benchmark_model(model_key, task_key)

    if result:
        print(f"\n✅ Results:")
        print(f"  Quality: {result.quality_score:.1f}/100")
        print(f"  Latency: {result.latency:.2f}s")
        print(f"  Cost: ${result.cost:.4f}")
        print(f"  Tokens: {result.tokens_in + result.tokens_out:,}")

    print("\n✅ Demo 2 complete!")


def demo_3_generate_report():
    """Demo 3: Generate comparison report."""
    print("\n" + "="*60)
    print("DEMO 3: Generate Report")
    print("="*60)

    benchmark = ModelBenchmark()

    if not benchmark.results:
        print("\n⚠️  No results available")
        print("Run demo_2 first")
        return

    print("\n📊 Generating report...")
    report = benchmark.generate_report()

    print("\n" + report)

    # Save to file
    with open("model_comparison_report.md", 'w') as f:
        f.write(report)

    print("\n✅ Report saved to: model_comparison_report.md")
    print("✅ Demo 3 complete!")


def main():
    import sys
    if len(sys.argv) < 2:
        print("Model Comparison Benchmark Suite")
        print("\nCommands:")
        print("  demo1  - List models and tasks")
        print("  demo2  - Run single benchmark")
        print("  demo3  - Generate report")
        return

    cmd = sys.argv[1]
    if cmd == "demo1":
        demo_1_list_models()
    elif cmd == "demo2":
        demo_2_single_benchmark()
    elif cmd == "demo3":
        demo_3_generate_report()


if __name__ == "__main__":
    main()
