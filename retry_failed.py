#!/usr/bin/env python3
"""
Retry Failed Files Script
Processes only the files that previously failed
"""

import json
import os
import sys
from pathlib import Path

def retry_failed_files():
    """Retry only the files that previously failed"""
    
    progress_file = '.processing_progress.json'
    
    if not os.path.exists(progress_file):
        print("❌ No progress file found. Run the main software first.")
        return
    
    # Load failed files
    with open(progress_file, 'r') as f:
        data = json.load(f)
    
    failed_files = data.get('failed_files', [])
    
    if not failed_files:
        print("✅ No failed files to retry!")
        return
    
    print(f"🔄 Found {len(failed_files)} failed files to retry:")
    for i, file_path in enumerate(failed_files, 1):
        filename = os.path.basename(file_path)
        print(f"  {i:2d}. {filename}")
    
    print(f"\n📊 Retry Options:")
    print(f"   1. Retry all failed files")
    print(f"   2. Retry specific files")
    print(f"   3. Clear failed files list")
    print(f"   4. Exit")
    
    try:
        choice = input("\nChoose option (1-4): ").strip()
    except EOFError:
        choice = "1"
        print("Using default: 1")
    
    if choice == "1":
        # Retry all failed files
        print(f"\n🚀 Retrying all {len(failed_files)} failed files...")
        
        # Clear the failed files list so they can be retried
        data['failed_files'] = []
        with open(progress_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("✅ Cleared failed files list. Run the main software to retry them.")
        print("   Command: python3 run.py")
        
    elif choice == "2":
        # Retry specific files
        print(f"\n📋 Select files to retry (enter numbers separated by commas):")
        try:
            selection = input("Enter file numbers: ").strip()
            if not selection:
                print("❌ No selection made")
                return
            
            # Parse selection
            indices = []
            for num in selection.split(','):
                try:
                    idx = int(num.strip()) - 1
                    if 0 <= idx < len(failed_files):
                        indices.append(idx)
                except ValueError:
                    print(f"⚠️  Invalid number: {num}")
            
            if not indices:
                print("❌ No valid files selected")
                return
            
            # Remove selected files from failed list
            selected_files = [failed_files[i] for i in indices]
            remaining_files = [f for i, f in enumerate(failed_files) if i not in indices]
            
            data['failed_files'] = remaining_files
            with open(progress_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Selected {len(selected_files)} files for retry:")
            for file_path in selected_files:
                print(f"   - {os.path.basename(file_path)}")
            print("   Run the main software to retry them.")
            print("   Command: python3 run.py")
            
        except EOFError:
            print("❌ No selection made")
            return
    
    elif choice == "3":
        # Clear failed files list
        data['failed_files'] = []
        with open(progress_file, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Cleared all failed files from the list")
        
    elif choice == "4":
        print("👋 Exiting")
        return
    
    else:
        print("❌ Invalid choice")

def show_failed_files():
    """Show detailed information about failed files"""
    
    progress_file = '.processing_progress.json'
    
    if not os.path.exists(progress_file):
        print("❌ No progress file found")
        return
    
    with open(progress_file, 'r') as f:
        data = json.load(f)
    
    failed_files = data.get('failed_files', [])
    processed_files = data.get('processed_files', [])
    
    print("📊 PROCESSING STATUS")
    print("=" * 50)
    print(f"✅ Processed: {len(processed_files)}")
    print(f"❌ Failed: {len(failed_files)}")
    print(f"📅 Last Update: {data.get('last_update', 'Unknown')}")
    
    if failed_files:
        print(f"\n❌ FAILED FILES ({len(failed_files)}):")
        for i, file_path in enumerate(failed_files, 1):
            filename = os.path.basename(file_path)
            exists = "✅" if os.path.exists(file_path) else "❌"
            print(f"  {i:2d}. {exists} {filename}")
    
    print(f"\n💡 To retry failed files, run: python3 retry_failed.py")

if __name__ == "__main__":
    print("🔄 OBSIDIAN AUTO-LINKER - RETRY FAILED FILES")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_failed_files()
    else:
        retry_failed_files()
