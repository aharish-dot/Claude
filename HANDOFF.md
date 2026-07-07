# Judgment-Digest Pipeline — Session Handoff

*Written at the end of a long session so a fresh chat can continue with no re-derivation.*
*If you're the next session: `git pull` this branch, then read this file and `tools/PLAYBOOK.md`.*

---

## 0. Start here (next session, first actions)
1. Work on branch **`claude/court-judgements-summary-x1rbai`** — this is the repo's **default** branch and where **everything** lives and where the user looks. `git fetch origin claude/court-judgements-summary-x1rbai && git checkout claude/court-judgements-summary-x1rbai && git pull`.
   - The branch `claude/high-court-case-processing-ozvc13` is **vestigial** — ignore it.
2. Read `tools/PLAYBOOK.md` (esp. **§7 token discipline** and **§1 per-case flow**).
3. Latest commit at handoff: **`c0c638c`**.

## 1. What this project is
A pipeline that turns an Indian court judgment (High Court / Supreme Court, mostly from Indian Kanoon) into a committed, rendered **legal digest** (PDF + JSON + HTML), plus an incremental **authorities ledger**. Court-agnostic: `high-court/` and `supreme-court/` mirror each other.

## 2. Current durable state
- **Done:** HC-001 … **HC-005** (`high-court/state/index.json`, `next_seq=6`). **Supreme Court: none yet** (`SC-001` is next).
- Per case, committed: `extracts/<id>.{txt,fp.json,extract.json}`, `src/<id>.html`, `summaries/pdf/<id>_<slug>_Digest.pdf`, `summaries/json/<id>.json`; source moved to `<court>/processed/`.
- `high-court/state/authorities-ledger.json` — **15 authorities**, keyed by Indian Kanoon doc-id.
- **Both input queues are empty.** The location of a source (`input/` vs `processed/`) is the durable progress marker.
- The 5 HC cases are all UP/Gujarat **electricity-law** matters (theft/assessment under the Electricity Act 2003, §126/135, plus a §528 BNSS quashing and a bail-adjacent matter). HC-002 (Torrent Power) is the authority HC-001 cited — nice internal cross-reference.

