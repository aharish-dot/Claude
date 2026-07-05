#!/usr/bin/env python3
"""Acquittal factory. Section 135 acquittals turning on failure of the foundational facts:
   identity of the user, a self-contradictory inspection, withheld material witnesses, missing
   Section 65B certification, or defective authorisation of the complaint. Shared spine +
   per-case grounds. Covers 026, 027, 032, 035, 042-049."""
from gen_08_11 import build, STD_CITES

MUKESH = STD_CITES[4]
KRISHNA = ("Krishna Gupta v. State", "Delhi HC",
  "The prosecution must prove the accused&rsquo;s direct nexus with the abstraction; mere presence at or proximity to the spot, without evidence of control or consumption, does not establish theft.")
AMIT_BANSAL = ("Tata Power Delhi Distribution Ltd. v. Amit Bansal", "Delhi HC",
  "Liability under Section 135 attaches only on proof that the accused was the actual consumer/user of the inspected premises.")
SATYE = ("Satye Singh v. State of Uttarakhand", "(2022) 5 SCC 438",
  "Section 106 of the Evidence Act does not relieve the prosecution of its primary burden of proof; it applies only to facts especially within the accused&rsquo;s knowledge.")
SHAMBU = ("Shambhu Nath Mehra v. State of Ajmer", "AIR 1956 SC 404",
  "Section 106 is an exception confined to facts within the accused&rsquo;s special knowledge and cannot be used to shift the prosecution&rsquo;s burden onto the accused.")
SADHU = ("Sadhu Singh v. State of Punjab", "&mdash;",
  "Material contradictions in the prosecution&rsquo;s own evidence entitle the accused to the benefit of the doubt.")
KALIRAM = ("Kali Ram v. State of Himachal Pradesh", "(1973) 2 SCC 808",
  "Where two views are reasonably possible on the evidence, the one favouring the accused must be adopted; the presumption of innocence is not lightly displaced.")
HANUMANT = ("Hanumant Govind Nargundkar v. State of M.P.", "AIR 1952 SC 343",
  "In a case of circumstantial evidence the proved circumstances must form a chain so complete as to exclude every reasonable hypothesis save the guilt of the accused.")
SUJIT = ("Sujit Biswas v. State of Assam", "(2013) 12 SCC 406",
  "Suspicion, however grave, cannot take the place of proof; the gap between &lsquo;may be true&rsquo; and &lsquo;must be true&rsquo; must be bridged by legal evidence.")
DAHIYA = ("State (CBI) v. Mahender Singh Dahiya", "(2011) 3 SCC 585",
  "The chain of circumstances, including scientific and expert material, must be conclusive and point only to the guilt of the accused.")
RAMESH = ("Ramesh Harijan v. State of U.P.", "(2012) 5 SCC 777",
  "Evidence must be appreciated with care; a finding cannot rest on testimony that does not inspire confidence.")
ANOOP = ("Anoop Joshi v. State", "Delhi HC",
  "Where public witnesses were available but not joined, the prosecution must meet a higher standard to establish the recovery and inspection.")
NARINDER = ("Narinder Aggarwal v. BSES Rajdhani Power Ltd.", "Delhi HC, W.P.(C) 1789/2011",
  "An assessment/speaking order must record the authority&rsquo;s own independent reasoning; a burnt meter is not necessarily a tampered meter.")

ACQUIT_INTERP = """  <h3 class="grp">Electricity Act, 2003</h3>
  <h3>Section 135(1) &mdash; Theft of Electricity: the Foundational Facts</h3>
  <p>The Court read Section 135(1) as requiring the prosecution first to prove, beyond reasonable doubt, the foundational facts &mdash; an unauthorised or artificial abstraction of electricity <em>and</em> the identity of the accused as its author or as the consumer/user of the inspected premises. Only upon proof of those facts does the offence, or the abetment of it, arise; a bare allegation, or mere presence at or near the spot, is not enough. As the Act does not define &ldquo;dishonestly,&rdquo; Section 24 IPC is imported, but dishonest intention presupposes an abstraction first fixed on the accused.</p>
  <h3>Third Proviso to Section 135(1) &mdash; When the Presumption Does Not Arise</h3>
  <p>The reverse-onus presumption of dishonest use operates only after the prosecution has established the artificial means of abstraction and connected it to the accused. Where that foundation fails &mdash; the inspection is self-contradictory, the user&rsquo;s identity is not fixed, material witnesses are withheld, the electronic record is not duly certified under Section 65B, or the officer&rsquo;s authority to complain is not proved &mdash; the presumption never arises. The ordinary rule then governs: the prosecution must prove guilt beyond reasonable doubt, and where two views are reasonably possible the one favouring the accused is adopted.</p>"""

def acquit(*, title, docket, court, judge, doj, dooff, parties, sections_label, one_line,
           charge, facts, headnote, grounds, ratio_summary, significance, sig_intro, cites,
           statutes=None, out):
    framing = ("The presumption arises only after the prosecution proves the foundational facts.",
      """The Court proceeded from first principles: the third proviso to Section 135(1) is a reverse-onus clause that operates only once the prosecution has proved, beyond reasonable doubt, both an unauthorised abstraction of electricity and the identity of the accused as its author or the consumer of the premises. Until that foundation is laid the ordinary burden rests on the prosecution, and where two views are reasonably possible the one favouring the accused must be preferred.""")
    conclusion = ("The cumulative doubt entitled the accused to acquittal.",
      f"""With {ratio_summary}, the foundational facts were not established to the standard the law requires. The statutory presumption never arose, the benefit of the doubt went to the accused, and the charge under {sections_label} was not brought home.""")
    reasoning = [framing] + grounds + [conclusion]
    result = (f"<strong>Acquitted &mdash; complaint dismissed.</strong> {one_line} "
              f"The accused stands acquitted of the charge under {sections_label}.")
    c = dict(
      title=title, subcite=f"{docket} &nbsp;|&nbsp; {court}", court=court, judge=judge,
      doj=doj, dooff=dooff, parties=parties, result=result, charge=charge, facts=facts,
      headnote=headnote, interp=ACQUIT_INTERP, mode_desc="",
      statutes=statutes or "Section 135 (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Sections 101, 106 &amp; 65B, Indian Evidence Act, 1872; Sections 251 &amp; 313, Cr.P.C.",
      reasoning=reasoning, bill="&mdash;",
      held=(f"<p>The prosecution having failed to prove the foundational facts &mdash; {ratio_summary} &mdash; the charge under {sections_label} was not established beyond reasonable doubt. <strong>The accused is accordingly acquitted, and the complaint is dismissed.</strong></p>"),
      sig_intro=sig_intro, significance=significance, cites=cites)
    build(c, out)

ROHINI = "Court of the Additional Sessions Judge (Electricity), North&#8209;West District, Rohini Courts, Delhi"
DWARKA = "Court of the Additional Sessions Judge (Electricity), South&#8209;West District, Dwarka Courts, Delhi"
SAKET = "Special Court (Electricity), South District, Saket Courts, New Delhi"

