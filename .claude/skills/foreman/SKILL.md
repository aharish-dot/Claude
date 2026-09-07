---
name: foreman
description: Low-overhead SCJ authoring pipeline that a FRESH main session runs directly (no Anthropic API needed — sub-agents only). The MAIN session acts as foreman: per case it runs Python claim (zero-LLM), spawns a Sonnet reader sub-agent to write a faithful verbatim brief, spawns a FRESH Opus author sub-agent to author the rich digest from that brief (grep-verifying every quote), then Python-finalizes and pushes. A fresh author child per case removes the cross-case context accumulation of the /next-batch background worker; quality is the SAME rich schema + author_check gate. Use when the user says "run foreman", "foreman batch", "/foreman", or wants to drain the SCJ queue at lower overhead than /next-batch. Optional args: a page budget (e.g. /foreman 90) or a case cap (e.g. /foreman cases=8).
---

# foreman — low-overhead SCJ authoring, orchestrated by the main session

`/next-batch` spawns ONE background Opus worker that authors every case of the batch
in a single, *accumulating* context (each case's extract + JSON stay resident and are
re-sent every turn). This skill removes that accumulation by making the **main session
the foreman**: it never reads a judgment itself — it delegates each case's *reading* to a
cheap Sonnet child and each case's *authoring* to a **fresh** Opus child, so no single
context carries more than one case. Output quality is unchanged (same RICH schema, same
verbatim-quote gate). Read `claude_tools/AUTHORING_CARD.md` once for the schema.

## Why the main session must be the foreman (do NOT delegate the loop)
A background/general-purpose sub-agent has **no Agent tool**, so it cannot spawn the
Sonnet reader or the fresh Opus author. Only the main session can. So YOU (the main
session) run the loop below directly. This is the one pipeline that authors from the
main window — but you still never read a judgment into your own context; the children do.

## Batch size — you decide; default 10 cases / ~75 source pages
- **Default: `{MAX_CASES}` = 10, `{PAGE_BUDGET}` = 75 pages** (whichever comes first; always
  finish the case you started; always do ≥1). A bare number arg is a page budget
  (`/foreman 90`); `cases=N` sets a hard case cap.
- The loop is **fully resumable** (`claim --next` skips finalized cases), so stopping at
  the cap and starting a fresh foreman session later loses nothing. Treat the cap as a
  review/commit checkpoint, not a hard limit. See **Context accumulation** below for why
  ~10–15 is the comfortable ceiling per session.

## Steps for the main session (the foreman)

**1. Sync & verify (one bash call), STOP if anything is wrong:**
```
cd /home/user/Claude
git rev-parse --abbrev-ref HEAD          # must be claude/supply-code-jurisprudence-design-yiwgen
git pull --rebase origin claude/supply-code-jurisprudence-design-yiwgen
python3 -m pip install --quiet pymupdf 2>/dev/null
python3 -c "import json;d=json.load(open('supply-code/state/index.json'));ids=sorted(int(c['case_id'].split('-')[1]) for c in d['cases']);g=[n for n in range(1,max(ids)+1) if n not in set(ids)];print('n',len(ids),'next_seq',d['next_seq'],'gaps',g[:8],'dups',len(ids)!=len(set(ids)))"
python3 -c "import json,os;m=json.load(open('supply-code/claude_input/_queue_manifest.json'));CQ='supply-code/claude_input';print({b:sum(os.path.exists(os.path.join(CQ,e['path'])) for e in m.get(b,[])) for b in ['new','new_from_grok_top10pct','upgrade']})"
```
If HEAD is not the branch → stop. If gaps/dups non-empty → stop (corpus integrity). If no
pending `new`/`new_from_grok_top10pct` → tell the user the NEW queue is drained and ask
before touching `upgrade` (upgrades deferred by user directive). Confirm Grok's loop is
NOT running (turn-based: shared id counter + per-machine lock).

**2. SETUP:** the foreman tracks `cum_pages` and `cases_done` itself across the loop — NOT in
shell (env vars and `mktemp` dirs do NOT persist between separate Bash tool calls, and the child
prompts need a literal path). Per-case scratch uses FIXED, git-ignored paths under
`supply-code/extracts/`: brief = `supply-code/extracts/<CID>.brief.md`, finalize log =
`supply-code/extracts/<CID>.fin.log`. Note THIS session's `Claude-Session` URL from the current
attribution guidance (for the report only; finalize stamps commits itself).

**3. PER-CASE LOOP.** Before each case: if `cases_done >= {MAX_CASES}` or `cum_pages >= {PAGE_BUDGET}` → stop & report. Otherwise, for one case:

