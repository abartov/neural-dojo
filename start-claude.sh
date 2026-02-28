#!/bin/bash
# Neural Dojo - Claude venv Wrapper
# Starts Claude inside Python virtual environment for AI/ML curriculum

set -e  # Exit on error

# Get script directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🥋 Starting Claude in Neural Dojo..."
echo "📁 Project: $PROJECT_DIR"

# Add GNU coreutils to PATH (if available on macOS)
if [ -d "/opt/homebrew/opt/coreutils/libexec/gnubin" ]; then
    export PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"
    echo "✅ GNU coreutils added to PATH"
fi

# Preflight check: Verify required tools
echo "🔍 Preflight check..."
MISSING_TOOLS=""
for tool in git python3 gh; do
    if ! command -v $tool &> /dev/null; then
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    fi
done

if [ -n "$MISSING_TOOLS" ]; then
    echo "❌ Error: Missing required tools:$MISSING_TOOLS"
    echo "Install with: brew install$MISSING_TOOLS"
    exit 1
fi
echo "✅ All required tools installed"

# Change to project directory
cd "$PROJECT_DIR"

# Check if venv exists, create if missing
if [ ! -f "venv/bin/activate" ]; then
    echo "⚠️  Virtual environment not found, creating..."
    echo "📦 Setting up Python 3.10+ virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        echo "Ensure Python 3.10+ is installed: brew install python@3.11"
        exit 1
    fi

    # Install dependencies
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip

    # Install common ML dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "❌ Error: Failed to install dependencies"
            exit 1
        fi
    else
        echo "ℹ️  No requirements.txt found - installing base dependencies"
        pip install openai anthropic tiktoken numpy pandas matplotlib
    fi

    echo "✅ Virtual environment created and dependencies installed"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated (Python $(python --version))"

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10 ]]; then
    echo "⚠️  Warning: Neural Dojo requires Python 3.10+, got $PYTHON_VERSION"
fi

# Check for API keys (non-blocking, just informational)
echo ""
echo "🔑 Checking API keys..."
API_KEYS_FOUND=0

if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API key found"
    API_KEYS_FOUND=1
fi

if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    echo "✅ Anthropic API key found"
    API_KEYS_FOUND=1
fi

if [ $API_KEYS_FOUND -eq 0 ]; then
    echo "ℹ️  No API keys detected (optional for some modules)"
    echo "   Set with: export OPENAI_API_KEY=sk-... or export ANTHROPIC_API_KEY=sk-ant-..."
fi

# Check if Qdrant is running (optional, needed for later modules)
if command -v curl &> /dev/null; then
    if curl -s http://localhost:6333/health &> /dev/null; then
        echo "✅ Qdrant VectorDB is running"
    else
        echo "ℹ️  Qdrant not running (needed for Phase 3 modules - start with: docker run -p 6333:6333 qdrant/qdrant)"
    fi
fi

# Show curriculum status and helpful reminders
echo ""
echo "📚 Neural Dojo Curriculum 🥋🧠⚡"
echo ""

# Check if START_HERE_TOMORROW.md exists and show recent status
if [ -f "docs/curriculum/START_HERE_TOMORROW.md" ]; then
    echo "📋 Session Handoff:"
    head -n 20 docs/curriculum/START_HERE_TOMORROW.md | grep -E "^(#|Status|Module|Phase)" || echo "   (see START_HERE_TOMORROW.md for details)"
    echo ""
fi

# Show quick reminders
echo "💡 Quick Start:"
echo "   • Session handoff: docs/curriculum/START_HERE_TOMORROW.md"
echo "   • Master curriculum: docs/curriculum/MASTER_CURRICULUM.md"
echo "   • Session history: docs/curriculum/notes/session_log.md"
echo "   • Guidelines: CLAUDE.md"

# Start Claude
echo ""
echo "🤖 Launching Claude Code..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
claude "$@"
