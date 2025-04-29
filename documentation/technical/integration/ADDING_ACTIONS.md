# How to Add a New Action to AICheck

## 1. Use the CLI to Create the Action

Run:

```sh
./ai new MyActionName
```

- Use PascalCase for the action name (e.g., `DataImport`, `UserOnboarding`).

## 2. Edit the Action Plan

- Open `.aicheck/actions/MyActionName/MyActionName-PLAN.md`.
- Fill out the sections: Purpose, Steps, Success Criteria, Notes.
- Use the template in `.aicheck/templates/ACTION_PLAN_TEMPLATE.md` for guidance.

## 3. Track and Update Progress

- Use the CLI to switch, update status, or delete actions:
  - `./ai switch MyActionName`
  - `./ai status MyActionName`
  - `./ai update-status MyActionName "In Progress"`
  - `./ai update-progress MyActionName "50%"`
  - `./ai delete MyActionName`

## 4. Follow RULES.md

- Ensure your action plan is clear, complete, and RULES.md compliant.
- Document supporting details in the `supporting_docs/` folder if needed.

## 5. Commit Your Changes

- Add and commit your new action and plan:

  ```sh
  git add .aicheck/actions/MyActionName/
  git commit -m "Add MyActionName action plan"
  ```

---
For more, see the README and RULES.md.
