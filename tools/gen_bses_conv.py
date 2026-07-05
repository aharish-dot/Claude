#!/usr/bin/env python3
"""BSES Yamuna convictions: 022, 024, 025 (owner-abettor, absconding user) via abet();
   020 (owner-abettor, co-accused tenant died -> abatement) and 028 (sole, direct theft) via build()."""
from gen_08_11 import build, STD_CITES
from gen_abet import abet, CITES_ABET

SUB_KKD = "Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi"

# ============ 022 Tilak Raj (two-core cable; user Akash; settlement+deposit+NOC) ============
abet(case_no="022", title="State v. Tilak Raj", sc="SC No.&nbsp;291/2021", fir="FIR No.&nbsp;476/2017", ps="PS Nand Nagri",
 doj="8 April 2026", dooff="24 October 2016",
 owner="State (BSES Yamuna Power Ltd.) <em>v.</em> Tilak Raj, R/o Nand Nagri, Delhi (registered consumer/owner of the inspected premises)",
 accused_name="Tilak Raj", user="Akash", team_head="its enforcement officer",
 mode_short="through a two-core cable tapped directly from the licensee&rsquo;s network, the premises having no meter",
 mode_full="No electricity meter was installed at the inspected premises; the supply was found being drawn through a two-core cable connected directly from the BSES YPL network, the user/tenant Akash being in occupation.",
 section_label="a clause (a) connection with the licensee&rsquo;s network",
 load="1.274", bill="84,637", noc=True, out="case_022.html")

# ============ 024 Nikhat (distribution-box tap; user Jahan Ara; wire not seized; settlement+deposit+NOC) ============
abet(case_no="024", title="State v. Nikhat", sc="SC No.&nbsp;908/2023", fir="FIR No.&nbsp;290/2022", ps="PS Seelampur",
 doj="6 April 2026", dooff="11 October 2021",
 owner="State (BSES Yamuna Power Ltd.) <em>v.</em> Nikhat, R/o Seelampur, Delhi (registered consumer/owner of the inspected premises)",
 accused_name="Nikhat", user="Jahan Ara", team_head="its enforcement officer",
 mode_short="through a wire tapped from the licensee&rsquo;s distribution box, the premises having no meter",
 mode_full="No electricity meter was installed at the inspected premises; the supply was found being drawn through an illegal wire connected from the Distribution Box of BSES YPL, used by the tenant Jahan Ara, who went untraced after the inspection. The illegal wire could not be removed and seized because of resistance at the spot.",
 section_label="a clause (a) connection with the licensee&rsquo;s distribution box",
 load="3.143", bill="53,982", noc=True,
 extra_sig=("Failure to seize the wire, amid resistance, is not fatal.",
   """That the illegal wire could not be removed because of resistance at the spot did not weaken the prosecution &mdash; the tap was independently established by the videography and the officials&rsquo; consistent testimony."""),
 out="case_024.html")

# ============ 025 Devanand (meter bypass; 4 meters; 3rd-floor service cable; user Rajesh; settlement+deposit) ============
abet(case_no="025", title="State v. Devanand", sc="SC No.&nbsp;263/2020", fir="FIR No.&nbsp;239/2019", ps="PS Gandhi Nagar",
 doj="13 March 2026", dooff="4 July 2019",
 owner="State (BSES Yamuna Power Ltd.) <em>v.</em> Devanand, R/o Gandhi Nagar, Delhi (registered consumer/owner of the inspected multi-unit premises)",
 accused_name="Devanand", user="Rajesh", team_head="its enforcement officer",
 mode_short="by bypassing the metering system &mdash; the premises&rsquo; four installed meters standing with their outgoing supply disconnected while the third-floor load ran directly through a service cable",
 mode_full="Four electricity meters were installed at the multi-unit premises but all their outgoing supplies stood disconnected, and the third-floor supply was found running directly through the service cable &mdash; a bypass of the metering system. The user/tenant Rajesh was not arrested.",
 section_label="a bypass of the metering system amounting to a dishonest abstraction under Section 135(1)",
 load="5.335", bill="4,57,556", noc=False,
 extra_sig=("Dead meters do not answer a service-cable bypass.",
   """That four meters stood installed did not help the owner where their outgoing supply was disconnected and the load ran directly through the service cable &mdash; the largest assessment among the abetment convictions (over Rs.&nbsp;4.5 lakh) followed from the connected load."""),
 out="case_025.html")

