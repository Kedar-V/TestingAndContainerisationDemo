"""DashBite Agent Prompt Board — independent Architect / Implementer / Reviewer chats."""

from __future__ import annotations

import streamlit as st

from pipeline.prompts.content import (
    BASE_PLAN,
    BASE_PLAN_TEACH,
    BASE_PLAN_TITLE,
    CREATE_SKILL_PROMPT,
    STAGES,
    StagePrompts,
)

PHASES = (
    ("plan", "Think it through", "Fresh architect chat — write plan.md"),
    ("execute", "Build it", "Fresh implementer chat — read plan.md, then build"),
    ("test", "Check it", "Fresh reviewer chat — inspect & verify"),
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
          .dpb-roles {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.25rem;
          }
          @media (max-width: 800px) {
            .dpb-roles { grid-template-columns: 1fr; }
          }
          .dpb-role {
            background: rgba(61, 143, 118, 0.08);
            border: 1px solid rgba(61, 143, 118, 0.35);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            color: inherit;
            font-size: 0.9rem;
          }
          .dpb-role strong {
            display: block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
            color: #3d8f76;
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
          <p>Agent Prompt Board — Think it through → Build it → Check it as three
          independent Cursor chats. The repo, <code>plan.md</code>, and tests are the shared source of truth.</p>
          <div class="dpb-loop">
            <span class="dpb-chip">THINK · ARCHITECT</span>
            <span class="dpb-chip">BUILD · IMPLEMENTER</span>
            <span class="dpb-chip">CHECK · REVIEWER</span>
            <span class="dpb-chip">fresh chat each time</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="dpb-how">
          <strong>How to use in the demo:</strong>
          Each step is intentionally run in a <em>fresh</em> Cursor chat.
          Think it through acts like an architect (writes <code>plan.md</code>),
          Build it like an implementer (reads <code>plan.md</code> first), and
          Check it like a reviewer. Each agent inspects the repository as it exists
          at that point — not a prior conversation. Wait for full <code>pytest</code>
          green before starting the next stage's architect chat.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="dpb-roles">
          <div class="dpb-role">
            <strong>ARCHITECT</strong>
            Fresh chat. Inspect the repo, propose the change, write it to plan.md — don't implement yet.
          </div>
          <div class="dpb-role">
            <strong>IMPLEMENTER</strong>
            Fresh chat. Read plan.md first, then implement against the current repo.
          </div>
          <div class="dpb-role">
            <strong>REVIEWER</strong>
            Fresh chat. Assume someone else wrote it. Inspect critically, strengthen tests, verify the suite.
          </div>
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
        st.caption("Room warm-up — diagram & mental model; click the copy icon")
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
    st.markdown("## Take the workflow with you")
    st.caption("ARCHITECT → IMPLEMENTER → REVIEWER")
    st.markdown(
        """
The prompts above are intentionally explicit so we can see the workflow during the demo.
In a real project, we don't want to rewrite this scaffolding every time.

Cursor Skills let us package the workflow once and reuse it across projects.

Install the `dev-cycle` skill, then start three fresh chats for a feature:
"""
    )
    st.code(
        "/dev-cycle architect Add caching to the API\n\n"
        "/dev-cycle implement Add caching to the API\n\n"
        "/dev-cycle review Add caching to the API",
        language="text",
    )
    st.info(
        "Each chat starts fresh. The repository, interfaces, and tests provide "
        "the shared context between agents."
    )
    st.markdown("### Create it once")
    st.caption("Paste into Cursor — click the copy icon")
    st.code(CREATE_SKILL_PROMPT, language="markdown")
    st.markdown(
        "Prefer a plain markdown file for Codex, Claude Code, or any agent? "
        "See [`docs/dev-cycle.md`](../docs/dev-cycle.md)."
    )
    st.markdown(
        "*Prompt engineering gets you through one task. "
        "A skill turns the workflow into reusable engineering infrastructure.*"
    )

    st.divider()
    st.caption(
        "Teaching point: plan.md, the repo, filesystem contracts, and automated tests "
        "let independent agents collaborate without shared chat history. "
        "Full pytest green before the next stage. Local board: make prompts → :8502."
    )


if __name__ == "__main__":
    main()
