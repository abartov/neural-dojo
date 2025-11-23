#!/usr/bin/env python3
"""
Module 08 Deliverable: Sampling Strategy Tuner

Tool for optimizing AI model sampling parameters.

Features:
- Test different temperature settings
- Experiment with top_p values
- Compare sampling strategies
- Find optimal parameters for tasks
- Generate tuning reports

Author: Neural Dojo
Date: 2025-11-23
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class SamplingConfig:
    """Sampling configuration."""
    temperature: float
    top_p: float
    top_k: Optional[int] = None
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"temp={self.temperature}_p={self.top_p}"


@dataclass
class SamplingResult:
    """Result from sampling experiment."""
    config: SamplingConfig
    prompt: str
    response: str
    diversity_score: float  # 0-100
    consistency_score: float  # 0-100 (when run multiple times)
    quality_score: float  # 0-100
    tokens: int


PRESETS = {
    "creative": SamplingConfig(temperature=0.9, top_p=0.95, name="Creative"),
    "balanced": SamplingConfig(temperature=0.7, top_p=0.9, name="Balanced"),
    "precise": SamplingConfig(temperature=0.3, top_p=0.85, name="Precise"),
    "deterministic": SamplingConfig(temperature=0.0, top_p=1.0, name="Deterministic"),
}


class SamplingTuner:
    """
    Sampling Strategy Tuner.

    Helps find optimal temperature and top_p settings for different tasks.
    """

    TASK_TYPES = {
        "creative_writing": {
            "name": "Creative Writing",
            "prompt": "Write a short story about a robot learning to paint.",
            "optimal_temp": 0.8,
            "optimal_top_p": 0.95
        },
        "code_generation": {
            "name": "Code Generation",
            "prompt": "Write a Python function to merge two sorted lists.",
            "optimal_temp": 0.2,
            "optimal_top_p": 0.85
        },
        "factual_qa": {
            "name": "Factual Q&A",
            "prompt": "What is the capital of France and its population?",
            "optimal_temp": 0.1,
            "optimal_top_p": 0.9
        },
        "brainstorming": {
            "name": "Brainstorming",
            "prompt": "List 10 innovative uses for blockchain in education.",
            "optimal_temp": 0.9,
            "optimal_top_p": 0.95
        },
        "translation": {
            "name": "Translation",
            "prompt": "Translate to Spanish: The quick brown fox jumps over the lazy dog.",
            "optimal_temp": 0.3,
            "optimal_top_p": 0.9
        }
    }

    def __init__(self, storage_dir: str = ".sampling_tuner"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.results_file = self.storage_dir / "results.json"
        self.results: List[SamplingResult] = []

        # Init client
        self.client = None
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        self._load_results()

    def _load_results(self):
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                data = json.load(f)
                self.results = [
                    SamplingResult(
                        config=SamplingConfig(**r['config']),
                        prompt=r['prompt'],
                        response=r['response'],
                        diversity_score=r['diversity_score'],
                        consistency_score=r['consistency_score'],
                        quality_score=r['quality_score'],
                        tokens=r['tokens']
                    )
                    for r in data
                ]

    def _save_results(self):
        with open(self.results_file, 'w') as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)

    def test_config(self, config: SamplingConfig, prompt: str, model: str = "claude-sonnet-4-5") -> Optional[SamplingResult]:
        """Test a sampling configuration."""
        if not self.client:
            print("⚠️  Claude client not available")
            return None

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=1024,
                temperature=config.temperature,
                top_p=config.top_p,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            tokens = response.usage.output_tokens

            # Calculate scores
            diversity_score = self._calculate_diversity(text)
            consistency_score = 50.0  # Would need multiple runs to measure
            quality_score = self._calculate_quality(text)

            result = SamplingResult(
                config=config,
                prompt=prompt,
                response=text,
                diversity_score=diversity_score,
                consistency_score=consistency_score,
                quality_score=quality_score,
                tokens=tokens
            )

            self.results.append(result)
            self._save_results()

            return result

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def _calculate_diversity(self, text: str) -> float:
        """Calculate text diversity score."""
        words = text.split()
        if len(words) == 0:
            return 0.0

        unique_words = len(set(words))
        diversity_ratio = unique_words / len(words)

        # Normalize to 0-100
        return min(diversity_ratio * 100, 100)

    def _calculate_quality(self, text: str) -> float:
        """Simple quality heuristic."""
        score = 50.0

        # Length check
        if 50 < len(text) < 2000:
            score += 20

        # Structure check
        if "." in text or "?" in text:
            score += 15

        # Completeness check
        if not text.endswith(("...", "incomplete")):
            score += 15

        return min(score, 100)

    def compare_presets(self, task_key: str) -> Dict[str, SamplingResult]:
        """Compare all preset configurations on a task."""
        if task_key not in self.TASK_TYPES:
            print(f"❌ Unknown task: {task_key}")
            return {}

        task = self.TASK_TYPES[task_key]
        print(f"\n🧪 Testing presets on: {task['name']}")

        results = {}
        for preset_name, config in PRESETS.items():
            print(f"  Testing {config.name}...")
            result = self.test_config(config, task["prompt"])
            if result:
                results[preset_name] = result

        return results

    def find_optimal(self, task_key: str, num_samples: int = 4) -> SamplingConfig:
        """Find optimal sampling config for a task through grid search."""
        if task_key not in self.TASK_TYPES:
            print(f"❌ Unknown task: {task_key}")
            return PRESETS["balanced"]

        task = self.TASK_TYPES[task_key]
        print(f"\n🔍 Finding optimal config for: {task['name']}")

        # Grid search
        temps = [0.0, 0.3, 0.7, 0.9]
        top_ps = [0.85, 0.9, 0.95]

        best_config = None
        best_score = 0.0

        tested = 0
        for temp in temps[:num_samples//len(top_ps)]:
            for top_p in top_ps[:2]:  # Limit combinations
                if tested >= num_samples:
                    break

                config = SamplingConfig(temperature=temp, top_p=top_p)
                print(f"  Testing temp={temp}, top_p={top_p}...")

                result = self.test_config(config, task["prompt"])
                if result:
                    # Combined score
                    score = (result.diversity_score + result.quality_score) / 2

                    if score > best_score:
                        best_score = score
                        best_config = config

                tested += 1

        if best_config:
            print(f"\n✅ Best config: temp={best_config.temperature}, top_p={best_config.top_p}")
            print(f"   Score: {best_score:.1f}/100")

        return best_config or PRESETS["balanced"]

    def generate_report(self) -> str:
        """Generate tuning report."""
        if not self.results:
            return "No results available."

        report = "# Sampling Strategy Tuning Report\n\n"

        # Group by prompt
        by_prompt = {}
        for r in self.results:
            if r.prompt not in by_prompt:
                by_prompt[r.prompt] = []
            by_prompt[r.prompt].append(r)

        for prompt, results in by_prompt.items():
            report += f"## Prompt: {prompt[:60]}...\n\n"
            report += "| Config | Diversity | Quality | Tokens |\n"
            report += "|--------|-----------|---------|--------|\n"

            for r in sorted(results, key=lambda x: x.quality_score, reverse=True):
                report += f"| {r.config.name:20} | {r.diversity_score:5.1f} | {r.quality_score:5.1f} | {r.tokens:6} |\n"

            report += "\n"

        return report


def demo_1_list_presets():
    """Demo 1: List preset configurations."""
    print("\n" + "="*60)
    print("DEMO 1: Preset Configurations")
    print("="*60)

    print("\n📋 Available Presets:\n")
    for name, config in PRESETS.items():
        print(f"  {config.name}")
        print(f"    Temperature: {config.temperature}")
        print(f"    Top-P: {config.top_p}")
        print()

    print("📋 Task Types:\n")
    tuner = SamplingTuner()
    for key, task in tuner.TASK_TYPES.items():
        print(f"  {task['name']}")
        print(f"    Optimal Temp: {task['optimal_temp']}")
        print(f"    Optimal Top-P: {task['optimal_top_p']}")
        print()

    print("✅ Demo 1 complete!")


def demo_2_test_preset():
    """Demo 2: Test a preset configuration."""
    print("\n" + "="*60)
    print("DEMO 2: Test Preset")
    print("="*60)

    tuner = SamplingTuner()

    if not tuner.client:
        print("\n⚠️  Claude client not available")
        print("Set ANTHROPIC_API_KEY to test sampling")
        return

    # Test creative preset on creative task
    config = PRESETS["creative"]
    task = tuner.TASK_TYPES["creative_writing"]

    print(f"\n🧪 Testing: {config.name}")
    print(f"Task: {task['name']}")

    result = tuner.test_config(config, task["prompt"])

    if result:
        print(f"\n✅ Results:")
        print(f"  Diversity: {result.diversity_score:.1f}/100")
        print(f"  Quality: {result.quality_score:.1f}/100")
        print(f"  Tokens: {result.tokens}")
        print(f"\n  Response preview:")
        print(f"  {result.response[:200]}...")

    print("\n✅ Demo 2 complete!")


def demo_3_compare_presets():
    """Demo 3: Compare all presets on a task."""
    print("\n" + "="*60)
    print("DEMO 3: Compare Presets")
    print("="*60)

    tuner = SamplingTuner()

    if not tuner.client:
        print("\n⚠️  Claude client not available")
        return

    results = tuner.compare_presets("code_generation")

    if results:
        print("\n📊 Comparison Results:\n")
        print("| Preset | Diversity | Quality | Tokens |")
        print("|--------|-----------|---------|--------|")

        for name, result in results.items():
            print(f"| {name:15} | {result.diversity_score:9.1f} | {result.quality_score:7.1f} | {result.tokens:6} |")

    print("\n✅ Demo 3 complete!")


def main():
    import sys
    if len(sys.argv) < 2:
        print("Sampling Strategy Tuner")
        print("\nCommands:")
        print("  demo1  - List presets and tasks")
        print("  demo2  - Test a preset")
        print("  demo3  - Compare presets")
        return

    cmd = sys.argv[1]
    if cmd == "demo1":
        demo_1_list_presets()
    elif cmd == "demo2":
        demo_2_test_preset()
    elif cmd == "demo3":
        demo_3_compare_presets()


if __name__ == "__main__":
    main()