# ================= 026 Vinod Kumar (e-rickshaw; not present; activity outside premises) =================
acquit(title="State v. Vinod Kumar", docket="Ct. Case No.&nbsp;325/2024 &nbsp;|&nbsp; PS Mangol Puri",
 court=ROHINI, judge="Sh. Kuljeevan Sidhar, Addl. Sessions Judge (Electricity)",
 doj="2 July 2026", dooff="date of inspection",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Vinod Kumar (alleged operator of an e-rickshaw charging point)",
 sections_label="Section 135 of the Electricity Act, 2003",
 one_line="The alleged theft was found to have been carried on outside the accused&rsquo;s registered premises, with no proof that he operated the charging point.",
 charge="<p>Whether the accused Vinod Kumar dishonestly abstracted electricity to run an e-rickshaw charging point, so as to attract Section 135(1) of the Electricity Act, 2003; and whether the prosecution proved that the abstraction was his, given that the alleged activity was found outside his registered premises.</p>",
 facts="""<p>An enforcement team of TPDDL alleged direct theft of electricity by a meter bypass and an LV-cable tap said to feed a large e-rickshaw charging load (a connected load of some 37.5&nbsp;KW, assessed at about Rs.&nbsp;18.97&nbsp;lakh). The accused was not present at the inspection, and the tapping/charging activity was found at an open area outside his registered premises. The team prepared the usual inspection documents; no operator or e-rickshaw owner was examined.</p>
<p>On a complaint under Section 135, the accused pleaded not guilty. The prosecution examined its officials. Under Section 313 Cr.P.C. the accused denied the allegations and led no defence evidence, contending that he neither ran the charging point nor was shown to have any control over it.</p>""",
 headnote="""A very large assessment for an e-rickshaw charging load does not convict where the abstraction was found outside the accused&rsquo;s registered premises, the accused was absent at the inspection, and no evidence &mdash; no operator, no e-rickshaw owner, no proof of control or collection of charges &mdash; connected him to the activity. Presence in the vicinity is not proof of theft.""",
 grounds=[
  ("The abstraction was located outside the registered premises.",
   """The alleged tap and charging activity were found not at the accused&rsquo;s registered premises but at an open area outside it; the prosecution offered nothing to bring that external activity home to the accused as its author."""),
  ("The accused&rsquo;s absence and the missing witnesses left identity unproved.",
   """The accused was not present at the inspection; no e-rickshaw owner or operator was examined, and there was no documentary proof that the accused controlled the charging point or collected charges &mdash; on <span class="cn">Krishna Gupta v. State</span>, mere proximity does not establish the direct nexus the offence requires."""),
  ("The scale of the assessment could not supply the missing proof.",
   """That the assessed load and demand were large (some 37.5&nbsp;KW / Rs.&nbsp;18.97&nbsp;lakh) went to quantum, not authorship; the accused could as easily have rebutted the presumption with paid bills (<span class="cn">Mukesh Rastogi</span>) had the foundational nexus been proved &mdash; but it was not."""),
 ],
 ratio_summary="the abstraction located outside the registered premises, the accused absent at the inspection and no witness connecting him to the charging point",
 significance=[
  ("Theft found outside the registered premises must still be tied to the accused.",
   """An abstraction in an open/public area is not automatically the registered consumer&rsquo;s; the prosecution must prove his control over the tapping or charging activity."""),
  ("Absence at inspection plus missing operators is fatal to identity.",
   """Where the accused is absent and no operator or beneficiary is examined, the &ldquo;who ran it&rdquo; question is left open (<span class="cn">Krishna Gupta</span>)."""),
  ("A large assessment is not a substitute for proof of authorship.",
   """The size of the load or bill goes to quantum; it cannot fill a gap in proof of who abstracted the electricity."""),
  ("The presumption never arose.",
   """Without the foundational nexus, the third-proviso presumption did not engage, and the ordinary burden defeated the prosecution."""),
 ],
 sig_intro="The largest assessment in the entire set (over Rs.&nbsp;18.9 lakh for a 37.5&nbsp;KW e-rickshaw load) &mdash; yet an acquittal, because authorship was never proved. Four propositions stand out:",
 cites=[KRISHNA, MUKESH], out="case_026.html")

# ================= 027 Smt. Rakhi (not resident; Aadhaar address different; s.150) =================
acquit(title="State v. Smt. Rakhi", docket="Ct. Case No.&nbsp;459/2024 &nbsp;|&nbsp; PS Inder Puri",
 court=ROHINI, judge="Sh. Syed Zishan Ali, Addl. Sessions Judge (Electricity)",
 doj="date of judgment", dooff="date of inspection",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Smt. Rakhi (alleged consumer of the inspected premises)",
 sections_label="Section 135 read with Section 150 of the Electricity Act, 2003",
 one_line="The prosecution failed to prove that the accused was the resident/consumer of the inspected premises, her own Aadhaar showing a different address.",
 charge="<p>Whether the accused Smt. Rakhi abstracted, or abetted the abstraction of, electricity at the inspected premises through a direct tap, so as to attract Section 135 read with Section 150 of the Electricity Act, 2003; and whether the prosecution proved that she was the consumer/user of those premises.</p>",
 facts="""<p>An enforcement team of TPDDL alleged direct tapping of the licensee&rsquo;s network at the inspected premises (a connected load of about 11&nbsp;KW, assessed at about Rs.&nbsp;2.55&nbsp;lakh) and named Smt. Rakhi as the consumer. Her Aadhaar card, however, recorded a different address, and the prosecution led no cogent evidence that she resided at or used the inspected premises.</p>
<p>On a complaint under Section 135 read with Section 150, the accused pleaded not guilty and denied being the resident/consumer. The prosecution examined its officials; under Section 313 Cr.P.C. the accused denied the allegations and led no defence evidence.</p>""",
 headnote="""Where the accused&rsquo;s own identity document shows a different address and the prosecution leads no reliable proof that she resided at or consumed electricity from the inspected premises, neither Section 135 nor abetment under Section 150 is made out; the burden to prove that she was the &ldquo;consumer&rdquo; lies on the prosecution and is not shifted by Section 106.""",
 grounds=[
  ("The accused&rsquo;s residence at the premises was not proved.",
   """The accused&rsquo;s Aadhaar card recorded an address different from the inspected premises, and the prosecution produced no tenancy, ownership or consumption evidence tying her to them &mdash; on <span class="cn">Tata Power Delhi Distribution Ltd. v. Amit Bansal</span>, liability attaches only on proof that the accused was the actual consumer/user."""),
  ("Section 106 did not cure the gap.",
   """The prosecution could not invoke Section 106 to shift onto the accused the burden of proving that she did <em>not</em> live there: on <span class="cn">Shambhu Nath Mehra</span> and <span class="cn">Satye Singh</span>, Section 106 is confined to facts within the accused&rsquo;s special knowledge and does not relieve the prosecution of its primary burden."""),
  ("No user being fixed, abetment under Section 150 also failed.",
   """Abetment presupposes a principal offence by an identified user; the user/consumer never being established, there was no theft that the accused could be said to have abetted."""),
 ],
 ratio_summary="the accused&rsquo;s Aadhaar showing a different address and no evidence that she resided at or consumed electricity from the inspected premises",
 significance=[
  ("Consumer status must be proved, not assumed.",
   """Naming a person in the complaint is not proof that she is the consumer; a contrary identity document defeats the assumption (<span class="cn">Amit Bansal</span>)."""),
  ("Section 106 cannot plug a hole in the prosecution&rsquo;s own case.",
   """The onus to prove residence/consumption stays with the prosecution (<span class="cn">Shambhu Nath Mehra</span>; <span class="cn">Satye Singh</span>)."""),
  ("Abetment falls with the principal offence.",
   """No identified user means no theft to abet under Section 150."""),
  ("A different Aadhaar address is powerful exculpatory material.",
   """The accused&rsquo;s own official record placing her elsewhere raised a reasonable doubt the prosecution could not dispel."""),
 ],
 sig_intro="An acquittal on identity of the consumer &mdash; the accused&rsquo;s Aadhaar placed her elsewhere. Four propositions stand out:",
 cites=[AMIT_BANSAL, SHAMBU, SATYE], out="case_027.html")

