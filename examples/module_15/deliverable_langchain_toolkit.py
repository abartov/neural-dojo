#!/usr/bin/env python3
"""
Module 15 Deliverable: LangChain Toolkit

A comprehensive toolkit demonstrating LangChain fundamentals:
1. Conversational chatbot with memory
2. LCEL pipelines with streaming
3. Multi-model router (complex → more capable, simple → faster)
4. Output parsing for structured data
5. Interactive chat mode

Usage:
    python deliverable_langchain_toolkit.py demo1       # Conversational chatbot
    python deliverable_langchain_toolkit.py demo2       # LCEL pipelines
    python deliverable_langchain_toolkit.py demo3       # Multi-model routing
    python deliverable_langchain_toolkit.py interactive # Interactive chat
    python deliverable_langchain_toolkit.py help        # Show help

Supports: Gemini (GOOGLE_API_KEY) or Claude (ANTHROPIC_API_KEY)

Author: Neural Dojo
Version: 2.0.0 (Updated for LangChain 1.1.0+)
"""

import os
import sys
import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime

# Check for API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not GOOGLE_API_KEY and not ANTHROPIC_API_KEY:
    print("⚠️  No API key set. Set GOOGLE_API_KEY or ANTHROPIC_API_KEY")

# Try to import LangChain
try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
    from pydantic import BaseModel, Field
    HAS_LANGCHAIN = True
except ImportError as e:
    HAS_LANGCHAIN = False
    print(f"⚠️  LangChain not fully installed: {e}")
    print("   Run: pip install langchain-core langchain-google-genai pydantic")

# Try to import LLM providers
LLM = None
LLM_NAME = None
LLM_FAST = None
LLM_FAST_NAME = None

try:
    if GOOGLE_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI
        LLM = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
        LLM_NAME = "Gemini 1.5 Flash"
        LLM_FAST = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
        LLM_FAST_NAME = "Gemini 1.5 Flash"
    elif ANTHROPIC_API_KEY:
        from langchain_anthropic import ChatAnthropic
        LLM = ChatAnthropic(model="claude-sonnet-4-20250514")
        LLM_NAME = "Claude Sonnet"
        LLM_FAST = ChatAnthropic(model="claude-sonnet-4-20250514")
        LLM_FAST_NAME = "Claude Sonnet"
except ImportError as e:
    print(f"⚠️  LLM provider not installed: {e}")


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ChatMessage:
    """A single chat message."""
    role: Literal["human", "assistant", "system"]
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConversationSession:
    """A conversation session with history."""
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    model: str = "gemini-1.5-flash"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RoutingDecision:
    """Decision from the model router."""
    complexity: Literal["simple", "complex"]
    model_used: str
    reasoning: str
    response: str


# =============================================================================
# Storage
# =============================================================================

STORAGE_DIR = os.path.join(os.path.dirname(__file__), ".langchain_toolkit")
os.makedirs(STORAGE_DIR, exist_ok=True)


