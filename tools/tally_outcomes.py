#!/usr/bin/env python3
"""Count lean records by outcome, optionally filtered by provision prefix.

Usage:
  python tools/tally_outcomes.py
  python tools/tally_outcomes.py UP-2005::4.4
  python tools/tally_outcomes.py 4.4

A case matches a prefix if any holding_units[].provision contains it
(case-insensitive). New-connection cluster is typically UP-2005::4.4.
Records without outcome (SCJ-001..300) are counted as unlabeled.
"""
from __future__ import annotations

import glob, json, os, re, sys
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..", "supply-code")
SUMM = os.path.join(ROOT, "summaries", "json")
ORDER = ("consumer", "licensee", "alternate_remedy", "pending", "none", "split",
         "unlabeled")


def load_cases():
    out = []
    for path in sorted(glob.glob(os.path.join(SUMM, "*.json"))):
        with open(path, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def matches(c, needle: str) -> bool:
    """Prefix match that does not treat 4.4 as matching 4.44 / 4.49."""
    if not needle:
        return True
    n = needle.lower()
    pat = re.compile(re.escape(n) + r"(?!\d)")
    for hu in c.get("holding_units") or []:
        prov = str(hu.get("provision") or hu.get("clause") or "").lower()
        if pat.search(prov):
            return True
    return False


def main():
    needle = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    cases = load_cases()
    picked = [c for c in cases if matches(c, needle)]
    counts = Counter()
    for c in picked:
        raw = (c.get("outcome") or "").strip().lower()
        counts[raw if raw else "unlabeled"] += 1
    label = f"provision contains {needle!r}" if needle else "all cases"
    print(f"{len(picked)} / {len(cases)} records  ({label})")
    print(f"{'outcome':22} {'n':>5}  {'pct':>6}")
    print("-" * 38)
    total = len(picked) or 1
    for k in ORDER:
        n = counts.get(k, 0)
        if n or k == "unlabeled":
            print(f"{k:22} {n:5d}  {100.0 * n / total:5.1f}%")
    extra = [k for k in counts if k not in ORDER]
    for k in extra:
        n = counts[k]
        print(f"{k:22} {n:5d}  {100.0 * n / total:5.1f}%")
    if needle:
        print()
        print("ids:")
        by = {}
        for c in picked:
            oc = (c.get("outcome") or "unlabeled").strip() or "unlabeled"
            by.setdefault(oc, []).append(c.get("case_id"))
        for oc in list(ORDER) + [k for k in by if k not in ORDER]:
            ids = by.get(oc) or []
            if not ids:
                continue
            print(f"  {oc} ({len(ids)}): {', '.join(ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
