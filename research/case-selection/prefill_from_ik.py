#!/usr/bin/env python3
"""Stage 0 — build the mechanical skeleton of a record from Indian Kanoon's own
doc JSON. ZERO model tokens: docid, court, court_type, date, bench, neutral_cite,
provisions_construed (statute cites), authority candidates (case cites), and
cited-by seeds for the citation graph. Feeds the (cached) Opus judgment pass.
Usage: prefill_from_ik.py <ik_doc.json>  ->  prints the prefill JSON.
"""
import json, re, sys
d = json.load(open(sys.argv[1]))
plain = re.sub("<[^>]+>", " ", d.get("doc", ""))
plain = re.sub(r"&nbsp;|&amp;|&#\d+;", " ", plain); plain = re.sub(r"\s+", " ", plain)
eqc = re.search(r"Equivalent citations:(.*?)Bench:", plain)
bench = re.search(r"Bench:\s*(.*?)\s+(?:REPORTABLE|IN THE|J U D)", plain)
cites = d.get("cites", [])
statutes = [c for c in cites if re.search(r"Section|Act|Code|Constitution", c.get("title", ""))]
cases = [c for c in cites if re.search(r"\bvs?\b\.?|\bv\.\b", c.get("title", "").lower())]
print(json.dumps({
    "_stage": "0 — IK metadata prefill (code, 0 model tokens)",
    "docid": str(d.get("tid")), "title": d.get("title"),
    "court": d.get("docsource"),
    "court_type": "SC" if "Supreme Court" in (d.get("docsource") or "") else "HC",
    "date": d.get("publishdate"),
    "neutral_cite": eqc.group(1).strip() if eqc else "",
    "bench": [b.strip() for b in re.split(",", bench.group(1))] if bench else [],
    "numcitedby": d.get("numcitedby"), "numcites": d.get("numcites"),
    "provisions_construed": [{"provision": c["title"].split(" in ")[0].replace("Section ", "s."),
                              "docid": str(c["tid"])} for c in statutes],
    "authority_candidates": [{"name": c["title"], "docid": str(c["tid"])} for c in cases],
    "cited_by_seeds": [{"name": x.get("title"), "docid": str(x.get("tid"))} for x in d.get("citedby", [])],
}, indent=2, ensure_ascii=False))
