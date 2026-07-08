# Process-improvement backlog

Ideas agreed with the user. **①②④⑤⑥ + coverage-driven selection pivot are DONE.**
**③⑦⑧ remain scheduled** — do not drop them.

## Done
- **① Pre-clean queue text** — `clean_queue.py` strips IK page-header/footer artifacts
  and rejoins hyphenated line-breaks; wired into `fetch_batch.py` so new fetches are
  born clean. Eliminated the main cause of verify re-cycles. (Extended to dashed page
  numbers, SC docket headers `C.A.@S.L.P(c) No.../<page>`, and footnote-definition lines.)
- **② Authority docids / canonicalisation** — `authority_registry.json` + `canonical()`
  in `build_aggregation.py` merge name variants (Seetaram was split 8×+5× → one 14×
  entry) and link authorities to records by docid.
- **④ Gate upstream + coverage tracker** — `gate_manifest.py` audits every active
  manifest case for ≥1 target Electricity-Act provision (zero-network, via prefill +
  record); `coverage.py` emits `coverage_report.md` (the gap-driven selection worklist).
- **⑤ Snowball selection** — surfaced in `select_next.py` §3: un-recorded high-in-degree
  authorities become candidates (drove the SC wave: Seetaram/Orion Metal).
- **⑥ Composite leading-case picker** — `build_aggregation.py` ranks leading case by
  `court-rank + in-corpus in-degree + issue-novelty` (not court rank alone) and reports
  `apex_case` (highest court) alongside, so binding hierarchy is preserved.
- **Coverage-driven selection pivot (de-dup)** — `select_next.py` classifies each
  issue-node MISSING/OPEN/THIN/DEVELOPING/SATURATED and flips selection from citation-
  rank to gap-driven, with a de-dup guard (stop feeding saturated nodes) + concentration
  warnings.

## Scheduled (do later)
- **③ Schema linter + bare-Act-recital check.** New `lint_record.py`: (a) enforce
  `issue_node ∈ taxonomy`, `treatment ∈ enum`, `holding_type ∈ enum`, required fields
  present, `provision_version` set; (b) flag any `key_para` that falls inside a
  reproduced-statute block (schema forbids quoting the bare Act instead of the court's
  reasoning). Run alongside `verify_record.py` before every commit.
- **⑦ External-authority ghost nodes in the map.** Render un-recorded high-in-degree
  authorities (e.g. Seetaram) as first-class "not-yet-recorded" nodes in
  `build_treatise.py`, so the jurisprudence map doubles as the worklist.
- **⑧ Version-aware "current law" view.** In `build_treatise.py` / `provision_index`,
  separate the current-text (post-2007) leading holding per provision from
  superseded-text (pre-2007 / pre-2003) holdings, so no one cites the old §126
  multiplier or presumption period as if current.
