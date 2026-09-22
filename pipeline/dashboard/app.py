"""Streamlit dashboards: Model Pulse (ML) and Ops Control (business)."""

from __future__ import annotations

import time
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from pipeline.dashboard.biz_metrics import at_risk_order_value, late_rate
from pipeline.dashboard.ml_metrics import (
    sample_volume,
    score_histogram,
    score_summary,
    volume_over_time,
)
from pipeline.dashboard.quality_metrics import (
    failures_ranked,
    field_failure_totals,
    throughput_summary,
)
from pipeline.paths import PROJECT_ROOT, features_dir, predictions_dir, quality_dir
from pipeline.preprocess import QUALITY_LOG

ACCENT = "#5B9BD5"
MUTED = "#6B7280"


def _load_csvs(directory: Path, pattern: str) -> pd.DataFrame:
    files = sorted(directory.glob(pattern))
    if not files:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(p) for p in files], ignore_index=True)


def load_features(base: Path | None = None) -> pd.DataFrame:
    return _load_csvs(features_dir(base), "features_*.csv")


def load_predictions(base: Path | None = None) -> pd.DataFrame:
    return _load_csvs(predictions_dir(base), "predictions_*.csv")


def load_quality_log(base: Path | None = None) -> pd.DataFrame:
    path = quality_dir(base) / QUALITY_LOG
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _volume_claim(volume_ts: pd.DataFrame) -> str:
    if volume_ts.empty or len(volume_ts) < 2:
        return "Order volume over the last hour"
    recent = volume_ts["orders"].tail(5).mean()
    prior = volume_ts["orders"].head(max(len(volume_ts) - 5, 1)).mean()
    if prior <= 0:
        return "Orders are arriving in the live window"
    if recent > prior * 1.15:
        return "Order volume is rising in the last hour"
    if recent < prior * 0.85:
        return "Order volume is cooling off in the last hour"
    return "Order volume is steady in the last hour"


def _score_claim(summary: dict, hist: pd.DataFrame) -> str:
    if hist.empty or summary["count"] == 0:
        return "Late-probability scores (waiting for predictions)"
    spread = summary["max_probability"] - summary["min_probability"]
    mean = summary["mean_probability"]
    if spread < 0.15:
        return f"Late scores are clustered near {mean:.2f} — check for a stuck model"
    if mean < 0.35:
        return "Late scores skew low — most orders look on-time"
    if mean > 0.65:
        return "Late scores skew high — many orders look at risk"
    return "Late scores span low-to-high — model is not stuck"


def _failure_claim(ranked: pd.DataFrame) -> str:
    if ranked.empty:
        return "Field failures (none yet)"
    top = ranked.iloc[0]
    return f"{top['field']} causes the most preprocess failures"


def _volume_chart(volume_ts: pd.DataFrame) -> alt.Chart:
    data = volume_ts.reset_index(names="minute")
    return (
        alt.Chart(data)
        .mark_area(line={"color": ACCENT}, color=ACCENT, opacity=0.35)
        .encode(
            x=alt.X("minute:T", title=None),
            y=alt.Y("orders:Q", title="Orders / minute"),
            tooltip=[
                alt.Tooltip("minute:T", title="Minute"),
                alt.Tooltip("orders:Q", title="Orders"),
            ],
        )
        .properties(height=260)
        .configure_axis(labelColor=MUTED, titleColor=MUTED)
        .configure_view(strokeWidth=0)
    )


