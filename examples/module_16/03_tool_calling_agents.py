#!/usr/bin/env python3
"""
Module 16, Example 3: Tool-Calling Agents

This example demonstrates creating agents that use tools:
1. Basic tool-calling agent with AgentExecutor
2. Agent with memory for conversations
3. Streaming agent output
4. Debugging and observability
5. Custom agent behavior

Usage:
    # Requires GOOGLE_API_KEY (Gemini) or ANTHROPIC_API_KEY (Claude)
    export GOOGLE_API_KEY="your-key"
    python 03_tool_calling_agents.py

    # Or use Claude
    export ANTHROPIC_API_KEY="your-key"
    python 03_tool_calling_agents.py --provider anthropic
"""

import os
import sys
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression.

    Use this for any math calculations: addition, subtraction,
    multiplication, division, powers, etc.

    Args:
        expression: Math expression like "2 + 2" or "15 * 7"

    Returns:
        The calculated result.
    """
    try:
        # Safety check
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "Error: Only numbers and basic operators allowed"
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time.

    Use this when the user asks about the current time,
    today's date, or what day it is.

    Args:
        timezone: Timezone name (currently only UTC supported)

    Returns:
        Current date and time.
    """
    now = datetime.utcnow()
    return f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def get_weather(location: str) -> str:
    """Get weather for a location (simulated).

    Use when user asks about weather, temperature,
    or conditions for a specific place.

    Args:
        location: City name like "Tokyo" or "New York"

    Returns:
        Weather information (simulated).
    """
    # Simulated data
    weather_data = {
        "tokyo": "18°C, Partly Cloudy",
        "new york": "22°C, Sunny",
        "london": "14°C, Rainy",
        "paris": "16°C, Cloudy",
    }
    conditions = weather_data.get(location.lower(), "20°C, Clear")
    return f"Weather in {location}: {conditions}"


@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for information.

    Use this for general knowledge questions,
    facts, or when you need to look something up.

    Args:
        query: The search query

    Returns:
        Relevant information (simulated).
    """
    # Simulated knowledge base
    knowledge = {
        "python": "Python is a high-level programming language created by Guido van Rossum in 1991. It emphasizes code readability and supports multiple programming paradigms.",
        "langchain": "LangChain is a framework for developing applications powered by language models. Created by Harrison Chase in 2022, it raised $200M within 14 months.",
        "agents": "AI agents are systems that use LLMs to reason and take actions. They use tools to interact with external systems and accomplish tasks.",
        "function calling": "Function calling allows LLMs to output structured data to invoke external functions. Released by OpenAI in June 2023.",
    }

    query_lower = query.lower()
    for key, info in knowledge.items():
        if key in query_lower:
            return info

    return f"No specific information found for '{query}'. Try a more specific search term."


# Collect all tools
TOOLS = [calculator, get_current_time, get_weather, search_knowledge_base]


# ============================================================================
# AGENT CREATION
# ============================================================================

def get_llm(provider: str = "google"):
    """Get the appropriate LLM based on provider."""
    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not set")
            return None
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            api_key=api_key
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not set")
            return None
        return ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0,
            api_key=api_key
        )
    else:
        print(f"❌ Unknown provider: {provider}")
        return None


def create_basic_agent(provider: str = "google"):
    """Create a basic tool-calling agent."""
    from langchain.agents import create_tool_calling_agent, AgentExecutor

    llm = get_llm(provider)
    if not llm:
        return None

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant with access to tools.

When answering questions:
1. Think about which tool(s) would help answer the question
2. Use tools when they would provide accurate information
3. Combine information from multiple tools if needed
4. Be concise but complete in your final answer

Available tools: calculator, get_current_time, get_weather, search_knowledge_base"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create the agent
    agent = create_tool_calling_agent(llm, TOOLS, prompt)

    # Create executor with settings
    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,  # Show reasoning
        max_iterations=5,  # Prevent infinite loops
        handle_parsing_errors=True,  # Handle malformed outputs
        return_intermediate_steps=True  # Include tool calls in response
    )

    return executor


def create_conversational_agent(provider: str = "google"):
    """Create an agent with conversation memory."""
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain_core.chat_history import InMemoryChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory

    llm = get_llm(provider)
    if not llm:
        return None

    # Prompt with conversation history
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant with access to tools.
You remember previous messages in the conversation.

When answering:
1. Consider context from earlier in the conversation
2. Use tools when needed for accurate information
3. Reference previous answers when relevant"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create agent and executor
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=5,
    )

    # Add memory
    message_history = InMemoryChatMessageHistory()

    agent_with_memory = RunnableWithMessageHistory(
        executor,
        lambda session_id: message_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return agent_with_memory, message_history


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_basic_agent(provider: str = "google"):
    """Demonstrate basic agent with tools."""
    print("\n" + "="*60)
    print("🤖 BASIC TOOL-CALLING AGENT DEMO")
    print("="*60)

    agent = create_basic_agent(provider)
    if not agent:
        print("⚠️ Could not create agent (missing API key)")
        return

    # Test queries that require tools
    queries = [
        "What is 15 multiplied by 27?",
        "What's the weather like in Tokyo?",
        "What time is it right now?",
        "What is LangChain?",
    ]

    for query in queries:
        print(f"\n{'─'*60}")
        print(f"📝 Query: {query}")
        print('─'*60)

        try:
            result = agent.invoke({"input": query})
            print(f"\n✅ Answer: {result['output']}")

            # Show intermediate steps
            if result.get('intermediate_steps'):
                print("\n📊 Tools Used:")
                for step in result['intermediate_steps']:
                    action, output = step
                    print(f"   - {action.tool}({action.tool_input}) → {output[:50]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def demo_multi_tool_query(provider: str = "google"):
    """Demonstrate agent using multiple tools."""
    print("\n" + "="*60)
    print("🔧 MULTI-TOOL QUERY DEMO")
    print("="*60)

    agent = create_basic_agent(provider)
    if not agent:
        print("⚠️ Could not create agent (missing API key)")
        return

    # Complex query requiring multiple tools
    query = """I'm planning a trip to Tokyo. Can you tell me:
    1. What's the weather there?
    2. What time is it?
    3. If I have $500 and the exchange rate is 150 yen per dollar, how many yen is that?"""

    print(f"\n📝 Complex Query: {query}")
    print('─'*60)

    try:
        result = agent.invoke({"input": query})
        print(f"\n✅ Answer:\n{result['output']}")

        if result.get('intermediate_steps'):
            print(f"\n📊 Used {len(result['intermediate_steps'])} tool calls")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def demo_conversational_agent(provider: str = "google"):
    """Demonstrate agent with memory."""
    print("\n" + "="*60)
    print("💬 CONVERSATIONAL AGENT DEMO")
    print("="*60)

    result = create_conversational_agent(provider)
    if not result:
        print("⚠️ Could not create agent (missing API key)")
        return

    agent, history = result

    # Conversation with context
    conversation = [
        "What's 100 plus 50?",
        "Now multiply that result by 2",
        "What's the weather in London?",
        "What about Tokyo? Is it warmer there?",
    ]

    session_id = "demo-session"

    for message in conversation:
        print(f"\n{'─'*60}")
        print(f"👤 User: {message}")
        print('─'*60)

        try:
            result = agent.invoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}}
            )
            print(f"🤖 Assistant: {result['output']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def demo_without_api():
    """Demo showing tool schemas without API calls."""
    print("\n" + "="*60)
    print("📋 TOOL SCHEMAS (No API Required)")
    print("="*60)

    print("\nThese tools are available to the agent:\n")

    for tool_obj in TOOLS:
        print(f"📦 {tool_obj.name}")
        print(f"   {tool_obj.description.split('.')[0]}.")
        if tool_obj.args_schema:
            schema = tool_obj.args_schema.model_json_schema()
            props = schema.get('properties', {})
            if props:
                print(f"   Parameters:")
                for name, info in props.items():
                    desc = info.get('description', 'No description')[:50]
                    print(f"     - {name}: {desc}")
        print()

    print("""
