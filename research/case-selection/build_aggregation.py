#!/usr/bin/env python3
"""Aggregation pass (schema [auto] tier). Reads every *.record.json in the corpus
(records/ + the two root gold examples) and combines them into three deliverables:

  provision_index.json  — every holding grouped by statutory provision, chronological
  issue_matrix.json     — cases + leading case + settled position per issue-node
  citation_graph.json   — authority edges (who cites whom, with treatment) + the
                          recurring-authority backbone and in-corpus in-degree

Never hand-entered; recomputed from the records on every run.
"""
import json, os, re, glob
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))

def load_records():
    paths = glob.glob(os.path.join(HERE, "records", "*.record.json"))
    paths += [os.path.join(HERE, p) for p in ("SC-001.record.json", "HC-003.record.json")
              if os.path.exists(os.path.join(HERE, p))]
    recs = []
    for p in sorted(paths):
        r = json.load(open(p))
        recs.append(r)
    # sort chronologically
    recs.sort(key=lambda r: r.get("date", ""))
    return recs

def base_section(prov):
    """Normalise 's.126(3)', 's.126 / s.135', 's.154(5)' -> the base sections it touches."""
    hits = re.findall(r"s\.?\s?(\d+[A-Z]?)", prov or "")
    if hits:
        return ["s." + h for h in dict.fromkeys(hits)]
    # regs / non-section provisions
    return [prov.strip()] if prov else ["(unspecified)"]

