# `ombudsman/` — UPERC Electricity Ombudsman jurisprudence

A new **forum** in this repo's judgment-digest pipeline, sitting one rung below `high-court/`
on the same ladder and interpreting the same statute (Electricity Act 2003 + U.P. Supply Code
2005 + UPERC regulations). Goal: turn Electricity Ombudsman (U.P.) orders into structured,
queryable jurisprudence.

## Status
**Phase 0 — strategy + proof of concept.** First **5** orders read and coded. Schema is a
**v0.1 proposal awaiting sign-off** before scaling. Nothing here is wired into the automated
Routine yet.

## Start here
1. **[`STRATEGY.md`](STRATEGY.md)** — the plan, the pattern that already emerged, and the open
   questions. Read this first.
2. **[`schema/facets.md`](schema/facets.md)** — the "excel sheet" columns + controlled
   vocabularies. **This is what needs your ratification.**
3. **[`data/orders.csv`](data/orders.csv)** — the 5 orders coded into that schema (open in Excel).
4. **[`data/orders-abstracts.md`](data/orders-abstracts.md)** — readable headnote per order.

## The idea in one picture
- **Layer 1 (deep):** one rich digest per order — reuse the golden `HC-001.extract.json` schema.
- **Layer 2 (wide):** one flat row per order in `orders.csv` — controlled vocab, for `GROUP BY`.
- **Graph:** an authorities ledger (reuse the HC pattern) linking provisions, precedents, and
  prior CGRF/HC orders across forums.

## The headline finding (n=5)
**4 of 5 orders were decided on a threshold question** — jurisdiction, maintainability,
no-power-of-review, or withdrawal — not on the electricity merits. The U.P. Ombudsman is, in
this sample, primarily a **jurisdictional gatekeeper**. Track "% disposed on threshold vs merits"
as the project's headline metric.

## Layout
```
ombudsman/
├── README.md                 # you are here
├── STRATEGY.md               # the plan + reasoning + open questions
├── schema/facets.md          # the flat-table schema (ratify before scaling)
├── data/
│   ├── orders.csv            # 5 orders coded (the "excel sheet")
│   └── orders-abstracts.md   # readable per-order headnotes
└── pipeline/
    ├── ocr_extract.py        # scanned bilingual PDF -> text (PyMuPDF + tesseract hin+eng)
    └── requirements.txt
```

## Processing a new order (once the schema is frozen)
```bash
# 1. OCR the scanned order to text
python pipeline/ocr_extract.py path/to/OrderAppealNoXX2026.pdf -o extracts/OMB-006.txt
# 2. (Phase 2) feed extracts/OMB-006.txt to the digest sub-agent -> OMB-006.extract.json
# 3. (Phase 2) verify.py gate -> render digest -> add a row to data/orders.csv
```

## Provenance note
Source PDFs are scanned bilingual (Hindi/English) images; text is recovered by OCR, so cells
carry an `ocr_confidence` flag. The Hindi-majority orders (OMB-001, OMB-003) are lower-confidence
and should be human-checked before they are relied on.
