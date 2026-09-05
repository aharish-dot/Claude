---
name: next-batch
description: Process the next batch of Supply Code jurisprudence cases on branch claude/supply-code-jurisprudence-design-yiwgen. Use when the user says "next batch", "process the next batch", "run a batch", "continue the SCJ queue", or invokes /next-batch. Syncs the branch, then spawns a background Opus worker that authors, validates, and pushes N cases and reports back only the token ledger. Default batch size 6; the user may pass a number (e.g. /next-batch 8).
---

# next-batch — run one batch of the SCJ rich-authoring pipeline

Turns "next batch" into a running batch on this branch, with no case content in the
chat. Read `claude_tools/AUTHORING_CARD.md` and `claude_tools/batch_worker_prompt.md`
for the full mechanics; this skill is the launcher.

## Batch size
Use the number the user passed (e.g. `/next-batch 8`), else **default 6** (optimum
range 5–8 — see the analysis in `claude_tools/README.md` / the handoff). Never exceed
~10 (context-window + quality risk).

## Steps for the session
1. **Sync & verify** (one bash call), and STOP if anything is wrong:
   ```
   cd /home/user/Claude
   git rev-parse --abbrev-ref HEAD          # must be claude/supply-code-jurisprudence-design-yiwgen
   git pull --rebase origin claude/supply-code-jurisprudence-design-yiwgen
   python3 -m pip install --quiet pymupdf 2>/dev/null
   python3 -c "import json;d=json.load(open('supply-code/state/index.json'));ids=sorted(int(c['case_id'].split('-')[1]) for c in d['cases']);import sys;g=[n for n in range(1,max(ids)+1) if n not in set(ids)];print('n',len(ids),'next_seq',d['next_seq'],'gaps',g[:8],'dups',len(ids)!=len(set(ids)))"
   # confirm the queue still has pending NEW cases:
   python3 -c "import json,os;m=json.load(open('supply-code/claude_input/_queue_manifest.json'));CQ='supply-code/claude_input';print({b:sum(os.path.exists(os.path.join(CQ,e['path'])) for e in m.get(b,[])) for b in ['new','new_from_grok_top10pct','upgrade']})"
   ```
   If HEAD is not the branch → stop and tell the user. If gaps/dups are non-empty →
   stop and report (corpus integrity issue). If no pending `new`/`new_from_grok_top10pct`
   cases remain → tell the user the NEW queue is drained and ask before touching the
   `upgrade` bucket (upgrades are deferred to the end by user directive).
2. **Spawn ONE background Opus worker.** Read `claude_tools/batch_worker_prompt.md`,
   substitute `{N}` with the batch size and `{SESSION_URL}` with THIS session's
   `Claude-Session` URL (from the current attribution guidance — not a hardcoded one),
   and launch a `general-purpose` agent with `model: opus`, run in background. Do not
   author cases in the main window.
3. **Wait for the completion notification.** Then relay to the user ONLY: the per-case
   status table (CID · pages · gate · push · ≤120-char disposition) and the tok_meter
   ledger for the batch. No extract/JSON/headnote text. Surface any blocker the worker
   reports.
4. Do not schedule follow-ups or process a second batch unless the user asks.

## Notes
- The pipeline is resumable by construction: `claim --next` advances through the
  manifest (skipping finalized cases), so "next batch" always continues where the
  last one stopped — no cursor to maintain.
- Grok advances the corpus out-of-band; the sync in step 1 and the worker's
  rebase-on-reject push handle that.
- Model tiering (Sonnet reads / Opus authors) is deferred (user decision) — the worker
  is all-Opus. Re-enable for the wordy ≤10pp bucket when we reach it.
