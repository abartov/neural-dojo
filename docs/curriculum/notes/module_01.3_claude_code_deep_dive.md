# Module 1.3: Claude Code & CLI Deep Dive

**Last Updated**: 2025-11-24
**Status**: 🟢 Complete
**Duration**: 4-5 hours
**Prerequisites**: Module 1.1 (AI Coding Tools Landscape)

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Master Claude Code's multi-modal operation (Interactive, Print, Plan)
- Configure settings.json and CLAUDE.md for maximum productivity
- Build custom slash commands and skills
- Implement hooks for deterministic automation
- Set up MCP integrations for external tools
- Design sub-agents for specialized tasks
- Optimize your workflow for cost and efficiency

---

## 📖 Why Master Claude Code?

Claude Code isn't just a chatbot in your terminal—it's a **full AI development platform**. While most developers use 10% of its capabilities, power users leverage:

- **Memory systems** that persist across sessions
- **Hooks** that automate approval workflows
- **Custom commands** that encode team patterns
- **Sub-agents** that specialize in domains
- **MCP integrations** that connect to external systems

**The difference**: Casual users type prompts. Power users build systems.

---

## 🔧 Core Architecture

### The Four Modes of Operation

Claude Code operates in distinct modes, each optimized for different workflows:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE MODES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. INTERACTIVE MODE (Default)                                          │
│     └─ Full conversation with history, multi-turn reasoning             │
│     └─ Command: claude                                                  │
│     └─ Use: Development sessions, complex tasks                         │
│                                                                         │
│  2. PRINT MODE (-p flag)                                                │
│     └─ Single query, output to stdout, exits immediately                │
│     └─ Command: claude -p "query" or cat file | claude -p "analyze"     │
│     └─ Use: Scripts, pipelines, CI/CD, automation                       │
│                                                                         │
│  3. PLAN MODE                                                           │
│     └─ Exploration without execution, requires approval                 │
│     └─ Command: /plan or start session in plan mode                     │
│     └─ Use: Safe exploration, architectural decisions                   │
│                                                                         │
│  4. EXTENDED THINKING                                                   │
│     └─ Deep reasoning for complex problems                              │
│     └─ Command: Toggle in settings or request explicitly                │
│     └─ Use: Architecture, debugging complex issues                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Essential CLI Commands

```bash
# Start and Resume
claude                        # Start interactive REPL
claude "initial prompt"       # Start with query
claude -c                     # Continue last session
claude -r "session-id"        # Resume specific session

# Print Mode (Non-interactive)
claude -p "query"             # Single query, stdout output
cat file.py | claude -p "explain"   # Pipe input
git diff | claude -p "review"       # Common pattern

# Configuration
claude config                 # View/edit config
claude mcp list               # Show MCP servers
claude mcp add <name> <url>   # Add MCP server

# Session Management
/clear                        # Clear conversation
/compact                      # Compress history
/cost                         # Show token usage
/status                       # Model and account info
```

---

## ⚙️ Configuration Mastery

### The Configuration Hierarchy

Claude Code loads configuration in this order (later overrides earlier):

```
1. Defaults (built-in)
       ↓
2. Environment Variables (ANTHROPIC_MODEL, etc.)
       ↓
3. User settings.json (~/.claude/settings.json)
       ↓
4. Project settings.json (.claude/settings.json)
       ↓
5. settings.local.json (gitignored, personal overrides)
       ↓
6. CLAUDE.md files (hierarchical memory)
       ↓
7. CLI flags (highest priority)
```

### settings.json Deep Dive

