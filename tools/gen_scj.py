#!/usr/bin/env python3
"""Supply Code Jurisprudence: lean record JSON -> self-contained digest HTML.

Usage:  python tools/gen_scj.py <record.json> <out.html>
Then render to PDF (Chromium, headless):
  chromium --headless=new --no-sandbox --no-pdf-header-footer \
           --print-to-pdf=<out.pdf> file://<abs path to out.html>

The lean schema is the SINGLE source of truth (supply-code/summaries/json/<id>.json).
Unlike the older tools/gen_hc.py (which renders the bulky per-case digest), this
generator renders only what the jurisprudence keeps: identity, headnote,
holding-units (supply_code = green, interplay = grey), principle tags,
not-decided register, and the 4-column table of authorities. HTML is fully
self-contained (styles inlined) so the PDF renders with no external assets.
Strings are treated as PLAIN TEXT and HTML-escaped; only the "smart" punctuation
already in the data is preserved.
"""
import sys, json, html

TREAT_CLASS = {
    "followed": "t-foll", "approved": "t-foll", "applied": "t-foll", "affirmed": "t-foll",
    "distinguished": "t-dist", "doubted": "t-dist", "overruled": "t-dist",
    "referred": "t-ref", "referred to": "t-ref", "noted": "t-ref", "considered": "t-ref",
    "relied on": "t-rel", "relied-on": "t-rel", "relied upon": "t-rel",
}

# who put the authority before the court
CITEDBY_CLASS = {
    "petitioner": "cb-pet", "appellant": "cb-pet",
    "respondent": "cb-resp", "respondents": "cb-resp",
    "court": "cb-court", "suo motu": "cb-court", "bench": "cb-court",
}

STYLE = """<style>
  @page{ size:A4; margin:0; }
  body{ font-family:Georgia,'Liberation Serif',serif; font-size:9.8pt; line-height:1.5;
        color:#1d2430; margin:0; padding:16mm 17mm; }
  .eyebrow{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.4pt; letter-spacing:.18em;
        text-transform:uppercase; color:#6b7787; margin-bottom:4pt; }
  h1{ font-size:15pt; margin:0 0 3pt; font-weight:700; }
  .idline{ background:#eef1f5; border-left:3px solid #64748b; padding:6pt 11pt; margin:0 0 11pt;
        font-size:9pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .headnote{ background:#f4f6f9; border:1pt solid #c9d3df; border-radius:3pt;
        padding:8pt 12pt; margin:0 0 12pt; font-size:9.4pt; line-height:1.5; text-align:justify;
        -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .headnote .hn{ display:block; font-family:Arial,'Liberation Sans',sans-serif; font-size:7.6pt;
        letter-spacing:.32em; text-transform:uppercase; font-weight:700; color:#14324f; margin-bottom:4pt; }
  .seclabel{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.4pt; letter-spacing:.13em;
        text-transform:uppercase; font-weight:700; color:#64748b; margin:14pt 0 6pt; }

  .hu{ border:1pt solid #a9d6ba; border-left:4px solid #2f8f57; border-radius:3pt;
        margin:0 0 11pt; overflow:hidden; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .hu-head{ background:#e3f3e8; padding:5pt 11pt; font-family:Arial,'Liberation Sans',sans-serif; }
  .hu-key{ font-size:9.4pt; font-weight:700; color:#14532d; }
  .hu-topic{ font-size:8pt; color:#2f6b46; }
  .hu-body{ padding:7pt 11pt 8pt; }
  .fld{ margin:0 0 6pt; } .fld:last-child{ margin-bottom:0; }
  .fl{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.2pt; letter-spacing:.13em;
        text-transform:uppercase; font-weight:700; color:#2f8f57; display:block; margin-bottom:1pt; }
  .fld p{ margin:0; text-align:justify; }
  .pn{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.8pt; font-weight:700;
        color:#8a94a3; white-space:nowrap; }

  .aux{ border:1pt solid #c7d0db; border-left:4px solid #64748b; }
  .aux .hu-head{ background:#eef1f5; }
  .aux .hu-key{ color:#334155; } .aux .fl{ color:#64748b; }
  .flagbox{ background:#fbf3d6; border:.5pt solid #e6d69a; border-radius:2pt; padding:3pt 8pt;
        font-size:8.6pt; color:#5b5010; margin-top:5pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .flagbox .fl{ color:#8a6d1a; display:inline; margin-right:5pt; }

  .tag{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.6pt; font-weight:700;
        color:#5b3a04; background:#fbf3d6; border:.5pt solid #e6d69a; padding:1.5pt 7pt;
        border-radius:8pt; white-space:nowrap; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .ptag{ margin:0 0 6pt; }
  .docid{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.4pt; color:#8a94a3; }
  .cn{ font-style:italic; }

  .nd{ background:#fbe9e0; border:.5pt solid #e8b79c; border-radius:3pt; padding:6pt 11pt;
        font-size:9pt; color:#7a2e0e; margin:0 0 8pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .nd .fl{ color:#b05a2a; }

  table.cit{ width:100%; border-collapse:collapse; margin:3pt 0 8pt; font-size:8.4pt; line-height:1.42; }
  table.cit th{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7pt; letter-spacing:.12em;
        text-transform:uppercase; color:#fff; background:#334155; text-align:left; padding:4pt 7pt;
        -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  table.cit td{ border-bottom:.5pt solid #dbe2ea; padding:4.5pt 7pt; vertical-align:top; }
  table.cit tr:nth-child(even) td{ background:#f8fafc; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .trt{ font-size:7.4pt; padding:1pt 6pt; border-radius:8pt; white-space:nowrap; display:inline-block;
        font-family:Arial,'Liberation Sans',sans-serif; font-weight:700;
        -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .t-foll{ color:#14532d; background:#e3f3e8; border:.5pt solid #a9d6ba; }
  .t-dist{ color:#7a2e0e; background:#fbe9e0; border:.5pt solid #e8b79c; }
  .t-ref { color:#334155; background:#eef1f5; border:.5pt solid #c7d0db; }
  .t-rel { color:#5f5010; background:#fbf3d6; border:.5pt solid #e6d69a; }
  .cb{ font-size:7.4pt; padding:1pt 6pt; border-radius:8pt; white-space:nowrap; display:inline-block;
       font-family:Arial,'Liberation Sans',sans-serif; font-weight:700;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .cb-pet{ color:#1e3a5f; background:#e6eefb; border:.5pt solid #b3ccef; }
  .cb-resp{ color:#5b2c46; background:#fbe6f1; border:.5pt solid #e8b3d2; }
  .cb-court{ color:#334155; background:#e9edf2; border:.5pt solid #c2ccd8; }

  .foot{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.6pt; color:#8a94a3;
        border-top:.5pt solid #c9d3df; margin-top:14pt; padding-top:5pt; }
  .disclaimer{ font-size:7.8pt; color:#8a94a3; font-style:italic; margin-top:3pt; }
</style>"""


