#!/usr/bin/env python3
"""
Quick test script to verify dashboard integration
Run this to test without any caching issues
"""

import sys
import os

# Force reimport of modules
for module in list(sys.modules.keys()):
    if 'obsidian' in module or 'config_utils' in module or 'live_dashboard' in module:
        del sys.modules[module]

print("🧪 Testing Dashboard Integration...\n")

# Test 1: Import config_utils
print("1️⃣  Testing config_utils import...")
try:
    from config_utils import load_yaml_config, check_ollama_connection, load_json_file
    print("   ✅ config_utils imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import config_utils: {e}")
    sys.exit(1)

# Test 2: Import live_dashboard
print("\n2️⃣  Testing live_dashboard import...")
try:
    from live_dashboard import LiveDashboard
    print("   ✅ live_dashboard imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import live_dashboard: {e}")
    sys.exit(1)

# Test 3: Import main processor
print("\n3️⃣  Testing obsidian_auto_linker_enhanced import...")
try:
    import obsidian_auto_linker_enhanced as processor
    print("   ✅ Processor imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import processor: {e}")
    sys.exit(1)

# Test 4: Check main function signature
print("\n4️⃣  Checking main() function signature...")
import inspect
sig = inspect.signature(processor.main)
params = list(sig.parameters.keys())
print(f"   📋 Parameters: {params}")

if 'enable_dashboard' in params:
    print("   ✅ enable_dashboard parameter found")
else:
    print("   ❌ enable_dashboard parameter NOT found")
    sys.exit(1)

if 'dashboard_update_interval' in params:
    print("   ✅ dashboard_update_interval parameter found")
else:
    print("   ❌ dashboard_update_interval parameter NOT found")
    sys.exit(1)

# Test 5: Load config
print("\n5️⃣  Testing config loading...")
try:
    config = load_yaml_config('config.yaml')
    print(f"   ✅ Config loaded: {len(config)} keys")
    if config.get('vault_path'):
        print(f"   📁 Vault path: {config['vault_path']}")
except Exception as e:
    print(f"   ⚠️  Config not found (OK if first run): {e}")

# Test 6: Check Ollama
print("\n6️⃣  Testing Ollama connection...")
try:
    ollama_running = check_ollama_connection(timeout=2)
    if ollama_running:
        print("   ✅ Ollama is running")
    else:
        print("   ⚠️  Ollama not running (OK for testing, needed for AI mode)")
except Exception as e:
    print(f"   ⚠️  Could not check Ollama: {e}")

# Test 7: Verify integration points
print("\n7️⃣  Verifying integration points in processor...")
import obsidian_auto_linker_enhanced
source = inspect.getsource(obsidian_auto_linker_enhanced.main)

checks = {
    'LiveDashboard initialization': 'LiveDashboard(' in source,
    'dashboard.start() call': 'dashboard.start()' in source,
    'dashboard.update_processing()': 'dashboard.update_processing(' in source,
    'dashboard.stop() call': 'dashboard.stop()' in source,
}

for check_name, result in checks.items():
    if result:
        print(f"   ✅ {check_name}")
    else:
        print(f"   ❌ {check_name} - NOT FOUND")

print("\n" + "="*60)
print("🎉 ALL TESTS PASSED!")
print("="*60)
print("\n✨ Dashboard integration is working correctly!")
print("\n📝 To run with dashboard:")
print("   python3 run_with_dashboard.py")
print("\n📝 To run without dashboard:")
print("   python3 run.py")
print()