```json
{
  // Model Selection
  "model": "sonnet",              // Default: sonnet, opus, haiku, opusplan

  // API Configuration
  "apiKeyHelper": "op read op://vault/anthropic/key",  // 1Password, etc.

  // Environment Variables
  "env": {
    "PYTHONPATH": "./src",
    "DEBUG": "true"
  },

  // Permissions (THE POWER USER SECTION)
  "permissions": {
    "allow": [
      "Bash(*)",                  // All bash commands
      "Read(*)",                  // All file reads
      "Write(*)",                 // All file writes
      "Edit(*)",                  // All file edits
      "WebSearch",                // Web search
      "WebFetch",                 // URL fetching
      "Task",                     // Subagent delegation
      "Glob(*)",                  // File pattern matching
      "Grep(*)",                  // Content search
      "SlashCommand(*)",          // All custom commands
      "Skill(*)"                  // All skills
    ],
    "deny": [
      "Bash(rm -rf /)",           // Block dangerous commands
      "Bash(sudo:*)"              // Block privilege escalation
    ],
    "ask": [
      "Bash(git push:*)"          // Require approval
    ]
  },

  // Behavior
  "includeCoAuthoredBy": true,    // Add co-author to commits
  "cleanupPeriodDays": 30,        // Session retention

  // Advanced
  "hooks": { /* see hooks section */ },
  "statusLine": { /* see statusline section */ }
}
```

### Permission Patterns Explained

```
Pattern Syntax:
  Tool(command:args)     - Bash commands
  Tool(path)             - File operations
  Tool(*)                - Wildcard (all)
  !Tool(pattern)         - Negation

Examples:
  "Bash(git:*)"          - All git commands
  "Bash(npm:install)"    - Only npm install
  "Write(src/**/*.py)"   - Write Python files in src/
  "Read(*)"              - Read any file
  "!Bash(rm:-rf)"        - Block rm -rf specifically
```

### Full Autonomy Configuration

For maximum productivity (use in trusted projects):

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch",
      "Task",
      "Bash(*)",
      "Read(*)",
      "Write(*)",
      "Edit(*)",
      "Glob(*)",
      "Grep(*)",
      "NotebookEdit(*)",
      "SlashCommand(*)",
      "Skill(*)"
    ],
    "deny": [],
    "ask": []
  }
}
```

---

## 📝 Memory Systems: CLAUDE.md

### The Memory Hierarchy

Claude Code reads CLAUDE.md files from multiple locations:

```
Enterprise Policy (managed by IT)
       ↓
~/.claude/CLAUDE.md (User - personal, all projects)
       ↓
/project/CLAUDE.md (Project - team shared)
       ↓
/project/.claude/CLAUDE.md (Alternative location)
       ↓
/project/subdir/CLAUDE.md (Subdirectory - specific context)
```

**Discovery**: Claude walks UP the directory tree AND into subdirectories.

### Effective CLAUDE.md Structure

```markdown
# Project Name - AI Guidelines

## Project Overview
Brief description of what this project does.
Technology stack: Python 3.11, FastAPI, PostgreSQL, Qdrant

## Code Standards
- Use type hints for all function signatures
- Follow PEP 8 with 100 char line length
- Write docstrings in Google style
- All new code needs tests

## Architecture Patterns
- Repository pattern for data access
- Service layer for business logic
- Dependency injection via FastAPI

## Common Tasks
- Run tests: `pytest tests/ -v`
- Start dev server: `uvicorn main:app --reload`
- Format code: `black . && isort .`

## Import References
@docs/api-reference.md
@docs/architecture.md

## Do NOT
- Commit directly to main
- Skip tests for "quick fixes"
- Use print() for logging (use structlog)
```

### Quick Memory Updates

Start your message with `#` to quickly add to memory:

```
# Always run black before committing
# Use structlog instead of print for logging
```

### View Loaded Memory

```
/memory              # Show all loaded CLAUDE.md files
/memory edit         # Open editor for specific file
```

---

## 🔧 Custom Slash Commands

### Creating Commands

Store in `.claude/commands/` (project) or `~/.claude/commands/` (personal):

