#!/bin/bash
# AICheck System Status Review Command
# This script triggers a comprehensive AICheck system review

set -e

# Change to project root
cd "$(dirname "$0")/../.."

# Create the command response
cat << 'EOF'
# /aicheck Command Executed

I'll now perform a comprehensive AICheck system status review. This will include:

1. Active Action Review
2. Action Index Analysis
3. System Health Check
4. Compliance Verification
5. Risk Assessment
6. Recommendations

Let me analyze the current state of the AICheck system...

EOF

# Note: The actual review will be performed by Claude when this prompt is used
echo "Please use the following to continue:"
echo "./ai claude prompt system-review/status-update"
