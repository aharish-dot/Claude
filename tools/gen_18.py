#!/usr/bin/env python3
from gen_08_11 import build

c018 = dict(
 title="State v. Imran",
 subcite="SC No.&nbsp;743/2023 &nbsp;|&nbsp; FIR No.&nbsp;187/2022, PS Seelampur &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="11 March 2026", dooff="3 February 2022",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Imran S/o Late Salauddin, R/o B-94, 4th Floor, near Main Market, New Seelampur, Delhi&#8209;110053",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Civil liability on the theft bill (Rs.&nbsp;11,61,828/&#8209;) settled and the amount deposited during trial. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Imran dishonestly abstracted electricity at his unmetered fourth-floor premises &mdash; powering a GSM (mobile telecom) antenna tower as well as domestic use &mdash; through a two-core black wire hooked from BSES Pole No.&nbsp;YVR-V-306, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether, the entire tapping wire not having been seized and the accused being absent at the inspection, he discharged the onus cast by the presumption in the third proviso to Section 135(1).</p>",
 facts="""<p>On 3 February 2022 at about 1.45 p.m., an enforcement team of BSES Yamuna Power Ltd. headed by Sh. Saurabh Sharma (Manager) inspected the fourth-floor premises at H. No.&nbsp;B-94, near Main Market, New Seelampur, Delhi. No electricity meter was installed; supply was being drawn through a yellow wire connected from the pole (near the transformer) and joined onward to a two-core black wire at the balcony of the premises, tapped from BSES Pole No.&nbsp;YVR-V-306 some 12&#8211;15 metres away. The connected load was 14.046&nbsp;KW &mdash; powering a GSM antenna tower on the premises as well as domestic use. The accused was not present; family members present identified Imran as the owner and user of the electricity. Sh. Deepak Kumar videographed the proceedings and furnished a Section 65B certificate; an Inspection Report, Load Report, Seizure Memo and Advisory Notice were prepared at the spot. Following the applicable (commercial) tariff, the company assessed a theft demand of Rs.&nbsp;11,61,828/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;187/2022 was registered at PS Seelampur.</p>
<p>Only the accessible black wire (the case property) was seized and sealed; the yellow segment could not be removed because of its excessive height. Notice under Section 251 Cr.P.C. was given on 16 November 2023; the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 Saurabh Sharma (team head; proved the CD, inspection report, load report, seizure memo, advisory notice, theft bill and complaint); PW-2 Deepak Kumar (videographer; proved the video and the Section 65B certificate Ex.PW2/1); and PW-3 ASI Devraj (IO; proved the FIR, site plan, Section 41A notice, Aadhaar and ownership documents, and Pabandinama). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication; he led no defence evidence. His counsel submitted that the civil liability had been settled and the settlement amount deposited.</p>""",
 headnote="""Powering a GSM antenna tower from unmetered premises by hooking the licensee&rsquo;s pole is direct theft under Section 135(1)(a) &mdash; the telecom load producing an assessment of over Rs.&nbsp;11.6 lakh &mdash; and neither the accused&rsquo;s absence at the inspection (family members identifying him as owner and user) nor the failure to seize the entire tapping wire (part being out of reach) defeats the prosecution. The unrebutted third-proviso presumption convicts.""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the pole hook feeding the antenna tower.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the wire run from BSES Pole No.&nbsp;YVR-V-306 to the unmetered premises &mdash; feeding a GSM antenna tower and domestic load &mdash; as a clause (a) connection with the licensee&rsquo;s lines. On proof of that artificial means the third proviso&rsquo;s presumption arose."""),
  ("The inspection was proved though the accused was absent.",
   """The accused was not at the premises during the inspection, but his family members present identified him as the owner and user of the electricity &mdash; a fact he never denied in cross-examination. PW-1 explained the mode of theft (a yellow wire from the pole near the transformer joined to a black wire at the balcony), the 14.046&nbsp;KW load and the running antenna tower; the consistent testimony and the videography established the factum and manner of the theft and fixed the accused as the consumer."""),
  ("Partial seizure of the tapping wire was not fatal.",
   """The defence pressed that the case property was planted because the entire wire was not seized. The Court accepted PW-1&rsquo;s explanation that the yellow segment could not be removed due to its excessive height, while the accessible black wire was seized and sealed; and it held that seizure of the wire is only extra corroborative material &mdash; the theft having been independently videographed &mdash; so non-seizure of the whole did not weaken the case."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested."""),
  ("The presumption was compulsory, and settlement of the bill fortified the case.",
   """Following <span class="cn">Neeraj Dutt</span> and <span class="cn">Hiten P. Dalal</span> on the compulsory presumption and its rebuttal standard, the Court noted the accused led no defence evidence, claimed no Genset, and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus). His settlement and deposit of the Rs.&nbsp;11,61,828/&#8209; bill, rather than protest against a false claim, fortified the prosecution case. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises &mdash; powering a telecom antenna tower &mdash; through a wire hooked from the licensee&rsquo;s pole",
 bill="Rs.&nbsp;11,61,828/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises and that Imran was found (through the inspection, the family&rsquo;s identification and the videography) to be the user indulging in direct theft of electricity through an illegal wire &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence, he failed to rebut the statutory presumption. <strong>Imran is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="The largest theft in the set &mdash; a mobile-tower installation drawing 14&nbsp;KW off a pole hook, assessed at over Rs.&nbsp;11.6 lakh. Six propositions stand out:",
 significance=[
  ("Telecom/commercial loads drive the assessment sky-high.",
   """Powering a GSM antenna tower (14.046&nbsp;KW) produced a Rs.&nbsp;11,61,828/&#8209; bill &mdash; roughly twenty times a typical domestic tap &mdash; because the assessment follows the actual (commercial) tariff, doubled under Regulation 63."""),
  ("The accused&rsquo;s absence at inspection is no shield.",
   """Family members present identifying him as the owner and user, coupled with his failure to deny it, fixed the accused as the &ldquo;consumer&rdquo; answerable for the theft."""),
  ("Partial seizure of the wire is not fatal.",
   """Where part of the tapping wire is out of reach, seizing the accessible segment suffices; seizure is only corroborative, the theft being videographed."""),
  ("A rooftop tower is not an innocent explanation.",
   """That the load ran a functioning telecom tower confirmed a substantial, sustained abstraction rather than incidental domestic use."""),
  ("Settlement corroborates guilt.",
   """Settling and depositing the (very large) theft bill was read as conduct inconsistent with innocence."""),
  ("The reverse-onus presumption did the rest.",
   """No meter, an unexplained running load, no Genset, no paid bills &mdash; the compulsory presumption convicted (<span class="cn">Neeraj Dutt</span>; <span class="cn">Hiten P. Dalal</span>; <span class="cn">Mukesh Rastogi</span>)."""),
 ],
)

build(c018, "case_018.html")
