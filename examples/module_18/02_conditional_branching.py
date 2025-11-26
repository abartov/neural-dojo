#!/usr/bin/env python3
"""
Module 18, Example 2: Conditional Branching & Cycles

This example demonstrates:
1. Conditional edges - routing based on state
2. Cycles (loops) - iterative refinement patterns
3. Maximum iteration safeguards
4. Real-world retry and review patterns

The ability to branch and loop is what makes LangGraph
more powerful than linear chains.

Usage:
    python 02_conditional_branching.py
"""

from typing import TypedDict, List, Annotated, Literal, Optional
import operator
import random
from datetime import datetime

# LangGraph imports
try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not installed. Install with: pip install langgraph")


# =============================================================================
# Part 1: Basic Conditional Branching
# =============================================================================

class TicketState(TypedDict):
    """State for support ticket routing."""
    ticket_text: str
    category: Literal["billing", "technical", "general", "unknown"]
    priority: Literal["low", "medium", "high", "critical"]
    response: str
    log: Annotated[List[str], operator.add]


def classify_ticket(state: TicketState) -> dict:
    """Classify ticket into category and priority."""
    text = state["ticket_text"].lower()

    # Simple keyword-based classification
    if any(word in text for word in ["payment", "invoice", "charge", "refund", "billing"]):
        category = "billing"
    elif any(word in text for word in ["error", "bug", "crash", "broken", "not working"]):
        category = "technical"
    elif any(word in text for word in ["question", "how to", "help", "information"]):
        category = "general"
    else:
        category = "unknown"

    # Priority based on urgency words
    if any(word in text for word in ["urgent", "asap", "critical", "emergency"]):
        priority = "critical"
    elif any(word in text for word in ["important", "soon", "quickly"]):
        priority = "high"
    elif any(word in text for word in ["when possible", "no rush"]):
        priority = "low"
    else:
        priority = "medium"

    return {
        "category": category,
        "priority": priority,
        "log": [f"Classified as {category} ({priority} priority)"]
    }


def handle_billing(state: TicketState) -> dict:
    """Handle billing-related tickets."""
    return {
        "response": "Thank you for contacting billing support. Our team will review your account and respond within 24 hours.",
        "log": ["Routed to billing team"]
    }


def handle_technical(state: TicketState) -> dict:
    """Handle technical support tickets."""
    return {
        "response": "Our technical team has received your issue. Please check our FAQ while waiting for a response.",
        "log": ["Routed to technical support"]
    }


def handle_general(state: TicketState) -> dict:
    """Handle general inquiries."""
    return {
        "response": "Thank you for your inquiry. A support representative will assist you shortly.",
        "log": ["Routed to general support"]
    }


def handle_unknown(state: TicketState) -> dict:
    """Handle unclassified tickets."""
    return {
        "response": "We've received your message. A team member will review and respond soon.",
        "log": ["Routed to triage queue"]
    }


def route_by_category(state: TicketState) -> str:
    """Route to appropriate handler based on category."""
    routing = {
        "billing": "billing_handler",
        "technical": "technical_handler",
        "general": "general_handler",
        "unknown": "unknown_handler"
    }
    return routing[state["category"]]


def demo_conditional_branching():
    """Demonstrate conditional routing based on state."""
    print("\n" + "="*60)
    print("Part 1: Conditional Branching")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build the routing workflow
    workflow = StateGraph(TicketState)

    # Add nodes
    workflow.add_node("classify", classify_ticket)
    workflow.add_node("billing_handler", handle_billing)
    workflow.add_node("technical_handler", handle_technical)
    workflow.add_node("general_handler", handle_general)
    workflow.add_node("unknown_handler", handle_unknown)

    # Entry point
    workflow.add_edge(START, "classify")

    # Conditional routing after classification
    workflow.add_conditional_edges(
        "classify",  # Source node
        route_by_category,  # Routing function
        {  # Map of return values to target nodes
            "billing_handler": "billing_handler",
            "technical_handler": "technical_handler",
            "general_handler": "general_handler",
            "unknown_handler": "unknown_handler"
        }
    )

    # All handlers lead to END
    workflow.add_edge("billing_handler", END)
    workflow.add_edge("technical_handler", END)
    workflow.add_edge("general_handler", END)
    workflow.add_edge("unknown_handler", END)

    app = workflow.compile()

    print("""
    Workflow with conditional branching:

    START → [classify] → route_by_category() ─┬→ [billing_handler] → END
                                              ├→ [technical_handler] → END
                                              ├→ [general_handler] → END
                                              └→ [unknown_handler] → END

    The route_by_category function examines state and returns
    the name of the next node to execute.
    """)

    # Test with different tickets
    test_tickets = [
        "I was charged twice on my invoice last month. Please refund.",
        "URGENT: The application crashes when I click submit!",
        "How do I reset my password?",
        "I love your product! Just wanted to say thanks."
    ]

    print("Testing ticket routing:")
    print("-" * 40)

    for ticket in test_tickets:
        result = app.invoke({
            "ticket_text": ticket,
            "log": [f"Received: {ticket[:40]}..."]
        })
        print(f"\nTicket: '{ticket[:50]}...'")
        print(f"  Category: {result['category']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Response: {result['response'][:60]}...")


