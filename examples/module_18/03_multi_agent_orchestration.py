#!/usr/bin/env python3
"""
Module 18, Example 3: Multi-Agent Orchestration

This example demonstrates:
1. Supervisor pattern - one agent coordinates others
2. Parallel agent execution
3. Agent communication through shared state
4. Human-in-the-loop patterns
5. Checkpointing for persistence

Multi-agent systems are where LangGraph really shines,
enabling complex collaborative AI workflows.

Usage:
    python 03_multi_agent_orchestration.py

Requires:
    pip install langgraph langchain-google-genai
"""

from typing import TypedDict, List, Annotated, Literal, Optional, Dict, Any
import operator
import os
from datetime import datetime
from dataclasses import dataclass

# LangGraph imports
try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not installed. Install with: pip install langgraph")

# LangChain imports for LLM integration
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    LLM_AVAILABLE = bool(os.getenv("GOOGLE_API_KEY"))
except ImportError:
    LLM_AVAILABLE = False


# =============================================================================
# Part 1: The Supervisor Pattern
# =============================================================================

class ResearchTeamState(TypedDict):
    """State for a research team with supervisor."""
    # The research task
    task: str

    # Work products from each agent
    research_notes: str
    analysis: str
    draft: str

    # Supervisor control
    next_agent: Literal["researcher", "analyst", "writer", "done"]
    iteration: int
    max_iterations: int

    # Communication log
    messages: Annotated[List[str], operator.add]


def supervisor_node(state: ResearchTeamState) -> dict:
    """
    Supervisor decides which agent should work next.

    The supervisor pattern:
    1. Examines current state
    2. Determines what work is needed
    3. Assigns to appropriate agent
    4. Monitors progress
    """
    research = state.get("research_notes", "")
    analysis = state.get("analysis", "")
    draft = state.get("draft", "")
    iteration = state.get("iteration", 0) + 1

    # Determine next step based on what's missing
    if not research:
        next_agent = "researcher"
        message = "Assigning research task to Researcher"
    elif not analysis:
        next_agent = "analyst"
        message = "Research complete. Assigning to Analyst"
    elif not draft:
        next_agent = "writer"
        message = "Analysis complete. Assigning to Writer"
    else:
        next_agent = "done"
        message = "All work complete!"

    return {
        "next_agent": next_agent,
        "iteration": iteration,
        "messages": [f"[Supervisor] {message}"]
    }


def researcher_node(state: ResearchTeamState) -> dict:
    """
    Researcher agent gathers information.

    In production, this would:
    - Use search tools
    - Query databases
    - Read documents
    """
    task = state["task"]

    # Simulated research (in real app, use LLM + tools)
    research_notes = f"""
    Research Notes for: {task}

    Key Findings:
    1. LangGraph enables stateful AI workflows
    2. The supervisor pattern coordinates multiple agents
    3. State is shared through TypedDict
    4. Conditional edges enable dynamic routing

    Sources:
    - LangGraph Documentation
    - LangChain Blog Posts
    - Academic Papers on Multi-Agent Systems
    """

    return {
        "research_notes": research_notes,
        "messages": [f"[Researcher] Completed research on '{task}'"]
    }


def analyst_node(state: ResearchTeamState) -> dict:
    """
    Analyst agent processes research into insights.

    In production, this would:
    - Synthesize information
    - Identify patterns
    - Draw conclusions
    """
    research = state["research_notes"]

    # Simulated analysis
    analysis = f"""
    Analysis Summary:

    Based on the research, here are the key insights:

    1. ARCHITECTURE: LangGraph uses a graph-based approach
       - Nodes are processing functions
       - Edges define flow
       - State persists across nodes

    2. PATTERNS: The supervisor pattern is effective for:
       - Coordinating specialized agents
       - Dynamic task assignment
       - Quality control

    3. RECOMMENDATIONS:
       - Use typed state for reliability
       - Implement checkpointing for long workflows
       - Add human-in-the-loop for critical decisions
    """

    return {
        "analysis": analysis,
        "messages": [f"[Analyst] Completed analysis"]
    }


