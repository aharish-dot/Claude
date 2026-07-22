#!/usr/bin/env python3
"""Categorised digest of the RATIO (holding) of every judgment -> self-contained HTML.
Unit = holding_unit (a ratio). Each ratio is categorised by its provision and
listed chronologically within its category, labelled with case, citation, issue,
holding text and limiting facts."""
import json, glob, html, re, sys
sys.path.insert(0,'/tmp'); import provcat
esc=html.escape
CATS=provcat.CATS

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

def provlabel(p):
    if p.startswith('OFFTOPIC::'): return 'off-topic'
    CODE={'EA2003':'Electricity Act 2003','UP-2005':'Supply Code 2005','UP-2002':'Supply Code 2002',
     'IEA1910':'IEA 1910','IBC':'IBC 2016','CA1956':'Companies Act 1956','EA1999(UP)':'UP Reforms Act 1999',
     'ESA1948':'ESA 1948','UPDR1958':'UP Dues Recovery 1958','UPGEU1958':'UPGEU 1958','UPEDA1952':'UP Electricity Duty 1952',
     'WB-2004':'WB Code 2004','JH-2005':'Jharkhand Code 2005','NIACT':'NI Act','CPC':'CPC','LSAA1987':'Legal Services Act',
     'ARREARS':'Arrears (general)','TORT':'Tort','PENALTY':'Penalty','RATE-SCHEDULE-UP':'UP Rate Schedule',
     'CONTEMPT':'Contempt','URUA1966':'UP Relief Undertakings 1966'}
    if '::' in p:
        c,cl=p.split('::',1)
        base=CODE.get(c,c)
        return f'{base} &sect;{cl}' if re.match(r'^[0-9]',cl) else base
    return p

# collect ratios
cases={}
for f in glob.glob('supply-code/summaries/json/SCJ-*.json'):
    d=json.load(open(f)); cases[d['case_id']]=d
buckets={code:[] for code,_ in CATS}
for cid,d in cases.items():
    dk=datekey(d.get('date_of_judgment') or d.get('date_display',''))
    for i,h in enumerate(d.get('holding_units',[])):
        cat=provcat.cat(h.get('provision','?'))
        buckets[cat].append((dk,cid,d,h,i,len(d.get('holding_units',[]))))
for code in buckets: buckets[code].sort(key=lambda x:(x[0],x[1],x[4]))

STYLE="""<style>
@page{ size:A4; margin:14mm 15mm; }
body{ font-family:Georgia,'Liberation Serif',serif; color:#1d2430; font-size:9.4pt; line-height:1.46; }
h1{ font-family:Arial,sans-serif; font-size:19pt; color:#0f2f4c; margin:0 0 2pt; }
.sub{ font-family:Arial,sans-serif; font-size:9pt; color:#5b6b7b; margin-bottom:2pt; }
.note{ font-family:Arial,sans-serif; font-size:8pt; color:#6b7787; margin-bottom:3pt; }
.rule{ height:2.4pt; background:#0f2f4c; margin:6pt 0 11pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.toc{ font-family:Arial,sans-serif; font-size:8.7pt; color:#26384a; columns:2; column-gap:14mm; }
.toc div{ break-inside:avoid; margin-bottom:2.5pt; } .toc b{ color:#0f2f4c; } .toc .n{ color:#7a8794; font-weight:700; }
.cathead{ font-family:Arial,sans-serif; font-weight:700; font-size:13pt; color:#fff; background:#12405f;
  padding:6pt 10pt; margin:17pt 0 3pt; border-radius:3pt; break-after:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.catmeta{ font-family:Arial,sans-serif; font-size:7.6pt; color:#5b6b7b; text-transform:uppercase; letter-spacing:.1em; margin:0 0 8pt 2pt; }
.r{ border:.5pt solid #d6dee7; border-left:3pt solid #2f6f9f; border-radius:3pt; padding:6pt 10pt; margin:0 0 8pt;
  break-inside:avoid; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.r-off{ border-left-color:#b9a24a; }
.rh{ display:flex; justify-content:space-between; align-items:baseline; gap:8pt; margin-bottom:2pt; }
.cid{ font-family:Arial,sans-serif; font-weight:700; font-size:8pt; color:#0f2f4c; }
.party{ font-weight:700; font-size:9.6pt; color:#10233a; }
.cite{ font-family:Arial,sans-serif; font-size:7.5pt; color:#6b7787; }
.bdg{ font-family:Arial,sans-serif; font-size:6.4pt; font-weight:700; padding:.5pt 4pt; border-radius:2pt; white-space:nowrap;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.bg-sc{ background:#0f2f4c; color:#fff; } .bg-hc{ background:#2f6f9f; color:#fff; }
.bg-oh{ background:#6b8ba6; color:#fff; } .bg-x{ background:#c7d0db; color:#333; }
.prov{ font-family:Arial,sans-serif; font-size:7pt; font-weight:700; color:#155e3f; background:#e6f2ea;
  border:.5pt solid #b2d8c1; border-radius:8pt; padding:.5pt 7pt; white-space:nowrap; margin-left:5pt;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.multi{ font-family:Arial,sans-serif; font-size:6.6pt; color:#8a5a00; background:#fbf1d8; border:.5pt solid #e6d29a;
  border-radius:8pt; padding:.5pt 6pt; margin-left:4pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.iss{ font-family:Arial,sans-serif; font-size:7pt; letter-spacing:.08em; text-transform:uppercase; color:#7a8794; margin:4pt 0 1pt; }
.issue{ font-size:8.7pt; color:#3a4854; font-style:italic; margin-bottom:3pt; }
.ratio{ font-size:9.3pt; color:#1d2430; }
.lf{ font-size:8pt; color:#5b6b7b; margin-top:3pt; }
.lf b{ font-family:Arial,sans-serif; font-size:6.6pt; letter-spacing:.08em; text-transform:uppercase; color:#8a97a4; }
.disp{ font-size:7.8pt; color:#556; margin-top:2pt; }
.disp b{ font-family:Arial,sans-serif; font-size:6.6pt; letter-spacing:.08em; text-transform:uppercase; color:#8a97a4; }
</style>"""

