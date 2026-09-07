#!/usr/bin/env python3
"""Categorised digest of all principle tags in the spine -> HTML, then PDF.

Usage:
  python tools/gen_principles_digest.py
  python tools/gen_principles_digest.py --date 2026-09-07

Writes:
  supply-code/tmp/principles_digest.html
  supply-code/booklet/Principles_Digest_categorised_<YYYY-MM-DD>.pdf

Does not overwrite earlier dated (or undated) booklet PDFs.
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finalize_scj

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "supply-code")
SPINE = os.path.join(SC, "jurisprudence", "index.json")
SUMM = os.path.join(SC, "summaries", "json")
BOOKLET = os.path.join(SC, "booklet")
HTML_OUT = os.path.join(SC, "tmp", "principles_digest.html")

html_esc = html.escape

CATS = [
    ("A", "Statutory architecture, vires & interpretation",
     "How the Code is read against the Act: hierarchy, retrospectivity, headings, and ultra vires."),
    ("B", "Duty to supply & access to a connection",
     "Section 43, occupier and tenant connections, indemnity bonds, and mandamus to connect."),
    ("C", "Arrears, transferee & occupier liability",
     "Who pays predecessor dues: premises charge, auction purchasers, landlords and directors."),
    ("D", "Insolvency interface — IBC, SICA & sick units",
     "Clean-slate, section 238 override, moratorium, and relief-undertaking protection."),
    ("E", "Premises, site, estimates, feeders & lines",
     "Independent feeders, tapping, change of site, estimates, and landowner objections."),
    ("F", "Security, load, tariff & regulatory economics",
     "Additional security, load change, tariff orders, rebates, and Commission-determined charges."),
    ("G", "Metering",
     "Clause 5.6 testing, defective and slow meters, check meters, and meter-reading disputes."),
    ("H", "Billing, payment, instalments & limitation",
     "Clause 6.5 objections, 6.14 instalments, first-due, and the two-year bar (s.56 / Cl. 6.15)."),
    ("I", "Disconnection, reconnection & restoration",
     "Permanent disconnection, notice, and restoration on deposit or bank guarantee."),
    ("J", "Unauthorised use (s.126) & assessment",
     "What is UUE, the 1.5× rate, notice and hearing, provisional and final assessment."),
    ("K", "Theft (s.135) & Chapter VIII of the Code",
     "Civil theft assessment, evidence, acquittal, and the Code’s Chapter VIII machinery."),
    ("L", "Recovery of assessment, citations & the 1958 Act",
     "When recovery may issue, stay pending appeal, tehsil citations, and collection charges."),
    ("M", "Fora — CGRF, Ombudsman, Inspector & Lok Adalat",
     "Who may decide what: consumer fora, ombudsman limits, Electrical Inspector, PLA."),
    ("N", "Appeals (s.127) & statutory remedies",
     "The section 127 appeal, independent judgment, pre-deposit, and the vested right of appeal."),
    ("O", "Writ, alternative remedy & public-law doctrines",
     "Article 226, Whirlpool exceptions, relegation, laches, clean hands, and costs."),
    ("P", "Criminal process, compounding & s.482",
     "Arrest safeguards, FIR, compounding, summoning, and inherent-power quashing."),
    ("Q", "Adjacent & miscellaneous",
     "Doctrines that sit beside the Code: arbitration, departmental inquiry, and residual."),
]
CAT_CODES = [c[0] for c in CATS]

# Ordered keyword rules. First match wins. Tokens are matched as substrings of the kebab tag.
RULES = [
    ("D", ("ibc", "sica", "cirp", "sick-unit", "sick-relief", "relief-undertaking",
           "section-238", "section-32a", "moratorium", "clean-slate", "waterfall",
           "corporate-debtor")),
    ("P", ("s135-arrest", "s135-1", "s135-2", "s135-summoning", "section-482",
           "compounding", "fir", "arrest-safeguard", "s138-", "s141-", "s151-",
           "criminal", "summoning", "charge-sheet")),
    ("O", ("contempt", "procedural-listing", "want-of-prosecution", "infructuous",
           "relegate", "whirlpool", "alternative-remedy", "alternate-remedy")),
    ("K", ("theft", "s135", "8.2", "chapter-viii", "clause-8.2", "8.1b-theft",
           "theft-uue", "theft-assessment", "theft-cannot", "theft-must",
           "surcharge-vs-theft")),
    ("N", ("s127", "section-127", "appellate", "vested-right-of-appeal",
           "127-appeal")),
    ("L", ("recovery-citation", "recovery-must", "recovery-of-assessment",
           "recovery-demand", "no-recovery", "1958", "upgeu", "collection-charges",
           "tehsil", "citation")),
    ("J", ("s126", "126-", "uue", "unauthorised-use", "unauthorised-connected",
           "6.8", "clause-6.8", "opportunity-before-final", "provisional-assessment",
           "final-assessment", "assessing", "assessment-must", "assessment-final",
           "assessment-service", "8.1", "clause-8.1", "1.5x", "365-days")),
    ("M", ("7.10", "cgrf", "ombudsman", "consumer-forum", "consumer-grievance",
           "lok-adalat", "electrical-inspector", "s26-6", "forum")),
    ("G", ("meter", "5.6", "5.7", "5.9", "check-meter", "slow-meter",
           "defective-meter")),
    ("H", ("6.5", "6.14", "6.15", "billing", "instal", "installment",
           "first-due", "two-year", "s56", "56(2)", "56-2", "limitation",
           "bill-correctness", "bill-computation", "due-date", "billing-cycle")),
    ("I", ("disconnect", "reconnect", "restor", "4.37", "4.38", "4.39",
           "permanent-disconnect")),
    ("F", ("4.20", "4.49", "4.27", "additional-security", "security-deposit",
           "prepayment", "tariff", "load-factor", "load-reduction", "rebate",
           "s47-4", "commission-determined", "mcg-", "lps-", "s62-6")),
    ("E", ("feeder", "3.4", "4.29", "4.5", "tapping", "landowner", "estimate",
           "change-of-site", "service-line", "4.8", "s67-", "single-point",
           "transformer")),
    ("C", ("arrears", "4.3", "4.44", "transferee", "auction-purchaser",
           "director-liab", "director-not-personally", "premises-specific",
           "as-is-where-is", "isha-marbles", "corporate-veil")),
    ("B", ("4.4", "occupier", "occupant", "indemnity", "s43-duty", "s43-",
           "tenant-connection", "landlord-consent", "landlord-noc",
           "duty-to-supply", "new-connection", "pending-private-dispute")),
    ("A", ("s174", "vires", "retrospective", "heading", "piecemeal",
           "statute-prevails", "s50", "s181", "legal-fiction", "liberally",
           "construction", "precedent-under-superseded", "unilateral-acceptance",
           "statutory-contract", "statutory-supply-code", "not-confined-to-s50")),
    ("O", ("relegate", "alternative-remedy", "alternate-remedy", "whirlpool",
           "article-226", "writ", "laches", "clean-hands", "want-of-prosecution",
           "infructuous", "contempt", "listing", "procedural-listing",
           "disputed-questions-of-fact", "voluntary-payment", "own-wrong",
           "waiver", "approbate", "costs")),
]

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}

SIG_RANK = {"significant": 0, "ordinary": 1, "procedural": 2, "none": 3}


def datekey(s):
    s = (s or "").strip()
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
    if m:
        return (int(m.group(3)), MONTHS.get(m.group(2).lower(), 6), int(m.group(1)))
    m = re.search(r"(\d{4})", s)
    return (int(m.group(1)), 6, 15) if m else (9999, 1, 1)


def label(tag):
    t = tag.replace("-", " ")
    t = re.sub(r"\bs(\d+)\b", r"s.\1", t)
    return t[0].upper() + t[1:] if t else tag


def court_badge(c):
    c = (c or "").lower()
    if "supreme" in c:
        return ("SC", "bg-sc")
    if "allahabad" in c:
        return ("All HC", "bg-hc")
    if "high court" in c or "hc" in c:
        return ("HC", "bg-oh")
    return ("—", "bg-x")


def court_rank(c):
    b, _ = court_badge(c)
    return {"SC": 0, "All HC": 1, "HC": 2}.get(b, 3)


def short_party(title):
    t = re.sub(r"^(M/s\.?|Smt\.?|Sri\.?|Shri\.?|Dr\.?)\s+", "", title or "", flags=re.I)
    t = re.split(r"\s+v\.\s+", t, maxsplit=1, flags=re.I)[0]
    return (t[:38] + "…") if len(t) > 39 else t


def cite_id(cid, significant):
    """SCJ-1085 -> SCJ_1085 or SCJ_1085_S."""
    core = (cid or "").replace("-", "_")
    if significant:
        return core + "_S"
    return core


def classify(tag):
    t = (tag or "").lower()
    for code, needles in RULES:
        for n in needles:
            if n.lower() in t:
                return code
    return "Q"


def weight_class(n):
    if n >= 10:
        return "leading", "w-lead"
    if n >= 5:
        return "extensive", "w-ext"
    if n >= 2:
        return "recurring", "w-rec"
    return "isolated", "w-iso"


STYLE = """<style>
@page{ size:A4; margin:16mm 14mm 18mm; }
body{ font-family:Georgia,'Liberation Serif',serif; color:#1d2430; font-size:9.4pt; line-height:1.48; }
.kicker{ font-family:Arial,'Liberation Sans',sans-serif; font-size:7.2pt; letter-spacing:.18em;
  text-transform:uppercase; color:#6b7787; margin:0 0 4pt; }
h1{ font-family:Arial,'Liberation Sans',sans-serif; font-size:22pt; color:#0f2f4c; margin:0 0 3pt;
  letter-spacing:-.2pt; font-weight:700; }
.sub{ font-family:Arial,sans-serif; font-size:9.2pt; color:#5b6b7b; margin:0 0 8pt; }
.rule{ height:2.6pt; background:#0f2f4c; margin:0 0 1.6pt;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.rule2{ height:.7pt; background:#c4a35a; margin:0 0 12pt;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.stats{ display:flex; gap:6pt; margin:0 0 11pt; }
.stat{ flex:1; border:.5pt solid #d6dee7; border-radius:3pt; padding:7pt 6pt 6pt; text-align:center;
  background:#f7f9fb; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.stat b{ display:block; font-family:Arial,sans-serif; font-size:16pt; color:#0f2f4c; font-weight:700; line-height:1.1; }
.stat span{ font-family:Arial,sans-serif; font-size:6.2pt; letter-spacing:.08em; text-transform:uppercase; color:#6b7787; }
.note{ background:#eef4fa; border-left:3.5pt solid #2f6f9f; padding:7pt 10pt; margin:0 0 9pt;
  font-size:8.6pt; color:#2a3b4c; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.legend{ font-family:Arial,sans-serif; font-size:7.6pt; color:#4a5967; margin:0 0 8pt; }
.sw{ display:inline-block; width:9pt; height:7pt; border:.5pt solid #c9d3df; margin:0 3pt 0 8pt;
  vertical-align:-1pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.sw-lead{ background:#f4ead2; border-color:#d9c48a; } .sw-ext{ background:#e3eef7; }
.sw-rec{ background:#f2f5f8; } .sw-iso{ background:#fff; }
.howto{ font-size:8.4pt; color:#4a5967; margin:0 0 10pt; }
.toc-h{ font-family:Arial,sans-serif; font-weight:700; font-size:10pt; color:#0f2f4c; margin:0 0 5pt; }
.toc{ font-family:Arial,sans-serif; font-size:8.5pt; color:#26384a; columns:2; column-gap:14mm; margin-bottom:4pt; }
.toc div{ break-inside:avoid; margin-bottom:2.2pt; display:flex; justify-content:space-between; gap:8pt; }
.toc b{ color:#0f2f4c; }
.toc .n{ color:#7a8794; font-weight:700; white-space:nowrap; }
.cathead{ font-family:Arial,sans-serif; font-weight:700; font-size:12.2pt; color:#fff; background:#12405f;
  padding:6pt 10pt; margin:16pt 0 2pt; border-radius:3pt; break-after:avoid;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.cathead .meta{ font-size:7.6pt; font-weight:600; letter-spacing:.04em; opacity:.85; margin-left:8pt; }
.catblurb{ font-size:8.6pt; color:#5b6b7b; margin:0 0 8pt 2pt; font-style:italic; }
.p{ border:.5pt solid #d6dee7; border-left:3.2pt solid #9aa8b5; border-radius:3pt; padding:6pt 9pt 7pt;
  margin:0 0 7pt; break-inside:avoid; background:#fff;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.p.w-lead{ border-left-color:#c4a35a; background:#fbf8f0; }
.p.w-ext{ border-left-color:#2f6f9f; background:#f7fafc; }
.p.w-rec{ border-left-color:#8aa4b8; }
.p.w-iso{ border-left-color:#c9d3df; }
.p-h{ font-family:Arial,sans-serif; font-weight:700; font-size:9.7pt; color:#123; margin-bottom:2pt; }
.p-h .num{ color:#2f6f9f; margin-right:5pt; }
.cnt{ font-family:Arial,sans-serif; font-size:6.8pt; font-weight:700; color:#0f2f4c; background:#e7eef5;
  border:.5pt solid #b9cbdd; border-radius:8pt; padding:0 6pt; margin-left:6pt; white-space:nowrap;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.gloss{ font-size:8.8pt; color:#33404d; margin:2pt 0 4pt; text-align:justify; }
.la{ font-family:Arial,sans-serif; font-size:7.3pt; color:#2f6f9f; margin:0 0 4pt; }
.la b{ letter-spacing:.08em; text-transform:uppercase; color:#7a8794; font-size:6.4pt; margin-right:4pt; }
.la i{ font-family:Georgia,serif; }
.chips{ font-family:Arial,sans-serif; font-size:7.4pt; line-height:1.9; }
.chip{ display:inline-block; background:#f4f7fa; border:.5pt solid #d3dde7; border-radius:3pt;
  padding:.4pt 5pt; margin:0 3pt 2pt 0; color:#26384a; white-space:nowrap;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.chip.sig{ background:#eef4e8; border-color:#b7cda8; }
.bdg{ font-size:6.2pt; font-weight:700; padding:0 3pt; border-radius:2pt; margin-left:3pt; vertical-align:1px;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.bg-sc{ background:#0f2f4c; color:#fff; } .bg-hc{ background:#2f6f9f; color:#fff; }
.bg-oh{ background:#6b8ba6; color:#fff; } .bg-x{ background:#c7d0db; color:#333; }
.yr{ color:#7a8794; font-weight:700; }
.more{ font-family:Arial,sans-serif; font-size:7.6pt; font-style:italic; color:#5b6b7b; margin-left:4pt; }
.idx-h{ font-family:Arial,sans-serif; font-weight:700; font-size:12.2pt; color:#fff; background:#12405f;
  padding:6pt 10pt; margin:16pt 0 6pt; border-radius:3pt;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.idx{ font-family:Arial,sans-serif; font-size:7.6pt; columns:2; column-gap:12mm; color:#26384a; }
.idx div{ break-inside:avoid; margin:0 0 1.6pt; }
.idx .cat{ color:#2f6f9f; font-weight:700; }
</style>"""


def pick_ten(cases, sig_of):
    """Significant first, then SC, then date ascending. Cap at 10."""
    def key(cc):
        cid = cc.get("case_id") or ""
        sig = sig_of.get(cid, "")
        return (SIG_RANK.get(sig, 4), court_rank(cc.get("court", "")),
                datekey(cc.get("date", "")), cid)
    ordered = sorted(cases, key=key)
    return ordered[:10], max(0, len(cases) - 10)


_GLOSS_STOP = {
    "the", "and", "for", "with", "from", "that", "this", "not", "under",
    "clause", "section", "to", "of", "in", "on", "a", "an", "is", "or",
    "by", "as", "at", "be", "no", "vs", "via",
}


def richest_gloss(cases, sig_of, tag=""):
    toks = [t for t in (tag or "").lower().split("-")
            if t not in _GLOSS_STOP and len(t) > 2]
    scored = []
    for cc in cases:
        a = re.sub(r"\s+", " ", (cc.get("application") or "").strip())
        if not a:
            continue
        al = a.lower()
        overlap = sum(1 for t in toks if t in al)
        sig = 0 if sig_of.get(cc.get("case_id"), "") == "significant" else 1
        # prefer applications that actually mention the tag's distinctive tokens
        scored.append((-overlap, sig, datekey(cc.get("date", "")), a))
    if not scored:
        return ""
    scored.sort()
    gloss = scored[0][3]
    if len(gloss) > 420:
        gloss = gloss[:417].rsplit(" ", 1)[0] + "…"
    return gloss


def lead_auths(shown):
    names = []
    seen = set()
    for cc in shown:
        for a in cc.get("lead_authorities") or []:
            if isinstance(a, dict):
                n = (a.get("name") or "").strip()
            else:
                n = str(a).strip()
            k = n.lower()
            if n and k not in seen:
                seen.add(k)
                names.append(n)
            if len(names) >= 3:
                return names
    return names


def load_significance():
    sig = {}
    spine = json.load(open(SPINE, encoding="utf-8"))
    for c in spine.get("cases") or []:
        cid = c.get("case_id")
        if cid and c.get("significance"):
            sig[cid] = c["significance"]
    # JSON is authoritative if spine is missing the field
    import glob
    for path in glob.glob(os.path.join(SUMM, "SCJ-*.json")):
        cid = os.path.splitext(os.path.basename(path))[0]
        if cid in sig:
            continue
        try:
            c = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        if c.get("significance"):
            sig[cid] = c["significance"]
    return sig


def build_html(date_iso: str) -> str:
    spine = json.load(open(SPINE, encoding="utf-8"))
    prins = spine["principles"]
    sig_of = load_significance()
    n_cases_corpus = spine.get("case_count") or len(spine.get("cases") or [])
    tagged_ids = set()
    for t, blob in prins.items():
        for cc in blob.get("cases") or []:
            tagged_ids.add(cc.get("case_id"))

    assign = {t: classify(t) for t in prins}
    n_apps = sum(len(prins[t].get("cases") or []) for t in prins)
    n_lead = sum(1 for t in prins if len(prins[t].get("cases") or []) >= 10)
    dt = datetime.datetime.strptime(date_iso, "%Y-%m-%d")
    date_display = dt.strftime("%-d %B %Y") if os.name != "nt" else dt.strftime("%#d %B %Y")

    out = [STYLE]
    out.append('<div class="kicker">Supply Code Jurisprudence &nbsp;&middot;&nbsp; Companion Reference</div>')
    out.append("<h1>Digest of Principles</h1>")
    out.append(
        f'<div class="sub">Every cross-cutting doctrine tagged in the corpus, classified by subject. '
        f"&middot; {html_esc(date_display)}</div>"
    )
    out.append('<div class="rule"></div><div class="rule2"></div>')
    out.append('<div class="stats">')
    for num, lab in (
        (len(prins), "Principles"),
        (n_apps, "Case-applications"),
        (len(tagged_ids), "Tagged cases"),
        (n_cases_corpus, "Cases in corpus"),
        (n_lead, "Leading (10+ cases)"),
        (len(CATS), "Subject classes"),
    ):
        out.append(f'<div class="stat"><b>{num}</b><span>{html_esc(lab)}</span></div>')
    out.append("</div>")
    out.append(
        '<div class="note">Drawn from the <b>principle_tags</b> field of the lean per-case records '
        "(tag &middot; application &middot; lead authorities &middot; pins). Each principle is filed "
        "once, under the subject that best describes it. A principle applied in ten or more cases is "
        "marked leading. Where a principle has more than ten case-applications, the card names ten "
        "(significant cases first) and records the remainder as <i>N more</i>. Within each class, "
        "principles are ordered by the number of case-applications, then alphabetically. An A–Z "
        "index is at the end. Significant cases are cited as <b>SCJ_NNNN_S</b>.</div>"
    )
    out.append(
        '<div class="legend">'
        '<span class="sw sw-lead"></span>Leading — 10 or more cases'
        '<span class="sw sw-ext"></span>Extensive — 5 to 9 cases'
        '<span class="sw sw-rec"></span>Recurring — 2 to 4 cases'
        '<span class="sw sw-iso"></span>Isolated — a single case'
        "</div>"
    )
    out.append(
        '<div class="howto">How to read a card: the title is the kebab-case tag, rendered in prose. '
        "The paragraph is the richest <i>application</i> recorded for that tag. Chips are the named "
        "cases that carry it, with year and court. A green chip is a <i>significant</i> decision.</div>"
    )
    out.append('<div class="toc-h">Contents <span style="font-weight:500;color:#7a8794">(principles · case-applications)</span></div>')
    out.append('<div class="toc">')
    for code, name, _blurb in CATS:
        tags = [t for t in prins if assign[t] == code]
        napps = sum(len(prins[t].get("cases") or []) for t in tags)
        out.append(
            f'<div><b>{code}.</b> {html_esc(name)} <span class="n">{len(tags)} · {napps}</span></div>'
        )
    out.append("</div>")

    for code, name, blurb in CATS:
        tags = [t for t in prins if assign[t] == code]
        tags.sort(key=lambda t: (-len(prins[t].get("cases") or []), t))
        napps = sum(len(prins[t].get("cases") or []) for t in tags)
        out.append(
            f'<div class="cathead">{html_esc(code)}. {html_esc(name)}'
            f'<span class="meta">{len(tags)} principles · {napps} case-applications</span></div>'
        )
        out.append(f'<div class="catblurb">{html_esc(blurb)}</div>')
        for i, t in enumerate(tags, 1):
            cases = prins[t].get("cases") or []
            shown, rest = pick_ten(cases, sig_of)
            wname, wcls = weight_class(len(cases))
            gloss = richest_gloss(cases, sig_of, t)
            las = lead_auths(shown)
            out.append(f'<div class="p {wcls}">')
            out.append(
                f'<div class="p-h"><span class="num">{code}-{i:02d}</span>'
                f"{html_esc(label(t))}"
                f'<span class="cnt">{len(cases)} case{"s" if len(cases) != 1 else ""}</span></div>'
            )
            if gloss:
                out.append(f'<div class="gloss">{html_esc(gloss)}</div>')
            if las:
                out.append(
                    '<div class="la"><b>Lead authorities</b> '
                    + "; ".join(f"<i>{html_esc(n)}</i>" for n in las)
                    + "</div>"
                )
            out.append('<div class="chips">')
            for cc in shown:
                cid = cc.get("case_id") or ""
                is_sig = sig_of.get(cid) == "significant"
                yr = datekey(cc.get("date", ""))[0]
                yr = "" if yr == 9999 else str(yr)
                bt, bc = court_badge(cc.get("court", ""))
                cls = "chip sig" if is_sig else "chip"
                out.append(
                    f'<span class="{cls}">{html_esc(cite_id(cid, is_sig))} &middot; '
                    f'{html_esc(short_party(cc.get("title", "")))} '
                    f'<span class="yr">{yr}</span>'
                    f'<span class="bdg {bc}">{bt}</span></span>'
                )
            if rest:
                out.append(f'<span class="more">{rest} more</span>')
            out.append("</div></div>")

    out.append('<div class="idx-h">A–Z index of principles</div>')
    out.append('<div class="idx">')
    for t in sorted(prins, key=lambda x: label(x).lower()):
        code = assign[t]
        n = len(prins[t].get("cases") or [])
        out.append(
            f'<div><span class="cat">{html_esc(code)}</span> {html_esc(label(t))} '
            f'<span class="yr">{n}</span></div>'
        )
    out.append("</div>")
    return "\n".join(out)


def render_pdf(html_path: str, pdf_path: str) -> None:
    chrome = finalize_scj.find_chrome()
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    ud = tempfile.mkdtemp(prefix="scj_prin_chrome_")
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--disable-dev-shm-usage", f"--user-data-dir={ud}",
         "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
         finalize_scj.file_uri(html_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 2000:
        raise SystemExit(f"PDF missing or too small: {pdf_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat(),
                    help="ISO date stamped into the filename and subtitle")
    args = ap.parse_args()
    html_body = build_html(args.date)
    os.makedirs(os.path.dirname(HTML_OUT), exist_ok=True)
    with open(HTML_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("<!doctype html><html lang='en'><head><meta charset='utf-8'></head><body>\n")
        f.write(html_body)
        f.write("\n</body></html>\n")
    pdf_name = f"Principles_Digest_categorised_{args.date}.pdf"
    pdf_path = os.path.join(BOOKLET, pdf_name)
    if os.path.exists(pdf_path):
        # dated snapshot is meant to be unique per day; overwrite same-day regen only
        pass
    render_pdf(HTML_OUT, pdf_path)
    print(f"wrote {HTML_OUT}")
    print(f"wrote {pdf_path} ({os.path.getsize(pdf_path)} bytes)")


if __name__ == "__main__":
    main()
