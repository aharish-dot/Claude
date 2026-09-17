"""Build a schema-shaped skeleton from an extract.

Deterministic metadata (court, coram, date, docket, page_count, source block) is
pre-filled so the authoring step only has to produce the analytical fields. A
skeleton deliberately FAILS validation (model == "PENDING", empty analysis) so
"passes validation" is an unambiguous signal that a case is genuinely authored.
"""
from __future__ import annotations

SCHEMA_VERSION = "scj-2.0"


def build_skeleton(extract: dict, case_id: str, model: str = "PENDING",
                   default_court: str = "") -> dict:
    m = extract.get("raw_meta", {})
    parties = m.get("parties") or ["", "", ""]
    _, _, title = parties
    coram = m.get("coram") or []
    flags = []
    cands = m.get("date_candidates") or []
    if len(cands) > 1:
        flags.append(f"multiple candidate dates {cands}; confirm the operative disposal date")
    if extract.get("truncated"):
        flags.append("lean text was truncated to the char cap; verify nothing material was cut")
    if not (m.get("court") or default_court):
        flags.append("court not detected in text; set it explicitly")
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "title": title or "",
        "neutral_citation": "",
        "court": m.get("court", "") or default_court,
        "bench": ("Division Bench" if len(coram) >= 2 else ("Single Bench" if coram else "")),
        "coram": "; ".join(coram),
        "date_of_judgment": m.get("date_of_judgment", ""),
        "date_display": "",
        "docket": m.get("docket", ""),
        "page_count": extract.get("page_count", 0),
        "significance": "",
        "outcome": "",
        "model": model,
        "disposition": "",
        "headnote": "",
        "facts": "",
        "reusable_constructions": [],
        "holding_units": [],
        "principle_tags": [],
        "not_decided": [],
        "authorities": [],
        "source": {
            "source_file": extract.get("source_file", ""),
            "sha256": extract.get("sha256", ""),
            "page_count": extract.get("page_count", 0),
            "engine": extract.get("engine", ""),
            "extracted_est_tokens": extract.get("est_tokens", 0),
            "truncated": extract.get("truncated", False),
        },
        "qa": {
            "confidence": None,
            "authored_by": "",
            "flags": flags,
            "auto_checks": [],
        },
    }
