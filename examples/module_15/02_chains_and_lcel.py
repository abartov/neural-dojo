#!/usr/bin/env python3
"""
Module 15 Example 2: Chains and LCEL

Demonstrates LangChain's chaining mechanisms:
- LCEL (LangChain Expression Language) - the modern way
- Sequential chains
- Parallel execution
- Streaming
- Async execution

LCEL is the future of LangChain - more composable, better streaming,
and cleaner async support.

Updated for LangChain 1.1.0+ (November 2025)
Supports: Gemini (GOOGLE_API_KEY) or Claude (ANTHROPIC_API_KEY)
"""

import os
import asyncio
from typing import List, Dict, Any

# Check for API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not GOOGLE_API_KEY and not ANTHROPIC_API_KEY:
    print("⚠️  No API key set. Set GOOGLE_API_KEY or ANTHROPIC_API_KEY")

# Try to import LangChain
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    print("⚠️  LangChain not installed. Run: pip install langchain-core")

# Try to import LLM providers
LLM = None
LLM_NAME = None

try:
    if GOOGLE_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI
        LLM = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
        LLM_NAME = "Gemini 1.5 Flash"
    elif ANTHROPIC_API_KEY:
        from langchain_anthropic import ChatAnthropic
        LLM = ChatAnthropic(model="claude-sonnet-4-20250514")
        LLM_NAME = "Claude Sonnet"
except ImportError as e:
    print(f"⚠️  LLM provider not installed: {e}")


def demo_simple_chain():
    """Demonstrate the simplest LCEL chain."""
    print("\n" + "="*60)
    print("DEMO 1: Simple LCEL Chain")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")

    # Components
    prompt = ChatPromptTemplate.from_template(
        "Tell me one interesting fact about {topic}. Keep it to one sentence."
    )
    output_parser = StrOutputParser()

    # LCEL chain with pipe operator
    chain = prompt | LLM | output_parser

    print("\n📝 Chain structure: prompt | model | output_parser")
    print("\n📤 Invoking chain...")

    result = chain.invoke({"topic": "the Eiffel Tower"})
    print(f"\n📥 Result: {result}")


def demo_sequential_chain():
    """Demonstrate chaining multiple operations."""
    print("\n" + "="*60)
    print("DEMO 2: Sequential Chain (Multi-step)")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    parser = StrOutputParser()

    # Chain 1: Generate a topic
    topic_prompt = ChatPromptTemplate.from_template(
        "Generate a random interesting topic for a blog post. "
        "Just respond with the topic, nothing else."
    )
    topic_chain = topic_prompt | LLM | parser

    # Chain 2: Write outline based on topic
    outline_prompt = ChatPromptTemplate.from_template(
        "Write a 3-point outline for a blog post about: {topic}\n"
        "Format: numbered list, one line each."
    )
    outline_chain = outline_prompt | LLM | parser

    # Combine: topic → outline
    # Use a dict to pass the topic to the next prompt
    full_chain = (
        topic_chain
        | (lambda topic: {"topic": topic})
        | outline_chain
    )

    print("\n📝 Chain: Generate Topic → Create Outline")
    print("\n📤 Running sequential chain...")

    result = full_chain.invoke({})
    print(f"\n📥 Final Outline:\n{result}")


