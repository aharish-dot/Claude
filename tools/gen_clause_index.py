#!/usr/bin/env python3
"""Clause-finder: for every U.P. Supply Code clause, all cases that engage it.
Distinguishes cases that DECIDE on a clause (provision/clause-field) from those
that merely DISCUSS it (text mention). Grouped by Code chapter."""
import json, glob, html, re, collections
esc=html.escape
spine=json.load(open('supply-code/jurisprudence/index.json'))
provtopic={k.split('::',1)[1]:v.get('topic','') for k,v in spine['provisions'].items() if k.startswith('UP-2005::')}
cases=[json.load(open(f)) for f in glob.glob('supply-code/summaries/json/SCJ-*.json')]

MONTHS={m:i for i,m in enumerate(['january','february','march','april','may','june','july','august','september','october','november','december'],1)}
def yr(d):
    s=d.get('date_of_judgment') or d.get('date_display','')
    m=re.search(r'(\d{4})',s or ''); return m.group(1) if m else ''
def datekey(d):
    s=d.get('date_of_judgment') or d.get('date_display','')
    m=re.search(r'(\d{4})-(\d{2})-(\d{2})',s or '')
    if m: return tuple(int(x) for x in m.groups())
    m=re.search(r'(\d{4})',s or ''); return (int(m.group(1)),6,15) if m else (9999,1,1)
def badge(c):
    c=(c or '').lower()
    if 'supreme' in c: return 'SC'
    if 'allahabad' in c: return 'All'
    if 'high court' in c: return 'HC'
    return ''
def party(t): return re.sub(r'\s*\[.*?\]\s*$','',t or '')
def toplevel(c):
    m=re.match(r'(\d+)\.(\d+)',c)
    if not m: return None
    a,b=int(m.group(1)),int(m.group(2))
    if a<1 or a>9 or b<1: return None   # Code has chapters 1-9; X.0 is a header, not a clause
    return f'{a}.{b}'

# clause -> case_id -> {'kind','detail'}   kind: 'decide' | 'discuss'
idx=collections.defaultdict(dict)
subdetail=collections.defaultdict(lambda: collections.defaultdict(set))
CLAUSE_TXT=re.compile(r'(?:Clause|Para(?:graph)?)\s*[- ]?\s*(\d+\.\d+[A-Za-z0-9()ivx]*)(?!\.\d{4})', re.I)

for d in cases:
    cid=d['case_id']
    decide=set(); discuss=set()
    # decide: from provision keys + clause fields of holdings
    for h in d.get('holding_units',[]):
        p=h.get('provision','')
        if p.startswith('UP-2005::'):
            raw=p.split('::',1)[1]; tl=toplevel(raw)
            if tl: decide.add(tl); subdetail[tl][cid].add(raw)
        cf=h.get('clause','')
        for tok in re.findall(r'\b(\d+\.\d+[A-Za-z0-9()ivx]*)(?!\.\d{4})', cf):
            tl=toplevel(tok)
            if tl: decide.add(tl); subdetail[tl][cid].add(tok)
    # discuss: "Clause X.Y"/"Para X.Y" anywhere in headnote/holdings
    blob=d.get('headnote','')+' '+' '.join(h.get('holding','')+' '+h.get('topic','')+' '+h.get('limiting_facts','') for h in d.get('holding_units',[]))
    for tok in CLAUSE_TXT.findall(blob):
        tl=toplevel(tok)
        if tl: discuss.add(tl)
    for tl in decide: idx[tl][cid]='decide'
    for tl in discuss:
        if idx[tl].get(cid)!='decide': idx[tl][cid]='discuss'

byid={d['case_id']:d for d in cases}
def clause_sort(c):
    a,b=c.split('.'); return (int(a),int(b))
allclauses=sorted(idx, key=clause_sort)

CHAP={2:'Chapter 2 — Definitions',3:'Chapter 3 — General Conditions of Supply',
 4:'Chapter 4 — Connections, Load & Agreements',5:'Chapter 5 — Metering',
 6:'Chapter 6 — Billing, Collection & Recovery',7:'Chapter 7 — Grievance Redressal',
 8:'Chapter 8 — Theft & Unauthorised Use',9:'Chapter 9 — Miscellaneous'}

