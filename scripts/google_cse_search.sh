#!/usr/bin/env bash

# Minimal Google Programmable Search (CSE) helper
# Usage:
#   GOOGLE_CSE_ID=xxxx GOOGLE_SEARCH_API_KEY=yyyy scripts/google_cse_search.sh "your query here"

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: GOOGLE_CSE_ID=... GOOGLE_SEARCH_API_KEY=... $0 \"your query\"" >&2
  exit 1
fi

if [[ -z "${GOOGLE_CSE_ID:-}" || -z "${GOOGLE_SEARCH_API_KEY:-}" ]]; then
  echo "Missing GOOGLE_CSE_ID or GOOGLE_SEARCH_API_KEY env vars." >&2
  exit 1
fi

QUERY="$1"

ENCODED_QUERY=$(python3 - <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.stdin.read().strip()))
PY
<<<"$QUERY")

curl -s "https://www.googleapis.com/customsearch/v1?key=${GOOGLE_SEARCH_API_KEY}&cx=${GOOGLE_CSE_ID}&q=${ENCODED_QUERY}" \
  | python3 - <<'PY'
import sys, json
data = json.load(sys.stdin)
items = data.get('items') or []
for it in items[:10]:
    print(f"- {it.get('title','(no title)')}\n  {it.get('link','')}\n  {it.get('snippet','').strip()}\n")
if not items:
    print("(no results)")
PY


