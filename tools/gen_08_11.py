#!/usr/bin/env python3
# Generates digest HTML for cases 008-011 (shared Rastogi single-accused skeleton).
import html as H

STD_CITES = [
 ("Punjab State Electricity Board v. Ashwani Kumar", "2010 (7) SCC 569",
  "An inspection report prepared by Board officers in discharge of official duty carries a presumption of regularity; the onus lies on the consumer to rebut it by cogent evidence."),
 ("Sushil Sharma v. BSES Rajdhani Power Ltd.", "Delhi HC, Crl. A. 1060/2010 (22.12.2010)",
  "Non-examination of an independent/public witness is no infirmity where the inspecting officials are trustworthy and bear no enmity towards the accused."),
 ("Neeraj Dutt v. State", "SLP(Crl.) 6497/2020",
  "&ldquo;Shall presume&rdquo; denotes a compulsory legal presumption which the Court is bound to draw until the fact is disproved."),
 ("Hiten P. Dalal v. Bratindranath Banerjee", "2001 (6) SCC 16",
  "A statutory presumption need not be conclusively disproved; the accused must adduce evidence making the defence reasonably probable to a prudent man."),
 ("Mukesh Rastogi v. North Delhi Power Ltd.", "2007 (99) DRJ 108",
  "The easiest rebuttal of the theft presumption is to produce paid electricity bills; under Section 106 of the Evidence Act the onus of proving lawful, metered use lies on the consumer."),
]