# ================= 032 Aamer Suhail (contradictions; meter existed but reported absent) =================
acquit(title="State v. Aamer Suhail", docket="Ct. Case No.&nbsp;92/2024 &nbsp;|&nbsp; PS Kanjhawala",
 court=ROHINI, judge="Sh. Prashant Kumar, Addl. Sessions Judge (Electricity)",
 doj="8 January 2026", dooff="date of inspection",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Aamer Suhail S/o Md. Saleem (tenant/resident of the inspected premises)",
 sections_label="Section 135 of the Electricity Act, 2003",
 one_line="The inspection documents were internally false &mdash; a meter that in fact existed was recorded as non-existent, and only external photographs were taken.",
 charge="<p>Whether the accused Aamer Suhail dishonestly abstracted electricity at the inspected premises, so as to attract Section 135(1) of the Electricity Act, 2003; and whether the prosecution&rsquo;s inspection, which recorded a non-existent state of affairs, proved the abstraction beyond reasonable doubt.</p>",
 facts="""<p>An enforcement team of TPDDL alleged a direct tap at the inspected premises (a connected load of about 6&nbsp;KW, assessed at about Rs.&nbsp;1.10&nbsp;lakh). The inspection report stated that no meter existed; the defence showed that a meter did in fact exist at the premises. The photographs placed on record showed only the exterior of the premises; there were no photographs of the interior or of the alleged illegal connection.</p>
<p>On a complaint under Section 135, the accused pleaded not guilty. The prosecution examined its officials; the contradictions between the inspection documents and the actual state of the premises emerged in cross-examination. Under Section 313 Cr.P.C. the accused denied the allegations and led no defence evidence.</p>""",
 headnote="""An inspection report that records a non-existent state of affairs &mdash; declaring &ldquo;no meter&rdquo; where a meter in fact existed &mdash; and is unsupported by any interior photograph of the alleged tap cannot be the foundation of a Section 135 conviction; the internal falsity of the prosecution&rsquo;s own documents raises a reasonable doubt fatal to the charge.""",
 grounds=[
  ("The inspection report was internally false.",
   """The report stated that no meter existed at the premises, whereas a meter in fact existed; a document that misstates the very state of the premises it purports to record cannot carry the presumption of regularity or prove the manner of abstraction."""),
  ("The photographs did not establish the tap.",
   """Only external photographs were taken; there was no photograph of the interior or of the alleged illegal connection, so the visual record neither showed the tap nor tied it to the accused."""),
  ("Material contradictions went to the root.",
   """On <span class="cn">Sadhu Singh v. State of Punjab</span>, contradictions in the prosecution&rsquo;s own evidence &mdash; here between the &ldquo;no meter&rdquo; recital and the meter&rsquo;s existence &mdash; entitle the accused to the benefit of the doubt."""),
 ],
 ratio_summary="the inspection report falsely reciting that no meter existed, and only exterior photographs having been taken",
 significance=[
  ("A false recital in the inspection report is corrosive.",
   """Recording &ldquo;no meter&rdquo; where a meter exists destroys the report&rsquo;s reliability and the presumption of regularity."""),
  ("Exterior-only photographs prove nothing.",
   """A visual record that never shows the interior or the alleged tap cannot establish the abstraction."""),
  ("Contradictions attract the benefit of the doubt.",
   """Self-contradiction in the prosecution&rsquo;s documents is enough to acquit (<span class="cn">Sadhu Singh</span>)."""),
  ("The presumption never engaged.",
   """With the foundational facts unproved, the reverse-onus presumption did not arise."""),
 ],
 sig_intro="An acquittal on the internal falsity of the prosecution&rsquo;s own inspection. Four propositions stand out:",
 cites=[SADHU], out="case_032.html")