def esc(s):
    return html.escape(str(s or ""), quote=False)


def pin(paras):
    p = (paras or "").strip()
    return f' <span class="pn">&para;&nbsp;{esc(p)}</span>' if p else ""


def field(label, value, pn_str=""):
    if not value:
        return ""
    return (f'      <div class="fld"><span class="fl">{esc(label)}</span>'
            f'<p>{esc(value)}{pin(pn_str)}</p></div>\n')


def holding_unit(u):
    interplay = (u.get("type") == "interplay")
    cls = "hu aux" if interplay else "hu"
    kind = "INTERPLAY" if interplay else "HOLDING-UNIT"
    key = u.get("provision") or u.get("clause") or ""
    head = (f'    <div class="hu-head"><span class="hu-key">{esc(kind)} &middot; {esc(key)}</span>'
            f'<br><span class="hu-topic">{esc(u.get("topic",""))}</span></div>\n')
    body = '    <div class="hu-body">\n'
    body += field("Question", u.get("question"))
    body += field("Holding", u.get("holding"), u.get("paras", ""))
    body += field("Limiting facts", u.get("limiting_facts"))
    body += field("Qualifier", u.get("qualifier"))
    if u.get("flag"):
        body += (f'      <div class="flagbox"><span class="fl">Flag</span>{esc(u["flag"])}</div>\n')
    body += '    </div>\n'
    return f'  <div class="{cls}">\n{head}{body}  </div>\n'


def principle_tag(t):
    auths = ""
    la = t.get("lead_authorities") or []
    if la:
        parts = []
        for a in la:
            d = f' <span class="docid">[{esc(a["docid"])}]</span>' if a.get("docid") else ""
            parts.append(f'<span class="cn">{esc(a["name"])}</span>{d}')
        auths = " Lead authorities: " + ", ".join(parts) + "."
    return (f'  <p class="ptag"><span class="tag">{esc(t.get("tag",""))}</span>&nbsp; '
            f'{esc(t.get("application",""))}{auths}{pin(t.get("paras",""))}</p>\n')


