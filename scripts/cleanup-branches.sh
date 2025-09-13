#!/bin/bash

# Script to clean up old branches
# This will list branches and allow selective deletion

echo "=== Git Branch Cleanup Tool ==="
echo "Branches to keep: main, production"
echo ""

# Get all remote branches except main and production
BRANCHES=$(git branch -r | grep -v '\->' | grep -v 'main' | grep -v 'production' | sed 's/origin\///')

# Count branches
COUNT=$(echo "$BRANCHES" | wc -l)
echo "Found $COUNT branches to potentially clean up."
echo ""

# Dependabot branches (usually safe to delete)
echo "=== Dependabot branches (usually safe to delete) ==="
echo "$BRANCHES" | grep 'dependabot/' | while read -r branch; do
    echo "  - $branch"
done

echo ""
echo "=== Other branches ==="
echo "$BRANCHES" | grep -v 'dependabot/' | while read -r branch; do
    echo "  - $branch"
done

echo ""
echo "To delete branches, use:"
echo "  git push origin --delete <branch-name>"
echo ""
echo "To delete multiple dependabot branches at once:"
echo "  git branch -r | grep 'dependabot/' | sed 's/origin\///' | xargs -n 1 git push origin --delete"