# ================= 035 Shakuntala (SOLE flagship acquittal; broken chain; e-rickshaw) =================
acquit(title="State v. Shakuntala", docket="Ct. Case No.&nbsp;50/2024 &nbsp;|&nbsp; PS Maurya Enclave",
 court=ROHINI, judge="Sh. Prashant Kumar, Addl. Sessions Judge (Electricity)",
 doj="28 February 2026", dooff="10 August 2023",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Shakuntala D/o Sh. Amit Kumar Yadav, R/o Jhuggi No.&nbsp;C-123, E-Rickshaw Charging Station, Block QD, Pitampura, Delhi&#8209;110034",
 sections_label="Section 135 of the Electricity Act, 2003",
 one_line="The prosecution failed to establish a complete chain connecting the accused to the e-rickshaw charging operation.",
 charge="<p>Whether the accused Shakuntala dishonestly abstracted electricity to run an e-rickshaw charging station through an illegal tap from the licensee&rsquo;s tyco box, so as to attract Section 135(1) of the Electricity Act, 2003; and whether the prosecution proved, by a complete chain of evidence, that the accused operated or controlled that abstraction.</p>",
 facts="""<p>On 10 August 2023 at about 6.00 a.m., a TPDDL team inspected Jhuggi No.&nbsp;C-123 at an e-rickshaw charging station in Pitampura and alleged a direct theft: an illegal connection from the TPDDL tyco box at pole No.&nbsp;508-49/25/1/3, using a two-core black aluminium wire for phase/neutral and a three-phase four-wire cable, carrying a load of 14.478&nbsp;KW for non-domestic (e-rickshaw charging) use. An inspection report, seizure memo, 46 photographs and a CD with a Section 65B certificate were prepared. Three prosecution witnesses were examined &mdash; the raiding-team leader, the authorised representative and the photographer.</p>
<p>The defence and the Court identified a series of gaps: the complaint alleged the wire ran through the jhuggi to the charging station, but the inspection was of an open public area, not the jhuggi; no photograph showed the wire connected to the jhuggi; no public witness was examined; no e-rickshaw owner was identified or examined; there was no documentary proof of the e-rickshaws&rsquo; ownership; and there was no proof that the accused collected charges or otherwise controlled the operation. The Judge observed that the testimony of none of the witnesses inspired confidence.</p>""",
 headnote="""The sole acquittal in the set. In a public-place theft resting on circumstantial evidence, the prosecution must build a chain so complete as to exclude every hypothesis but guilt. Inconsistent wire-routing, no photograph tying the wire to the accused&rsquo;s jhuggi, no e-rickshaw owner or public witness, and no proof that the accused collected charges left the chain broken; suspicion could not substitute for proof, and the accused was acquitted.""",
 grounds=[
  ("The wire-routing was inconsistent and unphotographed.",
   """The complaint alleged the illegal wire ran through the accused&rsquo;s jhuggi to the charging station, yet the inspection was of an open public area, not the jhuggi, and not one of the 46 photographs showed the wire connected to the jhuggi &mdash; the very link between the accused&rsquo;s premises and the tap was missing."""),
  ("No independent or beneficiary witness supported the operation.",
   """No public witness was examined though the site was public; no e-rickshaw owner was identified or examined; and there was no documentary proof of the e-rickshaws&rsquo; ownership &mdash; on <span class="cn">Anoop Joshi</span>, the absence of available public witnesses raised, not lowered, the standard the prosecution had to meet."""),
  ("Control and collection of charges were never proved.",
   """There was no evidence that the accused operated the charging point or collected charges; mere presence at a public place is not proof of running the operation. On <span class="cn">Hanumant Govind Nargundkar</span> and <span class="cn">Sujit Biswas</span>, the circumstances did not form a complete chain, and suspicion could not take the place of proof; on <span class="cn">Kali Ram</span>, the view favouring the accused had to be adopted."""),
 ],
 ratio_summary="inconsistent and unphotographed wire-routing, no independent or e-rickshaw-owner witness, and no proof that the accused controlled the operation or collected charges",
 significance=[
  ("Public-place theft demands a complete circumstantial chain.",
   """Where the tap is in a public area, the prosecution must connect it to the accused link by link (<span class="cn">Hanumant Govind Nargundkar</span>); a missing link acquits."""),
  ("Suspicion is not proof.",
   """The gap between &lsquo;may be true&rsquo; and &lsquo;must be true&rsquo; must be bridged by evidence (<span class="cn">Sujit Biswas</span>); mere presence will not do."""),
  ("Unexamined beneficiaries and public witnesses tell against the prosecution.",
   """No e-rickshaw owner, no public witness and no proof of collection of charges left the operation unattributed (<span class="cn">Anoop Joshi</span>; <span class="cn">Ramesh Harijan</span>)."""),
  ("Two possible views go to the accused.",
   """Where the evidence permits an innocent explanation, the benefit of the doubt is the accused&rsquo;s (<span class="cn">Kali Ram</span>; <span class="cn">Mahender Singh Dahiya</span>)."""),
 ],
 sig_intro="The only acquittal in the set and the leading statement of the standard of proof &mdash; six authorities on circumstantial evidence and benefit of doubt. Four propositions stand out:",
 cites=[KALIRAM, HANUMANT, SUJIT, DAHIYA, RAMESH, ANOOP], out="case_035.html")

# ================= 042 Sharad Rana / Savitri Devi (meter tampering; lab officers not examined; burnt != tampered) =================
acquit(title="State v. Sharad Rana &amp; Anr.", docket="Ct. Case No.&nbsp;938/2020 &nbsp;|&nbsp; CNR DLSW01-007380-2020",
 court=DWARKA, judge="Ms. Harleen Singh, Addl. Sessions Judge (Electricity)",
 doj="date of judgment", dooff="25 February 2020",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> (1) Sharad Rana (alleged user) and (2) Savitri Devi (registered consumer)",
 sections_label="Sections 135, 138, 150, 151 and 154 of the Electricity Act, 2003",
 one_line="The laboratory officers who tested the meter were never examined, the lab report was not proved, and a burnt meter was equated with a tampered one without basis.",
 charge="<p>Whether the accused tampered with the meter so as to abstract electricity, attracting Sections 135, 138, 150, 151 and 154 of the Electricity Act, 2003; and whether the prosecution proved the alleged tampering through legally admissible, internally consistent evidence.</p>",
 facts="""<p>BSES Rajdhani alleged that the meter was &ldquo;abnormally burnt&rdquo; and tampered, and relied on a laboratory test. The lab officers who conducted the test (named Kailash Sahu and Pankaj Kumar Sinha) were not examined; the lab report was not proved through them; and the &ldquo;speaking order&rdquo; did no more than reproduce the lab report without independent reasoning. The complaint lacked material particulars, the test date shifted from 25.02.2020 to 04.03.2020 without notice to the accused, the connected load differed between the complaint (11.753&nbsp;KW) and the load report (9.003&nbsp;KW), and the Board Resolution authorising the CEO to delegate the complaint was not placed on record.</p>
<p>On a complaint under Sections 135/138/150/151/154, both accused pleaded not guilty. In cross-examination the contradictions emerged and the material lab witnesses were found to have been withheld. Under Section 313 Cr.P.C. the accused denied the allegations.</p>""",
 headnote="""Meter-tampering theft proved only by a laboratory report collapses where the testing officers are not examined and the report is not proved; a &ldquo;burnt&rdquo; meter is not necessarily a &ldquo;tampered&rdquo; meter, and a speaking order that merely reproduces the lab report, unsupported by the licensee&rsquo;s proof of its officer&rsquo;s authority to complain, cannot sustain a conviction.""",
 grounds=[
  ("The testing officers were withheld and the lab report unproved.",
   """The laboratory officers who tested the meter were not examined and the lab report was never proved through them; the central plank of a meter-tampering case &mdash; the scientific finding of tampering &mdash; was therefore not in evidence at all."""),
  ("A burnt meter is not a tampered meter.",
   """The Court held that an &ldquo;abnormally burnt&rdquo; meter is not necessarily a tampered one, and the speaking order offered no independent reasoning &mdash; merely reproducing the lab report &mdash; so no reasoned finding of tampering existed (cf. <span class="cn">Narinder Aggarwal v. BSES Rajdhani</span>)."""),
  ("Authorisation, particulars and load all failed.",
   """The Board Resolution authorising the CEO/complainant was not on record; the complaint lacked material particulars; the test date was changed without notice; and the connected load differed between the complaint and the load report &mdash; a cumulation of defects fatal to the charge."""),
 ],
 ratio_summary="the testing officers unexamined, the lab report unproved, a burnt meter equated with a tampered one without basis, and the CEO&rsquo;s authority to complain unproved",
 significance=[
  ("A meter-tampering case stands or falls on the lab witnesses.",
   """If the testing officers are not examined and the report is not proved, there is no admissible finding of tampering."""),
  ("&lsquo;Burnt&rsquo; is not &lsquo;tampered&rsquo;.",
   """The licensee must prove tampering; a burnt meter may have many innocent causes (<span class="cn">Narinder Aggarwal</span>)."""),
  ("A speaking order must reason, not recite.",
   """Reproducing the lab report without independent reasoning is no speaking order at all."""),
  ("Unproved authority to complain is by itself a serious gap.",
   """Absent the Board Resolution proving the CEO&rsquo;s authority to delegate, the very competence of the complaint is in doubt."""),
 ],
 sig_intro="A meter-tampering acquittal on withheld lab witnesses and an unreasoned speaking order. Four propositions stand out:",
 cites=[NARINDER], out="case_042.html")