def writer_node(state: ResearchTeamState) -> dict:
    """
    Writer agent creates final content.

    In production, this would:
    - Generate polished content
    - Follow style guidelines
    - Incorporate feedback
    """
    analysis = state["analysis"]
    task = state["task"]

    # Simulated writing
    draft = f"""
    # {task}

    ## Executive Summary

    This report presents our findings on multi-agent orchestration
    using LangGraph.

    ## Key Points

    LangGraph provides a powerful framework for building AI systems
    where multiple specialized agents collaborate on complex tasks.

    The supervisor pattern enables:
    - Dynamic task assignment
    - Parallel processing where possible
    - Quality control through iteration

    ## Conclusion

    Multi-agent systems represent the future of AI workflows,
    enabling more sophisticated problem-solving through collaboration.
    """

    return {
        "draft": draft,
        "messages": [f"[Writer] Completed draft"]
    }


def route_to_agent(state: ResearchTeamState) -> str:
    """Route to the next agent based on supervisor's decision."""
    return state["next_agent"]


def demo_supervisor_pattern():
    """Demonstrate the supervisor pattern for multi-agent coordination."""
    print("\n" + "="*60)
    print("Part 1: The Supervisor Pattern")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build the multi-agent workflow
    workflow = StateGraph(ResearchTeamState)

    # Add all nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    # Entry point - supervisor first
    workflow.add_edge(START, "supervisor")

    # Supervisor routes to agents
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "done": END
        }
    )

    # Each agent reports back to supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("writer", "supervisor")

    app = workflow.compile()

    print("""
    Supervisor Pattern:

                        ┌─────────────┐
                        │  Supervisor │ ← Coordinates all work
                        └──────┬──────┘
               ┌───────────────┼───────────────┐
               ↓               ↓               ↓
        [Researcher]     [Analyst]       [Writer]
               │               │               │
               └───────────────┴───────────────┘
                               ↓
                        (report back)

    Each agent:
    1. Receives task from supervisor
    2. Does specialized work
    3. Updates shared state
    4. Returns to supervisor
    """)

    # Run the workflow
    print("Running research team workflow:")
    print("-" * 40)

    result = app.invoke({
        "task": "Explain Multi-Agent Orchestration in LangGraph",
        "research_notes": "",
        "analysis": "",
        "draft": "",
        "next_agent": "researcher",
        "iteration": 0,
        "max_iterations": 10,
        "messages": ["[System] Workflow started"]
    })

    print("\nWorkflow messages:")
    for msg in result["messages"]:
        print(f"  {msg}")

    print(f"\nFinal draft preview:")
    print(result["draft"][:300] + "...")


# =============================================================================
# Part 2: Parallel Agent Execution
# =============================================================================

class ParallelResearchState(TypedDict):
    """State for parallel research workflow."""
    query: str

    # Results from parallel searches
    web_results: str
    academic_results: str
    news_results: str

    # Combined results
    combined: str

    messages: Annotated[List[str], operator.add]


def web_search_agent(state: ParallelResearchState) -> dict:
    """Agent that searches the web."""
    query = state["query"]

    # Simulated web search
    results = f"Web results for '{query}': Found 10 relevant articles from tech blogs."

    return {
        "web_results": results,
        "messages": [f"[WebSearch] Completed search"]
    }


def academic_search_agent(state: ParallelResearchState) -> dict:
    """Agent that searches academic papers."""
    query = state["query"]

    # Simulated academic search
    results = f"Academic results for '{query}': Found 5 relevant papers from arXiv."

    return {
        "academic_results": results,
        "messages": [f"[AcademicSearch] Completed search"]
    }


def news_search_agent(state: ParallelResearchState) -> dict:
    """Agent that searches news."""
    query = state["query"]

    # Simulated news search
    results = f"News results for '{query}': Found 3 recent news articles."

    return {
        "news_results": results,
        "messages": [f"[NewsSearch] Completed search"]
    }


def combine_results(state: ParallelResearchState) -> dict:
    """Combine results from all search agents."""
    combined = f"""
    Combined Research Results:

    WEB: {state['web_results']}

    ACADEMIC: {state['academic_results']}

    NEWS: {state['news_results']}
    """

    return {
        "combined": combined,
        "messages": [f"[Combiner] All results combined"]
    }


