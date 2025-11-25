# Module 15 Deliverable: LangChain Toolkit

**Build conversational AI with memory, LCEL pipelines, and intelligent model routing.**

*Updated for LangChain 1.1.0+ (November 2025)*

## Features

- **Conversational Chatbot**: Memory-enabled conversations using RunnableWithMessageHistory
- **LCEL Pipelines**: Modern LangChain Expression Language with streaming
- **Multi-Model Router**: Route queries to appropriate models based on complexity
- **Session Persistence**: Save and load conversation history as JSON
- **Interactive Mode**: Real-time chat with memory commands
- **Multi-Provider Support**: Works with Gemini (Google) or Claude (Anthropic)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (choose one)
export GOOGLE_API_KEY="your-gemini-key"    # Recommended - fast and affordable
# OR
export ANTHROPIC_API_KEY="your-claude-key"

# Run demos
python deliverable_langchain_toolkit.py demo1       # Conversational chatbot with memory
python deliverable_langchain_toolkit.py demo2       # LCEL pipelines (simple, parallel, streaming)
python deliverable_langchain_toolkit.py demo3       # Multi-model routing by complexity
python deliverable_langchain_toolkit.py interactive # Interactive chat mode
python deliverable_langchain_toolkit.py help        # Show help
```

## Components

### 1. Conversational Chatbot (`demo1`)

Demonstrates LangChain's modern memory systems:

```python
# Uses RunnableWithMessageHistory (LangChain 1.1.0+)
# - Automatic message history tracking
# - Session-based storage for multi-user support
# - Built-in message trimming for long conversations
```

**Features:**
- Multi-turn conversation with context retention
- Automatic memory summarization when buffer exceeds limit
- Session persistence to JSON files

### 2. LCEL Pipelines (`demo2`)

Modern LangChain Expression Language patterns:

```python
# Simple chain
chain = prompt | model | parser

# Parallel execution
analysis = RunnableParallel(
    sentiment=sentiment_chain,
    keywords=keywords_chain,
    summary=summary_chain
)

# Streaming
for chunk in chain.stream({"topic": "AI"}):
    print(chunk, end="")
```

**Demonstrates:**
- Pipe operator for clean composition
- Parallel execution for concurrent LLM calls
- Streaming responses for real-time output

### 3. Multi-Model Router (`demo3`)

Intelligent routing to optimize cost and quality:

```
Simple query → Cheaper/faster model
Complex query → More capable model
```

**Strategy:**
- Classifier determines query complexity
- Routes to appropriate model
- Can reduce costs by 50-70% in production

## Memory Types Reference

| Type | Token Usage | Recall Quality | Best For |
|------|-------------|----------------|----------|
| Buffer | High (grows) | Perfect | Short conversations |
| BufferWindow | Medium (fixed) | Recent only | Chatbots |
| Summary | Low | Compressed | Long conversations |
| SummaryBuffer | Medium | Balanced | Most applications |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   LangChain Toolkit                          │
├─────────────────────────────────────────────────────────────┤
│  ConversationalChatbot     │  Memory-enabled conversations  │
│  LCELPipelineBuilder       │  Modern chain composition      │
│  MultiModelRouter          │  Complexity-based routing      │
├─────────────────────────────────────────────────────────────┤
│  Session Storage (.langchain_toolkit/)                       │
│  - JSON persistence                                          │
│  - Conversation history                                      │
│  - Session metadata                                          │
└─────────────────────────────────────────────────────────────┘
```

## Interactive Mode Commands

```
/memory  - Show current memory summary
/save    - Save conversation to disk
/quit    - Exit and save conversation
```

## Example Output

### Demo 1: Conversational Chatbot

```
📤 Starting conversation...

👤 Human: Hi! My name is Alice and I'm a Python developer.
🤖 Assistant: Hello Alice! Nice to meet you...

👤 Human: I've been coding for about 5 years, mostly backend.
🤖 Assistant: That's great experience! Backend development...

👤 Human: What should I focus on given my background?
🤖 Assistant: Given your 5 years of Python backend experience, Alice...

✅ The chatbot remembers context across messages!
```

### Demo 3: Multi-Model Router

```
📤 Query: What is the capital of France?
   🎯 Complexity: simple
   🤖 Model: Gemini 1.5 Flash (simple)
   📝 Response: Paris...

📤 Query: Design a microservices architecture for e-commerce...
   🎯 Complexity: complex
   🤖 Model: Gemini 1.5 Flash (complex)
   📝 Response: Here's a comprehensive architecture...
```

## When to Use LangChain

**Use LangChain for:**
- RAG systems (excellent retriever integrations)
- Conversational AI with memory
- Multi-step LLM workflows
- Agent-based applications
- Rapid prototyping

**Skip LangChain for:**
- Simple single-prompt tasks (use raw API)
- Maximum control needed
- Minimal dependencies required

## Files

```
examples/module_15/
├── deliverable_langchain_toolkit.py  # Main toolkit (545+ lines)
├── DELIVERABLE_README.md             # This file
├── requirements.txt                  # Dependencies
├── README.md                         # Module overview
├── 01_prompts_and_templates.py       # Prompt examples
├── 02_chains_and_lcel.py             # Chain examples
├── 03_memory_systems.py              # Memory examples
└── .langchain_toolkit/               # Session storage (auto-created)
```

## Requirements

- Python 3.10+
- API key: `GOOGLE_API_KEY` (Gemini) or `ANTHROPIC_API_KEY` (Claude)
- LangChain 1.1.0+ ecosystem packages

```bash
# For Gemini (recommended)
pip install langchain-core langchain-google-genai pydantic

# For Claude
pip install langchain-core langchain-anthropic pydantic
```

## Further Reading

- [LangChain Documentation](https://python.langchain.com/)
- [LCEL Guide](https://python.langchain.com/docs/expression_language/)
- [Memory Types](https://python.langchain.com/docs/modules/memory/)

---

**Time**: ~6-7 hours | **Lines**: 545+ | **Module**: 15 of 56 | **Author**: Neural Dojo
