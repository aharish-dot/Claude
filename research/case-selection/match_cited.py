#!/usr/bin/env python3
"""Match cases cited in the three uploaded documents against the shortlist.
Reports, for each cited case: is it in top-80 / 81-200 / pool-below-200 / not
harvested at all. Matching key = IK doc-id (exact) with title-keyword fallback.
"""
import json, os, csv, re

HERE = os.path.dirname(os.path.abspath(__file__))
pool = json.load(open(os.path.join(HERE, "candidates.json")))
by_tid = {r["tid"]: r for r in pool}

# rank map from shortlist_200.csv
rank = {}
with open(os.path.join(HERE, "shortlist_200.csv")) as f:
    for row in csv.DictReader(f):
        rank[int(row["tid"])] = int(row["rank"])

def norm(s): return " " + re.sub(r"[^a-z0-9]+", " ", s.lower()).strip() + " "
titles = [(r["tid"], norm(r["title"])) for r in pool]

def find_by_keywords(kws, court=None):
    """pool tids whose title contains ALL keywords (word-boundary), court-preferred"""
    ks = [" " + re.sub(r"[^a-z0-9]+", " ", k.lower()).strip() + " " for k in kws]
    ks = [k.strip() for k in ks]
    hits = [tid for tid, t in titles if all((" "+k+" ") in t or t.strip().startswith(k+" ")
                                            or (k in t) for k in ks)]
    if court in ("SC", "HC") and len(hits) > 1:
        pref = [h for h in hits if by_tid[h]["court_type"] == court]
        if pref:
            hits = pref + [h for h in hits if h not in pref]
    return hits

# --- cases cited across the three documents ---
# (name, court, docid-or-None, [fallback title keywords])
CITED = [
    # ---- Supreme Court ----
    ("SOUTHCO v. Seetaram Rice Mill (2012)", "SC", 43074463, ["seetaram"]),
    ("UPPCL v. Anis Ahmad (2013)", "SC", 55216283, ["anis", "ahmad"]),
    ("WBSEDCL v. Orion Metal (2020)", "SC", None, ["orion", "metal"]),
    ("Kerala SEB v. Thomas Joseph (2022)", "SC", 12823358, ["thomas", "joseph"]),
    ("Asst. Engineer Ajmer VVNL v. Rahamatullah Khan (2020)", "SC", None, ["rahamatullah"]),
    ("Radhey Shyam Bansal v. BSES Rajdhani", "SC/HC", None, ["radhey", "shyam", "bansal"]),
    # Avinash Kumar Chauhan is an explicit DISTRACTOR (Stamp Act) -> excluded on purpose
    # ---- High Courts ----
    ("Md. Abdul Matin v. WBSEDCL (Cal 2023)", "HC", None, ["abdul", "matin"]),
    ("Ashok Kumar Maity v. WBSEB (Cal 2022)", "HC", 108624484, ["maity"]),
    ("Tapan Sen Majumdar v. WBSEDCL (Cal 2022)", "HC", 107836520, ["tapan", "sen"]),
    ("CESC Ltd v. Appellate Authority (Cal 2023)", "HC", 172148038, ["cesc", "appellate"]),
    ("Brij Mohan Somani v. State of Odisha (Orissa 2023)", "HC", None, ["brij", "mohan", "somani"]),
    ("Etendra Kumar Gambhir v. MPMKVVCL (MP 2025)", "HC", 160281331, ["etendra"]),
    ("Illiyas Mangroo Shaikh v. BEST (Bombay)", "HC", None, ["illiyas"]),
    ("Sandeep Kesarwani v. State of U.P. (All 2014)", "HC", None, ["sandeep", "kesarwani"]),
    ("Rakesh Singh v. State of U.P. (All 2019)", "HC", 51255397, ["rakesh", "singh"]),
    ("M/s Mohit Paper Mills v. PVVNL (All 2011)", "HC", 57045694, ["mohit", "paper"]),
    ("Ashok Kumar v. State of U.P. (All 2008)", "HC", None, ["ashok", "kumar", "u p"]),
    ("Radha Krishna Cold Storage v. State of U.P. (All)", "HC", None, ["radha", "krishna", "cold"]),
    ("Paliwal Alloys v. UPPCL (All 2009)", "HC", None, ["paliwal"]),
    ("Basudeb Paine v. WBSEDCL (Cal)", "HC", None, ["basudeb", "paine"]),
    ("Smt. Vimla Tiwari v. State of U.P. (All 2012)", "HC", None, ["vimla", "tiwari"]),
    ("Naveen Kumar Jain v. MPMKVVCL (MP 2025)", "HC", None, ["naveen", "jain"]),
    ("Awadesh S. Pandey v. Tata Power (Bom)", "HC", None, ["awadesh", "pandey"]),
    ("Castron Technologies v. DVC (2022)", "HC", 176037461, ["castron"]),
    ("Hasi Mazumdar v. WBSEB (Cal 2005)", "HC", None, ["hasi", "mazumdar"]),
    ("M/s Shyam Lal Iron & Steel v. Jharkhand SEB (Jhk 2013)", "HC", None, ["shyam", "lal", "iron"]),
    ("Hasimuddin v. State of U.P. (All 2020)", "HC", None, ["hasimuddin"]),
    ("Vimla Kumari Pathak v. Tata Power Delhi (2026)", "HC", 174495284, ["vimla", "kumari"]),
    ("V. Swaminathan v. Superintending Engineer (2018)", "HC", 197023991, ["swaminathan"]),
    ("Sri Pradip Ghosh v. State of W.B. (2022)", "HC", 147966866, ["pradip", "ghosh"]),
    ("Kalpana Agarwal v. Western Electricity (All 2019)", "HC", None, ["kalpana", "agarwal"]),
    ("Neptune Poly Foils v. Madhyanchal (All 2015)", "HC", None, ["neptune"]),
    ("Vinod Sharma v. UPPCL (Lko 2013)", "HC", None, ["vinod", "sharma"]),
    ("Pintoo Singh v. State of U.P. (All 2016)", "HC", None, ["pintoo"]),
]

