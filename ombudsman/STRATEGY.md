# UPERC Electricity Ombudsman → jurisprudence — strategy v0.2

*Redesigned after coding 10 orders and your answers on scope, cost, and structure.*
*v0.1 (the two-layer, HC-mirroring plan) is superseded by this. Key changes are flagged **[changed]**.*

---

## 0. Your decisions, locked in

| question | decision | consequence |
|---|---|---|
| Repo home | **stays here** as `ombudsman/` | sibling of `high-court/`; nothing to migrate |
| What it's *for* | **research / search** over past orders | optimise for retrieval, not narrative digests |
| Vocabulary | **pragmatic, grown from data** | enums evolve as new subjects appear; no external taxonomy to import |
| Language | **bilingual** digests | OCR runs `hin+eng`; abstracts keep Hindi terms where they carry meaning |
| CGRF layer | **yes, later** | a future `cgrf/` forum completes the ladder |
| **Cost** | **optimise for tokens; the HC/SC pipeline is *not* required** | **[changed]** drop the rich digest + verify + render machinery entirely |

## 1. The biggest change: one cheap layer, not two **[changed]**

v0.1 proposed mirroring the High-Court pipeline — a rich `extract.json` digest per case, a Haiku sub-agent, `verify.py`, PDF rendering. **That's now dropped.** For a *search tool* over *short* orders, under a *token budget*, it's the wrong spend. The new shape:

```
scanned bilingual PDF ─(local OCR, hin+eng — 0 tokens)─► processed/OMB-XXX.txt
                                                              │
                              read HEAD + TAIL only (skip the ├─► data/orders.csv      (facets — the search index)
                              verbose middle submissions)     ├─► data/orders-abstracts.md (2-line bilingual headnote + ratio)
                                                              └─► state/cases.json    (processed-cases DB, dedup by hash)
```

- **`orders.csv` is the product**, not a by-product — 29 controlled-vocab columns, one row per order, the thing you `grep`/filter/sort to answer "show me all metering-assessment cases that got relief."
- **`orders-abstracts.md`** carries a short bilingual headnote + the **ratio** per order — enough to *read* a hit without opening the PDF.
- **No per-case rendered digest.** If you ever want one, it's a later, optional add — not on the critical path.

### Token discipline (the rule that keeps this cheap)
1. **OCR is free** — it's local `tesseract`, no model tokens. Do it in the background, at volume.
2. **Never read a full order into context.** These orders are 3–10 pages; the codeable facts sit in the **first page** (parties, connection, the impugned order) and the **last 1–2 pages** (the "Held/आदेश"). Read only those. The middle is party submissions — skip it. (This is exactly how the 5 new orders were coded here.)
3. **Code directly to the CSV row + 2-line abstract.** No intermediate rich JSON, no verify/render pass.
4. Rough budget: **a few thousand tokens per order**, vs the HC pipeline's order-of-magnitude more.

## 2. The pattern flipped at n=10 — which is the real lesson

At **n=5** the headline was "the Ombudsman is a gatekeeper — 4 of 5 dismissed at the threshold." **At n=10 that's gone:** the split is now **6 relief / 4 threshold.**

| decided on | n=5 | n=10 |
|---|---|---|
| reached relief / merits | 1 | **6** |
| threshold (jurisdiction / review / withdrawal) | 4 | 4 |

The five new orders were mostly **merits wins for consumers**, and a clear doctrine surfaced:

- **Metering-assessment on periodic-check failure** *(OMB-007, OMB-008)* — the licensee's breach of **Supply Code 2005 cl. 5.5(b)** (check the meter every 1–2 years) that dumps a delayed assessment on the consumer → **the assessment is corrected/reduced, paid in 5 interest-free installments, with action against the officials and meter replacement.** Two near-identical KESCO/Kanpur orders = a repeatable, citable rule.
- **SoP-compensation enforcement** *(OMB-006, OMB-010)* — the Ombudsman enforces CGRF Standards-of-Performance awards; **OMB-010 adds** that such complaints lie **only before the Company-level forum** (CGRF Regs 2022), not a Zonal one.
- **Billing / disconnection / surcharge** *(OMB-009)* — surcharge under cl. 4.38(ii) upheld, but prior OTS deposits credited.

