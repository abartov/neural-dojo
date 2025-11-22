#!/bin/bash
# Module 1.2: Ollama Installation Script
# Supports macOS, Linux, and Windows (WSL)
# Last updated: 2025-11-22

set -e  # Exit on error

echo "🚀 Ollama Setup for AI Coding - Module 1.2"
echo "=========================================="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    MINGW*)     PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "✓ Detected platform: ${PLATFORM}"
echo ""

# Check system requirements
echo "🔍 Checking system requirements..."

# Check RAM (requires at least 8GB for 7B models)
if [[ "$PLATFORM" == "Mac" ]]; then
    TOTAL_RAM=$(sysctl -n hw.memsize)
    TOTAL_RAM_GB=$((TOTAL_RAM / 1024 / 1024 / 1024))
elif [[ "$PLATFORM" == "Linux" ]]; then
    TOTAL_RAM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_RAM_GB=$((TOTAL_RAM / 1024 / 1024))
else
    TOTAL_RAM_GB=16  # Assume sufficient for Windows/WSL
fi

echo "  RAM: ${TOTAL_RAM_GB}GB"
if [ "$TOTAL_RAM_GB" -lt 8 ]; then
    echo "  ⚠️  Warning: Less than 8GB RAM detected"
    echo "  Recommend using smaller models (Phi-3.5 3.8B or Qwen 1.5B)"
fi

# Check disk space (need ~10-30GB)
if [[ "$PLATFORM" == "Mac" ]]; then
    FREE_SPACE=$(df -g . | tail -1 | awk '{print $4}')
elif [[ "$PLATFORM" == "Linux" ]]; then
    FREE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
else
    FREE_SPACE=50  # Assume sufficient for Windows/WSL
fi

echo "  Disk space: ${FREE_SPACE}GB available"
if [ "$FREE_SPACE" -lt 10 ]; then
    echo "  ❌ Error: Need at least 10GB free disk space"
    exit 1
fi

echo "✓ System requirements met"
echo ""

# Install Ollama
echo "📦 Installing Ollama..."

if [[ "$PLATFORM" == "Mac" ]]; then
    # macOS installation via Homebrew
    if command -v brew &> /dev/null; then
        echo "  Using Homebrew..."
        brew install ollama
    else
        echo "  Homebrew not found, using official installer..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
elif [[ "$PLATFORM" == "Linux" ]] || [[ "$PLATFORM" == "Windows" ]]; then
    # Linux/WSL installation
    echo "  Using official installer..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "  ❌ Unsupported platform: ${PLATFORM}"
    exit 1
fi

echo "✓ Ollama installed"
echo ""

# Start Ollama service
echo "🔧 Starting Ollama service..."

if [[ "$PLATFORM" == "Mac" ]]; then
    # macOS: Start as background service
    brew services start ollama 2>/dev/null || ollama serve > /dev/null 2>&1 &
elif [[ "$PLATFORM" == "Linux" ]] || [[ "$PLATFORM" == "Windows" ]]; then
    # Linux/WSL: Start as background process
    ollama serve > /dev/null 2>&1 &
fi

# Wait for Ollama to start
echo "  Waiting for Ollama to start..."
sleep 3

# Verify Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama service is running"
else
    echo "  ❌ Ollama service failed to start"
    echo "  Try running manually: ollama serve"
    exit 1
fi
echo ""

# Download recommended models
echo "📥 Downloading recommended coding models..."
echo "  (This will take 5-15 minutes depending on your internet speed)"
echo ""

# Determine which models to download based on RAM
if [ "$TOTAL_RAM_GB" -ge 16 ]; then
    MODELS=("qwen2.5-coder:7b" "deepseek-coder-v2:16b")
    echo "  Your system can handle larger models!"
    echo "  Downloading: Qwen 2.5-Coder 7B + DeepSeek Coder V2 16B"
elif [ "$TOTAL_RAM_GB" -ge 8 ]; then
    MODELS=("qwen2.5-coder:7b")
    echo "  Downloading: Qwen 2.5-Coder 7B (recommended for 8GB RAM)"
else
    MODELS=("phi3.5:3.8b")
    echo "  Downloading: Phi-3.5 3.8B (optimized for low-RAM systems)"
fi
echo ""

for model in "${MODELS[@]}"; do
    echo "  Downloading ${model}..."
    if ollama pull "$model"; then
        echo "  ✓ ${model} downloaded successfully"
    else
        echo "  ⚠️  Failed to download ${model}"
    fi
    echo ""
done

echo "✓ Models ready!"
echo ""

# Test the primary model
echo "🧪 Testing model..."
PRIMARY_MODEL="${MODELS[0]}"

echo "  Running test query on ${PRIMARY_MODEL}..."
TEST_RESPONSE=$(ollama run "$PRIMARY_MODEL" "Write a one-line Python function to reverse a string. Just the code, no explanation." --verbose=false 2>/dev/null || echo "FAILED")

if [[ "$TEST_RESPONSE" != "FAILED" ]]; then
    echo "✓ Model test passed!"
    echo ""
    echo "  Test output:"
    echo "  ${TEST_RESPONSE}"
else
    echo "  ⚠️  Model test failed (but model is downloaded)"
fi
echo ""

# List installed models
echo "📋 Installed models:"
ollama list
echo ""

# Installation complete
echo "✅ Setup complete!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Next Steps:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Test your models:"
echo "   python test_local_models.py"
echo ""
echo "2. Try interactive mode:"
echo "   ollama run ${PRIMARY_MODEL}"
echo ""
echo "3. Install Aider (AI coding assistant):"
echo "   pip install aider-chat"
echo "   aider --model ollama/${PRIMARY_MODEL}"
echo ""
echo "4. Configure Continue.dev (VS Code extension):"
echo "   cp continue_config.json ~/.continue/config.json"
echo "   # Then restart VS Code"
echo ""
echo "5. Read the setup guide:"
echo "   cat aider_with_local.md"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "💡 Tips:"
echo "  - Ollama runs on http://localhost:11434"
echo "  - Downloaded models are in ~/.ollama/models/"
echo "  - Stop Ollama: killall ollama"
echo "  - Start Ollama: ollama serve"
echo ""
echo "🎉 Happy coding! You're now saving \$40-100/month on API costs!"
echo ""
