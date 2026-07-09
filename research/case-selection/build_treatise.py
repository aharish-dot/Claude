#!/usr/bin/env python3
"""Render the three aggregation index files into one readable, theme-aware HTML
'jurisprudence map'. Self-contained (inline CSS). Run after build_aggregation.py.

Every case reference carries a compact (IK/GH) link pair:
  IK  -> Indian Kanoon judgment. For a specific holding it is a text-fragment
         deep link (#:~:text=...) built from the exact verbatim key_para, so the
         browser scrolls to and highlights that holding (Chromium/Safari; Firefox
         ignores the fragment and lands at the top of the judgment).
  GH  -> the record JSON on GitHub with a #L<start>-L<end> anchor on the holding
         block, so GitHub scrolls to and highlights it.
The paragraph number of each holding (para_ref) is always shown as plain text.
"""
import json, os, re, glob, html, subprocess
import urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))

pi = json.load(open(os.path.join(HERE, "provision_index.json")))
im = json.load(open(os.path.join(HERE, "issue_matrix.json")))
cg = json.load(open(os.path.join(HERE, "citation_graph.json")))

def e(s): return html.escape(str(s if s is not None else ""))
VBADGE = {"post-2007": "#2e7d32", "pre-2007": "#b26a00", "pre-2003": "#8e24aa", None: "#666"}

def vbadges(vs):
    return " ".join(f'<span class="ver" style="background:{VBADGE.get(v,"#666")}">{e(v)}</span>' for v in vs)

# ---------------------------------------------------------------- link machinery
def _git(*a):
    return subprocess.check_output(["git", "-C", HERE, *a]).decode().strip()
try:
    _remote = _git("remote", "get-url", "origin")
    _m = re.search(r"/([^/]+)/([^/]+?)(?:\.git)?/?$", _remote)
    OWNER, REPO = (_m.group(1), _m.group(2)) if _m else ("aharish-dot", "Claude")
    BRANCH = _git("rev-parse", "--abbrev-ref", "HEAD")
    SHA = _git("rev-parse", "HEAD")
    TOPLEVEL = _git("rev-parse", "--show-toplevel")
except Exception:
    OWNER, REPO, BRANCH, SHA, TOPLEVEL = "aharish-dot", "Claude", "main", "HEAD", os.path.dirname(HERE)
# GH links render the per-case HTML via githack (a CDN that serves committed files
# with the right content-type so the browser renders them, and supports #anchors).
# We pin the commit SHA rather than the branch: the branch name contains slashes,
# which githack/raw cannot disambiguate, and a SHA is cached immutably. NOTE: this
# requires the record HTMLs to already be committed at HEAD before the map is built
# (run render_record.py + commit the records, THEN build_treatise.py + commit the map),
# and it only resolves once the repository is public (githack cannot read private repos).
GITHACK = f"https://rawcdn.githack.com/{OWNER}/{REPO}/{SHA}"

def _record_paths():
    paths = glob.glob(os.path.join(HERE, "records", "*.record.json"))
    paths += [os.path.join(HERE, p) for p in ("SC-001.record.json", "HC-003.record.json")
              if os.path.exists(os.path.join(HERE, p))]
    return sorted(paths)

# case_meta[case_id]                 -> {docid, rel}
# hold_meta[(case_id, holding_text)] -> {docid, rel, para_ref, key_para, gh_start, gh_end}
case_meta, hold_meta = {}, {}
for path in _record_paths():
    r = json.load(open(path))
    cid = r["case_id"]
    rel = os.path.relpath(path, TOPLEVEL)
    case_meta[cid] = {"docid": r.get("docid", ""), "rel": rel}
    for hidx, h in enumerate(r.get("provision_holdings", [])):
        # hidx aligns with the id="h{hidx}" anchors emitted by render_record.py, so a
        # GH link can jump straight to the holding in the rendered case page.
        hold_meta[(cid, h.get("holding"))] = {
            "docid": r.get("docid", ""), "rel": rel, "hidx": hidx,
            "para_ref": h.get("para_ref", ""), "key_para": h.get("key_para", ""),
        }

