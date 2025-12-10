# Module 1.5: CLI AI Coding Agents

**Last Updated**: 2025-12-09
**Status**: 🟡 In Progress
**Duration**: 4-6 hours
**Prerequisites**: Module 01 (AI-Driven Development), Module 1.4 (Agent-First IDEs)

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand the advantages of CLI-based AI coding agents over IDE integrations
- Master Claude Code's hooks, MCP servers, and slash commands
- Use Aider for git-native AI pair programming
- Build automated workflows combining multiple CLI agents
- Know when to choose CLI agents vs IDE agents for specific tasks

---

## 📖 Theory

### The Power of the Command Line

While agent-first IDEs like Windsurf and Cursor wrap AI capabilities in polished GUIs, CLI-based AI coding agents take a fundamentally different approach. They integrate directly into your terminal workflow—where many developers already live.

**Why CLI matters:**

Think of CLI AI agents like having a skilled assistant who can follow you anywhere in your house. IDE-based agents are like assistants who only work in your living room—fantastic when you're there, but useless when you need to fix something in the basement (a remote server), the garage (a container), or the attic (a legacy system). CLI agents go wherever your terminal goes.

Think about how you actually work. You're SSH'd into a server fixing a production issue. You're running tests in one terminal, watching logs in another. You're inside a tmux session with six panes. An IDE can't follow you there—but a CLI agent can.

CLI agents are also inherently composable. They read stdin, write stdout, and respect the Unix philosophy. You can pipe code through them, script them, chain them together. They become part of your automation toolkit, not a separate application you switch to.

**The terminal renaissance:**

There's been a quiet revolution in terminal tooling. Modern terminals like Warp, Ghostty, and WezTerm support images, rich text, and interactive widgets. Tools like `bat`, `exa`, and `delta` have modernized the classics. Into this environment, CLI AI agents feel native—they're just another powerful tool in your shell.

---

## 🔧 The CLI Agent Landscape

### Claude Code: Anthropic's Official CLI

**What it is:** Claude Code is Anthropic's official command-line tool for interacting with Claude. It's designed as an "agentic" coding assistant that can read files, edit code, run commands, and manage complex multi-step tasks—all from your terminal.

> **💡 Did You Know?**
>
> Claude Code was released by Anthropic in February 2025, marking the company's first official coding tool. Unlike third-party integrations, Claude Code is built by the same team that builds Claude itself, giving it deep access to Claude's capabilities. The tool is open-source (Apache 2.0 license), which means you can inspect exactly how it works, contribute improvements, or fork it for custom use cases. Anthropic designed it with enterprise security in mind—Claude Code never stores your code on Anthropic's servers beyond what's needed for the API call, and all MCP server connections stay local to your machine.

**Architecture:**

```
┌──────────────────────────────────────────────────────┐
│                    Your Terminal                      │
├──────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │   Claude   │──│    Tools    │──│ MCP Servers  │  │
│  │   Code     │  │  (built-in) │  │ (extensible) │  │
│  └────────────┘  └─────────────┘  └──────────────┘  │
│        │                │                 │          │
│        ▼                ▼                 ▼          │
│  ┌─────────┐    ┌──────────────┐  ┌─────────────┐   │
│  │  Bash   │    │  Read/Write  │  │  Custom     │   │
│  │ Commands│    │  Edit Files  │  │  APIs/DBs   │   │
│  └─────────┘    └──────────────┘  └─────────────┘   │
└──────────────────────────────────────────────────────┘
```

**Key Concepts:**

**1. Hooks System**

Hooks let you run custom shell commands in response to Claude Code events. They're defined in your settings and execute automatically.

```json
// ~/.config/claude-code/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "command": "prettier --write $FILE_PATH"
      }
    ],
    "PreCommit": [
      {
        "command": "npm run lint"
      }
    ]
  }
}
```

Hook types:
- **PreToolUse**: Before Claude uses a tool (validate, block, modify)
- **PostToolUse**: After tool use (format, log, notify)
- **PreCommit**: Before git commits (lint, test)
- **UserPromptSubmit**: When user sends a message

**2. MCP (Model Context Protocol) Servers**

