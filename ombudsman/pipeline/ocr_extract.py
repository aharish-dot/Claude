#!/usr/bin/env python3
"""
ocr_extract.py — OCR front-end for scanned UPERC Electricity Ombudsman orders.

Unlike the High-Court pipeline (which ingests searchable IK HTML/PDF), Ombudsman
orders download as *scanned bilingual images* with no usable text layer. This
renders each page at 300 dpi and OCRs it (Hindi + English), producing the plain
`OMB-XXX.txt` that the existing extract sub-agent + verify.py gate then consume.

Usage:
    python ocr_extract.py INPUT.pdf [-o OUT.txt] [--lang hin+eng] [--dpi 300]
    python ocr_extract.py input/ --outdir extracts/     # batch a folder

Deps (self-installs PyMuPDF/Pillow/pytesseract if missing); the tesseract binary
and its language packs must exist on the system:
    apt-get install -y tesseract-ocr tesseract-ocr-hin
"""
import argparse
import io
import subprocess
import sys
from pathlib import Path


def _ensure(pkg, mod=None):
    try:
        __import__(mod or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg])
        __import__(mod or pkg)


def _check_tesseract(lang):
    import pytesseract
    try:
        have = set(pytesseract.get_languages(config=""))
    except Exception:
        print("WARNING: could not query tesseract languages; is the binary installed?",
              file=sys.stderr)
        return
    missing = [l for l in lang.split("+") if l not in have]
    if missing:
        print(f"WARNING: tesseract language pack(s) missing: {missing}. "
              f"Install e.g. `apt-get install -y tesseract-ocr-hin`. "
              f"Proceeding with available packs.", file=sys.stderr)


def ocr_pdf(pdf_path: Path, lang="hin+eng", dpi=300) -> str:
    """Render every page and OCR it; return page-delimited text."""
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image

    doc = fitz.open(pdf_path)
    out = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang=lang)
        out.append(f"\n\n===== PAGE {i + 1}/{len(doc)} =====\n{text}")
        print(f"  page {i + 1}/{len(doc)} ok ({len(text)} chars)", file=sys.stderr)
    return "".join(out)


def process(pdf_path: Path, out_path: Path, lang, dpi):
    print(f"OCR {pdf_path.name} -> {out_path.name}", file=sys.stderr)
    text = ocr_pdf(pdf_path, lang=lang, dpi=dpi)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    cpp = len(text) / max(1, text.count("===== PAGE"))
    flag = "  <-- LOW yield; check DPI / language packs" if cpp < 400 else ""
    print(f"wrote {out_path} ({len(text)} chars, ~{cpp:.0f}/page){flag}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="a PDF, or a directory of PDFs")
    ap.add_argument("-o", "--out", help="output .txt (single-file mode)")
    ap.add_argument("--outdir", default="extracts", help="output dir (batch mode)")
    ap.add_argument("--lang", default="hin+eng", help="tesseract langs (default hin+eng)")
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()

    _ensure("PyMuPDF", "fitz")
    _ensure("Pillow", "PIL")
    _ensure("pytesseract")
    _check_tesseract(args.lang)

    src = Path(args.input)
    if src.is_dir():
        pdfs = sorted(src.glob("*.pdf"))
        if not pdfs:
            sys.exit(f"no PDFs in {src}")
        for pdf in pdfs:
            process(pdf, Path(args.outdir) / f"{pdf.stem}.txt", args.lang, args.dpi)
    else:
        out = Path(args.out) if args.out else src.with_suffix(".txt")
        process(src, out, args.lang, args.dpi)


if __name__ == "__main__":
    main()
