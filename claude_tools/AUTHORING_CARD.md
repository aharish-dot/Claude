# SCJ rich-authoring card (lean, self-contained)

Everything needed to author ONE rich digest without opening the handoff or an
exemplar. Branch (never leave it): `claude/supply-code-jurisprudence-design-yiwgen`.
Turn-based: one worker at a time. `model` and `source_file` are set by finalize;
your commits carry the trailer at the bottom.

## Two-tier flow per case (keep it to few tool calls)
1. **prep (bash, 1 call)** — claim, compact, meter:
   ```
   OUT=$(python3 claude_tools/scj_claude.py claim --next 2>&1); echo "$OUT"
   CID=$(echo "$OUT" | grep -oE 'SCJ-[0-9]+' | head -1)
   MODE=$(echo "$OUT" | grep -oE 'mode=[a-z]+' | head -1 | cut -d= -f2)
   [ "$MODE" = new ] || { echo "STOP mode=$MODE"; }   # only NEW here; upgrades deferred
   python3 claude_tools/lean_extract.py "$CID"
   python3 claude_tools/tok_meter.py note "$CID" claim out claim_stdout ${#OUT}
   ```
2. **read (SONNET sub-agent)** — delegate the reading to a cheaper model. Spawn an
   Agent with `model: sonnet`, run in foreground, told to read
   `supply-code/extracts/<CID>.lean.txt` and WRITE a faithful brief to
   `<scratch>/<CID>.brief.md` per **Brief spec** below, and to meter it:
   `tok_meter.py log <CID> sonnet_read in lean supply-code/extracts/<CID>.lean.txt`
   and `tok_meter.py log <CID> sonnet_brief out brief <scratch>/<CID>.brief.md`.
3. **author (YOU, opus)** — Read `<CID>.brief.md` (log:
   `tok_meter.py log <CID> opus_read_brief in brief <scratch>/<CID>.brief.md`), then
   WRITE `supply-code/summaries/json/<CID>.json` in the **schema** below. You may
   `grep -n` the ORIGINAL `supply-code/extracts/<CID>.txt` to lift/confirm any exact
   quote. **If the brief is thin or you doubt it, read the lean extract yourself and
   author from that — never lower quality to save tokens.**
