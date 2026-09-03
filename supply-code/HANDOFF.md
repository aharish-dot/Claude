# Supply Code Jurisprudence — Session Handoff

> **Read this first in a fresh chat.** Strategic context + resume point.
> Mechanical procedure: **`RUNBOOK.md`**. One-command trigger: **`NEXT.md`**.
> Project rationale: **`README.md`**. Do not duplicate them.

_Last updated: 2 September 2026 — pipeline after wiring 6.8 + BILL/RELEGATE cues: (1) **6.8-assessment-hearing** stencil live; (2) BILL includes wrong bill / electricity amount due / unpaid dues / recovery citation; RELEGATE includes “should file a challenge” / “can get the bill corrected” / “if the petitioner approaches”; (3) **GRANT veto** (SCJ-411); (4) stencil write fail **demotes**; (5) `citation_count` is IK **or** prose. **Review at SCJ-537** (`sessions/2026-09-02-review-488-537.md`). Listing-only still off._

---

## 1. Where the project stands

- **487 judgments fully processed** → `SCJ-001` … `SCJ-487`. Lean JSON + digest PDF + folded into `jurisprudence/index.json`.
- **`state/index.json`**: `next_seq = 488`. **Review at SCJ-537** (`sessions/2026-09-02-review-488-537.md`). 388–437 notes: `sessions/2026-09-01-review-388-437.md`. 338–387 notes: `sessions/2026-09-01-pipeline-review.md`. SCJ-438–487 ran before the 388–437 review was filled; metrics for that batch were dropped.
- **Treatise outline** exists (`jurisprudence/treatise/00-OUTLINE.md`); **all Parts still `todo`**. Treatise remains **ON HOLD** until the input queue is empty.
- **Branch**: `claude/supply-code-jurisprudence-design-yiwgen` (commit and push each case).
- **Two working copies are allowed:** this Windows folder, and a separate Ubuntu clone of the same branch. Sources in the live queue are **PDFs in `supply-code/input/`**, not `html_input/`. Run the loop on **one machine at a time**; GitHub is the shared queue.

## 2. Governing decision (unchanged)

Process remaining judgments **first** (mechanical pipeline → index), **then** author the treatise **once** on the complete corpus. Do **not** write treatise Parts yet.

## 3. What the user will say

| User says | Do |
|---|---|
| **next** / **next case** / **now next one** | Process **exactly one** unique pending file. See **`NEXT.md`**. Do not ask. Stencil tickets: write+finalize only, do not read the judgment. |
| *(unattended)* | Windows: `powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 50 -Workers 2`. Ubuntu: `./tools/run_next_case_loop.sh --count 50 --workers 2`. Default **2** authoring workers (max 4). Claim + finalize stay serial under `tmp/queue.lock` (local to that PC). Each grok is a fresh `grok -p` **unless** `authoring=stencil` (no grok). `-Workers 1` / `--workers 1` = old serial loop. Never run both PCs at once. |
| **next batch** | `RUNBOOK.md` default: up to 8, early-stop ~22k words. |
| Anything about the treatise / booklet Parts | Not yet, unless they explicitly override §2. |

**Immediate next:** input queue is empty (`next_seq=537`, last done **SCJ-536**). When new PDFs land in `input/`: Windows `tools\run_next_case_loop.ps1 -Count 50 -Workers 2` or Ubuntu `./tools/run_next_case_loop.sh --count 50 --workers 2` from repo root (`git pull` first). Skip `(1)` twins.

## 4. Gotchas a fresh session MUST know

### Duplicate / skip
- **`WRIC(A)_20210_2012.pdf`** still in `input/` = already **SCJ-273**. Skip; optionally move to `processed/`.
- **`WRIC(A)_12303_2026.pdf`** may still be in `input/` = already **SCJ-283**. Docket-dup retire; no new id.
- Files named `… (1).pdf` are Chrome/re-upload twins. Skip; move to `processed/` when the un-suffixed twin is processed (done for 11370). Remaining `(1)` twins: `15707_2026`, `15943_2026`, `21747_2026`.
- **Docket duplicate:** `WRIC(A)_10937_2026.pdf` = **SCJ-169** (Abhimanyu Singh, 9 Apr 2026). Retired to `processed/` without a new id. **Always grep docket + parties before assigning `SCJ-NNN`.**