# =============================================================================
# Part 2: Cycles - The Review Loop
# =============================================================================

class WritingState(TypedDict):
    """State for iterative writing workflow."""
    topic: str
    draft: str
    feedback: str
    revision_count: int
    max_revisions: int
    quality_score: float
    is_approved: bool
    log: Annotated[List[str], operator.add]


def write_draft(state: WritingState) -> dict:
    """Write or revise the draft."""
    topic = state["topic"]
    revision = state.get("revision_count", 0)
    feedback = state.get("feedback", "")

    if revision == 0:
        # Initial draft
        draft = f"# {topic}\n\nThis is the initial draft about {topic}. It covers the main points."
        log_msg = "Created initial draft"
    else:
        # Revision incorporating feedback
        draft = f"# {topic}\n\nRevision {revision}: Improved based on feedback: {feedback}\n\nEnhanced content about {topic}."
        log_msg = f"Created revision {revision}"

    return {
        "draft": draft,
        "revision_count": revision + 1,
        "log": [log_msg]
    }


def review_draft(state: WritingState) -> dict:
    """Review the draft and provide feedback."""
    revision = state["revision_count"]

    # Simulate quality improvement with each revision
    # In a real app, this would use an LLM to evaluate
    base_score = 0.5
    improvement_per_revision = 0.15
    randomness = random.uniform(-0.05, 0.1)

    quality_score = min(1.0, base_score + (revision * improvement_per_revision) + randomness)

    if quality_score >= 0.8:
        feedback = "Excellent work! The draft meets our quality standards."
        is_approved = True
    else:
        issues = ["needs more detail", "improve structure", "add examples", "clarify main points"]
        feedback = f"Quality {quality_score:.0%}. Please: {random.choice(issues)}."
        is_approved = False

    return {
        "quality_score": quality_score,
        "feedback": feedback,
        "is_approved": is_approved,
        "log": [f"Review complete: {quality_score:.0%} quality"]
    }


def publish_draft(state: WritingState) -> dict:
    """Publish the approved draft."""
    return {
        "log": [f"Published after {state['revision_count']} revision(s)! Final quality: {state['quality_score']:.0%}"]
    }


def should_continue_writing(state: WritingState) -> str:
    """Decide whether to revise or publish."""
    if state["is_approved"]:
        return "publish"
    elif state["revision_count"] >= state["max_revisions"]:
        return "publish"  # Publish anyway after max attempts
    else:
        return "revise"


def demo_cycles():
    """Demonstrate cycles (loops) in workflows."""
    print("\n" + "="*60)
    print("Part 2: Cycles - The Review Loop")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build the writing workflow with a cycle
    workflow = StateGraph(WritingState)

    workflow.add_node("write", write_draft)
    workflow.add_node("review", review_draft)
    workflow.add_node("publish", publish_draft)

    workflow.add_edge(START, "write")
    workflow.add_edge("write", "review")

    # This creates a CYCLE: review can go back to write
    workflow.add_conditional_edges(
        "review",
        should_continue_writing,
        {
            "revise": "write",  # Loop back!
            "publish": "publish"
        }
    )

    workflow.add_edge("publish", END)

    app = workflow.compile()

    print("""
    Workflow with a cycle:

    START → [write] → [review] → should_continue() ─┬→ [publish] → END
                ↑                                    │
                └──────────── "revise" ─────────────┘

    The cycle continues until:
    1. Quality threshold is met (is_approved = True)
    2. Maximum revisions reached
    """)

    # Run the workflow
    print("Running iterative writing workflow:")
    print("-" * 40)

    # Set random seed for reproducibility in demo
    random.seed(42)

    result = app.invoke({
        "topic": "LangGraph Cycles",
        "draft": "",
        "feedback": "",
        "revision_count": 0,
        "max_revisions": 5,
        "quality_score": 0.0,
        "is_approved": False,
        "log": ["Starting writing process"]
    })

    print("\nProcess log:")
    for entry in result["log"]:
        print(f"  {entry}")

    print(f"\nFinal draft preview: {result['draft'][:100]}...")
    print(f"Total revisions: {result['revision_count']}")
    print(f"Final quality: {result['quality_score']:.0%}")


# =============================================================================
# Part 3: Retry Pattern with Exponential Backoff
# =============================================================================

