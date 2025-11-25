#!/usr/bin/env python3
"""
Module 15 Example 3: Memory Systems

Demonstrates conversation memory in LangChain 1.1.0+:
- Manual message history management
- RunnableWithMessageHistory for stateful chains
- In-memory chat history
- Message trimming strategies

Memory solves the statefulness problem: LLMs don't remember
previous messages unless you explicitly pass them!

Updated for LangChain 1.1.0+ (November 2025)
Supports: Gemini (GOOGLE_API_KEY) or Claude (ANTHROPIC_API_KEY)
"""

import os
from typing import List, Dict
from collections import defaultdict

# Check for API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not GOOGLE_API_KEY and not ANTHROPIC_API_KEY:
    print("⚠️  No API key set. Set GOOGLE_API_KEY or ANTHROPIC_API_KEY")

# Try to import LangChain
try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory
    HAS_LANGCHAIN = True
except ImportError as e:
    HAS_LANGCHAIN = False
    print(f"⚠️  LangChain not installed: {e}")
    print("   Run: pip install langchain-core")

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


def demo_stateless_problem():
    """Demonstrate why memory is needed."""
    print("\n" + "="*60)
    print("DEMO 1: The Stateless Problem")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    print("\n📤 Without memory:")

    # Call 1
    response1 = LLM.invoke([HumanMessage(content="My name is Alice. Nice to meet you!")])
    print(f"   Human: My name is Alice. Nice to meet you!")
    print(f"   AI: {response1.content[:100]}...")

    # Call 2 - LLM has no memory of call 1!
    response2 = LLM.invoke([HumanMessage(content="What's my name?")])
    print(f"\n   Human: What's my name?")
    print(f"   AI: {response2.content[:100]}...")

    print("\n❌ The LLM doesn't remember! Each call is independent.")
    print("   This is why we need memory...")


def demo_manual_message_history():
    """Demonstrate manually managing message history."""
    print("\n" + "="*60)
    print("DEMO 2: Manual Message History")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")
    print("\n📤 With manual message history:")

    # Maintain conversation history ourselves
    messages = [
        SystemMessage(content="You are a helpful assistant. Be concise.")
    ]

    exchanges = [
        "My name is Alice.",
        "I work as a software engineer.",
        "What's my name and what do I do?"
    ]

    for human_input in exchanges:
        # Add human message
        messages.append(HumanMessage(content=human_input))

        # Get response
        response = LLM.invoke(messages)

        # Add AI response to history
        messages.append(AIMessage(content=response.content))

        print(f"\n   Human: {human_input}")
        print(f"   AI: {response.content[:150]}...")

    print("\n✅ By passing full history, the LLM remembers context!")
    print(f"   Total messages in history: {len(messages)}")


def demo_runnable_with_message_history():
    """Demonstrate RunnableWithMessageHistory for automatic memory."""
    print("\n" + "="*60)
    print("DEMO 3: RunnableWithMessageHistory (Automatic Memory)")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")

    # Create a prompt that includes message history
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Be concise."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | LLM | StrOutputParser()

    # Store for multiple sessions
    store: Dict[str, InMemoryChatMessageHistory] = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    # Wrap chain with message history
    with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    print("\n📤 With RunnableWithMessageHistory:")

    # Same conversation as before
    exchanges = [
        "My name is Alice.",
        "I'm a Python developer with 5 years experience.",
        "What do you know about me?"
    ]

    session_id = "user_123"
    config = {"configurable": {"session_id": session_id}}

    for human_input in exchanges:
        response = with_history.invoke({"input": human_input}, config=config)
        print(f"\n   Human: {human_input}")
        print(f"   AI: {response[:150]}...")

    print(f"\n✅ Messages stored automatically in session '{session_id}'")
    print(f"   History length: {len(store[session_id].messages)} messages")


def demo_message_trimming():
    """Demonstrate trimming old messages to manage context window."""
    print("\n" + "="*60)
    print("DEMO 4: Message Trimming (Managing Context Window)")
    print("="*60)

    if not HAS_LANGCHAIN:
        print("⚠️  LangChain required")
        return

    print("""
Message Trimming Strategies:

When conversations get too long, you need to trim old messages
to fit within the model's context window.

┌────────────────────────────────────────────────────────────┐
│ Strategy         │ How it works                            │
├────────────────────────────────────────────────────────────┤
│ Keep Last K      │ Only keep the most recent K messages    │
│ Keep First + Last│ System msg + last K messages            │
│ Token-based      │ Keep messages until token budget        │
│ Summarize Old    │ Summarize old messages, keep recent     │
└────────────────────────────────────────────────────────────┘
    """)

    # Demonstrate keep-last-K strategy
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Message 1"),
        AIMessage(content="Response 1"),
        HumanMessage(content="Message 2"),
        AIMessage(content="Response 2"),
        HumanMessage(content="Message 3"),
        AIMessage(content="Response 3"),
        HumanMessage(content="Message 4"),
        AIMessage(content="Response 4"),
    ]

    def trim_messages(messages: list, max_messages: int = 5) -> list:
        """Keep system message + last N messages."""
        system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
        other_msgs = [m for m in messages if not isinstance(m, SystemMessage)]

        # Keep system message + last N
        return system_msgs + other_msgs[-(max_messages - len(system_msgs)):]

    print(f"\n📝 Before trimming: {len(messages)} messages")
    for msg in messages:
        prefix = "🤖" if isinstance(msg, AIMessage) else "👤" if isinstance(msg, HumanMessage) else "⚙️"
        print(f"   {prefix} {msg.content[:30]}...")

    trimmed = trim_messages(messages, max_messages=5)

    print(f"\n📝 After trimming (keep 5): {len(trimmed)} messages")
    for msg in trimmed:
        prefix = "🤖" if isinstance(msg, AIMessage) else "👤" if isinstance(msg, HumanMessage) else "⚙️"
        print(f"   {prefix} {msg.content[:30]}...")