# ================= 043 Narpal / Satvir Singh (RC dropped; meter in dropped-accused's name; S65B defects) =================
acquit(title="State v. Narpal", docket="Ct. Case No.&nbsp;767/2023 &nbsp;|&nbsp; CNR DLSW01-008472-2023",
 court=DWARKA, judge="Ms. Harleen Singh, Addl. Sessions Judge (Electricity)",
 doj="date of judgment", dooff="date of inspection",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> Narpal (alleged user) &mdash; the registered consumer (Satvir Singh) having been dropped mid-trial",
 sections_label="Sections 135, 151 and 154 of the Electricity Act, 2003",
 one_line="The registered consumer was dropped without explanation, the meter and bills pertained to him, and the accused&rsquo;s own consumer status was never established.",
 charge="<p>Whether the accused Narpal dishonestly abstracted electricity at the inspected premises, so as to attract Sections 135/151/154 of the Electricity Act, 2003; and whether the prosecution established that he &mdash; rather than the dropped registered consumer &mdash; was the consumer/user under Section 2(15).</p>",
 facts="""<p>BSES Rajdhani alleged theft (assessed at about Rs.&nbsp;7.53&nbsp;lakh). The registered consumer (accused no.&nbsp;2, Satvir Singh) was dropped from the case mid-trial with no explanation; yet the meter (No.&nbsp;40432523) stood in his name, and the consumption pattern and the bills both pertained to him, not to accused no.&nbsp;1. The material technician-witness (Suneel Kumar) was not examined; the videography was prepared in intervals rather than continuously and was not fully filed; and the Section 65B certificate was defective (a pre-printed form with no studio stamp, no computer or memory-card particulars). The alleged illegal cables were not seized despite police presence, and the Board Resolution authorising the CEO was not filed.</p>
<p>On a complaint under Sections 135/151/154, the accused pleaded not guilty. The contradictions and the withholding of the technician emerged in cross-examination. Under Section 313 Cr.P.C. the accused denied the allegations.</p>""",
 headnote="""Where the registered consumer &mdash; in whose name the meter, the consumption and the bills all stood &mdash; is dropped mid-trial without explanation, and the remaining accused&rsquo;s status as consumer under Section 2(15) is never established, the theft charge cannot stand; defective Section 65B certification, a withheld technician and unseized cables compound the failure of proof.""",
 grounds=[
  ("The consumer was dropped, yet the meter and bills were his.",
   """The registered consumer was dropped mid-trial without explanation, although the meter stood in his name and both the consumption pattern and the bills pertained to him; the prosecution never established that the remaining accused was the consumer/user under Section 2(15)."""),
  ("The electronic record was defectively certified.",
   """The videography was prepared in intervals, not continuously, and was not fully filed, and the Section 65B certificate was a pre-printed form bearing no studio stamp and no computer or memory-card particulars &mdash; the certificate did not satisfy the statutory conditions for admissibility."""),
  ("The material technician was withheld and no cable seized.",
   """The technician who alone could speak to the wiring was not examined, and no allegedly illegal cable was seized despite police presence; the primary and corroborative proof of the tap were both absent."""),
 ],
 ratio_summary="the registered consumer dropped though the meter and bills were his, the remaining accused&rsquo;s consumer status unproved, a defective Section 65B certificate and a withheld technician",
 significance=[
  ("Dropping the real consumer can sink the case.",
   """Where the meter, consumption and bills belong to the dropped accused, the person left in the dock may not be the &ldquo;consumer&rdquo; at all (Section 2(15))."""),
  ("A defective Section 65B certificate excludes the video.",
   """Interval videography and a pre-printed certificate without device particulars fail the admissibility conditions."""),
  ("Withholding the technician is fatal in a wiring case.",
   """The one witness who could prove the tap must be examined."""),
  ("Unseized cables leave the tap unproved.",
   """Police presence with no seizure undercuts the very existence of the illegal connection."""),
 ],
 sig_intro="An acquittal where the true consumer was dropped and the case against the wrong person collapsed. Four propositions stand out:",
 cites=[], out="case_043.html")

# ================= 044 Amit Gahlot (date discrepancy; CD malfunction; S65B mismatch; meter reinstated) =================
acquit(title="State v. Amit Gahlot", docket="Ct. Case No.&nbsp;300/2022 &nbsp;|&nbsp; CNR DLSW01-004506-2022",
 court=DWARKA, judge="Ms. Harleen Singh, Addl. Sessions Judge (Electricity)",
 doj="date of judgment", dooff="15 February 2022",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> Amit Gahlot (user / registered consumer)",
 sections_label="Section 135 read with Section 150 of the Electricity Act, 2003",
 one_line="A major date discrepancy, a malfunctioning original CD replaced by an uncertified substitute, and a valid commercial connection since 2019 undid the charge.",
 charge="<p>Whether the accused Amit Gahlot dishonestly abstracted electricity at the inspected premises, so as to attract Section 135 read with Section 150 of the Electricity Act, 2003; and whether the prosecution&rsquo;s evidence, marred by date and electronic-record defects, proved the abstraction.</p>",
 facts="""<p>BSES Rajdhani alleged theft (assessed at about Rs.&nbsp;13.52&nbsp;lakh). The complaint stated the date of inspection as 15.02.2021, while all the documents and witnesses put it at 15.02.2022 &mdash; a discrepancy of a full year. The original videography CD could not be played (30.09.2024); a substitute CD supplied later (04.12.2024) was admittedly not prepared by the original maker, and the Section 65B certificate from the old CD did not pertain to the new one, which was covered by no valid certificate. The material team head (Gulfan Ansari) was not examined; defence witnesses (neighbours) said the raid was at an adjacent/different premises; and there was no proof of service of the reports.</p>
<p>On a complaint under Section 135 r/w 150, the accused pleaded not guilty. The Court noted that the accused held a valid commercial connection since 2019 and directed BSES to reinstall the meter. Under Section 313 Cr.P.C. the accused denied the allegations.</p>""",
 headnote="""A year-long discrepancy in the date of inspection, an unplayable original CD replaced by a substitute covered by no valid Section 65B certificate, an unexamined team head and defence evidence that the raid was at a different premises leave the abstraction unproved &mdash; the more so where the accused held a valid commercial connection, prompting an order to reinstall the meter.""",
 grounds=[
  ("The date of inspection was internally inconsistent by a year.",
   """The complaint put the inspection at 15.02.2021 while every document and witness put it at 15.02.2022; a discrepancy of a full year in the foundational fact of when the raid occurred is not a clerical slip the Court could overlook."""),
  ("The electronic record was broken and uncertified.",
   """The original CD could not be played; the substitute CD was not prepared by the original maker and was covered by no valid Section 65B certificate (the old certificate not pertaining to it) &mdash; the videography, the heart of the proof, was inadmissible."""),
  ("Identity of the premises was contradicted.",
   """The team head was not examined, defence neighbours deposed that the raid was at an adjacent/different premises, and there was no proof of service of the reports; against this, the accused&rsquo;s valid commercial connection since 2019 led the Court to order the meter reinstalled."""),
 ],
 ratio_summary="a year-long discrepancy in the inspection date, an unplayable original CD replaced by an uncertified substitute, an unexamined team head and defence proof that the raid was elsewhere",
 significance=[
  ("A year&rsquo;s discrepancy in the raid date is fatal.",
   """When the prosecution cannot agree with itself on when the inspection happened, the foundational fact is unproved."""),
  ("A substitute CD needs its own Section 65B certificate.",
   """A certificate tied to an unplayable original does not cover a later substitute prepared by someone else."""),
  ("An unexamined team head plus contrary neighbour evidence unsettles identity.",
   """Where the defence shows the raid may have been elsewhere, the premises themselves are in doubt."""),
  ("A valid subsisting connection tells against theft.",
   """A commercial connection held since 2019 &mdash; and an order to reinstate the meter &mdash; is hard to square with the alleged theft."""),
 ],
 sig_intro="An acquittal (with a meter-reinstatement order) on a year-long date error and a broken electronic record. Four propositions stand out:",
 cites=[], out="case_044.html")

