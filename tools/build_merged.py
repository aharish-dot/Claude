#!/usr/bin/env python3
"""Build the four compilation/merged HTML files from per-case JSON extracts.
   Scales from the current 11 cases to all 50."""
import json, glob, os, re
from collections import OrderedDict, defaultdict

JSON_DIR = os.path.join(os.path.dirname(__file__), '..', 'json')
cases = []
for fp in sorted(glob.glob(os.path.join(JSON_DIR, 'case_*.json'))):
    cases.append(json.load(open(fp)))
N = len(cases)
first = cases[0]['case_no']; last = cases[-1]['case_no']
span = f"Cases {first}–{last}"

def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

def short_name(title):
    t = re.split(r'\sv\.\s', title, maxsplit=1)
    nm = t[1] if len(t) > 1 else title
    nm = re.sub(r'\s*\(FIR[^)]*\)', '', nm).strip()
    nm = re.sub(r'\s*&amp;\s*Anr\.?', ' & Anr.', nm)
    return nm

def chip(c):
    return f'<span class="chip"><b>{c["case_no"]}</b>&nbsp;{esc(short_name(c["title"]))}</span>'

def indian(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return '&mdash;'
    s = str(n);
    if len(s) <= 3: return s
    head, tail = s[:-3], s[-3:]
    head = re.sub(r'(\d)(?=(\d\d)+$)', r'\1,', head)
    return head + ',' + tail

CSS = """
<style>
  .lead-note{ font-size:9.5pt; color:#40506a; margin:0 0 14pt; }
  .scope{ font-family:Arial,'Liberation Sans',sans-serif; font-size:8pt; letter-spacing:.1em;
          text-transform:uppercase; color:#5b6b7f; margin:0 0 2pt; }
  .prov-note{ background:#eef4fb; border-left:3px solid #2f6fb3; color:#123f74;
              padding:8pt 12pt; margin:0 0 9pt; font-size:9.6pt; line-height:1.45;
              -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .entry{ margin:0 0 8pt; padding-left:2pt; }
  .entry .txt{ font-size:9.7pt; }
  .chips{ margin-top:3pt; }
  .chip{ display:inline-block; font-family:Arial,'Liberation Sans',sans-serif; font-size:7.6pt;
         background:#f2f5f9; border:.6pt solid #d3dae2; border-radius:9pt; padding:1pt 7pt;
         margin:0 4pt 4pt 0; color:#33455f; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .chip b{ color:#16243a; }
  .theme h2{ margin-top:16pt; }
  .sig-item{ margin:0 0 8pt; }
  .sig-item .pt{ font-weight:700; color:#1f3350; }
  table.matrix{ width:100%; border-collapse:collapse; font-size:7.5pt; table-layout:fixed; }
  table.matrix th{ background:#16243a; color:#fff; text-align:left; padding:4pt 4pt; font-family:Arial,'Liberation Sans',sans-serif;
                   font-size:7pt; letter-spacing:.02em; text-transform:uppercase; vertical-align:bottom;
                   -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  table.matrix td{ border:.5pt solid #d3dae2; padding:3.5pt 4pt; vertical-align:top; word-wrap:break-word; }
  table.matrix tbody tr:nth-child(even) td{ background:#f5f8fb; }
  table.matrix .num{ text-align:right; white-space:nowrap; }
  table.matrix .cn0{ font-weight:700; color:#16243a; }
  table.auth{ width:100%; border-collapse:collapse; font-size:8.7pt; }
  table.auth th{ background:#16243a; color:#fff; text-align:left; padding:5pt 7pt; font-family:Arial,'Liberation Sans',sans-serif;
                 font-size:7.6pt; text-transform:uppercase; letter-spacing:.04em;
                 -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  table.auth td{ border:.6pt solid #d3dae2; padding:5pt 7pt; vertical-align:top; }
  table.auth tbody tr:nth-child(even) td{ background:#f5f8fb; }
  table.auth .n{ text-align:center; font-weight:700; color:#2f6fb3; }
  .relied{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7pt; }
</style>
"""

HTML_STATIC = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
               '<link rel="stylesheet" href="digest.css">' + CSS + '</head><body>\n')
HTML_TMPL = """  <div class="scope">Section 135 Electricity Act — Compilation Digest &nbsp;·&nbsp; {span}</div>
  <h1 class="case">{h1}</h1>
  <div class="subcite">{sub}</div>
  <p class="lead-note">{lead}</p>
"""
def HTML_HEAD_fmt(**kw):
    return HTML_STATIC + HTML_TMPL.format(**kw)
HTML_TAIL = """
  <p class="disclaimer">Compilation digest generated from the per-case summaries of {span}. It collates the courts' own reasoning for cross-referencing and is not a substitute for the full judgments.</p>
</body></html>"""

