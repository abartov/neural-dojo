#!/usr/bin/env python3
"""
Module 17, Example 2: ReAct Pattern Implementation

ReAct (Reasoning + Acting) combines chain-of-thought reasoning with
the ability to take actions (use tools). This is the foundation of
modern AI agents.

The pattern: Thought → Action → Observation → Repeat

This example demonstrates:
1. The ReAct prompt format
2. Manual ReAct loop implementation
3. ReAct with LangChain agents
4. Comparing ReAct to pure reasoning

Usage:
    export GOOGLE_API_KEY="your-key"
    python 02_react_pattern.py

Author: Neural Dojo - Module 17
"""

import os
import sys
import re
import math
from typing import Optional, Dict, Any, Callable, Tuple
from datetime import datetime

# Check for API key
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")


def get_llm():
    """Get the appropriate LLM based on available API key."""
    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
        )
    elif os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0,
        )
    return None


# ============================================================================
# TOOLS FOR REACT AGENT
# ============================================================================

def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Only allow safe operations
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return f"Error: Invalid characters in expression"

        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def search_knowledge(query: str) -> str:
    """Simulated knowledge base search."""
    knowledge = {
        "population france": "France has a population of approximately 67.75 million (2023).",
        "population germany": "Germany has a population of approximately 84.4 million (2023).",
        "population japan": "Japan has a population of approximately 125 million (2023).",
        "capital france": "The capital of France is Paris.",
        "capital germany": "The capital of Germany is Berlin.",
        "capital japan": "The capital of Japan is Tokyo.",
        "eiffel tower height": "The Eiffel Tower is 330 meters (1,083 feet) tall.",
        "speed of light": "The speed of light is approximately 299,792,458 meters per second.",
        "earth radius": "Earth's radius is approximately 6,371 kilometers.",
        "pi value": "Pi (π) is approximately 3.14159265359.",
    }

    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower or all(word in query_lower for word in key.split()):
            return value

    return f"No information found for: {query}"


def get_current_date() -> str:
    """Get the current date."""
    return datetime.now().strftime("%Y-%m-%d")


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units."""
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("kg", "pounds"): lambda x: x * 2.20462,
        ("pounds", "kg"): lambda x: x * 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    return f"Unknown conversion: {from_unit} to {to_unit}"


# Tool registry
TOOLS = {
    "calculate": {
        "func": calculate,
        "description": "Evaluate a mathematical expression. Example: calculate(15 * 7 + 3)"
    },
    "search": {
        "func": search_knowledge,
        "description": "Search for factual information. Example: search(population of France)"
    },
    "date": {
        "func": lambda: get_current_date(),
        "description": "Get the current date. Example: date()"
    },
    "convert": {
        "func": lambda args: convert_units(*eval(args)) if args else "Error: need value, from_unit, to_unit",
        "description": "Convert units. Example: convert(100, km, miles)"
    },
}


# ============================================================================
# REACT IMPLEMENTATION
# ============================================================================

REACT_PROMPT_TEMPLATE = """You are an assistant that uses tools to answer questions.

Available tools:
{tool_descriptions}

Use this EXACT format:

