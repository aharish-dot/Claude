# High Court Judgment Digests

Pipeline mirrors the Delhi District Court project (`../delhi-dc/`), adapted for the longer,
more heavily reasoned and more citation-dense orders of the High Court.

## Folders

| Folder | Purpose |
|---|---|
| `input/` | Raw judgment PDFs awaiting processing — **you upload here**. |
| `processed/` | Raw PDFs moved here once the case's digest is committed (this move *is* the progress marker). |
| `extracts/` | Per-case cleaned text + structured-extract JSON — the source of truth for re-verification and full-bespoke upgrades. |
| `summaries/pdf/` | Per-case digest PDFs (the deliverables). |
| `summaries/json/` | Per-case JSON extracts that power the compilations. |
| `summaries/merged/` | Cross-case compilations (interpretations, table of authorities, significance, comparative facts). |
| `state/` | `progress.json`, `authorities-ledger.json`, `manifest.json`. |

## Workflow

1. Drop **searchable** HC judgment PDFs into `input/`.
2. The pipeline processes the next file in `input/`: extract → verify → render digest →
   commit → `git mv` the PDF into `processed/`.
3. "What's left" = whatever is still in `input/`; progress is visible here on GitHub as
   `input/` shrinks and `processed/` fills.

## Overnight automation

A scheduled Routine can process cases unattended (fresh session per run, resuming from the
`input/` queue). **It only runs when explicitly armed** — nothing fires on its own.
