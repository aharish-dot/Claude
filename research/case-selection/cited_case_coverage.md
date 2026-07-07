# Coverage check — cases cited in the three expert documents vs. the top 80

Cross-checked every court judgment cited across the three uploaded documents
(the two PDFs + the §126-vs-§135 practitioner markdown) against the harvested
pool and the ranked shortlist. Matching key = Indian Kanoon doc-id (exact),
title-keyword fallback, each match eyeballed against court/date.

Excluded from the check: bare-statute references; regulatory/CGRF/State-Commission
orders (Aasha Yadav, Jagdish Bihari, UPPCL v. Dr S.C. Katiyar); and the explicit
distractor the md itself flags — *Avinash Kumar Chauhan* (a Stamp Act case).

**34 distinct court judgments** are cited. Where they land:

| Bucket | Count | Cases |
|---|--:|---|
| **In top 80** | **7** | Anis Ahmad (#1), WBSEDCL v. Orion Metal (#16), Kerala SEB v. Thomas Joseph (#22), Shyam Lal Iron & Steel (#39), Mohit Paper Mills (#45), Hasi Mazumdar (#54), Ashok Kumar Maity (#74) |
| In 81–200 | 3 | Sandeep Kesarwani (#109), Tapan Sen Majumdar (#124), Etendra Kumar Gambhir (#168) |
| In pool but ranked >200 | 11 | **SOUTHCO v. Seetaram Rice Mill**, Md. Abdul Matin, CESC v. Appellate Authority, Brij Mohan Somani, Rakesh Singh, Castron Technologies, Hasimuddin, V. Swaminathan, Kalpana Agarwal, Vinod Sharma, Pintoo Singh |
| Not harvested at all | 13 | Asst. Engineer Ajmer VVNL v. **Rahamatullah Khan** (SC), **Radhey Shyam Bansal** v. BSES, **Illiyas Mangroo Shaikh** (Bom), Ashok Kumar v. State of U.P. (2008), Radha Krishna Cold Storage, **Paliwal Alloys**, Basudeb Paine, Vimla Tiwari, Naveen Kumar Jain (MP 2025), Awadesh S. Pandey, Vimla Kumari Pathak (2026), Sri Pradip Ghosh, Neptune Poly Foils |

**So 27 of the 34 cited cases are NOT in the current top 80.**

## What this means (it is not a simple failure)

The three docs cite cases the way a **practitioner** does — for a *specific
doctrinal or procedural point* (a 30-day-finalisation timeline, no-interest-on-
pre-deposit, §56(2) "first due", acquittal-vs-assessment) — regardless of how
often the case is cited. The shortlist ranks by **citation impact + proposition
breadth**. These are different lenses, so divergence is expected: the citation-
landmarks the docs *do* rely on (Anis Ahmad, Orion Metal, Thomas Joseph) are all
in the top 80. But three real gaps are exposed:

1. **A citation-count blind spot buries a foundational case.** *SOUTHCO v.
   Seetaram Rice Mill* (2012) 2 SCC 108 — the bedrock "no commonality between
   §126 and §135" authority — appears in Indian Kanoon (tid 43074463) with
   **citedby = 4**, so it ranks below 200. IK is undercounting/splitting its
   citations. **Action: force-include Seetaram**, and treat any expert-cited
   apex case as auto-in regardless of its IK citedby.

2. **Scope gaps beyond the query battery.** *Rahamatullah Khan* (§56(2)
   limitation / when a charge is "first due") and *Radhey Shyam Bansal* (§152
   compounding requires complainant consent) were never harvested — §56 was
   outside the section scope, and §152 is thin. Decision needed: add **§56(2)
   limitation** as a taxonomy node?

3. **Recency / relevance-depth gap.** Several 2022–2026 HC judgments
   (Naveen Kumar Jain, Vimla Kumari Pathak, Illiyas Mangroo Shaikh, Paliwal
   Alloys) are recent and lightly-cited, so they fall outside the relevance
   page-slice and the citedby tail. They matter for *current* practice.

## Recommended fix — treat the expert docs as a curated seed signal

Merge all 34 cited cases into the candidate pool, tag them **`expert-cited`**,
and add an `expert-cited` bonus to the composite score (an independent,
high-quality signal, per the agreed "union of independent signals" design).
Concretely:
- **Force-include** the citation-buried landmarks: Seetaram (and verify a
  higher-cited duplicate doc-id), plus any expert-cited SC case.
- **Fetch metadata** for the 13 not-harvested cases (doc-ids already known for
  several: Vimla Kumari Pathak 174495284, Sri Pradip Ghosh 147966866, and the
  citing-doc ids in the PDFs) and slot them into the pool.
- **Re-rank** with the `expert-cited` bonus, then re-cut the ~80.

This closes the gap without abandoning citation-ranking: the shortlist keeps the
citation-landmarks and now also guarantees every case these treatises actually
lean on is on the table.
