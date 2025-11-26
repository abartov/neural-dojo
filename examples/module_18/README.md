# Module 18 Examples: LangGraph & Stateful Workflows

This directory contains working code examples for Module 18, demonstrating LangGraph for building stateful AI workflows.

## Prerequisites

```bash
pip install -r requirements.txt
```

For LLM-powered features:
```bash
export GOOGLE_API_KEY="your-api-key"
```

## Examples

### Example 1: LangGraph Basics
**File**: `01_langgraph_basics.py`
**Description**: Introduction to LangGraph fundamentals - StateGraph, nodes, edges, and state management with reducers.

```bash
python 01_langgraph_basics.py
```

**Topics covered**:
- State definition with TypedDict
- State reducers (accumulation vs replacement)
- Adding nodes and edges
- Compiling and running graphs

### Example 2: Conditional Branching & Cycles
**File**: `02_conditional_branching.py`
**Description**: Dynamic routing and iterative workflows with cycles.

```bash
python 02_conditional_branching.py
```

**Topics covered**:
- Conditional edges with routing functions
- Cycles for iterative refinement
- Retry patterns
- Multi-stage validation pipelines

### Example 3: Multi-Agent Orchestration
**File**: `03_multi_agent_orchestration.py`
**Description**: Coordinating multiple agents for complex tasks.

```bash
python 03_multi_agent_orchestration.py
```

**Topics covered**:
- Supervisor pattern
- Parallel agent execution
- Human-in-the-loop
- Hierarchical agent teams
- LLM-powered agents

## Deliverable

### Stateful Workflow Engine
**File**: `deliverable_workflow_engine.py`
**Description**: Production-ready workflow engine with DSL, persistence, and history tracking.

```bash
# Demo 1: Document processing
python deliverable_workflow_engine.py demo1

# Demo 2: Research team (multi-agent)
python deliverable_workflow_engine.py demo2

# Demo 3: Smart routing
python deliverable_workflow_engine.py demo3

# Demo 4: Custom workflow builder
python deliverable_workflow_engine.py demo4

# List registered workflows
python deliverable_workflow_engine.py list

# Show execution history
python deliverable_workflow_engine.py history
```

See `DELIVERABLE_README.md` for complete documentation.

## Key Concepts

### StateGraph

```python
from langgraph.graph import StateGraph, START, END

class MyState(TypedDict):
    value: str
    history: Annotated[List[str], operator.add]

graph = StateGraph(MyState)
graph.add_node("process", process_fn)
graph.add_edge(START, "process")
graph.add_edge("process", END)
app = graph.compile()
```

### Conditional Edges

```python
def route(state):
    if state["success"]:
        return "finish"
    return "retry"

graph.add_conditional_edges(
    "check",
    route,
    {"finish": "done", "retry": "process"}
)
```

### State Reducers

```python
from typing import Annotated
import operator

class State(TypedDict):
    # Replaces on each update
    current: str

    # Accumulates (list concatenation)
    history: Annotated[List[str], operator.add]
```

## Expected Output

Running Example 1 shows:
```
Part 1: State Basics
Reducer Examples:
  operator.add(['message 1'], ['message 2'])
  Result: ['message 1', 'message 2']

Part 2: Simple Linear Workflow
Running workflow...
Final state:
  status: complete
  word_count: 19
```

## Notes

- LangGraph is required: `pip install langgraph`
- For LLM features, set `GOOGLE_API_KEY`
- Examples work without API keys (graceful degradation)
- Checkpointing enables pause/resume workflows