def norm_name(n):
    n = (n or "").lower()
    n = re.sub(r"\(.*?\)", " ", n)
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    n = re.sub(r"\b(v|vs|versus|ltd|limited|pvt|private|co|company|state|of|the|and|others|ors|anr|another)\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()

# ---------------------------------------------------------------- provision_index
def build_provision_index(recs):
    idx = defaultdict(list)
    for r in recs:
        for h in r.get("provision_holdings", []):
            for sec in base_section(h.get("provision", "")):
                idx[sec].append({
                    "case_id": r["case_id"], "title": r["title"], "court_type": r["court_type"],
                    "date": r["date"], "provision_cited_as": h.get("provision"),
                    "provision_version": h.get("provision_version"),
                    "issue_node": h.get("issue_node", []),
                    "holding_type": h.get("holding_type"),
                    "interpretation_type": h.get("interpretation_type"),
                    "holding": h.get("holding"),
                })
    out = {}
    def secnum(s):
        m = re.match(r"s\.?(\d+)", s)
        return (int(m.group(1)) if m else 999, s)
    for sec in sorted(idx, key=secnum):
        entries = sorted(idx[sec], key=lambda e: e["date"])
        ratios = [e for e in entries if e["holding_type"] == "ratio"]
        versions = sorted({e["provision_version"] for e in entries if e["provision_version"]})
        out[sec] = {
            "n_holdings": len(entries), "n_ratio": len(ratios),
            "cases": sorted({e["case_id"] for e in entries}),
            "versions_applied": versions,
            "holdings_chronological": entries,
        }
    return out

# ---------------------------------------------------------------- issue_matrix
COURT_RANK = {"SC": 3, "HC-DB": 2, "HC-SB": 1, "HC": 1}
def weight(r):
    base = COURT_RANK.get(r.get("court_type"), 0) * 10
    if r.get("court_type") != "SC":
        base = COURT_RANK.get(r.get("bench_type"), COURT_RANK.get("HC", 1)) * 10
    else:
        base = 30
    base += (r.get("bench_strength") or 1)
    if r.get("reportable"): base += 2
    return base

def build_issue_matrix(recs):
    by_issue = defaultdict(list)
    for r in recs:
        nodes = set()
        for h in r.get("provision_holdings", []):
            nodes.update(h.get("issue_node", []))
        for rt in r.get("ratio", []):
            if rt.get("issue_node"): nodes.add(rt["issue_node"])
        for n in nodes:
            by_issue[n].append(r)
    out = {}
    for node in sorted(by_issue):
        cases = by_issue[node]
        ranked = sorted(cases, key=lambda r: (weight(r), r.get("date", "")), reverse=True)
        leading = ranked[0]
        # is there an HC split? collect ratio propositions on this node
        props = []
        for r in cases:
            for rt in r.get("ratio", []):
                if rt.get("issue_node") == node:
                    props.append({"case_id": r["case_id"], "scope": rt.get("scope"),
                                  "novelty": rt.get("novelty"), "proposition": rt.get("proposition"),
                                  "conflicts_with": rt.get("conflicts_with", [])})
        split = any(rt.get("conflicts_with") for r in cases for rt in r.get("ratio", [])
                    if rt.get("issue_node") == node and rt.get("conflicts_with"))
        out[node] = {
            "n_cases": len(cases),
            "leading_case": {"case_id": leading["case_id"], "title": leading["title"],
                             "court_type": leading["court_type"], "date": leading["date"]},
            "line_of_authority": [{"case_id": r["case_id"], "title": r["title"],
                                   "court_type": r["court_type"], "date": r["date"],
                                   "outcome_for": r.get("outcome_for")}
                                  for r in sorted(cases, key=lambda r: r.get("date", ""))],
            "propositions": props,
            "split_flag": split,
        }
    return out

# ---------------------------------------------------------------- citation_graph
def build_citation_graph(recs):
    # corpus index for in-set matching
    by_docid = {r["docid"]: r["case_id"] for r in recs}
    by_name = {norm_name(r["title"]): r["case_id"] for r in recs}
    authority_hits = defaultdict(lambda: {"cite": "", "court": "", "treatments": Counter(),
                                          "cited_by": [], "on_issues": Counter()})
    edges = []
    in_corpus_indeg = Counter()
    for r in recs:
        for a in r.get("authorities", []):
            key = norm_name(a.get("name"))
            rec = authority_hits[key]
            rec["display"] = a.get("name")
            rec["cite"] = rec["cite"] or a.get("cite", "")
            rec["court"] = rec["court"] or a.get("court", "")
            rec["treatments"][a.get("treatment", "referred")] += 1
            rec["cited_by"].append({"case_id": r["case_id"], "treatment": a.get("treatment"),
                                    "on_issue": a.get("on_issue")})
            if a.get("on_issue"): rec["on_issues"][a["on_issue"]] += 1
            # in-corpus edge?
            tgt = a.get("docid") and by_docid.get(a["docid"]) or by_name.get(key)
            edges.append({"from": r["case_id"], "to_name": a.get("name"),
                          "to_case_id": tgt, "treatment": a.get("treatment"),
                          "on_issue": a.get("on_issue"), "in_corpus": bool(tgt)})
            if tgt and tgt != r["case_id"]:
                in_corpus_indeg[tgt] += 1
    # recurring authority backbone (cited by >=2 corpus cases)
    backbone = []
    for key, rec in authority_hits.items():
        n = len(rec["cited_by"])
        if n >= 2:
            backbone.append({"authority": rec["display"], "cite": rec["cite"], "court": rec["court"],
                             "times_cited": n,
                             "treatments": dict(rec["treatments"]),
                             "on_issues": dict(rec["on_issues"]),
                             "cited_by": rec["cited_by"]})
    backbone.sort(key=lambda x: -x["times_cited"])
    # per-record in-corpus in/out degree
    indeg = {r["case_id"]: in_corpus_indeg.get(r["case_id"], 0) for r in recs}
    return {
        "n_records": len(recs),
        "n_authority_edges": len(edges),
        "recurring_authorities": backbone,
        "in_corpus_in_degree": dict(sorted(indeg.items(), key=lambda x: -x[1])),
        "edges": edges,
    }

def main():
    recs = load_records()
    pi = build_provision_index(recs)
    im = build_issue_matrix(recs)
    cg = build_citation_graph(recs)
    json.dump(pi, open(os.path.join(HERE, "provision_index.json"), "w"), indent=2, ensure_ascii=False)
    json.dump(im, open(os.path.join(HERE, "issue_matrix.json"), "w"), indent=2, ensure_ascii=False)
    json.dump(cg, open(os.path.join(HERE, "citation_graph.json"), "w"), indent=2, ensure_ascii=False)
    print(f"corpus: {len(recs)} records ({sum(1 for r in recs if r['court_type']=='SC')} SC, "
          f"{sum(1 for r in recs if r['court_type']!='SC')} HC)")
    print(f"provision_index.json : {len(pi)} provisions")
    print(f"issue_matrix.json    : {len(im)} issue-nodes")
    print(f"citation_graph.json  : {cg['n_authority_edges']} edges, "
          f"{len(cg['recurring_authorities'])} recurring authorities")
    print("\n-- provisions --")
    for sec, v in pi.items():
        print(f"  {sec:10s} {v['n_holdings']:2d} holdings ({v['n_ratio']} ratio) across {len(v['cases'])} cases {v['versions_applied']}")
    print("\n-- issue-nodes (leading case) --")
    for node, v in im.items():
        print(f"  {node:22s} {v['n_cases']} cases  lead={v['leading_case']['case_id']} ({v['leading_case']['court_type']}){' SPLIT' if v['split_flag'] else ''}")
    print("\n-- recurring authority backbone --")
    for b in cg["recurring_authorities"]:
        print(f"  {b['times_cited']}x  {b['authority'][:52]:52s} {dict(b['treatments'])}")

if __name__ == "__main__":
    main()
