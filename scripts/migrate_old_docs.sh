#!/bin/bash

# Script to migrate old documentation files to the new .aicheck structure

# Create necessary directories
mkdir -p .aicheck/actions/{ANALYSIS_WORKFLOW,CONTENT_AUDIT,CONTENT_INVENTORY,DIRECTORY_MAPPING,DOCUMENT_PROCESSING,API_SPECIFICATION}/supporting_docs

# Move files to their respective action directories
mv documentation/OLD_to_review/moved_files/ANALYSIS_WORKFLOW.md .aicheck/actions/ANALYSIS_WORKFLOW/ANALYSIS_WORKFLOW-PLAN.md
mv documentation/OLD_to_review/moved_files/CONTENT_AUDIT.md .aicheck/actions/CONTENT_AUDIT/CONTENT_AUDIT-PLAN.md
mv documentation/OLD_to_review/moved_files/CONTENT_INVENTORY.md .aicheck/actions/CONTENT_INVENTORY/CONTENT_INVENTORY-PLAN.md
mv documentation/OLD_to_review/moved_files/DIRECTORY_MAPPING.md .aicheck/actions/DIRECTORY_MAPPING/DIRECTORY_MAPPING-PLAN.md
mv documentation/OLD_to_review/moved_files/DOCUMENT_PROCESSING_OVERVIEW.md .aicheck/actions/DOCUMENT_PROCESSING/DOCUMENT_PROCESSING-PLAN.md
mv documentation/OLD_to_review/moved_files/API_SPECIFICATION.md .aicheck/actions/API_SPECIFICATION/API_SPECIFICATION-PLAN.md

# Move supporting documentation
mv documentation/OLD_to_review/moved_files/PATTERNS.md .aicheck/actions/ANALYSIS_WORKFLOW/supporting_docs/
mv documentation/OLD_to_review/moved_files/PLAN.md .aicheck/actions/ANALYSIS_WORKFLOW/supporting_docs/

# Clean up old directory
rm -rf documentation/OLD_to_review

echo "Migration complete. Files have been moved to the new .aicheck structure."
