# Module 0: Prerequisites & Environment Setup

**Last Updated**: 2025-11-21
**Status**: ⚪ Not Started
**Duration**: 2-3 hours
**Prerequisites**: None - this is where you start!

---

## 🎯 Learning Objectives

By the end of this module, you will:
- Verify you have the required prerequisites (Python, git, command line)
- Set up your development environment (venv, pip, IDE)
- Configure API keys for Claude and OpenAI
- Make your first LLM API call
- Verify everything works before diving into Module 1

---

## 📋 Prerequisites Check

Before starting Neural Dojo, you should have:

### ✅ Required Skills

1. **Basic Python Programming** (variables, functions, loops, classes)
   - Can you write a Python script that reads a file and prints its contents?
   - Can you create a simple class with methods?
   - Can you use pip to install packages?

2. **Command Line Basics** (cd, ls, mkdir, running scripts)
   - Can you navigate directories in terminal?
   - Can you run a Python script from command line?
   - Can you create and delete files/directories?

3. **Git Basics** (clone, commit, push - optional but recommended)
   - Can you clone a repository?
   - Can you commit changes?
   - (This is helpful but not required)

### ✅ Required Software

1. **Python 3.10+** installed
2. **pip** package manager
3. **Git** (recommended)
4. **Text editor or IDE** (VS Code, PyCharm, Cursor, etc.)
5. **Terminal/Command Prompt** access

### 📝 Self-Assessment

Answer these questions honestly:

```python
# Can you understand and run this code?
def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to Neural Dojo."

if __name__ == "__main__":
    message = greet("Student")
    print(message)
```

- ✅ If YES: You're ready! Continue with this module.
- ❌ If NO: You may want to take a Python basics course first.

