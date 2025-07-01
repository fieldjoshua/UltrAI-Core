# Action Plan: dependency-hygiene

## 1. Objective
Eliminate critical & high CVE alerts reported by GitHub Dependabot for the UltraAI codebase.

## 2. Value
• Hardens the production attack-surface
• Keeps Docker/CI images compliant with security policies
• Prevents supply-chain exploit vectors

## 3. Scope
1. Enumerate current Dependabot alerts (export via GitHub API)
2. Patch ALL critical & high severities, and any moderate that affect runtime
3. Update `pyproject.toml` + `poetry.lock` accordingly
4. Add SBOM generation (`poetry export --format json` in CI)
5. Integrate `pip-audit` in dev dependencies and CI job
6. Update `.aicheck/RULES.md` with vulnerability-response SLA (≤7 days)

## 4. Deliverables
* Updated dependency versions & lockfile
* `documentation/security/sbom.json`
* New CI step for vulnerability auditing
* DONE.md summarising fixed CVEs

## 5. Risks & Mitigations
* Upstream breaking changes → mitigate via full test-suite & pin minor versions
* Transitive dependency conflicts → isolate upgrades one-by-one

## 6. Test Strategy
* Run entire `pytest` suite after each bump
* Manual smoke test of API routes

## 7. Timeline
* Day 1: Gather alerts, create upgrade branch
* Day 2-3: Patch & test
* Day 4: CI/Guardian review & merge 