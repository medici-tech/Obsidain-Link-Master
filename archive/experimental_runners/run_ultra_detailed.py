#!/usr/bin/env python3
"""
Run Obsidian Auto-Linker with Ultra Detailed Analytics
Qwen3:8b with maximum detail, before/after files, and reasoning analysis
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def setup_ultra_detailed_config():
    """Set up configuration for ultra detailed analytics"""
    print("🚀 Setting up ultra detailed analytics configuration...")
    
    # Copy ultra detailed config to main config
    if os.path.exists('config_qwen3_maximum_detail.yaml'):
        shutil.copy('config_qwen3_maximum_detail.yaml', 'config.yaml')
        print("✅ Ultra detailed analytics configuration applied")
        print("🧠 Using Qwen3:8b for maximum accuracy")
        print("📊 Including before/after files and reasoning analysis")
    else:
        print("⚠️ Ultra detailed config not found, using current config")
    
    return True

def run_processing():
    """Run the auto-linker with ultra detailed analytics"""
    print("🚀 Starting Obsidian Auto-Linker with ultra detailed analytics...")
    print("🧠 Using Qwen3:8b for maximum accuracy and reasoning")
    print("📊 Generating before/after file comparisons")
    print("🧠 Including AI reasoning analysis")
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
    print("=" * 70)
    print("🚀 OBSIDIAN AUTO-LINKER - ULTRA DETAILED ANALYTICS MODE")
    print("🧠 Qwen3:8b + Before/After Files + AI Reasoning Analysis")
    print("=" * 70)
    print()
    
    # Check prerequisites
    if not os.path.exists('obsidian_auto_linker_enhanced.py'):
        print("❌ Enhanced auto-linker script not found!")
        return False
    
    if not ensure_ultra_detailed_analytics():
        print("❌ Ultra detailed analytics setup failed!")
        return False
    
    # Setup configuration
    if not setup_ultra_detailed_config():
        print("❌ Configuration setup failed!")
        return False
    
    print("🎯 Configuration Summary:")
    print("   🧠 Model: Qwen3:8b (maximum accuracy)")
    print("   📊 Ultra detailed analytics: ENABLED")
    print("   📄 Before/after files: ENABLED")
    print("   🧠 AI reasoning analysis: ENABLED")
    print("   🌐 Auto-open report: ENABLED")
    print("   ⚡ Context window: 16,384 tokens")
    print("   📝 Max tokens: 2,048 (maximum detail)")
    print()
    
    # Confirm before proceeding
    try:
        response = input("🚀 Ready to start ultra detailed processing? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Processing cancelled by user")
            return False
    except KeyboardInterrupt:
        print("\n❌ Processing cancelled by user")
        return False
    
    print()
    print("🚀 Starting ultra detailed processing...")
    print("🧠 Using Qwen3:8b for maximum accuracy and detailed reasoning")
    print("📊 Generating comprehensive before/after file analysis")
    print("🧠 Including detailed AI reasoning breakdown")
    print("🌐 Ultra detailed report will open automatically when complete")
    print()
    print("⏱️  Note: This will take longer due to maximum detail settings")
    print("🧠 But you'll get the most comprehensive analysis possible!")
    print()
    
    # Run processing
    start_time = time.time()
    success = run_processing()
    end_time = time.time()
    
    print()
    print("=" * 70)
    if success:
        print("✅ ULTRA DETAILED PROCESSING COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        print("📊 Ultra detailed analytics report generated")
        print("📄 Before/after file analysis included")
        print("🧠 AI reasoning analysis included")
        print("🌐 Ultra detailed report should have opened automatically in your browser")
        print()
        print("📄 Available reports:")
        if os.path.exists('analytics_report.html'):
            print("   📊 Standard report: analytics_report.html")
        if os.path.exists('ultra_detailed_analytics_report.html'):
            print("   🚀 Ultra detailed report: ultra_detailed_analytics_report.html")
    else:
        print("❌ ULTRA DETAILED PROCESSING FAILED!")
        print("📊 Check the output above for error details")
    
    print("=" * 70)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