def party(title):
    t=re.sub(r'\s*\[.*?\]\s*$','',title or '')
    return t

out=[STYLE,'<h1>Ratio Digest &mdash; Every Judgment, Categorised</h1>',
 '<div class="sub">The holding (ratio decidendi) of each decision in the 263-case corpus, '
 'sorted into 14 thematic categories</div>',
 f'<div class="note">340 ratios &middot; a multi-issue judgment contributes one ratio to each category it decides. '
 'Ordered chronologically within each category.</div>',
 '<div class="rule"></div>','<div class="toc">']
for code,name in CATS:
    n=len(buckets[code])
    if n: out.append(f'<div><b>{code}.</b> {esc(name)} <span class="n">({n})</span></div>')
out.append('</div>')

for code,name in CATS:
    items=buckets[code]
    if not items: continue
    ncases=len({x[1] for x in items})
    out.append(f'<div class="cathead">{code}. &nbsp;{esc(name)}</div>')
    out.append(f'<div class="catmeta">{len(items)} ratios &middot; {ncases} judgments</div>')
    for dk,cid,d,h,i,ntot in items:
        yr=dk[0]; yr='' if yr==9999 else str(yr)
        bt,bc=court_badge(d.get('court',''))
        off = code=='N'
        issue=(h.get('question') or h.get('topic') or '').strip()
        ratio=(h.get('holding') or '').strip()
        lf=(h.get('limiting_facts') or '').strip()
        disp=(d.get('disposition') or '').strip()
        multi = f'<span class="multi">ratio {i+1} of {ntot}</span>' if ntot>1 else ''
        out.append(f'<div class="r{" r-off" if off else ""}">')
        out.append('<div class="rh"><div>'
            f'<span class="cid">{cid}</span> &nbsp;<span class="party">{esc(party(d.get("title","")))}</span>'
            f'<span class="prov">{provlabel(h.get("provision","?"))}</span>{multi}</div>'
            f'<div style="text-align:right; white-space:nowrap">'
            f'<span class="bdg {bc}">{bt}</span> <span class="cite">{yr}</span></div></div>')
        if d.get('neutral_citation'):
            out.append(f'<div class="cite">{esc(d["neutral_citation"])}</div>')
        if issue: out.append(f'<div class="iss">Issue</div><div class="issue">{esc(issue)}</div>')
        out.append(f'<div class="iss">Ratio</div><div class="ratio">{esc(ratio)}</div>')
        if lf: out.append(f'<div class="lf"><b>On the facts &nbsp;</b>{esc(lf)}</div>')
        if disp: out.append(f'<div class="disp"><b>Disposition &nbsp;</b>{esc(disp)}</div>')
        out.append('</div>')

open('/tmp/ratio_digest.html','w').write('\n'.join(out))
print(f"wrote /tmp/ratio_digest.html  ({sum(len(v) for v in buckets.values())} ratios)")