# ----------------------------------------------------------------------------
# DOC 1 : INTERPRETATIONS BY PROVISION
# ----------------------------------------------------------------------------
def canon_prov(p):
    q = p.lower()
    if '2(15)' in q: return (1, 'Section 2(15) — &ldquo;Consumer&rdquo;')
    if '154' in q:   return (5, 'Section 154(5) — Civil Liability')
    if '150' in q:   return (4, 'Section 150 — Abetment')
    if 'proviso' in q or 'presumption' in q: return (3, 'Third Proviso to Section 135(1) — Presumption of Dishonest Use')
    if 'reg' in q:   return (6, 'DERC (Supply Code) Regulations, 2007 — Regulations 60 to 63')
    if '135' in q:   return (2, 'Section 135(1)(a) — Theft of Electricity')
    return (9, esc(p))

PROV_NOTE = {
 'Section 2(15) — &ldquo;Consumer&rdquo;':
   'The Court read &ldquo;consumer&rdquo; to embrace both the person actually using the electricity and the owner/registered consumer of the connected premises. A registered consumer stays answerable for illegal abstraction found at the premises even where another person is the user (<i>Lokesh Chandela</i>).',
 'Section 135(1)(a) — Theft of Electricity':
   'Across the set the charge was confined to clause (a) &mdash; a dishonest tap on, or connection with, the licensee&rsquo;s lines, cables, service wires or service facilities &mdash; the cases being direct hooking rather than meter tampering (clauses (b)&ndash;(e)). &ldquo;Dishonestly&rdquo;, undefined in the Act, is supplied by Section 24 IPC (wrongful gain to one / wrongful loss to another). The unauthorised connection took many forms &mdash; pole hooks, distribution-box and street-light-box taps, punctured service cables, and change-over switches past stopped meters &mdash; each treated as satisfying clause (a).',
 'Third Proviso to Section 135(1) — Presumption of Dishonest Use':
   'A reverse-onus clause. On proof of an artificial or unauthorised means of abstraction, dishonest use is presumed &ldquo;until the contrary is proved.&rdquo; Read with <i>Neeraj Dutt</i> (&ldquo;shall presume&rdquo; is compulsory) and <i>Hiten P. Dalal</i> (rebuttal on the prudent-man standard), the burden shifts to the accused, the natural rebuttal being proof of lawful metered use &mdash; paid bills &mdash; under the Section 106 Evidence Act onus (<i>Mukesh Rastogi</i>). It was not rebutted in any case in this set.',
 'Section 150 — Abetment':
   'Abetment carries the punishment of the principal offence. A registered consumer who, knowing the meter is stopped, permits or consciously allows the user to draw an unauthorised supply abets the theft and is convicted under Section 135 read with Section 150.',
 'Section 154(5) — Civil Liability':
   'On conviction the Special Court may additionally fix civil liability for the electricity illegally used; the criminal conviction and the civil recovery are companion outcomes of the same trial.',
 'DERC (Supply Code) Regulations, 2007 — Regulations 60 to 63':
   'Reproduced in every judgment as the procedural backbone: the inspection power with photo-ID safeguards (Reg. 60); the contemporaneous site report with seizure, sealing and photo/video documentation, including recording any refusal of locals to witness (Reg. 61); the prosecution procedure, the 24-hour police complaint and the caution that a missing meter seal alone cannot found a theft case (Reg. 62); and assessment at twice the applicable tariff for up to twelve months with credit for units paid (Reg. 63). Unchallenged compliance was treated as confirming the inspection&rsquo;s regularity.',
}

def build_interpretations():
    buckets = defaultdict(lambda: OrderedDict())  # label -> {text -> [cases]}
    order = {}
    for c in cases:
        for it in c.get('interpretations', []):
            o, label = canon_prov(it['provision'])
            order[label] = o
            txt = esc(it['interpretation'])
            buckets[label].setdefault(txt, []).append(c)
    parts = []
    for label in sorted(buckets, key=lambda l: order[l]):
        parts.append(f'<h2>{label}</h2>')
        if label in PROV_NOTE:
            parts.append(f'<div class="prov-note">{PROV_NOTE[label]}</div>')
        for txt, cs in buckets[label].items():
            chips = ''.join(chip(c) for c in sorted(cs, key=lambda x: x['case_no']))
            parts.append(f'<div class="entry"><div class="txt">{txt}</div><div class="chips">{chips}</div></div>')
    lead = ('Every interpretation of a statutory provision drawn from the judgments, grouped by the provision '
            'construed. Identical readings are stated once with all contributing cases tagged; distinct readings '
            'appear separately. Provisions are ordered Section&nbsp;2(15) &rarr; 135(1)(a) &rarr; third proviso '
            '&rarr; 150 &rarr; 154(5) &rarr; DERC Regs 60&ndash;63.')
    html = HTML_HEAD_fmt(span=span, h1='Interpretation of the Electricity Act, 2003',
                            sub='Statutory construction across the judgments, grouped by provision',
                            lead=lead) + '\n'.join(parts) + HTML_TAIL.format(span=span)
    open('merged_1_interpretations.html', 'w').write(html)
    print('interpretations:', sum(len(v) for v in buckets.values()), 'distinct readings across', len(buckets), 'provisions')

