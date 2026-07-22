#!/usr/bin/env python3
"""All authorities across the corpus, grouped by forum, in the per-case table format.
Text is verbatim from each case's JSON authorities[] (proposition + how_treated are
shown PER CITATION, uncondensed)."""
import json, glob, html, re
esc=html.escape

TREAT={'followed':'t-foll','approved':'t-foll','applied':'t-foll','affirmed':'t-foll',
 'distinguished':'t-dist','doubted':'t-dist','overruled':'t-dist',
 'referred':'t-ref','referred to':'t-ref','noted':'t-ref','considered':'t-ref',
 'relied on':'t-rel','relied-on':'t-rel','relied upon':'t-rel'}
CB={'petitioner':'cb-pet','appellant':'cb-pet','respondent':'cb-resp','respondents':'cb-resp',
 'court':'cb-court','suo motu':'cb-court','bench':'cb-court'}
def treat_cls(x): return TREAT.get((x or '').strip().lower(),'t-ref')
def cb_cls(x): return CB.get((x or '').strip().lower(),'cb-court')

def court_group(c):
    # Detect High Court / Allahabad BEFORE Supreme Court: an HC decision whose
    # SLP was dismissed/affirmed by the SC is still an HC authority. Only a
    # judgment actually *delivered* by the Supreme Court belongs in group 0.
    c=(c or '').lower()
    if 'allahabad' in c: return 1
    if 'high court' in c or ' hc' in c or '(hc' in c: return 2
    if 'supreme' in c: return 0
    return 3
GNAMES={0:'Supreme Court of India',1:'Allahabad High Court',2:'Other High Courts',
        3:'Statutes, Tribunals, Treatises & Other'}
def sortname(n):
    return re.sub(r'^(m/s\.?|smt\.?|sri\.?|shri\.?|the |in re,? )','',(n or '').strip().lower())

# aggregate from source JSON, keyed by docid-or-name (same as build_supply_code.py)
auth={}
for f in sorted(glob.glob('supply-code/summaries/json/SCJ-*.json')):
    d=json.load(open(f)); cid=d['case_id']
    for a in d.get('authorities',[]):
        key=a.get('docid') or a.get('name','')
        e=auth.setdefault(key,{'names':set(),'citations':set(),'courts':[],'cites':[]})
        if a.get('name'): e['names'].add(a['name'])
        if a.get('citation'): e['citations'].add(a['citation'])
        if a.get('court'): e['courts'].append(a['court'])
        e['cites'].append({'case_id':cid,'title':d.get('title',''),
            'cited_by':a.get('cited_by',''),'treatment':a.get('treatment',''),
            'proposition':a.get('proposition',''),'how_treated':a.get('how_treated',''),
            'paras':a.get('how_treated_paras','')})

def pick_longest(s):
    return max(s,key=len) if s else ''
groups={0:[],1:[],2:[],3:[]}
for key,e in auth.items():
    name=pick_longest(e['names']); cit=pick_longest(e['citations'])
    court=max(e['courts'],key=len) if e['courts'] else ''
    g=court_group(court)
    groups[g].append({'name':name,'citation':cit,'court':court,'cites':e['cites']})
for g in groups: groups[g].sort(key=lambda a:sortname(a['name']))

