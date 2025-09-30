#!/usr/bin/env python3
"""
Generate a consolidated communal TODO from multiple task/coordination files.

Inputs scanned (if present):
- ACTIVE_TASKS.md (root and UltrAI-Core/)
- AI_COORDINATION.md (root and UltrAI-Core/)
- RENDER_TASKS_FOR_OTHER_AI.md (root and UltrAI-Core/)

Output:
- COMMUNAL_TODO.md (repo root)

Notes:
- Uses only Python stdlib. Includes basic logging and error handling.
- Tolerant parsers for slightly different markdown formats.
"""

from __future__ import annotations

import sys
import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Optional
from datetime import datetime, timezone


# ------------------------- Logging Setup -------------------------

logger = logging.getLogger("communal_todo")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# --------------------------- Data Types --------------------------

PRIORITY_ORDER = [
    "High",  # 🔴
    "Medium",  # 🟡
    "Low",  # 🟢 or unspecified lower
    None,
]


@dataclass
class Task:
    title: str
    status: Optional[str]
    owner: Optional[str]
    priority: Optional[str]
    source: str

    def dedupe_key(self) -> str:
        return re.sub(r"\s+", " ", self.title.strip().lower())


# ------------------------- File Discovery ------------------------

def find_candidate_files(repo_root: Path) -> List[Path]:
    candidates = [
        repo_root / "ACTIVE_TASKS.md",
        repo_root / "AI_COORDINATION.md",
        repo_root / "RENDER_TASKS_FOR_OTHER_AI.md",
        repo_root / "UltrAI-Core" / "ACTIVE_TASKS.md",
        repo_root / "UltrAI-Core" / "AI_COORDINATION.md",
        repo_root / "UltrAI-Core" / "RENDER_TASKS_FOR_OTHER_AI.md",
    ]
    return [p for p in candidates if p.exists()]


# ---------------------------- Parsers ----------------------------

def parse_active_tasks_md(path: Path, text: str) -> List[Task]:
    tasks: List[Task] = []
    current_priority: Optional[str] = None

    # Map headings to priority labels
    priority_heading_map: Dict[str, str] = {
        "high priority": "High",
        "medium priority": "Medium",
        "low priority": "Low",
    }

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect priority section headings like "### 🔴 High Priority Queue"
        if line.startswith("### "):
            lower = line.lower()
            for key, label in priority_heading_map.items():
                if key in lower:
                    current_priority = label
                    break
            i += 1
            continue

        # Detect task title line
        m_task = re.match(r"^(\d+)\.\s+\*\*(.+?)\*\*", line)
        if m_task:
            title = m_task.group(2).strip()
            status: Optional[str] = None
            owner: Optional[str] = None

            # Look ahead for metadata lines beginning with "- "
            j = i + 1
            while j < len(lines):
                meta = lines[j].strip()
                if not meta.startswith("-"):
                    break
                # Example: "- Status: 🆕 Not Started"
                m_status = re.match(r"^-\s*Status:\s*(.+)$", meta, re.IGNORECASE)
                if m_status:
                    status = m_status.group(1).strip()
                m_owner = re.match(r"^-\s*Owner:\s*(.+)$", meta, re.IGNORECASE)
                if m_owner:
                    owner = m_owner.group(1).strip()
                j += 1

            tasks.append(
                Task(
                    title=title,
                    status=status,
                    owner=owner,
                    priority=current_priority,
                    source=str(path.relative_to(path.parents[0])) if path.is_relative_to(path.parents[0]) else str(path),
                )
            )
            i = j
            continue

        i += 1

    return tasks


def parse_coordination_md(path: Path, text: str) -> List[Task]:
    tasks: List[Task] = []
    lines = text.splitlines()

    # Try to detect owner from log prefix, fallback None
    inferred_owner: Optional[str] = None
    # If file contains "Claude-" assume Claude Code session; do not overfit.
    if re.search(r"Claude-\d+", text):
        inferred_owner = "Claude Code"

    # Find "Task Breakdown" block and parse checklist items
    try:
        start_idx = next(
            idx for idx, l in enumerate(lines) if l.strip().lower().startswith("### task breakdown")
        )
        # scan forward until next heading or end
        idx = start_idx + 1
        while idx < len(lines) and not lines[idx].startswith("### "):
            line = lines[idx].strip()
            m_item = re.match(r"^\d+\.\s*\[( |x|X)\]\s*(.+)$", line)
            if m_item:
                done_flag = m_item.group(1).lower() == "x"
                title = m_item.group(2).strip()
                status = "Done" if done_flag else "Not Started"
                tasks.append(
                    Task(
                        title=title,
                        status=status,
                        owner=inferred_owner,
                        priority=None,
                        source=str(path.relative_to(path.parents[0])) if path.is_relative_to(path.parents[0]) else str(path),
                    )
                )
            idx += 1
    except StopIteration:
        # No task breakdown block found; ignore file
        pass

    return tasks


