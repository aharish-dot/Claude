# Supply Code Jurisprudence — Session Handoff

> **Read this first in a fresh chat.** Strategic context + resume point.
> Mechanical procedure: **`RUNBOOK.md`**. One-command trigger: **`NEXT.md`**.
> Project rationale: **`README.md`**. Do not duplicate them.

_Last updated: 27 August 2026 — SCJ-001…288 processed. Digest now has page_count, significance, FACTUAL SUMMARY; limiting_facts dropped; short authoring path for ≤2 pages / ≤800 words. PDF+push still every case._

---

## 1. Where the project stands

- **288 judgments fully processed** → `SCJ-001` … `SCJ-288`. Lean JSON + digest PDF + folded into `jurisprudence/index.json`.
- **`state/index.json`**: `next_seq = 289`.
- **Spine** (after SCJ-288): 288 cases · 157 provisions · 254 principles · 443 authorities · 200 not-decided.
- **Treatise outline** exists (`jurisprudence/treatise/00-OUTLINE.md`); **all Parts still `todo`**. Treatise remains **ON HOLD** until the input queue is empty.
- **Branch**: `claude/supply-code-jurisprudence-design-yiwgen` (commit and push each case).
- **This machine is Windows.** Sources in the live queue are **PDFs in `supply-code/input/`**, not `html_input/`.

## 2. Governing decision (unchanged)

Process remaining judgments **first** (mechanical pipeline → index), **then** author the treatise **once** on the complete corpus. Do **not** write treatise Parts yet.

## 3. What the user will say

| User says | Do |
|---|---|
| **next** / **next case** / **now next one** | Process **exactly one** unique pending file. See **`NEXT.md`**. Do not ask. |
| *(unattended)* | `powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 100` from repo root. Each iteration is a fresh `grok -p`. Short vs full prompt is chosen from the ticket. |
| **next batch** | `RUNBOOK.md` default: up to 8, early-stop ~22k words. |
| Anything about the treatise / booklet Parts | Not yet, unless they explicitly override §2. |

**Immediate next:** run `python tools/prepare_next_scj.py`. `WRIC(A)_12303_2026.pdf` may still sit in `input/` = **SCJ-283** — retire as docket dup, no new id. After that, first unique is likely **`WRIC(A)_15707_2026.pdf`**. Skip `(1)` twins.

## 4. Gotchas a fresh session MUST know

### Duplicate / skip
- **`WRIC(A)_20210_2012.pdf`** still in `input/` = already **SCJ-273**. Skip; optionally move to `processed/`.
- **`WRIC(A)_12303_2026.pdf`** may still be in `input/` = already **SCJ-283**. Docket-dup retire; no new id.
- Files named `… (1).pdf` are Chrome/re-upload twins. Skip; move to `processed/` when the un-suffixed twin is processed (done for 11370). Remaining `(1)` twins: `15707_2026`, `15943_2026`, `21747_2026`.
- **Docket duplicate:** `WRIC(A)_10937_2026.pdf` = **SCJ-169** (Abhimanyu Singh, 9 Apr 2026). Retired to `processed/` without a new id. **Always grep docket + parties before assigning `SCJ-NNN`.**

### Windows pipeline (this checkout)

**User does nothing after starting it.** Chat **next** or the loop command both end in JSON + PDF + commit + **push** per case.

Token split:

1. `python tools/prepare_next_scj.py` — next unique PDF, skip dups, extract text → `tmp/NEXT_TICKET.json` (`authoring`, `catalog_hits`, `page_count`).
2. Grok authors **only** `summaries/json/SCJ-NNN.json`.
   - **Short path** if pages ≤ 2 **or** words ≤ 800 (`authoring=short`, `tools/prompts/next_case_short.txt`, `catalog_hits` on the ticket, max 15 turns). **Do not** load `catalog.txt` or SCJ-280.
   - **Full path** otherwise (`tools/prompts/next_case_once.txt` + catalog + SCJ-280).
   - Does not load this HANDOFF or `jurisprudence/index.json`.
3. `python tools/finalize_scj.py SCJ-NNN --source "<file>"` — schema gates, Chrome PDF (`--user-data-dir` required on Windows), state, spine, catalog, git commit+push. Loop re-runs finalize if the agent wrote JSON but skipped this step.

- PDF name: `SCJ-<NNN>_<slug>.pdf` — **no `_Digest`**.
- Do not commit `extracts/SCJ-*.txt` / `.fp.json`.
- Linux Chromium path (`/opt/pw-browsers/…`) does **not** apply here.

### Schema (still breaks `build_supply_code.py` if wrong)
- `cited_by` = string (`"Court"` / `"Petitioner"` / `"Respondent"`), never a list.
- `lead_authorities` = `[{name, docid}, …]`, never bare strings.
- `provision` = `CODE::clause` (never merge a Code clause into an Act section).
- `type`: `"supply_code"` | `"interplay"` | `"electricity_act"`.
- `page_count` = integer pages of the **source judgment** (fingerprint / input PDF). Digest PDF page 1 eyebrow: `SUPPLY CODE JURISPRUDENCE · SCJ-NNN · N PAGES · SIGNIFICANT`.
- `significance`: `"significant"` | `"ordinary"` | `"procedural"` (`normal` aliases ordinary). Required on new records; old records without it still render.
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

## 5. Git

Branch `claude/supply-code-jurisprudence-design-yiwgen`. One commit per case, then push. Pipeline/docs commits are separate. No PR unless asked.

## 6. File map

| Path | What |
|---|---|
| `NEXT.md` | **Trigger card.** User said “next” → follow this. |
| `../tools/run_next_case_loop.ps1` | Unattended loop: `-Count N` fresh `grok -p` sessions. Picks short vs full prompt from the ticket. |
| `../tools/prepare_next_scj.py` | Pick next unique PDF, skip dups, extract, set `authoring` + `catalog_hits`. |
| `../tools/finalize_scj.py` | After JSON: PDF, state, index, catalog, git. Grok must not do this by hand. |
| `../tools/prompts/next_case_once.txt` | Full authoring prompt. |
| `../tools/prompts/next_case_short.txt` | Short authoring prompt (pages ≤ 2 or words ≤ 800). |
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

**One-line resume:** _288 cases done; treatise on hold; **next** or `tools\run_next_case_loop.ps1 -Count 100` = JSON+PDF+push (short path if ≤2 pages or ≤800 words); `next_seq=289`; 12303 in `input/` is SCJ-283 (retire)._
