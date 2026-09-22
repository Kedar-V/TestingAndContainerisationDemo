"""Stage metadata and Plan → Execute → Test agent prompts for the live demo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StagePrompts:
    number: int
    title: str
    teach: str
    plan: str
    execute: str
    test: str


BASE_PLAN_TITLE = "Base plan — Pipeline diagram"
BASE_PLAN_TEACH = (
    "Warm up: sketch the whole DashBite story on one diagram before anyone writes code."
)
BASE_PLAN = """\
We're kicking off a live build of DashBite — a small food-delivery app that predicts whether an order will be late.

Before we write any code, help us think through the shape of the system out loud.

Here's the story we want to tell:
Orders flow in, get cleaned into features, a tiny model trains when there's enough labeled data, a separate process scores new orders with the newest checkpoint, and two lightweight dashboards watch the pipeline. Stages talk through folders under data/ — not through importing each other. Train only writes checkpoints; infer only reads the newest one. No containers, no Kafka, nothing fancy — modular Python and CSVs are enough.

Please sketch a Mermaid flowchart (left-to-right is fine) that shows roughly:

Simulator → data/raw → Preprocess → data/features
features → Train → data/models (write checkpoint only)
features → Infer, and models → Infer (read newest checkpoint)
Infer → data/predictions
features and predictions → Dashboards

In a few short bullets, call out the teaching beats: separate processes, train/infer isolation, and that after each stage we run the full pytest suite before moving on.

Don't create files or implement anything yet — just the diagram and the story we can agree on as a room.
"""


STAGES: tuple[StagePrompts, ...] = (
    StagePrompts(
        number=0,
        title="Skeleton",
        teach="Lay down the project bones: folders, shared config, and a pytest gate.",
        plan="""\
Great — we have the big picture. Now Stage 0: the skeleton.

We're standing up a brand-new DashBite project. Plan (don't code yet) the smallest foundation we need so later stages have somewhere to live:

- a pipeline package with shared config (TRAIN_EVERY_N_EVENTS default 2000, BATCH_SIZE default 50, readable from env) and path helpers for data/raw, features, models, predictions, quality
- those data folders ready to go
- a simple test layout: unit / regression / integration / fixtures, with pytest markers wired

Keep it to the essentials. Skip the simulator, model, and dashboards for now. Tell us which files you'd create and what each one is responsible for.
""",
        execute="""\
Let's build Stage 0 from that plan.

Create the skeleton: pipeline/config.py and pipeline/paths.py, the data/ folders, tests/ with unit·regression·integration·fixtures, and pytest.ini markers. A thin requirements.txt and a tiny README are fine if we need them to run.

Stay on Stage 0 only — no simulator or ML yet. When you're done, we should be able to import load_config and create the data dirs cleanly.
""",
        test="""\
Time to lock Stage 0 in with tests.

Add a few small ones: config defaults / env overrides, path helpers, and ensure_data_dirs in a temp folder. One clear story per test is enough.

Then run the full pytest suite and stop once it's green — we don't start Stage 1 until then.
""",
    ),
    StagePrompts(
        number=1,
        title="Simulator",
        teach="Make the demo feel live: synthetic orders arrive in data/raw/.",
        plan="""\
Stage 0 is green. Next story beat: orders start showing up.

Plan Stage 1 — the simulator. Every couple of seconds it should drop a CSV of synthetic DashBite orders into data/raw/ (order_id, timestamp, distance_km, prep_minutes, order_value, was_late). Logs should feel live (“new orders arrived”), not talk about batches. Reuse our shared config for batch size and poll interval; it's okay if some rows are messy so preprocess has something to clean later.

We'll run it as `python -m pipeline.simulator`. Don't plan preprocess, train, or dashboards yet — just intake.
""",
        execute="""\
Implement the simulator we just planned.

A poll loop that writes CSVs under data/raw/, with a seeded generator so tests can be deterministic, and a log line when new orders arrive. Optional corruption rate is fine. Don't touch features, models, or predictions.

When it runs, data/raw/ should start filling up.
""",
        test="""\
Prove the intake works, then keep the whole suite green.

Unit: a batch has the right columns and sensible ranges.
Regression: seeded output matches a small golden CSV in fixtures.
Integration: one tick writes under data/raw/ (temp dirs are fine).

Run full pytest — Stages 0 and 1 must both pass before we move on.
""",
    ),
    StagePrompts(
        number=2,
        title="Preprocess",
        teach="Clean the raw feed and shape a simple feature table.",
        plan="""\
Orders are landing. Stage 2 is where we turn raw CSVs into something a model can eat.

Plan preprocess: watch data/raw/, drop invalid rows, add just one or two features — hour from timestamp and/or is_peak for lunch/dinner — and write to data/features/ (keep was_late for training). A small quality log under data/quality/ is welcome if it helps the dashboards later.

