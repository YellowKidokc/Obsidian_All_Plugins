"""
Axiom HTML Report

Builds one standalone HTML page from the axiom workbook.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path

from openpyxl import load_workbook


def build_axiom_html_report(workbook_path: str | Path, output_path: str | Path) -> Path:
    workbook_path = Path(workbook_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(workbook_path, read_only=True, data_only=True)
    axioms = _read_prefixed_rows(wb, "Axioms_")
    seven_q = _read_prefixed_rows(wb, "SevenQ_")

    law_counts = Counter(row.get("law_family") or "[unmapped]" for row in axioms)
    canon_counts = Counter(row.get("canon_status") or "candidate" for row in axioms)
    slot_counts = Counter(row.get("question_slot") or "[unmapped]" for row in seven_q)

    html = _render_html(
        workbook_path=workbook_path,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        axioms=axioms,
        seven_q=seven_q,
        law_counts=law_counts,
        canon_counts=canon_counts,
        slot_counts=slot_counts,
    )
    output_path.write_text(html, encoding="utf-8")
    return output_path


def _read_prefixed_rows(wb, prefix: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for ws in wb.worksheets:
        if not ws.title.startswith(prefix):
            continue
        headers = [str(cell.value or "") for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        for values in ws.iter_rows(min_row=2, values_only=True):
            row = {headers[idx]: "" if value is None else str(value) for idx, value in enumerate(values) if idx < len(headers)}
            if any(row.values()):
                rows.append(row)
    return rows


def _render_html(
    workbook_path: Path,
    generated_at: str,
    axioms: list[dict[str, str]],
    seven_q: list[dict[str, str]],
    law_counts: Counter,
    canon_counts: Counter,
    slot_counts: Counter,
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Axiom Pipeline Report — Proof Explorer</title>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600;700&family=Oswald:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Cinzel:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    :root {{
      --bg:#050505; --bg-panel:#0a0a0a; --bg-card:#111111; --bg-hover:#1a1a1a;
      --border:#222; --border-hover:#333; --text:#e0e0e0; --text-dim:#999; --text-muted:#555;
      --gold:#d4af37; --gold-dim:rgba(212,175,55,0.1); --red:#c94040; --red-dim:rgba(201,64,64,0.1);
      --blue:#3b82f6; --blue-dim:rgba(59,130,246,0.1); --teal:#14b8a6; --teal-dim:rgba(20,184,166,0.1);
      --violet:#8b7fc2; --violet-dim:rgba(139,127,194,0.1); --green:#22c55e;
    }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); line-height:1.6; overflow-x:hidden; }}
    .tp-ribbon {{ position:sticky; top:0; z-index:1001; background:#0a0a0a; border-bottom:2px solid #a855f733; padding:.5rem 1.5rem; display:flex; align-items:center; justify-content:space-between; font-size:.8rem; }}
    .top-nav {{ position:sticky; top:34px; z-index:1000; background:rgba(5,5,5,.95); backdrop-filter:blur(8px); border-bottom:1px solid var(--border); padding:.75rem 1.5rem; display:flex; align-items:center; gap:2rem; }}
    .brand {{ font-family:'Cinzel',serif; font-size:1rem; color:var(--gold); text-decoration:none; display:flex; align-items:center; gap:.5rem; }}
    .nav-links {{ display:flex; gap:.5rem; margin-left:auto; }}
    .nav-links a {{ font-family:'Oswald',sans-serif; font-size:.75rem; text-transform:uppercase; letter-spacing:.1em; color:var(--text-dim); text-decoration:none; padding:.35rem .85rem; border-radius:.3rem; }}
    .nav-links a.active, .nav-links a:hover {{ color:var(--gold); background:var(--gold-dim); }}
    .layout {{ display:grid; grid-template-columns:260px 1fr 300px; gap:1px; min-height:calc(100vh - 94px); }}
    .sidebar, .rightbar {{ background:var(--bg-panel); padding:1.25rem; overflow-y:auto; max-height:calc(100vh - 94px); }}
    .main {{ padding:1.5rem 2rem 3rem; overflow-y:auto; max-height:calc(100vh - 94px); }}
    .sidebar h3, .rightbar h3 {{ font-family:'Oswald',sans-serif; font-size:.65rem; text-transform:uppercase; letter-spacing:.2em; color:var(--text-muted); margin:0 0 .75rem; padding-bottom:.4rem; border-bottom:1px solid var(--border); }}
    .q-item {{ display:block; padding:.5rem .6rem; border-radius:.35rem; text-decoration:none; color:var(--text-dim); margin-bottom:.2rem; }}
    .q-item:hover, .q-item.active {{ background:var(--gold-dim); color:var(--gold); }}
    .q-row {{ display:flex; align-items:baseline; gap:.5rem; }}
    .q-num {{ font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--gold); min-width:1.25rem; }}
    .q-label {{ font-size:.8rem; font-weight:500; }}
    .q-desc {{ display:block; font-size:.7rem; color:var(--text-muted); padding-left:1.75rem; }}
    .breadcrumb {{ font-size:.78rem; color:var(--text-muted); margin-bottom:1rem; }}
    .breadcrumb a {{ color:var(--text-dim); text-decoration:none; }}
    .sep {{ margin:0 .45rem; color:var(--text-muted); }}
    .badges {{ display:flex; flex-wrap:wrap; gap:.5rem; margin-bottom:1rem; }}
    .badge {{ font-size:.7rem; padding:.25rem .55rem; border-radius:.25rem; border:1px solid var(--border); background:var(--bg-card); display:inline-flex; align-items:center; gap:.35rem; }}
    .badge.gold {{ color:var(--gold); border-color:rgba(212,175,55,.3); background:var(--gold-dim); }}
    .badge.green {{ color:var(--green); border-color:rgba(34,197,94,.3); background:rgba(34,197,94,.1); }}
    .badge.blue {{ color:var(--blue); border-color:rgba(59,130,246,.3); background:var(--blue-dim); }}
    .badge.violet {{ color:var(--violet); border-color:rgba(139,127,194,.3); background:var(--violet-dim); }}
    .paper-title {{ font-family:'Crimson Text',serif; font-size:clamp(1.7rem,3.5vw,2.5rem); font-weight:400; color:var(--text); line-height:1.2; margin-bottom:.4rem; }}
    .paper-subtitle {{ font-family:'Crimson Text',serif; font-size:1.1rem; color:var(--text-dim); font-style:italic; margin-bottom:1.5rem; }}
    .card {{ background:var(--bg-card); border:1px solid var(--border); border-radius:.5rem; padding:1.25rem; margin-bottom:1.25rem; }}
    .card-header {{ display:flex; align-items:center; gap:.6rem; margin-bottom:.875rem; font-family:'Oswald',sans-serif; font-size:.75rem; text-transform:uppercase; letter-spacing:.1em; color:var(--gold); }}
    .rigor-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:.875rem; }}
    .rigor-cell {{ background:var(--bg-panel); border:1px solid var(--border); border-radius:.35rem; padding:.875rem; }}
    .label {{ font-family:'JetBrains Mono',monospace; font-size:.6rem; text-transform:uppercase; letter-spacing:.15em; color:var(--text-muted); margin-bottom:.4rem; }}
    .value {{ font-size:.82rem; color:var(--text); line-height:1.5; }}
    table {{ width:100%; border-collapse:collapse; font-size:.82rem; table-layout:fixed; }}
    th,td {{ padding:.6rem .5rem; text-align:left; border-bottom:1px solid var(--border); vertical-align:top; overflow-wrap:anywhere; }}
    th {{ font-family:'Oswald',sans-serif; font-size:.68rem; text-transform:uppercase; letter-spacing:.1em; color:var(--text-muted); font-weight:500; }}
    td {{ color:var(--text-dim); }}
    tr:hover td {{ background:var(--bg-hover); }}
    .textcol {{ width:48%; }}
    .small {{ color:var(--text-muted); font-size:.72rem; margin-top:.25rem; }}
    .status {{ color:var(--gold); font-weight:700; }}
    .meta-row {{ display:flex; justify-content:space-between; gap:1rem; padding:.5rem 0; border-bottom:1px solid var(--border); font-size:.78rem; }}
    .meta-label {{ color:var(--text-muted); }}
    .meta-value {{ color:var(--text-dim); text-align:right; }}
    .spine-item {{ margin-bottom:.875rem; }}
    .spine-header {{ display:flex; justify-content:space-between; font-size:.78rem; margin-bottom:.2rem; }}
    .spine-name {{ color:var(--text-dim); }}
    .spine-status {{ color:var(--text-muted); font-size:.72rem; }}
    .spine-bar {{ height:3px; background:var(--bg-hover); border-radius:2px; overflow:hidden; }}
    .fill {{ height:100%; border-radius:2px; background:var(--gold); }}
    .chip {{ display:inline-block; font-size:.68rem; padding:.22rem .5rem; border-radius:.2rem; background:var(--bg-hover); border:1px solid var(--border); color:var(--text-dim); margin:.12rem; }}
    @media (max-width:1100px) {{ .layout {{ grid-template-columns:1fr; }} .sidebar,.rightbar,.main {{ max-height:none; }} .rigor-grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <nav class="tp-ribbon">
    <div><a href="/index.html" style="color:#999;text-decoration:none;">&larr; Main Index</a><span style="color:#333;margin:0 .75rem;">|</span><span style="color:#a855f7;font-weight:500;">Proof Explorer</span></div>
    <div style="color:#777;">Generated {escape(generated_at)}</div>
  </nav>
  <nav class="top-nav">
    <a href="index.html" class="brand"><i class="fas fa-atom"></i> THEOPHYSICS</a>
    <div class="nav-links">
      <a href="axioms-layer-0-core.html" class="active">Axioms</a>
      <a href="index.html">Papers</a>
      <a href="#seven-q">7Q Framework</a>
      <a href="#review">Review</a>
    </div>
  </nav>

  <div class="layout">
    <aside class="sidebar">
      <h3><i class="fas fa-compass" style="margin-right:.4rem;"></i>Navigation</h3>
      <a href="#summary" class="q-item active"><div class="q-row"><span class="q-num">R0</span><span class="q-label">Summary</span></div><span class="q-desc">Pipeline counts</span></a>
      <a href="#review" class="q-item"><div class="q-row"><span class="q-num">R1</span><span class="q-label">Review</span></div><span class="q-desc">Canon and law queues</span></a>
      <a href="#axioms" class="q-item"><div class="q-row"><span class="q-num">R2</span><span class="q-label">Axioms</span></div><span class="q-desc">Candidate rows</span></a>
      <a href="#seven-q" class="q-item"><div class="q-row"><span class="q-num">R3</span><span class="q-label">7QS</span></div><span class="q-desc">Question handles</span></a>
      <h3 style="margin-top:1.5rem;">Axiom Layers</h3>
      <a class="q-item" href="axioms-layer-0-core.html"><div class="q-row"><span class="q-num">L0</span><span class="q-label">Core</span></div></a>
      <a class="q-item" href="axioms-layer-2-derived.html"><div class="q-row"><span class="q-num">L2</span><span class="q-label">Derived</span></div></a>
      <a class="q-item" href="axioms-layer-3-extended.html"><div class="q-row"><span class="q-num">L3</span><span class="q-label">Extended</span></div></a>
      <a class="q-item" href="axioms-closure.html"><div class="q-row"><span class="q-num">Ω</span><span class="q-label">Closure</span></div></a>
    </aside>

    <main class="main">
      <div class="breadcrumb"><a href="index.html">Master Index</a><span class="sep">→</span><a href="#">Proof Explorer</a><span class="sep">→</span><span style="color:var(--gold);">Axiom Pipeline Report</span></div>
      <div class="badges">
        <span class="badge green"><i class="fas fa-check-circle"></i> Generated</span>
        <span class="badge gold"><i class="fas fa-layer-group"></i> {len(axioms)} Axiom Candidates</span>
        <span class="badge blue"><i class="fas fa-crosshairs"></i> {len(seven_q)} 7QS Handles</span>
        <span class="badge violet"><i class="fas fa-link"></i> {len({row.get('paper_id') for row in axioms + seven_q if row.get('paper_id')})} Source Pages</span>
      </div>
      <h1 class="paper-title">Axiom Pipeline Report</h1>
      <p class="paper-subtitle">Generated review surface for Proof Explorer axiom candidates, canon status, law mapping, and 7Q handles.</p>

      <div class="card" id="summary">
        <div class="card-header"><i class="fas fa-bolt"></i> Rigor Card</div>
        <div class="rigor-grid">
          <div class="rigor-cell"><div class="label">Axiom Candidates</div><div class="value">{len(axioms)}</div></div>
          <div class="rigor-cell"><div class="label">7QS Handles</div><div class="value">{len(seven_q)}</div></div>
          <div class="rigor-cell"><div class="label">Unmapped Laws</div><div class="value">{sum(1 for row in axioms if not row.get('law_family'))}</div></div>
        </div>
      </div>

      <div class="card" id="review">
        <div class="card-header"><i class="fas fa-filter"></i> Review Queues</div>
        <div>{_render_counter_chips("Canon", canon_counts)}{_render_counter_chips("Law", law_counts)}{_render_counter_chips("7QS", slot_counts)}</div>
      </div>

      <div class="card" id="axioms">
        <div class="card-header"><i class="fas fa-cubes"></i> Axiom Candidates</div>
        {_render_axiom_table(axioms)}
      </div>

      <div class="card" id="seven-q">
        <div class="card-header"><i class="fas fa-layer-group"></i> 7QS Handles</div>
        {_render_seven_q_table(seven_q)}
      </div>
    </main>

    <aside class="rightbar">
      <h3>Metadata</h3>
      <div class="meta-row"><span class="meta-label">Workbook</span><span class="meta-value">{escape(workbook_path.name)}</span></div>
      <div class="meta-row"><span class="meta-label">Generated</span><span class="meta-value">{escape(generated_at)}</span></div>
      <div class="meta-row"><span class="meta-label">Status</span><span class="meta-value" style="color:var(--gold);">Review Queue</span></div>
      <h3 style="margin-top:1.5rem;">Pipeline Spine</h3>
      {_render_spine_item("Extract", 100)}
      {_render_spine_item("Registry", 100)}
      {_render_spine_item("Canon Review", 30)}
      {_render_spine_item("Postgres Sync", 20)}
    </aside>
  </div>
</body>
</html>
"""


