#!/usr/bin/env python3
"""
Memory monitoring utility for Enhanced Obsidian Auto-Linker
Tracks RAM usage per process and provides optimization recommendations
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List

import psutil


class MemoryMonitor:
    def __init__(self):
        self.monitoring = False
        self.data = []

    def get_system_memory(self) -> Dict[str, float]:
        """Get current system memory usage"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent": memory.percent,
        }

    def get_process_memory(self, pid: int = None) -> Dict[str, float]:
        """Get memory usage for specific process or current process"""
        if pid is None:
            process = psutil.Process()
        else:
            process = psutil.Process(pid)

        memory_info = process.memory_info()
        return {
            "rss_mb": memory_info.rss / (1024**2),
            "vms_mb": memory_info.vms / (1024**2),
            "name": process.name(),
            "pid": process.pid,
        }

    def get_ollama_processes(self) -> List[Dict[str, Any]]:
        """Get all Ollama-related processes and their memory usage"""
        ollama_processes = []
        for proc in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
            try:
                if "ollama" in proc.info["name"].lower():
                    memory_info = proc.memory_info()
                    ollama_processes.append(
                        {
                            "pid": proc.pid,
                            "name": proc.info["name"],
                            "rss_mb": memory_info.rss / (1024**2),
                            "vms_mb": memory_info.vms / (1024**2),
                            "cpu_percent": proc.info["cpu_percent"],
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return ollama_processes

    def monitor_memory_usage(self, duration: int = 60, interval: int = 5):
        """Monitor memory usage over time"""
        print(f"🔍 Monitoring memory usage for {duration} seconds...")
        self.monitoring = True
        start_time = time.time()

        while self.monitoring and (time.time() - start_time) < duration:
            timestamp = datetime.now().isoformat()

            # System memory
            system_mem = self.get_system_memory()

            # Current process memory
            current_proc = self.get_process_memory()

            # Ollama processes
            ollama_procs = self.get_ollama_processes()

            # Store data
            self.data.append(
                {
                    "timestamp": timestamp,
                    "system_memory": system_mem,
                    "current_process": current_proc,
                    "ollama_processes": ollama_procs,
                }
            )

            # Print current status
            print(f"⏱️  {timestamp}")
            print(
                f"   System RAM: {system_mem['used_gb']:.1f}GB / {system_mem['total_gb']:.1f}GB ({system_mem['percent']:.1f}%)"
            )
            print(f"   Current process: {current_proc['rss_mb']:.1f}MB")
            if ollama_procs:
                total_ollama = sum(p["rss_mb"] for p in ollama_procs)
                print(f"   Ollama processes: {total_ollama:.1f}MB total")
            print()

            time.sleep(interval)

        self.monitoring = False
        return self.data

    def get_optimal_settings(self) -> Dict[str, Any]:
        """Calculate optimal settings based on current system"""
        system_mem = self.get_system_memory()
        ollama_procs = self.get_ollama_processes()

        # Calculate available memory
        total_ram_gb = system_mem["total_gb"]
        available_ram_gb = system_mem["available_gb"]

        # Ollama memory usage
        ollama_memory_mb = sum(p["rss_mb"] for p in ollama_procs)
        ollama_memory_gb = ollama_memory_mb / 1024

        # Calculate optimal parallel workers
        # Each Qwen3:8b process needs ~4-5GB
        # Reserve 2GB for system
        usable_ram = total_ram_gb - 2  # Reserve 2GB for system
        max_workers = int(usable_ram / 4)  # 4GB per worker
        optimal_workers = min(max_workers, 3)  # Cap at 3 for stability

        # Memory per process estimation
        memory_per_process_gb = 4  # Qwen3:8b typically uses 4GB

        return {
            "total_ram_gb": total_ram_gb,
            "available_ram_gb": available_ram_gb,
            "ollama_memory_gb": ollama_memory_gb,
            "optimal_parallel_workers": optimal_workers,
            "max_parallel_workers": max_workers,
            "memory_per_process_gb": memory_per_process_gb,
            "recommended_batch_size": 1,  # Keep at 1 for AI processing
            "system_reserve_gb": 2,
        }

    def generate_report(self) -> str:
        """Generate memory usage report"""
        if not self.data:
            return "No monitoring data available"

        # Calculate averages
        avg_system_used = sum(d["system_memory"]["used_gb"] for d in self.data) / len(
            self.data
        )
        avg_system_percent = sum(
            d["system_memory"]["percent"] for d in self.data
        ) / len(self.data)
        avg_current_proc = sum(d["current_process"]["rss_mb"] for d in self.data) / len(
            self.data
        )

        # Ollama memory
        ollama_totals = []
        for d in self.data:
            total = sum(p["rss_mb"] for p in d["ollama_processes"])
            ollama_totals.append(total)
        avg_ollama = sum(ollama_totals) / len(ollama_totals) if ollama_totals else 0

        report = f"""
📊 MEMORY USAGE REPORT
=====================
Monitoring Duration: {len(self.data) * 5} seconds
Data Points: {len(self.data)}

💻 SYSTEM MEMORY
- Average Used: {avg_system_used:.1f}GB
- Average Usage: {avg_system_percent:.1f}%
- Peak Usage: {max(d["system_memory"]["percent"] for d in self.data):.1f}%

🐍 PYTHON PROCESS
- Average Memory: {avg_current_proc:.1f}MB
- Peak Memory: {max(d["current_process"]["rss_mb"] for d in self.data):.1f}MB

🤖 OLLAMA PROCESSES
- Average Memory: {avg_ollama:.1f}MB
- Peak Memory: {max(ollama_totals):.1f}MB

🎯 OPTIMAL SETTINGS
"""

        optimal = self.get_optimal_settings()
        report += f"""
- Recommended Parallel Workers: {optimal["optimal_parallel_workers"]}
- Max Parallel Workers: {optimal["max_parallel_workers"]}
- Memory per Process: {optimal["memory_per_process_gb"]}GB
- Recommended Batch Size: {optimal["recommended_batch_size"]}
- System Reserve: {optimal["system_reserve_gb"]}GB
"""

        return report


def main():
    """Main function for memory monitoring"""
    monitor = MemoryMonitor()

    print("🔍 Enhanced Obsidian Auto-Linker - Memory Monitor")
    print("=" * 60)

    # Get current system status
    system_mem = monitor.get_system_memory()
    ollama_procs = monitor.get_ollama_processes()
    optimal = monitor.get_optimal_settings()

    print("📊 CURRENT SYSTEM STATUS")
    print(f"Total RAM: {system_mem['total_gb']:.1f}GB")
    print(f"Available RAM: {system_mem['available_gb']:.1f}GB")
    print(f"Used RAM: {system_mem['used_gb']:.1f}GB ({system_mem['percent']:.1f}%)")

    if ollama_procs:
        total_ollama = sum(p["rss_mb"] for p in ollama_procs)
        print(f"Ollama Memory: {total_ollama:.1f}MB")

    print(f"\n🎯 OPTIMAL SETTINGS FOR YOUR SYSTEM")
    print(f"Recommended Parallel Workers: {optimal['optimal_parallel_workers']}")
    print(f"Max Parallel Workers: {optimal['max_parallel_workers']}")
    print(f"Memory per Process: {optimal['memory_per_process_gb']}GB")
    print(f"Recommended Batch Size: {optimal['recommended_batch_size']}")

    # Ask if user wants to monitor
    try:
        choice = input("\n🔍 Start memory monitoring? (y/N): ").strip().lower()
        if choice == "y":
            duration = int(input("Duration in seconds (default 60): ") or "60")
            monitor.monitor_memory_usage(duration)
            print(monitor.generate_report())
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")


if __name__ == "__main__":
    main()
