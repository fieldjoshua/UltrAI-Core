#!/usr/bin/env python3
import argparse
import json
import os
import xml.etree.ElementTree as ET
from typing import Dict, List


def infer_category(testcase_name: str, classname: str) -> str:
    name = testcase_name.lower()
    cls = (classname or "").lower()
    # Heuristics by path/classname
    if "tests/unit/" in cls or "test_unit" in name or ".unit." in cls:
        return "unit"
    if "tests/integration/" in cls or "integration" in name or ".integration." in cls:
        return "integration"
    if "tests/live/test_live_providers.py" in cls or "live providers" in cls:
        # provider buckets based on name
        if "openai" in name:
            return "live_providers:openai"
        if "anthropic" in name:
            return "live_providers:anthropic"
        if "gemini" in name or "google" in name:
            return "live_providers:gemini"
        if "huggingface" in name or "hf" in name:
            return "live_providers:huggingface"
        return "live_providers:other"
    if "tests/live/test_demo_endpoints.py" in cls or "demo" in name:
        return "demo_endpoints"
    return "other"


def parse_junit(path: str) -> Dict[str, Dict[str, List[Dict]]]:
    tree = ET.parse(path)
    root = tree.getroot()
    # JUnit can be <testsuites> or <testsuite>
    suites = [root] if root.tag == "testsuite" else list(root)

    categories: Dict[str, List[Dict]] = {}
    for suite in suites:
        for case in suite.findall("testcase"):
            name = case.attrib.get("name", "")
            classname = case.attrib.get("classname", "")
            time_s = case.attrib.get("time", "0")
            status = "passed"
            details = None
            if case.find("failure") is not None:
                status = "failed"
                details = case.find("failure").attrib.get("message", "failure")
            elif case.find("error") is not None:
                status = "error"
                details = case.find("error").attrib.get("message", "error")
            elif case.find("skipped") is not None:
                status = "skipped"
                details = case.find("skipped").attrib.get("message", "skipped")

            cat = infer_category(name, classname)
            categories.setdefault(cat, []).append({
                "name": name,
                "classname": classname,
                "time": float(time_s) if time_s else 0.0,
                "status": status,
                "details": details,
            })

    return {"categories": categories}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", required=True, help="Path to offline junit.xml")
    ap.add_argument("--live", required=True, help="Path to live junit.xml")
    ap.add_argument("--demo", required=True, help="Path to demo junit.xml")
    ap.add_argument("--out", required=True, help="Output JSON path")
    args = ap.parse_args()

    combined: Dict[str, Dict[str, List[Dict]]] = {"modes": {}}
    combined["modes"]["offline"] = parse_junit(args.offline)
    combined["modes"]["live"] = parse_junit(args.live)
    combined["modes"]["demo"] = parse_junit(args.demo)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()


