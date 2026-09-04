#!/usr/bin/env python3
"""Pick the next unique pending PDF, extract text, write a work ticket.

Usage:  python tools/prepare_next_scj.py
        python tools/prepare_next_scj.py --claim-new
        python tools/prepare_next_scj.py --demote [--ticket PATH]
Exit 0  ticket at supply-code/tmp/tickets/SCJ-NNN.json
        (legacy copy at tmp/NEXT_TICKET.json)
Exit 2  no unique pending input (print NO_INPUT)

--demote  rewrite a READY stencil ticket to short/full (no re-extract).
          Used when stencil write fails (empty caption, fill incomplete).
          Does not bump next_seq.

Reserves SCJ-NNN at claim time (bumps next_seq under the queue lock) so
parallel workers cannot share an id. finalize_scj.py never rewinds it.
Retires filename and docket duplicates to processed/ (mirroring any input/
subfolder) without assigning an id. Nested queues stay nested.
"""
import argparse, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scj_lock
import scj_queue
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


def pending_files(done, skip_rels=None):
    """POSIX paths relative to input/, files at root and in subfolders."""
    skip = {s.replace("\\", "/").lstrip("/") for s in (skip_rels or [])}
    skip_base = {basename_of(s) for s in skip}
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
            if n in done or rel in skip or n in skip_base:
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
    # Robust catch-all (Claude patch, authorised): match "<num> of <year>" with
    # digit boundaries so connected petitions written "Nos. 16147 of 2009 and
    # 16149 of 2009" (plural / multi-docket) are caught even though the singular
    # needle "No. 16147 of 2009" is not a substring. (Missed dup -> SCJ-707/225.)
    m = FN_DOCKET.search(basename_of(filename))
    if m:
        num, year = m.group(1), m.group(2)
        if re.search(rf"(?<!\d){num}\s+of\s+{year}(?!\d)", docket_blob):
            return f"{num} of {year}"
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
    # Keep GitHub in sync when input/ is tracked: stage processed copy + input deletion.
    subprocess.run(
        ["git", "add", "--", posix_rel(dst, ROOT)],
        cwd=ROOT, check=False,
    )
    subprocess.run(
        ["git", "add", "-u", "--", posix_rel(src, ROOT)],
        cwd=ROOT, check=False,
    )
    print(f"retired duplicate {rel} ({reason}) → processed/{dest_rel}/")


def extract(src_rel, cid):
    os.makedirs(EXTRACTS, exist_ok=True)
    src = src_rel if os.path.isabs(src_rel) else under(INPUT, src_rel)
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


def _print_ready(ticket):
    extra = ""
    if ticket.get("authoring") == "stencil":
        extra = f" family={ticket.get('stencil_family')}"
    dest = scj_queue.ticket_path(ticket["case_id"])
    print(f"READY {ticket['case_id']} authoring={ticket.get('authoring')}{extra} "
          f"gate={ticket.get('gate')} source={ticket.get('source')} "
          f"pages={ticket.get('page_count')} words={ticket.get('word_count')} "
          f"citations={ticket.get('citation_count')} "
          f"(ik={ticket.get('ik_citation_count')} "
          f"text={ticket.get('text_citation_count')}) "
          f"catalog_hits={len(ticket.get('catalog_hits') or [])} "
          f"→ {dest}")


def resume_open_ticket():
    """Reuse the oldest unfinalized ticket instead of assigning a new id."""
    state = load_state()
    for ticket in scj_queue.open_tickets():
        cid = ticket.get("case_id")
        if not cid:
            continue
        if scj_queue.case_is_done(state, cid):
            scj_queue.delete_ticket(cid)
            continue
        if ticket.get("status") == "CLAIMING":
            scj_queue.delete_ticket(cid)
            continue
        if not scj_queue.ticket_takeable(ticket):
            continue
        ticket["status"] = "AUTHORING"
        ticket["owner_pid"] = os.getpid()
        scj_queue.save_ticket(ticket)
        _print_ready(ticket)
        print(f"RESUME {cid} (id already reserved; not claiming a new PDF)")
        return 0
    return None


