#!/usr/bin/env python3
"""
Run Obsidian Auto-Linker with Maximum Detailed Analytics
Automatically opens comprehensive report when complete
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def setup_detailed_config():
    """Set up configuration for maximum detailed analytics"""
    print("🔧 Setting up detailed analytics configuration...")
    
    # Copy detailed config to main config
    if os.path.exists('config_detailed_analytics.yaml'):
        shutil.copy('config_detailed_analytics.yaml', 'config.yaml')
        print("✅ Detailed analytics configuration applied")
    else:
        print("⚠️ Detailed config not found, using current config")
    
    return True

def run_processing():
    """Run the auto-linker with detailed analytics"""
    print("🚀 Starting Obsidian Auto-Linker with detailed analytics...")
    print("📊 This will generate the most comprehensive analytics possible")
    print("🌐 Report will open automatically when complete")
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

def ensure_enhanced_analytics():
    """Ensure enhanced analytics script is available"""
    if not os.path.exists('enhanced_analytics.py'):
        print("❌ Enhanced analytics script not found!")
        return False
    
    # Make it executable
    os.chmod('enhanced_analytics.py', 0o755)
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("📊 OBSIDIAN AUTO-LINKER - DETAILED ANALYTICS MODE")
    print("=" * 60)
    print()
    
    # Check prerequisites
    if not os.path.exists('obsidian_auto_linker_enhanced.py'):
        print("❌ Enhanced auto-linker script not found!")
        return False
    
    if not ensure_enhanced_analytics():
        print("❌ Enhanced analytics setup failed!")
        return False
    
    # Setup configuration
    if not setup_detailed_config():
        print("❌ Configuration setup failed!")
        return False
    
    print("🎯 Configuration Summary:")
    print("   📊 Maximum detailed analytics: ENABLED")
    print("   🌐 Auto-open report: ENABLED")
    print("   🔍 Comprehensive reporting: ENABLED")
    print("   ⚡ Full AI analysis: ENABLED")
    print()
    
    # Confirm before proceeding
    try:
        response = input("🚀 Ready to start processing with detailed analytics? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Processing cancelled by user")
            return False
    except KeyboardInterrupt:
        print("\n❌ Processing cancelled by user")
        return False
    
    print()
    print("🚀 Starting processing...")
    print("📊 Detailed analytics will be generated throughout the process")
    print("🌐 Comprehensive report will open automatically when complete")
    print()
    
    # Run processing
    start_time = time.time()
    success = run_processing()
    end_time = time.time()
    
    print()
    print("=" * 60)
    if success:
        print("✅ PROCESSING COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        print("📊 Comprehensive analytics report generated")
        print("🌐 Report should have opened automatically in your browser")
        print()
        print("📄 Available reports:")
        if os.path.exists('analytics_report.html'):
            print("   📊 Standard report: analytics_report.html")
        if os.path.exists('comprehensive_analytics_report.html'):
            print("   📈 Enhanced report: comprehensive_analytics_report.html")
    else:
        print("❌ PROCESSING FAILED!")
        print("📊 Check the output above for error details")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
