# Supply Code Jurisprudence — Session Handoff

> **Read this first in a fresh chat.** Strategic context + resume point.
> Mechanical procedure: **`RUNBOOK.md`**. One-command trigger: **`NEXT.md`**.
> Project rationale: **`README.md`**. Do not duplicate them.

_Last updated: 27 August 2026 — SCJ-273…282 processed; unattended loop + token-split (prepare → JSON → finalize) committed. PDF+push still happen every case._

---

## 1. Where the project stands

- **282 judgments fully processed** → `SCJ-001` … `SCJ-282`. Lean JSON + digest PDF + folded into `jurisprudence/index.json`.
- **`state/index.json`**: `next_seq = 283`.
- **Spine** (after SCJ-282): 282 cases · 157 provisions · 253 principles · 443 authorities · 186 not-decided.
- **Treatise outline** exists (`jurisprudence/treatise/00-OUTLINE.md`); **all Parts still `todo`**. Treatise remains **ON HOLD** until the input queue is empty.
- **Branch**: `claude/supply-code-jurisprudence-design-yiwgen` (commit and push each case).
- **This machine is Windows.** Sources in the live queue are **PDFs in `supply-code/input/`**, not `html_input/`.

## 2. Governing decision (unchanged)

Process remaining judgments **first** (mechanical pipeline → index), **then** author the treatise **once** on the complete corpus. Do **not** write treatise Parts yet.

## 3. What the user will say

| User says | Do |
|---|---|
| **next** / **next case** / **now next one** | Process **exactly one** unique pending file. See **`NEXT.md`**. Do not ask. |
| *(unattended)* | `powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 100` from repo root. Each iteration is a fresh `grok -p`. |
| **next batch** | `RUNBOOK.md` default: up to 8, early-stop ~22k words. |
| Anything about the treatise / booklet Parts | Not yet, unless they explicitly override §2. |

**Immediate next file:** `WRIC(A)_12303_2026.pdf` → **SCJ-283**.

~57 unique PDFs remain in `input/` after skipping twins (see §4).

## 4. Gotchas a fresh session MUST know

### Duplicate / skip
- **`WRIC(A)_20210_2012.pdf`** still in `input/` = already **SCJ-273**. Skip; optionally move to `processed/`.
- Files named `… (1).pdf` are Chrome/re-upload twins. Skip; move to `processed/` when the un-suffixed twin is processed (done for 11370). Remaining `(1)` twins: `15707_2026`, `15943_2026`, `21747_2026`.
- **Docket duplicate:** `WRIC(A)_10937_2026.pdf` = **SCJ-169** (Abhimanyu Singh, 9 Apr 2026). Retired to `processed/` without a new id. **Always grep docket + parties before assigning `SCJ-NNN`.**

### Windows pipeline (this checkout)

**User does nothing after starting it.** Chat **next** or the loop command both end in JSON + PDF + commit + **push** per case.

Token split (quality of the JSON unchanged):

1. `python tools/prepare_next_scj.py` — next unique PDF, skip dups, extract text → `tmp/NEXT_TICKET.json`
2. Grok authors **only** `summaries/json/SCJ-NNN.json` (full judgment + `catalog.txt` + example SCJ-280). Does not load this HANDOFF or `jurisprudence/index.json`.
3. `python tools/finalize_scj.py SCJ-NNN --source "<file>"` — schema gates, Chrome PDF (`--user-data-dir` required on Windows), state, spine, catalog, git commit+push. Loop re-runs finalize if the agent wrote JSON but skipped this step.

- PDF name: `SCJ-<NNN>_<slug>.pdf` — **no `_Digest`**.
- Do not commit `extracts/SCJ-*.txt` / `.fp.json`.
- Linux Chromium path (`/opt/pw-browsers/…`) does **not** apply here.
- First **live** run of this split has not been executed yet (only `-DryRun`).

### Schema (still breaks `build_supply_code.py` if wrong)
- `cited_by` = string (`"Court"` / `"Petitioner"` / `"Respondent"`), never a list.
- `lead_authorities` = `[{name, docid}, …]`, never bare strings.
- `provision` = `CODE::clause` (never merge a Code clause into an Act section).
- `type`: `"supply_code"` | `"interplay"` | `"electricity_act"`.
- `page_count` = integer pages of the **source judgment** (fingerprint / input PDF). Digest PDF page 1 eyebrow: `SUPPLY CODE JURISPRUDENCE · SCJ-NNN · N PAGES · SIGNIFICANT`.
- `significance`: `"significant"` | `"ordinary"` | `"procedural"` (`normal` aliases ordinary). Required on new records; old records without it still render.
- OFFTOPIC / thin orders still recorded, compactly, with a `flag`. Listing-only → `OFFTOPIC::procedural-listing`.
- Validate JSON + the two gotcha checks before `gen_scj.py`.

### Doctrinal notes from SCJ-273–282 (do not paper over)
- **SCJ-278** (Satish Kumar Bharti): s.135(1-A) 24-hour FIR + Clause 8.2 held **mandatory**; *Indresh Patel* (DB, directory) called **per incuriam**; follows *Varun Kumar Yadav* (SLP pending). Tension stays on the table. Statutory clock is from **disconnection**; Court used inspection-to-FIR gap.
- **SCJ-273**: possibility of theft ≠ actual theft; non-speaking assessment/appeal quashed.
- Clause 4.5(d) cluster now includes interlocutory **SCJ-282** (Tehsildar NOC + alt-route costing) beside SCJ-104/120/169.
- Contempt of a Clause 6.5 relegation: SCJ-275 (misconceived), SCJ-276 (infructuous on compliance).

## 5. Git

Branch `claude/supply-code-jurisprudence-design-yiwgen`. One commit per case, then push. No PR unless asked.

## 6. File map

| Path | What |
|---|---|
| `NEXT.md` | **Trigger card.** User said “next” → follow this. |
| `../tools/run_next_case_loop.ps1` | Unattended loop: `-Count N` fresh `grok -p` sessions. |
| `../tools/prepare_next_scj.py` | Pick next unique PDF, skip dups, extract text → `tmp/NEXT_TICKET.json`. |
| `../tools/finalize_scj.py` | After JSON: PDF, state, index, catalog, git. Grok must not do this by hand. |
| `jurisprudence/catalog.txt` | Compact provision-key + principle-tag list for reuse. Generated. |
| `HANDOFF.md` | This file. |
| `RUNBOOK.md` | Lean-schema procedure (batch size, schema). |
| `sessions/2026-08-27.md` | This chat: SCJ-273–282, then the loop + token-split. |
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

**One-line resume:** _282 cases done; treatise on hold; **next** or `tools\run_next_case_loop.ps1 -Count 100` = JSON+PDF+push per case (Grok writes JSON; finalize does the rest); next is `WRIC(A)_12303_2026.pdf` → SCJ-283._
