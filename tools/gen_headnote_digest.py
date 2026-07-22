#!/usr/bin/env python3
"""Categorised digest of every judgment's HEADNOTE (verbatim from the summary).
One headnote per case; each case filed under the category of its lead holding,
with secondary categories flagged."""
import json, glob, html, re, sys
sys.path.insert(0,'/tmp'); import provcat
esc=html.escape
CATS=provcat.CATS
CATNAME=dict(CATS)

MONTHS={m:i for i,m in enumerate(['january','february','march','april','may','june','july',
 'august','september','october','november','december'],1)}
def datekey(s):
    s=(s or '').strip()
    m=re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',s)
    if m: return (int(m.group(3)),MONTHS.get(m.group(2).lower(),6),int(m.group(1)))
    m=re.search(r'(\d{4})',s)
    return (int(m.group(1)),6,15) if m else (9999,1,1)
def court_badge(c):
    c=(c or '').lower()
    if 'supreme' in c: return ('SC','bg-sc')
    if 'allahabad' in c: return ('All HC','bg-hc')
    if 'high court' in c or ' hc' in c: return ('HC','bg-oh')
    return ('—','bg-x')

cases=[json.load(open(f)) for f in glob.glob('supply-code/summaries/json/SCJ-*.json')]
buckets={code:[] for code,_ in CATS}
for d in cases:
    hus=d.get('holding_units',[])
    primary=provcat.cat(hus[0]['provision']) if hus else 'N'
    secondary=[]
    for h in hus[1:]:
        c=provcat.cat(h['provision'])
        if c!=primary and c not in secondary: secondary.append(c)
    dk=datekey(d.get('date_of_judgment') or d.get('date_display',''))
    buckets[primary].append((dk,d,secondary))
for code in buckets: buckets[code].sort(key=lambda x:(x[0],x[1]['case_id']))

STYLE="""<style>
@page{ size:A4; margin:15mm 16mm; }
body{ font-family:Georgia,'Liberation Serif',serif; color:#1d2430; font-size:10pt; line-height:1.5; }
h1{ font-family:Arial,sans-serif; font-size:19pt; color:#0f2f4c; margin:0 0 2pt; }
.sub{ font-family:Arial,sans-serif; font-size:9pt; color:#5b6b7b; margin-bottom:2pt; }
.note{ font-family:Arial,sans-serif; font-size:8pt; color:#6b7787; margin-bottom:3pt; }
.rule{ height:2.4pt; background:#0f2f4c; margin:6pt 0 11pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.toc{ font-family:Arial,sans-serif; font-size:8.8pt; color:#26384a; columns:2; column-gap:14mm; }
.toc div{ break-inside:avoid; margin-bottom:2.5pt; } .toc b{ color:#0f2f4c; } .toc .n{ color:#7a8794; font-weight:700; }
.cathead{ font-family:Arial,sans-serif; font-weight:700; font-size:13pt; color:#fff; background:#12405f;
  padding:6pt 10pt; margin:18pt 0 3pt; border-radius:3pt; break-after:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.catmeta{ font-family:Arial,sans-serif; font-size:7.6pt; color:#5b6b7b; text-transform:uppercase; letter-spacing:.1em; margin:0 0 9pt 2pt; }
.c{ border:.5pt solid #d6dee7; border-left:3pt solid #2f6f9f; border-radius:3pt; padding:7pt 11pt; margin:0 0 9pt;
  break-inside:avoid; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.c-off{ border-left-color:#b9a24a; }
.ch{ margin-bottom:3pt; }
.cid{ font-family:Arial,sans-serif; font-weight:700; font-size:8.2pt; color:#0f2f4c; }
.party{ font-weight:700; font-size:10.8pt; color:#10233a; }
.bdg{ font-family:Arial,sans-serif; font-size:6.6pt; font-weight:700; padding:.5pt 4pt; border-radius:2pt;
  white-space:nowrap; margin-left:5pt; vertical-align:1.5px; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.bg-sc{ background:#0f2f4c; color:#fff; } .bg-hc{ background:#2f6f9f; color:#fff; }
.bg-oh{ background:#6b8ba6; color:#fff; } .bg-x{ background:#c7d0db; color:#333; }
.cite{ font-family:Arial,sans-serif; font-size:8pt; color:#6b7787; margin-top:1pt; }
.court{ font-family:Arial,sans-serif; font-size:7.8pt; color:#8a97a4; }
.also{ font-family:Arial,sans-serif; font-size:7.4pt; color:#7a8794; margin-top:2pt; }
.also b{ color:#155e3f; } .tag{ background:#eef3f8; border:.5pt solid #cdd9e5; border-radius:8pt;
  padding:.3pt 6pt; margin-right:3pt; white-space:nowrap; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.hn{ font-size:10pt; color:#1d2430; margin-top:5pt; text-align:justify; }
.disp{ font-family:Arial,sans-serif; font-size:8pt; color:#4a5967; margin-top:5pt; }
.disp b{ font-size:6.8pt; letter-spacing:.08em; text-transform:uppercase; color:#8a97a4; }
</style>"""
def party(t): return re.sub(r'\s*\[.*?\]\s*$','',t or '')

out=[STYLE,'<h1>Headnote Digest &mdash; Every Judgment, Categorised</h1>',
 '<div class="sub">The headnote of each decision in the 263-case corpus, verbatim, '
 'sorted into 14 thematic categories</div>',
 '<div class="note">Each judgment appears once, filed under the category of its lead holding; '
 'other categories it touches are flagged as &ldquo;also relevant to.&rdquo; Chronological within each category.</div>',
 '<div class="rule"></div>','<div class="toc">']
for code,name in CATS:
    n=len(buckets[code])
    if n: out.append(f'<div><b>{code}.</b> {esc(name)} <span class="n">({n})</span></div>')
out.append('</div>')

for code,name in CATS:
    items=buckets[code]
    if not items: continue
    out.append(f'<div class="cathead">{code}. &nbsp;{esc(name)}</div>')
    out.append(f'<div class="catmeta">{len(items)} judgments</div>')
    for dk,d,sec in items:
        bt,bc=court_badge(d.get('court',''))
        off=code=='N'
        out.append(f'<div class="c{" c-off" if off else ""}"><div class="ch">'
            f'<span class="cid">{d["case_id"]}</span> &nbsp;<span class="party">{esc(party(d.get("title","")))}</span>'
            f'<span class="bdg {bc}">{bt}</span>')
        if d.get('neutral_citation'): out.append(f'<div class="cite">{esc(d["neutral_citation"])}</div>')
        crt=' &middot; '.join(x for x in [d.get('court',''),d.get('coram',''),d.get('date_display','')] if x)
        if crt: out.append(f'<div class="court">{esc(crt)}</div>')
        if sec:
            chips=' '.join(f'<span class="tag">{s} &mdash; {esc(CATNAME[s])}</span>' for s in sec)
            out.append(f'<div class="also"><b>Also relevant to:</b> {chips}</div>')
        out.append('</div>')
        out.append(f'<div class="hn">{esc((d.get("headnote") or "").strip())}</div>')
        disp=(d.get('disposition') or '').strip()
        if disp: out.append(f'<div class="disp"><b>Disposition &nbsp;</b>{esc(disp)}</div>')
        out.append('</div>')

open('/tmp/headnote_digest.html','w').write('\n'.join(out))
print(f"wrote /tmp/headnote_digest.html  ({sum(len(v) for v in buckets.values())} judgments)")
