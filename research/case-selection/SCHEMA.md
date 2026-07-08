# Jurisprudence record schema — v1.0 (LOCKED)

One JSON record per case (`<ID>.record.json`), merged HC/SC. Rendered to PDF by
`render_record.py` → `render_record.js`. Three field tiers:

- **[core]** — extracted for **every** case (Haiku mechanical + Opus judgment pass), grep-verified behind `verify.py`. **Populated now.**
- **[enrich]** — extracted by the **Opus pass on the ~80 selected cases only**. **Reserved (keys defined, populated later).**
- **[auto]** — computed by the **aggregation pass** across the whole corpus, never hand-entered. **Reserved (populated later).**

Verbatim rule: every `key_para`, `principle_para`, `treatment_para`, and each
`issues_framed` entry must be an exact substring of the source judgment text
(grep-checked). Analysis fields (holding, principle, significance) are paraphrase.

---

## [core] — populated for every case

```jsonc
{
  "schema_version": "1.0",
  "case_id": "SC-001",
  "docid": "55216283",                     // Indian Kanoon id — primary join key
  "court": "Supreme Court of India",
  "court_type": "SC",                      // SC | HC
  "bench_type": "HC-DB",                   // HC-DB | HC-SB | SC (optional refinement)
  "title": "...", "neutral_cite": "...",
  "date": "2013-07-01",
  "bench": ["..."], "bench_strength": 2, "reportable": true,

  "one_line": "...",                       // the case in a sentence
  "facts_squib": "1–2 lines",
  "disposition": "one line",

  "procedural_posture": "Writ under Art. 226 | s.127 appeal | criminal appeal | ...",
  "outcome_for": "consumer | licensee | mixed (...)",
  "relief_granted": "quashed / remanded / upheld / refund-ordered ...",
  "consumer_category": ["industrial","commercial","domestic","agricultural"],
  "fact_pattern_tags": ["direct-hook/bypass","tampered-meter","excess-load",
                        "wrong-category/purpose","meter-missing","use-after-disconnection"],
  "state": ["Uttar Pradesh"],
  "discom": ["UPPCL ..."],
  "amendment_considered": "post-2007 (Act 26 of 2007) | pre-2007 | mixed",

  "issues_framed": ["<verbatim issue as framed by the court>", "..."],

  "provisions_construed": [ {"provision":"s.126","docid":"124046987"} ],

  "provision_holdings": [
    {
      "provision": "s.126",
      "provision_version": "post-2007",     // which statutory text was applied
      "issue_node": ["jurisdiction-145-154","assessment-126"],
      "holding_type": "ratio",              // ratio | explanatory | obiter | concession
      "holding": "<paraphrase>",
      "interpretation_type": "characterisation-procedure | defined-term | read-down | ...",
      "key_para": "<VERBATIM>",
      "para_ref": "para 30"
    }
  ],

  "authorities": [
    {
      "name": "...", "cite": "...", "court": "...", "docid": "...",
      "principle": "<paraphrase of what it is cited for>",
      "principle_para": "<VERBATIM passage the judgment quotes it for>",
      "treatment": "followed | distinguished | overruled | doubted | explained | referred",
      "treatment_para": "<VERBATIM of the court's own characterisation, when present>",
      "on_issue": "126v135"
    }
  ],
  "authorities_note": "<only when authorities is empty>",

  "regulations_construed": [
    {"reg":"UP Supply Code cl. 8.1","implements":"s.135/s.126","made_under":"s.50"}
  ],

  "ratio": [
    {
      "issue_node": "jurisdiction-145-154",
      "proposition": "<crisp statement>",
      "scope": "SC-binding | HC-DB-binding | HC-SB | obiter",
      "novelty": "new | settles-split | affirms | extends | applies | explains | conflicts",
      "conflicts_with": [], "note": "..."
    }
  ],

  "significance": "2–4 lines",
  "flags": ["leading-on-...","reverses-...","..."],

  "validity": {                             // [core] shell; per_issue/overall refined by [auto]
    "overall": "good-law",                  // good-law | partially-overruled | overruled | reversed | doubted | referred | superseded
    "as_of": "2026-07",
    "provision_version_ok": true,           // false if it applies superseded text as if current
    "per_issue": { "<issue_node>": "good-law; refined by <case> ..." },
    "note": "..."
  }
}
```

### Issue-node taxonomy (fixed keys)
`126v135` · `assessment-126` · `mensrea-135` · `appeal-127` ·
`jurisdiction-145-154` · `compounding-152` · `natural-justice` ·
`provisional-final` · `burden-proof` · `limitation-56`

---

## [enrich] — RESERVED (Opus pass, ~80 selected cases only)

Do **not** populate for the bulk 150; reserved so the shape is fixed:

```jsonc
{
  "subsequent_history": "SLP dismissed | affirmed in CA ... | ...",   // appeal outcome
  "tests_and_principles": [                                           // named tests, verbatim formulation
    {"name":"genus-species test","formulation":"<VERBATIM>","issue_node":"126v135"}
  ],
  "quotable_holding": "<the one sentence a pleader would cite, VERBATIM>",
  "quantum": {"assessed": 0, "disputed": 0, "currency":"INR"},
  "practice_points": ["..."],                                         // do/don't for practitioners
  "confidence": { "<field>": "high|medium|low" },                    // per uncertain field
  "editor_note": "VERIFY-flagged items, open questions"
}
```

## [auto] — RESERVED (aggregation pass, whole-corpus, never hand-entered)

Written by `build_*` tooling from the corpus; overwrites any placeholder:

```jsonc
{
  "cites_in_corpus": ["<docid>"],          // edges restricted to our ~150 cases
  "cited_by_in_corpus": ["<docid>"],       // reverse edges -> in-set in-degree (anchor metric)
  "precedential_weight": 0.0,              // f(bench_strength, reportable, court rank, in-degree)
  "validity.overall": "…",                 // recomputed from the citation graph + statute check
  "validity.per_issue": { },               // set/overwritten when a later case overrules/reverses
  "overruled_by": ["<docid>"], "distinguished_by": ["<docid>"], "followed_by": ["<docid>"],
  "related_records": ["<same-issue siblings>"],
  "split_flag": false,                     // HC divergence on an issue_node
  "extraction": {                          // provenance / QA
    "haiku_model":"claude-haiku-4-5","judgment_model":"claude-opus-4-8",
    "verify_status":"PASS","quotes_grep_verified": true,
    "needs_human_review": false, "retrieved_at":"..."
  }
}
```

### Aggregation deliverables built from the [auto] layer
- `provision_index.json` — every holding per provision, chronological, with evolution/splits/current position.
- `issue_matrix.json` — leading case + line of authority per issue-node.
- `citation_graph.json` — followed/distinguished/overruled edges; sets `validity` + `precedential_weight` + anchor in-degree.

---

## Model assignment (locked)
| Pass | Fields | Model |
|---|---|---|
| A. Mechanical | metadata, provisions_construed, authorities list, verbatim pulls | Haiku 4.5 |
| B. Judgment | holdings, interpretation_type, holding_type, treatment, ratio, novelty, significance, validity shell, [enrich] | **Opus 4.8** |
| C. Aggregation | all **[auto]** fields + the three index files | Opus 4.8 (one-time) |

Gate: `verify.py` must PASS and every VERBATIM field must grep-match the source before a record is committed — on every pass, regardless of model.
