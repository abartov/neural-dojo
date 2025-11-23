#!/usr/bin/env python3
"""
Module 07 Deliverable: Token Optimization Analyzer

Tool for analyzing and optimizing token usage in AI applications.

Features:
- Analyze prompt token counts
- Identify optimization opportunities
- Compare tokenization across models
- Generate cost savings reports
- Provide optimization recommendations

Author: Neural Dojo
Date: 2025-11-23
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


@dataclass
class TokenAnalysis:
    """Token usage analysis result."""
    text: str
    model: str
    token_count: int
    char_count: int
    word_count: int
    tokens_per_word: float
    estimated_cost_input: float
    estimated_cost_output: float
    optimization_score: float  # 0-100, higher is better
    recommendations: List[str] = field(default_factory=list)


@dataclass
class OptimizationResult:
    """Result of optimization attempt."""
    original_text: str
    optimized_text: str
    original_tokens: int
    optimized_tokens: int
    tokens_saved: int
    percent_saved: float
    cost_saved_per_1k_calls: float
    techniques_used: List[str] = field(default_factory=list)


class TokenOptimizer:
    """
    Token Optimization Analyzer.

    Analyzes token usage and suggests optimizations to reduce costs.
    """

    # Pricing per 1M tokens
    PRICING = {
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-opus-4": {"input": 15.00, "output": 75.00},
    }

    # Encoding mapping
    ENCODINGS = {
        "gpt-4": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "claude-sonnet-4-5": "cl100k_base",  # Approximation
        "claude-opus-4": "cl100k_base",  # Approximation
    }

    def __init__(self, storage_dir: str = ".token_optimizer"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        if not TIKTOKEN_AVAILABLE:
            print("⚠️  tiktoken not installed - using approximation")
            print("Install with: pip install tiktoken")

    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens for given text and model."""
        if TIKTOKEN_AVAILABLE and model in self.ENCODINGS:
            encoding = tiktoken.get_encoding(self.ENCODINGS[model])
            return len(encoding.encode(text))
        else:
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4

    def analyze_text(self, text: str, model: str = "gpt-4") -> TokenAnalysis:
        """Analyze token usage for text."""
        tokens = self.count_tokens(text, model)
        chars = len(text)
        words = len(text.split())
        tokens_per_word = tokens / words if words > 0 else 0

        # Calculate costs
        if model in self.PRICING:
            cost_input = (tokens / 1_000_000) * self.PRICING[model]["input"]
            cost_output = (tokens / 1_000_000) * self.PRICING[model]["output"]
        else:
            cost_input = 0.0
            cost_output = 0.0

        # Optimization score (lower tokens/word is better)
        # Typical: 1.3-1.5 tokens/word
        optimization_score = max(0, min(100, 100 - (tokens_per_word - 1.3) * 50))

        # Generate recommendations
        recommendations = self._generate_recommendations(text, tokens, words)

        return TokenAnalysis(
            text=text[:100] + "..." if len(text) > 100 else text,
            model=model,
            token_count=tokens,
            char_count=chars,
            word_count=words,
            tokens_per_word=tokens_per_word,
            estimated_cost_input=cost_input,
            estimated_cost_output=cost_output,
            optimization_score=optimization_score,
            recommendations=recommendations
        )

    def _generate_recommendations(self, text: str, tokens: int, words: int) -> List[str]:
        """Generate optimization recommendations."""
        recs = []

        # Check for common issues
        if words > 500:
            recs.append("Long prompt - consider breaking into smaller chunks")

        if "  " in text:
            recs.append("Multiple spaces detected - compress whitespace")

        if text.count("\n") > 20:
            recs.append("Many newlines - consider removing unnecessary line breaks")

        if any(filler in text.lower() for filler in ["please", "kindly", "could you", "i would like"]):
            recs.append("Polite phrases detected - AI doesn't need pleasantries")

        if text.count("example") > 3:
            recs.append("Many examples - consider reducing to most relevant ones")

        json_code_blocks = text.count("```json") + text.count("```python") + text.count("```")
        if json_code_blocks > 2:
            recs.append("Multiple code blocks - consider consolidating")

        return recs

    def optimize_text(self, text: str, model: str = "gpt-4") -> OptimizationResult:
        """Attempt to optimize text for token usage."""
        original_tokens = self.count_tokens(text, model)

        techniques = []
        optimized = text

        # Remove multiple spaces
        if "  " in optimized:
            optimized = " ".join(optimized.split())
            techniques.append("Compressed whitespace")

        # Remove polite phrases
        polite_phrases = [
            ("please ", ""),
            ("kindly ", ""),
            ("could you ", ""),
            ("i would like you to ", ""),
            ("would you mind ", ""),
        ]
        for phrase, replacement in polite_phrases:
            if phrase in optimized.lower():
                optimized = optimized.replace(phrase, replacement)
                if phrase not in techniques:
                    techniques.append("Removed polite phrases")

        # Compress excessive newlines
        while "\n\n\n" in optimized:
            optimized = optimized.replace("\n\n\n", "\n\n")
            if "Compressed newlines" not in techniques:
                techniques.append("Compressed newlines")

        optimized_tokens = self.count_tokens(optimized, model)
        tokens_saved = original_tokens - optimized_tokens
        percent_saved = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0

        # Calculate cost savings (assuming 1000 API calls)
        if model in self.PRICING:
            cost_per_call = (original_tokens / 1_000_000) * self.PRICING[model]["input"]
            saved_per_call = (tokens_saved / 1_000_000) * self.PRICING[model]["input"]
            cost_saved_1k = saved_per_call * 1000
        else:
            cost_saved_1k = 0.0

        return OptimizationResult(
            original_text=text,
            optimized_text=optimized,
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            tokens_saved=tokens_saved,
            percent_saved=percent_saved,
            cost_saved_per_1k_calls=cost_saved_1k,
            techniques_used=techniques
        )

    def compare_models(self, text: str) -> Dict[str, TokenAnalysis]:
        """Compare token counts across different models."""
        results = {}
        for model in self.PRICING.keys():
            results[model] = self.analyze_text(text, model)
        return results

    def generate_report(self, analysis: TokenAnalysis) -> str:
        """Generate optimization report."""
        report = f"""
# Token Optimization Report

## Text Analysis
- **Text**: {analysis.text}
- **Model**: {analysis.model}

## Token Metrics
- **Token Count**: {analysis.token_count:,}
- **Character Count**: {analysis.char_count:,}
- **Word Count**: {analysis.word_count:,}
- **Tokens per Word**: {analysis.tokens_per_word:.2f}

## Cost Estimates (per call)
- **Input Cost**: ${analysis.estimated_cost_input:.6f}
- **Output Cost**: ${analysis.estimated_cost_output:.6f}

## Optimization Score
**{analysis.optimization_score:.1f}/100** {"✅" if analysis.optimization_score >= 70 else "⚠️"}

## Recommendations
"""
        for i, rec in enumerate(analysis.recommendations, 1):
            report += f"{i}. {rec}\n"

        return report


