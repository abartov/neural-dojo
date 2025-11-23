#!/usr/bin/env python3
"""
Module 6: Prompt Testing Framework

A/B test the same prompt across different models to find the best one
for YOUR specific use case.

THEORY CONNECTION:
- Module 6 Section: "Choosing the Right Model" (line 484+)
- Key Concept: No "best" model - test with YOUR use case
- What you'll learn: How to systematically choose models

KEY INSIGHT: Benchmarks lie. Test with YOUR prompts on YOUR data!
"""

import os
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from anthropic import Anthropic
from dotenv import load_dotenv

# Try to import OpenAI (optional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

load_dotenv()


@dataclass
class TestResult:
    """Result from testing a prompt on a model."""
    model: str
    prompt: str
    response: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    quality_score: float = 0.0  # Manual scoring


class PromptTester:
    """Framework for A/B testing prompts across models."""

    PRICING = {
        # Anthropic (per 1M tokens)
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
        # OpenAI (per 1M tokens)
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }

    def __init__(self):
        """Initialize clients."""
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.openai_client = None

    def test_prompt(self, prompt: str, model: str) -> TestResult:
        """Test a prompt on a specific model."""
        start_time = time.time()

        if model.startswith("claude"):
            result = self._test_anthropic(prompt, model)
        elif model.startswith("gpt"):
            if not self.openai_client:
                raise ValueError("OpenAI API key not configured")
            result = self._test_openai(prompt, model)
        else:
            raise ValueError(f"Unknown model: {model}")

        result.latency_ms = int((time.time() - start_time) * 1000)
        return result

    def _test_anthropic(self, prompt: str, model: str) -> TestResult:
        """Test on Anthropic model."""
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        cost = self._calculate_cost(model, input_tokens, output_tokens)

        return TestResult(
            model=model,
            prompt=prompt,
            response=content,
            latency_ms=0,  # Will be set by caller
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )

    def _test_openai(self, prompt: str, model: str) -> TestResult:
        """Test on OpenAI model."""
        response = self.openai_client.chat.completions.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        cost = self._calculate_cost(model, input_tokens, output_tokens)

        return TestResult(
            model=model,
            prompt=prompt,
            response=content,
            latency_ms=0,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API call."""
        if model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def compare_models(self, prompt: str, models: List[str]) -> List[TestResult]:
        """Test the same prompt across multiple models."""
        results = []

        for model in models:
            print(f"Testing {model}...", end=" ")
            try:
                result = self.test_prompt(prompt, model)
                results.append(result)
                print(f"✓ ({result.latency_ms}ms)")
            except Exception as e:
                print(f"✗ Error: {e}")

        return results


def main():
    """Demonstrate prompt testing."""
    print("=" * 60)
    print("MODULE 6: PROMPT TESTING FRAMEWORK")
    print("=" * 60)

    tester = PromptTester()

    # Test Case 1: Code Generation
    print("\n📝 Test Case 1: Code Generation")
    print("-" * 60)

    code_prompt = """
Write a Python function to validate email addresses.
Include type hints and docstring.
Keep it under 20 lines.
"""

    models_to_test = [
        "claude-3-haiku-20240307",  # Cheap & fast
        "claude-sonnet-4-5-20250929",  # Balanced
    ]

    # Add GPT if available
    if tester.openai_client:
        models_to_test.append("gpt-3.5-turbo")

    print(f"Prompt: {code_prompt.strip()}")
    print(f"\nTesting {len(models_to_test)} models...")

    results1 = tester.compare_models(code_prompt, models_to_test)

    # Display results
    print("\n📊 Results:")
    for result in results1:
        print(f"\n{result.model}:")
        print(f"  Response: {result.response[:100]}...")
        print(f"  Latency: {result.latency_ms}ms")
        print(f"  Tokens: {result.input_tokens} in, {result.output_tokens} out")
        print(f"  Cost: ${result.cost_usd:.6f}")

    # Test Case 2: Creative Writing
    print("\n\n📝 Test Case 2: Creative Writing")
    print("-" * 60)

    creative_prompt = "Write a creative tagline for an AI coding assistant in 5 words."

    results2 = tester.compare_models(creative_prompt, models_to_test)

    print("\n📊 Results:")
    for result in results2:
        print(f"\n{result.model}: {result.response}")
        print(f"  Cost: ${result.cost_usd:.6f} | Latency: {result.latency_ms}ms")

    # Comparison Summary
    print("\n\n📊 COMPARISON SUMMARY:")
    print("=" * 60)

    print("\nModel Performance:")
    for result in results1:
        print(f"{result.model:30} {result.latency_ms:5}ms  ${result.cost_usd:.6f}")

    # Lessons learned
    print("\n\n💡 KEY INSIGHTS:")
    print("=" * 60)
    print("1. Different models excel at different tasks:")
    print("   - Code: Claude Sonnet, GPT-4")
    print("   - Creative: Claude Opus, GPT-4")
    print("   - Simple Q&A: Haiku, GPT-3.5")
    print("")
    print("2. Cost vs Quality trade-off:")
    print("   - 10x price difference between models")
    print("   - But quality improvement varies by task")
    print("   - Simple tasks: cheap models are fine")
    print("")
    print("3. Latency matters for UX:")
    print("   - Haiku: ~500-1000ms (feels instant)")
    print("   - Sonnet: ~2000-3000ms (acceptable)")
    print("   - Opus/GPT-4: ~5000-10000ms (noticeable lag)")
    print("")
    print("4. Test with YOUR data:")
    print("   - Benchmarks (MMLU, HumanEval) are generic")
    print("   - Your use case is unique")
    print("   - A/B test with real prompts")
    print("")
    print("5. Quality is subjective:")
    print("   - Rate responses yourself")
    print("   - Or ask users to rate")
    print("   - Automate with LLM-as-judge (Module 8!)")

    print("\n\n🎯 HOW TO USE THIS:")
    print("=" * 60)
    print("1. Collect representative prompts from your use case")
    print("2. Test 3-5 prompts on 3-4 models")
    print("3. Score quality manually (1-5 scale)")
    print("4. Calculate cost per 1K requests")
    print("5. Choose model based on quality/cost/latency needs")
    print("")
    print("Example Decision:")
    print("  - Use case: Customer support chatbot")
    print("  - Volume: 10K messages/day")
    print("  - Quality threshold: 4/5")
    print("  - Latency requirement: <2 seconds")
    print("  → Claude 3 Haiku ($25/day vs $300/day for Sonnet)")

    print("\n\n🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Add your own test prompts")
    print("2. Test Gemini (google-generativeai)")
    print("3. Build automated scoring (LLM-as-judge)")
    print("4. Track results over time")
    print("5. Integrate into your gateway!")


if __name__ == "__main__":
    main()
