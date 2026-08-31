#!/usr/bin/env python3
"""Propose (and optionally write) outcome on existing lean JSON.

  python tools/backfill_outcome.py           # print proposals
  python tools/backfill_outcome.py --apply   # write outcome onto JSON
"""
from __future__ import annotations

import argparse, glob, json, os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "supply-code")
SUMM = os.path.join(ROOT, "summaries", "json")

LICENSEE_PET = re.compile(
    r"\b(vidyut|vidyutvitran|electricity board|electricity supply|"
    r"power corporation|kesco|pvvnl|puvvnl|dvvnl|mvvnl|uppcl|upcl|"
    r"bses|tata power|torrent|cesc|wbsedcl|kptcl|mescom|gescom|"
    r"distribution (?:co|company|licensee)|supply company|"
    r"noida power|npcl|apdcl|pspcl|dhbvn|uhbvn|mseb|msedcl|"
    r"derc|cerc|serc|aptel)\b",
    re.I,
)
PENDING = re.compile(
    r"\b(interlocutory|listed|listing order|passed over|adjourn|"
    r"as fresh|notice issued|no substantive|listed for a future|"
    r"matter adjourned|till next date|week commencing)\b",
    re.I,
)
NONE = re.compile(
    r"\b(infructuous|not pressed|not-pressed|withdrawn|"
    r"contempt application dismissed|misconceived|"
    r"rendered infructuous)\b",
    re.I,
)
ALT = re.compile(
    r"\b(relegat(?:e|ed|ing)|alternative remedy|alternate remedy|"
    r"statutory (?:appeal|remedy)|clause 6\.5|under clause 6\.8|"
    r"section 127|s\.127|apply (?:in|under) the prescribed|"
    r"apply for a (?:fresh )?connection|"
    r"consider(?:ed)? (?:and decide|the (?:application|representation))|"
    r"to be (?:consider|decided) in accordance|"
    r"in accordance with law|"
    r"take a final call|"
    r"file (?:a )?(?:fresh )?(?:representation|objection|objections)|"
    r"liberty to (?:appeal|approach|apply|object|raise|pursue)|"
    r"without (?:examining|adverting|expressing).{0,40}merits)\b",
    re.I,
)
SPLIT = re.compile(
    r"\b(partly allowed|allowed in part|in part|consent|"
    r"installment|instalment)\b",
    re.I,
)
ALLOWED = re.compile(
    r"\b(allowed|quashed|set aside|mandamus to (?:grant|generate)|"
    r"connection (?:to be |shall be )?granted|"
    r"directed to (?:grant|provide|install|energise|energize)|"
    r"reconnection ordered|restored)\b",
    re.I,
)
DISMISSED = re.compile(
    r"\b(dismissed|refused|upheld|no mandamus|mandamus refused|"
    r"connection refused|challenge to the vires.{0,20}refused|"
    r"devoid of merit)\b",
    re.I,
)


def is_licensee_petitioner(c: dict) -> bool:
    title = c.get("title") or ""
    left = title.split(" v.")[0] if " v." in title.lower() or " v " in title.lower() else title
    # split on v. / vs
    m = re.split(r"\s+v(?:s\.?|\.)\s+", title, maxsplit=1, flags=re.I)
    left = m[0] if m else title
    return bool(LICENSEE_PET.search(left))


def blob(c: dict) -> str:
    parts = [c.get("disposition") or "", c.get("headnote") or ""]
    for hu in c.get("holding_units") or []:
        parts.append(hu.get("holding") or "")
        parts.append(hu.get("topic") or "")
    return " ".join(parts)