Question: [the question you're answering]
Thought: [your reasoning about what to do next]
Action: [tool_name(arguments)]
Observation: [result from the tool - I will fill this in]
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information to answer.
Final Answer: [your final answer to the question]

IMPORTANT:
- Always start with a Thought
- Each Action must be on its own line
- Wait for Observation before continuing
- End with "Final Answer:" when done

Begin!

Question: {question}
Thought:"""


def format_tool_descriptions() -> str:
    """Format tool descriptions for the prompt."""
    lines = []
    for name, info in TOOLS.items():
        lines.append(f"- {name}: {info['description']}")
    return "\n".join(lines)


def parse_action(text: str) -> Optional[Tuple[str, str]]:
    """Parse an Action line from the response."""
    # Look for Action: tool_name(arguments) pattern
    patterns = [
        r'Action:\s*(\w+)\(([^)]*)\)',
        r'Action:\s*(\w+)\((.*?)\)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            tool_name = match.group(1).lower()
            args = match.group(2).strip()
            return tool_name, args

    return None


def execute_tool(tool_name: str, args: str) -> str:
    """Execute a tool and return the result."""
    if tool_name not in TOOLS:
        return f"Unknown tool: {tool_name}. Available: {', '.join(TOOLS.keys())}"

    tool = TOOLS[tool_name]
    try:
        if tool_name == "date":
            return tool["func"]()
        elif tool_name == "convert":
            # Parse convert arguments: value, from_unit, to_unit
            parts = [p.strip().strip('"\'') for p in args.split(",")]
            if len(parts) == 3:
                return convert_units(float(parts[0]), parts[1], parts[2])
            return "Error: convert needs 3 arguments (value, from_unit, to_unit)"
        else:
            return tool["func"](args)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"


def react_loop(question: str, max_iterations: int = 5, verbose: bool = True) -> str:
    """Execute the ReAct loop."""
    if not API_KEY:
        return "No API key available"

    llm = get_llm()
    if not llm:
        return "Could not initialize LLM"

    # Build initial prompt
    prompt = REACT_PROMPT_TEMPLATE.format(
        tool_descriptions=format_tool_descriptions(),
        question=question
    )

    conversation = prompt

    for i in range(max_iterations):
        if verbose:
            print(f"\n--- Iteration {i+1} ---")

        # Get LLM response
        response = llm.invoke(conversation).content

        if verbose:
            print(f"LLM: {response[:300]}..." if len(response) > 300 else f"LLM: {response}")

        # Check for final answer
        if "Final Answer:" in response:
            match = re.search(r'Final Answer:\s*(.+?)(?:\n|$)', response, re.DOTALL)
            if match:
                return match.group(1).strip()
            # If no match but Final Answer exists, return everything after it
            idx = response.find("Final Answer:")
            return response[idx + 13:].strip()

        # Parse and execute action
        action = parse_action(response)
        if action:
            tool_name, args = action
            observation = execute_tool(tool_name, args)

            if verbose:
                print(f"Action: {tool_name}({args})")
                print(f"Observation: {observation}")

            # Add to conversation
            conversation += response + f"\nObservation: {observation}\nThought:"
        else:
            # No action found, add response and prompt for more
            conversation += response + "\nThought:"

    return "Max iterations reached without final answer"


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_react_format():
    """Show the ReAct prompt format."""
    print("\n" + "="*70)
    print("📝 DEMO: ReAct Prompt Format")
    print("="*70)

    print("""
The ReAct pattern interleaves Thinking and Acting:

┌─────────────────────────────────────────────────────────────┐
│  REACT PATTERN                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Question: What is the population of France divided by 3?   │
│                                                             │
│  Thought: I need to find France's population first.         │
│  Action: search(population of France)                       │
│  Observation: France has a population of 67.75 million.     │
│                                                             │
│  Thought: Now I need to divide 67.75 million by 3.          │
│  Action: calculate(67750000 / 3)                            │
│  Observation: 22583333.333333332                            │
│                                                             │
│  Thought: I have the answer now.                            │
│  Final Answer: France's population divided by 3 is          │
│                approximately 22.58 million.                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
    """)

    print("\n📦 Available Tools:")
    for name, info in TOOLS.items():
        print(f"   • {name}: {info['description']}")


def demo_manual_react():
    """Demonstrate manual ReAct execution."""
    print("\n" + "="*70)
    print("🔧 DEMO: Manual ReAct Loop")
    print("="*70)

    questions = [
        "What is the population of France divided by 2?",
        "How tall is the Eiffel Tower in feet?",
        "What is 15 * 7 + 23?",
    ]

    if not API_KEY:
        print("\n⚠️ No API key found. Showing what would happen:\n")

        for q in questions:
            print(f"\n📝 Question: {q}")
            print("   The ReAct agent would:")
            print("   1. Think about what information is needed")
            print("   2. Use search() or calculate() tools")
            print("   3. Observe the results")
            print("   4. Repeat until it has enough info")
            print("   5. Provide Final Answer")
        return

    for question in questions:
        print(f"\n{'─'*70}")
        print(f"📝 Question: {question}")
        print("─"*70)

        answer = react_loop(question, max_iterations=5, verbose=True)

        print(f"\n✅ Final Answer: {answer}")


def demo_react_vs_direct():
    """Compare ReAct to direct prompting."""
    print("\n" + "="*70)
    print("⚔️ DEMO: ReAct vs Direct Prompting")
    print("="*70)

    question = "What is the height of the Eiffel Tower converted to feet, then multiplied by 2?"

    print(f"\n📝 Question: {question}")

    if not API_KEY:
        print("\n⚠️ No API key. Showing comparison concept:\n")
        print("DIRECT PROMPTING:")
        print("   - Model must know Eiffel Tower height from training")
        print("   - Model must calculate conversion in 'head'")
        print("   - Prone to errors and hallucination")
        print("\nREACT APPROACH:")
        print("   - Search for accurate Eiffel Tower height")
        print("   - Use calculator for conversion")
        print("   - Each step verified by real tools")
        return

    llm = get_llm()

    # Direct prompting
    print("\n📌 DIRECT PROMPTING:")
    direct_prompt = f"Answer this question: {question}"
    direct_response = llm.invoke(direct_prompt).content
    print(f"   Response: {direct_response[:200]}...")

    # ReAct
    print("\n🔗 REACT APPROACH:")
    react_answer = react_loop(question, verbose=True)
    print(f"\n   Final: {react_answer}")


def demo_langchain_react():
    """Demonstrate ReAct with LangChain's built-in agent."""
    print("\n" + "="*70)
    print("🦜 DEMO: LangChain ReAct Agent")
    print("="*70)

    if not API_KEY:
        print("\n⚠️ No API key. Showing LangChain ReAct setup:\n")
        print("""
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain import hub

# Define tools
@tool
def search(query: str) -> str:
    '''Search for information.'''
    return search_knowledge(query)

@tool
def calculator(expression: str) -> str:
    '''Calculate a math expression.'''
    return calculate(expression)

# Create ReAct agent
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, [search, calculator], prompt)
executor = AgentExecutor(agent=agent, tools=[search, calculator])

# Run
result = executor.invoke({"input": "What is 15 * 7?"})
        """)
        return

    try:
        from langchain_core.tools import tool as lc_tool
        from langchain.agents import create_react_agent, AgentExecutor
        from langchain_core.prompts import PromptTemplate

        llm = get_llm()

        # Define tools
        @lc_tool
        def search_tool(query: str) -> str:
            """Search for factual information about countries, landmarks, or science facts."""
            return search_knowledge(query)

        @lc_tool
        def calculator_tool(expression: str) -> str:
            """Calculate a mathematical expression like '15 * 7 + 3'."""
            return calculate(expression)

        tools = [search_tool, calculator_tool]

        # ReAct prompt
        react_prompt = PromptTemplate.from_template("""Answer the following question using the available tools.

You have access to these tools:
{tools}

Use this format:

Question: the input question
Thought: think about what to do
Action: the action to take, one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer

Begin!

Question: {input}
Thought: {agent_scratchpad}""")

        # Create agent
        agent = create_react_agent(llm, tools, react_prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )

        print("\n📝 Running LangChain ReAct agent...")
        print("─"*50)

        result = executor.invoke({"input": "What is the population of Japan divided by 5?"})

        print("─"*50)
        print(f"\n✅ Final Answer: {result['output']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   (This demo requires langchain with ReAct support)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("="*70)
    print("🔄 ReAct Pattern - Module 17, Example 2")
    print("="*70)
    print("""
    ReAct = Reasoning + Acting

    The key insight: Combine thinking (chain-of-thought) with
    doing (tool use) for more capable AI agents.

    Pattern: Thought → Action → Observation → Repeat

    This is the foundation of modern AI agents!
    """)

    if not API_KEY:
        print("⚠️ No API key found.")
        print("   Set GOOGLE_API_KEY or ANTHROPIC_API_KEY for full demos.")
        print("   Running in example mode...\n")

    # Run demos
    demo_react_format()
    demo_manual_react()
    demo_react_vs_direct()
    demo_langchain_react()

    # Summary
    print("\n" + "="*70)
    print("📚 KEY TAKEAWAYS")
    print("="*70)
    print("""
    1. REACT COMBINES REASONING AND ACTING
       - Think about what info is needed
       - Take action to get that info
       - Observe results
       - Reason about what to do next

    2. ADVANTAGES OVER PURE COT
       - Can gather information it doesn't have
       - Verifies facts rather than hallucinating
       - Uses tools for accurate calculations
       - Adapts based on observations

    3. THE REACT LOOP
       Thought → Action → Observation → (repeat) → Final Answer

    4. LANGCHAIN SUPPORT
       - create_react_agent() for built-in ReAct
       - AgentExecutor handles the loop
       - Integrates with any LangChain tools

    5. BEST PRACTICES
       - Clear tool descriptions
       - Handle tool errors gracefully
       - Limit iterations to prevent loops
       - Verbose mode for debugging

    🔮 ReAct is the foundation of AI agents like Claude Code!
    """)


if __name__ == "__main__":
    main()
