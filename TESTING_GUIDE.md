# Complete Testing Guide
**Obsidian Auto-Linker - v1.1.0**

---

## Quick Start Testing (5 Minutes)

### 1. Verify Installation
```bash
cd /home/user/Obsidain-Link-Master

# Check Python version (need 3.9+ because of dashboard dependencies)
python3 --version

# Install dependencies
pip3 install -r requirements.txt

# Verify all imports work
python3 -c "
import config_utils
import config_schema
import logger_config
import live_dashboard
import obsidian_auto_linker_enhanced
print('✅ All modules imported successfully')
"
```

### 2. Run Test Suite
```bash
# Run all 75 tests
pytest

# Expected output:
# ====== 75 passed in 0.6s ======
```

### 3. Test Dashboard
```bash
# Start interactive runner
python3 run.py

# Follow prompts:
# 1. Enter vault path (use /tmp for testing)
# 2. Choose ordering: 1 (recent)
# 3. Choose mode: 1 (Fast Dry Run)
# 4. Choose batch: 1 (one file)
# 5. Enable dashboard: 1 (yes)
# 6. Confirm: y

# Should see live dashboard with panels
```

---

## Comprehensive Testing (30 Minutes)

### Test 1: Configuration Validation ✅

**What it tests**: Pydantic schema validation, type safety, security

```bash
# Test 1a: Valid configuration
python3 << 'EOF'
from config_schema import ObsidianConfig

config = ObsidianConfig(
    vault_path='/tmp/test_vault',
    dry_run=True,
    batch_size=5,
    file_ordering='recent',
    ollama_model='qwen2.5:3b'
)

print('✅ Valid config created')
print(f'   Vault: {config.vault_path}')
print(f'   Batch: {config.batch_size}')
print(f'   Model: {config.ollama_model}')
EOF

# Expected: ✅ Valid config created

# Test 1b: Invalid configurations (should reject)
python3 << 'EOF'
from config_schema import ObsidianConfig
from pydantic import ValidationError

# Test invalid file_ordering
try:
    config = ObsidianConfig(
        vault_path='/tmp',
        file_ordering='invalid_option'
    )
    print('❌ Should have rejected invalid file_ordering')
except ValidationError as e:
    print('✅ Correctly rejected invalid file_ordering')

# Test invalid batch_size
try:
    config = ObsidianConfig(
        vault_path='/tmp',
        batch_size=0  # Too low
    )
    print('❌ Should have rejected batch_size=0')
except ValidationError as e:
    print('✅ Correctly rejected batch_size=0')

# Test fast_dry_run without dry_run
try:
    config = ObsidianConfig(
        vault_path='/tmp',
        fast_dry_run=True,
        dry_run=False
    )
    print('❌ Should have rejected incompatible modes')
except ValidationError as e:
    print('✅ Correctly rejected incompatible modes')
EOF

# Expected: All 3 validations should pass (reject invalid configs)

# Test 1c: YAML file loading
cat > /tmp/test_config.yaml << 'EOF'
vault_path: /tmp/test_vault
dry_run: true
batch_size: 10
file_ordering: size
ollama_model: qwen2.5:3b
ollama_timeout: 30
EOF

python3 << 'EOF'
from config_schema import ObsidianConfig

config = ObsidianConfig.from_yaml_file('/tmp/test_config.yaml')
print('✅ YAML config loaded successfully')
print(f'   Batch size: {config.batch_size}')
print(f'   Ordering: {config.file_ordering}')
print(f'   Timeout: {config.ollama_timeout}s')

# Save back to file
config.save_to_yaml_file('/tmp/test_config_output.yaml')
print('✅ Config saved to YAML')
EOF

# Verify saved file
cat /tmp/test_config_output.yaml
```

**Expected Results**:
- ✅ Valid configs work
- ✅ Invalid configs are rejected with helpful errors
- ✅ YAML loading/saving works
- ✅ Type validation prevents mistakes

---

### Test 2: Path Security Validation 🔒

**What it tests**: Protection against path injection, system directory access

