#!/usr/bin/env python3
"""
Quick memory check for Enhanced Obsidian Auto-Linker
Shows current RAM usage and optimal settings
"""

import psutil
import os

def check_memory():
    """Check current memory usage and provide recommendations"""
    print("💻 MEMORY USAGE CHECK")
    print("=" * 40)
    
    # System memory
    memory = psutil.virtual_memory()
    print(f"Total RAM: {memory.total / (1024**3):.1f}GB")
    print(f"Available RAM: {memory.available / (1024**3):.1f}GB")
    print(f"Used RAM: {memory.used / (1024**3):.1f}GB ({memory.percent:.1f}%)")
    
    # Ollama processes
    ollama_memory = 0
    ollama_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            if 'ollama' in proc.info['name'].lower():
                mem = proc.memory_info()
                ollama_memory += mem.rss / (1024**2)
                ollama_count += 1
        except:
            pass
    
    print(f"\n🤖 Ollama Memory: {ollama_memory:.1f}MB ({ollama_count} processes)")
    
    # Calculate optimal settings
    total_ram_gb = memory.total / (1024**3)
    available_ram_gb = memory.available / (1024**3)
    
    # Reserve 2GB for system
    usable_ram = total_ram_gb - 2
    # Each Qwen3:8b process needs ~4GB
    max_workers = int(usable_ram / 4)
    optimal_workers = min(max_workers, 3)
    
    print(f"\n🎯 RECOMMENDED SETTINGS:")
    print(f"Parallel workers: {optimal_workers}")
    print(f"Batch size: 1 (keep for AI processing)")
    print(f"Max memory usage: 12GB")
    
    # Memory status
    if memory.percent > 90:
        print(f"\n⚠️  WARNING: High memory usage ({memory.percent:.1f}%)")
        print("Consider reducing parallel_workers or closing other applications")
    elif memory.percent > 80:
        print(f"\n⚠️  CAUTION: Moderate memory usage ({memory.percent:.1f}%)")
        print("Monitor memory usage during processing")
    else:
        print(f"\n✅ GOOD: Memory usage is healthy ({memory.percent:.1f}%)")
    
    return {
        'total_ram_gb': total_ram_gb,
        'available_ram_gb': available_ram_gb,
        'ollama_memory_mb': ollama_memory,
        'optimal_workers': optimal_workers,
        'memory_percent': memory.percent
    }

if __name__ == "__main__":
    check_memory()

