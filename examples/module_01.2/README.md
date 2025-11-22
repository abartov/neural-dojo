# Module 1.2 Examples: Local Models for AI Coding

This directory contains hands-on exercises for setting up and using local AI models with coding tools.

## Prerequisites

- Python 3.12+
- Homebrew (macOS) or package manager (Linux/Windows)
- 8GB+ RAM (16GB recommended for larger models)
- ~10-30GB free disk space (for models)

## What You'll Learn

1. **Install Ollama** - Local model management system
2. **Download coding models** - DeepSeek, Qwen, Llama, etc.
3. **Use with Aider** - Terminal AI coding assistant
4. **Configure Continue.dev** - VS Code AI coding extension
5. **Cost optimization** - Hybrid local + API approach

## Examples Overview

### 1. Setup Ollama (`setup_ollama.sh`)
**Description**: Installation script for Ollama on macOS/Linux
**Run**: `bash setup_ollama.sh`
**What it does**:
- Installs Ollama via Homebrew (macOS) or wget (Linux)
- Downloads recommended coding models (Qwen, DeepSeek)
- Verifies installation
- Tests basic model functionality

### 2. Test Local Models (`test_local_models.py`)
**Description**: Verify Ollama and models work correctly
**Run**: `python test_local_models.py`
**What it does**:
- Checks if Ollama is running
- Lists installed models
- Tests each model with a simple coding task
- Measures response time
- Shows token usage statistics

### 3. Aider Setup Guide (`aider_with_local.md`)
**Description**: Step-by-step guide to use Aider with local models
**Read**: Comprehensive walkthrough with examples
**What it covers**:
- Installing Aider
- Configuring for local models
- Basic usage examples
- Advanced workflows
- Troubleshooting

### 4. Continue.dev Configuration (`continue_config.json`)
**Description**: Working Continue.dev configuration for local models
**Use**: Copy to `~/.continue/config.json`
**What it includes**:
- Multiple local model profiles
- Autocomplete configuration
- Chat model settings
- Hybrid local + API setup

### 5. Cost Comparison (`cost_comparison.md`)
**Description**: Detailed analysis of local vs API costs
**Read**: ROI calculation and savings strategies
**What it shows**:
- Monthly cost breakdown
- Break-even analysis
- Hybrid approach savings
- Real usage scenarios

## Quick Start

### Option 1: Full Setup (Recommended)

```bash
# 1. Install Ollama and models
bash setup_ollama.sh

# 2. Verify everything works
python test_local_models.py

# 3. Install Aider
pip install aider-chat

# 4. Try Aider with local model
aider --model ollama/qwen2.5-coder:7b

# 5. Configure Continue.dev
cp continue_config.json ~/.continue/config.json
# Then restart VS Code
```

### Option 2: Ollama Only (Minimal)

```bash
# Install Ollama
brew install ollama  # macOS
# OR
curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Start Ollama service
ollama serve &

# Pull a small model
ollama pull qwen2.5-coder:7b

# Test it
ollama run qwen2.5-coder:7b "Write a Python function to reverse a string"
```

### Option 3: Just Aider (API-free Coding)

```bash
# Install
pip install aider-chat

# Ensure Ollama is running
ollama serve &

# Pull model
ollama pull qwen2.5-coder:7b

# Use Aider
aider --model ollama/qwen2.5-coder:7b
```

## Recommended Models by Use Case

### Daily Coding (Best Balance)
- **Qwen 2.5-Coder 7B** - Fast, excellent quality
- RAM needed: ~8GB
- Download: `ollama pull qwen2.5-coder:7b`

### Complex Projects (Best Quality)
- **DeepSeek Coder V2 16B** - Highest quality
- RAM needed: ~16GB
- Download: `ollama pull deepseek-coder-v2:16b`

### Low-Resource Machines
- **Phi-3.5 3.8B** - Smallest, still capable
- RAM needed: ~4GB
- Download: `ollama pull phi3.5:3.8b`

### Autocomplete (Fast & Light)
- **Qwen 2.5-Coder 1.5B** - Instant autocomplete
- RAM needed: ~2GB
- Download: `ollama pull qwen2.5-coder:1.5b`

## Expected Output

### `setup_ollama.sh`
```
✓ Checking system requirements...
✓ Installing Ollama...
✓ Starting Ollama service...
✓ Downloading qwen2.5-coder:7b...
✓ Testing model...
✓ All models ready!

Next steps:
1. Run: python test_local_models.py
2. Try: ollama run qwen2.5-coder:7b
```

### `test_local_models.py`
```
Testing Local Models
====================

✓ Ollama is running
✓ Found 3 installed models

Testing qwen2.5-coder:7b...
  Task: Write a function to reverse a string
  Response time: 2.3s
  Quality: ⭐⭐⭐⭐⭐ (code works, well-commented)

Testing deepseek-coder-v2:16b...
  Task: Write a function to reverse a string
  Response time: 4.1s
  Quality: ⭐⭐⭐⭐⭐ (code works, type hints, docstring)

All tests passed! ✓
```

## Troubleshooting

### Ollama won't start
```bash
# Check if already running
ps aux | grep ollama

# Kill existing process
killall ollama

# Start fresh
ollama serve
```

### Model download stuck
```bash
# Cancel and retry
# Ctrl+C to cancel
ollama pull qwen2.5-coder:7b
```

### Aider can't find Ollama
```bash
# Ensure Ollama is running
ollama serve &

# Verify it's accessible
curl http://localhost:11434/api/tags

# Try Aider again
aider --model ollama/qwen2.5-coder:7b
```

### Out of memory
```bash
# Use smaller model
ollama pull qwen2.5-coder:3b

# Or use quantized version
ollama pull qwen2.5-coder:7b-q4_K_M
```

## Real-World Integration

These examples tie into your real projects:

### kaizen (Lean DevOps Platform)
- Use local models for code generation (free!)
- Qwen for daily refactoring
- DeepSeek for complex architecture changes
- Keep sensitive code local (no API leaks)

### vibe (Teaching Platform)
- Generate code examples with local models
- No API costs for content creation
- Consistent code quality across lessons

### contrarian (Stock Analysis)
- Local models for data processing scripts
- Private analysis (no code sent to APIs)
- Cost-effective experimentation

## Cost Savings

**Scenario**: 100 hours coding/month

**API-only approach**:
- GPT-4: ~$50-100/month
- Claude: ~$40-80/month

**Local + Gemini Flash (your setup)**:
- Local models: $0 (after download)
- Gemini Flash: $0-5 (within free tier)
- **Savings**: $40-95/month = **$480-1,140/year**

## Next Steps

1. ✅ Complete all setup scripts
2. ✅ Test each model
3. ✅ Configure your favorite tool (Aider or Continue.dev)
4. ✅ Try hybrid approach (80% local, 20% API)
5. ✅ Track your savings!

## Further Reading

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Aider Docs](https://aider.chat/docs/)
- [Continue.dev Docs](https://continue.dev/docs/)
- [Qwen 2.5-Coder Paper](https://arxiv.org/abs/2409.12186)
- [DeepSeek Coder V2 Technical Report](https://github.com/deepseek-ai/DeepSeek-Coder-V2)

---

**Ready to code for free?** Start with `bash setup_ollama.sh`! 🚀
