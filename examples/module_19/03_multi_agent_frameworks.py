#!/usr/bin/env python3
"""
Module 19, Example 3: Multi-Agent Frameworks

This example demonstrates:
1. CrewAI - Role-based agent teams
2. AutoGen - Conversational multi-agent systems
3. Comparison of multi-agent approaches
4. When to use each framework

Multi-agent systems enable complex collaborative AI workflows.

Usage:
    python 03_multi_agent_frameworks.py

Note: This example shows concepts and simulated implementations.
      For real usage, install: pip install crewai autogen
"""

import os
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time

# Check for frameworks
CREWAI_AVAILABLE = False
AUTOGEN_AVAILABLE = False

try:
    import crewai
    CREWAI_AVAILABLE = True
except ImportError:
    pass

try:
    import autogen
    AUTOGEN_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Simulated Multi-Agent Framework
# =============================================================================

class AgentRole(str, Enum):
    """Predefined agent roles."""
    RESEARCHER = "researcher"
    WRITER = "writer"
    REVIEWER = "reviewer"
    ANALYST = "analyst"
    CODER = "coder"
    MANAGER = "manager"


@dataclass
class SimulatedAgent:
    """Simulated agent for demonstration."""
    name: str
    role: AgentRole
    goal: str
    backstory: str
    tools: List[str] = field(default_factory=list)

    def execute(self, task: str) -> str:
        """Simulate task execution."""
        time.sleep(0.1)  # Simulate work
        return f"[{self.name}] Completed: {task[:50]}... (Role: {self.role.value})"


@dataclass
class SimulatedTask:
    """Simulated task for demonstration."""
    description: str
    agent: SimulatedAgent
    expected_output: str
    context: List["SimulatedTask"] = field(default_factory=list)

    def run(self) -> str:
        """Execute the task."""
        context_info = ""
        if self.context:
            context_info = f" (with context from {len(self.context)} previous tasks)"
        return self.agent.execute(self.description + context_info)


class SimulatedCrew:
    """Simulated CrewAI-style crew."""

    def __init__(self, agents: List[SimulatedAgent], tasks: List[SimulatedTask],
                 process: str = "sequential"):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.results = []

    def kickoff(self) -> Dict[str, Any]:
        """Run the crew."""
        print(f"\n  Starting crew with {len(self.agents)} agents, {len(self.tasks)} tasks")
        print(f"  Process: {self.process}")
        print("-" * 40)

        for i, task in enumerate(self.tasks, 1):
            print(f"\n  Task {i}: {task.description[:40]}...")
            result = task.run()
            self.results.append(result)
            print(f"    {result}")

        return {
            "status": "completed",
            "results": self.results,
            "process": self.process
        }


# =============================================================================
# Part 1: CrewAI Concepts
# =============================================================================

def demo_crewai_concepts():
    """Demonstrate CrewAI concepts and patterns."""
    print("\n" + "="*60)
    print("Part 1: CrewAI - Role-Based Agent Teams")
    print("="*60)

    print("""
    CrewAI Philosophy:
    ─────────────────
    • Agents have ROLES (like job titles)
    • Agents have GOALS (what they aim to achieve)
    • Agents have BACKSTORY (expertise and personality)
    • Tasks are assigned to specific agents
    • Crews orchestrate agent collaboration

    Mental Model: Think of it like a human team!
    """)

    # Create agents
    researcher = SimulatedAgent(
        name="Alex",
        role=AgentRole.RESEARCHER,
        goal="Find comprehensive, accurate information",
        backstory="Senior research analyst with 10 years experience in data gathering",
        tools=["web_search", "document_reader"]
    )

    writer = SimulatedAgent(
        name="Jordan",
        role=AgentRole.WRITER,
        goal="Create clear, engaging content",
        backstory="Technical writer specializing in making complex topics accessible",
        tools=["text_editor"]
    )

    reviewer = SimulatedAgent(
        name="Sam",
        role=AgentRole.REVIEWER,
        goal="Ensure quality and accuracy",
        backstory="Editor with keen eye for errors and improvements",
        tools=["grammar_checker"]
    )

    print("\n  Created Agents:")
    for agent in [researcher, writer, reviewer]:
        print(f"    • {agent.name} ({agent.role.value})")
        print(f"      Goal: {agent.goal}")
        print(f"      Tools: {agent.tools}")

    # Create tasks
    research_task = SimulatedTask(
        description="Research the latest developments in AI multi-agent systems",
        agent=researcher,
        expected_output="Comprehensive research notes with sources"
    )

    writing_task = SimulatedTask(
        description="Write a blog post based on the research findings",
        agent=writer,
        expected_output="1500-word blog post in markdown",
        context=[research_task]
    )

    review_task = SimulatedTask(
        description="Review and improve the blog post for clarity and accuracy",
        agent=reviewer,
        expected_output="Edited blog post with suggestions",
        context=[writing_task]
    )

    print("\n  Created Tasks:")
    for task in [research_task, writing_task, review_task]:
        ctx = f" (depends on previous)" if task.context else ""
        print(f"    • {task.description[:50]}...{ctx}")
        print(f"      Assigned to: {task.agent.name}")

    # Run crew
    crew = SimulatedCrew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        process="sequential"
    )

    result = crew.kickoff()

    print(f"\n  Crew completed: {result['status']}")


