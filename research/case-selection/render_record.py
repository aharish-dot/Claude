#!/usr/bin/env python3
"""Render a jurisprudence record JSON into a readable, print-styled HTML.
Usage: python3 render_record.py SC-001.record.json  ->  SC-001.record.html
Then render to PDF with render_record.js (Playwright/Chromium).
"""
import json, sys, html, os

path = sys.argv[1]
rec = json.load(open(path))
def esc(x): return html.escape(str(x))

def chips(items):
    return " ".join(f'<span class="chip">{esc(i)}</span>' for i in items)

issue_labels = {
    "126v135": "§126 vs §135", "assessment-126": "§126 assessment",
    "mensrea-135": "§135 mens rea", "appeal-127": "§127 appeal",
    "jurisdiction-145-154": "jurisdiction (§145/§154)", "compounding-152": "§152 compounding",
    "natural-justice": "natural justice", "provisional-final": "provisional/final",
    "burden-proof": "burden of proof", "limitation-56": "§56(2) limitation",
}
def ilabel(n): return issue_labels.get(n, n)

ph_rows = ""
for h in rec.get("provision_holdings", []):
    nodes = h.get("issue_node", [])
    if isinstance(nodes, str): nodes = [nodes]
    htype = h.get("holding_type","")
    htbadge = f'<span class="htype ht-{esc(htype)}">{esc(htype)}</span>' if htype else ""
    pver = f'<span class="pver">{esc(h.get("provision_version",""))}</span>' if h.get("provision_version") else ""
    ph_rows += f"""
    <div class="holding">
      <div class="holding-head">
        <span class="prov">{esc(h['provision'])}</span>{htbadge}{pver}
        <span class="itype">{esc(h.get('interpretation_type',''))}</span>
        <span class="nodes">{chips(ilabel(n) for n in nodes)}</span>
      </div>
      <div class="holding-body">{esc(h['holding'])}</div>
      <blockquote>&ldquo;{esc(h['key_para'])}&rdquo;<cite>&mdash; {esc(h.get('para_ref',''))}</cite></blockquote>
    </div>"""

auth_html = ""
if rec.get("authorities"):
    treat_class = {"followed":"t-follow","distinguished":"t-distinguish","overruled":"t-overrule",
                   "doubted":"t-overrule","explained":"t-follow","referred":"t-refer"}
    for a in rec["authorities"]:
        tr = a.get("treatment","")
        pp = f'<blockquote class="q-principle">&ldquo;{esc(a["principle_para"])}&rdquo;<cite>&mdash; as quoted in the judgment</cite></blockquote>' if a.get("principle_para") else ""
        tp = f'<blockquote class="q-treat">&ldquo;{esc(a["treatment_para"])}&rdquo;<cite>&mdash; the Court&rsquo;s own treatment</cite></blockquote>' if a.get("treatment_para") else ""
        auth_html += f"""
        <div class="authcard">
          <div class="auth-head">
            <span class="auth-name">{esc(a.get('name',''))}</span>
            <span class="auth-cite">{esc(a.get('cite',''))} &middot; {esc(a.get('court',''))}</span>
            <span class="treat {treat_class.get(tr,'t-refer')}">{esc(tr)}</span>
          </div>
          <div class="auth-prin">Cited for: {esc(a.get('principle',''))}</div>
          {pp}{tp}
        </div>"""
else:
    auth_html = f'<p class="none">{esc(rec.get("authorities_note","No authorities cited."))}</p>'

ratio_html = ""
for r in rec.get("ratio", []):
    conflicts = r.get("conflicts_with", [])
    cnote = f'<div class="conflict">Conflicts with: {esc(", ".join(conflicts))}</div>' if conflicts else ""
    note = f'<div class="rnote">{esc(r["note"])}</div>' if r.get("note") else ""
    ratio_html += f"""
    <div class="ratio">
      <div class="ratio-head"><span class="chip solid">{esc(ilabel(r['issue_node']))}</span>
      <span class="tag">{esc(r.get('scope',''))}</span><span class="tag alt">{esc(r.get('novelty',''))}</span></div>
      <div class="ratio-body">{esc(r['proposition'])}</div>{cnote}{note}
    </div>"""

prov_construed = ", ".join(esc(p["provision"]) for p in rec.get("provisions_construed", []))
flags = chips(rec.get("flags", []))

# --- validity ---
v = rec.get("validity", {})
val_class = {"good-law":"v-good","partially-overruled":"v-warn","superseded":"v-warn",
             "doubted":"v-warn","referred":"v-warn","overruled":"v-bad","reversed":"v-bad"}
