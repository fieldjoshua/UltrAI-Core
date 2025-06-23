#!/usr/bin/env bash
# run_e2e.sh ── Execute Playwright end-to-end tests using the locally installed Google Chrome.
#
# Usage examples
#   ./run_e2e.sh                       # run every test marked e2e
#   ./run_e2e.sh -q tests/e2e/         # pass normal pytest flags / path
#
# This avoids Playwright CDN downloads (handy behind firewalls) by telling
# Playwright to launch the system Chrome executable.

set -euo pipefail

export PLAYWRIGHT_BROWSERS_PATH=0               # skip bundled downloads
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1       # extra safety
: "${PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH:="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}";

pytest -m e2e "$@"