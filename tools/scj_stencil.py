#!/usr/bin/env python3
"""Zero-LLM stencil for proved Supply Code families.

Live families (prepare/loop skip grok):
  6.5-billing-relegation   — disposed writ, relegated to Clause 6.5, no listing.
    s.126/135/FIR mention is not a veto when those facts are left open in writ
    ("cannot be decided" / "without examining" / "at the first instance").
    Relegation language includes approach EE/JE, liberty to apply/make/move an
    application, raise dispute, "should file a challenge", "can get the bill
    corrected", "if the petitioner approaches". "Clause/para/section 6.5" all
    count. Billing cue includes current/impugned bill (SCJ-353), wrong bill,
    electricity amount due, unpaid electrical dues, recovery citation (SCJ-408).
    Withdrawals stay off this family.
    Court-grant veto (SCJ-411): 6.5 only in counsel's mouth, Court grants
    (we intervene / forthwith comply / petition allowed / mandamus issued).
  6.8-assessment-hearing   — recovery citation, no hearing, deposit, Assessing
    Officer under 6.8, disposed, pages ≤ 2. Quash / s.135 / listing stay off.
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

LIVE = (
    "6.5-billing-relegation",
    "6.8-assessment-hearing",
    "contempt-6.5-dismissed",
)

EXPECTED = {
    "6.5-billing-relegation": {
        "SCJ-275": "no", "SCJ-276": "no", "SCJ-281": "no",
        "SCJ-283": "no", "SCJ-284": "no", "SCJ-291": "yes",
        "SCJ-295": "no", "SCJ-297": "no", "SCJ-298": "yes",
        "SCJ-300": "yes", "SCJ-301": "yes", "SCJ-306": "yes",
        # clones that missed on phrasing (move/make application, para 6.5, demand notice)
        "SCJ-327": "yes", "SCJ-331": "yes", "SCJ-333": "yes", "SCJ-335": "yes",
        # Allahabad `Petitioner :-` caption (not Lucknow `.....Petitioner`)
        "SCJ-358": "yes",
        # 338–387 review TPs (fill_65; loop metric missing on 358/360)
        "SCJ-360": "yes",
        "SCJ-366": "yes", "SCJ-370": "yes", "SCJ-371": "yes",
        "SCJ-374": "yes", "SCJ-378": "yes",
        # stay off stencil: no bill/dispose language; withdrawal with 6.5 liberty
        "SCJ-330": "no", "SCJ-332": "no",
        # 338–387 review: 6.5 order quashed (not a clone)
        "SCJ-379": "no",
        # BILL cue widened: "impugned current bill" (was a clone miss)
        "SCJ-353": "yes",
        # 388–437 review TPs
        "SCJ-405": "yes", "SCJ-419": "yes", "SCJ-420": "yes",
        "SCJ-421": "yes", "SCJ-422": "yes",
        # 388–437 FP: counsel raised 6.5; Court granted Lok Adalat compliance
        "SCJ-411": "no",
        # BILL + RELEGATE cues (408-class / 399 / 468 / 487)
        "SCJ-399": "yes", "SCJ-408": "yes", "SCJ-468": "yes", "SCJ-487": "yes",
        # 6.5 with no bill/demand in the order — stay off
        "SCJ-418": "no",
        # 438–487 stencil TPs (batch ran before the 388–437 review)
        "SCJ-474": "yes", "SCJ-484": "yes", "SCJ-485": "yes", "SCJ-486": "yes",
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
    # Live. 2-page SDS/Shukla recovery-citation → 6.8 hearing clones.
    "6.8-assessment-hearing": {
        "SCJ-424": "yes", "SCJ-425": "yes", "SCJ-428": "yes",
        "SCJ-429": "yes", "SCJ-431": "yes", "SCJ-432": "yes",
        "SCJ-433": "yes", "SCJ-435": "yes", "SCJ-437": "yes",
        "SCJ-438": "yes", "SCJ-439": "yes",
        # 3-page / quash / s.135 / listing bundle — must stay off
        "SCJ-415": "no", "SCJ-356": "no", "SCJ-367": "no",
        "SCJ-375": "no", "SCJ-376": "no", "SCJ-478": "no",
        "SCJ-283": "no", "SCJ-284": "no", "SCJ-379": "no",
        "SCJ-385": "no", "SCJ-411": "no",
    },
}

MAX_PAGES = 2
MAX_WORDS_65 = 500
MAX_WORDS_68 = 500
MAX_WORDS_CONTEMPT = 900

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

WS = re.compile(r"\s+")
CLAUSE_65 = re.compile(
    r"(?:cl[au]{0,2}se|para(?:graph)?s?|section|(?<![A-Za-z])s\.)[-\s]*6\s*\.\s*5",
    re.I)
CLAUSE_65B = re.compile(
    r"(?:cl[au]{0,2}se|para(?:graph)?s?|section|(?<![A-Za-z])s\.)[-\s]*6\s*\.\s*5\s*\(\s*b",
    re.I)
CLAUSE_44 = re.compile(r"\b4\s*\.\s*4(?!\d)", re.I)
CLAUSE_68 = re.compile(r"\b6\s*\.\s*8\b", re.I)
CLAUSE_68_NAMED = re.compile(
    r"(?:cl[au]{0,2}se|para(?:graph)?s?|section|(?<![A-Za-z])s\.)[-\s]*6\s*\.\s*8",
    re.I)
CONTEMPT = re.compile(r"\bcontempt\s+application\b", re.I)
DISPOSED = re.compile(r"\b(?:stands\s+)?dispos(?:e[d]?|ing)(?:\s+off?)?\b", re.I)
WITHDRAW = re.compile(
    r"\bprays?\s+to\s+withdraw\b"
    r"|\bwithdraw(?:s|n)?\s+the\s+(?:present\s+)?(?:writ\s+)?petition\b"
    r"|\bpetition\s+is\s+withdrawn\b",
    re.I,
)
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
# 6.5 mentioned (often by counsel) but the Court granted relief. SCJ-411.
GRANT_NOT_RELEGATE = re.compile(
    r"\bwe intervene\b"
    r"|\bforthwith comply\b"
    r"|\b(?:writ\s+)?petition is allowed\b"
    r"|\bmandamus is issued\b",
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
    r"\belectricity\s+bills?"
    r"|\binflated\b|\bexaggerated\b"
    r"|\bdisputed\s+(?:electricity\s+)?bills?"
    r"|\bcorrect(?:ness|ion)\s+of\s+(?:any\s+|the\s+)?bill"
    r"|\bincorrect\s+bill(?:ing|s)?"
    r"|\bbilling\s+dispute|\bbill\s+dispute"
    r"|\barrears\s+of\s+the\s+electricity"
    r"|\bunpaid\s+amount\s+of\s+electricity"
    r"|\bdemand\s+notice\b"
    r"|\bexorbitant\s+bills?\b"
    r"|\belectricity\s+(?:dues|charges|demand)\b"
    r"|\bimpugned\s+(?:current\s+|revised\s+|electricity\s+)?bills?"
    r"|\bcurrent\s+(?:electricity\s+)?bills?"
    r"|\bwrong\s+bills?"
    r"|\bincorrect\s+(?:imposition\s+of\s+)?bills?"
    r"|\belectricity\s+amount\s+due"
    r"|\bunpaid\s+(?:electrical|electricity)\s+dues"
    r"|\brecovery\s+(?:citation|certificate|notice)",
    re.I,
)
RELEGATE = re.compile(
    r"\brelegat(?:e|ed|ing)\b"
    r"|\balternative\s+remedy\b"
    r"|\bhas\s+a\s+remedy\s+to\s+approach\b"
    r"|\bapproach(?:es)?\s+the\s+competent\s+authority\b"
    r"|\bapproach(?:es)?\s+(?:the\s+)?(?:executive\s+engineer|junior\s+engineer)\b"
    r"|\bcan\s+still\s+approach\b"
    r"|\bfile\s+a\s+(?:fresh\s+)?representation\b"
    r"|\bfile\s+an?\s+application\b"
    r"|\b(?:move|make)\s+(?:an?\s+)?(?:appropriate\s+|fresh\s+)?application\b"
    r"|\bmove\s+a\s+fresh\s+representation\b"
    r"|\bpermitting\s+the\s+petitioner\s+to\s+file\b"
    r"|\bfresh\s+representation\b"
    r"|\bliberty\s+to\s+(?:file|approach|apply)\b"
    r"|\bliberty\s+(?:is\s+)?granted\s+to\s+(?:the\s+)?petitioner\s+to\s+"
    r"(?:move|make|file|approach|apply)\b"
    r"|\b(?:can\s+)?raise\s+(?:a\s+)?(?:comprehensive\s+)?dispute\b"
    r"|\bshould\s+file\s+a\s+challenge"
    r"|\bcan\s+get\s+the\s+bill\s+corrected"
    r"|\bmore\s+appropriately\s+(?:be\s+)?examined"
    r"|\bif\s+the\s+petitioner\s+approaches"
    r"|\bapplies?\s+for\s+correction",
    re.I,
)
ASSESS_CUE = re.compile(
    r"\brecovery\s+citation"
    r"|\belectricity\s+dues"
    r"|\bimpugned\s+demand"
    r"|\bassessment\s+procedure"
    r"|\bdisputed\s+demand",
    re.I,
)
HEARING_GAP = re.compile(
    r"\bno\s+opportunity\s+of\s+hearing"
    r"|\bopportunity\s+of\s+hearing\s+was\s+(?:not\s+)?given"
    r"|\bnot\s+clear\s+if\s+assessment"
    r"|\bassessment\s+procedure\s+has\s+been"
    r"|\bone\s+opportunity\s+is\s+given",
    re.I,
)
ASSESSING_OFFICER = re.compile(
    r"\bassessing\s+officer\b"
    r"|\brespondent\s+No\.?\s*\d+\s+under\s+Cl[au]{0,2}se\s+6\s*\.\s*8",
    re.I,
)
DEPOSIT_68 = re.compile(r"\bdepositing\s+Rs", re.I)
QUASH_ASSESS = re.compile(
    r"(?:recovery\s+(?:notices?|citations?)|assessment(?:\s+order)?|"
    r"demand\s+notices?)\s+(?:are|is|were|was)\s+quashed"
    r"|\bquashed\s+and\s+set\s+aside\b",
    re.I,
)
# s.126/135/FIR/theft mention is not a 6.5 veto when the Court leaves those facts open.
THEFT_NOT_DECIDED = re.compile(
    r"cannot\s+be\s+decided"
    r"|not\s+decided\s+(?:in|under)\s+writ"
    r"|without\s+adverting"
    r"|without\s+examining"
    r"|at\s+the\s+first\s+instance",
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
ORDER_DATE = re.compile(
    r"Order\s+Date\s*:-\s*(\d{1,2})\.(\d{1,2})\.(20\d{2})\b", re.I)
NEUTRAL = re.compile(r"Neutral\s+Citation\s+No\.\s*-\s*(\S+)", re.I)
PET = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Petitioner", re.I)
APP = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Applicant", re.I)
RESP = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Respondent", re.I)
OPP = re.compile(r"(?m)^(.+?)\n\s*\.{3,}\s*Opposite", re.I)
# Allahabad cause-list captions: "Petitioner :- Sahdeo Singh"
PET_COLON = re.compile(r"(?im)^(?:Petitioners?|Applicants?)\s*:-\s*(.+)$")
RESP_COLON = re.compile(
    r"(?im)^(?:Respondents?|Opposite\s+Part(?:y|ies))\s*:-\s*(.+)$")
RS = re.compile(r"Rs\.?\s*([\d,]+(?:\.\d+)?)\s*/?-?", re.I)
CODE_YEAR = re.compile(r"Electricity\s+Supply\s+Code,?\s*(20\d{2})", re.I)
DAYS = re.compile(
    r"within\s+(?:a\s+period\s+of\s+)?(\d+|ten|one|two|fifteen)\s+"
    r"(days?|months?|weeks?)", re.I)
STAY = re.compile(
    r"for\s+(?:a\s+period\s+of\s+)?(\d+|ten|one|two)\s+(days?|months?).{0,80}"
    r"(?:not\s+disconnect|no\s+coercive|shall\s+not\s+disconnect)", re.I)
OFFICER = re.compile(
    r"(Assessing\s+Officer|Junior\s+Engineer|Executive\s+Engineer|"
    r"competent\s+authority)", re.I)
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


def _theft_blocks_65(txt: str) -> bool:
    """Hard veto only when theft/126/135/FIR is mentioned and not left open."""
    if not _has_theft(txt):
        return False
    return not THEFT_NOT_DECIDED.search(txt)


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
    else:
        od = ORDER_DATE.findall(txt)
        if od:
            day, month, year = od[-1]
            month, day = int(month), int(day)
            if 1 <= month <= 12 and 1 <= day <= 31:
                date_iso = f"{year}-{month:02d}-{day:02d}"
                date_display = datetime(int(year), month, day).strftime("%d %B %Y").lstrip("0")
    pet_m = PET.search(txt) or APP.search(txt)
    resp_m = RESP.search(txt) or OPP.search(txt)
    petitioner = title_case_name(pet_m.group(1) if pet_m else "")
    respondent = title_case_name(resp_m.group(1) if resp_m else "")
    if not petitioner:
        cm = PET_COLON.search(txt)
        if cm:
            petitioner = title_case_name(cm.group(1))
    if not respondent:
        cm = RESP_COLON.search(txt)
        if cm:
            respondent = title_case_name(cm.group(1))
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
    nm = NEUTRAL.search(txt)
    how = ""
    if re.search(r"\binfructuous\b", txt, re.I):
        how = "infructuous"
    elif re.search(r"\bmisconceived\b", txt, re.I):
        how = "misconceived"
    return {
        "title": title,
        "neutral_citation": nm.group(1).strip() if nm else "",
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


def classify_65(txt: str, fp: dict, bill_rx=None, relegate_rx=None) -> dict:
    bill_rx = bill_rx or BILL
    relegate_rx = relegate_rx or RELEGATE
    info = _base(fp, [])
    r = info["reasons"]
    pages, words, cites = info["pages"], info["words"] or len(txt.split()), info["cites"]
    if CONTEMPT.search(txt):
        r.append("veto: contempt application")
    if WITHDRAW.search(txt):
        r.append("veto: withdrawn")
    if CLAUSE_65B.search(txt):
        r.append("veto: clause 6.5(b)")
    if INTERLOC.search(txt):
        r.append("veto: interlocutory listing/adjournment")
    if DISMISSED_WRIT.search(txt):
        r.append("veto: writ dismissed")
    if GRANT_NOT_RELEGATE.search(txt):
        r.append("veto: court granted relief (not a 6.5 relegation)")
    if _has_theft(txt):
        if _theft_blocks_65(txt):
            r.append("veto: theft/126/135/FIR")
        else:
            r.append("note: 126/135/FIR/theft mentioned, not decided")
    if cites:
        r.append(f"veto: citation_count={cites}")
    if isinstance(pages, int) and pages > MAX_PAGES:
        r.append(f"veto: pages={pages}>{MAX_PAGES}")
    if words > MAX_WORDS_65:
        r.append(f"veto: words={words}>{MAX_WORDS_65}")
    if not CLAUSE_65.search(txt):
        r.append("no: clause 6.5 not found")
    if not bill_rx.search(txt):
        r.append("no: not a billing grievance")
    if not DISPOSED.search(txt):
        r.append("no: not disposed")
    if not relegate_rx.search(txt):
        r.append("no: no relegation language")
    ok = not any(x.startswith("veto:") or x.startswith("no:") for x in r)
    if ok:
        r.append("pass: 6.5 billing relegation")
    slots = parse_caption(txt) if ok or CLAUSE_65.search(txt) else {}
    if slots and _has_theft(txt):
        slots["theft_mentioned"] = True
    return {
        "verdict": "STENCIL" if ok else "NO",
        "family": "6.5-billing-relegation" if ok else None,
        "reasons": r, "pages": pages, "words": words,
        "slots": slots,
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


def _fmt_rs(raw: str) -> str:
    raw = (raw or "").replace(",", "").strip()
    if not raw:
        return ""
    out = "Rs." + raw
    if "." not in raw:
        out += "/-"
    return out


def _enrich_68_slots(txt: str, slots: dict) -> dict:
    slots = dict(slots or {})
    amounts = RS.findall(txt)
    if amounts and not slots.get("recovery_amount"):
        slots["recovery_amount"] = _fmt_rs(amounts[0])
    dm = re.search(r"depositing\s+Rs\.?\s*([\d,]+(?:\.\d+)?)", txt, re.I)
    if dm:
        slots["deposit_amount"] = _fmt_rs(dm.group(1))
    if re.search(r"\bassessing\s+officer\b", txt, re.I):
        slots["officer"] = "Assessing Officer"
    elif not slots.get("officer") or slots.get("officer") == "competent authority":
        slots["officer"] = "Assessing Officer"
    days = DAYS.findall(txt)
    for n, unit in reversed(days or []):
        if "month" in unit.lower():
            n = WORD_NUM.get(str(n).lower(), n)
            slots["decide_within"] = f"{n} {unit.lower()}"
            break
    if re.search(r"recovery shall revive", txt, re.I):
        slots["recovery_revives"] = True
    return slots


def classify_68(txt: str, fp: dict) -> dict:
    """Recovery-citation / no-hearing / deposit / 6.8 AO clones."""
    info = _base(fp, [])
    r = info["reasons"]
    pages, words, cites = info["pages"], info["words"] or len(txt.split()), info["cites"]
    if CONTEMPT.search(txt):
        r.append("veto: contempt application")
    if WITHDRAW.search(txt):
        r.append("veto: withdrawn")
    if INTERLOC.search(txt):
        r.append("veto: interlocutory listing/adjournment")
    if DISMISSED_WRIT.search(txt):
        r.append("veto: writ dismissed")
    if GRANT_NOT_RELEGATE.search(txt):
        r.append("veto: court granted relief")
    if QUASH_ASSESS.search(txt):
        r.append("veto: assessment/recovery quashed")
    if _has_theft(txt):
        if _theft_blocks_65(txt):
            r.append("veto: theft/126/135/FIR")
        else:
            r.append("note: 126/135/FIR/theft mentioned, not decided")
    if cites:
        r.append(f"veto: citation_count={cites}")
    if isinstance(pages, int) and pages > MAX_PAGES:
        r.append(f"veto: pages={pages}>{MAX_PAGES}")
    if words > MAX_WORDS_68:
        r.append(f"veto: words={words}>{MAX_WORDS_68}")
    if not CLAUSE_68_NAMED.search(txt):
        r.append("no: clause 6.8 not found")
    if not ASSESS_CUE.search(txt):
        r.append("no: not a recovery/assessment demand")
    if not HEARING_GAP.search(txt):
        r.append("no: no hearing-gap / assessment-procedure cue")
    if not ASSESSING_OFFICER.search(txt):
        r.append("no: no Assessing Officer")
    if not DEPOSIT_68.search(txt):
        r.append("no: no deposit condition")
    if not DISPOSED.search(txt):
        r.append("no: not disposed")
    ok = not any(x.startswith("veto:") or x.startswith("no:") for x in r)
    if ok:
        r.append("pass: 6.8 assessment-hearing relegation")
    slots = {}
    if ok or CLAUSE_68_NAMED.search(txt):
        slots = _enrich_68_slots(txt, parse_caption(txt))
    return {
        "verdict": "STENCIL" if ok else "NO",
        "family": "6.8-assessment-hearing" if ok else None,
        "reasons": r, "pages": pages, "words": words,
        "slots": slots,
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
    for fn in (classify_65, classify_68, classify_contempt):
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
    if slots.get("theft_mentioned"):
        flags.append(
            "The Court mentions Section 126/135 or theft/FIR but does not decide "
            "those facts; the consumer is pointed to Clause 6.5. Recorded, not "
            "silently corrected."
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
    rec = {
        "case_id": cid,
        "title": slots.get("title") or "",
        "neutral_citation": slots.get("neutral_citation") or "",
        "court": "Allahabad High Court",
        "bench": slots.get("bench") or "",
        "coram": slots.get("coram") or "",
        "date_of_judgment": slots.get("date_of_judgment") or "",
        "date_display": slots.get("date_display") or "",
        "docket": slots.get("docket") or "",
        "page_count": fp.get("page_count"),
        "significance": "ordinary",
        "outcome": "alternate_remedy",
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
    if slots.get("theft_mentioned"):
        rec["not_decided"].append({
            "point": "Section 126/135 or theft/FIR facts mentioned in the order",
            "note": "Not decided in writ; the billing grievance is left to Clause 6.5.",
            "docid": "",
            "paras": "",
        })
    return rec


def fill_68(cid: str, fp: dict, slots: dict) -> dict:
    recovery = slots.get("recovery_amount") or slots.get("bill_amount") or ""
    deposit = slots.get("deposit_amount") or ""
    officer = slots.get("officer") or "Assessing Officer"
    decide = slots.get("decide_within") or "two months"
    rec_bit = f" of {recovery}" if recovery else ""
    dep_bit = f" of {deposit}" if deposit else ""
    revive = slots.get("recovery_revives")
    revive_bit = (
        " If the deposit or application is not made in time, the recovery revives."
        if revive else ""
    )
    headnote = (
        "Where a recovery citation for electricity dues is challenged and it is "
        "not clear that Clause 6.8 assessment procedure was followed or that a "
        "hearing was given, the writ is disposed of without deciding the demand. "
        f"Subject to deposit{dep_bit} towards the disputed demand, the consumer "
        f"may apply to the {officer}, who shall decide the objection by a reasoned "
        f"order after personal hearing, preferably within {decide}."
        f"{revive_bit}"
    )
    petitioner = slots.get("petitioner") or "The petitioner"
    facts = (
        f"{petitioner} challenged a recovery citation{rec_bit} towards electricity "
        "dues, alleging that no opportunity of hearing was given before the demand. "
        "The Court did not decide whether assessment procedure under Clause 6.8 "
        "had been complied with."
    )
    holding = (
        "A writ challenging a recovery citation for electricity dues is disposed "
        "of without examining whether Clause 6.8 assessment procedure was followed "
        "or the demand's validity. Subject to deposit"
        f"{dep_bit} towards the disputed demand, the consumer may file an "
        f"objection before the {officer} under Clause 6.8 of the U.P. Electricity "
        "Supply Code, 2005. The officer shall decide by a reasoned and speaking "
        f"order after confronting the consumer with adverse material and granting "
        f"personal hearing, preferably within {decide}."
        f"{revive_bit}"
    )
    unit = {
        "provision": "UP-2005::6.8",
        "code": "U.P. Electricity Supply Code, 2005",
        "clause": "6.8",
        "topic": "Assessment objection — relegation to Clause 6.8 after deposit",
        "type": "supply_code",
        "holding": holding,
        "paras": "",
    }
    flags = []
    if slots.get("code_year") and slots["code_year"] != "2005":
        flags.append(
            f"The order cites 'Clause 6.8 of the UP Electricity Supply Code, "
            f"{slots['code_year']}'. The Code in force is the 2005 Code. "
            "Recorded, not silently corrected."
        )
    if flags:
        unit["flag"] = " ".join(flags)
    disp = "Writ disposed of; petitioner relegated to Clause 6.8"
    if deposit:
        disp += f" after deposit of {deposit}"
    return {
        "case_id": cid,
        "title": slots.get("title") or "",
        "neutral_citation": slots.get("neutral_citation") or "",
        "court": "Allahabad High Court",
        "bench": slots.get("bench") or "",
        "coram": slots.get("coram") or "",
        "date_of_judgment": slots.get("date_of_judgment") or "",
        "date_display": slots.get("date_display") or "",
        "docket": slots.get("docket") or "",
        "page_count": fp.get("page_count"),
        "significance": "ordinary",
        "outcome": "alternate_remedy",
        "disposition": disp,
        "headnote": headnote,
        "facts": facts,
        "holding_units": [unit],
        "principle_tags": [],
        "not_decided": [
            {
                "point": "Whether Clause 6.8 assessment procedure was followed, and the merits of the demand",
                "note": "Left to the Assessing Officer after deposit and hearing.",
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
        "neutral_citation": slots.get("neutral_citation") or "",
        "court": "Allahabad High Court",
        "bench": slots.get("bench") or "Single Judge",
        "coram": slots.get("coram") or "",
        "date_of_judgment": slots.get("date_of_judgment") or "",
        "date_display": slots.get("date_display") or "",
        "docket": slots.get("docket") or "",
        "page_count": fp.get("page_count"),
        "significance": "procedural",
        "outcome": "none",
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
    "6.8-assessment-hearing": fill_68,
    "contempt-6.5-dismissed": fill_contempt,
}


def slots_fillable(slots: dict) -> bool:
    """True when parse_caption produced a title the filler can write."""
    return bool((slots or {}).get("title"))


def fill(cid: str, fp: dict, family: str, slots: dict) -> dict:
    fn = FILLERS.get(family)
    if not fn:
        raise SystemExit(f"FAILED · no filler for family {family!r}")
    rec = fn(cid, fp, slots)
    rec["model"] = "stencil"
    missing = [k for k in ("title", "holding_units") if not rec.get(k)]
    if missing:
        raise SystemExit(
            f"FAILED · stencil fill incomplete for {cid} ({family}): "
            f"missing {', '.join(missing)}"
        )
    return rec


def classify_family(txt: str, fp: dict, family: str) -> dict:
    return {
        "6.5-billing-relegation": classify_65,
        "contempt-6.5-dismissed": classify_contempt,
        "6.8-assessment-hearing": classify_68,
        "listing-only": classify_listing,
    }[family](txt, fp)


def pending_scan():
    """Classify unprocessed input PDFs. Read-only."""
    inp = os.path.join(SC, "input")
    if not os.path.isdir(inp):
        return
    try:
        import fitz
    except ImportError:
        print("\n=== pending queue === skipped (PyMuPDF not installed)")
        return
    pdfs = []
    for root, _dirs, files in os.walk(inp):
        for fn in files:
            if fn.lower().endswith(".pdf") and " (1)" not in fn:
                pdfs.append(os.path.join(root, fn))
    if not pdfs:
        print("\n=== pending queue === empty")
        return
    print()
    print(f"=== pending queue  n={len(pdfs)} PDFs in input/ ===")
    n68 = n65 = 0
    for path in sorted(pdfs):
        try:
            d = fitz.open(path)
            txt = "\n".join(p.get_text() for p in d)
            pages = d.page_count
            d.close()
        except Exception as e:
            print(f"  SKIP {os.path.basename(path)}: {e}")
            continue
        fp = {"page_count": pages, "word_count": len(txt.split()), "citation_count": 0}
        hit = classify(txt, fp, live_only=True)
        rel = os.path.relpath(path, inp)
        if hit.get("family") == "6.8-assessment-hearing":
            n68 += 1
            print(f"  6.8  {rel}  pp={pages} w={fp['word_count']}")
        elif hit.get("family") == "6.5-billing-relegation":
            n65 += 1
            print(f"  6.5  {rel}  pp={pages} w={fp['word_count']}")
    print(f"  pending would-be  6.8={n68}  live-6.5={n65}")


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
    seen, dry_families = [], []
    for f in LIVE + ("listing-only",):
        if f not in seen:
            seen.append(f)
            dry_families.append(f)
    for family in dry_families:
        live = family in LIVE
        tag = "LIVE" if live else "NOT LIVE"
        s = score_family(family, only)
        print()
        print(f"=== {family}  [{tag}]  TP={s['tp']} TN={s['tn']} FP={s['fp']} FN={s['fn']} ===")
        print(f"{'id':8} {'got':8} {'expect':8} {'sc':3} reasons")
        for cid, got, expected, sc, hit in s["rows"]:
            if sc == "TN" and not only and family == "listing-only" and got == "no":
                if cid not in (EXPECTED.get(family) or {}):
                    continue
            why = "; ".join((hit.get("reasons") or [])[:4])
            print(f"{cid:8} {got:8} {expected:8} {sc:3} {why}")
        if family in LIVE and (s["fp"] or s["fn"]):
            rc = 1
        if family == "listing-only" and s["tp"]:
            print("NOTE: listing-only had TPs — still not wired (see module docstring).")
        if live and s["fp"] == 0 and s["fn"] == 0:
            print("ok to wire")
    if not only:
        pending_scan()

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


def write_record(cid: str | None, out: str | None, force: bool,
                 ticket_path: str | None = None) -> int:
    ticket = None
    tpath = ticket_path or TICKET
    if os.path.exists(tpath):
        with open(tpath, encoding="utf-8") as f:
            ticket = json.load(f)
    from_ticket = not cid
    if not cid:
        if not ticket or not ticket.get("case_id"):
            print("FAILED · no ticket and no case_id", file=sys.stderr)
            return 1
        if ticket.get("status") not in ("READY", "AUTHORING", "CLAIMING"):
            print(f"FAILED · ticket.status={ticket.get('status')!r}",
                  file=sys.stderr)
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
    ap.add_argument("--ticket", help="ticket JSON (default tmp/NEXT_TICKET.json)")
    ap.add_argument("case_id", nargs="?", help="SCJ-NNN")
    args = ap.parse_args(argv)
    if args.write:
        return write_record(args.case_id, args.out, args.force, args.ticket)
    return dry_run(args.case_id)


if __name__ == "__main__":
    sys.exit(main())
