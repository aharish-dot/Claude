#!/usr/bin/env python3
"""Fetch each case in manifest.json from Indian Kanoon: save plain text to
queue/<ID>.txt and the free Stage-0 prefill to prefill/<ID>.prefill.json.
Idempotent — skips a case whose text already exists. Uses curl (agent proxy).
"""
import json, os, re, subprocess, sys
from clean_queue import clean as clean_text   # (1) born-clean fetches
HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("IK_API_TOKEN", "fd1bec72318f3a4a711b3d54a1008d86a5a44338")
man = json.load(open(os.path.join(HERE, "manifest.json")))

def fetch(docid):
    url = f"https://api.indiankanoon.org/doc/{docid}/?maxcites=50&maxcitedby=10"
    out = subprocess.run(["curl", "-sS", "-X", "POST", url,
                          "-H", f"Authorization: Token {TOKEN}"],
                         capture_output=True, text=True, timeout=120)
    return json.loads(out.stdout)

def plain(html):
    t = re.sub(r"<[^>]+>", " ", html)
    t = re.sub(r"&nbsp;|&amp;|&#\d+;|&quot;|&#x27;", " ", t)
    return re.sub(r"[ \t]+", " ", t).strip()

def prefill(d, plaintext):
    eqc = re.search(r"Equivalent citations:(.*?)Bench:", plaintext)
    bench = re.search(r"Bench:\s*(.*?)\s+(?:REPORTABLE|IN THE|J U D|JUDGMENT|ORDER)", plaintext)
    cites = d.get("cites", [])
    statutes = [c for c in cites if re.search(r"Section|Act|Code|Constitution", c.get("title", ""))]
    cases = [c for c in cites if re.search(r"\bvs\b|\bv\.\b", c.get("title", "").lower())]
    return {
        "docid": str(d.get("tid")), "title": d.get("title"), "court": d.get("docsource"),
        "court_type": "SC" if "Supreme Court" in (d.get("docsource") or "") else "HC",
        "date": d.get("publishdate"),
        "neutral_cite": eqc.group(1).strip() if eqc else "",
        "bench": [b.strip() for b in re.split(",", bench.group(1))] if bench else [],
        "numcitedby": d.get("numcitedby"), "numcites": d.get("numcites"),
        "provisions_construed": [{"provision": c["title"].split(" in ")[0].replace("Section ", "s."),
                                  "docid": str(c["tid"])} for c in statutes],
        "authority_candidates": [{"name": c["title"], "docid": str(c["tid"])} for c in cases],
        "cited_by_seeds": [{"name": x.get("title"), "docid": str(x.get("tid"))} for x in d.get("citedby", [])],
    }

for c in man["cases"]:
    tid = c["docid"]; cid = c["id"]
    tp = os.path.join(HERE, "queue", f"{cid}.txt")
    if os.path.exists(tp) and os.path.getsize(tp) > 500:
        print(f"skip {cid} (already fetched)"); continue
    d = fetch(tid)
    txt = clean_text(plain(d.get("doc", "")))
    open(tp, "w").write(txt)
    json.dump(prefill(d, txt), open(os.path.join(HERE, "prefill", f"{cid}.prefill.json"), "w"),
              indent=2, ensure_ascii=False)
    print(f"{cid}: {len(txt):>6} chars | cby={d.get('numcitedby')} | provs={len(prefill(d,txt)['provisions_construed'])} | {d.get('title','')[:40]}")
print("done")
