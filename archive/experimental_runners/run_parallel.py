#!/usr/bin/env python3
"""
Run Parallel Processing Obsidian Auto-Linker
Optimized for maximum speed with batch processing and parallel workers
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_parallel_processing():
    """Run the parallel processing version"""
    
    print("🚀 Starting Parallel Processing Obsidian Auto-Linker")
    print("=" * 60)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if config exists
    if not os.path.exists('configs/config_parallel_optimized.yaml'):
        print("❌ Parallel config not found. Please ensure configs/config_parallel_optimized.yaml exists.")
        return False
    
    # Check if parallel script exists
    if not os.path.exists('obsidian_auto_linker_parallel.py'):
        print("❌ Parallel script not found. Please ensure obsidian_auto_linker_parallel.py exists.")
        return False
    
    # Record start time for speed comparison
    start_time = time.time()
    
    try:
        # Run the parallel processing script
        print("🔧 Configuration:")
        print("   📦 Batch size: 7 files per batch")
        print("   ⚡ Parallel workers: 3 threads")
        print("   🤖 Model: qwen3:8b")
        print("   🚀 Mode: Real processing (files will be modified)")
        print()
        
        # Execute the parallel processing
        result = subprocess.run([
            sys.executable, 'obsidian_auto_linker_parallel.py'
        ], capture_output=False, text=True)
        
        # Record end time
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 PARALLEL PROCESSING SUMMARY")
        print("=" * 60)
        print(f"⏰ Total execution time: {total_time:.1f} seconds")
        print(f"📊 Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Parallel processing completed successfully!")
            print("📊 Check parallel_processing_analytics.html for detailed results")
        else:
            print("❌ Parallel processing encountered errors")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running parallel processing: {e}")
        return False

def compare_with_sequential():
    """Compare parallel processing with sequential processing"""
    
    print("\n" + "=" * 60)
    print("📈 SPEED COMPARISON ANALYSIS")
    print("=" * 60)
    
    # This would typically load previous sequential processing times
    # For now, we'll show the parallel processing metrics
    print("🔧 Parallel Processing Configuration:")
    print("   📦 Batch size: 7 files per batch")
    print("   ⚡ Parallel workers: 3 threads")
    print("   🚀 Expected speed improvement: 2-3x faster than sequential")
    print()
    print("📊 To get accurate comparison:")
    print("   1. Run sequential processing first (single file, single thread)")
    print("   2. Record the processing time")
    print("   3. Run this parallel processing")
    print("   4. Compare the results in the analytics report")

if __name__ == "__main__":
    print("🚀 Parallel Processing Obsidian Auto-Linker")
    print("   Optimized for maximum speed with batch processing")
    print()
    
    # Run parallel processing
    success = run_parallel_processing()
    
    if success:
        # Show comparison info
        compare_with_sequential()
        
        print("\n✅ Parallel processing completed!")
        print("📊 Check the analytics report for detailed performance metrics")
    else:
        print("\n❌ Parallel processing failed!")
        print("🔧 Check the error messages above for troubleshooting")

