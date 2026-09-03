# When the user says **next** / **next case**

Do **exactly one** unique pending judgment. Do not wait for confirmation. Do not start the treatise.

Unattended (user runs this; they do not babysit). Judgment PDFs live **in the GitHub repo** under `supply-code/input/<year>/`. Clone or `git pull` any working copy of this branch, then from that repo root.

**Windows** (this folder):

```
git pull
powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 50 -Workers 2
```

**Ubuntu** (a separate clone of the same branch — do not copy this Windows folder):

```
git pull
./tools/run_next_case_loop.sh --count 50 --workers 2
```

Both launchers call the same `tools/run_next_case_workers.py`. `--workers 2` (PowerShell `-Workers 2`) authors two cases at once. Claim (id + PDF) and finalize (Chrome/git/index) stay serial under a lock, so two windows of this command cannot share an SCJ id. `-Workers 1` / `--workers 1` is the old one-at-a-time loop. Max 4. Do not run the old pre-queue script against the same `input/` while this is going.

**One machine at a time.** GitHub is the queue (`input/`) and the archive (`processed/` + JSON + digest PDFs). The directory lock in `tmp/` is local and does not protect two PCs. Never start the loop on Ubuntu while it is still running on Windows (or the reverse). Switch only after the loop has stopped and `git status` is clean except gitignored `tmp/` / `extracts/`. Then `git pull` on the other machine. If you abort mid-case, finish or delete `supply-code/tmp/tickets/` on **that** machine and restore uncommitted `state/index.json` before switching — a reserved `next_seq` is not pushed until finalize.

First time on Ubuntu: clone branch `claude/supply-code-jurisprudence-design-yiwgen`, install Python 3, `pip install pymupdf`, Grok CLI (`~/.grok/bin` on PATH, logged in), Chromium or Chrome (`chromium` / `google-chrome` on PATH, or set `CHROME`). Verify with `./tools/run_next_case_loop.sh --dry-run --count 1` — it must print Grok and Chrome paths.

Each case still produces **JSON + digest PDF + commit + push**. `finalize_scj.py` does PDF/git, one at a time. If the ticket is **`authoring=stencil`**, Grok is **not** called — `tools/scj_stencil.py --write` fills the JSON. `-NoPush` / `--no-push` is opt-out. `-DryRun` / `--dry-run` prints the plan and checks Grok + Chrome. Logs: `supply-code/tmp/loop_logs/`. Crash recovery: `tmp/tickets/SCJ-NNN.json` is resumed on the next start.

## Chat path (same artifacts)

1. `python tools/prepare_next_scj.py`  
   Exit 2 / ticket `status: NO_INPUT` → stop. Docket/filename duplicates are retired to `processed/` with no new id. Reserves `SCJ-NNN` (queue lock). Per-case ticket: `tmp/tickets/SCJ-NNN.json`. Do not run this while an unattended loop is already claiming.
2. Read `supply-code/tmp/NEXT_TICKET.json` (copy of the reserved ticket).
   - **`authoring=stencil`** (proved clone: 6.5 billing relegation, 6.8 assessment-hearing, or contempt of a 6.5 writ dismissed): run `python tools/scj_stencil.py --write` then step 4. **Do not** read the judgment or write JSON by hand. If write fails: `python tools/prepare_next_scj.py --demote` then follow short/full — **do not** re-prepare the same PDF as stencil. Listing-only / 4.4 / 6.5-*refusals* / 6.8 quashes / court-grants (SCJ-411 Lok Adalat compliance) are **not** stencil.
   - **`authoring=short`** (pages ≤ 2 or words ≤ 800, or uncited with pages ≤ 3 and words ≤ 1500): follow `tools/prompts/next_case_short.txt`: ticket `.txt` + `.fp.json` + `catalog_hits` only — **do not** load `catalog.txt`, `SCJ-280.json`, RUNBOOK, or the generator. Schema is in the prompt. `paras` is a string; `not_decided` is `[{point, …}]`. Uncited = `citation_count` on the fingerprint (IK **or** prose reporters / `X v. Y` in the body, not the caption).
   - Else follow `tools/prompts/next_case_once.txt` (full catalog + SCJ-280).
   **Do not** load `HANDOFF.md` or `jurisprudence/index.json`.
3. Write **only** `supply-code/summaries/json/<case_id>.json` (lean schema) — skip this step on stencil. Include `page_count`, `significance` (`significant` | `ordinary` | `procedural`; `normal` = ordinary), `outcome` (`consumer` | `licensee` | `alternate_remedy` | `pending` | `none` | `split` — who succeeded on the electricity dispute, not CPC party role; required from SCJ-301), and `facts`. Never invent citations/holdings. `cited_by` is a string; `lead_authorities` is `[{name, docid}, …]`; provision keys are `CODE::clause`. No `limiting_facts`. Thin orders still recorded, with a `flag`. Unresolved points → `not_decided[]`.
4. `python tools/finalize_scj.py <case_id> --source "<ticket.source>"`  
   Do not Chrome/git/index by hand.
5. Stop. One-line status: `SCJ-NNN · title · disposition · next_seq=N · digest ok`.

Skip: `processed/` names · ` (1).pdf` · `WRIC(A)_20210_2012.pdf` (SCJ-273). Next: run prepare (`next_seq` in `state/index.json`).
