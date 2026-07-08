#!/usr/bin/env python3
"""Verify gate: every verbatim field in records/<ID>.record.json must be an exact
substring of queue/<ID>.txt (whitespace-normalised). Prints PASS / FAIL list.
Usage: verify_record.py <ID>
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
cid = sys.argv[1]
rec = json.load(open(os.path.join(HERE, "records", f"{cid}.record.json")))
src = open(os.path.join(HERE, "queue", f"{cid}.txt")).read()
def norm(s): return re.sub(r"\s+", " ", s or "").strip()
nsrc = norm(src)
problems = []
def check(label, text):
    if not text: return
    if norm(text) not in nsrc:
        problems.append((label, text[:90]))
for i, h in enumerate(rec.get("provision_holdings", [])):
    check(f"holding[{i}].key_para", h.get("key_para"))
for i, a in enumerate(rec.get("authorities", [])):
    check(f"auth[{i}].principle_para", a.get("principle_para"))
    check(f"auth[{i}].treatment_para", a.get("treatment_para"))
for i, q in enumerate(rec.get("issues_framed", [])):
    check(f"issues_framed[{i}]", q)
if problems:
    print(f"FAIL ({len(problems)} problems) for {cid}:")
    for lbl, t in problems: print(f"  - {lbl}: {t!r}")
    sys.exit(1)
print(f"PASS — {cid}: all verbatim fields grep-match the source.")