STYLE="""<style>
@page{ size:A4; margin:14mm 15mm; }
body{ font-family:Georgia,'Liberation Serif',serif; color:#1d2430; font-size:9.8pt; line-height:1.5; }
h1{ font-family:Arial,sans-serif; font-size:19pt; color:#0f2f4c; margin:0 0 2pt; }
.sub{ font-family:Arial,sans-serif; font-size:9pt; color:#5b6b7b; } .note{ font-family:Arial,sans-serif; font-size:8pt; color:#6b7787; margin-bottom:3pt; }
.rule{ height:2.4pt; background:#0f2f4c; margin:6pt 0 11pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.legend{ font-family:Arial,sans-serif; font-size:8pt; color:#4a5967; margin-bottom:8pt; }
.badge-d{ background:#e3f3e8; border:.5pt solid #a9d6ba; color:#14532d; }
.badge-x{ background:#eef1f5; border:.5pt solid #c7d0db; color:#334155; }
.kd{ font-family:Arial,sans-serif; font-size:6.6pt; font-weight:700; padding:.4pt 5pt; border-radius:8pt; white-space:nowrap;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.chap{ font-family:Arial,sans-serif; font-weight:700; font-size:12.5pt; color:#fff; background:#12405f;
  padding:5pt 10pt; margin:16pt 0 6pt; border-radius:3pt; break-after:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.cl{ border:.5pt solid #d6dee7; border-left:3pt solid #2f6f9f; border-radius:3pt; padding:5pt 9pt; margin:0 0 7pt;
  break-inside:avoid; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.clh{ font-family:Arial,sans-serif; font-weight:700; font-size:11pt; color:#0f2f4c; }
.cln{ font-size:8pt; color:#5b6b7b; font-family:Arial,sans-serif; }
.subs{ font-family:Arial,sans-serif; font-size:7.2pt; color:#155e3f; }
.topic{ font-size:8.6pt; color:#33404d; font-style:italic; margin:1pt 0 4pt; }
.row{ font-size:8.8pt; margin:1.5pt 0; padding-left:2pt; }
.scj{ font-family:Arial,sans-serif; font-weight:700; font-size:7.4pt; color:#0f2f4c; }
.yr{ color:#7a8794; font-weight:700; font-family:Arial,sans-serif; font-size:7.6pt; }
.ct{ font-family:Arial,sans-serif; font-size:6.4pt; font-weight:700; padding:0 3pt; border-radius:2pt; margin-left:2pt;
  background:#eef3f8; border:.5pt solid #cdd9e5; color:#26384a; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.toc{ font-family:Arial,sans-serif; font-size:8.6pt; color:#26384a; columns:3; column-gap:10mm; margin-bottom:4pt; }
.toc b{ color:#0f2f4c; }
</style>"""

out=[STYLE,'<h1>Clause Finder &mdash; Cases by Supply Code Clause</h1>',
 '<div class="sub">Every U.P. Electricity Supply Code, 2005 clause engaged by the 263-case corpus, '
 'with all cases under each.</div>',
 '<div class="note">A clause not listed here has no case in the corpus (e.g. Clause 4.46 is not litigated). '
 'Within a clause, cases are chronological.</div>',
 '<div class="legend"><span class="kd badge-d">DECIDES</span> the clause is the governing provision of a holding &nbsp;&nbsp;'
 '<span class="kd badge-x">discusses</span> the clause is referred to but not the ground of decision</div>',
 '<div class="rule"></div>']
# TOC of clauses
out.append('<div class="toc">')
for c in allclauses:
    n=len(idx[c]); out.append(f'<div><b>{c}</b> ({n})</div>')
out.append('</div>')

# group by chapter
bychap=collections.defaultdict(list)
for c in allclauses: bychap[int(c.split('.')[0])].append(c)
for ch in sorted(bychap):
    out.append(f'<div class="chap">{esc(CHAP.get(ch,f"Chapter {ch}"))}</div>')
    for c in bychap[ch]:
        entries=idx[c]
        topic=provtopic.get(c,'') or provtopic.get(c+'(', '')
        # best topic: try exact, else any subdetail's provision topic
        if not topic:
            for raw in set().union(*subdetail[c].values()) if subdetail[c] else []:
                if raw in provtopic: topic=provtopic[raw]; break
        subs=sorted(set().union(*subdetail[c].values())) if subdetail[c] else []
        subs=[s for s in subs if s!=c]
        out.append('<div class="cl">')
        out.append(f'<span class="clh">Clause {esc(c)}</span> <span class="cln">&nbsp;{len(entries)} case'
                   f'{"s" if len(entries)!=1 else ""}</span>')
        if subs: out.append(f' &nbsp;<span class="subs">[{esc(", ".join(subs))}]</span>')
        if topic: out.append(f'<div class="topic">{esc(topic)}</div>')
        # order: decide first then discuss, each chronological
        rows=sorted(entries.items(), key=lambda kv:(0 if kv[1]=="decide" else 1, datekey(byid[kv[0]]), kv[0]))
        for cid,kind in rows:
            d=byid[cid]; b=badge(d.get('court',''))
            kd='badge-d' if kind=='decide' else 'badge-x'; lbl='DECIDES' if kind=='decide' else 'discusses'
            out.append(f'<div class="row"><span class="kd {kd}">{lbl}</span> '
                f'<span class="scj">{cid}</span> {esc(party(d.get("title","")))} '
                f'<span class="yr">{yr(d)}</span>'+(f'<span class="ct">{b}</span>' if b else '')+'</div>')
        out.append('</div>')

# unnumbered descriptive UP-2005 provisions
desc=[k.split("::",1)[1] for k in spine['provisions'] if k.startswith('UP-2005::') and not re.match(r'\d',k.split("::",1)[1])]
if desc:
    out.append('<div class="chap">Unnumbered / descriptive Supply Code provisions</div>')
    for k in sorted(desc):
        pk='UP-2005::'+k; cs=spine['provisions'][pk]['cases']
        out.append('<div class="cl"><span class="clh">'+esc(k.replace('-',' '))+'</span> '
            f'<span class="cln">&nbsp;{len(cs)} case{"s" if len(cs)!=1 else ""}</span>')
        t=spine['provisions'][pk].get('topic','')
        if t: out.append(f'<div class="topic">{esc(t)}</div>')
        for cc in sorted(cs,key=lambda x:x.get("case_id","")):
            out.append(f'<div class="row"><span class="scj">{cc["case_id"]}</span> {esc(party(cc.get("title","")))}</div>')
        out.append('</div>')

open('/tmp/clause_index.html','w').write('\n'.join(out))
print(f"wrote /tmp/clause_index.html  ({len(allclauses)} numbered clauses)")
