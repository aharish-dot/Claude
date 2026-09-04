# Note for Grok — how we (Grok + Claude) share this repo without conflict

Hi Grok. Claude has joined this project to handle a slice of the work. Nothing about
your job changes in spirit — you still process judgments via `supply-code/NEXT.md`.
This note just marks the lanes so we never step on each other. The user asked me to
write it for you.

## TL;DR
- **You keep `tools/` and the `supply-code/input/` queue.** Run `NEXT.md` as usual.
- **Claude has its own `claude_tools/` and its own `supply-code/claude_input/` queue.** Please don't read/edit those for processing — they're Claude's lane.
- **Run one of us at a time** (turn-based). Not both at once.
- The corpus is contiguous **SCJ-001..708, `next_seq = 709`, no gaps.**

## Who owns what
| Lane | Grok | Claude |
|---|---|---|
| Programs | `tools/` | `claude_tools/` |
| Queue | `supply-code/input/` (~2,756 files, all ≤10 pages) | `supply-code/claude_input/` (Claude's; you never scan it) |
| Digest format | lean (`tools/gen_scj.py`), `model: "Grok 4.6"` | rich (`claude_tools/gen_scj.py`), `model: "Claude Opus 4.8"` |

**Shared — both write, but only through our own pipelines; never hand-edit:**
`supply-code/state/index.json` (`next_seq`), `supply-code/summaries/`,
`supply-code/jurisprudence/` (spine + catalog), `supply-code/processed/`.

## The division of labour
The user routes by size: **Claude authors everything > 10 pages, plus the wordiest
10 % of the ≤10-page cases; Grok authors the rest.** Those Claude cases were moved
out of `input/` into `claude_input/`, so your queue now contains only the cases meant
for you. Just process `input/` normally — you won't encounter Claude's cases.

## One change to your tool (authorised by the user — please keep it)
`tools/prepare_next_scj.py` → `is_docket_dup()` now also matches `"<n> of <year>"`
with digit boundaries. Reason: connected petitions are sometimes written
`"Nos. 16147 of 2009 and 16149 of 2009"` (plural), and the old singular needle
`"No. 16147 of 2009"` missed them — which created a duplicate case (SCJ-707 had
duplicated the existing SCJ-225). The fix is additive (your existing needles still
run first) and only helps you avoid making duplicates. **Please don't revert it.**
Nothing else in `tools/` was touched.

## Queue cleanup already done (why `input/` looks smaller)
A duplicate scan (`claude_tools/dupscan.py`) found **151 already-processed judgments
sitting in the queue**. They were handled so you won't re-process them:
- **102** small (≤10pp) duplicates → retired to `processed/` (no new ids).
- **49** large (>10pp) duplicates → moved to `claude_input/` for Claude to *upgrade*
  the existing lean records (same `SCJ-xxx` id, richer content — no new id).
- The only internal corpus duplicate (SCJ-707 = SCJ-225) was resolved.
Result: your `input/` is ~2,756 genuine, de-duplicated ≤10pp cases.

## Coordination rules
1. **Turn-based.** The `tmp/` queue lock is per-machine, and both of us write
   `state/index.json` + the spine, so running simultaneously will collide on
   `git push`. Please run only when Claude isn't, and `git pull` first.
2. **Ids** come from `next_seq` (currently 709) for both of us; turn-based keeps them
   unique. Claude also back-filled the 707 gap, so the sequence is contiguous.
3. **Provenance / telling our work apart:** Claude sets `model: "Claude Opus 4.8"`
   and signs its commits (`Co-Authored-By: Claude Opus 4.8` + a `Claude-Session:`
   trailer). Your lean records stay `model: "Grok 4.6"`. Rich digests carry extra
   sections (Reusable Constructions, per-holding Evidence, Related cases, a
   ratio/obiter badge, and a "Source file" line) — those are Claude's; leave them as is.

## If you pull and see new things
`claude_tools/` (Claude's programs incl. `SESSION_HANDOFF.md`), `supply-code/claude_input/`
(Claude's queue + `_queue_manifest.json`), `supply-code/input/dup_scan_report.json`,
and richer `SCJ-xxx.json`/PDFs — all expected, all Claude's. Your workflow is unchanged:
`git pull`, then run `NEXT.md` on `input/`.

Thanks — and happy to adjust the lanes if anything here gets in your way.
— Claude
