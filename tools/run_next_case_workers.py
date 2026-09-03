#!/usr/bin/env python3
"""Parallel Supply Code loop: N grok workers, serial claim + finalize.

Usage:
  python tools/run_next_case_workers.py --count 50 --workers 2
  ./tools/run_next_case_loop.sh --count 50 --workers 2
  powershell -File tools/run_next_case_loop.ps1 -Count 50 -Workers 2

Claim (id + PDF) and finalize (Chrome/git) take the queue lock so SCJ ids
and git never collide. Authoring (stencil or grok -p) runs in a thread pool
and writes JSON only. A worker that finishes authoring is replaced immediately
with the next case; Chrome/git of the finished case run on the side.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import log_scj_review
import scj_lock
import scj_queue

SC = os.path.join(ROOT, "supply-code")
PREPARE = os.path.join(ROOT, "tools", "prepare_next_scj.py")
FINALIZE = os.path.join(ROOT, "tools", "finalize_scj.py")
STENCIL = os.path.join(ROOT, "tools", "scj_stencil.py")
PROMPT_FULL = os.path.join(ROOT, "tools", "prompts", "next_case_once.txt")
PROMPT_SHORT = os.path.join(ROOT, "tools", "prompts", "next_case_short.txt")
MAX_WORKERS = 4


def log(msg: str, log_file: str | None = None) -> None:
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def find_grok() -> str:
    w = shutil.which("grok")
    if w:
        return w
    cand = os.path.join(os.path.expanduser("~"), ".grok", "bin", "grok.exe")
    if os.path.exists(cand):
        return cand
    cand2 = os.path.join(os.path.expanduser("~"), ".grok", "bin", "grok")
    if os.path.exists(cand2):
        return cand2
    raise SystemExit(
        "grok not found on PATH. Install Grok CLI and add ~/.grok/bin "
        "(Windows: %USERPROFILE%\\.grok\\bin) to PATH."
    )


def run_logged(args: list[str], case_log: str, cwd: str = ROOT) -> int:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    with open(case_log, "a", encoding="utf-8") as f:
        f.write(f"$ {' '.join(args)}\n")
        f.flush()
        p = subprocess.Popen(
            args, cwd=cwd, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
        assert p.stdout is not None
        for line in p.stdout:
            sys.stdout.write(line)
            f.write(line)
        return p.wait() or 0


def load_ticket_file(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ticket_rel(cid: str) -> str:
    return f"supply-code/tmp/tickets/{cid}.json"


def json_exists(cid: str) -> bool:
    p = scj_queue.json_path(cid)
    return os.path.exists(p) and os.path.getsize(p) > 50


def next_seq() -> int:
    return int(scj_queue.load_state().get("next_seq") or 0)


def case_done(cid: str) -> bool:
    return scj_queue.case_is_done(scj_queue.load_state(), cid)


def prepare_claim(py: str) -> tuple[int, dict | None, str]:
    r = subprocess.run(
        [py, PREPARE, "--claim-new"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 2:
        return 2, None, out
    if r.returncode != 0:
        return r.returncode or 1, None, out
    ticket = load_ticket_file(scj_queue.TICKET_LEGACY)
    if ticket and ticket.get("status") == "READY":
        return 0, ticket, out
    cid = None
    for line in out.splitlines():
        if line.startswith("READY "):
            cid = line.split()[1]
            break
    if cid:
        ticket = load_ticket_file(scj_queue.ticket_path(cid))
        if ticket and ticket.get("status") == "READY":
            return 0, ticket, out
    return 1, None, out


def author_one(ticket: dict, grok: str, py: str, case_log: str,
               max_turns: int | None) -> dict:
    """Write summaries/json/<cid>.json. Does not finalize."""
    cid = ticket["case_id"]
    tpath = scj_queue.ticket_path(cid)
    authoring = ticket.get("authoring") or "full"
    demoted = 0
    did_stencil = 0
    result = {
        "ok": False, "authoring": authoring, "demoted": 0, "grok": 0,
        "did_stencil": 0, "exit": 0,
    }
    if json_exists(cid):
        result["ok"] = True
        result["skipped"] = True
        return result

    if authoring == "stencil":
        code = run_logged(
            [py, STENCIL, "--write", cid, "--ticket", tpath, "--force"],
            case_log,
        )
        if code == 0 and json_exists(cid):
            result["ok"] = True
            result["did_stencil"] = 1
            result["grok"] = 0
            return result
        code = run_logged([py, PREPARE, "--demote", "--ticket", tpath], case_log)
        ticket = load_ticket_file(tpath) or ticket
        authoring = ticket.get("authoring") or ""
        if authoring in ("", "stencil"):
            result["exit"] = code or 1
            return result
        demoted = 1
        result["authoring"] = authoring
        result["demoted"] = 1

    base_path = PROMPT_SHORT if authoring == "short" else PROMPT_FULL
    with open(base_path, encoding="utf-8") as f:
        base = f.read()
    out_json = ticket.get("out_json") or f"supply-code/summaries/json/{cid}.json"
    body = scj_queue.make_json_only_prompt(base, ticket_rel(cid), cid, out_json)
    prompt_path = scj_queue.write_worker_prompt(cid, body)
    turns = 50
    if max_turns is not None:
        turns = max_turns
    elif ticket.get("max_turns"):
        turns = int(ticket["max_turns"])
    grok_args = [
        grok, "--cwd", ROOT, "--prompt-file", prompt_path,
        "--permission-mode", "bypassPermissions", "--always-approve",
        "--max-turns", str(turns), "--output-format", "plain", "--no-auto-update",
    ]
    code = run_logged(grok_args, case_log)
    result["exit"] = code
    result["grok"] = 1
    result["ok"] = json_exists(cid)
    result["did_stencil"] = did_stencil
    result["demoted"] = demoted
    result["authoring"] = authoring
    return result


def finalize_one(ticket: dict, py: str, case_log: str, no_push: bool) -> int:
    args = [py, FINALIZE, ticket["case_id"], "--source", ticket["source"]]
    if no_push:
        args.append("--no-push")
    return run_logged(args, case_log)


def tail(path: str, n: int = 8) -> str:
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        return " | ".join(lines[-n:])
    except OSError:
        return ""


def resume_tickets() -> list[dict]:
    with scj_lock.DirLock(scj_queue.LOCK_DIR):
        state = scj_queue.load_state()
        out = []
        for t in scj_queue.open_tickets():
            cid = t.get("case_id")
            if not cid:
                continue
            if t.get("status") == "CLAIMING":
                scj_queue.delete_ticket(cid)
                continue
            if scj_queue.case_is_done(state, cid):
                scj_queue.delete_ticket(cid)
                continue
            if not scj_queue.ticket_takeable(t):
                continue
            t["status"] = "AUTHORING"
            t["owner_pid"] = os.getpid()
            scj_queue.save_ticket(t, legacy=False)
            out.append(t)
        return out


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--max-turns", type=int, default=None)
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--repo-root", default="")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    repo = args.repo_root or ROOT
    os.chdir(repo)
    os.environ["PYTHONUTF8"] = "1"

    workers = args.workers
    if workers < 1:
        raise SystemExit("--workers must be >= 1")
    if workers > MAX_WORKERS:
        print(f"clamping --workers {workers} -> {MAX_WORKERS}", flush=True)
        workers = MAX_WORKERS

    py = sys.executable
    log_dir = os.path.join(SC, "tmp", "loop_logs")
    os.makedirs(log_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"next_case_loop_{stamp}.log")

    def L(msg: str) -> None:
        log(msg, log_file)

    grok = find_grok()
    from finalize_scj import find_chrome
    chrome = find_chrome()

    L(f"Repo: {repo}")
    L(f"Grok: {grok}")
    L(f"Chrome: {chrome}")
    L(f"Count: {args.count} | Workers: {workers} | MaxTurns: "
      f"{args.max_turns if args.max_turns is not None else 'ticket'} | "
      f"NoPush: {args.no_push} | Log: {log_file}")
    L(f"Starting next_seq={next_seq()}")

    if args.dry_run:
        L("DRY-RUN: claim under lock -> stencil or grok (JSON only) x workers")
        L("DRY-RUN: next case is claimed as soon as an author slot frees")
        L("DRY-RUN: serial finalize_scj.py (Chrome/git/index) does not block claiming")
        return 0

    ok = 0
    fail = 0
    claimed = 0
    no_input = False
    prep_fail_streak = 0
    author_fail_streak = 0
    inflight = {}
    pending_finalize = []
    seq = 0

    resumes = resume_tickets()
    if resumes:
        L(f"RESUME {len(resumes)} open ticket(s): "
          + ", ".join(t["case_id"] for t in resumes))

    def submit_ticket(ex: ThreadPoolExecutor, ticket: dict) -> None:
        nonlocal seq, claimed
        seq += 1
        claimed += 1
        cid = ticket["case_id"]
        case_log = os.path.join(
            log_dir, f"case_{seq:02d}_{cid}_{stamp}.log"
        )
        ticket["status"] = "AUTHORING"
        ticket["owner_pid"] = os.getpid()
        scj_queue.save_ticket(ticket, legacy=False)
        L(f"===== CASE {seq} / {args.count} | {cid} "
          f"authoring={ticket.get('authoring')} source={ticket.get('source')} "
          f"pages={ticket.get('page_count')} words={ticket.get('word_count')} "
          f"workers={workers} =====")
        fut = ex.submit(
            author_one, ticket, grok, py, case_log, args.max_turns
        )
        inflight[fut] = {
            "ticket": ticket, "case_log": case_log, "i": seq,
            "t0": time.time(),
        }

    def try_claim(ex: ThreadPoolExecutor) -> None:
        nonlocal no_input, prep_fail_streak
        if no_input or claimed >= args.count:
            return
        if len(inflight) >= workers:
            return
        code, ticket, out = prepare_claim(py)
        for line in (out or "").splitlines():
            L(line)
        if code == 2:
            no_input = True
            L(f"STOP: prepare reported NO_INPUT (next_seq={next_seq()})")
            return
        if code != 0 or not ticket:
            prep_fail_streak += 1
            L(f"FAIL prepare exit={code}")
            if prep_fail_streak >= 3:
                no_input = True
                L("STOP: prepare failed 3 times in a row")
            return
        prep_fail_streak = 0
        submit_ticket(ex, ticket)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for t in resumes:
            if claimed >= args.count:
                break
            if json_exists(t["case_id"]):
                pending_finalize.append(
                    {"ticket": t, "case_log": os.path.join(
                        log_dir, f"case_resume_{t['case_id']}_{stamp}.log"
                    ), "i": claimed + 1, "t0": time.time(),
                     "author": {"ok": True, "authoring": t.get("authoring"),
                                "demoted": 0, "grok": 0, "did_stencil": 0}}
                )
                claimed += 1
                seq += 1
                L(f"RESUME-FINALIZE {t['case_id']} (JSON already present)")
            else:
                submit_ticket(ex, t)

        def harvest_done(timeout=0):
            if not inflight:
                return
            done, _ = wait(list(inflight.keys()), timeout=timeout,
                           return_when=FIRST_COMPLETED)
            for fut in done:
                item = inflight.pop(fut)
                try:
                    author = fut.result()
                except Exception as e:
                    author = {"ok": False, "exit": 1}
                    L(f"FAIL case {item['i']} {item['ticket']['case_id']} {e}")
                item["author"] = author
                cid = item["ticket"]["case_id"]
                L(f"AUTHOR done {cid} ok={1 if author.get('ok') else 0}; "
                  f"inflight={len(inflight)} pending_finalize="
                  f"{len(pending_finalize) + 1}")
                pending_finalize.append(item)

        def fill_authors() -> None:
            while len(inflight) < workers and claimed < args.count and not no_input:
                before = claimed
                try_claim(ex)
                if claimed == before:
                    break

        def finalize_item(item: dict) -> None:
            nonlocal ok, fail, author_fail_streak, no_input
            ticket = item["ticket"]
            cid = ticket["case_id"]
            author = item.get("author") or {}
            elapsed = int(time.time() - item["t0"])
            fin_ok = False
            safety = 0
            if author.get("ok") and json_exists(cid):
                if not case_done(cid):
                    safety = 1
                    L(f"JSON unfinalized; running finalize_scj.py {cid}")
                    fin_code = finalize_one(
                        ticket, py, item["case_log"], args.no_push
                    )
                    if fin_code != 0:
                        L(f"FAIL case {item['i']} {cid} finalize exit={fin_code}")
                        L(f"  tail: {tail(item['case_log'])}")
                        fail += 1
                        author_fail_streak += 1
                    else:
                        fin_ok = case_done(cid)
                else:
                    fin_ok = True
                    scj_queue.delete_ticket(cid)
            if fin_ok:
                L(f"OK case {item['i']} {cid} done -> next_seq={next_seq()} "
                  f"elapsed={elapsed}s")
                L(f"  tail: {tail(item['case_log'])}")
                ok += 1
                author_fail_streak = 0
            elif not author.get("ok"):
                L(f"FAIL case {item['i']} {cid} author json missing "
                  f"elapsed={elapsed}s")
                L(f"  tail: {tail(item['case_log'])}")
                fail += 1
                author_fail_streak += 1
            try:
                log_scj_review.append({
                    "event": "loop",
                    "case_id": cid,
                    "authoring": author.get("authoring") or ticket.get("authoring"),
                    "family": ticket.get("stencil_family") or "",
                    "source": ticket.get("source") or "",
                    "pages": ticket.get("page_count"),
                    "words": ticket.get("word_count"),
                    "citations": ticket.get("citation_count"),
                    "gate": ticket.get("gate") or "",
                    "elapsed": elapsed,
                    "ok": "1" if fin_ok else "0",
                    "safety_finalize": "1" if safety else "0",
                    "grok": str(author.get("grok") or 0),
                    "demoted": str(author.get("demoted") or 0),
                    "ik_citations": ticket.get("ik_citation_count"),
                    "text_citations": ticket.get("text_citation_count"),
                    "demoted_from": "stencil" if author.get("demoted") else "",
                })
            except Exception:
                pass
            if author_fail_streak >= 3:
                L("STOP: 3 consecutive author/finalize failures")
                no_input = True

        fill_authors()
        while inflight or pending_finalize:
            harvest_done(timeout=0)
            fill_authors()
            if pending_finalize:
                finalize_item(pending_finalize.pop(0))
                continue
            if inflight:
                harvest_done(timeout=None)
                fill_authors()
                continue
            break

    skipped = max(0, args.count - claimed)
    L(f"===== DONE ok={ok} fail={fail} skipped_remaining~{skipped} "
      f"next_seq={next_seq()} =====")
    L(f"Full log: {log_file}")
    try:
        subprocess.run(
            [py, os.path.join(ROOT, "tools", "log_scj_review.py"), "--summary"],
            cwd=ROOT,
        )
    except Exception:
        pass
    print(f"Summary: ok={ok} fail={fail} | next_seq={next_seq()} | log={log_file}",
          flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nstopped; open tickets in supply-code/tmp/tickets/ will resume",
              flush=True)
        sys.exit(130)