def _render_counter_chips(label: str, counts: Counter) -> str:
    return "\n".join(
        f'<span class="chip">{escape(label)}: {escape(str(key))} = {value}</span>'
        for key, value in sorted(counts.items(), key=lambda item: str(item[0]))
    )


def _render_spine_item(label: str, percent: int) -> str:
    return (
        '<div class="spine-item">'
        f'<div class="spine-header"><span class="spine-name">{escape(label)}</span><span class="spine-status">{percent}%</span></div>'
        f'<div class="spine-bar"><div class="fill" style="width:{percent}%"></div></div>'
        '</div>'
    )


def _render_axiom_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{escape(row.get('paper_id', ''))}<div class='small'>{escape(row.get('article_title', ''))}</div></td>"
            f"<td class='textcol'>{escape(row.get('candidate_text', ''))}</td>"
            f"<td class='status'>{escape(row.get('canon_status', ''))}</td>"
            f"<td>{escape(row.get('law_family', ''))}</td>"
            f"<td>{escape(row.get('canonical_axiom_id', ''))}</td>"
            f"<td>{escape(row.get('reviewer_notes', ''))}</td>"
            "</tr>"
        )
    return "<table><thead><tr><th>Paper</th><th>Candidate</th><th>Status</th><th>Law</th><th>Canonical ID</th><th>Notes</th></tr></thead><tbody>" + "\n".join(body) + "</tbody></table>"


def _render_seven_q_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{escape(row.get('paper_id', ''))}<div class='small'>{escape(row.get('article_title', ''))}</div></td>"
            f"<td class='textcol'>{escape(row.get('handle_text', ''))}</td>"
            f"<td>{escape(row.get('question_slot', ''))}</td>"
            f"<td>{escape(row.get('classification', ''))}</td>"
            f"<td>{escape(row.get('falsification_note', ''))}</td>"
            f"<td>{escape(row.get('reviewer_notes', ''))}</td>"
            "</tr>"
        )
    return "<table><thead><tr><th>Paper</th><th>Handle</th><th>Slot</th><th>Classification</th><th>Falsification</th><th>Notes</th></tr></thead><tbody>" + "\n".join(body) + "</tbody></table>"
