# TODO: directory-cleanup-organization

## Active Tasks

### Phase 1: Safe Cleanup
- [ ] Create full backup of project (priority: high, status: pending)
- [ ] Remove all .DS_Store files (priority: high, status: pending)
- [ ] Remove all .bak files in app/routes/ (priority: high, status: pending)
- [ ] Remove old aicheck backups (priority: high, status: pending)
- [ ] Remove Python cache files and __pycache__ (priority: high, status: pending)
- [ ] Remove test environment directories (priority: medium, status: pending)
- [ ] Remove empty directories (priority: medium, status: pending)
- [ ] Document Phase 1 deletions (priority: high, status: pending)

### Phase 2: Archive Handling  
- [ ] Analyze ARCHIVE_20250606/ contents (priority: high, status: pending)
- [ ] Extract valuable code/docs from archives (priority: medium, status: pending)
- [ ] Remove or relocate archive directories (priority: high, status: pending)
- [ ] Process ARCHIVE_UNSORTED/ contents (priority: medium, status: pending)
- [ ] Document archive decisions (priority: high, status: pending)

### Phase 3: File Reorganization
- [ ] Create data/csv/ directory (priority: high, status: pending)
- [ ] Create scripts/automation/ directory (priority: high, status: pending)
- [ ] Move CSV files to data/csv/ (priority: medium, status: pending)
- [ ] Move utility scripts to scripts/automation/ (priority: medium, status: pending)
- [ ] Move email_validator.py to app/utils/ (priority: medium, status: pending)
- [ ] Update affected import statements (priority: high, status: pending)
- [ ] Document all file moves (priority: high, status: pending)

### Phase 4: .gitignore Updates
- [ ] Add system file exclusions (.DS_Store, etc) (priority: high, status: pending)
- [ ] Add build artifact exclusions (priority: high, status: pending)
- [ ] Add log file exclusions (priority: medium, status: pending)
- [ ] Add temporary file exclusions (priority: medium, status: pending)
- [ ] Test .gitignore effectiveness (priority: high, status: pending)

### Phase 5: Verification
- [ ] Run full test suite (priority: high, status: pending)
- [ ] Check for broken imports (priority: high, status: pending)
- [ ] Test development server (priority: high, status: pending)
- [ ] Test production server (priority: high, status: pending)
- [ ] Test frontend build (priority: high, status: pending)
- [ ] Create comprehensive cleanup log (priority: high, status: pending)
- [ ] Update documentation (priority: medium, status: pending)
- [ ] Commit changes with detailed message (priority: high, status: pending)

## Completed Tasks
<!-- Move tasks here as they are completed -->

## Notes
- Remember to run tests after each phase
- Keep detailed log of all changes
- Be extra careful with archive directories - review before deletion