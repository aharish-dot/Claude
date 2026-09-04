# Supply Code Jurisprudence — Processing Runbook

Self-contained procedure for processing a batch of judgments into the **lean schema**.
Any session (fresh or resumed) can execute this from repo state alone. Branch:
`claude/supply-code-jurisprudence-design-yiwgen` (git pull first).

## Batch size
**8 cases per run**, with an early stop if cumulative source exceeds ~22,000 words
(protects quality when a long-case cluster appears). Most UP writ orders are short
(~1-2k words); the occasional long regulatory/Supreme Court judgment counts more.

## Queue & progress
- Pending = files in `html_input/` (process the HTML format — smaller than the `.mht`
  twin in `input/`, extracts to the same clean text, no quoted-printable edge cases).
- "Next" = alphabetical order in `html_input/`.
- A case is **done** when its `summaries/json/<id>.json` + `summaries/pdf/<id>_<slug>_Digest.pdf`
  are committed and both source twins (`.html` and the `.mht` in `input/`) are moved to `processed/`.
- Ids are `SCJ-0NN`, sequential and stable; see `state/index.json` (`next_seq`).

## Per-case flow
1. `python tools/extract_judgment.py "html_input/<name>.html" /tmp/... <id>` → `<id>.txt` + `<id>.fp.json`.
2. Read `<id>.txt` (short cases: main thread is fine). Read `<id>.fp.json` for the Indian Kanoon **doc-ids**.
3. Write `summaries/json/<id>.json` in the lean schema (below). Use ONLY authorities actually
   discussed in the text; match their doc-ids to `<id>.fp.json`; never invent a citation or holding.
4. Render: `python tools/gen_scj.py summaries/json/<id>.json /tmp/<id>.html` then
   `chromium --headless=new --no-sandbox --no-pdf-header-footer --print-to-pdf=summaries/pdf/<id>_<slug>_Digest.pdf file://<abs>/<id>.html`.
5. Add the case to `state/index.json` (status `done`); `git mv` both source twins to `processed/`.

## After the batch
- `python tools/build_supply_code.py` — rebuilds `jurisprudence/index.json` (provision- &
  principle-keyed spine + authorities ledger). Never hand-edit that file.
- Commit (one commit for the batch is fine) and `git push -u origin <branch>`.

## Lean schema (per case) — the ONLY thing we keep
Top-level: `case_id, title, neutral_citation, court, bench, coram, date_of_judgment (ISO),
date_display, docket, page_count, significance, outcome, disposition, headnote, facts,
reusable_constructions[] (significant only), holding_units[],
principle_tags[], not_decided[], authorities[]`.

- **page_count**: integer pages of the **source judgment** (the input PDF), not the digest.
  Copied from the extract fingerprint; `finalize_scj.py` backfills it from the PDF.
- **significance**: `"significant"` | `"ordinary"` | `"procedural"`. Significant = a new or
  reusable construction of the Code/Act (including quashing on a doctrinal point). Ordinary
  (alias `"normal"`) = a routine reasoned disposal applying settled law. Procedural = listing,
  interlocutory, adjournment, contempt dismissed as infructuous/misconceived, not-pressed, or
  otherwise thin. Rendered on PDF page 1 as
  `SUPPLY CODE JURISPRUDENCE · SCJ-NNN · N PAGES · SIGNIFICANT`.

- **outcome**: `"consumer"` | `"licensee"` | `"alternate_remedy"` | `"pending"` |
  `"none"` | `"split"`. Who succeeded on the electricity dispute, not CPC party
  role. A discom-petitioner who wins is `licensee`. Relegation to 6.5 / “apply
  under 4.4 in accordance with law” is `alternate_remedy`, not a consumer win.
  A direction that the connection *shall be granted* is `consumer`. Required
  from SCJ-301. Tally: `python tools/tally_outcomes.py UP-2005::4.4`.

- **headnote**: one dense paragraph stating the whole-case rule (the anchor when a case
  appears under several provision chapters).
- **facts**: 1–2 short paragraphs (about 80–180 words) of the story — who, the connection,
  what happened, what was challenged. Enough to follow the case; not the holding and not a
  dump of docket trivia. Rendered on the digest under the headnote as **FACTUAL SUMMARY**
  (cream box). Labels print as ordinary words (Headnote / Factual Summary), not letter-spaced.
- **reusable_constructions[]**: `{construction, paras}` — required when
  `significance` is `"significant"`; **omit** on ordinary and procedural records.
  A numbered list of the portable propositions the case establishes (the "what to
  cite this for" headline). Distill the ratio into standalone rules; do not copy
  the holding paragraph. `paras` is a string. Rendered on the digest as an indigo
  **REUSABLE CONSTRUCTIONS** box under the facts. Shape: SCJ-225.
- **holding_units[]**: `{provision, code, clause, topic, type, question?, holding,
  qualifier?, paras, flag?}`. Do **not** write `limiting_facts` (dropped from the digest;
  the story belongs in `facts`). `provision` is the key, e.g. `UP-2005::4.3(f)`, `EA2003::56(2)`,
  `WB-2004::5.2` (multi-state — key by the actual Code/Act, never merge a Code clause into an Act
  section). `type` = `"supply_code"` (green) for a Supply Code clause, `"interplay"` (grey) for a
  companion Act provision (s.56(2), s.126/127, s.46, s.174, tariff ss.61/62/64…). `flag` records a
  data-quality note (e.g. a litigant conflating a Code clause with an Act section) or transitional/
  multi-state scope. `paras` = judgment paragraph pins.
- **principle_tags[]**: `{tag, application, lead_authorities:[{name,docid}], paras}` — cross-cutting
  doctrines (kebab-case tag reused across cases): e.g. `own-wrong-maxim`, `arrears-run-with-the-premises`,
  `arrears-bar-is-premises-specific`, `arrears-apportioned-pro-rata-on-subdivision`,
  `theft-uue-enforced-via-code`, `first-due-on-billing-not-consumption`,
  `disconnection-barred-but-recovery-not`, `opportunity-before-final-assessment`,
  `relegate-to-statutory-remedy`, `regulator-cannot-change-rules-at-truing-up`.
- **not_decided[]**: `{point, note, docid?, paras}` — the negative-authority register (points raised
  but not decided; expressly-reserved questions). Vital so nobody over-reads a case.
- **authorities[]**: `{name, citation, court, docid, proposition, how_treated, how_treated_paras,
  cited_by, treatment}`. Capture **every** precedent the judgment cites — electricity-related or not
  (that master table of citations is a project aim). `cited_by` ∈ {Petitioner, Respondent, Court}.
  `treatment` ∈ {Followed, Approved, Applied, Affirmed, Distinguished, Doubted, Overruled, Referred,
  Relied on}. `proposition` = the abstract rule; `how_treated` = what THIS court did with it (kept
  separate on purpose — proposition is reusable across cases, how_treated is case-specific).

Reference records: `SCJ-001` (parallel-operating charges; own-wrong maxim; s.56(2) interplay),
`SCJ-008` (full vested-right-of-appeal authority chain), `SCJ-009` (leading s.56(2) authority).

## Scope notes
- The corpus is **multi-state** (U.P. 2005 is the bulk, but Delhi/DERC, West Bengal 2004, Rajasthan
  etc. appear). Key provisions by their actual Code/Act.
- Theft (s.126 UUE / s.135) cases belong in the jurisprudence: the Supply Code supplies the
  assessment/compounding machinery. Even a "thin" case is a node — record it, don't discard it.
- Supreme Court / APTEL judgments that surface in the supply-code search are kept; set `court` accurately.
