#!/usr/bin/env python3
from gen_08_11 import build

# ---------------- CASE 016 : Shimla (widow, mixed shop+home, partial reduced settlement) ----------------
c016 = dict(
 title="State v. Shimla",
 subcite="SC No.&nbsp;570/2022 &nbsp;|&nbsp; FIR No.&nbsp;605/2019, PS Harsh Vihar &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="1 June 2026", dooff="22 October 2019",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Shimla W/o Late Sh. Sukhbir, R/o H. No.&nbsp;D-263, Gali No.&nbsp;4, Khasra No.&nbsp;155, Main Road, Pratap Nagar, Delhi&#8209;110093",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Civil liability settled during trial for a reduced sum of Rs.&nbsp;26,000/&#8209; (against a theft bill of Rs.&nbsp;51,607/&#8209;), of which Rs.&nbsp;3,000/&#8209; was deposited and the balance stated to be paid shortly. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Shimla dishonestly abstracted electricity at her unmetered premises &mdash; used for a shop on the ground floor and residence on the first &mdash; through a black cable hooked from the Distribution Box on BSES YPL Pole No.&nbsp;NNG-W159, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether she discharged the onus cast by the presumption in the third proviso to Section 135(1).</p>",
 facts="""<p>On 22 October 2019 at about 11.40 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. Deepak Singh Verma (the then Assistant Manager) inspected the premises at H. No.&nbsp;D-263, Gali No.&nbsp;4, Khasra No.&nbsp;155, Pratap Nagar, Delhi. No electricity meter was installed; the accused was found drawing supply through a black cable connected from the Distribution Box of BSES YPL Pole No.&nbsp;NNG-W159. The connected load was 1.563&nbsp;KW, used for commercial purposes (a shop on the ground floor) as well as domestic purposes (the first floor); the accused&rsquo;s son Rahul was present at the spot. Sh. Jagdeep Gill videographed the proceedings and furnished a Section 65B certificate; an Inspection Report and Load Report were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;51,607/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;605/2019 was registered at PS Harsh Vihar.</p>
<p>The IO, SI Illa Khan, served the Section 41A Cr.P.C. notice and seized the accused&rsquo;s Aadhaar and Election ID cards and an NCR recording the loss of the premises&rsquo; ownership documents. Notice under Section 251 Cr.P.C. was given on 21 November 2023; the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 Deepak Singh Verma (team head; proved the CD, inspection report, load report, theft bill and complaint); PW-2 Jagdeep Gill (videographer; proved the video and the Section 65B certificate Ex.PW2/A); and PW-3 SI Illa Khan (IO). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication; she led no defence evidence. Her counsel submitted that the civil liability had been settled for Rs.&nbsp;26,000/&#8209;, of which Rs.&nbsp;3,000/&#8209; had been deposited and the balance would be paid shortly.</p>""",
 headnote="""A distribution-box tap feeding an unmetered premises used partly as a shop and partly as a home is direct theft under Section 135(1)(a), the widow in occupation being the &ldquo;consumer&rdquo;; and even a partial, reduced settlement of the theft bill corroborates guilt rather than closing the criminal case, which the unrebutted third-proviso presumption sustains.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the distribution-box tap.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the black cable run from the Distribution Box on Pole No.&nbsp;NNG-W159 to the unmetered premises as a clause (a) connection with the licensee&rsquo;s works. On proof of that artificial means the third proviso&rsquo;s presumption arose."""),
  ("The inspection stood proved through unshaken, 65B-supported evidence.",
   """PW-1 and PW-2 were consistent on the absence of any meter, the pole-distribution-box tap and the 1.563&nbsp;KW mixed shop-and-home load; PW-1 added in cross-examination that the pole from which the theft ran was installed near the premises. The accused&rsquo;s son Rahul was present at the inspection, and neither his identity nor the identity of the premises in the videography was disputed; the load report&rsquo;s correctness went unchallenged."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested."""),
  ("The presumption was compulsory, and the accused led nothing to rebut it.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court noted the accused led no defence evidence, explained no lawful source for the appliances found, and claimed no Genset. The natural rebuttal &mdash; paid electricity bills, per <span class="cn">Mukesh Rastogi</span> and the Section 106 onus &mdash; was never attempted."""),
  ("Even a reduced, part-paid settlement corroborated guilt.",
   """The accused settled the Rs.&nbsp;51,607/&#8209; theft bill for Rs.&nbsp;26,000/&#8209; during trial, depositing only Rs.&nbsp;3,000/&#8209;. The Court reasoned, as elsewhere, that had the claim been false she would have protested and proceeded against the company rather than settling at all; her willingness to compromise, even partially, fortified the prosecution case. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered mixed shop-and-home premises through a cable hooked from the licensee&rsquo;s pole-mounted distribution box",
 bill="Rs.&nbsp;51,607/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises and that Shimla was found indulging in direct theft of electricity through an illegal wire &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, she failed to rebut the statutory presumption. <strong>Shimla is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A mixed shop-and-home theft where even a reduced, partly-paid settlement counted against the accused. Five propositions stand out:",
 significance=[
  ("A reduced, part-paid settlement still corroborates guilt.",
   """Settling the Rs.&nbsp;51,607/&#8209; bill for Rs.&nbsp;26,000/&#8209; and depositing only Rs.&nbsp;3,000/&#8209; was read as conduct inconsistent with innocence, not as a bargained compromise neutralising the criminal charge."""),
  ("Mixed shop-and-home use is one consumer&rsquo;s theft.",
   """A single tap feeding a ground-floor shop and a first-floor residence is direct theft, assessed across the mixed load."""),
  ("Occupancy fixes consumer status.",
   """The widow in occupation of the premises answered for the abstraction found there."""),
  ("A public witness is not essential.",
   """Official inspection testimony, videographed and 65B-certified, suffices absent shown enmity (<span class="cn">Ashwani Kumar</span>; <span class="cn">Sushil Sharma</span>)."""),
  ("The reverse-onus presumption did the rest.",
   """No meter, an unexplained running load, no Genset, no paid bills &mdash; the compulsory presumption convicted."""),
 ],
)