# ================= 045 Arvind / Sumitra Devi (presence/resistance/load contradictions; technician withheld) =================
acquit(title="State v. Arvind &amp; Anr.", docket="Ct. Case No.&nbsp;1001/2021 &nbsp;|&nbsp; CNR DLSW01-007808-2021",
 court=DWARKA, judge="Ms. Harleen Singh, Addl. Sessions Judge (Electricity)",
 doj="date of judgment", dooff="date of inspection",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> (1) Arvind S/o Raj Kumar (user) and (2) Sumitra Devi (registered consumer)",
 sections_label="Section 135 read with Section 150 of the Electricity Act, 2003",
 one_line="The complaint and the witnesses contradicted each other on presence, resistance, police involvement and even the nature of the load, and the material technician was withheld.",
 charge="<p>Whether the accused dishonestly abstracted electricity at the inspected premises, so as to attract Section 135 read with Section 150 of the Electricity Act, 2003; and whether the prosecution&rsquo;s mutually contradictory evidence proved the abstraction and the accused&rsquo;s part in it.</p>",
 facts="""<p>BSES Rajdhani alleged a direct tap (assessed at about Rs.&nbsp;2.28&nbsp;lakh). The prosecution&rsquo;s own account was riddled with contradictions: the complaint said both accused were present, but PW-1 and PW-3 said accused no.&nbsp;2 was absent; the complaint alleged resistance, but PW-3 denied any resistance and PW-1 said no one stopped the seizure; the complaint said police were present, but PW-3 said no law-enforcement was involved and there was no security risk; PW-1 said the premises were locked, but PW-3 said they were entered and videographed; and the load was described as domestic in the complaint but as non-domestic (a kabadi godown) by PW-1. The material technician (Deepak) was not examined, the wire was not tested to confirm it was live, and the connection point was not shown in the videography.</p>
<p>On a complaint under Section 135 r/w 150, the accused pleaded not guilty; the contradictions surfaced across the prosecution witnesses. Under Section 313 Cr.P.C. the accused denied the allegations.</p>""",
 headnote="""Where the complaint and the prosecution witnesses contradict one another on presence, resistance, police involvement, access and even the nature of the load, and the technician who alone could prove that the wire was live is withheld, the prosecution&rsquo;s case does not rise to proof beyond reasonable doubt and the accused must be acquitted.""",
 grounds=[
  ("Presence and resistance were told inconsistently.",
   """The complaint had both accused present and resistance offered; PW-1 and PW-3 placed accused no.&nbsp;2 elsewhere and denied any resistance &mdash; the prosecution could not keep its own story straight on who was there and what happened."""),
  ("Police presence, access and the load were all contradicted.",
   """The complaint asserted police presence and a locked premises with a domestic load; the witnesses variously denied police involvement, said the premises were entered and videographed, and described the load as a non-domestic kabadi godown &mdash; contradictions going to the core of the raid."""),
  ("The live wire was never proved and the technician withheld.",
   """The technician (Deepak) was not examined, the wire was not tested to confirm it carried current, and the videography did not show the connection point &mdash; so even the fact of a live illegal tap was unproved."""),
 ],
 ratio_summary="mutually contradictory prosecution evidence on presence, resistance, police involvement, access and the load, coupled with a withheld technician and an untested wire",
 significance=[
  ("Self-contradiction across witnesses defeats proof.",
   """When PW-1 and PW-3 contradict the complaint and each other on the basic facts of the raid, no reliable version survives."""),
  ("The nature of the load cannot be left uncertain.",
   """Domestic vs non-domestic goes to the assessment and the offence; an unresolved contradiction is telling."""),
  ("A live tap must be proved, not assumed.",
   """An untested wire and an unshown connection point leave the abstraction itself in doubt."""),
  ("Withholding the technician deprives the accused of a fair test.",
   """The one witness able to prove the wiring must be produced and cross-examined."""),
 ],
 sig_intro="An acquittal on a cascade of internal contradictions in the prosecution&rsquo;s own case. Four propositions stand out:",
 cites=[], out="case_045.html")

