---
name: next-batch
description: Process the next batch of Supply Code jurisprudence cases on branch claude/supply-code-jurisprudence-design-yiwgen. Use when the user says "next batch", "process the next batch", "run a batch", "continue the SCJ queue", or invokes /next-batch. Syncs the branch, then spawns a background Opus worker that authors, validates, and pushes cases sized by a cumulative page budget (default ~75 source pages, cap 10 cases) and reports back only the token ledger. The user may pass a page budget (e.g. /next-batch 90) or a case cap (e.g. /next-batch cases=8).
---

# next-batch — run one batch of the SCJ rich-authoring pipeline

Turns "next batch" into a running batch on this branch, with no case content in the
chat. Read `claude_tools/AUTHORING_CARD.md` and `claude_tools/batch_worker_prompt.md`
for the full mechanics; this skill is the launcher.

## Batch size — PAGE BUDGET, not a fixed case count
Cases vary 8→38pp, so a fixed case count swings token cost wildly. Size batches by a
**cumulative source-page budget** with a case-count guardrail:
- **Default: `{PAGE_BUDGET}` = 75 pages, `{MAX_CASES}` = 10** (min 1; the worker keeps
  claiming until cumulative pages hit the budget or the case cap, always finishing the
  case it started). With mostly <10pp cases this yields ~8–10 small cases; with big
  order-sheets it stops after 2–3. This normalizes cost/batch and amortizes the fixed
  one-time card read (~4.4k tok) over more cases.
- **User overrides:** a bare number is a *page* budget now (`/next-batch 90` → 90pp);
  `/next-batch cases=8` sets a hard case cap with the default page budget; the user may
  also give both. Keep `{MAX_CASES}` ≤ ~12 (context-window + quality risk).

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
   substitute `{PAGE_BUDGET}` and `{MAX_CASES}` (see Batch size above) and `{SESSION_URL}`
   with THIS session's `Claude-Session` URL (from the current attribution guidance — not a
   hardcoded one), and launch a `general-purpose` agent with `model: opus`, run in
   background. Do not author cases in the main window.
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
