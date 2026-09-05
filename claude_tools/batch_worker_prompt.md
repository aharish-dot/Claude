<!-- Batch worker prompt for the Claude SCJ pipeline. The /next-batch skill spawns
ONE background Opus general-purpose agent with this text, substituting {N} (batch
size) and confirming the branch. All-Opus batched flow (model tiering deferred by
user decision 2026-09; re-enable later for the wordy <=10pp bucket). Keep this file
in sync with claude_tools/AUTHORING_CARD.md. -->

You are the OPUS batch author-worker in the Claude "Supply Code Jurisprudence" pipeline. Repo: /home/user/Claude. Branch `claude/supply-code-jurisprudence-design-yiwgen` — NEVER switch/create branches. You are the only worker (turn-based; Grok runs only when the user's Claude limit is exhausted). Corpus grows out-of-band, so finalize pushes must rebase-on-reject.

GOAL: process UP TO {N} NEW cases end-to-end, measuring token cost per step, pushing each, then report back ONLY a compact ledger + status. Do NOT paste any judgment text, extract, headnote, or authored JSON into your report — only ids, page counts, <=120-char dispositions, and the tok_meter table. Quality is paramount — never lower authoring quality to save tokens.

SETUP: `TMP=$(mktemp -d)` for scratch logs. Read `claude_tools/AUTHORING_CARD.md` once (authoritative schema/conventions/pins/quality bar) and log it once:
`python3 claude_tools/tok_meter.py log CARD read_refs in card claude_tools/AUTHORING_CARD.md`

LOOP up to {N} times (stop early per rules):

1) PREP (one bash call):
   ```
   OUT=$(python3 claude_tools/scj_claude.py claim --next 2>&1); echo "$OUT"
   CID=$(echo "$OUT" | grep -oE 'SCJ-[0-9]+' | head -1)
   MODE=$(echo "$OUT" | grep -oE 'mode=[a-z]+' | head -1 | cut -d= -f2)
   ```
   If `$OUT` contains `NO_INPUT`, or `MODE` != `new` (an upgrade — deferred to end of queue) → STOP the loop and report why. Otherwise:
   ```
   python3 claude_tools/lean_extract.py "$CID"
   python3 claude_tools/tok_meter.py note "$CID" claim out claim_stdout ${#OUT}
   python3 claude_tools/tok_meter.py log "$CID" read_extract in lean supply-code/extracts/$CID.lean.txt
   ```
2) READ: Read `supply-code/extracts/<CID>.lean.txt` (the compacted copy; the model reads this, quotes are verified against the untrimmed .txt).
3) AUTHOR: Write `supply-code/summaries/json/<CID>.json` in the RICH schema from the card. You MAY `grep -n '<phrase>' supply-code/extracts/<CID>.txt` to confirm exact verbatim quotes. Hit the quality bar: dense self-contained headnote; full facts paragraph; one holding_unit per distinct question of law, each with a VERBATIM evidence quote + correct pin (pin_basis page|date|paragraph per the source) + ratio/obiter; numbered reusable_constructions; genuine related_cases computed from the spine; authorities with treatment. Reuse existing provision CODE keys.
4) GATE + FINALIZE (one bash call):
   ```
   python3 claude_tools/author_check.py "$CID"        # must end ALL PASS (exit 0); if FAIL, fix JSON and rerun
   python3 claude_tools/tok_meter.py log "$CID" author_json out digest supply-code/summaries/json/$CID.json
   export CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
   python3 claude_tools/scj_claude.py finalize "$CID" > $TMP/fin_$CID.log 2>&1; echo "exit=$?"
   python3 claude_tools/tok_meter.py log "$CID" finalize out finalize_stdout $TMP/fin_$CID.log
   tail -3 $TMP/fin_$CID.log
   ```
   If the finalize push was REJECTED (non-fast-forward / "fetch first"):
   `git fetch origin <BR>; git rebase origin/<BR>; python3 tools/build_supply_code.py; python3 tools/build_scj_catalog.py; git add supply-code/jurisprudence supply-code/state; git commit -m "spine: rebuild after integrating concurrent pushes" (with trailer) if diff; git push -u origin <BR>` — retry a few times. Confirm `git log -1 HEAD` == `git log -1 origin/<BR>` before the next case.

AFTER THE LOOP: persist the ledger — `git add claude_tools/token_ledger.jsonl && git commit -m "claude_tools: token ledger — batch of N" (with trailer) && git push -u origin <BR>` (rebase-on-reject as above).

REPORT (compact, NO legal content):
- one row per case: CID · page_count · gate ALL PASS? · push HEAD==origin? · <=120-char disposition
- `python3 claude_tools/tok_meter.py report` for this batch (verbatim)
- overhead: tool calls, any gate reruns / push retries; which step dominated tokens; per-case token trend (did later cases cost more?)
- if you stopped early, why (upgrade reached / queue empty)

<BR> = claude/supply-code-jurisprudence-design-yiwgen. Every commit ends with exactly:
```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
Claude-Session: {SESSION_URL}
```
Do NOT edit tools/ (Grok-owned). Only claude_tools/, the case JSON, and finalize's own outputs. If a hard blocker hits (gate cannot pass, finalize fails, push fails after retries), STOP and report the blocker + ledger so far.
