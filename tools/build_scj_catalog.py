#!/usr/bin/env python3
"""Compact provision-key + principle-tag list for the JSON author.

Usage:  python tools/build_scj_catalog.py
Writes  supply-code/jurisprudence/catalog.txt

Grok reads this (~a few KB) instead of grepping 280 JSON files. Rebuild after
each finalized case. Not a substitute for reading the judgment.
"""
import json, glob, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "supply-code")
SUMM = os.path.join(ROOT, "summaries", "json")
OUT = os.path.join(ROOT, "jurisprudence", "catalog.txt")


def main():
    provisions, tags = set(), set()
    for path in glob.glob(os.path.join(SUMM, "SCJ-*.json")):
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        for hu in c.get("holding_units") or []:
            k = (hu.get("provision") or "").strip()
            if k:
                provisions.add(k)
        for t in c.get("principle_tags") or []:
            k = (t.get("tag") or "").strip()
            if k:
                tags.add(k)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lines = [
        "# Reuse these keys when they fit. Do not invent a synonym for an existing tag.",
        "# New kebab-case tags are allowed only when none of these capture the holding.",
        "",
        f"PROVISIONS ({len(provisions)})",
    ]
    lines.extend(sorted(provisions, key=str.lower))
    lines += ["", f"TAGS ({len(tags)})"]
    lines.extend(sorted(tags, key=str.lower))
    lines.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT}: {len(provisions)} provisions, {len(tags)} tags")


if __name__ == "__main__":
    main()
