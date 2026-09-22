"""Stage 5 — ML monitoring helpers (sample volume + score summary)."""

from __future__ import annotations

import pandas as pd


def sample_volume(features: pd.DataFrame) -> int:
    """Count of feature samples available."""
    if features is None or features.empty:
        return 0
    return int(len(features))


def volume_over_time(
    features: pd.DataFrame,
    freq: str = "min",
    recent_minutes: int | None = 60,
) -> pd.DataFrame:
    """Bucket feature rows by timestamp for a time-series volume chart.

    Returns a DataFrame indexed by time with a single ``orders`` column
    (orders per time bucket). Empty / missing timestamps yield an empty frame.
    When ``recent_minutes`` is set, only the trailing window is returned so
    long quiet stretches don't bury the live story.
    """
    empty = pd.DataFrame(columns=["orders"])
    if features is None or features.empty or "timestamp" not in features.columns:
        return empty
    ts = pd.to_datetime(features["timestamp"], utc=True, errors="coerce")
    valid = ts.dropna()
    if valid.empty:
        return empty
    series = valid.dt.floor(freq).value_counts().sort_index().rename("orders")
    if recent_minutes is not None and len(series) > 0:
        cutoff = series.index.max() - pd.Timedelta(minutes=recent_minutes)
        series = series.loc[series.index >= cutoff]
    return series.to_frame()


def score_histogram(predictions: pd.DataFrame, n_bins: int = 10) -> pd.DataFrame:
    """Late-probability counts with human-readable bin labels (e.g. 0.0–0.1)."""
    empty = pd.DataFrame(columns=["score_band", "orders"])
    if (
        predictions is None
        or predictions.empty
        or "late_probability" not in predictions.columns
    ):
        return empty
    probs = predictions["late_probability"].astype(float).clip(0.0, 1.0)
    edges = [i / n_bins for i in range(n_bins + 1)]
    labels = [f"{edges[i]:.1f}–{edges[i + 1]:.1f}" for i in range(n_bins)]
    bands = pd.cut(
        probs,
        bins=edges,
        labels=labels,
        include_lowest=True,
        right=True,
    )
    counts = bands.value_counts().reindex(labels, fill_value=0)
    return pd.DataFrame(
        {"score_band": counts.index.astype(str), "orders": counts.to_numpy(dtype=int)}
    )


def score_summary(predictions: pd.DataFrame) -> dict:
    """Simple summary of late_probability distribution."""
    if predictions is None or predictions.empty or "late_probability" not in predictions.columns:
        return {
            "count": 0,
            "mean_probability": 0.0,
            "min_probability": 0.0,
            "max_probability": 0.0,
            "predicted_late_rate": 0.0,
        }
    probs = predictions["late_probability"].astype(float)
    pred_late = (
        predictions["predicted_late"].astype(int).mean()
        if "predicted_late" in predictions.columns
        else 0.0
    )
    return {
        "count": int(len(predictions)),
        "mean_probability": float(probs.mean()),
        "min_probability": float(probs.min()),
        "max_probability": float(probs.max()),
        "predicted_late_rate": float(pred_late),
    }