# ---------------- CASE 017 : Atul (son of Balram; companion to case 013; street-light; settlement+NOC) ----------------
c017 = dict(
 title="State v. Atul",
 subcite="SC No.&nbsp;986/2023 &nbsp;|&nbsp; FIR No.&nbsp;904/2022, PS New Usmanpur &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="1 April 2026", dooff="27 June 2022",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Atul S/o Late Balram, R/o H. No.&nbsp;B-135/1, Khasra No.&nbsp;1/368/2, First Floor, Gali No.&nbsp;10, Shanti Mohalla, Village New Usmanpur, Delhi",
 result="<strong>Convicted under Section 135, Electricity Act, 2003</strong> &mdash; notwithstanding that the theft bill (Rs.&nbsp;86,825/&#8209;) had been settled, the amount deposited, and an NOC issued by the complainant company. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Atul dishonestly abstracted electricity at his unmetered first-floor premises &mdash; held in the name of his late father &mdash; through a single-core black aluminium wire tapped from the street-light point on BSES YPL Pole No.&nbsp;YVR-H-799, so as to attract Section 135(1)(a) of the Electricity Act, 2003; whether he discharged the third-proviso onus; and what effect his settlement of the civil liability, with deposit and an NOC, had on the criminal charge.</p>",
 facts="""<p>On 27 June 2022 at about 11.11 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. Saurabh Sharma (Manager) inspected the first-floor premises at H. No.&nbsp;B-135/1, Shanti Mohalla, Village New Usmanpur, Delhi &mdash; the same building, and the same inspection drive, as the same-day prosecution of the accused&rsquo;s widowed mother Gyatri Devi (FIR 759/2022, a different floor). No electricity meter was installed; the accused was found drawing supply through a single-core black aluminium wire connected from the Street Light Point at Pole No.&nbsp;YVR-H-799. He was present at the spot; the connected load was 4.517&nbsp;KW, used for domestic purposes. Sh. Deepak videographed the proceedings and furnished a Section 65B certificate; an Inspection Report, Load Report and Seizure Memo were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;86,825/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;904/2022 was registered at PS New Usmanpur.</p>
<p>The IO, HC Anil Kumar, seized the accused&rsquo;s Aadhaar card, the ownership documents of the premises &mdash; which stood in the name of his late father Balram &mdash; and Balram&rsquo;s death certificate. Notice under Section 251 Cr.P.C. was given on 3 May 2024; the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 Saurabh Sharma (team head; proved the CD, inspection report, load report, seizure memo, theft bill and complaint, and the seized aluminium wires Ex.P1); PW-2 Deepak (videographer; proved the video and the Section 65B certificate Ex.PW2/A); and PW-3 HC Anil Kumar (IO). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication; he led no defence evidence. His counsel submitted that the theft bill had been settled, the amount deposited, and an NOC issued by the company.</p>""",
 headnote="""A companion to the same-day prosecution of the accused&rsquo;s mother at the same building: a street-light-point tap feeding unmetered premises held in the late father&rsquo;s name is direct theft under Section 135(1)(a), the son in occupation being the &ldquo;consumer&rdquo;; and settlement of the theft bill, even with deposit and an NOC, corroborates guilt rather than closing the criminal case, which the unrebutted third-proviso presumption sustains.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the street-light-point tap.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the single-core wire run from the street-light point on the licensee&rsquo;s pole to the unmetered premises as a clause (a) connection with the licensee&rsquo;s service facilities. On proof of that artificial means the third proviso&rsquo;s presumption arose."""),
  ("The inspection stood proved, and the accused was identified in the 65B-certified video.",
   """PW-1 and PW-2 were consistent and uncontradicted; PW-1 deposed to having received prior information of theft from the electricity pole and identified the accused in the videography (proved with a Section 65B certificate). The seized aluminium wires were identified in court, and the load report&rsquo;s correctness went unchallenged; the bare suggestion that the wire was planted was denied."""),
  ("Occupancy, not title, fixed the accused&rsquo;s status as consumer.",
   """That the premises stood in the name of the late Balram did not shield the accused: his son was in occupation and drawing the supply, and the IO had seized both the ownership documents and Balram&rsquo;s death certificate. As the person consuming the abstracted electricity he was the &ldquo;consumer&rdquo; answerable under the Act."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested."""),
  ("Settlement, deposit and even an NOC could not answer the criminal charge.",
   """Following <span class="cn">Neeraj Dutt</span> and <span class="cn">Hiten P. Dalal</span> on the compulsory presumption and its rebuttal standard, the Court noted the accused led no defence evidence, claimed no Genset, and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus). His settlement of the Rs.&nbsp;86,825/&#8209; bill, with deposit and NOC, was reasoned as elsewhere: had the claim been false he would have protested rather than paid, so the settlement corroborated the theft and the Section 135 liability survived the civil closure. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a wire tapped from the street-light point on the licensee&rsquo;s pole",
 bill="Rs.&nbsp;86,825/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises and that Atul was found indulging in direct theft of electricity through an illegal wire &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, he failed to rebut the statutory presumption, and his settlement of the civil liability did not answer the criminal charge. <strong>Atul is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="The son&rsquo;s companion to case&nbsp;013 &mdash; same building, same inspection day, same street-light pole &mdash; and another instance of settlement-plus-NOC yielding a conviction. Five propositions stand out:",
 significance=[
  ("An NOC after settlement is not immunity.",
   """Payment of the settled bill and an NOC from the licensee closed the civil account only; the Section 135 prosecution proceeded to conviction regardless."""),
  ("Occupancy, not title, fixes &ldquo;consumer&rdquo; status.",
   """That the premises stood in the late father&rsquo;s name did not shield the son in occupation who drew the supply."""),
  ("Street-light infrastructure is the licensee&rsquo;s works.",
   """A tap on the street-light point feeding public lighting is a Section 135(1)(a) connection with the licensee&rsquo;s service facilities, no different from a bare pole hook."""),
  ("Settlement corroborates guilt.",
   """Readiness to settle rather than protest a supposedly false bill was weighed against the accused."""),
  ("The reverse-onus presumption did the rest.",
   """No meter, an unexplained running load, no Genset, no paid bills &mdash; the compulsory presumption convicted."""),
 ],
)

build(c016, "case_016.html")
build(c017, "case_017.html")