**Recommended**: [Python for Everybody](https://www.py4e.com/) or [Automate the Boring Stuff](https://automatetheboringstuff.com/)

---

## 💻 Development Environment Setup

### Step 1: Verify Python Installation

```bash
# Check Python version (must be 3.10 or higher)
python --version
# or
python3 --version

# Check pip is installed
pip --version
# or
pip3 --version
```

**Expected Output**:
```
Python 3.10.x (or higher)
pip 23.x.x (or higher)
```

**Troubleshooting**:
- **macOS**: Use `python3` and `pip3` instead of `python` and `pip`
- **Windows**: Make sure Python is in your PATH
- **Linux**: Install with `sudo apt install python3.10 python3-pip`

---

### Step 2: Choose Your Text Editor/IDE

You'll need a good editor for writing code. Choose one:

#### Option A: **VS Code** (Recommended for beginners)
- Free, lightweight, great extensions
- Download: https://code.visualstudio.com/
- Install Python extension
- Install Claude Code extension (optional but helpful!)

#### Option B: **Cursor** (AI-native IDE)
- VS Code fork with AI built-in
- Great for AI-driven development (Module 1!)
- Download: https://cursor.sh/

#### Option C: **PyCharm** (Full-featured IDE)
- Professional Python IDE
- Free Community Edition available
- Download: https://www.jetbrains.com/pycharm/

#### Option D: **Your current editor**
- Already have vim, emacs, Sublime? That works too!

---

### Step 3: Create Project Directory

```bash
# Navigate to where you want to work
cd ~/projects  # or wherever you keep code

# Clone neural-dojo (if you haven't already)
git clone https://github.com/krisztiankoos/neural-dojo.git
cd neural-dojo

# Or if you already have it:
cd /Users/krisztiankoos/projects/neural-dojo
```

---

### Step 4: Create Virtual Environment

**Why virtual environments?**
- Isolate project dependencies
- Avoid conflicts between projects
- Reproducible environments

```bash
# Create virtual environment
python -m venv venv
# or on some systems:
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your prompt:
(venv) $
```

**Verify activation**:
```bash
which python
# Should show path to venv/bin/python

pip list
# Should show minimal packages
```

---

### Step 5: Install Initial Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install development tools
pip install pytest pytest-cov black isort flake8 mypy

# Verify installation
pytest --version
black --version
```

**Expected Output**:
```
pytest 7.4.x
black, 23.x.x
```

---

## 🔑 API Keys Setup

You'll need API keys to use LLMs. Let's set them up:

### ⚠️ Important: Subscriptions vs API Access

**Common confusion**: ChatGPT Plus, Claude Pro, and similar subscriptions give you access to use AI via their **web interfaces**, but they do NOT include API access!

**What's the difference?**
- **Subscription (ChatGPT Plus, Claude Pro)**: Pay for web/app access, unlimited usage in browser/app
- **API Access**: Pay-per-use for programmatic access via code (what we need for this curriculum)

**If you have a subscription**:
- ✅ Great for daily use and learning concepts
- ❌ Cannot use it for code examples in this curriculum
- ✅ You can still sign up for API access separately (different billing)

**Good news**: Most providers offer free API credits or very low startup costs!

### Option 1: Anthropic Claude API (Recommended)

1. **Create Account**: https://console.anthropic.com/
2. **Get API Key**: Settings → API Keys → Create Key
3. **Pricing**:
   - Pay-as-you-go (no subscription required)
   - New accounts often get free credits to start
   - Estimated cost for entire curriculum: $3-5
   - You only pay for what you use

**Why recommended**: Latest Sonnet 4.5 model, great for code, generous context window

### Option 2: OpenAI API

1. **Create Account**: https://platform.openai.com/
2. **Get API Key**: API Keys → Create new secret key
3. **Pricing**:
   - Pay-as-you-go
   - Some accounts get $5-18 in free trial credits
   - Estimated cost for curriculum: $5-10
   - Usage limits may apply to new accounts

**Note**: GPT-4 is powerful but more expensive than Claude for similar tasks

### Option 3: Local Models (Free but needs GPU)

- **Ollama**: https://ollama.ai/ (run models locally)
- **llama.cpp**: Run Llama models on your machine
- **Note**: We'll cover this in Module 6

### Option 4: Free API Alternatives (For Experimentation)

If you want to experiment without immediately setting up paid API access:

1. **Hugging Face Inference API** (Free tier available)
   - https://huggingface.co/inference-api
   - Access to many open-source models
   - Limited free usage, then pay-as-you-go

2. **Groq** (Free tier with rate limits)
   - https://console.groq.com/
   - Very fast inference
   - Free tier: 30 requests/minute

3. **Together AI** (Free trial credits)
   - https://www.together.ai/
   - Access to Llama, Mixtral, and other models
   - $25 free credits for new users

4. **Replicate** (Pay-per-use, very low cost)
   - https://replicate.com/
   - Many models available
   - Pay only for compute time used

**For this curriculum**: We recommend starting with Claude or OpenAI API (very affordable!) for best learning experience, but the free alternatives work for initial experimentation.

---

### Store API Keys Securely

**Never commit API keys to git!** Use environment variables instead.

#### Create `.env` file:

```bash
# In neural-dojo directory
touch .env

# Add to .gitignore (already done!)
echo ".env" >> .gitignore
```

#### Add your API keys to `.env`:

```bash
# .env file contents
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here

# Optional: Set default model
DEFAULT_MODEL=claude-sonnet-4-5-20250929
```

#### Install python-dotenv:

```bash
pip install python-dotenv
```

---

## 🧪 Verification: Your First LLM Call

Let's verify everything works!

### Test 1: Environment Check

Create `examples/module_00/test_environment.py`:

```python
"""
Test: Verify Python environment is set up correctly
"""
import sys
import subprocess

def test_python_version():
    """Verify Python 3.10+"""
    version = sys.version_info
    assert version.major == 3
    assert version.minor >= 10
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def test_pip_works():
    """Verify pip is available"""
    result = subprocess.run(
        ["pip", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    print(f"✅ pip works: {result.stdout.strip()}")

def test_imports():
    """Verify key packages can be imported"""
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed - run: pip install python-dotenv")
        return False

    return True

if __name__ == "__main__":
    print("🔍 Testing environment setup...\n")

    test_python_version()
    test_pip_works()
    success = test_imports()

    if success:
        print("\n✅ Environment setup complete!")
    else:
        print("\n❌ Environment setup incomplete. See errors above.")
```

**Run it**:
```bash
cd examples/module_00
python test_environment.py
```

---

### Test 2: Claude API Call

Create `examples/module_00/test_claude_api.py`:

```python
"""
Test: Make your first Claude API call
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_api():
    """Test Claude API with a simple call"""

    # Check API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("   Please add your API key to .env:")
        print("   ANTHROPIC_API_KEY=sk-ant-your-key-here")
        return False

    print("✅ API key found")

    # Try to import anthropic
    try:
        from anthropic import Anthropic
    except ImportError:
        print("❌ anthropic package not installed")
        print("   Run: pip install anthropic")
        return False

    print("✅ anthropic package imported")

    # Make API call
    try:
        client = Anthropic(api_key=api_key)

        print("\n🤖 Making API call to Claude...")

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from Neural Dojo!' and nothing else."
                }
            ]
        )

        response_text = message.content[0].text
        print(f"\n📩 Claude says: {response_text}")

        # Check usage
        print(f"\n📊 Token usage:")
        print(f"   Input tokens: {message.usage.input_tokens}")
        print(f"   Output tokens: {message.usage.output_tokens}")

        return True

    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Claude API...\n")

    # First install anthropic if needed
    print("Installing anthropic package...")
    os.system("pip install -q anthropic")

    success = test_claude_api()

    if success:
        print("\n✅ Claude API working! You're ready to start Module 1.")
    else:
        print("\n❌ Claude API test failed. Check the errors above.")
```

**Run it**:
```bash
python test_claude_api.py
```

**Expected Output**:
```
✅ API key found
✅ anthropic package imported

🤖 Making API call to Claude...

📩 Claude says: Hello from Neural Dojo!

📊 Token usage:
   Input tokens: 15
   Output tokens: 6

✅ Claude API working! You're ready to start Module 1.
```

---

### Test 3: OpenAI API Call (Optional)

Create `examples/module_00/test_openai_api.py`:

```python
"""
Test: OpenAI API call (optional)
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_openai_api():
    """Test OpenAI API with a simple call"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found - this is optional")
        print("   You can skip this if using Claude only")
        return True  # Not a failure

    print("✅ API key found")

    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not installed")
        print("   Run: pip install openai")
        return False

    print("✅ openai package imported")

    try:
        client = OpenAI(api_key=api_key)

        print("\n🤖 Making API call to OpenAI...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model for testing
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from Neural Dojo!' and nothing else."
                }
            ]
        )

        response_text = response.choices[0].message.content
        print(f"\n📩 GPT says: {response_text}")

        print(f"\n📊 Token usage:")
        print(f"   Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   Completion tokens: {response.usage.completion_tokens}")
        print(f"   Total tokens: {response.usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing OpenAI API...\n")

    print("Installing openai package...")
    os.system("pip install -q openai")

    success = test_openai_api()

    if success:
        print("\n✅ OpenAI API working!")
    else:
        print("\n❌ OpenAI API test failed.")
```

---

## 📊 Module 0 Checklist

Use this checklist to verify you're ready for Module 1:

- [ ] Python 3.10+ installed and verified
- [ ] Virtual environment created and activated
- [ ] pip working and packages installable
- [ ] Text editor/IDE chosen and installed
- [ ] neural-dojo repository cloned/accessed
- [ ] `.env` file created with API key(s)
- [ ] `test_environment.py` passes
- [ ] `test_claude_api.py` passes (or `test_openai_api.py`)
- [ ] Basic Python skills confirmed
- [ ] Command line comfortable

**All checked?** ✅ You're ready for Module 1!

---

## 🔧 Troubleshooting

### Problem: "python: command not found"

**Solution**:
- Try `python3` instead of `python`
- Make sure Python is installed
- Check PATH environment variable

### Problem: "pip: command not found"

**Solution**:
- Try `pip3` instead of `pip`
- Install pip: `python -m ensurepip --upgrade`

### Problem: "Module not found" error

**Solution**:
- Make sure virtual environment is activated (see `(venv)` in prompt)
- Try `pip install <package>` again
- Check you're in the right directory

### Problem: "API key not found"

**Solution**:
- Check `.env` file exists
- Check `.env` has correct format: `KEY=value` (no spaces around `=`)
- Make sure you've run `load_dotenv()` in code
- Try printing `os.getenv("ANTHROPIC_API_KEY")` to debug

### Problem: "Permission denied"

**Solution**:
- On Unix/Mac: Don't use `sudo pip install`
- Use virtual environment instead
- Check file/directory permissions

### Problem: "API call fails with authentication error"

**Solution**:
- Verify API key is correct (no extra spaces)
- Check API key hasn't expired
- Verify account has credits (Claude console, OpenAI dashboard)

---

## 💡 Did You Know?

**Virtual environments** are like isolated Python universes. Each project can have its own versions of packages without conflicts. It's like having separate toolboxes for each project!

**API keys** are like passwords for programmatic access. They let you authenticate without logging in every time. Always keep them secret - treat them like credit card numbers!

**The `.env` file** pattern is a best practice from [The Twelve-Factor App](https://12factor.net/config) methodology. It separates configuration from code, making your code more secure and portable.

---

## 📚 Further Reading

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [The Twelve-Factor App](https://12factor.net/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)

---

## ⏭️ Next Steps

**Congratulations!** 🎉 Your development environment is ready.

**Next**: Move on to **Module 1: Foundations of AI-Driven Development**

In Module 1, you'll learn:
- The AI development landscape (2024-2025)
- How to use AI coding assistants effectively
- The mental model of AI pair programming
- When to use AI vs traditional coding approaches

**Ready?** Let's build! 🥋🧠⚡

---

_Last updated: 2025-11-21_
_Module status: ⚪ Not Started_
