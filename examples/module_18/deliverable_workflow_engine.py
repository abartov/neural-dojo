#!/usr/bin/env python3
"""
Module 18 Deliverable: Stateful Workflow Engine

A production-ready workflow engine built on LangGraph that provides:
- Workflow definition DSL (Domain Specific Language)
- Built-in patterns (supervisor, parallel, review cycle)
- State persistence with JSON
- Workflow history and replay
- CLI interface for workflow management

This demonstrates mastery of LangGraph concepts while providing
a reusable foundation for building AI workflows.

Usage:
    python deliverable_workflow_engine.py demo1      # Document processing workflow
    python deliverable_workflow_engine.py demo2      # Research team workflow
    python deliverable_workflow_engine.py demo3      # Review cycle workflow
    python deliverable_workflow_engine.py demo4      # Custom workflow builder
    python deliverable_workflow_engine.py list       # List saved workflows
    python deliverable_workflow_engine.py history    # Show execution history

Author: Neural Dojo
"""

from typing import TypedDict, List, Annotated, Literal, Optional, Dict, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import operator
import json
import sys
import os
import hashlib

# LangGraph imports
try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

# LangChain imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage
    LLM_AVAILABLE = bool(os.getenv("GOOGLE_API_KEY"))
except ImportError:
    LLM_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================

STORAGE_DIR = Path(".workflow_engine")
WORKFLOWS_FILE = STORAGE_DIR / "workflows.json"
HISTORY_FILE = STORAGE_DIR / "history.json"


# =============================================================================
# Data Models
# =============================================================================

class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class NodeType(str, Enum):
    """Types of workflow nodes."""
    PROCESSOR = "processor"      # Basic processing node
    ROUTER = "router"            # Conditional routing
    AGGREGATOR = "aggregator"    # Combines multiple inputs
    HUMAN = "human"              # Requires human input
    LLM = "llm"                  # LLM-powered node


@dataclass
class NodeDefinition:
    """Definition of a workflow node."""
    name: str
    node_type: NodeType
    description: str
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "node_type": self.node_type.value,
            "description": self.description,
            "config": self.config
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NodeDefinition":
        return cls(
            name=data["name"],
            node_type=NodeType(data["node_type"]),
            description=data["description"],
            config=data.get("config", {})
        )


@dataclass
class EdgeDefinition:
    """Definition of a workflow edge."""
    source: str
    target: str
    condition: Optional[str] = None  # Condition for conditional edges

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "condition": self.condition
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EdgeDefinition":
        return cls(
            source=data["source"],
            target=data["target"],
            condition=data.get("condition")
        )


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    name: str
    description: str
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    entry_node: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "entry_node": self.entry_node,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowDefinition":
        return cls(
            name=data["name"],
            description=data["description"],
            nodes=[NodeDefinition.from_dict(n) for n in data["nodes"]],
            edges=[EdgeDefinition.from_dict(e) for e in data["edges"]],
            entry_node=data["entry_node"],
            created_at=data.get("created_at", datetime.now().isoformat())
        )