# ----------------------------------------------------------------------------
# DOC 2 : CITATIONS (TABLE OF AUTHORITIES)
# ----------------------------------------------------------------------------
def build_citations():
    auth = OrderedDict()  # case-name -> {citation, court, principle, cases:[]}
    for c in cases:
        for ct in c.get('citations', []):
            k = ct['case']
            if k not in auth:
                auth[k] = {'citation': ct.get('citation', ''), 'court': ct.get('court', ''),
                           'principle': ct.get('principle', ''), 'cases': []}
            auth[k]['cases'].append(c['case_no'])
    rows = sorted(auth.items(), key=lambda kv: (-len(kv[1]['cases']), kv[1]['cases'][0]))
    trs = []
    for name, d in rows:
        relied = ' '.join(f'<span class="chip"><b>{n}</b></span>' for n in d['cases'])
        trs.append(
          '<tr>'
          f'<td class="n">{len(d["cases"])}</td>'
          f'<td><span class="cn">{esc(name)}</span><br><span style="color:#5b6b7f">{esc(d["citation"])}'
          f'{(" &middot; " + esc(d["court"])) if d["court"] else ""}</span></td>'
          f'<td>{esc(d["principle"])}</td>'
          f'<td class="relied">{relied}</td>'
          '</tr>')
    table = ('<table class="auth"><thead><tr>'
             '<th style="width:6%">Cases</th><th style="width:26%">Authority</th>'
             '<th style="width:50%">Proposition cited for</th><th style="width:18%">Relied on in</th>'
             '</tr></thead><tbody>' + ''.join(trs) + '</tbody></table>')
    lead = (f'All authorities relied on across {span}, one row per authority, ranked by how many judgments invoked it. '
            'Every citation in this set was drawn from the courts&rsquo; own reasoning &mdash; neither prosecution nor defence '
            'argued from case law. Treatment is &ldquo;relied on&rdquo; throughout.')
    html = HTML_HEAD_fmt(span=span, h1='Table of Authorities', sub='Every case-law citation across the judgments, de-duplicated and ranked by frequency',
                            lead=lead) + table + HTML_TAIL.format(span=span)
    open('merged_2_citations.html', 'w').write(html)
    print('citations:', len(auth), 'distinct authorities')

# ----------------------------------------------------------------------------
# DOC 3 : SIGNIFICANCE (THEMATIC)
# ----------------------------------------------------------------------------
THEMES = [
 ('The reverse-onus presumption (third proviso)', ['reverse-onus', 'presumption', 'shall presume', 'proviso', 'section 106', 'template held']),
 ('Admissibility of inspection videography (Section 65B)', ['65b']),
 ('Defence cross-examination as admission', ['cross-exam', 'suggestion', 'mass-raid', 'video demands an explanation']),
 ('Non-joining of a public witness', ['public witness', 'public-witness']),
 ('Presence, occupancy & identity of the user', ['presence', 'signed inspection', 'passer-by', 'identification', 'appearing in the inspection video', 'bill in someone', 'occupancy', 'ownership documents', 'representative']),
 ('Registered-consumer liability & abetment', ['registered consumer', 'hide behind', 'landlord', 'abett']),
 ('Concealed devices & stopped meters', ['change-over', 'switch', 'stopped meter', 'live load', 'badge of dishonesty']),
 ('Scope of the licensee’s works tapped', ['street-light', 'infrastructure', 'puncturing', 'service cable', 'paradigm']),
 ('Commercial use & the size of the assessment', ['commercial', 'stakes']),
 ('Settlement of the theft bill as corroboration', ['settl', 'noc']),
 ('Criminal conviction & civil liability together', ['civil recovery', 'travel together', 'criminal conviction and civil']),
 ('Delay & procedural integrity', ['delay', 'successive io', 'report–testimony', 'report-testimony']),
]
def theme_of(point):
    p = point.lower()
    for label, kws in THEMES:
        if any(k in p for k in kws):
            return label
    return 'Other case-specific observations'

