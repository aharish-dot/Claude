# When the user says **next** / **next case**

Do **exactly one** unique pending judgment. Do not wait for confirmation. Do not start the treatise.

Unattended (user runs this; they do not babysit):

```
cd C:\Users\HP\Downloads\Grok\Claude
powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 100
```

Each iteration still produces **JSON + digest PDF + commit + push**. `finalize_scj.py` does PDF/git. If the ticket is **`authoring=stencil`**, Grok is **not** called — `tools/scj_stencil.py --write` fills the JSON. `-NoPush` is opt-out. `-DryRun` prints commands. Logs: `supply-code/tmp/loop_logs/`.

## Chat path (same artifacts)

1. `python tools/prepare_next_scj.py`  
   Exit 2 / ticket `status: NO_INPUT` → stop. Docket/filename duplicates are retired to `processed/` with no new id.
2. Read `supply-code/tmp/NEXT_TICKET.json`.
   - **`authoring=stencil`** (proved clone: 6.5 billing relegation, 6.8 assessment-hearing, or contempt of a 6.5 writ dismissed): run `python tools/scj_stencil.py --write` then step 4. **Do not** read the judgment or write JSON by hand. If write fails: `python tools/prepare_next_scj.py --demote` then follow short/full — **do not** re-prepare the same PDF as stencil. Listing-only / 4.4 / 6.5-*refusals* / 6.8 quashes / court-grants (SCJ-411 Lok Adalat compliance) are **not** stencil.
   - **`authoring=short`** (pages ≤ 2 or words ≤ 800, or uncited with pages ≤ 3 and words ≤ 1500): follow `tools/prompts/next_case_short.txt`: ticket `.txt` + `.fp.json` + `catalog_hits` only — **do not** load `catalog.txt`, `SCJ-280.json`, RUNBOOK, or the generator. Schema is in the prompt. `paras` is a string; `not_decided` is `[{point, …}]`. Uncited = `citation_count` on the fingerprint (IK **or** prose reporters / `X v. Y` in the body, not the caption).
   - Else follow `tools/prompts/next_case_once.txt` (full catalog + SCJ-280).
   **Do not** load `HANDOFF.md` or `jurisprudence/index.json`.
3. Write **only** `supply-code/summaries/json/<case_id>.json` (lean schema) — skip this step on stencil. Include `page_count`, `significance` (`significant` | `ordinary` | `procedural`; `normal` = ordinary), `outcome` (`consumer` | `licensee` | `alternate_remedy` | `pending` | `none` | `split` — who succeeded on the electricity dispute, not CPC party role; required from SCJ-301), and `facts`. Never invent citations/holdings. `cited_by` is a string; `lead_authorities` is `[{name, docid}, …]`; provision keys are `CODE::clause`. No `limiting_facts`. Thin orders still recorded, with a `flag`. Unresolved points → `not_decided[]`.
4. `python tools/finalize_scj.py <case_id> --source "<ticket.source>"`  
   Do not Chrome/git/index by hand.
5. Stop. One-line status: `SCJ-NNN · title · disposition · next_seq=N · digest ok`.

Skip: `processed/` names · ` (1).pdf` · `WRIC(A)_20210_2012.pdf` (SCJ-273). Next: run prepare (`next_seq` in `state/index.json`).
