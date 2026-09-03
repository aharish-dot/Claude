#!/usr/bin/env python3
"""Copy Grok CLI chats for this repo into grok_chats/ as YYYY-MM-DD_HH-MM-SS.

Folders are named from the session's created_at in local time.
Re-running updates an existing folder when the session id already matches.

  python tools/sync_grok_chats.py              # copy + rebuild INDEX
  python tools/sync_grok_chats.py --push       # then commit+push grok_chats/
  python tools/sync_grok_chats.py --hook       # SessionEnd: copy; push in background
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "grok_chats")
LOCK_DIR = os.path.join(ROOT, "supply-code", "tmp", "queue.lock")
SYNC_LOCK = os.path.join(ROOT, "supply-code", "tmp", "grok_chats_sync.lock")
LOG = os.path.join(ROOT, "supply-code", "tmp", "grok_chats_sync.log")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
SKIP_NAMES = {"INDEX.md", "README.md", "prompt_history.jsonl", ".manifest.json"}


def log(msg: str) -> None:
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_created(raw: str) -> datetime | None:
    if not raw:
        return None
    s = raw.strip()
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone()
    except ValueError:
        return None


def stamp_name(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d_%H-%M-%S")


def unique_name(base: str, used: set[str]) -> str:
    name = base
    n = 2
    while name in used:
        name = f"{base}_{n}"
        n += 1
    used.add(name)
    return name


def load_summary(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def session_id_of(summary: dict, fallback: str = "") -> str:
    info = summary.get("info") or {}
    return str(info.get("id") or summary.get("id") or fallback)


def grok_session_group(cwd: str) -> str:
    home = os.environ.get("GROK_HOME") or os.path.join(os.path.expanduser("~"), ".grok")
    encoded = quote(os.path.abspath(cwd), safe="")
    return os.path.join(home, "sessions", encoded)


def copy_if_stale(src: str, dst: str) -> bool:
    if not os.path.isfile(src):
        return False
    if os.path.isfile(dst):
        try:
            if (os.path.getsize(src) == os.path.getsize(dst)
                    and os.path.getmtime(src) <= os.path.getmtime(dst) + 0.01):
                return False
        except OSError:
            pass
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return True


def iter_archive_dirs() -> list[str]:
    if not os.path.isdir(DEST):
        return []
    out = []
    for name in os.listdir(DEST):
        if name in SKIP_NAMES:
            continue
        p = os.path.join(DEST, name)
        if os.path.isdir(p):
            out.append(name)
    return out


def id_map() -> dict[str, str]:
    """session_id -> archive folder name."""
    found = {}
    for name in iter_archive_dirs():
        summary = load_summary(os.path.join(DEST, name, "summary.json"))
        sid = session_id_of(summary, name if UUID_RE.match(name) else "")
        if sid:
            found[sid] = name
    return found


def rename_uuid_folders() -> int:
    """Turn UUID archive folders into local date-time names."""
    used = {n for n in iter_archive_dirs() if not UUID_RE.match(n)}
    rows = []
    for name in iter_archive_dirs():
        if not UUID_RE.match(name):
            continue
        summary = load_summary(os.path.join(DEST, name, "summary.json"))
        dt = parse_created(summary.get("created_at") or "")
        if dt is None:
            mtime = os.path.getmtime(os.path.join(DEST, name))
            dt = datetime.fromtimestamp(mtime).astimezone()
        rows.append((dt, name))
    rows.sort(key=lambda x: (x[0], x[1]))
    n = 0
    for dt, name in rows:
        dest = unique_name(stamp_name(dt), used)
        if dest == name:
            continue
        os.rename(os.path.join(DEST, name), os.path.join(DEST, dest))
        n += 1
    return n


def write_index() -> None:
    rows = []
    for name in iter_archive_dirs():
        summary = load_summary(os.path.join(DEST, name, "summary.json"))
        title = (summary.get("generated_title")
                 or summary.get("session_summary")
                 or "").replace("|", "/")
        n = summary.get("num_chat_messages") or 0
        rows.append((name, n, title))
    rows.sort()
    lines = [
        "# Grok chats — this working copy",
        "",
        "Each folder is named **local date and time** (`YYYY-MM-DD_HH-MM-SS`) "
        "from when the session started. Same-second sessions get `_2`, `_3`, …",
        "",
        f"**{len(rows)} sessions.** Live Grok sessions are copied here on "
        "`SessionEnd` (`tools/sync_grok_chats.py`).",
        "",
        "| Started | Messages | Folder | Title |",
        "|---|---:|---|---|",
    ]
    for name, n, title in rows:
        parts = name.split("_")
        started = parts[0]
        if len(parts) >= 2:
            started += " " + parts[1].replace("-", ":")
        if len(parts) >= 3:
            started += f" ({parts[2]})"
        lines.append(f"| {started} | {n} | [`{name}`]({name}/) | {title} |")
    lines.append("")
    os.makedirs(DEST, exist_ok=True)
    with open(os.path.join(DEST, "INDEX.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def sync_from_grok(cwd: str) -> tuple[int, int]:
    """Copy live sessions into dated grok_chats folders. Returns (new, updated)."""
    group = grok_session_group(cwd)
    os.makedirs(DEST, exist_ok=True)
    mapping = id_map()
    used = set(iter_archive_dirs())
    new = 0
    updated = 0
    if os.path.isdir(group):
        for sid in sorted(os.listdir(group)):
            src_dir = os.path.join(group, sid)
            if not os.path.isdir(src_dir) or not UUID_RE.match(sid):
                continue
            chat = os.path.join(src_dir, "chat_history.jsonl")
            summary_src = os.path.join(src_dir, "summary.json")
            if not os.path.isfile(chat):
                continue
            summary = load_summary(summary_src)
            dest_name = mapping.get(sid)
            is_new = dest_name is None
            if is_new:
                dt = parse_created(summary.get("created_at") or "")
                if dt is None:
                    dt = datetime.fromtimestamp(os.path.getmtime(chat)).astimezone()
                dest_name = unique_name(stamp_name(dt), used)
                mapping[sid] = dest_name
            dest_dir = os.path.join(DEST, dest_name)
            os.makedirs(dest_dir, exist_ok=True)
            changed = False
            if copy_if_stale(summary_src, os.path.join(dest_dir, "summary.json")):
                changed = True
            if copy_if_stale(chat, os.path.join(dest_dir, "chat_history.jsonl")):
                changed = True
            if is_new:
                new += 1
            elif changed:
                updated += 1
        ph = os.path.join(group, "prompt_history.jsonl")
        if os.path.isfile(ph):
            copy_if_stale(ph, os.path.join(DEST, "prompt_history.jsonl"))
    return new, updated


def git_busy() -> str | None:
    if os.path.isdir(LOCK_DIR):
        return "case loop holds queue.lock"
    index_lock = os.path.join(ROOT, ".git", "index.lock")
    if os.path.exists(index_lock):
        return "git index.lock present"
    return None


def git_push_chats() -> int:
    busy = git_busy()
    if busy:
        log(f"skip push: {busy}")
        return 0
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    subprocess.run(
        ["git", "add", "--", "grok_chats"],
        cwd=ROOT, check=False, env=env,
    )
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", "grok_chats"],
        cwd=ROOT, env=env,
    )
    if diff.returncode == 0:
        log("nothing to commit")
        return 0
    msg = "docs: sync grok_chats " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    r = subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=ROOT, capture_output=True, text=True, env=env,
    )
    if r.returncode != 0:
        err = (r.stdout or "") + (r.stderr or "")
        log(f"commit failed: {err.strip()[:400]}")
        return r.returncode
    r = subprocess.run(
        ["git", "push"],
        cwd=ROOT, capture_output=True, text=True, env=env,
    )
    if r.returncode != 0:
        log(f"push failed: {(r.stderr or r.stdout or '')[:400]}")
        return r.returncode
    log("pushed grok_chats")
    return 0


def spawn_push() -> None:
    kwargs = {
        "args": [sys.executable, os.path.abspath(__file__), "--push-only"],
        "cwd": ROOT,
        "stdout": open(LOG, "a", encoding="utf-8"),
        "stderr": subprocess.STDOUT,
        "close_fds": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = 0x00000008 | 0x08000000  # DETACHED | NO_WINDOW
        kwargs["stdin"] = subprocess.DEVNULL
    else:
        kwargs["start_new_session"] = True
        kwargs["stdin"] = subprocess.DEVNULL
    subprocess.Popen(**kwargs)


def hook_payload() -> dict:
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except (OSError, json.JSONDecodeError):
        return {}


def acquire_sync_lock(timeout: float = 6.0) -> bool:
    os.makedirs(os.path.dirname(SYNC_LOCK), exist_ok=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.mkdir(SYNC_LOCK)
            return True
        except FileExistsError:
            try:
                age = time.time() - os.path.getmtime(SYNC_LOCK)
            except OSError:
                age = 0
            if age > 120:
                try:
                    os.rmdir(SYNC_LOCK)
                except OSError:
                    pass
            time.sleep(0.1)
    return False


def release_sync_lock() -> None:
    try:
        os.rmdir(SYNC_LOCK)
    except OSError:
        pass


def run_sync(do_push: bool, background_push: bool) -> int:
    cwd = os.environ.get("GROK_WORKSPACE_ROOT") or ROOT
    here = os.path.normcase(os.path.abspath(ROOT))
    there = os.path.normcase(os.path.abspath(cwd))
    if here != there:
        return 0
    if not acquire_sync_lock():
        log("skip: sync lock busy")
        return 0
    try:
        renamed = rename_uuid_folders()
        new, updated = sync_from_grok(ROOT)
        write_index()
        log(f"renamed={renamed} new={new} updated={updated}")
        if background_push:
            spawn_push()
        elif do_push:
            return git_push_chats()
        return 0
    finally:
        release_sync_lock()


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--push-only" in args:
        return git_push_chats()
    if "--hook" in args:
        payload = hook_payload()
        if payload.get("subagentType"):
            return 0
        return run_sync(do_push=False, background_push=True)
    do_push = "--push" in args
    return run_sync(do_push=do_push, background_push=False)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