# ============ 020 Bobby Khurana (owner-abettor; co-accused tenant Shabbo died -> abatement; NO settlement) ============
c020 = dict(
 title="State v. Bobby Khurana",
 subcite="SC No.&nbsp;13/2024 &nbsp;|&nbsp; FIR No.&nbsp;310/2021, PS Welcome &nbsp;|&nbsp; " + SUB_KKD,
 doj="21 April 2026", dooff="24 March 2021",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Bobby Khurana S/o Sh. Raju Khurana, R/o H. No.&nbsp;J-16, Welcome, Delhi (registered consumer/owner of the inspected premises)",
 statutes="Sections 135, 150 &amp; 2(15) (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Section 106, Indian Evidence Act, 1872; Sections 251, 313 &amp; 41A, Cr.P.C.",
 result="<strong>Convicted under Section 135 read with Section 150 (abetment), Electricity Act, 2003.</strong> The co-accused tenant Shabbo, who actually used the electricity, having died during the trial, proceedings against her stood abated; the owner Bobby Khurana was convicted. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the tenant Shabbo (since deceased) dishonestly abstracted electricity at the inspected premises through a two-core cable hooked from BSES Pole No.&nbsp;GTR-I-438, the premises having no meter; whether the accused Bobby Khurana, the registered consumer/owner of those premises, abetted that theft by consciously permitting it, so as to be guilty under Section 135 read with Section 150 of the Electricity Act, 2003; and whether, once an unauthorised means of abstraction was proved, Bobby Khurana discharged the onus cast by the presumption in the third proviso to Section 135(1).</p>",
 facts="""<p>On 24 March 2021, an inspection team of BSES Yamuna Power Ltd. headed by Sh. N. Neela Kannan inspected the premises. No electricity meter was installed; the supply was being drawn through a two-core cable connected directly from BSES Pole No.&nbsp;GTR-I-438. The connected load was 3.076&nbsp;KW, used for domestic purposes; the tenant Shabbo was found to be the user of the electricity. The proceedings were videographed and an Inspection Report, Load Report and Seizure Memo (with an advisory notice) were prepared at the spot. Following the applicable tariff the company assessed a theft demand of Rs.&nbsp;51,349/&#8209;, which went unpaid, and its Authorised Officer filed a complaint under Section 135 read with Section 150 of the Act.</p>
<p>Shabbo was arraigned as a co-accused but died during the trial, and the proceedings against her abated; the prosecution proceeded against Bobby Khurana as the registered consumer/owner of the premises, whose ownership was proved through the seized documents. A notice under Section 251 Cr.P.C. was served and Bobby Khurana pleaded not guilty. The inspecting officials and the Investigating Officer were examined. Under Section 313 Cr.P.C. the accused denied the allegations and pleaded false implication, and led no defence evidence.</p>""",
 headnote="""A registered consumer/owner who consciously permits a tenant to draw an unauthorised supply from the licensee&rsquo;s network abets the theft and is guilty under Section 135 read with Section 150 &mdash; and the death of the actual user (abating the case against her) does not absolve the abettor, whose liability is independent of whether the principal is ever tried. &ldquo;Consumer&rdquo; in Section 2(15) reaches the owner (<span class="cn">Lokesh Chandela</span>), and the compulsory presumption in the third proviso to Section 135(1) convicts the owner who leads no evidence of lawful, metered use.""",
 reasoning=[
  ("The offence was made out on proof of an unauthorised abstraction at the owner&rsquo;s premises.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the two-core cable hooked from BSES Pole No.&nbsp;GTR-I-438 to the unmetered premises as a clause (a) connection with the licensee&rsquo;s lines. On proof of that artificial means the third proviso&rsquo;s presumption of dishonest use arose."""),
  ("The owner is a &ldquo;consumer&rdquo; under Section 2(15) and answerable for abstraction at the premises.",
   """Reproducing Section 2(15), the Court held that both the user and the owner/registered consumer fall within &ldquo;consumer,&rdquo; so Bobby Khurana was answerable once illegal abstraction was found at his premises &mdash; drawing support from <span class="cn">Lokesh Chandela v. State of NCT &amp; Ors.</span> (Delhi HC, Crl. A. 479/2011)."""),
  ("Conscious permission was abetment, and the user&rsquo;s death did not absolve the abettor.",
   """As registered consumer/owner, Bobby Khurana knew the premises had no lawful metered supply, yet permitted Shabbo to occupy and draw electricity through the unauthorised connection. That conscious allowance constituted abetment under Section 150, which carries the punishment of the principal offence. That Shabbo had died during the trial &mdash; abating the case against her &mdash; did not absolve the abettor: his liability is independent of whether the principal is ever tried."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity."""),
  ("The presumption was compulsory and, unrebutted, convicted.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court held that Bobby Khurana, having led no defence evidence and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus), failed to rebut the presumption. That the theft bill was never settled underscored, rather than diluted, the case against him."""),
 ],
 mode_desc="the drawing of supply to unmetered premises through a two-core cable hooked from the licensee&rsquo;s pole",
 bill="51,349",
 held="<p>The prosecution proved beyond reasonable doubt that no lawful metered supply existed at the inspected premises and that electricity was being abstracted through an unauthorised connection, which Bobby Khurana, as registered consumer/owner, consciously permitted. The death of the tenant Shabbo abated only the case against her. <strong>Bobby Khurana is accordingly convicted under Section 135 read with Section 150 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="An owner-as-abettor conviction where the actual user (the tenant Shabbo) died during trial and the case against her abated. Five propositions stand out:",
 significance=[
  ("An owner can be convicted of abetment even where the user is never tried.",
   """The registered consumer/owner who consciously permits a tenant to draw an unauthorised supply is guilty under Section 135 r/w Section 150; the death of the principal, abating her case, does not absolve the abettor."""),
  ("&ldquo;Consumer&rdquo; under Section 2(15) reaches the owner.",
   """The owner cannot disown liability for illegal abstraction at the premises merely because a tenant was the user (<span class="cn">Lokesh Chandela</span>)."""),
  ("The reverse-onus presumption binds the owner-abettor.",
   """Once the unauthorised means is proved, the owner must show lawful, metered use &mdash; paid bills under the Section 106 onus (<span class="cn">Mukesh Rastogi</span>) &mdash; failing which the compulsory presumption convicts."""),
  ("An unsettled bill is no mitigation of the charge.",
   """Unlike the settled-bill cases, here the theft demand was never paid; the Court treated the unpaid, unrebutted assessment as fortifying the prosecution."""),
  ("A public witness is not essential.",
   """Official inspection testimony suffices absent shown enmity (<span class="cn">Ashwani Kumar</span>; <span class="cn">Sushil Sharma</span>)."""),
 ],
 cites=CITES_ABET)