TPL_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="digest.css">
</head>
<body>

  <div class="eyebrow">Case Summary</div>
  <h1 class="case">{title}</h1>
  <div class="subcite">{subcite}</div>

  <div class="docket">
    <div class="row"><div class="k">Court</div><div class="v">Court of the Additional Sessions Judge&#8209;05 (Electricity), East District, Karkardooma Courts, Delhi</div></div>
    <div class="row"><div class="k">Judge</div><div class="v">Sh. Ashish Rastogi, Addl. Sessions Judge&#8209;05 (Electricity)</div></div>
    <div class="row"><div class="k">Date of Judgment</div><div class="v">{doj} &nbsp;<span style="color:#5b6b7f">(date of inspection / offence: {dooff})</span></div></div>
    <div class="row"><div class="k">Parties</div><div class="v">{parties}</div></div>
    <div class="row"><div class="k">Statutes Invoked</div><div class="v">Section 135 (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Sections 65B, 106 &amp; 4, Indian Evidence Act, 1872; Sections 251, 313 &amp; 41A, Cr.P.C.; Regulations 60&#8211;63, DERC (Supply Code) Regulations, 2007</div></div>
    <div class="row"><div class="k">Result</div><div class="v">{result}</div></div>
  </div>

  <h2>Charge Before the Court</h2>
  {charge}

  <h2>Facts</h2>
  {facts}

  <h2>Reasoning of the Court</h2>
  <div class="headnote">
    <span class="hn">Headnote</span>
    {headnote}
  </div>
{reasoning}
  <h2>Interpretation of the Electricity Statutes</h2>

  <h3 class="grp">Electricity Act, 2003</h3>
  <h3>Section 135(1)(a) &mdash; Theft of Electricity</h3>
  <p>The Court treated clause (a) &mdash; tapping or making a connection with a licensee&rsquo;s overhead, underground or service lines/wires &mdash; as the operative limb, the case being one of direct hooking rather than meter tampering (clauses (b)&#8211;(e) having no factual foundation). As the Act does not define &ldquo;dishonestly,&rdquo; the Court imported Section 24 IPC and treated {mode_desc} as satisfying the requirement of dishonest intention.</p>
  <h3>Third Proviso to Section 135(1) &mdash; Presumption of Dishonest Use</h3>
  <p>Read as a reverse-onus clause: proof of an artificial or unauthorised means of abstraction raises a presumption of dishonest use &ldquo;until the contrary is proved.&rdquo; Reading it with the &ldquo;shall presume&rdquo; jurisprudence (<span class="cn">Neeraj Dutt</span>) and the rebuttal standard (<span class="cn">Hiten P. Dalal</span>), the Court held that the burden shifted to the accused to make innocence reasonably probable &mdash; a bare denial, without evidence of a lawful source or paid bills, could not discharge it.</p>

  <h3 class="grp">DERC (Supply Code) Regulations, 2007 &mdash; Regulations 60 to 63</h3>
  <p>The Court reproduced Regulations 60&#8211;63 &mdash; the inspection power with photo-identification safeguards (Reg. 60), the contemporaneous site report with seizure, sealing and photographic/video documentation (Reg. 61), the prosecution procedure with the 24-hour police complaint and the caution that a missing meter seal alone cannot found a theft case (Reg. 62), and the assessment at twice the applicable tariff for up to twelve months with credit for units already paid (Reg. 63). Unchallenged compliance confirmed the inspection&rsquo;s regularity; the {bill} assessment measured the theft and required no separate proof as an ingredient.</p>

  <h2>Held</h2>
  {held}

  <h2>Significance</h2>
  <p>{sig_intro}</p>
  <ul class="sig">
{sig_items}
  </ul>

  <h2>Citations</h2>
  <p class="cit-preamble">Neither side argued from case law; every citation below is drawn from the Court&rsquo;s own reasoning.</p>
  <table class="cit">
    <thead>
      <tr><th style="width:29%">Case</th><th style="width:56%">Principle Cited For</th><th style="width:15%">Treatment</th></tr>
    </thead>
    <tbody>
{cite_rows}
    </tbody>
  </table>

  <p class="disclaimer">This summary is a condensed digest prepared for quick reference. It is not a substitute for the full text of the judgment and should not be relied upon for legal advice without verification against the original.</p>

</body>
</html>
"""

def cite_row(name, cit, principle):
    return ('      <tr>\n        <td><span class="cn">%s</span><br>%s</td>\n'
            '        <td>%s</td>\n        <td><span class="rep">Relied on</span></td>\n      </tr>' % (name, cit, principle))

def build(c, out):
    reasoning = "\n".join(
        '  <p><span class="bl">%s</span> %s</p>' % (lead, body) for lead, body in c["reasoning"])
    sig_items = "\n".join(
        '    <li><span class="bl">%s</span> %s</li>' % (lead, body) for lead, body in c["significance"])
    rows = "\n".join(cite_row(*x) for x in c.get("cites", STD_CITES))
    html_out = TPL_HEAD.format(
        title=c["title"], subcite=c["subcite"], doj=c["doj"], dooff=c["dooff"],
        parties=c["parties"], result=c["result"], charge=c["charge"], facts=c["facts"],
        headnote=c["headnote"], reasoning=reasoning, mode_desc=c["mode_desc"], bill=c["bill"],
        held=c["held"], sig_intro=c["sig_intro"], sig_items=sig_items, cite_rows=rows)
    open(out, "w").write(html_out)
    print("wrote", out, len(html_out))

# ---------------- CASE 008 ----------------
c008 = dict(
 title="State (BSES YPL) v. Ravinder",
 subcite="SC No.&nbsp;302/2023 &nbsp;|&nbsp; FIR No.&nbsp;794/2021, PS Shastri Park &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="27 March 2026", dooff="6 December 2021",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Ravinder S/o Bhagwat, R/o 12, 2nd Pusta, Old Village Usmanpur, Delhi",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Civil liability on the theft bill (Rs.&nbsp;1,73,901/&#8209;) settled and the settlement amount deposited during trial. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Ravinder dishonestly abstracted electricity at his unmetered ground-floor premises through a yellow wire joined to a two-core black wire hooked to BSES Pole No.&nbsp;YVR&nbsp;J081, the supply running a commercial wooden-work load, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether &mdash; the premises being let in part to a tenant who later vacated and became untraceable &mdash; the accused, as landlord present at the spot, discharged the onus cast by the third proviso to Section 135(1).</p>",
 facts="""<p>On 6 December 2021 at about 6.54 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. S.M. Pareek (Sr. Manager) inspected the residential premises at H.&nbsp;No.&nbsp;12, Ground Floor (Back Portion), Village Old Usmanpur, Delhi. No electricity meter was installed; supply was being drawn directly through a yellow wire joined with a two-core black wire connected from BSES Pole No.&nbsp;YVR&nbsp;J081. One Lokesh, present at the spot, disclosed that he was a tenant of the accused Ravinder, who was also present. The connected load was 2.435&nbsp;KW, used for commercial purposes (wooden work). Sh. Vinod videographed the proceedings; an Inspection Report, Load Report, Seizure Memo and Advisory Notice were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;1,73,901/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;794/2021 was registered.</p>
<p>Investigation (ASI Atul Singh) confirmed that Ravinder was the landlord of the inspected premises; the tenant Lokesh vacated after the inspection and went to an unknown place. A charge-sheet was filed against Ravinder, and notice under Section 251 Cr.P.C. was given on 7 March 2024, to which he pleaded not guilty. The prosecution examined three witnesses: PW-1 ASI Atul Singh (IO; proved the FIR, site plan, Section 41A and Section 91 Cr.P.C. notices, neighbours&rsquo; statements, the accused&rsquo;s investigation statement and Pabandinama); PW-2 S.M. Pareek (inspection team head; proved the videography CD, inspection report, load report, seizure memo, advisory notice, theft bill and complaint, and identified the seized half-metre black wire, Ex.P1); and PW-3 Vinod (videographer, who proved the video and a Section 65B certificate, Ex.PW3/A). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication, leading no defence evidence. His counsel stated that the theft bill had been settled and the settlement amount deposited with the company.</p>""",
 headnote="""A landlord present at his unmetered premises when an illegal pole tap is running answers for the theft as consumer and user; the tenant&rsquo;s subsequent flight does not derail the prosecution. With a Section 65B certificate on record, the videography stands proved, and unrebutted official testimony plus the compulsory presumption in the third proviso to Section 135(1) sustain conviction; the accused&rsquo;s settlement and deposit of the theft bill corroborates guilt rather than closing the case.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the pole-to-premises hook.",
   """The Court identified the operative ingredients &mdash; a dishonest tapping of, or connection with, a licensee&rsquo;s lines so as to abstract, consume or use electricity, punishable with imprisonment up to three years, fine or both &mdash; importing the Section 24 IPC definition of &ldquo;dishonestly.&rdquo; The allegation of hooking wires from BSES Pole No.&nbsp;YVR&nbsp;J081 to unmetered premises brought the case within clause (a), and under the third proviso the presumption of dishonest use arose on proof of the artificial means."""),
  ("The inspection stood proved through unshaken, 65B-supported evidence.",
   """PW-2 (Sr. Manager) and PW-3 (videographer), the inspection team&rsquo;s prime witnesses, deposed consistently to the absence of any meter, the wire from the pole, the 2.435&nbsp;KW commercial (wooden-work) load and the seizure of the half-metre wire identified in court; the videography was proved with a Section 65B certificate (Ex.PW3/A). Cross-examination elicited only that the raid was pre-planned &mdash; an answer that admitted the inspection itself &mdash; and the bare suggestions that the wire was planted or the documents fabricated were denied and left unsubstantiated."""),
  ("The landlord present at the spot was rightly prosecuted despite the tenant's presence.",
   """Investigation established Ravinder as landlord of the premises; he was present at the inspection alongside the tenant Lokesh, who vacated soon after and became untraceable. The accused never showed that the load was the tenant&rsquo;s alone or ran through any authorised meter; with the premises unmetered and the load undisputed, liability fastened on the landlord-occupant found at the running tap."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested in cross-examination."""),
  ("The presumption was compulsory, and settlement of the bill fortified the case.",
   """Following <span class="cn">Neeraj Dutt</span> (&ldquo;shall presume&rdquo; is compulsory) and <span class="cn">Hiten P. Dalal</span> (prudent-man rebuttal standard), the Court noted the accused led no defence evidence, claimed no Genset, and never produced paid bills &mdash; the natural rebuttal under <span class="cn">Mukesh Rastogi</span> and Section 106 of the Evidence Act. His settlement and deposit of the Rs.&nbsp;1,73,901/&#8209; bill, rather than protest against a false claim, corroborated the theft. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through wires hooked to the licensee&rsquo;s pole",
 bill="Rs.&nbsp;1,73,901/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises at the time of inspection and that Ravinder was found indulging in direct theft of electricity through illegal wires &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, he failed to rebut the statutory presumption. Ravinder is accordingly <strong>convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A landlord-liability variation on the direct-hooking template, with a commercial load and a vanished tenant. Five propositions stand out:",
 significance=[
  ("A landlord present at the tap answers for it.",
   """Where the premises are unmetered and the landlord is found at the spot with the theft running, the tenant&rsquo;s later disappearance does not shift or dilute liability."""),
  ("Commercial use multiplies the stakes.",
   """The 2.435&nbsp;KW wooden-work load produced a Rs.&nbsp;1,73,901/&#8209; assessment &mdash; roughly triple the typical domestic-use bills in companion cases &mdash; because assessment follows the applicable (commercial) tariff, doubled under Regulation 63."""),
  ("A filed 65B certificate forecloses the videography challenge.",
   """With Ex.PW3/A on record, the defence&rsquo;s fabrication suggestion had nothing to bite on."""),
  ("&ldquo;Planted evidence&rdquo; suggestions need material.",
   """Bare suggestions that the wire was planted, denied by the witness, cannot dent the presumption of regularity attaching to official inspection reports (<span class="cn">Ashwani Kumar</span>)."""),
  ("Settlement plus deposit still corroborates guilt.",
   """Even full payment of the settled bill was treated not as closure but as conduct inconsistent with innocence on the criminal charge."""),
 ],
)

