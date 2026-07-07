# Redesign: from per-case digests to a jurisprudence database

## The problem with the current schema

The existing extract/summary JSON (`high-court/extracts/HC-001.extract.json`) is a
beautiful **case-centric digest** — issues, facts, reasoning, ratio, obiter,
significance, authorities — built to render one standalone PDF. That is the right
shape for *reading a case* and the wrong shape for *building comprehensive
jurisprudence across 150 cases*, because:

- It stores prose keyed to the case, not **atomic propositions keyed to a
  statutory provision or a legal issue**. You can't ask "what has every court
  said about mens rea under §135?" without re-reading all 150 digests.
- Provisions, issues, and cited cases are free-text (`"Section&nbsp;135..."`),
  not normalized IDs, so nothing joins across cases.
- It carries a lot the jurisprudence doesn't need (multi-paragraph facts,
  disposition boilerplate, HTML entities, styling).

You said it: *"for a digest we don't need everything from a json."* Correct — for
jurisprudence we need **less prose and more structure**, and every load-bearing
field must link to a normalized key so cases aggregate.

## What to extract from each case (the three things you named)

A lean, **atomic and normalized** per-case record. Everything either links to a
provision/issue node or is a single load-bearing proposition with a verbatim
anchor quote (for the verify gate). Draft schema:

```jsonc
{
  "case_id": "SC-007",
  "docid": "55216283",                 // Indian Kanoon id — the join key
  "title": "...", "neutral_cite": "(2013) 8 SCC 491",
  "court": "Supreme Court", "court_rank": "SC",   // SC | HC-DB | HC-SB
  "date": "2013-07-01", "bench": ["Singhvi J", "Mukhopadhaya J"], "bench_strength": 2,
  "still_good_law": true,              // flipped if later overruled (set in aggregation)
  "one_line": "Consumer fora have no jurisdiction over s.126/s.135; remedy is s.127 appeal.",

  // (1) INTERPRETATION OF THE ELECTRICITY ACT — one row per provision, aggregatable
  "provision_holdings": [
    {
      "provision": "s.126",                    // normalized id
      "issue_node": "126v135",                 // links to the taxonomy (10 nodes + s.56)
      "holding": "s.126 is a civil assessment; no mens rea required.",
      "interpretation_type": "distinguished-from-135",  // defined-term | read-down | expanded | procedure | limitation | ...
      "key_para": "\"...unauthorised use ... even in the absence of intention.\"",  // verbatim
      "para_ref": "para 29"
    }
  ],

  // (2) CASE LAW CITED — each with the principle it is cited FOR + how it was treated
  "authorities": [
    {
      "name": "Seetaram Rice Mill", "cite": "(2012) 2 SCC 108", "docid": "43074463",
      "principle": "s.126 (civil, no intent) vs s.135 (criminal, mens rea) distinction",
      "treatment": "followed",                 // followed | distinguished | overruled | doubted | explained | referred
      "on_issue": "126v135"
    }
  ],

  // (3) WHAT THIS CASE DECIDED — ratio + significance, per issue, aggregatable
  "ratio": [
    {
      "issue_node": "jurisdiction-145-154",
      "proposition": "A s.126 assessment is not a 'consumer dispute'; consumer fora are barred.",
      "scope": "SC-binding",
      "novelty": "new",                        // new | affirms | extends | distinguishes | conflicts
      "conflicts_with": []                     // docids/names if it diverges from a prior line
    }
  ],
  "significance": "Leading authority routing all s.126/s.135 challenges to s.127, not consumer fora.",
  "flags": ["leading-on-jurisdiction", "overrules-none"]
}
```

**Dropped vs the current digest** (not needed for jurisprudence): multi-paragraph
`facts` (kept as the one-line squib), `headnote`, `disposition`/`result`
boilerplate, `obiter` prose (fold genuinely-important obiter into `ratio` with
`scope: "obiter"`), HTML entities and rendering fields.
**Kept but normalized:** provisions → `provision` ids, issues → `issue_node` ids,
authorities → `{docid, principle, treatment}` rows.

## The layer that produces the jurisprudence (aggregation)

Per-case records are the input; the **comprehensive jurisprudence is a second
pass** that pivots them (pure code, no model):

- **`provision_index.json`** — for each provision (s.126, s.135, s.127, s.145/154,
  s.152, s.56(2)): every holding across all cases, in date order, showing how the
  interpretation evolved, where courts split, and the current settled position.
- **`issue_matrix.json`** — for each of the 11 taxonomy nodes: the leading case +
  the full line of authority + any conflicts.
- **`citation_graph.json`** — authority edges (who followed/distinguished/overruled
  whom), which also powers the in-set in-degree anchor method from Stage 2 and
  auto-sets `still_good_law`.

This is the deliverable: a queryable doctrine map, from which a written treatise
(or the per-case PDFs, still renderable from the same records) falls out.

## Which model, and why (tiered)

Extraction splits into a **mechanical** part and a **judgment** part; use a
different model for each rather than one model for everything.

| Pass | Work | Model | Why |
|---|---|---|---|
| A. Mechanical | metadata, bench, list of authorities + their cite/docid, verbatim quote pulls | **Haiku 4.5** ($1/$5) | Cheap, deterministic, verify-gated; no legal judgment needed |
| B. Judgment | `interpretation_type`, ratio vs obiter, `treatment` of each authority, `novelty`/`conflicts`, `significance`, issue-tagging | **Sonnet 5** ($3/$15; $2/$10 intro to 2026-08-31) as the workhorse; **Opus 4.8** ($5/$25) for the ~30 SC landmarks | Characterising a principle, ratio/obiter, and doctrinal conflict is exactly where cheap models fail and errors propagate into the aggregation |
| C. Aggregation/synthesis | build the provision index / issue matrix / citation graph; write the treatise sections | **Opus 4.8** | One-time, whole-corpus reasoning where getting the doctrine right matters most |

Keep the existing **`verify.py` gate + grep-confirm of every `key_para`** on all
passes regardless of model — that is what lets Haiku do Pass A safely.

Rationale: running Opus on 150 full judgments end-to-end is unnecessary for the
mechanical fields and costly; running Haiku on the judgment fields is unsafe.
Tiering (Haiku extract → Sonnet 5 synthesise → Opus landmarks + final treatise)
optimises cost-for-quality and covers **all expert-cited cases + the ~100 picked**
comfortably. All three models have a 1M context window (Haiku 200K), so even long
judgments fit in one pass. Ballpark: ~150 cases × mostly Sonnet 5 with Opus on the
SC tail is a modest spend for a citable scholarly work; a Batch API run (50% off,
non-urgent) lowers it further.

## What changes operationally
- Replace the single extract schema with the record above; keep `render2.js` able
  to render a PDF from it (the jurisprudence view is the new primary artifact, the
  PDF a secondary view).
- Extraction becomes two model calls per case (Haiku then Sonnet 5/Opus), still
  behind the verify gate.
- Add the aggregation pass as new tooling (`build_provision_index.py`,
  `build_issue_matrix.py`, `build_citation_graph.py`).

**Not started — for your sign-off.** Open choices: (a) Sonnet 5 vs Opus 4.8 as the
Pass-B workhorse (I recommend Sonnet 5, Opus for SC only); (b) keep rendering
per-case PDFs, or go database-only; (c) one merged schema for HC and SC, or keep
the mirrored dirs.
