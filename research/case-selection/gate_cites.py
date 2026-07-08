#!/usr/bin/env python3
"""Provision-cites gate: fetch doc JSON for candidate tids, check whether the
judgment actually CITES the target Electricity Act 2003 provisions (s.126/127/
135/145/152/154/56). Prints, per tid, which target provisions it cites + a
tax-poison check. Only cases that cite >=1 target provision pass the gate.
"""
import json, re, subprocess, sys
TOKEN = "fd1bec72318f3a4a711b3d54a1008d86a5a44338"
# target Electricity Act 2003 provisions by title regex on cites
TARGETS = {
 "s.126":"126", "s.127":"127", "s.135":"135", "s.145":"145",
 "s.152":"152", "s.154":"154", "s.56":r"\b56\b",
}
TAX = re.compile(r"entry tax|value added|sales tax|income.?tax|\bVAT\b|land tax|stamp act|central excise|customs act", re.I)
ELECACT = re.compile(r"Electricity Act, 2003|Electricity Act 2003", re.I)

def fetch(docid):
    url = f"https://api.indiankanoon.org/doc/{docid}/?maxcites=60&maxcitedby=5"
    out = subprocess.run(["curl","-sS","-X","POST",url,"-H",f"Authorization: Token {TOKEN}"],
                         capture_output=True, text=True, timeout=120)
    return json.loads(out.stdout)

for tid in sys.argv[1:]:
    d = fetch(tid)
    title = d.get("title","")
    cites = d.get("cites", [])
    citetitles = " || ".join(c.get("title","") for c in cites)
    # which target provisions cited, restricted to Electricity Act context
    hit = []
    for name,pat in TARGETS.items():
        for c in cites:
            ct = c.get("title","")
            if re.search(pat, ct) and re.search(r"Electricity", ct, re.I):
                hit.append(name); break
    doctxt = re.sub(r"<[^>]+>"," ", d.get("doc",""))
    elec_in_body = len(re.findall(r"unauthori|theft|tamper|pilfer|assessing officer", doctxt, re.I))
    taxflag = "TAX?" if TAX.search(doctxt[:4000]) else ""
    verdict = "PASS" if hit else "FAIL"
    print(f"[{verdict}] {taxflag} tid={tid} cby={d.get('numcitedby')} len={len(doctxt)} provs={sorted(set(hit))} electerms={elec_in_body}")
    print(f"        {title[:95]}")
