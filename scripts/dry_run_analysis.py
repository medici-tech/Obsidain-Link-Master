#!/usr/bin/env python3
"""
Dry Run Analysis Script for Obsidian Auto-Linker
Shows what files would be categorized into which MOCs without actually processing them
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter
import requests

# Load config
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
except Exception as e:
    print(f"Error loading config: {e}")
    config = {}

VAULT_PATH = config.get('vault_path', '')
OLLAMA_BASE_URL = config.get('ollama_base_url', 'http://localhost:11434')
OLLAMA_MODEL = 'qwen2.5:3b'  # Force use of smaller, faster model

# MOC System
MOCS = {
    "Client Acquisition": "📍 Client Acquisition MOC",
    "Service Delivery": "📍 Service Delivery MOC", 
    "Revenue & Pricing": "📍 Revenue & Pricing MOC",
    "Marketing & Content": "📍 Marketing & Content MOC",
    "Garrison Voice Product": "📍 Garrison Voice Product MOC",
    "Technical & Automation": "📍 Technical & Automation MOC",
    "Business Operations": "📍 Business Operations MOC",
    "Learning & Skills": "📍 Learning & Skills MOC",
    "Personal Development": "📍 Personal Development MOC",
    "Health & Fitness": "📍 Health & Fitness MOC",
    "Finance & Money": "📍 Finance & Money MOC",
    "Life & Misc": "📍 Life & Misc MOC"
}

def call_ollama_for_categorization(content: str, file_path: str) -> Dict[str, Any]:
    """Call Ollama to categorize a single file"""
    try:
        # Extract main content (first 2000 chars)
        content_sample = content[:2000]
        filename = os.path.basename(file_path)
        
        prompt = f"""File: {filename}
Content: {content_sample[:500]}

Categorize into: Client Acquisition, Service Delivery, Revenue & Pricing, Marketing & Content, Garrison Voice Product, Technical & Automation, Business Operations, Learning & Skills, Personal Development, Health & Fitness, Finance & Money, Life & Misc

