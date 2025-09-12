#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/run_tests_all.sh \
#     --mode offline|live|demo \
#     --base-url https://ultrai-staging-api.onrender.com \
#     --report report.html \
#     --junit junit.xml

MODE="offline"
BASE_URL=""
REPORT="report.html"
JUNIT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"; shift 2 ;;
    --base-url)
      BASE_URL="$2"; shift 2 ;;
    --report)
      REPORT="$2"; shift 2 ;;
    --junit)
      JUNIT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ "${BASE_URL}" != "" ]]; then
  export DEMO_BASE_URL="${BASE_URL}"
fi

echo "Mode: ${MODE}"
echo "Report: ${REPORT}"
if [[ "${JUNIT}" != "" ]]; then
  echo "JUnit: ${JUNIT}"
fi

case "${MODE}" in
  offline)
    # Exclude mode-specific tests that are intended for integration/live
    TEST_MODE=offline pytest -v -m "not live and not live_online and not e2e and not integration" \
      --html="${REPORT}" --self-contained-html --alluredir=allure-results ${JUNIT:+--junitxml="${JUNIT}"} ;;
  live)
    # Requires provider keys in env
    # Auto-load provider keys from .env files if present
    if [[ -f .env ]]; then set -a && source .env && set +a; fi
    if [[ -f .env.local ]]; then set -a && source .env.local && set +a; fi
    TEST_MODE=live pytest -v -m live \
      --html="${REPORT}" --self-contained-html --alluredir=allure-results ${JUNIT:+--junitxml="${JUNIT}"} ;;
  demo)
    # Hits staging/prod endpoints; resilient to 502 via test skips
    TEST_MODE=live pytest -v -k "test_demo_" -m live \
      --html="${REPORT}" --self-contained-html --alluredir=allure-results ${JUNIT:+--junitxml="${JUNIT}"} ;;
  *)
    echo "Invalid mode: ${MODE}"; exit 2 ;;
esac

echo "Done."

