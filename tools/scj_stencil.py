#!/usr/bin/env python3
"""Zero-LLM stencil for proved Supply Code families.

Live families (prepare/loop skip grok):
  6.5-billing-relegation   — disposed writ, relegated to Clause 6.5, no listing
  contempt-6.5-dismissed   — contempt of a 6.5 writ, dismissed misconceived/infructuous

Not live (dry-run only): listing-only. Interlocutory orders that look like
listings often carry the real node (SCJ-283/284/288/289/290).

Usage:
  python tools/scj_stencil.py --dry-run
  python tools/scj_stencil.py --write          # ticket.authoring must be stencil
  python tools/scj_stencil.py --write SCJ-300 --out tmp.json --force
"""
from __future__ import annotations

import argparse, json, os, re, sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "supply-code")
EXTRACTS = os.path.join(SC, "extracts")
SUMM = os.path.join(SC, "summaries", "json")
TICKET = os.path.join(SC, "tmp", "NEXT_TICKET.json")

LIVE = ("6.5-billing-relegation", "contempt-6.5-dismissed")

EXPECTED = {
    "6.5-billing-relegation": {
        "SCJ-275": "no", "SCJ-276": "no", "SCJ-281": "no",
        "SCJ-283": "no", "SCJ-284": "no", "SCJ-291": "yes",
        "SCJ-295": "no", "SCJ-297": "no", "SCJ-298": "yes",
        "SCJ-300": "yes",
    },
    "contempt-6.5-dismissed": {
        "SCJ-275": "yes", "SCJ-276": "yes",
        "SCJ-281": "no", "SCJ-283": "no", "SCJ-284": "no",
        "SCJ-288": "no", "SCJ-291": "no", "SCJ-295": "no",
        "SCJ-297": "no", "SCJ-298": "no", "SCJ-300": "no",
    },
    "listing-only": {
        "SCJ-283": "no", "SCJ-284": "no", "SCJ-288": "no",
        "SCJ-289": "no", "SCJ-290": "no", "SCJ-294": "no",
        "SCJ-291": "no", "SCJ-298": "no", "SCJ-300": "no",
        "SCJ-275": "no", "SCJ-276": "no",
    },
}

MAX_PAGES = 2
MAX_WORDS_65 = 500
MAX_WORDS_CONTEMPT = 900

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

WS = re.compile(r"\s+")
CLAUSE_65 = re.compile(r"cl[au]{0,2}se[-\s]*6\s*\.\s*5", re.I)
CLAUSE_65B = re.compile(r"cl[au]{0,2}se[-\s]*6\s*\.\s*5\s*\(\s*b", re.I)
CLAUSE_44 = re.compile(r"\b4\s*\.\s*4(?!\d)", re.I)
CLAUSE_68 = re.compile(r"\b6\s*\.\s*8\b", re.I)
CONTEMPT = re.compile(r"\bcontempt\s+application\b", re.I)
DISPOSED = re.compile(r"\bdispos(?:e[d]?|ing)\s+off?\b", re.I)
DISMISSED_WRIT = re.compile(
    r"\b(?:writ\s+petition|petition|this\s+writ\s+petition)\s+is\s*\[[^\]]*\]?\s*dismissed\b"
    r"|\bwrit\s+petition\s+is\s+dismissed\b"
    r"|\baccordingly,?\s+this\s+writ\s+petition\s+is\s*\[[^\]]*\]?\s*dismissed\b",
    re.I,
)
CONTEMPT_OUT = re.compile(
    r"\b(?:misconceived|infructuous|no case for contempt)\b",
    re.I,
)
INTERLOC = re.compile(
    r"\blist(?:ed)?\s+on\b|\bas\s+fresh\b|\badjournment\s+is\s+granted\b"
    r"|\btill\s+(?:the\s+)?next\s+date\b|\bon\s+adjourned\s+date\b",
    re.I,
)
STAT_THEFT = re.compile(r"(?:section|s\.)\s*12[65]\b|(?:section|s\.)\s*135\b|\bFIR\b", re.I)
THEFT_WORD = re.compile(r"\btheft\b", re.I)
THEFT_NEG = re.compile(
    r"(?:no(?:\s+\w+){0,6}\s+theft|without\s+(?:any\s+)?(?:allegation\s+of\s+)?theft|"
    r"allegation\s+of\s+theft)",
    re.I,
)
BILL = re.compile(
    r"\belectricity\s+bill|\binflated\b|\bexaggerated\b|\bdisputed\s+(?:electricity\s+)?bill"
    r"|\bcorrect(?:ness|ion)\s+of\s+(?:any\s+|the\s+)?bill|\bbilling\s+dispute"
    r"|\bbill\s+dispute|\barrears\s+of\s+the\s+electricity",
    re.I,
)
RELEGATE = re.compile(
    r"\brelegat(?:e|ed|ing)\b"
    r"|\balternative\s+remedy\b"
    r"|\bhas\s+a\s+remedy\s+to\s+approach\b"
    r"|\bapproach(?:es)?\s+the\s+competent\s+authority\b"
    r"|\bfile\s+a\s+(?:fresh\s+)?representation\b"
    r"|\bpermitting\s+the\s+petitioner\s+to\s+file\b"
    r"|\bfresh\s+representation\b",
    re.I,
)
ON_QUERY = re.compile(r"\bon query\b", re.I)
ON_OMISSION = re.compile(r"\bon omission\b", re.I)
VIRES = re.compile(r"\bvires\b", re.I)
HONBLE = re.compile(r"HON'?BLE\s+(.+?),\s*J\.?", re.I)
DOCKET_W = re.compile(r"(WRIT\s*-?\s*C\s*No\.?\s*-?\s*\d+\s+of\s+\d{4})", re.I)
DOCKET_C = re.compile(
    r"(CONTEMPT\s+APPLICATION\s*\(CIVIL\)\s*No\.?\s*-?\s*\d+\s+of\s+\d{4})", re.I)