# ---------------- CASE 009 ----------------
c009 = dict(
 title="State (BSES YPL) v. Yasmeen",
 subcite="SC No.&nbsp;48/2022 &nbsp;|&nbsp; FIR No.&nbsp;545/2019, PS Seelampur &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="16 January 2026", dooff="18 November 2019",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Yasmeen, R/o H.&nbsp;No.&nbsp;E-16/B-178, T-Hut, New Seelampur, Delhi&#8209;110053",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Yasmeen dishonestly abstracted electricity at her unmetered first-floor premises through a two-core grey wire connected to the licensee&rsquo;s service cable at Pole No.&nbsp;YVR-Z-864 after puncturing that cable, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether she discharged the onus cast by the presumption in the third proviso to Section 135(1) once the unauthorised means of abstraction was proved.</p>",
 facts="""<p>On 18 November 2019 at about 6.55 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. Tara Chandra (the then Assistant Manager) inspected the residential premises at H.&nbsp;No.&nbsp;E-16B/178, First Floor, T-Hut, New Seelampur, Delhi. No electricity meter was installed; the accused was found drawing supply through a two-core grey wire connected from the BSES YPL service cable mounted at Pole No.&nbsp;YVR-Z-864, after puncturing that cable. The accused was present at the premises; the connected load was 2.222&nbsp;KW, used for domestic purposes. Sh. Sumit videographed the proceedings; an Inspection Report, Load Report, Seizure Memo and Advisory Notice were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;48,794/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;545/2019 was registered at PS Seelampur.</p>
<p>The IO, ASI Netrapal Singh, interrogated the inspection officials and the accused, seized her Election ID card and copies of the ownership documents of the inspected premises, and filed the charge-sheet. Notice under Section 251 Cr.P.C. was given on 12 January 2024; the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 ASI Netrapal Singh (IO), PW-2 Sumit (videographer, proving the CD and a Section 65B certificate, Ex.PW2/B) and PW-3 Tara Chandra (team head; proved the inspection report, load report, seizure memo, advisory notice, theft bill and complaint, and identified the seized half-metre PVC aluminium cable, Ex.P1). Under Section 313 Cr.P.C. the accused denied all allegations and pleaded false implication; she led no defence evidence.</p>""",
 headnote="""Puncturing the licensee&rsquo;s service cable to draw unmetered supply is direct theft within Section 135(1)(a); an occupant present at the premises and identified in the inspection videography is the consumer, and once the unauthorised means is proved the compulsory presumption in the third proviso convicts unless rebutted by evidence of a lawful, metered source &mdash; which a bare plea of false implication cannot supply.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the punctured-cable tap.",
   """The Court set out the ingredients of Section 135(1) &mdash; dishonest tapping of, or connection with, a licensee&rsquo;s lines, importing Section 24 IPC for &ldquo;dishonestly&rdquo; &mdash; and found the case squarely within clause (a): a wire connected to the licensee&rsquo;s service cable, after puncturing it, feeding unmetered premises. The third proviso&rsquo;s presumption of dishonest use arose on proof of that artificial means."""),
  ("The inspection stood proved, and the accused was identified in the videography.",
   """PW-3 (team head) and PW-2 (videographer) deposed consistently to the absence of any meter, the grey wire tapped from the pole-mounted service cable, the accused&rsquo;s presence, and the 2.222&nbsp;KW domestic load; the video, proved with a Section 65B certificate (Ex.PW2/B), showed the mode and manner of the theft, and PW-3 identified the accused in it. The suggestions that the wire was planted or the premises not hers were denied, and the seized half-metre cable was identified in court. The IO had, in addition, seized copies of the ownership documents of the premises during investigation."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested in cross-examination."""),
  ("The presumption was compulsory, and the accused led nothing to rebut it.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court noted that the accused led no defence evidence, that the premises admittedly had no meter, that appliances were running with no explanation of their source, and that no Genset or alternate source was claimed. The natural rebuttal &mdash; paid electricity bills, per <span class="cn">Mukesh Rastogi</span> and the Section 106 onus &mdash; was never attempted. The presumption stood unrebutted and the identity of neither the accused nor the premises in the video was disputed."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a wire connected to the licensee&rsquo;s service cable after puncturing it",
 bill="Rs.&nbsp;48,794/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises at the time of inspection and that Yasmeen was found indulging in direct theft of electricity through illegal wires &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, she failed to rebut the statutory presumption. Yasmeen is accordingly <strong>convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A clean application of the direct-theft template to a punctured service cable, decided on the inspection evidence alone. Five propositions stand out:",
 significance=[
  ("Puncturing a service cable is a clause (a) tap.",
   """The offence does not require a connection at the pole-head or distribution box; piercing the licensee&rsquo;s service cable to bleed supply is itself the actionable connection."""),
  ("Identification in the videography anchors user status.",
   """PW-3&rsquo;s identification of the accused in the 65B-certified video &mdash; never disputed as to her identity or the premises &mdash; carried the finding that she was the consumer."""),
  ("Ownership documents seized in investigation reinforce occupancy.",
   """The IO&rsquo;s seizure of the premises&rsquo; ownership papers pre-empted any premises-not-mine defence of the kind that failed in companion cases."""),
  ("No settlement was needed for conviction.",
   """Unlike several companion matters, no civil settlement featured; the conviction rests wholly on the unrebutted presumption and inspection evidence."""),
  ("A filed 65B certificate forecloses the videography challenge.",
   """With Ex.PW2/B on record, admissibility of the video was never seriously contestable."""),
 ],
)

