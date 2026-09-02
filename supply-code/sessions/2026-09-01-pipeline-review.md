# Review after 50 cases (SCJ-338 … SCJ-387)

**Do this when the loop has finalized 50 cases under the 1 Sep 2026 pipeline.** Do not skip. The loop prints `REVIEW DUE` and `python tools/log_scj_review.py --summary` dumps the tracked numbers.

Live metrics (gitignored): `supply-code/tmp/pipeline_review/metrics.jsonl`

## What changed (quality-preserving only)

1. **Finalize coerce + prompt types.** `paras` is a string; `not_decided` is `[{point, …}]`. Finalize normalizes those two shapes before Chrome so Grok is not asked to retry. Prompt spells the types out.
2. **6.5 stencil phrasing.** Same family. Now also matches para/section 6.5, “move/make an application”, “liberty granted to … make/move”, demand notice / electricity dues as the billing cue. **Withdrawals stay off** this family. Listing-only is still not live. 6.5-refusals (SCJ-283/284/288) still veto.
3. **Short gate widened, never narrowed.** Still short if pages ≤ 2 or words ≤ 800 (even with citations). Also short if `citation_count == 0` and pages ≤ 3 and words ≤ 1500. Full stays for cited orders and for uncited work above that (the SCJ-328 4-page quash pattern).

## Tracked parameters (next 50)

| Field | Why |
|---|---|
| `authoring` / `gate` | stencil vs short-pages vs short-words vs short-uncited vs full |
| `elapsed` | did stencil drop to ~10–40s; did short lose the 2-retry tax |
| `pages`, `words`, `citations` | confirm the new short gate is what we think |
| `coerce` | should fall toward empty if the prompt types work; non-empty is OK (finalize saved a retry) |
| `safety_finalize` | Grok wrote JSON but did not run finalize — still a time leak |
| `outcome`, `significance` | stencil must stay `alternate_remedy` / `ordinary` for 6.5 relegations |
| `family` | only `6.5-billing-relegation` and `contempt-6.5-dismissed` |
| `ok` | failures vs the old loop |

## Review checklist

- [x] `python tools/log_scj_review.py --summary` — elapsed by authoring; coerce rate; how many `short-uncited` and stencil.
- [x] **Stencil false positives:** for every `authoring=stencil` in the batch, skim extract vs JSON. Fail if the court refused 6.5, listed the matter, withdrew, or decided the bill.
- [x] **Short-uncited that should have been full:** 3-page uncited orders that actually construe a clause (quash / set aside / per incuriam). If more than a couple, tighten the gate.
- [x] **6.5 clones still on short:** 1–2 page “apply under 6.5” with a bill/demand that did *not* stencil. If several, the regex is still short; do not widen into refusals to chase them.
- [x] **Coerce rate:** if most short cases still coerce `paras` / `not_decided`, the prompt types did not stick (output was still saved; time save came from finalize, not from fewer Grok turns).
- [x] **SCJ-328-class:** any 4-page uncited doctrinal quash must still be `gate=full`.

Do not turn on listing-only from this review unless the stencil-FP check is clean *and* a separate dry-run on the pending queue agrees.

**Reviewed:** 1 September 2026. `next_seq=388`. Verdict below. **Do not turn on listing-only.**

---

## Findings (SCJ-338 … SCJ-387)

### Summary dump

```
pipeline review  SCJ-338–SCJ-387  logged=50/50
  ok=48 fail=0 coerce_any=0 safety_finalize=0
  stencil  n= 5  avg_s=7  gates={'stencil': 5}
  short    n=30  avg_s=116  gates={'short-pages': 26, 'short-words': 3, 'short-uncited': 1}
  full     n=13  avg_s=257  gates={'full': 13}
  ?        n= 2  avg_s=None  gates=-
```

The two `?` rows are **SCJ-358** and **SCJ-360**: stencil JSON, no loop metric. See “358 incident” below. All 50 JSON + PDF exist; `next_seq=388`.

