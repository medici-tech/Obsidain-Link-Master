#!/bin/bash

# 🚀 Enhanced Obsidian Auto-Linker - Quick Activation Script
# This script activates the environment and runs the application

echo "🚀 Enhanced Obsidian Auto-Linker"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./scripts/setup_new_computer.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is running
echo "🔍 Checking Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "⚠️  Ollama service not running. Starting it now..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 3
    
    if pgrep -f "ollama serve" > /dev/null; then
        echo "✅ Ollama service started"
    else
        echo "❌ Failed to start Ollama service"
        echo "Please start Ollama manually: ollama serve"
        exit 1
    fi
else
    echo "✅ Ollama service is running"
fi

# Check if models are available
echo "🤖 Checking AI models..."
if ollama list | grep -q "qwen3:8b"; then
    echo "✅ Qwen3:8b model available"
else
    echo "⚠️  Qwen3:8b model not found"
    echo "Installing model (this may take 10-15 minutes)..."
    ollama pull qwen3:8b
fi

if ollama list | grep -q "qwen2.5:3b"; then
    echo "✅ Qwen2.5:3b model available"
else
    echo "⚠️  Qwen2.5:3b model not found"
    echo "Installing model (this may take 5-10 minutes)..."
    ollama pull qwen2.5:3b
fi

# Test Ollama connection
echo "🧪 Testing Ollama connection..."
if python3 -c "
import requests
import time
time.sleep(2)
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('✅ Ollama connection successful')
        exit(0)
    else:
        print('❌ Ollama connection failed')
        exit(1)
except:
    print('❌ Ollama connection failed')
    exit(1)
"; then
    echo "✅ Ollama connection test passed"
else
    echo "❌ Ollama connection test failed"
    echo "Please check Ollama service: ollama serve"
    exit 1
fi

# Check configuration
echo "⚙️  Checking configuration..."
if [ -f "config.yaml" ]; then
    echo "✅ Configuration file found"
    
    # Check if vault path is set
    if grep -q "vault_path:" config.yaml; then
        VAULT_PATH=$(grep "vault_path:" config.yaml | cut -d' ' -f2)
        if [ -d "$VAULT_PATH" ]; then
            echo "✅ Vault path is valid: $VAULT_PATH"
        else
            echo "⚠️  Vault path not found: $VAULT_PATH"
            echo "Please update vault_path in config.yaml"
        fi
    else
        echo "⚠️  vault_path not set in config.yaml"
        echo "Please update config.yaml with your vault path"
    fi
else
    echo "❌ Configuration file not found"
    echo "Please create config.yaml or run setup"
    exit 1
fi

echo ""
echo "🎉 Environment ready!"
echo "==================="
echo ""
echo "Options:"
echo "1. 🚀 Run Enhanced Auto-Linker"
echo "2. 🧪 Run system verification"
echo "3. 📊 Run performance test"
echo "4. ❌ Exit"
echo ""

read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting Enhanced Obsidian Auto-Linker..."
        python3 obsidian_auto_linker_enhanced.py
        ;;
    2)
        echo "🧪 Running system verification..."
        python3 scripts/verify_system.py
        ;;
    3)
        echo "📊 Running performance test..."
        python3 scripts/model_performance_test.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac