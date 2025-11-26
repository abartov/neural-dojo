# Module 20 Deliverable: Autonomous Agent Framework

**A comprehensive framework demonstrating advanced agentic AI patterns for building intelligent, self-improving agents.**

## Features

- **Multi-Tier Memory System**: Short-term, long-term, and episodic memory with semantic search
- **Planning Algorithms**: Plan-and-Execute, ReWOO, Tree of Thought strategies
- **Multi-Agent Collaboration**: Supervisor, Swarm, and Debate patterns
- **Self-Improvement**: Reflection-based learning and performance tracking
- **API-Free Operation**: Works without LLM APIs using intelligent simulation

## Quick Start

```bash
# Research Agent with memory and planning
python deliverable_autonomous_agent.py demo1

# Problem Solver with Tree of Thought
python deliverable_autonomous_agent.py demo2

# Multi-Agent Team collaboration
python deliverable_autonomous_agent.py demo3

# Self-Improving Agent with reflection
python deliverable_autonomous_agent.py demo4

# Run all demos
python deliverable_autonomous_agent.py all

# Show help
python deliverable_autonomous_agent.py help
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Autonomous Agent                          │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │ Memory System  │  │ Planning       │  │ Reflection    │  │
│  │ • Short-term   │  │ • Plan-Execute │  │ • Learning    │  │
│  │ • Long-term    │  │ • ReWOO        │  │ • Performance │  │
│  │ • Episodic     │  │ • Tree-of-Thought│ │ • Adaptation │  │
│  └───────┬────────┘  └───────┬────────┘  └───────┬───────┘  │
│          └───────────────────┴───────────────────┘          │
│                              │                               │
│         ┌────────────────────┴────────────────────┐          │
│         │           LLM Interface                 │          │
│         │    (SimulatedLLM for demonstration)     │          │
│         └─────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Memory System

The hybrid memory system mimics human cognitive architecture:

| Memory Type | Purpose | Retention |
|-------------|---------|-----------|
| Short-term | Recent interactions | 20 messages max |
| Long-term | Important facts/knowledge | Persistent |
| Episodic | Task experiences | Event-based |

**Features:**
- Semantic similarity search using embeddings
- Automatic importance-based consolidation
- Context retrieval for decision-making

## Planning Strategies

### Plan-and-Execute
Traditional approach: create full plan, then execute step by step.
```
Plan → Step 1 → Step 2 → ... → Result
```

### ReWOO (Reasoning Without Observation)
Efficient approach: plan with evidence placeholders, batch execution.
```
Plan(#E1, #E2, #E3) → Execute(all) → Substitute(#E1, #E2, #E3)
```

### Tree of Thought
Exploratory approach: generate multiple paths, evaluate, choose best.
```
        ┌─ Path A ─┐
Goal ───┼─ Path B ─┼─── Evaluate → Best Path → Execute
        └─ Path C ─┘
```

## Multi-Agent Patterns

### Supervisor Pattern
Central coordinator delegates to specialized workers.
```
         Supervisor
        /    |    \
    Worker Worker Worker
```

### Swarm Pattern
Agents self-organize and hand off tasks based on specialization.
```
Agent A ←→ Agent B ←→ Agent C
    └──────────────────┘
```

### Debate Pattern
Multiple perspectives argue to reach consensus.
```
Proposition ← Critic A → Synthesis
     ↑                      ↓
Critic B ←──── Judge ──────→ Decision
```

## Self-Improvement

Agents learn through reflection after each task:

1. **Task Execution**: Complete the assigned task
2. **Outcome Analysis**: Evaluate success/failure
3. **Lesson Extraction**: Identify what worked/didn't
4. **Memory Update**: Store insights for future use
5. **Performance Update**: Track improvement over time

## Demo Descriptions

### Demo 1: Research Agent
- Initializes with background knowledge
- Executes research task with full planning
- Shows memory context retrieval
- Demonstrates reflection after completion

### Demo 2: Problem Solver
- Uses Tree of Thought for complex problems
- Compares different planning strategies
- Shows LLM call efficiency differences

### Demo 3: Multi-Agent Team
- Creates supervisor with 3 workers
- Demonstrates task delegation
- Shows swarm handoff behavior
- Displays message flow between agents

### Demo 4: Self-Improving Agent
- Executes 4 tasks sequentially
- Shows performance improvement (0.5 → 0.88)
- Demonstrates memory accumulation
- Displays reflection evolution

## Key Classes

| Class | Purpose |
|-------|---------|
| `AutonomousAgent` | Full-featured agent with memory, planning, reflection |
| `HybridMemorySystem` | Multi-tier memory with semantic search |
| `PlanningEngine` | Multiple planning strategy implementations |
| `SupervisorAgent` | Coordinates worker agents |
| `SwarmAgent` | Self-organizing collaboration |
| `DebateAgent` | Multi-perspective argumentation |

## Performance Metrics

Demo 4 shows performance improvement through learning:

| Task | Performance Score |
|------|-------------------|
| Initial | 0.50 |
| After Task 1 | 0.65 |
| After Task 2 | 0.75 |
| After Task 3 | 0.83 |
| After Task 4 | 0.88 |

## Storage

The framework stores state in `.autonomous_agent/`:
- `agent_state.json` - Agent configuration and metrics
- `memory_state.json` - Memory contents
- `*_memory.json` - Per-agent memory files

## Extension Points

To add a real LLM backend:

```python
class RealLLM:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# Use in agent
agent = AutonomousAgent("MyAgent", goals, llm=RealLLM(API_KEY))
```

## Related Examples

- `01_agent_memory_systems.py` - Deep dive into memory architectures
- `02_planning_algorithms.py` - Detailed planning algorithm implementations
- `03_multi_agent_collaboration.py` - Multi-agent communication patterns

**Time**: ~4 hours | **Lines**: 750+ | **Author**: Neural Dojo
