#!/bin/bash
# Activation script for Obsidian Auto-Linker virtual environment

echo "🚀 Activating Obsidian Auto-Linker environment..."
echo "=" * 50

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating it now..."
    python3 -m venv venv
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Virtual environment created and dependencies installed!"
else
    echo "✅ Virtual environment found"
fi

# Activate the virtual environment
source venv/bin/activate

echo "🐍 Python path: $(which python3)"
echo "📦 Dependencies:"
python3 -c "import requests, tqdm, yaml, psutil; print('✅ All imports successful!')"

echo ""
echo "🎉 Environment activated! You can now run:"
echo "   python3 obsidian_auto_linker_enhanced.py"
echo ""
echo "💡 To deactivate, run: deactivate"