def demo_parallel_execution():
    """Demonstrate parallel agent execution."""
    print("\n" + "="*60)
    print("Part 2: Parallel Agent Execution")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build parallel workflow
    workflow = StateGraph(ParallelResearchState)

    # Add search agents
    workflow.add_node("web_search", web_search_agent)
    workflow.add_node("academic_search", academic_search_agent)
    workflow.add_node("news_search", news_search_agent)
    workflow.add_node("combine", combine_results)

    # Fan out from START to all search agents (parallel)
    workflow.add_edge(START, "web_search")
    workflow.add_edge(START, "academic_search")
    workflow.add_edge(START, "news_search")

    # Fan in to combiner (waits for all)
    workflow.add_edge("web_search", "combine")
    workflow.add_edge("academic_search", "combine")
    workflow.add_edge("news_search", "combine")

    workflow.add_edge("combine", END)

    app = workflow.compile()

    print("""
    Parallel Execution Pattern:

                    START
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
    [WebSearch] [AcademicSearch] [NewsSearch]
          │           │           │
          └───────────┼───────────┘
                      ↓
                 [Combine]
                      │
                     END

    LangGraph automatically:
    - Executes independent nodes in parallel
    - Waits for all inputs before running dependent nodes
    """)

    # Run the parallel workflow
    print("Running parallel search workflow:")
    print("-" * 40)

    result = app.invoke({
        "query": "LangGraph multi-agent systems",
        "web_results": "",
        "academic_results": "",
        "news_results": "",
        "combined": "",
        "messages": ["[System] Starting parallel search"]
    })

    print("\nExecution messages:")
    for msg in result["messages"]:
        print(f"  {msg}")

    print(f"\nCombined results:")
    print(result["combined"])


# =============================================================================
# Part 3: Human-in-the-Loop
# =============================================================================

class ApprovalState(TypedDict):
    """State for workflow with human approval."""
    proposal: str
    proposal_type: str
    estimated_cost: float

    # Human input fields
    approved: Optional[bool]
    feedback: Optional[str]

    # Processing state
    status: str
    messages: Annotated[List[str], operator.add]


def create_proposal(state: ApprovalState) -> dict:
    """Create a proposal for human review."""
    proposal_type = state["proposal_type"]
    cost = state["estimated_cost"]

    proposal = f"""
    PROPOSAL: {proposal_type}

    Estimated Cost: ${cost:,.2f}

    Details:
    This proposal requests approval for {proposal_type.lower()}.
    The estimated budget is ${cost:,.2f}.

    Please review and approve/reject.
    """

    return {
        "proposal": proposal,
        "status": "pending_approval",
        "messages": [f"[System] Proposal created, awaiting approval"]
    }


def execute_proposal(state: ApprovalState) -> dict:
    """Execute the approved proposal."""
    if state.get("approved"):
        return {
            "status": "executed",
            "messages": [f"[System] Proposal APPROVED and executed!"]
        }
    else:
        feedback = state.get("feedback", "No feedback provided")
        return {
            "status": "rejected",
            "messages": [f"[System] Proposal REJECTED. Feedback: {feedback}"]
        }


def demo_human_in_the_loop():
    """Demonstrate human-in-the-loop pattern."""
    print("\n" + "="*60)
    print("Part 3: Human-in-the-Loop")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build workflow with interrupt
    workflow = StateGraph(ApprovalState)

    workflow.add_node("create", create_proposal)
    workflow.add_node("execute", execute_proposal)

    workflow.add_edge(START, "create")
    workflow.add_edge("create", "execute")
    workflow.add_edge("execute", END)

    # Compile with checkpointer for interrupts
    checkpointer = MemorySaver()
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute"]  # Pause before execution
    )

    print("""
    Human-in-the-Loop Pattern:

    START → [create] → INTERRUPT → [execute] → END
                           ↑
                     Human approval

    The workflow:
    1. Creates proposal
    2. PAUSES for human review
    3. Human approves/rejects
    4. Continues with decision
    """)

    # Start the workflow
    print("Running workflow with human interrupt:")
    print("-" * 40)

    config = {"configurable": {"thread_id": "proposal-001"}}

    # Run until interrupt
    result = app.invoke({
        "proposal_type": "Infrastructure Upgrade",
        "estimated_cost": 50000.00,
        "approved": None,
        "feedback": None,
        "status": "new",
        "messages": ["[System] Workflow started"]
    }, config)

    print("\nWorkflow paused for approval:")
    print(result["proposal"])
    print(f"Status: {result['status']}")

    # Simulate human approval
    print("\n[Human] Reviewing proposal...")
    print("[Human] Approving with feedback: 'Proceed with phase 1 only'")

    # Update state with human input
    app.update_state(
        config,
        {
            "approved": True,
            "feedback": "Proceed with phase 1 only"
        }
    )

    # Continue execution
    final = app.invoke(None, config)

    print(f"\nFinal status: {final['status']}")
    for msg in final["messages"]:
        print(f"  {msg}")