def claim_new():
    state = load_state()
    seq = scj_queue.next_free_seq(state)
    cid = scj_queue.case_id_for(seq)
    done = processed_names()
    docket_blob = existing_dockets()
    skip = scj_queue.open_sources()

    while True:
        pending = pending_files(done, skip)
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

    placeholder = {
        "status": "CLAIMING",
        "case_id": cid,
        "next_seq": seq,
        "source": name,
    }
    scj_queue.save_ticket(placeholder, legacy=False)

    try:
        fp = extract(name, cid)
    except SystemExit:
        scj_queue.delete_ticket(cid)
        raise
    if not isinstance(fp, dict):
        fp = {}
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
    ik_cites = int(fp.get("ik_citation_count") or 0)
    text_cites = int(fp.get("text_citation_count") or 0)
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
        "ik_citation_count": ik_cites,
        "text_citation_count": text_cites,
        "out_json": f"supply-code/summaries/json/{cid}.json",
        "demoted": False,
    }
    if is_stencil:
        ticket["authoring"] = "stencil"
        ticket["stencil_family"] = stencil["family"]
        ticket["gate"] = "stencil"
        ticket["max_turns"] = 0
        ticket["catalog_hits"] = []
        ticket["prompt"] = "tools/scj_stencil.py"
    else:
        apply_llm_authoring(ticket, txt, fp)
    scj_queue.bump_next_seq(state, seq)
    scj_queue.save_state(state)
    scj_queue.save_ticket(ticket)
    _print_ready(ticket)
    return 0


def main(claim_new_only=False):
    if not claim_new_only:
        resumed = resume_open_ticket()
        if resumed is not None:
            return resumed
    return claim_new()


def apply_llm_authoring(ticket, txt, fp):
    """Fill short/full fields. Never stencil. Mutates ticket."""
    words = int(ticket.get("word_count") or fp.get("word_count") or 0)
    pages = ticket.get("page_count")
    if pages is None:
        pages = fp.get("page_count")
    cites = int(fp.get("citation_count") or ticket.get("citation_count") or 0)
    ensure_catalog()
    hits = catalog_hits(txt)
    ticket["catalog_hits"] = hits
    ticket["citation_count"] = cites
    ticket["ik_citation_count"] = int(fp.get("ik_citation_count") or 0)
    ticket["text_citation_count"] = int(fp.get("text_citation_count") or 0)
    if is_short(pages, words, cites):
        ticket["authoring"] = "short"
        ticket["gate"] = short_gate(pages, words, cites)
        ticket["max_turns"] = SHORT_TURNS
        ticket["prompt"] = "tools/prompts/next_case_short.txt"
        ticket.pop("catalog", None)
        ticket.pop("example", None)
    else:
        ticket["authoring"] = "full"
        ticket["gate"] = "full"
        ticket["max_turns"] = FULL_TURNS
        ticket["prompt"] = "tools/prompts/next_case_once.txt"
        ticket["catalog"] = "supply-code/jurisprudence/catalog.txt"
        ticket["example"] = "supply-code/summaries/json/SCJ-280.json"
    return ticket


def demote_ticket(ticket_file=None):
    """Stencil write failed: same extract, author with short/full. No grok skip."""
    path = ticket_file or TICKET
    if not os.path.exists(path):
        print("FAILED · no ticket to demote", file=sys.stderr)
        return 1
    with open(path, encoding="utf-8") as f:
        ticket = json.load(f)
    if ticket.get("status") not in ("READY", "AUTHORING", "CLAIMING") or not ticket.get("case_id"):
        print("FAILED · ticket not READY", file=sys.stderr)
        return 1
    cid = ticket["case_id"]
    txt_path = os.path.join(EXTRACTS, cid + ".txt")
    txt = ""
    if os.path.exists(txt_path):
        txt = open(txt_path, encoding="utf-8", errors="replace").read()
    fp_path = os.path.join(EXTRACTS, cid + ".fp.json")
    fp = {}
    if os.path.exists(fp_path):
        with open(fp_path, encoding="utf-8") as f:
            fp = json.load(f)
    prev = ticket.get("authoring") or "stencil"
    fam = ticket.get("stencil_family") or ""
    apply_llm_authoring(ticket, txt, fp)
    ticket["demoted"] = True
    ticket["demoted_from"] = prev
    ticket["stencil_family"] = fam
    scj_queue.save_ticket(ticket)
    print(f"DEMOTED {cid} {prev} -> {ticket['authoring']} "
          f"gate={ticket.get('gate')} family={fam or '-'} "
          f"pages={ticket.get('page_count')} words={ticket.get('word_count')} "
          f"citations={ticket.get('citation_count')}")
    return 0


def _run(args):
    if args.demote:
        return demote_ticket(args.ticket)
    return main(claim_new_only=args.claim_new)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demote", action="store_true",
                    help="rewrite current stencil ticket to short/full")
    ap.add_argument("--ticket", help="ticket JSON path (demote / resume)")
    ap.add_argument("--claim-new", action="store_true",
                    help="do not resume an open ticket; claim the next PDF")
    ap.add_argument("--no-lock", action="store_true",
                    help="skip the queue lock (tests only)")
    args = ap.parse_args()
    if args.no_lock:
        sys.exit(_run(args))
    with scj_lock.DirLock(scj_queue.LOCK_DIR):
        sys.exit(_run(args))
