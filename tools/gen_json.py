#!/usr/bin/env python3
"""Build per-case JSON extracts for the 29 new cases by parsing the generated digest HTML
   (now the source of truth) and adding generic_facts from the fingerprints. Also scrubs DERC
   from the 21 existing JSONs."""
import re, json, glob, os, html as htmlmod

HERE = os.path.dirname(__file__)
FP = os.path.join(HERE, '..', 'fp')
JSONDIR = os.path.join(HERE, '..', 'json')

def clean(x):
    x = re.sub(r'<br\s*/?>', ' — ', x)
    x = re.sub(r'<[^>]+>', '', x)
    x = htmlmod.unescape(x)
    x = x.replace('\xa0', ' ').replace('‑', '-')
    return re.sub(r'\s+', ' ', x).strip()

def dv(s, key):
    m = re.search(r'<div class="k">%s</div><div class="v">(.*?)</div>' % re.escape(key), s, re.S)
    return clean(m.group(1)) if m else ''

STD_INTERP = {
 '2(15)': "'Consumer' under Section 2(15) includes the owner/registered consumer, not only the actual user; the owner is answerable for illegal abstraction found at the premises even where a tenant is the user (Lokesh Chandela).",
 '150': "A registered consumer/owner who consciously permits a tenant to draw an unauthorised supply abets the theft and is punishable u/s 150 with the principal's punishment; the abettor can be convicted even where the actual user has absconded or died and is never tried.",
 '154': "On conviction the Special Court may additionally fix civil liability for the electricity illegally used; criminal conviction and civil recovery are companion outcomes of the same trial.",
}

def load_fp(cn):
    for cand in (f"{cn}.json", f"0{cn[-2:]}.json"):
        p = os.path.join(FP, cand)
        if os.path.exists(p):
            d = json.load(open(p))
            if str(d.get('case_no','')).lstrip('0').rjust(3,'0') == cn:
                return d
    for p in glob.glob(os.path.join(FP, '*.json')):
        d = json.load(open(p))
        if str(d.get('case_no','')).lstrip('0').rjust(3,'0') == cn:
            return d
    return {}

def consumer_type(fp):
    n = (fp.get('notable') or '')
    if isinstance(n, list): n = ' '.join(n)
    blob = (n + ' ' + str(fp.get('theft_mode','')) ).lower()
    if 'e-rickshaw' in blob or 'rickshaw' in blob: return 'non-domestic (e-rickshaw charging)'
    if 'dhaba' in blob or 'eatery' in blob or 'godown' in blob or 'kabadi' in blob: return 'commercial'
    if 'pg ' in blob or 'paying guest' in blob or 'accommodation' in blob: return 'domestic used for non-domestic (PG)'
    if 'commercial' in blob or 'telecom' in blob or 'tower' in blob: return 'commercial'
    return 'domestic'

def generic_facts(cn, fp, statutes):
    secs = fp.get('sections_applied', [])
    secs_s = ' '.join(str(x) for x in secs)
    dec = (fp.get('decision','') or '')
    mode = fp.get('theft_mode','') or ''
    is_acq = 'acquit' in dec.lower()
    is_app = 'appeal' in dec.lower()
    is_civ = 'civil' in dec.lower()
    flags = fp.get('flags', {})
    if is_acq: outcome = 'Acquitted — complaint dismissed'
    elif is_app: outcome = 'Civil appeal dismissed (s.126 unauthorised use; s.145 bar)'
    elif is_civ: outcome = 'Civil suit (declaration/injunction)'
    elif '150' in secs_s: outcome = 'Convicted u/s 135 r/w 150 (abetment)'
    elif '138' in secs_s: outcome = 'Convicted u/s 135/138/150'
    else: outcome = 'Convicted u/s 135'
    gf = {
     'consumer_type': consumer_type(fp),
     'theft_mode': mode,
     'meter_status': ('no meter / no lawful metered supply' if ('no meter' in (str(fp.get('notable','')).lower()) or 'cable' in mode.lower() or 'tapping' in mode.lower() or 'hook' in mode.lower()) else ('meter tampered' if 'tamper' in mode.lower() or 'bypass' in mode.lower() or 'jump' in mode.lower() else '—')),
     'load_kw': fp.get('load_kw'),
     'assessment_rs': fp.get('assessment_rs'),
     'discom': fp.get('complainant_company',''),
     'public_witness_joined': fp.get('public_witness_joined'),
     'prosecution_witnesses': fp.get('pw_count'),
     'defence_witnesses': fp.get('dw_count') if fp.get('dw_count') is not None else 0,
     's65b_certificate_filed': flags.get('s65b_certificate'),
     'abetment_charge': '150' in secs_s,
     'absconding_user': bool(fp.get('user_absconding')),
     'noc_issued': flags.get('noc', False),
     'settlement': flags.get('settlement', False),
     'meter_bypass': ('bypass' in mode.lower() or 'tamper' in mode.lower() or 'jump' in mode.lower()),
     'outcome': outcome,
     'sentence': ('n/a (acquitted)' if is_acq else ('n/a (civil)' if (is_app or is_civ) else 'posted for hearing on quantum')),
     'defence': ('false implication; no defence evidence' ),
    }
    return gf

