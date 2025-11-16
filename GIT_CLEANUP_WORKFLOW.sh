#!/bin/bash
# Git Cleanup Workflow - Obsidian Auto-Linker Repository
# Generated: 2025-11-16
# Branch: claude/repo-analysis-refactor-01J39fKe8T531HiA5vBrGVRn

set -e  # Exit on error

echo "🔧 Starting Repository Cleanup and Refactoring"
echo "=============================================="
echo ""

# Check current branch
echo "📍 Step 1: Verify current branch"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "claude/repo-analysis-refactor-01J39fKe8T531HiA5vBrGVRn" ]; then
    echo "❌ ERROR: Not on expected branch"
    echo "   Current: $CURRENT_BRANCH"
    echo "   Expected: claude/repo-analysis-refactor-01J39fKe8T531HiA5vBrGVRn"
    exit 1
fi
echo "✅ On correct branch: $CURRENT_BRANCH"
echo ""

# Create backup
echo "💾 Step 2: Create safety backup"
git stash push -u -m "Pre-refactoring backup $(date +%Y%m%d_%H%M%S)"
git stash apply
echo "✅ Backup created (git stash list to view)"
echo ""

# Create archive directories
echo "📁 Step 3: Create archive directories"
mkdir -p archive/old_docs
mkdir -p tests/utilities
echo "✅ Directories created"
echo ""

# Priority 1: Delete broken file
echo "🗑️  Step 4: Delete broken file"
if [ -f "scripts/setup_ide.py" ]; then
    git rm scripts/setup_ide.py
    echo "✅ Deleted: scripts/setup_ide.py (1 byte, broken)"
else
    echo "ℹ️  File not found (may already be deleted)"
fi
echo ""

# Priority 1: Archive duplicate parallel implementation
echo "📦 Step 5: Archive duplicate parallel implementation"
if [ -f "obsidian_auto_linker_parallel.py" ]; then
    git mv obsidian_auto_linker_parallel.py archive/experimental_runners/
    echo "✅ Archived: obsidian_auto_linker_parallel.py"
else
    echo "ℹ️  File not found (may already be archived)"
fi

if [ -f "configs/config_parallel_timeout.yaml" ]; then
    git mv configs/config_parallel_timeout.yaml configs/deprecated/
    echo "✅ Deprecated: config_parallel_timeout.yaml"
else
    echo "ℹ️  File not found (may already be deprecated)"
fi
echo ""

# Priority 1: Move test utilities
echo "🔄 Step 6: Move test utilities to proper location"
if [ -f "scripts/test_confidence_threshold.py" ]; then
    git mv scripts/test_confidence_threshold.py tests/utilities/
    echo "✅ Moved: test_confidence_threshold.py → tests/utilities/"
else
    echo "ℹ️  File not found (may already be moved)"
fi

if [ -f "scripts/test_interactive.py" ]; then
    git mv scripts/test_interactive.py tests/utilities/
    echo "✅ Moved: test_interactive.py → tests/utilities/"
else
    echo "ℹ️  File not found (may already be moved)"
fi
echo ""

# Priority 1: Archive stale documentation
echo "📚 Step 7: Archive stale documentation"
for doc in "TONIGHT_TODO.md" "cleanup_plan.md" "REVIEW_SUMMARY.md"; do
    if [ -f "$doc" ]; then
        git mv "$doc" archive/old_docs/
        echo "✅ Archived: $doc"
    else
        echo "ℹ️  Not found: $doc"
    fi
done

# Archive docs/cleanup_*.md
if [ -d "docs" ]; then
    for doc in docs/cleanup_*.md; do
        if [ -f "$doc" ]; then
            git mv "$doc" archive/old_docs/
            echo "✅ Archived: $doc"
        fi
    done
fi
echo ""

# Create archive README
echo "📄 Step 8: Create archive documentation"
cat > archive/old_docs/README.md << 'EOF'
# Archived Documentation

**Archived**: 2025-11-16
**Reason**: Redundant, outdated, or session-specific documentation

## Session Documents
- `TONIGHT_TODO.md` - Session from 2025-11-14 (completed)

## Cleanup Documentation (Redundant)
- `cleanup_plan.md` - Superseded by PROJECT_TODO.md
- `REVIEW_SUMMARY.md` - Redundant with COMPREHENSIVE_REVIEW.md
- `cleanup_*.md` (from docs/) - Consolidated into CLEANUP_SUMMARY.md

## Canonical Sources

For current information, see:
- **Current tasks**: PROJECT_TODO.md
- **Cleanup history**: CLEANUP_SUMMARY.md
- **Project review**: COMPREHENSIVE_REVIEW.md

