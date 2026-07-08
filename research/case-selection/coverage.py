#!/usr/bin/env python3
"""Coverage-gap tracker -> the selection worklist.

Reads the corpus records + the aggregation indexes and reports where the
jurisprudence is THIN, so the next cases are chosen to fill gaps rather than pile
onto already-settled points. Run after build_aggregation.py. Writes
coverage_report.md and prints a summary.
"""
import json, os, glob
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TAXONOMY = ["126v135", "assessment-126", "mensrea-135", "appeal-127",
            "jurisdiction-145-154", "compounding-152", "natural-justice",
            "provisional-final", "burden-proof", "limitation-56"]
CATS = ["industrial", "commercial", "domestic", "agricultural"]

def load(name): return json.load(open(os.path.join(HERE, name)))
def load_records():
    paths = glob.glob(os.path.join(HERE, "records", "*.record.json"))
    paths += [os.path.join(HERE, p) for p in ("SC-001.record.json", "HC-003.record.json")
              if os.path.exists(os.path.join(HERE, p))]
    return [json.load(open(p)) for p in paths]

def main():
    recs = load_records()
    im = load("issue_matrix.json")
    pi = load("provision_index.json")
    cg = load("citation_graph.json")
    L = []
    def out(s=""): L.append(s)

    out(f"# Coverage report — selection worklist\n")
    nSC = sum(1 for r in recs if r["court_type"] == "SC")
    out(f"Corpus: **{len(recs)} records** — {nSC} SC, {len(recs)-nSC} HC "
        f"across {len(set(s for r in recs for s in r.get('state',[])))} states.\n")

    out("## 1 · Issue-node coverage (thin = <2 cases; single = 1)\n")
    for node in TAXONOMY:
        n = im.get(node, {}).get("n_cases", 0)
        tag = "❌ MISSING" if n == 0 else ("⚠️ single" if n == 1 else ("• thin" if n == 2 else "✓"))
        lead = im.get(node, {}).get("leading_case", {}).get("case_id", "-")
        out(f"- `{node}` — {n} case(s) {tag}  (lead {lead})")
    out()

    out("## 2 · Provision-version risk (holdings resting only on superseded text)\n")
    for sec, v in pi.items():
        vers = set(v["versions_applied"])
        if vers and "post-2007" not in vers and sec.startswith("s."):
            out(f"- `{sec}` — {v['n_holdings']} holding(s), only {sorted(vers)} → **no current-text authority**")
    if not any(set(v['versions_applied']) and 'post-2007' not in set(v['versions_applied'])
               for v in pi.values()):
        out("- (every multi-version provision has at least one post-2007 holding)")
    out()

    out("## 3 · Court hierarchy\n")
    out(f"- SC records: **{nSC}** — {'⚠️ backbone thin; SC cases anchor binding law' if nSC < 3 else '✓'}")
    bt = Counter(r.get("bench_type") for r in recs)
    out(f"- bench mix: {dict(bt)}\n")

    out("## 4 · Consumer-category coverage\n")
    seen = Counter()
    for r in recs:
        for c in r.get("consumer_category", []):
            for k in CATS:
                if k in c.lower(): seen[k] += 1
    for k in CATS:
        out(f"- {k}: {seen[k]} " + ("❌ none" if not seen[k] else ""))
    out()

    out("## 5 · Fact-pattern coverage\n")
    fp = Counter(t for r in recs for t in r.get("fact_pattern_tags", []))
    for t, n in fp.most_common():
        out(f"- {t}: {n}")
    out()

    out("## 6 · Highest-value un-recorded authorities (snowball worklist)\n")
    have = {r["title"].split(" v")[0].strip().lower() for r in recs}
    for b in cg["recurring_authorities"]:
        key = b["authority"].split(" v")[0].strip().lower()
        if not any(key in h or h in key for h in have):
            out(f"- **{b['authority']}** — cited {b['times_cited']}× ({b['treatments']}) → not yet a record")
    out()

    open(os.path.join(HERE, "coverage_report.md"), "w").write("\n".join(L))
    print("\n".join(L))
    print("\nwrote coverage_report.md")

if __name__ == "__main__":
    main()
