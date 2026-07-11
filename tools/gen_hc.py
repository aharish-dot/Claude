#!/usr/bin/env python3
"""HC/SC digest generator: structured extract JSON -> digest HTML (the approved HC format).

Usage: python tools/gen_hc.py <extract.json> <out.html>
The extract JSON schema is documented by high-court/extracts/HC-001.extract.json (the golden
reference). Strings may contain inline HTML (<em>, <strong>, <span class="cn">, entities).
Render the HTML with tools/render2.js, passing court_short + scope for the running header.
"""
import sys, json, html as _h

HC_STYLE = """<style>
  ol.issues{ margin:2pt 0 9pt; padding-left:18pt; }
  ol.issues li{ margin:0 0 5pt; text-align:justify; padding-left:4pt; }
  .ratio{ color:#14532d; background:#eef7f0; border-left:3px solid #2f8f57;
          padding:9pt 13pt; margin:2pt 0 12pt; font-size:9.9pt; line-height:1.46;
          -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .ratio .hn, .disp .hn{ display:block; font-family:Arial,'Liberation Sans',sans-serif;
          font-size:7.6pt; letter-spacing:.16em; text-transform:uppercase; font-weight:700; margin-bottom:3pt; }
  .ratio .hn{ color:#2f8f57; } .ratio .cn{ color:#14532d; }
  .disp{ color:#5b3a04; background:#fbf6ec; border-left:3px solid #b7791f;
         padding:9pt 13pt; margin:2pt 0 10pt; font-size:9.9pt; line-height:1.46;
         -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .disp .hn{ color:#b7791f; }
  .trt{ font-size:8.2pt; padding:1pt 6pt; border-radius:8pt; white-space:nowrap; display:inline-block;
        font-family:Arial,'Liberation Sans',sans-serif; letter-spacing:.02em; font-weight:700;
        -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .t-foll{ color:#14532d; background:#e3f3e8; border:.5pt solid #a9d6ba; }
  .t-dist{ color:#7a2e0e; background:#fbe9e0; border:.5pt solid #e8b79c; }
  .t-ref { color:#334155; background:#eef1f5; border:.5pt solid #c7d0db; }
  .t-rel { color:#5f5010; background:#fbf3d6; border:.5pt solid #e6d69a; }
  .pn{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.8pt; font-weight:700;
       color:#8a94a3; white-space:nowrap; letter-spacing:.02em; }
  .src{ font-family:Arial,'Liberation Sans',sans-serif; font-size:6.8pt; font-weight:700;
        letter-spacing:.09em; padding:1pt 5pt; border-radius:7pt; vertical-align:middle;
        margin-left:7pt; white-space:nowrap;
        -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .src-sc{ color:#5b3a04; background:#fbf3d6; border:.5pt solid #e6d69a; }
  .src-hc{ color:#14532d; background:#e3f3e8; border:.5pt solid #a9d6ba; }
</style>"""

TRT = {'followed':'t-foll','approved':'t-foll','affirmed':'t-foll','applied':'t-foll',
       'distinguished':'t-dist','doubted':'t-dist','overruled':'t-dist','dissented from':'t-dist',
       'referred':'t-ref','referred to':'t-ref','discussed':'t-ref','considered':'t-ref','noted':'t-ref',
       'relied on':'t-rel','relied-on':'t-rel','relied upon':'t-rel'}

def row(k, v):
    return f'    <div class="row"><div class="k">{k}</div><div class="v">{v}</div></div>'

def bl_items(items, tag='p'):
    if tag == 'li':
        return "\n".join(f'    <li><span class="bl">{lead}</span> {body}</li>' for lead, body in items)
    return "\n".join(f'  <p><span class="bl">{lead}</span> {body}</p>' for lead, body in items)

