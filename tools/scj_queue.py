#!/usr/bin/env python3
"""Disk-backed SCJ work queue: per-case tickets, id reservation, lock path.

Tickets live at supply-code/tmp/tickets/SCJ-NNN.json (gitignored). The legacy
single-slot file tmp/NEXT_TICKET.json is still written as a copy of the latest
ticket so chat-`next` / old prompts keep working.

Ids are reserved at claim time. finalize_scj.py must never rewind next_seq.
"""
from __future__ import annotations

import json
import os
import re
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "supply-code")
STATE = os.path.join(SC, "state", "index.json")
TICKETS_DIR = os.path.join(SC, "tmp", "tickets")
PROMPTS_DIR = os.path.join(SC, "tmp", "prompts")
LOCK_DIR = os.path.join(SC, "tmp", "queue.lock")
TICKET_LEGACY = os.path.join(SC, "tmp", "NEXT_TICKET.json")
OPEN_STATUSES = {"READY", "CLAIMING", "AUTHORING"}
CID_RE = re.compile(r"^SCJ-(\d+)$", re.I)


def cid_seq(cid: str) -> int:
    m = CID_RE.match(str(cid or "").strip())
    if not m:
        raise ValueError(f"bad case_id {cid!r}")
    return int(m.group(1))


def case_id_for(seq: int) -> str:
    return f"SCJ-{int(seq):03d}"


def atomic_write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".txt", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def atomic_write_json(path: str, obj) -> None:
    blob = json.dumps(obj, indent=2, ensure_ascii=False)
    if not blob.endswith("\n"):
        blob += "\n"
    atomic_write_text(path, blob)


def load_state(path: str = STATE) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict, path: str = STATE) -> None:
    atomic_write_json(path, state)


def ticket_path(cid: str, tickets_dir: str = TICKETS_DIR) -> str:
    return os.path.join(tickets_dir, f"{cid}.json")


def load_ticket(path: str) -> dict | None:
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_ticket(ticket: dict, *, legacy: bool = True,
                tickets_dir: str = TICKETS_DIR,
                legacy_path: str = TICKET_LEGACY) -> str:
    cid = ticket.get("case_id")
    if not cid:
        raise ValueError("ticket missing case_id")
    os.makedirs(tickets_dir, exist_ok=True)
    dest = ticket_path(cid, tickets_dir)
    ticket = dict(ticket)
    ticket["ticket"] = dest.replace("\\", "/")
    atomic_write_json(dest, ticket)
    if legacy:
        os.makedirs(os.path.dirname(legacy_path), exist_ok=True)
        atomic_write_json(legacy_path, ticket)
    return dest


def delete_ticket(cid: str, tickets_dir: str = TICKETS_DIR) -> None:
    p = ticket_path(cid, tickets_dir)
    if os.path.exists(p):
        os.remove(p)


def iter_tickets(tickets_dir: str = TICKETS_DIR) -> list[dict]:
    if not os.path.isdir(tickets_dir):
        return []
    out = []
    for name in os.listdir(tickets_dir):
        if not name.startswith("SCJ-") or not name.endswith(".json"):
            continue
        t = load_ticket(os.path.join(tickets_dir, name))
        if t:
            out.append(t)
    out.sort(key=lambda t: cid_seq(t.get("case_id") or "SCJ-0"))
    return out


def open_tickets(tickets_dir: str = TICKETS_DIR) -> list[dict]:
    return [t for t in iter_tickets(tickets_dir)
            if (t.get("status") or "") in OPEN_STATUSES]


def open_sources(tickets_dir: str = TICKETS_DIR) -> set[str]:
    out = set()
    for t in open_tickets(tickets_dir):
        src = (t.get("source") or "").replace("\\", "/").lstrip("/")
        if src:
            out.add(src)
            out.add(os.path.basename(src))
    return out


def reserved_seqs(state: dict, tickets: list[dict] | None = None) -> set[int]:
    taken = set()
    for c in state.get("cases") or []:
        try:
            taken.add(cid_seq(c.get("case_id")))
        except (TypeError, ValueError):
            continue
    for t in tickets if tickets is not None else open_tickets():
        if (t.get("status") or "") == "DONE":
            continue
        try:
            taken.add(cid_seq(t.get("case_id")))
        except (TypeError, ValueError):
            continue
    return taken


def next_free_seq(state: dict, tickets: list[dict] | None = None) -> int:
    """Next SCJ number not in cases[] and not on an open ticket."""
    taken = reserved_seqs(state, tickets)
    seq = int(state.get("next_seq") or 1)
    while seq in taken:
        seq += 1
    return seq


def bump_next_seq(state: dict, seq: int) -> int:
    """Reserve seq. Never decrease next_seq. Returns the new next_seq."""
    state["next_seq"] = max(int(state.get("next_seq") or 0), int(seq) + 1)
    return state["next_seq"]


def next_seq_after_finalize(state: dict) -> int:
    """Monotonic next_seq after appending a case. Never rewinds reservations."""
    cases = state.get("cases") or []
    maxseq = 0
    for c in cases:
        try:
            maxseq = max(maxseq, cid_seq(c.get("case_id")))
        except (TypeError, ValueError):
            continue
    return max(int(state.get("next_seq") or 0), maxseq + 1)


def ticket_takeable(ticket: dict) -> bool:
    """True if this process may author the ticket (not owned by a live worker)."""
    import scj_lock
    st = ticket.get("status") or ""
    if st == "READY":
        return True
    if st == "AUTHORING":
        try:
            pid = int(ticket.get("owner_pid") or 0)
        except (TypeError, ValueError):
            pid = 0
        return not scj_lock.pid_alive(pid)
    return False


def case_is_done(state: dict, cid: str) -> bool:
    for c in state.get("cases") or []:
        if c.get("case_id") == cid and (c.get("status") or "done") == "done":
            return True
    return False


def json_path(cid: str, sc: str = SC) -> str:
    return os.path.join(sc, "summaries", "json", cid + ".json")


def write_worker_prompt(cid: str, body: str, prompts_dir: str = PROMPTS_DIR) -> str:
    os.makedirs(prompts_dir, exist_ok=True)
    dest = os.path.join(prompts_dir, cid + ".txt")
    atomic_write_text(dest, body)
    return dest


def make_json_only_prompt(base: str, ticket_rel: str, cid: str, out_json: str) -> str:
    """Rewrite a serial prompt so a parallel worker writes JSON and stops."""
    rewritten = base.replace("supply-code/tmp/NEXT_TICKET.json", ticket_rel)
    header = (
        f"PARALLEL WORKER. Process exactly ONE case from {ticket_rel}.\n"
        f"Write ONLY {out_json}. Do NOT run finalize_scj.py, git, Chrome, "
        f"or a second case. If the instructions below say to finalize, skip that step.\n"
        f"End with: {cid} · <short title> · <disposition>≤15 words · json ok\n"
        f"If blocked: FAILED · <reason> · {cid}\n\n"
    )
    return header + rewritten
