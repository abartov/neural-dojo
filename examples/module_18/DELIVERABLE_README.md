# Module 18 Deliverable: Stateful Workflow Engine

**A production-ready workflow engine built on LangGraph for orchestrating complex AI workflows.**

## Features

- **Workflow Definition DSL**: Define workflows programmatically or from JSON
- **Built-in Patterns**: Supervisor, parallel execution, routing, review cycles
- **State Persistence**: JSON-based storage for workflows and execution history
- **Multiple Node Types**: Processor, router, aggregator, LLM-powered
- **Execution Tracking**: Complete history with status, timing, and results
- **CLI Interface**: Easy-to-use command-line interface

## Quick Start

```bash
# Install dependencies
pip install langgraph langchain-google-genai

# Run demos
python deliverable_workflow_engine.py demo1  # Document processing
python deliverable_workflow_engine.py demo2  # Research team
python deliverable_workflow_engine.py demo3  # Smart routing
python deliverable_workflow_engine.py demo4  # Custom builder

# Management commands
python deliverable_workflow_engine.py list     # List workflows
python deliverable_workflow_engine.py history  # Execution history
```

## Architecture

### Core Components

```
WorkflowEngine
├── WorkflowDefinition    # Schema for workflows
│   ├── NodeDefinition    # Individual nodes
│   └── EdgeDefinition    # Connections
├── NodeFactory           # Creates node functions
├── StateGraph            # LangGraph integration
└── ExecutionRecord       # Tracking
```

### Node Types

| Type | Purpose | Config Options |
|------|---------|----------------|
| `PROCESSOR` | Basic processing | `processor_type`: validate, transform, extract |
| `ROUTER` | Conditional routing | `routes`: keyword→node mapping |
| `AGGREGATOR` | Combine results | `aggregation`: concat, count |
| `LLM` | LLM-powered | `system_prompt`: persona for LLM |

### Workflow Definition

```python
from deliverable_workflow_engine import (
    WorkflowDefinition, NodeDefinition, EdgeDefinition, NodeType
)

workflow = WorkflowDefinition(
    name="my_workflow",
    description="Custom workflow",
    nodes=[
        NodeDefinition(
            name="step1",
            node_type=NodeType.PROCESSOR,
            description="First step",
            config={"processor_type": "validate"}
        ),
        NodeDefinition(
            name="step2",
            node_type=NodeType.LLM,
            description="LLM processing",
            config={"system_prompt": "You are helpful."}
        )
    ],
    edges=[
        EdgeDefinition("step1", "step2"),
        EdgeDefinition("step2", "END")
    ],
    entry_node="step1"
)
```

## Built-in Workflows

### Document Processor
```
validate → extract → summarize → output
```
- Validates document format
- Extracts keywords
- Generates summary (LLM)
- Aggregates results

### Research Team
```
researcher → analyst → writer → aggregate
```
- Multi-agent workflow
- Each agent has specialized persona
- Results combined at end

### Smart Router
```
classifier → tech_handler/billing_handler/general_handler
```
- Keyword-based routing
- Different handlers for categories
- Default fallback

## Execution Flow

1. **Register**: Define and register workflow
2. **Compile**: Convert to LangGraph StateGraph
3. **Execute**: Run with initial state
4. **Track**: Save execution record
5. **Review**: Check history and results

## State Schema

```python
class WorkflowState(TypedDict):
    task: str                          # Input task
    context: Dict[str, Any]            # Additional context
    results: List[Dict]                # Accumulated results
    current_node: str                  # Active node
    next_node: Optional[str]           # Routing target
    iteration: int                     # Loop counter
    max_iterations: int                # Safety limit
    status: str                        # Execution status
    errors: List[str]                  # Error messages
    log: List[str]                     # Processing log
```

## Storage

Data persists in `.workflow_engine/`:

```
.workflow_engine/
├── workflows.json    # Registered workflows
└── history.json      # Execution records
```

## Execution History

```python
engine = WorkflowEngine()
history = engine.get_history(limit=10)

for record in history:
    print(f"{record.execution_id}: {record.status}")
    print(f"  Workflow: {record.workflow_name}")
    print(f"  Duration: {record.started_at} → {record.completed_at}")
```

## Extending

### Custom Node Type

```python
def create_custom_node(name: str, config: Dict) -> Callable:
    def node(state: WorkflowState) -> dict:
        # Your custom logic
        result = process(state["task"])
        return {
            "results": [{"node": name, "result": result}],
            "log": [f"[{name}] Processed"]
        }
    return node
```

### Custom Workflow Pattern

```python
# Parallel execution pattern
workflow = WorkflowDefinition(
    name="parallel_search",
    nodes=[
        NodeDefinition("web", NodeType.LLM, "Web search", {...}),
        NodeDefinition("news", NodeType.LLM, "News search", {...}),
        NodeDefinition("combine", NodeType.AGGREGATOR, "Combine", {...})
    ],
    edges=[
        EdgeDefinition("web", "combine"),
        EdgeDefinition("news", "combine"),
        EdgeDefinition("combine", "END")
    ],
    entry_node="web"  # Both start from entry
)
```

## Demo Outputs

### Demo 1: Document Processing
```
Workflow: document_processor
Flow: validate → extract → summarize → output

Execution Results:
  [validate] Validated input
  [extract] Extracted 5 keywords
  [summarize] LLM response generated
  [output] Aggregated 3 results
```

### Demo 2: Research Team
```
Workflow: research_team
Team: researcher → analyst → writer

Execution Results:
  [researcher] Research complete
  [analyst] Analysis complete
  [writer] Report generated
```

## Performance

| Metric | Value |
|--------|-------|
| Workflow registration | <10ms |
| Compilation | <50ms |
| Simple execution | <100ms |
| LLM execution | 1-5s (API dependent) |
| History retrieval | <10ms |

## Error Handling

- Invalid workflow definitions are caught at registration
- Runtime errors are captured in execution records
- LLM failures fall back to simulated responses
- All errors logged with timestamps

## Requirements

```
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-google-genai>=2.0.0  # For LLM features
```

---

**Time**: ~4 hours | **Lines**: 650+ | **Author**: Neural Dojo