```bash
python3 << 'EOF'
from config_utils import validate_vault_path

print("\n🔒 Path Security Tests:\n")

# Test cases: (path, expected_result, description)
tests = [
    # Valid paths
    ('/tmp', True, 'Valid: /tmp directory'),
    ('/home/user/Documents', True, 'Valid: user directory'),

    # Security: System directories (should reject)
    ('/etc', False, 'SECURITY: System config directory'),
    ('/sys', False, 'SECURITY: System directory'),
    ('/proc', False, 'SECURITY: Process directory'),
    ('/dev', False, 'SECURITY: Device directory'),
    ('/bin', False, 'SECURITY: Binary directory'),

    # Security: Root directory (should reject)
    ('/', False, 'SECURITY: Root directory'),

    # Security: Null byte injection (should reject)
    ('/tmp/vault\x00/etc/passwd', False, 'SECURITY: Null byte injection'),

    # Edge cases
    ('', False, 'Empty path'),
    ('~/Documents', True, 'Tilde expansion'),
]

for path, expected, description in tests:
    result = validate_vault_path(path, must_exist=False)
    status = '✅' if result == expected else '❌'
    print(f'{status} {description}')
    if result != expected:
        print(f'   FAILED: Expected {expected}, got {result}')
    print()
EOF
```

**Expected Results**:
- ✅ All valid paths accepted
- ✅ All system directories rejected
- ✅ Null byte injection blocked
- ✅ Root directory blocked

---

### Test 3: Dashboard Integration 📊

**What it tests**: Live dashboard, metrics tracking, update interval

```bash
# Test 3a: Dashboard initialization
python3 << 'EOF'
from live_dashboard import LiveDashboard

dashboard = LiveDashboard(update_interval=15)

print('✅ Dashboard created')
print(f'   Update interval: {dashboard.update_interval}s')
print(f'   Running: {dashboard.running}')
print(f'   Stats initialized: {len(dashboard.stats)} metrics')

# Check key metrics
assert dashboard.stats['processed_files'] == 0
assert dashboard.stats['total_files'] == 0
assert dashboard.stats['ai_requests'] == 0
print('✅ Metrics initialized to zero')
EOF

# Test 3b: Dashboard with run.py
echo "Testing dashboard with run.py..."
echo "This is an interactive test - follow the prompts"

python3 run.py

# When prompted, enter:
# Vault path: /tmp
# File ordering: 1 (recent)
# Processing mode: 1 (Fast Dry Run)
# Batch size: 1
# Dashboard: 1 (Enable)
# Confirm: y

# Verify you see:
# - Dashboard panels appear
# - Updates every 15 seconds
# - File counts tracked
# - Resource usage shown
```

**Expected Results**:
- ✅ Dashboard initializes without errors
- ✅ Update interval is 15 seconds (not 30)
- ✅ Metrics start at zero
- ✅ Dashboard displays during processing

---

### Test 4: Run All Pytest Tests 🧪

**What it tests**: All modules, integration, edge cases

```bash
# Test 4a: Run full suite
pytest -v

# Expected: 75 passed

# Test 4b: Run with coverage
pytest --cov --cov-report=term-missing

# Expected coverage:
# config_utils.py:     90%+
# config_schema.py:    85%+
# logger_config.py:    80%+

# Test 4c: Run specific test modules
echo "\n=== Testing config_utils ==="
pytest tests/test_config_utils.py -v

# Expected: 28 passed

echo "\n=== Testing config_schema ==="
pytest tests/test_config_schema.py -v

# Expected: 26 passed

echo "\n=== Testing logger_config ==="
pytest tests/test_logger_config.py -v

# Expected: 10 passed

echo "\n=== Testing integration ==="
pytest tests/test_integration.py -v

# Expected: 11 passed

# Test 4d: Check for any warnings
pytest -v --strict-warnings

# Expected: No warnings, 75 passed
```

**Expected Results**:
- ✅ All 75 tests pass
- ✅ No test failures
- ✅ Coverage > 80% for core modules
- ✅ No warnings

---

### Test 5: Integration with Real Workflow 🚀

**What it tests**: End-to-end processing with dashboard

**⚠️ IMPORTANT**: This test creates files. Use a test vault or backup first!

```bash
# Step 1: Create test vault
mkdir -p /tmp/test_vault
cd /tmp/test_vault

# Create sample markdown files
cat > note1.md << 'EOF'
# Test Note 1

This is a test note about Python programming.
It discusses functions, classes, and modules.
EOF

cat > note2.md << 'EOF'
# Test Note 2

This note covers data structures.
Lists, dictionaries, and sets are important.
EOF

cat > note3.md << 'EOF'
# Test Note 3

Machine learning basics.
Neural networks and deep learning.
EOF

# Step 2: Run with Fast Dry Run
cd /home/user/Obsidain-Link-Master
python3 run.py

# Enter when prompted:
# Vault: /tmp/test_vault
# Ordering: 1 (recent)
# Mode: 1 (Fast Dry Run)
# Batch: 1
# Dashboard: 1 (Enable)
# Confirm: y

# Step 3: Verify results
echo "\n=== Checking results ==="

# Should see:
# - Dashboard appeared
# - Files Scanned: 3
# - Files Processed: 3 (or fewer)
# - No errors
# - Process completed

# Step 4: Check logs
tail -20 obsidian_linker.log

# Should show:
# - "Found 3 markdown files"
# - Processing messages
# - No ERROR level messages

# Step 5: Cleanup
rm -rf /tmp/test_vault
```

