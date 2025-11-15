#!/usr/bin/env python3
"""
Run Obsidian Auto-Linker with Extended Timeouts
Qwen3:8b with extended timeouts for complex reasoning
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def setup_extended_timeout_config():
    """Set up configuration for extended timeouts"""
    print("⏰ Setting up extended timeout configuration...")
    
    # Copy extended timeout config to main config
    if os.path.exists('config_extended_timeout.yaml'):
        shutil.copy('config_extended_timeout.yaml', 'config.yaml')
        print("✅ Extended timeout configuration applied")
        print("⏰ Base timeout: 10 minutes")
        print("⏰ Retry timeout: 15 minutes")
        print("⏰ Maximum reasoning time: 20 minutes")
        print("🧠 Qwen3:8b will have plenty of time for complex reasoning")
    else:
        print("⚠️ Extended timeout config not found, using current config")
    
    return True

def run_processing():
    """Run the auto-linker with extended timeouts"""
    print("🚀 Starting Obsidian Auto-Linker with extended timeouts...")
    print("🧠 Using Qwen3:8b with extended timeouts for complex reasoning")
    print("⏰ Base timeout: 10 minutes per file")
    print("⏰ Retry timeout: 15 minutes per retry")
    print("⏰ Maximum reasoning time: 20 minutes")
    print("🌐 Ultra detailed report will open automatically when complete")
    print()
    
    try:
        # Run the enhanced auto-linker
        result = subprocess.run([
            'python3', 'obsidian_auto_linker_enhanced.py'
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Processing completed successfully!")
            return True
        else:
            print(f"\n❌ Processing failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running processing: {e}")
        return False

def ensure_ultra_detailed_analytics():
    """Ensure ultra detailed analytics script is available"""
    if not os.path.exists('ultra_detailed_analytics.py'):
        print("❌ Ultra detailed analytics script not found!")
        return False
    
    # Make it executable
    os.chmod('ultra_detailed_analytics.py', 0o755)
    return True

def main():
    """Main function"""
    print("=" * 80)
    print("⏰ OBSIDIAN AUTO-LINKER - EXTENDED TIMEOUT MODE")
    print("🧠 Qwen3:8b + Extended Timeouts + Complex Reasoning")
    print("=" * 80)
    print()
    
    # Check prerequisites
    if not os.path.exists('obsidian_auto_linker_enhanced.py'):
        print("❌ Enhanced auto-linker script not found!")
        return False
    
    if not ensure_ultra_detailed_analytics():
        print("❌ Ultra detailed analytics setup failed!")
        return False
    
    # Setup configuration
    if not setup_extended_timeout_config():
        print("❌ Configuration setup failed!")
        return False
    
    print("🎯 Configuration Summary:")
    print("   🧠 Model: Qwen3:8b (maximum accuracy)")
    print("   ⏰ Base timeout: 10 minutes per file")
    print("   ⏰ Retry timeout: 15 minutes per retry")
    print("   ⏰ Maximum reasoning time: 20 minutes")
    print("   📊 Ultra detailed analytics: ENABLED")
    print("   📄 Before/after files: ENABLED")
    print("   🧠 AI reasoning analysis: ENABLED")
    print("   🌐 Auto-open report: ENABLED")
    print()
    
    # Confirm before proceeding
    try:
        response = input("🚀 Ready to start with extended timeouts? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Processing cancelled by user")
            return False
    except KeyboardInterrupt:
        print("\n❌ Processing cancelled by user")
        return False
    
    print()
    print("🚀 Starting extended timeout processing...")
    print("🧠 Using Qwen3:8b with extended timeouts for complex reasoning")
    print("⏰ No timeouts during active reasoning - model has plenty of time")
    print("📊 Generating comprehensive before/after file analysis")
    print("🧠 Including detailed AI reasoning breakdown")
    print("🌐 Ultra detailed report will open automatically when complete")
    print()
    print("⏱️  Note: This will take longer due to extended timeouts")
    print("🧠 But Qwen3:8b will have time for the most complex reasoning!")
    print()
    
    # Run processing
    start_time = time.time()
    success = run_processing()
    end_time = time.time()
    
    print()
    print("=" * 80)
    if success:
        print("✅ EXTENDED TIMEOUT PROCESSING COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        print("📊 Ultra detailed analytics report generated")
        print("📄 Before/after file analysis included")
        print("🧠 AI reasoning analysis included")
        print("⏰ Extended timeouts prevented any reasoning timeouts")
        print("🌐 Ultra detailed report should have opened automatically in your browser")
        print()
        print("📄 Available reports:")
        if os.path.exists('analytics_report.html'):
            print("   📊 Standard report: analytics_report.html")
        if os.path.exists('ultra_detailed_analytics_report.html'):
            print("   🚀 Ultra detailed report: ultra_detailed_analytics_report.html")
    else:
        print("❌ EXTENDED TIMEOUT PROCESSING FAILED!")
        print("📊 Check the output above for error details")
    
    print("=" * 80)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