def bucket(tid):
    if tid in rank:
        r = rank[tid]
        return ("TOP-80" if r <= 80 else "81-200"), r
    if tid in by_tid:
        return "POOL(>200)", None
    return "NOT-HARVESTED", None

print(f"{'Case':52} {'Ct':3} {'Status':13} {'rank':>4}  matched")
print("-"*100)
summary = {"TOP-80":0,"81-200":0,"POOL(>200)":0,"NOT-HARVESTED":0}
notin80 = []
for name, court, docid, kws in CITED:
    tid = None; how = ""
    if docid and docid in by_tid:
        tid = docid; how = f"docid {docid}"
    else:
        hits = find_by_keywords(kws, court)
        if hits:
            tid = hits[0]; how = f"title~ tid {tid}" + (f" (+{len(hits)-1})" if len(hits)>1 else "")
        elif docid:
            how = f"docid {docid} NOT in pool"
        else:
            how = "no match"
    if tid is not None:
        st, r = bucket(tid)
        m = by_tid[tid]
        mt = f"{m['court_type']} {m['date']} cby={m['numcitedby']} :: {m['title'][:44]}"
    else:
        st, r = ("NOT-HARVESTED", None); mt = ""
    summary[st] += 1
    if st != "TOP-80":
        notin80.append((name, court, st, how))
    print(f"{name[:46]:46} {st:13} {str(r or ''):>4} | {mt}")

print("\n=== SUMMARY ===")
for k in ["TOP-80","81-200","POOL(>200)","NOT-HARVESTED"]:
    print(f"  {k:13}: {summary[k]}")
print(f"\nCited cases NOT in the top 80 ({len(notin80)}):")
for name, court, st, how in notin80:
    print(f"  [{st:13}] {court:3} {name}  ({how})")
