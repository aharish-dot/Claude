# Judgment-Digest Pipeline — Session Handoff

*Written at the end of a long session so a fresh chat can continue with no re-derivation.*
*If you're the next session: `git pull` this branch, then read this file and `tools/PLAYBOOK.md`.*

---

## 0. Start here (next session, first actions)
1. Work on branch **`claude/court-judgements-summary-x1rbai`** — this is where **everything** lives and where the user looks. `git fetch origin claude/court-judgements-summary-x1rbai && git checkout claude/court-judgements-summary-x1rbai && git pull`.
   - The branch `claude/high-court-case-processing-ozvc13` is **vestigial** — ignore it.
2. Read `tools/PLAYBOOK.md` in full (esp. **§7 token discipline**, **§2/§3 attribution rules**, and **§1 per-case flow**).
3. Latest commit at handoff: **`892f164`**.

## 1. What this project is
A pipeline that turns an Indian court judgment (High Court / Supreme Court, mostly from Indian Kanoon) into a committed, rendered **legal digest** (PDF + JSON + HTML), plus an incremental **authorities ledger**. Court-agnostic: `high-court/` and `supreme-court/` mirror each other, each with its own `state/index.json` and `state/authorities-ledger.json`. A separate `notes/` directory holds standalone **interpretive/editorial notes** (analysis that is not a case digest — see §7).

## 2. Current durable state
- **Done:** High Court **HC-001 … HC-007** (`high-court/state/index.json`, `next_seq=8`). **Supreme Court: SC-001, SC-002** (`supreme-court/state/index.json`, `next_seq=3`).
- Per case, committed: `extracts/<id>.{txt,fp.json,extract.json}`, `src/<id>.html`, `summaries/pdf/<id>_<slug>_Digest.pdf`, `summaries/json/<id>.json`; source moved to `<court>/processed/`.
- `high-court/state/authorities-ledger.json` — **18 authorities**. `supreme-court/state/authorities-ledger.json` — **11 authorities**. Both keyed by Indian Kanoon doc-id.
- **Both input queues are empty** (`high-court/input/` has only `README.md`; `supreme-court/input/` is empty). The location of a source (`input/` vs `processed/`) is the durable progress marker.
- The corpus is entirely UP/Gujarat/Karnataka/Orissa **electricity-law** matters (theft/assessment under Electricity Act §§126/135; captive-generation/open-access under Rule 3 of the Electricity Rules 2005; a §528 BNSS quashing). It is genuinely interconnected — **check the ledger before assuming a new authority is unseen**:
  - HC-001 ↔ HC-002 (Torrent Power is the authority HC-001 cites).
  - SC-001 affirms HC-006 (Kadodara/APTEL); HC-007 applies SC-001 and refers to HC-006.
  - **SC-002 is the origin case for the §126 (civil)/§135 (criminal) distinction that HC-001 already cited** (as "Distinguished") — HC-001's citation had a blank doc-id until SC-002 was processed and the id (`43074463`) was backfilled into it. When you process a new case, always check whether an already-committed case cites the same authority with a blank `docid` and backfill it (see §6).
- `notes/UQR-Proportionality-Note.pdf` — a standalone interpretive note (not a digest) on a real defect in the Unitary Qualifying Ratio from *Dakshin Gujarat* (SC-001). See §7 for why it exists and what it says; it went through two full wrong drafts before landing correctly — don't regenerate it from an earlier assumption, read the file itself.

