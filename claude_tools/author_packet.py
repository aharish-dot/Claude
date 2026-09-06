#!/usr/bin/env python3
"""Deterministic author-packet precompute for the Claude SCJ pipeline (Phase 1).

Writes supply-code/extracts/<cid>.packet.md — everything the Opus author needs
that is MECHANICAL to derive, so the author never spends context/tool-calls
grepping the spine, re-deriving meta, or hunting provision keys. It NEVER
authors holdings, evidence, ratio/obiter, headnote or facts — those stay 100%
the model's job, so quality is unchanged. The packet only supplies:

  * META parsed from the judgment header (title/court/case-no/counsel/coram)
    — the fingerprint frequently leaves these blank.
  * PIN-BASIS hint from the extract's structure (numbered paras vs page breaks vs
    order-sheet dates) — a HINT the author confirms, never invents page numbers.
  * PROVISION CODE CATALOG — the existing CODE::clause keys from the spine
    (clean numeric clauses only), so the author reuses keys and never invents a CODE.
  * SPINE SIBLING CANDIDATES — for clause tokens actually seen in THIS extract,
    the prior cases on that provision (ready-made related_cases candidates to curate).
  * AUTHORITIES / TOKENS detected — from the fingerprint + a light scan.

Reads only: <cid>.txt, <cid>.fp.json, supply-code/jurisprudence/index.json.
Pure Python, zero LLM. Target packet size: a few KB (must stay well under the
lean extract, or it is not saving anything).

Usage: python3 claude_tools/author_packet.py <CID>
"""
from __future__ import annotations
import json, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTS = os.path.join(ROOT, "supply-code", "extracts")
SPINE = os.path.join(ROOT, "supply-code", "jurisprudence", "index.json")

SIB_CAP = 6            # sibling candidates listed per provision
TITLE_MAX = 44         # sibling title truncation
CAT_CAP = 40           # clean clauses listed per CODE in the catalog
MAIN_CODES = ["UP-2005", "UP-2002", "EA2003", "EA1999(UP)", "ESA1948",
              "IEA1910", "UPGEU1958", "IBC", "CPC"]

# a "clean" clause key: short, numeric-ish, optional letter/paren suffix — NOT prose
CLEAN_CLAUSE = re.compile(r"\d{1,2}(?:\.\d{1,3}[A-Za-z]?){0,2}(?:\([a-z0-9]+\))?$")
CLAUSE_RE = re.compile(r"\b\d{1,2}\.\d{1,3}(?:\([a-z0-9]+\))?\b")
DATE_RE = re.compile(r"\b\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4}\b")
SECTION_RE = re.compile(r"\bSection\s+(\d{1,3}[A-Z]?)\b")
CTX_RE = re.compile(r"(?:clause|cl\.|para(?:graph)?|regulation|reg\.|rule)\s*$", re.I)


def load_json(p, default=None):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def is_clean_clause(c: str) -> bool:
    return bool(c) and bool(CLEAN_CLAUSE.fullmatch(c.strip()))


def clause_sort_key(c: str):
    m = re.match(r"(\d+)(?:\.(\d+))?", c)
    return (int(m.group(1)), int(m.group(2) or 0), c) if m else (999, 999, c)


def parse_meta(txt: str, fp: dict) -> dict:
    head = txt[:1500]

    def grab(label):
        m = re.search(rf"{label}\s*:-?\s*(.+)", head)
        return m.group(1).strip() if m else ""

    petitioner = grab(r"Petitioner")
    respondent = grab(r"Respondent")
    court_no = grab(r"Court No\.")
    case_no = grab(r"Case")
    coram = ""
    m = re.search(r"Hon'?ble[^\n]{0,80}?J\b\.?", txt[:4000])
    if m:
        coram = m.group(0).strip()
    title = f"{petitioner} v. {respondent}".strip(" v.") if (petitioner or respondent) else ""
    return {
        "title": title or (fp.get("cause_title") or ""),
        "petitioner": petitioner, "respondent": respondent,
        "court_no": court_no, "case_no": case_no,
        "counsel_pet": grab(r"Counsel for Petitioner"),
        "counsel_resp": grab(r"Counsel for Respondent"),
        "coram": coram or (fp.get("coram") or ""),
        "court": fp.get("court") or "High Court of Judicature at Allahabad",
    }


