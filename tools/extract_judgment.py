#!/usr/bin/env python3
"""Deterministic pre-parser: a judgment (HTML/PDF/MHTML file, or an Indian Kanoon doc-id / URL
that is fetched via the IK API) -> cleaned text + raw fingerprint (no LLM).

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


# Prose citations (Allahabad PDFs have no IK doc-ids). Used for the
# short-uncited gate and the 6.5 stencil citation veto. Caption "X v. Y"
# and this judgment's own Neutral Citation No. must not count.
_OWN_NEUTRAL = re.compile(r"Neutral\s+Citation\s+No\.\s*[-:]\s*\S+", re.I)
_REPORTER = re.compile(
    r"\(\s*\d{4}\s*\)\s+\d+\s+SCC\s+\d+"
    r"|\bAIR\s+\d{4}\s+[A-Z]{2,}(?:\s+[A-Z]+)?\s+\d+"
    r"|\b\d{4}\s*\(\s*\d+\s*\)\s+(?:ADJ|ALD|ALR|SCALE|SCR|All\.?\s*L\.?J\.?)\s+\d+"
    r"|\b\d{4}\s+\d+\s+SCC\s+\d+",
    re.I,
)
_NEUTRAL_CITE = re.compile(
    r"\b(?:19|20)\d{2}:(?:INSC|AHC(?:-LKO)?|[A-Z]{2,8}):\d+",
    re.I,
)
_CASE_V = re.compile(
    r"\b([A-Z][A-Za-z.'()]+(?:\s+[A-Z][A-Za-z.'()]+){0,6})\s+"
    r"v(?:ersus|s)?\.?\s+"
    r"([A-Z][A-Za-z.'()]+(?:\s+[A-Z][A-Za-z.'()]+){0,8})\b"
)
_GENERIC_LEFT = re.compile(
    r"^(?:the\s+)?(?:petitioner|applicant|revisionist|appellant)s?\b", re.I)
_GENERIC_RIGHT = re.compile(
    r"^(?:the\s+)?(?:respondents?|opposite\s+part(?:y|ies)|ors?\.?|others)\b", re.I)
_BODY_START = re.compile(
    r"(?m)^(?:Heard\b|\s*1\.\s|This is a writ\b|The present (?:petition|application)\b)",
    re.I,
)


def _body_for_cites(txt):
    t = _OWN_NEUTRAL.sub(" ", txt or "", count=4)
    m = _BODY_START.search(t)
    if m:
        return t[m.start():]
    return t


def extract_text_cites(txt):
    """Return (count, sample_strings) of authorities discussed in the order.

    High precision over recall: a false positive blocks the 6.5 stencil and
    sends a 3-page order to full. Caption parties and this case's own
    neutral citation are excluded.
    """
    body = _body_for_cites(txt)
    found = []
    for rx in (_REPORTER, _NEUTRAL_CITE):
        found.extend(m.group(0).strip() for m in rx.finditer(body))
    for m in _CASE_V.finditer(body):
        left, right = m.group(1).strip(), m.group(2).strip()
        if _GENERIC_LEFT.match(left) or _GENERIC_RIGHT.match(right):
            continue
        if len(left.split()) == 1 and left.lower() in ("the", "this", "said", "hon"):
            continue
        found.append(m.group(0).strip())
    # de-dupe preserving order
    seen, uniq = set(), []
    for s in found:
        key = re.sub(r"\s+", " ", s).lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(s)
    return len(uniq), uniq[:12]


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
    page_count = d.page_count
    txt = "\n".join(p.get_text() for p in d)
    return txt, {}, "", "", "", page_count


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


def ik_docid(s):
    """Return an Indian Kanoon doc-id iff s is *only* a bare doc-id or a single IK /doc/ URL."""
    s = (s or "").strip()
    if re.fullmatch(r'\d{3,}', s):
        return s
    m = re.fullmatch(r'(?:https?://)?(?:www\.)?indiankanoon\.org/doc(?:fragment)?/(\d{3,})/?', s, re.I)
    return m.group(1) if m else ""


def from_ik_api(docid):
    """Fetch a judgment via the Indian Kanoon API (POST /doc/<id>/, header 'Authorization: Token').
    Needs IK_API_TOKEN in the environment and network access to api.indiankanoon.org. Reuses
    from_html on the returned document HTML and prefers the API's own title / court fields."""
    import os, json, subprocess
    token = os.environ.get('IK_API_TOKEN', '').strip()
    if not token:
        sys.exit("IK_API_TOKEN not set — add it to the cloud environment's variables")
    p = subprocess.run(
        ['curl', '-sS', '-X', 'POST', f'https://api.indiankanoon.org/doc/{docid}/',
         '-H', f'Authorization: Token {token}', '-H', 'Accept: application/json'],
        capture_output=True, timeout=90)
    if p.returncode != 0:
        sys.exit(f"IK API fetch failed for doc {docid}: {p.stderr.decode('utf-8', 'replace')[:200]}")
    try:
        d = json.loads(p.stdout.decode('utf-8', 'replace'))
    except Exception:
        sys.exit(f"IK API returned non-JSON for doc {docid}: {p.stdout[:160]!r}")
    if not d.get('doc'):
        sys.exit(f"IK API response for doc {docid} has no document body (keys: {list(d)})")
    txt, cites, t2, c2, co2 = from_html(d['doc'])
    return txt, cites, strip(d.get('title', '')) or t2, strip(d.get('docsource', '')) or c2, co2


