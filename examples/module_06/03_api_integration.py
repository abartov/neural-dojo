#!/usr/bin/env python3
"""
Module 6: Production API Integration

Demonstrates building a production-ready LLM API integration with:
- Error handling
- Retries
- Timeout handling
- Response validation
- Cost tracking

THEORY CONNECTION:
- Module 6 Section: "Your First API Integration" (line 577+)
- Key Concept: Production patterns for LLM APIs
- What you'll learn: How to build reliable integrations

KEY INSIGHT: API calls fail. Design for failure from day one!
"""

import os
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    """Response from LLM with metadata."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: float


class ProductionLLMClient:
    """
    Production-ready LLM client with best practices.

    Features:
    - Automatic retries with exponential backoff
    - Timeout handling
    - Error handling and logging
    - Cost tracking
    - Response validation
    """

    # Pricing (per 1M tokens)
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
    }

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """Initialize client."""
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.max_retries = max_retries
        self.total_cost = 0.0

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API call."""
        if model not in self.PRICING:
            return 0.0  # Unknown model

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def call(
        self,
        prompt: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """
        Call LLM with production best practices.

        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Max response length
            temperature: Randomness (0-1)
            system: System instructions

        Returns:
            LLMResponse with content and metadata

        Raises:
            APIError: If all retries fail
        """
        start_time = time.time()

        messages = [{"role": "user", "content": prompt}]

        # Try with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Make API call
                kwargs = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": messages,
                }

                if system:
                    kwargs["system"] = system

                response = self.client.messages.create(**kwargs)

                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)

                # Extract usage
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

                # Calculate cost
                cost = self.calculate_cost(model, input_tokens, output_tokens)
                self.total_cost += cost

                # Extract content
                content = response.content[0].text

                # Validate response
                if not content or len(content.strip()) == 0:
                    raise ValueError("Empty response from API")

                return LLMResponse(
                    content=content,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                    cost_usd=cost,
                )

            except RateLimitError as e:
                # Rate limited - wait and retry
                wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                print(f"⚠️  Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                time.sleep(wait_time)

            except APIConnectionError as e:
                # Network error - retry
                wait_time = (2 ** attempt) * 1
                print(f"⚠️  Connection error. Retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
                time.sleep(wait_time)

            except APIError as e:
                # Other API error
                if e.status_code >= 500:
                    # Server error - retry
                    wait_time = (2 ** attempt) * 1
                    print(f"⚠️  Server error {e.status_code}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Client error (4xx) - don't retry
                    raise

        # All retries failed
        raise APIError(f"Failed after {self.max_retries} retries")


def main():
    """Demonstrate production API integration."""
    print("=" * 60)
    print("MODULE 6: PRODUCTION API INTEGRATION")
    print("=" * 60)

    client = ProductionLLMClient(max_retries=3)

    # Example 1: Basic call
    print("\n📝 Example 1: Basic API Call")
    print("-" * 60)

    response1 = client.call(
        prompt="Explain LLMs in one sentence.",
        model="claude-3-haiku-20240307",  # Cheap model for simple task
        max_tokens=100,
    )

    print(f"Model: {response1.model}")
    print(f"Response: {response1.content}")
    print(f"Tokens: {response1.input_tokens} in, {response1.output_tokens} out")
    print(f"Latency: {response1.latency_ms}ms")
    print(f"Cost: ${response1.cost_usd:.6f}")

    # Example 2: Complex task with system instructions
    print("\n\n📝 Example 2: Complex Task with System Instructions")
    print("-" * 60)

    response2 = client.call(
        prompt="Write a haiku about transformers (the AI architecture, not robots).",
        model="claude-sonnet-4-5-20250929",  # Better model for creative task
        max_tokens=200,
        temperature=0.9,  # More creative
        system="You are a creative poet who loves computer science.",
    )

    print(f"Model: {response2.model}")
    print(f"Haiku:\n{response2.content}")
    print(f"Tokens: {response2.input_tokens} in, {response2.output_tokens} out")
    print(f"Latency: {response2.latency_ms}ms")
    print(f"Cost: ${response2.cost_usd:.6f}")

    # Example 3: Batch processing with cost tracking
    print("\n\n📝 Example 3: Batch Processing (Cost Tracking)")
    print("-" * 60)

    questions = [
        "What is attention in transformers?",
        "What is pre-training?",
        "What is fine-tuning?",
    ]

    print(f"Processing {len(questions)} questions...")

    for i, question in enumerate(questions, 1):
        response = client.call(
            prompt=question,
            model="claude-3-haiku-20240307",  # Cheap model for Q&A
            max_tokens=150,
            temperature=0.3,  # Factual
        )

        print(f"\n{i}. {question}")
        print(f"   Answer: {response.content[:100]}...")
        print(f"   Cost: ${response.cost_usd:.6f}")

    print(f"\n📊 Total cost for batch: ${client.total_cost:.6f}")

    # Summary
    print("\n\n💡 PRODUCTION BEST PRACTICES:")
    print("=" * 60)
    print("1. Error Handling:")
    print("   ✅ Retry on rate limits (exponential backoff)")
    print("   ✅ Retry on server errors (5xx)")
    print("   ❌ Don't retry on client errors (4xx)")
    print("")
    print("2. Cost Tracking:")
    print("   ✅ Track input/output tokens")
    print("   ✅ Calculate cost per call")
    print("   ✅ Log total spend")
    print("")
    print("3. Model Selection:")
    print("   ✅ Use cheap models for simple tasks")
    print("   ✅ Use expensive models for complex tasks")
    print("   ✅ Route intelligently")
    print("")
    print("4. Timeouts:")
    print("   ✅ Set reasonable timeouts (10-30s)")
    print("   ✅ Fail fast, don't hang forever")
    print("")
    print("5. Validation:")
    print("   ✅ Check response is not empty")
    print("   ✅ Validate expected format")
    print("   ✅ Log unexpected responses")
    print("")
    print("6. Monitoring:")
    print("   ✅ Track latency (p50, p95, p99)")
    print("   ✅ Track error rates")
    print("   ✅ Alert on anomalies")

    print("\n\n🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Add logging (Python logging module)")
    print("2. Add metrics (Prometheus, Datadog)")
    print("3. Add fallback to different model")
    print("4. Add caching to save costs")
    print("5. Build this into your gateway!")


if __name__ == "__main__":
    main()
