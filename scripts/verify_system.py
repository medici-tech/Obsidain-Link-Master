#!/usr/bin/env python3
"""
System Verification Script
Checks that all components are ready for production use
"""

import os
import sys
import yaml
import requests
from pathlib import Path

def check_file_structure():
    """Check that all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        'config.yaml',
        'obsidian_auto_linker_enhanced.py',
        'enhanced_analytics.py',
        'ultra_detailed_analytics.py'
    ]
    
    required_dirs = [
        'configs',
        'scripts',
        'docs',
        'reports',
        'backups'
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
            all_good = False
    
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"  ✅ {dir}/")
        else:
            print(f"  ❌ {dir}/ - MISSING!")
            all_good = False
    
    return all_good

def check_imports():
    """Check that all imports work"""
    print("\n🔍 Checking imports...")
    
    try:
        import yaml
        print("  ✅ yaml")
    except ImportError:
        print("  ❌ yaml - MISSING!")
        return False
    
    try:
        import requests
        print("  ✅ requests")
    except ImportError:
        print("  ❌ requests - MISSING!")
        return False
    
    try:
        import webbrowser
        print("  ✅ webbrowser")
    except ImportError:
        print("  ❌ webbrowser - MISSING!")
        return False
    
    return True

def check_config():
    """Check configuration file"""
    print("\n🔍 Checking configuration...")
    
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['vault_path', 'ollama_model', 'ollama_timeout']
        all_good = True
        
        for key in required_keys:
            if key in config:
                print(f"  ✅ {key}: {config[key]}")
            else:
                print(f"  ❌ {key} - MISSING!")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False

def check_ollama_connection():
    """Check Ollama connection"""
    print("\n🔍 Checking Ollama connection...")
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("  ✅ Ollama connection successful")
            return True
        else:
            print(f"  ❌ Ollama connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Ollama connection error: {e}")
        return False

def check_models():
    """Check available models"""
    print("\n🔍 Checking available models...")
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            
            print(f"  📊 Available models: {len(models)}")
            for model in models:
                print(f"    🤖 {model}")
            
            # Check for required models
            required_models = ['qwen3:8b', 'qwen2.5:3b']
            for model in required_models:
                if model in models:
                    print(f"  ✅ {model} - Available")
                else:
                    print(f"  ❌ {model} - MISSING!")
                    return False
            
            return True
        else:
            print(f"  ❌ Failed to get models: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Model check error: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 OBSIDIAN AUTO-LINKER SYSTEM VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Imports", check_imports),
        ("Configuration", check_config),
        ("Ollama Connection", check_ollama_connection),
        ("Available Models", check_models)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION RESULTS")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - SYSTEM READY FOR PRODUCTION!")
        print("🚀 You can now run: python3 obsidian_auto_linker_enhanced.py")
    else:
        print("⚠️  SOME CHECKS FAILED - PLEASE FIX ISSUES BEFORE RUNNING")
        print("🔧 Check the errors above and resolve them")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
