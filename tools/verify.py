#!/usr/bin/env python3
"""Deterministic verification of a case extract before it is rendered/committed.

Usage: python tools/verify.py <court_dir> <case_id>
Reads  <court_dir>/extracts/<case_id>.extract.json , .fp.json , .txt
Prints PASS or FAIL with a list of problems. Exit code 0 = pass, 1 = fail.

Catches the known failure modes: missing structural fields, authorities whose doc-id is not
in the source, authority names that are actually the bench's judges (leak), and a disposition
that does not appear in the judgment text.
"""
import sys, os, json, re

def norm(s):
    return re.sub(r'[^a-z0-9 ]', ' ', str(s).lower())

def tokens(s):
    return set(w for w in norm(s).split() if len(w) > 3)

def main():
    court, cid = sys.argv[1], sys.argv[2]
    ed = os.path.join(court, "extracts")
    ex = json.load(open(os.path.join(ed, f"{cid}.extract.json")))
    fp = json.load(open(os.path.join(ed, f"{cid}.fp.json"))) if os.path.exists(os.path.join(ed, f"{cid}.fp.json")) else {}
    txt = open(os.path.join(ed, f"{cid}.txt")).read()
    tl = norm(txt)
    problems, warns = [], []

    # 1. structural
    req = ["title","court","coram","date_of_judgment","nature","parties","provisions","result",
           "issues","facts","headnote","reasoning","interpretation","ratio","disposition",
           "sig_intro","significance","authorities"]
    for k in req:
        if not ex.get(k):
            problems.append(f"missing/empty field: {k}")
    for k in ["reasoning","obiter","significance"]:
        for i, it in enumerate(ex.get(k, [])):
            if not (isinstance(it, (list, tuple)) and len(it) == 2):
                problems.append(f"{k}[{i}] is not a [lead, body] pair")
    if len(ex.get("issues", [])) == 0:
        problems.append("no issues / points for determination")

    # 2. authorities: doc-id in source, or name present in text
    fp_docids = {str(c.get("docid")) for c in fp.get("citations", [])}
    coram_surnames = {w for w in tokens(ex.get("coram","")) if w not in
                      {"honble","justice","chief","the","and","mr","mrs","ms","hon"}}
    for a in ex.get("authorities", []):
        nm = a.get("name","")
        did = str(a.get("docid","")).strip()
        if did:
            if fp_docids and did not in fp_docids:
                problems.append(f"authority doc-id {did} ({nm[:40]}) not in source fingerprint")
        else:
            key = [w for w in norm(nm).split() if len(w) > 4 and w not in {"state","board","electricity","limited","power","company","supply"}]
            if key and not any(w in tl for w in key[:3]):
                warns.append(f"authority not clearly found in text: {nm[:50]}")
        # leak heuristic: authority name is really a bench judge
        anames = tokens(nm) - {"state","board","electricity","supply","company","power","limited","ltd"}
        if anames and anames <= coram_surnames:
            problems.append(f"authority looks like a bench judge (leak?): {nm[:50]}")
        if not a.get("treatment"):
            warns.append(f"authority has no treatment: {nm[:40]}")

    # 3. disposition keyword present in text
    disp_kw = ["allowed","dismissed","remand","quashed","set aside","disposed","modified",
               "acquitted","convicted","partly allowed","rejected"]
    if not any(k in norm(ex.get("disposition","")) for k in disp_kw):
        warns.append("disposition field has no recognised outcome keyword")
    if ex.get("disposition") and not any(k in tl for k in disp_kw):
        warns.append("no outcome keyword found in the source text")

    # 4. coram present in text
    if coram_surnames and not any(w in tl for w in coram_surnames):
        warns.append("none of the coram surnames appear in the source text")

    ok = not problems
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {len(problems)} problem(s), {len(warns)} warning(s)")
    for p in problems: print("  ✗", p)
    for w in warns: print("  ~", w)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
