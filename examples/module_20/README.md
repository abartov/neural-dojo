# Module 20: Advanced Agentic AI Examples

This directory contains working code examples for Module 20: Advanced Agentic AI.

## Prerequisites

```bash
pip install -r requirements.txt
```

No API keys required - all examples use intelligent simulation for demonstration.

## Examples

### Example 1: Agent Memory Systems
**File**: `01_agent_memory_systems.py`
**Description**: Demonstrates multi-tier memory architectures for AI agents including:
- ConversationBuffer (short-term memory)
- VectorMemory (long-term semantic memory)
- SummaryMemory (compressed historical memory)
- HybridMemory (combining all approaches)

```bash
python 01_agent_memory_systems.py demo1  # Short-term memory
python 01_agent_memory_systems.py demo2  # Long-term vector memory
python 01_agent_memory_systems.py demo3  # Summary memory
python 01_agent_memory_systems.py demo4  # Hybrid memory system
```

### Example 2: Planning Algorithms
**File**: `02_planning_algorithms.py`
**Description**: Implements various planning strategies for autonomous agents:
- Plan-and-Execute (traditional step-by-step)
- ReWOO (Reasoning Without Observation)
- Tree of Thought (exploratory reasoning)

```bash
python 02_planning_algorithms.py demo1  # Plan-and-Execute
python 02_planning_algorithms.py demo2  # ReWOO strategy
python 02_planning_algorithms.py demo3  # Tree of Thought
python 02_planning_algorithms.py demo4  # Compare all strategies
```

### Example 3: Multi-Agent Collaboration
**File**: `03_multi_agent_collaboration.py`
**Description**: Demonstrates multi-agent collaboration patterns:
- Supervisor pattern (central coordination)
- Swarm pattern (self-organizing teams)
- Debate pattern (adversarial reasoning)

```bash
python 03_multi_agent_collaboration.py demo1  # Supervisor pattern
python 03_multi_agent_collaboration.py demo2  # Swarm collaboration
python 03_multi_agent_collaboration.py demo3  # Multi-agent debate
python 03_multi_agent_collaboration.py demo4  # Compare all patterns
```

## Deliverable

### Autonomous Agent Framework
**File**: `deliverable_autonomous_agent.py`
**Documentation**: `DELIVERABLE_README.md`

A comprehensive framework combining all advanced agentic AI patterns:
- Multi-tier memory system with semantic search
- Multiple planning strategies
- Multi-agent collaboration capabilities
- Self-improvement through reflection

```bash
python deliverable_autonomous_agent.py demo1  # Research Agent
python deliverable_autonomous_agent.py demo2  # Problem Solver
python deliverable_autonomous_agent.py demo3  # Multi-Agent Team
python deliverable_autonomous_agent.py demo4  # Self-Improving Agent
python deliverable_autonomous_agent.py all    # Run all demos
```

## Expected Output

### Memory System Demo
```
=== Demo 1: Conversation Buffer Memory ===
📝 Simulating customer support conversation...

[Turn 1] User: What are your store hours?
Memory context (recent 10 messages):
  [assistant]: Hello! I'm here to help with any questions...
  [user]: What are your store hours?
```

### Planning Demo
```
=== Demo 4: Compare Planning Strategies ===

📊 Strategy Comparison Results:
| Pattern           | LLM Calls | Steps | Best For                    |
| Plan-and-Execute  |         3 |     5 | Complex multi-step tasks    |
| ReWOO             |         2 |     5 | Cost-efficient, parallel    |
| Tree of Thought   |        10 |     3 | Complex reasoning problems  |
```

### Multi-Agent Demo
```
=== Demo 1: Supervisor Pattern ===
🎯 Task: Research the impact of AI on software development...

📋 Supervisor Analysis:
  Identified sub-tasks: 3

📨 Message Flow (6 messages):
  supervisor → researcher: [task]
  researcher → supervisor: [result]
```

## Architecture Overview

```
Module 20 Examples
├── 01_agent_memory_systems.py     # Memory architectures
├── 02_planning_algorithms.py      # Planning strategies
├── 03_multi_agent_collaboration.py # Agent communication
└── deliverable_autonomous_agent.py # Complete framework
```

## Key Concepts

### Memory Types
| Type | Purpose | Persistence |
|------|---------|-------------|
| Short-term | Recent context | Session |
| Long-term | Important facts | Permanent |
| Episodic | Experiences | Event-based |
| Summary | Compressed history | Periodic |

### Planning Strategies
| Strategy | LLM Calls | Best For |
|----------|-----------|----------|
| Plan-Execute | High | Complex tasks |
| ReWOO | Low | Cost efficiency |
| Tree of Thought | Variable | Creative problems |

### Agent Patterns
| Pattern | Coordination | Scalability |
|---------|--------------|-------------|
| Supervisor | Centralized | Limited |
| Swarm | Distributed | High |
| Debate | Adversarial | Medium |

## Notes

- All examples run without API keys using intelligent simulation
- Simulated LLM provides realistic responses for demonstration
- Storage directories (`.agent_memory/`, `.planning_cache/`, etc.) are created automatically
- For production use, replace SimulatedLLM with real API calls

## Theory Reference

For in-depth explanations, see:
`docs/curriculum/notes/module_20_advanced_agentic_ai.md`
