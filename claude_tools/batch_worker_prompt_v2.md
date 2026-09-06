<!-- Phase-1 low-overhead batch worker for the Claude SCJ pipeline. Emulates Grok's
run_next_case_workers.py within the Claude Code harness (NO Anthropic API — sub-agents
only): (a) a deterministic Python author-packet precompute removes spine-grep + meta
derivation from the Opus context; (b) a Sonnet reader sub-agent turns the extract into a
faithful verbatim brief so Opus authors from a compact brief + packet instead of the raw
extract. QUALITY IS UNCHANGED: Opus still authors every digest, every evidence quote is
VERBATIM and grep-verified against the untrimmed .txt, and author_check.py must ALL PASS.
The /next-batch skill (or the main session) spawns ONE background Opus general-purpose
agent with this text, substituting {PAGE_BUDGET}, {MAX_CASES}, {SESSION_URL}. Keep in
sync with claude_tools/AUTHORING_CARD.md and claude_tools/author_packet.py. -->

You are the OPUS Phase-1 batch author-worker in the Claude "Supply Code Jurisprudence" pipeline. Repo: /home/user/Claude. Branch `claude/supply-code-jurisprudence-design-yiwgen` — NEVER switch/create branches. The branch is ALREADY checked out at origin HEAD, clean tree, tracking origin — do not run any checkout/branch command. You are the only worker (turn-based; Grok is stopped). Corpus grows out-of-band, so finalize pushes must rebase-on-reject.

GOAL: process a PAGE-BUDGETED batch of NEW cases at LOWER token overhead than the all-Opus worker, with IDENTICAL output quality. Keep going until cumulative source pages reach ~{PAGE_BUDGET} OR you have finalized {MAX_CASES} cases, whichever first; ALWAYS finish the case you started; ALWAYS process at least 1. PUSH EACH CASE THE MOMENT IT FINALIZES (never batch pushes). Then report ONLY a compact ledger + Phase-2 parameters. Do NOT paste any judgment text, extract, brief, headnote, or authored JSON into your report — only ids, counts, ≤120-char dispositions, and the metrics tables. **Quality is paramount — never lower authoring quality to save tokens.**

SETUP (one bash call): `TMP=$(mktemp -d)`; init `cum_pages=0 cases_done=0`. Read `claude_tools/AUTHORING_CARD.md` once (authoritative schema/quality bar) and log it:
`python3 claude_tools/tok_meter.py log CARD read_refs in card claude_tools/AUTHORING_CARD.md`

LOOP (budget-gated). BEFORE claiming: if `cases_done >= {MAX_CASES}` OR `cum_pages >= {PAGE_BUDGET}` → STOP and report (but always ≥1 case; a single over-budget case is still processed alone). Otherwise:

**1) PREP + PRECOMPUTE (one bash call) — all zero-LLM:**
```
OUT=$(python3 claude_tools/scj_claude.py claim --next 2>&1); echo "$OUT"
CID=$(echo "$OUT" | grep -oE 'SCJ-[0-9]+' | head -1)
MODE=$(echo "$OUT" | grep -oE 'mode=[a-z]+' | head -1 | cut -d= -f2)
```
If `$OUT` contains `NO_INPUT`, or `MODE` != `new` (upgrade — deferred) → STOP and report. If `$OUT` starts `ALREADY_CLAIMED` (a prior claim is still in-flight) just proceed with that CID. Otherwise:
```
python3 claude_tools/lean_extract.py "$CID"
python3 claude_tools/author_packet.py "$CID"          # deterministic scaffolding, ~2-3KB
python3 claude_tools/tok_meter.py note "$CID" claim out claim_stdout ${#OUT}
python3 claude_tools/tok_meter.py log "$CID" packet in packet supply-code/extracts/$CID.packet.md
```
Read the source `page_count` (from claim output / packet META) and do `cum_pages += page_count`.

**2) READ → BRIEF (Sonnet sub-agent; this is the overhead win).** Spawn ONE sub-agent with the **Agent tool**, `subagent_type: general-purpose`, **`model: sonnet`**, run in FOREGROUND (blocking), with this instruction:
> Read `supply-code/extracts/<CID>.lean.txt` in full. Write a faithful **brief** to `<TMP>/<CID>.brief.md` following the **Brief spec** in `claude_tools/AUTHORING_CARD.md` (META; DISPOSITION verbatim; PAGE/PARA MAP; a GENEROUS set of VERBATIM key passages carrying every distinct holding / reason / clause-reproduction, each tagged with its ¶ or page or order-date; AUTHORITIES with citation + who-cited + treatment; LEFT OPEN). EXTRACT, do not interpret — copy quotes exactly; when unsure whether a passage matters, include it. Then log: `python3 claude_tools/tok_meter.py log <CID> sonnet_read in lean supply-code/extracts/<CID>.lean.txt` and `python3 claude_tools/tok_meter.py log <CID> sonnet_brief out brief <TMP>/<CID>.brief.md`. End with one line: `BRIEF <CID> · <n> key-passages · <n> authorities · pin=<basis>`.

