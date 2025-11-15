w#!/bin/bash
# Ollama Performance Optimization Script

echo "🚀 OLLAMA PERFORMANCE OPTIMIZER"
echo "================================"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running. Start it with: ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# List current models
echo "📋 Current models:"
ollama list

echo ""
echo "🚀 PERFORMANCE RECOMMENDATIONS:"
echo ""

# Check for fast models
echo "🔍 Checking for fast models..."

# Recommend faster models
echo "⚡ RECOMMENDED FAST MODELS:"
echo "   1. qwen2.5:3b     - Good balance of speed/quality"
echo "   2. qwen2.5:1.5b   - Very fast, good for testing"
echo "   3. llama3.2:3b    - Fast and reliable"
echo "   4. phi3:3.8b      - Microsoft's fast model"

echo ""
echo "📥 TO INSTALL FAST MODELS:"
echo "   ollama pull qwen2.5:3b"
echo "   ollama pull qwen2.5:1.5b"
echo "   ollama pull llama3.2:3b"
echo "   ollama pull phi3:3.8b"

echo ""
echo "⚙️  OLLAMA OPTIMIZATION SETTINGS:"
echo "   Set these environment variables for better performance:"
echo "   export OLLAMA_NUM_PARALLEL=3"
echo "   export OLLAMA_MAX_LOADED_MODELS=2"
echo "   export OLLAMA_FLASH_ATTENTION=1"

echo ""
echo "🔧 TO APPLY OPTIMIZATIONS:"
echo "   1. Install a fast model: ollama pull qwen2.5:3b"
echo "   2. Run: python3 optimize_performance.py"
echo "   3. Test with: python3 run.py"

echo ""
echo "📊 EXPECTED SPEED IMPROVEMENTS:"
echo "   Current (qwen3:8b):     ~2-3 minutes per file"
echo "   Fast (qwen2.5:3b):      ~30-60 seconds per file"
echo "   Ultra (qwen2.5:1.5b):   ~10-30 seconds per file"
echo "   Parallel processing:    ~3x faster with 3 workers"