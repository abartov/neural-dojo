# Module 16: LangChain Tools & Function Calling

This module teaches you how to extend LLM capabilities using tools and function calling.

## Learning Objectives

- Understand function calling / tool use protocols
- Build custom LangChain tools
- Create tool-calling agents
- Handle tool execution errors
- Implement tool selection strategies

## Examples

### Example 1: Tool Basics (`01_tool_basics.py`)
Learn the three ways to create tools in LangChain:
- `@tool` decorator (simplest)
- `StructuredTool` (more control)
- `BaseTool` subclass (maximum flexibility)

```bash
python 01_tool_basics.py
```

### Example 2: Custom Tools (`02_custom_tools.py`)
Build production-ready tools:
- Developer tools (file operations, code search)
- API integration (weather, web search)
- Security patterns (input validation, whitelisting)
- Error handling

```bash
python 02_custom_tools.py
```

### Example 3: Tool-Calling Agents (`03_tool_calling_agents.py`)
Create agents that use tools intelligently:
- Basic agent with AgentExecutor
- Conversational agent with memory
- Multi-tool queries

```bash
# Requires API key
export GOOGLE_API_KEY="your-key"
python 03_tool_calling_agents.py
```

## Deliverable: Tool Orchestrator

A comprehensive system for managing tools and building agents.

```bash
python deliverable_tool_orchestrator.py demo1  # Tool registry
python deliverable_tool_orchestrator.py demo2  # Agent execution
python deliverable_tool_orchestrator.py demo3  # Analytics
python deliverable_tool_orchestrator.py chat   # Interactive mode
```

See [DELIVERABLE_README.md](DELIVERABLE_README.md) for full documentation.

## Prerequisites

```bash
pip install -r requirements.txt
```

For agent demos, set an API key:
```bash
export GOOGLE_API_KEY="your-key"    # For Gemini
# OR
export ANTHROPIC_API_KEY="your-key"  # For Claude
```

## Key Concepts

1. **Tool Schema** - JSON definition of tool name, description, parameters
2. **@tool Decorator** - Converts Python functions to LangChain tools
3. **AgentExecutor** - Runs the agent loop (think → act → observe)
4. **Tool Selection** - LLM chooses tools based on descriptions

## Next Module

**Module 17: Chain-of-Thought & Reasoning** - Learn how to make agents "think out loud" for better results.
