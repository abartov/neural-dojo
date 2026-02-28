#!/bin/bash
# Neural Dojo - MkDocs Development Server
# Starts MkDocs server on port 8002 (kills any existing process on that port first)

set -e  # Exit on error

PORT=8002
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🥋 Starting Neural Dojo Documentation Server..."
echo "📁 Project: $PROJECT_DIR"
echo "🌐 Port: $PORT"

cd "$PROJECT_DIR"

# Check if something is running on port 8002
echo ""
echo "🔍 Checking port $PORT..."
PID=$(lsof -ti tcp:$PORT 2>/dev/null || true)

if [ ! -z "$PID" ]; then
    echo "⚠️  Found process $PID running on port $PORT"
    echo "🔪 Killing process..."
    kill -9 $PID 2>/dev/null || true
    sleep 1

    # Verify it's killed
    if lsof -ti tcp:$PORT >/dev/null 2>&1; then
        echo "❌ Failed to kill process on port $PORT"
        echo "   Try manually: kill -9 $(lsof -ti tcp:$PORT)"
        exit 1
    fi
    echo "✅ Process killed successfully"
else
    echo "✅ Port $PORT is available"
fi

# Check if venv exists and activate it
if [ -f "venv/bin/activate" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
    echo "   Create one with: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi

# Check if mkdocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "❌ Error: mkdocs not found"
    echo "   Install with: pip install mkdocs-material mkdocs-minify-plugin"
    exit 1
fi

echo ""
echo "🚀 Starting MkDocs server on http://localhost:$PORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start MkDocs server
mkdocs serve -a localhost:$PORT
