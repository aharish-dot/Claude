# When the user says **next** / **next case**

Do **exactly one** unique pending judgment. Do not wait for confirmation. Do not start the treatise.

Unattended (user runs this; they do not babysit):

```
cd C:\Users\HP\Downloads\Grok\Claude
powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 100
```

Each iteration still produces **JSON + digest PDF + commit + push**. Grok only authors the JSON; `finalize_scj.py` does PDF/git. `-NoPush` is opt-out. `-DryRun` prints commands. Logs: `supply-code/tmp/loop_logs/`.

## Chat path (same artifacts)

1. `python tools/prepare_next_scj.py`  
   Exit 2 / ticket `status: NO_INPUT` → stop. Docket/filename duplicates are retired to `processed/` with no new id.
2. Read `supply-code/tmp/NEXT_TICKET.json`, then the ticket's `.txt` (full judgment) and `.fp.json`. Read `supply-code/jurisprudence/catalog.txt` for existing keys. Shape like `summaries/json/SCJ-280.json`. **Do not** load `HANDOFF.md` or `jurisprudence/index.json`.
3. Write **only** `supply-code/summaries/json/<case_id>.json` (lean schema). Never invent citations/holdings. `cited_by` is a string; `lead_authorities` is `[{name, docid}, …]`; provision keys are `CODE::clause`. Thin orders still recorded, with a `flag`. Unresolved points → `not_decided[]`.
4. `python tools/finalize_scj.py <case_id> --source "<ticket.source>"`  
   Do not Chrome/git/index by hand.
5. Stop. One-line status: `SCJ-NNN · title · disposition · next_seq=N · digest ok`.

Skip: `processed/` names · ` (1).pdf` · `WRIC(A)_20210_2012.pdf` (SCJ-273). Next as of handoff: **`WRIC(A)_12303_2026.pdf` → SCJ-283**.
