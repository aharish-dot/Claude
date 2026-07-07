#!/usr/bin/env python3
"""
Stage 1 harvest for the Electricity Act s.126/s.135 jurisprudence project.

Runs a battery of targeted Indian Kanoon searches (SC near-exhaustive + HC
issue-specific), unions results by doc-id, and keeps ONLY free metadata that
every search result already carries (title, court, date, numcites, numcitedby,
headline snippet). Reads zero full judgments.

Each candidate is tagged with which query/queries matched it -> a free,
per-case issue fingerprint used later for proposition-clustering (Stage 2).

Outputs (in this folder):
  raw/<label>_p<page>.json  cached raw API pages (so re-runs are free)
  candidates.json           unioned candidate records
  candidates.csv            flattened sheet for human review
"""
import json, os, sys, time, urllib.parse, subprocess, collections

TOKEN = os.environ.get("IK_API_TOKEN", "fd1bec72318f3a4a711b3d54a1008d86a5a44338")
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

# ---- query battery -------------------------------------------------------
# (label, base_query, doctypes, maxpages, issue_tag)
# issue_tag maps the query to a taxonomy node so matches self-cluster.
QUERIES = [
    # --- Supreme Court: near-exhaustive (universe ~68) ---
    ("sc_core",      'electricity ("section 126" ORR "section 135")', "supremecourt", 10, "126v135"),
    ("sc_127",       'electricity "section 127" appeal',              "supremecourt", 5,  "appeal-127"),
    ("sc_152",       'electricity "section 152" compounding',         "supremecourt", 5,  "compounding-152"),
    ("sc_145_154",   'electricity "section 145" ORR "section 154"',   "supremecourt", 5,  "jurisdiction-145-154"),
    ("sc_assess",    'electricity assessment "unauthorised use"',     "supremecourt", 5,  "assessment-126"),
    ("sc_theft",     'electricity theft dishonest intention',         "supremecourt", 5,  "mensrea-135"),

    # --- High Courts: issue-specific, ranked later by numcitedby ---
    ("hc_135",       '"section 135" electricity theft',               "highcourts", 25, "mensrea-135"),
    ("hc_126",       '"section 126" electricity "unauthorised use"',  "highcourts", 25, "assessment-126"),
    ("hc_126v135",   'electricity ("section 126" ORR "section 135")', "highcourts", 25, "126v135"),
    ("hc_127",       'electricity "section 127" appeal pre-deposit',  "highcourts", 15, "appeal-127"),
    ("hc_152",       'electricity "section 152" compounding',         "highcourts", 15, "compounding-152"),
    ("hc_145_154",   'electricity "section 145" ORR "section 154" special court', "highcourts", 15, "jurisdiction-145-154"),
    ("hc_hearing",   'electricity assessment "opportunity of hearing" natural justice', "highcourts", 15, "natural-justice"),
    ("hc_provisional",'electricity "provisional assessment" "final assessment"', "highcourts", 10, "provisional-final"),
    ("hc_burden",    'electricity theft "burden of proof" presumption', "highcourts", 10, "burden-proof"),
]

def api_search(base, doctypes, pagenum):
    # IMPORTANT: the +doctypes token must use a LITERAL '+' (not %2B), so we
    # url-encode only the base query and append the filter unencoded.
    # Shell out to curl: the agent proxy accepts curl but 403s python-urllib.
    fi = urllib.parse.quote(base) + "+doctypes:" + doctypes
    url = f"https://api.indiankanoon.org/search/?formInput={fi}&pagenum={pagenum}"
    out = subprocess.run(
        ["curl", "-sS", "-X", "POST", url,
         "-H", f"Authorization: Token {TOKEN}"],
        capture_output=True, text=True, timeout=90)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip()[:200])
    return json.loads(out.stdout)

