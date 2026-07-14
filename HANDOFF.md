# Judgment-Digest Pipeline — Session Handoff

*Written at the end of a long session so a fresh chat can continue with no re-derivation.*
*If you're the next session: `git pull` this branch, then read this file and `tools/PLAYBOOK.md`.*

---

## 0. Start here (next session, first actions)
1. Work on branch **`claude/court-judgements-summary-x1rbai`** — this is where **everything** lives and where the user looks. `git fetch origin claude/court-judgements-summary-x1rbai && git checkout claude/court-judgements-summary-x1rbai && git pull`.
   - The branch `claude/high-court-case-processing-ozvc13` is **vestigial** — ignore it.
2. Read `tools/PLAYBOOK.md` in full (esp. **§7 token discipline**, **§2/§3 attribution rules** — new this session, see §5 below — and **§1 per-case flow**).
3. Latest commit at handoff: **`e67126f`**.

## 1. What this project is
A pipeline that turns an Indian court judgment (High Court / Supreme Court, mostly from Indian Kanoon) into a committed, rendered **legal digest** (PDF + JSON + HTML), plus an incremental **authorities ledger**. Court-agnostic: `high-court/` and `supreme-court/` mirror each other. A separate `notes/` directory holds standalone **interpretive/editorial notes** (analysis that is not a case digest — see §6).

## 2. Current durable state
- **Done:** High Court **HC-001 … HC-007** (`high-court/state/index.json`, `next_seq=8`). **Supreme Court: SC-001** (`supreme-court/state/index.json`, `next_seq=2`).
- Per case, committed: `extracts/<id>.{txt,fp.json,extract.json}`, `src/<id>.html`, `summaries/pdf/<id>_<slug>_Digest.pdf`, `summaries/json/<id>.json`; source moved to `<court>/processed/`.
- `high-court/state/authorities-ledger.json` — **17 authorities**, keyed by Indian Kanoon doc-id.
- **Both input queues are empty** (`high-court/input/` has only `README.md`; `supreme-court/input/` is empty). The location of a source (`input/` vs `processed/`) is the durable progress marker.
- The corpus is entirely UP/Gujarat/Karnataka **electricity-law** matters (theft/assessment under Electricity Act §§126/135; captive-generation/open-access under Rule 3 of the Electricity Rules 2005; a §528 BNSS quashing). It cross-links: HC-001↔HC-002 (Torrent Power is the authority HC-001 cites); SC-001 affirms HC-006 (Kadodara/APTEL); HC-007 applies SC-001 and refers to HC-006. This corpus is genuinely interconnected — check the ledger before assuming a new authority is unseen.
- `notes/UQR-Proportionality-Note.pdf` — a standalone interpretive note (not a digest) on a real defect in the Unitary Qualifying Ratio from *Dakshin Gujarat* (SC-001). See §6 for why it exists and what it says; it went through two full rewrites this session and the final version is correct — don't regenerate it from an earlier assumption.

