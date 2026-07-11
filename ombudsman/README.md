# `ombudsman/` — UPERC Electricity Ombudsman jurisprudence

A **research/search corpus** of Electricity Ombudsman (U.P.) orders, coded into a flat facet
table so patterns can be measured across cases. A forum in this repo's collection, sibling to
`high-court/` — but deliberately **lighter**: no rich digest / verify / render pipeline, because
the goal is retrieval over short orders on a token budget.

## Status
**Phase 1 — 10 orders coded, archived, and in the database.** Schema is a v0.1 proposal awaiting
your sign-off before batch-scaling. Same adjudicator (Sanjay Srivastava) across all 10.

## Start here
1. **[`STRATEGY.md`](STRATEGY.md)** — the (v0.2) plan, the token-cheap design, and the pattern
   that flipped at n=10. Read first.
2. **[`schema/facets.md`](schema/facets.md)** — the facet columns + controlled vocabularies. **Needs your sign-off.**
3. **[`data/orders.csv`](data/orders.csv)** — 10 orders coded (open in Excel; this is the search index).
4. **[`data/orders-abstracts.md`](data/orders-abstracts.md)** — bilingual headnote + ratio per order.
5. **[`state/cases.json`](state/cases.json)** — the processed-cases database (dedup by PDF hash).

## The headline finding (and why it matters)
At **n=5** it looked like "the Ombudsman dismisses 4 of 5 at the threshold." At **n=10 that flipped
to 6 relief / 4 threshold** — the first five were an unrepresentative run. The lesson: don't trust a
pattern volume hasn't stress-tested. A real merits doctrine also surfaced — **metering-assessment on
periodic-check failure** (Supply Code cl. 5.5(b)) → assessment corrected + interest-free installments
(OMB-007, OMB-008).

## Layout
```
ombudsman/
├── README.md · STRATEGY.md
├── schema/facets.md          # the flat-table schema (ratify before scaling)
├── data/
│   ├── orders.json           # source of truth: facets + bilingual summaries + Supply Code
│   ├── orders.csv            # generated flat search index
│   └── orders-abstracts.md   # generated bilingual summaries + Supply Code detail
├── state/cases.json          # processed-cases DB; dedup key = source-PDF sha256; next_seq
├── processed/                # the archive: OMB-XXX.pdf (source) + OMB-XXX.txt (OCR, hin+eng)
├── report/ombudsman-analytics.html   # at-a-glance analytics view (n=10)
└── pipeline/                 # ocr_extract.py (PDF->text, tesseract hin+eng) · build_dataset.py (json->csv/md/ledger)
```

## Processing a new order (token-cheap flow)
```bash
# 0. DEDUP: hash first; skip if the sha256 is already in state/cases.json
sha256sum new_order.pdf
# 1. OCR (local, free) — bilingual
python pipeline/ocr_extract.py new_order.pdf -o processed/OMB-011.txt
# 2. A Sonnet sub-agent reads the FULL .txt -> one record appended to data/orders.json
#    (facets + condensed bilingual summary + EVERY Supply Code clause). Opus only orchestrates.
# 3. python pipeline/build_dataset.py   # regenerates orders.csv, orders-abstracts.md, state/cases.json
# 4. git add processed/OMB-011.* data/ state/ && commit
```

## Provenance
Source PDFs are scanned bilingual (Hindi/English) images; text recovered by OCR, so every row
carries an `ocr_confidence` flag and some rupee amounts are marked approximate. Search-grade, not
citation-grade, until a row is human-checked.
