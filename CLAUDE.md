# Repo working agreement — READ FIRST

This repo builds the **Supply Code Jurisprudence (SCJ)** corpus. Work happens on
branch **`claude/supply-code-jurisprudence-design-yiwgen`** only. Never switch or
create branches.

## "next batch" ⇒ spawn the background worker (do NOT process in the main window)

When the user says **"next batch"**, "process the next batch", "run a batch", or
"continue the SCJ queue":

1. **Invoke the `next-batch` skill** (`.claude/skills/next-batch/SKILL.md`). That is the
   launcher — it syncs the branch and **spawns ONE background `general-purpose` agent
   with `model: opus`** using `claude_tools/batch_worker_prompt.md`.
2. **Do NOT author cases yourself in the main window.** The main session only launches
   the worker and, when it finishes, relays the compact status table + token ledger.
3. **Batch size = PAGE BUDGET, not a case count:** default **75 source pages**, cap
   **10 cases**. A bare number overrides pages (`/next-batch 90`); `cases=N` caps count.

Processing cases interactively in the main window is the expensive, wrong path — it
reads each judgment into the chat context. The background worker reads a lean extract
in a subagent and reports only a ledger. Always use the worker.

## Two pipelines, two queues, TURN-BASED (never run both at once)

| | Claude | Grok |
|---|---|---|
| Tools | `claude_tools/` (`scj_claude.py`) | `tools/` (`prepare_next_scj.py`) — **do not edit or use** |
| Queue | `supply-code/claude_input/` (manifest: `new`, `new_from_grok_top10pct`, `upgrade`) | `supply-code/input/<year>/` |
| Schema | RICH — `claude_tools/AUTHORING_CARD.md` | lean |
| Stamp | `model: "Claude Opus 4.8"` + attribution trailer | `model: "Grok 4.6"` |

Both pipelines share the same sequential id counter (`supply-code/state/index.json`
`next_seq`) and the queue lock is **per-machine only**. So they must run **turn-based**:
**Grok runs only when the user's Claude limit is exhausted.** Running Claude and Grok
at the same time causes id collisions and wasted work. If a push is rejected
(non-fast-forward), rebase on `origin` and retry — never force-push.

## Always sync first (a fresh session can start from a stale clone)

Before any batch: `git pull --rebase origin claude/supply-code-jurisprudence-design-yiwgen`.
If `git log`/`next_seq` looks far behind what the remote shows, the clone is stale —
re-sync before doing anything. Confirm HEAD is the branch above.

## References
- `.claude/skills/next-batch/SKILL.md` — the launcher (page budget, cap, steps)
- `claude_tools/batch_worker_prompt.md` — the worker prompt (loop, gate, finalize, push)
- `claude_tools/AUTHORING_CARD.md` — authoritative RICH schema / quality bar
- `claude_tools/README.md`, `claude_tools/SESSION_HANDOFF.md` — pipeline notes

Commits: end with the `Co-Authored-By: Claude Opus 4.8` + `Claude-Session:` trailer
(the SCJ finalize tooling adds this automatically). Do not open PRs unless asked.
