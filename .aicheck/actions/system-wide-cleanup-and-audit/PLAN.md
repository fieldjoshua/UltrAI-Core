# PLAN: System-Wide Cleanup and Audit

## Objective

To restore stability, improve deployment speed, and create a clean, maintainable codebase by performing a full system audit, eliminating unused code and dependencies, and refactoring the application's structure.

## Phase 1: Full-System Audit (Current Phase)

- [ ] **Dependency Analysis:** Statically analyze the `backend` and `src` directories to generate a definitive list of _required_ production dependencies.
- [ ] **Code Discovery:** Map the complete application structure, identifying all obsolete, orphaned, and duplicated code files.
- [ ] **Route Identification:** Programmatically list every API route to understand the full surface area of the application.

## Phase 2: Code & Dependency Archival

- [ ] **Archive Unused Code:** Move all identified non-essential files and directories into a dedicated `ARCHIVE` folder.
- [ ] **Create Lean Requirements:** Generate a new, clean `requirements.txt` based _only_ on the results of the dependency analysis.

## Phase 3: Structural Refactoring

- [ ] **Unify Application Structure:** Consolidate the duplicative `src` and `backend` directories into a single, logical `app` directory.
- [ ] **Standardize Imports:** Refactor all application imports to use absolute paths from the new `app` root, completely eliminating all `sys.path` manipulation.

## Phase 4: Verification & Deployment

- [ ] **Update Deployment Configuration:** Modify `render.yaml` to use the new, clean application entry point and the lean `requirements.txt`.
- [ ] **Deploy & Confirm:** Deploy the refactored, stable application and run the final verification tests to confirm the orchestrator is fully functional.