def _textfrag(text):
    """Build a #:~:text= fragment from an exact verbatim passage. For long passages
    use textStart,textEnd (first/last few words) so the match is robust."""
    words = (text or "").split()
    q = lambda s: urllib.parse.quote(s, safe="")
    if not words:
        return ""
    if len(words) > 12:
        return f"#:~:text={q(' '.join(words[:6]))},{q(' '.join(words[-6:]))}"
    return f"#:~:text={q(' '.join(words))}"

def links(case_id, holding_text=None):
    """Return the compact '(IK/GH)' HTML for a case, deep-linking to a specific
    holding when holding_text is given and known."""
    cm = case_meta.get(case_id)
    if not cm:
        return ""
    docid, rel = cm["docid"], cm["rel"]
    rel_html = rel[:-len(".record.json")] + ".record.html" if rel.endswith(".record.json") else rel
    ik = f"https://indiankanoon.org/doc/{docid}/" if docid else ""
    gh = f"{GITHACK}/{urllib.parse.quote(rel_html)}"
    hm = hold_meta.get((case_id, holding_text)) if holding_text else None
    if hm:
        if docid and hm.get("key_para"):
            ik = f"https://indiankanoon.org/doc/{docid}/{_textfrag(hm['key_para'])}"
        if hm.get("hidx") is not None:
            gh = f"{GITHACK}/{urllib.parse.quote(rel_html)}#h{hm['hidx']}"
    ik_h = (f'<a href="{ik}" target="_blank" rel="noopener">IK</a>' if ik
            else '<span class="nolink">IK</span>')
    gh_h = f'<a href="{gh}" target="_blank" rel="noopener">GH</a>'
    return f'<span class="lk">({ik_h}/{gh_h})</span>'

def para_tag(case_id, holding_text):
    hm = hold_meta.get((case_id, holding_text))
    pr = hm.get("para_ref") if hm else None
    return f'<span class="para">{e(pr)}</span>' if pr else ""

# ---------------------------------------------------------------- provision index
prov_html = []
for sec, v in pi.items():
    hold = []
    for h in v["holdings_chronological"]:
        cid, htext = h["case_id"], h.get("holding")
        hold.append(f"""<tr>
          <td class="cid">{e(cid)}{links(cid, htext)}</td>
          <td>{e(h['date'][:4])}</td>
          <td>{e(h['provision_cited_as'])} <span class="ver" style="background:{VBADGE.get(h['provision_version'],'#666')}">{e(h['provision_version'])}</span></td>
          <td>{'· '.join('<span class=node>'+e(n)+'</span>' for n in h['issue_node'])}</td>
          <td class="{ 'ratio' if h['holding_type']=='ratio' else 'obiter'}">{e(h['holding_type'])}</td>
          <td>{para_tag(cid, htext)}{e(htext)}</td></tr>""")
    prov_html.append(f"""<details open>
      <summary><b>{e(sec)}</b> — {v['n_holdings']} holdings ({v['n_ratio']} ratio) · {len(v['cases'])} cases {vbadges(v['versions_applied'])}</summary>
      <table><thead><tr><th>Case</th><th>Yr</th><th>as</th><th>issue-node</th><th>type</th><th>holding (para · text)</th></tr></thead>
      <tbody>{''.join(hold)}</tbody></table></details>""")

# ---------------------------------------------------------------- issue matrix
issue_html = []
for node, v in im.items():
    line = " → ".join(
        f'<span class="cid">{e(c["case_id"])}</span>{links(c["case_id"])}'
        f'<span class=ct>{e(c["court_type"])}·{e(c["date"][:4])}</span>'
        for c in v["line_of_authority"])
    def card(p):
        cid = p["case_id"]
        if p.get("source") == "ratio":
            tag = f'<span class=scope>{e(p.get("scope"))}</span> <span class=nov>{e(p.get("novelty"))}</span>'
            lk, pt = links(cid), ""                       # ratio: case-level link, no verbatim para
        else:
            tag = f'<span class=hold>holding · {e(p.get("provision"))} · {e(p.get("holding_type"))}</span>'
            lk, pt = links(cid, p.get("text")), para_tag(cid, p.get("text"))
        return f"""<div class=prop><span class="cid">{e(cid)}</span>{lk} {tag} {pt}
              <div>{e(p['text'])}</div></div>"""
    props = "".join(card(p) for p in v["contributions"])
    _rank = {"SC": 3, "HC-DB": 2, "HC-SB": 1, "HC": 1}
    lead, apex = v["leading_case"], v.get("apex_case", {})
    apex_html = (f' · <span class=meta>apex</span> <span class=cid>{e(apex["case_id"])}</span> ({e(apex["court_type"])})'
                 if apex and _rank.get(apex["court_type"],0) > _rank.get(lead["court_type"],0) else "")
    issue_html.append(f"""<details {'open' if v['n_cases']>=4 else ''}>
      <summary><b>{e(node)}</b> — {v['n_cases']} cases · lead <span class=cid>{e(lead['case_id'])}</span>
        ({e(lead['court_type'])}){apex_html}{' <span class=split>HC SPLIT</span>' if v['split_flag'] else ''}</summary>
      <div class=line><b>line of authority:</b> {line}</div>
      {props}</details>""")