def main():
    if len(sys.argv) < 4:
        sys.exit("usage: extract_judgment.py <input_file> <out_dir> <case_id>")
    inp, outdir, cid = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(inp, 'rb').read()
    ext = os.path.splitext(inp)[1].lower()
    content = raw.decode('utf-8', 'replace')
    # Fetch-request: the input is *only* an Indian Kanoon doc-id or /doc/ URL (as file content,
    # or - for an empty file with no judgment extension - as the filename) -> fetch via the API.
    docid = ik_docid(content) if len(raw) < 4000 else ""
    if not docid and not content.strip() and ext not in ('.pdf', '.html', '.htm', '.xhtml', '.mht', '.mhtml'):
        docid = ik_docid(os.path.splitext(os.path.basename(inp))[0])
    page_count = None
    if docid:
        txt, cites, title, court, coram = from_ik_api(docid)
        fmt = 'ik-api'
    elif ext == '.pdf':
        txt, cites, title, court, coram, page_count = from_pdf(inp)
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
    with open(os.path.join(outdir, cid + '.txt'), 'w', encoding='utf-8') as f:
        f.write(txt)
    secs = sorted(set(re.findall(r'[Ss]ections?\s+(\d+[A-Z]?)', txt)), key=lambda x: (len(x), x))[:60]
    ik_n = len(cites)
    text_n, text_samples = extract_text_cites(txt)
    # IK hyperlinks win when present (HTML). PDFs have none — use prose.
    cite_n = max(ik_n, text_n)
    fp = {
        "case_id": cid, "source_file": os.path.basename(inp), "format": fmt,
        "char_count": len(txt), "word_count": len(txt.split()),
        "para_count": txt.count('\n\n') + 1,
        "cause_title": title, "court": court, "coram": coram,
        "sections_cited": secs,
        "ik_citation_count": ik_n,
        "text_citation_count": text_n,
        "text_citation_samples": text_samples,
        "citation_count": cite_n,
        "citations": sorted(cites.values(), key=lambda c: -c["count"]),
        "page_count": page_count,
    }
    with open(os.path.join(outdir, cid + '.fp.json'), 'w', encoding='utf-8') as f:
        json.dump(fp, f, indent=1, ensure_ascii=False)
    print(f"{cid}: fmt={fmt} words={fp['word_count']} pages={page_count} "
          f"citations={cite_n} (ik={ik_n} text={text_n}) "
          f"sections={secs[:8]} title={title[:60]!r}")


if __name__ == '__main__':
    main()