### Pipeline (Windows or Ubuntu)

**User does nothing after starting it.** Chat **next** or the loop command both end in JSON + digest PDF + commit + **push** per case. Source PDFs are tracked in `supply-code/input/` on this branch; finalize moves each one to `processed/` **in git** (not only on disk). Drop new year folders into `input/` on GitHub, `git pull` on any machine, run the loop. Extracts stay local (`supply-code/extracts/` is gitignored) — they are rebuilt on whichever PC claims the case.

Windows stays in this folder. Ubuntu is a **fresh clone**, not a copy of the Windows tree (`tmp/` tickets and `queue.lock` must not travel). Switch PCs only when the loop is stopped and the working tree is clean; then `git pull` on the other machine. Do not run both loops at once — `tmp/queue.lock` is per-disk, not a GitHub lock.

Token split:

1. `python tools/prepare_next_scj.py` — next unique PDF, skip dups, extract text, **reserve `SCJ-NNN`** (bumps `next_seq` under the queue lock). Per-case ticket at `tmp/tickets/SCJ-NNN.json`; legacy copy at `tmp/NEXT_TICKET.json`. Classifier may set `authoring=stencil` + `stencil_family`. Open tickets are skipped so two workers cannot take the same PDF. `--claim-new` skips resume (the parallel loop uses this).
2. JSON:
   - **Stencil** (`authoring=stencil`): `python tools/scj_stencil.py --write` — **no grok**, do not read the judgment. Live families: `6.5-billing-relegation`, `6.8-assessment-hearing`, `contempt-6.5-dismissed`. BILL cue includes `current`/`impugned` bill (SCJ-353), `wrong bill`, `electricity amount due`, unpaid electrical dues, recovery citation (SCJ-408). RELEGATE includes “should file a challenge” / “can get the bill corrected” / “if the petitioner approaches” (SCJ-399/468/487). GRANT veto: `we intervene` / `forthwith comply` / petition allowed / mandamus issued (SCJ-411). 6.8 is recovery citation + no hearing + deposit + Assessing Officer, pages ≤ 2; quash / s.135 stay off. Not stencil: listing-only, 4.4, 6.5 invoked-but-not-applied (SCJ-283/284/288), 6.5 order quashed (SCJ-379), 6.8 quashes (SCJ-367/375), court-grants.
   - **If stencil write fails:** `python tools/prepare_next_scj.py --demote` then follow the new `authoring` (short/full). **Do not** re-run prepare as stencil on the same id (358 burned 30 retries). Loop does this itself. Track `demoted`.
   - **Short path** if pages ≤ 2 **or** words ≤ 800, **or** uncited with pages ≤ 3 and words ≤ 1500 (`authoring=short`, `tools/prompts/next_case_short.txt`, `catalog_hits` on the ticket, max 15 turns). **Do not** load `catalog.txt`, SCJ-280, RUNBOOK, `finalize_scj.py`, or `gen_scj.py`. Schema is in the prompt. `paras` is a string; `not_decided` is objects. Uncited = fingerprint `citation_count` (IK hyperlinks **or** prose reporters / body `X v. Y`; not the caption or this case’s Neutral Citation No.).
   - **Full path** otherwise (`tools/prompts/next_case_once.txt` + catalog + SCJ-280).
   - Does not load this HANDOFF or `jurisprudence/index.json`.
3. `python tools/finalize_scj.py SCJ-NNN --source "<file>"` — schema gates, Chrome/Chromium PDF (`--user-data-dir` always; Windows Google Chrome or Linux `chromium` / `google-chrome` / Playwright cache / `$CHROME`), state, spine, catalog, git commit+push. Takes the same queue lock as prepare. Never rewinds `next_seq` (inflight reservations stay reserved). Parallel workers do **not** run this; the orchestrator does, one case at a time.

- PDF name: `SCJ-<NNN>_<slug>.pdf` — **no `_Digest`**.
- Do not commit `extracts/SCJ-*.txt` / `.fp.json` (gitignored). Input PDFs **are** committed; the case commit also stages `input/<file>` deleted + `processed/<file>` added.
- Chrome lookup: Windows `chrome.exe`; Linux PATH (`chromium`, `google-chrome`), `/opt/pw-browsers/…`, `~/.cache/ms-playwright/…`, or env `CHROME`.

