"""Shared paths, IO, hashing and text helpers. Pure standard library."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
PDFS = DATA / "pdfs"
EXTRACTS = DATA / "extracts"
OUT = DATA / "out"
WORK = DATA / "work"
LEDGER = DATA / "ledger.jsonl"
PROMPTS = BASE / "prompts"
SCHEMA = BASE / "schema" / "scj.schema.json"


def ensure_dirs() -> None:
    for d in (DATA, PDFS, EXTRACTS, OUT, WORK):
        d.mkdir(parents=True, exist_ok=True)


def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write_json(p, obj) -> None:
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text(p) -> str:
    return Path(p).read_text(encoding="utf-8", errors="replace")


def write_text(p, s: str) -> None:
    Path(p).write_text(s, encoding="utf-8")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(s: str, maxlen: int = 60) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s or "").strip("-")
    return (s[:maxlen].strip("-")) or "case"


def normalize_ws(s: str) -> str:
    s = (s or "").replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t ]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def est_tokens(s: str) -> int:
    """Rough token estimate (~4 chars/token) for context-budget reporting."""
    return (len(s or "") + 3) // 4


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")
