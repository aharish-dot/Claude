# Building jurisprudence from UPERC Electricity Ombudsman orders — a strategy

*Draft v0.1, written after coding the first 5 orders. Everything here is a proposal for you to shoot at, not a finished design.*

---

## 0. TL;DR

1. **Your instinct is right, but the columns you named capture the wrong half of the case.** Consumer type / load / problem-class describe *what the dispute is about*. But in this sample **4 of 5 orders were decided on a threshold question** (jurisdiction, maintainability, power-of-review, withdrawal) and never reached the electricity merits at all. The doctrine lives in *how the case was disposed*, not *what it was about*. So the schema needs a **procedural/jurisdictional axis** as a first-class citizen.
2. **Patterns don't need 100 rows. They need the right facets.** With 5 orders, coded on the axis above, a clear doctrine already emerges (see §3). Volume sharpens confidence; it doesn't create the pattern. Better facets beat more rows.
3. **This is not a new system — it's a new *forum* in the pipeline you already built.** Your `high-court/` and `supreme-court/` digests are already UP electricity-law cases (§126/135 theft/assessment). The Ombudsman sits one rung below the High Court on the *same ladder*, deciding the *same statute*. Treat `ombudsman/` as a sibling of `high-court/`, reuse the digest schema, and you get **cross-forum jurisprudence** almost for free.
4. **Two layers, not one.** Keep the rich per-case digest (`extract.json`, like `HC-001`) *and* add a thin, flat, controlled-vocabulary **facet table** (`orders.csv`) on top. The digest is for *reading* one case; the facet table is for *GROUP BY* across a hundred. Your "excel sheet" is layer 2.
5. **One hard operational difference from the HC pipeline: these PDFs are scanned bilingual images, not text.** They need an OCR front-end (Hindi + English). That's built (`pipeline/ocr_extract.py`) and is the only genuinely new plumbing.

---

## 1. What the 5 orders actually are

All five are 2026 orders of the **Electricity Ombudsman, U.P.** (the appellate/supervisory forum that sits above the Consumer Grievance Redressal Forums — CGRFs — under the UPERC CGRF & Ombudsman Regulations). The English-signed ones are by **Sanjay Srivastava**. Coded rows are in [`data/orders.csv`](data/orders.csv); readable headnotes in [`data/orders-abstracts.md`](data/orders-abstracts.md).

| id | consumer | segment / load | what it was about | how it was decided | outcome |
|----|----------|----------------|-------------------|--------------------|---------|
| **OMB-001** (C-19/2026) | Smt. Shabina (Lucknow) | Domestic | theft re-assessment + non-compliance of a prior order | **subject-matter bar** — theft/UUE outside forum | dismissed, not maintainable |
| **OMB-002** (C-20/2026) | Maa Shakumbhari Plastic Udyog | Industrial, HV | defective-meter kVAH assessment | **no power of review** of own order (CPC O.47) | dismissed |
| **OMB-003** (C-25/2026) | M/s Om Industries (rice mill) | Industrial, HV-2, 110 KVA | electricity-duty exemption + non-compliance of CGRF order | **enforcement** under s.142 | **directed compliance** (only merits win) |
| **OMB-004** (23/2026) | Sri Alok Kumar (OXY Homes flat) | Domestic, single-point/franchisee | builder over-recovery via prepaid billing; "consumer" u/s 2(15) | **withdrawn** with liberty (threshold: consumer-definition) | dismissed as withdrawn |
| **OMB-005** (15/2026) | M/s J.K. Industries | Industrial, MV-6, 80 HP | poor supply (6h→2h) → ₹7.5 cr compensation | **no original jurisdiction** — exhaust CGRF/SoP first | dismissed, not maintainable |

## 2. Why your proposed schema needs upgrading

Your columns → my read:

| you proposed | keep? | why / what to add |
|--------------|-------|-------------------|
| **consumer type** | ✅ | Split into `consumer_segment` (Domestic/Commercial/Industrial/Institutional) **and** `tariff_category` (LMV-1, HV-2, MV-6 …). The statutory tariff code is the analytically useful one and is often stated verbatim. |
| **load** | ✅ | Keep, but normalise the unit — orders mix **KW / HP / KVA / kVAH**. Store value + unit separately if you want to sort. |
| **problem classification** | ✅ but rename | Call it `primary_subject` and allow a `secondary_subjects` list. Metering/billing/load-change/new-connection are a good start; this sample also needed **theft/UUE-assessment, electricity-duty, supply-reliability/hours, disconnection, franchisee/single-point recovery, non-compliance-of-order**. Controlled vocab in [`schema/facets.md`](schema/facets.md). |
| **supply code / law interpretation** | ✅ but structure it | Don't put it in one prose cell. Break into `act_sections`, `supply_code_clauses`, `regulations_cited`, `precedents_cited`, and a single `key_provision_interpreted`. Structured citations are what let you build the **authorities graph** (you already do this for HC in `state/authorities-ledger.json`). |
| **final judgement** | ✅ but split into three | `disposition` (the outcome verb), `relief_granted` (what the consumer actually got), and `ratio_short` (the *holding* — the reusable rule). The ratio is the jurisprudence; the disposition alone isn't. |

