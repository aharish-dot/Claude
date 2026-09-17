"""Tiny JSONL ledger keyed by source_file.

One record per input PDF tracking case_id + status through the pipeline
(queued -> extracted -> prepared -> authored / needs-fix). It is what makes a
session resumable: outputs live on disk, progress lives here, so a run can stop
and continue (or survive a context compaction) without redoing work.
"""
from __future__ import annotations

import json

from scjlib import common as C


def load() -> list[dict]:
    if not C.LEDGER.exists():
        return []
    recs = []
    for line in C.LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            recs.append(json.loads(line))
    return recs


def save(recs: list[dict]) -> None:
    C.ensure_dirs()
    C.LEDGER.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs),
        encoding="utf-8",
    )


def by_source(recs) -> dict:
    return {r["source_file"]: r for r in recs}


def upsert(recs: list[dict], rec: dict) -> list[dict]:
    idx = by_source(recs)
    if rec["source_file"] in idx:
        idx[rec["source_file"]].update(rec)
    else:
        recs.append(rec)
    return recs


def max_id_num(recs, prefix: str) -> int:
    nums = []
    for r in recs:
        cid = r.get("case_id", "")
        if cid.startswith(prefix + "-"):
            tail = cid[len(prefix) + 1:]
            if tail.isdigit():
                nums.append(int(tail))
    return max(nums) if nums else 0


def fmt_id(prefix: str, n: int, width: int = 4) -> str:
    return f"{prefix}-{n:0{width}d}"
