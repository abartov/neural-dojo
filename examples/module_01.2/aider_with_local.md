# Using Aider with Local Models

**Module 1.2: Local Models for AI Coding**

Aider is a terminal-based AI coding assistant that integrates with git. This guide shows you how to use Aider with local models via Ollama.

---

## 📋 Prerequisites

1. **Ollama installed and running**
   ```bash
   ollama serve
   ```

2. **At least one coding model downloaded**
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

3. **Aider installed**
   ```bash
   pip install aider-chat
   ```

---

## 🚀 Quick Start

### Basic Usage

```bash
# Use Qwen 2.5-Coder (recommended)
aider --model ollama/qwen2.5-coder:7b

# Use DeepSeek Coder V2 (higher quality, slower)
aider --model ollama/deepseek-coder-v2:16b

# Use Phi-3.5 (faster, lower resource)
aider --model ollama/phi3.5:3.8b
```

### With Specific Files

```bash
# Work on specific files
aider --model ollama/qwen2.5-coder:7b src/main.py tests/test_main.py

# Add files interactively
aider --model ollama/qwen2.5-coder:7b
> /add src/utils.py
> /add src/models.py
```

---

## 💡 Practical Examples

### Example 1: Refactoring Code

```bash
# Start Aider with your file
aider --model ollama/qwen2.5-coder:7b src/calculator.py

# In Aider prompt:
> Refactor this code to use type hints and add docstrings

# Aider will:
# 1. Read your code
# 2. Generate improved version
# 3. Show you the diff
# 4. Ask if you want to apply changes
# 5. Commit to git automatically
```

**Example session**:
```
Aider v0.50.1
Model: qwen2.5-coder:7b (via Ollama)
Git repo: /Users/you/project
Files: src/calculator.py

You: Refactor this code to use type hints and add docstrings

Aider: I'll refactor calculator.py with type hints and docstrings.

───────────────────────────────────────────────────
src/calculator.py
───────────────────────────────────────────────────
+ from typing import Union
+
+ def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
+     """Add two numbers and return the result.
+
+     Args:
+         a: First number
+         b: Second number
+
+     Returns:
+         Sum of a and b
+     """
      return a + b

Apply these changes? (Y)es/(N)o/(D)on't ask again [Yes]: y

Applied changes to src/calculator.py
Commit message: Refactor calculator with type hints and docstrings

    Generated with Claude Code
    Co-Authored-By: Claude <noreply@anthropic.com>

Committed!
```

### Example 2: Bug Fixing

```bash
aider --model ollama/qwen2.5-coder:7b src/app.py

# In Aider:
> Fix the bug where empty input causes a crash
```

Aider will:
1. Analyze your code
2. Identify the issue
3. Propose a fix with error handling
4. Show you the changes
5. Commit if you approve

### Example 3: Adding New Features

```bash
aider --model ollama/qwen2.5-coder:7b src/user.py

# In Aider:
> Add a method to validate email addresses using regex
```

### Example 4: Writing Tests

```bash
aider --model ollama/qwen2.5-coder:7b src/utils.py tests/test_utils.py

# In Aider:
> Write pytest tests for all functions in utils.py
```

---

## ⚙️ Configuration

### Create `.aider.conf.yml` in your project root

```yaml
# .aider.conf.yml
model: ollama/qwen2.5-coder:7b

# Auto-commit changes
auto-commits: true

# Show diffs before applying
show-diffs: true

# Prettier output
pretty: true

# Dark mode for diffs
dark-mode: true

# Git settings
git: true
gitignore: true

# Editor for commit messages
editor: vim  # or nano, emacs, etc.
```

### Per-Project Model Selection

```yaml
# For complex projects (need high quality)
model: ollama/deepseek-coder-v2:16b

# For simple projects (need speed)
model: ollama/qwen2.5-coder:7b

# For low-resource machines
model: ollama/phi3.5:3.8b
```

---

## 🎯 Advanced Usage

### Multi-Model Workflow

Use different models for different tasks:

```bash
# Quick refactoring with Qwen (fast)
aider --model ollama/qwen2.5-coder:7b src/simple.py

# Complex architecture with DeepSeek (quality)
aider --model ollama/deepseek-coder-v2:16b src/core.py

# Code review with API model (occasional)
aider --model gemini/gemini-2.5-flash src/critical.py
```

### Hybrid Local + API Approach

```bash
# Daily work: 100% local (FREE)
aider --model ollama/qwen2.5-coder:7b

# Complex features: Use Gemini Flash (FREE tier)
aider --model gemini/gemini-2.5-flash
```

**Cost**: ~$0-5/month (stay in Gemini free tier)
vs $50-100/month (API-only)

### Voice Mode (Experimental)

```bash
# Use voice input (requires API model)
aider --model gemini/gemini-2.5-flash --voice-language en
```

---

## 🔧 Troubleshooting

