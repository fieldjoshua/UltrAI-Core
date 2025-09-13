#!/bin/bash
# Restore production settings by removing local overrides
cd "$(dirname "$0")/../frontend"
rm -f .env.local
echo "Frontend restored to production settings"
