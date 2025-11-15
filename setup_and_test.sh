#!/bin/bash
# Quick setup script for testing

echo "🔧 Installing dependencies..."

# Install all requirements
pip3 install -r requirements.txt

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "Running tests..."
echo ""

# Run pytest
pytest -v

echo ""
echo "📊 Test summary complete!"
