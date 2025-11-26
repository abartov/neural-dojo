# Module 19 Examples: LlamaIndex & Alternative Frameworks

This directory contains working code examples for Module 19, exploring LlamaIndex and comparing it with alternative AI frameworks.

## Prerequisites

```bash
pip install -r requirements.txt
```

For full functionality:
```bash
export GOOGLE_API_KEY="your-api-key"
```

## Examples

### Example 1: LlamaIndex Fundamentals
**File**: `01_llamaindex_fundamentals.py`
**Description**: Core LlamaIndex concepts - documents, nodes, indexes, and query engines.

```bash
python 01_llamaindex_fundamentals.py
```

**Topics covered**:
- Document loading and creation
- Node parsing (chunking)
- Index types (Vector, Summary, Keyword)
- Query engines and chat engines
- Persistence and storage

### Example 2: Framework Comparison
**File**: `02_framework_comparison.py`
**Description**: Side-by-side comparison of LangChain and LlamaIndex.

```bash
python 02_framework_comparison.py
```

**Topics covered**:
- Code complexity comparison
- Feature comparison matrix
- Performance benchmarking
- Integration patterns
- Decision framework

### Example 3: Multi-Agent Frameworks
**File**: `03_multi_agent_frameworks.py`
**Description**: Overview of CrewAI, AutoGen, and other multi-agent frameworks.

```bash
python 03_multi_agent_frameworks.py
```

**Topics covered**:
- CrewAI role-based teams
- AutoGen conversational agents
- Framework comparison
- Selection guidelines

## Deliverable

### Framework Selector Toolkit
**File**: `deliverable_framework_selector.py`
**Description**: Interactive tool for selecting the right AI framework.

```bash
# Interactive recommendation
python deliverable_framework_selector.py recommend

# Compare frameworks
python deliverable_framework_selector.py compare

# Quick analysis
python deliverable_framework_selector.py analyze

# Full demo
python deliverable_framework_selector.py demo
```

See `DELIVERABLE_README.md` for complete documentation.

## Framework Quick Reference

| Framework | Best For | Learning Curve |
|-----------|----------|----------------|
| **LlamaIndex** | RAG, Data indexing | Medium |
| **LangChain** | Agents, Flexibility | High |
| **LangGraph** | Stateful workflows | High |
| **CrewAI** | Multi-agent teams | Low |
| **AutoGen** | Research, Coding | Medium |

## Key Concepts

### LlamaIndex Basics

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load and index
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Query
response = index.as_query_engine().query("What is X?")
```

### Framework Selection

- **RAG-focused** → LlamaIndex
- **Agent-focused** → LangChain + LangGraph
- **Multi-agent** → CrewAI or AutoGen
- **Enterprise** → Semantic Kernel

## Notes

- LlamaIndex requires ~70% less code for basic RAG
- LangChain offers more flexibility for complex agents
- CrewAI is great for quick multi-agent prototypes
- Consider using multiple frameworks together
