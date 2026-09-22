"""Stage metadata and Plan → Execute → Test agent prompts for the live demo."""

from __future__ import annotations

from dataclasses import dataclass

# Shared framing: attendees build from scratch, not from a completed solution repo.
EMPTY_REPO = (
    "Starting point: an EMPTY git repository (no pipeline code yet). "
    "Build everything from scratch in this repo. "
    "Do not assume a pre-built solution, reference implementation, or hidden starter files exist."
)


@dataclass(frozen=True)
class StagePrompts:
    number: int
    title: str
    teach: str
    plan: str
    execute: str
    test: str


# Kickoff prompt — high-level architecture before any stage work
BASE_PLAN_TITLE = "Base plan — Pipeline diagram"
BASE_PLAN_TEACH = (
    "Agree the modular layout with the room: stages, data folders, and "
    "train/infer isolation — before writing Stage 0 in an empty repo."
)
BASE_PLAN = f"""\
You are helping design DashBite — a late-delivery ML pipeline demo built one stage at a time with agents (plan → execute → test).

{EMPTY_REPO}

BASE PLAN ONLY — do not write implementation code, create files, or start Stage 0 yet.

Goal:
Produce a short high-level plan whose centerpiece is an architecture diagram of the modular pipeline (file-based handoffs, no containers). The room will then implement it stage-by-stage into this empty repo.

Use case:
- Predict whether a food-delivery order will be late (`was_late`: 0/1).
- Raw fields (keep short): order_id, timestamp, distance_km, prep_minutes, order_value, was_late.

Diagram requirements (Mermaid flowchart LR preferred):
Show this flow (node names can match):
  1_Simulator → data/raw → 2_Preprocess → data/features
  data/features → 3_Train → data/models  (label: write checkpoint only)
  data/features → 4_Infer
  data/models → 4_Infer  (label: read newest checkpoint)
  4_Infer → data/predictions
  data/features → 5_6_Dashboards
  data/predictions → 5_6_Dashboards

Teaching points the plan must state clearly:
1. Stages are separate Python modules/processes sharing folders under data/.
2. Train and infer are independent — neither imports/calls the other; only coupling is data/models/.
3. Train only writes checkpoints; infer only reads the newest checkpoint (skip if none).
4. After every stage: unit + regression + integration tests; full pytest must be green before the next stage.
5. Build order: Stage 0 skeleton → 1 simulator → 2 preprocess → 3 train → 4 infer → 5 ML dashboard → 6 business dashboard.

Constraints:
- No Docker, Kafka, Spark, MLflow, or drift libraries.
- Keep the plan concise: diagram + bullets (stack, handoffs, what NOT to build yet).
- Do not implement any stage in this response.

Output:
1. Mermaid flowchart (or equivalent ASCII) matching the flow above
2. A short bullet plan the room can agree on before Stage 0
"""


def _prior_stages_note(through: int) -> str:
    if through < 0:
        return EMPTY_REPO
    if through == 0:
        return (
            f"{EMPTY_REPO} "
            "In this session you already built Stage 0 only — that is all that should exist in the repo."
        )
    return (
        f"{EMPTY_REPO} "
        f"In this session you already built Stages 0–{through} from scratch — "
        "that is all that should exist; do not invent later-stage code early."
    )