def demo_crewai_code():
    """Show actual CrewAI code structure."""
    print("\n" + "="*60)
    print("Part 2: CrewAI Code Example")
    print("="*60)

    print("""
    Actual CrewAI Code:
    ───────────────────

    from crewai import Agent, Task, Crew, Process

    # Define agents with roles
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Find comprehensive information about AI frameworks",
        backstory="Expert at finding and analyzing technical information.",
        tools=[search_tool, web_scraper],
        verbose=True
    )

    writer = Agent(
        role="Technical Writer",
        goal="Create clear, engaging technical content",
        backstory="Specializes in making complex topics accessible.",
        verbose=True
    )

    # Define tasks
    research_task = Task(
        description="Research the latest AI framework developments",
        agent=researcher,
        expected_output="Comprehensive research notes with sources"
    )

    writing_task = Task(
        description="Write a blog post based on the research",
        agent=writer,
        expected_output="1500-word blog post in markdown",
        context=[research_task]  # Uses research output
    )

    # Create and run crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential  # or Process.hierarchical
    )

    result = crew.kickoff()


    Key CrewAI Features:
    ────────────────────
    1. Role-based agents (like job descriptions)
    2. Task dependencies via context
    3. Sequential or hierarchical processes
    4. Built-in memory and delegation
    5. Tool integration per agent
    """)


# =============================================================================
# Part 3: AutoGen Concepts
# =============================================================================

def demo_autogen_concepts():
    """Demonstrate AutoGen concepts and patterns."""
    print("\n" + "="*60)
    print("Part 3: AutoGen - Conversational Agents")
    print("="*60)

    print("""
    AutoGen Philosophy:
    ───────────────────
    • Agents CONVERSE with each other
    • Messages are the primary interface
    • Human-in-the-loop is native
    • Code execution is built-in
    • Research-focused design

    Mental Model: Agents having a group chat!
    """)

    # Simulated AutoGen-style conversation
    print("\n  Simulated AutoGen Conversation:")
    print("-" * 40)

    conversation = [
        {"agent": "User", "message": "Create a Python function to calculate fibonacci numbers"},
        {"agent": "Assistant", "message": "I'll create an efficient fibonacci function using memoization."},
        {"agent": "Coder", "message": """Here's the implementation:
```python
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]
```"""},
        {"agent": "Critic", "message": "The code looks good! Consider adding type hints and docstring."},
        {"agent": "Coder", "message": """Updated version:
```python
def fibonacci(n: int, memo: dict = {}) -> int:
    \"\"\"Calculate fibonacci number using memoization.\"\"\"
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]
```"""},
        {"agent": "User", "message": "TERMINATE"}
    ]

    for msg in conversation:
        print(f"\n  [{msg['agent']}]:")
        for line in msg['message'].split('\n'):
            print(f"    {line}")


def demo_autogen_code():
    """Show actual AutoGen code structure."""
    print("\n" + "="*60)
    print("Part 4: AutoGen Code Example")
    print("="*60)

    print("""
    Actual AutoGen Code:
    ────────────────────

    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

    # Create agents
    assistant = AssistantAgent(
        name="assistant",
        llm_config={"model": "gpt-4"},
        system_message="You are a helpful AI assistant."
    )

    coder = AssistantAgent(
        name="coder",
        llm_config={"model": "gpt-4"},
        system_message="You write Python code to solve problems."
    )

    critic = AssistantAgent(
        name="critic",
        llm_config={"model": "gpt-4"},
        system_message="You review code and suggest improvements."
    )

    # User proxy (human-in-the-loop)
    user_proxy = UserProxyAgent(
        name="user",
        human_input_mode="TERMINATE",  # or "ALWAYS", "NEVER"
        code_execution_config={"work_dir": "coding"}
    )

    # Group chat
    group_chat = GroupChat(
        agents=[user_proxy, assistant, coder, critic],
        messages=[],
        max_round=10
    )

    manager = GroupChatManager(groupchat=group_chat)

    # Start conversation
    user_proxy.initiate_chat(
        manager,
        message="Create a fibonacci function with tests"
    )


    Key AutoGen Features:
    ─────────────────────
    1. Conversational interface (chat-based)
    2. Built-in code execution sandbox
    3. Flexible human-in-the-loop modes
    4. Group chat orchestration
    5. Research-grade design (Microsoft)
    """)


