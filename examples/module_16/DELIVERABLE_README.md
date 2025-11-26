# Module 16 Deliverable: Tool Orchestrator

**A comprehensive tool orchestration system for building AI agents with custom tools.**

## Features

- **Tool Registry**: Manage and categorize tools with validation
- **Tracked Execution**: All tool calls logged with latency metrics
- **Agent Builder**: Create agents with custom tool combinations
- **Performance Analytics**: Benchmark and analyze tool performance
- **Interactive Chat**: Chat with an agent using all tools

## Quick Start

```bash
# No API key needed for demo1 and demo3
python deliverable_tool_orchestrator.py demo1  # Tool registry & execution
python deliverable_tool_orchestrator.py demo3  # Performance analytics

# Requires API key for demo2 and chat
export GOOGLE_API_KEY="your-key"
python deliverable_tool_orchestrator.py demo2  # Agent execution
python deliverable_tool_orchestrator.py chat   # Interactive chat
```

## Built-in Tools

| Tool | Category | Description |
|------|----------|-------------|
| `calculator` | math | Evaluate math expressions |
| `string_processor` | data | Text operations (upper, lower, length, etc.) |
| `datetime_tool` | data | Date/time functions |
| `unit_converter` | math | Convert between units (km/mi, kg/lb, etc.) |
| `json_helper` | data | JSON validation, formatting, parsing |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Tool Orchestrator                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  Tool Registry  │    │ Execution       │                 │
│  │  - Built-in     │    │ Tracker         │                 │
│  │  - Custom       │    │  - Latency      │                 │
│  │  - Categories   │───▶│  - Success/Fail │                 │
│  └─────────────────┘    │  - Analytics    │                 │
│          │              └─────────────────┘                 │
│          ▼                       │                          │
│  ┌─────────────────┐            │                          │
│  │ Agent Builder   │◀───────────┘                          │
│  │  - Config       │                                        │
│  │  - LangChain    │                                        │
│  │  - Multi-model  │                                        │
│  └─────────────────┘                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Storage

The tool orchestrator persists data to `.tool_orchestrator/`:

- `tools.json` - Tool definitions and usage stats
- `executions.json` - Execution history (last 1000)
- `analytics.json` - Computed analytics

## Example: Creating a Custom Agent

```python
from deliverable_tool_orchestrator import (
    ToolRegistry, ExecutionTracker, TrackedToolExecutor, AgentBuilder
)

# Initialize components
registry = ToolRegistry()
tracker = ExecutionTracker()
executor = TrackedToolExecutor(registry, tracker)
builder = AgentBuilder(registry, executor)

# Create custom agent
config = builder.create_agent(
    name="math_helper",
    tools=["calculator", "unit_converter"],
    system_prompt="You are a math helper. Use tools for calculations.",
    provider="google"  # or "anthropic"
)

# Get LangChain agent
agent = builder.get_langchain_agent(config)

# Use the agent
result = agent.invoke({"input": "What is 15 * 7?"})
print(result["output"])
```

## Performance Metrics

After running demo3, you'll see metrics like:

```
Tool                 Calls    Success  Avg (ms)   Errors
------------------------------------------------------------
calculator           10       10       0.14       0
string_processor     10       10       0.12       0
datetime_tool        10       10       0.13       0
```

## Key Concepts Demonstrated

1. **Tool Registry Pattern** - Central management of tool definitions
2. **Execution Tracking** - Observability for debugging and optimization
3. **Agent Configuration** - Declarative agent setup
4. **Multi-model Support** - Works with Gemini and Claude
5. **Graceful Degradation** - Works without API keys for local tools

---

**Time**: ~4 hours | **Lines**: 700+ | **Author**: Neural Dojo Module 16
