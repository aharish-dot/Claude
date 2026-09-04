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
import argparse, glob, json, os, re, subprocess, sys, tempfile
from shutil import which

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scj_lock
import scj_queue

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
    s = title or ""
    # M/S (Messrs) must not become M_S — that looks like the significant marker.
    s = re.sub(r"\bM\s*[./]\s*[Ss]\.?\b", "MS", s)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")[:60].rstrip("_")
    return s or "untitled"


def digest_pdf_basename(cid, slug, significance=None):
    """SCJ-NNN_S_<slug>.pdf when significant, else SCJ-NNN_<slug>.pdf."""
    raw = str(significance or "").strip().lower()
    if SIG_ALIASES.get(raw) == "significant":
        return f"{cid}_S_{slug}.pdf"
    return f"{cid}_{slug}.pdf"


def digest_pdf_subdir(cid, significance=None):
    """Folder under summaries/pdf/. Significant → significant/; else 001-1000, 1001-2000, …"""
    raw = str(significance or "").strip().lower()
    if SIG_ALIASES.get(raw) == "significant":
        return "significant"
    try:
        seq = int(str(cid).split("-")[1])
    except (IndexError, ValueError):
        seq = 1
    if seq < 1:
        seq = 1
    lo = ((seq - 1) // 1000) * 1000 + 1
    hi = lo + 999
    return f"{lo:03d}-{hi}"


def digest_pdf_relpath(cid, slug, significance=None):
    """Path relative to summaries/pdf/, e.g. significant/SCJ-401_S_….pdf."""
    return digest_pdf_subdir(cid, significance) + "/" + digest_pdf_basename(
        cid, slug, significance
    )


def retire_other_digests(cid, keep_path):
    """Remove leftover digest PDFs for this id (old slug, missing _S_, or old folder)."""
    root = os.path.join(SC, "summaries", "pdf")
    retired = []
    if not os.path.isdir(root):
        return retired
    keep_path = os.path.normpath(os.path.abspath(keep_path))
    prefix = cid + "_"
    for dirpath, _dirs, filenames in os.walk(root):
        for n in filenames:
            if not n.endswith(".pdf") or not n.startswith(prefix):
                continue
            path = os.path.normpath(os.path.abspath(os.path.join(dirpath, n)))
            if path == keep_path:
                continue
            try:
                os.remove(path)
                retired.append(
                    os.path.relpath(path, ROOT).replace("\\", "/")
                )
            except OSError:
                pass
    return retired


def find_chrome():
    """Resolve a headless Chrome/Chromium binary on Windows or Linux."""
    env = os.environ.get("CHROME")
    if env and os.path.exists(env):
        return env
    for p in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ):
        if p and os.path.exists(p):
            return p
    for c in (
        "chromium", "chromium-browser", "google-chrome",
        "google-chrome-stable", "chrome", "msedge",
    ):
        w = which(c)
        if w:
            return w
    home = os.path.expanduser("~")
    globs = (
        os.path.join(home, ".cache", "ms-playwright", "chromium-*",
                     "chrome-linux", "chrome"),
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        os.path.join(home, ".cache", "ms-playwright",
                     "chromium_headless_shell-*",
                     "chrome-headless-shell-linux64", "chrome-headless-shell"),
    )
    fixed = (
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/snap/bin/chromium",
    )
    candidates = list(fixed)
    for pattern in globs:
        candidates.extend(sorted(glob.glob(pattern), reverse=True))
    for p in candidates:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    die("Chrome/Chromium not found — install Chromium or set CHROME to the binary")


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


def _paras_to_str(p):
    if p is None:
        return None, False
    if isinstance(p, list):
        return ", ".join(str(x).strip() for x in p if str(x).strip()), True
    if isinstance(p, str):
        return p, False
    return str(p), True