def build(c):
    doj = c["date_of_judgment"]
    if c.get("date_note"):
        doj += f' &nbsp;<span style="color:#5b6b7f">({c["date_note"]})</span>'
    docket = "\n".join([
        row("Court", c["court"]), row("Coram", c["coram"]), row("Date of Judgment", doj),
        row("Nature of Proceeding", c["nature"]), row("Parties", c["parties"]),
        row("Provisions", c["provisions"]), row("Result", c["result"])])
    issues = "\n".join(f'    <li>{i}</li>' for i in c["issues"])
    facts = "\n".join(f'  <p>{p}</p>' for p in c["facts"])
    reasoning = bl_items(c["reasoning"])
    interp = f'  <h3 class="grp">{c.get("interp_group","Electricity Act, 2003")}</h3>\n' + "\n".join(
        f'  <h3>{h}</h3>\n  <p>{t}</p>' for h, t in c["interpretation"])
    obiter = bl_items(c.get("obiter", []), 'li')
    obiter_block = (f'  <h2>Also Held &amp; Obiter</h2>\n  <ul class="sig">\n{obiter}\n  </ul>\n' if c.get("obiter") else "")
    sig = bl_items(c["significance"], 'li')
    auth_rows = []
    for a in c["authorities"]:
        cls = TRT.get((a.get("treatment") or "").strip().lower(), 't-ref')
        cite = a.get("cite", "")
        if a.get("court"):
            cite += (" &middot; " if cite else "") + a["court"]
        auth_rows.append(
            f'      <tr>\n        <td><span class="cn">{a["name"]}</span><br>{cite}</td>\n'
            f'        <td>{a["prop"]}</td>\n'
            f'        <td><span class="trt {cls}">{a.get("treatment","Referred")}</span></td>\n      </tr>')
    auth = "\n".join(auth_rows)
    _cl = c.get("court", "").lower()
    court_type = ("Supreme Court" if "supreme court" in _cl
                  else "High Court" if "high court" in _cl
                  else (c.get("court_short") or "Judgment"))
    interp_h2 = c.get("interp_heading") or "Interpretation of the Electricity Statutes"
    reasoning_h2 = c.get("reasoning_heading") or "Reasoning of the Court"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="digest.css">
{HC_STYLE}
</head>
<body>

  <div class="eyebrow">{court_type} &middot; Judgment Digest</div>
  <h1 class="case">{c["title"]}</h1>
  <div class="subcite">{c["subcite"]}</div>

  <div class="docket">
{docket}
  </div>

  <h2>Point for Determination</h2>
  <ol class="issues">
{issues}
  </ol>

  <h2>Facts</h2>
{facts}

  <h2>{reasoning_h2}</h2>
  <div class="headnote">
    <span class="hn">Headnote</span>
    {c["headnote"]}
  </div>
{reasoning}

  <h2>{interp_h2}</h2>
{interp}

  <div class="ratio">
    <span class="hn">Ratio Decidendi</span>
    {c["ratio"]}
  </div>

{obiter_block}  <div class="disp">
    <span class="hn">Disposition</span>
    {c["disposition"]}
  </div>

  <h2>Significance</h2>
  <p>{c["sig_intro"]}</p>
  <ul class="sig">
{sig}
  </ul>

  <h2>Table of Authorities</h2>
  <p class="cit-preamble">{c.get("cit_preamble","Authorities discussed in the judgment, with the treatment each received.")}</p>
  <table class="cit">
    <thead>
      <tr><th style="width:30%">Authority</th><th style="width:52%">Proposition &amp; how treated</th><th style="width:18%">Treatment</th></tr>
    </thead>
    <tbody>
{auth}
    </tbody>
  </table>

  <p class="disclaimer">This digest is a condensed reference prepared from the text of the judgment. It is not a substitute for the full judgment and should be verified against the original before use.</p>

</body>
</html>
"""

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    c = json.load(open(src))
    open(out, "w").write(build(c))
    print(f"wrote {out} from {src} ({len(c.get('authorities',[]))} authorities)")
