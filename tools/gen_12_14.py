#!/usr/bin/env python3
from gen_08_11 import build  # reuses the single-accused Rastogi template + STD_CITES

# ---------------- CASE 012 : Shehzad & Anr. (two spouses, both u/s 135) ----------------
c012 = dict(
 title="State v. Shehzad &amp; Anr.",
 subcite="SC No.&nbsp;897/2023 &nbsp;|&nbsp; FIR No.&nbsp;728/2022, PS Jafrabad &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="15 January 2026", dooff="3 June 2022",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> (1) Shehzad S/o Jane Alam; (2) Shaziya W/o Shehzad, both R/o H. No.&nbsp;E-11, Khasra No.&nbsp;01/148, 2nd Floor, Gali No.&nbsp;2, Chauhan Bangar, Delhi",
 result="<strong>Both Shehzad and Shaziya convicted under Section 135, Electricity Act, 2003.</strong> Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Shehzad and his wife Shaziya dishonestly abstracted electricity at their unmetered second-floor premises through a two-core black wire tapped &mdash; by puncturing &mdash; into the service cable of BSES YPL Pole No.&nbsp;YVR-Z-724, so as to attract the offence of theft of electricity under Section 135(1)(a) of the Electricity Act, 2003; and whether, once the prosecution proved the unauthorised means of abstraction, they discharged the onus cast by the presumption in the third proviso to Section 135(1).</p>",
 facts="""<p>On 3 June 2022 at about 10.15 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. Vipin Kumar Gautam (DGM) inspected the second-floor residential premises at H. No.&nbsp;E-11, Khasra No.&nbsp;01/148, Kalyanwali Gali No.&nbsp;2, Chauhan Bangar, Delhi. No electricity meter was installed for the inspected floor &mdash; the five-floor building had meters for its other floors alone &mdash; and supply was being drawn through a two-core black wire connected from the yellow service cable of Pole No.&nbsp;YVR-Z-724 by puncturing that cable and running the wire up to the second floor. Accused Shehzad was present at the spot; the connected load was 4.022&nbsp;KW, used for domestic purposes. Sh. Sandeep Verma videographed the proceedings and furnished a Section 65B certificate; an Inspection Report, Load Report and Seizure Memo were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;62,109/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;728/2022 was registered at PS Jafrabad.</p>
<p>Notice under Section 251 Cr.P.C. was given on 12 January 2024; both accused pleaded not guilty. The prosecution examined three witnesses: PW-1 Sandeep Verma (videographer; proved the CD Ex.PW1/A, a Section 65B certificate Ex.PW1/B and six photographs); PW-2 Vipin Kumar Gautam (DGM and team head; proved the inspection report, load report, seizure memo, theft bill and complaint, and the seized wire Ex.P1); and PW-3 HC Gulab Singh (IO; proved the endorsement, FIR, site plan, the Section 41A and Section 91 Cr.P.C. notices served on both accused, the interrogation reports, Shaziya&rsquo;s reply to the Section 91 notice, Aadhaar cards, the ownership documents of the premises, and the Pabandinamas). Under Section 313 Cr.P.C. both accused denied everything and pleaded false implication; neither led any defence evidence.</p>""",
 headnote="""Where whole floors of a building run with no meter and a wire is tapped, by puncturing, into the licensee&rsquo;s pole-mounted service cable, the direct-theft offence under Section 135(1)(a) is made out; spouses jointly occupying and drawing that unauthorised supply are each liable as consumers and convictable under Section 135 without recourse to the abetment provision. The compulsory presumption in the third proviso convicts both where neither leads evidence of a lawful, metered source.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the punctured service-cable tap.",
   """The Court set out the ingredients of Section 135(1) &mdash; reproducing, for completeness, also the cognate meter-interference offence in Section 138 &mdash; but held only clause (a) of Section 135(1) applicable: a dishonest tap on the licensee&rsquo;s service cable, importing the Section 24 IPC meaning of &ldquo;dishonestly.&rdquo; On proof of that artificial means the third proviso&rsquo;s presumption of dishonest use arose."""),
  ("Both spouses were properly convicted as principals, not merely as abettors.",
   """Shehzad was present at the inspection; the premises were the couple&rsquo;s joint residence; Shaziya herself answered the Section 91 Cr.P.C. notice. Both having been charged and tried under Section 135 as persons drawing and using the abstracted supply, the Court convicted each as a principal offender rather than routing the wife through Section 150."""),
  ("The inspection stood proved through unshaken, 65B-supported evidence.",
   """PW-1 and PW-2 were consistent and uncontradicted on the absence of any meter for the inspected floor, the punctured-cable tap and the seizure; the CD (proved with a Section 65B certificate) was played in court and neither the accused&rsquo;s nor the premises&rsquo; identity was disputed. That the building carried authorised meters for its other floors underscored the absence of one for the inspected second floor. The suggestions that the case property was planted or the documents fabricated were denied and left unsubstantiated."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested in cross-examination."""),
  ("The presumption was compulsory, and neither spouse rebutted it.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court noted that neither accused led defence evidence, explained the source running the appliances, or claimed a Genset. The natural rebuttal &mdash; paid electricity bills, per <span class="cn">Mukesh Rastogi</span> and the Section 106 onus &mdash; was never attempted, and the presumption stood unrebutted against both."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a wire tapped, by puncturing, into the licensee&rsquo;s pole-mounted service cable",
 bill="Rs.&nbsp;62,109/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available for the inspected premises and that Shehzad and Shaziya were found indulging in direct theft of electricity through an illegal wire &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, they failed to rebut the statutory presumption. <strong>Shehzad and Shaziya are accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and are to be heard on the quantum of sentence.</p>",
 sig_intro="A joint spousal conviction turning on a punctured service cable in a multi-floor building. Five propositions stand out:",
 significance=[
  ("Both occupants can be convicted as principals.",
   """Where spouses jointly occupy unmetered premises fed by one illegal tap, each is a &ldquo;consumer&rdquo; drawing the supply and each is convicted under Section 135 &mdash; there is no need to route the second occupant through the abetment provision."""),
  ("Puncturing a pole-mounted service cable is a clause (a) tap.",
   """Piercing the licensee&rsquo;s service cable at the pole to bleed supply is itself the actionable connection under Section 135(1)(a)."""),
  ("Meters for other floors do not help.",
   """That the building carried authorised meters for its other floors underscored, rather than excused, the absence of any meter for the inspected floor."""),
  ("A filed 65B certificate forecloses the videography challenge.",
   """With Ex.PW1/B on record, the planting and fabrication suggestions had nothing to bite on."""),
  ("The reverse-onus presumption binds every occupant.",
   """Neither spouse produced paid bills or any lawful-source evidence; the compulsory third-proviso presumption convicted both."""),
 ],
)

