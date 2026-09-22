"""Stage metadata and Think it through → Build it → Check it prompts for the live demo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StagePrompts:
    number: int
    title: str
    teach: str
    plan: str  # Think it through
    execute: str  # Build it
    test: str  # Check it


BASE_PLAN_TITLE = "Base plan — Pipeline diagram"
BASE_PLAN_TEACH = (
    "Warm up together: get the same mental model on one diagram before anyone touches code."
)
BASE_PLAN = """\
We're about to build a small ML pipeline together. Before we touch code, help me sketch the system so everyone in the room has the same mental model.

The product story is DashBite: food-delivery orders come in, and we want to predict whether an order will be late. Keep the raw fields short — order_id, timestamp, distance_km, prep_minutes, order_value, was_late.

Architecturally I want something modular and demo-friendly:
- separate stages that feel like separate processes
- they hand off through folders under data/, not by importing each other
- training publishes versioned checkpoints; inference is a separate consumer of the newest checkpoint on disk
- if training is down, inference should still work off whatever model is already there
- a couple of lightweight dashboards that read existing outputs rather than owning pipeline logic
- no containers, Kafka, Spark, etc. — plain Python and files are enough

Sketch a Mermaid flowchart (left-to-right is fine) that captures that story, including the train write path and the infer read path. Then give me a few short bullets on the teaching beats we should keep repeating as we build.

Don't create files yet — just the diagram and the shared picture for the room.
"""


STAGES: tuple[StagePrompts, ...] = (
    StagePrompts(
        number=0,
        title="Skeleton",
        teach="Smallest foundation: shared config, data folders, and a pytest gate.",
        plan="""\
We have the big picture. Let's put down the smallest foundation we need before building anything interesting.

I want a tiny project skeleton we can grow into: a pipeline package with shared config and path helpers, the usual data/ folders for handoffs, and a pytest setup with unit / regression / integration so every later stage has a gate.

Shared config should cover things like how often we retrain and batch size, preferably overridable from the environment. Beyond that, use your judgment for what's essential vs. premature.

Take a look at what we already have (likely almost nothing) and propose the smallest clean foundation. Before changing anything, walk me through what you'd add and how you'd smoke-test it.
""",
        execute="""\
Yep, that sounds good. Go ahead and build it.

Keep the change scoped to this foundation stage — no simulator or model yet. Reuse whatever tiny bits already exist, and run a quick import / pytest sanity check as you work.
""",
        test="""\
Before we move on, review what you just built like you would before opening a PR.

Make sure we have useful unit, regression, and integration coverage for the skeleton — config, paths, data dirs. Run the full suite too. If something's awkward, fix the design rather than weakening the tests.

Then give me a short summary of what you verified.
""",
    ),
    StagePrompts(
        number=1,
        title="Simulator",
        teach="Make the system feel alive: synthetic orders land under data/raw/.",
        plan="""\
The foundation is in place. Now I want the system to actually feel alive.

Next up is a small intake process that periodically writes synthetic DashBite orders into data/raw/. Enough columns for the rest of the pipeline — ids, timestamp, distance, prep time, order value, late label. Logs should feel like “new orders arrived,” not like we're dumping batch files. It's fine if some rows are messy; preprocess can clean them later.

Look at the repo first and propose the smallest simulator that fits what we already have. We're not doing preprocess or training yet.

Before changing anything, walk me through what you'd do and how you'd test it.
""",
        execute="""\
That matches what I had in mind. Build it.

Stay on intake only — write under data/raw/, reuse shared config/paths, and run the relevant tests as you go.
""",
        test="""\
Before we move on, review the simulator like a pre-PR check.

I want useful unit, regression, and integration coverage for this stage — columns/ranges, a seeded golden fixture, and proof that a tick lands a file under data/raw/. Run the full suite so we didn't break Stage 0. Fix real issues instead of softening asserts.

Then summarize what you verified.
""",
    ),
    StagePrompts(
        number=2,
        title="Preprocess",
        teach="Turn raw orders into a simple feature table under data/features/.",
        plan="""\
Raw orders are coming in now. Next I want to turn them into something the model can actually use.

Take a look at what we already have and propose the smallest sensible preprocessing stage. We need to clean obviously bad rows, derive a couple of useful features, and write the result under data/features/ — including the late label so training can use it later. A lightweight quality log is nice if it helps dashboards, but don't overbuild.

Keep it simple for the demo. We're not doing training yet. Stages should keep talking through files under data/.

Before changing anything, tell me what you'd add or modify and how you'd test it.
""",
        execute="""\
Yep, that sounds good. Go ahead and build it.

