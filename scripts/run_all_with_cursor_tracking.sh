#!/usr/bin/env bash
set -euo pipefail

# Runs offline, live, and demo tests using scripts/run_tests_all.sh,
# stores reports/logs under reports/<timestamp>, and writes a concise
# summary JSON to .cursor/test-latest.json for easy tracking in Cursor.

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
REPORT_ROOT="${ROOT_DIR}/reports"
TS="$(date -u +%Y%m%d%H%M%S)"
OUT_DIR="${REPORT_ROOT}/${TS}"
CURSOR_JSON="${ROOT_DIR}/.cursor/test-latest.json"

mkdir -p "${OUT_DIR}"
mkdir -p "${ROOT_DIR}/.cursor"

activate_venv() {
  if [[ -f "${ROOT_DIR}/venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    . "${ROOT_DIR}/venv/bin/activate"
  fi
}

extract_summary() {
  awk '/=+ .* in .*s =+/{ summary=$0 } END{ if (summary) print summary; else print "(no summary found)" }' "$1"
}

run_mode() {
  local mode="$1"; shift
  local report_file="$1"; shift
  local log_file="$1"; shift

  echo "==> Running mode: ${mode}"
  # Allow failures without stopping the entire sweep; we capture summary anyway
  set +e
  bash "${ROOT_DIR}/scripts/run_tests_all.sh" --mode "${mode}" --report "${report_file}" | tee "${log_file}"
  local rc=$?
  set -e
  echo "<== Mode ${mode} exit code: ${rc}"
  extract_summary "${log_file}"
}

main() {
  activate_venv

  OFFLINE_REPORT="${OUT_DIR}/report_offline.html"
  LIVE_REPORT="${OUT_DIR}/report_live.html"
  DEMO_REPORT="${OUT_DIR}/report_demo.html"

  OFFLINE_LOG="${OUT_DIR}/offline.log"
  LIVE_LOG="${OUT_DIR}/live.log"
  DEMO_LOG="${OUT_DIR}/demo.log"

  OFFLINE_JUNIT="${OUT_DIR}/offline.junit.xml"
  LIVE_JUNIT="${OUT_DIR}/live.junit.xml"
  DEMO_JUNIT="${OUT_DIR}/demo.junit.xml"
  STABLE_JUNIT_DIR="${ROOT_DIR}/.cursor/junit"
  mkdir -p "${STABLE_JUNIT_DIR}"

  OFFLINE_SUMMARY=$(run_mode offline "${OFFLINE_REPORT}" "${OFFLINE_LOG}")
  bash "${ROOT_DIR}/scripts/run_tests_all.sh" --mode offline --report "${OFFLINE_REPORT}" --junit "${OFFLINE_JUNIT}" >/dev/null 2>&1 || true

  LIVE_SUMMARY=$(run_mode live "${LIVE_REPORT}" "${LIVE_LOG}")
  bash "${ROOT_DIR}/scripts/run_tests_all.sh" --mode live --report "${LIVE_REPORT}" --junit "${LIVE_JUNIT}" >/dev/null 2>&1 || true
  # Allow overriding base URL: DEMO_BASE_URL=https://ultrai-prod-api.onrender.com ./scripts/run_all_with_cursor_tracking.sh
  DEMO_SUMMARY=$(run_mode demo "${DEMO_REPORT}" "${DEMO_LOG}")
  bash "${ROOT_DIR}/scripts/run_tests_all.sh" --mode demo --report "${DEMO_REPORT}" --junit "${DEMO_JUNIT}" >/dev/null 2>&1 || true

  # Copy JUnit to stable paths for Cursor/VS Code Test Explorer integrations
  cp -f "${OFFLINE_JUNIT}" "${STABLE_JUNIT_DIR}/offline.xml" 2>/dev/null || true
  cp -f "${LIVE_JUNIT}" "${STABLE_JUNIT_DIR}/live.xml" 2>/dev/null || true
  cp -f "${DEMO_JUNIT}" "${STABLE_JUNIT_DIR}/demo.xml" 2>/dev/null || true

  # Write concise JSON for Cursor
  # Build detailed tracking with categories using JUnit
  python3 "${ROOT_DIR}/scripts/parse_junit_to_cursor.py" \
    --offline "${OFFLINE_JUNIT}" \
    --live "${LIVE_JUNIT}" \
    --demo "${DEMO_JUNIT}" \
    --out "${ROOT_DIR}/.cursor/test-categories.json" >/dev/null 2>&1 || true

  cat > "${CURSOR_JSON}" <<JSON
{
  "timestamp_utc": "${TS}",
  "reports": {
    "offline": {
      "report_html": "${OFFLINE_REPORT#${ROOT_DIR}/}",
      "log": "${OFFLINE_LOG#${ROOT_DIR}/}",
      "summary": "${OFFLINE_SUMMARY}"
    },
    "live": {
      "report_html": "${LIVE_REPORT#${ROOT_DIR}/}",
      "log": "${LIVE_LOG#${ROOT_DIR}/}",
      "summary": "${LIVE_SUMMARY}"
    },
    "demo": {
      "base_url": "${DEMO_BASE_URL:-https://ultrai-staging-api.onrender.com}",
      "report_html": "${DEMO_REPORT#${ROOT_DIR}/}",
      "log": "${DEMO_LOG#${ROOT_DIR}/}",
      "summary": "${DEMO_SUMMARY}"
    }
  },
  "categories_file": ".cursor/test-categories.json"
}
JSON

  echo "\nSummary written to: ${CURSOR_JSON}"
  echo "Offline: ${OFFLINE_SUMMARY}"
  echo "Live:    ${LIVE_SUMMARY}"
  echo "Demo:    ${DEMO_SUMMARY}"
}

main "$@"