def detect_pins(txt: str, fp: dict) -> dict:
    lines = txt.split("\n")
    numbered = sum(1 for ln in lines if re.match(r"\s*\d{1,3}\.\s", ln))
    formfeeds = txt.count("\x0c")
    standalone_num = sum(1 for ln in lines if re.match(r"\s*\d{1,3}\s*$", ln))
    order_hits = len(re.findall(r"\border\s+dated\b|\border-?sheet\b", txt, re.I))
    dates = len(DATE_RE.findall(txt))
    if numbered >= 4:
        basis, why = "paragraph", f"{numbered} numbered-paragraph lines → pins render '¶ N'"
    elif formfeeds >= 1 or standalone_num >= 3:
        basis, why = "page", f"{formfeeds} page breaks / {standalone_num} page-number lines → pins 'p. N'"
    elif order_hits >= 2 or (dates >= 6 and numbered == 0):
        basis, why = "date", "order-sheet pattern (dated entries, no numbered paras) → pins 'order of DD.MM.YYYY'"
    else:
        basis, why = "paragraph?", "no clear numbered paras / page markers — AUTHOR DECIDES from the source; never invent page numbers"
    return {"pin_basis": basis, "why": why, "numbered": numbered,
            "formfeeds": formfeeds, "standalone_num": standalone_num,
            "order_hits": order_hits, "dates": dates}


def detect_clause_tokens(txt: str) -> Counter:
    """Clause tokens seen, with dates excluded and weak matches context-gated."""
    date_spans = [m.span() for m in DATE_RE.finditer(txt)]

    def in_date(a, b):
        return any(not (b <= s or a >= e) for s, e in date_spans)

    seen = Counter()
    for m in CLAUSE_RE.finditer(txt):
        a, b = m.span()
        tok = m.group(0)
        if in_date(a, b):
            continue
        # a bare D.M immediately followed by .YYYY is a date fragment
        if re.match(r"[.\-/]\d{2,4}", txt[b:b + 5]):
            continue
        has_paren = "(" in tok
        three_part = tok.count(".") >= 2
        ctx = bool(CTX_RE.search(txt[max(0, a - 12):a]))
        # keep strong signals; a bare D.M needs context or paren/3-part to count
        if has_paren or three_part or ctx or _known_clause(tok):
            seen[tok] += 1
    return seen


_SPINE_CLAUSES: set[str] = set()


def _known_clause(tok: str) -> bool:
    return tok in _SPINE_CLAUSES


def load_spine_clause_index(prov: dict):
    """clean-clause token -> [provision keys]; also fill _SPINE_CLAUSES."""
    idx = defaultdict(list)
    for key, e in prov.items():
        clause = (e.get("clause") if isinstance(e, dict) else "") or ""
        tail = key.split("::")[-1]
        for frag in {clause.strip(), tail.strip()}:
            base = re.match(r"\d{1,2}\.\d{1,3}(?:\([a-z0-9]+\))?", frag or "")
            if base:
                b = base.group(0)
                idx[b].append(key)
                _SPINE_CLAUSES.add(b)
    return idx


def provision_catalog(prov: dict) -> str:
    by_code = defaultdict(set)
    for key, e in prov.items():
        code = (e.get("code") if isinstance(e, dict) else "") or key.split("::")[0]
        clause = (e.get("clause") if isinstance(e, dict) else "") or ""
        tail = key.split("::")[-1]
        cand = clause.strip() if is_clean_clause(clause.strip()) else (
            tail.strip() if is_clean_clause(tail.strip()) else "")
        if cand and len(code) <= 14:            # skip prose "codes"
            by_code[code].add(cand)
    lines = ["- canonical prefixes: UP-2005=Supply Code 2005 · EA2003=Electricity Act 2003 · "
             "UP-2002=Supply Code 2002 · EA1999(UP)=Reforms Act 1999 · ESA1948 · IEA1910 · "
             "UPGEU1958 · IBC · CPC · OFFTOPIC::slug only if truly outside supply law"]
    for code in sorted(by_code, key=lambda c: (c not in MAIN_CODES, c)):
        cl = sorted(by_code[code], key=clause_sort_key)[:CAT_CAP]
        if cl:
            lines.append(f"- **{code}**: " + " · ".join(cl))
    return "\n".join(lines)


def sibling_candidates(prov: dict, clause_index: dict, tokens: Counter) -> str:
    out, seen_keys = [], set()
    for tok, _ in tokens.most_common():
        for key in clause_index.get(tok, []):
            if key in seen_keys:
                continue
            seen_keys.add(key)
            e = prov[key]
            cases = e.get("cases", []) if isinstance(e, dict) else []
            sibs = "; ".join(f"{c.get('case_id')} {(c.get('title') or '')[:TITLE_MAX]}"
                             for c in cases[:SIB_CAP])
            topic = ((e.get("topic") if isinstance(e, dict) else "") or "")[:70]
            out.append(f"- **{tok}** → `{key}` ({topic}): {sibs or '(no prior siblings)'}")
    if not out:
        return "- (no clause tokens matched existing spine provisions — author computes related_cases directly)"
    return "\n".join(out[:16])