def parse_render_tasks_md(path: Path, text: str) -> List[Task]:
    tasks: List[Task] = []
    lines = text.splitlines()

    # Owner from H1 if present, e.g., "# ... (Assigned: Claude Code)"
    owner: Optional[str] = None
    if lines:
        m_owner = re.search(r"\(Assigned:\s*([^\)]+)\)", lines[0])
        if m_owner:
            owner = m_owner.group(1).strip()

    for line in lines:
        line_stripped = line.strip()
        m_h3 = re.match(r"^###\s+\d+\.\s+(.+)$", line_stripped)
        if m_h3:
            title = m_h3.group(1).strip()
            tasks.append(
                Task(
                    title=title,
                    status="Not Started",
                    owner=owner,
                    priority="Medium",
                    source=str(path.relative_to(path.parents[0])) if path.is_relative_to(path.parents[0]) else str(path),
                )
            )

    return tasks


def parse_file(path: Path) -> List[Task]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error("Failed to read %s: %s", path, exc)
        return []

    name = path.name
    if name == "ACTIVE_TASKS.md":
        return parse_active_tasks_md(path, text)
    if name == "AI_COORDINATION.md":
        return parse_coordination_md(path, text)
    if name == "RENDER_TASKS_FOR_OTHER_AI.md":
        return parse_render_tasks_md(path, text)

    return []


# ------------------------- Consolidation -------------------------

def consolidate(tasks: Iterable[Task]) -> List[Task]:
    by_key: Dict[str, Task] = {}

    for t in tasks:
        key = t.dedupe_key()
        if key not in by_key:
            by_key[key] = t
            continue

        existing = by_key[key]

        # Prefer known owner over None/TBD
        prefer_owner = (
            (existing.owner is None or existing.owner.lower() in {"tbd", "unknown"})
            and t.owner
            and t.owner.lower() not in {"tbd", "unknown"}
        )
        if prefer_owner:
            existing.owner = t.owner

        # Prefer more informative status (e.g., not None)
        if (existing.status is None or existing.status.strip() == "") and t.status:
            existing.status = t.status

        # Prefer higher priority if conflicting
        def priority_rank(p: Optional[str]) -> int:
            try:
                return PRIORITY_ORDER.index(p)
            except ValueError:
                return len(PRIORITY_ORDER)

        if priority_rank(t.priority) < priority_rank(existing.priority):
            existing.priority = t.priority

        # Keep first source; we could append, but keep minimal noise
        by_key[key] = existing

    return list(by_key.values())


def sort_tasks(tasks: List[Task]) -> List[Task]:
    def priority_rank(p: Optional[str]) -> int:
        try:
            return PRIORITY_ORDER.index(p)
        except ValueError:
            return len(PRIORITY_ORDER)

    def status_rank(s: Optional[str]) -> int:
        if not s:
            return 3
        low = s.lower()
        if "in progress" in low or "🔄" in low:
            return 0
        if "not started" in low or "🆕" in low:
            return 1
        if "done" in low or "✅" in low or "completed" in low:
            return 2
        return 3

    return sorted(
        tasks,
        key=lambda t: (
            priority_rank(t.priority),
            status_rank(t.status),
            (t.owner or "zzz").lower(),
            t.title.lower(),
        ),
    )


# ---------------------------- Rendering --------------------------

def render_markdown(tasks: List[Task]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: List[str] = []
    lines.append("# Communal TODO")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")

    if not tasks:
        lines.append("No tasks discovered.")
        return "\n".join(lines) + "\n"

    # Group by priority
    by_priority: Dict[Optional[str], List[Task]] = {}
    for t in tasks:
        by_priority.setdefault(t.priority, []).append(t)

    for priority in PRIORITY_ORDER:
        section = by_priority.get(priority, [])
        if not section:
            continue
        header = priority or "Unspecified Priority"
        lines.append(f"## {header}")
        lines.append("")
        lines.append("| Title | Status | Owner | Source |")
        lines.append("|-------|--------|-------|--------|")
        for t in sort_tasks(section):
            title = t.title.replace("|", "\\|")
            status = (t.status or "").replace("|", "\\|")
            owner = (t.owner or "TBD").replace("|", "\\|")
            source = t.source.replace("|", "\\|")
            lines.append(f"| {title} | {status} | {owner} | `{source}` |")
        lines.append("")

    return "\n".join(lines) + "\n"


# ------------------------------ Main -----------------------------

def main(argv: List[str]) -> int:
    try:
        repo_root = Path(__file__).resolve().parents[1]
        output_path = repo_root / "COMMUNAL_TODO.md"

        files = find_candidate_files(repo_root)
        if not files:
            logger.warning("No candidate task files found.")

        all_tasks: List[Task] = []
        for p in files:
            try:
                parsed = parse_file(p)
                logger.info("Parsed %d tasks from %s", len(parsed), p.relative_to(repo_root))
                all_tasks.extend(parsed)
            except Exception as exc:
                logger.error("Error parsing %s: %s", p, exc)

        consolidated = consolidate(all_tasks)
        logger.info("Consolidated to %d unique tasks", len(consolidated))

        markdown = render_markdown(consolidated)
        output_path.write_text(markdown, encoding="utf-8")
        logger.info("Wrote %s", output_path.relative_to(repo_root))
        return 0
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

