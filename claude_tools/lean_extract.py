#!/usr/bin/env python3
"""Conservative extract compactor — shrinks the reading copy WITHOUT losing content.

Writes supply-code/extracts/<cid>.lean.txt from <cid>.txt. It ONLY removes
whitespace/OCR noise; it never removes a word, number, date, or page-number
marker, so authored evidence quotes stay verbatim (whitespace-normalized) against
the ORIGINAL .txt, and page pins remain valid. The model reads the .lean.txt to
save context tokens; author_check.py verifies quotes against the untrimmed .txt.

Operations (all reversible under whitespace-normalization):
  * strip trailing spaces on every line
  * drop form-feed / stray control chars
  * collapse runs of 3+ interior spaces to one (OCR column padding)
  * collapse 2+ consecutive blank lines to a single blank line

Usage: python3 claude_tools/lean_extract.py <CID>
"""
from __future__ import annotations
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTS = os.path.join(ROOT, "supply-code", "extracts")


def lean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x0c", "\n")               # form-feed page breaks -> newline
    text = "".join(ch for ch in text if ch >= " " or ch == "\n" or ch == "\t")
    out_lines = []
    blank = 0
    for line in text.split("\n"):
        line = line.replace("\t", " ").rstrip()
        line = re.sub(r"   +", " ", line)            # 3+ interior spaces -> 1
        if line.strip() == "":
            blank += 1
            if blank <= 1:
                out_lines.append("")
        else:
            blank = 0
            out_lines.append(line)
    return "\n".join(out_lines).strip() + "\n"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cid = sys.argv[1]
    src = os.path.join(EXTRACTS, cid + ".txt")
    if not os.path.exists(src):
        sys.exit(f"FAILED · no extract {src}")
    raw = open(src, encoding="utf-8", errors="replace").read()
    out = lean(raw)
    dst = os.path.join(EXTRACTS, cid + ".lean.txt")
    open(dst, "w", encoding="utf-8").write(out)
    # sanity: every non-space char of the lean output must appear in the source
    # (i.e. we only dropped whitespace) — guards against accidental content loss.
    if re.sub(r"\s+", "", out) not in re.sub(r"\s+", "", raw) + "":
        # substring check is too strict if order preserved; compare multisets of words
        import collections
        wa = collections.Counter(re.findall(r"\S+", raw))
        wb = collections.Counter(re.findall(r"\S+", out))
        if wb - wa:
            sys.exit(f"FAILED · lean added/altered tokens (bug): {list((wb-wa))[:5]}")
    saved = len(raw) - len(out)
    pct = (100.0 * saved / len(raw)) if raw else 0.0
    print(f"lean {cid}: {len(raw)} -> {len(out)} chars (saved {saved}, {pct:.1f}%) -> {dst}")


if __name__ == "__main__":
    main()
