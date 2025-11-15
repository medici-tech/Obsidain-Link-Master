#!/usr/bin/env python3
"""
Ultra Detailed Analytics with Before/After Files and Reasoning Analysis
Generates comprehensive reports with file comparisons and AI reasoning breakdown
"""

import os
import json
import yaml
import time
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any
import webbrowser
from pathlib import Path
import difflib

def load_analytics_data() -> Dict[str, Any]:
    """Load analytics data from various sources"""
    analytics = {}
    
    # Load processing analytics
    if os.path.exists('processing_analytics.json'):
        with open('processing_analytics.json', 'r') as f:
            analytics['processing'] = json.load(f)
    
    # Load cache data
    if os.path.exists('.ai_cache.json'):
        with open('.ai_cache.json', 'r') as f:
            analytics['cache'] = json.load(f)
    
    # Load before/after file data
    if os.path.exists('before_after_analysis.json'):
        with open('before_after_analysis.json', 'r') as f:
            analytics['before_after'] = json.load(f)
    
    # Load reasoning analysis
    if os.path.exists('reasoning_analysis.json'):
        with open('reasoning_analysis.json', 'r') as f:
            analytics['reasoning'] = json.load(f)
    
    return analytics

def generate_before_after_comparison(analytics: Dict[str, Any]) -> str:
    """Generate before/after file comparison HTML"""
    before_after = analytics.get('before_after', {})
    
    if not before_after:
        return "<div class='section'><h3>📄 Before/After Analysis</h3><p>No before/after data available</p></div>"
    
    html = """
    <div class="section">
        <h3>📄 Before/After File Analysis</h3>
        <div class="before-after-grid">
    """
    
    for file_path, changes in before_after.items():
        filename = os.path.basename(file_path)
        html += f"""
            <div class="file-comparison">
                <h4>📁 {filename}</h4>
                <div class="comparison-stats">
                    <div class="stat">
                        <span class="label">Lines Added:</span>
                        <span class="value added">{changes.get('lines_added', 0)}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Lines Removed:</span>
                        <span class="value removed">{changes.get('lines_removed', 0)}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Lines Modified:</span>
                        <span class="value modified">{changes.get('lines_modified', 0)}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Change Score:</span>
                        <span class="value score">{changes.get('change_score', 0):.1f}%</span>
                    </div>
                </div>
        """
        
        # Show key changes
        if 'key_changes' in changes:
            html += "<div class='key-changes'><h5>🔑 Key Changes:</h5><ul>"
            for change in changes['key_changes'][:5]:  # Show top 5 changes
                html += f"<li>{change}</li>"
            html += "</ul></div>"
        
        html += "</div>"
    
    html += """
        </div>
    </div>
    """
    
    return html

def generate_reasoning_analysis(analytics: Dict[str, Any]) -> str:
    """Generate AI reasoning analysis HTML"""
    reasoning = analytics.get('reasoning', {})
    
    if not reasoning:
        return "<div class='section'><h3>🧠 AI Reasoning Analysis</h3><p>No reasoning data available</p></div>"
    
    html = """
    <div class="section">
        <h3>🧠 AI Reasoning Analysis</h3>
        <div class="reasoning-stats">
    """
    
    # Reasoning patterns
    if 'reasoning_patterns' in reasoning:
        patterns = reasoning['reasoning_patterns']
        html += f"""
            <div class="reasoning-patterns">
                <h4>📊 Reasoning Patterns</h4>
                <div class="pattern-grid">
        """
        
        for pattern, count in patterns.items():
            html += f"""
                <div class="pattern-item">
                    <span class="pattern-name">{pattern}</span>
                    <span class="pattern-count">{count}</span>
                </div>
            """
        
        html += """
                </div>
            </div>
        """
    
    # Confidence analysis
    if 'confidence_analysis' in reasoning:
        conf_analysis = reasoning['confidence_analysis']
        html += f"""
            <div class="confidence-analysis">
                <h4>🎯 Confidence Analysis</h4>
                <div class="confidence-stats">
                    <div class="conf-stat">
                        <span class="label">Average Confidence:</span>
                        <span class="value">{conf_analysis.get('average_confidence', 0):.1f}%</span>
                    </div>
                    <div class="conf-stat">
                        <span class="label">High Confidence (>80%):</span>
                        <span class="value">{conf_analysis.get('high_confidence_count', 0)}</span>
                    </div>
                    <div class="conf-stat">
                        <span class="label">Low Confidence (<50%):</span>
                        <span class="value">{conf_analysis.get('low_confidence_count', 0)}</span>
                    </div>
                </div>
            </div>
        """
    
    # Reasoning examples
    if 'reasoning_examples' in reasoning:
        examples = reasoning['reasoning_examples']
        html += """
            <div class="reasoning-examples">
                <h4>💡 Reasoning Examples</h4>
        """
        
        for i, example in enumerate(examples[:3]):  # Show top 3 examples
            html += f"""
                <div class="example-item">
                    <h5>Example {i+1}: {example.get('category', 'Unknown')}</h5>
                    <p class="reasoning-text">"{example.get('reasoning', 'No reasoning available')}"</p>
                    <div class="example-meta">
                        <span class="confidence">Confidence: {example.get('confidence', 0):.1f}%</span>
                        <span class="file">File: {os.path.basename(example.get('file', 'Unknown'))}</span>
                    </div>
                </div>
            """
        
        html += "</div>"
    
    html += """
        </div>
    </div>
    """
    
    return html

