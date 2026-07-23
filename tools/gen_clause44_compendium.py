#!/usr/bin/env python3
"""Combine the full digest summaries of the Clause 4.4 (occupier/tenant) cases
into one chronological compendium PDF, reusing gen_scj.py's per-case renderer."""
import json, re, html, sys, os
sys.path.insert(0,'tools')
import gen_scj
esc=html.escape

order=json.load(open('/tmp/clause44.json'))
cases=[json.load(open(f'supply-code/summaries/json/{cid}.json')) for cid in order]

MONTHS={m:i for i,m in enumerate(['january','february','march','april','may','june','july','august','september','october','november','december'],1)}
def yr(d):
    s=d.get('date_of_judgment') or d.get('date_display',''); m=re.search(r'(\d{4})',s or ''); return m.group(1) if m else ''
def badge(c):
    c=(c or '').lower()
    return 'SC' if 'supreme' in c else ('All HC' if 'allahabad' in c else ('HC' if 'high court' in c else ''))
def party(t): return re.sub(r'\s*\[.*?\]\s*$','',t or '')

def body_of(c):
    full=gen_scj.build(c)
    m=re.search(r'<body>(.*)</body>', full, re.S)
    return m.group(1)

COVER="""<style>
@page{ size:A4; margin:15mm 16mm; }
.cw{ height:255mm; display:flex; flex-direction:column; justify-content:center; text-align:center; page-break-after:always; }
.cw .crest{ font-family:Arial,sans-serif; font-size:8pt; letter-spacing:.4em; text-transform:uppercase; color:#2f6f9f; margin-bottom:18pt; }
.cw h1{ font-family:Georgia,serif; font-size:26pt; color:#0f2f4c; margin:0 0 4pt; line-height:1.2; }
.cw .cl{ font-family:Arial,sans-serif; font-size:13pt; letter-spacing:.14em; text-transform:uppercase; color:#12405f; font-weight:700; margin-top:8pt; }
.cw .sub{ font-size:12pt; color:#33475b; font-style:italic; margin-top:14pt; }
.cw .bar{ width:54%; height:2.6pt; background:#0f2f4c; margin:22pt auto; }
.cw .stat{ font-family:Arial,sans-serif; font-size:9pt; color:#5b6b7b; line-height:1.9; }
.toc-page{ page-break-after:always; }
.toc-h{ font-family:Arial,sans-serif; font-size:15pt; color:#0f2f4c; border-bottom:2pt solid #0f2f4c; padding-bottom:5pt; margin:0 0 8pt; }
table.toc{ width:100%; border-collapse:collapse; font-size:9.4pt; }
table.toc th{ font-family:Arial,sans-serif; font-size:7pt; letter-spacing:.1em; text-transform:uppercase; color:#5b6b7b; text-align:left; border-bottom:1pt solid #0f2f4c; padding:4pt 6pt; }
table.toc td{ border-bottom:.5pt solid #d0dbe6; padding:5pt 6pt; vertical-align:top; }
table.toc td.n{ font-family:Arial,sans-serif; font-weight:700; color:#0f2f4c; white-space:nowrap; }
table.toc td.y{ font-family:Arial,sans-serif; font-weight:700; color:#7a8794; white-space:nowrap; }
.kd{ font-family:Arial,sans-serif; font-size:6.6pt; font-weight:700; padding:.4pt 5pt; border-radius:8pt; white-space:nowrap;
  background:#e3f3e8; border:.5pt solid #a9d6ba; color:#14532d; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.kd.x{ background:#eef1f5; border:.5pt solid #c7d0db; color:#334155; }
.scb{ font-family:Arial,sans-serif; font-size:6.4pt; font-weight:700; background:#0f2f4c; color:#fff; padding:.4pt 4pt; border-radius:2pt; margin-left:3pt; }
.case-sheet{ page-break-before:always; }
</style>"""

# which cases DECIDE vs discuss 4.4 (recompute quickly for the TOC tag)
def kind(d):
    for h in d.get('holding_units',[]):
        if h.get('provision','').startswith('UP-2005::4.4') or re.match(r'^4\.4\b', h.get('clause','') or ''):
            return 'DECIDES'
    return 'discusses'

out=[COVER]
# cover
out.append('<div class="cw"><div class="crest">U.P. Electricity Supply Code, 2005 &middot; Clause Compendium</div>'
  '<h1>Connection to a Tenant or Occupier</h1>'
  '<div class="cl">Clause 4.4</div>'
  '<div class="sub">The complete line of authority, in full, arranged chronologically</div>'
  '<div class="bar"></div>'
  f'<div class="stat">{len(cases)} decisions &middot; {yr(cases[0])}&ndash;{yr(cases[-1])}<br>'
  'High Court of Judicature at Allahabad</div></div>')
# TOC
out.append('<div class="toc-page"><div class="toc-h">Cases in this Compendium</div>'
  '<table class="toc"><thead><tr><th style="width:6%">#</th><th style="width:9%">Year</th>'
  '<th style="width:62%">Case</th><th style="width:12%">Cite</th><th style="width:11%">On 4.4</th></tr></thead><tbody>')
for i,d in enumerate(cases,1):
    b=badge(d.get('court',''))
    k=kind(d); kc='' if k=='DECIDES' else ' x'
    out.append(f'<tr><td class="n">{i}</td><td class="y">{yr(d)}</td>'
      f'<td><b>{esc(party(d.get("title","")))}</b> <span class="scb">{d["case_id"]}</span>'
      +(f' <span class="scb" style="background:#2f6f9f">{b}</span>' if b=="SC" else '')+'</td>'
      f'<td style="font-family:Arial,sans-serif;font-size:7.6pt;color:#5b6b7b">{esc((d.get("neutral_citation","") or "").split(":")[0][:22])}</td>'
      f'<td><span class="kd{kc}">{k}</span></td></tr>')
out.append('</tbody></table>'
  '<p style="font-family:Arial,sans-serif;font-size:8pt;color:#6b7787;margin-top:8pt">'
  '&ldquo;DECIDES&rdquo; = Clause 4.4 is the ground of the holding; &ldquo;discusses&rdquo; = the clause is engaged but the ratio rests elsewhere. '
  'Each summary reproduces the headnote, holding-units, principle tags, matters not decided, and the table of authorities from the case record.</p></div>')
# each case body
for d in cases:
    out.append(f'<div class="case-sheet">{body_of(d)}</div>')

open('/tmp/clause44_compendium.html','w').write('\n'.join(out))
print(f"wrote /tmp/clause44_compendium.html  ({len(cases)} cases)")