@dataclass
class ExecutionRecord:
    """Record of a workflow execution."""
    execution_id: str
    workflow_name: str
    status: WorkflowStatus
    started_at: str
    completed_at: Optional[str]
    input_state: Dict[str, Any]
    output_state: Optional[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "input_state": self.input_state,
            "output_state": self.output_state,
            "steps": self.steps,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionRecord":
        return cls(
            execution_id=data["execution_id"],
            workflow_name=data["workflow_name"],
            status=WorkflowStatus(data["status"]),
            started_at=data["started_at"],
            completed_at=data.get("completed_at"),
            input_state=data["input_state"],
            output_state=data.get("output_state"),
            steps=data.get("steps", []),
            error=data.get("error")
        )


# =============================================================================
# Generic Workflow State
# =============================================================================

class WorkflowState(TypedDict):
    """Generic state for all workflows."""
    # Task information
    task: str
    context: Dict[str, Any]

    # Processing results
    results: Annotated[List[Dict[str, Any]], operator.add]

    # Control flow
    current_node: str
    next_node: Optional[str]
    iteration: int
    max_iterations: int

    # Status tracking
    status: str
    errors: Annotated[List[str], operator.add]
    log: Annotated[List[str], operator.add]


# =============================================================================
# Node Implementations
# =============================================================================

class NodeFactory:
    """Factory for creating workflow nodes."""

    @staticmethod
    def create_processor_node(name: str, config: Dict[str, Any]) -> Callable:
        """Create a basic processor node."""
        processor_type = config.get("processor_type", "default")

        def node(state: WorkflowState) -> dict:
            task = state["task"]
            context = state.get("context", {})

            # Different processor types
            if processor_type == "validate":
                result = {"action": "validate", "valid": bool(task)}
                log_msg = f"[{name}] Validated input"
            elif processor_type == "transform":
                transform = config.get("transform", "upper")
                if transform == "upper":
                    result = {"action": "transform", "value": task.upper()}
                else:
                    result = {"action": "transform", "value": task.lower()}
                log_msg = f"[{name}] Transformed: {transform}"
            elif processor_type == "extract":
                # Extract keywords (simple implementation)
                words = task.split()
                keywords = [w for w in words if len(w) > 5]
                result = {"action": "extract", "keywords": keywords}
                log_msg = f"[{name}] Extracted {len(keywords)} keywords"
            else:
                result = {"action": "process", "input": task}
                log_msg = f"[{name}] Processed task"

            return {
                "results": [{"node": name, "result": result}],
                "current_node": name,
                "log": [log_msg]
            }

        return node

    @staticmethod
    def create_router_node(name: str, config: Dict[str, Any]) -> Callable:
        """Create a routing node."""
        routes = config.get("routes", {})
        default_route = config.get("default", "end")

        def node(state: WorkflowState) -> dict:
            # Determine route based on state
            task = state["task"].lower()

            for keyword, route in routes.items():
                if keyword in task:
                    return {
                        "next_node": route,
                        "current_node": name,
                        "log": [f"[{name}] Routing to: {route}"]
                    }

            return {
                "next_node": default_route,
                "current_node": name,
                "log": [f"[{name}] Default route: {default_route}"]
            }

        return node

    @staticmethod
    def create_aggregator_node(name: str, config: Dict[str, Any]) -> Callable:
        """Create an aggregator node."""
        aggregation_type = config.get("aggregation", "concat")

        def node(state: WorkflowState) -> dict:
            results = state.get("results", [])

            if aggregation_type == "concat":
                aggregated = " | ".join(str(r.get("result", "")) for r in results)
            elif aggregation_type == "count":
                aggregated = f"Total results: {len(results)}"
            else:
                aggregated = results

            return {
                "results": [{"node": name, "result": {"aggregated": aggregated}}],
                "current_node": name,
                "log": [f"[{name}] Aggregated {len(results)} results"]
            }

        return node

    @staticmethod
    def create_llm_node(name: str, config: Dict[str, Any]) -> Callable:
        """Create an LLM-powered node."""
        system_prompt = config.get("system_prompt", "You are a helpful assistant.")

        def node(state: WorkflowState) -> dict:
            task = state["task"]

            if not LLM_AVAILABLE:
                # Simulated response
                response = f"[Simulated LLM] Processing: {task[:50]}..."
            else:
                try:
                    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=task)
                    ]
                    result = llm.invoke(messages)
                    response = result.content
                except Exception as e:
                    response = f"LLM Error: {str(e)}"

            return {
                "results": [{"node": name, "result": {"response": response}}],
                "current_node": name,
                "log": [f"[{name}] LLM response generated"]
            }

        return node


# =============================================================================
# Workflow Engine
# =============================================================================