class APICallState(TypedDict):
    """State for API call with retry logic."""
    endpoint: str
    payload: str
    response: Optional[str]
    error: Optional[str]
    attempt: int
    max_attempts: int
    success: bool
    log: Annotated[List[str], operator.add]


def call_api(state: APICallState) -> dict:
    """Simulate an API call that might fail."""
    attempt = state.get("attempt", 0) + 1

    # Simulate flaky API - fails 60% of the time on first attempts
    failure_rate = max(0.1, 0.6 - (attempt * 0.2))
    will_fail = random.random() < failure_rate

    if will_fail:
        errors = [
            "Connection timeout",
            "Rate limited",
            "Service unavailable",
            "Gateway timeout"
        ]
        return {
            "attempt": attempt,
            "error": random.choice(errors),
            "success": False,
            "log": [f"Attempt {attempt}: FAILED - {random.choice(errors)}"]
        }
    else:
        return {
            "attempt": attempt,
            "response": f"Success! Data for {state['endpoint']}",
            "error": None,
            "success": True,
            "log": [f"Attempt {attempt}: SUCCESS"]
        }


def handle_success(state: APICallState) -> dict:
    """Handle successful API call."""
    return {
        "log": [f"API call completed after {state['attempt']} attempt(s)"]
    }


def handle_failure(state: APICallState) -> dict:
    """Handle final failure after all retries."""
    return {
        "log": [f"API call FAILED after {state['attempt']} attempts. Last error: {state['error']}"]
    }


def should_retry(state: APICallState) -> str:
    """Decide whether to retry the API call."""
    if state["success"]:
        return "success"
    elif state["attempt"] >= state["max_attempts"]:
        return "failure"
    else:
        return "retry"


def demo_retry_pattern():
    """Demonstrate retry pattern with cycles."""
    print("\n" + "="*60)
    print("Part 3: Retry Pattern")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build retry workflow
    workflow = StateGraph(APICallState)

    workflow.add_node("call_api", call_api)
    workflow.add_node("success", handle_success)
    workflow.add_node("failure", handle_failure)

    workflow.add_edge(START, "call_api")

    workflow.add_conditional_edges(
        "call_api",
        should_retry,
        {
            "retry": "call_api",  # Loop back to retry
            "success": "success",
            "failure": "failure"
        }
    )

    workflow.add_edge("success", END)
    workflow.add_edge("failure", END)

    app = workflow.compile()

    print("""
    Retry workflow:

    START → [call_api] → should_retry() ─┬→ [success] → END
                ↑                        ├→ [failure] → END
                └──────── "retry" ───────┘

    Retries until:
    1. API call succeeds
    2. Maximum attempts reached
    """)

    # Run multiple times to show different outcomes
    print("Running API call with retry (5 test runs):")
    print("-" * 40)

    random.seed(None)  # Use real randomness

    for run in range(1, 6):
        result = app.invoke({
            "endpoint": "/api/data",
            "payload": "test",
            "attempt": 0,
            "max_attempts": 3,
            "success": False,
            "log": [f"Run {run}: Starting API call"]
        })

        status = "SUCCESS" if result["success"] else "FAILED"
        print(f"\nRun {run}: {status} after {result['attempt']} attempt(s)")
        for entry in result["log"][1:]:  # Skip "Starting" message
            print(f"    {entry}")


# =============================================================================
# Part 4: Multi-Stage Validation Pipeline
# =============================================================================

class ValidationState(TypedDict):
    """State for multi-stage validation."""
    data: dict
    validation_stage: str
    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]
    is_valid: bool
    log: Annotated[List[str], operator.add]


def validate_format(state: ValidationState) -> dict:
    """Validate data format."""
    data = state["data"]
    errors = []
    warnings = []

    # Check required fields
    required = ["name", "email", "age"]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    return {
        "validation_stage": "format",
        "errors": errors,
        "is_valid": len(errors) == 0,
        "log": [f"Format validation: {len(errors)} errors found"]
    }


def validate_content(state: ValidationState) -> dict:
    """Validate data content."""
    data = state["data"]
    errors = []
    warnings = []

    # Validate email format
    email = data.get("email", "")
    if email and "@" not in email:
        errors.append(f"Invalid email format: {email}")

    # Validate age
    age = data.get("age", 0)
    if age < 0 or age > 150:
        errors.append(f"Invalid age: {age}")
    elif age < 18:
        warnings.append(f"User is a minor (age {age})")

    return {
        "validation_stage": "content",
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0 and state["is_valid"],
        "log": [f"Content validation: {len(errors)} errors, {len(warnings)} warnings"]
    }