def generate_ultra_detailed_report(analytics: Dict[str, Any]) -> str:
    """Generate the most comprehensive analytics report possible"""
    
    processing = analytics.get('processing', {})
    
    # Calculate comprehensive metrics
    total_files = processing.get('total_files', 0)
    processed_files = processing.get('processed_files', 0)
    skipped_files = processing.get('skipped_files', 0)
    failed_files = processing.get('failed_files', 0)
    processing_time = processing.get('processing_time', 0)
    
    # MOC distribution analysis
    moc_dist = processing.get('moc_distribution', {})
    moc_percentages = {}
    for moc, count in moc_dist.items():
        moc_percentages[moc] = (count / total_files * 100) if total_files > 0 else 0
    
    # Performance metrics
    files_per_minute = (processed_files / processing_time * 60) if processing_time > 0 else 0
    avg_time_per_file = processing_time / processed_files if processed_files > 0 else 0
    
    # Generate ultra-comprehensive HTML report
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Ultra Detailed Obsidian Auto-Linker Analytics</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3em;
            color: #2c3e50;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .timestamp {{
            background: #e74c3c;
            color: white;
            padding: 15px 25px;
            border-radius: 25px;
            display: inline-block;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .metric-card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .section h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 10px;
        }}
        
        .before-after-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        
        .file-comparison {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #3498db;
        }}
        
        .comparison-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        
        .stat {{
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 8px;
        }}
        
        .stat .label {{
            display: block;
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        
        .stat .value {{
            display: block;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .value.added {{ color: #27ae60; }}
        .value.removed {{ color: #e74c3c; }}
        .value.modified {{ color: #f39c12; }}
        .value.score {{ color: #3498db; }}
        
        .reasoning-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .pattern-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .pattern-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .pattern-name {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .pattern-count {{
            background: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
        }}
        
        .confidence-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .conf-stat {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .conf-stat .label {{
            display: block;
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        
        .conf-stat .value {{
            display: block;
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .reasoning-examples {{
            margin-top: 20px;
        }}
        
        .example-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #27ae60;
        }}
        
        .example-item h5 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .reasoning-text {{
            font-style: italic;
            color: #7f8c8d;
            margin-bottom: 10px;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }}
        
        .example-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        
        .confidence {{ color: #27ae60; font-weight: bold; }}
        .file {{ color: #3498db; }}
        
        .key-changes {{
            margin-top: 15px;
        }}
        
        .key-changes ul {{
            list-style: none;
            padding: 0;
        }}
        
        .key-changes li {{
            background: white;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #f39c12;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .before-after-grid {{
                grid-template-columns: 1fr;
            }}
            
            .comparison-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Ultra Detailed Obsidian Auto-Linker Analytics</h1>
            <div class="subtitle">Maximum Detail Analysis with Before/After Files & AI Reasoning</div>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📁 Total Files</h3>
                <div class="metric-value">{total_files:,}</div>
                <div class="metric-label">Files in vault</div>
            </div>
            
            <div class="metric-card">
                <h3>✅ Processed</h3>
                <div class="metric-value">{processed_files:,}</div>
                <div class="metric-label">Successfully processed</div>
            </div>
            
            <div class="metric-card">
                <h3>⏭️ Skipped</h3>
                <div class="metric-value">{skipped_files:,}</div>
                <div class="metric-label">Files skipped</div>
            </div>
            
            <div class="metric-card">
                <h3>❌ Failed</h3>
                <div class="metric-value">{failed_files:,}</div>
                <div class="metric-label">Processing failures</div>
            </div>
            
            <div class="metric-card">
                <h3>⏱️ Processing Time</h3>
                <div class="metric-value">{processing_time:.1f}s</div>
                <div class="metric-label">Total processing time</div>
            </div>
            
            <div class="metric-card">
                <h3>🚀 Speed</h3>
                <div class="metric-value">{files_per_minute:.0f}</div>
                <div class="metric-label">Files per minute</div>
            </div>
        </div>
        
        {generate_before_after_comparison(analytics)}
        
        {generate_reasoning_analysis(analytics)}
        
        <div class="footer">
            <p>🚀 Generated by Ultra Detailed Obsidian Auto-Linker Analytics System</p>
            <p>🕒 Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def auto_open_report(report_path: str):
    """Automatically open the report in the default browser"""
    try:
        # Get absolute path
        abs_path = os.path.abspath(report_path)
        
        # Open in browser
        webbrowser.open(f'file://{abs_path}')
        print(f"🌐 Ultra detailed report opened in browser: {abs_path}")
    except Exception as e:
        print(f"❌ Could not auto-open report: {e}")
        print(f"📄 Report saved to: {report_path}")

def main():
    """Main function to generate ultra detailed analytics"""
    print("🚀 Generating ultra detailed analytics report...")
    print("📊 Including before/after files and AI reasoning analysis...")
    
    # Load analytics data
    analytics = load_analytics_data()
    
    # Generate ultra detailed report
    html_report = generate_ultra_detailed_report(analytics)
    
    # Save report
    report_path = "ultra_detailed_analytics_report.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"✅ Ultra detailed analytics report generated!")
    print(f"📄 Report saved to: {report_path}")
    
    # Auto-open report
    auto_open_report(report_path)
    
    return report_path

if __name__ == "__main__":
    main()