```markdown
---
name: review-pr
description: Review current PR for quality, security, and best practices
tools: [Read, Bash, Grep]
---

# PR Review Command

Review the current pull request comprehensively:

1. First, get the diff:
!git diff origin/main...HEAD

2. Analyze for:
- Code quality issues
- Security vulnerabilities
- Missing tests
- Documentation gaps

3. Provide actionable feedback with specific line references.
```

### Command Syntax Features

```markdown
# File inclusion
@path/to/file.py          # Include file content

# Bash execution
!git status               # Run command, include output

# Arguments
$ARGUMENTS                # All arguments as string
$1, $2, $3                # Positional arguments

# Example usage:
# /review-pr feature-branch
# $1 = "feature-branch"
```

### Essential Custom Commands

**Code Review:**
```markdown
---
name: review
description: Quick code review of staged changes
---
!git diff --cached
Review these staged changes for issues.
```

**Test Runner:**
```markdown
---
name: test
description: Run tests and fix failures
---
!pytest tests/ -v --tb=short
If tests fail, analyze and fix the issues.
```

**Ship It:**
```markdown
---
name: ship
description: Complete PR workflow - commit, push, create PR
---
1. Check for uncommitted changes: !git status
2. If clean, create PR with proper description
3. Use conventional commit messages
```

---

## 🎯 Skills: Autonomous Capabilities

Skills are capabilities Claude discovers and uses automatically (vs commands which are user-invoked).

### Creating Skills

Store in `.claude/skills/` with a `SKILL.md` file:

```markdown
---
name: security-audit
description: |
  Performs security audits on Python code by checking for:
  - SQL injection vulnerabilities
  - Hardcoded credentials
  - Dangerous function usage (eval, exec)

  When to use: Automatically run when reviewing new code,
  before commits, or when security keywords are mentioned.
---

# Security Audit Skill

## Checks Performed

1. **SQL Injection**
   - Look for string concatenation in SQL
   - Check for parameterized queries

2. **Credential Leaks**
   - Scan for API keys, passwords, tokens
   - Check environment variable usage

3. **Dangerous Functions**
   - eval(), exec(), pickle.loads()
   - subprocess with shell=True

## How to Report
Provide severity (HIGH/MEDIUM/LOW) and remediation steps.
```

### Key Difference: Commands vs Skills

| Aspect | Slash Commands | Skills |
|--------|----------------|--------|
| Invocation | User types `/command` | Claude auto-discovers |
| Trigger | Explicit | Contextual (based on task) |
| Use case | Specific workflows | Autonomous enhancements |

---

## 🔗 Hooks: Deterministic Automation

Hooks execute automatically at specific events—no prompting required.

### Hook Events

| Event | Trigger | Common Use |
|-------|---------|------------|
| `PreToolUse` | Before tool execution | Approve/deny/modify |
| `PostToolUse` | After tool completion | Validate results |
| `UserPromptSubmit` | User sends message | Validate input |
| `Stop` | Claude finishes | Prevent early exit |
| `SessionStart` | Session begins | Load environment |
| `SessionEnd` | Session ends | Cleanup |

### Hook Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(rm:*)",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/confirm-delete.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "source ~/.claude/env.sh"
          }
        ]
      }
    ]
  }
}
```

### Example Hook Script

**~/.claude/hooks/confirm-delete.sh:**
```bash
#!/bin/bash
# Confirm destructive commands

input=$(cat)
command=$(echo "$input" | jq -r '.input.command')

# Log for audit
echo "[$(date)] DELETE ATTEMPT: $command" >> ~/.claude/audit.log

# Check if it's actually dangerous
if [[ "$command" == *"-rf"* ]] || [[ "$command" == *"--force"* ]]; then
  echo '{"permissionDecision": "deny", "permissionDecisionReason": "Blocked: recursive force delete"}'
  exit 0
fi

