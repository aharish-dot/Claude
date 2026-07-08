# Judgment-pass extraction spec (in-session, Pro plan)

The record for each case is produced by **me (Opus) in this session** — no external
API token, no per-use billing. This file is the standing instruction set so every
record comes out identically shaped and quality-gated.

## Per-case procedure (resumable)
1. **Stage 0 (free):** `prefill/<ID>.prefill.json` already holds docid, court,
   court_type, date, bench, neutral_cite, provisions_construed, authority_candidates,
   cited_by_seeds — parsed from Indian Kanoon. Start from it; never re-derive by hand.
2. **Read** `queue/<ID>.txt` (the full judgment).
3. **Write** `records/<ID>.record.json` conforming to `SCHEMA.md` v1.0 ([core]
   populated; [enrich] only for the ~80 selected; [auto] left for aggregation).
   Model both gold examples: `SC-001.record.json` (no authorities) and
   `HC-003.record.json` (nine authorities with `principle_para`/`treatment_para`).
4. **Verify gate** (`verify_record.py <ID>`): every `key_para`, `principle_para`,
   `treatment_para`, and each `issues_framed` entry MUST be an exact substring of
   `queue/<ID>.txt` (whitespace-normalised). Must print PASS before commit.
5. **Render** `render_record.py records/<ID>.record.json` → HTML → PDF.
6. **Commit** the record + html + pdf; set `manifest.json.status[<ID>]="done"`.

## Quality rules (non-negotiable)
- **Verbatim fields are exact quotes** from the judgment — court's own reasoning,
  not the reproduced bare-act text. If a quote won't grep-match, fix the quote,
  don't loosen the gate.
- **Route to issue-nodes accurately** — a case's headline issue is not its only
  issue; tag every proposition (e.g. a 126-vs-135 case that also decides
  natural-justice and §56(2)).
- **holding_type**: mark `ratio` vs `explanatory`/`obiter` honestly — obiter must
  not feed the binding-law aggregation.
- **authorities**: `principle_para` = the passage the judgment quotes the authority
  for; `treatment_para` = the court's own characterisation, when present; both
  verbatim. Empty `authorities` + a `authorities_note` is correct for a
  pure-statutory case.
- **validity**: set the shell (`overall`, `provision_version_ok`, per-issue notes);
  the citation-graph recompute happens in aggregation.
- **amendment_considered / provision_version**: state pre-2007 vs post-2007 — the
  2007 amendment changed the §126 multiplier, §127 pre-deposit and inserted
  "dishonestly" into §135.

## Wave 1 (this batch): HC-006 … HC-015
Delhi (Kantroo, Harvinder), Rajasthan (Hindustan Zinc), Punjab-Haryana (Ramesh
Chand), Kerala (Sulabha), Allahabad (Shishir Jain), Calcutta (WBSEB), Patna
(Bihar SEB), Bombay (MSEDCL), Orissa (OPGC) — 8 High Courts.

Progress is tracked in `manifest.json.status`; re-running skips done cases, so a
Pro usage-limit interruption is safe to resume.
