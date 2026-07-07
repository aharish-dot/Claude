#!/usr/bin/env python3
"""
Stage 2 (draft): rank the harvested candidates and produce a shortlist of 200,
then report how much of the issue-space each cutoff (80/100/125/150/200) covers.

Ranking = composite score from FREE metadata only (no full text):
  + citation impact   z(log1p(numcitedby))     (log tames the Anis Ahmad outlier)
  + proposition breadth  #distinct issues the case touches
  + apex-court weight   SC > HC
  + currency           post-2003-Act bonus
  + core-relevance      matched the central 126/135 query
A mild diversity guard (per-court soft cap via redundancy penalty) keeps one
court from dominating. Non-topical and already-digested cases are dropped.

Coverage is reported under two lenses:
  BREADTH  = issue-nodes represented / 9      (saturates fast -> breadth is cheap)
  DEPTH    = per-issue citation-mass captured  (this is where N actually matters)
"""
import json, os, math, csv, statistics, collections

HERE = os.path.dirname(os.path.abspath(__file__))
recs = json.load(open(os.path.join(HERE, "candidates.json")))

ISSUES = ["126v135","assessment-126","mensrea-135","appeal-127",
          "jurisdiction-145-154","compounding-152","natural-justice",
          "provisional-final","burden-proof"]

# --- already-digested exclusions (by title; doc-ids unknown here) ---
ALREADY = ["Torrent Power"]  # HC-002; extend when other done-case ids are known

pool = [r for r in recs if r["topical"] and not any(a in r["title"] for a in ALREADY)]

# --- normalisation basis ---
logc = [math.log1p(r["numcitedby"]) for r in pool]
mu, sd = statistics.mean(logc), (statistics.pstdev(logc) or 1.0)
maxiss = max(len(r["issues"]) for r in pool)

def base_score(r):
    z = (math.log1p(r["numcitedby"]) - mu) / sd
    breadth = len(r["issues"]) / maxiss
    sc = 1.0 if r["court_type"] == "SC" else 0.0
    try:
        yr = int(r["date"][:4])
    except Exception:
        yr = 0
    currency = 1.0 if yr >= 2004 else 0.5
    core = 1.0 if "126v135" in r["issues"] else 0.0
    return 1.0*z + 0.6*breadth + 0.5*sc + 0.3*currency + 0.25*core

for r in pool:
    r["_base"] = base_score(r)

# --- greedy rank with per-court soft cap (redundancy penalty) ---
pool.sort(key=lambda r: -r["_base"])
court_count = collections.Counter()
ranked = []
remaining = pool[:]
# soft cap: after a court has C picks, its cases are penalised by step*over
SOFT_CAP, STEP = 8, 0.15
while remaining:
    best, bi = None, None
    for i, r in enumerate(remaining):
        over = max(0, court_count[r["court"]] - SOFT_CAP + 1)
        adj = r["_base"] - STEP*over*(0 if r["court_type"]=="SC" else 1)
        if best is None or adj > best:
            best, bi = adj, i
    r = remaining.pop(bi)
    r["_adj"] = best
    court_count[r["court"]] += 1
    ranked.append(r)

shortlist = ranked[:200]

# --- coverage metrics ---
# DEPTH denominator: total citation mass per issue across the WHOLE topical pool
mass = {i: 0.0 for i in ISSUES}
for r in pool:
    for i in r["issues"]:
        mass[i] += r["numcitedby"]

def coverage(N):
    top = ranked[:N]
    nodes = set()
    cap = {i: 0.0 for i in ISSUES}
    landmark_have = 0
    for r in top:
        for i in r["issues"]:
            nodes.add(i); cap[i] += r["numcitedby"]
    depth = [cap[i]/mass[i] if mass[i] else 1.0 for i in ISSUES]
    return {
        "breadth_pct": 100.0*len(nodes)/len(ISSUES),
        "depth_mean_pct": 100.0*statistics.mean(depth),
        "depth_min_pct": 100.0*min(depth),
        "sc": sum(1 for r in top if r["court_type"]=="SC"),
        "hc": sum(1 for r in top if r["court_type"]=="HC"),
        "courts": len(set(r["court"] for r in top)),
        "per_issue": {i: 100.0*(cap[i]/mass[i] if mass[i] else 1.0) for i in ISSUES},
    }

# also: landmark-tier recall (cases cited >=10 times)
land_total = sum(1 for r in pool if r["numcitedby"] >= 10)
def landmark_recall(N):
    return 100.0*sum(1 for r in ranked[:N] if r["numcitedby"]>=10)/land_total

print(f"Topical pool ranked: {len(pool)}  (SC {sum(r['court_type']=='SC' for r in pool)}, "
      f"HC {sum(r['court_type']=='HC' for r in pool)})")
print(f"Landmark-tier cases (citedby>=10) in pool: {land_total}\n")

print(f"{'N':>4} | {'SC':>3} {'HC':>4} {'#HC-courts':>10} | {'breadth':>7} | "
      f"{'depth(mean)':>11} {'depth(min)':>10} | {'landmark recall':>15}")
print("-"*90)
for N in [80,100,125,150,200]:
    c = coverage(N)
    print(f"{N:>4} | {c['sc']:>3} {c['hc']:>4} {c['courts']:>10} | "
          f"{c['breadth_pct']:>6.0f}% | {c['depth_mean_pct']:>10.1f}% {c['depth_min_pct']:>9.1f}% | "
          f"{landmark_recall(N):>14.1f}%")

print("\nPer-issue DEPTH (citation-mass captured) at each cutoff:")
hdr = "issue".ljust(22) + "".join(f"{N:>8}" for N in [80,100,125,150,200])
print(hdr); print("-"*len(hdr))
cov = {N: coverage(N) for N in [80,100,125,150,200]}
for i in ISSUES:
    row = i.ljust(22) + "".join(f"{cov[N]['per_issue'][i]:>7.0f}%" for N in [80,100,125,150,200])
    print(row)

# --- write shortlist files ---
def label(r):
    return "SC" if r["court_type"]=="SC" else "HC"
with open(os.path.join(HERE,"shortlist_200.csv"),"w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["rank","tid","court_type","court","date","numcitedby","numcites",
                "score","issues","title","headline"])
    for n,r in enumerate(shortlist,1):
        w.writerow([n,r["tid"],r["court_type"],r["court"],r["date"],
                    r["numcitedby"],r["numcites"],round(r["_adj"],3),
                    "|".join(r["issues"]),r["title"],r["headline"][:180]])

with open(os.path.join(HERE,"shortlist_200.md"),"w") as f:
    f.write("# Ranked shortlist — top 200 (Stage 2 draft)\n\n")
    f.write("Ranked by composite score (citation impact + proposition breadth + "
            "apex-court weight + currency), per-court soft cap applied. "
            "Non-topical and already-digested cases excluded.\n\n")
    f.write("| # | Ct | Court | Date | Cited | Issues | Case |\n|--:|--|--|--|--:|--|--|\n")
    for n,r in enumerate(shortlist,1):
        f.write(f"| {n} | {label(r)} | {r['court'].replace('|',' ')} | {r['date']} | "
                f"{r['numcitedby']} | {' '.join(r['issues'])} | {r['title'][:70]} |\n")
print("\nWrote shortlist_200.csv and shortlist_200.md")