## 3. How the pipeline works (per case)
Input goes into `high-court/input/` or `supreme-court/input/`. **Four input forms** now, three handled directly by `tools/extract_judgment.py` (it sniffs content, so file extension doesn't matter), one handled manually (§6):
- **Indian Kanoon doc-id or /doc/ URL** as the file's content (or an empty file named `<docid>.ik`) → **fetched via the IK API** by `extract_judgment.py` itself.
- **HTML** (IK page saved as HTML — richest, keeps citation doc-ids).
- **MHTML** (Chrome "Webpage, Single File" / "Saved by Blink") — decoded automatically.
- **PDF** (searchable) — `from_pdf` self-installs PyMuPDF if missing.
- **A case name / citation typed in chat, no file or doc-id given** — `extract_judgment.py` has no search capability; you look it up yourself first via the IK *search* API (not just the fetch API), confirm the match, then feed the resulting doc-id through the normal `<docid>.ik` path. Full recipe in §6.

Flow: `extract_judgment.py` (→ `<id>.txt` + `<id>.fp.json`) → **ONE Haiku sub-agent** reads `<id>.txt` and writes `<id>.extract.json` matching the golden schema `high-court/extracts/HC-001.extract.json` (also cross-check **`HC-007.extract.json`**, the worked example for attribution — see §5), ending with an **evidence block** (verbatim quotes) → `python tools/verify.py <court> <id>` **must print PASS (0 problems)** — if it can't even *parse* the JSON, see §6 for the usual cause — + grep-confirm the evidence quotes, obiter grounding, AND attribution (§5) → `tools/gen_hc.py` + `tools/gen_hc_json.py` + render via `tools/render2.js` (`NODE_PATH=/opt/node22/lib/node_modules/playwright/node_modules`, pass court_short + scope) → `git mv` source to `processed/` (if the input file was never `git add`ed yet, plain `git mv` fails with "not under version control" — just `mv` it and `git add` the destination, same net effect) → update `index.json` + `python tools/update_ledger.py <court> <id>` → **commit per case** → push.

**Never read a full judgment into the main context** — always via the throwaway Haiku sub-agent (PLAYBOOK §7). Key tools: `extract_judgment.py`, `verify.py`, `gen_hc.py`, `gen_hc_json.py`, `update_ledger.py`, `render2.js`, and `render_note.js` (for standalone notes, §7).

## 4. Automation (built earlier; status unconfirmed — see open items)
- **Routine** `trig_01AaNkXtjbtJAw6R2hYYK8q3` ("HC/SC judgment-digest auto-processor"): fresh cloud session per fire; daily cron + API trigger + push notifications.
- **`.github/workflows/on-input-push.yml`** — on a push that **adds** a file to `*/input/**`, `curl`s the Routine's `/fire` endpoint (secret `CLAUDE_ROUTINE_TOKEN`). Proven working end-to-end some sessions ago.
- **`.github/workflows/resume-pending.yml`** — every 2h, if any case <48h old is still pending in `input/`, `/fire`s the Routine to resume.
- **Every case actually processed so far (HC-001…HC-007, SC-001…SC-002) was done interactively, not autonomously.** The open question — *has the Routine ever completed a case unattended?* — has now gone **several handoffs without being re-verified**. Ask the user, or check `claude.ai/code/routines`, before relying on it. If it's still unconfirmed next time too, treat that itself as the answer and say so plainly rather than carrying the question forward a fourth time.

## 5. ⚠️ Two correctness incidents — read before extracting anything else
Both are fixed and guarded against in `tools/PLAYBOOK.md`; understand *why*, because the guard only works if it's actually followed.

**(a) Hallucinated obiter (SC-001).** The Haiku sub-agent invented a "Distinction from unauthorised use (§126) and theft (§135)" obiter point that does not appear anywhere in the Dakshin Gujarat judgment (grep-confirmed: zero hits). Fixed by removing it (`197d12f`). **Guard added:** PLAYBOOK §2 now requires a verbatim quote for every obiter item; §3 requires grep-confirming each obiter against `<caseid>.txt` and dropping anything with zero support.

**(b) Mis-attribution (HC-007).** The bigger issue. The HC-007 digest presented the Supreme Court's *Dakshin Gujarat* holdings — the 26%/51% thresholds, the Unitary Qualifying Ratio and its five worked illustrations, anti-gaming and weighted-average principles — as if the Karnataka High Court had originated them. It hadn't; the HC largely **quotes** Dakshin Gujarat and decides only a narrow question on top of it. The tell: an "interpretation" item was pinned to ¶29, which on inspection only *quotes the statutory definition* — no interpretation happens there at all. Root cause: treating "this paragraph is in the judgment" as equivalent to "this court is saying this," which is false whenever a judgment extracts, quotes, or reproduces someone else's text.
  - **Fixed** (`9124149`): HC-007 reworked into two clearly separated sections — **"Framework Applied — Reproduced from the Supreme Court"** (each item tagged `SUPREME COURT`, prefixed "Per the Supreme Court…, reproduced at ¶N") and **"This Court's Reasoning & Holding"** confined to what the Karnataka HC actually decided itself (¶45–49 only).
  - **Guard added** to `tools/PLAYBOOK.md` (`9346061`): §2 has an explicit "whose voice is it?" attribution rule with tell-tale phrases ("reads as under", "the Apex Court held", "according to the petitioners"); §3 requires opening the pinned paragraph and confirming the deciding court is speaking in its own voice there; §4 documents the reproduced-framework convention (`interp_heading`, the `.src`/`.src-sc`/`.src-hc` CSS tags in `gen_hc.py`, the settable `reasoning_heading`), with **HC-007's extract JSON pinned as the worked reference example**.
  - **Read `high-court/extracts/HC-007.extract.json` before your first extraction** — it's the template for how a "this case mostly applies a higher authority" digest should look.

**The standing lesson:** a pin (`¶ N`) only promises "this text is drawn from paragraph N." It does **not** by itself promise "paragraph N is this court speaking in its own voice," and — per §6 below — it doesn't even guarantee paragraph N is unambiguous within the file. Both are separate checks the sub-agent and the verify step have to make explicitly, every time.

## 6. SC-002 — lessons from a clean run
SC-002 (Executive Engineer, SOUTHCO v. Sri Seetaram Rice Mill) shipped with none of the errors in §5 — the guards held. Along the way this run surfaced four reusable techniques/gotchas worth knowing before your first case:

- **Finding a case from a name/citation alone.** The user gave a case name + SCC citation, no file, no doc-id. `extract_judgment.py` cannot search — it only fetches a known doc-id. Instead, hit the IK **search** endpoint directly with the same token: `curl -sS -X POST "https://api.indiankanoon.org/search/?formInput=<url-encoded query>&pagenum=0" -H "Authorization: Token $IK_API_TOKEN"`. Relevance is weak on generic multi-word queries (lots of noise); narrow to the most distinctive party-name fragment, and a `doctypes:supremecourt`-style filter helps. Before spending a sub-agent call, **fetch the candidate doc and manually confirm** its title/parties/coram/date match what the user gave. Once confirmed, drop the doc-id into an empty `input/<docid>.ik` file and run it through the *normal* pipeline (same `input/`→`processed/` lifecycle as any upload) — don't shortcut around `extract_judgment.py` once you have the id.
- **`verify.py` can fail to even parse the JSON**, not just fail its checks — Haiku occasionally mis-closes a long array (e.g. a `]` where a `}` was needed on the last object). The traceback gives an exact line number; open the file at that line and fix the one bracket rather than regenerating the whole extract.
- **A judgment can block-quote another case at such length that the quoted case's own paragraph numbers appear inline and collide with the citing judgment's numbering.** SC-002 has two unrelated "¶51"s in its raw text — the real one (about §126/§127), and one from an unrelated debt-recovery judgment it quotes for an interpretive canon. A pin is only trustworthy once you've confirmed which occurrence it resolves to. Fastest check: dump every paragraph marker in file order — `grep -noE '^[0-9]{1,2}\.' <id>.txt` — and read the sequence; a quote block shows up as a short run of numbers that breaks the monotonic count, and you can identify what's quoted from the sentence right before it (look for "held as under:", "stated the law thus:", etc.).
- **When a new case's doc-id becomes known, grep the corpus for existing citations of it with a blank `docid`** (it happened for HC-001's citation of SC-002) and backfill: update the citing case's `extract.json`, regenerate its `summaries/json` export, re-run `update_ledger.py` for it. `docid` isn't rendered in the visible PDF (purely a ledger/verification key), so this never requires a PDF re-render — just the JSON + ledger update.

