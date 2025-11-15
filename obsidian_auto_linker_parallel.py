#!/usr/bin/env python3
"""
Enhanced Obsidian Vault Auto-Linker with PARALLEL PROCESSING
Processes conversations in batches with parallel workers for maximum speed
"""

import os
import re
import yaml
import json
import shutil
import hashlib
import time
import threading
import signal
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor, TimeoutError
import requests
from tqdm import tqdm
import fnmatch

# Load config
try:
    with open('configs/config_parallel_timeout.yaml', 'r') as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
except Exception as e:
    print(f"Error loading config: {e}")
    config = {}

VAULT_PATH = config.get('vault_path', '')
BACKUP_FOLDER = os.path.join(VAULT_PATH, config.get('backup_folder', '_backups'))
DRY_RUN = config.get('dry_run', True)
FAST_DRY_RUN = config.get('fast_dry_run', False)
MAX_BACKUPS = config.get('max_backups', 5)
MAX_SIBLINGS = config.get('max_siblings', 5)
BATCH_SIZE = config.get('batch_size', 7)  # Process 7 files per batch
MAX_RETRIES = config.get('max_retries', 2)
PARALLEL_WORKERS = config.get('parallel_workers', 3)  # Use 3 parallel workers
FILE_ORDERING = config.get('file_ordering', 'recent')
RESUME_ENABLED = config.get('resume_enabled', True)
CACHE_ENABLED = config.get('cache_enabled', True)
INTERACTIVE_MODE = config.get('interactive_mode', False)  # Disabled for speed
ANALYTICS_ENABLED = config.get('analytics_enabled', True)

# Quality control settings
CONFIDENCE_THRESHOLD = config.get('confidence_threshold', 0.8)
ENABLE_REVIEW_QUEUE = config.get('enable_review_queue', True)
REVIEW_QUEUE_PATH = config.get('review_queue_path', 'reviews/')

# Ollama configuration
OLLAMA_BASE_URL = config.get('ollama_base_url', 'http://localhost:11434')
OLLAMA_MODEL = config.get('ollama_model', 'qwen3:8b')
OLLAMA_TEMPERATURE = config.get('ollama_temperature', 0.1)
OLLAMA_MAX_TOKENS = config.get('ollama_max_tokens', 1024)
OLLAMA_CONTEXT_WINDOW = config.get('ollama_context_window', 8192)
OLLAMA_TIMEOUT = config.get('ollama_timeout', 30)  # Reduced to 30 seconds per file
OLLAMA_RETRY_TIMEOUT = config.get('ollama_retry_timeout', 60)  # Reduced to 1 minute
OLLAMA_MAX_REASONING_TIME = config.get('ollama_max_reasoning_time', 90)  # Reduced to 90 seconds
FILE_PROCESSING_TIMEOUT = config.get('file_processing_timeout', 60)  # 60 seconds max per file

# Speed tracking
SPEED_TRACKING = config.get('track_speed_comparison', True)
PARALLEL_EFFICIENCY = config.get('track_parallel_efficiency', True)

# Global variables for tracking
analytics = {
    'start_time': None,
    'end_time': None,
    'total_files': 0,
    'processed_files': 0,
    'skipped_files': 0,
    'failed_files': 0,
    'timeout_files': 0,
    'processing_time': 0,
    'moc_distribution': {},
    'error_types': {},
    'retry_attempts': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'low_confidence_files': 0,
    'review_queue_count': 0,
    'parallel_processing_time': 0,
    'sequential_processing_time': 0,
    'speed_improvement': 0,
    'parallel_efficiency': 0
}

progress_data = {
    'processed_files': set(),
    'failed_files': set(),
    'cache': {}
}

