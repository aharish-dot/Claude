#!/usr/bin/env python3
"""Pick the next unique pending PDF, extract text, write a work ticket.

Usage:  python tools/prepare_next_scj.py
Exit 0  ticket at supply-code/tmp/NEXT_TICKET.json
Exit 2  no unique pending input (print NO_INPUT)

Does not bump next_seq (finalize_scj.py does that). Retires filename and
docket duplicates to processed/ without assigning an id.
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
SHORT_TURNS = 15
FULL_TURNS = 50

FN_DOCKET = re.compile(r"_(\d+)_(\d{4})\.pdf$", re.I)
CLAUSE_NUM = re.compile(r"\b\d+\.\d+(?:\([A-Za-z0-9]+\))*")
SECTION_NUM = re.compile(r"(?i)\b(?:sections?|s\.)\s*(\d+[A-Z]?(?:\(\d+[A-Z]?\))*)")


def load_state():
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def processed_names():
    if not os.path.isdir(PROCESSED):
        return set()
    return {n for n in os.listdir(PROCESSED) if n != ".gitkeep"}


def pending_files(done):
    if not os.path.isdir(INPUT):
        return []
    out = []
    for n in sorted(os.listdir(INPUT)):
        p = os.path.join(INPUT, n)
        if not os.path.isfile(p) or n == ".gitkeep":
            continue
        if n in SKIP_NAMES or n in done or re.search(r" \(1\)\.pdf$", n):
            continue
        out.append(n)
    return out


def docket_needles(filename):
    m = FN_DOCKET.search(filename)
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


def retire(name, reason):
    src = os.path.join(INPUT, name)
    dst = os.path.join(PROCESSED, name)
    os.makedirs(PROCESSED, exist_ok=True)
    if os.path.exists(src):
        os.replace(src, dst)
    print(f"retired duplicate {name} ({reason}) → processed/")


def extract(src_name, cid):
    os.makedirs(EXTRACTS, exist_ok=True)
    src = os.path.join(INPUT, src_name)
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


def is_short(page_count, word_count):
    if isinstance(page_count, int) and page_count <= SHORT_PAGES:
        return True
    return int(word_count or 0) <= SHORT_WORDS


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
        hit = is_docket_dup(name, docket_blob)
        if hit:
            retire(name, f"docket already in corpus: {hit}")
            done.add(name)
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
    )
    short = is_short(pages, words)
    ticket = {
        "status": "READY",
        "case_id": cid,
        "next_seq": seq,
        "source": name,
        "txt": f"supply-code/extracts/{cid}.txt",
        "fp": f"supply-code/extracts/{cid}.fp.json",
        "word_count": words,
        "page_count": pages,
        "citation_count": fp.get("citation_count", 0),
        "out_json": f"supply-code/summaries/json/{cid}.json",
    }
    if is_stencil:
        ticket["authoring"] = "stencil"
        ticket["stencil_family"] = stencil["family"]
        ticket["max_turns"] = 0
        ticket["catalog_hits"] = []
        ticket["prompt"] = "tools/scj_stencil.py"
    else:
        ensure_catalog()
        hits = catalog_hits(txt)
        ticket["catalog_hits"] = hits
        if short:
            ticket["authoring"] = "short"
            ticket["max_turns"] = SHORT_TURNS
            ticket["prompt"] = "tools/prompts/next_case_short.txt"
        else:
            ticket["authoring"] = "full"
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
    print(f"READY {cid} authoring={ticket['authoring']}{extra} source={name} "
          f"pages={pages} words={words} catalog_hits={len(ticket.get('catalog_hits') or [])} "
          f"→ {TICKET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
