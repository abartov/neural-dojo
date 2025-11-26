#!/usr/bin/env python3
"""
Module 18, Example 1: LangGraph Basics & State Management

This example demonstrates:
1. Creating a StateGraph with typed state
2. Adding nodes (processing functions)
3. Connecting nodes with edges
4. Understanding state reducers (accumulation vs replacement)
5. Running and inspecting workflows

LangGraph is built on top of LangChain and provides graph-based
workflow orchestration for AI agents.

Usage:
    python 01_langgraph_basics.py
"""

from typing import TypedDict, List, Annotated, Optional
import operator
from datetime import datetime

# LangGraph imports
try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not installed. Install with: pip install langgraph")


# =============================================================================
# Part 1: Understanding State with TypedDict
# =============================================================================

def demo_state_basics():
    """Demonstrate state definition and reducer concepts."""
    print("\n" + "="*60)
    print("Part 1: State Basics")
    print("="*60)

    # State is defined using TypedDict
    # Annotations control how updates are merged

    print("""
    In LangGraph, state is defined with TypedDict:

    class MyState(TypedDict):
        # Simple field - gets REPLACED on each update
        current_value: str

        # Annotated field - uses reducer to MERGE updates
        messages: Annotated[List[str], operator.add]

    The reducer function (operator.add) determines how to combine
    the old value with the new value.
    """)

    # Demonstrate reducer behavior
    print("Reducer Examples:")
    print("-" * 40)

    # operator.add for lists - concatenates
    old_list = ["message 1"]
    new_list = ["message 2"]
    result = operator.add(old_list, new_list)
    print(f"  operator.add({old_list}, {new_list})")
    print(f"  Result: {result}")

    # operator.add for numbers - sums
    old_num = 5
    new_num = 3
    result = operator.add(old_num, new_num)
    print(f"\n  operator.add({old_num}, {new_num})")
    print(f"  Result: {result}")

    # Custom reducer - always take new value
    replace_reducer = lambda old, new: new
    old_val = "old"
    new_val = "new"
    result = replace_reducer(old_val, new_val)
    print(f"\n  replace_reducer('{old_val}', '{new_val}')")
    print(f"  Result: '{result}'")

    # Custom reducer - keep old if new is None
    keep_if_none = lambda old, new: old if new is None else new
    print(f"\n  keep_if_none('old', None) = '{keep_if_none('old', None)}'")
    print(f"  keep_if_none('old', 'new') = '{keep_if_none('old', 'new')}'")


# =============================================================================
# Part 2: Building a Simple Workflow
# =============================================================================

# Define state for a document processing workflow
class DocumentState(TypedDict):
    """State for document processing workflow."""
    # Input document (replaced each time)
    document: str

    # Processing status (replaced)
    status: str

    # Word count result (replaced)
    word_count: int

    # Processing log (accumulates)
    log: Annotated[List[str], operator.add]

    # Timestamps (accumulates)
    timestamps: Annotated[List[str], operator.add]


def log_timestamp(message: str) -> str:
    """Create a timestamped log message."""
    return f"[{datetime.now().strftime('%H:%M:%S')}] {message}"


# Node functions - each takes state and returns partial update
def validate_node(state: DocumentState) -> dict:
    """Validate the input document."""
    doc = state["document"]

    if not doc or len(doc.strip()) == 0:
        return {
            "status": "invalid",
            "log": [log_timestamp("Validation FAILED: empty document")]
        }

    return {
        "status": "validated",
        "log": [log_timestamp(f"Validation passed: {len(doc)} characters")],
        "timestamps": [datetime.now().isoformat()]
    }


def count_words_node(state: DocumentState) -> dict:
    """Count words in the document."""
    doc = state["document"]
    word_count = len(doc.split())

    return {
        "word_count": word_count,
        "status": "counted",
        "log": [log_timestamp(f"Word count: {word_count} words")],
        "timestamps": [datetime.now().isoformat()]
    }


def summarize_node(state: DocumentState) -> dict:
    """Generate a summary (simulated)."""
    word_count = state["word_count"]

    summary = f"Document has {word_count} words."
    if word_count < 10:
        summary += " This is a short document."
    elif word_count < 100:
        summary += " This is a medium-length document."
    else:
        summary += " This is a long document."

    return {
        "status": "complete",
        "log": [log_timestamp(f"Summary: {summary}")],
        "timestamps": [datetime.now().isoformat()]
    }