### Schema (still breaks `build_supply_code.py` if wrong)
- `cited_by` = string (`"Court"` / `"Petitioner"` / `"Respondent"`), never a list.
- `lead_authorities` = `[{name, docid}, …]`, never bare strings.
- `provision` = `CODE::clause` (never merge a Code clause into an Act section).
- `type`: `"supply_code"` | `"interplay"` | `"electricity_act"`.
- `page_count` = integer pages of the **source judgment** (fingerprint / input PDF). Digest PDF page 1 eyebrow: `SUPPLY CODE JURISPRUDENCE · SCJ-NNN · N PAGES · SIGNIFICANT`.
- `significance`: `"significant"` | `"ordinary"` | `"procedural"` (`normal` aliases ordinary). Required on new records; old records without it still render.
- `outcome`: `"consumer"` | `"licensee"` | `"alternate_remedy"` | `"pending"` | `"none"` | `"split"`. Who succeeded on the **electricity dispute**, not the CPC petitioner label (a discom that files and wins is `licensee`). `alternate_remedy` = relegated to 6.5/6.8/s.127 or “apply/consider in accordance with law” without a merits grant. `pending` = listed. `none` = infructuous / not-pressed / contempt dismissed without deciding the bill. Required from **SCJ-301**. Aliases: petitioner→consumer, discom→licensee. Tally: `python tools/tally_outcomes.py UP-2005::4.4`.
- `facts`: 1–2 short paragraphs of the story. Digest PDF: cream **FACTUAL SUMMARY** box under the headnote. Labels print as ordinary words (`HEADNOTE` / `FACTUAL SUMMARY`), not letter-spaced. Old records without `facts` still render.
- Do **not** write `limiting_facts` on holding-units (dropped from the digest from SCJ-287 on). Generator ignores the field even if present on old JSON.
- OFFTOPIC / thin orders still recorded, compactly, with a `flag`. Listing-only → `OFFTOPIC::procedural-listing`.
- Validate JSON + the two gotcha checks before `gen_scj.py`.

### Doctrinal notes (do not paper over)
- **SCJ-278** (Satish Kumar Bharti): s.135(1-A) 24-hour FIR + Clause 8.2 held **mandatory**; *Indresh Patel* (DB, directory) called **per incuriam**; follows *Varun Kumar Yadav* (SLP pending). Tension stays on the table. Statutory clock is from **disconnection**; Court used inspection-to-FIR gap.
- **SCJ-273**: possibility of theft ≠ actual theft; non-speaking assessment/appeal quashed, **remitted**.
- **SCJ-285 / SCJ-286** (Sangam Crusher / K.G.N. Stone Crusher, twins, 27 Feb 2026): 11 kV cable on the floor from which theft “can be done” is **not** theft; s.135(1) proviso presumption misplaced without artificial means on the spot; s.126 assessment + s.127 appeal **set aside, no remand**. Follows *Ashok Kumar* 2008 (6) ADJ 660. Same `theft-cannot-rest-on-mere-possibility` line as SCJ-070/273.
- **SCJ-288** (Shabanam Begam): interlocutory. Clause 4.4 indemnity (tenant without landlord consent) vs arrears attaching to the premises / 4.4(vii) prepaid — **raised, not decided**. Landlord’s son added; listed 22.5.2026.
- Clause 4.5(d) cluster includes interlocutory **SCJ-282** (Tehsildar NOC + alt-route costing) beside SCJ-104/120/169.
- Contempt of a Clause 6.5 relegation: SCJ-275 (misconceived), SCJ-276 (infructuous on compliance).
- **SCJ-401** (Guddi Kesarwani): occupier / trespasser entitled to a domestic connection as Art. 21; 4.4 rejection for want of ownership proof quashed; connection directed. Followed in SCJ-409 (remit).
- **SCJ-411** (Abdul Jabbar): Lok Adalat bill-correction award is not answered by Clause 6.5. s.22-A LSAA (supply of power is a public utility service); licensee directed to comply forthwith. First live stencil FP; rewritten; GRANT veto now live.
- **SCJ-430** (Akriti Food): Clause 5.6(e) check-meter clock (7–15 days) is mandatory; order passed four days after installation set aside.

