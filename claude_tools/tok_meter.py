#!/usr/bin/env python3
"""Token-expense meter for the Claude SCJ pipeline.

Estimates (not exact model tokens) the token cost of each pipeline step by
measuring the bytes/words that cross into or out of the model's context at
that step, and appends one JSON line per measurement to a ledger so we can
see where the tokens go and decide what to cut.

est_tokens uses tiktoken cl100k_base when available (a rough proxy for the
Claude tokenizer); otherwise it falls back to len(chars)/4.0. The method is
recorded on every row so mixed-method ledgers stay honest.

Usage:
  tok_meter.py log  <case_id> <step> <in|out> <label> <path>   # measure a file
  tok_meter.py note <case_id> <step> <in|out> <label> <chars>  # record a raw char count
  tok_meter.py report [<case_id>]                              # per-step + total table

Steps are free-form strings; the pipeline uses: claim, read_extract, read_refs,
author_json, self_check, finalize.
"""
from __future__ import annotations
import json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "claude_tools", "token_ledger.jsonl")

try:
    import tiktoken  # type: ignore
    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:  # pragma: no cover - tiktoken usually absent
    _ENC = None


def est_tokens(text):
    if _ENC is not None:
        return len(_ENC.encode(text)), "tiktoken:cl100k_base"
    return int(round(len(text) / 4.0)), "chars/4"


def _row(case_id, step, kind, label, chars, words, text=None):
    if text is not None:
        toks, method = est_tokens(text)
    else:
        toks, method = int(round(chars / 4.0)), "chars/4"
    return {"ts": round(time.time(), 3), "case_id": case_id, "step": step,
            "kind": kind, "label": label, "chars": chars, "words": words,
            "est_tokens": toks, "method": method}


def _append(row):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def cmd_log(case_id, step, kind, label, path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    row = _row(case_id, step, kind, label, len(text), len(text.split()), text)
    _append(row)
    print(f"logged {case_id} {step} {kind} {label}: {row['chars']} chars, "
          f"~{row['est_tokens']} tokens ({row['method']})")


def cmd_note(case_id, step, kind, label, chars):
    chars = int(chars)
    row = _row(case_id, step, kind, label, chars, 0)
    _append(row)
    print(f"noted {case_id} {step} {kind} {label}: {chars} chars, ~{row['est_tokens']} tokens")


def cmd_report(case_id=None):
    if not os.path.exists(LEDGER):
        print("(no ledger yet)")
        return
    rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]
    if case_id:
        rows = [r for r in rows if r.get("case_id") == case_id]
    if not rows:
        print("(no rows)")
        return
    by_step = {}
    for r in rows:
        k = (r["case_id"], r["step"], r["kind"])
        by_step.setdefault(k, {"chars": 0, "tokens": 0})
        by_step[k]["chars"] += r["chars"]
        by_step[k]["tokens"] += r["est_tokens"]
    print(f"{'case':10} {'step':14} {'kind':4} {'chars':>8} {'~tokens':>8}")
    total = 0
    for (cid, step, kind) in sorted(by_step):
        v = by_step[(cid, step, kind)]
        total += v["tokens"]
        print(f"{cid:10} {step:14} {kind:4} {v['chars']:>8} {v['tokens']:>8}")
    print(f"{'':10} {'TOTAL':14} {'':4} {'':>8} {total:>8}")


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    c = a[0]
    if c == "log" and len(a) == 6:
        return cmd_log(*a[1:])
    if c == "note" and len(a) == 6:
        return cmd_note(*a[1:])
    if c == "report":
        return cmd_report(a[1] if len(a) > 1 else None)
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