def build_simple_workflow():
    """Build and return a simple linear workflow."""
    if not LANGGRAPH_AVAILABLE:
        return None

    # Create the graph with our state type
    workflow = StateGraph(DocumentState)

    # Add nodes (processing steps)
    workflow.add_node("validate", validate_node)
    workflow.add_node("count", count_words_node)
    workflow.add_node("summarize", summarize_node)

    # Add edges (connections between nodes)
    # START is a special node representing the entry point
    workflow.add_edge(START, "validate")
    workflow.add_edge("validate", "count")
    workflow.add_edge("count", "summarize")
    workflow.add_edge("summarize", END)  # END marks completion

    # Compile the graph into a runnable
    return workflow.compile()


def demo_simple_workflow():
    """Demonstrate running a simple workflow."""
    print("\n" + "="*60)
    print("Part 2: Simple Linear Workflow")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build the workflow
    app = build_simple_workflow()

    print("""
    Workflow structure:
    START → [validate] → [count] → [summarize] → END

    Each node:
    1. Receives the current state
    2. Performs processing
    3. Returns a partial state update
    """)

    # Prepare initial state
    initial_state = {
        "document": "LangGraph is a powerful framework for building stateful AI workflows. It enables cycles, conditional branching, and multi-agent coordination.",
        "status": "pending",
        "word_count": 0,
        "log": [log_timestamp("Workflow started")],
        "timestamps": []
    }

    print("Initial state:")
    print(f"  document: '{initial_state['document'][:50]}...'")
    print(f"  status: {initial_state['status']}")
    print()

    # Run the workflow
    print("Running workflow...")
    result = app.invoke(initial_state)

    print("\nFinal state:")
    print(f"  status: {result['status']}")
    print(f"  word_count: {result['word_count']}")
    print(f"\nProcessing log:")
    for entry in result['log']:
        print(f"    {entry}")


# =============================================================================
# Part 3: State Accumulation in Action
# =============================================================================

class ConversationState(TypedDict):
    """State for a conversation workflow demonstrating accumulation."""
    # Current user input (replaced each turn)
    user_input: str

    # Conversation history (accumulates)
    history: Annotated[List[dict], operator.add]

    # Message count (uses custom reducer to increment)
    turn_count: int

    # Processing metadata (accumulates)
    metadata: Annotated[List[str], operator.add]


def user_input_node(state: ConversationState) -> dict:
    """Process user input."""
    user_msg = state["user_input"]
    turn = state.get("turn_count", 0) + 1

    return {
        "history": [{"role": "user", "content": user_msg, "turn": turn}],
        "turn_count": turn,
        "metadata": [f"User input received (turn {turn})"]
    }


def assistant_response_node(state: ConversationState) -> dict:
    """Generate assistant response (simulated)."""
    user_msg = state["user_input"]
    turn = state["turn_count"]

    # Simple response logic (in real app, would use LLM)
    if "hello" in user_msg.lower():
        response = "Hello! How can I help you today?"
    elif "?" in user_msg:
        response = "That's a great question! Let me think about that."
    else:
        response = f"I understand you said: '{user_msg}'"

    return {
        "history": [{"role": "assistant", "content": response, "turn": turn}],
        "metadata": [f"Response generated (turn {turn})"]
    }


def demo_state_accumulation():
    """Demonstrate how state accumulates across workflow runs."""
    print("\n" + "="*60)
    print("Part 3: State Accumulation")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build conversation workflow
    workflow = StateGraph(ConversationState)
    workflow.add_node("process_input", user_input_node)
    workflow.add_node("generate_response", assistant_response_node)

    workflow.add_edge(START, "process_input")
    workflow.add_edge("process_input", "generate_response")
    workflow.add_edge("generate_response", END)

    app = workflow.compile()

    print("""
    This workflow shows how annotated fields accumulate:
    - history: Annotated[List[dict], operator.add]  # Grows with each message
    - metadata: Annotated[List[str], operator.add]  # Grows with each step
    - turn_count: int  # Replaced each time (tracks current turn)
    """)

    # Simulate a multi-turn conversation
    # Note: In real use, you'd use checkpointing to maintain state
    conversation_inputs = [
        "Hello there!",
        "What is LangGraph?",
        "Thanks for explaining!"
    ]

    # Track accumulated state manually for demo
    accumulated_state = {
        "user_input": "",
        "history": [],
        "turn_count": 0,
        "metadata": ["Conversation started"]
    }

    print("Simulating multi-turn conversation:")
    print("-" * 40)

    for user_input in conversation_inputs:
        # Update user input
        accumulated_state["user_input"] = user_input

        # Run one turn
        result = app.invoke(accumulated_state)

        # Merge accumulated fields manually (checkpointing does this automatically)
        accumulated_state["history"] = result["history"]
        accumulated_state["turn_count"] = result["turn_count"]
        accumulated_state["metadata"] = result["metadata"]

        print(f"\nTurn {result['turn_count']}:")
        print(f"  User: {user_input}")
        # Get latest assistant message
        assistant_msgs = [h for h in result["history"] if h["role"] == "assistant"]
        if assistant_msgs:
            print(f"  Assistant: {assistant_msgs[-1]['content']}")

    print(f"\nFinal conversation history ({len(accumulated_state['history'])} messages):")
    for msg in accumulated_state['history']:
        print(f"  [{msg['role']}] {msg['content']}")