Keep the change scoped to preprocess, reuse the path/config pieces we already have, and run the relevant tests as you work.
""",
        test="""\
Before we move on, review preprocess like you would before a PR.

Cover the cleaning + feature behavior with unit/regression/integration tests, and run the full suite so Stages 0–1 still pass. If something fails, fix the underlying issue rather than watering down the tests.

Short summary of what you verified, please.
""",
    ),
    StagePrompts(
        number=3,
        title="Train",
        teach="Model write path: retrain on enough labels, publish checkpoints only.",
        plan="""\
We have labeled feature rows now. Let's add the model's write path.

I want the simplest training process that makes sense for this demo. It should retrain after enough new labeled examples and publish a versioned model artifact under data/models/ that another process can consume independently. Train should only write — it shouldn't import or call inference, and it shouldn't need scoring to be running.

Keep the model intentionally boring; the architecture is what we care about. Look at the repo and propose the smallest clean approach.

Before changing anything, walk me through what you'd do.
""",
        execute="""\
Love it — especially keeping train as a pure publisher. Build it.

Scoped to the training stage only. Reuse existing config/feature conventions, and run tests as you go.
""",
        test="""\
Pre-PR pass on training, please.

Useful unit/regression/integration coverage for the retrain trigger and checkpoint publish path, plus a check that train stays decoupled from infer. Run the full suite. Fix real breakage; don't weaken tests to get green.

Then a short summary of what you verified.
""",
    ),
    StagePrompts(
        number=4,
        title="Infer",
        teach="Model read path: separate consumer of the newest checkpoint on disk.",
        plan="""\
We have training producing checkpoints now. I want inference to be a completely separate consumer of those checkpoints.

Think through how you'd add that without coupling inference to the training process. If training is down, inference should still be able to use the latest model on disk. If no model exists yet, it should just wait cleanly. Score new feature rows and write predictions under data/predictions/ with enough columns that dashboards can use later.

Look at the repo first and walk me through the change you'd make. Don't implement it yet.
""",
        execute="""\
That separation is exactly what I want. Build it.

Keep infer as a read-only consumer of checkpoints. Run the relevant tests while you work.
""",
        test="""\
Before we move on, review inference like a careful pre-PR.

I care a lot about isolation here: newest-checkpoint selection, clean wait when nothing's on disk yet, predictions landing in the right place, and hard proof that infer doesn't import or depend on train being alive. Full suite green for everything so far. Fix underlying issues if something fails.

Then tell me briefly what you verified.
""",
    ),
    StagePrompts(
        number=5,
        title="ML Dashboard",
        teach="Model Pulse: a lightweight view for someone watching the ML system.",
        plan="""\
Predictions are flowing. I'd like a lightweight view for someone watching the ML system.

Propose the smallest Model Pulse-style dashboard that reads the outputs we already have under data/features/ and data/predictions/. Prefer pure helpers we can unit-test, with a sparse Streamlit page on top — volume and score shape are enough. Dashboards should consume existing outputs, not own pipeline logic.

We're not building the business/ops view yet.

Take a look at the repo and walk me through what you'd add before changing anything.
""",
        execute="""\
That keeps it suitably thin. Go ahead and build it.

ML monitoring only — leave ops KPIs for the next stage. Run relevant tests as you work.
""",
        test="""\
Pre-PR review on the ML dashboard helpers/page wiring.

Useful unit/regression/integration coverage on the metric helpers (browser UI itself doesn't need automation). Full suite still green. Fix real issues rather than softening asserts.

Short summary of what you checked.
""",
    ),
    StagePrompts(
        number=6,
        title="Business Dashboard",
        teach="Ops Control: same pipeline, different audience — late rate and at-risk value.",
        plan="""\
Same underlying pipeline, different audience. Let's add a simple operational view.

I want an Ops Control-style page beside Model Pulse: late rate and something like orders-at-risk value, derived from the features/predictions we already produce. Keep Model Pulse intact. Still: dashboards read data/, they don't become the pipeline.

Look at what Stage 5 left us and propose the smallest clean addition. Before changing anything, walk me through it.
""",
        execute="""\
Yep — build the ops view.

Stay scoped to business KPIs alongside Model Pulse. Reuse loading patterns we already have, and run tests as you go.
""",
        test="""\
Final pre-PR pass for the demo pipeline.

Useful coverage for the ops helpers and handoff, full suite green across everything we've built. If something's off, fix the cause. Optionally leave a short README note on running stages in separate terminals and gating on pytest.

Then give me a brief wrap-up of what you verified — that's our cue the room can celebrate green.
""",
    ),
)