val_html = ""
if v:
    per = "".join(f'<div class="vitem"><b>{esc(ilabel(k))}:</b> {esc(val)}</div>' for k,val in v.get("per_issue",{}).items())
    vnote = f'<div class="vnote">{esc(v["note"])}</div>' if v.get("note") else ""
    val_html = f"""<div class="validity {val_class.get(v.get('overall',''),'v-good')}">
      <span class="vbadge">{esc(v.get('overall','')).upper()}</span>
      <span class="vas">as of {esc(v.get('as_of',''))} &middot; provision-version OK: {esc(v.get('provision_version_ok'))}</span>
      {per}{vnote}</div>"""

# --- case profile ---
def kv(label, val):
    if not val: return ""
    if isinstance(val, list): val = ", ".join(str(x) for x in val)
    return f'<tr><td class="k">{esc(label)}</td><td>{esc(val)}</td></tr>'
profile = "".join([
    kv("Procedural posture", rec.get("procedural_posture")),
    kv("Outcome for", rec.get("outcome_for")),
    kv("Relief granted", rec.get("relief_granted")),
    kv("Consumer category", rec.get("consumer_category")),
    kv("Fact-pattern", rec.get("fact_pattern_tags")),
    kv("State", rec.get("state")),
    kv("DISCOM / party", rec.get("discom")),
    kv("Statutory version", rec.get("amendment_considered")),
])
profile_html = f'<table class="profile">{profile}</table>' if profile else ""

# --- issues framed ---
issues = rec.get("issues_framed", [])
issues_html = ("<ol class='issues'>" + "".join(f"<li>{esc(i)}</li>" for i in issues) + "</ol>") if issues else ""

# --- regulations construed ---
regs = rec.get("regulations_construed", [])
regs_html = ""
if regs:
    regs_html = "<ul class='regs'>" + "".join(
        f"<li><b>{esc(r.get('reg',''))}</b> &mdash; implements {esc(r.get('implements',''))}"
        + (f" (made under {esc(r.get('made_under',''))})" if r.get('made_under') else "") + "</li>"
        for r in regs) + "</ul>"

doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 18mm 16mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: Georgia, 'Times New Roman', serif; color:#1a1a1a; font-size:11pt; line-height:1.5; }}
h1 {{ font-size:16pt; margin:0 0 2px; }}
.sub {{ color:#555; font-size:10pt; margin-bottom:2px; }}
.meta {{ font-size:9.5pt; color:#444; border-bottom:2px solid #7a2e2e; padding-bottom:8px; margin-bottom:14px; }}
.meta b {{ color:#111; }}
.oneline {{ background:#f7f2ee; border-left:3px solid #7a2e2e; padding:8px 12px; font-style:italic; margin:12px 0; }}
h2 {{ font-size:11.5pt; color:#7a2e2e; border-bottom:1px solid #d8c9c0; padding-bottom:3px; margin:18px 0 8px; text-transform:uppercase; letter-spacing:.5px; }}
.holding {{ margin:0 0 12px; padding:0 0 10px; border-bottom:1px dotted #ddd; }}
.holding-head {{ margin-bottom:4px; }}
.prov {{ font-weight:bold; background:#7a2e2e; color:#fff; padding:1px 7px; border-radius:3px; font-size:9.5pt; font-family:Arial,sans-serif; }}
.itype {{ font-family:Arial,sans-serif; font-size:8.5pt; color:#7a2e2e; margin-left:6px; }}
.nodes {{ float:right; }}
.chip {{ display:inline-block; background:#efe7e2; color:#5a3a30; border:1px solid #ddcfc7; border-radius:10px; padding:0 8px; font-size:8pt; font-family:Arial,sans-serif; margin-left:3px; }}
.chip.solid {{ background:#7a2e2e; color:#fff; border-color:#7a2e2e; }}
.holding-body {{ margin:3px 0; }}
blockquote {{ margin:5px 0 0; padding:5px 10px; background:#faf8f6; border-left:2px solid #bbb; font-size:9.5pt; color:#333; }}
blockquote cite {{ display:block; text-align:right; font-size:8.5pt; color:#888; font-style:normal; }}
.authcard {{ margin:0 0 11px; padding:0 0 9px; border-bottom:1px dotted #ddd; }}
.auth-head {{ margin-bottom:3px; }}
.auth-name {{ font-weight:bold; }}
.auth-cite {{ color:#888; font-size:8.5pt; margin-left:6px; }}
.auth-prin {{ font-size:9.5pt; color:#333; margin:2px 0; }}
.treat {{ float:right; padding:1px 8px; border-radius:3px; font-size:8pt; font-family:Arial,sans-serif; color:#fff; }}
.t-follow {{ background:#2e6a3e; }}
.t-distinguish {{ background:#a85a2e; }}
.t-overrule {{ background:#8a2e2e; }}
.t-refer {{ background:#5a6b7a; }}
.q-principle {{ border-left:2px solid #bbb; }}
.q-treat {{ border-left:2px solid #a85a2e; background:#faf5f1; }}
.none {{ font-style:italic; color:#666; background:#faf8f6; padding:8px 12px; border-left:2px solid #ccc; }}
.ratio {{ margin:0 0 10px; padding:8px 12px; background:#f7f2ee; border-radius:4px; }}
.ratio-head {{ margin-bottom:4px; }}
.tag {{ font-family:Arial,sans-serif; font-size:8pt; color:#555; background:#e8e0da; padding:1px 6px; border-radius:3px; margin-left:4px; }}
.tag.alt {{ background:#dde7ee; color:#2a4a5e; }}
.conflict {{ color:#8a2e2e; font-size:9pt; margin-top:3px; }}
.rnote {{ color:#666; font-size:9pt; font-style:italic; margin-top:3px; }}
.sig {{ font-size:10.5pt; }}
.htype {{ font-family:Arial,sans-serif; font-size:7.5pt; color:#fff; padding:1px 6px; border-radius:3px; margin-left:5px; }}
.ht-ratio {{ background:#2e5a6b; }}
.ht-explanatory {{ background:#8a7a2e; }}
.ht-obiter {{ background:#9a6a3a; }}
.pver {{ font-family:Arial,sans-serif; font-size:7.5pt; color:#666; background:#eee; padding:1px 6px; border-radius:3px; margin-left:4px; }}
.validity {{ padding:8px 12px; border-radius:4px; margin:12px 0; font-size:9.5pt; }}
.v-good {{ background:#eef5ee; border-left:4px solid #2e6a3e; }}
.v-warn {{ background:#fbf5e9; border-left:4px solid #b8860b; }}
.v-bad {{ background:#f8eded; border-left:4px solid #8a2e2e; }}
.vbadge {{ font-family:Arial,sans-serif; font-weight:bold; font-size:9pt; letter-spacing:.5px; }}
.vas {{ color:#666; font-size:8.5pt; margin-left:8px; }}
.vitem {{ margin-top:4px; }}
.vnote {{ margin-top:4px; color:#555; font-style:italic; font-size:9pt; }}
table.profile {{ width:100%; border-collapse:collapse; font-size:9.5pt; margin:4px 0; }}
table.profile td {{ padding:3px 8px; border-bottom:1px solid #f0eae6; vertical-align:top; }}
table.profile td.k {{ width:150px; color:#7a2e2e; font-family:Arial,sans-serif; font-size:8.5pt; }}
ol.issues {{ margin:4px 0 4px 18px; padding:0; font-size:10pt; }}
ol.issues li {{ margin-bottom:4px; }}
ul.regs {{ margin:4px 0 4px 18px; padding:0; font-size:9.5pt; }}
ul.regs li {{ margin-bottom:3px; }}
.foot {{ margin-top:16px; padding-top:8px; border-top:1px solid #ddd; font-size:8.5pt; color:#888; }}
</style></head><body>
<h1>{esc(rec['title'])}</h1>
<div class="sub">{esc(rec.get('neutral_cite',''))}</div>
<div class="meta">
<b>{esc(rec['court'])}</b> ({esc(rec.get('bench_type', rec['court_type']))}) &nbsp;|&nbsp; {esc(rec['date'])} &nbsp;|&nbsp;
Bench: {esc(', '.join(rec.get('bench',[])))} ({esc(rec.get('bench_strength',''))}) &nbsp;|&nbsp;
IK doc {esc(rec['docid'])} &nbsp;|&nbsp; {esc(rec['case_id'])} &nbsp;|&nbsp; schema {esc(rec.get('schema_version',''))}
</div>

<div class="oneline">{esc(rec['one_line'])}</div>
{val_html}

<h2>Facts &amp; profile</h2>
<p>{esc(rec.get('facts_squib',''))}</p>
{profile_html}
<p style="font-size:9.5pt;color:#555"><b>Disposition:</b> {esc(rec.get('disposition',''))}</p>

<h2>Issues framed</h2>
{issues_html}

<h2>Interpretation of the Electricity Act</h2>
<p style="font-size:9pt;color:#666">Provisions construed: {prov_construed}</p>
{ph_rows}
{f'<h2>Regulations / Supply Code construed</h2>{regs_html}' if regs_html else ''}

<h2>Authorities cited</h2>
{auth_html}

<h2>Ratio &amp; what was decided</h2>
{ratio_html}

<h2>Significance</h2>
<p class="sig">{esc(rec['significance'])}</p>

<h2>Flags</h2>
<p>{flags}</p>

<div class="foot">Jurisprudence record &mdash; generated from {esc(os.path.basename(path))} for the Electricity Act §126/§135 project. Verbatim quotes are grep-verifiable against the source judgment.</div>
</body></html>"""

out = path.replace(".json", ".html")
open(out, "w").write(doc)
print("wrote", out)
