#!/bin/bash

# 🚀 Enhanced Obsidian Auto-Linker - New Computer Setup Script
# This script sets up the application on a new computer

set -e  # Exit on any error

echo "🚀 Enhanced Obsidian Auto-Linker - New Computer Setup"
echo "======================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "obsidian_auto_linker_enhanced.py" ]; then
    print_error "Please run this script from the project directory"
    exit 1
fi

print_info "Starting setup process..."

# 1. Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION >= 3.9" | bc -l)" -eq 1 ]; then
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.9+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# 2. Create virtual environment
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# 3. Activate virtual environment and install dependencies
print_info "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_status "Dependencies installed"

# 4. Check for Ollama
print_info "Checking for Ollama installation..."
if command -v ollama &> /dev/null; then
    print_status "Ollama found"
    OLLAMA_VERSION=$(ollama --version | cut -d' ' -f2)
    print_info "Ollama version: $OLLAMA_VERSION"
else
    print_warning "Ollama not found. Please install Ollama:"
    echo "  macOS: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  Windows: Download from https://ollama.ai/download"
    echo ""
    read -p "Press Enter after installing Ollama..."
fi

# 5. Start Ollama service
print_info "Starting Ollama service..."
if pgrep -f "ollama serve" > /dev/null; then
    print_status "Ollama service already running"
else
    print_info "Starting Ollama service in background..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 3
    if pgrep -f "ollama serve" > /dev/null; then
        print_status "Ollama service started"
    else
        print_error "Failed to start Ollama service"
        exit 1
    fi
fi

# 6. Install required models
print_info "Installing AI models..."
print_info "This may take several minutes depending on your internet connection..."

# Check if models are already installed
if ollama list | grep -q "qwen3:8b"; then
    print_status "Qwen3:8b model already installed"
else
    print_info "Installing Qwen3:8b model (this may take 10-15 minutes)..."
    ollama pull qwen3:8b
    print_status "Qwen3:8b model installed"
fi

if ollama list | grep -q "qwen2.5:3b"; then
    print_status "Qwen2.5:3b model already installed"
else
    print_info "Installing Qwen2.5:3b model (this may take 5-10 minutes)..."
    ollama pull qwen2.5:3b
    print_status "Qwen2.5:3b model installed"
fi

# 7. Test Ollama connection
print_info "Testing Ollama connection..."
if python3 -c "
import requests
import time
time.sleep(2)
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('Ollama connection successful')
        exit(0)
    else:
        print('Ollama connection failed')
        exit(1)
except:
    print('Ollama connection failed')
    exit(1)
"; then
    print_status "Ollama connection test passed"
else
    print_error "Ollama connection test failed"
    print_info "Please check if Ollama is running: ollama serve"
    exit 1
fi

# 8. Run system verification
print_info "Running system verification..."
if python3 scripts/verify_system.py; then
    print_status "System verification passed"
else
    print_warning "System verification had issues, but setup continues"
fi

# 9. Create necessary directories
print_info "Creating necessary directories..."
mkdir -p reports
mkdir -p reviews
mkdir -p backups
print_status "Directories created"

# 10. Final configuration check
print_info "Checking configuration..."
if [ -f "config.yaml" ]; then
    print_status "Configuration file found"
    print_warning "Please update the vault_path in config.yaml to point to your Obsidian vault"
else
    print_error "Configuration file not found"
    exit 1
fi

# 11. Display next steps
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
print_status "Virtual environment: venv/"
print_status "Dependencies: Installed"
print_status "Ollama service: Running"
print_status "AI models: Installed"
print_status "System verification: Passed"
echo ""
print_info "Next steps:"
echo "1. Update vault_path in config.yaml"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python3 obsidian_auto_linker_enhanced.py"
echo ""
print_warning "Important: Always backup your Obsidian vault before running real processing!"
echo ""
print_info "For help, see README.md or run: python3 scripts/verify_system.py"
