#!/usr/bin/env python3
"""
build_dataset.py — regenerate the search corpus from one source of truth.

Source of truth: data/orders.json  (one object per order; the Sonnet summariser writes it).
Generates, deterministically:
  data/orders.csv            flat facet table (Excel / quick faceting)
  data/orders-abstracts.md   readable bilingual digests + Supply Code detail
  state/cases.json           processed-cases ledger; dedup key = source-PDF sha256

Run from the ombudsman/ dir:  python pipeline/build_dataset.py
"""
import csv, json, hashlib, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORDERS = ROOT / "data" / "orders.json"

CSV_COLS = ["case_id","representation_no","order_date","ombudsman","discom","district",
"petitioner","petitioner_role","consumer_segment","tariff_category","sanctioned_load",
"connection_type","primary_subject","secondary_subjects","procedural_posture","decided_on",
"disposition","maintainability_holding","amount_in_dispute","act_sections","supply_code_clauses",
"regulations_cited","precedents_cited","key_provision_interpreted","relief_granted","ratio_short",
"tags","source_pdf","ocr_confidence"]


def j(v):
    """Join a list with '; ' for flat cells; pass strings through."""
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return "" if v is None else str(v)


def sha256(path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main():
    orders = json.loads(ORDERS.read_text(encoding="utf-8"))
    orders.sort(key=lambda o: o["case_id"])

    # 1) orders.csv
    with open(ROOT / "data" / "orders.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(CSV_COLS)
        for o in orders:
            w.writerow([j(o.get(c, "")) for c in CSV_COLS])

    # 2) orders-abstracts.md
    lines = ["# Order abstracts — UPERC Electricity Ombudsman",
             "",
             "*Generated from `data/orders.json` by `pipeline/build_dataset.py` — do not hand-edit.*",
             "Bilingual condensed summary + Supply Code detail per order. Source: OCR of scanned",
             "bilingual orders; `ocr_confidence` flags reliability. Search-grade, not citation-grade.",
             ""]
    for o in orders:
        sc = o.get("supply_code_detail") or []
        sc_md = "; ".join(f"**{d['clause']}** — {d['note']}" for d in sc) if sc else "— none cited"
        lines += [
            f"## {o['case_id']} — Representation {o.get('representation_no','')}",
            f"**{j(o.get('discom'))} · {j(o.get('district'))} · {j(o.get('order_date'))} · "
            f"OCR {j(o.get('ocr_confidence'))}**",
            "",
            f"- **Consumer:** {j(o.get('petitioner'))} — {j(o.get('consumer_segment'))}, "
            f"{j(o.get('tariff_category'))}, {j(o.get('sanctioned_load'))}, {j(o.get('connection_type'))}",
            f"- **Summary:** {j(o.get('summary_en'))}",
            f"- **सारांश:** {j(o.get('summary_hi'))}",
            f"- **Supply Code, 2005:** {sc_md}",
            f"- **Also cited:** EA 2003 §{j(o.get('act_sections')) or '—'} · Regs "
            f"{j(o.get('regulations_cited')) or '—'} · Precedent {j(o.get('precedents_cited')) or '—'}",
            f"- **Decided on:** {j(o.get('decided_on'))} → **{j(o.get('disposition'))}**",
            f"- **Ratio:** {j(o.get('ratio_short'))}",
            f"- **Tags:** {j(o.get('tags'))}",
            "",
        ]
    (ROOT / "data" / "orders-abstracts.md").write_text("\n".join(lines), encoding="utf-8")

    # 3) state/cases.json  (dedup ledger)
    seqs = [int(o["case_id"].split("-")[1]) for o in orders]
    ledger = {"forum": "ombudsman", "prefix": "OMB",
              "next_seq": (max(seqs) + 1) if seqs else 1,
              "note": "Processed-cases DB. Dedup key = source-PDF sha256; never rework a processed case.",
              "cases": []}
    for o in orders:
        pdf = ROOT / "processed" / f"{o['case_id']}.pdf"
        ledger["cases"].append({
            "case_id": o["case_id"],
            "representation_no": o.get("representation_no", ""),
            "order_date": o.get("order_date", ""),
            "primary_subject": o.get("primary_subject", ""),
            "decided_on": o.get("decided_on", ""),
            "disposition": o.get("disposition", ""),
            "source_pdf": f"processed/{o['case_id']}.pdf",
            "sha256": sha256(pdf) if pdf.exists() else "",
            "ocr_confidence": o.get("ocr_confidence", ""),
            "status": "done",
        })
    (ROOT / "state" / "cases.json").write_text(
        json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"built: {len(orders)} orders -> orders.csv, orders-abstracts.md, state/cases.json "
          f"(next_seq={ledger['next_seq']})")


if __name__ == "__main__":
    if not ORDERS.exists():
        sys.exit(f"missing {ORDERS}")
    main()