### Problem: "Connection refused" error

**Solution**: Ensure Ollama is running
```bash
# Check if running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve &
```

### Problem: Model responds very slowly

**Solutions**:
1. Use smaller model: `--model ollama/qwen2.5-coder:3b`
2. Use quantized model: `ollama pull qwen2.5-coder:7b-q4_K_M`
3. Close other apps to free RAM
4. Use GPU if available (Ollama auto-detects)

### Problem: Model gives low-quality responses

**Solutions**:
1. Use larger model: `--model ollama/deepseek-coder-v2:16b`
2. Be more specific in prompts
3. Add more context files to Aider session
4. Switch to API model for complex tasks

### Problem: Aider can't find Ollama models

**Solution**: Verify model format
```bash
# List available models
ollama list

# Correct format in Aider
aider --model ollama/qwen2.5-coder:7b
#                ^^^^^^ prefix required!
```

### Problem: Git commits are too verbose

**Solution**: Customize commit messages
```yaml
# .aider.conf.yml
commit-prompt: |
  Write a concise git commit message.
  First line: 50 chars max, imperative mood
  Body: Explain why, not what
```

---

## 📊 Performance Comparison

### Response Time (Average)

| Model | Simple Task | Complex Task | Code Quality |
|-------|-------------|--------------|--------------|
| Qwen 2.5-Coder 7B | 2-4s | 8-15s | ⭐⭐⭐⭐⭐ |
| DeepSeek V2 16B | 4-8s | 15-30s | ⭐⭐⭐⭐⭐ |
| Phi-3.5 3.8B | 1-3s | 5-10s | ⭐⭐⭐⭐ |
| Gemini Flash (API) | 1-2s | 3-6s | ⭐⭐⭐⭐⭐ |

### Memory Usage

| Model | RAM Needed | Disk Space |
|-------|------------|------------|
| Qwen 2.5-Coder 7B | ~8GB | ~4.7GB |
| DeepSeek V2 16B | ~16GB | ~9.8GB |
| Phi-3.5 3.8B | ~4GB | ~2.3GB |

---

## 🎓 Real-World Workflows

### Workflow 1: Daily Coding (100% Local)

```bash
# Morning: Start coding session
aider --model ollama/qwen2.5-coder:7b

# Work on features
> Add error handling to API endpoints
> Refactor database queries for performance
> Write unit tests for new functions

# End of day: All commits in git, $0 spent!
```

### Workflow 2: Hybrid Approach (80% Local, 20% API)

```bash
# Routine tasks (80% of time): Local
aider --model ollama/qwen2.5-coder:7b

# Complex architecture (20% of time): API
aider --model gemini/gemini-2.5-flash

# Monthly cost: $0-5 (within Gemini free tier)
```

### Workflow 3: Team Collaboration

```bash
# Each developer uses local models
aider --model ollama/qwen2.5-coder:7b

# Code reviews: Use API for consistency
aider --model gemini/gemini-2.5-flash --review

# Team savings: 10 devs × $50/mo = $500/mo → $0/mo
```

---

## 💰 Cost Savings Calculation

### Scenario: 100 hours coding/month

**API-only approach**:
- GPT-4: ~$50-100/month
- Claude: ~$40-80/month
- **Total**: $50-100/month

**Local-only approach**:
- Qwen 2.5-Coder 7B: $0/month
- DeepSeek V2 16B: $0/month
- **Total**: $0/month

**Hybrid approach (your setup)**:
- Local (80%): $0
- Gemini Flash (20%): $0-5 (free tier)
- **Total**: $0-5/month

**Annual savings**: $480-1,140 💰

---

## 🚀 Next Steps

1. **Try each model**:
   ```bash
   aider --model ollama/qwen2.5-coder:7b
   aider --model ollama/deepseek-coder-v2:16b
   ```

2. **Create project config**:
   ```bash
   # In your project root
   cat > .aider.conf.yml <<EOF
   model: ollama/qwen2.5-coder:7b
   auto-commits: true
   show-diffs: true
   EOF
   ```

3. **Integrate into workflow**:
   - Use for daily refactoring
   - Generate boilerplate code
   - Write tests automatically
   - Fix bugs with AI assistance

4. **Track your savings**:
   - Log API calls you didn't make
   - Calculate monthly savings
   - Celebrate $500-1000/year saved!

---

## 📚 Additional Resources

- [Aider Documentation](https://aider.chat/docs/)
- [Ollama Model Library](https://ollama.com/library)
- [Qwen 2.5-Coder Benchmarks](https://github.com/QwenLM/Qwen2.5-Coder)
- [DeepSeek Coder V2 Paper](https://github.com/deepseek-ai/DeepSeek-Coder-V2)

---

**Ready to code with AI for FREE?** Start Aider now! 🎉

```bash
aider --model ollama/qwen2.5-coder:7b
```