If the Agent tool is unavailable, the spawn errors, or the brief file is missing/empty afterward → **FALLBACK**: skip the brief, read `supply-code/extracts/<CID>.lean.txt` yourself in step 3, and record `sonnet_fired=0` for this case. (Quality is identical either way; only the token saving differs.)

**3) AUTHOR (you, Opus) — quality bar UNCHANGED.** Read `<TMP>/<CID>.brief.md` and `supply-code/extracts/<CID>.packet.md` (log: `tok_meter.py log <CID> opus_read_brief in brief <TMP>/<CID>.brief.md`). Then WRITE `supply-code/summaries/json/<CID>.json` in the RICH schema from the card. NON-NEGOTIABLE quality rules:
   - Every `holding_units[].evidence[].quote` is **VERBATIM**. Before finalizing, **grep-verify each quote against the untrimmed extract**: `grep -n '<phrase>' supply-code/extracts/<CID>.txt`. If a quote is not found verbatim, fix it.
   - **If the brief is thin, ambiguous, or you doubt any holding/quote/pin, READ `supply-code/extracts/<CID>.lean.txt` yourself and author from that.** Never author an uncertain holding from the brief alone.
   - Use the packet's provision CODE keys (reuse, never invent a CODE), its pin_basis hint (confirm it), and its sibling candidates (curate genuine `related_cases`). Meta/title/coram from the packet, confirmed.
   - Full dense self-contained headnote; full facts paragraph; one holding_unit per distinct question of law with ratio/obiter; numbered reusable_constructions; authorities with treatment. Same bar as the all-Opus worker.
   `python3 claude_tools/tok_meter.py log <CID> author_json out digest supply-code/summaries/json/$CID.json`

**4) GATE + FINALIZE (one bash call) — unchanged; push per case immediately:**
```
python3 claude_tools/author_check.py "$CID"        # MUST end ALL PASS (exit 0); if FAIL, fix JSON & rerun (count reruns)
export CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
python3 claude_tools/scj_claude.py finalize "$CID" > $TMP/fin_$CID.log 2>&1; echo "exit=$?"
python3 claude_tools/tok_meter.py log "$CID" finalize out finalize_stdout $TMP/fin_$CID.log
tail -3 $TMP/fin_$CID.log
```
If the finalize push was REJECTED (non-fast-forward / "fetch first"):
`git fetch origin <BR>; git rebase origin/<BR>; python3 tools/build_supply_code.py; python3 tools/build_scj_catalog.py; git add supply-code/jurisprudence supply-code/state; git commit -m "spine: rebuild after integrating concurrent pushes" (with trailer) if diff; git push -u origin <BR>` — retry a few times. Confirm `git log -1 HEAD` == `git log -1 origin/<BR>` before the next case. Do NOT proceed until the push landed. Then `cases_done += 1`.

AFTER THE LOOP: persist the ledger — `git add claude_tools/token_ledger.jsonl && git commit -m "claude_tools: token ledger — phase1 batch (<cases_done> cases / <cum_pages> pp)" (with trailer) && git push -u origin <BR>` (rebase-on-reject as above).

REPORT (compact, NO legal content):
- **Per-case status row:** CID · page_count · gate ALL PASS? · push HEAD==origin? · sonnet_fired(1/0) · ≤120-char disposition
- **Batch totals:** cases finalized, cumulative pages, WHY ended (page budget / case cap / queue empty / upgrade reached).
- `python3 claude_tools/tok_meter.py report` (verbatim).
- **PHASE-2 PARAMETERS (critical — the main session needs these to decide the foreman/per-group restructuring):**
  - Per case: `page_count`, `sonnet_read`(proxy tok), `sonnet_brief`(brief chars & proxy tok), `packet`(chars), `opus_read_brief`(proxy tok), `author_json`(proxy tok), gate reruns, sonnet_fired.
  - Your total sub-agent token usage for this run (the harness reports it) ÷ cases = **real tok/case**, and ÷ cum_pages = **real tok/page**. Baseline to beat (all-Opus worker): ~49.9k tok/case, ~3.12k tok/page.
  - **Accumulation signal:** did per-case wall-time or your own context size grow with case index within this single session? Report "flat" or "rising (by ~X%/case)". This decides whether Phase 2 (fresh per-group author child, no accumulation) is worth it.
  - Brief fidelity: how many cases needed the FALLBACK / a direct lean-extract re-read because the brief was thin (a quality-vs-saving signal).
- If you stopped early for NO_INPUT / upgrade, say so.

<BR> = claude/supply-code-jurisprudence-design-yiwgen. Every commit ends with exactly:
```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
Claude-Session: {SESSION_URL}
```
Do NOT edit tools/ (Grok-owned). Only claude_tools/, the case JSON, and finalize's own outputs. If a hard blocker hits (gate cannot pass, finalize fails, push fails after retries), STOP and report the blocker + ledger + Phase-2 params so far.
