# Version Control Workflow

To keep `main` production-ready while we iterate on repository ingestion, every checklist item must follow this cadence:

1. Pull latest changes from `origin/main`.
2. Complete the scoped implementation work.
3. Run applicable automated checks (pytest, linting, frontend build/tests).
4. Resolve issues and rerun checks until they pass or document any known blockers.
5. Verify `git status` is clean except for intentional changes.
6. Stage changes with `git add`, commit using a descriptive message, and push directly to `main`.

This mirrors the Execution Protocol in `PROJECT_PLAN.md` and ensures we always have a good working copy before starting the next task.