**The columns you're missing — and they're the important ones:**

- **`procedural_posture`** — appeal-from-CGRF vs non-compliance/execution (s.142) vs review/recall vs direct-complaint vs post-writ-remand. This sample had *five different postures in five orders.*
- **`decided_on`** — the ground the case actually turned on: **Merits / Maintainability-jurisdiction / Maintainability-procedure / Withdrawal / Compliance-execution / Remand.** This is the single most predictive column. In this batch it's `Maintainability` or `Withdrawal` in 4 of 5.
- **`maintainability_holding`** — Maintainable / Not-maintainable / Not-decided. A dedicated flag because "did the forum even reach the merits?" is the first question any researcher asks.
- Metadata that makes rows joinable: `discom` (MVVNL / PVVNL / …), `district`, `ombudsman` (which adjudicator), `order_date`, and `prior_order_ref` (the CGRF/Ombudsman/HC order being challenged — this is what links the forum ladder).

## 3. The pattern that already emerged (n=5)

Even at five rows, coding the procedural axis surfaces a real doctrine:

> **The U.P. Electricity Ombudsman in 2026 is behaving primarily as a **gatekeeper of its own jurisdiction**, not as a merits court.** Four of five orders were disposed on a threshold ground, and they cluster into two distinct doctrines:
>
> - **(a) Subject-matter bar** — theft / unauthorised-use assessments belong to the s.126/135/127 machinery and the Special Court, *not* the CGRF/Ombudsman (OMB-001; Reg 3.10 of the 2022 Regulations).
> - **(b) Hierarchy / exhaustion** — the Ombudsman has **only appellate/supervisory** jurisdiction over the CGRF and **no original jurisdiction**; a consumer must exhaust the CGRF (and, for compensation, the Standards-of-Performance Regs 2019, cl. 8/8.4.4) first — and a High Court's "liberty to approach the Ombudsman" does *not* manufacture jurisdiction (OMB-005). Add to this the **no-power-of-review** rule (OMB-002; CPC Order XLVII by analogy) and **consumer-definition** threshold under s.2(15) (OMB-004).
>
> The lone merits outcome (OMB-003) was **not** a fresh adjudication either — it was *enforcement* of a CGRF order under s.142. So the forum's "wins for consumers" in this sample are execution, not first-instance relief.

That is exactly the kind of sentence the user wanted patterns to produce — and it's falsifiable: as rows accumulate, the "% disposed on threshold grounds" and the split between doctrine (a) and (b) become measurable. **Track that ratio as the project's headline metric.**

Secondary patterns worth watching:
- **Consumer mix skews industrial** (3/5: plastics, rice-mill, hinges) — MSMEs using the forum over billing/duty/supply, often after a business loss.
- **"Non-compliance of a prior order" (s.142) is its own sub-genre** (OMB-001, OMB-003) — worth a boolean facet.
- Same adjudicator across the English orders → we're initially mapping **one Ombudsman's doctrine**; note it, so later comparison across adjudicators is possible.

## 4. Architecture — two layers + a graph

```
                 ┌─────────────────────────────────────────────┐
  scanned PDF ─► │ pipeline/ocr_extract.py  (PyMuPDF + tesseract│
   (Hindi+Eng)   │  hin+eng)  →  ombudsman/extracts/OMB-XXX.txt │
                 └───────────────────┬─────────────────────────┘
                                     │  (reuse existing sub-agent + verify.py)
             ┌───────────────────────▼───────────────────────┐
  LAYER 1    │ ombudsman/extracts/OMB-XXX.extract.json        │  ← rich digest,
  (deep)     │  same golden schema as HC-001.extract.json     │    one per order,
             │  issues/facts/ratio/interpretation/authorities │    for READING
             └───────────────────────┬───────────────────────┘
                                     │  (distil the controlled facets)
             ┌───────────────────────▼───────────────────────┐
  LAYER 2    │ ombudsman/data/orders.csv                      │  ← flat facet table,
  (wide)     │  29 controlled-vocab columns, 1 row per order  │    the "excel sheet",
             │  → GROUP BY subject × decided_on × outcome      │    for COUNTING
             └───────────────────────┬───────────────────────┘
                                     │
             ┌───────────────────────▼───────────────────────┐
  GRAPH      │ authorities-ledger.json (reuse HC pattern)     │  ← every s.126, cl.4.46,
             │  provision / precedent → [cases citing it]      │    Reg 3.10, CGRF order
             └────────────────────────────────────────────────┘    → cross-forum links
```

