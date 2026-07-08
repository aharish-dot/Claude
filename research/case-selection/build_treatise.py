#!/usr/bin/env python3
"""Render the three aggregation index files into one readable, theme-aware HTML
'jurisprudence map'. Self-contained (inline CSS). Run after build_aggregation.py.
"""
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
pi = json.load(open(os.path.join(HERE, "provision_index.json")))
im = json.load(open(os.path.join(HERE, "issue_matrix.json")))
cg = json.load(open(os.path.join(HERE, "citation_graph.json")))

def e(s): return html.escape(str(s if s is not None else ""))
VBADGE = {"post-2007": "#2e7d32", "pre-2007": "#b26a00", "pre-2003": "#8e24aa", None: "#666"}

def vbadges(vs):
    return " ".join(f'<span class="ver" style="background:{VBADGE.get(v,"#666")}">{e(v)}</span>' for v in vs)

rows = []
# ---- provision index ----
prov_html = []
for sec, v in pi.items():
    hold = []
    for h in v["holdings_chronological"]:
        hold.append(f"""<tr>
          <td class="cid">{e(h['case_id'])}</td>
          <td>{e(h['date'][:4])}</td>
          <td>{e(h['provision_cited_as'])} <span class="ver" style="background:{VBADGE.get(h['provision_version'],'#666')}">{e(h['provision_version'])}</span></td>
          <td>{'· '.join('<span class=node>'+e(n)+'</span>' for n in h['issue_node'])}</td>
          <td class="{ 'ratio' if h['holding_type']=='ratio' else 'obiter'}">{e(h['holding_type'])}</td>
          <td>{e(h['holding'])}</td></tr>""")
    prov_html.append(f"""<details {'open' if v['n_holdings']>=5 else ''}>
      <summary><b>{e(sec)}</b> — {v['n_holdings']} holdings ({v['n_ratio']} ratio) · {len(v['cases'])} cases {vbadges(v['versions_applied'])}</summary>
      <table><thead><tr><th>Case</th><th>Yr</th><th>as</th><th>issue-node</th><th>type</th><th>holding</th></tr></thead>
      <tbody>{''.join(hold)}</tbody></table></details>""")

# ---- issue matrix ----
issue_html = []
for node, v in im.items():
    line = " → ".join(f'<span class="cid">{e(c["case_id"])}</span><span class=ct>{e(c["court_type"])}·{e(c["date"][:4])}</span>'
                      for c in v["line_of_authority"])
    props = "".join(f"""<div class=prop><span class="cid">{e(p['case_id'])}</span>
              <span class=scope>{e(p['scope'])}</span> <span class=nov>{e(p['novelty'])}</span>
              <div>{e(p['proposition'])}</div></div>""" for p in v["propositions"])
    issue_html.append(f"""<details {'open' if v['n_cases']>=4 else ''}>
      <summary><b>{e(node)}</b> — {v['n_cases']} cases · lead <span class=cid>{e(v['leading_case']['case_id'])}</span>
        ({e(v['leading_case']['court_type'])}){' <span class=split>HC SPLIT</span>' if v['split_flag'] else ''}</summary>
      <div class=line><b>line of authority:</b> {line}</div>
      {props}</details>""")

# ---- citation backbone ----
back_html = []
for b in cg["recurring_authorities"]:
    cb = ", ".join(f'{e(c["case_id"])}<span class=ct>{e(c["treatment"])}</span>' for c in b["cited_by"])
    back_html.append(f"""<tr><td class=big>{b['times_cited']}×</td>
      <td><b>{e(b['authority'])}</b><br><span class=meta>{e(b['cite'])} · {e(b['court'])}</span></td>
      <td>{e(b['treatments'])}</td><td class=cbcell>{cb}</td></tr>""")

nSC = sum(1 for cid in [] )  # placeholder
edges_in = [x for x in cg["edges"] if x["in_corpus"]]