**Expected Results**:
- ✅ 3 files discovered
- ✅ Dashboard shows file counts
- ✅ Processing completes without errors
- ✅ Logs show activity
- ✅ No crashes or exceptions

---

## Advanced Testing (Optional)

### Memory & Performance Testing

```bash
# Test with larger batch
python3 << 'EOF'
from live_dashboard import LiveDashboard
import time

dashboard = LiveDashboard(update_interval=15)
dashboard.start()

# Simulate processing
for i in range(100):
    dashboard.stats['processed_files'] = i
    dashboard.stats['total_files'] = 100
    time.sleep(0.1)

dashboard.stop()
print('✅ Dashboard handled 100 updates')
EOF
```

### Stress Test Configuration Validation

```bash
# Test 1000 config validations
python3 << 'EOF'
from config_schema import ObsidianConfig
import time

start = time.time()
for i in range(1000):
    config = ObsidianConfig(
        vault_path=f'/tmp/vault_{i}',
        batch_size=i % 100 + 1,
        file_ordering=['recent', 'size', 'random', 'alphabetical'][i % 4]
    )

elapsed = time.time() - start
print(f'✅ 1000 validations in {elapsed:.2f}s')
print(f'   Average: {elapsed/1000*1000:.2f}ms per validation')
EOF
```

---

## Continuous Integration Testing

### GitHub Actions (Future)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Troubleshooting Tests

### Tests Fail: Import Errors

```bash
# Solution: Install dependencies
pip3 install -r requirements.txt

# Verify installations
pip3 list | grep -E "pytest|pydantic|rich|psutil|pyyaml"
```

### Tests Fail: Permission Errors

```bash
# Solution: Check file permissions
chmod +x run.py run_with_dashboard.py

# Check directory permissions
ls -la /home/user/Obsidain-Link-Master
```

### Dashboard Doesn't Appear

```bash
# Solution: Check Rich library
pip3 install --upgrade rich

# Test Rich directly
python3 -c "from rich.console import Console; Console().print('[bold green]Rich works![/bold green]')"
```

### Config Validation Fails

```bash
# Solution: Check Pydantic version
pip3 show pydantic

# Must be >= 2.0.0
pip3 install --upgrade 'pydantic>=2.0.0'
```

---

## Test Results Checklist

After running all tests, verify:

- [ ] ✅ All 75 pytest tests pass
- [ ] ✅ No warnings or errors in test output
- [ ] ✅ Dashboard appears when enabled in run.py
- [ ] ✅ Dashboard updates every 15 seconds (not 30)
- [ ] ✅ File counts (scanned/processed) display correctly
- [ ] ✅ Config validation rejects invalid inputs
- [ ] ✅ Path security blocks system directories
- [ ] ✅ Path security blocks null byte injection
- [ ] ✅ YAML config loading/saving works
- [ ] ✅ No import errors for any module
- [ ] ✅ Logs written to obsidian_linker.log
- [ ] ✅ Resource summary shows at end of processing

---

## Next Steps After Testing

If all tests pass:
1. ✅ System is production-ready
2. ✅ Safe to use with real vault (with backups)
3. ✅ Dashboard provides real-time monitoring
4. ✅ Security validates all paths
5. ✅ Configuration prevents mistakes

If tests fail:
1. Note which test failed
2. Check the troubleshooting section
3. Verify dependencies are installed
4. Check Python version (need 3.9+)
5. Review error messages carefully

---

## Quick Test Commands Summary

```bash
# Run everything
pytest -v && python3 config_schema.py

# Test dashboard
python3 run.py  # Enable dashboard when prompted

# Test config validation
python3 -c "from config_schema import ObsidianConfig; config = ObsidianConfig(vault_path='/tmp'); print('✅ Works')"

# Test path security
python3 -c "from config_utils import validate_vault_path; print('System dir blocked:', not validate_vault_path('/etc', False))"

# Coverage report
pytest --cov --cov-report=html && open htmlcov/index.html
```

---

**Happy Testing! 🎉**

All features have been thoroughly tested and are ready for use.
