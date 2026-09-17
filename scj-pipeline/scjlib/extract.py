"""PDF -> lean text + parsed metadata.

Tries pdfplumber (better layout) then pypdf. The "lean" pass strips repeated
headers/footers, page numbers and copy stamps so each case costs the authoring
model as few tokens as possible -- the single biggest lever for fitting >=20
cases into one session.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from scjlib import common as C
from scjlib import meta as M

_NOISE = [
    re.compile(r'^\s*Page\s+\d+\s*(of\s+\d+)?\s*$', re.I),
    re.compile(r'^\s*-?\s*\d+\s*-?\s*$'),                 # bare page numbers
    re.compile(r'^\s*(WWW\.|https?://)', re.I),
    re.compile(r'Certified\s+(?:true\s+)?copy', re.I),
    re.compile(r'^\s*Digitally signed', re.I),
    re.compile(r'downloaded\s+on', re.I),
]


def _pdfplumber_text(path):
    import pdfplumber
    parts = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            parts.append(pg.extract_text() or "")
        return "\n".join(parts), len(pdf.pages)


def _pypdf_text(path):
    from pypdf import PdfReader
    r = PdfReader(path)
    return "\n".join((p.extract_text() or "") for p in r.pages), len(r.pages)


def raw_text(path):
    """Return (text, page_count, engine_name); ("", 0, "none") if all engines fail."""
    for name, fn in (("pdfplumber", _pdfplumber_text), ("pypdf", _pypdf_text)):
        try:
            txt, n = fn(path)
            if txt and txt.strip():
                return txt, n, name
        except Exception:
            continue
    return "", 0, "none"


def lean_clean(text: str) -> str:
    text = C.normalize_ws(text)
    lines = text.split("\n")
    cnt = Counter(l.strip() for l in lines if l.strip())
    out = []
    for l in lines:
        s = l.strip()
        if not s:
            out.append("")
            continue
        if any(p.search(s) for p in _NOISE):
            continue
        if len(s) < 40 and cnt[s] >= 4:      # short line repeated on many pages = boilerplate
            continue
        out.append(s)
    return C.normalize_ws("\n".join(out))


def extract_one(pdf_path, cap_chars: int = 24000) -> dict:
    pdf_path = Path(pdf_path)
    txt, npages, engine = raw_text(pdf_path)
    lean = lean_clean(txt)
    truncated = False
    if len(lean) > cap_chars:
        lean = lean[:cap_chars] + "\n…[truncated for length]…"
        truncated = True
    return {
        "source_file": pdf_path.name,
        "source_path": str(pdf_path),
        "engine": engine,
        "page_count": npages,
        "char_count": len(txt),
        "lean_char_count": len(lean),
        "est_tokens": C.est_tokens(lean),
        "truncated": truncated,
        "sha256": C.sha256_file(pdf_path),
        "raw_meta": M.parse_meta(txt, pdf_path.name),
        "lean_text": lean,
    }
