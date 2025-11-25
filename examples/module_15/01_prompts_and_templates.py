#!/usr/bin/env python3
"""
Module 15 Example 1: Prompts and Templates

Demonstrates LangChain's prompt templating system:
- Basic PromptTemplate
- ChatPromptTemplate for chat models
- Few-shot prompts with examples
- Partial prompts
- Integration with LLMs (Gemini or Claude)

Why templates matter:
- Reusable across your application
- Type-safe variable injection
- Format instructions for output parsers
- Easier to test and maintain

Updated for LangChain 1.1.0+ (November 2025)
"""

import os
from typing import List, Optional

# Check for API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not GOOGLE_API_KEY and not ANTHROPIC_API_KEY:
    print("⚠️  No API key set. Set GOOGLE_API_KEY or ANTHROPIC_API_KEY")

# Try to import LangChain
try:
    from langchain_core.prompts import (
        PromptTemplate,
        ChatPromptTemplate,
        FewShotPromptTemplate,
        HumanMessagePromptTemplate,
        SystemMessagePromptTemplate,
    )
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


def demo_basic_prompt_template():
    """Demonstrate basic PromptTemplate usage."""
    print("\n" + "="*60)
    print("DEMO 1: Basic PromptTemplate")
    print("="*60)

    if not HAS_LANGCHAIN:
        print("⚠️  LangChain required")
        return

    # Create a simple template
    template = PromptTemplate(
        input_variables=["topic", "style"],
        template="Write a {style} explanation of {topic}."
    )

    # Format the template
    prompt = template.format(topic="recursion", style="simple")
    print(f"\n📝 Formatted prompt:\n   {prompt}")

    # Alternative: from_template factory method (auto-detects variables)
    template2 = PromptTemplate.from_template(
        "Explain {concept} to a {audience}."
    )
    prompt2 = template2.format(concept="machine learning", audience="5-year-old")
    print(f"\n📝 Factory method prompt:\n   {prompt2}")

    # Validate missing variables (this would raise an error)
    try:
        template.format(topic="recursion")  # Missing 'style'!
    except KeyError as e:
        print(f"\n✅ Template validation caught missing variable: {e}")


def demo_chat_prompt_template():
    """Demonstrate ChatPromptTemplate for chat models."""
    print("\n" + "="*60)
    print("DEMO 2: ChatPromptTemplate")
    print("="*60)

    if not HAS_LANGCHAIN:
        print("⚠️  LangChain required")
        return

    # Method 1: From messages (simplest)
    chat_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful {role}. Respond in {language}."),
        ("human", "{question}")
    ])

    messages = chat_template.format_messages(
        role="Python tutor",
        language="simple terms",
        question="What is a list comprehension?"
    )

    print("\n📝 Formatted messages:")
    for msg in messages:
        print(f"   [{msg.type}]: {msg.content}")

    # Method 2: Using message templates explicitly
    chat_template2 = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are an expert in {domain}."
        ),
        HumanMessagePromptTemplate.from_template(
            "Question: {question}\nContext: {context}"
        )
    ])

    messages2 = chat_template2.format_messages(
        domain="machine learning",
        question="What is overfitting?",
        context="Training a neural network on MNIST"
    )

    print("\n📝 Explicit message templates:")
    for msg in messages2:
        content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
        print(f"   [{msg.type}]: {content_preview}")


def demo_few_shot_prompt():
    """Demonstrate few-shot prompting with examples."""
    print("\n" + "="*60)
    print("DEMO 3: Few-Shot Prompts")
    print("="*60)

    if not HAS_LANGCHAIN:
        print("⚠️  LangChain required")
        return

    # Define examples
    examples = [
        {"word": "happy", "antonym": "sad"},
        {"word": "tall", "antonym": "short"},
        {"word": "fast", "antonym": "slow"},
    ]

    # Template for each example
    example_template = PromptTemplate(
        input_variables=["word", "antonym"],
        template="Word: {word}\nAntonym: {antonym}"
    )

    # Create few-shot prompt
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_template,
        prefix="Give the antonym of each word.\n",
        suffix="\nWord: {input}\nAntonym:",
        input_variables=["input"],
        example_separator="\n\n"
    )

    # Format
    prompt = few_shot_prompt.format(input="bright")

    print("\n📝 Few-shot prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)

    print("\n💡 The model sees 3 examples before answering!")


def demo_partial_prompts():
    """Demonstrate partial prompts with pre-filled variables."""
    print("\n" + "="*60)
    print("DEMO 4: Partial Prompts")
    print("="*60)

    if not HAS_LANGCHAIN:
        print("⚠️  LangChain required")
        return

    # Create a template with many variables
    template = PromptTemplate(
        input_variables=["company", "role", "task"],
        template="You work at {company} as a {role}. Your task: {task}"
    )

    # Partially fill - useful when some vars are known at startup
    company_template = template.partial(company="Neural Dojo")
    print(f"\n📝 After partial(company='Neural Dojo'):")
    print(f"   Remaining variables: {company_template.input_variables}")

    # Now only need role and task
    prompt = company_template.format(role="AI Engineer", task="Build a RAG system")
    print(f"\n📝 Final prompt:\n   {prompt}")

    # Partial with function (computed at format time)
    from datetime import datetime

    def get_current_date():
        return datetime.now().strftime("%Y-%m-%d")

    dated_template = PromptTemplate(
        input_variables=["task"],
        partial_variables={"date": get_current_date},
        template="Today is {date}. Task: {task}"
    )

    print(f"\n📝 Dynamic partial (date computed at format time):")
    print(f"   {dated_template.format(task='Review the code')}")


def demo_prompt_with_llm():
    """Demonstrate using prompts with an actual LLM."""
    print("\n" + "="*60)
    print("DEMO 5: Prompts + LLM Integration")
    print("="*60)

    if not HAS_LANGCHAIN:
        print("⚠️  LangChain required")
        return

    if not LLM:
        print("⚠️  API key required for LLM demo (GOOGLE_API_KEY or ANTHROPIC_API_KEY)")
        return

    print(f"\n🤖 Using: {LLM_NAME}")

    chat_template = ChatPromptTemplate.from_messages([
        ("system", "You are a concise assistant. Respond in one sentence."),
        ("human", "{question}")
    ])

    # Format and invoke
    messages = chat_template.format_messages(question="What is Python?")
    print("\n📤 Sending to LLM...")

    response = LLM.invoke(messages)
    print(f"\n📥 Response: {response.content}")


def main():
    """Run all demos."""
    print("="*60)
    print("LangChain Prompts and Templates")
    print("="*60)
    print("""
Prompts are the foundation of LangChain. Templates let you:
- Create reusable prompt patterns
- Inject variables safely
- Build few-shot examples
- Compose complex prompts
    """)

    demo_basic_prompt_template()
    demo_chat_prompt_template()
    demo_few_shot_prompt()
    demo_partial_prompts()
    demo_prompt_with_llm()

    print("\n" + "="*60)
    print("✅ Prompts and Templates Demo Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
