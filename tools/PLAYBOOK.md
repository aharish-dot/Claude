# Judgment Digest Pipeline — Playbook (High Court & Supreme Court)

Standing procedure for turning an uploaded judgment into a committed digest. It is
**court-agnostic**: substitute `high-court` or `supreme-court` for `<COURT>` throughout.
Any fresh session — including an unattended overnight Routine run — can execute this end to
end from repo state alone. Nothing here depends on Google Drive or any external fetch.

---

## Kickoff — how to start a fresh chat on this

**First, make sure the new session is on the branch that holds this pipeline:**
`claude/court-judgements-summary-x1rbai` (the tools and queue are NOT on the default branch).
When creating the Claude Code session, pick that branch; or make it the new chat's first action:
`git fetch origin claude/court-judgements-summary-x1rbai && git checkout claude/court-judgements-summary-x1rbai && git pull`

**Then paste this prompt** (edit the court and the batch size):

> Work on branch `claude/court-judgements-summary-x1rbai` (git pull first). Follow
> `tools/PLAYBOOK.md` for the **high-court** set: process the next **3** files in
> `high-court/input/` (skip `README.md`). For each case, launch **one sub-agent** to read the
> full judgment in its own context and write `high-court/extracts/<id>.extract.json` matching
> the schema of `high-court/extracts/HC-001.extract.json` — **do not read judgments into your
> own context.** Then run `python tools/verify.py high-court <id>`, `python tools/gen_hc.py`,
> render with `tools/render2.js` (pass the court name + scope), `git mv` the source PDF/HTML to
> `high-court/processed/`, update `high-court/state/index.json`, commit per case, and push at the end.

Swap `high-court` → `supreme-court` for that set. A shorter version also works once the session
has read this file: *"Follow tools/PLAYBOOK.md, process the next 3 in high-court/input."*

---

## 0. Orient
- `git pull`.
- **Pending work = files in `<COURT>/input/`** (ignore `README.md` and `.gitkeep`).
- Shared tools in `tools/`. Per-court state in `<COURT>/state/`.
- The location of a source file (`input/` vs `processed/`) is the durable progress marker.

## 1. Per-case flow — one file at a time
1. Pick the next file in `<COURT>/input/` (sorted; a numeric prefix like `01-` forces order).
2. **Assign / look up** its case id in `<COURT>/state/index.json` (`HC-0NN` / `SC-0NN`,
   sequential, stable — reuse if the filename is already indexed).
   **Idempotency / duplicate guard — do this FIRST, before assigning any id:** if the input
   file's basename already appears in `index.json` with `status:"done"` (an identical case was
   already processed and its source now lives in `processed/`), it is a re-upload. `git rm` it
   from `input/` and skip it — do NOT assign a new id or regenerate a digest. Only genuinely new
   filenames are processed. (This makes re-uploads and repeated auto-runs safe no-ops.)
3. **Pre-parse (deterministic, no LLM):**
   `python tools/extract_judgment.py "<input>" <COURT>/extracts <caseid>`
   → writes `<caseid>.txt` (clean text) and `<caseid>.fp.json` (raw fingerprint: citations
   with Indian Kanoon doc-ids, cause title, court, coram, sections, counts). Handles HTML and PDF.
4. **Deep-extract (ONE Haiku sub-agent per case, throwaway context — prompt in §2):**
   reads `<caseid>.txt`, writes `<COURT>/extracts/<caseid>.extract.json` (structured digest content).
   One judgment per sub-agent — never batch (batching truncates on long orders).
5. **Verify (§3) — nothing proceeds unverified.**
6. **Generate** the digest HTML from the extract JSON (main thread) and render to
   `<COURT>/summaries/pdf/<caseid>_<slug>.pdf` via `tools/render2.js` (or `render_all.js` for batches).
7. Write `<COURT>/summaries/json/<caseid>.json`; **append this case's authorities to
   `<COURT>/state/authorities-ledger.json`** (keyed by doc-id).
8. `git mv "<input>" <COURT>/processed/`; set the case `status:"done"` in `state/index.json`.
9. **Commit:** `<caseid> <short cause title>: digest + extract`.
10. After a batch: rebuild the four compilations (`tools/build_merged.py`, court-parameterised)
    and `git push`.