doc = f"""<title>Electricity Act §126/§135 — Jurisprudence Map</title>
<style>
:root {{ --bg:#fff; --fg:#1a1a1a; --mut:#666; --line:#e2e2e2; --card:#f7f7f8; --accent:#0b5; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#15161a; --fg:#e8e8ea; --mut:#9a9aa2; --line:#2c2e36; --card:#1d1f26; }} }}
:root[data-theme=dark] {{ --bg:#15161a; --fg:#e8e8ea; --mut:#9a9aa2; --line:#2c2e36; --card:#1d1f26; }}
:root[data-theme=light] {{ --bg:#fff; --fg:#1a1a1a; --mut:#666; --line:#e2e2e2; --card:#f7f7f8; }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; margin:0; padding:28px; max-width:1050px; margin:auto; }}
h1 {{ font-size:26px; margin:0 0 4px; }} h2 {{ font-size:19px; margin:34px 0 10px; border-bottom:2px solid var(--accent); padding-bottom:5px; }}
.sub {{ color:var(--mut); margin:0 0 20px; }}
.stat {{ display:inline-block; background:var(--card); border:1px solid var(--line); border-radius:8px; padding:8px 13px; margin:3px 5px 3px 0; }}
.stat b {{ font-size:20px; }}
details {{ border:1px solid var(--line); border-radius:8px; margin:8px 0; background:var(--card); }}
summary {{ cursor:pointer; padding:10px 13px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; padding:6px 9px; border-top:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--mut); font-weight:600; }}
.cid {{ font-weight:700; color:var(--accent); white-space:nowrap; }}
.ct {{ color:var(--mut); font-size:11px; margin-left:4px; }}
.ver {{ color:#fff; font-size:10px; padding:1px 6px; border-radius:9px; white-space:nowrap; }}
.node {{ background:var(--bg); border:1px solid var(--line); border-radius:9px; padding:0 6px; font-size:11px; margin-right:3px; white-space:nowrap; }}
.ratio {{ color:var(--accent); font-weight:600; }} .obiter {{ color:var(--mut); }}
.line {{ padding:8px 13px; font-size:13px; }} .line .cid{{margin-left:2px;}}
.prop {{ padding:6px 13px 10px; border-top:1px dashed var(--line); font-size:13px; }}
.scope {{ background:#0b52; border-radius:9px; padding:0 7px; font-size:11px; }}
.nov {{ color:var(--mut); font-size:11px; }}
.split {{ background:#c62828; color:#fff; padding:1px 7px; border-radius:9px; font-size:11px; }}
.big {{ font-size:20px; font-weight:700; color:var(--accent); }}
.meta {{ color:var(--mut); font-size:11px; }} .cbcell{{font-size:11px;}} .cbcell .ct{{color:var(--accent);}}
.callout {{ background:#0b51; border:1px solid var(--accent); border-radius:8px; padding:11px 14px; margin:12px 0; }}
</style>

<h1>Electricity Act 2003 — §126/§135 Jurisprudence Map</h1>
<p class="sub">Aggregation pass over {cg['n_records']} case-records · combined from <code>provision_index</code> · <code>issue_matrix</code> · <code>citation_graph</code></p>

<div>
<span class=stat><b>{cg['n_records']}</b> records</span>
<span class=stat><b>{len(pi)}</b> provisions</span>
<span class=stat><b>{len(im)}</b> issue-nodes</span>
<span class=stat><b>{cg['n_authority_edges']}</b> authority citations</span>
<span class=stat><b>{len(edges_in)}</b> in-corpus edges</span>
</div>

<div class=callout>🔑 <b>Backbone finding:</b> the single most load-bearing authority across the corpus is
<b>Executive Engineer (SOUTHCO) v. Seetaram Rice Mill</b> (2012) 2 SCC 108 — <b>cited by 6 of 12 records</b>
(5× followed). It is <b>not yet a record</b> → it is the #1 Supreme-Court-wave target.</div>

<h2>1 · Provision index <span class=meta>— every holding grouped by section, oldest→newest, with the statutory version applied</span></h2>
{''.join(prov_html)}

<h2>2 · Issue matrix <span class=meta>— line of authority + leading case per issue-node</span></h2>
{''.join(issue_html)}

<h2>3 · Citation backbone <span class=meta>— authorities the corpus repeatedly rests on (≥2 records)</span></h2>
<table><thead><tr><th>freq</th><th>authority</th><th>treatment</th><th>cited by</th></tr></thead>
<tbody>{''.join(back_html)}</tbody></table>
"""
open(os.path.join(HERE, "jurisprudence_map.html"), "w").write(doc)
print("wrote jurisprudence_map.html")