| Gate | n | avg | Notes |
|---|---|---|---|
| stencil | 5 logged (+2 unlogged) | 7s | Target 10–40s. Hit. No grok. |
| short-pages | 26 | ~100s excl. SCJ-344 | Pages ≤ 2. |
| short-words | 3 | 94 / 163 / 159s | SCJ-341, 347, 376. Words ≤ 800. |
| short-uncited | 1 | 99s | SCJ-362 only (3 pp, 835 words). |
| full | 13 | 257s | Includes 25-page SCJ-342 (329s). |

`citation_count=0` on **every** fingerprint in this batch (Allahabad PDFs, no IK doc-ids). The new short-uncited gate is therefore “3 pages and 801–1500 words”, not “orders that cite no authority”. Pages ≤ 2 still win `short-pages`; words ≤ 800 still win `short-words`.

### Stencil false positives — none

Logged stencil (all `6.5-billing-relegation`, all `alternate_remedy` / `ordinary`):

| id | source | extract |
|---|---|---|
| SCJ-366 | WRIC(A)_12560_2025 | electricity bills → file under 6.5 → disposed |
| SCJ-370 | WRIC(A)_13365_2025 | demand notice / erroneous bill → liberty to file 6.5 |
| SCJ-371 | WRIC(A)_14152_2025 | dues / installments / restore → liberty to file 6.5 |
| SCJ-374 | WRIC(A)_14458_2025 | quash bill Rs.66,986 → file 6.5; no coercive action meantime |
| SCJ-378 | WRIC(A)_16402_2025 | oral demand Rs.1,48,000 / correct current bill → file 6.5 |

None refused 6.5, listed, withdrew, or decided the bill. Live classify on the 50 extracts still returns these five plus 358/360. **FP = 0.**

No `contempt-6.5-dismissed` in the batch.

### 358 incident (caption fill, then 30 retries)

Loop `20260901_134544` finished SCJ-338–357 (`ok=20`), then classified **SCJ-358** as stencil and failed `stencil fill incomplete` (empty title: Allahabad `Petitioner :-` caption, not Lucknow `.....Petitioner`). The loop retried the same ticket for the remaining count (**30 FAIL writes**, cases 21–50) instead of stopping. `stencilFailStreak >= 3` is in the current loop script; it did not fire on this run (added after, or the native-exit pipeline hid `exit=1` and the streak path was not the one taken).

358 was later filled by hand (JSON is the `fill_65` template) after `PET_COLON` landed. 360 was stencil in loop `20260901_151148` (`authoring=stencil`, 2 pp / 280 words); that loop died mid-case, so no loop metric, but finalize wrote the same template. Classify now: both STENCIL, slots fillable.

**Keep:** Allahabad `Petitioner :-` caption parser. **Confirm** the loop stops after 3 consecutive stencil-write failures and does not consume the rest of `-Count`.

### Short-uncited — do not tighten

Only **SCJ-362** (Kiran Singh, 3 pp, 835 words). Dismissed, not quashed. Construes Clause **4.3(f)(vi)**: landlord who consented to a tenant connection cannot mandamus a fresh connection while tenant dues remain. JSON matches the extract. One construing case is not “more than a couple”. Leave the gate.

### 6.5 clones still on short — one BILL miss, do not widen into refusals

True clone that should have stenciled:

- **SCJ-353** (1 p, 218 words): “impugned **current bill** … Rs.11,396” → apply under 6.5 → disposed. `classify_65` = `no: not a billing grievance`. BILL wants `electricity bills?` / `demand notice` / `electricity dues`, not “current bill”.

Correctly off stencil (do **not** widen to catch them):

