#!/usr/bin/env python3
"""Index every PDF in supply-code/input/ with its page count and word count.

Claude-owned tool (kept out of tools/ so it never collides with Grok's edits).
Runs programmatically — it does NOT feed any PDF text into an LLM context.

page_count and word_count are computed exactly as tools/extract_judgment.py does,
so the numbers line up with each case's fingerprint (fp.json) and the pipeline's
short/full routing:
    txt        = "\\n".join(page.get_text() for page in doc)
    word_count = len(txt.split())
    page_count = doc.page_count

Usage:
    python claude_tools/index_input_pdfs.py                 # index supply-code/input/
    python claude_tools/index_input_pdfs.py --dir supply-code/processed
    python claude_tools/index_input_pdfs.py --out some/other.json

Output (default): supply-code/input/input_pdf_stats.json
    {
      "generated_at": "<UTC ISO8601>",
      "root": "supply-code/input",
      "method": "PyMuPDF; word_count=len(text.split()) over all pages",
      "count": <n>, "ok": <n>, "errors": <n>,
      "total_pages": <n>, "total_words": <n>,
      "files": [ {"path","page_count","word_count","char_count","size_bytes"} , ... ]
    }
"""
from __future__ import annotations
import argparse, datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import pymupdf as _fitz          # newer name
except ImportError:                   # pragma: no cover
    import fitz as _fitz             # legacy name


def iter_pdfs(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            if name.lower().endswith(".pdf"):
                yield os.path.join(dirpath, name)


def stat_pdf(path: str) -> dict:
    rec = {"path": None, "page_count": None, "word_count": None,
           "char_count": None, "size_bytes": None}
    try:
        rec["size_bytes"] = os.path.getsize(path)
    except OSError:
        pass
    try:
        doc = _fitz.open(path)
        txt = "\n".join(p.get_text() for p in doc)
        rec["page_count"] = doc.page_count
        rec["char_count"] = len(txt)
        rec["word_count"] = len(txt.split())
        doc.close()
    except Exception as e:                       # keep going on a bad PDF
        rec["error"] = f"{type(e).__name__}: {e}"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join("supply-code", "input"),
                    help="directory to scan (relative to repo root or absolute)")
    ap.add_argument("--out", default=None,
                    help="output JSON path (default: <dir>/input_pdf_stats.json)")
    ap.add_argument("--progress", type=int, default=200,
                    help="print a progress line every N files (0 = silent)")
    args = ap.parse_args()

    scan_dir = args.dir if os.path.isabs(args.dir) else os.path.join(ROOT, args.dir)
    scan_dir = os.path.normpath(scan_dir)
    if not os.path.isdir(scan_dir):
        print(f"FAILED · not a directory: {scan_dir}", file=sys.stderr)
        return 1
    out = args.out or os.path.join(scan_dir, "input_pdf_stats.json")
    out = out if os.path.isabs(out) else os.path.join(ROOT, out)

    rel_root = os.path.relpath(scan_dir, ROOT).replace("\\", "/")
    files, ok, errors, total_pages, total_words = [], 0, 0, 0, 0
    all_pdfs = list(iter_pdfs(scan_dir))
    n = len(all_pdfs)
    for i, path in enumerate(all_pdfs, 1):
        rec = stat_pdf(path)
        rec["path"] = os.path.relpath(path, scan_dir).replace("\\", "/")
        if "error" in rec:
            errors += 1
        else:
            ok += 1
            total_pages += rec["page_count"] or 0
            total_words += rec["word_count"] or 0
        files.append(rec)
        if args.progress and (i % args.progress == 0 or i == n):
            print(f"  {i}/{n} indexed ({errors} errors)", flush=True)

    files.sort(key=lambda r: r["path"])
    payload = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
                         .isoformat(timespec="seconds"),
        "root": rel_root,
        "method": "PyMuPDF; page_count=doc.page_count; "
                  "word_count=len(text.split()) over all pages",
        "count": len(files), "ok": ok, "errors": errors,
        "total_pages": total_pages, "total_words": total_words,
        "files": files,
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {os.path.relpath(out, ROOT).replace(chr(92),'/')}: "
          f"{len(files)} PDFs ({ok} ok, {errors} errors), "
          f"{total_pages} pages, {total_words} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
