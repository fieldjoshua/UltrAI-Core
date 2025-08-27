# Phase 2 Tasks for Cursor AI - Documentation Cleanup

Copy these tasks one by one into Cursor's AI assistant:

## Task 1: Find and List Duplicate Documentation Files
```
Please find all duplicate markdown files in the project. Look for files with the same name (like api_documentation.md, product_vision.md, requirements.md, etc.) that appear in multiple directories such as:
- /documentation/
- /supporting_docs/
- /.aicheck/actions/*/supporting_docs/
- /Nontechnical/
- Root directory

Create a list showing which files are duplicated and their locations.
```

## Task 2: Consolidate API Documentation
```
We have multiple copies of api_documentation.md in different locations. Please:
1. Compare all versions of api_documentation.md
2. Identify which one is most complete/recent
3. Keep only the best version in /documentation/api_documentation.md
4. Delete all other copies
5. Update any references to the old locations
```

## Task 3: Consolidate Product Vision Documents
```
Find all product_vision.md files and similar vision/strategy documents. Please:
1. Compare all versions
2. Merge any unique content into a single /documentation/product_vision.md
3. Remove all duplicate copies
4. Check for related files like strategy.md, vision.md that should be consolidated
```

## Task 4: Clean Up Supporting Docs
```
The supporting_docs/ directory has many duplicate files. Please:
1. List all files in supporting_docs/ 
2. Check if they duplicate content in /documentation/
3. For any duplicates, keep the version in /documentation/ and remove from supporting_docs/
4. Move any unique technical docs from supporting_docs/ to /documentation/
```

## Task 5: Remove UI/UX HTML Mockups
```
The documentation/ui-ux directory contains 35 HTML mockup files. Please:
1. Remove all .html files from documentation/ui-ux/
2. Keep only essential design documentation (.md files, images)
3. If there are important mockups, suggest moving them to a separate design repository
```

## Task 6: Consolidate AICheck Documentation
```
There are multiple AICheck action directories with their own documentation. Please:
1. Find all .aicheck/actions/*/supporting_docs/ directories
2. Identify any documentation that should be preserved at the project level
3. Move important docs to /documentation/aicheck/
4. Remove redundant action-specific documentation
```

## Task 7: Clean Up Root Level Docs
```
Check the root directory for documentation files that should be organized. Please:
1. List all .md files in the root directory
2. Keep only: README.md, CLAUDE.md, CODEBASE_REDUCTION_REPORT.md, CURSOR_*.md
3. Move other documentation to appropriate subdirectories in /documentation/
4. Update any references to moved files
```

## After Each Task:
- Verify no critical documentation was lost
- Check that file references/links still work
- Commit changes with a clear message about what was consolidated