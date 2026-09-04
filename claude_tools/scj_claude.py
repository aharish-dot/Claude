#!/usr/bin/env python3
"""Claude authoring pipeline for the claude_input/ queue (>10pp + wordiest cases).

Claude-owned (never touches Grok's input/ queue). Two modes, decided by the
queue manifest (supply-code/claude_input/_queue_manifest.json):
  * NEW     — a fresh judgment -> assign an id (fills the 707 gap first, then
              next_free_seq) and author a new record.
  * UPGRADE — a judgment already in the corpus (a lean Grok record) -> author a
              RICH replacement into the SAME existing case_id (no new id).

Chat flow (serial, one case at a time):
  1. python claude_tools/scj_claude.py claim --file <rel-in-claude_input>   [or --next]
       -> extracts text, reserves/attaches the id, writes tmp/CLAUDE_TICKET.json,
          prints READY <mode> <case_id> <source>.
  2. Claude reads supply-code/extracts/<id>.txt and writes
       supply-code/summaries/json/<id>.json in the RICH schema (see the handoff:
       + reusable_constructions[], holding_units[].evidence[], holding_units[].nature,
         related_cases[], pin_basis, source_file; model is set by finalize).
  3. python claude_tools/scj_claude.py finalize <case_id>
       -> renders with claude_tools/gen_scj.py, moves claude_input->processed,
          updates state (NEW appends; UPGRADE keeps id), rebuilds spine+catalog,
          commits (signed, model="Claude Opus 4.8") and pushes.

Reuses Grok's shared modules unmodified (scj_queue, scj_lock, finalize_scj helpers,
extract_judgment, build_supply_code, build_scj_catalog).
"""
from __future__ import annotations
import argparse, glob, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
CLAUDE_TOOLS = os.path.join(ROOT, "claude_tools")
sys.path.insert(0, TOOLS)
import scj_queue          # noqa: E402
import scj_lock           # noqa: E402
import finalize_scj as F  # noqa: E402  (reuse slug/pdf/chrome/coerce/check helpers)

SC = os.path.join(ROOT, "supply-code")
CQ = os.path.join(SC, "claude_input")
EXTRACTS = os.path.join(SC, "extracts")
JSON_DIR = os.path.join(SC, "summaries", "json")
STATE = os.path.join(SC, "state", "index.json")
MANIFEST = os.path.join(CQ, "_queue_manifest.json")
TICKET = os.path.join(SC, "tmp", "CLAUDE_TICKET.json")
BRANCH = "claude/supply-code-jurisprudence-design-yiwgen"
MODEL = "Claude Opus 4.8"


def die(msg):
    sys.exit(f"FAILED · {msg}")


def load_manifest():
    if not os.path.exists(MANIFEST):
        die(f"missing manifest {MANIFEST}")
    return json.load(open(MANIFEST, encoding="utf-8"))


def manifest_lookup(man):
    """rel-path -> {'mode','existing_case_id'?}. Order: big-new, wordy-new, upgrades LAST.

    User directive (2026-09): author the NEW cases first; drain the 'upgrade'
    bucket (rich rewrites of existing lean Grok records) at the end of the queue.
    """
    order, info = [], {}
    for e in man.get("new", []):
        p = e["path"]; order.append(p); info[p] = {"mode": "new"}
    for e in man.get("new_from_grok_top10pct", []):
        p = e["path"]; order.append(p); info[p] = {"mode": "new"}
    for e in man.get("upgrade", []):
        p = e["path"]; order.append(p)
        info[p] = {"mode": "upgrade", "existing_case_id":
                   e["existing_case_id"] if isinstance(e["existing_case_id"], str)
                   else e["existing_case_id"][0]}
    return order, info


def still_pending(rel):
    return os.path.exists(os.path.join(CQ, rel))