When the agent receives a query like "What's 15 * 7?":

1. 📝 Agent sees the query and available tools
2. 🤔 Agent reasons: "This is a math question, I should use calculator"
3. 📤 Agent outputs: {"tool": "calculator", "args": {"expression": "15 * 7"}}
4. ⚙️  AgentExecutor runs: calculator("15 * 7") → "Result: 105"
5. 📥 Agent receives result and formulates answer
6. ✅ User sees: "15 multiplied by 7 equals 105"

This is the agent loop - think, act, observe, repeat!
""")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("="*60)
    print("🤖 Tool-Calling Agents - Module 16, Example 3")
    print("="*60)

    # Check for provider flag
    provider = "google"
    if "--provider" in sys.argv:
        idx = sys.argv.index("--provider")
        if idx + 1 < len(sys.argv):
            provider = sys.argv[idx + 1]

    print(f"\n📡 Using provider: {provider}")

    # Check for API key
    if provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print(f"\n⚠️ No API key found for {provider}")
        print("Running demo without API calls...\n")
        demo_without_api()
        print("\nTo run full demos:")
        print("  export GOOGLE_API_KEY='your-key'")
        print("  python 03_tool_calling_agents.py")
        print("\nOr use Anthropic:")
        print("  export ANTHROPIC_API_KEY='your-key'")
        print("  python 03_tool_calling_agents.py --provider anthropic")
        return

    # Run demos
    demo_basic_agent(provider)
    demo_multi_tool_query(provider)
    demo_conversational_agent(provider)

    # Summary
    print("\n" + "="*60)
    print("📚 KEY TAKEAWAYS")
    print("="*60)
    print("""
    1. AGENT COMPONENTS
       - LLM: The "brain" that decides what to do
       - Tools: Functions the agent can call
       - Prompt: Instructions for the agent
       - Executor: Runs the agent loop

    2. THE AGENT LOOP
       Think → Act → Observe → Repeat

    3. VERBOSE MODE
       - Set verbose=True to see reasoning
       - return_intermediate_steps shows all tool calls
       - Essential for debugging

    4. ERROR HANDLING
       - max_iterations prevents infinite loops
       - handle_parsing_errors catches malformed outputs
       - Tools should return helpful error messages

    5. MEMORY
       - Use RunnableWithMessageHistory for conversations
       - Agent remembers previous exchanges
       - Essential for multi-turn interactions
    """)


if __name__ == "__main__":
    main()
