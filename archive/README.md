# 📦 Archived Experimental Code

This directory contains experimental and duplicate scripts that were archived during the project cleanup on 2025-11-15.

## Why These Files Were Archived

These files were experimental implementations or duplicates created during development. The canonical implementations are in the main project directory.

---

## 📂 experimental_runners/

**Purpose**: Experimental parallel processing and timeout handling implementations

### Parallel Processing Variants

- `run_parallel.py` - Early parallel processing attempt
- `run_parallel_real.py` - Second iteration
- `run_parallel_fixed.py` - Bug fix attempt
- `run_parallel_fast.py` - Performance optimization attempt
- `run_parallel_timeout.py` - Timeout handling variant
- `run_parallel_working.py` - "Working" version (outdated)
- `run_parallel_optimized.sh` - Shell script wrapper

**Status**: Parallel processing is planned but not yet implemented in the main codebase. See PHASE_2_3_STATUS.md for implementation roadmap.

**Canonical Implementation**: Use `run.py` (interactive) or `run_with_dashboard.py` (with monitoring)

### Specialized Runners

- `run_extended_timeout.py` - Extended timeout configuration
- `run_ultra_detailed.py` - Ultra-detailed analytics mode
- `run_detailed_analytics.py` - Detailed analytics runner

**Status**: Functionality merged into `run.py` with config options

**Canonical Implementation**: Use `run.py` with appropriate config.yaml settings

---

## 📂 experimental_tests/

**Purpose**: Test files that were in root directory during development

- `test_parallel_simple.py` - Simple parallel processing test
- `test_sequential_2_files.py` - Sequential processing test
- `test_integration.py` - Integration test (may be duplicate)

**Status**: Experimental tests, may have duplicates in tests/ directory

**Canonical Tests**: See tests/ directory for maintained test suite

---

## 🔄 Can These Be Deleted?

**Short Answer**: Not yet - preserve for reference

**Recommendation**: Keep archived for 1-2 months while the canonical implementations stabilize, then delete if no longer needed.

**Before Deleting**:
- ✅ Verify parallel processing is implemented in main codebase
- ✅ Verify all unique functionality is merged
- ✅ Ensure no config files reference these scripts

---

## 📝 Restoration Instructions

If you need to restore any of these files:

```bash
# From the archive directory
git mv archive/experimental_runners/filename.py ./
git commit -m "Restore filename.py from archive"
```

---

## 📊 Archive Statistics

- **Files Archived**: 10 scripts
- **Archive Date**: 2025-11-15
- **Disk Space Saved**: ~150KB
- **Maintainability Improvement**: Huge (root directory cleanup)

---

## 🗑️ Scheduled for Deletion

**Date**: 2026-01-15 (2 months from archive)

**Criteria for Earlier Deletion**:
- Parallel processing implemented and tested
- All unique features verified as merged
- No references in documentation

---

**Questions?** See [COMPREHENSIVE_REVIEW.md](../COMPREHENSIVE_REVIEW.md) section on "Code Organization Crisis"
