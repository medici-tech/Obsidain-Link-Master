#!/usr/bin/env python3
"""
Run Parallel Processing Obsidian Auto-Linker with Timeout Management
Optimized to prevent stuck workers and improve processing efficiency
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_parallel_processing_with_timeout():
    """Run the parallel processing version with timeout management"""
    
    print("🚀 Starting Parallel Processing with Timeout Management")
    print("=" * 60)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if config exists
    if not os.path.exists('configs/config_parallel_timeout.yaml'):
        print("❌ Timeout config not found. Please ensure configs/config_parallel_timeout.yaml exists.")
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
        print("   📦 Batch size: 5 files per batch (reduced for timeout management)")
        print("   ⚡ Parallel workers: 3 threads")
        print("   🤖 Model: qwen3:8b")
        print("   ⏰ File timeout: 60 seconds per file")
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
        print("📊 PARALLEL PROCESSING WITH TIMEOUT SUMMARY")
        print("=" * 60)
        print(f"⏰ Total execution time: {total_time:.1f} seconds")
        print(f"📊 Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Parallel processing with timeout management completed successfully!")
            print("📊 Check parallel_processing_analytics.html for detailed results")
        else:
            print("❌ Parallel processing encountered errors")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running parallel processing: {e}")
        return False

def show_timeout_benefits():
    """Show the benefits of timeout management"""
    
    print("\n" + "=" * 60)
    print("⏰ TIMEOUT MANAGEMENT BENEFITS")
    print("=" * 60)
    
    print("🔧 Timeout Configuration:")
    print("   📁 File processing timeout: 60 seconds per file")
    print("   🤖 AI call timeout: 30 seconds per call")
    print("   📦 Batch timeout: 120 seconds per batch")
    print("   ⚡ Retry timeout: 60 seconds max")
    print()
    
    print("🚀 Expected Improvements:")
    print("   ✅ No more stuck workers")
    print("   ✅ Faster processing of problematic files")
    print("   ✅ Better resource utilization")
    print("   ✅ More reliable parallel processing")
    print("   ✅ Clear timeout reporting in analytics")
    print()
    
    print("📊 Timeout Tracking:")
    print("   ⏰ Files that timeout are tracked separately")
    print("   📈 Analytics show timeout vs failure rates")
    print("   🔄 Timeout files can be retried later")
    print("   📝 Clear error messages for timeouts")

if __name__ == "__main__":
    print("🚀 Parallel Processing with Timeout Management")
    print("   Prevents stuck workers and improves efficiency")
    print()
    
    # Show timeout benefits
    show_timeout_benefits()
    
    # Run parallel processing
    success = run_parallel_processing_with_timeout()
    
    if success:
        print("\n✅ Parallel processing with timeout management completed!")
        print("📊 Check the analytics report for detailed performance metrics")
        print("⏰ Timeout files are tracked and can be retried if needed")
    else:
        print("\n❌ Parallel processing failed!")
        print("🔧 Check the error messages above for troubleshooting")