# case_no -> (html, discom-for-fallback)
NEW = ["020","022","024","025","028","030","031","033","034","036","037","038","050",
       "026","027","032","035","042","043","044","045","046","047","048","049",
       "029","039","040","041"]

def parse_case(cn):
    s = open(os.path.join(HERE, f"case_{cn}.html")).read()
    fp = load_fp(cn)
    title = clean(re.search(r'<h1 class="case">(.*?)</h1>', s, re.S).group(1))
    subcite = clean(re.search(r'<div class="subcite">(.*?)</div>', s, re.S).group(1))
    court = dv(s, 'Court'); judge = dv(s, 'Judge'); parties = dv(s, 'Parties')
    result = dv(s, 'Result'); statutes_raw = dv(s, 'Statutes Invoked')
    statutes = [x.strip() for x in re.split(r';', statutes_raw) if x.strip()]
    # interpretations
    isec = re.search(r'<h2>Interpretation of the Electricity Statutes</h2>(.*?)<h2>Held</h2>', s, re.S)
    interps = []
    act = 'Electricity Act, 2003'
    if isec:
        body = isec.group(1)
        for m in re.finditer(r'<h3 class="grp">(.*?)</h3>|<h3>(.*?)</h3>\s*<p>(.*?)</p>', body, re.S):
            if m.group(1):
                act = clean(m.group(1))
            elif m.group(2):
                interps.append({'act': act, 'provision': clean(m.group(2)), 'interpretation': clean(m.group(3))})
    # augment by case type
    secs_s = ' '.join(str(x) for x in fp.get('sections_applied', []))
    provs = ' '.join(i['provision'] for i in interps)
    if '150' in secs_s and '2(15)' not in provs and 'acquit' not in (fp.get('decision','') or '').lower():
        interps.append({'act':'Electricity Act, 2003','provision':'Section 2(15)','interpretation':STD_INTERP['2(15)']})
        interps.append({'act':'Electricity Act, 2003','provision':'Section 150','interpretation':STD_INTERP['150']})
    if '154' in secs_s and '154' not in provs:
        interps.append({'act':'Electricity Act, 2003','provision':'Section 154(5)','interpretation':STD_INTERP['154']})
    # significance
    sig = []
    sm = re.search(r'<ul class="sig">(.*?)</ul>', s, re.S)
    if sm:
        for li in re.finditer(r'<li><span class="bl">(.*?)</span>\s*(.*?)</li>', sm.group(1), re.S):
            sig.append({'point': clean(li.group(1)).rstrip('.'), 'explanation': clean(li.group(2))})
    # citations
    cits = []
    cm = re.search(r'<table class="cit">(.*?)</table>', s, re.S)
    if cm:
        for tr in re.finditer(r'<tr>\s*<td><span class="cn">(.*?)</span><br>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>', cm.group(1), re.S):
            cits.append({'case': clean(tr.group(1)), 'citation': clean(tr.group(2)),
                         'court': '', 'principle': clean(tr.group(3)), 'treatment': clean(tr.group(4)) or 'Relied on'})
    out = {
     'case_no': cn, 'title': title, 'subcite': subcite,
     'court': court, 'judge': judge,
     'date_of_judgment': fp.get('date_of_judgment',''), 'offence_date': fp.get('offence_date',''),
     'discom': fp.get('complainant_company',''), 'parties': parties,
     'result': result, 'statutes': statutes,
     'interpretations': interps, 'citations': cits, 'significance': sig,
     'generic_facts': generic_facts(cn, fp, statutes),
    }
    return out

n=0
for cn in NEW:
    d = parse_case(cn)
    json.dump(d, open(os.path.join(JSONDIR, f"case_{cn}.json"), 'w'), indent=1, ensure_ascii=False)
    n+=1
print("wrote", n, "new JSONs")

# ---- scrub DERC from existing 21 JSONs ----
scrubbed=0
for p in glob.glob(os.path.join(JSONDIR, 'case_*.json')):
    d = json.load(open(p)); ch=False
    ints = [i for i in d.get('interpretations',[]) if 'derc' not in (i.get('provision','')+i.get('act','')+i.get('interpretation','')).lower() and 'regulations 60' not in i.get('provision','').lower()]
    if len(ints) != len(d.get('interpretations',[])): d['interpretations']=ints; ch=True
    sts = [x for x in d.get('statutes',[]) if 'derc' not in x.lower() and 'regulations 60' not in x.lower()]
    if len(sts) != len(d.get('statutes',[])): d['statutes']=sts; ch=True
    if ch:
        json.dump(d, open(p,'w'), indent=1, ensure_ascii=False); scrubbed+=1
print("DERC-scrubbed", scrubbed, "JSONs")
