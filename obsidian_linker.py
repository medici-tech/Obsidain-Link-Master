#!/usr/bin/env python3
"""
Simple Obsidian Auto-Linker CLI
Process your Obsidian vault with local AI
"""

import os
import sys
import argparse
import yaml
import requests
from pathlib import Path

def check_ollama():
    """Check if Ollama is running and get available models"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return True, models
        else:
            return False, []
    except:
        return False, []

def load_config():
    """Load configuration from YAML file"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            return config if config is not None else {}
    except:
        return {}

def save_config(config):
    """Save configuration to YAML file"""
    try:
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        return True
    except:
        return False

def setup_config():
    """Interactive configuration setup"""
    print("🔧 Obsidian Auto-Linker Setup")
    print("=" * 40)
    
    config = load_config()
    
    # Vault path
    vault_path = input(f"📁 Vault path [{config.get('vault_path', '')}]: ").strip()
    if not vault_path:
        vault_path = config.get('vault_path', '')
    if not vault_path:
        print("❌ Vault path is required!")
        return False
    
    if not os.path.exists(vault_path):
        print(f"❌ Vault path does not exist: {vault_path}")
        return False
    
    # Check Ollama
    print("\n🔍 Checking Ollama...")
    ollama_running, models = check_ollama()
    if not ollama_running:
        print("❌ Ollama is not running!")
        print("   Please run: ollama serve")
        return False
    
    print(f"✅ Ollama is running with {len(models)} models")
    
    # Model selection
    if models:
        print("\n📋 Available models:")
        for i, model in enumerate(models, 1):
            print(f"   {i}. {model}")
        
        while True:
            try:
                choice = input(f"\n🤖 Select model [1-{len(models)}]: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(models):
                    selected_model = models[int(choice) - 1]
                    break
                else:
                    print("❌ Invalid choice")
            except KeyboardInterrupt:
                return False
    else:
        print("❌ No models found in Ollama")
        return False
    
    # Batch size
    batch_size = input(f"\n📦 Batch size [{config.get('batch_size', 5)}]: ").strip()
    if not batch_size:
        batch_size = config.get('batch_size', 5)
    else:
        try:
            batch_size = int(batch_size)
        except:
            batch_size = 5
    
    # Dry run
    dry_run = input(f"\n🔥 Dry run mode? (y/N) [{config.get('dry_run', True)}]: ").strip().lower()
    if dry_run == 'y':
        dry_run = True
    elif dry_run == 'n':
        dry_run = False
    else:
        dry_run = config.get('dry_run', True)
    
    # Save config
    config.update({
        'vault_path': vault_path,
        'ollama_model': selected_model,
        'batch_size': batch_size,
        'dry_run': dry_run
    })
    
    if save_config(config):
        print("\n✅ Configuration saved!")
        return True
    else:
        print("\n❌ Failed to save configuration")
        return False

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Obsidian Auto-Linker CLI')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    parser.add_argument('--models', action='store_true', help='Show available models')
    parser.add_argument('--run', action='store_true', help='Run processing')
    
    args = parser.parse_args()
    
    if args.setup:
        if setup_config():
            print("\n🚀 Setup complete! Run with --run to start processing")
        return
    
    if args.config:
        config = load_config()
        print("📋 Current Configuration:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        return
    
    if args.models:
        ollama_running, models = check_ollama()
        if ollama_running:
            print("📋 Available Models:")
            for model in models:
                print(f"   - {model}")
        else:
            print("❌ Ollama is not running")
        return
    
    if args.run:
        # Run the enhanced script
        print("🚀 Starting Obsidian Auto-Linker...")
        print("⚠️  Note: Local AI models are slow (2-3 minutes per file)")
        print("   This is normal - local processing takes time!")
        print()
        
        try:
            import subprocess
            subprocess.run([sys.executable, 'obsidian_auto_linker_enhanced.py'])
        except KeyboardInterrupt:
            print("\n👋 Processing stopped by user")
        return
    
    # No arguments - show help
    print("🚀 Obsidian Auto-Linker CLI")
    print("=" * 40)
    print()
    print("Usage:")
    print("  python3 obsidian_linker.py --setup    # Run setup wizard")
    print("  python3 obsidian_linker.py --config   # Show configuration")
    print("  python3 obsidian_linker.py --models   # Show available models")
    print("  python3 obsidian_linker.py --run      # Start processing")
    print()
    print("Quick start:")
    print("  1. python3 obsidian_linker.py --setup")
    print("  2. python3 obsidian_linker.py --run")

if __name__ == "__main__":
    main()
