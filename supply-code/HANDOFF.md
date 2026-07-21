# Supply Code Jurisprudence — Session Handoff

> **Read this first in a fresh chat.** It gives the strategic context, current state, and the
> immediate next task. For the mechanical per-batch procedure, this file defers to
> **`RUNBOOK.md`** (authoritative) and **`README.md`** (project rationale). Don't duplicate them.

_Last updated: end of the session that finished the first 151 cases + wrote the treatise outline._

---

## 1. Where the project stands (as of this handoff)

- **151 judgments fully processed** → `SCJ-001` … `SCJ-151`. Each has a lean JSON record
  (`summaries/json/`), a rendered digest PDF (`summaries/pdf/`), and is folded into the
  machine-generated spine (`jurisprudence/index.json`).
- **`state/index.json`**: `next_seq = 152`, 151 cases marked `done`.
- **Index spine stats**: 151 cases · 114 provision-keys · 139 principle-keys · 330 authorities
  · 77 open questions.
- **Treatise outline written and committed**: `jurisprudence/treatise/00-OUTLINE.md` — the
  master plan for the authored booklet (10 Parts + appendices, with a BUILD TRACKER). **All
  Parts are `todo`.** The treatise is deliberately **ON HOLD** (see §2).
- **Branch**: `claude/supply-code-jurisprudence-design-yiwgen`. All work committed and pushed.
- **`html_input/` is empty.** Every source judgment received so far has been processed.

## 2. The decision that governs the next phase (IMPORTANT)

The user has **112 more Supply Code judgments** to add. We deliberated sequencing and chose:

> **Process all 112 new judgments FIRST (mechanical pipeline → index), THEN author the treatise
> ONCE on the complete ~263-case corpus.**

**Do NOT start writing the treatise Parts yet.** Reason (agreed with the user): the authored
synthesis is the expensive, write-once work; 112 cases is ~43% of the eventual corpus and will
likely refine/qualify doctrine (as SCJ-054's IBC qualification already did to the arrears
line), so a booklet written on 151 would need a costly rewrite. The outline already captures
the structural "scaffold" benefit at low cost. Ingest everything, let `index.json` settle,
then write the treatise once.

**So the immediate job for the next several sessions = process the 112, batch by batch,
exactly like the first 151.** The treatise resumes only after the queue is empty again.

## 3. Your immediate next task in a fresh chat

1. **Check for the new judgments.** The user will upload the 112 (as `.html`/`.mht`/PDF, or
   Indian Kanoon doc-ids). Expect them in `supply-code/input/` and/or a refilled
   `supply-code/html_input/`. If nothing new is there yet, ask the user to upload the next
   drop.
2. **Process a batch** following `RUNBOOK.md` (8 cases/run, early-stop ~22k words). The user's
   shorthand **"next batch"** = do exactly that: read → draft lean JSON → `gen_scj.py` →
   chromium PDF → `git mv` sources to `processed/` → update `state/index.json` → rebuild index
   → commit → push.
3. Continue until the queue is empty, then hand back for the treatise phase.

## 4. Loose ends / gotchas a fresh session MUST know

- **`input/` currently holds 29 `.mht` files — these are ALREADY-PROCESSED twins**, not new
  work. (In the last several batches the `.html` from `html_input/` was processed and moved,
  but the `.mht` twin in `input/` wasn't retired.) **Do not mistake them for the 112.** They
  correspond to cases already in `summaries/json/`. Optional cleanup: `git mv` them to
  `processed/` to keep `input/` clean; otherwise ignore. The 112 NEW judgments are a separate,
  not-yet-uploaded drop.
- **No cases are being held back anymore.** The old standing instruction *"leave Thomas Joseph
  for the end"* is **discharged** — Thomas Joseph was processed as **SCJ-147** (it became the
  richest record in the corpus). There are no skip-lists in effect.
- **PDF naming actually used** = `SCJ-<NNN>_<slug>.pdf` where `slug` = title with
  `[^A-Za-z0-9]→_`, squeezed, cut to 60 chars, trailing `_` stripped. (Note: RUNBOOK §"done"
  mentions a `_Digest` suffix — the 151 existing files do **not** use it; match the existing
  files, i.e. **no `_Digest`**, for consistency.)
- **Chromium binary**: `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`
  (`--headless=new --no-sandbox --no-pdf-header-footer --print-to-pdf=<out.pdf> file://<abs.html>`).