## 2. Sub-agent deep-extract prompt (per case)
> You are extracting one court judgment into strict JSON for a legal digest. Read the file
> `<caseid>.txt` in full. Output ONLY a JSON object with these keys:
> `cause_title, court, coram (list of judges), nature_of_proceeding (e.g. "Criminal appeal
> u/s 374 CrPC"), sections_in_issue[], issues[] (numbered points for determination),
> facts (2–4 short paras), reasoning_by_issue[] (each: {issue, holding, reasoning}),
> authorities[] (each: {docid, name, citation, treatment ∈
> {followed, distinguished, overruled, referred, relied-on, doubted}, proposition, paras}),
> ratio (the binding ratio decidendi), obiter[] (notable obiter), disposition
> (allowed / dismissed / partly allowed / remanded, + relief), significance[] (each:
> {point, explanation}).
> Rules: cite paragraph numbers where possible; use ONLY authorities actually discussed in the
> text (match the doc-ids already listed in `<caseid>.fp.json`); never invent a citation or a
> holding; if something is unclear or absent, use null / "not stated" rather than guessing.

## 3. Verification checklist (before commit)
- Every `authorities[].docid` in the extract exists in `<caseid>.fp.json` (grep the source).
- `coram`, `nature_of_proceeding`, and `disposition` each appear (in substance) in `<caseid>.txt`.
- Every section in `sections_in_issue` is present in the text.
- No judge or party name has leaked into the authorities list (a recurring Haiku error).
- Spot-check one `treatment` label against its cited paragraph in the source.
- Assessment/relief figures, if any, match the text.

## 4. HC / SC digest format (extends the Delhi DC format)
The DC digest sections (title, docket, charge, facts, reasoning-with-blue-lead-ins, headnote,
interpretation, held, significance, citations) **plus**:
- **Docket:** Bench / Coram; Nature of proceeding (+ provision); appeal-from / posture.
- **Issues / Points for Determination:** numbered.
- **Reasoning:** organised issue-by-issue.
- **Table of Authorities:** adds a **Treatment** column (followed / distinguished / overruled /
  referred / relied-on / doubted) — not just "relied on".
- **Ratio vs Obiter:** stated separately.
- **Disposition:** the operative order.
- Compilations gain a treatment dimension and group authorities by how they were treated.
> Lock the exact look against the FIRST sample digest before any bulk run.

## 5. Overnight Routine (only when armed)
- A scheduled trigger fires a **fresh session** with: *"Execute `tools/PLAYBOOK.md` for
  `<COURT>`: process the next N files in `input/`, verify and commit each, `git mv` to
  `processed/`, stop when `input/` is empty or the token budget is low, then push and post a
  summary."*
- Fresh session per fire = lean context. Self-heals across session limits because the queue
  lives in `input/`. If the account is limited, a firing simply no-ops; the next one resumes.
- **It never runs unless explicitly armed.** Disarm any time by disabling the trigger.

## 6. Reusable assets in `tools/`
- `extract_judgment.py` — deterministic HTML / MHTML / PDF → text + citation fingerprint. Also
  accepts an Indian Kanoon **doc-id or /doc/ URL** (as file content, or an empty `<docid>.ik`
  file) and fetches the judgment via the IK API — needs `IK_API_TOKEN` in the env + network to
  `api.indiankanoon.org`. So a "link file" flows through the normal pipeline like any upload.
- `render2.js`, `render_all.js`, `render3.js` — HTML → PDF (Chromium).
- `digest.css` — shared stylesheet.
- `gen_08_11.py`, `gen_abet.py`, `build_merged.py`, … — DC generators to adapt for HC/SC.
- `verify.py` — deterministic extract check; run before every commit (PASS = 0 problems).
- `gen_hc.py` — HC/SC extract JSON → digest HTML.
- `gen_hc_json.py` — HC/SC extract JSON → clean, HTML-stripped `summaries/json/<caseid>.json`.

## 7. Token discipline — run lean every time
Each turn re-sends the system prompt **and** all prior tool output, so cost ≈ Σ over turns of
(fixed overhead + accumulated context). The two levers that dominate are **fewer turns** and a
**small accumulated context**. The `verify.py` gate means none of the below trades away quality.

- **Keep the judgment out of the main thread.** Exactly one sub-agent reads `<caseid>.txt`, in
  its own context — use **Haiku** (a failed extract is caught by verify and re-run cheaply).
  Never `grep`/`cat` judgment paragraphs into your own context: that text then re-bills on every
  later turn and defeats the whole point of the sub-agent.
- **Verify from evidence, not dumps.** Make the sub-agent end with a short *evidence block* —
  paragraph numbers + one-line quotes for coram, disposition, and each authority's treatment.
  Then confirm with `grep -c` / line numbers (presence only); avoid wide `grep -in -A/-B`
  paragraph dumps into the main thread.
- **Batch independent checks** (orient, env probe, structural counts) into one shell call —
  fewer round-trips means fewer re-billed turns.
- **Don't re-read generated files.** `verify.py` + one targeted count validates the extract;
  do not read the whole `.extract.json` back in. Edit/Write already report success.
- **Don't fan out exploratory searches.** If the target branch/folder/intent is unclear, ask
  one question — do not sweep Drive or the repo. A single overflowing result re-bills for the
  rest of the session.
- **Confirm the destination branch first.** Outputs must land on the branch the user actually
  views (the pipeline / default branch). Verify the branch before rendering, not after — the
  common failure mode is a correct digest committed where the user never looks.
- **Amortise setup.** Toolchain dry-runs and environment probing are one-time (case 1 only);
  skip them for later cases in the same session.
- **Run batches in FRESH sessions — never continue an old chat.** Every turn re-bills the whole
  conversation history, so a lean case run inside a long session still pays for everything that
  came before it. The queue (`input/`) and progress marker (`processed/`) live in the repo, so a
  new session loses nothing — use the Kickoff block above. Batch 3–5 cases per fresh session,
  keep chat replies terse (detail belongs in commit messages), then stop.