def harvest():
    records = {}         # tid -> record
    tag_map = collections.defaultdict(set)   # tid -> set(issue_tag)
    query_map = collections.defaultdict(set) # tid -> set(query label)
    pages_fetched = 0

    for label, base, doctypes, maxpages, tag in QUERIES:
        total = None
        for p in range(maxpages):
            cache = os.path.join(RAW, f"{label}_p{p}.json")
            if os.path.exists(cache):
                d = json.load(open(cache))
            else:
                try:
                    d = api_search(base, doctypes, p)
                except Exception as e:
                    print(f"  ! {label} p{p} error: {e}")
                    break
                json.dump(d, open(cache, "w"))
                pages_fetched += 1
                time.sleep(0.3)
            docs = d.get("docs", [])
            if total is None:
                total = d.get("found")
                print(f"[{label}] found={total}")
            if not docs:
                break
            for x in docs:
                if x.get("doctype") == 1:   # skip Acts/laws
                    continue
                tid = x["tid"]
                tag_map[tid].add(tag)
                query_map[tid].add(label)
                if tid not in records:
                    src = x.get("docsource", "") or ""
                    records[tid] = {
                        "tid": tid,
                        "title": x.get("title", ""),
                        "court": src,
                        "court_type": "SC" if "Supreme Court" in src else "HC",
                        "date": x.get("publishdate", ""),
                        "numcites": x.get("numcites", 0),
                        "numcitedby": x.get("numcitedby", 0),
                        "headline": (x.get("headline", "") or "").replace("\n", " ").strip(),
                    }
            # stop early if fewer than a full page (exhausted this query)
            if len(docs) < 10:
                break

    # attach fingerprints + a cheap topicality flag
    ELEC = ("electric", "energy", "power corp", "power company", "vidyut", "vij",
            "bijli", "board", "meter", "tariff", "discom", "distribution", "consumer",
            "vvnl", "vpnl", "pvvnl", "mseb", "kseb", "gseb", "supply")
    for tid, rec in records.items():
        rec["issues"] = sorted(tag_map[tid])
        rec["matched_queries"] = sorted(query_map[tid])
        blob = (rec["title"] + " " + rec["headline"]).lower()
        rec["topical"] = any(w in blob for w in ELEC)

    print(f"\nPages fetched this run: {pages_fetched}")
    return list(records.values())

def main():
    recs = harvest()
    recs.sort(key=lambda r: (r["court_type"] != "SC", -r["numcitedby"]))
    json.dump(recs, open(os.path.join(HERE, "candidates.json"), "w"), indent=1)

    # CSV
    import csv
    cols = ["tid", "court_type", "court", "date", "numcitedby", "numcites",
            "topical", "issues", "matched_queries", "title", "headline"]
    with open(os.path.join(HERE, "candidates.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in recs:
            w.writerow([r["tid"], r["court_type"], r["court"], r["date"],
                        r["numcitedby"], r["numcites"], r["topical"],
                        "|".join(r["issues"]), "|".join(r["matched_queries"]),
                        r["title"], r["headline"][:200]])

    # summary
    sc = [r for r in recs if r["court_type"] == "SC"]
    hc = [r for r in recs if r["court_type"] == "HC"]
    print(f"\n=== CANDIDATE POOL ===")
    print(f"Total unique candidates: {len(recs)}  (SC={len(sc)}, HC={len(hc)})")
    print(f"SC topical: {sum(r['topical'] for r in sc)} / {len(sc)}")
    print(f"HC topical: {sum(r['topical'] for r in hc)} / {len(hc)}")
    import collections as C
    cc = C.Counter(r["court"] for r in hc)
    print("HC court spread (top 12):")
    for k, v in cc.most_common(12):
        print(f"  {v:>3}  {k}")
    print("Issue coverage (candidates tagged per node):")
    ic = C.Counter()
    for r in recs:
        for i in r["issues"]:
            ic[i] += 1
    for k, v in ic.most_common():
        print(f"  {v:>4}  {k}")

if __name__ == "__main__":
    main()
