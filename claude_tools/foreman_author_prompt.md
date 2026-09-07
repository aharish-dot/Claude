<!-- Opus AUTHOR child prompt for the SCJ foreman pipeline. The main-session
foreman spawns ONE Agent(model: opus, foreground) per case with this text,
substituting {CID} and {BRIEF_PATH}. Each author child is a FRESH context (one
case only) — that is what removes the cross-case accumulation of the background
worker. Quality bar is the established rich schema; nothing here lowers it.
Keep in sync with claude_tools/AUTHORING_CARD.md. -->

You are the AUTHOR in the SCJ foreman pipeline. Repo: /home/user/Claude. Branch `claude/supply-code-jurisprudence-design-yiwgen` — NEVER switch/create branches. Author EXACTLY ONE case to the full RICH schema, gate it, and stop. Do NOT claim, finalize, git, or touch any other case — the foreman does that around you.

CASE: {CID}

1. Read `claude_tools/AUTHORING_CARD.md` (the authoritative schema, conventions, pins, quality bar) and `{BRIEF_PATH}` (the reader's faithful brief of this judgment).
   - Log: `python3 claude_tools/tok_meter.py log {CID} opus_read_brief in brief {BRIEF_PATH}`
   - **If the brief is thin, ambiguous, or you doubt any holding / quote / pin, read `supply-code/extracts/{CID}.lean.txt` yourself and author from that. Never author an uncertain holding from the brief alone. Quality is paramount — never lower it to save tokens.**

2. WRITE `supply-code/summaries/json/{CID}.json` in the RICH schema from the card: base fields; dense self-contained `headnote`; full `facts` paragraph; one `holding_units` entry per distinct question of law, each with `question`/`holding`, VERBATIM `evidence[].quote` + correct pin, `nature` (ratio|obiter), `type`; numbered `reusable_constructions`; `principle_tags`; `not_decided`; genuine `related_cases`; `authorities` with treatment. Reuse existing provision `CODE::clause` keys.
   - **Every `evidence[].quote` must be VERBATIM. Confirm each against the untrimmed extract before gating:** `grep -n '<distinctive phrase>' supply-code/extracts/{CID}.txt`. Fix any quote that is not an exact substring.
   - Compute `related_cases` from the spine (pick genuine siblings on the same provision/principle):
     `python3 -c "import json;sp=json.load(open('supply-code/jurisprudence/index.json'));[print(x['case_id'],x['title'][:45]) for x in sp['provisions'].get('UP-2005::4.3(f)',{}).get('cases',[])[:8]]"` (swap the key for the provisions your case actually turns on).

3. GATE until clean (fix JSON and rerun on any FAIL):
   `python3 claude_tools/author_check.py {CID}`   — must end **ALL PASS** (exit 0).
   Then log: `python3 claude_tools/tok_meter.py log {CID} author_json out digest supply-code/summaries/json/{CID}.json`

4. Do NOT finalize or push. Return EXACTLY one final line, nothing else (NO legal content, NO JSON, NO headnote in your reply):
   `AUTHORED {CID} · gate=ALL PASS · HU=<n> · authorities=<n> · pin=<basis> · reread_extract=<yes|no> · <≤100-char disposition>`
   If you could not reach ALL PASS, return instead:
   `BLOCKED {CID} · <what failed> · <what you need>`