# ================= 046 Geeta / Om Parkash (premises misdescription - no first floor; absurd narrative; RC died) =================
acquit(title="State v. Geeta", docket="Ct. Case No.&nbsp;257/2023 &nbsp;|&nbsp; CNR DLSW01-002468-2023",
 court=DWARKA, judge="Ms. Harleen Singh, Addl. Sessions Judge (Electricity)",
 doj="date of judgment", dooff="date of inspection",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> Geeta W/o Jeet Singh (user) &mdash; the registered consumer (Om Parkash) having died during proceedings",
 sections_label="Section 135 read with Section 150 of the Electricity Act, 2003",
 one_line="The inspection described a first floor that does not exist, the seizure account was found &lsquo;absurd&rsquo;, and the accused could not even be identified.",
 charge="<p>Whether the accused Geeta dishonestly abstracted electricity at the inspected premises (described as &ldquo;FF&rdquo;/first floor), so as to attract Section 135 read with Section 150 of the Electricity Act, 2003; and whether the prosecution proved that abstraction where the very description of the premises was false.</p>",
 facts="""<p>BSES Rajdhani alleged an illegal tap (assessed at about Rs.&nbsp;92,989) at premises described in the complaint and documents as the first floor (&ldquo;FF&rdquo;). The accused proved that the premises were built only to the ground floor &mdash; there was no first floor &mdash; and that she had resided at the ground floor for some twenty years, a fact left unrefuted. PW-1&rsquo;s account that the accused snatched and hid the illegal wire while the door was closed was found by the Court to be &ldquo;absurd, to say the least.&rdquo; The cable was described inconsistently (&ldquo;AB cable&rdquo; by PW-1, &ldquo;service cable&rdquo; by PW-3); PW-3 could not identify the accused; the material technician (Sunil Kumar) was not examined; no photograph of the alleged cut in the cable was placed on record; and no material was seized despite police presence.</p>
<p>On a complaint under Section 135 r/w 150, the accused pleaded not guilty; the proceedings against the registered consumer (Om Parkash) abated on his death. Under Section 313 Cr.P.C. the accused denied the allegations.</p>""",
 headnote="""An inspection that locates the theft on a first floor which does not exist, an account of the seizure the Court itself called &ldquo;absurd,&rdquo; inconsistent descriptions of the cable, a witness who could not identify the accused, and no seized material or photograph leave nothing on which a Section 135 conviction could rest; the accused is acquitted and the case against the deceased consumer abates.""",
 grounds=[
  ("The premises were misdescribed &mdash; no first floor exists.",
   """The complaint and documents placed the theft on the first floor, but the accused proved the building rose only to the ground floor, where she had lived unrefuted for some twenty years; the abstraction was located at a place that does not exist."""),
  ("The seizure narrative was &lsquo;absurd&rsquo; and identity failed.",
   """The Court found PW-1&rsquo;s account &mdash; that the accused snatched and hid the wire while the door was closed &mdash; &ldquo;absurd, to say the least&rdquo;; PW-3 could not identify the accused and described the cable differently from PW-1, so neither the act nor its author was reliably proved."""),
  ("No material, no photograph, no technician.",
   """Despite police presence nothing was seized, no photograph of the alleged cut cable was filed, and the technician who could speak to the wiring was not examined &mdash; the physical proof of the tap was wholly absent."""),
 ],
 ratio_summary="a theft located on a non-existent first floor, a seizure account the Court called absurd, a failure to identify the accused, and no seized material, photograph or technician",
 significance=[
  ("A false description of the premises is corrosive to the whole case.",
   """If the theft is placed where no such floor exists, the inspection cannot be trusted on anything else."""),
  ("An &lsquo;absurd&rsquo; seizure account cannot prove the act.",
   """Testimony the Court itself disbelieves as absurd carries no weight."""),
  ("Failure to identify the accused is decisive.",
   """A witness who cannot identify the accused cannot fix the abstraction on her."""),
  ("No seizure and no photograph leave the tap unproved.",
   """Physical proof, readily available with police present, was simply not gathered."""),
 ],
 sig_intro="An acquittal where the theft was placed on a floor that does not exist. Four propositions stand out:",
 cites=[], out="case_046.html")

# ================= 047 Munni Devi / Kapoor Singh (authorisation + procedure defects) =================
acquit(title="State v. Munni Devi", docket="Ct. Case No.&nbsp;386/2020 &nbsp;|&nbsp; CNR DLSW01-003090-2020",
 court=DWARKA, judge="Ms. Harleen Singh, Addl. Sessions Judge (Electricity)",
 doj="date of judgment", dooff="date of inspection",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> (1) Munni Devi (user/owner) and (2) Kapoor Singh (registered consumer)",
 sections_label="Sections 135, 150, 151 and 154 of the Electricity Act, 2003",
 one_line="No Board Resolution proved the CEO&rsquo;s authority to delegate the complaint, only one of four team members was examined, and computer-generated documents came without a Section 65B certificate.",
 charge="<p>Whether the accused abstracted electricity at the inspected premises, so as to attract Sections 135/150/151/154 of the Electricity Act, 2003; and whether the complaint was competently authorised and the prosecution&rsquo;s evidence legally proved.</p>",
 facts="""<p>BSES Rajdhani alleged a direct theft (assessed at about Rs.&nbsp;2.45&nbsp;lakh). The prosecution did not place on record any Board Resolution proving that the CEO was authorised to delegate the power to complain; only one of the four members of the inspecting team was examined; the computer-generated documents were filed without a Section 65B certificate; the videographer was not examined; and the witnesses gave inconsistent accounts of the seizure of the wire.</p>
<p>On a complaint under Sections 135/150/151/154, the accused pleaded not guilty. The defects in authorisation and proof emerged in cross-examination. Under Section 313 Cr.P.C. the accused denied the allegations.</p>""",
 headnote="""A theft complaint by a licensee fails where the authority of the complaining officer is not proved (no Board Resolution empowering the CEO to delegate), the inspecting team is all but unexamined, the computer-generated records lack a Section 65B certificate and the videographer is not produced; the accumulation of authorisation and proof defects denies the charge a foundation.""",
 grounds=[
  ("The competence of the complaint was not proved.",
   """No Board Resolution was placed on record to show that the CEO was authorised to delegate the power to lodge the complaint; the very authority behind the prosecution was therefore unestablished."""),
  ("The inspection was barely proved.",
   """Only one of the four members of the inspecting team was examined, and the videographer &mdash; who alone could prove the recording &mdash; was not produced, so the inspection rested on a fraction of those who conducted it."""),
  ("The electronic and computer records were uncertified.",
   """The computer-generated documents were filed without the Section 65B certificate the law requires, and the accounts of the seizure of the wire were inconsistent &mdash; the documentary and physical proof were both legally infirm."""),
 ],
 ratio_summary="no Board Resolution proving the CEO&rsquo;s authority to complain, only one of four team members examined, computer records without a Section 65B certificate and an unexamined videographer",
 significance=[
  ("Authority to complain is a foundational fact.",
   """Without proof that the complaining officer was empowered, the prosecution&rsquo;s competence is in doubt from the outset."""),
  ("Examining one of four is not enough.",
   """A largely unexamined team and a missing videographer leave the inspection unproved."""),
  ("Computer-generated records need Section 65B certification.",
   """Uncertified electronic/computer documents are inadmissible."""),
  ("Procedural defects can be cumulative and decisive.",
   """Individually curable lapses, taken together, deny the charge a foundation."""),
 ],
 sig_intro="An acquittal on authorisation and proof defects &mdash; the licensee&rsquo;s own competence unproved. Four propositions stand out:",
 cites=[], out="case_047.html")

