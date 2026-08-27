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
SC = os.path.join(ROOT, "supply-code")
INPUT = os.path.join(SC, "input")
PROCESSED = os.path.join(SC, "processed")
STATE = os.path.join(SC, "state", "index.json")
SUMM = os.path.join(SC, "summaries", "json")
EXTRACTS = os.path.join(SC, "extracts")
TICKET = os.path.join(SC, "tmp", "NEXT_TICKET.json")
SKIP_NAMES = {"WRIC(A)_20210_2012.pdf"}  # already SCJ-273

FN_DOCKET = re.compile(r"_(\d+)_(\d{4})\.pdf$", re.I)


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
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    if r.stdout:
        print(r.stdout.strip())
    fp_path = os.path.join(EXTRACTS, cid + ".fp.json")
    fp = json.load(open(fp_path, encoding="utf-8")) if os.path.exists(fp_path) else {}
    return fp


def ensure_catalog():
    cat = os.path.join(SC, "jurisprudence", "catalog.txt")
    if not os.path.exists(cat):
        subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "build_scj_catalog.py")],
            cwd=ROOT, check=True,
        )


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
    ensure_catalog()
    ticket = {
        "status": "READY",
        "case_id": cid,
        "next_seq": seq,
        "source": name,
        "txt": f"supply-code/extracts/{cid}.txt",
        "fp": f"supply-code/extracts/{cid}.fp.json",
        "word_count": fp.get("word_count", 0),
        "citation_count": fp.get("citation_count", 0),
        "catalog": "supply-code/jurisprudence/catalog.txt",
        "example": "supply-code/summaries/json/SCJ-280.json",
        "out_json": f"supply-code/summaries/json/{cid}.json",
    }
    os.makedirs(os.path.dirname(TICKET), exist_ok=True)
    with open(TICKET, "w", encoding="utf-8") as f:
        json.dump(ticket, f, indent=2)
        f.write("\n")
    print(f"READY {cid} source={name} words={ticket['word_count']} → {TICKET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
