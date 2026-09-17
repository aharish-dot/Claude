# SCJ pipeline — 20+ judgment summaries per session, no external API

A greenfield pipeline for turning court-judgment PDFs into rich structured JSON
summaries (the `SCJ-3166` shape). It is built for one constraint above all:

> **produce at least 20 summaries in a single chat session, using no external LLM
> API** — Claude-in-the-session is the model.

## The idea

Authoring a summary like `examples/SCJ-3166.json` is genuinely hard legal work, and
that is the *only* part that needs the model. Everything around it is deterministic.
So the pipeline pushes ~90% of the work into plain Python and shrinks what the model
has to hold in context:

| Step | Who | Cost to the session |
|------|-----|---------------------|
| PDF → text, de-boilerplate ("lean") | Python (`pdfplumber`/`pypdf`) | 0 |
| Parse court, bench, coram, date, docket, parties | Python (`scjlib/meta.py`) | 0 |
| Assign case IDs, track progress, resume | Python (`scjlib/ledger.py`) | 0 |
| Build a metadata-filled skeleton JSON | Python (`scjlib/stencil.py`) | 0 |
| **Write the legal analysis into the skeleton** | **Claude, in-session** | **~2.3k in + ~2.5k out per case** |
| Validate + gate the result | Python (`scjlib/validate.py`) | 0 |

Because each case only costs the model a small, self-contained slice (read one lean
extract ≈ 2.3k tokens, write one JSON ≈ 2k tokens) and finished work is written
straight to disk, **20 cases fit comfortably in one context window**:

```
one-time:  authoring card ≈ 1.5k
per case:  ~2.3k (read lean text) + ~2.5k (author + write JSON) ≈ 4.8k
20 cases:  ≈ 1.5k + 20 × 4.8k ≈ ~97k tokens  → well inside a 200k window
```

If a session is compacted or interrupted, the ledger + on-disk outputs make it fully
**resumable** — rerun `prep` and it skips what is already done.

## Layout

```
pipeline.py              # the CLI (ids | extract | prep | validate | report | selftest)
scjlib/                  # deterministic engine (pure stdlib + pypdf/pdfplumber)
  extract.py  meta.py  stencil.py  validate.py  ledger.py  common.py
prompts/authoring_card.md   # the ONE thing Claude reads per session; the quality bar
schema/scj.schema.json      # portable JSON Schema (spec); validate.py is the gate
examples/SCJ-3166.json      # gold reference, in the refined scj-2.0 schema
data/
  pdfs/        # input judgments  (point --pdf-dir here, or drop files in)
  extracts/    # <case_id>.txt (lean) + <case_id>.extract.json
  out/         # <case_id>.json  ← the deliverables
  work/        # WORKLIST.md + worklist.json for the current batch
  ledger.jsonl # per-PDF status: queued → extracted → prepared → authored/needs-fix
```

## Run a session (single-thread — the default, works anywhere)

```bash
# 0. put PDFs in data/pdfs/  (all Allahabad HC here, so pass a default court)
# 1. prepare the next 20 pending cases (extract + stencil + worklist)
python pipeline.py prep --next 20 --court "Allahabad High Court"

# 2. Claude authors them:
#    - read prompts/authoring_card.md ONCE
#    - work through data/work/WORKLIST.md: read each lean .txt, fill each skeleton .json
#
# 3. gate the results and update the ledger
python pipeline.py validate --all --verbose

# 4. see throughput + context budget
python pipeline.py report
```

Only `data/out/*.json` that pass validation count as done; skeletons deliberately
fail (`model: "PENDING"`) so "valid" == "authored".

## Scaling past one window (optional parallel mode)

To go beyond ~20–25 (or to go faster), fan the worklist out to **Claude Code
subagents** — in-session workers, each with its own fresh context (still no external
API). The orchestrator hands each subagent a slice of `worklist.json` + the authoring
card; each writes its `data/out/*.json`; the orchestrator only tracks completion via
the ledger. Trigger it by telling Claude, e.g., *"author the worklist using 4
subagents, 5 cases each."* Throughput then scales with worker count instead of a
single window.

## Notes, defaults, limits

- **No network, no API keys, no extra installs.** Uses `pypdf`/`pdfplumber` (already
  present) and the Python standard library. `jsonschema` is intentionally *not*
  required — `validate.py` is self-contained.
- **Model field.** `model` records who authored the analysis (e.g. "Claude Opus 4.8").
  It is provenance, not configuration.
- **Metadata is best-effort and self-checking.** Anything uncertain is left blank and
  surfaced in `qa.flags` (e.g. concatenated orders → multiple candidate dates) for the
  author to resolve — the pipeline never silently guesses a disposal date or a party.
- **Other courts / codes.** `meta.py` heuristics are tuned for Allahabad HC e-copies;
  add patterns there for other formats. Catalog-key conventions live in the authoring
  card.
- **Scanned/image PDFs** are out of scope (needs OCR); `engine: "none"` in an extract
  flags a PDF no text engine could read.
