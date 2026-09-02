#!/usr/bin/env python3
"""Append-only metrics for the SCJ-488–537 pipeline review.

After 50 finalized cases, read:
  supply-code/sessions/2026-09-02-review-488-537.md
  python tools/log_scj_review.py --summary
"""
from __future__ import annotations

import argparse, json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "supply-code")
DIR = os.path.join(SC, "tmp", "pipeline_review")
CONFIG = os.path.join(DIR, "config.json")
METRICS = os.path.join(DIR, "metrics.jsonl")
STATE = os.path.join(SC, "state", "index.json")
SESSION = "supply-code/sessions/2026-09-02-review-488-537.md"

REVIEW_FROM = 488
REVIEW_N = 50
REVIEW_UNTIL = REVIEW_FROM + REVIEW_N - 1  # SCJ-537
REVIEW_ID = "2026-09-02-68-bill-relegate"


def _seq(cid: str) -> int:
    try:
        return int(str(cid).split("-")[1])
    except (IndexError, ValueError, AttributeError):
        return 0


def in_batch(cid: str) -> bool:
    n = _seq(cid)
    return REVIEW_FROM <= n <= REVIEW_UNTIL


def ensure_dir():
    os.makedirs(DIR, exist_ok=True)
    cfg = {
        "review_id": REVIEW_ID,
        "from_seq": REVIEW_FROM,
        "until_seq": REVIEW_UNTIL,
        "target_n": REVIEW_N,
        "note": SESSION,
        "status": "in_progress",
        "changes": [
            "6.8-assessment-hearing stencil LIVE (recovery citation, no hearing, deposit)",
            "BILL+RELEGATE cues: wrong bill, electricity amount due, unpaid dues, recovery citation; should file a challenge / can get the bill corrected / if the petitioner approaches",
            "GRANT veto: we intervene / forthwith comply / petition allowed (SCJ-411)",
            "stencil write fail demotes to short/full (no retry)",
            "citation_count = max(ik, text) so PDFs can leave short-uncited",
        ],
    }
    # Refresh if missing or still on the previous batch id.
    old = {}
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG, encoding="utf-8") as f:
                old = json.load(f)
        except (OSError, json.JSONDecodeError):
            old = {}
    if old.get("review_id") != REVIEW_ID:
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
            f.write("\n")


