#!/usr/bin/env python3
"""Append a case's doc-id'd authorities to <court>/state/authorities-ledger.json.

Usage: python tools/update_ledger.py <court_dir> <case_id>
Reads  <court_dir>/extracts/<case_id>.extract.json and merges each authority that
carries an Indian Kanoon doc-id into the ledger (keyed by doc-id), recording
{case_id, treatment, proposition}. Idempotent: re-running for the same case
does not duplicate entries. Inline HTML in the extract is stripped to plain text.
"""
import sys, json, re, html as H


def clean(x):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', str(x or '')))).strip()


def main():
    court, cid = sys.argv[1], sys.argv[2]
    ex = json.load(open(f"{court}/extracts/{cid}.extract.json"))
    lp = f"{court}/state/authorities-ledger.json"
    led = json.load(open(lp))
    added = 0
    for a in ex.get("authorities", []):
        did = str(a.get("docid", "")).strip()
        if not did:
            continue
        e = led["authorities"].setdefault(did, {
            "name": clean(a.get("name")),
            "cite": clean(a.get("cite")),
            "court": clean(a.get("court")),
            "cited_by": [],
        })
        if not e.get("cite") and a.get("cite"):
            e["cite"] = clean(a["cite"])
        if not any(c["case_id"] == cid for c in e["cited_by"]):
            e["cited_by"].append({
                "case_id": cid,
                "treatment": clean(a.get("treatment")),
                "proposition": clean(a.get("prop")),
            })
            added += 1
    with open(lp, "w") as f:
        json.dump(led, f, indent=1, ensure_ascii=False)
    print(f"ledger: +{added} citation(s) for {cid}; {len(led['authorities'])} authorities total")


if __name__ == "__main__":
    main()