## Can These Be Deleted?

Yes, after 2 months (2026-01-16) if no longer referenced.
EOF

git add archive/old_docs/README.md
echo "✅ Created: archive/old_docs/README.md"
echo ""

# Update archive README
echo "📄 Step 9: Update main archive README"
cat >> archive/README.md << 'EOF'

## 📦 Second Archival - 2025-11-16

### obsidian_auto_linker_parallel.py

**Status**: Archived to `archive/experimental_runners/`

**Reason**: Duplicate implementation of parallel processing. The canonical version (`obsidian_auto_linker_enhanced.py`) already has infrastructure for parallel processing.

**Config**: Used `config_parallel_timeout.yaml` (also deprecated)

**Lines**: 745 lines

**Migration Path**: Use `obsidian_auto_linker_enhanced.py` with `parallel_workers > 1` in config

**Before Deleting**:
- ✅ Verify parallel processing works in main file
- ✅ Test with production config
- ✅ Ensure no unique functionality lost

**Scheduled Deletion**: 2026-03-16 (4 months)

---

## 📂 old_docs/

**Archived**: 2025-11-16

Session-specific and redundant documentation:
- TONIGHT_TODO.md (session 2025-11-14)
- cleanup_plan.md (deprecated)
- REVIEW_SUMMARY.md (redundant)
- cleanup_*.md (3 files from docs/)

**Canonical Sources**: PROJECT_TODO.md, CLEANUP_SUMMARY.md, COMPREHENSIVE_REVIEW.md
EOF

git add archive/README.md
echo "✅ Updated: archive/README.md"
echo ""

# Update tests README
echo "📄 Step 10: Update tests README"
cat >> tests/README.md << 'EOF'

## 🛠️ Test Utilities

Test utilities are in `tests/utilities/`:

### test_confidence_threshold.py
Tests for confidence threshold settings and their impact on link quality.

**Moved**: 2025-11-16 from scripts/ (better organization)

### test_interactive.py
Interactive testing utilities for manual testing and development.

**Moved**: 2025-11-16 from scripts/ (better organization)

### Usage

```bash
# Run confidence threshold tests
python tests/utilities/test_confidence_threshold.py

# Run interactive tests
python tests/utilities/test_interactive.py
```
EOF

git add tests/README.md
echo "✅ Updated: tests/README.md"
echo ""

# Commit Priority 1 changes
echo "💾 Step 11: Commit Priority 1 changes"
git add .
git commit -m "refactor: Priority 1 cleanup - remove duplicates and broken files

- Delete broken file (scripts/setup_ide.py - 1 byte)
- Archive duplicate parallel implementation
  - obsidian_auto_linker_parallel.py → archive/experimental_runners/
  - config_parallel_timeout.yaml → configs/deprecated/
- Move test utilities to proper location
  - scripts/test_*.py → tests/utilities/
- Archive 6 stale/redundant documentation files
  - TONIGHT_TODO.md, cleanup_plan.md, REVIEW_SUMMARY.md
  - docs/cleanup_*.md (3 files)
- Create archive documentation (archive/old_docs/README.md)
- Update archive and tests READMEs

Files changed:
- Deleted: 1 (broken file)
- Archived: 7 (1 Python, 6 docs)
- Moved: 2 (test utilities)
- Created: 1 (archive README)
- Updated: 3 (archive README, tests README, deprecated README)

Improves repository organization and removes duplication.
Ref: REFACTORING_PLAN.md, REPOSITORY_ANALYSIS_SUMMARY.md
"
echo "✅ Committed Priority 1 changes"
echo ""

# Push changes
echo "🚀 Step 12: Push to remote"
read -p "Push changes to remote? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push -u origin claude/repo-analysis-refactor-01J39fKe8T531HiA5vBrGVRn
    echo "✅ Pushed to remote"
else
    echo "⏸️  Skipped push (run manually: git push -u origin claude/repo-analysis-refactor-01J39fKe8T531HiA5vBrGVRn)"
fi
echo ""

echo "=============================================="
echo "✅ Priority 1 Cleanup Complete!"
echo ""
echo "📊 Summary:"
echo "  - Files deleted: 1"
echo "  - Files archived: 7"
echo "  - Files moved: 2"
echo "  - Directories created: 2"
echo ""
echo "📋 Next Steps:"
echo "  1. Review changes: git log -1 --stat"
echo "  2. Test imports: python3 -c 'import obsidian_auto_linker_enhanced'"
echo "  3. Run tests: pytest -v"
echo "  4. Continue with Priority 2 (config consolidation)"
echo ""
echo "📚 See REFACTORING_PLAN.md for Priority 2 & 3 tasks"
echo "=============================================="