# Hand calls after reading disposition + title. Beats the regex.
OVERRIDES = {
    "SCJ-004": "none",          # FIR not quashed; s.41 safeguards only
    "SCJ-005": "licensee",      # auction-purchaser must clear 4.3(f) dues
    "SCJ-006": "alternate_remedy",  # process the tenant's application
    "SCJ-007": "split",         # remand for pro-rata
    "SCJ-009": "consumer",      # licensee appeal; demand not enforced
    "SCJ-012": "alternate_remedy",  # apply on No-Dues Certificate
    "SCJ-017": "none",          # employment reinstatement, not a supply dispute
    "SCJ-026": "consumer",      # EE v Ombudsman; licensee writ dismissed, award stands
    "SCJ-243": "consumer",      # restoration of domestic connection directed
    "SCJ-030": "split",         # MG not recoverable; set-off refused
    "SCJ-036": "split",         # purchaser liable; connection on 50% deposit
    "SCJ-039": "none",          # KESCO v UPERC, frivolous, no consumer party
    "SCJ-043": "pending",       # reference answered; appeal remitted
    "SCJ-048": "consumer",      # demand set aside (liberty to reassess is not relegation)
    "SCJ-051": "licensee",      # assessment upheld on merits
    "SCJ-077": "none",          # MSEDCL v MERC, no consumer party
    "SCJ-079": "none",          # IPC/dowry, off-topic
    "SCJ-080": "none",          # family pension, off-topic
    "SCJ-081": "none",          # FIR not quashed
    "SCJ-082": "none",          # FIR not quashed
    "SCJ-084": "alternate_remedy",  # hearing + fresh final assessment
    "SCJ-088": "none",          # bail
    "SCJ-096": "alternate_remedy",  # withdraw to CGRF
    "SCJ-104": "alternate_remedy",  # apply under Works of Licensees Rules
    "SCJ-105": "alternate_remedy",  # approach CGRF
    "SCJ-119": "alternate_remedy",  # object to provisional assessment
    "SCJ-120": "alternate_remedy",  # appear before DM
    "SCJ-130": "none",          # appointments / suo motu, not consumer-licensee
    "SCJ-135": "none",          # Cauvery water, off-topic
    "SCJ-163": "licensee",      # interference at provisional stage declined
    "SCJ-169": "alternate_remedy",  # directions on fresh estimate
    "SCJ-172": "alternate_remedy",  # stay pending objections
    "SCJ-175": "pending",       # interim restrain additional security
    "SCJ-176": "alternate_remedy",  # stay pending fresh assessment
    "SCJ-177": "alternate_remedy",  # stay pending objections
    "SCJ-179": "pending",       # interim stay (licensee appeal)
    "SCJ-181": "licensee",      # not entertained, consigned to record
    "SCJ-189": "pending",       # interim recovery stay
    "SCJ-190": "alternate_remedy",  # process connection on indemnity
    "SCJ-191": "alternate_remedy",  # fresh final assessment after hearing
    "SCJ-196": "alternate_remedy",  # consider mutation under 4.44
    "SCJ-199": "consumer",      # connection to be given on part-payment + indemnity
    "SCJ-203": "pending",       # interim restoration
    "SCJ-205": "licensee",      # interference declined; time to deposit
    "SCJ-206": "pending",       # interim stay
    "SCJ-210": "consumer",      # mandamus to provide tenant a new connection
    "SCJ-212": "alternate_remedy",  # application to be decided in four weeks
    "SCJ-214": "pending",       # interim stay
    "SCJ-219": "pending",       # interim stay of 4.49 BG
    "SCJ-220": "alternate_remedy",  # technical audit directed
    "SCJ-222": "pending",       # interim stay of contempt
    "SCJ-223": "consumer",      # new connection on securing disputed amount
    "SCJ-233": "none",          # criminal bail rejected, off-topic
    "SCJ-244": "split",         # no right to object to tapping; feasibility recorded
    "SCJ-257": "none",          # assessment already paid; service directions only
    "SCJ-261": "none",          # KESCO v UPERC, frivolous, no consumer party
    "SCJ-268": "consumer",      # grant new connection; don't insist on tenant arrears
    "SCJ-277": "none",          # already paid; compounding report; no merits
    "SCJ-297": "consumer",      # mandamus to generate domestic bill without surcharge
    "SCJ-299": "alternate_remedy",  # consider 4.4 indemnity application
}


