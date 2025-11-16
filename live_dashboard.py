#!/usr/bin/env python3
"""
Live Terminal Dashboard for Obsidian Auto-Linker
Optimized for MacBook Air M4 2025
"""

import time
import psutil
import threading
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque
from pathlib import Path
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box

class LiveDashboard:
    """
    Ultra-detailed live monitoring dashboard with 30-second updates
    Optimized for M4 MacBook Air with performance & efficiency core tracking
    """

    def __init__(self, update_interval: int = 15):
        self.console = Console()
        self.update_interval = update_interval
        self.running = False
        self.update_thread = None

        # Metrics storage
        self.stats = {
            # Processing stats
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'current_file': '',
            'current_stage': 'Initializing',
            'start_time': datetime.now(),
            'last_update': datetime.now(),

            # AI Performance
            'ai_requests': 0,
            'ai_success': 0,
            'ai_failures': 0,
            'ai_timeouts': 0,
            'ai_retries': 0,
            'ai_response_times': deque(maxlen=100),  # Last 100 requests
            'tokens_per_second': 0,
            'avg_tokens': 0,

            # Cache Performance
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_size_mb': 0,
            'cache_entries': 0,
            'cache_lookup_times': deque(maxlen=100),
            'time_saved_seconds': 0,

            # System Resources
            'cpu_percent': 0,
            'cpu_per_core': [],
            'memory_percent': 0,
            'memory_used_gb': 0,
            'memory_total_gb': 0,
            'disk_read_mb': 0,
            'disk_write_mb': 0,
            'network_sent_kb': 0,
            'network_recv_kb': 0,
            'temperature': 0,
            'power_watts': 0,

            # File Analysis
            'file_times_small': deque(maxlen=50),
            'file_times_medium': deque(maxlen=50),
            'file_times_large': deque(maxlen=50),
            'moc_distribution': {},

            # Error Tracking
            'recent_errors': deque(maxlen=10),
            'error_types': {},

            # Activity Log
            'recent_activity': deque(maxlen=5),
        }

        # Initial system baseline
        self.initial_disk_io = psutil.disk_io_counters()
        self.initial_net_io = psutil.net_io_counters()
        self.last_disk_io = self.initial_disk_io
        self.last_net_io = self.initial_net_io
        self.last_io_check = time.time()

    def start(self):
        """Start the dashboard"""
        self.running = True
        self.stats['start_time'] = datetime.now()

    def stop(self):
        """Stop the dashboard"""
        self.running = False

    def update_processing(self, **kwargs):
        """Update processing statistics"""
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] = value
        self.stats['last_update'] = datetime.now()

    def add_ai_request(self, response_time: float, success: bool, tokens: int = 0, timeout: bool = False):
        """Track AI request metrics"""
        self.stats['ai_requests'] += 1
        if success:
            self.stats['ai_success'] += 1
            self.stats['ai_response_times'].append(response_time)
            if tokens > 0:
                # Update token metrics
                total_tokens = self.stats['avg_tokens'] * (self.stats['ai_success'] - 1) + tokens
                self.stats['avg_tokens'] = total_tokens / self.stats['ai_success']
                if response_time > 0:
                    self.stats['tokens_per_second'] = tokens / response_time
        else:
            self.stats['ai_failures'] += 1
            if timeout:
                self.stats['ai_timeouts'] += 1

    def add_cache_hit(self, lookup_time: float = 0):
        """Track cache hit"""
        self.stats['cache_hits'] += 1
        if lookup_time > 0:
            self.stats['cache_lookup_times'].append(lookup_time)

    def add_cache_miss(self):
        """Track cache miss"""
        self.stats['cache_misses'] += 1

    def update_cache_stats(self, size_mb: float, entries: int):
        """Update cache statistics"""
        self.stats['cache_size_mb'] = size_mb
        self.stats['cache_entries'] = entries

    def add_file_processing_time(self, file_size_kb: int, processing_time: float):
        """Track file processing time by size category"""
        if file_size_kb < 5:
            self.stats['file_times_small'].append(processing_time)
        elif file_size_kb < 50:
            self.stats['file_times_medium'].append(processing_time)
        else:
            self.stats['file_times_large'].append(processing_time)

    def add_moc_category(self, category: str):
        """Track MOC category distribution"""
        if category not in self.stats['moc_distribution']:
            self.stats['moc_distribution'][category] = 0
        self.stats['moc_distribution'][category] += 1

    def add_error(self, error_type: str, message: str):
        """Track error"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.stats['recent_errors'].append(f"[{timestamp}] {error_type}: {message}")

        if error_type not in self.stats['error_types']:
            self.stats['error_types'][error_type] = 0
        self.stats['error_types'][error_type] += 1

    def add_activity(self, message: str, success: bool = True):
        """Add activity log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = "✓" if success else "✗"
        self.stats['recent_activity'].append(f"[{timestamp}] {icon} {message}")

    def update_system_resources(self):
        """Update system resource metrics - M4 optimized"""
        # CPU
        self.stats['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        self.stats['cpu_per_core'] = psutil.cpu_percent(interval=0.1, percpu=True)

        # Memory
        mem = psutil.virtual_memory()
        self.stats['memory_percent'] = mem.percent
        self.stats['memory_used_gb'] = mem.used / (1024**3)
        self.stats['memory_total_gb'] = mem.total / (1024**3)

        # Disk I/O
        current_time = time.time()
        time_delta = current_time - self.last_io_check

        if time_delta > 0:
            disk_io = psutil.disk_io_counters()
            if disk_io and self.last_disk_io:
                read_bytes = disk_io.read_bytes - self.last_disk_io.read_bytes
                write_bytes = disk_io.write_bytes - self.last_disk_io.write_bytes
                self.stats['disk_read_mb'] = (read_bytes / (1024**2)) / time_delta
                self.stats['disk_write_mb'] = (write_bytes / (1024**2)) / time_delta
                self.last_disk_io = disk_io

            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io and self.last_net_io:
                sent_bytes = net_io.bytes_sent - self.last_net_io.bytes_sent
                recv_bytes = net_io.bytes_recv - self.last_net_io.bytes_recv
                self.stats['network_sent_kb'] = (sent_bytes / 1024) / time_delta
                self.stats['network_recv_kb'] = (recv_bytes / 1024) / time_delta
                self.last_net_io = net_io

            self.last_io_check = current_time

        # Try to get temperature (macOS specific)
        try:
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                self.stats['temperature'] = temps['coretemp'][0].current
        except (AttributeError, KeyError):
            # Temperature sensors not available on all systems
            pass

    def _calculate_stats(self, values: deque) -> Dict[str, float]:
        """Calculate min, max, avg, median from deque"""
        if not values:
            return {'min': 0, 'max': 0, 'avg': 0, 'median': 0}

        sorted_vals = sorted(values)
        return {
            'min': sorted_vals[0],
            'max': sorted_vals[-1],
            'avg': sum(values) / len(values),
            'median': sorted_vals[len(sorted_vals) // 2]
        }

    def _create_processing_panel(self) -> Panel:
        """Create processing status panel"""
        processed = self.stats['processed_files']
        total = self.stats['total_files']
        failed = self.stats['failed_files']

        # Calculate progress
        progress_pct = (processed / total * 100) if total > 0 else 0

        # Calculate speed and ETA
        elapsed = datetime.now() - self.stats['start_time']
        elapsed_seconds = elapsed.total_seconds()

        if processed > 0 and elapsed_seconds > 0:
            speed = processed / (elapsed_seconds / 60)  # files per minute
            remaining = total - processed
            eta_minutes = remaining / speed if speed > 0 else 0
            eta_str = f"{eta_minutes:.0f}min" if eta_minutes < 60 else f"{eta_minutes/60:.1f}h"
            speed_str = f"{speed:.1f} files/min"
        else:
            eta_str = "calculating..."
            speed_str = "0.0 files/min"

        # Create progress bar
        bar_width = 40
        filled = int(bar_width * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        content = f"""[bold cyan]Files:[/bold cyan] {processed}/{total} ({progress_pct:.1f}%) [{bar}]
[bold cyan]Current:[/bold cyan] {self.stats['current_file'][:60]}
[bold cyan]Stage:[/bold cyan] {self.stats['current_stage']}
[bold cyan]Speed:[/bold cyan] {speed_str}  [bold cyan]ETA:[/bold cyan] {eta_str}
[bold cyan]Elapsed:[/bold cyan] {str(elapsed).split('.')[0]}  [bold red]Failed:[/bold red] {failed}"""

        return Panel(content, title="📊 PROCESSING STATUS", border_style="cyan", box=box.ROUNDED)

    def _create_system_panel(self) -> Panel:
        """Create system resources panel - M4 optimized"""
        cpu_pct = self.stats['cpu_percent']
        mem_pct = self.stats['memory_percent']

        # CPU bar
        cpu_bar = self._create_bar(cpu_pct, 40, "cyan")
        mem_bar = self._create_bar(mem_pct, 40, "yellow")

        # M4 specific: Show performance vs efficiency cores
        cores = self.stats['cpu_per_core']
        core_info = "N/A"

        if isinstance(cores, (list, tuple)) and cores:
            if len(cores) == 8:
                # M4 has 4 P-cores + 4 E-cores
                p_cores = cores[:4]
                e_cores = cores[4:]
                p_avg = sum(p_cores) / len(p_cores)
                e_avg = sum(e_cores) / len(e_cores)
                core_info = f"P-cores: {p_avg:.0f}%  E-cores: {e_avg:.0f}%"
            else:
                core_info = f"{len(cores)} cores"
        elif isinstance(cores, (int, float)):
            core_info = f"Avg load: {cores:.0f}%"

        temp_str = f"{self.stats['temperature']:.0f}°C" if self.stats['temperature'] > 0 else "N/A"

        content = f"""[bold green]CPU:[/bold green] [{cpu_bar}] {cpu_pct:.1f}%  ({core_info})
[bold yellow]Memory:[/bold yellow] [{mem_bar}] {self.stats['memory_used_gb']:.1f}/{self.stats['memory_total_gb']:.1f} GB ({mem_pct:.1f}%)
[bold blue]Disk I/O:[/bold blue] ↓ {self.stats['disk_read_mb']:.1f} MB/s  ↑ {self.stats['disk_write_mb']:.1f} MB/s
[bold magenta]Network:[/bold magenta] ↓ {self.stats['network_recv_kb']:.1f} KB/s  ↑ {self.stats['network_sent_kb']:.1f} KB/s
[bold red]Temp:[/bold red] {temp_str}"""

        return Panel(content, title="🖥️  SYSTEM RESOURCES (M4)", border_style="green", box=box.ROUNDED)

    def _create_ai_panel(self) -> Panel:
        """Create AI performance panel"""
        total_requests = self.stats['ai_requests']
        success = self.stats['ai_success']
        failures = self.stats['ai_failures']
        timeouts = self.stats['ai_timeouts']

        success_rate = (success / total_requests * 100) if total_requests > 0 else 0

        # Calculate response time statistics
        response_stats = self._calculate_stats(self.stats['ai_response_times'])

        content = f"""[bold cyan]Requests:[/bold cyan] {total_requests} total  [green]✓ {success}[/green]  [red]✗ {failures}[/red]  ({success_rate:.1f}%)
[bold cyan]Response Time:[/bold cyan] {response_stats['avg']:.1f}s avg  [{response_stats['min']:.1f}s min  {response_stats['max']:.1f}s max  {response_stats.get('median', 0):.1f}s median]
[bold cyan]Tokens/sec:[/bold cyan] {self.stats['tokens_per_second']:.1f}  [bold cyan]Avg tokens:[/bold cyan] {self.stats['avg_tokens']:.0f}
[bold yellow]Timeouts:[/bold yellow] {timeouts}  [bold yellow]Retries:[/bold yellow] {self.stats['ai_retries']}"""

        return Panel(content, title="🤖 AI PERFORMANCE (Ollama)", border_style="blue", box=box.ROUNDED)

    def _create_cache_panel(self) -> Panel:
        """Create cache performance panel"""
        hits = self.stats['cache_hits']
        misses = self.stats['cache_misses']
        total_lookups = hits + misses

        hit_rate = (hits / total_lookups * 100) if total_lookups > 0 else 0
        hit_bar = self._create_bar(hit_rate, 30, "green")

        # Estimate time saved
        avg_ai_time = self._calculate_stats(self.stats['ai_response_times'])['avg']
        time_saved_seconds = hits * avg_ai_time
        time_saved_str = f"{time_saved_seconds/60:.1f}min" if time_saved_seconds < 3600 else f"{time_saved_seconds/3600:.1f}h"

        lookup_stats = self._calculate_stats(self.stats['cache_lookup_times'])

        content = f"""[bold green]Hit Rate:[/bold green] [{hit_bar}] {hit_rate:.1f}%
[bold cyan]Hits:[/bold cyan] {hits}  [bold cyan]Misses:[/bold cyan] {misses}  [bold cyan]Total:[/bold cyan] {total_lookups}
[bold cyan]Cache Size:[/bold cyan] {self.stats['cache_size_mb']:.1f} MB ({self.stats['cache_entries']} entries)
[bold green]Time Saved:[/bold green] {time_saved_str}  [bold cyan]Avg lookup:[/bold cyan] {lookup_stats['avg']*1000:.1f}ms"""

        return Panel(content, title="💾 CACHE PERFORMANCE", border_style="magenta", box=box.ROUNDED)

    def _create_file_analysis_panel(self) -> Panel:
        """Create file analysis panel"""
        small_stats = self._calculate_stats(self.stats['file_times_small'])
        medium_stats = self._calculate_stats(self.stats['file_times_medium'])
        large_stats = self._calculate_stats(self.stats['file_times_large'])

        # MOC distribution top 5
        moc_items = sorted(self.stats['moc_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]
        moc_lines = []
        total_categorized = sum(self.stats['moc_distribution'].values())

        for moc, count in moc_items:
            pct = (count / total_categorized * 100) if total_categorized > 0 else 0
            bar = self._create_bar(pct, 15, "cyan")
            moc_lines.append(f"  {moc[:25]:<25} [{bar}] {count} ({pct:.0f}%)")

        moc_content = "\n".join(moc_lines) if moc_lines else "  No data yet"

        content = f"""[bold cyan]Processing Time by Size:[/bold cyan]
  Small (<5KB):   {small_stats['avg']:.1f}s avg  [{len(self.stats['file_times_small'])} files]
  Medium (5-50KB): {medium_stats['avg']:.1f}s avg  [{len(self.stats['file_times_medium'])} files]
  Large (>50KB):  {large_stats['avg']:.1f}s avg  [{len(self.stats['file_times_large'])} files]

[bold cyan]MOC Distribution (Top 5):[/bold cyan]
{moc_content}"""

        return Panel(content, title="📁 FILE ANALYSIS", border_style="yellow", box=box.ROUNDED)

    def _create_activity_panel(self) -> Panel:
        """Create recent activity panel"""
        activities = list(self.stats['recent_activity'])
        if not activities:
            activities = ["No activity yet"]

        content = "\n".join(activities)
        return Panel(content, title="📜 RECENT ACTIVITY", border_style="white", box=box.ROUNDED)

    def _create_errors_panel(self) -> Panel:
        """Create errors panel"""
        errors = list(self.stats['recent_errors'])
        if not errors:
            content = "[green]✓ No errors[/green]"
        else:
            content = "\n".join(errors[-5:])  # Last 5 errors

        return Panel(content, title="⚠️  ERRORS & WARNINGS", border_style="red", box=box.ROUNDED)

    def _create_bar(self, percentage: float, width: int, color: str = "cyan") -> str:
        """Create a progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{color}]{bar}[/{color}]"

    def export_to_json(self, filepath: str = "dashboard_metrics.json") -> bool:
        """
        Export dashboard metrics to JSON file

        Args:
            filepath: Path to save JSON file (default: dashboard_metrics.json)

        Returns:
            True if export successful, False otherwise
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'session_duration': str(datetime.now() - self.stats['start_time']),

                # Processing metrics
                'processing': {
                    'total_files': self.stats['total_files'],
                    'processed_files': self.stats['processed_files'],
                    'failed_files': self.stats['failed_files'],
                    'skipped_files': self.stats['skipped_files'],
                    'success_rate': round((self.stats['processed_files'] / self.stats['total_files'] * 100)
                                        if self.stats['total_files'] > 0 else 0, 2),
                },

                # AI metrics
                'ai_performance': {
                    'total_requests': self.stats['ai_requests'],
                    'successful_requests': self.stats['ai_success'],
                    'failed_requests': self.stats['ai_failures'],
                    'timeouts': self.stats['ai_timeouts'],
                    'retries': self.stats['ai_retries'],
                    'avg_response_time': round(sum(self.stats['ai_response_times']) / len(self.stats['ai_response_times']), 3)
                                        if self.stats['ai_response_times'] else 0,
                    'avg_tokens': round(self.stats['avg_tokens'], 1),
                    'tokens_per_second': round(self.stats['tokens_per_second'], 2),
                    'success_rate': round((self.stats['ai_success'] / self.stats['ai_requests'] * 100)
                                        if self.stats['ai_requests'] > 0 else 0, 2),
                },

                # Cache metrics
                'cache_performance': {
                    'hits': self.stats['cache_hits'],
                    'misses': self.stats['cache_misses'],
                    'hit_rate': round((self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) * 100)
                                    if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0, 2),
                    'size_mb': round(self.stats['cache_size_mb'], 2),
                    'entries': self.stats['cache_entries'],
                    'time_saved_seconds': round(self.stats['time_saved_seconds'], 1),
                },

                # System resources
                'system_resources': {
                    'cpu_percent': round(self.stats['cpu_percent'], 1),
                    'memory_percent': round(self.stats['memory_percent'], 1),
                    'memory_used_gb': round(self.stats['memory_used_gb'], 2),
                    'disk_read_mb_per_sec': round(self.stats['disk_read_mb'], 2),
                    'disk_write_mb_per_sec': round(self.stats['disk_write_mb'], 2),
                    'network_sent_kb_per_sec': round(self.stats['network_sent_kb'], 2),
                    'network_recv_kb_per_sec': round(self.stats['network_recv_kb'], 2),
                    'temperature': round(self.stats['temperature'], 1) if self.stats['temperature'] else 0,
                },

                # MOC distribution
                'moc_distribution': dict(self.stats['moc_distribution']),

                # Error summary
                'errors': {
                    'total_errors': len(self.stats['recent_errors']),
                    'error_types': dict(self.stats['error_types']),
                    'recent_errors': list(self.stats['recent_errors']),
                },
            }

            # Write to file
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            print(f"✅ Dashboard metrics exported to {filepath}")
            return True

        except Exception as e:
            print(f"❌ Failed to export metrics to JSON: {e}")
            return False

    def export_to_csv(self, filepath: str = "dashboard_metrics.csv") -> bool:
        """
        Export dashboard metrics to CSV file

        Args:
            filepath: Path to save CSV file (default: dashboard_metrics.csv)

        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(['Metric Category', 'Metric Name', 'Value', 'Unit'])
                writer.writerow([])

                # Session info
                writer.writerow(['Session', 'Export Timestamp', datetime.now().isoformat(), ''])
                writer.writerow(['Session', 'Duration', str(datetime.now() - self.stats['start_time']), ''])
                writer.writerow([])

                # Processing metrics
                writer.writerow(['Processing', 'Total Files', self.stats['total_files'], 'files'])
                writer.writerow(['Processing', 'Processed Files', self.stats['processed_files'], 'files'])
                writer.writerow(['Processing', 'Failed Files', self.stats['failed_files'], 'files'])
                writer.writerow(['Processing', 'Skipped Files', self.stats['skipped_files'], 'files'])
                writer.writerow(['Processing', 'Success Rate',
                               round((self.stats['processed_files'] / self.stats['total_files'] * 100)
                                   if self.stats['total_files'] > 0 else 0, 2), '%'])
                writer.writerow([])

                # AI metrics
                writer.writerow(['AI Performance', 'Total Requests', self.stats['ai_requests'], 'requests'])
                writer.writerow(['AI Performance', 'Successful Requests', self.stats['ai_success'], 'requests'])
                writer.writerow(['AI Performance', 'Failed Requests', self.stats['ai_failures'], 'requests'])
                writer.writerow(['AI Performance', 'Timeouts', self.stats['ai_timeouts'], 'timeouts'])
                writer.writerow(['AI Performance', 'Retries', self.stats['ai_retries'], 'retries'])
                writer.writerow(['AI Performance', 'Avg Response Time',
                               round(sum(self.stats['ai_response_times']) / len(self.stats['ai_response_times']), 3)
                               if self.stats['ai_response_times'] else 0, 'seconds'])
                writer.writerow(['AI Performance', 'Avg Tokens', round(self.stats['avg_tokens'], 1), 'tokens'])
                writer.writerow(['AI Performance', 'Tokens Per Second', round(self.stats['tokens_per_second'], 2), 'tokens/s'])
                writer.writerow(['AI Performance', 'Success Rate',
                               round((self.stats['ai_success'] / self.stats['ai_requests'] * 100)
                                   if self.stats['ai_requests'] > 0 else 0, 2), '%'])
                writer.writerow([])

                # Cache metrics
                writer.writerow(['Cache', 'Hits', self.stats['cache_hits'], 'hits'])
                writer.writerow(['Cache', 'Misses', self.stats['cache_misses'], 'misses'])
                writer.writerow(['Cache', 'Hit Rate',
                               round((self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) * 100)
                                   if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0, 2), '%'])
                writer.writerow(['Cache', 'Size', round(self.stats['cache_size_mb'], 2), 'MB'])
                writer.writerow(['Cache', 'Entries', self.stats['cache_entries'], 'entries'])
                writer.writerow(['Cache', 'Time Saved', round(self.stats['time_saved_seconds'], 1), 'seconds'])
                writer.writerow([])

                # System resources
                writer.writerow(['System', 'CPU Usage', round(self.stats['cpu_percent'], 1), '%'])
                writer.writerow(['System', 'Memory Usage', round(self.stats['memory_percent'], 1), '%'])
                writer.writerow(['System', 'Memory Used', round(self.stats['memory_used_gb'], 2), 'GB'])
                writer.writerow(['System', 'Disk Read', round(self.stats['disk_read_mb'], 2), 'MB/s'])
                writer.writerow(['System', 'Disk Write', round(self.stats['disk_write_mb'], 2), 'MB/s'])
                writer.writerow(['System', 'Network Sent', round(self.stats['network_sent_kb'], 2), 'KB/s'])
                writer.writerow(['System', 'Network Received', round(self.stats['network_recv_kb'], 2), 'KB/s'])
                if self.stats['temperature']:
                    writer.writerow(['System', 'Temperature', round(self.stats['temperature'], 1), '°C'])
                writer.writerow([])

                # MOC distribution
                writer.writerow(['MOC Distribution', '', '', ''])
                for category, count in self.stats['moc_distribution'].items():
                    writer.writerow(['MOC', category, count, 'files'])
                writer.writerow([])

                # Error summary
                writer.writerow(['Errors', 'Total Errors', len(self.stats['recent_errors']), 'errors'])
                for error_type, count in self.stats['error_types'].items():
                    writer.writerow(['Error Type', error_type, count, 'occurrences'])

            print(f"✅ Dashboard metrics exported to {filepath}")
            return True

        except Exception as e:
            print(f"❌ Failed to export metrics to CSV: {e}")
            return False

    def render(self) -> Layout:
        """Render the complete dashboard"""
        # Update system resources
        self.update_system_resources()

        # Create layout
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        layout["left"].split_column(
            Layout(name="processing"),
            Layout(name="system"),
            Layout(name="ai")
        )

        layout["right"].split_column(
            Layout(name="cache"),
            Layout(name="files"),
            Layout(name="activity"),
            Layout(name="errors")
        )

        # Header
        header = Panel(
            "[bold white]OBSIDIAN AUTO-LINKER - LIVE DASHBOARD[/bold white]\n"
            f"Running on MacBook Air M4 2025  |  Updates every {self.update_interval}s  |  Press Ctrl+C to stop",
            style="bold white on blue"
        )
        layout["header"].update(header)

        # Panels
        layout["processing"].update(self._create_processing_panel())
        layout["system"].update(self._create_system_panel())
        layout["ai"].update(self._create_ai_panel())
        layout["cache"].update(self._create_cache_panel())
        layout["files"].update(self._create_file_analysis_panel())
        layout["activity"].update(self._create_activity_panel())
        layout["errors"].update(self._create_errors_panel())

        # Footer
        footer = Panel(
            f"[dim]Last update: {datetime.now().strftime('%H:%M:%S')}  |  "
            f"Dashboard running for: {str(datetime.now() - self.stats['start_time']).split('.')[0]}[/dim]",
            style="dim white"
        )
        layout["footer"].update(footer)

        return layout

# Global dashboard instance
_dashboard_instance: Optional[LiveDashboard] = None

def get_dashboard(update_interval: int = 15) -> LiveDashboard:
    """Get or create the global dashboard instance"""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = LiveDashboard(update_interval=update_interval)
    return _dashboard_instance

if __name__ == "__main__":
    # Test the dashboard
    dashboard = LiveDashboard(update_interval=2)
    dashboard.start()

    # Simulate some activity
    dashboard.update_processing(
        total_files=100,
        processed_files=25,
        failed_files=2,
        current_file="test-file-name-that-is-very-long.md",
        current_stage="AI Analysis"
    )

    # Simulate AI requests
    for _ in range(10):
        dashboard.add_ai_request(8.5, True, 250)
    dashboard.add_ai_request(15.0, False, timeout=True)

    # Simulate cache
    for _ in range(20):
        dashboard.add_cache_hit(0.0003)
    for _ in range(30):
        dashboard.add_cache_miss()
    dashboard.update_cache_stats(2.4, 458)

    # Simulate MOC categories
    for category in ["Client Acquisition", "Technical Automation", "Learning & Skills"]:
        for _ in range(10):
            dashboard.add_moc_category(category)

    # Add activity
    dashboard.add_activity("Processed: test-file.md (8.1s)", True)
    dashboard.add_activity("Failed: corrupted.md (timeout)", False)

    # Render with Live
    try:
        with Live(dashboard.render(), refresh_per_second=0.5, screen=True) as live:
            for i in range(100):
                time.sleep(2)
                dashboard.stats['processed_files'] = 25 + i
                dashboard.add_ai_request(8.0 + (i % 5), True, 250)
                live.update(dashboard.render())
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")