def save_session(session: ConversationSession) -> None:
    """Save a conversation session."""
    filepath = os.path.join(STORAGE_DIR, f"session_{session.session_id}.json")
    data = {
        "session_id": session.session_id,
        "messages": [asdict(m) for m in session.messages],
        "model": session.model,
        "created_at": session.created_at
    }
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_session(session_id: str) -> Optional[ConversationSession]:
    """Load a conversation session."""
    filepath = os.path.join(STORAGE_DIR, f"session_{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath) as f:
            data = json.load(f)
            messages = [ChatMessage(**m) for m in data.get("messages", [])]
            return ConversationSession(
                session_id=data["session_id"],
                messages=messages,
                model=data.get("model", "unknown"),
                created_at=data.get("created_at", "")
            )
    return None


# =============================================================================
# Conversational Chatbot
# =============================================================================

class ConversationalChatbot:
    """
    A chatbot with conversation memory using RunnableWithMessageHistory.

    Uses the modern LangChain 1.1.0+ approach:
    - RunnableWithMessageHistory for automatic message tracking
    - InMemoryChatMessageHistory for session storage
    - Message trimming for long conversations
    """

    def __init__(self, max_messages: int = 20):
        if not HAS_LANGCHAIN or not LLM:
            raise RuntimeError("LangChain and API key required")

        self.llm = LLM
        self.max_messages = max_messages

        # Create the prompt template with message history
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Be concise but thorough."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

        # Session storage
        self.store: Dict[str, InMemoryChatMessageHistory] = {}

        # Create the chain with message history
        self.with_history = RunnableWithMessageHistory(
            self.chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        # For saving to disk
        self.session = ConversationSession(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            model=LLM_NAME or "unknown"
        )
        self.config = {"configurable": {"session_id": self.session.session_id}}

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history."""
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def chat(self, message: str) -> str:
        """Send a message and get a response."""
        # Add to our session for disk persistence
        self.session.messages.append(
            ChatMessage(role="human", content=message)
        )

        # Get response using the chain with history
        response = self.with_history.invoke(
            {"input": message},
            config=self.config
        )

        # Add response to session
        self.session.messages.append(
            ChatMessage(role="assistant", content=response)
        )

        # Trim if needed
        self._trim_history()

        return response

    def _trim_history(self) -> None:
        """Trim history if it exceeds max_messages."""
        history = self.store.get(self.session.session_id)
        if history and len(history.messages) > self.max_messages:
            # Keep last max_messages
            history.messages = history.messages[-self.max_messages:]

    def get_memory_summary(self) -> str:
        """Get a summary of current memory."""
        history = self.store.get(self.session.session_id)
        if not history:
            return "No messages yet."

        messages = history.messages
        lines = []
        for msg in messages[-10:]:  # Show last 10
            prefix = "Human" if isinstance(msg, HumanMessage) else "AI"
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            lines.append(f"  {prefix}: {content}")

        return f"Last {min(10, len(messages))} of {len(messages)} messages:\n" + "\n".join(lines)

    def save(self) -> None:
        """Save the current session."""
        save_session(self.session)
        print(f"💾 Session saved: {self.session.session_id}")


# =============================================================================
# LCEL Pipeline Builder
# =============================================================================

class LCELPipelineBuilder:
    """
    Builder for LCEL (LangChain Expression Language) pipelines.

    Demonstrates:
    - Simple chains
    - Parallel execution
    - Streaming
    - Output parsing
    """

    def __init__(self):
        if not HAS_LANGCHAIN or not LLM:
            raise RuntimeError("LangChain and API key required")

        self.llm = LLM
        self.parser = StrOutputParser()

    def simple_chain(self, template: str):
        """Create a simple prompt → model → parser chain."""
        prompt = ChatPromptTemplate.from_template(template)
        return prompt | self.llm | self.parser

    def parallel_analysis(self):
        """
        Create a parallel analysis chain.

        Runs sentiment, keywords, and summary in parallel.
        """
        sentiment_prompt = ChatPromptTemplate.from_template(
            "Analyze sentiment in one word (positive/negative/neutral): {text}"
        )
        keywords_prompt = ChatPromptTemplate.from_template(
            "Extract 3 keywords as comma-separated list: {text}"
        )
        summary_prompt = ChatPromptTemplate.from_template(
            "Summarize in one sentence: {text}"
        )

        return RunnableParallel(
            sentiment=sentiment_prompt | self.llm | self.parser,
            keywords=keywords_prompt | self.llm | self.parser,
            summary=summary_prompt | self.llm | self.parser
        )

    def streaming_chain(self, template: str):
        """Create a chain that supports streaming."""
        prompt = ChatPromptTemplate.from_template(template)
        return prompt | self.llm | self.parser

    def invoke_with_streaming(self, chain, inputs: Dict[str, Any]) -> str:
        """Invoke a chain with streaming output."""
        full_response = ""
        for chunk in chain.stream(inputs):
            print(chunk, end="", flush=True)
            full_response += chunk
        print()  # Newline after streaming
        return full_response


# =============================================================================
# Multi-Model Router
# =============================================================================

class MultiModelRouter:
    """
    Routes queries to different models based on complexity.

    Strategy:
    - Simple queries → faster model (or same model with simpler prompt)
    - Complex queries → more capable model

    This can save costs when using different model tiers!
    """

    def __init__(self):
        if not HAS_LANGCHAIN or not LLM:
            raise RuntimeError("LangChain and API key required")

        self.complex_llm = LLM
        self.simple_llm = LLM_FAST or LLM
        self.parser = StrOutputParser()

        # Classifier prompt
        self.classifier_prompt = ChatPromptTemplate.from_template(
            """Classify this query as SIMPLE or COMPLEX.

SIMPLE: Factual questions, definitions, simple tasks
COMPLEX: Reasoning, analysis, creative tasks, multi-step problems

Query: {query}

Respond with only: SIMPLE or COMPLEX"""
        )

        self.classifier = self.classifier_prompt | self.simple_llm | self.parser

    def route(self, query: str) -> RoutingDecision:
        """Route a query to the appropriate model."""
        # Classify
        classification = self.classifier.invoke({"query": query}).strip().upper()
        is_complex = "COMPLEX" in classification

        # Select model
        llm = self.complex_llm if is_complex else self.simple_llm
        model_name = f"{LLM_NAME} (complex)" if is_complex else f"{LLM_FAST_NAME} (simple)"

        # Generate response
        response_prompt = ChatPromptTemplate.from_template("{query}")
        chain = response_prompt | llm | self.parser

        response = chain.invoke({"query": query})

        return RoutingDecision(
            complexity="complex" if is_complex else "simple",
            model_used=model_name,
            reasoning=classification,
            response=response
        )


# =============================================================================
# Demo Functions
# =============================================================================

def demo_1_conversational_chatbot():
    """Demo 1: Conversational chatbot with memory."""
    print("\n" + "="*60)
    print("DEMO 1: Conversational Chatbot with Memory")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  Requires LangChain and API key (GOOGLE_API_KEY or ANTHROPIC_API_KEY)")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    print("""
This demo shows a chatbot that remembers conversation context.
Uses RunnableWithMessageHistory to:
- Automatically track conversation history
- Support message trimming for long conversations
    """)

    chatbot = ConversationalChatbot()

    conversations = [
        "Hi! My name is Alice and I'm a Python developer.",
        "I've been coding for about 5 years, mostly backend.",
        "I'm interested in learning machine learning.",
        "What should I focus on given my background?"
    ]

    print("📤 Starting conversation...\n")

    for msg in conversations:
        print(f"👤 Human: {msg}")
        response = chatbot.chat(msg)
        print(f"🤖 Assistant: {response}\n")

    print("\n📝 Memory Summary:")
    print("-" * 40)
    print(chatbot.get_memory_summary())

    chatbot.save()
    print("\n✅ Demo 1 Complete!")


def demo_2_lcel_pipelines():
    """Demo 2: LCEL pipeline examples."""
    print("\n" + "="*60)
    print("DEMO 2: LCEL Pipelines")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  Requires LangChain and API key (GOOGLE_API_KEY or ANTHROPIC_API_KEY)")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    print("""
LCEL (LangChain Expression Language) is the modern way to build chains.
Uses the pipe operator: prompt | model | parser
    """)

    builder = LCELPipelineBuilder()

    # Simple chain
    print("\n📊 Simple Chain:")
    simple = builder.simple_chain("Tell me one fact about {topic} in one sentence.")
    result = simple.invoke({"topic": "the Moon"})
    print(f"   Result: {result}")

    # Parallel analysis
    print("\n📊 Parallel Analysis (3 tasks simultaneously):")
    text = """
    LangChain has become the most popular framework for building LLM applications.
    It provides useful abstractions but has also been criticized for over-engineering.
    The framework continues to evolve rapidly with LCEL as the new standard.
    """
    parallel = builder.parallel_analysis()
    results = parallel.invoke({"text": text})
    print(f"   Sentiment: {results['sentiment']}")
    print(f"   Keywords: {results['keywords']}")
    print(f"   Summary: {results['summary']}")

    # Streaming
    print("\n📊 Streaming Chain:")
    print("   Response: ", end="")
    streaming = builder.streaming_chain("Write a haiku about {topic}.")
    builder.invoke_with_streaming(streaming, {"topic": "programming"})

    print("\n✅ Demo 2 Complete!")


def demo_3_multi_model_router():
    """Demo 3: Multi-model routing."""
    print("\n" + "="*60)
    print("DEMO 3: Multi-Model Router")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  Requires LangChain and API key (GOOGLE_API_KEY or ANTHROPIC_API_KEY)")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    print("""
Routes queries to different models based on complexity:
- Simple queries → faster/cheaper model
- Complex queries → more capable model

This strategy can reduce costs by 50-70% in production!
    """)

    router = MultiModelRouter()

    queries = [
        "What is the capital of France?",  # Simple
        "Explain the philosophical implications of AI consciousness.",  # Complex
        "What is 2 + 2?",  # Simple
        "Design a microservices architecture for an e-commerce platform.",  # Complex
    ]

    for query in queries:
        print(f"\n📤 Query: {query[:50]}...")
        decision = router.route(query)
        print(f"   🎯 Complexity: {decision.complexity}")
        print(f"   🤖 Model: {decision.model_used}")
        print(f"   📝 Response: {decision.response[:100]}...")

    print("\n✅ Demo 3 Complete!")


def interactive_chat():
    """Interactive chat mode."""
    print("\n" + "="*60)
    print("INTERACTIVE CHAT MODE")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  Requires LangChain and API key (GOOGLE_API_KEY or ANTHROPIC_API_KEY)")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    print("""
Chat with an AI that remembers your conversation!

Commands:
  /memory  - Show memory summary
  /save    - Save conversation
  /quit    - Exit
    """)

    chatbot = ConversationalChatbot()

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "/quit":
                chatbot.save()
                print("👋 Goodbye!")
                break

            if user_input.lower() == "/memory":
                print("\n📝 Memory Summary:")
                print(chatbot.get_memory_summary())
                continue

            if user_input.lower() == "/save":
                chatbot.save()
                continue

            response = chatbot.chat(user_input)
            print(f"\n🤖 Assistant: {response}")

        except KeyboardInterrupt:
            chatbot.save()
            print("\n👋 Goodbye!")
            break


def show_help():
    """Show help information."""
    print("""
LangChain Toolkit - Module 15 Deliverable
==========================================

Usage:
    python deliverable_langchain_toolkit.py <command>

Commands:
    demo1       Conversational chatbot with memory
    demo2       LCEL pipelines (simple, parallel, streaming)
    demo3       Multi-model routing by complexity
    interactive Interactive chat mode
    help        Show this help message

Requirements:
    - GOOGLE_API_KEY or ANTHROPIC_API_KEY environment variable
    - pip install langchain-core langchain-google-genai pydantic
      OR
    - pip install langchain-core langchain-anthropic pydantic

Examples:
    export GOOGLE_API_KEY="your-gemini-key"
    python deliverable_langchain_toolkit.py demo1
    python deliverable_langchain_toolkit.py interactive

Output:
    Sessions saved to .langchain_toolkit/ directory
    """)


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    print("="*60)
    print("LangChain Toolkit - Module 15 Deliverable")
    print("="*60)

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_1_conversational_chatbot()
    elif command == "demo2":
        demo_2_lcel_pipelines()
    elif command == "demo3":
        demo_3_multi_model_router()
    elif command == "interactive":
        interactive_chat()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
