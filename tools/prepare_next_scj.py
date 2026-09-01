#!/usr/bin/env python3
"""Pick the next unique pending PDF, extract text, write a work ticket.

Usage:  python tools/prepare_next_scj.py
Exit 0  ticket at supply-code/tmp/NEXT_TICKET.json
Exit 2  no unique pending input (print NO_INPUT)

Does not bump next_seq (finalize_scj.py does that). Retires filename and
docket duplicates to processed/ (mirroring any input/ subfolder) without
assigning an id. Nested queues (e.g. input/2025/*.pdf) stay nested.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scj_stencil
SC = os.path.join(ROOT, "supply-code")
INPUT = os.path.join(SC, "input")
PROCESSED = os.path.join(SC, "processed")
STATE = os.path.join(SC, "state", "index.json")
SUMM = os.path.join(SC, "summaries", "json")
EXTRACTS = os.path.join(SC, "extracts")
TICKET = os.path.join(SC, "tmp", "NEXT_TICKET.json")
SKIP_NAMES = {"WRIC(A)_20210_2012.pdf"}  # already SCJ-273
CATALOG = os.path.join(SC, "jurisprudence", "catalog.txt")
SHORT_PAGES = 2
SHORT_WORDS = 800
# Uncited 3-pagers that used to miss the 800-word gate (e.g. SCJ-329 at 804
# words) go short. A 4-page doctrinal quash (SCJ-328) stays full.
SHORT_PAGES_UNCITED = 3
SHORT_WORDS_UNCITED = 1500
SHORT_TURNS = 15
FULL_TURNS = 50

FN_DOCKET = re.compile(r"_(\d+)_(\d{4})\.pdf$", re.I)
CLAUSE_NUM = re.compile(r"\b\d+\.\d+(?:\([A-Za-z0-9]+\))*")
SECTION_NUM = re.compile(r"(?i)\b(?:sections?|s\.)\s*(\d+[A-Z]?(?:\(\d+[A-Z]?\))*)")
TWIN_PDF = re.compile(r" \(1\)\.pdf$", re.I)


def load_state():
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def posix_rel(path, start):
    return os.path.relpath(path, start).replace("\\", "/")


def under(root, rel):
    rel = (rel or "").replace("\\", "/").lstrip("/")
    if not rel or rel == ".":
        return root
    return os.path.join(root, *rel.split("/"))


def basename_of(rel):
    return os.path.basename((rel or "").replace("\\", "/"))


def processed_names():
    """Basenames already in processed/ (any subfolder)."""
    names = set()
    if not os.path.isdir(PROCESSED):
        return names
    for dirpath, _, filenames in os.walk(PROCESSED):
        for n in filenames:
            if n != ".gitkeep":
                names.add(n)
    return names


def pending_files(done):
    """POSIX paths relative to input/, files at root and in subfolders."""
    if not os.path.isdir(INPUT):
        return []
    out = []
    for dirpath, dirnames, filenames in os.walk(INPUT):
        dirnames.sort()
        for n in sorted(filenames):
            if n == ".gitkeep" or not n.lower().endswith(".pdf"):
                continue
            if n in SKIP_NAMES or TWIN_PDF.search(n):
                continue
            rel = posix_rel(os.path.join(dirpath, n), INPUT)
            if n in done:
                continue
            out.append(rel)
    out.sort()
    return out


def docket_needles(filename):
    m = FN_DOCKET.search(basename_of(filename))
    if not m:
        return []
    num, year = m.group(1), m.group(2)
    return [
        f"No. {num} of {year}",
        f"No. - {num} of {year}",
        f"No.- {num} of {year}",
        f"No.{num} of {year}",
    ]


def existing_dockets():
    """Load all dockets once (cheap: 280 small JSON files)."""
    blob = []
    if not os.path.isdir(SUMM):
        return ""
    for n in os.listdir(SUMM):
        if not n.endswith(".json"):
            continue
        with open(os.path.join(SUMM, n), encoding="utf-8") as f:
            try:
                d = json.load(f)
            except json.JSONDecodeError:
                continue
        blob.append(d.get("docket") or "")
        blob.append(d.get("case_id") or "")
        blob.append(os.path.splitext(n)[0])
    return "\n".join(blob).lower()


def is_docket_dup(filename, docket_blob):
    for needle in docket_needles(filename):
        if needle.lower() in docket_blob:
            return needle
    return None


def retire(rel, reason):
    src = under(INPUT, rel)
    dst = under(PROCESSED, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    dest_rel = os.path.dirname(rel.replace("\\", "/")) or "."
    if os.path.exists(src):
        if os.path.exists(dst) and os.path.abspath(src) != os.path.abspath(dst):
            os.remove(src)
        else:
            os.replace(src, dst)
    print(f"retired duplicate {rel} ({reason}) → processed/{dest_rel}/")


def extract(src_rel, cid):
    os.makedirs(EXTRACTS, exist_ok=True)
    src = under(INPUT, src_rel)
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "extract_judgment.py"),
         src, EXTRACTS, cid],
        cwd=ROOT, capture_output=True, text=True,
    )
    if r.stdout:
        print(r.stdout.strip())
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
        sys.exit(r.returncode)
    fp_path = os.path.join(EXTRACTS, cid + ".fp.json")
    fp = json.load(open(fp_path, encoding="utf-8")) if os.path.exists(fp_path) else {}
    return fp


def ensure_catalog():
    if not os.path.exists(CATALOG):
        subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "build_scj_catalog.py")],
            cwd=ROOT, check=True,
        )


def is_short(page_count, word_count, citation_count=0):
    """Short path: old page/word gate, or uncited and not long.

    Never stricter than before (pages ≤ 2 or words ≤ 800 still short even
    with citations). Full stays for cited orders and for uncited work
    above 3 pages / 1500 words.
    """
    pages = page_count if isinstance(page_count, int) else None
    words = int(word_count or 0)
    cites = int(citation_count or 0)
    if pages is not None and pages <= SHORT_PAGES:
        return True
    if words <= SHORT_WORDS:
        return True
    if cites == 0 and words <= SHORT_WORDS_UNCITED:
        if pages is None or pages <= SHORT_PAGES_UNCITED:
            return True
    return False


def short_gate(pages, words, citation_count=0):
    """Why authoring=short (or None if not short)."""
    if not is_short(pages, words, citation_count):
        return None
    if isinstance(pages, int) and pages <= SHORT_PAGES:
        return "short-pages"
    if int(words or 0) <= SHORT_WORDS:
        return "short-words"
    return "short-uncited"


def catalog_hits(txt, limit=40):
    """Provision/tag lines that mention clause or section numbers found in the order."""
    if not txt or not os.path.exists(CATALOG):
        return []
    needles = {m.group(0).lower() for m in CLAUSE_NUM.finditer(txt)}
    needles.update(m.group(1).lower() for m in SECTION_NUM.finditer(txt))
    needles = {n for n in needles if n and n not in {"1", "2", "3"}}
    if not needles:
        return []
    hits, seen = [], set()
    with open(CATALOG, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if (not s or s.startswith("#")
                    or s.startswith("PROVISIONS ") or s.startswith("TAGS ")):
                continue
            low = s.lower()
            if any(n in low for n in needles) and s not in seen:
                seen.add(s)
                hits.append(s)
            if len(hits) >= limit:
                break
    return hits


def main():
    state = load_state()
    seq = int(state["next_seq"])
    cid = f"SCJ-{seq:03d}"
    done = processed_names()
    docket_blob = existing_dockets()

    while True:
        pending = pending_files(done)
        if not pending:
            os.makedirs(os.path.dirname(TICKET), exist_ok=True)
            json.dump({"status": "NO_INPUT", "next_seq": seq}, open(TICKET, "w"))
            print(f"NO_INPUT · next_seq={seq} · stop")
            return 2
        name = pending[0]
        base = basename_of(name)
        if base in done:
            retire(name, "filename already in processed/")
            continue
        hit = is_docket_dup(base, docket_blob)
        if hit:
            retire(name, f"docket already in corpus: {hit}")
            done.add(base)
            continue
        break

    fp = extract(name, cid)
    words = int(fp.get("word_count") or 0)
    pages = fp.get("page_count")
    txt_path = os.path.join(EXTRACTS, cid + ".txt")
    txt = open(txt_path, encoding="utf-8", errors="replace").read() if os.path.exists(txt_path) else ""
    stencil = scj_stencil.classify(txt, fp, live_only=True)
    is_stencil = (
        stencil.get("verdict") == "STENCIL"
        and stencil.get("family") in scj_stencil.LIVE
        and scj_stencil.slots_fillable(stencil.get("slots") or {})
    )
    cites = int(fp.get("citation_count") or 0)
    short = is_short(pages, words, cites)
    ticket = {
        "status": "READY",
        "case_id": cid,
        "next_seq": seq,
        "source": name,
        "txt": f"supply-code/extracts/{cid}.txt",
        "fp": f"supply-code/extracts/{cid}.fp.json",
        "word_count": words,
        "page_count": pages,
        "citation_count": cites,
        "out_json": f"supply-code/summaries/json/{cid}.json",
    }
    if is_stencil:
        ticket["authoring"] = "stencil"
        ticket["stencil_family"] = stencil["family"]
        ticket["gate"] = "stencil"
        ticket["max_turns"] = 0
        ticket["catalog_hits"] = []
        ticket["prompt"] = "tools/scj_stencil.py"
    else:
        ensure_catalog()
        hits = catalog_hits(txt)
        ticket["catalog_hits"] = hits
        if short:
            ticket["authoring"] = "short"
            ticket["gate"] = short_gate(pages, words, cites)
            ticket["max_turns"] = SHORT_TURNS
            ticket["prompt"] = "tools/prompts/next_case_short.txt"
        else:
            ticket["authoring"] = "full"
            ticket["gate"] = "full"
            ticket["max_turns"] = FULL_TURNS
            ticket["catalog"] = "supply-code/jurisprudence/catalog.txt"
            ticket["example"] = "supply-code/summaries/json/SCJ-280.json"
            ticket["prompt"] = "tools/prompts/next_case_once.txt"
    os.makedirs(os.path.dirname(TICKET), exist_ok=True)
    with open(TICKET, "w", encoding="utf-8") as f:
        json.dump(ticket, f, indent=2)
        f.write("\n")
    extra = ""
    if is_stencil:
        extra = f" family={ticket['stencil_family']}"
    print(f"READY {cid} authoring={ticket['authoring']}{extra} "
          f"gate={ticket.get('gate')} source={name} "
          f"pages={pages} words={words} citations={cites} "
          f"catalog_hits={len(ticket.get('catalog_hits') or [])} "
          f"→ {TICKET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
