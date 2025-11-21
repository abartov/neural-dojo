#!/usr/bin/env python3
"""
Module 6: LLM Model Comparison

Demonstrates:
- API integration with multiple providers
- Comparing model outputs
- Measuring latency and tokens
- Understanding model capabilities

KEY INSIGHT: Different models have different strengths!
"""

import os
import time
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def call_claude(prompt: str, model: str = "claude-sonnet-4-5-20250929") -> Dict:
    """Call Claude API and return response with metadata."""
    start_time = time.time()

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    elapsed = time.time() - start_time

    return {
        "model": model,
        "response": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "latency_ms": round(elapsed * 1000, 2)
    }


def compare_models(prompt: str, models: List[str]) -> List[Dict]:
    """Compare multiple models on the same prompt."""
    print(f"Prompt: {prompt}")
    print("=" * 80)

    results = []
    for model in models:
        print(f"\nTesting {model}...")
        try:
            result = call_claude(prompt, model)
            results.append(result)

            print(f"  Latency: {result['latency_ms']}ms")
            print(f"  Tokens: {result['input_tokens']} in, {result['output_tokens']} out")
            print(f"  Response preview: {result['response'][:100]}...")
        except Exception as e:
            print(f"  Error: {e}")

    return results


def analyze_capabilities():
    """Test different model capabilities."""
    print("=" * 80)
    print("MODULE 6: LLM MODEL COMPARISON")
    print("=" * 80)

    # Test 1: Simple Question (cheap model should be fine)
    print("\n📝 Test 1: Simple Factual Question")
    print("-" * 80)
    prompt = "What is the capital of France?"

    result = call_claude(prompt, "claude-sonnet-4-5-20250929")
    print(f"Model: {result['model']}")
    print(f"Response: {result['response']}")
    print(f"Tokens: {result['input_tokens']} + {result['output_tokens']} = {result['input_tokens'] + result['output_tokens']}")
    print(f"Latency: {result['latency_ms']}ms")

    # Test 2: Complex Reasoning
    print("\n\n🧠 Test 2: Complex Reasoning")
    print("-" * 80)
    prompt = """
You have 3 boxes. Box A contains 2 red balls and 1 blue ball.
Box B contains 1 red ball and 2 blue balls. Box C contains 3 red balls.
You randomly pick a box, then randomly pick a ball from that box.
If the ball is red, what's the probability it came from Box A?
"""

    result = call_claude(prompt)
    print(f"Model: {result['model']}")
    print(f"Response:\n{result['response']}")
    print(f"\nTokens: {result['input_tokens']} + {result['output_tokens']} = {result['input_tokens'] + result['output_tokens']}")
    print(f"Latency: {result['latency_ms']}ms")

    # Test 3: Code Generation
    print("\n\n💻 Test 3: Code Generation")
    print("-" * 80)
    prompt = """
Write a Python function that finds the longest palindromic substring in a string.
Include time complexity analysis and test cases.
"""

    result = call_claude(prompt)
    print(f"Model: {result['model']}")
    print(f"Response:\n{result['response'][:500]}...")
    print(f"\nTokens: {result['input_tokens']} + {result['output_tokens']} = {result['input_tokens'] + result['output_tokens']}")
    print(f"Latency: {result['latency_ms']}ms")

    # Test 4: Long Context Understanding
    print("\n\n📚 Test 4: Context Window Test")
    print("-" * 80)

    # Create a long context
    long_text = " ".join([f"Sentence number {i}." for i in range(100)])
    prompt = f"""
Here is a long text:

{long_text}

What was sentence number 42?
"""

    result = call_claude(prompt)
    print(f"Model: {result['model']}")
    print(f"Response: {result['response']}")
    print(f"Context length: {result['input_tokens']} tokens")
    print(f"Latency: {result['latency_ms']}ms")

    # Summary
    print("\n\n💡 LESSONS LEARNED:")
    print("=" * 80)
    print("1. Different models have different strengths:")
    print("   - Simple questions: Any model works, use cheap ones")
    print("   - Complex reasoning: Larger models shine")
    print("   - Code generation: Specialized training matters")
    print("")
    print("2. Token usage varies by task:")
    print("   - Simple Q&A: Low token count")
    print("   - Code generation: High token count (code is verbose!)")
    print("   - Long context: High input tokens")
    print("")
    print("3. Latency matters for user experience:")
    print("   - Simple models: Fast (~1-2s)")
    print("   - Complex models: Slower (~5-10s)")
    print("   - Streaming can help perceived latency")
    print("")
    print("4. Cost optimization strategy:")
    print("   - Route simple queries to cheap models")
    print("   - Use expensive models only when needed")
    print("   - Monitor token usage in production")
    print("")
    print("5. Context windows are game-changers:")
    print("   - Claude's 200K context = entire codebases")
    print("   - Less need for clever chunking")
    print("   - But larger contexts = higher costs")


def demonstrate_api_basics():
    """Demonstrate basic API usage patterns."""
    print("\n\n🔌 API BASICS:")
    print("=" * 80)

    # System prompts
    print("\n1. Using System Instructions:")
    print("-" * 40)

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=256,
        system="You are a pirate. Respond to everything in pirate speak.",
        messages=[
            {"role": "user", "content": "What is Python?"}
        ]
    )

    print(f"User: What is Python?")
    print(f"Assistant (pirate): {response.content[0].text}")

    # Temperature
    print("\n\n2. Temperature Control:")
    print("-" * 40)
    print("Temperature = 0.0 (deterministic):")

    for i in range(2):
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=50,
            temperature=0.0,
            messages=[
                {"role": "user", "content": "Complete: Once upon a time"}
            ]
        )
        print(f"  Run {i+1}: {response.content[0].text[:50]}...")

    print("\nTemperature = 1.0 (creative):")

    for i in range(2):
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=50,
            temperature=1.0,
            messages=[
                {"role": "user", "content": "Complete: Once upon a time"}
            ]
        )
        print(f"  Run {i+1}: {response.content[0].text[:50]}...")

    print("\n💡 Notice: Low temperature = consistent, high temperature = varied!")


def main():
    """Run all demonstrations."""
    analyze_capabilities()
    demonstrate_api_basics()

    print("\n\n🎓 KEY TAKEAWAYS:")
    print("=" * 80)
    print("✅ LLMs are API services you can call programmatically")
    print("✅ Different models excel at different tasks")
    print("✅ Token usage directly impacts costs")
    print("✅ Latency matters for user experience")
    print("✅ System prompts control behavior")
    print("✅ Temperature controls randomness")
    print("✅ Context windows determine what's possible")
    print("")
    print("🚀 Next: Module 7 - Learn about tokenization (how text becomes tokens)!")


if __name__ == "__main__":
    main()