def demo_memory_comparison():
    """Compare different memory strategies."""
    print("\n" + "="*60)
    print("DEMO 5: Memory Strategy Comparison")
    print("="*60)

    print("""
Memory Strategy Comparison:

┌────────────────────────┬─────────────┬─────────────┬──────────────┐
│ Strategy               │ Token Usage │ Recall      │ Best For     │
├────────────────────────┼─────────────┼─────────────┼──────────────┤
│ Keep All Messages      │ High        │ Perfect     │ Short convos │
│ Keep Last K (k=5)      │ Medium      │ Recent only │ Chatbots     │
│ Summarize Old          │ Low         │ Compressed  │ Long convos  │
│ Summary + Recent       │ Medium      │ Balanced    │ Most apps    │
└────────────────────────┴─────────────┴─────────────┴──────────────┘

Example after 50 exchanges:

Keep All Messages:
  - Stores: All 50 exchanges verbatim
  - Tokens: ~5,000-10,000
  - Risk: May exceed context window!

Keep Last K (k=5):
  - Stores: Last 5 exchanges only
  - Tokens: ~500-1,000
  - Risk: Forgets important early context

Summarize Old:
  - Stores: "User Alice (Python dev, London) discussed learning ML..."
  - Tokens: ~100-300
  - Risk: May lose important details

Summary + Recent (Best for most cases):
  - Stores: Summary + last 3 exchanges
  - Tokens: ~400-700
  - Best balance for most applications!

Implementation in LangChain 1.1.0+:
  - Use RunnableWithMessageHistory for automatic history
  - Implement custom trimming/summarization logic
  - Use langchain-community for more memory options
    """)


def demo_multiple_sessions():
    """Demonstrate managing multiple conversation sessions."""
    print("\n" + "="*60)
    print("DEMO 6: Multiple Sessions")
    print("="*60)

    if not HAS_LANGCHAIN or not LLM:
        print("⚠️  LangChain and API key required")
        return

    print(f"\n🤖 Using: {LLM_NAME}")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Be concise."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | LLM | StrOutputParser()

    # Multi-session store
    store: Dict[str, InMemoryChatMessageHistory] = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    print("\n📤 Managing multiple concurrent sessions:")

    # User 1 session
    response1 = with_history.invoke(
        {"input": "My name is Alice"},
        config={"configurable": {"session_id": "user_alice"}}
    )
    print(f"\n   [Session: user_alice]")
    print(f"   Human: My name is Alice")
    print(f"   AI: {response1[:80]}...")

    # User 2 session
    response2 = with_history.invoke(
        {"input": "My name is Bob"},
        config={"configurable": {"session_id": "user_bob"}}
    )
    print(f"\n   [Session: user_bob]")
    print(f"   Human: My name is Bob")
    print(f"   AI: {response2[:80]}...")

    # Back to User 1 - should remember Alice!
    response3 = with_history.invoke(
        {"input": "What's my name?"},
        config={"configurable": {"session_id": "user_alice"}}
    )
    print(f"\n   [Session: user_alice]")
    print(f"   Human: What's my name?")
    print(f"   AI: {response3[:80]}...")

    print(f"\n✅ Each session maintains separate history!")
    print(f"   Sessions active: {list(store.keys())}")


def main():
    """Run all demos."""
    print("="*60)
    print("LangChain Memory Systems (1.1.0+)")
    print("="*60)
    print("""
Memory gives LLMs the ability to "remember" conversations.

Without memory: Each API call is independent
With memory: Previous context is included in each request

Modern approach (LangChain 1.1.0+):
- Use RunnableWithMessageHistory for automatic memory
- Implement custom trimming for long conversations
- Support multiple concurrent sessions
    """)

    demo_stateless_problem()
    demo_manual_message_history()
    demo_runnable_with_message_history()
    demo_message_trimming()
    demo_memory_comparison()
    demo_multiple_sessions()

    print("\n" + "="*60)
    print("✅ Memory Systems Demo Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