# =============================================================================
# Part 4: Agent with LLM (if available)
# =============================================================================

class LLMAgentState(TypedDict):
    """State for LLM-powered agent."""
    task: str
    context: str
    response: str
    messages: Annotated[List[dict], operator.add]


def create_llm_node(persona: str, system_prompt: str):
    """Factory to create LLM-powered agent nodes."""

    def node(state: LLMAgentState) -> dict:
        """Process task using LLM."""
        if not LLM_AVAILABLE:
            # Fallback for no API key
            return {
                "response": f"[{persona}] (Simulated) Response to: {state['task'][:50]}...",
                "messages": [{"role": persona, "content": f"Processed task (simulated)"}]
            }

        try:
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Task: {state['task']}\n\nContext: {state.get('context', 'None')}")
            ]

            response = llm.invoke(messages)

            return {
                "response": response.content,
                "messages": [{"role": persona, "content": response.content[:200]}]
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "messages": [{"role": persona, "content": f"Error: {str(e)}"}]
            }

    return node


def demo_llm_agents():
    """Demonstrate LLM-powered agents."""
    print("\n" + "="*60)
    print("Part 4: LLM-Powered Agents")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Create specialized LLM agents
    researcher_llm = create_llm_node(
        "Researcher",
        "You are a research assistant. Provide concise, factual information about the given topic."
    )

    analyst_llm = create_llm_node(
        "Analyst",
        "You are an analyst. Synthesize information and provide insights."
    )

    # Build simple two-agent workflow
    workflow = StateGraph(LLMAgentState)

    workflow.add_node("research", researcher_llm)
    workflow.add_node("analyze", analyst_llm)

    workflow.add_edge(START, "research")
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", END)

    app = workflow.compile()

    if LLM_AVAILABLE:
        print("Running LLM-powered agents (with Gemini):")
    else:
        print("Running simulated agents (set GOOGLE_API_KEY for real LLMs):")

    print("-" * 40)

    result = app.invoke({
        "task": "Explain the benefits of multi-agent AI systems",
        "context": "Focus on practical applications in software development",
        "response": "",
        "messages": []
    })

    print("\nAgent responses:")
    for msg in result["messages"]:
        print(f"\n[{msg['role']}]:")
        print(f"  {msg['content'][:300]}...")


# =============================================================================
# Part 5: Hierarchical Agent Teams
# =============================================================================

class HierarchicalState(TypedDict):
    """State for hierarchical agent organization."""
    project: str

    # Team leads
    frontend_work: str
    backend_work: str
    devops_work: str

    # Coordination
    current_team: str
    teams_completed: Annotated[List[str], operator.add]
    all_complete: bool

    messages: Annotated[List[str], operator.add]


def project_manager(state: HierarchicalState) -> dict:
    """Project manager coordinates team leads."""
    completed = state.get("teams_completed", [])

    if "frontend" not in completed:
        return {
            "current_team": "frontend",
            "messages": ["[PM] Assigning to Frontend Team"]
        }
    elif "backend" not in completed:
        return {
            "current_team": "backend",
            "messages": ["[PM] Assigning to Backend Team"]
        }
    elif "devops" not in completed:
        return {
            "current_team": "devops",
            "messages": ["[PM] Assigning to DevOps Team"]
        }
    else:
        return {
            "current_team": "done",
            "all_complete": True,
            "messages": ["[PM] All teams complete!"]
        }


def frontend_team(state: HierarchicalState) -> dict:
    """Frontend team lead with sub-workers."""
    project = state["project"]

    # In production, this could spawn sub-agents
    work = f"Frontend: Built UI components for {project}"

    return {
        "frontend_work": work,
        "teams_completed": ["frontend"],
        "messages": ["[Frontend] Team completed UI work"]
    }


