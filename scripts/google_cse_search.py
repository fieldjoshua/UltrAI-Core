#!/usr/bin/env python3
"""
Minimal Google Programmable Search (CSE) helper.
Usage:
  export GOOGLE_CSE_ID=xxxx
  export GOOGLE_SEARCH_API_KEY=yyyy
  python3 scripts/google_cse_search.py "your query here"
"""

import os
import sys
import json
import urllib.parse
import urllib.request


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: GOOGLE_CSE_ID=... GOOGLE_SEARCH_API_KEY=... google_cse_search.py 'your query'", file=sys.stderr)
        return 1

    cse_id = os.getenv("GOOGLE_CSE_ID")
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    if not cse_id or not api_key:
        print("Missing GOOGLE_CSE_ID or GOOGLE_SEARCH_API_KEY env vars.", file=sys.stderr)
        return 1

    query = sys.argv[1]
    encoded = urllib.parse.quote(query)
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={encoded}"

    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 2

    items = data.get("items") or []
    for it in items[:10]:
        title = it.get("title", "(no title)")
        link = it.get("link", "")
        snippet = (it.get("snippet") or "").strip()
        print(f"- {title}\n  {link}\n  {snippet}\n")

    if not items:
        print("(no results)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