- **`gen_scj.py` interface**: `python3 tools/gen_scj.py <record.json> <out.html>`.
- **Rebuild spine after every batch**: `python3 tools/build_supply_code.py` (writes
  `jurisprudence/index.json`; **never hand-edit** that file).

### Schema gotchas learned the hard way (avoid these — they broke `build_supply_code.py` before)
- In `authorities[]`, **`cited_by` must be a plain STRING** (`"Court"` / `"Petitioner"` /
  `"Respondent"`), **never a list**.
- In `principle_tags[]`, **`lead_authorities` must be a list of `{"name":…, "docid":…}`
  OBJECTS**, never bare strings.
- **`type`** on each holding-unit: `"supply_code"` for a State-Code clause, `"interplay"` for a
  companion Act provision (s.126/127, s.56(2), tariff ss.61/62, etc.), `"electricity_act"` was
  also used for Act-section-primary holdings — keep consistent with neighbours.
- **`provision` keys**: `CODE::clause` — never merge a Code clause into an Act section
  (`UP-2005::6.8`, `EA2003::126`, `WB-2004::5.2`, `IEA1910::26(6)`, `NIACT::138-…`).
- **OFFTOPIC convention**: peripheral/no-Supply-Code-nexus cases are still recorded (the
  "master citation ledger" aim) but compactly, with a `flag` on the holding-unit explaining
  why it's recorded compactly. Bare procedural orders (adjournments etc.) get a one-line record
  with `provision: "OFFTOPIC::procedural-listing"`.
- **Always validate** each JSON with `python3 -c "import json; json.load(open(...))"` and
  run the two-line gotcha check (cited_by is str; lead_authorities entries are dicts) before
  rendering.

## 5. Git conventions (unchanged)

- Work on branch `claude/supply-code-jurisprudence-design-yiwgen`. Before pushing:
  `git fetch origin <branch>` and confirm remote is an ancestor of local (no divergence).
- Push with `git push -u origin <branch>`.
- Commit-message trailer: use the **`Co-Authored-By:` / `Claude-Session:` trailer your session's
  own environment specifies** (it is injected per-session — don't hardcode a name from this
  file). One commit per batch is fine.
- Only push to the designated branch. Don't open a PR unless the user asks.

## 6. Key file map (for orientation)

| Path | What it is |
|---|---|
| `supply-code/README.md` | Project rationale + schema philosophy. |
| `supply-code/RUNBOOK.md` | **Authoritative per-batch procedure.** Follow this to process cases. |
| `supply-code/HANDOFF.md` | This file — strategic context + resume point. |
| `supply-code/state/index.json` | filename→case_id map + `next_seq`. Update per batch. |
| `supply-code/summaries/json/SCJ-*.json` | The 151 lean records (the leaves). |
| `supply-code/summaries/pdf/` | Rendered digest PDFs. |
| `supply-code/jurisprudence/index.json` | Machine-generated spine (provision/principle/authority). Never hand-edit. |
| `supply-code/jurisprudence/treatise/00-OUTLINE.md` | The treatise plan + BUILD TRACKER (for the LATER authoring phase). |
| `supply-code/processed/` | Retired source judgments (the move = the progress marker). |
| `supply-code/input/`, `html_input/` | Incoming judgments. `input/` currently = 29 stale `.mht` twins only. |
| `tools/gen_scj.py`, `tools/build_supply_code.py`, `tools/extract_judgment.py` | The pipeline. |

## 7. When the 112 are done (the phase AFTER this one)

- Rebuild the index; skim the refreshed provision/principle/authority counts to see what
  shifted (new clusters, qualified doctrines).
- **Revisit `treatise/00-OUTLINE.md`** — adjust Parts/sub-sections for anything the 112
  reshaped — then author the treatise **once**, Part by Part, per the outline's conventions
  (inline SCJ-ID citations, paragraph pins, treatment tags, no new law, tensions surfaced not
  resolved). Tick the BUILD TRACKER boxes as each Part is committed.
- The optional early-value hybrid we discussed (authoring only the apex-anchored, saturated
  Parts — arrears/transferee, s.126-vs-135, Code-vires — before the rest) remains available if
  the user wants a partial deliverable sooner, but the default is: ingest all, then write once.

---

**One-line resume:** _151 cases done + treatise outline written; treatise on hold; next job =
ingest the 112 new judgments batch-by-batch per RUNBOOK.md (mechanical, "next batch"), starting
at SCJ-152; the 29 `.mht` in `input/` are stale twins, not the new drop._
