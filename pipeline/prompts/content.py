"""Stage metadata and Think / Build / Check prompts (independent agent chats)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StagePrompts:
    number: int
    title: str
    teach: str
    plan: str  # Think it through — Architect
    execute: str  # Build it — Implementer
    test: str  # Check it — Reviewer


BASE_PLAN_TITLE = "Base plan — Pipeline diagram"
BASE_PLAN_TEACH = (
    "Warm up: one shared mental model before anyone opens an agent chat on code."
)
BASE_PLAN = """\
We're about to build a small ML pipeline together. Before anyone touches application code, help me sketch the system so everyone in the room has the same mental model.

The product story is DashBite: food-delivery orders come in, and we want to predict whether an order will be late. Keep the raw fields short — order_id, timestamp, distance_km, prep_minutes, order_value, was_late.

Architecturally I want something modular and demo-friendly:
- separate stages that feel like separate processes
- they hand off through folders under data/, not by importing each other
- training publishes versioned checkpoints; inference is a separate consumer of the newest checkpoint on disk
- if training is down, inference should still work off whatever model is already there
- a couple of lightweight dashboards that read existing outputs rather than owning pipeline logic
- no containers, Kafka, Spark, etc. — plain Python and files are enough

Sketch a Mermaid flowchart (left-to-right is fine) that captures that story, including the train write path and the infer read path. Then give me a few short bullets on the teaching beats we should keep repeating as we build.

Write that diagram and the short bullets into plan.md at the repo root so later chats can find it. Don't implement the pipeline yet — plan.md only.
"""

CREATE_SKILL_PROMPT = """\
Use Cursor's /create-skill workflow to create a user-level skill named `dev-cycle` so I can use it across repositories.

The skill should support three roles: architect, implement, and review.

Each role may run in a completely fresh chat, so the skill must never depend on previous conversational context. The repository should be treated as the shared source of truth.

Architect:
- inspect the current repository
- do not modify files
- understand the requested feature
- propose the smallest clean design
- identify relevant files/interfaces
- explain how it should be tested

Implement:
- assume the planning conversation is unavailable
- inspect the repository and reconstruct context yourself
- implement the requested behavior using existing patterns
- keep the change scoped
- add/update relevant tests
- run relevant tests and the broader suite when practical
- summarize what changed and test status

Review:
- assume another agent implemented the feature
- inspect it like a PR you did not author
- verify the requested behavior and architecture
- look for bugs, regressions, coupling, edge cases, and weak tests
- add useful missing tests
- fix implementation bugs rather than weakening legitimate tests
- run the relevant tests and broader suite
- summarize findings and final test status

Across all roles:
- inspect before assuming
- prefer existing project conventions
- avoid unnecessary abstractions
- keep changes small and reviewable
- tests are part of the handoff contract between independent agents

Make the skill available globally/user-level rather than only inside this repository.
"""

_PLAN_MD_SHAPE = """\
Write (or replace) plan.md using a concise structure like:

# Stage N — <Title>

## Goal
...

## Proposed changes
- ...

## Architecture / boundaries
- ...

## Automated tests
- Unit: ...
- Regression: ...
- Integration: ...

## Manual Smoke Test
### What we're proving
...
### Terminal
(pasteable commands; label Terminal 1 / 2 / 3 if needed)
### Watch for
...
### Stop
Ctrl+C when a process should be stopped

The Manual Smoke Test is for a live classroom demo — visible logs, files on disk, readable CSV/model output. Do NOT use `pytest` as the smoke test; that's automated verification.
"""


STAGES: tuple[StagePrompts, ...] = (
    StagePrompts(
        number=0,
        title="Skeleton",
        teach="Smallest foundation: shared config, data folders, and a pytest gate.",
        plan=f"""\
We're starting DashBite from an empty-ish repo and need the smallest foundation before anything interesting.

Inspect the repository and write the implementation plan to plan.md.

Include:
- what we're changing
- relevant files/interfaces
- architectural constraints
- automated test strategy
- a manual smoke test I can run live from the terminal after implementation