# ================= 048 Anmol / Narender Singh (identity - wrong grandfather; lab tampering confirmed but identity failed) =================
acquit(title="State v. Anmol", docket="Ct. Case No.&nbsp;189/2020 &nbsp;|&nbsp; CNR DLST01-002109-2020",
 court=SAKET, judge="Sh. Vivek Kumar Gulia, Addl. Sessions Judge",
 doj="date of judgment", dooff="date of inspection",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> Anmol (alleged user/owner) &mdash; the registered consumer (Narender Singh) having died",
 sections_label="Section 135 read with Sections 150 and 313 of the Electricity Act, 2003",
 one_line="Meter tampering was confirmed by the laboratory, but the accused was not shown to be the user/owner &mdash; the grandfather named did not match, and suspicion cannot replace proof.",
 charge="<p>Whether the accused Anmol was the user/owner who tampered with the meter and abstracted electricity, so as to attract Section 135 (with Sections 150/313) of the Electricity Act, 2003; and whether, tampering being established, the prosecution proved the accused&rsquo;s identity as the person answerable.</p>",
 facts="""<p>BSES Rajdhani alleged meter tampering and direct theft (assessed at about Rs.&nbsp;11.97&nbsp;lakh), and the laboratory test confirmed tampering. The difficulty was identity. The user present, Mukesh Kumar, disclosed a grandson&rsquo;s name, but the accused&rsquo;s grandfather was a different person (Late Gurcharan Singh Bindra, not Narender Singh); no ownership documents were shown during the inspection tying the accused to the premises; and nothing else established that the accused was the user/owner answerable for the tampering.</p>
<p>On a complaint under Section 135 (with Sections 150/313), the accused pleaded not guilty; the registered consumer, Narender Singh, had died. Under Section 313 Cr.P.C. the accused denied the allegations. The Court held that strong suspicion of tampering could not, without proof of the accused&rsquo;s identity as the user/owner, sustain a conviction.</p>""",
 headnote="""Even where the laboratory confirms meter tampering, the conviction fails if the prosecution does not prove that the accused was the user/owner of the premises; a mismatch in the family particulars (the grandfather named being a different person) and the absence of any ownership document at the inspection leave identity unproved &mdash; and suspicion, however strong, cannot replace proof.""",
 grounds=[
  ("Tampering was proved, but not by whom.",
   """The laboratory confirmed that the meter had been tampered with; what the prosecution did not prove was that the accused was the user/owner answerable for it &mdash; the offence needs both the act and its author, and only the act was established."""),
  ("The identity particulars did not match.",
   """The user present disclosed a grandson&rsquo;s name, but the accused&rsquo;s grandfather was Late Gurcharan Singh Bindra, not the registered consumer Narender Singh; the family particulars relied on to connect the accused to the premises did not fit."""),
  ("No ownership document and mere suspicion.",
   """No ownership document was shown at the inspection tying the accused to the premises; the Court held that suspicion of tampering, however grave, cannot without proof of identity sustain a conviction."""),
 ],
 ratio_summary="confirmed tampering but no proof that the accused was the user/owner, a mismatch in the family particulars and no ownership document",
 significance=[
  ("Proof of tampering is not proof of the tamperer.",
   """A confirmed lab finding fixes the act, not the person; identity must be independently proved."""),
  ("Mismatched family particulars defeat identity.",
   """Where the grandfather named does not match the accused, the link to the premises is broken."""),
  ("Suspicion cannot replace proof.",
   """However strong the suspicion of tampering, a conviction needs legal proof of the accused&rsquo;s identity as user/owner."""),
  ("A deceased registered consumer sharpens the identity gap.",
   """With the registered consumer dead, the prosecution had to prove the accused&rsquo;s own status &mdash; and could not."""),
 ],
 sig_intro="Confirmed meter tampering &mdash; yet an acquittal, because the tamperer was never identified. Four propositions stand out:",
 cites=[], out="case_048.html")

# ================= 049 Arjun / Taraq (identity - masked person said 'Barun' not 'Arjun') =================
acquit(title="State v. Arjun", docket="Ct. Case No.&nbsp;489/2021 &nbsp;|&nbsp; CNR DLST01-007309-2021",
 court=SAKET, judge="Sh. Vivek Kumar Gulia, Addl. Sessions Judge",
 doj="date of judgment", dooff="date of inspection",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> Arjun (alleged contractor) &mdash; the co-accused Taraq having been declared a proclaimed person",
 sections_label="Section 135 read with Section 154 of the Electricity Act, 2003",
 one_line="A duly certified video existed, but the masked person in it gave his name as &lsquo;Barun&rsquo;; the claim that he was &lsquo;Arjun&rsquo; rested on resemblance alone.",
 charge="<p>Whether the accused Arjun was the person who abstracted electricity through the tap shown in the inspection, so as to attract Section 135 (with Section 154) of the Electricity Act, 2003; and whether the prosecution proved that the masked person in the video was in fact the accused.</p>",
 facts="""<p>BSES Rajdhani alleged a direct theft (assessed at about Rs.&nbsp;18.19&nbsp;lakh) and, unusually, had a properly certified Section 65B video of the inspection. The difficulty, again, was identity: the person at the inspection wore a mask and disclosed his name as &ldquo;Barun,&rdquo; yet the prosecution claimed he was &ldquo;Arjun&rdquo; on the strength of resemblance. The mask was never removed, no identity document was demanded on video, and the information linking the accused came from a co-accused (Taraq) who had been declared a proclaimed person; the inspection documents recorded the name Arjun, but the video did not confirm that the masked man was the accused.</p>
<p>On a complaint under Section 135 (with Section 154), the accused pleaded not guilty. Under Section 313 Cr.P.C. the accused denied the allegations. The Court held that a certified video does not prove identity where the person in it is masked and names himself differently.</p>""",
 headnote="""A properly certified video of the theft does not convict where it cannot fix the identity of the offender: the person recorded was masked, disclosed a different name (&ldquo;Barun,&rdquo; not the accused &ldquo;Arjun&rdquo;), was never asked to remove the mask or produce identification, and was linked to the accused only by resemblance and by a proclaimed co-accused. Identity, not the tap, was the missing foundational fact.""",
 grounds=[
  ("The person in the video was masked and self-named differently.",
   """The inspection was videographed with a valid Section 65B certificate, but the person recorded wore a mask and gave his name as &ldquo;Barun&rdquo;; the prosecution&rsquo;s case that he was the accused &ldquo;Arjun&rdquo; rested on resemblance, not proof."""),
  ("No step was taken to establish identity.",
   """The mask was never removed and no identity document was demanded on video; the ordinary means of fixing who was present were simply not used, so the certified recording proved the tap but not the tamperer."""),
  ("The link to the accused came from a proclaimed co-accused.",
   """The information connecting the accused derived from a co-accused (Taraq) who had been declared a proclaimed person; such a source could not supply the certain identification the video lacked."""),
 ],
 ratio_summary="a masked person who named himself &lsquo;Barun&rsquo;, identified as the accused only by resemblance and by a proclaimed co-accused, with no mask removal or identity check on video",
 significance=[
  ("A certified video proves the act, not necessarily the actor.",
   """Where the person recorded is masked and self-names differently, Section 65B admissibility does not translate into proof of identity."""),
  ("Resemblance is not identification.",
   """Claiming the masked man &ldquo;looks like&rdquo; the accused cannot bridge a self-declared different name."""),
  ("Elementary identity steps must be taken.",
   """Failing to remove the mask or demand identification on video leaves identity unproved."""),
  ("A proclaimed co-accused is a weak source of identity.",
   """Identification resting on an absconding co-accused cannot supply certainty."""),
 ],
 sig_intro="A certified video, a very large assessment &mdash; yet an acquittal, because a masked man named himself &lsquo;Barun&rsquo;. Four propositions stand out:",
 cites=[], out="case_049.html")

print("Acquittals 026,027,032,035,042,043,044,045,046,047,048,049 generated.")
