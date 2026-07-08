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
# (6) Composite leading-case score: court rank is no longer the sole factor, so the
# lone SC record no longer auto-"leads" nodes it does not actually anchor. Score =
# court-rank base + bench_strength + reportable + in-corpus in-degree (anchor metric)
# + issue-specific novelty. `apex_case` (highest court) is reported alongside so the
# binding hierarchy is never lost.
COURT_BASE = {"SC": 30, "HC-DB": 20, "HC-SB": 10, "HC": 10}
NOVELTY = {"new": 6, "settles": 6, "settles-split": 6, "settles-explains": 5,
           "extends": 4, "affirms": 3, "applies": 2, "explains": 1, "conflicts": 0}

def court_base(r):
    return COURT_BASE.get(r.get("court_type") if r.get("court_type") == "SC" else r.get("bench_type"),
                          COURT_BASE.get("HC", 10))

def novelty_on(r, node):
    vals = [NOVELTY.get(rt.get("novelty"), 0) for rt in r.get("ratio", []) if rt.get("issue_node") == node]
    return max(vals) if vals else 0

def composite(r, node, indeg):
    return (court_base(r) + (r.get("bench_strength") or 1) + (2 if r.get("reportable") else 0)
            + 5 * indeg.get(r["case_id"], 0) + novelty_on(r, node))

def build_issue_matrix(recs, indeg):
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
        ranked = sorted(cases, key=lambda r: (composite(r, node, indeg), r.get("date", "")), reverse=True)
        leading = ranked[0]
        apex = sorted(cases, key=lambda r: (court_base(r), r.get("date", "")), reverse=True)[0]
        # One detail card per case in the line of authority: prefer the case's ratio
        # on this node; fall back to its provision_holding(s) on the node so every
        # case in the line has a card (fixes nodes carried only via holdings).
        contribs = []
        for r in sorted(cases, key=lambda r: r.get("date", "")):
            node_ratios = [rt for rt in r.get("ratio", []) if rt.get("issue_node") == node]
            node_holds = [h for h in r.get("provision_holdings", []) if node in h.get("issue_node", [])]
            if node_ratios:
                for rt in node_ratios:
                    contribs.append({"case_id": r["case_id"], "source": "ratio",
                                     "scope": rt.get("scope"), "novelty": rt.get("novelty"),
                                     "text": rt.get("proposition"),
                                     "conflicts_with": rt.get("conflicts_with", [])})
            else:
                for h in node_holds:
                    contribs.append({"case_id": r["case_id"], "source": "holding",
                                     "provision": h.get("provision"), "holding_type": h.get("holding_type"),
                                     "text": h.get("holding")})
        split = any(rt.get("conflicts_with") for r in cases for rt in r.get("ratio", [])
                    if rt.get("issue_node") == node and rt.get("conflicts_with"))
        out[node] = {
            "n_cases": len(cases),
            "leading_case": {"case_id": leading["case_id"], "title": leading["title"],
                             "court_type": leading["court_type"], "date": leading["date"],
                             "score": composite(leading, node, indeg)},
            "apex_case": {"case_id": apex["case_id"], "title": apex["title"],
                          "court_type": apex["court_type"], "date": apex["date"]},
            "ranking": [{"case_id": r["case_id"], "court_type": r["court_type"],
                         "score": composite(r, node, indeg), "in_degree": indeg.get(r["case_id"], 0),
                         "novelty": novelty_on(r, node)}
                        for r in ranked],
            "line_of_authority": [{"case_id": r["case_id"], "title": r["title"],
                                   "court_type": r["court_type"], "date": r["date"],
                                   "outcome_for": r.get("outcome_for")}
                                  for r in sorted(cases, key=lambda r: r.get("date", ""))],
            "contributions": contribs,
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
    cg = build_citation_graph(recs)                       # first -> in-corpus in-degree
    im = build_issue_matrix(recs, cg["in_corpus_in_degree"])
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
    print("\n-- issue-nodes (leading = composite score; apex = highest court) --")
    for node, v in im.items():
        lead, apex = v['leading_case'], v['apex_case']
        # only surface apex when it outranks the leader on court hierarchy (SC over HC)
        show = COURT_BASE.get(apex['court_type'], 0) > COURT_BASE.get(lead['court_type'], 0)
        same = f"  apex={apex['case_id']}({apex['court_type']})" if show else ""
        print(f"  {node:22s} {v['n_cases']} cases  lead={lead['case_id']}({lead['court_type']},s{lead['score']}){same}{' SPLIT' if v['split_flag'] else ''}")
    print("\n-- recurring authority backbone --")
    for b in cg["recurring_authorities"]:
        print(f"  {b['times_cited']}x  {b['authority'][:52]:52s} {dict(b['treatments'])}")

if __name__ == "__main__":
    main()
