# Case Selection — Electricity Act §126/§135 Jurisprudence

Goal: from Indian Kanoon, pick the **landmark** Supreme Court and High Court
judgments on **§126 (assessment / unauthorised use of electricity)** and
**§135 (theft of electricity)** of the Electricity Act, 2003, together with the
closely-entangled neighbours **§127 (appeal / pre-deposit), §145 & §154
(civil-court bar / Special Courts), and §152 (compounding)**.

Target (agreed): **quality-first, ~30 SC + ~50 HC (~80 total)**; primary
selection axis = **distinct legal proposition** (one leading case per issue),
tie-broken by citation impact and court diversity.

## Method (three stages)

**Stage 1 — metadata harvest (this folder, DONE).** A battery of targeted IK
searches (`harvest.py`), unioned by doc-id. We keep only the *free* metadata
every search result already carries — title, court, date, `numcites`,
`numcitedby`, headline snippet. **Zero full judgments are read.** Each case is
tagged with which query/issue matched it, giving a free per-case issue
fingerprint for clustering.

**Stage 2 — cluster & select (next).** On the harvested sheet only:
- bin candidates into the issue-taxonomy from their fingerprints;
- score = normalised `numcitedby` + topical-relevance + doctrinal-lineage
  (cites/cited-by an anchor) + currency − duplicate-proposition penalty −
  already-processed exclusion;
- **anchors are derived, not hand-picked** — a coverage-balanced set spanning
  every issue (Idea 1), seeded one-per-issue (Idea 3), validated by in-set
  citation in-degree (Idea 2). This avoids skew toward a single anchor;
- hard rules: every issue ≥1 case; per-HC cap; exclude the 50 DC + 5 HC already
  digested (Torrent Power = HC-002 is already in the corpus).

**Stage 3 — full-text digests.** Only the final ~80 approved cases are fetched
and run through the existing `tools/` digest pipeline.

## Files
| file | what |
|---|---|
| `harvest.py` | Stage-1 harvester (re-runnable; caches pages in `raw/`) |
| `candidates.json` | unioned candidate records (full fields) |
| `candidates.csv` | flattened sheet for human review |
| `raw/` | cached raw API pages (so re-runs cost nothing) |

## Stage-1 result
- **1,193 unique candidates** — SC **172**, HC **1,021** — deduplicated by doc-id.
- Topicality flag (electricity-domain terms in title/headline) separates the
  genuine set from generic-section noise: SC **48/172** topical, HC **853/1021**.
  (The §145/§154 SC query alone pulled 559 generic-jurisdiction hits — flagged,
  not deleted, so nothing is silently lost.)
- All 9 issue-taxonomy nodes are well populated (100–318 candidates each).
- HC court spread is broad (Allahabad, Kerala, Gujarat, Madras, Punjab-Haryana,
  Bombay, Delhi, Calcutta, MP, Jharkhand, Andhra, Rajasthan, …).
- Cost: 175 API pages (~₹87).

### Issue taxonomy (fingerprint tags)
`126v135` · `assessment-126` · `mensrea-135` · `appeal-127` ·
`jurisdiction-145-154` · `compounding-152` · `natural-justice` ·
`provisional-final` · `burden-proof`

## Reproduce
```
IK_API_TOKEN=<token> python3 harvest.py     # uses cached raw/ pages if present
```
