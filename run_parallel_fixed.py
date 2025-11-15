#!/usr/bin/env python3
"""
Real Parallel Processing with Detailed Analytics - Fixed Version
"""

import os
import sys
import time
import yaml
import requests
import json
import warnings
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress urllib3 warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

def load_config():
    """Load configuration"""
    try:
        with open('configs/config_parallel_optimized.yaml', 'r') as f:
            return yaml.safe_load(f)
    except:
        return {
            'vault_path': '/Users/medici/Documents/MediciVault',
            'batch_size': 7,
            'parallel_workers': 3,
            'ollama_model': 'qwen3:8b',
            'ollama_base_url': 'http://localhost:11434',
            'ollama_timeout': 120
        }

def call_ollama(prompt: str, system_prompt: str = "") -> str:
    """Call Ollama API with timeout"""
    config = load_config()
    try:
        # Ensure we have the full URL
        base_url = config.get('ollama_base_url', 'http://localhost:11434')
        if not base_url.startswith('http'):
            base_url = f"http://{base_url}"
        if not base_url.endswith(':11434'):
            base_url = base_url.rstrip('/') + ':11434'
        
        payload = {
            "model": config.get('ollama_model', 'qwen3:8b'),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 1024
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=config.get('ollama_timeout', 120)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            print(f"  ❌ Ollama HTTP error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ Ollama connection error: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"  ❌ Ollama timeout: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Ollama error: {e}")
        return None

def analyze_file_with_ai(file_path: str, existing_notes: dict) -> dict:
    """Analyze file with AI"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': f"Could not read file: {e}"}
    
    # Check if already processed
    if '## 📊 METADATA' in content and '## 🔗 WIKI STRUCTURE' in content:
        return {'status': 'already_processed'}
    
    # Create context from existing notes
    context_notes = []
    for note_name, note_content in list(existing_notes.items())[:5]:
        context_notes.append(f"Note: {note_name}\nContent: {note_content[:200]}...")
    
    context = "\n\n".join(context_notes) if context_notes else "No existing notes"
    
    system_prompt = """You are an expert at categorizing content for a knowledge management system.

Available categories:
- Life & Misc: General life topics, personal notes
- Technical & Automation: Programming, automation, technical documentation
- Client Acquisition: Sales, marketing, customer acquisition
- Service Delivery: Service processes, delivery methods
- Finance & Money: Financial planning, investments, money management
- Marketing & Content: Content creation, marketing strategies
- Revenue & Pricing: Pricing strategies, revenue optimization
- Business Operations: Operations, processes, business management
- Health & Fitness: Health, fitness, wellness topics
- Personal Development: Self-improvement, learning, personal growth

Analyze the content and provide JSON:
{
    "moc_category": "Category Name",
    "confidence": 0.85,
    "reasoning": "Brief explanation",
    "tags": ["tag1", "tag2"],
    "siblings": ["related_note1", "related_note2"]
}"""

    prompt = f"""Content to analyze:
{content[:1500]}...

Existing notes context:
{context[:500]}...

Analyze and categorize this content."""

    response = call_ollama(prompt, system_prompt)
    if not response:
        return {'error': 'AI analysis failed'}
    
    try:
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return {
                'status': 'success',
                'moc_category': result.get('moc_category', 'Life & Misc'),
                'confidence': result.get('confidence', 0.5),
                'reasoning': result.get('reasoning', 'No reasoning provided'),
                'tags': result.get('tags', []),
                'siblings': result.get('siblings', [])
            }
        else:
            return {'error': 'No JSON found in response'}
    except json.JSONDecodeError as e:
        return {'error': f'JSON decode error: {e}'}

def process_file_real(file_path: str, existing_notes: dict, stats: dict):
    """Process a single file with real AI analysis"""
    filename = os.path.basename(file_path)
    start_time = time.time()
    
    # Analyze with AI
    ai_result = analyze_file_with_ai(file_path, existing_notes)
    processing_time = time.time() - start_time
    
    if 'error' in ai_result:
        return {
            'file': filename,
            'status': 'failed',
            'error': ai_result['error'],
            'processing_time': processing_time
        }
    
    if ai_result.get('status') == 'already_processed':
        return {
            'file': filename,
            'status': 'skipped',
            'reason': 'already_processed',
            'processing_time': processing_time
        }
    
    # Update stats
    stats['processed'] += 1
    stats['links_added'] += len(ai_result.get('siblings', []))
    stats['tags_added'] += len(ai_result.get('tags', []))
    stats['confidence_scores'].append(ai_result.get('confidence', 0.5))
    stats['processing_times'].append(processing_time)
    
    return {
        'file': filename,
        'status': 'processed',
        'moc_category': ai_result.get('moc_category', 'Life & Misc'),
        'confidence': ai_result.get('confidence', 0.5),
        'links_added': len(ai_result.get('siblings', [])),
        'tags_added': len(ai_result.get('tags', [])),
        'processing_time': processing_time
    }

def process_batch_parallel_real(batch_files, existing_notes, max_workers=3):
    """Process a batch of files in parallel with real AI"""
    batch_stats = {
        'processed': 0,
        'skipped': 0,
        'failed': 0,
        'links_added': 0,
        'tags_added': 0,
        'confidence_scores': [],
        'processing_times': []
    }
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_file_real, file_path, existing_notes, batch_stats): file_path 
            for file_path in batch_files
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                
                if result['status'] == 'processed':
                    batch_stats['processed'] += 1
                elif result['status'] == 'skipped':
                    batch_stats['skipped'] += 1
                else:
                    batch_stats['failed'] += 1
                    
            except Exception as e:
                results.append({
                    'file': os.path.basename(file_path),
                    'status': 'failed',
                    'error': str(e),
                    'processing_time': 0
                })
                batch_stats['failed'] += 1
    
    return results, batch_stats

def show_progress(current_file, status, processed_count, total_files, start_time):
    """Show detailed progress with ETA"""
    elapsed = datetime.now() - start_time
    elapsed_seconds = elapsed.total_seconds()
    
    if processed_count > 0:
        avg_time_per_file = elapsed_seconds / processed_count
        remaining_files = total_files - processed_count
        eta_seconds = remaining_files * avg_time_per_file
        eta = timedelta(seconds=int(eta_seconds))
        files_per_minute = (processed_count / elapsed_seconds) * 60
    else:
        eta = "Calculating..."
        files_per_minute = 0
    
    progress_percent = (processed_count / total_files) * 100
    
    print(f"📊 Progress: {processed_count}/{total_files} ({progress_percent:.1f}%) | ⏱️ {elapsed} | 🏃 {files_per_minute:.1f}/min | ⏳ {eta} | 📁 {current_file}... | 🔄 {status}")

def get_all_notes(vault_path: str) -> dict:
    """Get all existing notes for context"""
    notes = {}
    try:
        for root, dirs, files in os.walk(vault_path):
            if '_backups' in root:
                continue
            for file in files:
                if file.endswith('.md') and not file.startswith(('📍', 'MOC')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        notes[file.replace('.md', '')] = content[:300]
                    except:
                        continue
    except Exception as e:
        print(f"Error scanning vault: {e}")
    return notes

def main():
    print("🚀 REAL PARALLEL PROCESSING WITH DETAILED ANALYTICS")
    print("=" * 60)
    print(f"⏰ Start: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Load config
    config = load_config()
    vault_path = config.get('vault_path', '/Users/medici/Documents/MediciVault')
    batch_size = config.get('batch_size', 7)
    parallel_workers = config.get('parallel_workers', 3)
    
    print("🔧 Configuration:")
    print(f"   📦 Batch size: {batch_size} files per batch")
    print(f"   ⚡ Parallel workers: {parallel_workers} threads")
    print(f"   🤖 Model: {config.get('ollama_model', 'qwen3:8b')}")
    print(f"   📁 Vault: {vault_path}")
    print()
    
    # Check vault
    if not os.path.exists(vault_path):
        print(f"❌ Vault not found: {vault_path}")
        return
    
    # Test Ollama connection
    print("🔍 Testing Ollama connection...")
    try:
        # First check if Ollama is running
        base_url = config.get('ollama_base_url', 'http://localhost:11434')
        if not base_url.startswith('http'):
            base_url = f"http://{base_url}"
        if not base_url.endswith(':11434'):
            base_url = base_url.rstrip('/') + ':11434'
        
        print(f"  🔗 Checking Ollama at: {base_url}")
        test_response = requests.get(f"{base_url}/api/tags", timeout=5)
        if test_response.status_code != 200:
            print("❌ Ollama is not responding. Please start Ollama first.")
            print("   Run: ollama serve")
            return
        print("✅ Ollama server is running")
        
        # Test actual generation
        test_response = call_ollama("Hello", "You are a helpful assistant.")
        if not test_response:
            print("❌ Ollama generation failed. Check model availability.")
            return
        else:
            print("✅ Ollama connection and generation successful")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("   Please ensure Ollama is running: ollama serve")
        return
    
    # Find files to process
    print("🔍 Scanning vault...")
    all_files = []
    for root, dirs, files in os.walk(vault_path):
        if '_backups' in root:
            continue
        for file in files:
            if file.endswith('.md') and not file.startswith(('📍', 'MOC')):
                all_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(all_files)} markdown files")
    
    if not all_files:
        print("✅ No files to process!")
        return
    
    # Get existing notes for context
    print("📚 Loading existing notes for context...")
    existing_notes = get_all_notes(vault_path)
    print(f"   Found {len(existing_notes)} existing notes")
    
    # Process files in batches
    print(f"\n🚀 Starting real parallel processing...")
    print(f"   📦 Processing {len(all_files)} files in batches of {batch_size}")
    print(f"   ⚡ Using {parallel_workers} parallel workers")
    print(f"   🤖 AI model: {config.get('ollama_model', 'qwen3:8b')}")
    
    start_time = datetime.now()
    total_stats = {
        'processed': 0,
        'skipped': 0,
        'failed': 0,
        'links_added': 0,
        'tags_added': 0,
        'confidence_scores': [],
        'processing_times': []
    }
    
    # Process in batches
    total_batches = (len(all_files) + batch_size - 1) // batch_size
    
    for i in range(0, len(all_files), batch_size):
        batch_files = all_files[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch_files)} files)")
        
        # Process batch in parallel
        batch_start = time.time()
        batch_results, batch_stats = process_batch_parallel_real(batch_files, existing_notes, parallel_workers)
        batch_time = time.time() - batch_start
        
        # Update total stats
        total_stats['processed'] += batch_stats['processed']
        total_stats['skipped'] += batch_stats['skipped']
        total_stats['failed'] += batch_stats['failed']
        total_stats['links_added'] += batch_stats['links_added']
        total_stats['tags_added'] += batch_stats['tags_added']
        total_stats['confidence_scores'].extend(batch_stats['confidence_scores'])
        total_stats['processing_times'].extend(batch_stats['processing_times'])
        
        # Show detailed batch results
        print(f"   ✅ Batch {batch_num} complete in {batch_time:.1f}s")
        print(f"   📊 Processed: {batch_stats['processed']}, Skipped: {batch_stats['skipped']}, Failed: {batch_stats['failed']}")
        print(f"   🔗 Links: {batch_stats['links_added']}, Tags: {batch_stats['tags_added']}")
        
        # Show progress
        processed_count = total_stats['processed'] + total_stats['skipped'] + total_stats['failed']
        show_progress(f"Batch {batch_num}", "Completed", processed_count, len(all_files), start_time)
    
    # Final results
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("✅ REAL PARALLEL PROCESSING COMPLETE")
    print("=" * 60)
    print(f"📊 Total processed: {total_stats['processed']}")
    print(f"⏭️  Total skipped: {total_stats['skipped']}")
    print(f"❌ Total failed: {total_stats['failed']}")
    print(f"🔗 Total links: {total_stats['links_added']}")
    print(f"🏷️  Total tags: {total_stats['tags_added']}")
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"⚡ Speed: {len(all_files)/total_time:.1f} files/second")
    print(f"🚀 Parallel efficiency: {total_stats['processed']/total_time:.1f} processed/second")
    
    # Detailed analytics
    if total_stats['processing_times']:
        avg_processing_time = sum(total_stats['processing_times']) / len(total_stats['processing_times'])
        print(f"📈 Average processing time per file: {avg_processing_time:.1f}s")
    
    if total_stats['confidence_scores']:
        avg_confidence = sum(total_stats['confidence_scores']) / len(total_stats['confidence_scores'])
        print(f"🎯 Average confidence score: {avg_confidence:.1%}")
    
    print(f"\n✅ Real parallel processing with AI analysis complete!")
    print(f"📊 Processed {total_stats['processed']} files with {parallel_workers} parallel workers")

if __name__ == "__main__":
    main()