# ---------------- CASE 010 ----------------
c010 = dict(
 title="State (BSES YPL) v. Tilak Raj",
 subcite="SC No.&nbsp;286/2021 &nbsp;|&nbsp; FIR No.&nbsp;755/2017, PS Nand Nagri &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="28 January 2026 (reserved 24 December 2025)", dooff="3 August 2017",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Tilak Raj, R/o E-61-A/388, Jhuggi, D-2 Block, Nand Nagri, Delhi (new address: B-66, Gali No.&nbsp;3, Saboli Extension, Delhi)",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Tilak Raj dishonestly abstracted electricity at his unmetered ground-floor jhuggi premises through a two-core black wire connected from the Distribution Box of a BSES YPL street light, the supply running a commercial wire-rolling workshop, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether he discharged the onus cast by the third proviso to Section 135(1).</p>",
 facts="""<p>On 3 August 2017 at about 11.10 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. Jitendra Kumar (DGM) inspected the premises at E-61/A-338, Block D-2, Ground Floor, Nand Nagri, Shahdara, Delhi. No electricity meter was installed at the site; the accused was found drawing supply through a two-core black wire connected from the Distribution Box of a BSES YPL street light. The accused was present at the spot; the connected load was 2.518&nbsp;KW, used for commercial purposes (wire-rolling work), with some of the accused&rsquo;s workers also present. Sh. Akshay Kaushik videographed the proceedings; an Inspection Report, Load Report and Seizure Memo were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;1,73,506/&#8209;, which went unpaid; its Authorised Officer thereupon filed the complaint on which FIR No.&nbsp;755/2017 was registered.</p>
<p>Notice under Section 251 Cr.P.C. was given on 25 July 2024 &mdash; nearly seven years after the offence &mdash; and the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 SI Ombir Singh (IO; proved the endorsement, FIR, Section 41A notice, Aadhaar copy and Pabandinama), PW-2 Akshay Kaushik (videographer, proving the CD and a Section 65B certificate, Ex.PW2/B) and PW-3 Jitendra Kumar (DGM and team head; proved the inspection report, load report, seizure memo, theft bill and complaint). Under Section 313 Cr.P.C. the accused denied all allegations and pleaded false implication; he led no defence evidence, and no settlement of the theft bill was reported.</p>""",
 headnote="""Tapping the distribution box of the licensee&rsquo;s street-light infrastructure to run a commercial workshop from unmetered premises is direct theft within Section 135(1)(a); the compulsory presumption in the third proviso operates with full force where the accused leads no evidence, and neither the passage of more than eight years from offence to judgment nor the accused&rsquo;s relocation erodes unshaken official testimony supported by a Section 65B-certified videography.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the street-light distribution box tap.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the two-core wire run from the street-light Distribution Box of BSES YPL to the unmetered premises as a clause (a) connection with the licensee&rsquo;s service facilities. On proof of that artificial means, the third proviso&rsquo;s presumption of dishonest use arose."""),
  ("The inspection stood proved through unshaken, 65B-supported evidence.",
   """PW-3 (DGM and team head) and PW-2 (videographer) deposed consistently to the absence of any meter, the wire from the street-light distribution box, the accused&rsquo;s presence, and the 2.518&nbsp;KW commercial (wire-rolling) load; the CD was played in court and proved with a Section 65B certificate (Ex.PW2/B). In cross-examination PW-3 reaffirmed that no meter existed and added that the accused&rsquo;s workers were present &mdash; answers that strengthened rather than shook the prosecution. The bare suggestion that the videography was fabricated was denied, and neither the accused&rsquo;s identity nor the premises&rsquo; identity in the video was disputed."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested in cross-examination."""),
  ("The presumption was compulsory, and the accused led nothing to rebut it.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court noted the accused led no defence evidence, offered no explanation for the appliances running at the premises, and claimed no Genset. The natural rebuttal &mdash; paid electricity bills, per <span class="cn">Mukesh Rastogi</span> and the Section 106 onus &mdash; was never attempted; nor was there an iota of evidence that the premises in the videography were not his. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a wire connected from the distribution box of the licensee&rsquo;s street-light network",
 bill="Rs.&nbsp;1,73,506/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises at the time of inspection and that Tilak Raj was found indulging in direct theft of electricity through an illegal wire &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, he failed to rebut the statutory presumption. Tilak Raj is accordingly <strong>convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="The oldest offence in the present set (2017) decided in 2026, and a reminder that public street-light infrastructure is as much the licensee&rsquo;s property as its poles. Five propositions stand out:",
 significance=[
  ("Street-light infrastructure counts as the licensee's works.",
   """A tap on the distribution box feeding public street lights is a Section 135(1)(a) connection with the licensee&rsquo;s service facilities, no different from a pole hook."""),
  ("Commercial theft is priced accordingly.",
   """The 2.518&nbsp;KW wire-rolling load generated a Rs.&nbsp;1,73,506/&#8209; assessment at double the commercial tariff under Regulation 63."""),
  ("Cross-examination answers bound the accused.",
   """PW-3&rsquo;s elicited answers &mdash; no meter installed, the accused&rsquo;s workers present &mdash; came from the defence&rsquo;s own questions and reinforced the prosecution."""),
  ("Delay did not dilute the case.",
   """More than eight years passed between offence (2017) and judgment (2026), including a Section 251 notice served seven years after the inspection, yet the documented, videographed inspection held firm."""),
  ("No settlement, no rebuttal &mdash; the presumption operated at full force.",
   """With the bill unpaid and no defence evidence, the conviction rests squarely on the unrebutted third-proviso presumption."""),
 ],
)

