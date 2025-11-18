# 📦 Archived Experimental Code

This directory contains experimental and duplicate scripts that were archived during the project cleanup on 2025-11-15.

## Why These Files Were Archived

These files were experimental implementations or duplicates created during development. The canonical implementations are in the main project directory.

---

## 📂 experimental_runners/

**Purpose**: Legacy wrappers for specialized runs that pre-date the unified launcher.

### Specialized Runners (still available)

- `run_extended_timeout.py` - Extended timeout configuration
- `run_ultra_detailed.py` - Ultra-detailed analytics mode
- `run_detailed_analytics.py` - Detailed analytics runner

**Status**: Functionality has been merged into `run.py` via configuration options. These scripts are kept only as reference wrappers.

**Canonical Implementation**: Use `run.py` (interactive) or `run_with_dashboard.py` (with monitoring)

### Removed Parallel Prototypes (2025-11-26)

Legacy parallel runner prototypes were deleted to reduce bloat and avoid confusion. Parallel execution is now handled directly in
`obsidian_auto_linker_enhanced.py` via configuration flags (`parallel_processing_enabled`, `parallel_workers`).

---

## 📂 experimental_tests/

**Purpose**: Test files that were in root directory during development

- `test_parallel_simple.py` - Simple parallel processing test
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

- **Files Archived**: 3 specialized runners + 2 experimental tests (reference only)
- **Archive Date**: 2025-11-15 (parallel prototypes removed 2025-11-26)
- **Disk Space Saved**: Significant after deleting legacy parallel prototypes (multiple hundred KB)
- **Maintainability Improvement**: Huge (root directory cleanup, reduced parallel runner confusion)

---

## 🗑️ Scheduled for Deletion

**Date**: 2026-01-15 (2 months from archive)

**Criteria for Earlier Deletion**:
- Parallel processing implemented and tested
- All unique features verified as merged
- No references in documentation

---

**Questions?** See [COMPREHENSIVE_REVIEW.md](../COMPREHENSIVE_REVIEW.md) section on "Code Organization Crisis"
