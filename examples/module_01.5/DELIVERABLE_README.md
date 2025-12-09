# Module 1.5 Deliverable: CLI Agent Automation Toolkit

**Orchestrate CLI AI coding agents for automated development workflows.**

## Features

- Single-agent task execution with Claude Code, Aider, Goose
- Multi-agent pipeline orchestration with dependency management
- Automated code review workflow with multiple perspectives
- Usage metrics tracking and cost analysis
- Auto-detection of available agents

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run demos
python deliverable_cli_agent_toolkit.py demo1  # Single-agent tasks
python deliverable_cli_agent_toolkit.py demo2  # Multi-agent pipeline
python deliverable_cli_agent_toolkit.py demo3  # Code review workflow
python deliverable_cli_agent_toolkit.py demo4  # Usage metrics
python deliverable_cli_agent_toolkit.py help   # Show usage
```

## Supported Agents

| Agent | Command | Key Feature |
|-------|---------|-------------|
| Claude Code | `claude` | Hooks, MCP, slash commands |
| Aider | `aider` | Git-native with auto-commits |
| Goose | `goose` | Extensible toolkits |
| Copilot CLI | `gh copilot` | Command suggestions |

## Pipeline Orchestration

Define multi-step workflows with dependencies:

```python
pipeline = [
    PipelineStep(name="analyze", agent_type=AgentType.CLAUDE_CODE, ...),
    PipelineStep(name="refactor", agent_type=AgentType.AIDER, depends_on=["analyze"]),
    PipelineStep(name="test", agent_type=AgentType.AIDER, depends_on=["refactor"]),
]
```

## Code Review Workflow

Multi-perspective automated code review:
- Security analysis (injection, OWASP top 10)
- Performance review (optimization opportunities)
- Code quality (style, readability, best practices)

## Metrics Tracking

The toolkit tracks:
- Task execution times
- Token usage per agent
- Cost per task
- Success/failure rates

Data stored in `.cli_agent_toolkit/metrics.jsonl`

## Environment Variables

```bash
export ANTHROPIC_API_KEY=...  # For Claude Code
export OPENAI_API_KEY=...     # For Aider/Goose
export GITHUB_TOKEN=...       # For Copilot CLI
```

## Agent Detection

The toolkit auto-detects available agents by checking:
1. Command exists in PATH
2. Required environment variables are set

**Time**: ~3 hours | **Lines**: 814 | **Author**: Neural Dojo
