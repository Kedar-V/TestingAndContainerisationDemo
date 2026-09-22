"""Generate a static GitHub Pages site from prompt content.

Usage (from repo root):
  PYTHONPATH=. python -m pipeline.prompts.build_static
"""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.prompts.content import (
    BASE_PLAN,
    BASE_PLAN_TEACH,
    BASE_PLAN_TITLE,
    STAGES,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "index.html"


def build() -> Path:
    data = {
        "base": {
            "title": BASE_PLAN_TITLE,
            "teach": BASE_PLAN_TEACH,
            "plan": BASE_PLAN,
        },
        "stages": [
            {
                "number": s.number,
                "title": s.title,
                "teach": s.teach,
                "plan": s.plan,
                "execute": s.execute,
                "test": s.test,
            }
            for s in STAGES
        ],
    }
    # Prevent accidental </script> breakout inside the JSON blob
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
  <title>DashBite — Agent Prompt Board</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #0e1117;
      --surface: #1a2421;
      --hero-a: #0f241f;
      --hero-b: #1a3a32;
      --hero-c: #243d28;
      --border: #2d5a4e;
      --accent: #3d8f76;
      --text: #e8f2ee;
      --muted: #b8c9c2;
      --primary: #ff4b4b;
      --code-bg: #0b0f0d;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "DM Sans", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 1.5rem 1.25rem 3rem;
    }}
    .hero {{
      background: linear-gradient(135deg, var(--hero-a) 0%, var(--hero-b) 45%, var(--hero-c) 100%);
      color: var(--text);
      padding: 1.75rem;
      border-radius: 12px;
      margin-bottom: 1.25rem;
      border: 1px solid var(--border);
    }}
    .hero h1 {{
      margin: 0 0 0.35rem;
      font-size: 1.85rem;
      letter-spacing: -0.02em;
    }}
    .hero p {{ margin: 0; opacity: 0.9; }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 1rem;
    }}
    .chip {{
      background: rgba(232, 242, 238, 0.12);
      border: 1px solid rgba(232, 242, 238, 0.25);
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.8rem;
      letter-spacing: 0.04em;
    }}
    .how {{
      background: rgba(61, 143, 118, 0.14);
      border-left: 4px solid var(--accent);
      padding: 0.85rem 1rem;
      margin-bottom: 1.25rem;
      border-radius: 0 8px 8px 0;
      font-size: 0.95rem;
    }}
    .how code {{
      font-family: "IBM Plex Mono", monospace;
      color: #9fdbc5;
    }}
    .toolbar {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 1rem;
    }}
    .toolbar label {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      color: var(--muted);
    }}
    details.stage {{
      border: 1px solid rgba(61, 143, 118, 0.35);
      border-radius: 10px;
      margin-bottom: 0.75rem;
      background: transparent;
      overflow: hidden;
    }}
    details.stage > summary {{
      cursor: pointer;
      padding: 0.9rem 1rem;
      font-weight: 600;
      list-style: none;
      background: var(--surface);
    }}
    details.stage > summary::-webkit-details-marker {{ display: none; }}
    details.stage > summary::before {{
      content: "▸";
      display: inline-block;
      margin-right: 0.55rem;
      color: var(--accent);
      transition: transform 0.15s ease;
    }}
    details.stage[open] > summary::before {{ transform: rotate(90deg); }}
    .stage-body {{ padding: 0.75rem 1rem 1.1rem; }}
    .teach {{
      color: var(--muted);
      margin: 0 0 0.85rem;
      font-size: 0.95rem;
    }}
    .tabs {{
      display: flex;
      gap: 0.25rem;
      border-bottom: 1px solid var(--border);
      margin-bottom: 0.75rem;
    }}
    .tab {{
      background: transparent;
      border: none;
      color: var(--muted);
      padding: 0.55rem 0.9rem;
      cursor: pointer;
      font-family: inherit;
      font-size: 0.95rem;
      border-bottom: 2px solid transparent;
    }}
    .tab.active {{
      color: var(--primary);
      border-bottom-color: var(--primary);
    }}
    .panel {{ display: none; }}
    .panel.active {{ display: block; }}
    .caption {{
      color: var(--muted);
      font-size: 0.85rem;
      margin-bottom: 0.4rem;
    }}
    .prompt-wrap {{
      position: relative;
      background: var(--code-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.75rem 0.85rem 0.85rem;
    }}
    .prompt-wrap pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.82rem;
      line-height: 1.5;
      color: var(--text);
    }}
    .copy-btn {{
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      background: var(--hero-b);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.3rem 0.65rem;
      font-size: 0.8rem;
      cursor: pointer;
      font-family: inherit;
    }}
    .copy-btn:hover {{ background: var(--border); }}
    .copy-btn.copied {{ background: var(--accent); border-color: var(--accent); }}
    .roles {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.75rem;
      margin-bottom: 1.25rem;
    }}
    @media (max-width: 800px) {{
      .roles {{ grid-template-columns: 1fr; }}
    }}
    .role {{
      background: rgba(61, 143, 118, 0.08);
      border: 1px solid rgba(61, 143, 118, 0.35);
      border-radius: 10px;
      padding: 0.85rem 1rem;
      font-size: 0.9rem;
      color: var(--text);
    }}
    .role strong {{
      display: block;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.78rem;
      letter-spacing: 0.04em;
      margin-bottom: 0.35rem;
      color: var(--accent);
    }}
    footer {{
      margin-top: 1.5rem;
      color: var(--muted);
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <main>
    <div class="hero">
      <h1>DashBite</h1>
      <p>Agent Prompt Board — Think it through → Build it → Check it as three
        independent Cursor chats. The repo and tests are the shared source of truth.</p>
      <div class="chips">
        <span class="chip">THINK · ARCHITECT</span>
        <span class="chip">BUILD · IMPLEMENTER</span>
        <span class="chip">CHECK · REVIEWER</span>
        <span class="chip">fresh chat each time</span>
      </div>
    </div>

    <div class="how">
      <strong>How to use in the demo:</strong>
      Each step is intentionally run in a <em>fresh</em> Cursor chat.
      Think it through acts like an architect, Build it like an implementer, and
      Check it like a reviewer. Each agent inspects the repository as it exists
      at that point — not a prior conversation. Wait for full <code>pytest</code>
      green before starting the next stage's architect chat.
    </div>

    <div class="roles">
      <div class="role">
        <strong>ARCHITECT</strong>
        Fresh chat. Understand the current repo and propose the change — don't modify files yet.
      </div>
      <div class="role">
        <strong>IMPLEMENTER</strong>
        Fresh chat. Understand the current repo and implement the requested behavior.
      </div>
      <div class="role">
        <strong>REVIEWER</strong>
        Fresh chat. Assume someone else wrote it. Inspect critically, strengthen tests, verify the suite.
      </div>
    </div>

    <div class="toolbar">
      <label><input type="checkbox" id="expand-all" checked /> Expand all stages</label>
    </div>

    <div id="board"></div>

    <footer>
      Teaching point: a well-structured repo, filesystem contracts, and automated tests
      let independent agents collaborate without shared chat history.
      Full <code>pytest</code> green before the next stage.
      Local Streamlit board: <code>make prompts</code> → :8502.
    </footer>
  </main>

  <script type="application/json" id="prompt-data">{payload}</script>
  <script>
    const data = JSON.parse(document.getElementById("prompt-data").textContent);
    const board = document.getElementById("board");

    function escapeHtml(s) {{
      return s
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
    }}

    function promptBlock(label, text) {{
      const id = "p-" + Math.random().toString(36).slice(2);
      return `
        <div class="caption">${{label}} — click Copy</div>
        <div class="prompt-wrap">
          <button class="copy-btn" type="button" data-copy="${{id}}">Copy</button>
          <pre id="${{id}}">${{escapeHtml(text)}}</pre>
        </div>`;
    }}

    function stageDetails(title, teach, innerHtml, open) {{
      return `
        <details class="stage" ${{open ? "open" : ""}}>
          <summary>${{escapeHtml(title)}}</summary>
          <div class="stage-body">
            <p class="teach"><strong>Teach:</strong> ${{escapeHtml(teach)}}</p>
            ${{innerHtml}}
          </div>
        </details>`;
    }}

    function tabsFor(stage) {{
      const phases = [
        ["plan", "Think it through", "Fresh architect chat — inspect & propose"],
        ["execute", "Build it", "Fresh implementer chat — inspect & build"],
        ["test", "Check it", "Fresh reviewer chat — inspect & verify"],
      ];
      const tabBtns = phases.map(([key, label], i) =>
        `<button class="tab ${{i === 0 ? "active" : ""}}" type="button" data-tab="${{key}}">${{label}}</button>`
      ).join("");
      const panels = phases.map(([key, , caption], i) =>
        `<div class="panel ${{i === 0 ? "active" : ""}}" data-panel="${{key}}">
          ${{promptBlock(caption, stage[key])}}
        </div>`
      ).join("");
      return `<div class="tabs">${{tabBtns}}</div>${{panels}}`;
    }}

    function render(openAll) {{
      const baseInner = promptBlock(
        "Room warm-up — diagram & mental model",
        data.base.plan
      );
      let html = stageDetails("0′ — " + data.base.title, data.base.teach, baseInner, openAll);
      for (const s of data.stages) {{
        html += stageDetails(
          `Stage ${{s.number}} — ${{s.title}}`,
          s.teach,
          tabsFor(s),
          openAll
        );
      }}
      board.innerHTML = html;
      bindInteractions();
    }}

    function bindInteractions() {{
      board.querySelectorAll(".tabs").forEach((tabBar) => {{
        const parent = tabBar.parentElement;
        tabBar.querySelectorAll(".tab").forEach((btn) => {{
          btn.addEventListener("click", () => {{
            tabBar.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
            parent.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
            btn.classList.add("active");
            parent.querySelector(`[data-panel="${{btn.dataset.tab}}"]`).classList.add("active");
          }});
        }});
      }});

      board.querySelectorAll(".copy-btn").forEach((btn) => {{
        btn.addEventListener("click", async () => {{
          const pre = document.getElementById(btn.dataset.copy);
          try {{
            await navigator.clipboard.writeText(pre.textContent);
            btn.textContent = "Copied";
            btn.classList.add("copied");
            setTimeout(() => {{
              btn.textContent = "Copy";
              btn.classList.remove("copied");
            }}, 1200);
          }} catch (e) {{
            btn.textContent = "Select text";
          }}
        }});
      }});
    }}

    const expandAll = document.getElementById("expand-all");
    expandAll.addEventListener("change", () => render(expandAll.checked));
    render(true);
  </script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path}")