Think of MCP servers like giving Claude Code a toolbelt. Without MCP, Claude can read files and run commands—like a worker with just their hands. With MCP, you're adding specialized tools: a database wrench, a GitHub screwdriver, a Kubernetes hammer. Each MCP server is a new tool that makes Claude capable of handling a new type of task.

MCP extends Claude Code's capabilities by connecting it to external services. Instead of just reading files, Claude can query databases, call APIs, or interact with any custom service.

```json
// MCP server configuration
{
  "mcpServers": {
    "database": {
      "command": "mcp-postgres",
      "args": ["postgresql://localhost/mydb"]
    },
    "github": {
      "command": "mcp-github",
      "env": {"GITHUB_TOKEN": "..."}
    }
  }
}
```

With MCP, Claude Code becomes infinitely extensible. Need it to query your company's internal APIs? Write an MCP server. Want it to manage your Kubernetes cluster? There's an MCP for that.

**3. Slash Commands**

Custom commands defined as markdown files that expand into prompts:

```markdown
<!-- .claude/commands/review.md -->
Review this code for:
1. Security vulnerabilities
2. Performance issues
3. Best practices violations

Focus on: $ARGUMENTS
```

Usage: `/review authentication flow`

**4. CLAUDE.md Project Context**

Every project can have a `CLAUDE.md` file that Claude reads automatically. This becomes your project's AI briefing document—coding standards, architecture decisions, common pitfalls, team conventions.

```markdown
# CLAUDE.md

## Project Overview
This is a FastAPI backend serving React frontend.

## Conventions
- Use pydantic for all data validation
- Async functions for all I/O
- Tests in pytest, aim for 80% coverage

## Don't
- Never commit .env files
- Don't use raw SQL, always use SQLAlchemy ORM
```

---

### Aider: Git-Native AI Pair Programming

**What it is:** Aider is an open-source AI pair programming tool that works directly in your terminal. Its killer feature: it's deeply integrated with git, automatically committing changes with meaningful messages.

**Did You Know?** Aider was created by Paul Gauthier in 2023. It consistently ranks in the top 3 on the SWE-bench coding benchmark, often outperforming commercial alternatives. The project has over 20,000 GitHub stars and processes hundreds of thousands of conversations monthly.

**Architecture Philosophy:**

```
┌─────────────────────────────────────────────┐
│               Your Repository               │
├─────────────────────────────────────────────┤
│                                             │
│   ┌─────────┐    ┌─────────────────────┐   │
│   │  Aider  │───▶│  Git Working Tree   │   │
│   │         │◀───│                     │   │
│   └─────────┘    └─────────────────────┘   │
│        │                   │                │
│        ▼                   ▼                │
│   ┌─────────┐    ┌─────────────────────┐   │
│   │   LLM   │    │  Automatic Commits  │   │
│   │  (any)  │    │  with messages      │   │
│   └─────────┘    └─────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

**Key Features:**

**1. Git-First Workflow**

Think of Aider's git integration like having a meticulous lab notebook keeper. Scientists don't just do experiments—they document every step so they can reproduce results or understand what went wrong. Aider automatically records every code change in git, creating a detailed history you can traverse, undo, or learn from.

Every change Aider makes is automatically committed:

```bash
$ aider
> Add input validation to the User model

# Aider edits the file and commits:
# "feat: Add input validation to User model"
# - Added email format validation
# - Added password strength requirements
# - Added age range check
```

You can always `git diff HEAD~1` to see exactly what changed, or `git revert HEAD` to undo.

**2. Multi-File Editing**

Aider maintains a "chat context" of files it's working with:

```bash
$ aider src/models/user.py src/api/routes.py tests/test_user.py

> Refactor User to use dataclass and update all usages
```

It understands relationships between files and makes coordinated changes across all of them.

**3. Voice Mode**

Aider supports voice input—speak your requirements, and it codes:

```bash
$ aider --voice
🎤 Listening...
"Add a rate limiting middleware that allows 100 requests per minute per IP"
```

**4. Architect Mode**

For larger changes, Aider can plan before implementing:

```bash
$ aider --architect

> Implement user authentication with JWT