**Why this matters for the project:** a confident pattern from 5 rows was wrong by row 10. That is the argument *for* your instinct ("I'm not sure yet") and *for* this whole exercise — you need the coded corpus precisely because eyeballing a handful misleads. It also sets the operating rule: **keep the schema stable and re-measure the headline at every milestone (n=25/50/100); never trust a pattern that volume hasn't stress-tested.**

## 3. What survives from v0.1 (unchanged and validated)
- **The facet schema** (`schema/facets.md`) — the procedural/jurisdictional axis (`decided_on`) is *exactly* what let the n=10 flip be visible; a subject-only sheet would have hidden it. **This was the right call; keep it.**
- **Structured citations** → the authorities/citation core (Supply Code cl. 5.5(b), 4.37, 4.38, 4.46; EA s.42, 142; SoP Regs 2019; CGRF Regs 2022) is already forming and is the seed of the cross-forum map.
- **Provenance honesty** — `ocr_confidence` per row; Hindi-heavy rows flagged.

## 4. The processed-cases database (new, and load-bearing for "never rework")
`state/cases.json` is the ledger that makes re-processing impossible:
- one record per case: `case_id`, `representation_no`, `order_date`, `discom`, `district`, `primary_subject`, `decided_on`, `disposition`, **`sha256` of the source PDF**, `pages`, paths to `processed/OMB-XXX.pdf` + `.txt`, `ocr_confidence`, `status`, `processed_date`, and `next_seq`.
- **Dedup rule:** before processing any new upload, hash it; if the `sha256` is already in the ledger, **skip** — the case is done. This is how "don't rework any given case" is enforced mechanically, not by memory.
- The source PDFs and OCR text live in **`processed/`** (your instruction), so the durable archive and the ledger travel together in git.

## 5. Retrieval — how "research/search" actually gets used
For now the corpus *is* searchable with plain tools (the point of the flat CSV + text):
- **Filter:** `csvgrep`/pandas on `orders.csv` — e.g. `decided_on == Merits AND primary_subject ~ metering`.
- **Full-text:** `grep` across `processed/*.txt` (bilingual) for a clause or phrase.
- **By authority:** `grep` the `supply_code_clauses` / `act_sections` columns to pull every order touching cl. 5.5(b).

**Later (optional, cheap):** a single self-contained static HTML search page (client-side filter over a generated `orders.json`) — no server, no tokens to run. Only worth building once n is larger.

## 6. Roadmap
- **Phase 1 — now (this commit):** 10 orders coded + archived in `processed/`; `state/cases.json` live; strategy redesigned. **← done.**
- **Phase 2 — ratify vocab:** you skim `schema/facets.md`; we freeze the `primary_subject` / `decided_on` enums (they've already grown: +`metering-assessment (periodic-check)`, +`disconnection/surcharge`, +`SoP-compensation enforcement`).
- **Phase 3 — batch cheaply:** feed more orders through OCR→head/tail→row. Re-run the headline metric at n=25/50/100. Commit per batch; hash-dedup guards against repeats.
- **Phase 4 — CGRF forum:** add `cgrf/` as a sibling (same schema) to complete CGRF → Ombudsman → HC, and start drawing the prior-order links between them.
- **Phase 5 — search surface (optional):** the static filter page, if the volume justifies it.

## 7. Still open for you
1. **Vocab freeze** — react to `schema/facets.md` so Phase 3 codes against a stable set.
2. **Discom for Bareilly (OMB-010)** — the order names only the division, not the nigam; I left it unresolved rather than guess. Do you know the mapping, or should I look it up once?
3. **Amounts** — a few rupee figures in the Hindi orders are OCR-fuzzy (flagged `~` / `(OCR)`). For a search tool that's fine; if you want them exact, they need a human/second-pass check on those specific rows.
