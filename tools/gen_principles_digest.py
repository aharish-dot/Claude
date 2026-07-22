#!/usr/bin/env python3
"""Categorised digest of all principle tags in the spine -> self-contained HTML."""
import json, html, re, sys, datetime
html_esc = html.escape
spine = json.load(open('supply-code/jurisprudence/index.json'))
assign_data = json.load(open('/tmp/assign.json'))
assign = assign_data['assign']; CATS = assign_data['cats']
prins = spine['principles']

MONTHS = {m:i for i,m in enumerate(
    ['january','february','march','april','may','june','july','august',
     'september','october','november','december'],1)}
def datekey(s):
    s=(s or '').strip()
    m=re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',s)
    if m: return (int(m.group(3)), MONTHS.get(m.group(2).lower(),6), int(m.group(1)))
    m=re.search(r'(\d{4})',s)
    return (int(m.group(1)),6,15) if m else (9999,1,1)

def label(tag):
    t=tag.replace('-',' ')
    t=re.sub(r'\bs(\d+)\b', r's.\1', t)
    return t[0].upper()+t[1:]

def court_badge(c):
    c=(c or '').lower()
    if 'supreme' in c: return ('SC','bg-sc')
    if 'allahabad' in c: return ('All HC','bg-hc')
    if 'high court' in c or 'hc' in c: return ('HC','bg-oh')
    return ('—','bg-x')

def short_party(title):
    t=re.sub(r'^(M/s\.?|Smt\.?|Sri\.?|Shri\.?|Dr\.?)\s+','',title or '')
    t=re.split(r'\s+v\.\s+', t)[0]
    return (t[:38]+'…') if len(t)>39 else t

CATSTYLE="""<style>
@page{ size:A4; margin:14mm 15mm; }
body{ font-family:Georgia,'Liberation Serif',serif; color:#1d2430; font-size:9.6pt; line-height:1.5; }
h1{ font-family:Arial,'Liberation Sans',sans-serif; font-size:19pt; color:#0f2f4c; margin:0 0 2pt; letter-spacing:.2pt; }
.sub{ font-family:Arial,sans-serif; font-size:9pt; color:#5b6b7b; margin-bottom:3pt; }
.rule{ height:2.4pt; background:#0f2f4c; margin:6pt 0 12pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.toc{ font-family:Arial,sans-serif; font-size:8.7pt; color:#26384a; columns:2; column-gap:14mm; margin-bottom:6pt; }
.toc div{ break-inside:avoid; margin-bottom:2.5pt; }
.toc b{ color:#0f2f4c; }
.cathead{ font-family:Arial,sans-serif; font-weight:700; font-size:12.5pt; color:#fff; background:#12405f;
  padding:5pt 10pt; margin:16pt 0 2pt; border-radius:3pt; -webkit-print-color-adjust:exact; print-color-adjust:exact;
  break-after:avoid; }
.catmeta{ font-family:Arial,sans-serif; font-size:7.6pt; color:#5b6b7b; text-transform:uppercase; letter-spacing:.1em; margin:0 0 7pt 2pt; }
.p{ border:.5pt solid #d6dee7; border-left:3pt solid #2f6f9f; border-radius:3pt; padding:6pt 9pt; margin:0 0 7pt;
  break-inside:avoid; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.p-h{ font-family:Arial,sans-serif; font-weight:700; font-size:9.8pt; color:#123; margin-bottom:1pt; }
.cnt{ font-family:Arial,sans-serif; font-size:7pt; font-weight:700; color:#0f2f4c; background:#e7eef5;
  border:.5pt solid #b9cbdd; border-radius:8pt; padding:0 6pt; margin-left:5pt; white-space:nowrap;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.gloss{ font-size:8.9pt; color:#33404d; margin:2pt 0 4pt; }
.chips{ font-family:Arial,sans-serif; font-size:7.5pt; line-height:1.85; }
.chip{ display:inline-block; background:#f4f7fa; border:.5pt solid #d3dde7; border-radius:3pt;
  padding:.5pt 5pt; margin:0 3pt 2pt 0; color:#26384a; white-space:nowrap;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.bdg{ font-size:6.3pt; font-weight:700; padding:0 3pt; border-radius:2pt; margin-left:3pt; vertical-align:1px;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.bg-sc{ background:#0f2f4c; color:#fff; } .bg-hc{ background:#2f6f9f; color:#fff; }
.bg-oh{ background:#6b8ba6; color:#fff; } .bg-x{ background:#c7d0db; color:#333; }
.yr{ color:#7a8794; font-weight:700; }
</style>"""

out=[CATSTYLE]
out.append('<h1>The U.P. Electricity Supply Code in the Courts</h1>')
out.append('<div class="sub">Companion Reference &mdash; Categorised Digest of Principles &middot; '
           f'{len(prins)} principles across 263 decisions</div>')
out.append('<div class="rule"></div>')
# TOC
out.append('<div class="toc">')
for c,name in CATS:
    n=sum(1 for t in prins if assign[t]==c)
    out.append(f'<div><b>{c}.</b> {html_esc(name)} <span class="yr">({n})</span></div>')
out.append('</div>')

for c,name in CATS:
    tags=[t for t in prins if assign[t]==c]
    # order principles by descending case count then alpha
    tags.sort(key=lambda t:(-len(prins[t]['cases']), t))
    ncases=sum(len(prins[t]['cases']) for t in tags)
    out.append(f'<div class="cathead">{c}. &nbsp;{html_esc(name)}</div>')
    out.append(f'<div class="catmeta">{len(tags)} principles &middot; {ncases} case-applications</div>')
    for t in tags:
        cases=sorted(prins[t]['cases'], key=lambda x:datekey(x.get('date','')))
        # gloss from earliest substantive application
        gloss=''
        for cc in cases:
            a=(cc.get('application') or '').strip()
            if a: gloss=a; break
        gloss=re.sub(r'\s+',' ',gloss)
        if len(gloss)>340: gloss=gloss[:337].rsplit(' ',1)[0]+'…'
        out.append('<div class="p">')
        out.append(f'<div class="p-h">{html_esc(label(t))}<span class="cnt">{len(cases)} case'
                   f'{"s" if len(cases)!=1 else ""}</span></div>')
        if gloss: out.append(f'<div class="gloss">{html_esc(gloss)}</div>')
        out.append('<div class="chips">')
        for cc in cases:
            yr=datekey(cc.get('date',''))[0]; yr='' if yr==9999 else str(yr)
            bt,bc=court_badge(cc.get('court',''))
            out.append(f'<span class="chip">{cc["case_id"]} &middot; {html_esc(short_party(cc.get("title","")))} '
                       f'<span class="yr">{yr}</span><span class="bdg {bc}">{bt}</span></span>')
        out.append('</div></div>')

open('/tmp/principles_digest.html','w').write('\n'.join(out))
print("wrote /tmp/principles_digest.html")
