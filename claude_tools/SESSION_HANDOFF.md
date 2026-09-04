# Claude Session Handoff — Supply Code Jurisprudence

**Read this first in a fresh chat.** It has everything to continue Claude's part of
this project without re-deriving. Companion: `claude_tools/README.md` (the split
contract). Grok's docs: `supply-code/{NEXT,HANDOFF,RUNBOOK}.md`, `tools/PLAYBOOK.md`
(useful background, but the Claude pipeline below supersedes them for Claude's work).

_Last updated: end of the session that built the Claude pipeline (commit ~`970cc43`)._

---

## 0. The one-paragraph situation
This repo turns Indian electricity **Supply Code** judgments into lean+rich JSON
digests (+ a PDF each) folded into a provision/principle **spine**
(`supply-code/jurisprudence/index.json`). **Grok** and **Claude** both work the
same shared corpus but from **separate queues and separate tools** so they never
clash. **Claude authors everything > 10 pages, plus the wordiest 10 % of the short
cases; Grok authors the rest.** Branch (never leave it):
`claude/supply-code-jurisprudence-design-yiwgen`.

## 1. First actions in a new session
1. `cd /home/user/Claude` and `git pull --rebase origin claude/supply-code-jurisprudence-design-yiwgen`.
2. `python3 -m pip install --quiet pymupdf` (needed for extract/index; not always present).
3. `export CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (glob may differ; `ls /opt/pw-browsers/` — finalize also auto-finds it).
4. Read this file + `claude_tools/README.md`.
5. Process the next case (§4). Work **turn-based** — do not run while Grok is running.

## 2. The Claude/Grok split (do not violate)
- **Tools:** Grok owns `tools/`. Claude **runs** `tools/` unmodified and puts any
  new/modified program in **`claude_tools/`**. (One authorised exception was made:
  a minimal fix to `tools/prepare_next_scj.py` `is_docket_dup`, see §7.)
- **Queues:** Grok's queue is `supply-code/input/`. Claude's queue is
  `supply-code/claude_input/` (Grok never scans it). Manifest of Claude's queue:
  `supply-code/claude_input/_queue_manifest.json`.
- **Shared (via the pipeline only):** `state/index.json` (`next_seq`), `summaries/`,
  the `jurisprudence/` spine + catalog, `processed/`. Never hand-edit the spine.
- **Provenance:** Claude sets JSON `model: "Claude Opus 4.8"` and signs every commit
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` + a `Claude-Session:` trailer.

## 3. Current durable state (verify with the commands, don't trust this blindly)
- **Corpus:** 708 cases, `next_seq = 709`, **no gaps** (`SCJ-001..708` contiguous).
  Check: `python3 -c "import json;d=json.load(open('supply-code/state/index.json'));ids=sorted(int(c['case_id'].split('-')[1]) for c in d['cases']);print('n',len(ids),'next',d['next_seq'],'gaps',[n for n in range(1,max(ids)+1) if n not in set(ids)])"`
- **Grok queue** `supply-code/input/`: ~2,756 genuine ≤10pp PDFs (+ `input_pdf_stats.json`, `dup_scan_report.json`).
- **Claude queue** `supply-code/claude_input/`: **411 PDFs remaining** (started 412; SCJ-707 done). Manifest buckets:
  - `new` — genuine >10pp, author a NEW record (57; 1 done).
  - `upgrade` — >10pp judgments already in the corpus as lean Grok records; author a RICH replacement into the **existing** `case_id` (49). Each entry has `existing_case_id`.
  - `new_from_grok_top10pct` — wordiest ≤10pp genuine, author NEW (306).
- **Done this session as exemplars (rich format):** SCJ-708 (new), SCJ-225 (upgrade of the Raman Ispat dup; SCJ-707-the-dup was retired), SCJ-707 (new, the Baba Ice contempt case — the 707 gap fill). Look at these three JSON/PDF as templates.

## 4. Processing one case (the pipeline)
Serial, chat-driven. Two commands in `claude_tools/scj_claude.py`:
```
# 1. claim (auto-picks next: upgrades, then big-new, then wordy) OR name a file:
python3 claude_tools/scj_claude.py claim --next
python3 claude_tools/scj_claude.py claim --file 2010/WRIC(A)_70238_2010.pdf
#    -> prints READY mode=<new|upgrade> <case_id> <source>, writes tmp/CLAUDE_TICKET.json,
#       extracts text to supply-code/extracts/<case_id>.txt (+ .fp.json)

# 2. Claude authors supply-code/summaries/json/<case_id>.json in the RICH schema (§5),
#    reading ONLY supply-code/extracts/<case_id>.txt (never the whole PDF into context).
#    For mode=upgrade, OVERWRITE the existing <case_id>.json with the richer version,
#    keeping its best identity fields (neutral_citation, full docket, title).

# 3. finalize (renders rich PDF, moves claude_input->processed, updates state+spine+catalog,
#    stamps model, commits signed, pushes):
python3 claude_tools/scj_claude.py finalize <case_id>
```
Before finalize, self-check: JSON parses; `cited_by` is a string; `lead_authorities`
are `{name,docid}` objects; every `paras` is a string; `provision` is `CODE::clause`;
no `limiting_facts`; **grep every `evidence` quote against `extracts/<id>.txt`** so it
is verbatim. Suggested order: upgrades and >10pp first (your firm ">10pp must be
rewritten" rule), then the wordy ≤10pp. ~6-10 cases per session, then a fresh chat.

## 5. The RICH schema (what Claude adds over Grok's lean schema)
Base fields (keep): `case_id, title, neutral_citation, court, bench, coram,
date_of_judgment (ISO), date_display, docket, page_count, significance
(significant|ordinary|procedural), outcome (consumer|licensee|alternate_remedy|
pending|none|split), disposition, headnote, facts, holding_units[], principle_tags[],
not_decided[], authorities[]`. Rules for these are in `supply-code/RUNBOOK.md`.
**Claude additions (rendered by `claude_tools/gen_scj.py`):**
- `source_file` — the source PDF basename (finalize sets it from the ticket; shown on the PDF as "Source file: …"). This is point (4) the user asked for — traceability.
- `pin_basis` — `"page"` (pins render `p. N`; use for PDFs with printed page numbers), `"date"` (pins render as-is, e.g. `order of 28.04.2010`; use for contempt/order-sheets with no page numbers), or `"paragraph"`/absent (`¶ N`). **Pins MUST match the actual source file** — the SCJ-225 bug was inherited reporter-page pins (505-512) that weren't in the 14-page PDF; always pin to what the reader can open.
- `reusable_constructions[]` — `[{construction, paras}]`, a **numbered** list of the portable propositions the case establishes/applies (the headline "what to cite this for"; see the Raman Ispat list in SCJ-225).
- `holding_units[].evidence[]` — `[{quote, paras}]`, a **verbatim** grounding quote (+pin) per holding. Anti-hallucination guard — grep-confirm each quote.
- `holding_units[].nature` — `"ratio"` | `"obiter"`.
- `related_cases[]` — `[{case_id, note}]`, prior SCJ cases sharing a provision/tag. Compute from the spine:
  `python3 -c "import json;sp=json.load(open('supply-code/jurisprudence/index.json'));print([(c['case_id'],c['title'][:40]) for c in sp['provisions'].get('UP-2005::4.3(f)',{}).get('cases',[])])"`
New JSON fields are ignored by Grok's shared spine builder (verified), so they never break it.

## 6. Tools in claude_tools/
- `scj_claude.py` — the claimer/finalizer (§4). Reuses `tools/` modules unmodified.
- `gen_scj.py` — rich digest generator (fork of `tools/gen_scj.py`); renders the §5 additions.
- `dupscan.py` — duplicate scanner (`python3 claude_tools/dupscan.py` → `supply-code/input/dup_scan_report.json`). Run it after big queue changes.
- `index_input_pdfs.py` — page/word-count index of a queue dir (`--dir supply-code/input` or `claude_input`).
- `README.md` — the split contract. `SESSION_HANDOFF.md` — this file.

## 7. Duplicates & the dedup fix (context)
The docket-dedup in `tools/prepare_next_scj.py` searched `"No. <n> of <yr>"` and
missed connected petitions written `"Nos. 16147 of 2009 and 16149 of 2009"` — which
created SCJ-707 as a duplicate of SCJ-225. Fixed (authorised) by adding a digit-boundary
`"<n> of <yr>"` regex catch-all in `is_docket_dup`. A full scan found **only** 225/707
internal, **151 queue duplicates** (retired: 102 small ones to `processed/`; the 49
>10pp ones are the `upgrade` bucket), and 5 false-positive soft candidates. Both queues
are now duplicate-free. If new PDFs are added later, re-run `dupscan.py`.

## 8. Open items / decisions pending
- **411 Claude-queue cases** remain to author (56 new + 49 upgrade + 306 wordy). This is the main ongoing work.
- **Existing >10pp corpus cases with no queue twin:** the user's rule "anything >10pp must be rewritten" may extend to lean Grok records already in the corpus that were never in a queue. Not yet quantified or actioned — raise with the user. Quantify:
  `python3 -c "import json,glob;n=[f for f in glob.glob('supply-code/summaries/json/SCJ-*.json') if (lambda c: isinstance(c.get('page_count'),int) and c['page_count']>10 and 'reusable_constructions' not in c)(json.load(open(f)))];print(len(n),'existing >10pp lean records')"`
- **Doc-id backfill** (Indian Kanoon API; `IK_API_TOKEN` is set) was offered and deferred — authorities mostly have blank `docid`. Optional future quality win.

## 9. If Claude's usage limit is exhausted — can Grok run? (user Q)
**Yes.** Grok processes `supply-code/input/` (the ~2,756 ≤10pp cases) and **never
touches `claude_input/`**, so it cannot collide with Claude's queue. Grok now has the
patched dedup (once it pulls this branch), so it won't recreate connected-petition
duplicates. Caveats: (a) **turn-based** — run Grok OR Claude, not both at once (the
`tmp/` lock is per-machine, and both write `state/index.json`/spine → concurrent runs
conflict on push); (b) Grok assigns ids from `next_seq` (709+), same as Claude's new
cases, so alternate, don't overlap; (c) Grok authors the lean format, not the rich one.
Start Grok per `supply-code/NEXT.md` (e.g. Ubuntu `./tools/run_next_case_loop.sh --count 50 --workers 2`).
```
```