- **Layer 1 (digest)** reuses everything you already have. An Ombudsman order maps cleanly onto the `HC-001` schema — it has parties, issues, provisions, reasoning, ratio, disposition. `verify.py` and the render tools should work with a thin `gen_omb.py` clone.
- **Layer 2 (facets)** is the new analytical surface and the direct answer to "the excel sheet." It's *derived* from Layer 1 (or coded directly during extraction). One row per order, controlled vocabularies so counts are meaningful.
- **The graph** is where jurisprudence stops being a list and becomes a map: the same `authorities-ledger.json` idea, extended to Supply-Code clauses, Regulation clauses, and — crucially — **prior-order references**, which stitch CGRF → Ombudsman → High Court together. OMB-005 literally comes down from an Allahabad HC writ; that's a cross-forum edge you can draw.

## 5. Why "patterns emerge at 100 rows" is only half true

Three quantitative things genuinely need volume, and it's worth saying which:

1. **Base rates** — "what share of billing disputes succeed" needs enough billing disputes to be a rate, not an anecdote. ~30–50 per subject-class before a percentage means anything.
2. **Cross-tabs** — `primary_subject × decided_on × disposition` is a 3-way table; cells get thin fast. This is the real driver of the 100+ intuition.
3. **Outliers vs. rules** — one pro-consumer merits order (OMB-003) could be the norm or the exception; only volume tells you which.

But **doctrine emerges immediately** once the procedural axis is coded — you don't wait for 100 rows to notice "theft is always bounced." So: **code the right facets from row 1, and let volume upgrade observations into rates.** Suggested checkpoints: re-run the pattern report at **n=25, 50, 100**.

## 6. Concrete roadmap

**Phase 0 — foundations (this commit).** `ombudsman/` scaffold; the 5 orders coded in `orders.csv`; readable abstracts; OCR pipeline; this strategy. ← *done, for your review.*

**Phase 1 — lock the schema (needs your input).** You react to `schema/facets.md`; we freeze the controlled vocabularies (especially the `primary_subject` and `decided_on` enums) *before* scaling, because re-coding 100 rows after a vocab change is the expensive mistake.

**Phase 2 — wire into the pipeline.** Point `ocr_extract.py` at the same `input/ → processed/` flow the HC forum uses; add `ombudsman/` to `index.json`-style state; clone `gen_hc.py`→`gen_omb.py` so each order also gets a rendered digest. Re-use the Haiku extract sub-agent + `verify.py` gate.

**Phase 3 — batch the corpus.** Pull the next tranche of orders (you have the source list from uperc.org). Target n=25, then 50, then 100, committing per order as the HC pipeline does.

**Phase 4 — the analytics surface.** A tiny `report.py` (or a notebook / the artifact viewer) that reads `orders.csv` and emits the headline metrics: % disposed on threshold vs merits, subject × outcome cross-tab, most-cited provisions, adjudicator comparison, and the CGRF→Ombudsman→HC citation graph.

## 7. Open questions for you

1. **Repo home.** I could not create a standalone `Ombudsman` repo (the GitHub app in this session isn't allowed to create repos). Architecturally it fits best as the `ombudsman/` forum in *this* repo, next to `high-court/`. Want it (a) here as a folder, or (b) broken out into a separate repo you create and I push into? (See the chat message.)
2. **Scope of "jurisprudence."** Is the goal (a) a *research/search* tool over past orders, (b) a *predictive* tool ("given these facts, likely outcome"), or (c) a *drafting* aid (find the on-point ratio to cite)? The schema supports all three, but it changes what we optimise Layer 2 for.
3. **Vocabulary authority.** Should `primary_subject` follow an official UPERC taxonomy (tariff schedule / Supply Code chapter headings) if one exists, or a pragmatic one we grow from the data? I've started pragmatic.
4. **Hindi.** Several orders are Hindi-majority. Do you want the digests in English (translated), bilingual, or Hindi-preserving? Affects OCR language config and the sub-agent prompt.
5. **CGRF layer.** The Ombudsman constantly points *down* to the CGRF. Do you eventually want CGRF orders as a *third* forum folder, to complete the ladder?
