#!/usr/bin/env python3
"""Upstream topicality gate (enforcement layer).

gate_cites.py is the SELECTION-TIME gate: run it on a candidate docid before you
ever add it to the manifest — it fetches the doc and confirms the judgment cites
>=1 target Electricity Act 2003 provision. This script is the CORPUS-WIDE audit
that makes sure nothing slipped through: for every ACTIVE (non-rejected) manifest
case it checks, with zero network calls, that the case actually construes a target
provision (via prefill provisions_construed and/or the committed record). It is the
guard that would have caught HC-007/012/015 (land/income/entry tax) before they
were processed.

Exit 1 if any active case fails the gate. Usage: gate_manifest.py
"""
import json, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = {"126", "127", "135", "145", "152", "153", "154", "56"}   # Electricity Act 2003
_secnum = re.compile(r"s\.?\s?(\d+)")

def sections(provs):
    out = set()
    for p in provs or []:
        s = p if isinstance(p, str) else p.get("provision", "")
        for m in _secnum.findall(s):
            out.add(m)
    return out

def main():
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    status = man.get("status", {})
    fails, checked = [], 0
    for c in man["cases"]:
        cid = c["id"]
        st = status.get(cid, "pending")
        if st.startswith("rejected"):
            continue
        checked += 1
        secs = set()
        pf = os.path.join(HERE, "prefill", f"{cid}.prefill.json")
        if os.path.exists(pf):
            secs |= sections(json.load(open(pf)).get("provisions_construed"))
        rp = os.path.join(HERE, "records", f"{cid}.record.json")
        rp = rp if os.path.exists(rp) else os.path.join(HERE, f"{cid}.record.json")
        if os.path.exists(rp):
            secs |= sections(json.load(open(rp)).get("provisions_construed"))
        hit = secs & TARGET
        mark = "PASS" if hit else "FAIL"
        if not hit:
            fails.append(cid)
        print(f"  [{mark}] {cid:8s} {c.get('title','')[:52]:52s} targets={sorted(hit)}")
    print(f"\ngate_manifest: {checked} active cases checked, {len(fails)} FAILED"
          + (f" -> {fails}" if fails else ""))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