# =============================================================================
# Part 5: Framework Comparison
# =============================================================================

def demo_comparison():
    """Compare CrewAI and AutoGen."""
    print("\n" + "="*60)
    print("Part 5: CrewAI vs AutoGen Comparison")
    print("="*60)

    print("""
    ┌─────────────────────────┬───────────────────┬───────────────────┐
    │ Aspect                  │ CrewAI            │ AutoGen           │
    ├─────────────────────────┼───────────────────┼───────────────────┤
    │ Mental Model            │ Team with roles   │ Group chat        │
    │ Agent Definition        │ Role + Goal       │ System message    │
    │ Task Assignment         │ Explicit          │ Dynamic           │
    │ Communication           │ Task handoff      │ Messages          │
    │ Human-in-the-Loop       │ Limited           │ First-class       │
    │ Code Execution          │ Via tools         │ Built-in sandbox  │
    │ Learning Curve          │ Lower             │ Higher            │
    │ Flexibility             │ Moderate          │ High              │
    │ Use Case Focus          │ Business teams    │ Research/coding   │
    │ Production Ready        │ Yes               │ Experimental      │
    └─────────────────────────┴───────────────────┴───────────────────┘


    When to Use CrewAI:
    ───────────────────
    • Modeling business processes
    • Clear role separation needed
    • Task-based workflows
    • Simpler setup requirements
    • Production applications

    When to Use AutoGen:
    ────────────────────
    • Research and experimentation
    • Code generation workflows
    • Complex multi-turn dialogues
    • Need agents to debate/critique
    • Heavy human interaction needed


    When to Use LangGraph Instead:
    ──────────────────────────────
    • Need precise control over flow
    • Complex state management
    • Custom orchestration logic
    • Integration with LangChain
    • Production reliability required
    """)


# =============================================================================
# Part 6: Other Frameworks Overview
# =============================================================================

def demo_other_frameworks():
    """Overview of other multi-agent frameworks."""
    print("\n" + "="*60)
    print("Part 6: Other Multi-Agent Frameworks")
    print("="*60)

    print("""
    Semantic Kernel (Microsoft):
    ────────────────────────────
    • Enterprise-focused, Azure integration
    • C# and Python support
    • Plugin architecture
    • Best for: Microsoft ecosystem

    import semantic_kernel as sk
    kernel = sk.Kernel()
    kernel.add_service(AzureChatCompletion(...))


    Haystack:
    ─────────
    • Search-first design
    • Pipeline architecture
    • Strong NLP focus
    • Best for: Search applications

    from haystack import Pipeline
    pipeline = Pipeline()
    pipeline.add_component("retriever", retriever)
    pipeline.add_component("generator", generator)


    DSPy (Stanford):
    ────────────────
    • Prompt optimization
    • Declarative approach
    • Research-focused
    • Best for: Prompt engineering research

    import dspy
    class QA(dspy.Signature):
        context = dspy.InputField()
        question = dspy.InputField()
        answer = dspy.OutputField()


    Swarm (OpenAI - Experimental):
    ──────────────────────────────
    • Lightweight multi-agent
    • Handoff-based routing
    • Very simple API
    • Best for: Quick prototypes

    from swarm import Agent, Swarm
    agent = Agent(name="Assistant", instructions="...")
    client = Swarm()
    response = client.run(agent=agent, messages=[...])
    """)


# =============================================================================
# Part 7: Decision Framework
# =============================================================================

def demo_decision_framework():
    """Present decision framework for multi-agent systems."""
    print("\n" + "="*60)
    print("Part 7: Multi-Agent Framework Selection")
    print("="*60)

    print("""
    Decision Tree:
    ─────────────

                    What's your multi-agent need?
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    Role-based            Chat-based           Custom control
    teams                 dialogue              workflows
        │                     │                     │
        ▼                     ▼                     ▼
      CrewAI               AutoGen              LangGraph
        │                     │                     │
    "Business              "Research           "Production
     process"              coding"              agents"


    Framework Selection Matrix:
    ───────────────────────────

    ┌────────────────────────┬──────────┬─────────┬───────────┐
    │ Requirement            │ CrewAI   │ AutoGen │ LangGraph │
    ├────────────────────────┼──────────┼─────────┼───────────┤
    │ Quick prototype        │ ✅ Best  │ ✅ Good │ ⚠️ More   │
    │ Production deployment  │ ✅ Good  │ ⚠️ Exp  │ ✅ Best   │
    │ Role-based agents      │ ✅ Best  │ ⚠️ OK   │ ✅ Good   │
    │ Code generation        │ ⚠️ OK    │ ✅ Best │ ✅ Good   │
    │ Human-in-the-loop      │ ⚠️ OK    │ ✅ Best │ ✅ Good   │
    │ State management       │ ⚠️ Basic │ ⚠️ Basic│ ✅ Best   │
    │ Custom workflows       │ ⚠️ Limited│ ⚠️ Limited│ ✅ Best │
    │ Learning curve         │ ✅ Low   │ ⚠️ Med  │ ⚠️ High  │
    └────────────────────────┴──────────┴─────────┴───────────┘


    Practical Recommendations:
    ──────────────────────────
    1. START with CrewAI for quick multi-agent prototypes
    2. USE AutoGen for research and code-heavy workflows
    3. MOVE TO LangGraph when you need production control
    4. COMBINE frameworks as needed (they're not exclusive)
    """)


