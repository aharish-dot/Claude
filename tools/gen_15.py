#!/usr/bin/env python3
from gen_08_11 import build, STD_CITES

BALU = ("Balu Sudam Khalde v. State of Maharashtra", "2023 INSC 314",
        "Incriminating suggestions put by defence counsel in cross-examination bind the accused and can themselves establish facts such as the factum of, and presence at, the inspection.")
CITES_015 = [STD_CITES[0], STD_CITES[1], BALU, STD_CITES[2], STD_CITES[3], STD_CITES[4]]

c015 = dict(
 title="State v. Laxmi Mishra",
 subcite="SC No.&nbsp;403/2021 &nbsp;|&nbsp; FIR No.&nbsp;48/2021, PS Sonia Vihar &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
 doj="12 March 2026", dooff="16 January 2020",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Laxmi Mishra W/o Sh. Adesh Mishra, R/o G-5/69, Gali No.&nbsp;5, Sonia Vihar, Delhi (inspected premises: H. No.&nbsp;2674, Gali No.&nbsp;16, Pusta-5, Sonia Vihar)",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Laxmi Mishra dishonestly abstracted electricity at her unmetered premises (used for mixed commercial and domestic purposes) by illegally tapping from the Distribution Box of BSES YPL, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether &mdash; having obstructed the inspection, removed the tapped wires before they could be seized, and given the inspectors a false name &mdash; she discharged the onus cast by the third proviso to Section 135(1), her plea of solar power being unsupported by any evidence.</p>",
 facts="""<p>On 16 January 2020 at about 7.41 a.m., a joint inspection team of BSES Yamuna Power Ltd. headed by Sh. Ravi Kumar Tiwari (Assistant Manager) inspected the premises at H. No.&nbsp;2674, Gali No.&nbsp;16, Pusta-5, Sonia Vihar, Delhi. No electricity meter was installed; the accused was found drawing supply by illegal tapping from the Distribution Box of BSES YPL. The connected load was 1.835&nbsp;KW, used for commercial as well as domestic purposes. The inspection was actively resisted: the five-member team could not get the premises opened; the accused&rsquo;s ground-floor shop opened only briefly before her son pulled down its shutter; the load could not be captured on videography because of the accused&rsquo;s resistance and was instead taken physically on her own verbal disclosure; and the illegal wires could not be seized because the accused removed them and, despite repeated requests, refused to hand them over. Sh. Mukesh Kumar videographed what proceedings he could and furnished a Section 65B certificate. The company assessed a theft demand of Rs.&nbsp;61,827/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;48/2021 was registered at PS Sonia Vihar.</p>
<p>During investigation it emerged that the accused had given a false name &mdash; &ldquo;Geeta&rdquo; &mdash; at the inspection to conceal her identity. Notice under Section 251 Cr.P.C. was given on 12 April 2023; the accused pleaded not guilty. The prosecution examined three witnesses: PW-1 ASI Narender Singh (IO; proved the FIR, Section 41A notice, interrogation report, Aadhaar, ownership documents and Pabandinama, and deposed to the false name); PW-2 Ravi Kumar Tiwari (team head; proved the CD, inspection report, load report, advisory notice, theft bill and complaint); and PW-3 Mukesh Kumar (videographer; proved the video and the Section 65B certificate Ex.PW3/A). Under Section 313 Cr.P.C. the accused denied everything and pleaded false implication; she led no defence evidence, her counsel merely suggesting &mdash; without proof &mdash; that she was using solar power.</p>""",
 headnote="""Obstructing an inspection &mdash; refusing to open the premises, spiriting away the tapped wires, and giving a false name &mdash; does not defeat a Section 135 prosecution; the offence is proved by the officials&rsquo; consistent testimony, the videographed proceedings and the load taken on the accused&rsquo;s own disclosure, and her obstruction and concealment are themselves circumstances of guilt. A bare, unproved plea of solar power cannot rebut the compulsory presumption in the third proviso to Section 135(1).""",
 reasoning=[
  ("Section 135(1)(a) was engaged by the distribution-box tap.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the illegal tapping from the BSES YPL Distribution Box to the unmetered premises as a clause (a) connection with the licensee&rsquo;s works. On proof of that artificial means the third proviso&rsquo;s presumption arose."""),
  ("Obstruction and concealment were treated as circumstances of guilt.",
   """The accused refused to open the premises to a five-member team; her son shut the shop shutter; the tapped wires were removed and, despite repeated requests, never handed over; and she gave the inspectors a false name, &ldquo;Geeta,&rdquo; exposed only in investigation. Far from creating a doubt, this conduct was read as demonstrating the accused&rsquo;s malafide intention and active involvement in the theft."""),
  ("The load stood proved though the wires were never seized and the video could not capture it.",
   """Because the accused&rsquo;s resistance prevented videographic capture of the load, it was taken physically on her own verbal disclosure &mdash; and never disputed in cross-examination, where she did not challenge the load report. That the wires could not be seized (the accused having removed them) did not defeat proof of the tap: the officials&rsquo; consistent testimony and the videographed proceedings established it. The defence&rsquo;s own question to the videographer about the make of the handycam was, on <span class="cn">Balu Sudam Khalde v. State of Maharashtra</span>, 2023 INSC 314, an admission of the factum of videography."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested."""),
  ("The unproved solar-power plea could not rebut the compulsory presumption.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court held that the defence&rsquo;s bare suggestion of solar power, put forward without a shred of evidence, could not make the defence reasonably probable. The accused led no defence evidence, claimed no Genset, and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus); nor was there any evidence that the videographed premises were not hers. The presumption stood unrebutted."""),
 ],
 mode_desc="the drawing of supply to unmetered premises by illegal tapping from the licensee&rsquo;s distribution box",
 bill="Rs.&nbsp;61,827/&#8209;",
 held="<p>The prosecution proved beyond reasonable doubt that no electricity meter was available at the accused&rsquo;s premises and that Laxmi Mishra was found indulging in direct theft of electricity through illegal wires &mdash; an offence punishable under Section 135 of the Electricity Act, 2003. Having led no evidence and offered only an unproved solar-power plea, she failed to rebut the statutory presumption. <strong>Laxmi Mishra is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A rare obstruction case &mdash; the accused fought the inspection, hid the wires and gave a false name, yet was convicted. Six propositions stand out:",
 significance=[
  ("Obstruction is a circumstance of guilt.",
   """Refusing to open the premises, removing the tapped wires, and giving a false name were read as malafide conduct pointing to involvement &mdash; not as gaps in the prosecution."""),
  ("The load can be proved without seizing the wires.",
   """Where the accused spirits away the case property, the load taken physically on her own disclosure, together with the videographed proceedings, still proves the theft."""),
  ("A false name backfires.",
   """Giving the inspectors a wrong name (&ldquo;Geeta&rdquo;), exposed in investigation, corroborated dishonest intention rather than raising a doubt about identity."""),
  ("An unproved solar-power plea is no rebuttal.",
   """A bare suggestion of solar power, unsupported by any evidence, cannot discharge the third-proviso onus &mdash; only proof of lawful, metered use (paid bills; Section 106 onus, <span class="cn">Mukesh Rastogi</span>) will."""),
  ("Defence questions can admit the inspection.",
   """Asking the videographer about the make of the handycam admitted the factum of videography (<span class="cn">Balu Sudam Khalde</span>)."""),
  ("A public witness remains unnecessary.",
   """Official inspection testimony, videographed and 65B-certified, suffices absent shown enmity (<span class="cn">Ashwani Kumar</span>; <span class="cn">Sushil Sharma</span>)."""),
 ],
 cites=CITES_015,
)

build(c015, "case_015.html")