## 3. How the pipeline works (per case)
Input goes into `high-court/input/` or `supreme-court/input/`. **Three input forms, all handled by `tools/extract_judgment.py`** (it sniffs content, so file extension doesn't matter):
- **Indian Kanoon doc-id or /doc/ URL** as the file's content (or an empty file named `<docid>.ik`) → **fetched via the IK API**.
- **HTML** (IK page saved as HTML — richest, keeps citation doc-ids).
- **MHTML** (Chrome "Webpage, Single File" / "Saved by Blink") — decoded automatically.
- **PDF** (searchable) — `from_pdf` self-installs PyMuPDF if missing.

Flow: `extract_judgment.py` (→ `<id>.txt` + `<id>.fp.json`) → **ONE Haiku sub-agent** reads `<id>.txt` and writes `<id>.extract.json` matching the golden schema `high-court/extracts/HC-001.extract.json` (also cross-check **`HC-007.extract.json`** — see §5, it's the worked example for attribution), ending with an **evidence block** (verbatim quotes) → `python tools/verify.py <court> <id>` **must print PASS (0 problems)** + grep-confirm the evidence quotes, obiter grounding, AND attribution (§5) → `tools/gen_hc.py` + `tools/gen_hc_json.py` + render via `tools/render2.js` (`NODE_PATH=/opt/node22/lib/node_modules/playwright/node_modules`, pass court_short + scope) → `git mv` source to `processed/` → update `index.json` + `python tools/update_ledger.py <court> <id>` → **commit per case** → push.

**Never read a full judgment into the main context** — always via the throwaway Haiku sub-agent (PLAYBOOK §7). Key tools: `extract_judgment.py`, `verify.py`, `gen_hc.py`, `gen_hc_json.py`, `update_ledger.py`, `render2.js`, and `render_note.js` (for standalone notes, §6).

## 4. Automation (built earlier; status unconfirmed — see open items)
- **Routine** `trig_01AaNkXtjbtJAw6R2hYYK8q3` ("HC/SC judgment-digest auto-processor"): fresh cloud session per fire; daily cron + API trigger + push notifications.
- **`.github/workflows/on-input-push.yml`** — on a push that **adds** a file to `*/input/**`, `curl`s the Routine's `/fire` endpoint (secret `CLAUDE_ROUTINE_TOKEN`). Proven working end-to-end as of the previous handoff.
- **`.github/workflows/resume-pending.yml`** — every 2h, if any case <48h old is still pending in `input/`, `/fire`s the Routine to resume.
- **Every case actually processed so far (HC-001…HC-007, SC-001) was done interactively, not autonomously.** The open question from the last handoff — *has the Routine ever completed a case unattended?* — was **not re-verified this session**. Ask the user, or check `claude.ai/code/routines`, before relying on it.

## 5. ⚠️ Two correctness incidents this session — read before extracting anything else
Both are now fixed, both are now guarded against in `tools/PLAYBOOK.md`, but the next session should understand *why*, because the guard only works if it's actually followed.

**(a) Hallucinated obiter (SC-001).** The Haiku sub-agent invented a "Distinction from unauthorised use (§126) and theft (§135)" obiter point that does not appear anywhere in the Dakshin Gujarat judgment (grep-confirmed: zero hits). Fixed by removing it (`197d12f`). **Guard added:** PLAYBOOK §2 now requires a verbatim quote for every obiter item; §3 requires grep-confirming each obiter against `<caseid>.txt` and dropping anything with zero support.

**(b) Mis-attribution (HC-007).** The bigger issue. The HC-007 digest presented the Supreme Court's *Dakshin Gujarat* holdings — the 26%/51% thresholds, the Unitary Qualifying Ratio and its five worked illustrations, anti-gaming and weighted-average principles — as if the Karnataka High Court had originated them. It hadn't; the HC largely **quotes** Dakshin Gujarat (its own paras 34–37, 43–47 reproduce the Supreme Court's paras 43–47 near-verbatim) and decides only a narrow question on top of it (whether KERC's Clause 6.7 could swap the Supreme Court's fixed qualifying-ratio benchmark for a dynamic one). The tell: an "interpretation" item was pinned to ¶29, which on inspection only *quotes the statutory definition* — no interpretation happens there at all. Root cause: the sub-agent (and I, reviewing it) treated "this paragraph is in the judgment" as equivalent to "this court is saying this," which is false whenever a judgment extracts, quotes, or reproduces someone else's text.
  - **Fixed** (`9124149`): HC-007 reworked so the digest now has two clearly separated sections — a **"Framework Applied — Reproduced from the Supreme Court"** section (each item tagged with a `SUPREME COURT` pill and prefixed "Per the Supreme Court…, reproduced at ¶N") and a **"This Court's Reasoning & Holding"** section confined to what the Karnataka HC actually decided itself (¶45–49 only).
  - **Guard added** to `tools/PLAYBOOK.md` (`9346061`): §2 has an explicit "whose voice is it?" attribution rule with tell-tale phrases to watch for ("reads as under", "the Apex Court held", "according to the petitioners"); §3 adds a verification step that requires opening the pinned paragraph and confirming the deciding court is speaking in its own voice there; §4 documents the reproduced-framework convention (`interp_heading`, the `.src`/`.src-sc`/`.src-hc` CSS tags in `gen_hc.py`, the settable `reasoning_heading`) with **HC-007's extract JSON pinned as the worked reference example**.
  - **Read `high-court/extracts/HC-007.extract.json` before your first extraction this session** — it's the template for how a "this case mostly applies a higher authority" digest should look.

**The lesson for whoever extracts next:** a pin (`¶ N`) currently only promises "this text is drawn from paragraph N of the judgment." It does **not** yet promise "paragraph N is this court speaking in its own voice" — that's a separate check the sub-agent and the verify step both have to make explicitly, every time, especially in any case that affirms/applies/follows a higher authority at length.

## 6. `notes/` — standalone interpretive notes (new this session)
Not every useful output is a case digest. The user raised a substantive legal question — a suspected flaw in the Unitary Qualifying Ratio formula from *Dakshin Gujarat* — and asked for a **separate PDF**, explicitly *not* touching any case digest. This is a new, second content type:
- Lives in `notes/<slug>.html` + `notes/<Slug>.pdf`, rendered via **`tools/render_note.js`** (sibling of `render2.js`; header reads "Interpretive Note · <scope>" instead of "<Court> · Judgment Digest" so it can't be mistaken for a case output). Uses the same `tools/digest.css`.
- Must open with a plain-language statement that it is **editorial commentary, not a court holding** (see the `.disp "Nature of this note"` box at the top of `UQR-proportionality-note.html` for the pattern).
- **This note went through two substantive wrong drafts before landing correctly** — worth reading `notes/UQR-proportionality-note.html` in full before trusting the final content, and worth taking as a caution generally: novel legal-arithmetic analysis (as opposed to summarizing what a judgment says) is exactly the kind of task where reading only part of the source (here, the Supreme Court's five worked illustrations at para 44) produces a confident, wrong answer. Read the *entire* relevant passage before asserting how a formula is actually applied, not just the paragraph that states it. The first draft was wrong because it hadn't read the illustrations at all; the second draft over-corrected by leaning on a fact-pattern (Illustration 5, a token-shareholder gaming case) that the user pointed out doesn't actually match the scenario under discussion — a reminder to check that an example is truly analogous, not just superficially on-topic, before resting an argument on it.
- Current final content (accurate, user-confirmed direction as of last message): the UQR operates as a **per-user consumption floor** (≥1.764% of generation per 1% of shareholding), correctly used to catch token-shareholder gaming (Illustration 5 in Dakshin Gujarat is a gaming case, not a counter-example — don't lean on it as if it were). It **over-reaches** on a distinct fact pattern the Court never illustrated: symmetric co-owners (e.g. two owners at 25%/25% consuming 30%/30%) who clear both the 26%/51% aggregates, split consumption in exact proportion to ownership, over-consume relative to their own stake, and engage in no gaming — yet are disqualified because the per-user floor sums to more than the 51% Rule 3 itself treats as sufficient. Karnataka HC (HC-007) did not reach this; it reaffirmed the fixed 1.96 baseline while deciding a different question (dynamic vs qualifying denominator).
- If the user asks for another note like this: don't reuse the digest generator (`gen_hc.py`) or its "Judgment Digest" framing — build a bespoke HTML page in the digest house style, same as this one, and render with `render_note.js`.

## 7. Gotchas & conventions
- **Fresh session per batch** recommended, but this session ran long and productively on follow-up correctness work — the risk isn't session length per se, it's *not re-verifying claims against source text*. If continuing a long session, still re-read the actual judgment text for anything you're about to assert, don't rely on your own earlier summary of it.
- `verify.py` must PASS before any commit; also grep-confirm the sub-agent's evidence quotes, obiter grounding (§5a), and attribution (§5b) against `<id>.txt`.
- Commit **per case** (or per logical fix); push to `claude/court-judgements-summary-x1rbai` only; **do not open PRs**; retry pushes with backoff (2s/4s/8s/16s).
- `[skip ci]` on housekeeping/PLAYBOOK-only commits so they don't fire the input-processing workflow.
- Never commit the Indian Kanoon API key — it lives only as the `IK_API_TOKEN` env var.
- Model identity (whichever model ran a given session) must never appear in commits, PRs, or repo artifacts — chat replies only.
- Commits end with `Co-Authored-By: Claude <...> <noreply@anthropic.com>` + a `Claude-Session:` trailer — match the format already in the git log, adjusted for whichever model is running.
- Suggested kickoff prompt for the next chat:
  > Continue the judgment-digest pipeline on branch `claude/court-judgements-summary-x1rbai` (git pull first). Read `HANDOFF.md` and `tools/PLAYBOOK.md` (esp. §5 on attribution — read `HC-007.extract.json` as the worked example before extracting anything). Then <process the next case in input/ / answer an open question below>.

## 8. Open questions for the user at the start of the next chat
1. **Has an autonomous Routine run ever completed a case unattended?** Not re-checked this session (§4). If the answer is still "no," the automation may need actual debugging rather than continued trust.
2. **More notes like `notes/UQR-Proportionality-Note.pdf`?** Now that the pattern exists (§6), is there an appetite for more interpretive/editorial analysis alongside the digest corpus, or was this a one-off?
3. **Any more cases queued?** Both `input/` folders are empty as of this handoff.
4. **Anything to change in the digest format** — the HC-007 provenance rework (§5b) added a new section type (`.src` tags, reproduced-framework heading); worth confirming the user likes the look before it becomes the default for every case that heavily cites a higher authority.
