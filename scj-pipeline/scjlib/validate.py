"""Dependency-free structural + semantic validation for SCJ summaries.

No jsonschema dependency so it always runs. schema/scj.schema.json is the
portable spec; this is the enforced gate. Errors block a case; warnings are
advisory (surfaced for the author to consider).
"""
from __future__ import annotations

import re

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
CID_RE = re.compile(r'^[A-Z]{2,6}-\d{3,6}$')
CATALOG_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9.\- ]*::[A-Za-z0-9().\-]+$')
PARAS_RE = re.compile(r'^[\d,\s\-–]+$')

REQUIRED_NONEMPTY = ["case_id", "title", "court", "date_of_judgment",
                     "disposition", "headnote", "facts"]


def _is_paras(s) -> bool:
    s = str(s or "").strip()
    return bool(s) and bool(PARAS_RE.match(s)) and any(ch.isdigit() for ch in s)


def validate_doc(doc: dict):
    """Return (errors, warnings) lists of human-readable strings."""
    errors, warnings = [], []

    if doc.get("model", "") in ("", "PENDING"):
        errors.append("model is PENDING/empty (case not authored yet)")

    for f in REQUIRED_NONEMPTY:
        v = doc.get(f, "")
        if not (isinstance(v, str) and v.strip()):
            errors.append(f"required field '{f}' is empty")

    cid = doc.get("case_id", "")
    if cid and not CID_RE.match(cid):
        warnings.append(f"case_id '{cid}' not in PREFIX-#### form")

    d = doc.get("date_of_judgment", "")
    if d and not DATE_RE.match(d):
        errors.append(f"date_of_judgment '{d}' is not YYYY-MM-DD")

    hu = doc.get("holding_units", [])
    if not isinstance(hu, list) or not hu:
        errors.append("holding_units is empty")
    else:
        for i, h in enumerate(hu):
            for k in ("provision", "topic", "holding", "paras"):
                if not str(h.get(k, "")).strip():
                    errors.append(f"holding_units[{i}] missing '{k}'")
            prov, typ = h.get("provision", ""), h.get("type", "")
            if typ in ("supply_code", "electricity_act") and prov and not CATALOG_RE.match(prov):
                warnings.append(f"holding_units[{i}].provision '{prov}' is not catalog-key form (CODE::clause)")
            if h.get("paras") and not _is_paras(h["paras"]):
                warnings.append(f"holding_units[{i}].paras '{h.get('paras')}' is not paragraph-number form")

    for i, a in enumerate(doc.get("authorities", []) or []):
        if not str(a.get("name", "")).strip():
            errors.append(f"authorities[{i}] missing name")

    if isinstance(doc.get("headnote"), str) and len(doc["headnote"]) < 120:
        warnings.append("headnote is very short (<120 chars)")
    if isinstance(doc.get("facts"), str) and len(doc["facts"]) < 120:
        warnings.append("facts is very short (<120 chars)")

    return errors, warnings


def is_authored(doc: dict) -> bool:
    errs, _ = validate_doc(doc)
    return not errs
