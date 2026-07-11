# Facet schema v0.1 — the "excel sheet" columns

The flat, one-row-per-order analytical layer ([`../data/orders.csv`](../data/orders.csv)).
**Freeze the controlled vocabularies below before coding at volume** — re-coding 100 rows after
an enum change is the expensive mistake. Free-text columns can evolve freely; enum columns should not.

## Columns

| # | column | type | notes |
|---|--------|------|-------|
| 1 | `case_id` | id | `OMB-NNN`, stable, never renumbered (mirrors HC/SC convention) |
| 2 | `representation_no` | text | official no., e.g. `C-19/2026`, `23/2026` |
| 3 | `order_date` | date | ISO; mark `(approx)` when inferred from file/hearing dates |
| 4 | `ombudsman` | text | adjudicator — enables per-adjudicator comparison |
| 5 | `discom` | enum* | `MVVNL` / `PVVNL` / `PuVVNL` / `DVVNL` / `KESCO` / … |
| 6 | `district` | text | |
| 7 | `petitioner` | text | |
| 8 | `petitioner_role` | text | Proprietor / Occupier / Owner / Society / … |
| 9 | `consumer_segment` | **enum** | see below |
| 10 | `tariff_category` | text | statutory code as stated: LMV-1, LMV-2, HV-2, MV-6 … |
| 11 | `sanctioned_load` | text | value + unit (KW/HP/KVA/kVAH); keep the unit |
| 12 | `connection_type` | **enum** | see below |
| 13 | `primary_subject` | **enum** | see below — *what the dispute is about* |
| 14 | `secondary_subjects` | list | `;`-separated, same vocab as primary |
| 15 | `procedural_posture` | **enum** | see below — *how the matter reached the forum* |
| 16 | `decided_on` | **enum** | see below — *the ground it turned on* ⟵ key axis |
| 17 | `disposition` | **enum** | see below — *the outcome verb* |
| 18 | `maintainability_holding` | enum | `Maintainable` / `Not maintainable` / `Not decided` |
| 19 | `amount_in_dispute` | text | value + what it is |
| 20 | `act_sections` | list | Electricity Act 2003 sections, `;`-separated |
| 21 | `supply_code_clauses` | list | U.P. Electricity Supply Code 2005 clauses |
| 22 | `regulations_cited` | list | CGRF & Ombudsman Regs; SoP Regs; etc. |
| 23 | `precedents_cited` | list | case names (feed the authorities ledger) |
| 24 | `key_provision_interpreted` | text | the single most load-bearing provision |
| 25 | `relief_granted` | text | what the consumer actually got (or None) |
| 26 | `ratio_short` | text | the holding / reusable rule in 1–2 sentences |
| 27 | `tags` | list | precedent-value slugs, `;`-separated |
| 28 | `source_pdf` | text | filename in `input/`/`processed/` |
| 29 | `ocr_confidence` | enum | `high` / `medium` / `low` — provenance honesty |

\* `discom` is semi-open: fixed list of the 5 UP discoms, but allow additions.

## Controlled vocabularies (v0.1 — proposed, please ratify)

**`consumer_segment`** — `Domestic` · `Commercial` · `Industrial` · `Institutional` · `Agricultural` · `Unknown`

**`connection_type`** — `Direct-metered` · `Single-point / deemed-franchisee` · `Prepaid` · `Temporary` · `Unmetered` · `Unknown`

**`primary_subject`** (grow deliberately; each addition is a schema decision):
- `Metering - defective / assessment` (incl. kVAH, MRI, multiplying-factor disputes)
- `Assessment - Theft / Unauthorised use` (s.126/135 territory)
- `Billing - tariff / charges`
- `Billing - Electricity Duty`
- `Load - change / sanctioned-load`
- `New connection / release`
- `Disconnection / reconnection`
- `Supply reliability / hours / quality`
- `Franchisee / single-point recovery`
- `Compensation (Standards of Performance)`
- `Non-compliance of prior order`
- `Security deposit / refund`
- `Other`

**`procedural_posture`**:
- `Appeal from CGRF (s.42(6))`
- `Non-compliance / execution (s.142)`
- `Review / recall of own order`
- `Direct complaint to Ombudsman`
- `Post-writ remand (HC liberty)`
- `Other`

**`decided_on`** ⟵ *the analytically decisive column*:
- `Merits`
- `Maintainability - subject-matter jurisdiction`
- `Maintainability - hierarchy / exhaustion`
- `Maintainability - procedure (limitation / review-power / form)`
- `Withdrawal`
- `Compliance / execution`
- `Remand`

**`disposition`**:
- `Allowed` · `Partly allowed` · `Dismissed` · `Dismissed as not maintainable` ·
  `Dismissed as withdrawn` · `Directed compliance` · `Remanded` · `Disposed with liberty`

**`tags`** — free but reuse slugs so they aggregate. Seen so far:
`theft-jurisdiction-bar`, `no-original-jurisdiction`, `appellate-only`, `exhaust-cgrf-first`,
`no-review-power`, `cpc-order-47-standard`, `consumer-definition-2(15)`, `deemed-franchisee-4.46`,
`no-profit-no-loss`, `sop-compensation-clause8`, `hc-liberty-no-jurisdiction`,
`electricity-duty-exemption`, `industrial-policy-2004`, `s142-enforcement`, `s142-noncompliance`,
`withdrawn-liberty`, `finality-of-orders`, `supply-hours`, `builder-society-recovery`,
`cgrf-order-compliance`, `forum-competence`.

## Design rules
1. **Separate *subject* from *disposition-basis*.** `primary_subject` = what it's about; `decided_on` = why it ended that way. They are independent and both matter.
2. **Structured citations, not prose.** Split Act / Supply-Code / Regulations / precedents into their own columns so they feed the authorities graph.
3. **Provenance honesty.** `ocr_confidence` travels with every row; low-confidence rows are flagged for human check.
4. **Enums are contracts.** Adding a value is fine; renaming/removing one means re-coding. Decide the vocab, then scale.
