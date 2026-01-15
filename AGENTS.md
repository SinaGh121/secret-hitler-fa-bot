# AGENTS.md

This file defines how Codex agents should keep continuity in this repo.

## Mandatory update rule
- After any change by Codex, update `PROJECT_CONTEXT.md` and `DECISIONS.md` in the same change set.
- Update `AGENTS.md` only when the process itself changes.

## What to update
- `PROJECT_CONTEXT.md`: system overview, entry points, configuration, repo map, known issues, testing notes.
- `DECISIONS.md`: append a dated entry for each decision or a brief "No decision; maintenance change" note.

## Workflow
- Scan the repo and affected files.
- Make code or doc changes.
- Update `PROJECT_CONTEXT.md` and `DECISIONS.md` to reflect those changes.
- Mention doc updates in the final response.

## Constraints
- Keep these docs ASCII-only unless they already contain non-ASCII content.
- Do not delete history; append new entries.
