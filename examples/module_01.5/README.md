# Module 1.5 Examples: CLI AI Coding Agents

This directory contains working examples and the deliverable for Module 1.5: CLI AI Coding Agents.

## Overview

This module explores command-line AI coding agents that integrate directly into your terminal workflow. Unlike IDE-based agents, CLI agents are composable, scriptable, and work anywhere you have a terminal—including remote servers and CI/CD pipelines.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Tools Covered

- **Claude Code**: Anthropic's official CLI with hooks, MCP, and slash commands
- **Aider**: Git-native AI pair programming with auto-commits
- **Goose**: Block's extensible agent with toolkits
- **GitHub Copilot CLI**: Command suggestion tool

## Deliverable

**File**: `deliverable_cli_agent_toolkit.py`

A comprehensive toolkit for working with CLI AI coding agents:

```bash
# Run demos
python deliverable_cli_agent_toolkit.py demo1  # Single-agent task
python deliverable_cli_agent_toolkit.py demo2  # Multi-agent pipeline
python deliverable_cli_agent_toolkit.py demo3  # Automated code review
python deliverable_cli_agent_toolkit.py demo4  # Usage metrics
python deliverable_cli_agent_toolkit.py help   # Show usage
```

## Examples

### Example 1: Claude Code Hooks
Configuration examples for Claude Code hooks system.

### Example 2: Aider Workflows
Scripts demonstrating Aider's git-native workflow.

### Example 3: Multi-Agent Pipelines
Combining multiple CLI agents for complex tasks.

### Example 4: CI/CD Integration
GitHub Actions workflow for AI-powered code review.

## Notes

- Requires appropriate API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)
- Some tools (Aider, Goose) support local models via Ollama
- Claude Code requires Anthropic API access

## Related Theory

See `docs/curriculum/notes/module_01.5_cli_ai_coding_agents.md` for full theory coverage.
