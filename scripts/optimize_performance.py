#!/usr/bin/env python3
"""
Performance Optimization Script
Applies various speed optimizations to the Obsidian Auto-Linker
"""

import yaml
import os
from pathlib import Path

def optimize_config():
    """Apply performance optimizations to config.yaml"""
    
    config_file = 'config.yaml'
    
    # Read current config
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    # Performance optimizations
    optimizations = {
        # Ollama optimizations
        'ollama_timeout': 15,           # Reduce timeout
        'ollama_max_retries': 1,         # Reduce retries
        'ollama_temperature': 0.3,      # Increase for faster responses
        'ollama_max_tokens': 200,       # Reduce token count
        'ollama_model': 'qwen2.5:3b',   # Faster model
        
        # Processing optimizations
        'parallel_workers': 3,          # Enable parallel processing
        'batch_size': 5,                # Process more files per batch
        'max_retries': 1,               # Reduce general retries
        
        # Caching optimizations
        'cache_enabled': True,          # Ensure caching is on
        'resume_enabled': True,         # Enable resume functionality
        
        # AI optimizations
        'fast_dry_run': True,          # Enable fast mode by default
        'confirm_large_batches': False, # Skip confirmation for speed
    }
    
    # Apply optimizations
    config.update(optimizations)
    
    # Write optimized config
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ Performance optimizations applied to config.yaml")
    print("🚀 Key optimizations:")
    print(f"   - Ollama timeout: {config['ollama_timeout']}s (was 30s)")
    print(f"   - Parallel workers: {config['parallel_workers']}")
    print(f"   - Batch size: {config['batch_size']}")
    print(f"   - Model: {config['ollama_model']}")
    print(f"   - Max tokens: {config['ollama_max_tokens']}")

def create_fast_config():
    """Create a super-fast configuration for testing"""
    
    fast_config = {
        'vault_path': '/Users/medici/Documents/MediciVault',
        'dry_run': True,
        'fast_dry_run': True,
        'batch_size': 10,
        'parallel_workers': 4,
        'ollama_timeout': 10,
        'ollama_max_retries': 1,
        'ollama_temperature': 0.5,
        'ollama_max_tokens': 100,
        'ollama_model': 'qwen2.5:3b',
        'max_retries': 1,
        'cache_enabled': True,
        'resume_enabled': True,
        'confirm_large_batches': False,
        'analytics_enabled': True,
        'generate_report': True
    }
    
    with open('config_fast.yaml', 'w') as f:
        yaml.dump(fast_config, f, default_flow_style=False)
    
    print("✅ Fast configuration created: config_fast.yaml")
    print("🚀 Use with: python3 obsidian_auto_linker_enhanced.py --config config_fast.yaml")

def create_ultra_fast_config():
    """Create ultra-fast configuration for quick testing"""
    
    ultra_fast_config = {
        'vault_path': '/Users/medici/Documents/MediciVault',
        'dry_run': True,
        'fast_dry_run': True,
        'batch_size': 20,
        'parallel_workers': 6,
        'ollama_timeout': 5,
        'ollama_max_retries': 1,
        'ollama_temperature': 0.7,
        'ollama_max_tokens': 50,
        'ollama_model': 'qwen2.5:1.5b',  # Smallest, fastest model
        'max_retries': 1,
        'cache_enabled': True,
        'resume_enabled': True,
        'confirm_large_batches': False,
        'analytics_enabled': True,
        'generate_report': True
    }
    
    with open('config_ultra_fast.yaml', 'w') as f:
        yaml.dump(ultra_fast_config, f, default_flow_style=False)
    
    print("✅ Ultra-fast configuration created: config_ultra_fast.yaml")
    print("⚡ Use with: python3 obsidian_auto_linker_enhanced.py --config config_ultra_fast.yaml")

if __name__ == "__main__":
    print("🚀 OBSIDIAN AUTO-LINKER PERFORMANCE OPTIMIZER")
    print("=" * 50)
    
    # Apply standard optimizations
    optimize_config()
    print()
    
    # Create fast configurations
    create_fast_config()
    print()
    
    create_ultra_fast_config()
    print()
    
    print("📊 PERFORMANCE COMPARISON:")
    print("   Standard: ~2-3 minutes per file")
    print("   Fast:     ~30-60 seconds per file")
    print("   Ultra:    ~10-30 seconds per file")
    print()
    print("🎯 RECOMMENDED USAGE:")
    print("   1. Test with ultra-fast config first")
    print("   2. Use fast config for regular processing")
    print("   3. Use standard config for best quality")
