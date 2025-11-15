#!/usr/bin/env python3
"""
Test Sequential Processing with 2 Files
Simple test to verify basic functionality before scaling to parallel
"""

import os
import sys
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the parallel processing functions
from obsidian_auto_linker_parallel import (
    get_all_notes, should_process_file, process_conversation_parallel,
    analytics, progress_data, save_progress, load_progress
)

def test_sequential_2_files():
    """Test processing exactly 2 files sequentially"""
    
    print("🧪 TESTING SEQUENTIAL PROCESSING - 2 FILES")
    print("=" * 60)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load progress
    load_progress()
    
    # Get vault path from config
    import yaml
    try:
        with open('configs/config_parallel_timeout.yaml', 'r') as f:
            config = yaml.safe_load(f)
        vault_path = config.get('vault_path', '/Users/medici/Documents/MediciVault')
    except:
        vault_path = '/Users/medici/Documents/MediciVault'
    
    print(f"📁 Vault path: {vault_path}")
    
    # Get existing notes for context
    print("🔍 Loading existing notes for context...")
    existing_notes = get_all_notes(vault_path)
    print(f"   Found {len(existing_notes)} existing notes")
    
    # Find files to process
    print("🔎 Finding files to process...")
    all_files = []
    for root, dirs, files in os.walk(vault_path):
        if '_backups' in root:
            continue
        for file in files:
            if should_process_file(os.path.join(root, file)):
                all_files.append(os.path.join(root, file))
    
    # Filter out already processed files
    all_files = [f for f in all_files if f not in progress_data['processed_files']]
    
    print(f"   Found {len(all_files)} files to process")
    
    if len(all_files) < 2:
        print("❌ Not enough files to test (need at least 2)")
        return False
    
    # Take only the first 2 files
    test_files = all_files[:2]
    print(f"🧪 Testing with 2 files:")
    for i, file_path in enumerate(test_files, 1):
        print(f"   {i}. {os.path.basename(file_path)}")
    
    print()
    
    # Process files sequentially
    results = []
    start_time = time.time()
    
    for i, file_path in enumerate(test_files, 1):
        print(f"📄 Processing file {i}/2: {os.path.basename(file_path)}")
        file_start = time.time()
        
        try:
            result = process_conversation_parallel(file_path, existing_notes, {})
            file_time = time.time() - file_start
            
            results.append(result)
            
            print(f"   ✅ File {i} completed in {file_time:.1f}s")
            print(f"   📊 Success: {result['success']}")
            print(f"   📝 Processed: {result['processed']}")
            print(f"   ⏭️  Skipped: {result['skipped']}")
            print(f"   ❌ Failed: {result['failed']}")
            if result.get('timeout'):
                print(f"   ⏰ Timeout: {result['timeout']}")
            if result.get('error'):
                print(f"   ❌ Error: {result['error']}")
            print(f"   🔗 Links added: {result['links_added']}")
            print(f"   🏷️  Tags added: {result['tags_added']}")
            print(f"   🎯 Confidence: {result['confidence']:.2f}")
            print(f"   📂 MOC Category: {result['moc_category']}")
            print()
            
        except Exception as e:
            print(f"   ❌ Exception processing file {i}: {e}")
            results.append({
                'file_path': file_path,
                'success': False,
                'error': str(e)
            })
            print()
    
    total_time = time.time() - start_time
    
    # Summary
    print("=" * 60)
    print("📊 SEQUENTIAL TEST RESULTS")
    print("=" * 60)
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"📁 Files tested: {len(test_files)}")
    
    successful = sum(1 for r in results if r.get('success', False))
    processed = sum(1 for r in results if r.get('processed', False))
    skipped = sum(1 for r in results if r.get('skipped', False))
    failed = sum(1 for r in results if not r.get('success', False))
    timeouts = sum(1 for r in results if r.get('timeout', False))
    
    print(f"✅ Successful: {successful}/{len(test_files)}")
    print(f"📝 Processed: {processed}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"⏰ Timeouts: {timeouts}")
    
    if successful == len(test_files):
        print("\n🎉 All files processed successfully!")
        print("✅ Sequential processing is working correctly")
        return True
    else:
        print(f"\n⚠️  {len(test_files) - successful} files had issues")
        print("🔍 Check the error messages above for details")
        return False

if __name__ == "__main__":
    print("🧪 Sequential Processing Test - 2 Files")
    print("   Testing basic functionality before parallel processing")
    print()
    
    success = test_sequential_2_files()
    
    if success:
        print("\n✅ Sequential test passed!")
        print("🚀 Ready to scale up to parallel processing")
    else:
        print("\n❌ Sequential test failed!")
        print("🔧 Fix issues before trying parallel processing")