# =============================================================================
# Part 4: Inspecting the Graph
# =============================================================================

def demo_graph_inspection():
    """Demonstrate how to inspect a compiled graph."""
    print("\n" + "="*60)
    print("Part 4: Graph Inspection")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    app = build_simple_workflow()

    print("""
    You can inspect a compiled graph to understand its structure:
    - Get node names
    - Visualize the graph
    - Generate Mermaid diagrams
    """)

    # Get the graph structure
    graph = app.get_graph()

    print("Graph nodes:")
    for node in graph.nodes:
        print(f"  - {node}")

    print("\nGraph edges:")
    for edge in graph.edges:
        print(f"  {edge}")

    # Generate Mermaid diagram (text format)
    print("\nMermaid diagram (paste into mermaid.live):")
    print("-" * 40)
    try:
        mermaid = graph.draw_mermaid()
        print(mermaid)
    except Exception as e:
        print(f"  Could not generate Mermaid: {e}")

    print("""
    To visualize in Jupyter notebook:
        from IPython.display import Image, display
        display(Image(app.get_graph().draw_mermaid_png()))
    """)


# =============================================================================
# Part 5: Error Handling in Nodes
# =============================================================================

class ProcessingState(TypedDict):
    """State with error handling."""
    input_data: str
    result: Optional[str]
    error: Optional[str]
    log: Annotated[List[str], operator.add]


def risky_processing_node(state: ProcessingState) -> dict:
    """A node that might fail."""
    data = state["input_data"]

    # Simulate validation
    if not data:
        return {
            "error": "Input data is empty",
            "log": ["ERROR: Processing failed - empty input"]
        }

    if "error" in data.lower():
        return {
            "error": "Input contains forbidden word",
            "log": ["ERROR: Processing failed - forbidden content"]
        }

    # Success case
    return {
        "result": f"Processed: {data.upper()}",
        "error": None,
        "log": ["SUCCESS: Processing complete"]
    }


def output_node(state: ProcessingState) -> dict:
    """Output node that handles both success and error cases."""
    if state.get("error"):
        return {
            "log": [f"Final status: FAILED - {state['error']}"]
        }
    else:
        return {
            "log": [f"Final status: SUCCESS - {state['result']}"]
        }


def demo_error_handling():
    """Demonstrate error handling in workflows."""
    print("\n" + "="*60)
    print("Part 5: Error Handling")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build workflow with error-aware nodes
    workflow = StateGraph(ProcessingState)
    workflow.add_node("process", risky_processing_node)
    workflow.add_node("output", output_node)

    workflow.add_edge(START, "process")
    workflow.add_edge("process", "output")
    workflow.add_edge("output", END)

    app = workflow.compile()

    print("""
    Nodes should handle errors gracefully:
    1. Catch exceptions within the node
    2. Return error information in state
    3. Let downstream nodes react to errors
    """)

    # Test cases
    test_cases = [
        {"input_data": "Hello World", "log": ["Test: valid input"]},
        {"input_data": "", "log": ["Test: empty input"]},
        {"input_data": "This has an error word", "log": ["Test: forbidden word"]}
    ]

    for i, test_state in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        print(f"  Input: '{test_state['input_data']}'")

        result = app.invoke(test_state)

        print(f"  Result: {result.get('result', 'None')}")
        print(f"  Error: {result.get('error', 'None')}")
        print(f"  Log: {result['log'][-1]}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*60)
    print("Module 18, Example 1: LangGraph Basics")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("\n*** LangGraph is not installed ***")
        print("Install with: pip install langgraph")
        print("\nDemonstrating concepts without running graphs...")
        demo_state_basics()
        return

    # Run all demos
    demo_state_basics()
    demo_simple_workflow()
    demo_state_accumulation()
    demo_graph_inspection()
    demo_error_handling()

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("""
    Key takeaways:

    1. STATE: Use TypedDict with Annotated fields for accumulation
       - Regular fields get replaced
       - Annotated[List, operator.add] accumulates

    2. NODES: Functions that take state and return partial updates
       - Only return fields that changed
       - LangGraph merges updates with existing state

    3. EDGES: Connect nodes to define flow
       - START → first_node
       - last_node → END

    4. COMPILE: Call graph.compile() to get runnable app
       - app.invoke(state) runs the workflow
       - Returns final state

    Next: Example 2 covers conditional branching and cycles!
    """)


if __name__ == "__main__":
    main()
