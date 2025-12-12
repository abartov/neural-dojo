---
hide:
  - toc
---

# Getting Started

Welcome to Neural Dojo! This guide will help you set up your environment and begin your journey from zero to AI guru.

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed
- **Git** for version control
- **A code editor** (VS Code recommended with AI extensions)
- **API keys** for OpenAI and/or Anthropic (for most modules)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/krisztiankoos/neural-dojo.git
cd neural-dojo
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Set Up API Keys

Create a `.env` file in the project root:

```bash
# Required for most modules
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional - for specific modules
HUGGINGFACE_TOKEN=hf_your-token-here
QDRANT_API_KEY=your-qdrant-key
```

### 4. Install Base Dependencies

```bash
pip install -r requirements.txt
```

## Learning Path Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 0: Prerequisites                                         │
│  Set up your environment and tools                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  Phase 1: AI-Native Development (9 modules)                     │
│  Master AI coding tools, prompt engineering, debugging          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  Phase 2: Generative AI (5 modules)                             │
│  Understand LLMs, tokenization, embeddings                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  Phase 3: Vector Search & RAG (4 modules)                       │
│  Build intelligent search and retrieval systems                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  Phase 4: Frameworks & Agents (7 modules)                       │
│  Master LangChain, LangGraph, and AI agents                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  Phase 5-12: Advanced Topics                                    │
│  Deep Learning, MLOps, Safety, and more...                      │
└─────────────────────────────────────────────────────────────────┘
```

## Recommended Order

We recommend following the modules in order, as each phase builds on the previous:

1. **Start with [Prerequisites](curriculum/notes/module_00_prerequisites.md)** - Essential setup
2. **Move to [AI Coding Tools](curriculum/notes/module_01.1_ai_coding_tools.md)** - Begin using AI assistants
3. **Learn [Prompt Engineering](curriculum/notes/module_02_prompt_engineering.md)** - Master the art of prompting
4. **Continue through the curriculum** - Each module is designed to build on previous knowledge

## Time Commitment

| Pace | Hours/Week | Duration |
|------|------------|----------|
| Intensive | 6-8 hours | ~40 weeks |
| Steady | 4-5 hours | ~52 weeks |
| Casual | 2-3 hours | ~80 weeks |

## Module Structure

Each module includes:

- **Theory** - Deep explanations with real-world examples
- **Hands-On Practice** - Step-by-step exercises
- **Deliverables** - Concrete projects to build
- **Further Reading** - Additional resources

Look for :crystal_ball: **Heureka Moments** - transformative insights that fundamentally change how you think about AI!

## Tips for Success

!!! tip "Active Learning"
    Don't just read - build! Each module has hands-on exercises and deliverables. The real learning happens when you write code.

!!! tip "Take Notes"
    Keep a learning journal. Document your insights, questions, and "aha!" moments.

!!! tip "Experiment"
    Try variations of the examples. Break things intentionally to understand how they work.

!!! tip "Build Projects"
    Apply concepts to your own projects. The curriculum connects to real-world applications.

## Get Help

- **GitHub Issues**: [Report bugs or ask questions](https://github.com/krisztiankoos/neural-dojo/issues)
- **Discussions**: Join the community discussions on GitHub

---

<div style="text-align: center; margin-top: 2rem;">
<a href="curriculum/notes/module_00_prerequisites/" class="md-button md-button--primary">Start with Prerequisites</a>
</div>