Runnable as `python -m pipeline.preprocess`. Still no training or inference.
""",
        execute="""\
Build preprocess from that plan.

Poll new raw files, clean them, add hour / is_peak, write feature CSVs. Leave training and predictions alone, and don't change how the simulator behaves from the outside.

When raw files appear, features should follow.
""",
        test="""\
Gate Stage 2.

Unit: drop-invalid + hour / is_peak.
Regression: fixed raw fixture → golden features CSV.
Integration: raw → features, and older tests still pass.

Full pytest green for Stages 0–2 before Stage 3.
""",
    ),
    StagePrompts(
        number=3,
        title="Train",
        teach="Retrain when enough labels arrive — write checkpoints, nothing else.",
        plan="""\
We have features. Stage 3 is the write path for the model.

Plan training: count new labeled rows since the last train; when we hit TRAIN_EVERY_N_EVENTS, fit a tiny LogisticRegression on distance_km + prep_minutes and write a timestamped checkpoint (and a little metrics JSON) under data/models/. Training owns that folder — it never imports or calls inference, never blocks on scoring.

Runnable as `python -m pipeline.train`. Infer and dashboards wait for later.
""",
        execute="""\
Implement training as planned.

Poll features, retrain when enough new labels arrive, write checkpoint_*.joblib + metrics, and remember train state so we don't retrain every tick. Do not import infer or write predictions.

We're done for this stage when a checkpoint shows up after enough labeled rows.
""",
        test="""\
Lock the train path.

Unit: retrain only when count ≥ N; checkpoint gets written.
Regression: fixed features → stable metrics shape with a seed.
Integration: features → checkpoint, and train does not import infer.

Full pytest for Stages 0–3 must be green.
""",
    ),
    StagePrompts(
        number=4,
        title="Infer",
        teach="Score with the newest checkpoint — no dependency on train being alive.",
        plan="""\
Checkpoint exists. Stage 4 is the read path — and this is the isolation beat of the lesson.

Plan inference: on each poll, pick the newest checkpoint in data/models/, score new feature rows, write order_id, late_probability, predicted_late, checkpoint_id to data/predictions/. If there's no checkpoint yet, log once and wait — don't crash, don't kick off training, don't import train.

Runnable as `python -m pipeline.infer`.
""",
        execute="""\
Build infer from that plan.

Newest-checkpoint selection, score unscored rows, write predictions CSVs, skip cleanly when no model is there yet. Never import train or write checkpoints.

Predictions should grow whenever we have both a checkpoint and new features.
""",
        test="""\
Prove infer — and that it stays independent of train.

Unit: newest checkpoint; clean skip when missing.
Regression: fixed features + checkpoint → golden predictions (tolerance OK).
Integration: writes under data/predictions/; infer does not import train; older stages still green.

Full pytest for Stages 0–4.
""",
    ),
    StagePrompts(
        number=5,
        title="ML Dashboard",
        teach="Model Pulse: a sparse view of volume and scores.",
        plan="""\
Pipeline is scoring. Stage 5 is for the ML audience — Model Pulse.

Plan a thin Streamlit page plus pure helpers we can unit-test: sample volume from features, a simple score summary from predictions. One or two charts is enough. Read from data/features/ and data/predictions/ only.

Leave the business / Ops Control page for Stage 6.
""",
        execute="""\
Implement Model Pulse.

Helpers like sample_volume and score_summary, and a sparse Streamlit page that shows them. Keep business KPIs (late rate, at-risk value) out of this stage.

When features and predictions exist, the page should light up.
""",
        test="""\
Test the helpers, not the browser.

Unit + regression on volume / score numbers from fixtures; a small integration read from a temp data tree shaped like earlier stages.

Full pytest for Stages 0–5 before we add Ops Control.
""",
    ),
    StagePrompts(
        number=6,
        title="Business Dashboard",
        teach="Ops Control: late rate and orders at risk — same data, different audience.",
        plan="""\
Same pipeline, different audience. Stage 6 is Ops Control.

Plan helpers for late rate and at-risk order value (orders predicted late), plus a second Streamlit view beside Model Pulse. Reuse how we load features / predictions. Still keep KPIs to those two ideas — don't redesign Model Pulse.
""",
        execute="""\
Add the business dashboard.

biz_metrics helpers and an Ops Control page for late rate and at-risk value. Don't break Model Pulse.

When you're done, ops can read the same folders the ML page does.
""",
        test="""\
Final gate for the demo pipeline.

Unit + regression on late rate and at-risk helpers; integration across the features/predictions handoff; full suite Stages 0–6 green.

Optionally leave a short README note on how to run each stage in its own terminal and re-run pytest after every stage. Then we're done — celebrate the green suite.
""",
    ),
)
