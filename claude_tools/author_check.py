#!/usr/bin/env python3
"""One-shot quality gate for a rich SCJ record — run BEFORE finalize.

Combines the base pipeline validation (tools/finalize_scj.check_record, after the
same coercion finalize applies) with the RICH-schema checks the handoff lists, so
the whole self-check is a single tool call. Every evidence quote is verified
VERBATIM (whitespace-normalized) against the UNtrimmed extract, so fidelity is to
the true source even when the model read the .lean.txt copy.

Usage: python3 claude_tools/author_check.py <CID>
Exit 0 iff every hard check passes (prints PASS/FAIL per check).
"""
from __future__ import annotations
import copy, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
JSON_DIR = os.path.join(ROOT, "supply-code", "summaries", "json")
EXTRACTS = os.path.join(ROOT, "supply-code", "extracts")

OUTCOMES = {"consumer", "licensee", "alternate_remedy", "pending", "none", "split"}
SIGS = {"significant", "ordinary", "procedural"}


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cid = sys.argv[1]
    rec_path = os.path.join(JSON_DIR, cid + ".json")
    if not os.path.exists(rec_path):
        sys.exit(f"FAILED · no record {rec_path}")
    fails = []

    def chk(cond, msg):
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    # 1. parses
    try:
        c = json.load(open(rec_path, encoding="utf-8"))
        chk(True, "json parses")
    except Exception as e:
        chk(False, f"json parses ({e})")
        sys.exit("FAILED · unparseable JSON")

    # 2. base gate: finalize's own coerce + check_record (catches missing/empty fields,
    #    page_count, significance/outcome vocab, cited_by str, lead_authorities shape)
    try:
        import finalize_scj as F
        cc = copy.deepcopy(c)
        F.coerce_record_shapes(cc)
        F.check_record(cc, cid)
        chk(True, "finalize.check_record (base fields, vocab, shapes)")
    except SystemExit as e:
        chk(False, f"finalize.check_record: {e}")
    except Exception as e:
        chk(False, f"finalize.check_record raised {type(e).__name__}: {e}")

    # 3. outcome present + valid (all new cases are SCJ-301+, so required)
    o = str(c.get("outcome", "")).strip().lower().replace(" ", "_").replace("-", "_")
    chk(bool(o) and o in OUTCOMES, f"outcome present & valid ({c.get('outcome')!r})")
    s = str(c.get("significance", "")).strip().lower()
    chk(s in SIGS, f"significance valid ({c.get('significance')!r})")

    # 4. no limiting_facts anywhere
    lf = []
    def walk(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "limiting_facts":
                    lf.append(p + "/" + k)
                walk(v, p + "/" + k)
        elif isinstance(o, list):
            for i, x in enumerate(o):
                walk(x, f"{p}[{i}]")
    walk(c)
    chk(not lf, f"no limiting_facts (found {lf})")

    # 5. every paras is a string
    bad_paras = []
    def paras(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "paras" and not isinstance(v, str):
                    bad_paras.append(p + "/" + k)
                paras(v, p + "/" + k)
        elif isinstance(o, list):
            for i, x in enumerate(o):
                paras(x, f"{p}[{i}]")
    paras(c)
    chk(not bad_paras, f"all paras are strings (bad {bad_paras})")

    # 6. holdings present; provision CODE::clause; nature vocab
    hus = c.get("holding_units") or []
    chk(len(hus) >= 1, f"has >=1 holding_unit ({len(hus)})")
    for i, h in enumerate(hus):
        chk(bool(re.match(r"^[^:\s][^:]*::.+", str(h.get("provision", "")))),
            f"HU{i} provision CODE::clause ({h.get('provision')!r})")
        nat = h.get("nature")
        chk(nat in ("ratio", "obiter"), f"HU{i} nature ratio|obiter ({nat!r})")

    # 7. evidence quotes verbatim (normalized) against the UNtrimmed extract
    ext_path = os.path.join(EXTRACTS, cid + ".txt")
    if not os.path.exists(ext_path):
        chk(False, f"extract present for quote check ({ext_path})")
    else:
        big = norm(open(ext_path, encoding="utf-8", errors="replace").read())
        n_ev = 0
        for i, h in enumerate(hus):
            ev = h.get("evidence") or []
            chk(len(ev) >= 1, f"HU{i} has >=1 evidence quote")
            for j, e in enumerate(ev):
                n_ev += 1
                q = norm(e.get("quote", ""))
                chk(bool(q) and q in big,
                    f"HU{i} ev{j} verbatim in source (\"{q[:45]}...\")")
        chk(n_ev >= 1, f"total evidence quotes checked ({n_ev})")

    # 8. related_cases well-formed
    for i, r in enumerate(c.get("related_cases") or []):
        chk(bool(re.match(r"^SCJ-\d+$", str(r.get("case_id", "")))),
            f"related_cases[{i}] case_id ({r.get('case_id')!r})")

    # 9. pin_basis vocab (soft-required)
    pb = c.get("pin_basis")
    chk(pb in ("page", "date", "paragraph", None), f"pin_basis vocab ({pb!r})")

    print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + str(len(fails))}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