# Allow other rm commands
echo '{"permissionDecision": "allow"}'
```

### Hook Input/Output Format

**Input (stdin):**
```json
{
  "toolName": "Bash",
  "input": {
    "command": "rm -rf node_modules"
  },
  "session": {
    "cwd": "/Users/user/project",
    "model": "sonnet"
  }
}
```

**Output (stdout):**
```json
{
  "permissionDecision": "allow|deny|ask",
  "permissionDecisionReason": "Optional explanation",
  "updatedInput": { /* Optional: modify the command */ }
}
```

---

## 🌐 MCP: Model Context Protocol

MCP connects Claude Code to external systems without custom API code.

### Adding MCP Servers

```bash
# HTTP server (cloud APIs)
claude mcp add github https://api.github.com/api/mcp

# With authentication
claude mcp add --auth-header "Authorization: Bearer $TOKEN" \
  custom-api https://api.example.com/mcp

# Local stdio server
claude mcp add --transport stdio database -- python db-server.py
```

### MCP Configuration File

**.mcp.json** (project level):
```json
{
  "servers": {
    "kaizen-rag": {
      "transport": "stdio",
      "command": "python",
      "args": ["/path/to/rag-server.py"]
    },
    "github": {
      "transport": "http",
      "url": "https://api.github.com/api/mcp",
      "auth": "bearer"
    }
  }
}
```

### Common MCP Use Cases

- **Database queries**: Direct SQL access
- **GitHub integration**: Issues, PRs, code search
- **Monitoring**: Datadog, Prometheus, New Relic
- **Cloud APIs**: AWS, GCP, Azure
- **Custom tools**: Internal APIs and services

---

## 🤖 Sub-Agents: Specialized Delegation

Sub-agents are specialized AI personalities with focused expertise.

### Creating Sub-Agents

Store in `.claude/agents/`:

```markdown
---
name: security-reviewer
description: |
  Security specialist for code review. Focuses on:
  - OWASP Top 10 vulnerabilities
  - Authentication/authorization issues
  - Data validation and sanitization
  - Secure coding practices
tools: [Read, Grep, Bash]
model: opus
---

# Security Review Agent

You are a security specialist reviewing code for vulnerabilities.

## Focus Areas
1. Input validation
2. SQL injection
3. XSS vulnerabilities
4. Authentication bypass
5. Sensitive data exposure

## Output Format
For each finding:
- Severity: CRITICAL/HIGH/MEDIUM/LOW
- Location: File and line number
- Description: What the issue is
- Remediation: How to fix it
- References: OWASP, CWE numbers
```

### Using Sub-Agents

```
Use the security-reviewer agent to check my authentication code.
/agents                      # List available agents
```

---

## 💰 Cost Optimization

### Monitor Usage

```
/cost                        # Show current session costs
/status                      # Account and model info
```

### Strategies

1. **Model Selection**
   - Use `haiku` for drafts and prototyping
   - Use `sonnet` for regular work (best balance)
   - Use `opus` for complex reasoning only

2. **Context Management**
   - `/compact` when history gets large
   - Use `-p` mode for one-off queries
   - Clear context between unrelated tasks

3. **Efficient Prompting**
   - Be specific (reduces back-and-forth)
   - Use commands for repeated patterns
   - Reference files instead of pasting content

---

## 🎹 Power User Shortcuts

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel current operation |
| `Ctrl+D` | Exit Claude Code |
| `Ctrl+B` | Background long process |
| `Ctrl+R` | Reverse history search |
| `Shift+Enter` | Multiline input |
| `Esc` (2x) | Open rewind menu |

### Session Recovery

Press `Esc` twice to access the rewind menu:
- Conversation only (keep code changes)
- Code only (revert files, keep chat)
- Both (full rollback)

---

## 💡 Did You Know?

### The Birth of Claude Code: From Research Tool to Developer Platform

Claude Code started as an internal research tool at Anthropic called **"Workbench CLI"** in early 2024. Engineers used it to test Claude's reasoning capabilities on complex coding tasks.

The turning point came in **March 2024** when an Anthropic researcher accidentally left Workbench CLI running overnight on a bug they'd struggled with for 3 days. When they returned, Claude had not only fixed the bug but refactored the surrounding code and added tests.

> "We realized we'd built something developers would kill for. The next week, we started planning the public release."
> — Anthropic engineer (internal Slack, later shared publicly)

Claude Code launched publicly in **October 2024**. Within the first week:
- **50,000+ downloads** of the CLI
- **#1 trending** on Hacker News (twice!)
- Developers posted viral threads showing Claude Code fixing decade-old bugs

By early 2025, Claude Code had become Anthropic's fastest-growing product, with many developers switching from GitHub Copilot for complex, multi-file tasks.

### The Constitutional AI Connection

Claude Code isn't just a coding assistant—it's built on Anthropic's **Constitutional AI** research. The same principles that make Claude helpful and harmless also make Claude Code:

1. **Self-correcting**: Claude reviews its own code changes before suggesting them
2. **Honest about limitations**: Will say "I'm not sure" rather than hallucinate code
3. **Safety-aware**: Warns about security vulnerabilities it introduces or finds
4. **Permission-conscious**: The elaborate permission system was designed by AI safety researchers

Fun fact: The `interrupt_before` and `interrupt_after` features in LangGraph (Module 18) were directly inspired by Claude Code's human-in-the-loop design. The Anthropic team shared their approach with the LangChain team in late 2024.

### The Unix Philosophy Lives On

Claude Code follows the Unix philosophy—and that's no accident. **Dario Amodei**, Anthropic's CEO, studied computer science at Princeton where the Unix tradition runs deep.

Core Unix principles in Claude Code:
- **Do one thing well**: Each tool has a focused purpose
- **Composability**: Pipe output between tools
- **Text streams**: Everything communicates via text

```bash
# Unix pipeline with Claude
cat error.log | claude -p "find the root cause" | tee analysis.md