# =============================================================================
# Part 8: Practical Example - Research Team
# =============================================================================

def demo_practical_example():
    """Show a practical multi-agent example."""
    print("\n" + "="*60)
    print("Part 8: Practical Example - Research Team")
    print("="*60)

    print("\n  Building a research team to analyze AI trends...")

    # Create specialized agents
    agents = [
        SimulatedAgent(
            name="Data Collector",
            role=AgentRole.RESEARCHER,
            goal="Gather data from multiple sources",
            backstory="Expert at finding and validating information sources",
            tools=["web_search", "api_caller", "document_reader"]
        ),
        SimulatedAgent(
            name="Data Analyst",
            role=AgentRole.ANALYST,
            goal="Analyze and synthesize findings",
            backstory="PhD in data science with pattern recognition expertise",
            tools=["data_analyzer", "chart_maker"]
        ),
        SimulatedAgent(
            name="Report Writer",
            role=AgentRole.WRITER,
            goal="Create comprehensive reports",
            backstory="Technical writer with journalism background",
            tools=["text_editor", "citation_manager"]
        ),
        SimulatedAgent(
            name="Quality Manager",
            role=AgentRole.MANAGER,
            goal="Ensure accuracy and completeness",
            backstory="Former editor with fact-checking expertise",
            tools=["fact_checker", "plagiarism_detector"]
        )
    ]

    # Create task pipeline
    tasks = [
        SimulatedTask(
            description="Collect data on AI framework adoption in 2024",
            agent=agents[0],
            expected_output="Raw data with sources"
        ),
        SimulatedTask(
            description="Analyze trends and patterns in the data",
            agent=agents[1],
            expected_output="Analysis with charts and insights"
        ),
        SimulatedTask(
            description="Write comprehensive trend report",
            agent=agents[2],
            expected_output="10-page report with executive summary"
        ),
        SimulatedTask(
            description="Review and fact-check the report",
            agent=agents[3],
            expected_output="Verified report ready for publication"
        )
    ]

    # Add dependencies
    tasks[1].context = [tasks[0]]
    tasks[2].context = [tasks[1]]
    tasks[3].context = [tasks[2]]

    # Run the crew
    crew = SimulatedCrew(
        agents=agents,
        tasks=tasks,
        process="sequential"
    )

    result = crew.kickoff()

    print(f"\n  Research team completed!")
    print(f"  Total tasks executed: {len(result['results'])}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*60)
    print("Module 19, Example 3: Multi-Agent Frameworks")
    print("="*60)

    status = []
    if CREWAI_AVAILABLE:
        status.append("CrewAI: Installed")
    else:
        status.append("CrewAI: Not installed (using simulation)")

    if AUTOGEN_AVAILABLE:
        status.append("AutoGen: Installed")
    else:
        status.append("AutoGen: Not installed (using simulation)")

    print(f"\nFramework Status: {', '.join(status)}")
    print("(Examples use simulations to demonstrate concepts)")

    # Run all demos
    demo_crewai_concepts()
    demo_crewai_code()
    demo_autogen_concepts()
    demo_autogen_code()
    demo_comparison()
    demo_other_frameworks()
    demo_decision_framework()
    demo_practical_example()

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("""
    Multi-Agent Framework Summary:

    1. CREWAI: Role-based teams
       - Agents have roles, goals, backstories
       - Tasks assigned to specific agents
       - Sequential or hierarchical process
       - Best for: Business workflows, clear responsibilities

    2. AUTOGEN: Conversational agents
       - Agents communicate via messages
       - Built-in code execution
       - Strong human-in-the-loop
       - Best for: Research, coding, dialogue

    3. LANGGRAPH: State machine agents
       - Maximum control and flexibility
       - Production-ready
       - Complex state management
       - Best for: Production systems

    Key Insight: Start simple (CrewAI), go complex (LangGraph)
                 as your needs grow.

    Module 19 Complete! You can now select the right framework!
    """)


if __name__ == "__main__":
    main()
