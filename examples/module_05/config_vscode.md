# VSCode Configuration for AI Coding Assistants

**VS Code** is the most popular code editor and supports multiple AI coding assistants simultaneously. This guide shows how to configure and use them effectively together.

---

## 🛠️ Available AI Tools for VSCode

### Native Extensions

1. **GitHub Copilot** - Official Microsoft/GitHub extension
   - Extension ID: `GitHub.copilot`
   - Best for: Inline autocomplete, suggestions
   - Cost: $10/month or $100/year

2. **Continue.dev** - Open-source AI coding assistant
   - Extension ID: `Continue.continue`
   - Best for: Customizable AI workflows, multiple LLM support
   - Cost: Free (you pay for LLM API usage)

3. **Cline** - Autonomous coding agent
   - Extension ID: `saoudrizwan.claude-dev`
   - Best for: Agentic coding, complex multi-file tasks
   - Cost: Free (you pay for Claude API usage)

4. **Codeium** - Free Copilot alternative
   - Extension ID: `Codeium.codeium`
   - Best for: Free autocomplete
   - Cost: Free

### External Tools (work with VSCode)

5. **Aider.ai** - Terminal-based AI pair programmer
6. **Claude Code** - Anthropic's coding assistant (terminal/web)
7. **ChatGPT/Gemini** - Browser-based (copy/paste workflow)

---

## 📦 Installation

### Option 1: Via VSCode UI

1. Open VSCode
2. Click Extensions icon (Cmd+Shift+X / Ctrl+Shift+X)
3. Search for "GitHub Copilot"
4. Click Install
5. Sign in with GitHub account
6. Repeat for Continue, Cline, etc.

### Option 2: Via Command Line

```bash
# GitHub Copilot
code --install-extension GitHub.copilot

# Continue.dev
code --install-extension Continue.continue

# Cline
code --install-extension saoudrizwan.claude-dev

# Codeium (free alternative)
code --install-extension Codeium.codeium
```

---

## ⚙️ GitHub Copilot Configuration

### Settings (settings.json)

```json
{
  // Enable Copilot
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "plaintext": false,
    "markdown": true
  },

  // Inline suggestions
  "editor.inlineSuggest.enabled": true,

  // Show suggestions automatically
  "github.copilot.editor.enableAutoCompletions": true,

  // Advanced settings
  "github.copilot.advanced": {
    "debug.overrideEngine": "gpt-4",  // Use GPT-4 if available
    "debug.testOverrideProxyUrl": "",
    "debug.overrideProxyUrl": ""
  }
}
```

### Keyboard Shortcuts

Add to `keybindings.json`:

```json
[
  // Accept Copilot suggestion
  {
    "key": "tab",
    "command": "editor.action.inlineSuggest.commit",
    "when": "inlineSuggestVisible && !editorReadonly"
  },

  // Next suggestion
  {
    "key": "alt+]",
    "command": "editor.action.inlineSuggest.showNext",
    "when": "inlineSuggestVisible"
  },

  // Previous suggestion
  {
    "key": "alt+[",
    "command": "editor.action.inlineSuggest.showPrevious",
    "when": "inlineSuggestVisible"
  },

  // Open Copilot chat
  {
    "key": "cmd+i",
    "command": "github.copilot.interactiveEditor.explain"
  }
]
```

### Usage Tips

**1. Comment-Driven Development**:
```python
# Parse ISO 8601 date string and return datetime object
# Copilot will generate the implementation
```

**2. Function Name Hints**:
```python
def calculate_compound_interest_monthly(principal, rate, years):
    # Copilot infers what you want from the name
```

**3. Pattern Replication**:
```python
# Write one function well
def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()

# Start typing the next one
def get_user_by_email(
    # Copilot completes following the pattern
```

---

## ⚙️ Continue.dev Configuration

### Setup

1. Install extension
2. Press `Cmd+L` (or `Ctrl+L`) to open Continue sidebar
3. Click "Configure" → Select your LLM provider:
   - OpenAI (GPT-4)
   - Anthropic (Claude)
   - Ollama (Local models)
   - Azure OpenAI
   - etc.

### Config File (~/.continue/config.json)

```json
{
  "models": [
    {
      "title": "Claude Sonnet",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "apiKey": "your-api-key-here"
    },
    {
      "title": "GPT-4",
      "provider": "openai",
      "model": "gpt-4-turbo-preview",
      "apiKey": "your-api-key-here"
    },
    {
      "title": "Local Llama",
      "provider": "ollama",
      "model": "codellama:13b"
    }
  ],
  "slashCommands": [
    {
      "name": "edit",
      "description": "Edit selected code"
    },
    {
      "name": "comment",
      "description": "Add comments to code"
    },
    {
      "name": "share",
      "description": "Export conversation"
    }
  ],
  "contextProviders": [
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "folder",
      "params": {}
    },
    {
      "name": "codebase",
      "params": {}
    }
  ]
}
```

### Usage

**Cmd+L**: Open chat sidebar

Common workflows:

```
// Select code and ask:
"Explain this function"
"Add error handling"
"Optimize this for performance"
"Write tests for this"

// Codebase-wide:
"@codebase How does authentication work?"
"@codebase Find all API endpoints"

// Use /commands:
"/edit Add type hints to this function"
"/comment Explain each step"
"/test Generate unit tests"
```

---

## ⚙️ Cline Configuration

### Setup

1. Install extension
2. Set Anthropic API key in settings
3. Click Cline icon in sidebar

### Settings

```json
{
  "cline.anthropicApiKey": "your-api-key",
  "cline.autoApprove": false,  // Require approval for changes
  "cline.maxIterations": 10,
  "cline.model": "claude-3-5-sonnet-20241022"
}
```