DATE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(\d{1,2}),\s+(20\d{2})\b", re.I)
PET = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Petitioner", re.I)
APP = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Applicant", re.I)
RESP = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Respondent", re.I)
OPP = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Opposite", re.I)
RS = re.compile(r"Rs\.?\s*([\d,]+(?:\.\d+)?)\s*/?-?", re.I)
CODE_YEAR = re.compile(r"Electricity\s+Supply\s+Code,?\s*(20\d{2})", re.I)
DAYS = re.compile(
    r"within\s+(?:a\s+period\s+of\s+)?(\d+|ten|one|two|fifteen)\s+(days?|months?)", re.I)
STAY = re.compile(
    r"for\s+(?:a\s+period\s+of\s+)?(\d+|ten|one|two)\s+(days?|months?).{0,80}"
    r"(?:not\s+disconnect|no\s+coercive|shall\s+not\s+disconnect)", re.I)
OFFICER = re.compile(
    r"(Junior\s+Engineer|Executive\s+Engineer|competent\s+authority)", re.I)
DISCOM = re.compile(
    r"(Purvanchal\s+Vidyut\s+Vitran\s+Nigam(?:\s+Ltd\.?)?"
    r"|Pashchimanchal\s+Vidyut\s+Vitran\s+Nigam(?:\s+Limited)?"
    r"|Dakshinanchal\s+Vidyut\s+Vitran\s+Nigam"
    r"|Madhyanchal\s+Vidyut\s+Vitran\s+Nigam"
    r"|Kanpur\s+Electricity\s+Supply\s+Company)", re.I)
WORD_NUM = {"one": 1, "two": 2, "ten": 10, "fifteen": 15}
SMALL = {"of", "and", "the", "for", "in", "on", "to", "a", "an"}


def norm(s: str) -> str:
    return WS.sub(" ", s or "").strip()


def title_case_name(s: str) -> str:
    s = norm(s)
    if not s:
        return s
    out = []
    for i, w in enumerate(s.split()):
        if w.lower() in ("v.", "v", "vs", "vs."):
            out.append("v.")
            continue
        if re.match(r"^[A-Z]\.(?:[A-Z]\.)+$", w) or w in ("U.P.", "U.P"):
            out.append(w if w.endswith(".") or w == "U.P." else "U.P.")
            continue
        low = w.lower()
        if i > 0 and low in SMALL:
            out.append(low)
        else:
            out.append(w[:1].upper() + w[1:] if w.isupper() else (w[:1].upper() + w[1:].lower() if w.islower() else w[:1].upper() + w[1:]))
            # "Of" / "AND" leftovers
            if out[-1] in ("Of", "And", "The"):
                out[-1] = out[-1].lower()
    return " ".join(out)


