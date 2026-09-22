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


STAGES: tuple[StagePrompts, ...] = (
    StagePrompts(
        number=0,
        title="Skeleton",
        teach="Smallest foundation: shared config, data folders, and a pytest gate.",
        plan="""\
We're starting DashBite from an empty-ish repo and need the smallest foundation before anything interesting.

Inspect whatever is already there first so the proposal fits reality.

I want a `pipeline` package with shared config and path helpers, data folders for raw / features / models / predictions / quality, and a pytest layout with unit / regression / integration markers.

Non-negotiables for this demo:
- config defaults include TRAIN_EVERY_N_EVENTS=2000 and BATCH_SIZE=50, overridable from the environment
- path helpers that resolve those data/ subfolders and can create them

Don't implement the code yet. Write your recommended approach and how you'd smoke-test it into plan.md (replace whatever is there — this stage owns that file now). Then stop so an implementer can pick it up.
""",
        execute="""\
We're adding the Stage 0 skeleton for the DashBite pipeline.

Start by reading plan.md — that was written by the architect chat for this stage. Treat it as the agreed approach unless something in the repo clearly conflicts; if it conflicts, say so briefly and follow the safer path that still meets the constraints below.

Inspect the current repo and fit this into whatever is already there.

Build the foundation: a `pipeline` package with shared config and path helpers, the data/ folders (raw, features, models, predictions, quality), and a pytest setup with unit / regression / integration markers. Config defaults should include TRAIN_EVERY_N_EVENTS=2000 and BATCH_SIZE=50, overridable from the environment.

Keep stages independent later by communicating through data/ — this stage is only the bones. No simulator or model yet.

Keep the implementation small. Implement it and run the relevant tests when you're done.
""",
        test="""\
Review the current Stage 0 skeleton as if this were a PR you hadn't worked on.

Inspect both the implementation and existing tests. You can skim plan.md for intent, but judge the code and tests on their own merits.

We expect shared config (including TRAIN_EVERY_N_EVENTS and BATCH_SIZE), path helpers for the data/ handoff folders, and a pytest layout with unit / regression / integration markers.

Add or improve tests where they provide meaningful coverage. Run the full pytest suite. If something fails, fix the underlying implementation problem rather than weakening a legitimate test.

Finish with a short summary of what you checked, anything you changed, and whether the full suite passes.
""",
    ),
    StagePrompts(
        number=1,
        title="Simulator",
        teach="Make the system feel alive: synthetic orders land under data/raw/.",
        plan="""\
The project foundation should already be in place. Next I want the system to feel alive with synthetic DashBite orders.

Inspect the current repo first so your proposal fits existing config/path patterns.

We need a small intake process that periodically writes CSVs under data/raw/. Logs should feel like “new orders arrived,” not like we're dumping batch files. Messy rows are fine — preprocess can clean them later.

Non-negotiables:
- columns: order_id, timestamp, distance_km, prep_minutes, order_value, was_late
- runnable roughly as `python -m pipeline.simulator`, driven by shared batch size / poll interval

We're not doing preprocess or training yet. Don't implement code — write the approach and how you'd test it into plan.md for this stage, then stop.
""",
        execute="""\
We're adding the simulator / intake stage to the DashBite pipeline.

Read plan.md first — that's the architect's plan for this stage. Follow it unless the repo makes something impossible; call out any deviation briefly.

The skeleton (config, paths, data folders, pytest) should already exist. Inspect the repo and follow those conventions.

Build a process that periodically writes synthetic orders under data/raw/ with columns order_id, timestamp, distance_km, prep_minutes, order_value, was_late. Prefer live-feeling logs (“new orders arrived”). A bit of intentional messiness in some rows is fine. Drive batch size and poll interval from shared config, and make it runnable as `python -m pipeline.simulator` (or equivalent).

Keep this scoped to intake — don't implement preprocess or training. Run the relevant tests when you're done.
""",
        test="""\
Review the current Stage 1 simulator as if this were a PR you hadn't worked on.

Inspect the implementation and existing tests. plan.md is optional context for intent only.

Expected behavior: synthetic orders land under data/raw/ with order_id, timestamp, distance_km, prep_minutes, order_value, was_late; intake is driven by shared config; it doesn't reach into features/models/predictions.

Verify useful unit, regression, and integration coverage — including a seeded golden fixture and proof that a tick writes under data/raw/. Run the full suite so earlier stages still pass. Fix real bugs instead of softening asserts.

Finish with a short summary of what you checked, what you changed, and suite status.
""",
    ),
    StagePrompts(
        number=2,
        title="Preprocess",
        teach="Turn raw orders into a simple feature table under data/features/.",
        plan="""\
Raw orders are already landing under data/raw/. Next we need a preprocessing stage that turns them into model-ready features.

Inspect the current repo first so your proposal fits what already exists.

We need obviously invalid rows cleaned, hour and is_peak derived, and the result written under data/features/. Keep was_late because training will need it later. A lightweight quality log is nice but optional.

Keep this small. We're not building training yet. Stages should stay independent and talk through data/.

Don't implement yet. Capture your recommended approach and tests in plan.md, then stop for the implementer.
""",
        execute="""\
We're adding the preprocessing stage to the DashBite pipeline.

Read plan.md first and treat it as the agreed design for this stage. If something in the repo conflicts, note it and stay aligned with the constraints below.

Raw synthetic orders are already being written under data/raw/. Inspect the repo and fit this into the patterns that are already there.

Build a preprocessing process that cleans obviously invalid rows, derives hour from the timestamp and an is_peak feature for lunch/dinner periods, and writes model-ready CSVs under data/features/. Keep was_late because training will use it later.

Keep stages independent and communicate through data/ rather than importing another stage's runtime logic.

Keep the implementation small and consistent with the existing config/path helpers. Run the relevant tests when you're done.
""",
        test="""\
Review the current Stage 2 preprocess implementation as if this were a PR you hadn't worked on.

Inspect both the code and the tests. plan.md is background only.

We care that invalid rows are dropped, hour and is_peak exist, was_late is preserved, and outputs land under data/features/ without reaching into train/infer.

Add or improve unit, regression, and integration coverage where it's meaningful. Run the full pytest suite. If something fails, fix the implementation rather than weakening a legitimate test.

Finish with a short summary of findings, changes, and whether the suite is green.
""",
    ),
    StagePrompts(
        number=3,
        title="Train",
        teach="Model write path: retrain on enough labels, publish checkpoints only.",
        plan="""\
Clean labeled features should already be showing up under data/features/. Next is the model's write path.

Inspect the repo first so the design fits existing conventions.

Training should retrain after enough new labeled examples and publish a versioned artifact under data/models/ that another process can consume on its own. Train only writes — it must not import, call, or wait on inference.

Non-negotiables:
- LogisticRegression on distance_km + prep_minutes
- checkpoint on disk (joblib is fine) plus a small metrics sidecar
- threshold from TRAIN_EVERY_N_EVENTS

Don't implement code. Write the plan into plan.md for this stage, then stop.
""",
        execute="""\
We're at the training stage of the DashBite pipeline. Clean labeled features are already being written under data/features/.

Read plan.md first — implement from that architect plan. Flag briefly if you must diverge.

Inspect the current repo and add the model's write path.

Training should retrain after TRAIN_EVERY_N_EVENTS new labeled examples and publish a versioned checkpoint under data/models/, with a small metrics sidecar. Use a simple LogisticRegression over distance_km and prep_minutes.

The important architecture constraint is that training is only a publisher. It must not import, call, or wait on inference.

Fit this into the existing project conventions, implement it, and run the relevant tests.
""",
        test="""\
Review the current Stage 3 training implementation as if this were a PR you hadn't worked on.

Inspect the code and tests. Use plan.md only as optional intent context.

Focus on the retrain trigger, checkpoint (+ metrics) publish under data/models/, LogisticRegression on distance_km + prep_minutes, and hard isolation from inference (no import/call/wait).

Strengthen unit, regression, and integration coverage where it helps. Run the full suite. Fix underlying bugs rather than weakening tests.

Summarize what you checked, what you changed, and pass/fail for the full suite.
""",
    ),
    StagePrompts(
        number=4,
        title="Infer",
        teach="Model read path: separate consumer of the newest checkpoint on disk.",
        plan="""\
Training should already be publishing versioned checkpoints under data/models/, with features under data/features/. I want inference as a completely separate consumer of those artifacts.

Inspect the repo first.

Inference must pick the newest checkpoint on disk, score new feature rows, and write under data/predictions/. If training is down, it should still use whatever checkpoint is already there. If none exists yet, wait cleanly — don't crash.

Non-negotiables:
- prediction columns: order_id, late_probability, predicted_late, checkpoint_id
- never import training or trigger retraining

Don't implement yet. Put the design and test ideas into plan.md, then stop.
""",
        execute="""\
We're adding inference to the DashBite pipeline. Training already publishes versioned model checkpoints under data/models/, and feature files arrive under data/features/.

Read plan.md first and implement from that plan. Call out any necessary deviations briefly.

Inspect the existing implementation as well.

Build inference as a completely independent consumer of those artifacts. It should select the newest checkpoint on disk, score new feature rows, and write order_id, late_probability, predicted_late, and checkpoint_id under data/predictions/.

If training isn't running, inference should continue using the latest checkpoint already on disk. If no checkpoint exists yet, it should wait cleanly rather than crash.

Do not import training or trigger retraining from inference.

Implement this using the project's existing patterns and run the relevant tests.
""",
        test="""\
Review the current inference stage as if this were a PR you hadn't worked on.

Inspect both the implementation and existing tests. plan.md is optional background.

The behavior we care most about is process isolation: inference should consume the newest checkpoint from data/models/ without importing or depending on the training process.

Verify:
- newest checkpoint selection
- clean behavior when no checkpoint exists
- predictions are written under data/predictions/
- expected prediction fields are present (order_id, late_probability, predicted_late, checkpoint_id)
- inference does not import or trigger training
- inference can operate using an existing checkpoint even if training isn't running

Add or improve unit, regression, and integration tests where they provide meaningful coverage.

Run the full pytest suite. If something fails, fix the underlying implementation problem rather than weakening a legitimate test.

Finish with a short summary of what you checked, anything you changed, and whether the full suite passes.
""",
    ),
    StagePrompts(
        number=5,
        title="ML Dashboard",
        teach="Model Pulse: a lightweight view for someone watching the ML system.",
        plan="""\
Features and predictions should already be flowing under data/features/ and data/predictions/. I'd like a lightweight Model Pulse view for someone watching the ML system.

Inspect the repo first.

Prefer pure helpers we can unit-test, with a sparse Streamlit page on top. Dashboards should consume existing outputs, not own pipeline logic.

Non-negotiables:
- helpers for sample volume (from features) and a score summary (from late_probability)
- we're not building the business/ops view in this stage

Don't implement yet. Write the approach into plan.md, then stop.
""",
        execute="""\
We're adding the ML monitoring dashboard (Model Pulse) to DashBite.

Read plan.md first and build from that architect plan.

Feature and prediction files should already exist under data/features/ and data/predictions/. Inspect the repo and fit into existing load/path patterns.

Build pure helpers for sample volume and a late_probability score summary, plus a sparse Streamlit page that reads those outputs. Dashboards consume data/ — they don't become the pipeline. Leave ops / business KPIs for the next stage.

Implement it and run the relevant tests (helpers especially).
""",
        test="""\
Review the current Stage 5 ML dashboard as if this were a PR you hadn't worked on.

Inspect helpers, page wiring, and tests. plan.md is optional intent context.

We expect sample volume and score-summary helpers backed by data/features/ and data/predictions/, without inventing pipeline logic in the UI.

Add meaningful unit/regression/integration coverage for the helpers (browser automation isn't required). Run the full suite; fix real issues rather than softening tests.

Summarize what you checked, changes made, and suite status.
""",
    ),
    StagePrompts(
        number=6,
        title="Business Dashboard",
        teach="Ops Control: same pipeline, different audience — late rate and at-risk value.",
        plan="""\
Same underlying pipeline, different audience. Model Pulse should already exist; next is a simple Ops Control view beside it.

Inspect what Stage 5 left in the repo.

Non-negotiables:
- late_rate from labeled features
- at-risk order value (sum of order_value where predicted_late)
- keep Model Pulse intact; dashboards still only read data/

Don't implement yet. Capture the plan in plan.md, then stop for the implementer.
""",
        execute="""\
We're adding the business / Ops Control dashboard to DashBite.

Read plan.md first and implement from it. Note briefly if you need to diverge.

Model Pulse and the upstream feature/prediction outputs should already be in place. Inspect the repo and reuse existing loading patterns.

Add late_rate and at-risk order value (sum of order_value where predicted_late), with an Ops Control view beside Model Pulse. Don't break or redesign Model Pulse. Dashboards read data/; they don't own the pipeline.

Implement it and run the relevant tests.
""",
        test="""\
Review the current Stage 6 business dashboard as if this were a PR you hadn't worked on — final gate for the demo pipeline.

Inspect implementation and tests. plan.md is optional background only.

We expect late_rate and at-risk order value helpers, Model Pulse still healthy, and dashboards remaining thin consumers of data/.

Strengthen coverage where useful, run the full suite across everything built so far, and fix underlying bugs rather than weakening tests. A short README note on running stages separately and gating on pytest is a nice extra if missing.

Finish with a wrap-up of what you verified, what you changed, and whether the full suite passes.
""",
    ),
)