Planning...
1. Create auth service module
2. Add JWT utility functions
3. Create login/register endpoints
4. Add auth middleware
5. Update user model with password hash
6. Add tests

Proceed? [y/n]
```

**Model Flexibility:**

Aider works with virtually any LLM:

```bash
# OpenAI
$ aider --model gpt-4o

# Anthropic
$ aider --model claude-3-5-sonnet

# Local models via Ollama
$ aider --model ollama/deepseek-coder

# Any OpenAI-compatible API
$ aider --openai-api-base http://localhost:8000/v1
```

---

### Goose: Block's Open-Source Agent

**What it is:** Goose is an open-source AI agent from Block (formerly Square). It emphasizes extensibility through "toolkits"—modular packages that give Goose new capabilities.

**Did You Know?** Block released Goose in late 2024 as part of their commitment to open-source AI tooling. The name comes from the idea of a "goose that lays golden eggs"—an agent that produces valuable code.

**Architecture:**

```
┌───────────────────────────────────────┐
│              Goose CLI                │
├───────────────────────────────────────┤
│  ┌─────────────────────────────────┐  │
│  │         Core Agent Loop         │  │
│  │  (plan → execute → observe)     │  │
│  └─────────────────────────────────┘  │
│                  │                    │
│  ┌───────────────┴───────────────┐   │
│  │         Toolkits              │   │
│  ├──────┬──────┬──────┬─────────┤   │
│  │ Git  │Shell │ Web  │ Custom  │   │
│  └──────┴──────┴──────┴─────────┘   │
└───────────────────────────────────────┘
```

**Toolkit System:**

Goose's power comes from toolkits. Each toolkit is a self-contained package of tools:

```python
# Custom toolkit example
from goose.toolkit import Toolkit, tool

class DatabaseToolkit(Toolkit):
    """Tools for database operations."""

    @tool
    def query(self, sql: str) -> str:
        """Execute a SQL query and return results."""
        return self.db.execute(sql)

    @tool
    def schema(self, table: str) -> str:
        """Get the schema for a table."""
        return self.db.get_schema(table)
```

**Built-in Toolkits:**
- **developer**: File operations, code editing
- **screen**: Take and analyze screenshots
- **github**: PR creation, issue management
- **jira**: Ticket management
- **browser**: Web automation

---

### Other Notable CLI Agents

**OpenAI Codex CLI** (Historical)

OpenAI's original Codex model had a CLI interface that influenced many successors. While deprecated, its patterns live on.

**GitHub Copilot CLI**

```bash
$ gh copilot suggest "find all Python files modified in the last week"
git log --since="1 week ago" --name-only --pretty=format: -- "*.py" | sort -u
```

Copilot CLI suggests shell commands rather than editing code directly. It's specialized for command-line tasks.

**Amazon Q CLI**

AWS's CLI agent focuses on cloud operations:

```bash
$ q "create an S3 bucket with versioning enabled"
```

Deep integration with AWS services and IAM.

---

## 🔄 Comparing CLI Agents

### Feature Matrix

| Feature | Claude Code | Aider | Goose |
|---------|-------------|-------|-------|
| **Git Integration** | Manual commits | Auto-commits | Manual |
| **Multi-file Editing** | Yes | Yes | Yes |
| **Extensibility** | MCP servers | Limited | Toolkits |
| **Voice Input** | No | Yes | No |
| **Model Support** | Claude only | Multi-model | Multi-model |
| **Custom Commands** | Slash commands | Limited | Toolkits |
| **Project Context** | CLAUDE.md | .aider files | Config |
| **IDE Integration** | Yes (plugins) | No | No |
| **Open Source** | No | Yes | Yes |

### Strengths Summary

**Claude Code excels at:**
- Complex multi-step tasks
- Deep codebase understanding
- Tool orchestration via MCP
- Project-specific customization

**Aider excels at:**
- Rapid iteration with git safety net
- Working with any LLM
- Voice-driven development
- Large refactoring tasks

**Goose excels at:**
- Custom automation workflows
- Enterprise integrations (Jira, etc.)
- Extensibility via toolkits
- Self-hosted deployments

---

## 🏗️ Building CLI Workflows

Think of CLI workflow automation like building with LEGO bricks. Each CLI agent (Claude Code, Aider, Goose) is a specialized brick. Individually, they're useful. But when you snap them together in a pipeline—test runner → error analyzer → code fixer → committer—you create something far more powerful than any single tool.

### Scripting with Claude Code

Claude Code can be invoked non-interactively for automation:

```bash
#!/bin/bash
# review-pr.sh - Automated PR review

