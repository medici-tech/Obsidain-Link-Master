#!/usr/bin/env python3
"""
Quick Analytics Report Generator
Shows detailed analytics in terminal
"""

import json
import os
from datetime import datetime

def quick_report():
    """Generate a quick terminal report"""
    
    analytics_file = 'processing_analytics.json'
    if not os.path.exists(analytics_file):
        print("❌ No analytics data found. Run the software first.")
        return
    
    with open(analytics_file, 'r') as f:
        analytics = json.load(f)
    
    print("=" * 80)
    print("📊 DETAILED PROCESSING REPORT")
    print("=" * 80)
    
    # Basic stats
    total = analytics.get('total_files', 0)
    processed = analytics.get('processed_files', 0)
    skipped = analytics.get('skipped_files', 0)
    failed = analytics.get('failed_files', 0)
    processing_time = analytics.get('processing_time', 0)
    
    print(f"📁 Total Files: {total}")
    print(f"✅ Processed: {processed}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Processing Time: {processing_time:.1f} seconds")
    
    if total > 0:
        success_rate = (processed / total) * 100
        skip_rate = (skipped / total) * 100
        failure_rate = (failed / total) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"📊 Skip Rate: {skip_rate:.1f}%")
        print(f"📊 Failure Rate: {failure_rate:.1f}%")
    
    print("\n" + "=" * 80)
    print("🏷️  MOC DISTRIBUTION")
    print("=" * 80)
    
    moc_dist = analytics.get('moc_distribution', {})
    for moc, count in moc_dist.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {moc}: {count} files ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)
    print("⚡ PERFORMANCE METRICS")
    print("=" * 80)
    
    cache_hits = analytics.get('cache_hits', 0)
    cache_misses = analytics.get('cache_misses', 0)
    retry_attempts = analytics.get('retry_attempts', 0)
    
    print(f"💾 Cache Hits: {cache_hits}")
    print(f"💾 Cache Misses: {cache_misses}")
    print(f"🔄 Retry Attempts: {retry_attempts}")
    
    if cache_hits + cache_misses > 0:
        cache_hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100
        print(f"📊 Cache Hit Rate: {cache_hit_rate:.1f}%")
    
    print("\n" + "=" * 80)
    print("⏱️  TIMELINE")
    print("=" * 80)
    
    start_time = analytics.get('start_time', 'N/A')
    end_time = analytics.get('end_time', 'N/A')
    
    print(f"🕐 Start: {start_time}")
    print(f"🕐 End: {end_time}")
    print(f"⏱️  Duration: {processing_time:.1f} seconds")
    
    if processing_time > 0 and processed > 0:
        files_per_second = processed / processing_time
        print(f"📈 Processing Speed: {files_per_second:.2f} files/second")
    
    print("\n" + "=" * 80)
    print("❌ ERROR SUMMARY")
    print("=" * 80)
    
    error_types = analytics.get('error_types', {})
    if error_types:
        for error, count in error_types.items():
            print(f"  {error}: {count} occurrences")
    else:
        print("  ✅ No errors recorded")
    
    print("\n" + "=" * 80)
    print("📊 REPORT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    quick_report()