## 3. How the pipeline works (per case)
Input goes into `high-court/input/` or `supreme-court/input/`. **Three input forms, all handled by `tools/extract_judgment.py` (it sniffs content, so file extension doesn't matter):**
- **Indian Kanoon doc-id or /doc/ URL** as the file's content (or an empty file named `<docid>.ik`) → **fetched via the IK API**.
- **HTML** (IK page saved as HTML — richest, keeps citation doc-ids).
- **MHTML** (Chrome "Webpage, Single File" / "Saved by Blink") — decoded automatically.
- **PDF** (searchable) — `from_pdf` self-installs PyMuPDF if missing.

Flow: `extract_judgment.py` (→ `<id>.txt` + `<id>.fp.json`) → **ONE Haiku sub-agent** reads `<id>.txt` and writes `<id>.extract.json` matching the golden schema `high-court/extracts/HC-001.extract.json`, ending with an **evidence block** (verbatim quotes) → `python tools/verify.py <court> <id>` **must print PASS (0 problems)** + grep-confirm the evidence quotes → `tools/gen_hc.py` + `tools/gen_hc_json.py` + render via `tools/render2.js` (`NODE_PATH=/opt/node22/lib/node_modules/playwright/node_modules`, pass court_short + scope) → `git mv` source to `processed/` → update `index.json` + `python tools/update_ledger.py <court> <id>` → **commit per case** → push.

**Never read a full judgment into the main context** — always via the throwaway Haiku sub-agent (PLAYBOOK §7). Key tools: `extract_judgment.py`, `verify.py`, `gen_hc.py`, `gen_hc_json.py`, `update_ledger.py`, `render2.js`.

## 4. Automation (all built and configured)
- **Routine** `trig_01AaNkXtjbtJAw6R2hYYK8q3` ("HC/SC judgment-digest auto-processor"): fresh cloud session per fire; **daily 06:00 UTC cron** (safety net) + **API trigger** + **push notifications**. Its saved prompt is the full autonomous pipeline spec. (Editable only in the claude.ai UI — `update_trigger` can't change the prompt, and recreating it would change the id and break the workflows + the API token.)
- **`.github/workflows/on-input-push.yml`** — on a push that **adds** a file to `*/input/**`, `curl`s the Routine's `/fire` endpoint (secret `CLAUDE_ROUTINE_TOKEN`). This is the "drop a case → it processes" trigger. Proven working end-to-end.
- **`.github/workflows/resume-pending.yml`** — every 2h on **free CI**, if any case <48h old is still pending in `input/`, `/fire`s the Routine to **resume**. Self-heals after an interrupted / usage-limited run. Idle = free; Claude budget spent only when work is pending.
- **User-side config already done:** environment **Network access = Full**; env var **`IK_API_TOKEN`** = the IK API key; GitHub secret **`CLAUDE_ROUTINE_TOKEN`** = the Routine's API token.
- **How the user submits (minimum friction):** bookmark `https://github.com/aharish-dot/Claude/new/claude/court-judgements-summary-x1rbai/high-court/input` → new file, name = doc-id, content = the IK link → Commit. Or upload an HTML/MHTML/PDF to the same folder.

## 5. ⚠️ THE open problem — read this
**The autonomous Routine has not yet been *observed* to complete a fresh case end-to-end on its own.** Every digest so far (HC-002…HC-005) was produced by me **interactively**. Routine firings have either correctly no-op'd (empty queue) or failed on causes now fixed:
- Run on an MHTML upload → **failed** (parser didn't decode MHTML) → **fixed**.
- Run on the first doc-id → **failed** (`IK_API_TOKEN` not yet live in that session — timing) → token now set.
- A later firing left **zero trace** (no branch/commit/PR). User's hypothesis: **usage-limit exhaustion mid-run**. The new `resume-pending.yml` addresses *recovery*, but a clean autonomous completion still hasn't been witnessed.

**I cannot read a Routine's cloud-session transcript from inside a session** (no MCP tool/resource; the session URL is an authed app page). So diagnosing an autonomous failure needs the user to open it in the UI.

## 6. What I'd like to know / confirm at the start of the next chat
1. **Did an autonomous Routine run finally complete a case?** If one failed, please open **claude.ai/code/routines → "HC/SC judgment-digest auto-processor" → the run → its session**, and paste the **tail** (where it stopped / any error, and whether it got past `extract_judgment.py`, past the sub-agent, and to `git push`). This is the single thing I can't see myself.
2. **Is `IK_API_TOKEN` saved as an environment *variable*** (not only a GitHub secret)? The Routine's fresh sessions read it from the env. (Confirmed present in the interactive env; please confirm it's in the cloud-environment variable list.)
3. **Cadence prefs:** resume check is every 2h with a 48h give-up bound — keep, or change?
4. **One at a time or batches?** If batches, consider editing the Routine prompt (UI) to **push after each case** so a mid-batch death doesn't lose finished cases.
5. **Court routing:** currently the folder you drop into (`high-court` vs `supreme-court`) decides HC vs SC. Want **auto-detect** from the judgment so there's one drop spot?
6. **Anything to change in the digest format** (sections, styling, length)? Lock against `HC-001.extract.json` / the rendered PDFs.
7. **Supreme Court:** no SC case done yet — is an SC-001 coming? (SC has its own `supreme-court/` dirs + empty `state/index.json`.)

## 7. Gotchas & conventions
- **Fresh session per batch** — don't continue a long chat (this handoff exists for exactly that; long sessions degrade — I lost track of my own completed HC-005 near the end of this one).
- `verify.py` must PASS before any commit; also grep-confirm the sub-agent's evidence quotes against `<id>.txt`; patch any authority whose fingerprint doc-id the sub-agent dropped.
- Commit **per case**; push to `claude/court-judgements-summary-x1rbai` only; **do not open PRs**; retry pushes with backoff.
- `[skip ci]` on housekeeping commits so they don't fire the workflow.
- Model: this session ran as `claude-opus-4-8`; the Routine's extract sub-agent uses **Haiku** (cheap; the verify gate protects quality).
- Suggested kickoff prompt for the next chat:
  > Continue the judgment-digest pipeline on branch `claude/court-judgements-summary-x1rbai` (git pull first). Read `HANDOFF.md` and `tools/PLAYBOOK.md`. Then <answer the questions in HANDOFF §6 / process the next case in input/>.
