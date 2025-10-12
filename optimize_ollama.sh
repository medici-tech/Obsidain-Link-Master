#!/bin/bash
# Ollama Optimization Script
# Run this to optimize Ollama for better performance and fewer timeouts

echo "🚀 Optimizing Ollama for Auto-Linker..."

# 1. Set environment variables for better performance
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*
export OLLAMA_KEEP_ALIVE=5m
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_MAX_QUEUE=1

# 2. Set system limits (if on macOS/Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS optimizations
    echo "🍎 Applying macOS optimizations..."
    
    # Increase file descriptor limits
    ulimit -n 65536 2>/dev/null || true
    
    # Set memory limits
    ulimit -m 8388608 2>/dev/null || true  # 8GB
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux optimizations
    echo "🐧 Applying Linux optimizations..."
    
    # Increase file descriptor limits
    ulimit -n 65536 2>/dev/null || true
    
    # Set memory limits
    ulimit -m 8388608 2>/dev/null || true  # 8GB
fi

# 3. Kill any existing Ollama processes
echo "🔄 Restarting Ollama..."
pkill ollama 2>/dev/null || true
sleep 2

# 4. Start Ollama with optimized settings
echo "🚀 Starting Ollama with optimizations..."
ollama serve &
sleep 3

# 5. Pre-load the model to avoid cold starts
echo "📦 Pre-loading model..."
ollama run qwen3:8b "Hello" > /dev/null 2>&1 || true

echo "✅ Ollama optimization complete!"
echo "💡 Tips to prevent timeouts:"
echo "   - Close other memory-intensive applications"
echo "   - Ensure you have at least 8GB RAM available"
echo "   - Use a smaller model if qwen3:8b is too slow"
echo "   - Consider using llama3.2:3b for faster responses"