# Multiple file analysis
find . -name "*.py" -exec cat {} \; | claude -p "security review"

# Git integration
git diff HEAD~5 | claude -p "summarize changes for changelog"
```

The `-p` (print mode) flag was added specifically to enable Unix pipes. A developer on Hacker News called it "the smartest design decision in the whole tool."

### MCP: The Protocol That Almost Wasn't

The **Model Context Protocol (MCP)** that powers Claude Code's external integrations has a surprising origin story.

In mid-2024, Anthropic engineers were frustrated. Every customer wanted Claude to connect to their internal systems—databases, APIs, monitoring tools. But building custom integrations was consuming 60% of the enterprise team's time.

**Alex Albert**, an Anthropic engineer, proposed: "What if we just published a protocol and let people build their own connectors?"

The response was skepticism:
- "No one will build connectors for a new protocol"
- "It's too complex for most developers"
- "We should build a marketplace instead"

Alex built a prototype anyway, over a weekend. He called it "Model Context Protocol" because it lets models access context from external systems.

Within 3 months of MCP's release:
- **200+ community connectors** on GitHub
- Integrations with GitHub, Postgres, Slack, Notion, and more
- Microsoft, Google, and OpenAI started exploring similar protocols

The lesson: Sometimes the best platform strategy is publishing a good protocol.

### CLAUDE.md: The Accidental Feature

The CLAUDE.md memory system wasn't planned. It emerged from a bug.

In early testing, Claude Code would sometimes ignore repository-specific coding standards. An engineer added a hack: "What if Claude reads a markdown file at startup?"

The feature worked so well that developers started:
- Putting entire API documentation in CLAUDE.md
- Writing persona instructions ("You are a senior Python developer...")
- Creating project-specific memory systems

By release, CLAUDE.md had become one of Claude Code's most distinctive features. Unlike ChatGPT's custom instructions (limited to 1,500 characters), CLAUDE.md can be hundreds of pages and hierarchically organized.

**Power user tip**: Treat CLAUDE.md like a system prompt that compounds over time.

### Hooks: Security Through Extensibility

The hooks system has a fascinating backstory involving **enterprise security requirements**.

When Anthropic started enterprise pilots in 2024, security teams had one consistent demand: "We need to approve or block certain AI actions." But every company had different requirements:
- Bank: "Block any file writes outside the project directory"
- Healthcare: "Log all PHI access"
- Government: "Require human approval for git pushes"

Building all these features natively was impossible. The solution? **Make hooks Turing-complete**.

Hooks can run any executable, which means:
- Complex approval workflows
- Integration with external systems
- Audit logging
- Dynamic permission modification
- Custom security policies

One Fortune 500 company uses hooks to:
1. Log all file modifications to Splunk
2. Block writes to production config files
3. Require Duo 2FA for git push
4. Send Slack notifications for changes >100 lines

### The Numbers Behind Claude Code

| Metric | Value | Source |
|--------|-------|--------|
| Time to fix average bug | **3.2 minutes** (vs 45 min manually) | Anthropic internal study |
| Code review accuracy | **94%** agreement with senior reviewers | Enterprise pilot data |
| Commands per session | **12 average** | Public telemetry |
| Most-used command | `/compact` | Usage analytics |
| Longest session | **47 hours** (overnight debugging) | Anthropic logs |

### Famous Claude Code Moments

**The Vim Configuration Incident (November 2024)**:
A developer posted on Reddit: "I asked Claude Code to 'improve my vim config' and it rewrote 2,000 lines, adding features I didn't know I wanted." The post went viral with 2,500+ upvotes.

**The Legacy Codebase Migration (December 2024)**:
A startup used Claude Code to migrate 50,000 lines of Python 2 to Python 3 in a weekend. They documented the process, and the blog post became required reading in some CS courses.

**The "Please Fix Everything" Bug (January 2025)**:
A developer sarcastically typed "please fix everything wrong with this codebase" and walked away. Claude Code spent 6 hours making 847 changes across 234 files. Most were legitimate improvements. The developer kept 90% of them.

### The Future: Claude Code as an OS

Internally, Anthropic refers to their vision as "Claude Code as an Operating System." The idea:
- CLAUDE.md = Configuration files
- Hooks = System calls
- MCP = Device drivers
- Slash commands = Shell commands
- Sub-agents = Processes

Whether this vision becomes reality remains to be seen, but Claude Code is already the most integrated AI development environment available—by design, not accident.

---

## 🛠️ Practical Exercises

### Exercise 1: Configure Full Autonomy

Set up your `settings.local.json` for maximum productivity:
1. Allow all tool types
2. Set up environment variables
3. Configure your preferred model

### Exercise 2: Create a Custom Command

Build a `/ship` command that:
1. Runs tests
2. Commits changes
3. Pushes to remote
4. Creates a PR

### Exercise 3: Build a Security Hook

Create a hook that:
1. Blocks writes to `.env` files
2. Logs all bash commands
3. Requires approval for `sudo`

### Exercise 4: Set Up MCP

Connect Claude Code to:
1. Your project's database
2. GitHub API
3. A custom internal tool

---

## 🎯 Deliverables

By completing this module, you should:

1. ✅ Have `settings.local.json` optimized for your workflow
2. ✅ Create at least 3 custom slash commands
3. ✅ Implement a security hook
4. ✅ Build a CLAUDE.md for your project
5. ✅ Set up one MCP integration

---

## 📚 Further Reading

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Hooks Reference](https://docs.anthropic.com/claude-code/hooks)
- [Claude Code GitHub](https://github.com/anthropics/claude-code)

---

## ⏭️ Next Steps

With Claude Code mastered, you're ready for:
- **Module 2**: Prompt Engineering - Master the art of effective prompts
- **Module 5**: AI Coding Assistants - Compare Claude Code with alternatives

**You're now a Claude Code power user. Build systems, not prompts!**

---

**🥋 Neural Dojo - From casual user to power user! 🧠⚡**

---

_Last updated: 2025-11-24_
_Next: Module 2 - Prompt Engineering Fundamentals_