STYLE="""<style>
@page{ size:A4 landscape; margin:11mm 12mm; }
body{ font-family:Georgia,'Liberation Serif',serif; color:#1d2430; font-size:10pt; line-height:1.46; }
h1{ font-family:Arial,sans-serif; font-size:18pt; color:#0f2f4c; margin:0 0 2pt; }
.sub{ font-family:Arial,sans-serif; font-size:9.4pt; color:#5b6b7b; margin-bottom:3pt; }
.rule{ height:2.2pt; background:#0f2f4c; margin:5pt 0 10pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.toc{ font-family:Arial,sans-serif; font-size:9.4pt; color:#26384a; margin-bottom:4pt; }
.toc span{ margin-right:18pt; } .toc b{ color:#0f2f4c; }
.gh{ font-family:Arial,sans-serif; font-weight:700; font-size:12.5pt; color:#fff; background:#12405f;
  padding:5pt 10pt; margin:15pt 0 6pt; border-radius:3pt; break-after:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.gh small{ font-weight:400; font-size:8.6pt; opacity:.85; }
.auth{ border:.5pt solid #d0dbe6; border-radius:3pt; margin:0 0 9pt; break-inside:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.auth-h{ background:#eef3f8; border-bottom:.5pt solid #cdd9e5; padding:5pt 9pt;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.an{ font-style:italic; font-weight:700; font-size:10.6pt; color:#10233a; }
.ac{ font-family:Arial,sans-serif; font-size:8.4pt; color:#5b6b7b; }
table.cit{ width:100%; border-collapse:collapse; font-size:9.4pt; line-height:1.46; }
table.cit th{ font-family:Arial,sans-serif; font-size:7.2pt; letter-spacing:.09em; text-transform:uppercase;
  color:#5b6b7b; text-align:left; border-bottom:.5pt solid #cdd9e5; padding:4pt 9pt; background:#f6f9fc;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
table.cit td{ border-bottom:.5pt solid #e4e9ef; padding:5pt 9pt; vertical-align:top; }
table.cit tr:last-child td{ border-bottom:none; }
.cid{ font-family:Arial,sans-serif; font-weight:700; font-size:8.4pt; color:#0f2f4c; display:block; margin-bottom:1pt; }
.ctitle{ font-size:8.8pt; color:#3a4753; }
.paras{ font-family:Arial,sans-serif; font-size:7.6pt; color:#8a97a4; }
.trt,.cbb{ font-size:8pt; padding:1pt 7pt; border-radius:9pt; white-space:nowrap; display:inline-block;
  font-family:Arial,sans-serif; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.t-foll{ color:#14532d; background:#e3f3e8; border:.5pt solid #a9d6ba; }
.t-dist{ color:#7a2e0e; background:#fbe9e0; border:.5pt solid #e8b79c; }
.t-ref{ color:#334155; background:#eef1f5; border:.5pt solid #c7d0db; }
.t-rel{ color:#5f5010; background:#fbf3d6; border:.5pt solid #e6d69a; }
.cb-pet{ color:#1e3a5f; background:#e6eefb; border:.5pt solid #b3ccef; }
.cb-resp{ color:#5b2c46; background:#fbe6f1; border:.5pt solid #e8b3d2; }
.cb-court{ color:#334155; background:#e9edf2; border:.5pt solid #c2ccd8; }
</style>"""

tot_auth=sum(len(groups[g]) for g in groups)
out=[STYLE,'<h1>Table of Authorities &mdash; Consolidated</h1>',
 f'<div class="sub">Every case, statute and text cited across the 263-decision corpus &middot; '
 f'{tot_auth} authorities, grouped by forum. Proposition and treatment shown verbatim, per citation.</div>'
 '<div class="rule"></div>','<div class="toc">']
for g in range(4):
    if groups[g]: out.append(f'<span><b>{GNAMES[g]}</b> ({len(groups[g])})</span>')
out.append('</div>')

for g in range(4):
    items=groups[g]
    if not items: continue
    tot=sum(len(a['cites']) for a in items)
    out.append(f'<div class="gh">{GNAMES[g]} &nbsp;<small>{len(items)} authorities &middot; {tot} citations</small></div>')
    for a in items:
        meta=' &nbsp;&middot;&nbsp; '.join(x for x in [esc(a['citation']),esc(a['court'])] if x)
        out.append('<div class="auth"><div class="auth-h">'
            f'<span class="an">{esc(a["name"])}</span>'
            + (f'<div class="ac">{meta}</div>' if meta else '') + '</div>')
        rows=[]
        for c in a['cites']:
            paras=esc((c.get('paras') or '').strip())
            paras=f'<div class="paras">{paras}</div>' if paras else ''
            rows.append('<tr>'
                f'<td><span class="cid">{c["case_id"]}</span><span class="ctitle">{esc(c.get("title",""))}</span></td>'
                f'<td><span class="cbb {cb_cls(c.get("cited_by"))}">{esc(c.get("cited_by") or "—")}</span></td>'
                f'<td><span class="trt {treat_cls(c.get("treatment"))}">{esc(c.get("treatment") or "Referred")}</span></td>'
                f'<td>{esc((c.get("proposition") or "").strip())}</td>'
                f'<td>{esc((c.get("how_treated") or "").strip())}{paras}</td></tr>')
        out.append('<table class="cit"><thead><tr>'
            '<th style="width:19%">Cited In</th><th style="width:7%">By</th>'
            '<th style="width:9%">Treatment</th>'
            '<th style="width:33%">Proposition (as stated in the judgment)</th>'
            '<th style="width:32%">How Treated</th>'
            '</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>')

open('/tmp/authorities_table.html','w').write('\n'.join(out))
print(f"wrote /tmp/authorities_table.html  ({tot_auth} authorities, {sum(len(a['cites']) for g in groups for a in groups[g])} citations)")