Return JSON: {{"moc_category": "Category", "confidence_score": 0.8, "reasoning": "explanation"}}"""

        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "top_k": 10,
                "num_ctx": 1024,
                "num_predict": 150
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get('response', '').strip()
        
        # Debug: print the raw response
        print(f"    🔍 Raw AI response: {response_text[:200]}...")
        
        # Try to extract JSON from response
        try:
            # First try to parse the response directly as JSON
            if response_text.startswith('{') and response_text.endswith('}'):
                print(f"    🔍 Direct JSON: {response_text}")
                return json.loads(response_text)
            
            # Look for JSON in the response
            json_match = re.search(r'\{[^{}]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                print(f"    🔍 Extracted JSON: {json_str}")
                return json.loads(json_str)
            else:
                print(f"    ❌ No JSON found in response")
                return {"moc_category": "Life & Misc", "confidence_score": 0.0, "reasoning": "Failed to parse JSON"}
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON decode error: {e}")
            return {"moc_category": "Life & Misc", "confidence_score": 0.0, "reasoning": "Invalid JSON response"}
            
    except Exception as e:
        return {"moc_category": "Life & Misc", "confidence_score": 0.0, "reasoning": f"Error: {str(e)}"}

def get_all_md_files(vault_path: str) -> List[str]:
    """Get all markdown files in the vault"""
    files = []
    for root, dirs, filenames in os.walk(vault_path):
        # Skip backup folders
        if '_backups' in root or 'backup' in root.lower():
            continue
        for filename in filenames:
            if filename.endswith('.md') and not filename.startswith(('📍', 'MOC')) and 'MOC' not in filename:
                file_path = os.path.join(root, filename)
                files.append(file_path)
    return files

def analyze_files_dry_run(vault_path: str, sample_size: int = 50) -> Dict[str, Any]:
    """Analyze files for dry run categorization"""
    print(f"🔍 Scanning vault: {vault_path}")
    
    all_files = get_all_md_files(vault_path)
    print(f"📁 Found {len(all_files)} markdown files")
    
    # Take a sample for analysis
    sample_files = all_files[:sample_size]
    print(f"📊 Analyzing sample of {len(sample_files)} files...")
    
    results = {
        'total_files': len(all_files),
        'sample_size': len(sample_files),
        'moc_distribution': defaultdict(int),
        'file_analysis': [],
        'errors': []
    }
    
    for i, file_path in enumerate(sample_files, 1):
        try:
            print(f"\n📄 [{i}/{len(sample_files)}] Analyzing: {os.path.basename(file_path)}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if already processed
            if '## 📊 METADATA' in content:
                print("  ⏭️  Already processed - skipping")
                continue
            
            # Get file info
            file_size = len(content)
            word_count = len(content.split())
            
            print(f"  📊 Size: {file_size} chars, {word_count} words")
            
            # Categorize with AI
            print("  🤖 Categorizing with AI...")
            ai_result = call_ollama_for_categorization(content, file_path)
            
            moc_category = ai_result.get('moc_category', 'Life & Misc')
            confidence = ai_result.get('confidence_score', 0.0)
            reasoning = ai_result.get('reasoning', 'No reasoning provided')
            
            print(f"  ✓ MOC: {moc_category}")
            print(f"  ✓ Confidence: {confidence:.0%}")
            print(f"  ✓ Reasoning: {reasoning[:100]}...")
            
            # Track results
            results['moc_distribution'][moc_category] += 1
            results['file_analysis'].append({
                'filename': os.path.basename(file_path),
                'moc_category': moc_category,
                'confidence': confidence,
                'reasoning': reasoning,
                'file_size': file_size,
                'word_count': word_count
            })
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            print(f"  ❌ {error_msg}")
            results['errors'].append(error_msg)
    
    return results

def generate_dry_run_report(results: Dict[str, Any]) -> str:
    """Generate HTML report for dry run analysis"""
    
    # Calculate percentages
    total_analyzed = sum(results['moc_distribution'].values())
    moc_percentages = {}
    for moc, count in results['moc_distribution'].items():
        moc_percentages[moc] = (count / total_analyzed * 100) if total_analyzed > 0 else 0
    
    # Sort MOCs by count
    sorted_mocs = sorted(results['moc_distribution'].items(), key=lambda x: x[1], reverse=True)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dry Run Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; }}
        .chart {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .moc-dist {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .moc-item {{ background: #e3f2fd; padding: 10px; border-radius: 3px; }}
        .file-analysis {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 3px; }}
        .confidence-high {{ color: #2e7d32; }}
        .confidence-medium {{ color: #f57c00; }}
        .confidence-low {{ color: #d32f2f; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Dry Run Analysis Report</h1>
        <p>Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="chart">
        <h2>📊 Analysis Summary</h2>
        <div class="metric"><strong>Total Files in Vault:</strong> {results['total_files']}</div>
        <div class="metric"><strong>Files Analyzed:</strong> {results['sample_size']}</div>
        <div class="metric"><strong>Successfully Categorized:</strong> {total_analyzed}</div>
        <div class="metric"><strong>Errors:</strong> {len(results['errors'])}</div>
    </div>
    
    <div class="chart">
        <h2>🏷️ MOC Distribution (Real Analysis)</h2>
        <div class="moc-dist">"""
    
    for moc, count in sorted_mocs:
        percentage = moc_percentages[moc]
        html += f'<div class="moc-item">{moc}: {count} files ({percentage:.1f}%)</div>'
    
    html += """
        </div>
    </div>
    
    <div class="chart">
        <h2>📄 File Analysis Details</h2>"""
    
    for file_info in results['file_analysis']:
        confidence_class = 'confidence-high' if file_info['confidence'] > 0.7 else 'confidence-medium' if file_info['confidence'] > 0.4 else 'confidence-low'
        html += f"""
        <div class="file-analysis">
            <strong>{file_info['filename']}</strong><br>
            <span class="{confidence_class}">MOC: {file_info['moc_category']} (Confidence: {file_info['confidence']:.0%})</span><br>
            <small>Reasoning: {file_info['reasoning']}</small><br>
            <small>Size: {file_info['file_size']} chars, {file_info['word_count']} words</small>
        </div>"""
    
    if results['errors']:
        html += """
    <div class="chart">
        <h2>❌ Errors</h2>"""
        for error in results['errors']:
            html += f'<div class="metric">{error}</div>'
        html += "</div>"
    
    html += """
    </div>
</body>
</html>"""
    
    return html

def main():
    """Main function"""
    if not VAULT_PATH:
        print("❌ No vault path configured in config.yaml")
        return
    
    if not os.path.exists(VAULT_PATH):
        print(f"❌ Vault path does not exist: {VAULT_PATH}")
        return
    
    print("🚀 Starting Dry Run Analysis...")
    print(f"📁 Vault: {VAULT_PATH}")
    print(f"🤖 Model: {OLLAMA_MODEL}")
    
    # Analyze files
    results = analyze_files_dry_run(VAULT_PATH, sample_size=3)  # Analyze just 3 files
    
    # Generate report
    print("\n📊 Generating report...")
    html_report = generate_dry_run_report(results)
    
    # Save report
    report_path = "dry_run_analysis_report.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"\n✅ Dry run analysis complete!")
    print(f"📊 Analyzed {results['sample_size']} files out of {results['total_files']} total")
    print(f"📈 MOC Distribution:")
    for moc, count in sorted(results['moc_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / sum(results['moc_distribution'].values()) * 100) if sum(results['moc_distribution'].values()) > 0 else 0
        print(f"   {moc}: {count} files ({percentage:.1f}%)")
    
    print(f"\n📄 Report saved to: {report_path}")
    print(f"🌐 Open in browser: open {report_path}")

if __name__ == "__main__":
    main()