def demo_1_analyze_prompt():
    """Demo 1: Analyze a prompt."""
    print("\n" + "="*60)
    print("DEMO 1: Token Analysis")
    print("="*60)

    optimizer = TokenOptimizer()

    # Sample prompt
    prompt = """
    Please could you kindly help me write a Python function that calculates
    the fibonacci sequence? I would like you to include type hints and a
    comprehensive docstring with examples. Thank you very much!

    Here are some examples of what I'm looking for:

    Example 1: fibonacci(5) should return [0, 1, 1, 2, 3]
    Example 2: fibonacci(10) should return [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    Example 3: fibonacci(0) should return []

    Please make sure to handle edge cases.
    """

    print("\n📊 Analyzing prompt...")
    analysis = optimizer.analyze_text(prompt, "gpt-4")

    print(f"\n✅ Results:")
    print(f"  Tokens: {analysis.token_count:,}")
    print(f"  Words: {analysis.word_count:,}")
    print(f"  Tokens/Word: {analysis.tokens_per_word:.2f}")
    print(f"  Optimization Score: {analysis.optimization_score:.1f}/100")
    print(f"  Estimated Cost (1K calls): ${analysis.estimated_cost_input * 1000:.2f}")

    if analysis.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in analysis.recommendations:
            print(f"  • {rec}")

    print("\n✅ Demo 1 complete!")


def demo_2_optimize_prompt():
    """Demo 2: Optimize a prompt."""
    print("\n" + "="*60)
    print("DEMO 2: Prompt Optimization")
    print("="*60)

    optimizer = TokenOptimizer()

    prompt = """
    Please could you kindly help me write a Python function that calculates
    the fibonacci sequence? I would like you to include type hints and a
    comprehensive docstring with examples. Thank you very much!

    Here are some examples of what I'm looking for:

    Example 1: fibonacci(5) should return [0, 1, 1, 2, 3]
    Example 2: fibonacci(10) should return [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    Please make sure to handle edge cases.
    """

    print("\n🔧 Optimizing prompt...")
    result = optimizer.optimize_text(prompt, "gpt-4")

    print(f"\n✅ Results:")
    print(f"  Original: {result.original_tokens} tokens")
    print(f"  Optimized: {result.optimized_tokens} tokens")
    print(f"  Saved: {result.tokens_saved} tokens ({result.percent_saved:.1f}%)")
    print(f"  Cost Savings (1K calls): ${result.cost_saved_per_1k_calls:.2f}")

    if result.techniques_used:
        print(f"\n🛠️  Techniques Applied:")
        for tech in result.techniques_used:
            print(f"  • {tech}")

    print(f"\n📝 Optimized Text:")
    print(f"  {result.optimized_text[:200]}...")

    print("\n✅ Demo 2 complete!")


def demo_3_compare_models():
    """Demo 3: Compare across models."""
    print("\n" + "="*60)
    print("DEMO 3: Model Comparison")
    print("="*60)

    optimizer = TokenOptimizer()

    prompt = "Write a Python function to reverse a string. Include type hints."

    print("\n📊 Comparing models...")
    results = optimizer.compare_models(prompt)

    print("\n| Model | Tokens | Cost (1K calls) |")
    print("|-------|--------|-----------------|")

    for model, analysis in results.items():
        cost_1k = analysis.estimated_cost_input * 1000
        print(f"| {model:20} | {analysis.token_count:6} | ${cost_1k:14.2f} |")

    print("\n✅ Demo 3 complete!")


def main():
    import sys
    if len(sys.argv) < 2:
        print("Token Optimization Analyzer")
        print("\nCommands:")
        print("  demo1  - Analyze prompt tokens")
        print("  demo2  - Optimize prompt")
        print("  demo3  - Compare models")
        return

    cmd = sys.argv[1]
    if cmd == "demo1":
        demo_1_analyze_prompt()
    elif cmd == "demo2":
        demo_2_optimize_prompt()
    elif cmd == "demo3":
        demo_3_compare_models()


if __name__ == "__main__":
    main()
