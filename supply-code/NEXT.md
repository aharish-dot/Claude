# When the user says **next** / **next case**

Do **exactly one** unique pending judgment. Do not wait for confirmation. Do not start the treatise.

Read `HANDOFF.md` + `RUNBOOK.md` if this is a fresh chat. Then:

## 1. Pick the file
- Queue = PDFs in `supply-code/input/` (alphabetical).
- **Skip:** already in `processed/` · names matching ` (1).pdf` (upload twins) · `WRIC(A)_20210_2012.pdf` (already **SCJ-273**).
- **Duplicate guard BEFORE assigning an id:** grep `state/index.json` and `summaries/json/` for the writ/docket number and party names. `WRIC(A)_10937_2026.pdf` was **already SCJ-169** — retire to `processed/` without a new id, then take the following unique file (that is still “next”).
- Id = `SCJ-` + zero-padded `state/index.json` → `next_seq` (currently **283**). Next file as of this note: **`WRIC(A)_12303_2026.pdf`**.

## 2. Extract and draft
```
python tools/extract_judgment.py "supply-code/input/<file>" "supply-code/extracts" SCJ-NNN
```
Read `.txt` (short cases: this thread). Reuse existing `principle_tags` / provision keys. Do not invent citations or holdings. Thin / interlocutory / contempt / not-pressed orders: still record, compactly, with a `flag`. Points raised but not decided → `not_decided[]`.

Schema gotchas: `cited_by` is a **string**; `lead_authorities` is `[{name, docid}, …]`; provision keys are `CODE::clause`.

## 3. Render, index, commit
```
python tools/gen_scj.py summaries/json/SCJ-NNN.json summaries/SCJ-NNN.html
```
Windows Chrome (must use a **separate** `--user-data-dir` or a running Chrome swallows the job):

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --no-sandbox --user-data-dir="%TEMP%\chrome-pdf-scj" --no-pdf-header-footer --print-to-pdf="<abs pdf>" "file:///<abs html with forward slashes>"
```

PDF name: `SCJ-NNN_<slug>.pdf` — **no `_Digest`**. Bump `next_seq`, append the case in `state/index.json`, `Move-Item` source → `processed/`, delete the temp HTML, `python tools/build_supply_code.py` (never hand-edit `jurisprudence/index.json`).

Commit one case, message `supply-code: process SCJ-NNN (short title — one-line holding)`, push branch `claude/supply-code-jurisprudence-design-yiwgen`. Do not commit `extracts/SCJ-*.txt` / `.fp.json`.

## 4. Reply
Cause title, court/bench/date/docket, disposition, what was held / not decided, paths, spine counts, next filename. Then stop.
