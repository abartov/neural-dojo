# Module 0 Examples: Prerequisites & Environment Setup

This directory contains verification scripts to ensure your development environment is properly configured before starting Module 1.

## Prerequisites

1. Python 3.10+ installed
2. Virtual environment activated
3. API key(s) configured in `.env` file

## Setup

```bash
# From neural-dojo root directory
cd examples/module_00

# Make sure venv is activated
source ../../venv/bin/activate  # On macOS/Linux
# or
..\..\venv\Scripts\activate  # On Windows

# Install required packages
pip install python-dotenv anthropic openai
```

## Examples

### 1. test_environment.py

**Purpose**: Verify Python environment is set up correctly

**What it tests**:
- Python version (3.10+)
- pip is working
- python-dotenv is installed

**Run**:
```bash
python test_environment.py
```

**Expected Output**:
```
🔍 Testing environment setup...

✅ Python 3.10.x
✅ pip works: pip 23.x.x
✅ python-dotenv installed

✅ Environment setup complete!
```

---

### 2. test_claude_api.py

**Purpose**: Verify Claude API is configured and working

**What it tests**:
- ANTHROPIC_API_KEY is set in `.env`
- anthropic package is installed
- Can make a successful API call
- Token usage is tracked

**Run**:
```bash
python test_claude_api.py
```

**Expected Output**:
```
🔍 Testing Claude API...

✅ API key found
✅ anthropic package imported

🤖 Making API call to Claude...

📩 Claude says: Hello from Neural Dojo!

📊 Token usage:
   Input tokens: 15
   Output tokens: 6

✅ Claude API working! You're ready to start Module 1.
```

**Cost**: ~$0.001 per test (less than a penny!)

---

### 3. test_openai_api.py

**Purpose**: (Optional) Verify OpenAI API is configured

**What it tests**:
- OPENAI_API_KEY is set in `.env` (optional)
- openai package is installed
- Can make a successful API call

**Run**:
```bash
python test_openai_api.py
```

**Expected Output**:
```
🔍 Testing OpenAI API...

✅ API key found
✅ openai package imported

🤖 Making API call to OpenAI...

📩 GPT says: Hello from Neural Dojo!

📊 Token usage:
   Prompt tokens: 20
   Completion tokens: 6
   Total tokens: 26

✅ OpenAI API working!
```

**Cost**: ~$0.001 per test

---

## ⚠️ Important: API Access vs Subscriptions

**Common confusion**: If you have ChatGPT Plus or Claude Pro, those are **web subscriptions** and do NOT include API access!

- **Web subscription** = Use AI in browser/app (ChatGPT Plus, Claude Pro)
- **API access** = Use AI in your code (what we need for examples)

**You need API access** for these examples to work. See Module 0 theory document for:
- How to get API keys (separate from subscriptions)
- Free tier options and trial credits
- Alternative free APIs (Hugging Face, Groq, Together AI, Replicate)

**Estimated cost**: $3-5 for entire curriculum with Claude/OpenAI APIs

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

1. Check `.env` file exists in project root
2. Check format: `ANTHROPIC_API_KEY=sk-ant-your-key-here` (no spaces around `=`)
3. Get API key from: https://console.anthropic.com/
4. **Note**: API access is separate from Claude Pro subscription!

### "Module 'anthropic' not found"

```bash
pip install anthropic
```

### "Permission denied" errors

Make sure virtual environment is activated (you should see `(venv)` in your prompt).

---

## Next Steps

Once all tests pass:
✅ Your environment is ready!
✅ Move on to Module 1: Foundations of AI-Driven Development

---

_Last updated: 2025-11-21_
