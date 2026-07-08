# Process-improvement backlog

Ideas agreed with the user. **①④⑥ are DONE** (this commit). **②③⑤⑦⑧ are scheduled
for later** — do not drop them.

## Done
- **① Pre-clean queue text** — `clean_queue.py` strips IK page-header/footer artifacts
  and rejoins hyphenated line-breaks; wired into `fetch_batch.py` so new fetches are
  born clean. Eliminated the main cause of verify re-cycles.
- **④ Gate upstream + coverage tracker** — `gate_manifest.py` audits every active
  manifest case for ≥1 target Electricity-Act provision (zero-network, via prefill +
  record); `coverage.py` emits `coverage_report.md` (the gap-driven selection worklist).
- **⑥ Composite leading-case picker** — `build_aggregation.py` ranks leading case by
  `court-rank + in-corpus in-degree + issue-novelty` (not court rank alone) and reports
  `apex_case` (highest court) alongside, so binding hierarchy is preserved.

## Scheduled (do later)
- **② Wire authority docids from free IK `cites` metadata.** In `prefill_from_ik.py` /
  `fetch_batch.py`, name-match each `authorities[].name` to the IK `cites` block and
  attach its `docid`. Makes the citation graph link in-corpus edges instead of relying
  on fuzzy title match. Zero extra tokens (cites already fetched).
- **③ Schema linter + bare-Act-recital check.** New `lint_record.py`: (a) enforce
  `issue_node ∈ taxonomy`, `treatment ∈ enum`, `holding_type ∈ enum`, required fields
  present, `provision_version` set; (b) flag any `key_para` that falls inside a
  reproduced-statute block (schema forbids quoting the bare Act instead of the court's
  reasoning). Run alongside `verify_record.py` before every commit.
- **⑤ Authority-driven (snowball) selection.** Use `citation_graph.json` +
  `coverage.py` §6 to propose next candidates from the `citedby`/`cites` of the
  highest-in-degree authorities (e.g. Seetaram Rice Mill), not just keyword search.
  Feed proposals through `gate_cites.py` before adding to the manifest.
- **⑦ External-authority ghost nodes in the map.** Render un-recorded high-in-degree
  authorities (e.g. Seetaram) as first-class "not-yet-recorded" nodes in
  `build_treatise.py`, so the jurisprudence map doubles as the worklist.
- **⑧ Version-aware "current law" view.** In `build_treatise.py` / `provision_index`,
  separate the current-text (post-2007) leading holding per provision from
  superseded-text (pre-2007 / pre-2003) holdings, so no one cites the old §126
  multiplier or presumption period as if current.