def demo_parallel_chain():
    """Demonstrate parallel execution with RunnableParallel."""
    print("\n" + "="*60)
    print("DEMO 3: Parallel Chain")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    parser = StrOutputParser()

    # Create parallel analysis chains
    sentiment_prompt = ChatPromptTemplate.from_template(
        "Analyze the sentiment of this text in one word (positive/negative/neutral): {text}"
    )
    keyword_prompt = ChatPromptTemplate.from_template(
        "Extract 3 keywords from this text as a comma-separated list: {text}"
    )
    summary_prompt = ChatPromptTemplate.from_template(
        "Summarize this text in one sentence: {text}"
    )

    # Run all three in parallel
    analysis_chain = RunnableParallel(
        sentiment=sentiment_prompt | LLM | parser,
        keywords=keyword_prompt | LLM | parser,
        summary=summary_prompt | LLM | parser
    )

    sample_text = """
    LangChain is a framework for developing applications powered by language models.
    It enables applications that are context-aware and can reason. The framework
    provides integrations with many LLM providers and tools.
    """

    print("\n📝 Running 3 analyses in parallel...")
    print(f"   Text: {sample_text.strip()[:50]}...")

    result = analysis_chain.invoke({"text": sample_text})

    print("\n📥 Results (ran in parallel!):")
    print(f"   Sentiment: {result['sentiment']}")
    print(f"   Keywords: {result['keywords']}")
    print(f"   Summary: {result['summary']}")


def demo_streaming():
    """Demonstrate streaming with LCEL."""
    print("\n" + "="*60)
    print("DEMO 4: Streaming")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")

    prompt = ChatPromptTemplate.from_template(
        "Write a haiku about {topic}."
    )
    parser = StrOutputParser()

    chain = prompt | LLM | parser

    print("\n📤 Streaming response:")
    print("-" * 40)

    # Stream tokens as they arrive
    for chunk in chain.stream({"topic": "programming"}):
        print(chunk, end="", flush=True)

    print("\n" + "-" * 40)
    print("✅ Streaming complete!")


async def demo_async():
    """Demonstrate async execution."""
    print("\n" + "="*60)
    print("DEMO 5: Async Execution")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")

    prompt = ChatPromptTemplate.from_template(
        "In one word, what color is a {thing}?"
    )
    parser = StrOutputParser()

    chain = prompt | LLM | parser

    # Run multiple async calls concurrently
    things = ["banana", "sky", "grass", "fire"]

    print(f"\n📤 Running {len(things)} async calls concurrently...")

    tasks = [chain.ainvoke({"thing": t}) for t in things]
    results = await asyncio.gather(*tasks)

    print("\n📥 Results (ran concurrently!):")
    for thing, color in zip(things, results):
        print(f"   {thing}: {color.strip()}")


def demo_passthrough():
    """Demonstrate RunnablePassthrough for forwarding inputs."""
    print("\n" + "="*60)
    print("DEMO 6: RunnablePassthrough")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    parser = StrOutputParser()

    # Simulate a retriever that returns context
    def fake_retriever(query: str) -> str:
        return f"Context about '{query}': It's a popular topic in AI."

    # Chain that uses both retrieved context AND the original question
    prompt = ChatPromptTemplate.from_template(
        "Context: {context}\n\nQuestion: {question}\n\nAnswer briefly:"
    )

    # Use itemgetter for cleaner syntax
    from operator import itemgetter

    chain = (
        {
            "context": itemgetter("question") | (lambda q: fake_retriever(q)),
            "question": itemgetter("question")
        }
        | prompt
        | LLM
        | parser
    )

    print("\n📝 Chain combines retrieval + original question")
    result = chain.invoke({"question": "What is LangChain?"})
    print(f"\n📥 Result: {result}")


def main():
    """Run all demos."""
    print("="*60)
    print("LangChain Chains and LCEL")
    print("="*60)
    print("""
LCEL (LangChain Expression Language) is the modern way to build chains.

Key concepts:
- Pipe operator (|) chains components
- RunnableParallel for concurrent execution
- Streaming and async are built-in
- RunnablePassthrough forwards inputs

chain = prompt | model | parser
    """)

    demo_simple_chain()
    demo_sequential_chain()
    demo_parallel_chain()
    demo_streaming()
    demo_passthrough()

    # Run async demo
    if HAS_LANGCHAIN and LLM:
        print("\n🔄 Running async demo...")
        asyncio.run(demo_async())

    print("\n" + "="*60)
    print("✅ Chains and LCEL Demo Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