build(c020, "case_020.html")

# ============ 028 Shehzad (SOLE accused; direct theft s.135; punctured service cable; present; settlement) ============
c028 = dict(
 title="State v. Shehzad",
 subcite="SC No.&nbsp;898/2023 &nbsp;|&nbsp; FIR No.&nbsp;717/2022, PS Jafrabad &nbsp;|&nbsp; " + SUB_KKD,
 doj="15 January 2026", dooff="8 March 2022",
 parties="State (BSES Yamuna Power Ltd.) <em>v.</em> Shehzad, R/o Jafrabad, Delhi",
 statutes="Section 135 (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Sections 65B &amp; 106, Indian Evidence Act, 1872; Sections 251, 313 &amp; 41A, Cr.P.C.",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> Civil liability on the theft bill (Rs.&nbsp;80,516/&#8209;) settled and the amount deposited during trial. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Shehzad dishonestly abstracted electricity at his premises by puncturing the licensee&rsquo;s service cable and drawing supply ahead of the meter, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether, an unauthorised means of abstraction having been proved, he discharged the onus cast by the presumption in the third proviso to Section 135(1).</p>",
 facts="""<p>On 8 March 2022, an inspection team of BSES Yamuna Power Ltd. inspected the premises of the accused Shehzad. The licensee&rsquo;s service cable was found punctured, the supply being drawn directly through the puncture so as to bypass measurement. The connected load was 5.427&nbsp;KW. The accused was present at the inspection. The proceedings were videographed and a Section 65B certificate furnished; an Inspection Report, Load Report, Seizure Memo and advisory notice were prepared at the spot. Following the applicable tariff the company assessed a theft demand of Rs.&nbsp;80,516/&#8209;, which went unpaid, and on its Authorised Officer&rsquo;s complaint FIR No.&nbsp;717/2022 was registered at PS Jafrabad.</p>
<p>A notice under Section 251 Cr.P.C. was served and the accused pleaded not guilty. The inspecting officials and the Investigating Officer were examined and the videography and Section 65B certificate proved. Under Section 313 Cr.P.C. the accused denied the allegations and pleaded false implication, and led no defence evidence. His counsel submitted that the civil liability had been settled and the settlement amount deposited during trial.</p>""",
 headnote="""Puncturing the licensee&rsquo;s service cable to draw supply ahead of the meter is a direct, artificial abstraction under Section 135(1)(a); the accused being present at the videographed inspection, his identity as the person indulging in theft was fixed, and the unrebutted third-proviso presumption &mdash; he leading no evidence and producing no paid bills &mdash; convicts. Settlement of the theft bill corroborates, rather than closes, the criminal charge.""",
 reasoning=[
  ("A punctured service cable is a clause (a) abstraction.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the puncturing of the licensee&rsquo;s service cable &mdash; drawing supply ahead of the meter &mdash; as a clause (a) tapping of the licensee&rsquo;s line. On proof of that artificial means the third proviso&rsquo;s presumption of dishonest use arose."""),
  ("The accused&rsquo;s presence at the videographed inspection fixed his identity.",
   """Unlike the abetment cases where the user had absconded, Shehzad was present at the inspection of his own premises; the videography and the Section 65B certificate established the factum and manner of the abstraction and fixed him as the person indulging in the theft."""),
  ("The electronic record was duly proved.",
   """The videography was accompanied by a Section 65B certificate, satisfying the condition for admissibility of the electronic record; the officials&rsquo; consistent testimony proved the inspection, the punctured cable and the connected load."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity."""),
  ("The presumption was compulsory, and settlement of the bill fortified the case.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court held that Shehzad, having led no defence evidence and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus), failed to rebut the presumption; and his settlement and deposit of the Rs.&nbsp;80,516/&#8209; bill corroborated the theft rather than answering the criminal charge."""),
 ],
 mode_desc="the abstraction of supply by puncturing the licensee&rsquo;s service cable to draw power ahead of the meter",
 bill="80,516",
 held="<p>The prosecution proved beyond reasonable doubt that the accused Shehzad abstracted electricity by puncturing the licensee&rsquo;s service cable and drawing supply ahead of the meter, an offence punishable under Section 135 of the Electricity Act, 2003, and that he led no evidence to rebut the statutory presumption. <strong>Shehzad is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A sole-accused, direct-theft conviction where the accused was present at inspection &mdash; contrasting the owner-abettor pattern. Five propositions stand out:",
 significance=[
  ("Puncturing the service cable is direct theft.",
   """Drawing supply through a puncture in the licensee&rsquo;s service cable, ahead of the meter, is a clause (a) abstraction &mdash; no separate hooked wire is needed."""),
  ("Presence at inspection fixes identity.",
   """Where the accused is himself present at the videographed inspection of his premises, the recurring &ldquo;who was the user&rdquo; defence is unavailable."""),
  ("A Section 65B certificate secures the video.",
   """The certified videography proved the manner of abstraction and dispensed with any need for a public witness."""),
  ("Settlement corroborates guilt.",
   """Settling and depositing the theft bill was read as conduct inconsistent with innocence, not a neutral compromise."""),
  ("The reverse-onus presumption did the rest.",
   """No meter reading, an unexplained tapped load, no paid bills &mdash; the compulsory presumption convicted (<span class="cn">Neeraj Dutt</span>; <span class="cn">Hiten P. Dalal</span>; <span class="cn">Mukesh Rastogi</span>)."""),
 ],
 cites=STD_CITES)
build(c028, "case_028.html")
print("BSES convictions 020,022,024,025,028 generated.")