def _has_theft(txt: str) -> bool:
    if STAT_THEFT.search(txt):
        return True
    for m in THEFT_WORD.finditer(txt):
        ctx = txt[max(0, m.start() - 48):m.end() + 8]
        if THEFT_NEG.search(ctx):
            continue
        return True
    return False


def load_fp(cid: str) -> dict:
    p = os.path.join(EXTRACTS, cid + ".fp.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_json(cid: str) -> dict | None:
    p = os.path.join(SUMM, cid + ".json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_txt(cid: str) -> str:
    p = os.path.join(EXTRACTS, cid + ".txt")
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_caption(txt: str) -> dict:
    pre = re.split(r"(?m)^\s*1\.\s", txt, maxsplit=1)[0]
    judges = [norm(j).title() for j in HONBLE.findall(pre)] or [
        norm(j).title() for j in HONBLE.findall(txt[:1200])
    ]
    dm = DATE.findall(txt)
    date_iso, date_display = "", ""
    if dm:
        mon, day, year = dm[-1]
        month = MONTHS[mon.lower()]
        date_iso = f"{year}-{month:02d}-{int(day):02d}"
        date_display = datetime(int(year), month, int(day)).strftime("%d %B %Y").lstrip("0")
    pet_m = PET.search(txt) or APP.search(txt)
    resp_m = RESP.search(txt) or OPP.search(txt)
    petitioner = title_case_name(pet_m.group(1) if pet_m else "")
    respondent = title_case_name(resp_m.group(1) if resp_m else "")
    petitioner = re.sub(r"^(?:Versus|Counsel.*)$", "", petitioner, flags=re.I).strip()
    docket = ""
    dm2 = DOCKET_C.search(txt) or DOCKET_W.search(txt)
    if dm2:
        docket = re.sub(r"\s+", " ", dm2.group(1))
        docket = re.sub(r"No\.\s*-", "No.", docket)
        docket = docket.replace("WRIT", "Writ").replace("CONTEMPT", "Contempt")
        docket = docket.replace("APPLICATION", "Application")
    amounts = RS.findall(txt)
    bill = ""
    if amounts:
        bill = "Rs." + amounts[0].replace(",", "")
        if "." not in bill.split("Rs.")[-1]:
            bill += "/-"
    days = DAYS.findall(txt)
    apply_within = ""
    if days:
        n, unit = days[0]
        n = WORD_NUM.get(str(n).lower(), n)
        apply_within = f"{n} {unit.lower()}"
    stay = ""
    stay_m = STAY.search(norm(txt))
    if stay_m:
        n, unit = stay_m.group(1), stay_m.group(2)
        n = WORD_NUM.get(n.lower(), n)
        stay = f"{n} {unit.lower()}"
    officers = [norm(x) for x in OFFICER.findall(txt)]
    officer = officers[-1] if officers else "competent authority"
    years = CODE_YEAR.findall(txt)
    code_year = years[-1] if years else "2005"
    discom_m = DISCOM.search(txt)
    discom = norm(discom_m.group(1)) if discom_m else ""
    bench = "Division Bench" if len(judges) >= 2 else ("Single Judge" if judges else "")
    coram = ""
    if judges:
        jj = [j if j.endswith("J.") else f"{j}, J." for j in judges]
        coram = jj[0] if len(jj) == 1 else ", ".join(jj[:-1]) + " and " + jj[-1]
    title = f"{petitioner} v. {respondent}" if petitioner and respondent else petitioner
    how = ""
    if re.search(r"\binfructuous\b", txt, re.I):
        how = "infructuous"
    elif re.search(r"\bmisconceived\b", txt, re.I):
        how = "misconceived"
    return {
        "title": title,
        "petitioner": petitioner,
        "respondent": respondent,
        "court": "Allahabad High Court",
        "bench": bench,
        "coram": coram,
        "date_of_judgment": date_iso,
        "date_display": date_display,
        "docket": docket,
        "bill_amount": bill,
        "apply_within": apply_within,
        "stay": stay,
        "officer": officer,
        "code_year": code_year,
        "discom": discom,
        "judges": judges,
        "contempt_how": how,
    }


def _base(fp: dict, reasons: list) -> dict:
    pages = fp.get("page_count")
    words = int(fp.get("word_count") or 0)
    return {
        "pages": pages,
        "words": words or None,
        "reasons": reasons,
        "cites": int(fp.get("citation_count") or 0),
    }


def classify_65(txt: str, fp: dict) -> dict:
    info = _base(fp, [])
    r = info["reasons"]
    pages, words, cites = info["pages"], info["words"] or len(txt.split()), info["cites"]
    if CONTEMPT.search(txt):
        r.append("veto: contempt application")
    if CLAUSE_65B.search(txt):
        r.append("veto: clause 6.5(b)")
    if INTERLOC.search(txt):
        r.append("veto: interlocutory listing/adjournment")
    if DISMISSED_WRIT.search(txt):
        r.append("veto: writ dismissed")
    if _has_theft(txt):
        r.append("veto: theft/126/135/FIR")
    if cites:
        r.append(f"veto: citation_count={cites}")
    if isinstance(pages, int) and pages > MAX_PAGES:
        r.append(f"veto: pages={pages}>{MAX_PAGES}")
    if words > MAX_WORDS_65:
        r.append(f"veto: words={words}>{MAX_WORDS_65}")
    if not CLAUSE_65.search(txt):
        r.append("no: clause 6.5 not found")
    if not BILL.search(txt):
        r.append("no: not a billing grievance")
    if not DISPOSED.search(txt):
        r.append("no: not disposed")
    if not RELEGATE.search(txt):
        r.append("no: no relegation language")
    ok = not any(x.startswith("veto:") or x.startswith("no:") for x in r)
    if ok:
        r.append("pass: 6.5 billing relegation")
    return {
        "verdict": "STENCIL" if ok else "NO",
        "family": "6.5-billing-relegation" if ok else None,
        "reasons": r, "pages": pages, "words": words,
        "slots": parse_caption(txt) if ok or CLAUSE_65.search(txt) else {},
    }


def classify_contempt(txt: str, fp: dict) -> dict:
    info = _base(fp, [])
    r = info["reasons"]
    pages, words, cites = info["pages"], info["words"] or len(txt.split()), info["cites"]
    if not CONTEMPT.search(txt):
        r.append("no: not a contempt application")
    if not CLAUSE_65.search(txt):
        r.append("no: clause 6.5 not found")
    if not CONTEMPT_OUT.search(txt):
        r.append("no: not dismissed as misconceived/infructuous")
    if INTERLOC.search(txt) and not CONTEMPT_OUT.search(txt):
        r.append("veto: interlocutory listing")
    if cites:
        r.append(f"veto: citation_count={cites}")
    if isinstance(pages, int) and pages > MAX_PAGES:
        r.append(f"veto: pages={pages}>{MAX_PAGES}")
    if words > MAX_WORDS_CONTEMPT:
        r.append(f"veto: words={words}>{MAX_WORDS_CONTEMPT}")
    ok = not any(x.startswith("veto:") or x.startswith("no:") for x in r)
    if ok:
        r.append("pass: contempt of 6.5 writ dismissed")
    return {
        "verdict": "STENCIL" if ok else "NO",
        "family": "contempt-6.5-dismissed" if ok else None,
        "reasons": r, "pages": pages, "words": words,
        "slots": parse_caption(txt) if ok or CONTEMPT.search(txt) else {},
    }


def classify_listing(txt: str, fp: dict) -> dict:
    """Dry-run only. Not live — too many listings are the interesting node."""
    info = _base(fp, [])
    r = info["reasons"]
    pages, words = info["pages"], info["words"] or len(txt.split())
    if CONTEMPT.search(txt):
        r.append("veto: contempt")
    if CLAUSE_65.search(txt) or CLAUSE_44.search(txt) or CLAUSE_68.search(txt):
        r.append("veto: named Code clause")
    if _has_theft(txt):
        r.append("veto: theft/FIR")
    if ON_QUERY.search(txt) or ON_OMISSION.search(txt):
        r.append("veto: on query / on omission")
    if VIRES.search(txt):
        r.append("veto: vires")
    if DISPOSED.search(txt):
        r.append("veto: disposed")
    if not INTERLOC.search(txt):
        r.append("no: not listed as fresh / list on")
    if isinstance(pages, int) and pages > MAX_PAGES:
        r.append(f"veto: pages={pages}>{MAX_PAGES}")
    ok = not any(x.startswith("veto:") or x.startswith("no:") for x in r)
    if ok:
        r.append("pass: listing-only (would-be; NOT LIVE)")
    return {
        "verdict": "STENCIL" if ok else "NO",
        "family": "listing-only" if ok else None,
        "reasons": r, "pages": pages, "words": words,
        "slots": parse_caption(txt) if ok else {},
    }


def classify(txt: str, fp: dict, live_only: bool = True) -> dict:
    """First live-family match wins. listing-only is never returned if live_only."""
    for fn in (classify_65, classify_contempt):
        hit = fn(txt, fp)
        if hit["verdict"] == "STENCIL":
            return hit
    empty = classify_65(txt, fp)
    empty["verdict"] = "NO"
    empty["family"] = None
    if not live_only:
        listing = classify_listing(txt, fp)
        if listing["verdict"] == "STENCIL":
            return listing
        empty["reasons"] = empty.get("reasons") or listing["reasons"]
    return empty


def fill_65(cid: str, fp: dict, slots: dict) -> dict:
    amount = slots.get("bill_amount") or ""
    officer = slots.get("officer") or "competent authority"
    apply_within = slots.get("apply_within")
    apply_bit = f" after completing the formalities within {apply_within}" if apply_within else ""
    stay = slots.get("stay")
    stay_bit = f" For {stay} the licensee shall not disconnect." if stay else ""
    flags = []
    if slots.get("code_year") and slots["code_year"] != "2005":
        flags.append(
            f"The order cites 'Clause 6.5 of the UP Electricity Supply Code, "
            f"{slots['code_year']}'. The Code in force is the 2005 Code. "
            "Recorded, not silently corrected."
        )
    if officer.lower() == "junior engineer":
        flags.append(
            "The Court directed the Clause 6.5 representation to a Junior Engineer. "
            "The ordinary 6.5 channel is the Executive Engineer. Recorded, not silently corrected."
        )
    discom = slots.get("discom")
    discom_bit = f" ({discom})" if discom else ""
    amt_bit = f" of {amount}" if amount else ""
    headnote = (
        f"A consumer who challenges an electricity bill{amt_bit} and seeks a writ "
        "quashing the bill or restraining disconnection is relegated to Clause 6.5 "
        "of the U.P. Electricity Supply Code, 2005. If the consumer applies under "
        f"that clause{apply_bit}, the {officer} is to consider and decide it in "
        f"accordance with law.{stay_bit} The Court does not examine the bill."
    )
    facts = (
        f"{slots.get('petitioner') or 'The petitioner'} challenged an electricity bill"
        f"{amt_bit}{discom_bit}. The Court treated the grievance as one against an "
        f"electricity bill and pointed the petitioner to Clause 6.5 before the {officer}."
    )
    holding = (
        "A writ seeking quashing of an electricity bill and/or a restraint on "
        "disconnection is disposed of without examining the bill. The consumer has "
        f"a remedy before the {officer} under Clause 6.5 of the U.P. Electricity "
        "Supply Code, 2005."
    )
    if apply_within:
        holding += (
            f" If an application is made{apply_bit}, it shall be considered and "
            "decided in accordance with law."
        )
    if stay:
        holding += f" For {stay} the respondent officers shall not disconnect."
    unit = {
        "provision": "UP-2005::6.5",
        "code": "U.P. Electricity Supply Code, 2005",
        "clause": "6.5",
        "topic": "Billing objection — relegation to Clause 6.5",
        "type": "supply_code",
        "holding": holding,
        "paras": "",
    }
    if flags:
        unit["flag"] = " ".join(flags)
    return {
        "case_id": cid,
        "title": slots.get("title") or "",
        "neutral_citation": "",
        "court": "Allahabad High Court",
        "bench": slots.get("bench") or "",
        "coram": slots.get("coram") or "",
        "date_of_judgment": slots.get("date_of_judgment") or "",
        "date_display": slots.get("date_display") or "",
        "docket": slots.get("docket") or "",
        "page_count": fp.get("page_count"),
        "significance": "ordinary",
        "disposition": (
            "Writ disposed of; petitioner relegated to Clause 6.5"
            + (f"; no disconnection for {stay}" if stay else "")
        ),
        "headnote": headnote,
        "facts": facts,
        "holding_units": [unit],
        "principle_tags": [],
        "not_decided": [
            {
                "point": "Merits of the disputed electricity bill",
                "note": "Left to the Clause 6.5 authority.",
                "docid": "",
                "paras": "",
            }
        ],
        "authorities": [],
    }


def fill_contempt(cid: str, fp: dict, slots: dict) -> dict:
    how = slots.get("contempt_how") or "dismissed"
    how_disp = {
        "infructuous": "infructuous",
        "misconceived": "misconceived",
    }.get(how, "dismissed")
    petitioner = slots.get("petitioner") or "The applicant"
    headnote = (
        "Civil contempt of a writ that relegated a billing dispute to Clause 6.5 "
        "of the U.P. Electricity Supply Code, 2005 is dismissed as "
        f"{how_disp}. This Court does not re-decide the bill or further construe "
        "Clause 6.5."
    )
    facts = (
        f"{petitioner} brought a civil contempt application of a writ order that "
        "had pointed the consumer to Clause 6.5. The contempt court dismissed "
        f"the application as {how_disp}."
    )
    holding = (
        "Where the underlying writ only relegated a billing dispute to Clause 6.5, "
        f"civil contempt of that order is {how_disp}. The contempt court does not "
        "re-examine the bill or independently construe Clause 6.5."
    )
    return {
        "case_id": cid,
        "title": slots.get("title") or "",
        "neutral_citation": "",
        "court": "Allahabad High Court",
        "bench": slots.get("bench") or "Single Judge",
        "coram": slots.get("coram") or "",
        "date_of_judgment": slots.get("date_of_judgment") or "",
        "date_display": slots.get("date_display") or "",
        "docket": slots.get("docket") or "",
        "page_count": fp.get("page_count"),
        "significance": "procedural",
        "disposition": (
            f"Contempt application dismissed as {how_disp}; "
            "Clause 6.5 bill not re-decided"
        ),
        "headnote": headnote,
        "facts": facts,
        "holding_units": [
            {
                "provision": "UP-2005::6.5",
                "code": "U.P. Electricity Supply Code, 2005",
                "clause": "6.5",
                "topic": "Contempt of a Clause 6.5 relegation writ — dismissed; bill not re-decided",
                "type": "supply_code",
                "holding": holding,
                "flag": (
                    "This Court recites the earlier writ's Clause 6.5 relegation and "
                    "decides only the contempt. No independent construction of the clause."
                ),
                "paras": "",
            }
        ],
        "principle_tags": [],
        "not_decided": [
            {
                "point": "Merits of the underlying electricity bill",
                "note": "The contempt court did not re-decide the billing dispute.",
                "docid": "",
                "paras": "",
            }
        ],
        "authorities": [],
    }


FILLERS = {
    "6.5-billing-relegation": fill_65,
    "contempt-6.5-dismissed": fill_contempt,
}


def fill(cid: str, fp: dict, family: str, slots: dict) -> dict:
    fn = FILLERS.get(family)
    if not fn:
        raise SystemExit(f"FAILED · no filler for family {family!r}")
    rec = fn(cid, fp, slots)
    if not rec.get("title") or not rec.get("holding_units"):
        raise SystemExit(f"FAILED · stencil fill incomplete for {cid} ({family})")
    return rec


def classify_family(txt: str, fp: dict, family: str) -> dict:
    return {
        "6.5-billing-relegation": classify_65,
        "contempt-6.5-dismissed": classify_contempt,
        "listing-only": classify_listing,
    }[family](txt, fp)


def iter_extracts(only: str | None):
    names = sorted(
        n for n in os.listdir(EXTRACTS)
        if n.endswith(".txt") and n.startswith("SCJ-")
    )
    for n in names:
        cid = n[:-4]
        if only and cid.upper() != only.upper():
            continue
        yield cid, load_txt(cid), load_fp(cid)


def score_family(family: str, only: str | None):
    exp_map = EXPECTED.get(family) or {}
    tp = tn = fp_ = fn = 0
    rows = []
    unexpected = []
    for cid, txt, fp in iter_extracts(only):
        hit = classify_family(txt, fp, family)
        got = "yes" if hit["verdict"] == "STENCIL" else "no"
        expected = exp_map.get(cid)
        if expected is None:
            expected = "no"
        if expected == "yes" and got == "yes":
            tp += 1
            sc = "TP"
        elif expected == "no" and got == "no":
            tn += 1
            sc = "TN"
        elif expected == "no" and got == "yes":
            fp_ += 1
            sc = "FP"
        else:
            fn += 1
            sc = "FN"
        if sc in ("TP", "FP", "FN") or cid in exp_map:
            rows.append((cid, got, expected, sc, hit))
            if sc == "FP" and cid not in exp_map:
                unexpected.append(cid)
    return {"tp": tp, "tn": tn, "fp": fp_, "fn": fn, "rows": rows,
            "unexpected": unexpected}


def dry_run(only: str | None) -> int:
    rc = 0
    print("SCJ stencil dry-run  (extracts only; no JSON written to summaries/)")
    for family in LIVE + ("listing-only",):
        live = family in LIVE
        tag = "LIVE" if live else "NOT LIVE"
        s = score_family(family, only)
        print()
        print(f"=== {family}  [{tag}]  TP={s['tp']} TN={s['tn']} FP={s['fp']} FN={s['fn']} ===")
        print(f"{'id':8} {'got':8} {'expect':8} {'sc':3} reasons")
        for cid, got, expected, sc, hit in s["rows"]:
            if sc == "TN" and not only and family == "listing-only" and got == "no":
                # still show the must-not-match set
                if cid not in EXPECTED["listing-only"]:
                    continue
            why = "; ".join((hit.get("reasons") or [])[:4])
            print(f"{cid:8} {got:8} {expected:8} {sc:3} {why}")
        if s["fp"] or s["fn"]:
            rc = 1
        if not live and s["tp"]:
            print("NOTE: listing-only had TPs — still not wired (see module docstring).")
        if live and s["fp"] == 0 and s["fn"] == 0:
            print("ok to wire")

    # Live classify (first match) + slots for hits
    print()
    print("=== live classify (first match) ===")
    for cid, txt, fp in iter_extracts(only):
        hit = classify(txt, fp, live_only=True)
        if hit["verdict"] != "STENCIL":
            continue
        print(f"{cid} → {hit['family']}")
        rec = fill(cid, fp, hit["family"], hit["slots"] or parse_caption(txt))
        authored = load_json(cid)
        if authored:
            for k in ("title", "court", "bench", "coram", "date_of_judgment",
                      "docket", "significance"):
                a, b = rec.get(k), authored.get(k)
                mark = "ok" if norm(str(a or "")).lower() == norm(str(b or "")).lower() else "DIFF"
                if mark == "DIFF":
                    print(f"  {mark:4} {k:20} stencil={a!r}  authored={b!r}")
    return rc


def write_record(cid: str | None, out: str | None, force: bool) -> int:
    ticket = None
    if os.path.exists(TICKET):
        with open(TICKET, encoding="utf-8") as f:
            ticket = json.load(f)
    from_ticket = not cid
    if not cid:
        if not ticket or ticket.get("status") != "READY":
            print("FAILED · no ticket and no case_id", file=sys.stderr)
            return 1
        cid = ticket["case_id"]
    if from_ticket and ticket.get("authoring") != "stencil":
        print(f"FAILED · ticket.authoring={ticket.get('authoring')!r} (need stencil)",
              file=sys.stderr)
        return 1
    txt = load_txt(cid)
    fp = load_fp(cid)
    hit = classify(txt, fp, live_only=True)
    if hit["verdict"] != "STENCIL" or hit["family"] not in LIVE:
        print(f"FAILED · {cid} is not a live stencil "
              f"({hit.get('family')}; {'; '.join((hit.get('reasons') or [])[:5])})",
              file=sys.stderr)
        return 1
    rec = fill(cid, fp, hit["family"], hit["slots"] or parse_caption(txt))
    dest = out or os.path.join(SUMM, cid + ".json")
    if os.path.exists(dest) and not force and not out:
        print(f"FAILED · {dest} already exists (pass --force to overwrite)",
              file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {dest} family={hit['family']}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="score families on extracts; write nothing")
    ap.add_argument("--write", action="store_true",
                    help="write lean JSON for a stencil ticket / case_id")
    ap.add_argument("--out", help="write JSON to this path instead of summaries/json")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("case_id", nargs="?", help="SCJ-NNN")
    args = ap.parse_args(argv)
    if args.write:
        return write_record(args.case_id, args.out, args.force)
    return dry_run(args.case_id)


if __name__ == "__main__":
    sys.exit(main())
