#!/usr/bin/env python3
"""Generate HTML review report for information-theory skill task evals."""

import json
from pathlib import Path

RESULTS = Path("/Users/jacobelder/Documents/GitHub/jakes-skills/information-theory/results")
EVALS_PATH = Path("/Users/jacobelder/Documents/GitHub/jakes-skills/information-theory/information-theory/evals/evals.json")
OUT = Path("/Users/jacobelder/Documents/GitHub/jakes-skills/information-theory/review.html")

with open(EVALS_PATH) as f:
    evals_data = json.load(f)
evals = evals_data["evals"]

with open(RESULTS / "aggregate_grading.json") as f:
    agg = json.load(f)

def read_grading(eval_id: int, variant: str) -> dict:
    p = RESULTS / f"eval_{eval_id:02d}" / f"{variant}_grading.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}

def read_transcript(eval_id: int, variant: str) -> str:
    p = RESULTS / f"eval_{eval_id:02d}" / variant / "transcript.md"
    if p.exists():
        return p.read_text()
    return "(no transcript)"

def esc(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

rows = []
for ev in evals:
    eid = ev["id"]
    wg = read_grading(eid, "with_skill")
    bg = read_grading(eid, "without_skill")
    wt = read_transcript(eid, "with_skill")
    bt = read_transcript(eid, "without_skill")
    rows.append({
        "id": eid,
        "name": ev["name"],
        "prompt": ev["prompt"],
        "assertions": ev["assertions"],
        "with_grading": wg,
        "without_grading": bg,
        "with_transcript": wt,
        "without_transcript": bt,
    })

ws_total = agg["with_skill"]["passed"]
ws_max = agg["with_skill"]["total"]
bl_total = agg["without_skill"]["passed"]
bl_max = agg["without_skill"]["total"]

html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>information-theory — Task Eval Review</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f0; margin: 0; padding: 20px; color: #1a1a18; }}
h1 {{ font-size: 1.5rem; margin-bottom: 4px; }}
.subtitle {{ color: #666; margin-bottom: 20px; font-size: 0.9rem; }}
.summary-bar {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; display: flex; gap: 32px; align-items: center; }}
.metric {{ text-align: center; }}
.metric .val {{ font-size: 1.8rem; font-weight: 700; }}
.metric .lbl {{ font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }}
.green {{ color: #4a8c3f; }}
.red {{ color: #c0392b; }}
.delta {{ color: #2471a3; }}
.eval-card {{ background: white; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }}
.eval-header {{ background: #f9f8f4; border-bottom: 1px solid #eee; padding: 10px 16px; display: flex; gap: 16px; align-items: center; cursor: pointer; }}
.eval-id {{ font-size: 0.75rem; color: #888; font-weight: 600; min-width: 28px; }}
.eval-name {{ font-weight: 600; flex: 1; font-size: 0.92rem; }}
.score-badge {{ font-size: 0.78rem; padding: 2px 8px; border-radius: 12px; font-weight: 600; }}
.badge-pass {{ background: #d5ecd4; color: #2d7a2a; }}
.badge-fail {{ background: #fde8e6; color: #c0392b; }}
.badge-partial {{ background: #fef3cd; color: #8a6300; }}
.eval-body {{ padding: 16px; display: none; }}
.prompt-box {{ background: #f0f0e8; border-radius: 4px; padding: 10px 12px; font-size: 0.85rem; margin-bottom: 12px; line-height: 1.5; }}
.assertions-table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 0.82rem; }}
.assertions-table th {{ text-align: left; padding: 4px 8px; background: #f5f5f0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: #666; }}
.assertions-table td {{ padding: 5px 8px; vertical-align: top; border-top: 1px solid #eee; }}
.pass-icon {{ color: #4a8c3f; font-weight: bold; }}
.fail-icon {{ color: #c0392b; font-weight: bold; }}
.transcript-toggle {{ font-size: 0.78rem; color: #2471a3; cursor: pointer; text-decoration: underline; margin-top: 6px; display: inline-block; }}
.transcript-box {{ background: #f8f8f5; border: 1px solid #e0e0d8; border-radius: 4px; padding: 12px; font-size: 0.78rem; white-space: pre-wrap; word-break: break-word; max-height: 400px; overflow-y: auto; display: none; margin-top: 6px; line-height: 1.55; }}
.side-by-side {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.panel-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; margin-bottom: 6px; }}
.with-label {{ color: #2d7a2a; }}
.without-label {{ color: #8a6300; }}
.evidence-text {{ color: #555; font-size: 0.78rem; font-style: italic; }}
</style>
</head>
<body>
<h1>information-theory — Task Eval Review</h1>
<div class="subtitle">20 evals · with-skill vs without-skill baseline · graded programmatically</div>

<div class="summary-bar">
  <div class="metric">
    <div class="val green">{ws_total}/{ws_max}</div>
    <div class="lbl">With Skill</div>
  </div>
  <div class="metric">
    <div class="val green">{ws_total/ws_max:.0%}</div>
    <div class="lbl">Pass Rate</div>
  </div>
  <div class="metric">
    <div class="val">{bl_total}/{bl_max}</div>
    <div class="lbl">Baseline</div>
  </div>
  <div class="metric">
    <div class="val">{bl_total/bl_max:.0%}</div>
    <div class="lbl">Base Rate</div>
  </div>
  <div class="metric">
    <div class="val delta">+{(ws_total-bl_total)/ws_max:.0%}</div>
    <div class="lbl">Delta</div>
  </div>
</div>

<div id="evals">
"""]

for row in rows:
    eid = row["id"]
    wg = row["with_grading"]
    bg = row["without_grading"]
    ws = wg.get("summary", {})
    bs = bg.get("summary", {})
    w_pass = ws.get("passed", 0); w_total = ws.get("total", 0)
    b_pass = bs.get("passed", 0); b_total = bs.get("total", 0)

    def badge(p, t):
        if t == 0: return '<span class="score-badge badge-fail">?/?</span>'
        if p == t: return f'<span class="score-badge badge-pass">{p}/{t} ✓</span>'
        if p == 0: return f'<span class="score-badge badge-fail">{p}/{t} ✗</span>'
        return f'<span class="score-badge badge-partial">{p}/{t}</span>'

    delta_pp = (w_pass/w_total - b_pass/b_total)*100 if w_total > 0 and b_total > 0 else 0
    delta_str = f"&nbsp;<span style='color:#2471a3;font-size:0.78rem'>+{delta_pp:.0f}pp</span>" if delta_pp > 0 else ""

    # Build assertions comparison
    assertions = row["assertions"]
    w_exps = wg.get("expectations", [])
    b_exps = bg.get("expectations", [])

    assertion_rows = ""
    for i, a in enumerate(assertions):
        w_exp = w_exps[i] if i < len(w_exps) else {}
        b_exp = b_exps[i] if i < len(b_exps) else {}
        w_icon = '<span class="pass-icon">✓</span>' if w_exp.get("passed") else '<span class="fail-icon">✗</span>'
        b_icon = '<span class="pass-icon">✓</span>' if b_exp.get("passed") else '<span class="fail-icon">✗</span>'
        w_ev = esc(w_exp.get("evidence", ""))
        b_ev = esc(b_exp.get("evidence", ""))
        assertion_rows += f"""
          <tr>
            <td style="max-width:360px">{esc(a['text'])}</td>
            <td>{w_icon}</td>
            <td class="evidence-text" style="max-width:260px">{w_ev}</td>
            <td>{b_icon}</td>
            <td class="evidence-text" style="max-width:260px">{b_ev}</td>
          </tr>"""

    wt_id = f"wt_{eid}"
    bt_id = f"bt_{eid}"
    card_id = f"card_{eid}"

    html_parts.append(f"""
<div class="eval-card">
  <div class="eval-header" onclick="toggle('{card_id}')">
    <div class="eval-id">#{eid}</div>
    <div class="eval-name">{esc(row['name'])}</div>
    <div>With: {badge(w_pass, w_total)}&nbsp;&nbsp;Base: {badge(b_pass, b_total)}{delta_str}</div>
  </div>
  <div class="eval-body" id="{card_id}">
    <div class="prompt-box"><strong>Prompt:</strong> {esc(row['prompt'])}</div>
    <table class="assertions-table">
      <thead>
        <tr>
          <th>Assertion</th>
          <th>W✓</th><th>With-skill evidence</th>
          <th>B✓</th><th>Baseline evidence</th>
        </tr>
      </thead>
      <tbody>{assertion_rows}
      </tbody>
    </table>
    <div class="side-by-side">
      <div>
        <div class="panel-label with-label">With Skill — Transcript</div>
        <span class="transcript-toggle" onclick="toggleTx('{wt_id}')">show/hide transcript</span>
        <div class="transcript-box" id="{wt_id}">{esc(row['with_transcript'])}</div>
      </div>
      <div>
        <div class="panel-label without-label">Baseline (no skill) — Transcript</div>
        <span class="transcript-toggle" onclick="toggleTx('{bt_id}')">show/hide transcript</span>
        <div class="transcript-box" id="{bt_id}">{esc(row['without_transcript'])}</div>
      </div>
    </div>
  </div>
</div>""")

html_parts.append("""
</div>
<script>
function toggle(id) {
  var el = document.getElementById(id);
  el.style.display = el.style.display === 'block' ? 'none' : 'block';
}
function toggleTx(id) {
  var el = document.getElementById(id);
  el.style.display = el.style.display === 'block' ? 'none' : 'block';
}
</script>
</body>
</html>
""")

OUT.write_text("".join(html_parts))
print(f"Report written to {OUT}")
print(f"Open with: open {OUT}")