PR_NUMBER=$1
DIFF=$(gh pr diff $PR_NUMBER)

echo "$DIFF" | claude-code -p "Review this diff for:
1. Security issues
2. Performance concerns
3. Test coverage gaps

Output as markdown checklist."
```

### Chaining Tools

Combine multiple CLI agents for complex workflows:

```bash
#!/bin/bash
# smart-fix.sh - Diagnose and fix issues

# Step 1: Run tests to find failures
pytest --tb=short 2>&1 | tee test_output.txt

# Step 2: If tests fail, use Aider to fix
if [ $? -ne 0 ]; then
  aider --message "Fix the failing tests shown in test_output.txt" \
        --file test_output.txt \
        $(grep -l "FAILED" test_output.txt | head -5)
fi
```

### CI/CD Integration

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: AI Review
        run: |
          gh pr diff ${{ github.event.pull_request.number }} | \
          claude-code -p "Review this PR for issues" > review.md

      - name: Post Comment
        uses: actions/github-script@v7
        with:
          script: |
            const review = require('fs').readFileSync('review.md', 'utf8');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ github.event.pull_request.number }},
              body: review
            });
```

---

## 🔬 Advanced Patterns

### Context Management

CLI agents work best with focused context. Too many files = confused agent.

**Good pattern:**
```bash
# Only include relevant files
aider src/auth/*.py tests/test_auth.py
```

**Anti-pattern:**
```bash
# Don't include your entire codebase
aider **/*.py  # Overwhelming!
```

### Prompt Engineering for CLI

Terminal agents often need more explicit prompts than IDE agents:

```bash
# Too vague
> "improve the code"

# Better
> "Refactor the UserService class to:
> 1. Use dependency injection for the database connection
> 2. Add type hints to all methods
> 3. Extract email validation to a separate utility
> Keep the public API unchanged."
```

### Error Recovery

Build retry logic into your scripts:

```bash
#!/bin/bash
MAX_RETRIES=3
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
  aider --message "Fix any remaining test failures" && break
  RETRY=$((RETRY + 1))
  echo "Attempt $RETRY failed, retrying..."
  sleep 2
done
```

---

## 💻 Hands-On Practice

### Exercise 1: Claude Code Mastery (45 min)

**Objective:** Configure Claude Code with hooks, MCP, and slash commands.

**Steps:**
1. Create a new project directory
2. Set up `CLAUDE.md` with project conventions
3. Add a formatting hook that runs on every file edit
4. Create a `/test` slash command that runs your test suite
5. Connect an MCP server (start with filesystem or SQLite)

**Success criteria:** Demonstrate hooks triggering automatically and custom commands working.

### Exercise 2: Aider Git Workflow (45 min)

**Objective:** Use Aider's git-native workflow for a refactoring task.

**Steps:**
1. Clone a sample repository
2. Start Aider with a few files
3. Request a significant refactoring
4. Review the auto-generated commits
5. Use `git revert` to undo one change, then re-do it differently
6. Try voice mode if your system supports it

**Success criteria:** Multiple clean commits with meaningful messages.

### Exercise 3: Building an Automation Pipeline (60 min)

**Objective:** Create a script that combines multiple CLI agents.

**Build a pipeline that:**
1. Analyzes a Python file for issues (using Claude Code)
2. Fixes the issues (using Aider with auto-commit)
3. Runs tests to verify (pytest)
4. Generates a summary report

**Success criteria:** End-to-end automated improvement of a code file.

### Exercise 4: CLI vs IDE Comparison (30 min)

**Objective:** Complete the same task in both CLI and IDE to understand trade-offs.

**Task:** Add a new endpoint to a FastAPI application.