# MOC categories
MOCS = {
    "Life & Misc": "General life topics, personal notes, miscellaneous content",
    "Technical & Automation": "Programming, automation, technical documentation",
    "Client Acquisition": "Sales, marketing, customer acquisition strategies",
    "Service Delivery": "Service processes, delivery methods, customer service",
    "Finance & Money": "Financial planning, investments, money management",
    "Marketing & Content": "Content creation, marketing strategies, branding",
    "Revenue & Pricing": "Pricing strategies, revenue optimization, business models",
    "Garrison Voice Product": "Product development, voice products, specific offerings",
    "Business Operations": "Operations, processes, business management",
    "Health & Fitness": "Health, fitness, wellness topics",
    "Personal Development": "Self-improvement, learning, personal growth",
    "Learning & Skills": "Education, skill development, training"
}

def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("File processing timed out")

def call_ollama(prompt: str, system_prompt: str = "") -> Optional[str]:
    """Call Ollama API with enhanced error handling and timeout management"""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": OLLAMA_TEMPERATURE,
                "num_predict": OLLAMA_MAX_TOKENS,
                "num_ctx": OLLAMA_CONTEXT_WINDOW
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            print(f"  ❌ Ollama API error: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"  ⏰ Ollama timeout after {OLLAMA_TIMEOUT}s")
        return None
    except Exception as e:
        print(f"  ❌ Ollama error: {e}")
        return None

def process_with_timeout(func, timeout_seconds, *args, **kwargs):
    """Execute a function with a timeout"""
    result = None
    exception = None
    
    def target():
        nonlocal result, exception
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            exception = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        print(f"  ⏰ Processing timed out after {timeout_seconds}s")
        return None
    
    if exception:
        raise exception
    
    return result

def analyze_with_balanced_ai(content: str, existing_notes: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Analyze content with balanced AI approach"""
    
    # Create context from existing notes
    context_notes = []
    for note_name, note_content in list(existing_notes.items())[:10]:  # Limit context
        newline = "\n"
        context_notes.append(f"Note: {note_name}{newline}Content: {note_content[:200]}...")
    
    context = "\n\n".join(context_notes) if context_notes else "No existing notes"
    
    system_prompt = f"""You are an expert at categorizing and structuring content for a knowledge management system.

Available MOC categories:
{json.dumps(MOCS, indent=2)}

Analyze the content and provide:
1. Most appropriate MOC category
2. Confidence score (0.0-1.0)
3. Reasoning for the categorization
4. Suggested tags (2-3 tags)
5. Related sibling notes from existing notes

Return JSON format:
{{
    "moc_category": "Category Name",
    "confidence": 0.85,
    "reasoning": "Brief explanation",
    "tags": ["tag1", "tag2"],
    "siblings": ["related_note1", "related_note2"]
}}"""

    prompt = f"""Content to analyze:
{content[:2000]}...

Existing notes context:
{context[:1000]}...

Analyze and categorize this content."""

    response = call_ollama(prompt, system_prompt)
    if not response:
        return None
    
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            print(f"  ⚠️  No JSON found in response")
            return None
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON decode error: {e}")
        return None

def process_conversation_parallel(file_path: str, existing_notes: Dict[str, str], stats: Dict) -> Dict:
    """Process single conversation file for parallel processing with timeout"""
    
    filename = os.path.basename(file_path)
    result = {
        'file_path': file_path,
        'filename': filename,
        'success': False,
        'processed': False,
        'skipped': False,
        'failed': False,
        'links_added': 0,
        'tags_added': 0,
        'confidence': 0.0,
        'moc_category': None,
        'error': None,
        'timeout': False
    }
    
    # Check if already processed
    if file_path in progress_data['processed_files']:
        result['skipped'] = True
        return result
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result['error'] = f"Could not read file: {e}"
        result['failed'] = True
        return result
    
    # Check if already processed (has proper structure)
    if '## 📊 METADATA' in content and '## 🔗 WIKI STRUCTURE' in content:
        has_parent = re.search(r'Parent: \[\[📍.*MOC\]\]', content)
        if has_parent:
            result['skipped'] = True
            return result
    
    # Use timeout wrapper for AI analysis
    def analyze_with_timeout():
        ai_result = None
        for attempt in range(MAX_RETRIES):
            try:
                ai_result = analyze_with_balanced_ai(content, existing_notes)
                if ai_result:
                    break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return ai_result
    
    # Process with timeout
    ai_result = process_with_timeout(analyze_with_timeout, FILE_PROCESSING_TIMEOUT)
    
    if ai_result is None:
        result['failed'] = True
        result['timeout'] = True
        result['error'] = f"Processing timed out after {FILE_PROCESSING_TIMEOUT}s"
        return result
    
    # Extract results
    moc_category = ai_result.get('moc_category', 'Life & Misc')
    confidence = ai_result.get('confidence', 0.5)
    reasoning = ai_result.get('reasoning', 'No reasoning provided')
    tags = ai_result.get('tags', [])
    siblings = ai_result.get('siblings', [])
    
    result['confidence'] = confidence
    result['moc_category'] = moc_category
    result['tags_added'] = len(tags)
    result['links_added'] = len(siblings)
    
    # Check confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        analytics['low_confidence_files'] += 1
        if ENABLE_REVIEW_QUEUE:
            analytics['review_queue_count'] += 1
    
    # Process the file (simplified for parallel processing)
    if not DRY_RUN:
        try:
            # Create backup
            backup_path = os.path.join(BACKUP_FOLDER, f"{filename}.backup")
            os.makedirs(BACKUP_FOLDER, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # Create enhanced content with MOC structure
            enhanced_content = create_enhanced_content(content, moc_category, confidence, reasoning, tags, siblings, existing_notes)
            
            # Write enhanced content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            result['processed'] = True
            result['success'] = True
        except Exception as e:
            result['failed'] = True
            result['error'] = f"File processing error: {e}"
    else:
        result['success'] = True  # Dry run success
    
    return result

def create_enhanced_content(content: str, moc_category: str, confidence: float, reasoning: str, tags: List[str], siblings: List[str], existing_notes: Dict[str, str]) -> str:
    """Create enhanced content with MOC structure"""
    
    # Create MOC link
    moc_link = f"[[📍 {moc_category} MOC]]"
    
    # Create sibling links
    sibling_links = []
    for sibling in siblings[:MAX_SIBLINGS]:
        if sibling in existing_notes:
            sibling_links.append(f"[[{sibling}]]")
    
    # Create tags
    tag_links = [f"#{tag.replace(' ', '_').lower()}" for tag in tags]
    
    # Create enhanced content
    processed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = os.path.basename(content.split('\n')[0]) if content else 'Untitled'
    enhanced = f"""# {title}

## 📊 METADATA
- **Parent**: {moc_link}
- **Confidence**: {confidence:.1%}
- **Category**: {moc_category}
- **Tags**: {' '.join(tag_links)}
- **Siblings**: {' '.join(sibling_links)}

## 🧠 AI REASONING
{reasoning}

## 🔗 WIKI STRUCTURE
{content}

## 📝 PROCESSING NOTES
- Processed: {processed_time}
- Model: {OLLAMA_MODEL}
- Processing: Parallel Batch Mode
"""
    
    return enhanced

def process_batch_parallel(batch_files: List[str], existing_notes: Dict[str, str]) -> Dict:
    """Process a batch of files in parallel with timeout handling"""
    
    batch_stats = {
        'processed': 0,
        'skipped': 0,
        'failed': 0,
        'timeout': 0,
        'links_added': 0,
        'tags_added': 0,
        'confidence_scores': [],
        'processing_times': []
    }
    
    # Process files in parallel using ThreadPoolExecutor with timeout
    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        # Submit all tasks with individual timeouts
        future_to_file = {}
        for file_path in batch_files:
            future = executor.submit(process_conversation_parallel, file_path, existing_notes, batch_stats)
            future_to_file[future] = file_path
        
        # Collect results as they complete with timeout
        try:
            for future in as_completed(future_to_file, timeout=FILE_PROCESSING_TIMEOUT * 2):
                file_path = future_to_file[future]
                try:
                    result = future.result(timeout=FILE_PROCESSING_TIMEOUT)
                    
                    if result['success']:
                        if result['processed']:
                            batch_stats['processed'] += 1
                            progress_data['processed_files'].add(file_path)
                        elif result['skipped']:
                            batch_stats['skipped'] += 1
                        else:
                            batch_stats['failed'] += 1
                            progress_data['failed_files'].add(file_path)
                        
                        batch_stats['links_added'] += result['links_added']
                        batch_stats['tags_added'] += result['tags_added']
                        batch_stats['confidence_scores'].append(result['confidence'])
                    else:
                        if result.get('timeout', False):
                            batch_stats['timeout'] += 1
                            print(f"  ⏰ Timeout processing {os.path.basename(file_path)}")
                        else:
                            batch_stats['failed'] += 1
                            print(f"  ❌ Failed processing {os.path.basename(file_path)}: {result.get('error', 'Unknown error')}")
                        progress_data['failed_files'].add(file_path)
                        
                except TimeoutError:
                    print(f"  ⏰ Timeout processing {os.path.basename(file_path)}")
                    batch_stats['timeout'] += 1
                    progress_data['failed_files'].add(file_path)
                except Exception as e:
                    print(f"  ❌ Error processing {os.path.basename(file_path)}: {e}")
                    batch_stats['failed'] += 1
                    progress_data['failed_files'].add(file_path)
        except TimeoutError:
            # Handle batch timeout - mark remaining futures as timed out
            print(f"  ⏰ Batch timeout - marking remaining files as timed out")
            for future in future_to_file:
                if not future.done():
                    file_path = future_to_file[future]
                    print(f"  ⏰ Batch timeout for {os.path.basename(file_path)}")
                    batch_stats['timeout'] += 1
                    progress_data['failed_files'].add(file_path)
    
    return batch_stats

def get_all_notes(vault_path: str) -> Dict[str, str]:
    """Get all existing notes for context"""
    notes = {}
    try:
        for root, dirs, files in os.walk(vault_path):
            if config.get('backup_folder', '_backups') in root:
                continue
            for file in files:
                if file.endswith('.md') and not file.startswith(('📍', 'MOC')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        notes[file.replace('.md', '')] = content[:500]  # Limit content
                    except:
                        continue
    except Exception as e:
        print(f"Error scanning vault: {e}")
    return notes

def should_process_file(file_path: str) -> bool:
    """Check if file should be processed"""
    if not file_path.endswith('.md'):
        return False
    if '_linked.md' in file_path:
        return False
    if file_path.startswith(('📍', 'MOC')):
        return False
    return True

def create_moc_note(moc_name: str, vault_path: str):
    """Create MOC note if it doesn't exist"""
    moc_file = os.path.join(vault_path, f"📍 {moc_name} MOC.md")
    if not os.path.exists(moc_file):
        moc_content = f"""# 📍 {moc_name} MOC

## 📋 Overview
{MOCS.get(moc_name, 'Category description')}

## 📝 Notes
<!-- Add notes here as they are processed -->

## 🔗 Related Categories
<!-- Links to related MOCs will be added automatically -->
"""
        with open(moc_file, 'w', encoding='utf-8') as f:
            f.write(moc_content)

def save_progress():
    """Save progress data"""
    try:
        with open('progress_data.json', 'w') as f:
            json.dump({
                'processed_files': list(progress_data['processed_files']),
                'failed_files': list(progress_data['failed_files']),
                'last_save': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving progress: {e}")

def load_progress():
    """Load progress data"""
    try:
        if os.path.exists('progress_data.json'):
            with open('progress_data.json', 'r') as f:
                data = json.load(f)
                progress_data['processed_files'] = set(data.get('processed_files', []))
                progress_data['failed_files'] = set(data.get('failed_files', []))
    except Exception as e:
        print(f"Error loading progress: {e}")

def generate_parallel_analytics_report():
    """Generate analytics report with parallel processing metrics"""
    
    if not ANALYTICS_ENABLED:
        return
    
    analytics['end_time'] = datetime.now()
    analytics['processing_time'] = (analytics['end_time'] - analytics['start_time']).total_seconds()
    
    # Calculate speed improvements
    if SPEED_TRACKING:
        sequential_time = analytics.get('sequential_processing_time', 0)
        parallel_time = analytics['processing_time']
        if sequential_time > 0:
            analytics['speed_improvement'] = ((sequential_time - parallel_time) / sequential_time) * 100
            analytics['parallel_efficiency'] = (analytics['processed_files'] / parallel_time) if parallel_time > 0 else 0
    
    # Generate HTML report
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>🚀 Parallel Processing Analytics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #3498db; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #e74c3c; margin-bottom: 5px; }}
        .metric-label {{ color: #7f8c8d; font-size: 1.1em; }}
        .speed-comparison {{ background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #27ae60; }}
        .parallel-stats {{ background: #fff3cd; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Parallel Processing Analytics</h1>
            <p>Generated: {analytics['end_time'].strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{analytics['total_files']}</div>
                <div class="metric-label">Total Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analytics['processed_files']}</div>
                <div class="metric-label">Processed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analytics['skipped_files']}</div>
                <div class="metric-label">Skipped</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analytics['failed_files']}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analytics.get('timeout_files', 0)}</div>
                <div class="metric-label">Timeouts</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analytics['processing_time']:.1f}s</div>
                <div class="metric-label">Processing Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analytics.get('parallel_efficiency', 0):.1f}/s</div>
                <div class="metric-label">Files/Second</div>
            </div>
        </div>
        
        <div class="speed-comparison">
            <h3>⚡ Speed Comparison</h3>
            <p><strong>Parallel Processing Time:</strong> {analytics['processing_time']:.1f} seconds</p>
            <p><strong>Speed Improvement:</strong> {analytics.get('speed_improvement', 0):.1f}% faster than sequential</p>
            <p><strong>Parallel Efficiency:</strong> {analytics.get('parallel_efficiency', 0):.1f} files per second</p>
        </div>
        
        <div class="parallel-stats">
            <h3>🔧 Parallel Processing Stats</h3>
            <p><strong>Batch Size:</strong> {BATCH_SIZE} files per batch</p>
            <p><strong>Parallel Workers:</strong> {PARALLEL_WORKERS} threads</p>
            <p><strong>Model:</strong> {OLLAMA_MODEL}</p>
            <p><strong>Confidence Threshold:</strong> {CONFIDENCE_THRESHOLD}</p>
        </div>
    </div>
</body>
</html>"""
    
    with open('parallel_processing_analytics.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📊 Parallel processing analytics saved to: parallel_processing_analytics.html")

def main():
    """Main parallel processing function"""
    
    print("=" * 60)
    print("🚀 PARALLEL PROCESSING OBSIDIAN AUTO-LINKER")
    print("   🔥 BATCH SIZE: 7 files per batch")
    print("   ⚡ PARALLEL WORKERS: 3 threads")
    print("   🚀 MAXIMUM SPEED MODE")
    print("=" * 60)
    print()
    
    # Initialize analytics
    analytics['start_time'] = datetime.now()
    
    # Load progress
    load_progress()
    
    # Skip connection test for speed
    print("🚀 Skipping connection test for maximum speed...")
    print(f"   🤖 Using model: {OLLAMA_MODEL}")
    print(f"   ⚡ Parallel workers: {PARALLEL_WORKERS}")
    print(f"   📦 Batch size: {BATCH_SIZE}")
    print("   ⚠️  Will test connection during first AI call")
    
    # Scan vault
    print("🔍 Scanning vault...")
    existing_notes = get_all_notes(VAULT_PATH)
    print(f"   Found {len(existing_notes)} existing notes")
    
    # Create MOC notes
    print("📚 Creating MOC notes...")
    for moc_name in MOCS.keys():
        create_moc_note(moc_name, VAULT_PATH)
    
    # Find files to process
    print("🔎 Finding files to process...")
    all_files = []
    for root, dirs, files in os.walk(VAULT_PATH):
        if config.get('backup_folder', '_backups') in root:
            continue
        for file in files:
            if should_process_file(os.path.join(root, file)):
                all_files.append(os.path.join(root, file))
    
    # Filter out already processed files
    if RESUME_ENABLED:
        all_files = [f for f in all_files if f not in progress_data['processed_files']]
    
    print(f"   Found {len(all_files)} files to process")
    analytics['total_files'] = len(all_files)
    
    if not all_files:
        print("✅ No files to process!")
        return
    
    # Process files in batches
    print(f"\n🚀 Starting parallel processing...")
    print(f"   📦 Batch size: {BATCH_SIZE}")
    print(f"   ⚡ Parallel workers: {PARALLEL_WORKERS}")
    print(f"   📁 Total files: {len(all_files)}")
    
    total_stats = {
        'processed': 0,
        'skipped': 0,
        'failed': 0,
        'timeout': 0,
        'links_added': 0,
        'tags_added': 0
    }
    
    # Process in batches
    for i in range(0, len(all_files), BATCH_SIZE):
        batch_files = all_files[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(all_files) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch_files)} files)")
        
        # Process batch in parallel
        batch_start = time.time()
        batch_stats = process_batch_parallel(batch_files, existing_notes)
        batch_time = time.time() - batch_start
        
        # Update totals
        total_stats['processed'] += batch_stats['processed']
        total_stats['skipped'] += batch_stats['skipped']
        total_stats['failed'] += batch_stats['failed']
        total_stats['timeout'] += batch_stats['timeout']
        total_stats['links_added'] += batch_stats['links_added']
        total_stats['tags_added'] += batch_stats['tags_added']
        
        # Show batch results
        print(f"   ✅ Batch {batch_num} complete in {batch_time:.1f}s")
        print(f"   📊 Processed: {batch_stats['processed']}, Skipped: {batch_stats['skipped']}, Failed: {batch_stats['failed']}, Timeouts: {batch_stats['timeout']}")
        print(f"   🔗 Links: {batch_stats['links_added']}, Tags: {batch_stats['tags_added']}")
        
        # Save progress
        save_progress()
    
    # Update analytics
    analytics['processed_files'] = total_stats['processed']
    analytics['skipped_files'] = total_stats['skipped']
    analytics['failed_files'] = total_stats['failed']
    analytics['timeout_files'] = total_stats['timeout']
    
    # Final report
    print("\n" + "=" * 60)
    print("✅ PARALLEL PROCESSING COMPLETE")
    print("=" * 60)
    print(f"📊 Total processed: {total_stats['processed']}")
    print(f"⏭️  Total skipped: {total_stats['skipped']}")
    print(f"❌ Total failed: {total_stats['failed']}")
    print(f"⏰ Total timeouts: {total_stats['timeout']}")
    print(f"🔗 Total links: {total_stats['links_added']}")
    print(f"🏷️  Total tags: {total_stats['tags_added']}")
    print(f"⏱️  Total time: {analytics['processing_time']:.1f} seconds")
    print(f"⚡ Speed: {analytics.get('parallel_efficiency', 0):.1f} files/second")
    
    # Generate analytics report
    generate_parallel_analytics_report()
    
    print(f"\n📊 Analytics report: parallel_processing_analytics.html")

if __name__ == "__main__":
    main()