STAGES: tuple[StagePrompts, ...] = (
    StagePrompts(
        number=0,
        title="Skeleton",
        teach="Project layout, shared config, and the pytest gate.",
        plan=f"""\
You are helping build DashBite — a late-delivery ML pipeline demo — one stage at a time.

{_prior_stages_note(-1)}

STAGE 0 — Skeleton (PLAN ONLY)
Do not write implementation code yet. Produce a short plan for Stage 0 only.

Context:
- Use case: predict whether a food-delivery order will be late (`was_late`: 0/1).
- Raw fields (keep short): order_id, timestamp, distance_km, prep_minutes, order_value, was_late.
- No Docker/containers. Modular Python packages coupled via folders under data/.

Plan must cover:
1. Package layout: pipeline/ with config.py and paths.py; empty placeholders for later stages is fine.
2. Data folders: data/raw, data/features, data/models, data/predictions, data/quality.
3. Shared Config: TRAIN_EVERY_N_EVENTS (default 2000), BATCH_SIZE (default 50), overridable via env.
4. Test harness: tests/unit, tests/regression, tests/integration, tests/fixtures + pytest markers.
5. Minimal project glue you will need from an empty repo: requirements.txt, pytest.ini, README stub OK.

Constraints:
- 1–2 features only for this stage.
- Do not implement simulator, preprocess, train, infer, or dashboards.
- End with: files to create, public APIs, and what NOT to touch.

Output: a concise bullet plan only.""",
        execute=f"""\
STAGE 0 — Skeleton (EXECUTE)
{_prior_stages_note(-1)}
Implement ONLY Stage 0 from the agreed plan. Do not implement later stages.

Requirements:
1. pipeline/config.py — frozen Config dataclass + load_config() from env
   (TRAIN_EVERY_N_EVENTS default 2000, BATCH_SIZE default 50).
2. pipeline/paths.py — helpers for data/raw, features, models, predictions, quality
   and ensure_data_dirs().
3. Create the data/ folder tree (gitkeep OK) and tests/unit|regression|integration|fixtures.
4. Wire pytest.ini with unit/regression/integration markers.
5. Add requirements.txt with the minimal deps you will need (e.g. pytest now; pandas/sklearn later is OK if listed).

Rules:
- No simulator, preprocess, train, infer, or dashboard code.
- Keep it tiny and importable: `from pipeline.config import load_config`.
- Create files fresh — do not look for or depend on a pre-existing solution tree.

Done when Stage 0 modules import cleanly and the project skeleton is in place.""",
        test=f"""\
STAGE 0 — Skeleton (TEST)
{_prior_stages_note(-1)}
Add the Stage 0 test gate, then run the full suite. Do not start Stage 1 until green.

Add:
1. Unit: config loads TRAIN_EVERY_N_EVENTS; required data dir helpers resolve.
2. Regression: default config values match a frozen expected dict.
3. Integration: ensure_data_dirs works in a temp workspace.

Then run: pytest
Must pass all unit + regression + integration tests for stages completed so far (0).

Rules:
- Keep each test tiny — one clear assertion story.
- Do not implement Stage 1.
- Stop and report when pytest is green.""",
    ),
    StagePrompts(
        number=1,
        title="Simulator",
        teach="Timed synthetic orders land in data/raw/ (“new orders arrived”).",
        plan=f"""\
You are continuing DashBite stage by stage in the same empty-started repo.

{_prior_stages_note(0)}

STAGE 1 — Simulator / Intake (PLAN ONLY)
Do not write implementation code yet. Produce a short plan for Stage 1 only.

Teach goal: produce data on a schedule into a landing zone.

Plan must cover:
1. Every few seconds, write a batch CSV of synthetic orders to data/raw/.
2. Columns: order_id, timestamp, distance_km, prep_minutes, order_value, was_late.
3. Log line like “new orders arrived” (live feel) — no “batch” jargon in user-facing logs.
4. Use shared Config for BATCH_SIZE and POLL_INTERVAL_SECONDS; optional CORRUPT_BATCH_RATE for bad rows later stages will clean.
5. Runnable as: python -m pipeline.simulator

Constraints:
- 1–2 features only.
- Do not implement preprocess, train, infer, or dashboards.
- File-based handoff only under data/raw/.

Output: concise bullet plan — files, APIs, poll loop, and what NOT to touch.""",
        execute=f"""\
STAGE 1 — Simulator (EXECUTE)
{_prior_stages_note(0)}
Implement ONLY Stage 1 from the agreed plan. Do not implement later stages.

Requirements:
1. pipeline/simulator.py — poll loop that writes CSV files under data/raw/.
2. Each tick: BATCH_SIZE synthetic orders with required columns and valid ranges.
3. Log “new orders arrived” (or similar). Support CORRUPT_BATCH_RATE for occasional NaN/bad types.
4. Entrypoint: python -m pipeline.simulator using shared config/paths.

Rules:
- Do not read or write data/features, models, or predictions.
- Do not implement preprocess/train/infer/dashboard.
- Keep generation deterministic enough to seed for tests (RANDOM_SEED).

Done when data/raw/ fills while the simulator runs.""",
        test=f"""\
STAGE 1 — Simulator (TEST)
{_prior_stages_note(0)}
Add Stage 1 tests, then run the full suite. Do not start Stage 2 until green.

Add:
1. Unit: one batch has required columns and valid ranges.
2. Regression: seeded generator matches a golden small CSV under tests/fixtures/.
3. Integration: running one tick writes a file under data/raw/ (use temp dirs).

Then run: pytest
Must pass ALL tests from stages 0 and 1.

Rules:
- Tiny tests; reuse fixtures where helpful.
- Do not implement Stage 2.
- Stop when the full suite is green.""",
    ),
    StagePrompts(
        number=2,
        title="Preprocess",
        teach="Clean raw CSVs and write feature tables to data/features/.",
        plan=f"""\
You are continuing DashBite stage by stage in the same empty-started repo.

{_prior_stages_note(1)}

STAGE 2 — Preprocess (PLAN ONLY)
Do not write implementation code yet. Produce a short plan for Stage 2 only.

Teach goal: clean raw data and create a feature table for ML.

Plan must cover:
1. Read new raw CSVs from data/raw/ → drop rows with missing/invalid values.
2. Add one or two columns only: hour from timestamp and/or is_peak (lunch/dinner window).
3. Write to data/features/ (keep was_late for training).
4. Optionally log per-batch throughput / field failures to data/quality/ for later dashboards.
5. Runnable as: python -m pipeline.preprocess

Constraints:
- 1–2 feature columns only — do not expand the schema.
- Do not implement train, infer, or dashboards.
- Earlier stages must keep working via file handoffs.

Output: concise bullet plan — files, clean rules, feature defs, handoff, what NOT to touch.""",
        execute=f"""\
STAGE 2 — Preprocess (EXECUTE)
{_prior_stages_note(1)}
Implement ONLY Stage 2 from the agreed plan. Do not implement later stages.

Requirements:
1. pipeline/preprocess.py — poll for new raw CSVs, drop invalid rows, add hour / is_peak.
2. Write feature CSVs under data/features/ including was_late.
3. Optionally append batch quality metrics to data/quality/.
4. Entrypoint: python -m pipeline.preprocess using shared config/paths.

Rules:
- Do not train models or write predictions.
- Do not change the simulator’s public behavior.
- Keep feature engineering to hour + is_peak only.

Done when feature CSVs appear as raw files land.""",
        test=f"""\
STAGE 2 — Preprocess (TEST)
{_prior_stages_note(1)}
Add Stage 2 tests, then run the full suite. Do not start Stage 3 until green.

Add:
1. Unit: drop-invalid + feature columns (hour / is_peak).
2. Regression: fixed raw fixture → golden features CSV.
3. Integration: raw landing → features output; Stage 0–1 tests still pass.

Then run: pytest
Must pass ALL tests from stages 0–2.

Rules:
- Tiny tests; one clear assertion story each.
- Do not implement Stage 3.
- Stop when the full suite is green.""",
    ),
    StagePrompts(
        number=3,
        title="Train",
        teach="Retrain when enough new labels arrive; write checkpoints only.",
        plan=f"""\
You are continuing DashBite stage by stage in the same empty-started repo.

{_prior_stages_note(2)}

STAGE 3 — Training (PLAN ONLY)
Do not write implementation code yet. Produce a short plan for Stage 3 only.

Teach goal: models retrain when enough new labeled data arrives; training owns checkpoints.

Plan must cover:
1. Count new labeled feature rows since last train; if ≥ TRAIN_EVERY_N_EVENTS, train.
2. Fit a tiny model (e.g. LogisticRegression on distance_km + prep_minutes).
3. Write a new checkpoint under data/models/ (checkpoint_YYYYMMDD_HHMMSS.joblib + metrics JSON).
4. Train ONLY writes — never calls infer, never imports infer, never blocks on scoring.
5. Runnable as: python -m pipeline.train

Constraints:
- Independent process from inference (file coupling only via data/models/).
- 1–2 features for the model only (use Config.feature_columns).
- Do not implement infer or dashboards.

Output: concise bullet plan — trigger logic, checkpoint naming, isolation rules, what NOT to touch.""",
        execute=f"""\
STAGE 3 — Train (EXECUTE)
{_prior_stages_note(2)}
Implement ONLY Stage 3 from the agreed plan. Do not implement later stages.

Requirements:
1. pipeline/train.py — poll features; retrain when new labeled count ≥ TRAIN_EVERY_N_EVENTS.
2. Fit LogisticRegression (or similarly tiny model) on Config.feature_columns; seed via RANDOM_SEED.
3. Write checkpoint_*.joblib + matching metrics_*.json under data/models/; persist train state so you do not retrain every tick.
4. Entrypoint: python -m pipeline.train

Hard rules:
- Do NOT import or call pipeline.infer.
- Do NOT write to data/predictions/.
- Train only writes checkpoints; it does not notify inference.

Done when the first checkpoint appears after N new labeled rows.""",
        test=f"""\
STAGE 3 — Train (TEST)
{_prior_stages_note(2)}
Add Stage 3 tests, then run the full suite. Do not start Stage 4 until green.

Add:
1. Unit: retrain triggers only when new labeled count ≥ N; checkpoint filename written.
2. Regression: fixed features fixture → stable metrics JSON shape (deterministic seed).
3. Integration: features → new checkpoint in data/models/; assert train does not import infer.

Then run: pytest
Must pass ALL tests from stages 0–3.

Rules:
- Prove train/infer isolation in tests if possible (import checks).
- Do not implement Stage 4.
- Stop when the full suite is green.""",
    ),
    StagePrompts(
        number=4,
        title="Infer",
        teach="Score with the newest checkpoint; never depends on train being alive.",
        plan=f"""\
You are continuing DashBite stage by stage in the same empty-started repo.

{_prior_stages_note(3)}

STAGE 4 — Inference (PLAN ONLY)
Do not write implementation code yet. Produce a short plan for Stage 4 only.

Teach goal: apply the newest saved checkpoint to new data; inference never depends on the train process being alive.

Plan must cover:
1. On each poll: resolve the most recent checkpoint in data/models/; reload if newer.
2. Score new feature rows; write order_id, late_probability, predicted_late, checkpoint_id to data/predictions/.
3. If no checkpoint exists, log once and wait — do not crash or trigger training.
4. Infer ONLY reads checkpoints — never imports train, never triggers retrain.
5. Runnable as: python -m pipeline.infer

Constraints:
- Independent process from training (shared folder only).
- Do not implement dashboards.
- Keep output schema minimal and stable for tests.

Output: concise bullet plan — newest-checkpoint selection, output columns, isolation rules, what NOT to touch.""",
        execute=f"""\
STAGE 4 — Infer (EXECUTE)
{_prior_stages_note(3)}
Implement ONLY Stage 4 from the agreed plan. Do not implement later stages.

Requirements:
1. pipeline/infer.py — poll features + models; pick newest checkpoint (mtime or timestamp in name).
2. Score unscored feature rows; write predictions_*.csv under data/predictions/ with
   order_id, late_probability, predicted_late, checkpoint_id.
3. Skip cleanly when no checkpoint exists.
4. Entrypoint: python -m pipeline.infer

Hard rules:
- Do NOT import or call pipeline.train.
- Do NOT write checkpoints.
- Do not require train to be running.

Done when predictions grow whenever a checkpoint and new features exist.""",
        test=f"""\
STAGE 4 — Infer (TEST)
{_prior_stages_note(3)}
Add Stage 4 tests, then run the full suite. Do not start Stage 5 until green.

Add:
1. Unit: newest-checkpoint selection; skip cleanly when no checkpoint.
2. Regression: fixed features + checkpoint → golden predictions (ids/scores within tolerance).
3. Integration: features + checkpoint → data/predictions/; assert infer does not import train;
   older stages still pass.

Then run: pytest
Must pass ALL tests from stages 0–4.

Rules:
- Prove train/infer isolation.
- Do not implement Stage 5.
- Stop when the full suite is green.""",
    ),
    StagePrompts(
        number=5,
        title="ML Dashboard",
        teach="Model Pulse: sample volume and score distribution helpers.",
        plan=f"""\
You are continuing DashBite stage by stage in the same empty-started repo.

{_prior_stages_note(4)}

STAGE 5 — ML monitoring dashboard (PLAN ONLY)
Do not write implementation code yet. Produce a short plan for Stage 5 only.

Teach goal: watch the data and model outputs (Model Pulse).

Plan must cover:
1. Pure helper functions that compute sample volume / score summary from dataframes
   (test these — not the browser UI).
2. Sparse Streamlit page showing sample volume and late_probability distribution
   (or recent predictions vs was_late).
3. Read from data/features/ and data/predictions/ only — no coupling to train process.
4. Layout can live under pipeline/dashboard/ (app + ml_metrics helpers).

Constraints:
- 1–2 charts/widgets only for this stage.
- Do not build the business/Ops Control page yet (Stage 6).
- Prefer helpers that pytest can exercise with fixtures.

Output: concise bullet plan — helpers, page widgets, files, what NOT to touch.""",
        execute=f"""\
STAGE 5 — ML Dashboard (EXECUTE)
{_prior_stages_note(4)}
Implement ONLY Stage 5 from the agreed plan. Do not implement Stage 6 business KPIs.

Requirements:
1. pipeline/dashboard/ml_metrics.py — sample_volume(features), score_summary(predictions).
2. Streamlit Model Pulse page (pipeline/dashboard/app.py or equivalent) that shows those KPIs
   and a simple score distribution / recent chart.
3. Load CSVs from data/features/ and data/predictions/.

Rules:
- Test helpers with pytest; do not rely on browser automation.
- Do not add late_rate / at-risk business metrics yet (Stage 6).
- Keep the page sparse — teaching clarity over polish.

Done when Model Pulse reads live feature/prediction files.""",
        test=f"""\
STAGE 5 — ML Dashboard (TEST)
{_prior_stages_note(4)}
Add Stage 5 tests, then run the full suite. Do not start Stage 6 until green.

Add:
1. Unit: helpers that compute sample volume / score summary from dataframes.
2. Regression: fixture preds/features → expected KPI numbers.
3. Integration: helpers read real-shaped files from a temp data tree like prior stages.

Then run: pytest
Must pass ALL tests from stages 0–5.

Rules:
- Test metric helpers, not the Streamlit browser UI.
- Do not implement Stage 6.
- Stop when the full suite is green.""",
    ),
    StagePrompts(
        number=6,
        title="Business Dashboard",
        teach="Ops Control: late rate and orders-at-risk value.",
        plan=f"""\
You are continuing DashBite stage by stage in the same empty-started repo.

{_prior_stages_note(5)}

STAGE 6 — Business dashboard (PLAN ONLY)
Do not write implementation code yet. Produce a short plan for Stage 6 only.

Teach goal: same pipeline, different audience metrics (Ops Control).

Plan must cover:
1. Helpers: late_rate and at-risk order value (count or sum of order_value where predicted late).
2. Second Streamlit page/section for business KPIs.
3. Read features + predictions handoff; reuse Stage 5 loading patterns.
4. Still test helpers with pytest, not the browser.

Constraints:
- 1–2 business KPIs only.
- Do not redesign Model Pulse; add Ops Control alongside it.
- No Docker, Kafka, Spark, MLflow, or drift libraries.

Output: concise bullet plan — helpers, page, files, what NOT to touch.""",
        execute=f"""\
STAGE 6 — Business Dashboard (EXECUTE)
{_prior_stages_note(5)}
Implement ONLY Stage 6 from the agreed plan.

Requirements:
1. pipeline/dashboard/biz_metrics.py — late_rate(...) and at_risk_order_value(...).
2. Ops Control Streamlit page showing late rate and orders at risk (value or count).
3. Join/use features + predictions as needed for KPIs.

Rules:
- Do not break Model Pulse (Stage 5).
- Keep KPIs to late rate + at-risk value only.
- Prefer pure helpers that unit tests can call.

Done when Ops Control shows business KPIs from the same data folders.""",
        test=f"""\
STAGE 6 — Business Dashboard (TEST)
{_prior_stages_note(5)}
Add Stage 6 tests, then run the full suite. Pipeline stages are complete when green.

Add:
1. Unit: late rate + at-risk value helpers.
2. Regression: fixture → expected KPI numbers.
3. Integration: reads features/predictions handoff; full suite including stages 0–5 still green.

Then run: pytest
Must pass ALL tests from stages 0–6.

Rules:
- Test helpers, not the browser UI.
- After green: optionally note README runbook (run each stage in its own terminal; pytest after every stage).
- Stop when the full suite is green — demo pipeline complete.""",
    ),
)
