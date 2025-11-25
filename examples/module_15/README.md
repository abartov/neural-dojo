# Module 15: LangChain Fundamentals

This directory contains examples for LangChain, the most popular framework for building LLM applications.

## Overview

LangChain provides abstractions for:
- **Prompts**: Templates for LLM instructions
- **Chains**: Sequences of operations
- **Memory**: Conversation history management
- **LCEL**: Modern composable pipelines

## Examples

### 1. Prompts and Templates (`01_prompts_and_templates.py`)

```bash
python 01_prompts_and_templates.py
```

Covers:
- Basic PromptTemplate
- ChatPromptTemplate for chat models
- Few-shot prompts with examples
- Partial prompts

### 2. Chains and LCEL (`02_chains_and_lcel.py`)

```bash
python 02_chains_and_lcel.py
```

Covers:
- Simple LCEL chains (prompt | model | parser)
- Sequential chains
- Parallel execution with RunnableParallel
- Streaming responses
- Async execution

### 3. Memory Systems (`03_memory_systems.py`)

```bash
python 03_memory_systems.py
```

Covers:
- ConversationBufferMemory
- ConversationBufferWindowMemory
- ConversationSummaryMemory
- Memory comparison

### 4. LangChain Toolkit (Deliverable)

```bash
python deliverable_langchain_toolkit.py demo1  # Conversational chatbot
python deliverable_langchain_toolkit.py demo2  # LCEL pipeline
python deliverable_langchain_toolkit.py demo3  # Multi-model router
python deliverable_langchain_toolkit.py interactive  # Interactive chat
```

## Prerequisites

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
```

## Key Concepts

### LCEL (LangChain Expression Language)

The modern, recommended way to build chains:

```python
from langchain.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

# Compose with pipe operator
chain = prompt | model | parser

# Invoke
result = chain.invoke({"topic": "AI"})

# Stream
for chunk in chain.stream({"topic": "AI"}):
    print(chunk, end="")
```

### Memory Types

| Type | Stores | Best For |
|------|--------|----------|
| Buffer | All messages | Short conversations |
| BufferWindow | Last K messages | Chatbots |
| Summary | Compressed summary | Long conversations |
| SummaryBuffer | Summary + recent | Most applications |

## When to Use LangChain

**Use it for:**
- RAG systems
- Conversational AI with memory
- Multi-step LLM workflows
- Rapid prototyping

**Skip it for:**
- Simple single prompts (use raw API)
- Maximum control needed
- Minimal dependencies required

## Further Reading

- [LangChain Documentation](https://python.langchain.com/)
- [LCEL Guide](https://python.langchain.com/docs/expression_language/)
- [Memory Types](https://python.langchain.com/docs/modules/memory/)

---

**Time**: 6-7 hours | **Module**: 15 of 56 | **Phase**: 4 - Frameworks & Agents