def coerce_record_shapes(c):
    """Normalize known LLM shape drift. Does not invent holdings or citations.

    Returns a list of field paths that changed (empty if the record was already
    generator-clean). Loop logs this so we can see whether the prompt fix
    actually stopped the two-retry pattern.
    """
    changed = []
    for i, u in enumerate(c.get("holding_units") or []):
        if not isinstance(u, dict):
            continue
        new, did = _paras_to_str(u.get("paras"))
        if did:
            u["paras"] = new
            changed.append(f"holding_units[{i}].paras")
    for i, t in enumerate(c.get("principle_tags") or []):
        if not isinstance(t, dict):
            continue
        new, did = _paras_to_str(t.get("paras"))
        if did:
            t["paras"] = new
            changed.append(f"principle_tags[{i}].paras")
    nd = c.get("not_decided")
    if isinstance(nd, list):
        new_nd = []
        for i, n in enumerate(nd):
            if isinstance(n, str):
                new_nd.append({"point": n.strip()} if n.strip() else {"point": n})
                changed.append(f"not_decided[{i}]")
            elif isinstance(n, dict):
                if not n.get("point") and n.get("issue"):
                    n = dict(n)
                    n["point"] = n.get("issue") or ""
                    changed.append(f"not_decided[{i}].issue")
                new, did = _paras_to_str(n.get("paras")) if isinstance(n, dict) else (None, False)
                if did:
                    n["paras"] = new
                    changed.append(f"not_decided[{i}].paras")
                new_nd.append(n)
            else:
                new_nd.append(n)
        c["not_decided"] = new_nd
    return changed


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
    ticket = scj_queue.load_ticket(scj_queue.ticket_path(cid))
    if ticket:
        model = "stencil" if (ticket.get("authoring") or "") == "stencil" else "Grok 4.6"
        if c.get("model") != model:
            c["model"] = model
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
    rc = c.get("reusable_constructions")
    sig = SIG_ALIASES.get(str(c.get("significance") or "").strip().lower())
    if sig == "significant":
        if not isinstance(rc, list) or not rc:
            die("significant records require reusable_constructions[] "
                "([{construction, paras}, …])")
    if rc is not None:
        if not isinstance(rc, list):
            die("reusable_constructions must be a list")
        for i, r in enumerate(rc):
            if not isinstance(r, dict) or not str(r.get("construction") or "").strip():
                die(f"reusable_constructions[{i}] must be {{construction, paras}}")
            p = r.get("paras")
            if p is not None and not isinstance(p, str):
                die(f"reusable_constructions[{i}].paras must be a string, "
                    f"not {type(p).__name__}")


def render_pdf(cid, slug, rec, chrome, significance=None):
    work = tempfile.mkdtemp(prefix="scj_html_")
    html = os.path.join(work, cid + ".html")
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "gen_scj.py"), rec, html],
        cwd=ROOT, check=True,
    )
    rel = digest_pdf_relpath(cid, slug, significance)
    out = os.path.join(SC, "summaries", "pdf", *rel.split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ud = tempfile.mkdtemp(prefix="scj_chrome_")
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--disable-dev-shm-usage", f"--user-data-dir={ud}",
         "--no-pdf-header-footer", f"--print-to-pdf={out}", file_uri(html)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        die(f"digest PDF missing or too small: {out}")
    retire_other_digests(cid, out)
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
    state["next_seq"] = scj_queue.next_seq_after_finalize(state)
    scj_queue.save_state(state, path)
    return state["next_seq"]


def git_commit_push(cid, title, pdf_rel, src, do_push):
    rel, _ = _src_parts(src)
    files = [
        f"supply-code/summaries/json/{cid}.json",
        os.path.relpath(pdf_rel, ROOT).replace("\\", "/"),
        "supply-code/state/index.json",
        "supply-code/jurisprudence/index.json",
        "supply-code/jurisprudence/catalog.txt",
        f"supply-code/processed/{rel}",
    ]
    subprocess.run(["git", "add", "--"] + files, cwd=ROOT, check=False)
    subprocess.run(
        ["git", "add", "-u", "--", "supply-code/summaries/pdf"],
        cwd=ROOT, check=False,
    )
    # Source PDFs now live on GitHub in input/. Stage the deletion so the
    # blob moves to processed/ instead of remaining in both trees.
    subprocess.run(
        ["git", "add", "-u", "--", f"supply-code/input/{rel}"],
        cwd=ROOT, check=False,
    )
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
    coerced = coerce_record_shapes(c)
    meta = inject_judgment_meta(c, cid, src)
    if coerced or meta:
        with open(rec, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2, ensure_ascii=False)
            f.write("\n")
        if coerced:
            print("  coerce: " + "; ".join(coerced))
    check_record(c, cid)
    title = c.get("title") or cid
    slug = slug_from_title(title)

    chrome = find_chrome()
    pdf = render_pdf(cid, slug, rec, chrome, c.get("significance"))
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
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import log_scj_review
        log_scj_review.append({
            "event": "finalize",
            "case_id": cid,
            "source": src,
            "coerce": coerced,
            "outcome": c.get("outcome"),
            "significance": c.get("significance"),
            "pages": c.get("page_count"),
        })
    except Exception:
        pass
    scj_queue.delete_ticket(cid)
    print(f"finalized {cid}; next_seq={nxt}")


def _main():
    main()


if __name__ == "__main__":
    with scj_lock.DirLock(scj_queue.LOCK_DIR):
        _main()
