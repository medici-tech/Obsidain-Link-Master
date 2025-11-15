#!/bin/bash

# Parallel Processing Obsidian Auto-Linker
# Optimized for maximum speed with batch processing and parallel workers

echo "🚀 Starting Parallel Processing Obsidian Auto-Linker"
echo "============================================================"
echo "⏰ Start time: $(date)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required files exist
if [ ! -f "obsidian_auto_linker_parallel.py" ]; then
    echo "❌ Parallel processing script not found."
    exit 1
fi

if [ ! -f "configs/config_parallel_optimized.yaml" ]; then
    echo "❌ Parallel config not found."
    exit 1
fi

# Run parallel processing
echo "🚀 Starting parallel processing with optimized settings..."
echo "   📦 Batch size: 7 files per batch"
echo "   ⚡ Parallel workers: 3 threads"
echo "   🤖 Model: qwen3:8b"
echo "   🚀 Mode: Real processing (files will be modified)"
echo ""

python3 obsidian_auto_linker_parallel.py

# Check if analytics report was generated
if [ -f "parallel_processing_analytics.html" ]; then
    echo ""
    echo "📊 Analytics report generated: parallel_processing_analytics.html"
    echo "🔍 Opening analytics report..."
    open parallel_processing_analytics.html
fi

echo ""
echo "✅ Parallel processing completed!"
echo "📊 Check the analytics report for detailed performance metrics"

