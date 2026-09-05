# claude_tools/ — Claude's working copy of the pipeline

This folder exists so **Claude** and **Grok** never edit the same program file and
collide in git. Grok owns and edits `tools/`. Claude does **not** edit `tools/`.

## The contract

**Separate (per-agent) — this is the only thing that is forked:**

- `tools/` is **shared source but Grok-owned**. Claude may *run* anything in `tools/`
  **unmodified**.
- If Claude needs to change a pipeline program, Claude **copies it into `claude_tools/`
  and edits the copy there**, then runs the copy. The original in `tools/` is left
  untouched. New Claude-only programs are created here too.
- Every fork here carries a one-line header note: which `tools/` file it was copied
  from, at which commit, and what was changed — so drift from the upstream is visible.

**Shared (never forked — one source of truth, reached only through the normal pipeline):**

| Shared resource | Path |
|---|---|
| Sequence counter / id reservation | `supply-code/state/index.json` (`next_seq`) |
| Per-case digests (JSON) | `supply-code/summaries/json/` |
| Per-case digests (PDF) | `supply-code/summaries/pdf/` |
| Jurisprudence spine (the "db") | `supply-code/jurisprudence/` (never hand-edit) |
| Live queue | `supply-code/input/` |
| Progress marker | `supply-code/processed/` |

Claude writes these **only** through the existing locked pipeline
(`prepare_next_scj.py` → author → `finalize_scj.py`), exactly as Grok does, so
ids stay unique and the spine stays consistent. A forked tool in `claude_tools/`
must still read/write these shared paths — never a private copy of them.

## Clash-avoidance protocol Claude follows

The `tmp/` queue lock is **per-disk** (gitignored), so it does **not** protect
against Claude and Grok running at the same time from different checkouts. Therefore:

1. `git pull` immediately before claiming a case (reserving `next_seq`).
2. One agent processes at a time unless the queue is explicitly partitioned
   (e.g. by `input/<year>/`) — matches the project's existing "one machine at a
   time" rule.
3. Commit per case and push right away; on a rejected push, `git pull --rebase`
   and retry with backoff. Never rewind `next_seq`.
4. Stay on branch `claude/supply-code-jurisprudence-design-yiwgen`.

See `supply-code/NEXT.md` (trigger), `supply-code/HANDOFF.md` (strategy),
`supply-code/RUNBOOK.md` (schema), `tools/PLAYBOOK.md` (attribution/verify).

## Batch economics & token notes (2026-09)
- PDF→text extraction is done by `tools/extract_judgment.py` (pymupdf) during `claim`
  — pure code, ZERO model tokens. Pre-converting PDFs saves nothing; the token cost is
  the model INGESTING the judgment text to author, which is unavoidable.
- Ledger step names (`claude_tools/token_ledger.jsonl`):
  read_extract = model reading the judgment text (the compacted `.lean.txt`) into
  context, the largest per-case input (~2.7k–7k tok, scales with page count);
  read_refs = reading guidance (now the one-time lean `AUTHORING_CARD.md` ~2.2k/batch,
  not the old 16k handoff+exemplar); author_json = the authored digest output
  (~2.4k–5.4k tok); claim/finalize = tool stdout (~100–260 tok, negligible).
- Cost levers applied WITHOUT quality loss: batch (amortize cold start), lean card
  (replace handoff+exemplar), fewer turns (combined gate+finalize), read the compacted
  `.lean.txt`, prompt caching (harness, automatic). Deferred: model tiering (Sonnet
  reads / Opus authors) — safe for the wordy ≤10pp bucket, risky for >10pp.
- Optimum batch size: default 6, range 5–8. Below ~4 wastes per-spawn cold start;
  above ~8 the accumulating in-context extracts + context-window/quality risk outweigh
  it (caching softens, does not remove, the accumulation). Tune from the per-case token
  trend in the ledger.
- Measured: single spawn w/ full handoff ~127k tok/case; batched(4)+lean card+fewer
  turns ~59k tok/case (~54% less), quality held (gate ALL PASS first try).
- Resume a batch in any fresh session on this branch: `/next-batch [N]` (skill) — syncs,
  then spawns the Opus worker from `claude_tools/batch_worker_prompt.md`.
