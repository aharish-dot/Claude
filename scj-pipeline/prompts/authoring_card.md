# SCJ authoring card

Load this **once per session**, then apply it to each case on the worklist. It is
the entire instruction set for the analytical step — everything else (PDF text,
metadata, IDs, validation) is done for you by `pipeline.py`.

You are summarising Indian High Court judgments (mostly Allahabad HC electricity /
U.P. Electricity Supply Code, 2005 matters) into a structured JSON catalog. The
gold-standard quality bar is `examples/SCJ-3166.json` — match its density,
neutrality and precision.

## The loop (per worklist item)

1. **Read** the lean text file (`data/extracts/<case_id>.txt`). It is the whole
   judgment, de-boilerplated. It may concatenate several orders (a listing order
   plus the disposal) — summarise the **operative disposal**, not the listing.
2. **Open** the skeleton (`data/out/<case_id>.json`). Its metadata block is already
   filled from the PDF. **Trust it, but fix anything the text contradicts** (and
   note the fix in `qa.flags`). Resolve every item already sitting in `qa.flags`
   (e.g. "confirm the operative disposal date").
3. **Fill** every analytical field (below), editing the JSON in place.
4. **Set** `model` to your model name, `qa.confidence` to `high|medium|low`, and
   `qa.authored_by`. Leave `data/out/<case_id>.json` as valid JSON.
5. Move to the next item. **Do not** paste the whole judgment back into chat or
   re-summarise prior cases — write straight to the file to conserve context.

## Fields to author

- **date_display** — human form of `date_of_judgment` (e.g. "6 April 2016").
- **significance** — `landmark` | `significant` | `routine` (precedential weight).
- **outcome** — who prevailed in the disposal: `consumer` | `licensee` |
  `mixed` | `remanded` | `other`.
- **disposition** — the operative order in one sentence (what was allowed/quashed/
  directed). Concrete: name the citation/amount/date quashed and any directions.
- **headnote** — the ratio as a dense, self-contained paragraph a lawyer could cite
  from. State the rule, the controlling provisions, and the lead authority. Past
  tense for what the court held.
- **facts** — neutral narrative: parties, the impugned action, the rival contentions.
  No argument, no conclusion. (See the gold example's two-paragraph shape.)
- **holding_units[]** — one per provision actually decided. Each:
  - `provision` — catalog key `CODE::clause` (see conventions).
  - `code`, `clause` — human forms (e.g. "U.P. Electricity Supply Code, 2005",
    "6.8(1)(b)").
  - `type` — `supply_code` | `electricity_act` | `constitution` | `other`.
  - `topic` — short phrase naming the point.
  - `question` — the legal question in one line.
  - `holding` — the court's answer with reasoning, self-contained.
  - `paras` — paragraph numbers relied on (e.g. "6, 8-9").
  - `flag` — *optional*; any caveat (odd clause numbering, source concatenation,
    mismatch between the facts and the cited authority, etc.).
- **reusable_constructions[]** — portable statements of law (`construction` + `paras`)
  that could be reused as a proposition in another case.
- **principle_tags[]** — each: a kebab-case `tag`, an `application` sentence tying it
  to this case, `lead_authorities` (`name` + `docid` when known, else `""`), `paras`.
- **not_decided[]** — points expressly left open: `point`, `note`, `paras`.
- **authorities[]** — every case/authority cited: `name`, `citation`, `court`,
  `docid` (only if you actually know it — never invent), `proposition`,
  `cited_by` (`Petitioner`|`Respondent`|`Court`), `treatment`
  (`Followed`|`Relied on`|`Distinguished`|`Referred`|`Overruled`).

## Conventions & hard rules

- **Catalog keys.** Supply Code → `UP-2005::<clause>` (e.g. `UP-2005::6.8(b)`).
  Electricity Act 2003 → `EA2003::<section>` (e.g. `EA2003::126(3)`). Keep the key
  stable even when the source's clause punctuation varies.
- **Never silently correct** a clause/section number that looks off — keep what the
  court wrote and record the discrepancy in `flag`.
- **Never invent** authorities, citations, `docid`s, dates or amounts. If the text
  does not support a value, leave it `""`/`[]` and add a `qa.flags` note.
- **Paras** are the sequential blocks of the operative order (count from the first
  substantive paragraph, e.g. "Heard learned counsel …").
- **Stay in the record.** Summarise only what the judgment decides; do not import
  outside law. Merits the court did not reach belong in `not_decided`, not `holding_units`.
- **Confidence.** `high` = clear judgment fully captured; `medium` = some ambiguity
  (note it); `low` = extract truncated/garbled or reasoning unclear — flag and keep
  the fields you are sure of.

## Output contract

Each `data/out/<case_id>.json` must pass `python pipeline.py validate --all`:
non-empty `disposition`, `headnote`, `facts`, `title`, `court`,
`date_of_judgment` (YYYY-MM-DD); at least one complete `holding_unit`; every
authority named; `model` not `PENDING`. Warnings (short headnote, non-standard
catalog key) are advisory — resolve or justify them.
