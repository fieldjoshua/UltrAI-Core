"""
Simple regex-based scan to ensure no pricing/cost terms appear in frontend code.

Blocks common terms in UI code paths. This is a lightweight guard, not exhaustive.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Iterable, List, Tuple


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
FRONTEND_DIRS = [
    os.path.join(ROOT, "frontend"),
    os.path.join(ROOT, "ultrai-ui"),
]

BLOCK_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"\b(cost|pricing|price|bill(?:ing)?|usd|\$\/1k|per\s*1k)\b", re.IGNORECASE),
]

ALLOWED_EXT = {".ts", ".tsx", ".js", ".jsx", ".html"}


def iter_files(paths: Iterable[str]) -> Iterable[str]:
    for base in paths:
        if not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            for f in files:
                if os.path.splitext(f)[1].lower() in ALLOWED_EXT:
                    yield os.path.join(root, f)


def scan_file(path: str) -> List[Tuple[str, str]]:
    findings: List[Tuple[str, str]] = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
    except Exception as exc:  # pragma: no cover
        print(f"WARN: could not read {path}: {exc}", file=sys.stderr)
        return findings

    for pat in BLOCK_PATTERNS:
        for m in pat.finditer(content):
            snippet = content[max(0, m.start()-20): m.end()+20].replace("\n", " ")
            findings.append((pat.pattern, snippet))
    return findings


def main() -> int:
    violations: List[Tuple[str, str, str]] = []
    for path in iter_files(FRONTEND_DIRS):
        for pattern, snippet in scan_file(path):
            violations.append((path, pattern, snippet))

    if violations:
        print("No-cost UI scan found potential violations:")
        for path, pattern, snippet in violations:
            print(f" - {path}: /{pattern}/ => ...{snippet}...")
        return 1
    print("No-cost UI scan passed: no pricing/cost terms detected in UI code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