**Do it twice:**
1. Using Claude Code or Aider in terminal
2. Using Windsurf or Cursor IDE

**Document:**
- Time to complete
- Number of interactions
- Quality of final code
- When would you choose each approach?

---

## 🎯 Deliverables

### Primary Deliverable: CLI Agent Automation Toolkit

Build a Python toolkit that provides:

1. **Multi-Agent Orchestrator**: Script that routes tasks to appropriate CLI agent
2. **Context Manager**: Intelligent file selection for agent context
3. **Workflow Templates**: Pre-built automation scripts
4. **Metrics Dashboard**: Track agent usage, success rates, token costs

**File:** `examples/module_01.5/deliverable_cli_agent_toolkit.py`

**Features:**
- `demo1`: Single-agent task execution
- `demo2`: Multi-agent pipeline
- `demo3`: Automated code review workflow
- `demo4`: Metrics and reporting

**Success Criteria:**
- All demo functions work without errors
- Can execute tasks with at least two different CLI agents
- Generates useful metrics about agent performance

---

## 📚 Further Reading

### Official Documentation
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Aider Documentation](https://aider.chat/docs)
- [Goose GitHub Repository](https://github.com/block/goose)

### Tutorials
- "Building CLI Automation with Claude Code" - Anthropic Blog
- "Git-Native AI Development with Aider" - Paul Gauthier
- "Enterprise Agents with Goose" - Block Engineering Blog

### Benchmarks
- [SWE-bench Leaderboard](https://swebench.com) - Compare coding agents
- [Aider Benchmarks](https://aider.chat/benchmarks) - Model comparison

---

## 💡 Did You Know?

### The Unix Philosophy Lives On

Ken Thompson and Dennis Ritchie designed Unix with a philosophy: small, focused tools that do one thing well, connected by pipes. CLI AI agents are the modern embodiment of this principle. They read text, produce text, and can be chained together infinitely.

### Aider's Benchmark Dominance

Despite being a solo developer project, Aider regularly outperforms tools from companies with billion-dollar valuations on SWE-bench. The secret? Deep git integration that lets developers confidently iterate. Every change is a commit you can inspect, revert, or build upon.

### The 10x Developer Myth—Resolved?

For decades, the industry debated whether "10x developers" exist. CLI agents might have settled the debate. A skilled developer with a well-configured CLI agent workflow can genuinely output an order of magnitude more code than one working without—but only if they understand what they're building. The agent amplifies expertise, it doesn't replace it.

### Voice Coding's Origins

Voice coding for accessibility dates back to Dragon NaturallySpeaking in the 1990s. But Aider's voice mode represents something new: natural language programming. You don't dictate code syntax—you describe intent, and the agent implements it.

### The Return of Text Mode

In an era of Electron apps and web-based IDEs, CLI tools are having a renaissance. They're faster (no DOM rendering), more accessible (SSH from anywhere), and more automatable (just shell scripts). AI agents accelerated this trend—turns out language models work great with text-based interfaces.

---

## ⏭️ Next Steps

You now understand both GUI-based (Module 1.4) and CLI-based AI coding agents. The choice between them isn't either/or—it's about picking the right tool for your context:

- **IDE agents**: Visual work, design, documentation, learning
- **CLI agents**: Automation, scripting, remote work, CI/CD integration

**Next:** Move to Module 02 to start building real AI-powered tools with prompt engineering fundamentals.

---

## 🔧 Appendix: Quick Start Commands

### Claude Code Setup

```bash
# Install
npm install -g @anthropic-ai/claude-code

# Start interactive session
claude

# Non-interactive with prompt
claude -p "explain this file" < src/main.py

# With specific model
claude --model claude-sonnet-4-20250514
```

### Aider Setup

```bash
# Install
pip install aider-chat

# Start with files
aider src/main.py src/utils.py

# With specific model
aider --model gpt-4o

# Voice mode
aider --voice
```

### Goose Setup

```bash
# Install
pip install goose-ai

# Start session
goose session start

# With specific toolkit
goose session start --toolkit developer github
```

---

_Last Updated: 2025-12-09_
_Module Status: 🟡 In Progress_
_Estimated Time: 4-6 hours_