def _score_chart(hist: pd.DataFrame) -> alt.Chart:
    bars = (
        alt.Chart(hist)
        .mark_bar(color=ACCENT)
        .encode(
            x=alt.X(
                "score_band:N",
                title="Late probability",
                sort=list(hist["score_band"]),
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y("orders:Q", title="Orders"),
            tooltip=[
                alt.Tooltip("score_band:N", title="Band"),
                alt.Tooltip("orders:Q", title="Orders"),
            ],
        )
    )
    rule = (
        alt.Chart(pd.DataFrame({"score_band": ["0.5–0.6"]}))
        .mark_rule(color="#F59E0B", strokeDash=[4, 4])
        .encode(x="score_band:N")
    )
    return (
        (bars + rule)
        .properties(height=280)
        .configure_axis(labelColor=MUTED, titleColor=MUTED)
        .configure_view(strokeWidth=0)
    )


def _failure_chart(ranked: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(ranked)
        .mark_bar(color=ACCENT)
        .encode(
            x=alt.X("failed_rows:Q", title="Failed rows"),
            y=alt.Y("field:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("field:N", title="Field"),
                alt.Tooltip("failed_rows:Q", title="Failed rows"),
            ],
        )
        .properties(height=max(160, 36 * len(ranked)))
        .configure_axis(labelColor=MUTED, titleColor=MUTED)
        .configure_view(strokeWidth=0)
    )


def main() -> None:
    st.set_page_config(page_title="DashBite", layout="wide")
    st.title("DashBite")

    page = st.sidebar.radio("Page", ["Model Pulse", "Ops Control"])
    auto = st.sidebar.checkbox("Auto-refresh (15s)", value=True)
    base = PROJECT_ROOT
    features = load_features(base)
    predictions = load_predictions(base)
    quality = load_quality_log(base)
    throughput = throughput_summary(quality)
    failures = field_failure_totals(quality)
    summary = score_summary(predictions)

    if page == "Model Pulse":
        st.header("Model Pulse")
        st.caption("Is the late-prediction system healthy?")

        c1, c2, c3 = st.columns(3)
        c1.metric("Samples scored", f"{sample_volume(features):,}")
        c2.metric("Drop rate", f"{throughput['drop_rate']:.0%}")
        c3.metric("Mean late score", f"{summary['mean_probability']:.2f}")

        volume_ts = volume_over_time(features, recent_minutes=60)
        st.subheader(_volume_claim(volume_ts))
        st.caption("Last 60 minutes of feature rows · orders per minute")
        if not volume_ts.empty:
            st.altair_chart(_volume_chart(volume_ts), width="stretch")
        else:
            st.info("No timestamped features yet — waiting for preprocess.")

        hist = score_histogram(predictions)
        st.subheader(_score_claim(summary, hist))
        st.caption("Predicted late probability · dashed band marks the 0.5 decision region")
        if not hist.empty:
            st.altair_chart(_score_chart(hist), width="stretch")
        else:
            st.info("No predictions yet.")

        ranked = failures_ranked(failures)
        st.subheader(_failure_claim(ranked))
        st.caption("Corrupt / invalid fields caught in preprocess")
        if not ranked.empty and ranked["failed_rows"].sum() > 0:
            st.altair_chart(_failure_chart(ranked), width="stretch")
        else:
            st.info("No field failures yet — waiting for preprocess.")

    else:
        st.header("Ops Control")
        st.caption("How much delivery value looks late right now?")

        rate = late_rate(features)
        risk = at_risk_order_value(features, predictions)

        st.subheader(
            f"${risk:,.0f} of order value is flagged late"
            if risk > 0
            else "No predicted-late order value yet"
        )
        c1, c2 = st.columns(2)
        c1.metric("Orders at risk (value)", f"${risk:,.0f}")
        c2.metric("Historical late rate", f"{rate:.0%}")

        if not predictions.empty:
            cols = [
                c
                for c in ("order_id", "late_probability", "predicted_late")
                if c in predictions.columns
            ]
            recent = predictions.loc[:, cols].tail(25).copy()
            if "late_probability" in recent.columns:
                recent["late_probability"] = recent["late_probability"].round(2)
            st.caption("Latest 25 scores · drill-down only")
            st.dataframe(recent, width="stretch", hide_index=True)
        else:
            st.info("No predictions yet.")

    if auto:
        time.sleep(15)
        st.rerun()


if __name__ == "__main__":
    main()