# ---------------- CASE 013 : Gyatri Devi (widow, street-light point, settlement+NOC) ----------------
c013 = dict(
 title="State v. Gyatri Devi",
 subcite="SC No.&nbsp;987/2023 &nbsp;|&nbsp; FIR No.&nbsp;759/2022, PS New Usmanpur &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="1 April 2026", dooff="27 June 2022",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Gyatri Devi W/o Late Balram, R/o H. No.&nbsp;B-135/1, Khasra No.&nbsp;1/368/2, First Floor, Gali No.&nbsp;10, Shanti Mohalla, Village New Usmanpur, Delhi",
 result="<strong>Convicted under Section 135, Electricity Act, 2003</strong> &mdash; notwithstanding that the theft bill (Rs.&nbsp;78,428/&#8209;) had been settled, the amount deposited, and an NOC issued by the complainant company. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Gyatri Devi dishonestly abstracted electricity at her unmetered premises &mdash; held in the name of her late husband &mdash; through a single-core black aluminium wire tapped from the street-light point on BSES YPL Pole No.&nbsp;YVR-H-799, so as to attract Section 135(1)(a) of the Electricity Act, 2003; whether she discharged the onus under the third proviso; and what effect her settlement of the civil liability, with deposit and an NOC, had on the criminal charge.</p>",
 facts="""<p>On 27 June 2022 at about 11.14 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. Saurabh Sharma (Manager) inspected the residential premises at H. No.&nbsp;B-135/1, Shanti Mohalla, Village New Usmanpur, Delhi. No electricity meter was installed; the accused was found drawing supply through a single-core black aluminium wire connected from the Street Light Point at Pole No.&nbsp;YVR-H-799. She was present at the spot; the connected load was 4.144&nbsp;KW, used for domestic purposes. Sh. Deepak videographed the proceedings and furnished a Section 65B certificate; an Inspection Report, Load Report and Seizure Memo were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;78,428/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;759/2022 was registered at PS New Usmanpur.</p>
<p>The IO, HC Anil Kumar, seized the accused&rsquo;s Aadhaar card, the ownership documents of the premises &mdash; which stood in the name of her late husband Balram &mdash; and his death certificate. Notice under Section 251 Cr.P.C. was given on 29 April 2024; the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 Saurabh Sharma (team head; proved the CD, inspection report, load report, seizure memo, theft bill and complaint, and the seized aluminium wires Ex.P1); PW-2 Deepak (videographer; proved the video and the Section 65B certificate Ex.PW2/A); and PW-3 HC Anil Kumar (IO). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication; she led no defence evidence. Her counsel submitted that the theft bill had been settled, the amount deposited, and an NOC issued by the company.</p>""",
 headnote="""Tapping the street-light point on the licensee&rsquo;s pole to feed unmetered premises is direct theft under Section 135(1)(a); a widow in occupation of premises standing in her late husband&rsquo;s name is the &ldquo;consumer&rdquo; answerable for the abstraction. Settlement of the theft bill &mdash; even with deposit and an NOC &mdash; corroborates guilt rather than closing the criminal case, which the unrebutted third-proviso presumption sustains.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the street-light-point tap.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the single-core wire run from the street-light point on the licensee&rsquo;s pole to the unmetered premises as a clause (a) connection with the licensee&rsquo;s service facilities. On proof of that artificial means the third proviso&rsquo;s presumption arose."""),
  ("The inspection stood proved, and the accused was identified in the 65B-certified video.",
   """PW-1 and PW-2 were consistent and uncontradicted; PW-1 deposed that he had received information of theft from the electricity pole, and identified the accused in the videography (proved with a Section 65B certificate). The seized half-metre aluminium wires were identified in court, and the load report&rsquo;s correctness went unchallenged. The bare suggestion that the wire was planted was denied."""),
  ("Occupancy, not title, fixed the accused&rsquo;s status as consumer.",
   """That the premises stood in the name of the late Balram did not shield the accused: she was in occupation and drawing the supply, and the IO had seized both the ownership documents and Balram&rsquo;s death certificate. As the person consuming the abstracted electricity she was the &ldquo;consumer&rdquo; answerable under the Act."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested."""),
  ("Settlement, deposit and even an NOC could not answer the criminal charge.",
   """Following <span class="cn">Neeraj Dutt</span> and <span class="cn">Hiten P. Dalal</span> on the compulsory presumption and its rebuttal standard, the Court noted the accused led no defence evidence, claimed no Genset, and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus). Her settlement of the Rs.&nbsp;78,428/&#8209; bill, with deposit and NOC, was reasoned as elsewhere: had the claim been false she would have protested rather than paid, so the settlement corroborated the theft and the Section 135 liability survived the civil closure. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a wire tapped from the street-light point on the licensee&rsquo;s pole",
 bill="Rs.&nbsp;78,428/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises and that Gyatri Devi was found indulging in direct theft of electricity through an illegal wire &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, she failed to rebut the statutory presumption, and her settlement of the civil liability did not answer the criminal charge. <strong>Gyatri Devi is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A street-light-point theft where full civil closure &mdash; deposit plus NOC &mdash; still yielded a criminal conviction. Five propositions stand out:",
 significance=[
  ("An NOC after settlement is not immunity.",
   """Payment of the settled bill and an NOC from the licensee closed the civil account only; the Section 135 prosecution proceeded to conviction regardless."""),
  ("Street-light infrastructure is the licensee&rsquo;s works.",
   """A tap on the street-light point feeding public lighting is a Section 135(1)(a) connection with the licensee&rsquo;s service facilities, no different from a bare pole hook."""),
  ("Occupancy, not title, fixes &ldquo;consumer&rdquo; status.",
   """That the premises stood in the late husband&rsquo;s name did not shield the widow in occupation who drew the supply."""),
  ("Settlement corroborates guilt.",
   """Readiness to settle rather than protest a supposedly false bill was weighed against the accused."""),
  ("The reverse-onus presumption did the rest.",
   """No meter, an unexplained running load, no Genset, no paid bills &mdash; the compulsory presumption convicted."""),
 ],
)

# ---------------- CASE 014 : Mustak Hussain (scrap work, worker's statement, advisory notice) ----------------
c014 = dict(
 title="State v. Mustak Hussain",
 subcite="SC No.&nbsp;1030/2022 &nbsp;|&nbsp; FIR No.&nbsp;146/2021, PS Shastri Park &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="9 January 2026", dooff="21 January 2021",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Mustak Hussain S/o Shabbir Hussain, R/o H. No.&nbsp;B-10A, Ground Floor, Khasra No.&nbsp;1/91, Gali No.&nbsp;1, Shastri Park, Delhi",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Civil liability on the theft bill (Rs.&nbsp;72,006/&#8209;) settled and the amount deposited during trial. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Mustak Hussain dishonestly abstracted electricity at his unmetered ground-floor premises &mdash; used for scrap/labour work &mdash; through a 14-metre yellow cable hooked from a BSES YPL pole, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether he discharged the onus cast by the presumption in the third proviso to Section 135(1).</p>",
 facts="""<p>On 21 January 2021 at about 11.30 a.m., an inspection team of BSES Yamuna Power Ltd. headed by Sh. R.B. Yadav (Assistant Manager) inspected the ground-floor premises at H. No.&nbsp;B-10A, Khasra No.&nbsp;1/91, Gali No.&nbsp;1, Shastri Park, Delhi. No electricity meter was installed; the accused was found drawing supply through a yellow cable &mdash; 14 metres long &mdash; connected from a BSES YPL pole. The connected load was 1.501&nbsp;KW, the premises being used for scrap/labour work; one Sameer, the accused&rsquo;s worker, was present at the spot. Sh. Mohsin videographed the proceedings and furnished a Section 65B certificate; an Inspection Report, Load Report, Seizure Memo and Advisory Notice were prepared at the spot. The company assessed a theft demand of Rs.&nbsp;72,006/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;146/2021 was registered at PS Shastri Park.</p>
<p>The IO, HC Sushil Kumar, recorded the statement of the worker Sameer (Ex.PW1/G), who stated that he did scrap labour at the ground floor and that the accused committed the theft by hooking an illegal wire from the BSES pole. Notice under Section 251 Cr.P.C. was given on 3 April 2024; the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 HC Sushil Kumar (IO; proved the FIR, site plan, Section 41A notice, interrogation report, Aadhaar, ownership documents, Sameer&rsquo;s statement and the Pabandinama); PW-2 R.B. Yadav (team head; proved the CD, inspection report, load report, seizure memo, advisory notice, theft bill and complaint, and the seized 14-metre yellow cable Ex.P1); and PW-3 Mohsin (videographer; proved the video and the Section 65B certificate Ex.PW3/A). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication; he led no defence evidence. His counsel submitted that the civil liability had been settled and the amount deposited.</p>""",
 headnote="""A long cable hooked from the licensee&rsquo;s pole to run scrap work at unmetered premises is direct theft under Section 135(1)(a); a worker&rsquo;s statement placing the theft at the premises, the accused&rsquo;s failure to object to the advisory notice within the stipulated four days, and his settlement of the bill all corroborate guilt, and the unrebutted third-proviso presumption convicts.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the pole hook.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the yellow cable run from the BSES pole to the unmetered ground-floor premises as a clause (a) connection with the licensee&rsquo;s lines. On proof of that artificial means the third proviso&rsquo;s presumption arose."""),
  ("The inspection stood proved, and the worker&rsquo;s statement corroborated the theft.",
   """PW-2 and PW-3 were consistent on the absence of any meter, the pole-hooked cable, the 1.501&nbsp;KW load run entirely on the illegal wire, and the seizure; PW-2 testified that at inspection no electricity was drawn from any meter, the whole load running on the illegal cable. The IO proved the statement of the worker Sameer, who placed the scrap work at the ground floor and the theft on the accused; the accused never denied that Sameer was his worker there."""),
  ("The unanswered advisory notice fortified the finding of guilt.",
   """The advisory notice (Ex.PW2/E) expressly invited the accused to file a written objection to the inspection within four working days. He filed none &mdash; conduct the Court read as indicating involvement, since an innocent consumer would have objected before the competent authority."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested."""),
  ("The presumption was compulsory, and settlement of the bill fortified the case.",
   """Following <span class="cn">Neeraj Dutt</span> and <span class="cn">Hiten P. Dalal</span> on the compulsory presumption and its rebuttal standard, the Court noted the accused led no defence evidence, claimed no Genset, and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus). His settlement and deposit of the Rs.&nbsp;72,006/&#8209; bill, rather than protest against a false claim, fortified the prosecution case. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a long cable hooked from the licensee&rsquo;s pole",
 bill="Rs.&nbsp;72,006/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises and that Mustak Hussain was found indulging in direct theft of electricity through an illegal wire &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, he failed to rebut the statutory presumption. <strong>Mustak Hussain is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A scrap-workshop theft corroborated by a worker&rsquo;s statement and an unanswered advisory notice. Five propositions stand out:",
 significance=[
  ("A worker&rsquo;s statement can anchor occupancy and theft.",
   """Sameer&rsquo;s statement placed the scrap work &mdash; and the theft &mdash; at the accused&rsquo;s premises, and the accused never denied that Sameer was his worker there."""),
  ("Silence on the advisory notice cuts against the accused.",
   """The advisory notice invited a written objection within four working days; filing none was read as conduct consistent with guilt."""),
  ("Load size does not gate the offence.",
   """A modest 1.501&nbsp;KW load was still direct theft; the deliberately laid 14-metre cable showed an engineered, dishonest tap."""),
  ("Settlement corroborates guilt.",
   """Settling and depositing the theft bill was read as conduct inconsistent with innocence, not as neutral compromise."""),
  ("The reverse-onus presumption did the rest.",
   """No meter, an unexplained running load, no Genset, no paid bills &mdash; the compulsory presumption convicted."""),
 ],
)

build(c012, "case_012.html")
build(c013, "case_013.html")
build(c014, "case_014.html")