def next_new_id(state):
    """Fill the 707 gap first, else next free seq."""
    ids = {c.get("case_id") for c in state.get("cases", [])}
    if "SCJ-707" not in ids:
        return "SCJ-707"
    return scj_queue.case_id_for(scj_queue.next_free_seq(state))


def do_claim(args):
    man = load_manifest()
    order, info = manifest_lookup(man)
    rel = args.file
    if rel:
        rel = rel.replace("\\", "/")
        if rel.startswith("claude_input/"):
            rel = rel[len("claude_input/"):]
        if rel not in info:
            die(f"{rel} not in the Claude queue manifest")
        if not still_pending(rel):
            die(f"{rel} already processed (not in claude_input/)")
    else:  # --next
        rel = next((p for p in order if still_pending(p)), None)
        if not rel:
            print("NO_INPUT · Claude queue empty · stop")
            return 2
    mode = info[rel]["mode"]
    src_abs = os.path.join(CQ, rel)
    source_file = os.path.basename(rel)

    with scj_lock.DirLock(scj_queue.LOCK_DIR):
        state = scj_queue.load_state()
        if mode == "upgrade":
            cid = info[rel]["existing_case_id"]
            if not os.path.exists(os.path.join(JSON_DIR, cid + ".json")):
                die(f"upgrade target {cid}.json missing")
        else:
            cid = next_new_id(state)
            scj_queue.bump_next_seq(state, scj_queue.cid_seq(cid))
            scj_queue.save_state(state)

    os.makedirs(EXTRACTS, exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "extract_judgment.py"),
                        src_abs, EXTRACTS, cid], cwd=ROOT, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.strip())
    if r.returncode != 0:
        die("extract failed: " + (r.stderr or "")[:400])
    fp = {}
    fpp = os.path.join(EXTRACTS, cid + ".fp.json")
    if os.path.exists(fpp):
        fp = json.load(open(fpp, encoding="utf-8"))

    ticket = {"mode": mode, "case_id": cid, "source": rel, "source_file": source_file,
              "txt": f"supply-code/extracts/{cid}.txt", "fp": f"supply-code/extracts/{cid}.fp.json",
              "page_count": fp.get("page_count"), "word_count": fp.get("word_count"),
              "out_json": f"supply-code/summaries/json/{cid}.json"}
    os.makedirs(os.path.dirname(TICKET), exist_ok=True)
    json.dump(ticket, open(TICKET, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"READY mode={mode} {cid} pages={fp.get('page_count')} words={fp.get('word_count')} "
          f"source={rel}")
    print(f"  -> author supply-code/summaries/json/{cid}.json (rich schema), then "
          f"`python claude_tools/scj_claude.py finalize {cid}`")
    if mode == "upgrade":
        print(f"  UPGRADE: overwrite existing {cid}.json (same id, richer content).")
    return 0


def render_pdf(cid, rec_path, c):
    slug = F.slug_from_title(c.get("title") or cid)
    rel = F.digest_pdf_relpath(cid, slug, c.get("significance"))
    out = os.path.join(SC, "summaries", "pdf", *rel.split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    work = tempfile.mkdtemp(prefix="scjc_")
    html = os.path.join(work, cid + ".html")
    subprocess.run([sys.executable, os.path.join(CLAUDE_TOOLS, "gen_scj.py"), rec_path, html],
                   cwd=ROOT, check=True)
    chrome = F.find_chrome()
    ud = tempfile.mkdtemp(prefix="scjc_chrome_")
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--disable-dev-shm-usage", f"--user-data-dir={ud}",
                    "--no-pdf-header-footer", f"--print-to-pdf={out}", F.file_uri(html)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        die(f"digest PDF missing/too small: {out}")
    F.retire_other_digests(cid, out)
    return out, rel


def move_source_cq(rel):
    src = os.path.join(CQ, rel)
    dst = os.path.join(SC, "processed", rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and not os.path.exists(src):
        return
    if not os.path.exists(src):
        die(f"missing source in claude_input/: {rel}")
    os.replace(src, dst)


def do_finalize(args):
    cid = args.case_id
    if not os.path.exists(TICKET):
        die("no CLAUDE_TICKET.json; run claim first")
    tk = json.load(open(TICKET, encoding="utf-8"))
    if tk.get("case_id") != cid:
        die(f"ticket case_id {tk.get('case_id')} != {cid}")
    mode = tk.get("mode")
    rec = os.path.join(JSON_DIR, cid + ".json")
    if not os.path.exists(rec):
        die(f"author {rec} first")
    c = json.load(open(rec, encoding="utf-8"))

    # normalise + provenance
    F.coerce_record_shapes(c)
    F.inject_judgment_meta(c, cid, tk["source"])   # backfills page_count, significance/outcome
    c["model"] = MODEL
    c["source_file"] = tk.get("source_file") or c.get("source_file", "")
    json.dump(c, open(rec, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(rec, "a").write("\n")
    F.check_record(c, cid)

    pdf, pdf_name = render_pdf(cid, rec, c)
    print(f"  digest: {pdf}")
    move_source_cq(tk["source"])

    with scj_lock.DirLock(scj_queue.LOCK_DIR):
        state = scj_queue.load_state()
        ids = {x["case_id"] for x in state["cases"]}
        if mode == "new" and cid not in ids:
            state["cases"].append({"case_id": cid,
                                   "source_basename": tk.get("source_file", ""),
                                   "title": c.get("title", ""), "status": "done"})
        elif mode == "upgrade" and cid not in ids:
            die(f"upgrade target {cid} not in state")
        state["next_seq"] = scj_queue.next_seq_after_finalize(state)
        scj_queue.save_state(state)
        nxt = state["next_seq"]

    subprocess.run([sys.executable, os.path.join(TOOLS, "build_supply_code.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, os.path.join(TOOLS, "build_scj_catalog.py")], cwd=ROOT, check=True)

    rel = tk["source"]
    files = [f"supply-code/summaries/json/{cid}.json",
             f"supply-code/summaries/pdf/{pdf_name}",
             "supply-code/state/index.json",
             "supply-code/jurisprudence/index.json",
             "supply-code/jurisprudence/catalog.txt",
             f"supply-code/processed/{rel}"]
    subprocess.run(["git", "add", "--"] + files, cwd=ROOT, check=False)
    subprocess.run(["git", "add", "-u", "--", "supply-code/summaries/pdf",
                    f"supply-code/claude_input/{rel}"], cwd=ROOT, check=False)
    verb = "process" if mode == "new" else "upgrade"
    title = (c.get("title") or cid)[:80]
    msg = (f"supply-code: {verb} {cid} ({title})\n\n"
           f"Claude rich digest (mode={mode}, source {tk.get('source_file')}).\n\n"
           f"Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>\n"
           f"Claude-Session: https://claude.ai/code/session_011t8CKvMGHwszG3pZEexUw5")
    r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr).lower():
        print(r.stdout + r.stderr); die("git commit failed")
    if not args.no_push:
        for a in range(4):
            if subprocess.run(["git", "push", "-u", "origin", BRANCH], cwd=ROOT).returncode == 0:
                break
            __import__("time").sleep(2 ** (a + 1))
    try:
        os.remove(TICKET)
    except OSError:
        pass
    print(f"finalized {cid} (mode={mode}); next_seq={nxt}")
    print(f"STATUS: {cid} · {c.get('title','')[:50]} · {str(c.get('disposition',''))[:60]} · next_seq={nxt} · digest ok")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("claim"); c.add_argument("--file"); c.add_argument("--next", action="store_true")
    f = sub.add_parser("finalize"); f.add_argument("case_id"); f.add_argument("--no-push", action="store_true")
    args = ap.parse_args()
    if args.cmd == "claim":
        return do_claim(args)
    return do_finalize(args)


if __name__ == "__main__":
    sys.exit(main())