def validate_policy(state: ValidationState) -> dict:
    """Validate against business policies."""
    data = state["data"]
    errors = []
    warnings = []

    # Example policy checks
    name = data.get("name", "")
    if len(name) < 2:
        errors.append("Name must be at least 2 characters")

    email_domain = data.get("email", "").split("@")[-1] if "@" in data.get("email", "") else ""
    blocked_domains = ["spam.com", "fake.com"]
    if email_domain in blocked_domains:
        errors.append(f"Email domain {email_domain} is blocked")

    return {
        "validation_stage": "policy",
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0 and state["is_valid"],
        "log": [f"Policy validation: {len(errors)} errors"]
    }


def accept_data(state: ValidationState) -> dict:
    """Accept valid data."""
    return {
        "log": ["Data ACCEPTED - all validations passed"]
    }


def reject_data(state: ValidationState) -> dict:
    """Reject invalid data."""
    all_errors = state["errors"]
    return {
        "log": [f"Data REJECTED - {len(all_errors)} error(s): {'; '.join(all_errors)}"]
    }


def route_validation(state: ValidationState) -> str:
    """Route based on validation result."""
    if not state["is_valid"]:
        return "reject"

    # Move through stages
    if state["validation_stage"] == "format":
        return "content"
    elif state["validation_stage"] == "content":
        return "policy"
    else:
        return "accept"


def demo_multi_stage_validation():
    """Demonstrate multi-stage validation with branching."""
    print("\n" + "="*60)
    print("Part 4: Multi-Stage Validation")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("Skipping - LangGraph not available")
        return

    # Build validation pipeline
    workflow = StateGraph(ValidationState)

    workflow.add_node("format_check", validate_format)
    workflow.add_node("content_check", validate_content)
    workflow.add_node("policy_check", validate_policy)
    workflow.add_node("accept", accept_data)
    workflow.add_node("reject", reject_data)

    workflow.add_edge(START, "format_check")

    # Each stage can either continue or reject
    workflow.add_conditional_edges(
        "format_check",
        route_validation,
        {"content": "content_check", "reject": "reject"}
    )

    workflow.add_conditional_edges(
        "content_check",
        route_validation,
        {"policy": "policy_check", "reject": "reject"}
    )

    workflow.add_conditional_edges(
        "policy_check",
        route_validation,
        {"accept": "accept", "reject": "reject"}
    )

    workflow.add_edge("accept", END)
    workflow.add_edge("reject", END)

    app = workflow.compile()

    print("""
    Multi-stage validation pipeline:

    START → [format] ─┬→ [content] ─┬→ [policy] ─┬→ [accept] → END
                      │             │            │
                      └─────────────┴────────────┴→ [reject] → END

    Each stage can reject early, preventing unnecessary processing.
    """)

    # Test with different data
    test_cases = [
        {"name": "John Doe", "email": "john@example.com", "age": 30},  # Valid
        {"name": "Jane", "email": "jane@example.com"},  # Missing age
        {"name": "Bob", "email": "invalid-email", "age": 25},  # Bad email
        {"name": "X", "email": "test@spam.com", "age": 25},  # Policy violation
        {"name": "Alice", "email": "alice@example.com", "age": 16},  # Minor (warning)
    ]

    print("Testing validation pipeline:")
    print("-" * 40)

    for i, data in enumerate(test_cases, 1):
        result = app.invoke({
            "data": data,
            "validation_stage": "",
            "errors": [],
            "warnings": [],
            "is_valid": True,
            "log": [f"Test {i}: Validating {data}"]
        })

        status = "ACCEPTED" if result["is_valid"] else "REJECTED"
        print(f"\nTest {i}: {status}")
        print(f"  Data: {data}")
        if result["errors"]:
            print(f"  Errors: {result['errors']}")
        if result["warnings"]:
            print(f"  Warnings: {result['warnings']}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all demonstrations."""
    print("="*60)
    print("Module 18, Example 2: Conditional Branching & Cycles")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("\n*** LangGraph is not installed ***")
        print("Install with: pip install langgraph")
        return

    demo_conditional_branching()
    demo_cycles()
    demo_retry_pattern()
    demo_multi_stage_validation()

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("""
    Key takeaways:

    1. CONDITIONAL EDGES: Route based on state
       - add_conditional_edges(source, routing_func, mapping)
       - routing_func returns the name of the next node

    2. CYCLES: Create loops for iterative refinement
       - Point an edge back to an earlier node
       - ALWAYS include exit conditions!

    3. SAFEGUARDS: Prevent infinite loops
       - Track iteration count
       - Set maximum attempts
       - Check in routing function

    4. PATTERNS:
       - Review/revise loop
       - Retry with backoff
       - Multi-stage validation (early exit)

    Next: Example 3 covers multi-agent orchestration!
    """)


if __name__ == "__main__":
    main()