- SCJ-364 / 365 — 6.5 direction, **no bill/demand in the order**
- SCJ-368 / 377 — decide an **already-filed** representation/objection as 6.5 (no relegation language)
- SCJ-361 — theft/126/135/FIR veto (relegated anyway; keep the veto)
- SCJ-373 — 6.5 disposal, but the PDF also has an earlier “list as fresh” listing → INTERLOC veto. Bundled listing+judgment, not a regex hole in 6.5 itself
- SCJ-379 — **6.5 order quashed** for no hearing and remanded (refusal/remand, not a clone)
- SCJ-382 / 372 / 381 — Clause **7.10** CGRF, not 6.5
- SCJ-385 — reconnection **granted** while 6.5 pending (merits, `consumer` / `significant`)

One BILL miss is not “several”. Do not add “current bill” unless the next 50 shows more. Do not stencil 6.5-refusals or 7.10.

### Coerce rate — prompt types stuck

`coerce_any=0`. Finalize did not have to reshape `paras` lists or string `not_decided`. Time save is from fewer Grok retries, not from coerce.

Nit: **SCJ-373** omitted `holding_units[0].paras` entirely. Coerce converts list→string; it does not default a missing key to `""`. Generator still rendered. Optional: coerce missing `paras` to `""` so the field is always present.

`safety_finalize=0` on logged cases. SCJ-344 (2 pp, 409s) is a short-pages outlier (other short-pages 67–142s); JSON is fine; no finalize metric row.

### SCJ-328-class

| id | gate | pp | words | what happened |
|---|---|---|---|---|
| SCJ-340 | **full** | 4 | 982 | s.135 FIR not quashed; Arnesh Kumar. Correctly full. |
| SCJ-352 | **full** | 4 | 1003 | s.126/127 deposit / fresh representation. Correctly full. |
| SCJ-341 | short-words | 4 | 680 | FIR-quash **listed**, not decided. Procedural. Words ≤ 800 is the old gate. |
| SCJ-376 | short-words | 4 | 778 | Twin of SCJ-375: EE (Revenue) assessment quashed; 2007 left to appeal. **Doctrinal quash on the short-words gate**, not short-uncited. JSON is faithful (vires in `not_decided`). |

The new short-uncited gate did **not** swallow a 4-page quash. SCJ-376 leaked through the **existing** words ≤ 800 rule. Quality held (and SCJ-375 on full, 5 pp / 840 words, is the same holding with a richer record). Do not raise the 800-word floor on one well-authored short case. Watch the next 50 for another 4-page short-words quash.

### Listing-only — still off

Live listing-only dry-run on these 50 extracts: **0 would-be TPs**. Stencil FP is clean, but that is not a pending-queue dry-run. **Do not wire listing-only.**

### Outcome / significance (spot-check)

`outcome`: alternate_remedy 24, consumer 10, pending 6, none 4, licensee 4, split 2.

`significance`: ordinary 27, procedural 15, significant 8 (342, 351, 355, 367, 375, 376, 380, 385).

Stencil family stayed `alternate_remedy` / `ordinary`. Schema otherwise clean (`cited_by` strings, `provision` has `::`). Soft nits, not pipeline fails:

- SCJ-344 `outcome=consumer` on an interim s.135 stay + connection, listed after six weeks — closer to `pending`
- SCJ-356 `alternate_remedy` after the licensee **withdrew** the recovery and the Court only directed a hearing
- SCJ-342 `significant` / `consumer` on a 25-page s.420 quash that does construe 4.4 — keep

### Decisions for the next run

1. **Keep** stencil 6.5 as live. FP clean. ~7s vs ~100s short.
2. **Keep** short-uncited (3 pp / ≤1500 words / uncited). Do not tighten.
3. **Keep** words ≤ 800 even with a 4-page quash in this batch. Watch SCJ-376-class.
4. **Do not** turn on listing-only.
5. **Do not** widen BILL / RELEGATE into refusals, pending-representation, or 7.10.
6. **Loop:** stop after 3 stencil-write failures; do not burn `-Count` on one stuck caption.
7. Optional later: coerce missing `paras` to `""`; add `"current bill"` to BILL only if it recurs.