# ---------------- CASE 011 ----------------
c011 = dict(
 title="State (BSES YPL) v. Altaf",
 subcite="SC No.&nbsp;840/2023 &nbsp;|&nbsp; FIR No.&nbsp;478/2021, PS Seelampur &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="15 April 2026", dooff="7 October 2021",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Altaf S/o Chand Miya, R/o H.&nbsp;No.&nbsp;64, 2nd Floor, Gali No.&nbsp;3, Jafrabad, Seelampur, Delhi&#8209;110053",
 result="<strong>Convicted under Section 135, Electricity Act, 2003</strong> &mdash; notwithstanding that the theft bill had been settled, the settlement amount deposited, and an NOC issued by the complainant company. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Altaf dishonestly abstracted electricity at his unmetered second-floor premises through a two-core black wire connected from a Distribution Box of BSES YPL, so as to attract Section 135(1)(a) of the Electricity Act, 2003; whether he discharged the onus cast by the third proviso to Section 135(1); and what effect, if any, his settlement of the civil liability &mdash; complete with deposit and an NOC from the company &mdash; had on the criminal charge.</p>",
 facts="""<p>On 7 October 2021 at about 6.35 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. R.B. Yadav (Assistant Manager) inspected the residential premises at H.&nbsp;No.&nbsp;64, 2nd Floor, Gali No.&nbsp;3, Jafrabad, Delhi. No electricity meter was installed; the premises drew supply through a two-core black aluminium wire connected from a Distribution Box of BSES YPL. Per the complaint the accused was present at the premises; in evidence, PW-3 deposed that a person present at the spot disclosed himself as the accused&rsquo;s representative and that the accused was the user of the electricity. The connected load was 2.370&nbsp;KW, used for domestic purposes. Sh. Mohsin Ali videographed the proceedings; an Inspection Report, Load Report and Seizure Memo were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;50,979/&#8209;, which initially went unpaid; on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;478/2021 was registered at PS Seelampur.</p>
<p>Investigation passed from HC Jugal Kishore to HC Vikas, who served the Section 41A Cr.P.C. notice, recorded a disclosure statement, and seized the accused&rsquo;s Aadhaar card and copies of the ownership documents of the premises. Notice under Section 251 Cr.P.C. was given on 11 January 2024; the accused pleaded not guilty. The prosecution examined four witnesses: PW-1 ASI Jugal Kishore (first IO; proved the FIR), PW-2 HC Vikas (second IO; proved the site plan, notices, interrogation report, Aadhaar and ownership documents, and Pabandinama), PW-3 R.B. Yadav (team head; proved the videography CD, inspection report, load report, seizure memo, theft bill and complaint, and identified the seized half-metre black aluminium wire, Ex.P1) and PW-4 Mohsin Ali (videographer, proving the video and a Section 65B certificate, Ex.PW4/A). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication, leading no defence evidence. His counsel submitted that the theft bill had been settled, the amount deposited, and an NOC issued by the company.</p>""",
 headnote="""Settlement of the theft bill &mdash; even when the amount is deposited and the licensee issues a No-Objection Certificate &mdash; neither bars nor blunts the criminal charge under Section 135; the Court treated the settlement as conduct corroborating the theft. Direct hooking from the licensee&rsquo;s distribution box to unmetered premises engages Section 135(1)(a), and the compulsory third-proviso presumption convicts where the accused leads no evidence of a lawful, metered source.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the distribution-box tap.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the two-core black wire connected from the BSES YPL Distribution Box to the unmetered second-floor premises as a clause (a) connection with the licensee&rsquo;s works. On proof of that artificial means, the third proviso&rsquo;s presumption of dishonest use arose."""),
  ("The inspection stood proved through unshaken, 65B-supported evidence.",
   """PW-3 (team head) and PW-4 (videographer) deposed consistently to the absence of any meter, the wire from the distribution box, and the 2.370&nbsp;KW domestic load; the videography was proved with a Section 65B certificate (Ex.PW4/A), the seized half-metre wire was identified in court, and the load report&rsquo;s correctness was never challenged. PW-3&rsquo;s evidence was that a person present had disclosed himself as the accused&rsquo;s representative, the accused being the user; neither that representative&rsquo;s identity nor the identity of the premises in the video was disputed. The suggestion of false implication was denied and left unsubstantiated."""),
  ("Two successive IOs did not break the investigative chain.",
   """The first IO proved the FIR; the second proved the site plan, notices, interrogation report, the accused&rsquo;s Aadhaar and the ownership documents of the premises seized during investigation. Nothing turned on the transfer of investigation, and the documentary chain from complaint to charge-sheet remained intact."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested in cross-examination."""),
  ("Settlement, deposit and even an NOC could not answer the criminal charge.",
   """Following <span class="cn">Neeraj Dutt</span> and <span class="cn">Hiten P. Dalal</span> on the compulsory presumption and its rebuttal standard, the Court noted the accused led no defence evidence, claimed no Genset, and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus). His settlement of the Rs.&nbsp;50,979/&#8209; bill with deposit and NOC was reasoned the same way as in the companion cases: had the claim been false, he would have protested rather than paid &mdash; so the settlement corroborated the theft, and the criminal liability under Section 135 survived the civil closure. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a wire connected from the licensee&rsquo;s distribution box",
 bill="Rs.&nbsp;50,979/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises at the time of inspection and that Altaf was found indulging in direct theft of electricity through illegal wires &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, he failed to rebut the statutory presumption, and his settlement of the civil liability did not answer the criminal charge. Altaf is accordingly <strong>convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="The clearest statement in this set that buying peace with the discom does not buy peace with the criminal law. Five propositions stand out:",
 significance=[
  ("An NOC after settlement is not immunity.",
   """Payment of the settled bill and issuance of a No-Objection Certificate by the licensee closed the civil account only; the Section 135 prosecution proceeded to conviction regardless."""),
  ("Settlement conduct still corroborates guilt.",
   """As in the companion cases, the readiness to settle &mdash; rather than protest a supposedly false bill &mdash; was itself weighed against the accused."""),
  ("A representative&rsquo;s presence sufficed on the facts.",
   """The person at the spot identified himself as the accused&rsquo;s representative, and the unchallenged videography tied the accused, as user, to the premises."""),
  ("Successive IOs are unobjectionable.",
   """Transfer of the investigation midway, with each IO proving his own documents, left no gap the defence could exploit."""),
  ("The unmetered-premises template held.",
   """No meter, a distribution-box tap, an unexplained running load, no Genset, no paid bills &mdash; the compulsory presumption (<span class="cn">Neeraj Dutt</span>; <span class="cn">Hiten P. Dalal</span>; <span class="cn">Mukesh Rastogi</span>) did the rest."""),
 ],
)

build(c008, "case_008.html")
build(c009, "case_009.html")
build(c010, "case_010.html")
build(c011, "case_011.html")