# ---------------------------------------------------------------- citation backbone
back_html = []
for b in cg["recurring_authorities"]:
    cb = ", ".join(f'{e(c["case_id"])}{links(c["case_id"])}<span class=ct>{e(c["treatment"])}</span>'
                   for c in b["cited_by"])
    back_html.append(f"""<tr><td class=big>{b['times_cited']}×</td>
      <td><b>{e(b['authority'])}</b><br><span class=meta>{e(b['cite'])} · {e(b['court'])}</span></td>
      <td>{e(b['treatments'])}</td><td class=cbcell>{cb}</td></tr>""")

edges_in = [x for x in cg["edges"] if x["in_corpus"]]
top = cg["recurring_authorities"][0] if cg["recurring_authorities"] else None
# is the top backbone authority itself now a record? (match by title against corpus)
_top_cid = None
if top:
    for cid, cm in case_meta.items():
        pass
_norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
if top:
    for sec in pi.values():
        for h in sec["holdings_chronological"]:
            if "seetaram" in _norm(top["authority"]) and h["case_id"] == "SC-002":
                _top_cid = "SC-002"
callout = ""
if top:
    incorpus = (f' — now recorded in-corpus as <span class=cid>{_top_cid}</span>{links(_top_cid)}'
                if _top_cid else " — not yet a record")
    callout = (f'🔑 <b>Backbone finding:</b> the single most load-bearing authority across the corpus is '
               f'<b>{e(top["authority"])}</b> {e(top["cite"])}{incorpus}, '
               f'<b>cited by {top["times_cited"]} of {cg["n_records"]} records</b> '
               f'({e(top["treatments"])}). It anchors the §126-vs-§135 line and several neighbouring nodes.')

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Electricity Act §126/§135 — Jurisprudence Map</title>
<style>
:root {{ --bg:#fff; --fg:#1a1a1a; --mut:#666; --line:#e2e2e2; --card:#f7f7f8; --accent:#0b5; --link:#1565c0; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#15161a; --fg:#e8e8ea; --mut:#9a9aa2; --line:#2c2e36; --card:#1d1f26; --link:#6fb0ff; }} }}
:root[data-theme=dark] {{ --bg:#15161a; --fg:#e8e8ea; --mut:#9a9aa2; --line:#2c2e36; --card:#1d1f26; --link:#6fb0ff; }}
:root[data-theme=light] {{ --bg:#fff; --fg:#1a1a1a; --mut:#666; --line:#e2e2e2; --card:#f7f7f8; --link:#1565c0; }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; margin:0; padding:28px; max-width:1050px; margin:auto; }}
h1 {{ font-size:26px; margin:0 0 4px; }} h2 {{ font-size:19px; margin:34px 0 10px; border-bottom:2px solid var(--accent); padding-bottom:5px; }}
.sub {{ color:var(--mut); margin:0 0 8px; }}
a {{ color:var(--link); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
.stat {{ display:inline-block; background:var(--card); border:1px solid var(--line); border-radius:8px; padding:8px 13px; margin:3px 5px 3px 0; }}
.stat b {{ font-size:20px; }}
details {{ border:1px solid var(--line); border-radius:8px; margin:8px 0; background:var(--card); }}
summary {{ cursor:pointer; padding:10px 13px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; padding:6px 9px; border-top:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--mut); font-weight:600; }}
.cid {{ font-weight:700; color:var(--accent); white-space:nowrap; }}
.ct {{ color:var(--mut); font-size:11px; margin-left:4px; }}
.lk {{ font-size:10.5px; font-weight:600; margin-left:2px; white-space:nowrap; }}
.lk a {{ color:var(--link); }}
.nolink {{ color:var(--mut); opacity:.5; }}
.ver {{ color:#fff; font-size:10px; padding:1px 6px; border-radius:9px; white-space:nowrap; }}
.node {{ background:var(--bg); border:1px solid var(--line); border-radius:9px; padding:0 6px; font-size:11px; margin-right:3px; white-space:nowrap; }}
.para {{ background:var(--bg); border:1px solid var(--line); border-radius:9px; padding:0 6px; font-size:11px; color:var(--mut); margin-right:5px; white-space:nowrap; font-weight:600; }}
.ratio {{ color:var(--accent); font-weight:600; }} .obiter {{ color:var(--mut); }}
.line {{ padding:8px 13px; font-size:13px; }} .line .cid{{margin-left:2px;}}
.prop {{ padding:6px 13px 10px; border-top:1px dashed var(--line); font-size:13px; }}
.scope {{ background:#0b52; border-radius:9px; padding:0 7px; font-size:11px; }}
.hold {{ background:#8884; border-radius:9px; padding:0 7px; font-size:11px; color:var(--mut); }}
.nov {{ color:var(--mut); font-size:11px; }}
.split {{ background:#c62828; color:#fff; padding:1px 7px; border-radius:9px; font-size:11px; }}
.big {{ font-size:20px; font-weight:700; color:var(--accent); }}
.meta {{ color:var(--mut); font-size:11px; }} .cbcell{{font-size:11px;}} .cbcell .ct{{color:var(--accent);}}
.callout {{ background:#0b51; border:1px solid var(--accent); border-radius:8px; padding:11px 14px; margin:12px 0; }}
.legend {{ color:var(--mut); font-size:12px; margin:0 0 18px; border:1px dashed var(--line); border-radius:8px; padding:8px 12px; }}
.legend code {{ font-size:11px; }}
</style></head><body>

<h1>Electricity Act 2003 — §126/§135 Jurisprudence Map</h1>
<p class="sub">Aggregation pass over {cg['n_records']} case-records · combined from <code>provision_index</code> · <code>issue_matrix</code> · <code>citation_graph</code></p>
<p class="legend">Each case shows <b>(<a href="#">IK</a>/<a href="#">GH</a>)</b> links.
<b>IK</b> = the judgment on Indian Kanoon; on a specific holding it jumps to and highlights the exact passage
(text-fragment link — works in Chrome/Edge/Safari; Firefox opens the judgment at the top).
<b>GH</b> = the rendered case page (via githack), which opens with that holding highlighted.
The paragraph number of each holding is shown as a tag, e.g. <span class="para">para 23</span>.</p>

<div>
<span class=stat><b>{cg['n_records']}</b> records</span>
<span class=stat><b>{len(pi)}</b> provisions</span>
<span class=stat><b>{len(im)}</b> issue-nodes</span>
<span class=stat><b>{cg['n_authority_edges']}</b> authority citations</span>
<span class=stat><b>{len(edges_in)}</b> in-corpus edges</span>
</div>

<div class=callout>{callout}</div>

<h2>1 · Provision index <span class=meta>— every holding grouped by section, oldest→newest, with the statutory version applied</span></h2>
{''.join(prov_html)}

<h2>2 · Issue matrix <span class=meta>— line of authority + leading case per issue-node</span></h2>
{''.join(issue_html)}

<h2>3 · Citation backbone <span class=meta>— authorities the corpus repeatedly rests on (≥2 records)</span></h2>
<table><thead><tr><th>freq</th><th>authority</th><th>treatment</th><th>cited by</th></tr></thead>
<tbody>{''.join(back_html)}</tbody></table>
</body></html>
"""
# ASCII-only output (numeric entities) so the page never mojibakes regardless of
# how the viewer guesses the charset.
open(os.path.join(HERE, "jurisprudence_map.html"), "w",
     encoding="ascii", errors="xmlcharrefreplace").write(doc)
print("wrote jurisprudence_map.html")
