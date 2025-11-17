#!/usr/bin/env python3
"""
Enhanced Analytics System for Obsidian Auto-Linker
Generates comprehensive, detailed analytics reports
"""

import os
import json
import yaml
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import webbrowser
from pathlib import Path

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
    
    return analytics

def generate_comprehensive_report(analytics: Dict[str, Any]) -> str:
    """Generate the most detailed analytics report possible"""
    
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
    
    # Generate comprehensive HTML report
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Comprehensive Obsidian Auto-Linker Analytics</title>
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
            max-width: 1400px;
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
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .timestamp {{
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            font-weight: bold;
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
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
        }}
        
        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-container h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 10px;
        }}
        
        .moc-distribution {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        
        .moc-item {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .moc-item:hover {{
            transform: scale(1.05);
        }}
        
        .moc-name {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        
        .moc-count {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .moc-percentage {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .detailed-stats {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }}
        
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .timeline {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .timeline-item {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        .timeline-time {{
            font-weight: bold;
            color: #2c3e50;
            margin-right: 15px;
            min-width: 120px;
        }}
        
        .timeline-event {{
            color: #7f8c8d;
        }}
        
        .recommendations {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .recommendation-item {{
            background: #e8f5e8;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }}
        
        .recommendation-title {{
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 5px;
        }}
        
        .recommendation-text {{
            color: #2c3e50;
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
            
            .moc-distribution {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Comprehensive Obsidian Auto-Linker Analytics</h1>
            <div class="subtitle">Detailed Performance Analysis & Insights</div>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>

        <h2 style="color: #fff; margin-bottom: 10px;">Processing Summary</h2>

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
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(processed_files/total_files*100) if total_files > 0 else 0:.1f}%"></div>
                </div>
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
        
        <div class="chart-container">
            <h2>🏷️ MOC Distribution Analysis</h2>
            <div class="moc-distribution">"""
    
    # Add MOC distribution
    for moc, count in sorted(moc_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = moc_percentages[moc]
        html += f"""
                <div class="moc-item">
                    <div class="moc-name">{moc}</div>
                    <div class="moc-count">{count:,}</div>
                    <div class="moc-percentage">{percentage:.1f}%</div>
                </div>"""
    
    html += """
            </div>
        </div>
        
        <div class="detailed-stats">
            <h2>📈 Detailed Performance Metrics</h2>
            <div class="stats-grid">"""
    
    # Add detailed statistics
    stats = [
        ("Success Rate", f"{(processed_files/total_files*100) if total_files > 0 else 0:.1f}%"),
        ("Skip Rate", f"{(skipped_files/total_files*100) if total_files > 0 else 0:.1f}%"),
        ("Failure Rate", f"{(failed_files/total_files*100) if total_files > 0 else 0:.1f}%"),
        ("Avg Time/File", f"{avg_time_per_file:.2f}s"),
        ("Cache Hits", processing.get('cache_hits', 0)),
        ("Cache Misses", processing.get('cache_misses', 0)),
        ("Retry Attempts", processing.get('retry_attempts', 0)),
        ("Error Types", len(processing.get('error_types', {})))
    ]
    
    for label, value in stats:
        html += f"""
                <div class="stat-item">
                    <div class="stat-value">{value}</div>
                    <div class="stat-label">{label}</div>
                </div>"""
    
    html += """
            </div>
        </div>
        
        <div class="timeline">
            <h2>⏰ Processing Timeline</h2>"""
    
    # Add timeline events
    timeline_events = [
        ("Start", processing.get('start_time', 'Unknown')),
        ("End", processing.get('end_time', 'Unknown')),
        ("Duration", f"{processing_time:.1f} seconds"),
        ("Files/Min", f"{files_per_minute:.0f}"),
        ("Avg/File", f"{avg_time_per_file:.2f}s")
    ]
    
    for event, time_info in timeline_events:
        html += f"""
            <div class="timeline-item">
                <div class="timeline-time">{event}</div>
                <div class="timeline-event">{time_info}</div>
            </div>"""
    
    html += """
        </div>
        
        <div class="recommendations">
            <h2>💡 Recommendations & Insights</h2>"""
    
    # Generate recommendations based on data
    recommendations = []
    
    if failed_files > 0:
        recommendations.append(("⚠️ Processing Issues", f"Consider reviewing the {failed_files} failed files and checking for content issues or model timeouts."))
    
    if processing_time > 300:  # More than 5 minutes
        recommendations.append(("🐌 Performance", "Processing took longer than expected. Consider using faster model or reducing batch size."))
    
    if total_files > 0 and (moc_dist.get('Life & Misc', 0) / total_files) > 0.5:
        recommendations.append(("🏷️ Categorization", "High percentage of 'Life & Misc' files. Consider refining MOC categories or improving AI prompts."))
    
    if files_per_minute < 10:
        recommendations.append(("⚡ Speed Optimization", "Processing speed could be improved. Consider using parallel processing or faster model."))
    
    if not recommendations:
        recommendations.append(("✅ Excellent Performance", "All metrics look great! Your auto-linker is working optimally."))
    
    for title, text in recommendations:
        html += f"""
            <div class="recommendation-item">
                <div class="recommendation-title">{title}</div>
                <div class="recommendation-text">{text}</div>
            </div>"""
    
    html += """
        </div>
        
        <div class="footer">
            <p>📊 Generated by Obsidian Auto-Linker Enhanced Analytics System</p>
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
        print(f"🌐 Report opened in browser: {abs_path}")
    except Exception as e:
        print(f"❌ Could not auto-open report: {e}")
        print(f"📄 Report saved to: {report_path}")

def main():
    """Main function to generate comprehensive analytics"""
    print("📊 Generating comprehensive analytics report...")
    
    # Load analytics data
    analytics = load_analytics_data()
    
    # Generate comprehensive report
    html_report = generate_comprehensive_report(analytics)
    
    # Save report
    report_path = "comprehensive_analytics_report.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"✅ Comprehensive analytics report generated!")
    print(f"📄 Report saved to: {report_path}")
    
    # Auto-open report
    auto_open_report(report_path)
    
    return report_path

if __name__ == "__main__":
    main()
