#!/usr/bin/env python3
"""
Fast Parallel Processing - Bypasses connection tests
"""

import os
import sys
import time
from datetime import datetime

def main():
    print("🚀 FAST PARALLEL PROCESSING")
    print("=" * 50)
    print(f"⏰ Start: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Check if files exist
    if not os.path.exists('obsidian_auto_linker_parallel.py'):
        print("❌ Parallel script not found")
        return
    
    if not os.path.exists('configs/config_parallel_optimized.yaml'):
        print("❌ Parallel config not found")
        return
    
    print("🔧 Configuration:")
    print("   📦 Batch size: 7 files per batch")
    print("   ⚡ Parallel workers: 3 threads")
    print("   🤖 Model: qwen3:8b")
    print("   🚀 Mode: Real processing")
    print()
    
    # Start processing
    start_time = time.time()
    
    try:
        print("🚀 Starting parallel processing...")
        print("   (Skipping connection test for speed)")
        print()
        
        # Run the parallel processing script
        import subprocess
        result = subprocess.run([
            sys.executable, 'obsidian_auto_linker_parallel.py'
        ], capture_output=False, text=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 50)
        print("📊 PARALLEL PROCESSING COMPLETE")
        print("=" * 50)
        print(f"⏰ Total time: {total_time:.1f} seconds")
        print(f"📊 Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Success!")
        else:
            print("❌ Errors occurred")
            
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