Non-negotiables for this demo:
- config defaults include TRAIN_EVERY_N_EVENTS=2000 and BATCH_SIZE=50, overridable from the environment
- path helpers that resolve data/raw, features, models, predictions, quality and can create them
- pytest layout with unit / regression / integration markers

For the Manual Smoke Test, design something short and visible: load config (and maybe an env override), then show data dirs resolving/being created — e.g. a tiny `python -c` that prints load_config() and ensure_data_dirs().

{_PLAN_MD_SHAPE}

Do not implement the feature yet. Only write plan.md, then stop.
""",
        execute="""\
We're implementing Stage 0 of the DashBite pipeline.

Inspect the repository and read plan.md first. Treat it as the architecture and behavior handoff from the planning agent — including the Manual Smoke Test section.

Implement the planned skeleton using the existing project patterns: pipeline package with shared config and path helpers, data/ folders, pytest markers. Config defaults should include TRAIN_EVERY_N_EVENTS=2000 and BATCH_SIZE=50, overridable from the environment.

Keep the change scoped — no simulator or model yet. Add/update the relevant tests, and run them as you work.

When implementation is complete, do not replace the manual smoke-test instructions in plan.md. Make sure they still match the actual commands and behavior. If implementation details changed enough that the documented smoke test is no longer accurate, update only that section so it is runnable.
""",
        test="""\
Review the current Stage 0 skeleton as if this were a PR you did not author.

Read plan.md first to understand the intended behavior, architecture, automated test strategy, and manual smoke test.

Verify the implementation against that contract: shared config (TRAIN_EVERY_N_EVENTS / BATCH_SIZE), path helpers, data dirs, pytest layout.

Add or improve unit, regression, and integration tests where they provide meaningful coverage. Run the full pytest suite. If something fails, fix the underlying implementation problem rather than weakening a legitimate test.

