# Project Reorganization

## Objective

Systematically reorganize the project structure to improve maintainability, navigation, and documentation while ensuring all functionality remains intact.

## Value

This reorganization will:

- Reduce root directory clutter
- Improve discoverability of key components
- Centralize and standardize documentation
- Establish clearer separation of concerns
- Make the codebase more approachable for new contributors

## Current State

The project currently has:

- Many files in the root directory
- Documentation spread across multiple locations
- Potentially redundant directories (backend/ and src/)
- Scripts with hard-coded paths that make relocation difficult

## Implementation Plan

### Phase 1: Documentation Reorganization (Completed)

- ✅ Create structured documentation directory with categorized subdirectories
- ✅ Move technical documentation to appropriate subdirectories
- ✅ Move implementation docs to designated location
- ✅ Create configuration documentation
- ✅ Document file organization standards

### Phase 2: File Relocations (Partially Completed)

- ✅ Move `cyberpunk-demo.html` to `frontend/demos/`
- ✅ Move `result_images/` to `data/images/`
- ⬜ Address script relocation issues

### Phase 3: Script and Path Updates

- ⬜ Refactor scripts to use relative paths
- ⬜ Update path references in automation scripts
- ⬜ Create symlinks from original locations to maintain compatibility
- ⬜ Test all scripts thoroughly after changes

### Phase 4: AICheck Structure Updates

- ⬜ Remove `supporting_docs/` directories from action folders
- ⬜ Move all action supporting documentation to appropriate `/documentation/` subdirectories
- ⬜ Rename `.aicheck/docs/` to `.aicheck/indexing/`
- ⬜ Update all scripts to reference the new structure
- ⬜ Create backward compatibility symlinks as needed

### Phase 5: Codebase Consolidation Analysis

- ⬜ Analyze overlap between `backend/` and `src/`
- ⬜ Document recommended consolidation approach
- ⬜ Create detailed migration plan if consolidation is recommended

### Phase 6: RULES and Documentation Updates

- ⬜ Update RULES.md to reflect new structure
- ⬜ Update core README with project structure index
- ⬜ Update .aicheck documentation and guidelines

## Success Criteria

1. All files are organized according to the new structure
2. All scripts and functionality work properly from their new locations
3. Documentation is updated to reflect the new organization
4. No regression in system functionality
5. Clear paths forward for any pending consolidation work

## Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking script paths | Test scripts thoroughly after changes; maintain backward compatibility |
| Disrupting workflows | Document changes clearly; create transition guides |
| Incomplete migration | Track progress carefully with clear status indicators |
| Lost files | Back up all files before moving; use copy-then-remove approach |
| Path reference issues | Create temporary compatibility symlinks during transition |