> **Execution model:** in this harness sub-agents run ASYNC even when you request foreground — you spawn a child and get a *completion notification* a few minutes later, not a blocking return. So the loop spans multiple turns: spawn the reader → (notification) → spawn the author → (notification) → finalize → next case. The claim-guard keeps exactly one case in flight (a second `claim --next` while a ticket is open just re-emits `ALREADY_CLAIMED`), so this stays strictly sequential and safe. Do not try to claim the next case until the current one has finalized.

  a. **CLAIM + LEAN (bash, zero-LLM):**
  ```
  OUT=$(python3 claude_tools/scj_claude.py claim --next 2>&1); echo "$OUT"
  CID=$(echo "$OUT" | grep -oE 'SCJ-[0-9]+' | head -1)
  MODE=$(echo "$OUT" | grep -oE 'mode=[a-z]+' | head -1 | cut -d= -f2)
  ```
  If `$OUT` has `NO_INPUT`, or `MODE` != `new` (upgrade — deferred) → stop the loop & report.
  If `$OUT` starts `ALREADY_CLAIMED`, proceed with that CID. Else:
  `python3 claude_tools/lean_extract.py "$CID"`. Read `page_count` from the claim line; `cum_pages += page_count`.

  b. **READER child (Agent tool, `model: sonnet`, spawn it; it runs ASYNC).** Prompt: "Read
  `claude_tools/foreman_reader_prompt.md` and follow it with {CID}=`<CID>`,
  {BRIEF_PATH}=`supply-code/extracts/<CID>.brief.md`." On its completion notification, take its one-line `BRIEF …` result. Keep only
  that line — do NOT read the brief yourself.

  c. **AUTHOR child (Agent tool, `model: opus`, spawn it; it runs ASYNC) — fresh per case.**
  Prompt: "Read `claude_tools/foreman_author_prompt.md` and follow it with {CID}=`<CID>`,
  {BRIEF_PATH}=`supply-code/extracts/<CID>.brief.md`." On its completion notification, take its one-line `AUTHORED … gate=ALL PASS …`
  result. If it returns `BLOCKED …`, stop the loop and report the blocker (do NOT finalize).
  Keep only the status line — do NOT read the JSON yourself.

  d. **FINALIZE + PUSH (bash, zero-LLM):**
  ```
  export CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
  python3 claude_tools/scj_claude.py finalize "$CID" > supply-code/extracts/$CID.fin.log 2>&1; echo "exit=$?"; tail -3 supply-code/extracts/$CID.fin.log
  ```
  If the push was REJECTED (non-fast-forward): `git fetch origin <BR>; git rebase origin/<BR>; python3 tools/build_supply_code.py; python3 tools/build_scj_catalog.py; git add supply-code/jurisprudence supply-code/state; git commit -m "spine: rebuild after integrating concurrent pushes" (with trailer) if diff; git push -u origin <BR>` — retry a few times. Confirm `git rev-parse HEAD == origin/<BR>` before the next case. Then `cases_done += 1`.

  **Never** read `supply-code/extracts/<CID>.{txt,lean.txt}`, the brief, or the authored JSON
  into your own (foreman) context. Your context should only ever hold short bash stdout and
  the children's one-line results — that is what keeps the foreman lean across the batch.

**4. AFTER THE LOOP:** persist the ledger — `git add claude_tools/token_ledger.jsonl && git commit -m "claude_tools: token ledger — foreman batch (<cases_done> cases / <cum_pages> pp)" (with trailer) && git push` (rebase-on-reject). Then REPORT to the user:
- per-case row: CID · pages · gate ALL PASS? · push HEAD==origin? · reader/author OK? · ≤120-char disposition
- batch totals: cases finalized, cumulative pages, why it ended (cap / budget / NO_INPUT / upgrade)
- `python3 claude_tools/tok_meter.py report`
- your own approximate context growth (a proxy for how many more cases this session can take)

## Context accumulation (read this — it sets the per-session case count)
- The **authoring never accumulates**: each Opus author child is a fresh, single-case
  context, and the big content (extract, brief, JSON) lives in the children + on disk, never
  in the foreman. This is the whole point of the design.
- The **foreman (main session) accumulates lightly**: per case it retains only short bash
  stdout + two one-line child results + its own orchestration text ≈ **~1.5–3k tokens/case**,
  with no judgment content. Over 10 cases that is ~15–30k of residue — comfortably within the
  window; the harness compacts it if it grows long.
- So the binding limit is your **account rate/usage limit**, not the foreman context. Because
  each case is cheaper than the accumulating background worker, you get more cases per limit
  window. **Recommended: ~10 cases per foreman session** (a clean review + commit + re-sync
  checkpoint); push to ~15–20 if the session's limit is holding. When a limit hits, just start
  a fresh foreman session — `claim --next` continues exactly where it stopped.

## Provenance / rules
- Never leave branch `claude/supply-code-jurisprudence-design-yiwgen`. Turn-based with Grok
  (run only when Grok's loop is stopped). Do NOT edit `tools/` (Grok-owned). Do NOT open PRs.
- Every commit carries the finalize tool's `Co-Authored-By: Claude Opus 4.8` + `Claude-Session`
  trailer automatically; the ledger/spine commits you make must carry it too.
- `<BR>` = claude/supply-code-jurisprudence-design-yiwgen.

## References
- `claude_tools/foreman_reader_prompt.md` — the Sonnet reader child prompt
- `claude_tools/foreman_author_prompt.md` — the fresh Opus author child prompt
- `claude_tools/AUTHORING_CARD.md` — the authoritative RICH schema / quality bar
- `claude_tools/scj_claude.py` (claim/finalize), `author_check.py` (gate), `lean_extract.py`