Inspect whether the documented Manual Smoke Test is still accurate and runnable (you don't need to perform the live classroom demo). Keep plan.md synchronized with reality if commands or outputs changed.

Finish with a short summary of what you checked, anything you changed, and whether the full suite passes.
""",
    ),
    StagePrompts(
        number=1,
        title="Simulator",
        teach="Make the system feel alive: synthetic orders land under data/raw/.",
        plan=f"""\
The project foundation should already be in place. Next I want the system to feel alive with synthetic DashBite orders.

Inspect the repository and write the implementation plan to plan.md.

Include:
- what we're changing
- relevant files/interfaces
- architectural constraints
- automated test strategy
- a manual smoke test I can run live from the terminal after implementation

Non-negotiables:
- columns: order_id, timestamp, distance_km, prep_minutes, order_value, was_late
- runnable roughly as `python -m pipeline.simulator`, driven by shared batch size / poll interval
- live-feeling logs (“new orders arrived”); messy rows OK for later cleaning

For the Manual Smoke Test, make it visual: Terminal 1 runs the simulator; Terminal 2 does `ls -lh data/raw` and `head` on a generated CSV. Students should see “new orders arrived” and new files appearing. Include Ctrl+C to stop the loop.

{_PLAN_MD_SHAPE}

Do not implement the feature yet. Only write plan.md, then stop.
""",
        execute="""\
We're implementing Stage 1 of the DashBite pipeline (simulator / intake).

Inspect the repository and read plan.md first. Treat it as the architecture and behavior handoff from the planning agent — including the Manual Smoke Test.

Implement the planned intake process: periodically write synthetic orders under data/raw/ with order_id, timestamp, distance_km, prep_minutes, order_value, was_late; live-feeling logs; shared config for batch size / poll interval; runnable as `python -m pipeline.simulator` (or equivalent).

Keep this scoped to intake. Add/update relevant tests and run them as you work.

When implementation is complete, do not replace the manual smoke-test instructions in plan.md. Make sure they still match the actual commands and behavior. If details changed enough that the smoke test is no longer accurate, update only that section so it is runnable.
""",
        test="""\
Review the current Stage 1 simulator as if this were a PR you did not author.

Read plan.md first for intended behavior, architecture, automated tests, and the Manual Smoke Test.

Verify intake writes the expected columns under data/raw/, uses shared config, and doesn't reach into features/models/predictions. Strengthen unit/regression/integration coverage (seeded golden fixture + one-tick write). Run the full suite.

Inspect whether the documented Manual Smoke Test is still accurate and runnable. Keep plan.md synchronized if commands or outputs changed. Fix real bugs rather than softening asserts.

Summarize findings, changes, and suite status.
""",
    ),
    StagePrompts(
        number=2,
        title="Preprocess",
        teach="Turn raw orders into a simple feature table under data/features/.",
        plan=f"""\
Raw orders are already landing under data/raw/. Next we need a preprocessing stage that turns them into model-ready features.

Inspect the repository and write the implementation plan to plan.md.

Include:
- what we're changing
- relevant files/interfaces
- architectural constraints
- automated test strategy
- a manual smoke test I can run live from the terminal after implementation

Non-negotiables:
- clean invalid rows; derive hour and is_peak; write under data/features/; keep was_late
- stages stay independent and talk through data/

For the Manual Smoke Test, prefer separate terminals so the room sees Simulator → data/raw → Preprocess → data/features. Then `ls` / `head` a feature CSV and call out hour / is_peak / was_late. Include Ctrl+C for loops.

{_PLAN_MD_SHAPE}

Do not implement the feature yet. Only write plan.md, then stop.
""",
        execute="""\
We're implementing Stage 2 of the DashBite pipeline.

Inspect the repository and read plan.md first. Treat it as the architecture and behavior handoff from the planning agent.

Implement the planned preprocessing stage using the existing project patterns: clean obviously invalid rows, derive hour from timestamp and is_peak for lunch/dinner, write model-ready CSVs under data/features/, keep was_late. Communicate through data/ rather than importing another stage's runtime logic.

Keep the change scoped, add/update the relevant tests, and run them as you work.

When implementation is complete, do not replace the manual smoke-test instructions in plan.md. Make sure they still match the actual commands and behavior. If implementation details changed enough that the documented smoke test is no longer accurate, update only that section so it is runnable.
""",
        test="""\
Review the current Stage 2 implementation as if this were a PR you did not author.

Read plan.md first to understand the intended behavior, architecture, automated test strategy, and manual smoke test.

Verify the implementation against that contract (invalid rows dropped; hour / is_peak / was_late; outputs under data/features/).

Run the automated tests and inspect whether the documented Manual Smoke Test is still accurate and runnable.

If implementation bugs exist, fix them rather than weakening legitimate tests. Keep plan.md synchronized with reality if commands or outputs changed.

Finish with a short summary of findings, changes, and suite status.
""",
    ),
    StagePrompts(
        number=3,
        title="Train",
        teach="Model write path: retrain on enough labels, publish checkpoints only.",
        plan=f"""\
Clean labeled features should already be showing up under data/features/. Next is the model's write path.

Inspect the repository and write the implementation plan to plan.md.

Include:
- what we're changing
- relevant files/interfaces
- architectural constraints
- automated test strategy
- a manual smoke test I can run live from the terminal after implementation

Non-negotiables:
- LogisticRegression on distance_km + prep_minutes
- versioned checkpoint under data/models/ (joblib OK) plus a small metrics sidecar
- threshold from TRAIN_EVERY_N_EVENTS
- train only publishes — never import, call, or wait on inference

For the Manual Smoke Test, make the classroom moment “Training published an artifact to disk.” Run enough data through to trigger a retrain (use a small TRAIN_EVERY_N_EVENTS if helpful for the demo), then `ls -lh data/models` and show the metrics sidecar. Do not involve inference yet.

{_PLAN_MD_SHAPE}

Do not implement the feature yet. Only write plan.md, then stop.
""",
        execute="""\
We're implementing Stage 3 of the DashBite pipeline (training / write path).

Inspect the repository and read plan.md first. Treat it as the architecture and behavior handoff from the planning agent — including the Manual Smoke Test.

Implement training: retrain after TRAIN_EVERY_N_EVENTS new labeled examples; publish a versioned checkpoint under data/models/ with a small metrics sidecar; LogisticRegression on distance_km + prep_minutes. Training is only a publisher — must not import, call, or wait on inference.

Keep the change scoped, add/update relevant tests, and run them as you work.

When implementation is complete, do not replace the manual smoke-test instructions in plan.md. Make sure they still match the actual commands and behavior. If details changed enough that the smoke test is no longer accurate, update only that section so it is runnable.
""",
        test="""\
Review the current Stage 3 training implementation as if this were a PR you did not author.

Read plan.md first for intended behavior, architecture, automated tests, and Manual Smoke Test.

Verify retrain trigger, checkpoint + metrics under data/models/, LogisticRegression features, and hard isolation from inference. Strengthen coverage, run the full suite, fix real bugs.

Confirm the documented Manual Smoke Test is still accurate and runnable (artifact-on-disk demo, not inference). Sync plan.md if commands changed.

Summarize findings, changes, and suite status.
""",
    ),
    StagePrompts(
        number=4,
        title="Infer",
        teach="Model read path: separate consumer of the newest checkpoint on disk.",
        plan=f"""\
Training should already be publishing versioned checkpoints under data/models/, with features under data/features/. I want inference as a completely separate consumer of those artifacts.

Inspect the repository and write the implementation plan to plan.md.

Include:
- what we're changing
- relevant files/interfaces
- architectural constraints
- automated test strategy
- a manual smoke test I can run live from the terminal after implementation

Non-negotiables:
- newest checkpoint on disk; predictions under data/predictions/ with order_id, late_probability, predicted_late, checkpoint_id
- never import training or trigger retraining
- wait cleanly if no checkpoint exists

For the Manual Smoke Test, this is the strongest classroom beat. Prefer separate terminals. Show inference finding a checkpoint, scoring features, and writing predictions (`ls` / `head` under data/predictions/). Design it so the instructor can prove “Training does not need to be running”: create a checkpoint, stop training, keep/start inference, process another batch, show scoring still works from the artifact on disk.

{_PLAN_MD_SHAPE}

Do not implement the feature yet. Only write plan.md, then stop.
""",
        execute="""\
We're implementing Stage 4 of the DashBite pipeline (inference / read path).

Inspect the repository and read plan.md first. Treat it as the architecture and behavior handoff from the planning agent — including the Manual Smoke Test that proves train/infer isolation.

Build inference as a completely independent consumer: newest checkpoint on disk; score new feature rows; write order_id, late_probability, predicted_late, checkpoint_id under data/predictions/. If training isn't running, keep using the latest checkpoint; if none exists, wait cleanly. Do not import training or trigger retraining.

Keep the change scoped, add/update relevant tests, and run them as you work.

When implementation is complete, do not replace the manual smoke-test instructions in plan.md. Make sure they still match the actual commands and behavior. If details changed enough that the smoke test is no longer accurate, update only that section so it is runnable.
""",
        test="""\
Review the current inference stage as if this were a PR you did not author.

Read plan.md first to understand the intended behavior, architecture, automated test strategy, and manual smoke test — especially the isolation demo.

Verify:
- newest checkpoint selection
- clean behavior when no checkpoint exists
- predictions under data/predictions/ with the expected fields
- inference does not import or trigger training
- inference can operate from an existing checkpoint when training isn't running

Add or improve unit, regression, and integration tests where meaningful. Run the full suite. Fix underlying bugs rather than weakening legitimate tests.

Inspect whether the documented Manual Smoke Test is still accurate and runnable. Keep plan.md synchronized if commands or outputs changed.

Finish with a short summary of what you checked, anything you changed, and whether the full suite passes.
""",
    ),
    StagePrompts(
        number=5,
        title="ML Dashboard",
        teach="Model Pulse: a lightweight view for someone watching the ML system.",
        plan=f"""\
Features and predictions should already be flowing under data/features/ and data/predictions/. I'd like a lightweight Model Pulse view for someone watching the ML system.

Inspect the repository and write the implementation plan to plan.md.

Include:
- what we're changing
- relevant files/interfaces
- architectural constraints
- automated test strategy
- a manual smoke test I can run live from the terminal after implementation

Non-negotiables:
- helpers for sample volume (from features) and a score summary (from late_probability)
- sparse Streamlit page; dashboards consume data/, don't own pipeline logic
- no business/ops KPIs in this stage

For the Manual Smoke Test, launch Streamlit with the project's actual command (e.g. whatever Makefile/README already use). Students should visibly see sample volume, score summary, and one or two charts. Keep enough terminal output to show Streamlit is reading existing pipeline artifacts.

{_PLAN_MD_SHAPE}

Do not implement the feature yet. Only write plan.md, then stop.
""",
        execute="""\
We're implementing Stage 5 of the DashBite pipeline (ML / Model Pulse dashboard).

Inspect the repository and read plan.md first. Treat it as the architecture and behavior handoff from the planning agent — including the Manual Smoke Test.

Build pure helpers for sample volume and late_probability score summary, plus a sparse Streamlit page that reads data/features/ and data/predictions/. Leave ops KPIs for the next stage.

Keep the change scoped, add/update relevant tests (helpers especially), and run them as you work.

When implementation is complete, do not replace the manual smoke-test instructions in plan.md. Make sure they still match the actual commands and behavior. If details changed enough that the smoke test is no longer accurate, update only that section so it is runnable.
""",
        test="""\
Review the current Stage 5 ML dashboard as if this were a PR you did not author.

Read plan.md first for intended behavior, architecture, automated tests, and Manual Smoke Test.

Verify sample volume / score-summary helpers and that the UI only consumes existing artifacts. Strengthen helper tests, run the full suite, fix real issues.

Confirm the documented Manual Smoke Test (Streamlit launch + what to watch for) is still accurate. Sync plan.md if commands changed.

Summarize findings, changes, and suite status.
""",
    ),
    StagePrompts(
        number=6,
        title="Business Dashboard",
        teach="Ops Control: same pipeline, different audience — late rate and at-risk value.",
        plan=f"""\
Same underlying pipeline, different audience. Model Pulse should already exist; next is a simple Ops Control view beside it.

Inspect the repository and write the implementation plan to plan.md.

Include:
- what we're changing
- relevant files/interfaces
- architectural constraints
- automated test strategy
- a manual smoke test I can run live from the terminal after implementation

Non-negotiables:
- late_rate from labeled features
- at-risk order value (sum of order_value where predicted_late)
- keep Model Pulse intact; dashboards still only read data/

For the Manual Smoke Test, launch or refresh the Streamlit view and show late rate + at-risk order value. Emphasize it reads the same pipeline outputs as Model Pulse for a different audience.

{_PLAN_MD_SHAPE}

Do not implement the feature yet. Only write plan.md, then stop.
""",
        execute="""\
We're implementing Stage 6 of the DashBite pipeline (business / Ops Control dashboard).

Inspect the repository and read plan.md first. Treat it as the architecture and behavior handoff from the planning agent — including the Manual Smoke Test.

Add late_rate and at-risk order value with an Ops Control view beside Model Pulse. Don't break Model Pulse. Dashboards read data/; they don't own the pipeline.

Keep the change scoped, add/update relevant tests, and run them as you work.

When implementation is complete, do not replace the manual smoke-test instructions in plan.md. Make sure they still match the actual commands and behavior. If details changed enough that the smoke test is no longer accurate, update only that section so it is runnable.
""",
        test="""\
Review the current Stage 6 business dashboard as if this were a PR you did not author — final gate for the demo pipeline.

Read plan.md first for intended behavior, architecture, automated tests, and Manual Smoke Test.

Verify late_rate / at-risk helpers, Model Pulse still healthy, dashboards remain thin consumers. Strengthen coverage, run the full suite, fix real bugs.

Confirm the documented Manual Smoke Test is still accurate and runnable. Sync plan.md if commands changed. A short README note on running stages separately is a nice extra if missing.

Finish with a wrap-up of what you verified, what you changed, and whether the full suite passes.
""",
    ),
)
