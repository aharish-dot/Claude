#!/usr/bin/env python3
"""Coverage-driven selection worklist with a de-duplication (saturation) rule
(improvement 3).

Wave 2 showed that citation-rank is a weak axis for a jurisprudence DB: the lowest-
ranked cases were often the most valuable (anchors, vires, compounding), while mid-
rank cases piled onto already-settled points. So selection is flipped to be gap-
driven: this tool ranks issue-nodes by how UNDER-covered they are and tells you what
kind of case to look for next, applies a de-dup rule so we STOP adding to saturated
nodes (unless a candidate is a higher court, a genuine split, or a new fact-pattern),
surfaces the un-recorded citation backbone (snowball), and flags author/court over-
concentration. Writes selection_worklist.md.

Run after build_aggregation.py.
"""
import json, os, glob
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TAXONOMY = ["126v135", "assessment-126", "mensrea-135", "appeal-127",
            "jurisdiction-145-154", "compounding-152", "natural-justice",
            "provisional-final", "burden-proof", "limitation-56"]

def load(n): return json.load(open(os.path.join(HERE, n)))
def load_records():
    p = glob.glob(os.path.join(HERE, "records", "*.record.json"))
    p += [os.path.join(HERE, f) for f in ("SC-001.record.json", "HC-003.record.json")
          if os.path.exists(os.path.join(HERE, f))]
    return [json.load(open(x)) for x in p]

def saturation(node, im, recs):
    """Classify an issue-node: MISSING / OPEN / THIN / DEVELOPING / SATURATED."""
    entry = im.get(node)
    if not entry:
        return "MISSING", {"n": 0, "courts": 0, "has_sc": False}
    cases = entry["line_of_authority"]
    ids = {c["case_id"] for c in cases}
    by_id = {r["case_id"]: r for r in recs}
    courts = {by_id[c].get("court") for c in ids if c in by_id}
    states = {s for c in ids if c in by_id for s in by_id[c].get("state", [])}
    has_sc = any(by_id[c].get("court_type") == "SC" for c in ids if c in by_id)
    n = len(ids)
    meta = {"n": n, "courts": len(courts), "states": len(states), "has_sc": has_sc}
    if n == 0: return "MISSING", meta
    if n == 1: return "OPEN", meta
    if n == 2: return "THIN", meta
    # de-dup rule: 3+ cases, 2+ courts, and (SC anchor OR 4+ cases) -> saturated
    if n >= 3 and len(courts) >= 2 and (has_sc or n >= 4):
        return "SATURATED", meta
    return "DEVELOPING", meta

def main():
    recs = load_records()
    im = load("issue_matrix.json")
    cg = load("citation_graph.json")
    by_docid = {r["docid"] for r in recs}
    L = []
    def out(s=""): L.append(s)

    out("# Selection worklist (coverage-driven, de-dup)\n")
    out(f"Corpus: {len(recs)} records "
        f"({sum(1 for r in recs if r['court_type']=='SC')} SC, "
        f"{sum(1 for r in recs if r['court_type']!='SC')} HC).\n")

    # 1) issue-node saturation table
    order = {"MISSING": 0, "OPEN": 1, "THIN": 2, "DEVELOPING": 3, "SATURATED": 4}
    rows = [(node, *saturation(node, im, recs)) for node in TAXONOMY]
    rows.sort(key=lambda r: (order[r[1]], -r[2]["n"]))
    out("## 1 · Where to spend the next slots (target the top of this list)\n")
    ACTION = {
        "MISSING": "❗ FIND a case on this node",
        "OPEN": "➕ add 1-2 (any court)",
        "THIN": "➕ add (prefer a different court / an SC anchor)",
        "DEVELOPING": "◦ optional (add only if higher court or new fact-pattern)",
        "SATURATED": "⏹ STOP — skip unless higher court / genuine split / new fact-pattern",
    }
    for node, status, m in rows:
        sc = " · has-SC" if m["has_sc"] else " · NO SC anchor"
        out(f"- `{node}` — {m['n']} case(s), {m['courts']} court(s){sc}  →  **{status}** · {ACTION[status]}")
    out()

    # 2) de-dup guard: nodes we are over-covering
    sat = [node for node, s, m in rows if s == "SATURATED"]
    out("## 2 · De-dup guard (do NOT keep feeding these)\n")
    if sat:
        for node in sat:
            m = dict(saturation(node, im, recs)[1])
            out(f"- `{node}` is SATURATED ({m['n']} cases, {m['courts']} courts) — a new candidate here "
                "earns a slot ONLY if it is a higher court, creates/resolves a split, or adds a new fact-pattern.")
    else:
        out("- (no node is saturated yet)")
    out()

    # 3) snowball: recurring authorities not yet recorded
    out("## 3 · Snowball candidates (un-recorded authorities the corpus leans on)\n")
    reg = json.load(open(os.path.join(HERE, "authority_registry.json")))["authorities"]
    def reg_docid(disp):
        low = disp.lower()
        for e in reg.values():
            if any(a in low for a in e.get("aliases", [])):
                return e.get("docid", "")
        return ""
    for b in cg["recurring_authorities"]:
        d = reg_docid(b["authority"])
        if d and d in by_docid:
            continue  # already a record
        court = b.get("court", "")
        out(f"- **{b['authority']}** — cited {b['times_cited']}× {b['treatments']} "
            f"{'(docid '+d+')' if d else '(docid unknown)'} → {'SC' if 'Supreme' in court else 'HC'} candidate")
    out()

    # 4) concentration warnings (author / court / state)
    out("## 4 · Concentration warnings (diversify)\n")
    authors = Counter(b for r in recs for b in r.get("bench", []))
    courts = Counter(r.get("court") for r in recs if r["court_type"] != "SC")
    states = Counter(s for r in recs for s in r.get("state", []))
    for label, ctr, thr in [("author (judge)", authors, 3), ("HC court", courts, 4), ("state", states, 4)]:
        heavy = [(k, v) for k, v in ctr.most_common() if v >= thr]
        if heavy:
            out(f"- {label}: " + ", ".join(f"{k} ({v})" for k, v in heavy) + " — over-represented; prefer new ones.")
    if not any([[1 for k, v in authors.most_common() if v >= 3]]):
        pass
    out()

    open(os.path.join(HERE, "selection_worklist.md"), "w").write("\n".join(L))
    print("\n".join(L))
    print("\nwrote selection_worklist.md")

if __name__ == "__main__":
    main()
