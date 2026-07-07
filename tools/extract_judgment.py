#!/usr/bin/env python3
"""Deterministic pre-parser: judgment HTML/PDF/MHTML -> cleaned text + raw fingerprint (no LLM).

Usage:  python tools/extract_judgment.py <input_file> <out_dir> <case_id>
Writes: <out_dir>/<case_id>.txt        cleaned plain text
        <out_dir>/<case_id>.fp.json    raw fingerprint (citations w/ doc-ids, cause title,
                                       court, coram, sections, counts)

Optimised for Indian Kanoon HTML (data-docid spans and /doc/ or /docfragment/ links);
falls back to generic HTML tag-stripping, and to PyMuPDF for PDFs. The LLM deep-extract
(issues, reasoning, treatment of authorities, ratio, disposition) is a separate step that
reads the .txt this produces; this script stays deterministic so citations and structure
are captured cheaply and accurately.
"""
import sys, os, re, json, html as H


def strip(x):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', x))).strip()


def first(s, pats):
    for p in pats:
        m = re.search(p, s, re.S | re.I)
        if m and strip(m.group(1)):
            return strip(m.group(1))
    return ""


def clean_text(s):
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?i)</p>|<br\s*/?>|</div>|</h[1-6]>|</li>|</tr>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = H.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n[ \t]+', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def extract_cites(s):
    cites = {}
    def add(did, nm):
        nm = strip(nm)
        if did not in cites:
            cites[did] = {"docid": did, "name": nm, "count": 0}
        if nm and not cites[did]["name"]:
            cites[did]["name"] = nm
        cites[did]["count"] += 1
    for m in re.finditer(r'data-docid="(\d+)"[^>]*>(.*?)</', s, re.S):
        add(m.group(1), m.group(2))
    for m in re.finditer(r'href="/doc(?:fragment)?/(\d+)/?[^"]*"[^>]*>(.*?)</a>', s, re.S):
        add(m.group(1), m.group(2))
    return cites


def from_html(s):
    cites = extract_cites(s)
    title = first(s, [r'<h2 class="doc_title"[^>]*>(.*?)</h2>',
                      r'<div class="doc_title"[^>]*>(.*?)</div>',
                      r'<title>(.*?)</title>'])
    court = first(s, [r'<h2 class="docsource_main"[^>]*>(.*?)</h2>',
                      r'<div class="docsource[^"]*"[^>]*>(.*?)</div>'])
    coram = first(s, [r'<div class="doc_bench"[^>]*>(.*?)</div>',
                      r'(?i)\b(?:coram|bench)\b[:\s]*(?:</[^>]+>\s*)?([A-Z][^<\n]{0,120})'])
    idx = s.find('class="judgments"')
    if idx != -1:
        gt = s.find('>', idx)
        body_src = s[gt + 1:] if gt != -1 else s[idx:]
    else:
        body_src = s
    return clean_text(body_src), cites, title, court, coram


def from_pdf(path):
    try:
        import fitz
    except ImportError:  # PyMuPDF absent (e.g. a fresh cloud session) — install once; pypi is allowlisted
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "pymupdf"], check=True)
        import fitz
    d = fitz.open(path)
    return "\n".join(p.get_text() for p in d), {}, "", "", ""


def looks_html(raw):
    head = raw[:2048].lstrip().lower()
    return head.startswith(b'<!doctype') or b'<html' in head or b'<body' in head or b'<div' in head


def from_mhtml(raw):
    """MHTML / MIME web archive (Chrome 'Webpage, Single File', .mhtml) -> decode the
    text/html MIME part(s) (quoted-printable / base64) and reuse from_html. Embedded images
    and other non-HTML parts are skipped."""
    import email
    msg = email.message_from_bytes(raw)
    parts = []
    for p in msg.walk():
        if p.get_content_type() == 'text/html':
            payload = p.get_payload(decode=True)
            if payload:
                parts.append(payload.decode(p.get_content_charset() or 'utf-8', 'replace'))
    return from_html("\n".join(parts))


def looks_mhtml(raw):
    head = raw[:1024].lstrip().lower()
    return (head.startswith(b'from: <saved by blink>')
            or head.startswith(b'content-type: multipart/related')
            or (b'mime-version:' in head and b'multipart/related' in raw[:4096].lower()))


def main():
    if len(sys.argv) < 4:
        sys.exit("usage: extract_judgment.py <input_file> <out_dir> <case_id>")
    inp, outdir, cid = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(inp, 'rb').read()
    ext = os.path.splitext(inp)[1].lower()
    if ext == '.pdf':
        txt, cites, title, court, coram = from_pdf(inp)
        fmt = 'pdf'
    elif ext in ('.mht', '.mhtml') or looks_mhtml(raw):
        txt, cites, title, court, coram = from_mhtml(raw)
        fmt = 'mhtml'
    elif ext in ('.html', '.htm', '.xhtml') or looks_html(raw):
        txt, cites, title, court, coram = from_html(raw.decode('utf-8', 'replace'))
        fmt = 'html'
    else:
        txt, cites, title, court, coram = clean_text(raw.decode('utf-8', 'replace')), {}, "", "", ""
        fmt = 'text'
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, cid + '.txt'), 'w') as f:
        f.write(txt)
    secs = sorted(set(re.findall(r'[Ss]ections?\s+(\d+[A-Z]?)', txt)), key=lambda x: (len(x), x))[:60]
    fp = {
        "case_id": cid, "source_file": os.path.basename(inp), "format": fmt,
        "char_count": len(txt), "word_count": len(txt.split()),
        "para_count": txt.count('\n\n') + 1,
        "cause_title": title, "court": court, "coram": coram,
        "sections_cited": secs, "citation_count": len(cites),
        "citations": sorted(cites.values(), key=lambda c: -c["count"]),
    }
    with open(os.path.join(outdir, cid + '.fp.json'), 'w') as f:
        json.dump(fp, f, indent=1, ensure_ascii=False)
    print(f"{cid}: fmt={fmt} words={fp['word_count']} citations={len(cites)} "
          f"sections={secs[:8]} title={title[:60]!r}")


if __name__ == '__main__':
    main()