### Usage

Cline is **agentic** - it can:
- Read multiple files
- Write/edit files
- Run terminal commands
- Iterate on tasks

**Example Task**:
```
"Add user authentication to this FastAPI app.
Use JWT tokens, PostgreSQL database.
Create tests and update documentation."
```

Cline will:
1. Analyze your codebase
2. Create necessary files
3. Update existing code
4. Run tests
5. Ask for approval at each step

---

## 🎯 Recommended Setup: Multi-Tool Workflow

Use multiple tools together for maximum productivity:

```json
{
  // Settings.json - Enable all tools
  "github.copilot.enable": {"*": true},
  "continue.enableTabAutocomplete": true,
  "cline.enabled": true,

  // Keybindings.json - Quick access
  [
    {"key": "tab", "command": "editor.action.inlineSuggest.commit"},       // Copilot
    {"key": "cmd+l", "command": "continue.continueGUIView.focus"},          // Continue
    {"key": "cmd+shift+c", "command": "cline.openClineGUIView"}             // Cline
  ]
}
```

---

## 📋 Workflow Examples

### Workflow 1: Fast Feature Development

1. **Copilot**: Write boilerplate quickly
   ```python
   # User model with email, password, created_at
   # [Tab to accept Copilot suggestion]
   ```

2. **Continue (Cmd+L)**: Handle complex logic
   ```
   "@codebase How should I implement password reset flow?"
   ```

3. **Cline**: Multi-file changes
   ```
   "Add password reset endpoints, email templates, and tests"
   ```

---

### Workflow 2: Debugging

1. **Copilot**: Quick fixes
   ```python
   # Fix: Add null check
   # [Copilot suggests the fix]
   ```

2. **Continue**: Analysis
   ```
   Select error log → "What could cause this error?"
   ```

3. **Terminal AI (Aider)**: Systematic debugging
   ```bash
   aider
   > "Debug this error: [paste error]. Check related files."
   ```

---

## 🔒 Privacy and Security

### GitHub Copilot
- **Sends**: Code snippets to GitHub servers
- **Stores**: Prompts and suggestions for improvement
- **Option**: Disable telemetry in settings
- **Enterprise**: GitHub Copilot for Business (better privacy)

### Continue.dev
- **Sends**: Code to your chosen LLM API (OpenAI, Anthropic, etc.)
- **Local Option**: Use Ollama for 100% local processing
- **Control**: You control which LLM provider

### Cline
- **Sends**: Code to Anthropic (Claude API)
- **Privacy**: Same as using Claude directly
- **Control**: You approve all changes

### For Sensitive Code

**Use Local Models**:
```json
{
  "models": [
    {
      "title": "Local CodeLlama",
      "provider": "ollama",
      "model": "codellama:13b"
    }
  ]
}
```

All processing stays on your machine.

---

## 🎯 Optimization Tips

### Performance

**1. Exclude Large Directories**:
```json
{
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/.git/**": true,
    "**/venv/**": true,
    "**/__pycache__/**": true
  }
}
```

**2. Limit Context**:
```json
{
  "continue.contextLength": 8000,  // Smaller = faster, cheaper
  "github.copilot.advanced": {
    "contextSize": "small"  // small, medium, large
  }
}
```

---

### Productivity

**1. Use Snippets + AI**:
```json
{
  "python.snippets": {
    "Fast API Route": {
      "prefix": "route",
      "body": [
        "@router.${1:get}(\"/${2:path}\")",
        "async def ${3:handler}():",
        "    ${4:pass}",
        "    # Let Copilot fill in the implementation"
      ]
    }
  }
}
```

**2. Create Custom Continue Commands**:
```json
{
  "slashCommands": [
    {
      "name": "secure",
      "description": "Review code for security issues",
      "prompt": "Review this code for security vulnerabilities: SQL injection, XSS, CSRF, etc."
    },
    {
      "name": "perf",
      "description": "Optimize for performance",
      "prompt": "Analyze this code for performance bottlenecks and suggest optimizations"
    }
  ]
}
```

---

## ✅ Quick Start Checklist

- [ ] Install GitHub Copilot
- [ ] Install Continue.dev or Cline (pick one to start)
- [ ] Configure API keys
- [ ] Set up keyboard shortcuts
- [ ] Test each tool with a simple task
- [ ] Read privacy policies for your organization
- [ ] Set up .gitignore to exclude AI config files if needed
- [ ] Practice multi-tool workflow

---

## 📊 Cost Comparison

| Tool | Cost | Notes |
|------|------|-------|
| **GitHub Copilot** | $10/mo | Fixed price, unlimited use |
| **Copilot Business** | $19/user/mo | Better privacy, admin controls |
| **Continue.dev** | Free + API costs | $0.01-0.10 per 1K tokens |
| **Cline** | Free + API costs | Uses Claude (~$0.015/1K tokens) |
| **Codeium** | Free | Ad-supported for individuals |
| **Ollama (local)** | Free | Requires GPU, slower than cloud |

**Budget Recommendation**:
- **$0/month**: Codeium (autocomplete) + Continue w/ Ollama (chat)
- **$10/month**: GitHub Copilot only
- **$20-30/month**: Copilot + Continue/Cline with API usage

---

## 🚀 Next Steps

1. Install and configure tools
2. Try each tool on a small task
3. Build your preferred workflow
4. Measure productivity gains
5. Share with team

---

**Remember**: More tools ≠ more productive. Start with 1-2 tools, master them, then add more.

**Recommended Starting Combo**: GitHub Copilot (autocomplete) + Continue.dev (chat/edits)
