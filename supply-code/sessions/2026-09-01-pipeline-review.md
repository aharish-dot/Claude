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

- [ ] `python tools/log_scj_review.py --summary` — elapsed by authoring; coerce rate; how many `short-uncited` and stencil.
- [ ] **Stencil false positives:** for every `authoring=stencil` in the batch, skim extract vs JSON. Fail if the court refused 6.5, listed the matter, withdrew, or decided the bill.
- [ ] **Short-uncited that should have been full:** 3-page uncited orders that actually construe a clause (quash / set aside / per incuriam). If more than a couple, tighten the gate.
- [ ] **6.5 clones still on short:** 1–2 page “apply under 6.5” with a bill/demand that did *not* stencil. If several, the regex is still short; do not widen into refusals to chase them.
- [ ] **Coerce rate:** if most short cases still coerce `paras` / `not_decided`, the prompt types did not stick (output was still saved; time save came from finalize, not from fewer Grok turns).
- [ ] **SCJ-328-class:** any 4-page uncited doctrinal quash must still be `gate=full`.

Do not turn on listing-only from this review unless the stencil-FP check is clean *and* a separate dry-run on the pending queue agrees.