4. **gate + finalize (bash, 1 call)**:
   ```
   python3 claude_tools/author_check.py "$CID" || { echo GATE_FAIL; }   # fix & rerun if FAIL
   python3 claude_tools/tok_meter.py log "$CID" author_json out digest supply-code/summaries/json/$CID.json
   export CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
   python3 claude_tools/scj_claude.py finalize "$CID" > <scratch>/fin.log 2>&1; echo "exit=$?"
   python3 claude_tools/tok_meter.py log "$CID" finalize out finalize_stdout <scratch>/fin.log
   tail -3 <scratch>/fin.log     # confirm STATUS + push
   ```
   If finalize's push was rejected: `git fetch origin <BR>; git rebase origin/<BR>;
   python3 tools/build_supply_code.py; python3 tools/build_scj_catalog.py;
   git add supply-code/jurisprudence supply-code/state; git commit -m ... ; git push`.

## Brief spec (what the SONNET reader must produce — EXTRACT, don't interpret)
A markdown file with these sections, faithful and verbatim where quoted:
- **META**: court; bench (Single Judge/Division Bench); coram (exact, as on the
  delivered judgment); date_of_judgment (ISO) + display; docket (full, incl.
  connected petitions); page_count; whether the source has printed page numbers,
  numbered paragraphs, or is an order-sheet (→ pin_basis hint).
- **DISPOSITION**: the final operative order, verbatim or near-verbatim.
- **PAGE MAP**: one line per printed page ("p.7: clause 4.41 reproduced; …") so pins
  are groundable.
- **KEY PASSAGES**: a generous set of VERBATIM excerpts carrying every distinct
  holding / reason / clause-reproduction, each tagged with its page (or order-date).
  Copy exactly; do not paraphrase; when unsure whether a passage matters, include it.
- **AUTHORITIES**: every case/statute cited — name, citation, who cited it, how
  treated (verbatim treatment word if stated).
- **LEFT OPEN**: any point the court expressly did not decide.

## RICH schema (fields authored by you)
Base: `case_id, title, neutral_citation` (may be ""), `court, bench, coram,
date_of_judgment` (YYYY-MM-DD), `date_display, docket, page_count` (int),
`significance` (significant|ordinary|procedural), `outcome`
(consumer|licensee|alternate_remedy|pending|none|split), `disposition, headnote,
facts`. Rich additions:
- `source_file` — source PDF basename (finalize also sets it from the ticket).
- `pin_basis` — `page` (printed page numbers present; pins render `p. N`), `date`
  (order-sheets/contempt, no page numbers; pins like `order of 28.04.2010`), or
  `paragraph` (numbered ¶; pins `¶ N`). **Pins MUST be groundable in the source the
  reader opens — never invent reporter page numbers not in the PDF.**
- `reusable_constructions` — `[{construction, paras}]`, numbered portable propositions
  ("what to cite this for").
- `holding_units` — `[{provision "CODE::clause", code, clause, topic, type, nature,
  question, holding, evidence:[{quote, paras}], paras, qualifier?, flag?}]`.
  `nature` = `ratio`|`obiter`. `type` = `supply_code`|`electricity_act`|`interplay`.
  Each `evidence.quote` is VERBATIM from the extract (author_check greps it).
- `principle_tags` — `[{tag (kebab-case), application, lead_authorities:[{name,docid}],
  paras}]` (`lead_authorities` may be []).
- `not_decided` — `[{point, note, docid, paras}]`.
- `related_cases` — `[{case_id, note}]`, prior SCJ cases sharing a provision/tag.
  Compute from the spine:
  `python3 -c "import json;sp=json.load(open('supply-code/jurisprudence/index.json'));[print(x['case_id'],x['title'][:45]) for x in sp['provisions'].get('UP-2005::4.3(f)',{}).get('cases',[])[:8]]"`
- `authorities` — `[{name, citation, court, docid, proposition, how_treated,
  how_treated_paras, cited_by, treatment}]`.

Rules author_check enforces: every `paras` is a STRING; `cited_by` is a STRING;
`lead_authorities` items are `{name,docid}`; `provision` is `CODE::clause`; NO
`limiting_facts`; each holding has ≥1 verbatim `evidence` quote; `nature` set.

## Conventions (use existing keys so the spine stays consistent)
CODE prefixes → full `code` string (electricity-relevant, common first):
- `UP-2005` = U.P. Electricity Supply Code, 2005  (the main one)
- `EA2003` = Electricity Act, 2003
- `UP-2002` = U.P. Electricity Supply Code, 2002
- `EA1999(UP)` = U.P. Electricity Reforms Act, 1999
- `ESA1948` = Electricity (Supply) Act, 1948 · `IEA1910` = Indian Electricity Act, 1910
- `UPGEU1958` = U.P. Government Electrical Undertakings (Dues Recovery) Act, 1958
- `URUA1966` = U.P. Industrial Undertaking (Special Provisions for Prevention of Unemployment) Act, 1966
- `IBC` = Insolvency and Bankruptcy Code, 2016 · `CA1956` = Companies Act, 1956
- `CPC` = Code of Civil Procedure, 1908 · `NIACT` = Negotiable Instruments Act, 1881
- other-state codes: `BIHAR-2007`, `JH-2005`, `WB-2004`. Use `OFFTOPIC::<slug>` only
  when a holding is genuinely outside electricity supply law.
`type`: supply_code | electricity_act | interplay.  `nature`: ratio | obiter.
`treatment` (authorities): Followed | Referred | Relied on | Distinguished | Applied |
Overruled | Doubted | Affirmed.  `cited_by`: Court | Petitioner | Respondent | Applicant.

## Quality bar (do not compromise)
- `headnote`: dense, self-contained, multi-sentence — states each holding + the key
  reasoning and result, readable without the judgment.
- `facts`: a full paragraph of the material facts, dates, parties.
- One `holding_unit` per distinct question of law; frame `question`/`holding` crisply;
  ground each with a verbatim `evidence` quote + correct pin; mark ratio vs obiter.
- `reusable_constructions`: the portable propositions, numbered, quotable.
- `related_cases`: pick genuine spine siblings on the same provision/principle.

## Mini-example (shape only — abbreviated real holding)
```json
{
  "provision": "UP-2005::4.49",
  "code": "U.P. Electricity Supply Code, 2005",
  "clause": "4.49 (unamended, as on 31.3.2005) r/w 4.41(b),(e)",
  "topic": "Load-reduction stands approved on the licensee's decision; only ministerial steps remain",
  "type": "supply_code", "nature": "ratio",
  "question": "Where the licensee decided to reduce load on a complete application, does the reduction stand approved and from when is it effective?",
  "holding": "Yes. The competent authority decided the reduction on 19.4.2006 ... effective under Clause 4.41(e) from the first day of the following month, i.e. 1.5.2006 ...",
  "evidence": [{"quote": "the reduction of the load of the petitioner stood approved on 19.4.2006 and any further action which was to be taken by the respondents thereafter was only ministerial", "paras": "20"}],
  "paras": "18-20",
  "flag": "Source not paragraph-numbered; pins are printed page numbers."
}
```
principle_tag: `{"tag":"load-reduction-stands-approved-on-licensee-decision","application":"...","lead_authorities":[],"paras":"18-20"}`

## Provenance (every commit you make)
```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01FPhAi1amQo6vBtPTXVG2Zt
```