def backend_team(state: HierarchicalState) -> dict:
    """Backend team lead with sub-workers."""
    project = state["project"]

    work = f"Backend: Built API endpoints for {project}"

    return {
        "backend_work": work,
        "teams_completed": ["backend"],
        "messages": ["[Backend] Team completed API work"]
    }


def devops_team(state: HierarchicalState) -> dict:
    """DevOps team lead with sub-workers."""
    project = state["project"]

    work = f"DevOps: Set up CI/CD and deployment for {project}"

    return {
        "devops_work": work,
        "teams_completed": ["devops"],
        "messages": ["[DevOps] Team completed infrastructure work"]
    }


def route_to_team(state: HierarchicalState) -> str:
    """Route to appropriate team."""
    return state["current_team"]


def demo_hierarchical_teams():
    """Demonstrate hierarchical agent organization."""
    print("\n" + "="*60)
    print("Part 5: Hierarchical Agent Teams")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build hierarchical workflow
    workflow = StateGraph(HierarchicalState)

    workflow.add_node("pm", project_manager)
    workflow.add_node("frontend", frontend_team)
    workflow.add_node("backend", backend_team)
    workflow.add_node("devops", devops_team)

    workflow.add_edge(START, "pm")

    workflow.add_conditional_edges(
        "pm",
        route_to_team,
        {
            "frontend": "frontend",
            "backend": "backend",
            "devops": "devops",
            "done": END
        }
    )

    # Teams report back to PM
    workflow.add_edge("frontend", "pm")
    workflow.add_edge("backend", "pm")
    workflow.add_edge("devops", "pm")

    app = workflow.compile()

    print("""
    Hierarchical Team Structure:

                    ┌──────────────────┐
                    │ Project Manager  │
                    └────────┬─────────┘
           ┌─────────────────┼─────────────────┐
           ↓                 ↓                 ↓
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Frontend Lead│ │ Backend Lead │ │ DevOps Lead  │
    └──────────────┘ └──────────────┘ └──────────────┘
           ↓                 ↓                 ↓
     [Sub-workers]     [Sub-workers]     [Sub-workers]

    Each team lead could spawn their own sub-graph!
    """)

    # Run the project
    print("Running hierarchical project workflow:")
    print("-" * 40)

    result = app.invoke({
        "project": "AI Dashboard",
        "frontend_work": "",
        "backend_work": "",
        "devops_work": "",
        "current_team": "",
        "teams_completed": [],
        "all_complete": False,
        "messages": ["[System] Project started"]
    })

    print("\nProject execution log:")
    for msg in result["messages"]:
        print(f"  {msg}")

    print(f"\nProject deliverables:")
    print(f"  Frontend: {result['frontend_work']}")
    print(f"  Backend: {result['backend_work']}")
    print(f"  DevOps: {result['devops_work']}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*60)
    print("Module 18, Example 3: Multi-Agent Orchestration")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("\n*** LangGraph is not installed ***")
        print("Install with: pip install langgraph")
        return

    demo_supervisor_pattern()
    demo_parallel_execution()
    demo_human_in_the_loop()
    demo_llm_agents()
    demo_hierarchical_teams()

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("""
    Multi-Agent Patterns:

    1. SUPERVISOR: One agent coordinates others
       - Examines state, assigns tasks
       - Agents report back
       - Supervisor decides next step

    2. PARALLEL: Independent agents run simultaneously
       - Fan out from single node
       - Fan in to combiner
       - LangGraph handles synchronization

    3. HUMAN-IN-THE-LOOP: Pause for human input
       - Use interrupt_before/interrupt_after
       - Requires checkpointer
       - update_state() to provide input

    4. LLM-POWERED: Agents backed by language models
       - Each agent has specialized persona
       - State carries context between agents
       - Can use different models per agent

    5. HIERARCHICAL: Nested team structures
       - Team leads can spawn sub-agents
       - Subgraphs for complex teams
       - Scales to large organizations

    Key Insights:
    - Shared state enables communication
    - Supervisor pattern prevents chaos
    - Checkpointing enables human intervention
    - Each agent should have clear responsibility
    """)


if __name__ == "__main__":
    main()