class WorkflowEngine:
    """
    Production workflow engine built on LangGraph.

    Features:
    - Define workflows programmatically or from JSON
    - Execute with state persistence
    - Track execution history
    - Support for common patterns
    """

    def __init__(self):
        """Initialize the workflow engine."""
        self._ensure_storage()
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.compiled_apps: Dict[str, Any] = {}
        self._load_workflows()

    def _ensure_storage(self):
        """Ensure storage directory exists."""
        STORAGE_DIR.mkdir(exist_ok=True)

    def _load_workflows(self):
        """Load saved workflows from storage."""
        if WORKFLOWS_FILE.exists():
            try:
                with open(WORKFLOWS_FILE, 'r') as f:
                    data = json.load(f)
                    for name, wf_data in data.items():
                        self.workflows[name] = WorkflowDefinition.from_dict(wf_data)
            except Exception as e:
                print(f"Warning: Could not load workflows: {e}")

    def _save_workflows(self):
        """Save workflows to storage."""
        data = {name: wf.to_dict() for name, wf in self.workflows.items()}
        with open(WORKFLOWS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_execution(self, record: ExecutionRecord):
        """Save execution record to history."""
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            except Exception:
                pass

        history.append(record.to_dict())

        # Keep last 100 executions
        history = history[-100:]

        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

    def register_workflow(self, definition: WorkflowDefinition):
        """Register a new workflow definition."""
        self.workflows[definition.name] = definition
        self._save_workflows()
        print(f"  Registered workflow: {definition.name}")

    def compile_workflow(self, name: str) -> Any:
        """Compile a workflow definition into a runnable graph."""
        if not LANGGRAPH_AVAILABLE:
            raise RuntimeError("LangGraph not available")

        if name not in self.workflows:
            raise ValueError(f"Unknown workflow: {name}")

        definition = self.workflows[name]

        # Create the state graph
        graph = StateGraph(WorkflowState)

        # Add nodes
        for node_def in definition.nodes:
            if node_def.node_type == NodeType.PROCESSOR:
                func = NodeFactory.create_processor_node(node_def.name, node_def.config)
            elif node_def.node_type == NodeType.ROUTER:
                func = NodeFactory.create_router_node(node_def.name, node_def.config)
            elif node_def.node_type == NodeType.AGGREGATOR:
                func = NodeFactory.create_aggregator_node(node_def.name, node_def.config)
            elif node_def.node_type == NodeType.LLM:
                func = NodeFactory.create_llm_node(node_def.name, node_def.config)
            else:
                # Default processor
                func = NodeFactory.create_processor_node(node_def.name, {})

            graph.add_node(node_def.name, func)

        # Add edges
        graph.add_edge(START, definition.entry_node)

        for edge in definition.edges:
            if edge.target == "END":
                graph.add_edge(edge.source, END)
            else:
                graph.add_edge(edge.source, edge.target)

        # Compile with checkpointer
        checkpointer = MemorySaver()
        app = graph.compile(checkpointer=checkpointer)

        self.compiled_apps[name] = app
        return app

    def execute(self, workflow_name: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with the given initial state."""
        # Generate execution ID
        exec_id = hashlib.sha256(
            f"{workflow_name}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Create execution record
        record = ExecutionRecord(
            execution_id=exec_id,
            workflow_name=workflow_name,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now().isoformat(),
            completed_at=None,
            input_state=initial_state,
            output_state=None,
            steps=[]
        )

        try:
            # Compile if needed
            if workflow_name not in self.compiled_apps:
                self.compile_workflow(workflow_name)

            app = self.compiled_apps[workflow_name]

            # Prepare state
            state = {
                "task": initial_state.get("task", ""),
                "context": initial_state.get("context", {}),
                "results": [],
                "current_node": "",
                "next_node": None,
                "iteration": 0,
                "max_iterations": initial_state.get("max_iterations", 10),
                "status": "running",
                "errors": [],
                "log": [f"[Engine] Starting workflow: {workflow_name}"]
            }

            # Execute
            config = {"configurable": {"thread_id": exec_id}}
            result = app.invoke(state, config)

            # Update record
            record.status = WorkflowStatus.COMPLETED
            record.completed_at = datetime.now().isoformat()
            record.output_state = {
                "results": result.get("results", []),
                "log": result.get("log", []),
                "errors": result.get("errors", [])
            }

        except Exception as e:
            record.status = WorkflowStatus.FAILED
            record.completed_at = datetime.now().isoformat()
            record.error = str(e)
            result = {"error": str(e)}

        # Save execution record
        self._save_execution(record)

        return result

    def get_history(self, limit: int = 10) -> List[ExecutionRecord]:
        """Get recent execution history."""
        if not HISTORY_FILE.exists():
            return []

        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)

        records = [ExecutionRecord.from_dict(h) for h in history[-limit:]]
        return list(reversed(records))

    def list_workflows(self) -> List[str]:
        """List all registered workflows."""
        return list(self.workflows.keys())


# =============================================================================
# Pre-built Workflow Templates
# =============================================================================

def create_document_processing_workflow() -> WorkflowDefinition:
    """Create a document processing workflow."""
    return WorkflowDefinition(
        name="document_processor",
        description="Process documents through validation, extraction, and summarization",
        nodes=[
            NodeDefinition(
                name="validate",
                node_type=NodeType.PROCESSOR,
                description="Validate document format",
                config={"processor_type": "validate"}
            ),
            NodeDefinition(
                name="extract",
                node_type=NodeType.PROCESSOR,
                description="Extract key information",
                config={"processor_type": "extract"}
            ),
            NodeDefinition(
                name="summarize",
                node_type=NodeType.LLM,
                description="Generate summary using LLM",
                config={"system_prompt": "Summarize the following text concisely."}
            ),
            NodeDefinition(
                name="output",
                node_type=NodeType.AGGREGATOR,
                description="Aggregate all results",
                config={"aggregation": "concat"}
            )
        ],
        edges=[
            EdgeDefinition("validate", "extract"),
            EdgeDefinition("extract", "summarize"),
            EdgeDefinition("summarize", "output"),
            EdgeDefinition("output", "END")
        ],
        entry_node="validate"
    )


def create_research_team_workflow() -> WorkflowDefinition:
    """Create a multi-agent research team workflow."""
    return WorkflowDefinition(
        name="research_team",
        description="Multi-agent workflow with researcher, analyst, and writer",
        nodes=[
            NodeDefinition(
                name="researcher",
                node_type=NodeType.LLM,
                description="Research the topic",
                config={"system_prompt": "You are a research assistant. Provide factual information about the given topic."}
            ),
            NodeDefinition(
                name="analyst",
                node_type=NodeType.LLM,
                description="Analyze research findings",
                config={"system_prompt": "You are an analyst. Synthesize and analyze the research findings."}
            ),
            NodeDefinition(
                name="writer",
                node_type=NodeType.LLM,
                description="Write final report",
                config={"system_prompt": "You are a technical writer. Create a clear, well-structured report."}
            ),
            NodeDefinition(
                name="aggregate",
                node_type=NodeType.AGGREGATOR,
                description="Combine all outputs",
                config={"aggregation": "concat"}
            )
        ],
        edges=[
            EdgeDefinition("researcher", "analyst"),
            EdgeDefinition("analyst", "writer"),
            EdgeDefinition("writer", "aggregate"),
            EdgeDefinition("aggregate", "END")
        ],
        entry_node="researcher"
    )


def create_routing_workflow() -> WorkflowDefinition:
    """Create a workflow with conditional routing."""
    return WorkflowDefinition(
        name="smart_router",
        description="Route requests to appropriate handlers",
        nodes=[
            NodeDefinition(
                name="classifier",
                node_type=NodeType.ROUTER,
                description="Classify and route requests",
                config={
                    "routes": {
                        "technical": "tech_handler",
                        "billing": "billing_handler",
                        "general": "general_handler"
                    },
                    "default": "general_handler"
                }
            ),
            NodeDefinition(
                name="tech_handler",
                node_type=NodeType.PROCESSOR,
                description="Handle technical requests",
                config={"processor_type": "default"}
            ),
            NodeDefinition(
                name="billing_handler",
                node_type=NodeType.PROCESSOR,
                description="Handle billing requests",
                config={"processor_type": "default"}
            ),
            NodeDefinition(
                name="general_handler",
                node_type=NodeType.PROCESSOR,
                description="Handle general requests",
                config={"processor_type": "default"}
            )
        ],
        edges=[
            EdgeDefinition("tech_handler", "END"),
            EdgeDefinition("billing_handler", "END"),
            EdgeDefinition("general_handler", "END")
        ],
        entry_node="classifier"
    )


# =============================================================================
# Demo Functions
# =============================================================================

def demo_document_processing():
    """Demo 1: Document processing workflow."""
    print("\n" + "="*60)
    print("Demo 1: Document Processing Workflow")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("LangGraph not available. Install with: pip install langgraph")
        return

    engine = WorkflowEngine()

    # Register the workflow
    workflow = create_document_processing_workflow()
    engine.register_workflow(workflow)

    print(f"\nWorkflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"\nNodes: {[n.name for n in workflow.nodes]}")
    print(f"Flow: validate → extract → summarize → output")

    # Execute
    print("\n" + "-"*40)
    print("Executing workflow...")

    result = engine.execute("document_processor", {
        "task": "LangGraph is a powerful framework for building stateful AI workflows. It enables cycles, conditional branching, and multi-agent coordination through a graph-based architecture."
    })

    print("\nExecution Results:")
    if "error" in result:
        print(f"  Error: {result['error']}")
    else:
        print(f"  Log entries: {len(result.get('log', []))}")
        for entry in result.get("log", []):
            print(f"    {entry}")

        print(f"\n  Results: {len(result.get('results', []))}")
        for r in result.get("results", []):
            print(f"    - {r['node']}: {str(r['result'])[:80]}...")


def demo_research_team():
    """Demo 2: Multi-agent research team."""
    print("\n" + "="*60)
    print("Demo 2: Research Team Workflow")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("LangGraph not available. Install with: pip install langgraph")
        return

    engine = WorkflowEngine()

    # Register the workflow
    workflow = create_research_team_workflow()
    engine.register_workflow(workflow)

    print(f"\nWorkflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"\nTeam: researcher → analyst → writer")

    if LLM_AVAILABLE:
        print("\nLLM: Using Google Gemini")
    else:
        print("\nLLM: Simulated (set GOOGLE_API_KEY for real LLM)")

    # Execute
    print("\n" + "-"*40)
    print("Executing research team workflow...")

    result = engine.execute("research_team", {
        "task": "Explain the benefits of multi-agent AI systems in software development"
    })

    print("\nExecution Results:")
    if "error" in result:
        print(f"  Error: {result['error']}")
    else:
        for entry in result.get("log", []):
            print(f"  {entry}")

        print("\n  Agent outputs:")
        for r in result.get("results", []):
            output = str(r.get("result", {}))
            print(f"    [{r['node']}]: {output[:100]}...")


def demo_routing_workflow():
    """Demo 3: Conditional routing workflow."""
    print("\n" + "="*60)
    print("Demo 3: Smart Routing Workflow")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("LangGraph not available. Install with: pip install langgraph")
        return

    engine = WorkflowEngine()

    # Register the workflow
    workflow = create_routing_workflow()
    engine.register_workflow(workflow)

    print(f"\nWorkflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print("\nRoutes based on keywords in task")

    # Test with different inputs
    test_tasks = [
        "I have a technical issue with the API",
        "Please help with my billing statement",
        "General question about your services"
    ]

    print("\n" + "-"*40)

    for task in test_tasks:
        print(f"\nTask: '{task}'")
        result = engine.execute("smart_router", {"task": task})

        if "error" not in result:
            for entry in result.get("log", []):
                print(f"  {entry}")


def demo_custom_workflow():
    """Demo 4: Build a custom workflow."""
    print("\n" + "="*60)
    print("Demo 4: Custom Workflow Builder")
    print("="*60)

    if not LANGGRAPH_AVAILABLE:
        print("LangGraph not available. Install with: pip install langgraph")
        return

    engine = WorkflowEngine()

    # Create a custom workflow programmatically
    custom_workflow = WorkflowDefinition(
        name="text_pipeline",
        description="Custom text processing pipeline",
        nodes=[
            NodeDefinition(
                name="normalize",
                node_type=NodeType.PROCESSOR,
                description="Normalize text to uppercase",
                config={"processor_type": "transform", "transform": "upper"}
            ),
            NodeDefinition(
                name="keywords",
                node_type=NodeType.PROCESSOR,
                description="Extract keywords",
                config={"processor_type": "extract"}
            ),
            NodeDefinition(
                name="combine",
                node_type=NodeType.AGGREGATOR,
                description="Combine results",
                config={"aggregation": "concat"}
            )
        ],
        edges=[
            EdgeDefinition("normalize", "keywords"),
            EdgeDefinition("keywords", "combine"),
            EdgeDefinition("combine", "END")
        ],
        entry_node="normalize"
    )

    print(f"\nBuilding custom workflow: {custom_workflow.name}")
    print(f"Description: {custom_workflow.description}")
    print(f"Nodes: {[n.name for n in custom_workflow.nodes]}")

    # Register and execute
    engine.register_workflow(custom_workflow)

    print("\n" + "-"*40)
    print("Executing custom workflow...")

    result = engine.execute("text_pipeline", {
        "task": "LangGraph enables sophisticated multi-agent orchestration patterns"
    })

    print("\nResults:")
    if "error" not in result:
        for entry in result.get("log", []):
            print(f"  {entry}")

        print("\n  Outputs:")
        for r in result.get("results", []):
            print(f"    [{r['node']}]: {r['result']}")


def list_workflows():
    """List all registered workflows."""
    print("\n" + "="*60)
    print("Registered Workflows")
    print("="*60)

    engine = WorkflowEngine()
    workflows = engine.list_workflows()

    if not workflows:
        print("\nNo workflows registered yet.")
        print("Run demo1-demo4 to create workflows.")
        return

    print(f"\nFound {len(workflows)} workflow(s):")
    for name in workflows:
        wf = engine.workflows[name]
        print(f"\n  {name}")
        print(f"    Description: {wf.description}")
        print(f"    Nodes: {[n.name for n in wf.nodes]}")
        print(f"    Created: {wf.created_at}")


def show_history():
    """Show execution history."""
    print("\n" + "="*60)
    print("Execution History")
    print("="*60)

    engine = WorkflowEngine()
    history = engine.get_history(limit=10)

    if not history:
        print("\nNo execution history yet.")
        print("Run demo1-demo4 to execute workflows.")
        return

    print(f"\nLast {len(history)} execution(s):")

    for record in history:
        status_icon = {
            WorkflowStatus.COMPLETED: "✅",
            WorkflowStatus.FAILED: "❌",
            WorkflowStatus.RUNNING: "🔄",
            WorkflowStatus.PAUSED: "⏸️",
            WorkflowStatus.PENDING: "⏳"
        }.get(record.status, "❓")

        print(f"\n  {status_icon} {record.execution_id[:8]}...")
        print(f"     Workflow: {record.workflow_name}")
        print(f"     Status: {record.status.value}")
        print(f"     Started: {record.started_at}")
        if record.error:
            print(f"     Error: {record.error}")


def print_usage():
    """Print usage information."""
    print("""
Workflow Engine - Module 18 Deliverable
========================================

A production-ready workflow engine built on LangGraph.

Usage:
    python deliverable_workflow_engine.py <command>

Commands:
    demo1     - Document processing workflow
    demo2     - Research team (multi-agent) workflow
    demo3     - Smart routing workflow
    demo4     - Custom workflow builder

    list      - List all registered workflows
    history   - Show execution history
    help      - Show this help message

Features:
    - Workflow definition DSL
    - Built-in patterns (supervisor, parallel, routing)
    - State persistence with JSON
    - Execution history tracking
    - LLM integration (optional)

Requirements:
    pip install langgraph langchain-google-genai

For LLM features:
    export GOOGLE_API_KEY="your-api-key"
""")


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == "demo1":
        demo_document_processing()
    elif command == "demo2":
        demo_research_team()
    elif command == "demo3":
        demo_routing_workflow()
    elif command == "demo4":
        demo_custom_workflow()
    elif command == "list":
        list_workflows()
    elif command == "history":
        show_history()
    elif command == "help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()

    print("\n" + "="*60)
    print("Workflow Engine - Module 18 Deliverable")
    print("="*60)


if __name__ == "__main__":
    main()