def build_significance():
    grouped = OrderedDict((label, []) for label, _ in THEMES)
    grouped['Other case-specific observations'] = []
    for c in cases:
        for s in c.get('significance', []):
            grouped[theme_of(s['point'])].append((c, s))
    parts = []
    for label, items in grouped.items():
        if not items: continue
        parts.append(f'<div class="theme"><h2>{esc(label)}</h2>')
        for c, s in items:
            parts.append(
              f'<div class="sig-item">{chip(c)} <span class="pt">{esc(s["point"])}.</span> '
              f'{esc(s["explanation"])}</div>')
        parts.append('</div>')
    lead = (f'Every &ldquo;significance&rdquo; takeaway from {span}, clustered by the proposition it illustrates so recurring '
            'themes and outliers are visible side by side. Each point is tagged with its source case.')
    html = HTML_HEAD_fmt(span=span, h1='Significance — Cross-Case Propositions', sub='What each judgment adds to the Section 135 jurisprudence, grouped by theme',
                            lead=lead) + '\n'.join(parts) + HTML_TAIL.format(span=span)
    open('merged_3_significance.html', 'w').write(html)
    tot = sum(len(v) for v in grouped.values())
    print('significance:', tot, 'points across', len([1 for v in grouped.values() if v]), 'themes')

# ----------------------------------------------------------------------------
# DOC 4 : COMPARATIVE FACTS MATRIX  (landscape)
# ----------------------------------------------------------------------------
def gv(gf, *keys, default='&mdash;'):
    for k in keys:
        if k in gf and gf[k] not in (None, ''):
            return gf[k]
    return default

def yn(v, true='Yes', false='No'):
    if v is True: return true
    if v is False: return false
    return '&mdash;'

def build_facts():
    heads = ['#', 'Accused', 'DISCOM', 'Use', 'Theft mode', 'Meter status', 'Load (KW)',
             'Assessment (Rs.)', 'PW / DW', 'Pub. wit.', '65B cert.', 'Defence', 'Outcome']
    ws =   ['3%', '11%', '6%', '8%', '17%', '11%', '5%', '7%', '5%', '6%', '5%', '13%', '9%']
    ths = ''.join(f'<th style="width:{w}">{h}</th>' for h, w in zip(heads, ws))
    trs = []
    n_conv = 0
    for c in cases:
        gf = c.get('generic_facts', {})
        out = str(gv(gf, 'outcome'))
        if 'convict' in out.lower(): n_conv += 1
        pw = gv(gf, 'prosecution_witnesses', default='&mdash;')
        dw = gf.get('defence_witnesses', 0)
        pubwit = gf.get('public_witness_joined')
        pw_cell = 'No (refused)' if (pubwit is False and gf.get('public_witness_refusal_recorded')) else yn(pubwit)
        cert = gf.get('s65b_certificate_filed')
        cert_cell = 'Yes' if cert is True else ('No*' if cert is False else '&mdash;')
        trs.append(
          '<tr>'
          f'<td class="cn0">{c["case_no"]}</td>'
          f'<td>{esc(short_name(c["title"]))}</td>'
          f'<td>{esc(gv(gf, "discom", default=c.get("discom","&mdash;")).replace("BSES Yamuna Power Ltd.","BSES YPL").replace("Tata Power Delhi Distribution Ltd. (TPDDL)","TPDDL"))}</td>'
          f'<td>{esc(gv(gf, "consumer_type"))}</td>'
          f'<td>{esc(gv(gf, "theft_mode"))}</td>'
          f'<td>{esc(gv(gf, "meter_status"))}</td>'
          f'<td class="num">{esc(gv(gf, "load_kw"))}</td>'
          f'<td class="num">{indian(gf.get("assessment_rs"))}</td>'
          f'<td class="num">{esc(pw)} / {esc(dw)}</td>'
          f'<td>{pw_cell}</td>'
          f'<td>{cert_cell}</td>'
          f'<td>{esc(gv(gf, "defence"))}</td>'
          f'<td>{esc(gv(gf, "outcome"))}</td>'
          '</tr>')
    table = f'<table class="matrix"><thead><tr>{ths}</tr></thead><tbody>' + ''.join(trs) + '</tbody></table>'
    lead = (f'One row per case, case-specific detail stripped to comparable descriptors so patterns across {span} stand out '
            f'(consumer type, mode of theft, meter status, load, assessed value, witnesses, defence, outcome). '
            f'All {N} convicted. <span style="color:#5b6b7f">65B cert. &ldquo;No*&rdquo; = videography admitted without a certificate under the waived-objection rule in <i>Sonu @ Amar</i>.</span>')
    html = HTML_HEAD_fmt(span=span, h1='Comparative Facts Matrix', sub='Generic, case-stripped facts for side-by-side comparison',
                            lead=lead) + table + HTML_TAIL.format(span=span)
    open('merged_4_facts_matrix.html', 'w').write(html)
    print('facts matrix:', N, 'cases,', n_conv, 'convicted')

build_interpretations()
build_citations()
build_significance()
build_facts()
print('done; span =', span)