## 5. Git

Branch `claude/supply-code-jurisprudence-design-yiwgen`. One commit per case, then push. Pipeline/docs commits are separate. No PR unless asked. Working copy can be any folder: `git pull` then run the loop; GitHub is the queue (`input/`) and the archive (`processed/` + JSON + digest PDFs).

## 6. File map

| Path | What |
|---|---|
| `NEXT.md` | **Trigger card.** User said “next” → follow this. |
| `../tools/run_next_case_loop.ps1` | Windows unattended loop: `-Count N -Workers 2`. Wrapper around `run_next_case_workers.py`. |
| `../tools/run_next_case_loop.sh` | Ubuntu unattended loop: `--count N --workers 2`. Same Python orchestrator. |
| `../grok_chats/` | Grok transcripts, folders named `YYYY-MM-DD_HH-MM-SS`. Synced on SessionEnd. |
| `../tools/sync_grok_chats.py` | Copy live Grok sessions into `grok_chats/` and optionally `git push`. |
| `../tools/run_next_case_workers.py` | Parallel orchestrator: N grok workers, serial claim + finalize. |
| `../tools/scj_queue.py` / `scj_lock.py` | Per-case tickets + directory lock. |
| `../tools/prepare_next_scj.py` | Pick next unique PDF, reserve id, skip dups, extract, set `authoring` (`stencil`/`short`/`full`). |
| `../tools/scj_stencil.py` | Zero-LLM JSON for proved families. `--dry-run` scores extracts. `--write` fills JSON. |
| `../tools/tally_outcomes.py` | Count records by `outcome`, optional provision filter (`UP-2005::4.4`). |
| `../tools/finalize_scj.py` | After JSON: PDF, state, index, catalog, git. Do not do this by hand. |
| `../tools/prompts/next_case_once.txt` | Full authoring prompt. |
| `../tools/prompts/next_case_short.txt` | Short authoring prompt (pages ≤ 2 or words ≤ 800, or uncited pages ≤ 3 / words ≤ 1500). |
| `../tools/log_scj_review.py` | Metrics for the SCJ-488–537 review. `--summary` after 50. |
| `sessions/2026-09-02-review-488-537.md` | **Review after this 50.** 6.8 stencil / BILL+RELEGATE cues / GRANT veto. |
| `sessions/2026-09-01-review-388-437.md` | Prior 50 (SCJ-388–437). GRANT veto came from here. |
| `sessions/2026-09-01-pipeline-review.md` | Prior 50 (SCJ-338–387). |
| `jurisprudence/catalog.txt` | Compact provision-key + principle-tag list. Generated. |
| `HANDOFF.md` | This file. |
| `RUNBOOK.md` | Lean-schema procedure (batch size, schema). |
| `sessions/2026-08-27.md` | Earlier chat: SCJ-273–282, loop + token-split. |
| `sessions/2026-08-27-grok.md` | This chat: digest fields, short path, SCJ-285…288. |
| `state/index.json` | filename → id + `next_seq`. |
| `summaries/json/`, `summaries/pdf/` | Leaves. |
| `jurisprudence/index.json` | Spine. Never hand-edit. |
| `jurisprudence/treatise/00-OUTLINE.md` | Treatise plan (later). |
| `input/` | Live PDF queue. |
| `processed/` | Progress marker. |
| `tools/extract_judgment.py`, `gen_scj.py`, `build_supply_code.py` | Pipeline. |

## 7. After the queue is empty

Rebuild index; skim what shifted; revisit the outline; then author the treatise once.

---

**One-line resume:** _536 cases done; input empty; treatise on hold; **next** or Windows `tools\run_next_case_loop.ps1 -Count 50 -Workers 2` / Ubuntu `./tools/run_next_case_loop.sh --count 50 --workers 2` = parallel JSON + serial PDF/git; one PC at a time; live stencil: 6.5 + **6.8-assessment-hearing** + contempt-6.5; BILL+RELEGATE cues (408/399/468/487); GRANT veto (SCJ-411); demote on stencil write fail; `citation_count` = max(IK, prose); listing-only off; `next_seq=537`._
