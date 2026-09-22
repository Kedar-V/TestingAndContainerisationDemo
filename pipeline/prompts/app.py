"""DashBite Agent Prompt Board — Think it through → Build it → Check it."""

from __future__ import annotations

import streamlit as st

from pipeline.prompts.content import (
    BASE_PLAN,
    BASE_PLAN_TEACH,
    BASE_PLAN_TITLE,
    STAGES,
    StagePrompts,
)

PHASES = (
    ("plan", "Think it through", "Same agent chat — inspect & propose before coding"),
    ("execute", "Build it", "Short follow-up — agent already has the plan context"),
    ("test", "Check it", "Pre-PR review — coverage + full pytest"),
)


def _prompt_text(stage: StagePrompts, key: str) -> str:
    return getattr(stage, key)


def _inject_style() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

          html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
          }

          .block-container {
            padding-top: 1.5rem;
            max-width: 1100px;
          }

          .dpb-hero {
            background: linear-gradient(135deg, #0f241f 0%, #1a3a32 45%, #243d28 100%);
            color: #e8f2ee;
            padding: 1.75rem 1.75rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.25rem;
            border: 1px solid #2d5a4e;
          }
          .dpb-hero h1 {
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0 0 0.35rem 0;
            letter-spacing: -0.02em;
          }
          .dpb-hero p {
            margin: 0;
            opacity: 0.9;
            font-size: 1rem;
            line-height: 1.45;
          }
          .dpb-loop {
            display: inline-flex;
            gap: 0.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
          }
          .dpb-chip {
            background: rgba(232, 242, 238, 0.12);
            border: 1px solid rgba(232, 242, 238, 0.25);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.8rem;
            letter-spacing: 0.04em;
          }
          .dpb-how {
            background: rgba(61, 143, 118, 0.14);
            border-left: 4px solid #3d8f76;
            padding: 0.85rem 1rem;
            margin-bottom: 1.25rem;
            border-radius: 0 8px 8px 0;
            color: inherit;
            font-size: 0.95rem;
          }
          .dpb-stage-meta {
            color: inherit;
            opacity: 0.9;
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
          }
          div[data-testid="stExpander"] details {
            border: 1px solid rgba(61, 143, 118, 0.35) !important;
            border-radius: 10px !important;
            background: transparent !important;
          }
          div[data-testid="stExpander"] details > div,
          div[data-testid="stExpander"] [data-testid="stExpanderDetails"],
          div[data-testid="stExpander"] .streamlit-expanderContent,
          div[data-testid="stExpander"] summary {
            background: transparent !important;
            color: inherit !important;
          }
          code, pre, .stCode {
            font-family: 'IBM Plex Mono', monospace !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="DashBite Agent Prompts",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _inject_style()

    st.markdown(
        """
        <div class="dpb-hero">
          <h1>DashBite</h1>
          <p>Agent Prompt Board — paste one message at a time into the same Cursor chat.
          Think it through → Build it → Check it, stage by stage, with the room.</p>
          <div class="dpb-loop">
            <span class="dpb-chip">THINK IT THROUGH</span>
            <span class="dpb-chip">BUILD IT</span>
            <span class="dpb-chip">CHECK IT</span>
            <span class="dpb-chip">same agent chat</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="dpb-how">
          <strong>How to use in the demo:</strong>
          Keep one Cursor agent conversation open. For each beat, paste
          <em>Think it through</em> → review the proposal with the room → paste
          <em>Build it</em> (short on purpose — the agent already has context) → paste
          <em>Check it</em> → wait for full <code>pytest</code> green → next stage.
          Attendees copy the same prompts and build along.
        </div>
        """,
        unsafe_allow_html=True,
    )

    expand_all = st.toggle("Expand all stages", value=True)

    with st.expander(f"0′ — {BASE_PLAN_TITLE}", expanded=expand_all):
        st.markdown(
            f'<p class="dpb-stage-meta"><strong>Teach:</strong> {BASE_PLAN_TEACH}</p>',
            unsafe_allow_html=True,
        )
        st.caption("Warm-up only — diagram & mental model; click the copy icon")
        st.code(BASE_PLAN, language="markdown")

    for stage in STAGES:
        header = f"Stage {stage.number} — {stage.title}"
        with st.expander(header, expanded=expand_all):
            st.markdown(
                f'<p class="dpb-stage-meta"><strong>Teach:</strong> {stage.teach}</p>',
                unsafe_allow_html=True,
            )

            tabs = st.tabs([label for _, label, _ in PHASES])
            for tab, (key, label, caption) in zip(tabs, PHASES):
                with tab:
                    st.caption(f"{caption} — click the copy icon on the code block")
                    st.code(_prompt_text(stage, key), language="markdown")

    st.divider()
    st.caption(
        "After every stage: full `pytest` green before advancing. "
        "Build prompts stay short on purpose — conversational context is the lesson. "
        "Local board: make prompts → :8502."
    )


if __name__ == "__main__":
    main()