def not_decided(n):
    d = f' <span class="docid">[{esc(n["docid"])}]</span>' if n.get("docid") else ""
    return (f'  <div class="nd"><span class="fl">Not decided &mdash; {esc(n.get("point",""))}</span>'
            f'{esc(n.get("note",""))}{d}{pin(n.get("paras",""))}</div>\n')


def auth_row(a):
    cls = TREAT_CLASS.get((a.get("treatment") or "").strip().lower(), "t-ref")
    meta = []
    if a.get("citation"):
        meta.append(esc(a["citation"]))
    if a.get("docid"):
        meta.append(f'<span class="docid">[{esc(a["docid"])}]</span>')
    if a.get("court"):
        meta.append(f'<span class="docid">{esc(a["court"])}</span>')
    metahtml = "<br>".join(meta)
    ht = esc(a.get("how_treated", "")) + pin(a.get("how_treated_paras", ""))
    cb = a.get("cited_by", "")
    cb_cell = ""
    if cb:
        cbcls = CITEDBY_CLASS.get(cb.strip().lower(), "cb-court")
        cb_cell = f'<span class="cb {cbcls}">{esc(cb)}</span>'
    return (f'      <tr>\n'
            f'        <td><span class="cn">{esc(a["name"])}</span><br>{metahtml}</td>\n'
            f'        <td>{esc(a.get("proposition",""))}</td>\n'
            f'        <td>{ht}</td>\n'
            f'        <td>{cb_cell}</td>\n'
            f'        <td><span class="trt {cls}">{esc(a.get("treatment","Referred"))}</span></td>\n'
            f'      </tr>\n')


def build(c):
    ident = " &middot; ".join(x for x in [
        esc(c.get("court", "")), esc(c.get("bench", "")),
        esc(c.get("date_display") or c.get("date_of_judgment", "")),
        esc(c.get("neutral_citation", "")), esc(c.get("docket", "")),
        f'<strong>{esc(c.get("disposition",""))}</strong>' if c.get("disposition") else "",
    ] if x)

    hus = "".join(holding_unit(u) for u in c.get("holding_units", []))
    tags = "".join(principle_tag(t) for t in c.get("principle_tags", []))
    nds = "".join(not_decided(n) for n in c.get("not_decided", []))
    rows = "".join(auth_row(a) for a in c.get("authorities", []))

    tags_sec = f'  <div class="seclabel">Principle tags</div>\n{tags}' if tags else ""
    nd_sec = f'  <div class="seclabel">Not decided &mdash; negative authority</div>\n{nds}' if nds else ""
    auth_sec = ""
    if rows:
        auth_sec = (
            '  <div class="seclabel">Table of Authorities</div>\n'
            '  <table class="cit"><thead><tr>'
            '<th style="width:21%">Authority</th><th style="width:28%">Proposition</th>'
            '<th style="width:27%">How Treated</th><th style="width:11%">Cited By</th>'
            '<th style="width:13%">Treatment</th>'
            f'</tr></thead>\n    <tbody>\n{rows}    </tbody>\n  </table>\n')

    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8">
{STYLE}
</head>
<body>
  <div class="eyebrow">Supply Code Jurisprudence &middot; {esc(c.get("case_id",""))}</div>
  <h1>{esc(c.get("title",""))}</h1>
  <div class="idline">{ident}</div>

  <div class="headnote"><span class="hn">H&nbsp;E&nbsp;A&nbsp;D&nbsp;N&nbsp;O&nbsp;T&nbsp;E</span>{esc(c.get("headnote",""))}</div>

  <div class="seclabel">Holding-units</div>
{hus}
{tags_sec}{nd_sec}{auth_sec}
  <div class="foot">{esc(c.get("case_id",""))} &middot; {esc(c.get("title",""))} &middot; {esc(c.get("neutral_citation",""))} &middot; Supply Code Jurisprudence
    <div class="disclaimer">A jurisprudence extract prepared from the text of the judgment; not a substitute for the judgment, and to be verified against the original before use.</div>
  </div>
</body>
</html>
"""


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    c = json.load(open(src))
    open(out, "w").write(build(c))
    print(f"wrote {out} from {src} "
          f"({len(c.get('holding_units', []))} holding-units, {len(c.get('authorities', []))} authorities)")