def propose(c: dict) -> tuple[str, str]:
    """Return (outcome, reason)."""
    cid = c.get("case_id") or ""
    if cid in OVERRIDES:
        return OVERRIDES[cid], "override"
    disp = c.get("disposition") or ""
    text = blob(c)
    lic_pet = is_licensee_petitioner(c)
    sig = (c.get("significance") or "").lower()

    if PENDING.search(disp) and not re.search(
        r"\b(allowed|dismissed as infructuous|disposed of;)\b", disp, re.I
    ):
        # listing-only / interlocutory. "disposed of" + listed should not hit if
        # disposed is the main verb... but "listed 6 May" in interlocutory orders.
        if re.match(r"(?i)\s*(interlocutory|listed|listing order|notice to )", disp):
            return "pending", "interlocutory disposition"
        if sig == "procedural" and PENDING.search(disp) and not DISMISSED.search(disp) and not ALLOWED.search(disp):
            return "pending", "procedural listing"

    if re.search(r"(?i)contempt application dismissed", disp):
        return "none", "contempt dismissed"
    if re.search(r"(?i)dismissed as infructuous", disp):
        return "none", "infructuous"
    if re.search(r"(?i)not pressed", disp):
        return "none", "not pressed"
    if re.search(r"(?i)arbitrator .* appointed", disp):
        return "none", "arbitration referred, no merits"
    if re.search(r"(?i)^interim order\b", disp.strip()):
        return "pending", "interim order"
    if re.search(r"(?i)\bbail (granted|application rejected|granted with)\b", disp):
        return "none", "bail / off-topic criminal"
    if re.search(r"(?i)FIR not quashed", disp):
        return "none", "FIR stands"
    if NONE.search(disp) and not ALLOWED.search(disp):
        return "none", "none-pattern"

    # Alternative remedy beats a bare dismissed.
    if ALT.search(disp) or ALT.search(text[:800]):
        if re.search(r"(?i)dismissed (?:on the ground of|as premature|.*alternative remedy)", disp):
            return "alternate_remedy", "dismissed to alt remedy"
        if re.search(r"(?i)relegat", disp) or re.search(r"(?i)relegat", text[:500]):
            return "alternate_remedy", "relegated"
        if re.search(r"(?i)apply (?:in|under) the prescribed|apply for a (?:fresh )?connection", disp):
            return "alternate_remedy", "apply under Code"
        if re.search(r"(?i)consider(?:ed)? (?:and decide|the application)|take a final call|in accordance with law", disp):
            if not re.search(r"(?i)connection (?:to be |shall be )?granted|directed to (?:grant|provide|install)", disp):
                return "alternate_remedy", "consider/decide, no grant"
        if re.search(r"(?i)section 127|s\.127|statutory appeal", disp) and re.search(
            r"(?i)relegat|liberty to appeal|alternative remedy", disp
        ):
            return "alternate_remedy", "s.127 relegation"
        if re.search(r"(?i)clause 6\.5", disp) and re.search(r"(?i)relegat|representation|permitting", disp):
            return "alternate_remedy", "6.5 relegation"

    if SPLIT.search(disp) and re.search(r"(?i)partly allowed|allowed in part", disp):
        return "split", "partly allowed"

    if re.search(r"(?i)connection (?:to be |shall be )?granted|directed to (?:grant|provide|install|energise)|mandamus to grant", disp):
        return ("licensee" if lic_pet else "consumer"), "connection directed"

    if re.match(r"(?i)\s*(writ petition|petition|appeals?|application|ia|special leave petition) allowed", disp):
        return ("licensee" if lic_pet else "consumer"), "allowed" + (" (licensee-petitioner)" if lic_pet else "")

    if re.search(r"(?i)quashed|set aside", disp) and re.search(r"(?i)allowed", disp):
        return ("licensee" if lic_pet else "consumer"), "allowed+quashed"

    if re.match(r"(?i)\s*(writ petition|petition|appeals?|application|review application|special leave petition) dismissed", disp):
        if ALT.search(disp):
            return "alternate_remedy", "dismissed + alt remedy"
        return ("consumer" if lic_pet else "licensee"), "dismissed" + (" (licensee-petitioner)" if lic_pet else "")

    if re.search(r"(?i)refused", disp) and re.search(r"(?i)connection refused|mandamus refused|no mandamus", disp):
        return "licensee", "relief refused"

    # disposed of with a grant
    if re.search(r"(?i)disposed of", disp):
        if re.search(r"(?i)connection (?:to be |shall be )?granted|directed to (?:grant|provide|install|energise)|reconnection ordered|restore", disp):
            return "consumer", "disposed+grant"
        if ALT.search(disp):
            return "alternate_remedy", "disposed+alt"
        if re.search(r"(?i)quashed|set aside", disp):
            return ("licensee" if lic_pet else "consumer"), "disposed+quash"
        if re.search(r"(?i)instalment|installment|consent", disp):
            return "split", "disposed+consent/instalment"
        if DISMISSED.search(disp):
            return ("consumer" if lic_pet else "licensee"), "disposed+dismissive"
        return "UNSURE", "disposed-of residual"

    if ALLOWED.search(disp):
        return ("licensee" if lic_pet else "consumer"), "allowed-pattern"
    if DISMISSED.search(disp):
        return ("consumer" if lic_pet else "licensee"), "dismissed-pattern"
    if PENDING.search(disp) or PENDING.search(text[:400]):
        return "pending", "pending leftover"
    if ALT.search(text[:800]):
        return "alternate_remedy", "alt leftover"

    return "UNSURE", "no rule"


def load_all():
    rows = []
    for path in sorted(glob.glob(os.path.join(SUMM, "SCJ-*.json"))):
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        rows.append((path, c))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    rows = load_all()
    unsure = 0
    counts = {}
    for path, c in rows:
        oc, why = propose(c)
        counts[oc] = counts.get(oc, 0) + 1
        if oc == "UNSURE":
            unsure += 1
        disp = (c.get("disposition") or "").replace("\n", " ")[:140]
        print(f"{c['case_id']}\t{oc:18}\t{why:28}\t{disp}")
        if args.apply and oc != "UNSURE":
            if c.get("outcome") != oc:
                c["outcome"] = oc
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(c, f, indent=2, ensure_ascii=False)
                    f.write("\n")
    print("---")
    print("counts", counts, "unsure", unsure)
    if args.apply and unsure:
        print("UNSURE records left unlabeled", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
