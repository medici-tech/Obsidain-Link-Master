# 🧹 File Cleanup and Organization Plan

## 📊 Current Issues Found:

### 🔄 Duplicate Files:
- `model_performance_test.py` (duplicate in root and scripts/)
- Multiple config files with overlapping settings
- `vault_review_report.md` (duplicate in root and docs/)

### 📁 Organization Issues:
- Scripts scattered in root directory
- Multiple config files with similar purposes
- Reports directory not being used consistently
- Backup system needs verification

## 🎯 Cleanup Actions:

### 1. Remove Duplicate Files
- [ ] Remove duplicate `model_performance_test.py` from scripts/
- [ ] Remove duplicate `vault_review_report.md` from root
- [ ] Consolidate similar config files

### 2. Organize Scripts
- [ ] Move utility scripts to `scripts/` directory
- [ ] Keep only main launcher scripts in root
- [ ] Create proper script categories

### 3. Consolidate Configs
- [ ] Keep `config.yaml` as main config
- [ ] Move specialized configs to `configs/` directory
- [ ] Create config documentation

### 4. Verify Core Functionality
- [ ] Test main auto-linker script
- [ ] Verify backup system
- [ ] Check all imports and dependencies
- [ ] Test analytics generation

### 5. Create Clean Structure
```
Obsidain Link Master/
├── config.yaml (main config)
├── obsidian_auto_linker_enhanced.py (main script)
├── run_*.py (launcher scripts)
├── configs/ (specialized configs)
├── scripts/ (utility scripts)
├── docs/ (documentation)
├── reports/ (generated reports)
└── backups/ (backup files)
```

## ✅ Quality Checks:
- [ ] No duplicate files
- [ ] All imports working
- [ ] Config files organized
- [ ] Backup system verified
- [ ] Main script functional
- [ ] Analytics working