## 7. `notes/` — standalone interpretive notes
Not every useful output is a case digest. If the user raises a substantive legal/analytical question and asks for a **separate PDF** rather than a change to a case digest, that's this second content type:
- Lives in `notes/<slug>.html` + `notes/<Slug>.pdf`, rendered via **`tools/render_note.js`** (sibling of `render2.js`; header reads "Interpretive Note · <scope>" instead of "<Court> · Judgment Digest" so it can't be mistaken for a case output). Uses the same `tools/digest.css`.
- Must open with a plain-language statement that it is **editorial commentary, not a court holding** (see the `.disp "Nature of this note"` box at the top of `UQR-proportionality-note.html` for the pattern).
- **This note went through two substantive wrong drafts before landing correctly** — read `notes/UQR-proportionality-note.html` in full before trusting it, and take it as a general caution: novel legal-arithmetic analysis is exactly the task where reading only part of the source produces a confident, wrong answer. Read the *entire* relevant passage before asserting how a formula is actually applied, not just the paragraph that states it. Also check that any example you lean on for support is truly analogous to the point being made, not just superficially on-topic — the second draft over-corrected by resting on a fact pattern the user pointed out didn't actually match.
- Current, correct content: the UQR operates as a **per-user consumption floor** (≥1.764% of generation per 1% of shareholding), correctly used to catch token-shareholder gaming. It **over-reaches** on a fact pattern the Court never illustrated: symmetric co-owners who clear both the 26%/51% aggregates, consume in exact proportion to ownership, over-consume relative to their own stake, and engage in no gaming — yet are disqualified because the per-user floor sums to more than the 51% Rule 3 treats as sufficient.
- If asked for another note like this: don't reuse the digest generator (`gen_hc.py`) or its "Judgment Digest" framing — build a bespoke HTML page in the digest house style and render with `render_note.js`.

## 8. Gotchas & conventions
- **Fresh session per batch** is still the recommendation, but if continuing a long session instead, the real risk isn't length — it's *not re-verifying claims against source text*. Re-read the actual judgment (or re-grep it) for anything you're about to assert; don't rely on your own earlier summary of it.
- `verify.py` must PASS before any commit; also grep-confirm the sub-agent's evidence quotes, obiter grounding (§5a), and attribution (§5b) against `<id>.txt`.
- Commit **per case** (or per logical fix); push to `claude/court-judgements-summary-x1rbai` only; **do not open PRs**; retry pushes with backoff (2s/4s/8s/16s).
- `[skip ci]` on housekeeping/PLAYBOOK-only commits so they don't fire the input-processing workflow.
- Never commit the Indian Kanoon API key — it lives only as the `IK_API_TOKEN` env var.
- Model identity (whichever model ran a given session) must never appear in commits, PRs, or repo artifacts — chat replies only.
- Commits end with `Co-Authored-By: Claude <...> <noreply@anthropic.com>` + a `Claude-Session:` trailer — match the format already in the git log, adjusted for whichever model is running.
- Suggested kickoff prompt for the next chat:
  > Continue the judgment-digest pipeline on branch `claude/court-judgements-summary-x1rbai` (git pull first). Read `HANDOFF.md` and `tools/PLAYBOOK.md` (esp. §5 on attribution — read `HC-007.extract.json` as the worked example — and §6 on finding/verifying a case from a citation alone). Then <process the next case in input/ / answer an open question below>.

## 9. Open questions for the user at the start of the next chat
1. **Has an autonomous Routine run ever completed a case unattended?** Unconfirmed across multiple handoffs now (§4). If still unconfirmed, say so plainly rather than re-asking a fourth time — it may be more useful to actually debug it than to keep carrying the question forward.
2. **More notes like `notes/UQR-Proportionality-Note.pdf`?** Now that the pattern exists (§7), is there an appetite for more interpretive/editorial analysis alongside the digest corpus, or was this a one-off?
3. **Any more cases queued?** Both `input/` folders are empty as of this handoff.
4. **Anything to change in the digest format** — the HC-007 provenance rework (§5b) added a new section type (`.src` tags, reproduced-framework heading); worth confirming the user likes the look before it becomes the default for every case that heavily cites a higher authority.
