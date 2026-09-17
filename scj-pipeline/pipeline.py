#!/usr/bin/env python3
"""SCJ greenfield summarization pipeline (no external API).

The deterministic steps below are all that Python does. The legal authoring
happens inside the chat session: Claude reads each lean extract and fills the
skeleton (see prompts/authoring_card.md). Keeping the model's job to just the
analytical fields -- over lean, de-boilerplated text, with metadata pre-filled --
is what lets one session finish >=20 cases.

Typical session:
    python pipeline.py prep --next 20      # extract + stencil 20 pending cases
    # ... Claude authors data/out/*.json following data/work/WORKLIST.md ...
    python pipeline.py validate --all      # gate the results, update the ledger
    python pipeline.py report              # throughput + context-budget summary
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scjlib import common as C          # noqa: E402
from scjlib import ledger as L          # noqa: E402
from scjlib import extract as E         # noqa: E402
from scjlib import stencil as S         # noqa: E402
from scjlib import validate as V        # noqa: E402


def _extract_for(rec: dict) -> dict:
    ex = E.extract_one(rec["source_path"])
    cid = rec["case_id"]
    exj = C.EXTRACTS / f"{cid}.extract.json"
    C.write_json(exj, ex)
    C.write_text(C.EXTRACTS / f"{cid}.txt", ex["lean_text"])
    rec["extract"] = str(exj)
    rec["docket"] = ex["raw_meta"].get("docket", "")
    rec["updated"] = C.now_iso()
    if rec.get("status") in (None, "queued"):
        rec["status"] = "extracted"
    return ex


def cmd_ids(args) -> int:
    C.ensure_dirs()
    recs = L.load()
    idx = L.by_source(recs)
    n = L.max_id_num(recs, args.prefix)
    if args.start:
        n = max(n, args.start - 1)
    pdfs = sorted(C.PDFS.glob("*.pdf"))
    assigned = 0
    for p in pdfs:
        if p.name in idx and idx[p.name].get("case_id"):
            continue
        n += 1
        L.upsert(recs, {"source_file": p.name, "source_path": str(p),
                        "case_id": L.fmt_id(args.prefix, n), "status": "queued",
                        "updated": C.now_iso()})
        idx = L.by_source(recs)
        assigned += 1
    L.save(recs)
    print(f"[ids] {len(pdfs)} pdf(s) in data/pdfs; assigned {assigned} new id(s); ledger now {len(recs)}")
    if args.list:
        for r in recs:
            print(f"  {r.get('case_id', '?'):12} {r.get('status', '?'):10} {r['source_file']}")
    return 0


def cmd_extract(args) -> int:
    C.ensure_dirs()
    recs = L.load()
    done = 0
    for r in recs:
        if args.case and r.get("case_id") != args.case:
            continue
        if not r.get("source_path"):
            continue
        if not args.force and not args.case and r.get("status") not in ("queued", "extracted"):
            continue
        _extract_for(r)
        done += 1
        print(f"[extract] {r['case_id']} <- {r['source_file']}  ({r.get('docket', '')})")
    L.save(recs)
    print(f"[extract] processed {done} case(s)")
    return 0


def _write_worklist_md(items) -> None:
    lines = ["# SCJ authoring worklist", "",
             f"{len(items)} case(s) prepared. Read `prompts/authoring_card.md` ONCE, then for each item:",
             "1. Read the lean text file.",
             "2. Edit the skeleton JSON, filling every analytical field per the card.",
             "3. When all are done, run `python pipeline.py validate --all`.", ""]
    for i, it in enumerate(items, 1):
        lines += [f"## {i}. {it['case_id']}   {it.get('docket', '')}".rstrip(),
                  f"- read:  `{it['lean_txt']}`  (~{it['est_tokens']} tokens)",
                  f"- write: `{it['skeleton']}`", ""]
    C.write_text(C.WORK / "WORKLIST.md", "\n".join(lines))


def cmd_prep(args) -> int:
    C.ensure_dirs()
    cmd_ids(argparse.Namespace(prefix=args.prefix, start=args.start, list=False))
    recs = L.load()
    pending = [r for r in recs if r.get("status") in ("queued", "extracted")][:args.next]
    items = []
    for r in pending:
        ex = _extract_for(r)
        cid = r["case_id"]
        outp = C.OUT / f"{cid}.json"
        if not outp.exists() or args.force:
            C.write_json(outp, S.build_skeleton(ex, cid, default_court=args.court))
        r["output"] = str(outp)
        r["status"] = "prepared"
        r["updated"] = C.now_iso()
        items.append({"case_id": cid, "lean_txt": str(C.EXTRACTS / f"{cid}.txt"),
                      "skeleton": str(outp), "docket": r.get("docket", ""),
                      "est_tokens": ex["est_tokens"]})
    L.save(recs)
    C.write_json(C.WORK / "worklist.json", {"count": len(items), "items": items})
    _write_worklist_md(items)
    tot = sum(i["est_tokens"] for i in items)
    per = tot // max(len(items), 1)
    print(f"[prep] prepared {len(items)} case(s); input ~{tot} tokens total (~{per}/case)")
    print(f"[prep] worklist -> {C.WORK / 'WORKLIST.md'}")
    return 0


def cmd_validate(args) -> int:
    recs = L.load()
    idx = {r.get("case_id"): r for r in recs}
    if args.case:
        outs = [C.OUT / f"{args.case}.json"]
    else:
        outs = sorted(C.OUT.glob("*.json"))
    npass = nfail = 0
    for o in outs:
        if not o.exists():
            print(f"[validate] missing {o}")
            nfail += 1
            continue
        doc = C.read_json(o)
        errs, warns = V.validate_doc(doc)
        cid = doc.get("case_id", o.stem)
        if errs:
            nfail += 1
        else:
            npass += 1
        print(f"[{'PASS' if not errs else 'FAIL'}] {cid}  errors={len(errs)} warnings={len(warns)}")
        for e in errs:
            print(f"    ! {e}")
        if args.verbose:
            for w in warns:
                print(f"    ~ {w}")
        if cid in idx:
            idx[cid]["status"] = "authored" if not errs else "needs-fix"
            idx[cid]["qa_errors"] = len(errs)
            idx[cid]["qa_warnings"] = len(warns)
            idx[cid]["updated"] = C.now_iso()
    L.save(recs)
    print(f"[validate] pass={npass} fail={nfail}")
    return 1 if nfail else 0


def cmd_report(args) -> int:
    recs = L.load()
    counts = Counter(r.get("status", "?") for r in recs)
    print("== Ledger ==")
    for k in ("queued", "extracted", "prepared", "authored", "needs-fix"):
        if k in counts:
            print(f"  {k:10} {counts[k]}")
    print(f"  {'total':10} {len(recs)}")
    ests = []
    for r in recs:
        t = C.EXTRACTS / f"{r.get('case_id')}.txt"
        if t.exists():
            ests.append(C.est_tokens(C.read_text(t)))
    if ests:
        avg = sum(ests) // len(ests)
        print("== Context budget (lean extracts) ==")
        print(f"  cases with extract : {len(ests)}")
        print(f"  avg input tokens   : {avg}/case  (min {min(ests)}, max {max(ests)})")
        print(f"  20-case session est: input ~{avg * 20} + output ~{2000 * 20} = ~{avg * 20 + 40000} tokens")
    return 0


def cmd_selftest(args) -> int:
    C.ensure_dirs()
    pdfs = sorted(C.PDFS.glob("*.pdf"))
    if not pdfs:
        print("[selftest] put a PDF in data/pdfs/ first")
        return 1
    ex = E.extract_one(pdfs[0])
    print(f"[selftest] {pdfs[0].name}: pages={ex['page_count']} chars={ex['char_count']} "
          f"lean={ex['lean_char_count']} (~{ex['est_tokens']} tok) engine={ex['engine']}")
    print(f"[selftest] meta: {json.dumps(ex['raw_meta'], ensure_ascii=False)}")
    errs, _ = V.validate_doc(S.build_skeleton(ex, "SCJ-0000"))
    print(f"[selftest] skeleton correctly fails validation: {'yes' if errs else 'NO (bug)'} "
          f"({len(errs)} blocking errors as expected)")
    print("[selftest] OK")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="SCJ summarization pipeline (no external API).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ids", help="scan data/pdfs and assign case_ids")
    p.add_argument("--prefix", default="SCJ")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--list", action="store_true")

    p = sub.add_parser("extract", help="PDF -> lean extract")
    p.add_argument("--case")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("prep", help="ids + extract + stencil for the next N pending")
    p.add_argument("--prefix", default="SCJ")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--next", type=int, default=20)
    p.add_argument("--court", default="", help="default court when not detected in text")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("validate", help="gate data/out/*.json")
    p.add_argument("--case")
    p.add_argument("--all", action="store_true")
    p.add_argument("--verbose", "-v", action="store_true")

    sub.add_parser("report", help="ledger + context-budget summary")
    sub.add_parser("selftest", help="smoke test on the first pdf in data/pdfs")

    args = ap.parse_args()
    fn = {"ids": cmd_ids, "extract": cmd_extract, "prep": cmd_prep,
          "validate": cmd_validate, "report": cmd_report, "selftest": cmd_selftest}[args.cmd]
    sys.exit(fn(args) or 0)


if __name__ == "__main__":
    main()
