"""Best-effort metadata parsing from judgment text.

Heuristic and defensive: every function returns "" / [] rather than raising, so a
bad match never blocks the pipeline. Whatever is uncertain is left blank for the
authoring step (Claude) to fill or correct from the lean text.
"""
from __future__ import annotations

import re

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}


def _iso_from_dmy(d, m, y) -> str:
    try:
        d, m, y = int(d), int(m), int(y)
        if y < 100:
            y += 2000 if y < 50 else 1900
        if 1 <= m <= 12 and 1 <= d <= 31 and 1900 < y < 2100:
            return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        pass
    return ""


def candidate_dates(text: str):
    """Salient dates from the header region, in reading order, de-duplicated.

    These judgments often concatenate several orders (e.g. a listing order plus
    the disposal), so more than one date is normal -- the extra candidates are
    surfaced for the author to pick the operative disposal date.
    """
    t = text[:3000]
    out = []
    for m in re.finditer(r'Order\s*Date\s*:-?\s*(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2,4})', t, re.I):
        out.append(_iso_from_dmy(*m.groups()))
    for m in re.finditer(r'(\d{1,2})(?:st|nd|rd|th)\s+([A-Za-z]+),?\s+(\d{4})', t):
        if m.group(2).lower() in MONTHS:
            out.append(_iso_from_dmy(m.group(1), MONTHS[m.group(2).lower()], m.group(3)))
    seen, res = set(), []
    for d in out:
        if d and d not in seen:
            seen.add(d)
            res.append(d)
    return res


def find_date(text: str) -> str:
    t = text[:8000]
    orders = [_iso_from_dmy(*m.groups()) for m in
              re.finditer(r'Order\s*Date\s*:-?\s*(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2,4})', t, re.I)]
    orders = [o for o in orders if o]
    if orders:
        return orders[-1]                       # last order = the disposal, not the listing
    cands = candidate_dates(text)
    if cands:
        return cands[0]
    m = re.search(r'(?:Date\s*of\s*(?:Order|Judgment|Decision)|Reserved\s*on|Delivered\s*on|'
                  r'Decided\s*on)[^\d]{0,15}(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2,4})', t[:4000], re.I)
    if m:
        return _iso_from_dmy(*m.groups())
    m = re.search(r'\b(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})\b', t[:2000])
    return _iso_from_dmy(*m.groups()) if m else ""


def find_docket(text: str) -> str:
    t = text[:4000]
    pats = [
        r'((?:Writ|WRIT)\s*[-–]?\s*[ABC]?\s*No\.?\s*[-–]?\s*\d[\d,]*\s*of\s*\d{4})',
        r'(Civil\s+Misc\.?\s+Writ\s+Petition\s+No\.?\s*\d[\d,]*\s*of\s*\d{4})',
        r'([A-Z]{2,6}\s*No\.?\s*\d[\d,]*\s*of\s*\d{4})',
    ]
    for p in pats:
        m = re.search(p, t, re.I)
        if m:
            return re.sub(r'\s+', ' ', m.group(1)).strip()
    return ""


def find_coram(text: str):
    t = text[:6000]
    names = re.findall(r"Hon'?ble\s+(?:Mr\.?\s+|Ms\.?\s+|Mrs\.?\s+|Justice\s+)?"
                       r"([A-Z][A-Za-z.\s]+?),?\s*J\.", t)
    seen, out = set(), []
    for n in names:
        n = re.sub(r'\s+', ' ', n).strip(' ,.')
        if len(n) > 2 and n.lower() not in ("the", "of") and n not in seen:
            seen.add(n)
            out.append(f"{n}, J.")
    return out[:4]


def find_court(text: str) -> str:
    t = text[:2500]
    if re.search(r'Judicature at Allahabad', t, re.I):
        return "Allahabad High Court"
    if re.search(r'Supreme Court of India', t, re.I):
        return "Supreme Court of India"
    m = re.search(r'HIGH COURT OF ([A-Z][A-Z ]+?)(?:\n| AT )', t)
    if m:
        return ("High Court of " + m.group(1).title()).strip()
    return ""


def find_parties(text: str):
    t = text[:2500]
    # Primary: Allahabad e-copy header ("Petitioner :- X" / "Respondent :- Y").
    pet = re.search(r'Petitioner\s*:-\s*(.+)', t)
    res = re.search(r'Respondent\s*:-\s*(.+)', t)
    if pet and res:
        p = re.sub(r'\s+', ' ', pet.group(1)).strip(' .,-')
        r = re.sub(r'\s+', ' ', res.group(1)).strip(' .,-')
        if p and r:
            return [p, r, f"{p} v. {r}"]
    # Fallback: a "Versus" line in the header, skipping citation references.
    for line in t.split("\n"):
        if re.search(r'\bNo\.\s*\d[\d,]*\s+of\s+\d{4}', line):
            continue
        m = re.search(r'(.{3,80}?)\s+(?:Versus|Vs\.?)\s+(.{3,120}?)$', line.strip(), re.I)
        if m:
            p = re.sub(r'\s+', ' ', m.group(1)).strip(' .,-')
            r = re.sub(r'\s+', ' ', m.group(2)).strip(' .,-')
            if p and r:
                return [p, r, f"{p} v. {r}"]
    return ["", "", ""]


def parse_meta(text: str, filename: str = "") -> dict:
    return {
        "court": find_court(text),
        "date_of_judgment": find_date(text),
        "date_candidates": candidate_dates(text),
        "docket": find_docket(text),
        "coram": find_coram(text),
        "parties": find_parties(text),
    }
