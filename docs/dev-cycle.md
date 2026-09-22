# Dev Cycle — Architect → Implementer → Reviewer

Portable workflow for Cursor, Claude Code, Codex, and similar coding agents.

Each role runs in a **fresh chat**. Never depend on previous conversational context. The **repository** (and optional `plan.md`) is the shared source of truth.

## How to use

Start three independent sessions for a feature:

```text
Architect:  /dev-cycle architect Add caching to the API
Implement:  /dev-cycle implement Add caching to the API
Review:     /dev-cycle review Add caching to the API
```

If your tool does not support `/dev-cycle`, paste the matching role section below and append the feature request.

---

## Architect

- inspect the current repository
- do not modify files
- understand the requested feature
- propose the smallest clean design
- identify relevant files/interfaces
- explain how it should be tested

Write the proposal to `plan.md` at the repo root (replace prior stage content) so an implementer in a fresh chat can pick it up. Stop after writing `plan.md` — do not implement.

---

## Implement

- assume the planning conversation is unavailable
- inspect the repository and reconstruct context yourself
- **read `plan.md` first** when it exists; treat it as the agreed approach unless the repo clearly requires a small deviation (call those out briefly)
- implement the requested behavior using existing patterns
- keep the change scoped
- add/update relevant tests
- run relevant tests and the broader suite when practical
- summarize what changed and test status

---

## Review

- assume another agent implemented the feature
- inspect it like a PR you did not author
- verify the requested behavior and architecture
- look for bugs, regressions, coupling, edge cases, and weak tests
- add useful missing tests
- fix implementation bugs rather than weakening legitimate tests
- run the relevant tests and broader suite
- summarize findings and final test status

`plan.md` is optional background for intent only — judge the code and tests on their own merits.

---

## Across all roles

- inspect before assuming
- prefer existing project conventions
- avoid unnecessary abstractions
- keep changes small and reviewable
- tests are part of the handoff contract between independent agents

---

## Cursor install (user-level skill)

Copy this folder to `~/.cursor/skills/dev-cycle/` with a `SKILL.md` (see the companion skill in that path), or paste the create-skill prompt from the DashBite Prompt Board (“Take the workflow with you”).
