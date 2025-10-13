#!/usr/bin/env python3
"""
Enhanced Analytics Report Generator
Creates detailed reports from processing analytics
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_detailed_report():
    """Generate a comprehensive detailed report"""
    
    # Check if analytics exist
    analytics_file = 'processing_analytics.json'
    if not os.path.exists(analytics_file):
        print("❌ No analytics data found. Run the software first.")
        return
    
    # Load analytics data
    with open(analytics_file, 'r') as f:
        analytics = json.load(f)
    
    # Generate detailed HTML report
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Detailed Obsidian Auto-Linker Report</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            text-align: center;
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .section {{ 
            margin: 30px 0; 
            padding: 20px; 
            background: #f9f9f9; 
            border-radius: 8px; 
            border-left: 4px solid #667eea;
        }}
        .section h2 {{ 
            margin: 0 0 20px 0; 
            color: #333; 
            font-size: 1.5em;
        }}
        .metrics-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin: 20px 0;
        }}
        .metric {{ 
            background: white; 
            padding: 15px; 
            border-radius: 6px; 
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{ 
            font-size: 2em; 
            font-weight: bold; 
            color: #667eea; 
            margin-bottom: 5px;
        }}
        .metric-label {{ 
            color: #666; 
            font-size: 0.9em;
        }}
        .moc-dist {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px; 
            margin: 15px 0;
        }}
        .moc-item {{ 
            background: #e3f2fd; 
            padding: 10px 15px; 
            border-radius: 20px; 
            font-size: 0.9em;
            border: 1px solid #bbdefb;
        }}
        .error-item {{ 
            background: #ffebee; 
            padding: 10px; 
            border-radius: 4px; 
            margin: 5px 0;
            border-left: 3px solid #f44336;
        }}
        .performance-chart {{ 
            background: white; 
            padding: 20px; 
            border-radius: 6px; 
            margin: 15px 0;
        }}
        .timeline {{ 
            background: white; 
            padding: 20px; 
            border-radius: 6px; 
            margin: 15px 0;
        }}
        .timeline-item {{ 
            display: flex; 
            justify-content: space-between; 
            padding: 10px 0; 
            border-bottom: 1px solid #eee;
        }}
        .timeline-item:last-child {{ border-bottom: none; }}
        .success {{ color: #4caf50; }}
        .warning {{ color: #ff9800; }}
        .error {{ color: #f44336; }}
        .info {{ color: #2196f3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Detailed Processing Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <!-- Processing Summary -->
            <div class="section">
                <h2>📈 Processing Summary</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-value">{analytics.get('total_files', 0)}</div>
                        <div class="metric-label">Total Files</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value success">{analytics.get('processed_files', 0)}</div>
                        <div class="metric-label">Successfully Processed</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value warning">{analytics.get('skipped_files', 0)}</div>
                        <div class="metric-label">Skipped</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value error">{analytics.get('failed_files', 0)}</div>
                        <div class="metric-label">Failed</div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="section">
                <h2>⚡ Performance Metrics</h2>
                <div class="performance-chart">
                    <div class="metrics-grid">
                        <div class="metric">
                            <div class="metric-value">{analytics.get('processing_time', 0):.1f}s</div>
                            <div class="metric-label">Total Processing Time</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{analytics.get('cache_hits', 0)}</div>
                            <div class="metric-label">Cache Hits</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{analytics.get('cache_misses', 0)}</div>
                            <div class="metric-label">Cache Misses</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{analytics.get('retry_attempts', 0)}</div>
                            <div class="metric-label">Retry Attempts</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- MOC Distribution -->
            <div class="section">
                <h2>🏷️ MOC (Map of Content) Distribution</h2>
                <div class="moc-dist">
                    {''.join([f'<div class="moc-item">{moc}: {count} files</div>' for moc, count in analytics.get('moc_distribution', {}).items()])}
                </div>
            </div>
            
            <!-- Timeline -->
            <div class="section">
                <h2>⏱️ Processing Timeline</h2>
                <div class="timeline">
                    <div class="timeline-item">
                        <span>Start Time</span>
                        <span class="info">{analytics.get('start_time', 'N/A')}</span>
                    </div>
                    <div class="timeline-item">
                        <span>End Time</span>
                        <span class="info">{analytics.get('end_time', 'N/A')}</span>
                    </div>
                    <div class="timeline-item">
                        <span>Duration</span>
                        <span class="info">{analytics.get('processing_time', 0):.1f} seconds</span>
                    </div>
                </div>
            </div>
            
            <!-- Error Summary -->
            <div class="section">
                <h2>❌ Error Summary</h2>
                {''.join([f'<div class="error-item"><strong>{error}:</strong> {count} occurrences</div>' for error, count in analytics.get('error_types', {}).items()]) if analytics.get('error_types') else '<div class="info">No errors recorded</div>'}
            </div>
            
            <!-- Success Rate -->
            <div class="section">
                <h2>📊 Success Rate Analysis</h2>
                <div class="performance-chart">
                    {f'''
                    <div class="metrics-grid">
                        <div class="metric">
                            <div class="metric-value success">{(analytics.get("processed_files", 0) / max(analytics.get("total_files", 1), 1) * 100):.1f}%</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value warning">{(analytics.get("skipped_files", 0) / max(analytics.get("total_files", 1), 1) * 100):.1f}%</div>
                            <div class="metric-label">Skip Rate</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value error">{(analytics.get("failed_files", 0) / max(analytics.get("total_files", 1), 1) * 100):.1f}%</div>
                            <div class="metric-label">Failure Rate</div>
                        </div>
                    </div>
                    ''' if analytics.get('total_files', 0) > 0 else '<div class="info">No files processed</div>'}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    # Save detailed report
    with open('detailed_report.html', 'w') as f:
        f.write(html_content)
    
    print("📊 Detailed report generated: detailed_report.html")
    print("🌐 Open in browser to view the full report")

if __name__ == "__main__":
    generate_detailed_report()