def append(event: dict) -> None:
    cid = event.get("case_id") or event.get("cid")
    if not cid or not in_batch(cid):
        return
    ensure_dir()
    event = dict(event)
    event.setdefault("ts", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    if "cid" in event and "case_id" not in event:
        event["case_id"] = event.pop("cid")
    with open(METRICS, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_events():
    if not os.path.exists(METRICS):
        return []
    out = []
    with open(METRICS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if in_batch(e.get("case_id") or ""):
                out.append(e)
    return out


def merge_cases(events=None):
    """Last-write-wins per case_id, but union coerce lists and keep first authoring."""
    merged = {}
    for e in events if events is not None else load_events():
        cid = e.get("case_id")
        if not cid:
            continue
        cur = merged.setdefault(cid, {"case_id": cid})
        for k, v in e.items():
            if k in ("ts", "event"):
                cur.setdefault("events", []).append(e.get("event") or "")
                continue
            if k == "coerce":
                prev = cur.get("coerce") or []
                extra = v if isinstance(v, list) else ([v] if v else [])
                cur["coerce"] = list(dict.fromkeys([*prev, *[x for x in extra if x]]))
                continue
            if v is None or v == "":
                continue
            cur[k] = v
    return merged


def _truthy(v) -> bool:
    return v in (True, 1, "1", "true", "True")


def summarize() -> int:
    merged = merge_cases()
    rows = [merged[k] for k in sorted(merged, key=_seq)]
    n = len(rows)
    ok = [r for r in rows if _truthy(r.get("ok"))]
    fail = [r for r in rows if r.get("ok") in (False, 0, "0", "false", "False")]
    by = {}
    for r in rows:
        by.setdefault(r.get("authoring") or "?", []).append(r)
    coerce_n = sum(1 for r in rows if r.get("coerce"))
    safety_n = sum(1 for r in rows if _truthy(r.get("safety_finalize")))
    demote_n = sum(1 for r in rows if _truthy(r.get("demoted")))
    cites_n = sum(1 for r in rows if int(r.get("citations") or 0) > 0)
    text_n = sum(1 for r in rows if int(r.get("text_citations") or 0) > 0)
    ik_n = sum(1 for r in rows if int(r.get("ik_citations") or 0) > 0)
    print(f"pipeline review  SCJ-{REVIEW_FROM:03d}–SCJ-{REVIEW_UNTIL:03d}  "
          f"logged={n}/{REVIEW_N}")
    print(f"  ok={len(ok)} fail={len(fail)} coerce_any={coerce_n} "
          f"safety_finalize={safety_n} demoted={demote_n}")
    print(f"  citations>0={cites_n}  ik>0={ik_n}  text>0={text_n}")
    for auth in ("stencil", "short", "full", "?"):
        grp = by.get(auth) or []
        if not grp:
            continue
        el = [int(r["elapsed"]) for r in grp if str(r.get("elapsed", "")).isdigit()]
        avg = int(sum(el) / len(el)) if el else None
        gates = {}
        for r in grp:
            g = r.get("gate") or ""
            if g:
                gates[g] = gates.get(g, 0) + 1
        print(f"  {auth:8} n={len(grp):2}  avg_s={avg}  gates={gates or '-'}")
        if auth == "stencil":
            fam = {}
            oc, sig = {}, {}
            for r in grp:
                f = r.get("family") or "?"
                fam[f] = fam.get(f, 0) + 1
                o = r.get("outcome") or ""
                s = r.get("significance") or ""
                if o:
                    oc[o] = oc.get(o, 0) + 1
                if s:
                    sig[s] = sig.get(s, 0) + 1
            print(f"           families={fam or '-'}")
            print(f"           outcome={oc or '-'}  significance={sig or '-'}")
    if n >= REVIEW_N:
        print(f"REVIEW DUE — see {SESSION}")
        print(f"  metrics: {METRICS}")
        print("  python tools/log_scj_review.py --summary")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--cid")
    ap.add_argument("--case_id")
    ap.add_argument("--event", default="loop")
    ap.add_argument("--authoring")
    ap.add_argument("--family", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--pages", default="")
    ap.add_argument("--words", default="")
    ap.add_argument("--citations", default="")
    ap.add_argument("--gate", default="")
    ap.add_argument("--elapsed", default="")
    ap.add_argument("--ok", default="")
    ap.add_argument("--safety_finalize", default="")
    ap.add_argument("--coerce", default="")
    ap.add_argument("--outcome", default="")
    ap.add_argument("--significance", default="")
    ap.add_argument("--grok", default="")
    ap.add_argument("--demoted", default="")
    ap.add_argument("--ik_citations", default="")
    ap.add_argument("--text_citations", default="")
    ap.add_argument("--demoted_from", default="")
    args = ap.parse_args(argv)
    if args.summary:
        return summarize()
    cid = args.case_id or args.cid
    if not cid:
        print("FAILED · need --cid or --summary", file=sys.stderr)
        return 1
    coerce = [x for x in (args.coerce or "").split(";") if x.strip()]
    event = {
        "event": args.event,
        "case_id": cid,
        "authoring": args.authoring or None,
        "family": args.family or None,
        "source": args.source or None,
        "pages": int(args.pages) if str(args.pages).isdigit() else args.pages or None,
        "words": int(args.words) if str(args.words).isdigit() else args.words or None,
        "citations": int(args.citations) if str(args.citations).isdigit() else args.citations or None,
        "gate": args.gate or None,
        "elapsed": int(args.elapsed) if str(args.elapsed).isdigit() else args.elapsed or None,
        "ok": args.ok if args.ok != "" else None,
        "safety_finalize": args.safety_finalize if args.safety_finalize != "" else None,
        "coerce": coerce,
        "outcome": args.outcome or None,
        "significance": args.significance or None,
        "grok": args.grok if args.grok != "" else None,
        "demoted": args.demoted if args.demoted != "" else None,
        "ik_citations": int(args.ik_citations) if str(args.ik_citations).isdigit() else args.ik_citations or None,
        "text_citations": int(args.text_citations) if str(args.text_citations).isdigit() else args.text_citations or None,
        "demoted_from": args.demoted_from or None,
    }
    event = {k: v for k, v in event.items() if v is not None and v != []}
    append(event)
    if args.event == "loop" and args.ok in ("1", "true", "True"):
        n = sum(1 for r in merge_cases().values() if _truthy(r.get("ok")))
        if n == REVIEW_N:
            print(f"REVIEW DUE after {n} cases "
                  f"(SCJ-{REVIEW_FROM:03d}–SCJ-{REVIEW_UNTIL:03d}). "
                  f"See {SESSION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