def authorities_block(fp: dict, txt: str) -> str:
    lines = []
    for c in (fp.get("citations") or [])[:16]:
        lines.append(f"- {c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)[:130]}")
    for s in (fp.get("text_citation_samples") or [])[:10]:
        lines.append(f"- (text) {str(s)[:130]}")
    secs = fp.get("sections_cited") or []
    if secs:
        lines.append(f"- sections_cited (fp): {', '.join(map(str, secs[:30]))}")
    vs, uniq = re.findall(r"[A-Z][A-Za-z.&' ]{3,38}\sv\.\s[A-Z][A-Za-z.&' ]{3,38}", txt), []
    for v in vs:
        v = re.sub(r"\s+", " ", v).strip()
        if v not in uniq:
            uniq.append(v)
    if uniq:
        lines.append("- 'v.' name-scan (verify; excludes the parties themselves): "
                     + " | ".join(uniq[:10]))
    return "\n".join(lines) if lines else "- (fingerprint carried no citations — derive authorities from the extract)"


def build(cid: str) -> str:
    txt_p = os.path.join(EXTRACTS, cid + ".txt")
    if not os.path.exists(txt_p):
        sys.exit(f"FAILED · no extract {txt_p} (run claim + lean_extract first)")
    txt = open(txt_p, encoding="utf-8", errors="replace").read()
    fp = load_json(os.path.join(EXTRACTS, cid + ".fp.json"), {}) or {}
    prov = (load_json(SPINE, {}) or {}).get("provisions", {}) or {}

    clause_index = load_spine_clause_index(prov)   # also fills _SPINE_CLAUSES
    meta = parse_meta(txt, fp)
    pins = detect_pins(txt, fp)
    clause_tokens = detect_clause_tokens(txt)
    sections = Counter(m.group(1) for m in SECTION_RE.finditer(txt))

    clause_summary = " · ".join(f"{c}(×{n})" for c, n in clause_tokens.most_common(16)) or "(none)"
    section_summary = " · ".join(f"§{s}(×{n})" for s, n in sections.most_common(16)) or "(none)"

    md = f"""# AUTHOR PACKET · {cid}   (deterministic precompute — curate, do NOT trust blindly)

> Mechanical scaffolding only. You still author every headnote, fact, holding,
> evidence quote (VERBATIM, grep-verified against {cid}.txt), ratio/obiter and
> reusable_construction yourself. Nothing here lowers the quality bar; it spares
> you the spine greps and meta re-derivation.

## META  (parsed from the header; confirm against the source)
- **title**: {meta['title'] or '(parse failed — read header)'}
- court: {meta['court']}   {meta['case_no']}   (Court No. {meta['court_no']})
- coram: {meta['coram'] or '(not auto-detected — read the delivered-by line)'}
- counsel: pet = {meta['counsel_pet']}  |  resp = {meta['counsel_resp']}
- page_count(fp): {fp.get('page_count')}   para_count(fp): {fp.get('para_count')}   words(fp): {fp.get('word_count')}

## PIN BASIS  → **{pins['pin_basis']}**
{pins['why']}
(signals: numbered-para={pins['numbered']} · page-breaks={pins['formfeeds']} · standalone-num={pins['standalone_num']} · order-hits={pins['order_hits']} · date-tokens={pins['dates']}) — NEVER invent reporter page numbers not in the source.

## PROVISION CODE CATALOG  (reuse these EXACT keys; never invent a CODE)
{provision_catalog(prov)}

## SPINE SIBLING CANDIDATES  (clause tokens in THIS extract → prior cases; curate genuine related_cases)
{sibling_candidates(prov, clause_index, clause_tokens)}

## CLAUSE / SECTION TOKENS SEEN  (raw — for holding_units.provision keys)
- clauses: {clause_summary}
- sections: {section_summary}

## AUTHORITIES DETECTED  (fill docids + treatment; verify — do not treat parties as authorities)
{authorities_block(fp, txt)}
"""
    return md


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cid = sys.argv[1]
    md = build(cid)
    dst = os.path.join(EXTRACTS, cid + ".packet.md")
    open(dst, "w", encoding="utf-8").write(md)
    print(f"packet {cid}: {len(md)} chars -> {dst}")


if __name__ == "__main__":
    main()
