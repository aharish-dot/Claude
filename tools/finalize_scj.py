#!/usr/bin/env python3
"""Mechanical finalize after the lean JSON is written. No LLM.

Usage:
  python tools/finalize_scj.py SCJ-283 --source "WRIC(A)_12303_2026.pdf"
  python tools/finalize_scj.py SCJ-283 --source "WRIC(A)_12303_2026.pdf" --no-push
  python tools/finalize_scj.py SCJ-283 --source "WRIC(A)_12303_2026.pdf" --no-git

Does: schema-gotcha check → gen_scj.py → Chrome PDF → move input→processed
→ append state → bump next_seq → build_supply_code.py → catalog → git commit
(and push unless --no-push). Idempotent if re-run on an already-finalized case.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from shutil import which

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "supply-code")
BRANCH = "claude/supply-code-jurisprudence-design-yiwgen"
SIG_ALIASES = {
    "significant": "significant",
    "ordinary": "ordinary",
    "normal": "ordinary",
    "procedural": "procedural",
}
# Who succeeded on the electricity dispute (not CPC party role).
# consumer = the occupier/applicant got the relief; licensee = discom succeeded;
# alternate_remedy = relegated to a Code/Act channel without a merits win.
OUTCOME_ALIASES = {
    "consumer": "consumer",
    "petitioner": "consumer",
    "applicant": "consumer",
    "licensee": "licensee",
    "discom": "licensee",
    "supply_company": "licensee",
    "alternate_remedy": "alternate_remedy",
    "relegated": "alternate_remedy",
    "relegation": "alternate_remedy",
    "pending": "pending",
    "interlocutory": "pending",
    "none": "none",
    "infructuous": "none",
    "split": "split",
}


def die(msg):
    sys.exit(f"FAILED · {msg}")


def slug_from_title(title):
    s = re.sub(r"[^A-Za-z0-9]+", "_", title or "")
    s = re.sub(r"_+", "_", s).strip("_")[:60].rstrip("_")
    return s or "untitled"


def find_chrome():
    if os.environ.get("CHROME") and os.path.exists(os.environ["CHROME"]):
        return os.environ["CHROME"]
    for p in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ):
        if p and os.path.exists(p):
            return p
    for c in ("chromium", "google-chrome", "chrome", "msedge"):
        w = which(c)
        if w:
            return w
    die("Chrome/Chromium not found — set CHROME")


def file_uri(path):
    path = os.path.abspath(path).replace("\\", "/")
    if not path.startswith("/"):
        path = "/" + path
    return "file://" + path


def pdf_page_count(path):
    try:
        import fitz
        d = fitz.open(path)
        n = d.page_count
        d.close()
        return n
    except Exception:
        return None


def inject_judgment_meta(c, cid, src):
    """Backfill page_count from the source PDF / fingerprint; normalise significance.

    page_count is the source judgment's page count (not the digest). significance is
    significant | ordinary | procedural (normal is an alias of ordinary). Old records
    without these fields still finalize; the digest eyebrow just omits the blanks.
    """
    changed = False
    pc = None
    fp_path = os.path.join(SC, "extracts", cid + ".fp.json")
    if os.path.exists(fp_path):
        try:
            fp = json.load(open(fp_path, encoding="utf-8"))
            pc = fp.get("page_count")
        except (OSError, json.JSONDecodeError):
            pc = None
    if not isinstance(pc, int) or pc < 1:
        rel = src.replace("\\", "/").lstrip("/")
        parts = rel.split("/") if rel else []
        for folder in ("input", "processed"):
            p = os.path.join(SC, folder, *parts) if parts else os.path.join(SC, folder)
            if os.path.exists(p) and p.lower().endswith(".pdf"):
                pc = pdf_page_count(p)
                if isinstance(pc, int) and pc > 0:
                    break
    if isinstance(pc, int) and pc > 0 and c.get("page_count") != pc:
        c["page_count"] = pc
        changed = True
    raw = c.get("significance")
    if raw is not None and str(raw).strip():
        key = str(raw).strip().lower()
        if key not in SIG_ALIASES:
            die("significance must be significant|ordinary|procedural "
                f"(normal is accepted as ordinary), got {raw!r}")
        mapped = SIG_ALIASES[key]
        if c.get("significance") != mapped:
            c["significance"] = mapped
            changed = True
    raw_o = c.get("outcome")
    if raw_o is not None and str(raw_o).strip():
        key = str(raw_o).strip().lower().replace(" ", "_").replace("-", "_")
        if key not in OUTCOME_ALIASES:
            die("outcome must be consumer|licensee|alternate_remedy|pending|none|split "
                "(petitioner/discom/relegated/interlocutory are aliases), got "
                f"{raw_o!r}")
        mapped = OUTCOME_ALIASES[key]
        if c.get("outcome") != mapped:
            c["outcome"] = mapped
            changed = True
    return changed


def check_record(c, cid):
    if c.get("case_id") != cid:
        die(f"record case_id {c.get('case_id')!r} != {cid}")
    for k in ("title", "court", "disposition", "headnote", "holding_units"):
        if not c.get(k):
            die(f"missing/empty field: {k}")
    pc = c.get("page_count")
    if pc is not None and (not isinstance(pc, int) or pc < 1):
        die(f"page_count must be a positive integer, got {pc!r}")
    raw = c.get("significance")
    if raw is not None and str(raw).strip():
        if str(raw).strip().lower() not in SIG_ALIASES:
            die("significance must be significant|ordinary|procedural "
                f"(normal is accepted as ordinary), got {raw!r}")
    raw_o = c.get("outcome")
    try:
        seq = int(str(cid).split("-")[1])
    except (IndexError, ValueError):
        seq = 0
    if seq >= 301 and not (raw_o and str(raw_o).strip()):
        die("outcome required on SCJ-301+ "
            "(consumer|licensee|alternate_remedy|pending|none|split)")
    if raw_o is not None and str(raw_o).strip():
        key = str(raw_o).strip().lower().replace(" ", "_").replace("-", "_")
        if key not in OUTCOME_ALIASES:
            die("outcome must be consumer|licensee|alternate_remedy|pending|none|split "
                f"(petitioner/discom/relegated/interlocutory are aliases), got {raw_o!r}")
    for i, a in enumerate(c.get("authorities") or []):
        cb = a.get("cited_by")
        if cb is not None and not isinstance(cb, str):
            die(f"authorities[{i}].cited_by must be a string, not {type(cb).__name__}")
    for i, t in enumerate(c.get("principle_tags") or []):
        la = t.get("lead_authorities") or []
        if not isinstance(la, list):
            die(f"principle_tags[{i}].lead_authorities must be a list")
        for j, x in enumerate(la):
            if not isinstance(x, dict) or "name" not in x:
                die(f"principle_tags[{i}].lead_authorities[{j}] must be {{name, docid}}")


def render_pdf(cid, slug, rec, chrome):
    work = tempfile.mkdtemp(prefix="scj_html_")
    html = os.path.join(work, cid + ".html")
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "gen_scj.py"), rec, html],
        cwd=ROOT, check=True,
    )
    out_dir = os.path.join(SC, "summaries", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{cid}_{slug}.pdf")
    ud = tempfile.mkdtemp(prefix="scj_chrome_")
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         f"--user-data-dir={ud}", "--no-pdf-header-footer",
         f"--print-to-pdf={out}", file_uri(html)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        die(f"digest PDF missing or too small: {out}")
    return out


def _src_parts(src):
    rel = (src or "").replace("\\", "/").lstrip("/")
    return rel, (rel.split("/") if rel else [])


def move_source(src):
    rel, parts = _src_parts(src)
    src_path = os.path.join(SC, "input", *parts) if parts else os.path.join(SC, "input")
    dst_path = os.path.join(SC, "processed", *parts) if parts else os.path.join(SC, "processed")
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    if os.path.exists(dst_path) and not os.path.exists(src_path):
        print(f"  source already in processed/{rel}")
        return
    if not os.path.exists(src_path):
        die(f"missing input source: supply-code/input/{rel}")
    os.replace(src_path, dst_path)


def update_state(cid, src, title, c):
    path = os.path.join(SC, "state", "index.json")
    state = json.load(open(path, encoding="utf-8"))
    ids = {x["case_id"] for x in state["cases"]}
    rel, _ = _src_parts(src)
    if cid not in ids:
        state["cases"].append({
            "case_id": cid,
            "source_basename": os.path.basename(rel),
            "title": title,
            "status": "done",
        })
    maxseq = max(int(x["case_id"].split("-")[1]) for x in state["cases"])
    state["next_seq"] = maxseq + 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return state["next_seq"]


def git_commit_push(cid, title, pdf_rel, src, do_push):
    rel, _ = _src_parts(src)
    files = [
        f"supply-code/summaries/json/{cid}.json",
        f"supply-code/summaries/pdf/{os.path.basename(pdf_rel)}",
        "supply-code/state/index.json",
        "supply-code/jurisprudence/index.json",
        "supply-code/jurisprudence/catalog.txt",
        f"supply-code/processed/{rel}",
    ]
    subprocess.run(["git", "add", "--"] + files, cwd=ROOT, check=False)
    msg = f"supply-code: process {cid} ({title[:80]})"
    r = subprocess.run(
        ["git", "commit", "-m", msg], cwd=ROOT,
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        err = (r.stdout or "") + (r.stderr or "")
        if "nothing to commit" in err.lower() or "no changes added" in err.lower():
            print("  git: nothing to commit (already finalized)")
            return
        print(err)
        die("git commit failed")
    print(f"  commit: {msg}")
    if do_push:
        subprocess.run(
            ["git", "push", "-u", "origin", BRANCH],
            cwd=ROOT, check=True,
        )
        print(f"  pushed {BRANCH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case_id")
    ap.add_argument(
        "--source",
        required=True,
        help="path relative to supply-code/input/ (may include a year subfolder)",
    )
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()
    cid, src = args.case_id, args.source

    rec = os.path.join(SC, "summaries", "json", cid + ".json")
    if not os.path.exists(rec):
        die(f"missing record {rec}")
    c = json.load(open(rec, encoding="utf-8"))
    if inject_judgment_meta(c, cid, src):
        with open(rec, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2, ensure_ascii=False)
            f.write("\n")
    check_record(c, cid)
    title = c.get("title") or cid
    slug = slug_from_title(title)

    chrome = find_chrome()
    pdf = render_pdf(cid, slug, rec, chrome)
    print(f"  digest: {pdf}")
    move_source(src)
    nxt = update_state(cid, src, title, c)
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "build_supply_code.py")],
        cwd=ROOT, check=True,
    )
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "build_scj_catalog.py")],
        cwd=ROOT, check=True,
    )
    if not args.no_git:
        git_commit_push(cid, title, pdf, src, do_push=not args.no_push)
    print(f"finalized {cid}; next_seq={nxt}")


if __name__ == "__main__":
    main()
