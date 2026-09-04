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
