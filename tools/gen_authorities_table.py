#!/usr/bin/env python3
"""All authorities in the spine ledger, grouped by court, in the per-case table format."""
import json, html, re
esc=html.escape
spine=json.load(open('supply-code/jurisprudence/index.json'))
led=spine['authorities_ledger']

TREAT={'followed':'t-foll','approved':'t-foll','applied':'t-foll','affirmed':'t-foll',
 'distinguished':'t-dist','doubted':'t-dist','overruled':'t-dist',
 'referred':'t-ref','referred to':'t-ref','noted':'t-ref','considered':'t-ref',
 'relied on':'t-rel','relied-on':'t-rel','relied upon':'t-rel'}
CB={'petitioner':'cb-pet','appellant':'cb-pet','respondent':'cb-resp','respondents':'cb-resp',
 'court':'cb-court','suo motu':'cb-court','bench':'cb-court'}
def treat_cls(x): return TREAT.get((x or '').strip().lower(),'t-ref')
def cb_cls(x): return CB.get((x or '').strip().lower(),'cb-court')

def court_group(c):
    c=(c or '').lower()
    if 'supreme' in c: return (0,'Supreme Court of India')
    if 'allahabad' in c: return (1,'Allahabad High Court')
    if 'high court' in c or 'hc' in c: return (2,'Other High Courts')
    return (3,'Statutes, Tribunals, Treatises & Other')

def sortname(n):
    return re.sub(r'^(m/s\.?|smt\.?|sri\.?|shri\.?|the |in re,? )','',(n or '').strip().lower())

groups={0:[],1:[],2:[],3:[]}
for name,a in led.items():
    g,_=court_group(a.get('court',''))
    groups[g].append(a)
for g in groups: groups[g].sort(key=lambda a:sortname(a.get('name','')))
GNAMES={0:'Supreme Court of India',1:'Allahabad High Court',2:'Other High Courts',
        3:'Statutes, Tribunals, Treatises & Other'}

STYLE="""<style>
@page{ size:A4 landscape; margin:11mm 12mm; }
body{ font-family:Georgia,'Liberation Serif',serif; color:#1d2430; font-size:8.6pt; line-height:1.4; }
h1{ font-family:Arial,sans-serif; font-size:17pt; color:#0f2f4c; margin:0 0 2pt; }
.sub{ font-family:Arial,sans-serif; font-size:8.6pt; color:#5b6b7b; margin-bottom:3pt; }
.rule{ height:2.2pt; background:#0f2f4c; margin:5pt 0 10pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.toc{ font-family:Arial,sans-serif; font-size:8.4pt; color:#26384a; margin-bottom:4pt; }
.toc span{ margin-right:16pt; } .toc b{ color:#0f2f4c; }
.gh{ font-family:Arial,sans-serif; font-weight:700; font-size:12pt; color:#fff; background:#12405f;
  padding:5pt 10pt; margin:15pt 0 5pt; border-radius:3pt; break-after:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.gh small{ font-weight:400; font-size:8pt; opacity:.85; }
.auth{ border:.5pt solid #d6dee7; border-radius:3pt; margin:0 0 6pt; break-inside:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.auth-h{ background:#eef3f8; border-bottom:.5pt solid #d0dbe6; padding:4pt 8pt;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.an{ font-style:italic; font-weight:700; font-size:9pt; color:#10233a; }
.ac{ font-family:Arial,sans-serif; font-size:7.4pt; color:#5b6b7b; }
.ap{ font-size:8.4pt; color:#2b3742; padding:4pt 8pt; }
.ap b{ font-family:Arial,sans-serif; font-size:6.6pt; letter-spacing:.1em; color:#7a8794; text-transform:uppercase; }
table.cit{ width:100%; border-collapse:collapse; font-size:8pt; line-height:1.38; }
table.cit th{ font-family:Arial,sans-serif; font-size:6.6pt; letter-spacing:.1em; text-transform:uppercase;
  color:#5b6b7b; text-align:left; border-top:.5pt solid #d0dbe6; border-bottom:.5pt solid #d0dbe6;
  padding:3pt 8pt; background:#f8fafc; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
table.cit td{ border-bottom:.5pt solid #e4e9ef; padding:3.5pt 8pt; vertical-align:top; }
.cid{ font-family:Arial,sans-serif; font-weight:700; font-size:7.4pt; color:#0f2f4c; }
.trt,.cbb{ font-size:7pt; padding:.5pt 6pt; border-radius:8pt; white-space:nowrap; display:inline-block;
  font-family:Arial,sans-serif; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.t-foll{ color:#14532d; background:#e3f3e8; border:.5pt solid #a9d6ba; }
.t-dist{ color:#7a2e0e; background:#fbe9e0; border:.5pt solid #e8b79c; }
.t-ref{ color:#334155; background:#eef1f5; border:.5pt solid #c7d0db; }
.t-rel{ color:#5f5010; background:#fbf3d6; border:.5pt solid #e6d69a; }
.cb-pet{ color:#1e3a5f; background:#e6eefb; border:.5pt solid #b3ccef; }
.cb-resp{ color:#5b2c46; background:#fbe6f1; border:.5pt solid #e8b3d2; }
.cb-court{ color:#334155; background:#e9edf2; border:.5pt solid #c2ccd8; }
</style>"""

out=[STYLE,'<h1>Table of Authorities &mdash; Consolidated</h1>',
 f'<div class="sub">Every case, statute and text cited across the 263-decision corpus &middot; '
 f'{len(led)} authorities, grouped by forum</div><div class="rule"></div>']
out.append('<div class="toc">')
for g in range(4):
    out.append(f'<span><b>{GNAMES[g]}</b> ({len(groups[g])})</span>')
out.append('</div>')

for g in range(4):
    items=groups[g]
    if not items: continue
    tot=sum(len(a.get('cited_in',[])) for a in items)
    out.append(f'<div class="gh">{GNAMES[g]} &nbsp;<small>{len(items)} authorities &middot; {tot} citations</small></div>')
    for a in items:
        meta=' &middot; '.join([x for x in [esc(a.get('citation','')), esc(a.get('court',''))] if x])
        out.append('<div class="auth"><div class="auth-h">'
                   f'<span class="an">{esc(a.get("name",""))}</span>'
                   + (f'<span class="ac"> &nbsp;{meta}</span>' if meta else '') + '</div>')
        prop=(a.get('proposition') or '').strip()
        if prop: out.append(f'<div class="ap"><b>Proposition &nbsp;</b>{esc(prop)}</div>')
        cited=a.get('cited_in',[])
        if cited:
            rows=[]
            for c in cited:
                rows.append('<tr>'
                    f'<td><span class="cid">{c.get("case_id","")}</span> {esc(c.get("title",""))}</td>'
                    f'<td><span class="cbb {cb_cls(c.get("cited_by"))}">{esc(c.get("cited_by") or "—")}</span></td>'
                    f'<td><span class="trt {treat_cls(c.get("treatment"))}">{esc(c.get("treatment") or "Referred")}</span></td>'
                    f'<td>{esc((c.get("how_treated") or "").strip())}</td></tr>')
            out.append('<table class="cit"><thead><tr>'
                '<th style="width:40%">Cited In</th><th style="width:9%">Cited By</th>'
                '<th style="width:11%">Treatment</th><th style="width:40%">How Treated</th>'
                '</tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
        out.append('</div>')

open('/tmp/authorities_table.html','w').write('\n'.join(out))
print("wrote /tmp/authorities_table.html  ("+str(len(led))+" authorities)")
