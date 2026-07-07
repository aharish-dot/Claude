#!/usr/bin/env python3
"""Match cases cited in the two OCR'd commentary books against pool + top-80."""
import json, os, csv, re
HERE=os.path.dirname(os.path.abspath(__file__))
pool=json.load(open(os.path.join(HERE,"candidates.json")))
by_tid={r["tid"]:r for r in pool}
rank={}
with open(os.path.join(HERE,"shortlist_200.csv")) as f:
    for row in csv.DictReader(f): rank[int(row["tid"])]=int(row["rank"])
def norm(s): return " "+re.sub(r"[^a-z0-9]+"," ",s.lower()).strip()+" "
titles=[(r["tid"],norm(r["title"])) for r in pool]
def find(kws,court=None):
    ks=[k.lower() for k in kws]
    hits=[tid for tid,t in titles if all((" "+k+" ") in t or k in t for k in ks)]
    if court and len(hits)>1:
        pref=[h for h in hits if by_tid[h]["court_type"]==court]
        if pref: hits=pref+[h for h in hits if h not in pref]
    return hits

# (display name, citation, court, [keywords]) — cleaned from OCR
BOOK=[
 ("Bihar SEB, Patna v. Snehlata Gupta","AIR 2015 Pat 129","HC",["snehlata"]),
 ("K. Dominic v. Asst. Exec. Engineer, TNEB","AIR 2023 Mad 33","HC",["dominic"]),
 ("N.B. Hi-Tech Industries v. TNEB","AIR 2006 (NOC) 557 Mad","HC",["hi tech industries"]),
 ("Ayyanar v. State Electricity Board","2009 (1) JCR 94","HC",["ayyanar"]),
 ("Ashok Kumar v. State of U.P.","2008 (5) ALJ 383","HC",["ashok","kumar","u p"]),
 ("... Deoghar v. Jharkhand SEB, Ranchi","2008 (3) JCR 316","HC",["deoghar"]),
 ("Rishi Cement Co. Ltd v. Jharkhand SEB","2008 (4) JCR 776","HC",["rishi","cement"]),
 ("Accounts Officer, Jharkhand SEB v. Anwar Ali","AIR 2008 NOC 2258 / 2008(4) ALJ 291","SC",["anwar","ali"]),
 ("M/s Jindal Resources Pvt Ltd v. Exec Engr WESCO","AIR 2018 Ori 176","HC",["jindal","resources"]),
 ("Ganpat R. Sheth v. Matariya Textiles","AIR 2012 (NOC) 92","HC",["matariya"]),
 ("Harvinder Motors v. BSES Rajdhani Power","AIR 2007 Del 85","HC",["harvinder","motors"]),
 ("J. Madhavan v. Supt. Engineer, Kancheepuram","AIR 2024 Mad 262","HC",["madhavan"]),
 ("Jiyajeerao Cotton Mills Ltd v. M.P. Elec. Board","AIR 1989 SC 788","SC",["jiyajeerao"]),
 ("Kawsar Ali v. State of West Bengal","AIR 2006 Cal 65","HC",["kawsar"]),
 ("Kulwinder Singh v. SDM, Patiala","AIR 2018 P&H 1","HC",["kulwinder"]),
 ("M. Paramaivam v. Union of India","AIR 2007 (NOC) 600 Ker","HC",["paramaivam"]),
 ("M/s Global Feeds / FEDCO v. Commr-cum-Secy, Odisha","AIR 2019 Ori 119","HC",["fedco"]),
 ("M/s Himadri Steel Pvt Ltd v. Jharkhand Urja Vikas Nigam","AIR 2019 Jhar 28","HC",["himadri"]),
 ("M/s Shree Shyam Ispat, Assam v. Assam Power Distribution","AIR 2019 Gau 123","HC",["shyam","ispat"]),
 ("Ramasubbu Ginning Factory v. Supt. Engineer, TN","AIR 2023 Mad 91","HC",["ramasubbu"]),
 ("Vijay Shankar Singh v. State of U.P.","2008 (4) ALJ 421","HC",["vijay","shankar","singh"]),
 ("Sri Rice Mill, Baheri v. Madhyanchal VVN Ltd","AIR 2012 All 45","HC",["baheri"]),
 ("... v. Sri Durga (Cement/Elec) Co","AIR 2005 Guj 40","HC",["durga"]),
 ("... v. Devabhai Memabhai Myatra","AIR 2014 Guj 26","HC",["memabhai"]),
 ("UPPCL v. Anis Ahmad (cited in text)","(2013) 8 SCC 491","SC",["anis","ahmad"]),
 ("Kerala SEB v. Thomas Joseph (cited in text)","2022 INSC 1293","SC",["thomas","joseph"]),
]
def bucket(tid):
    if tid in rank:
        r=rank[tid]; return ("TOP-80" if r<=80 else "81-200"),r
    if tid in by_tid: return "POOL(>200)",None
    return "NOT-HARVESTED",None
print(f"{'#':>2} {'Book case':50} {'Status':13} {'rk':>4} | pool match")
print("-"*108)
summ={"TOP-80":0,"81-200":0,"POOL(>200)":0,"NOT-HARVESTED":0}; in80=[]
for i,(name,cit,court,kws) in enumerate(BOOK,1):
    hits=find(kws,court); tid=hits[0] if hits else None
    if tid: st,r=bucket(tid); m=by_tid[tid]; mt=f"{m['court_type']} {m['date']} cby={m['numcitedby']} {m['title'][:38]}"
    else: st,r=("NOT-HARVESTED",None); mt=""
    summ[st]+=1
    if st=="TOP-80": in80.append(name)
    print(f"{i:>2} {name[:50]:50} {st:13} {str(r or ''):>4} | {mt}")
print("\n=== SUMMARY (book cases) ===")
for k in ["TOP-80","81-200","POOL(>200)","NOT-HARVESTED"]: print(f"  {k:13}: {summ[k]}")
print(f"\nBook cases already in top 80 ({len(in80)}): "+"; ".join(in80))
