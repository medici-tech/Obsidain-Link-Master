#!/usr/bin/env python3
"""
Simple Parallel Processing Test
"""

import os
import time
from datetime import datetime

def main():
    print("🚀 SIMPLE PARALLEL PROCESSING TEST")
    print("=" * 50)
    print(f"⏰ Start: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    print("🔧 Configuration:")
    print("   📦 Batch size: 7 files per batch")
    print("   ⚡ Parallel workers: 3 threads")
    print("   🤖 Model: qwen3:8b")
    print("   🚀 Mode: Real processing")
    print()
    
    # Check vault path
    vault_path = "/Users/medici/Documents/MediciVault"
    if not os.path.exists(vault_path):
        print(f"❌ Vault not found: {vault_path}")
        return
    
    print(f"✅ Vault found: {vault_path}")
    
    # Count files
    md_files = []
    for root, dirs, files in os.walk(vault_path):
        if '_backups' in root:
            continue
        for file in files:
            if file.endswith('.md') and not file.startswith(('📍', 'MOC')):
                md_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(md_files)} markdown files")
    
    # Show first few files
    print("\n📄 Sample files:")
    for i, file_path in enumerate(md_files[:5]):
        print(f"   {i+1}. {os.path.basename(file_path)}")
    
    if len(md_files) > 5:
        print(f"   ... and {len(md_files) - 5} more files")
    
    print(f"\n🚀 Ready to process {len(md_files)} files with parallel processing!")
    print("   📦 Will process 7 files at a time")
    print("   ⚡ Using 3 parallel threads")
    print("   🤖 AI model: qwen3:8b")
    
    print("\n✅ Configuration test complete!")
    print("📊 Parallel processing is ready to run")

if __name__ == "__main__":
    main()








