#!/usr/bin/env python3
"""Find duplicate judgments the docket-dedup missed, in the corpus and the queue.

Claude-owned diagnostic (kept out of tools/). READ-ONLY: it never deletes or
moves anything — it writes a JSON report and prints a summary. Deletion/retirement
is a separate, confirmed step.

Why it exists: tools/prepare_next_scj.py builds its docket needle as "No. <n> of
<yr>" (singular). Connected petitions are often written "Nos. 16147 of 2009 and
16149 of 2009" (plural, multi-docket), so "No. 16147" is not a substring of "Nos.
16147" and the twin is claimed as a fresh case (e.g. SCJ-707 duplicated SCJ-225).

This scanner keys on the robust signal instead: every "<n> of <yyyy>" docket
number appearing anywhere in a case's docket field OR its source filename. A queue
PDF whose docket number is already owned by a corpus case is a duplicate; two
corpus cases sharing a docket number are the same judgment under two ids. A softer
secondary signal (same date + coram + lead-party token) is reported separately.

Usage:
    python claude_tools/dupscan.py                       # scan corpus + queue
    python claude_tools/dupscan.py --out <path.json>
"""
from __future__ import annotations
import argparse, json, os, re, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "supply-code")
JSON_DIR = os.path.join(SC, "summaries", "json")
STATE = os.path.join(SC, "state", "index.json")
QUEUE_STATS = os.path.join(SC, "input", "input_pdf_stats.json")

DOCKET_RE = re.compile(r"(\d{1,7})\s+of\s+(\d{4})")          # "16147 of 2009"
FN_DOCKET_RE = re.compile(r"(\d{1,7})_(\d{4})(?:\.pdf)?$", re.I)  # WRIC(A)_16147_2009.pdf


def docket_nums(text: str) -> set[tuple[str, str]]:
    return {(m.group(1), m.group(2)) for m in DOCKET_RE.finditer(text or "")}


def fn_docket(name: str) -> tuple[str, str] | None:
    m = FN_DOCKET_RE.search(os.path.splitext(os.path.basename(name or ""))[0] + ".pdf")
    return (m.group(1), m.group(2)) if m else None


def norm_party(title: str) -> str:
    """First distinctive party token, lowercased (skip M/s, Smt., etc.)."""
    t = re.sub(r"(?i)\b(m/?s\.?|messrs|smt\.?|shri|sri|the)\b", " ", title or "")
    t = re.sub(r"[^A-Za-z0-9 ]", " ", t)
    for w in t.split():
        if len(w) > 3:
            return w.lower()
    return (t.strip().split() or [""])[0].lower()


def load_corpus():
    cases = []
    for f in sorted(glob.glob(os.path.join(JSON_DIR, "SCJ-*.json"))):
        try:
            c = json.load(open(f, encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        cases.append(c)
    # source_basename per case (adds the file's own docket number)
    src = {}
    if os.path.exists(STATE):
        st = json.load(open(STATE, encoding="utf-8"))
        for e in st.get("cases", []):
            src[e.get("case_id")] = e.get("source_basename", "")
    return cases, src


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(SC, "input", "dup_scan_report.json"))
    args = ap.parse_args()

    cases, src = load_corpus()
    owner = collections.defaultdict(set)     # (num,year) -> {case_id}
    meta = {}
    for c in cases:
        cid = c.get("case_id")
        nums = docket_nums(c.get("docket", ""))
        fb = src.get(cid, "")
        fd = fn_docket(fb)
        if fd:
            nums.add(fd)
        for k in nums:
            owner[k].add(cid)
        cor = c.get("coram", "")
        if isinstance(cor, list):
            cor = ", ".join(str(x) for x in cor)
        meta[cid] = {"title": c.get("title", ""), "date": c.get("date_of_judgment", ""),
                     "coram": str(cor), "docket_nums": sorted(nums)}

    # 1) internal duplicate groups: a docket number owned by >1 case id
    groups = {}
    for k, cids in owner.items():
        if len(cids) > 1:
            key = tuple(sorted(cids))
            groups.setdefault(key, set()).update([f"{n} of {y}" for (n, y) in [k]])
    internal = []
    for cids, shared in sorted(groups.items(), key=lambda x: x[0]):
        internal.append({
            "case_ids": list(cids),
            "shared_dockets": sorted(shared),
            "titles": {cid: meta[cid]["title"] for cid in cids},
        })

    # 2) secondary signal: same date + coram + lead party, different id, no docket overlap
    sig = collections.defaultdict(list)
    for cid, m in meta.items():
        if m["date"] and m["coram"]:
            sig[(m["date"], m["coram"].strip().lower(), norm_party(m["title"]))].append(cid)
    soft = []
    already = {frozenset(g["case_ids"]) for g in internal}
    for k, cids in sig.items():
        if len(cids) > 1 and frozenset(cids) not in already:
            soft.append({"date": k[0], "coram": k[1], "party": k[2], "case_ids": sorted(cids),
                         "titles": {cid: meta[cid]["title"] for cid in cids}})

    # 3) queue coverage: queue PDF whose docket number is already owned by a case
    covered, queue_n = [], 0
    if os.path.exists(QUEUE_STATS):
        qs = json.load(open(QUEUE_STATS, encoding="utf-8"))
        for f in qs.get("files", []):
            queue_n += 1
            path = f.get("path", "")
            fd = fn_docket(path)
            if fd and fd in owner:
                covered.append({"file": path, "docket": f"{fd[0]} of {fd[1]}",
                                "pages": f.get("page_count"),
                                "covered_by": sorted(owner[fd])})

    report = {
        "corpus_cases": len(cases),
        "queue_files": queue_n,
        "internal_duplicate_groups": internal,
        "internal_duplicate_group_count": len(internal),
        "soft_duplicate_candidates": soft,
        "soft_duplicate_candidate_count": len(soft),
        "queue_files_already_in_corpus": covered,
        "queue_covered_count": len(covered),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(report, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(args.out, "a").write("\n")

    print(f"corpus cases: {len(cases)} | queue files: {queue_n}")
    print(f"internal duplicate groups (share a docket number): {len(internal)}")
    for g in internal[:20]:
        print(f"  {', '.join(g['case_ids'])}  shared {g['shared_dockets']}")
    print(f"soft duplicate candidates (same date+coram+party): {len(soft)}")
    for g in soft[:20]:
        print(f"  {', '.join(g['case_ids'])}  {g['date']} · {g['party']}")
    print(f"queue PDFs already covered by a corpus case: {len(covered)}")
    for g in covered[:25]:
        print(f"  {g['file']}  ({g['docket']}) -> {', '.join(g['covered_by'])}")
    print(f"\nreport: {os.path.relpath(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
