# UltraAI • Universal Rules (v 2.2.0)

> **One rule to remember** — *If it isn’t written down first, we don’t build it.*

---

## 1 · Core Principles

| ID | Plain‑English Expectation | How We Enforce It |
|----|---------------------------|-------------------|
| **ONE SOURCE** | This document is the controlling document. Changes to it must be approved by the human manager on this project (`jfield@forresterfield.com`). | `.github/CODEOWNERS` entry for `documentation/RULES.md` + branch‑protection rule requiring @fieldjoshua review. |
| **ELEMENTS_DEFINED** | Changes to program architecture, dependencies, or ENV VAR definitions are governed by Section 2 below and stored in `documentation/CONFIG_DEFINITIONS.md`. | Pre‑commit hook blocks edits to `infra/` or `.env.example` unless the matching definition file is updated in the same commit. |
| **STYLE_STANDARDS** | Editors must follow established style guidelines in addition to the timing and manner system for ACTIONs. | `black`, `isort`, `flake8`, and `markdownlint` run in pre‑commit & CI. |
| **DOCUMENTED‑ACTIONPLAN‑PROCESS** | Documentation must precede any Action. Every Action starts with written documentation. | Pre‑commit blocks commits adding code when no file in `Actions/<name>/` or `documentation/` changed. |
| **ACTION‑DIRECTORY** | Each Action lives in its own `Actions/<name>/` folder containing a `PLAN.md` and supporting materials (`Research/`, `Prototypes/`, etc.) that **must** follow templates in `documentation/Templates/`. | `validate_plan_dirs.py` (pre‑commit & CI) checks folder layout and template usage. |
| **SINGLE‑ACTION** | Only **one** Action may carry `state: WORKING` at any moment. | `check_single_action.py` fails commit/CI if more than one `PLAN.md` has `state: WORKING`. |
| **REGULAR UPDATES** | Editors must update the relevant Action directory after every working session to reflect progress and show which single Action is being worked on. | Commit‑message linter warns if code changes but the active `PLAN.md` timestamp is unchanged for > 1 h. |
| **SUBSTANTIVE CHANGES** | Creating new Actions, ending/merging existing ones, or other large edits require review by the human manager (`jfield@forresterfield.com`). | Any commit that adds or removes an `Actions/<folder>` triggers CODEOWNERS review request to @fieldjoshua. |
| **EDITOR REVIEW** | Editors must stay conscious of scope creep and ensure their work does not drift into other Actions. | `check_single_action.py` plus reviewer checks; PRs touching multiple Actions without justification are rejected. |

---

## 2 · When Code Can Change

| Rule ID | Condition to Touch Code | Enforcement |
|---------|-------------------------|-------------|
| **CODE‑CHANGE‑GATE** | You may edit source code **only** when a matching `PLAN.md` exists, is in `WORKING`, and you are on an Implementation checklist item. | Pre‑commit hook parses staged paths + reads the active `PLAN.md`; blocks otherwise. |
| **STATUS‑UPDATE** | Update `PLAN.md` after completing a checklist item **or** at the end of your work session. | Commit‑message linter warns if `PLAN.md` timestamp unchanged for > 1 h of edits. |

---

## 3 · How to Update Action Status

| Allowed Transition | When it Happens |
|--------------------|-----------------|
| `QUEUED → WORKING` | You start actively coding and have committed your `PLAN.md`. |
| `WORKING → REVIEW` | Implementation checklist finished; open a PR. |
| `REVIEW → ACCEPTED` | PR approved and merged. |
| `ACCEPTED → RELEASED` | Feature is deployed. |
| `WORKING → BLOCKED` | External issue stops progress; note reason in `PLAN.md`. |

> **Tip:** Keep the `state:` line at the very top of `PLAN.md` so it’s easy to diff.

---

## 4 · Commit Checklist

```
[ ] A `PLAN.md` exists and is in state WORKING
[ ] This commit relates to a step listed in the plan
[ ] PLAN.md updated (checkbox ticked or status changed)
[ ] Only this one Action is in state WORKING
```

---

## 5 · Style Requirements

| ID | Plain‑English Standard | Enforcement |
|----|------------------------|-------------|
| **LINE‑LENGTH** | Keep code lines ≤ 88 characters. | `black` auto‑formats; pre‑commit aborts if not compliant. |
| **BLACK‑FORMAT** | Always run Black before committing. | `black --check` hook; CI repeats. |
| **ISORT‑IMPORTS** | Sort Python imports consistently. | `isort` hook auto‑fixes; CI verifies. |
| **FLAKE‑LINT** | No Flake8 errors or warnings. | `flake8` hook & CI job. |
| **NAMING‑CONVENTIONS** | Use `snake_case` for variables/functions, `CamelCase` for classes. | `flake8‑naming` plugin. |
| **DOCSTRINGS** | Public functions/classes must have Google‑style docstrings. | `pydocstyle` runs in CI. |
| **UTF‑8‑ONLY** | Source files encoded UTF‑8 with LF line endings. | `.editorconfig` + CI check. |
| **MARKDOWN‑HEADINGS** | Headings start with a capital letter and one space after `#`. | `markdownlint` hook/CI. |
| **NO‑DEBUG‑PRINTS** | Remove `print()` / `console.log` from production code. | Regex pre‑commit hook flags them. |
| **TEMPLATE‑DOCS** | Supporting docs in an Action must use templates from `documentation/Templates/`. | `validate_plan_dirs.py` checks template heading IDs. |

---

*End of Rules v 2.2.0*
