#!/usr/bin/env python3
"""Structurally distinct cases: 029 (Section 126 vs 135 civil appeal), 039 (civil suit),
   040 (meter-tampering conviction, clause (b)/(c)), 041 (Section 138 interference + 135/150)."""
from gen_08_11 import build, STD_CITES

ROHINI = "Court of the Additional Sessions Judge (Electricity), North&#8209;West District, Rohini Courts, Delhi"
J_PK = "Sh. Prashant Kumar, Addl. Sessions Judge (Electricity)"

# ===== 029 Vimla Kumari Pathak v. TPDDL (RCA; s.126 vs 135; s.145 civil bar; appeal dismissed) =====
SARJIWAN = ("Sarjiwan Singh v. DVB", "Delhi HC",
  "On the statutory scheme for assessment of unauthorised use under Section 126 and its distinct, non-criminal character.")
S126_GRP = [
 ("Yogesh Nayyar v. TPDDL", "Delhi (CS No.&nbsp;821/16)",
  "A civil suit challenging a Section 126 assessment is barred; the remedy lies in the statutory appeal."),
 ("Deepak Santiya v. BSES Yamuna Power Ltd.", "Delhi (CS No.&nbsp;2085/21)",
  "The civil court&rsquo;s jurisdiction is ousted by Section 145 in matters the assessing/appellate authority is empowered to decide."),
 ("Joginder Kumar Goyal v. BSES Rajdhani Power Ltd.", "Delhi HC, W.P.(C) 17658/2022",
  "Unauthorised-use disputes are to be pursued through the Section 127 appellate mechanism, not the civil court."),
 ("B L Kantroo v. BSES Rajdhani Power Ltd.", "Delhi HC, RFA(OS) No.&nbsp;12/2008",
  "Reaffirming the bar of Section 145 against civil suits touching a Section 126 assessment."),
]
c029 = dict(
 title="Vimla Kumari Pathak v. Tata Power Delhi Distribution Ltd.",
 subcite="RCA (DJ) No.&nbsp;77/26 (Civil Appeal) &nbsp;|&nbsp; Court of the District Judge&#8209;06, Central District, Tis Hazari Courts, Delhi",
 court="Court of the District Judge&#8209;06, Central District, Tis Hazari Courts, Delhi",
 judge="Ms. Shivali Sharma, District Judge&#8209;06",
 doj="16 April 2026", dooff="21 November 2025",
 parties="Vimla Kumari Pathak W/o Sh. Ram Murti Pathak, R/o H. No.&nbsp;353, Gali No.&nbsp;4, Near Main Market, Sant Nagar, Burari, Delhi&#8209;110084 (appellant/plaintiff) <em>v.</em> Tata Power Delhi Distribution Ltd. (respondent)",
 statutes="Sections 126, 127, 135 &amp; 145, Electricity Act, 2003; Order 7 Rule 11(d), Code of Civil Procedure, 1908",
 result="<strong>Civil appeal dismissed.</strong> The rejection of the plaint under Order 7 Rule 11(d) CPC &mdash; as barred by Section 145 of the Electricity Act &mdash; is affirmed. The appellant&rsquo;s remedy against the Section 126 assessment lies in the statutory appeal under Section 127, not in a civil suit.",
 charge="<p><strong>Point for determination:</strong> Whether a civil suit challenging an inspection report and an assessment order for <em>unauthorised use</em> of electricity under Section 126 of the Electricity Act, 2003 is maintainable, or is barred by Section 145 (ouster of civil-court jurisdiction), the appropriate remedy being the statutory appeal under Section 127; and whether the facts disclosed theft under Section 135 (criminal) or unauthorised use under Section 126 (civil).</p>",
 facts="""<p>The appellant owns a multi-storey residential property at Burari with several domestic connections and tenants. On 21 November 2025, TPDDL inspected the premises and found the domestic supply being used for an unauthorised non-domestic purpose &mdash; paying-guest (PG) accommodation. It issued a provisional assessment order (28 November 2025) and a final assessment order (20 January 2026) raising a demand of over Rs.&nbsp;1.40&nbsp;lakh, and the connections were later disconnected.</p>
<p>The appellant sued civilly to challenge the inspection report and the assessment. The trial court rejected the plaint under Order 7 Rule 11(d) CPC as barred by Section 145 of the Electricity Act, which ousts the jurisdiction of civil courts in matters an assessing officer or appellate authority is empowered to determine. The present first appeal challenges that rejection.</p>""",
 headnote="""Using a sanctioned domestic connection for a non-domestic purpose (here, PG accommodation) is <em>unauthorised use</em> under Section 126 &mdash; a civil, assessment-based liability &mdash; not theft under Section 135. The remedy against a Section 126 assessment is the statutory appeal under Section 127; Section 145 bars a civil suit, and the plaint was rightly rejected under Order 7 Rule 11(d) CPC. The appeal is dismissed.""",
 interp="""  <h3 class="grp">Electricity Act, 2003</h3>
  <h3>Section 126 <em>vs</em> Section 135 &mdash; Unauthorised Use is not Theft</h3>
  <p>The Court drew the cardinal distinction: Section 126 addresses the <em>unauthorised use</em> of electricity &mdash; putting a lawful supply to a purpose other than that for which it was sanctioned (here, a domestic connection used for PG accommodation) &mdash; and gives rise to a civil, assessment-based liability fixed by the assessing officer. Section 135 addresses <em>theft</em> &mdash; a dishonest abstraction &mdash; and is criminal. Diverting a lawful connection to an unauthorised purpose falls under Section 126, not Section 135.</p>
  <h3>Sections 127 &amp; 145 &mdash; Statutory Appeal and the Civil-Court Bar</h3>
  <p>The remedy against a Section 126 assessment is the statutory appeal under Section 127 before the appellate authority. Section 145 ousts the jurisdiction of civil courts in matters the assessing officer or appellate authority is empowered to decide, so a civil suit challenging a Section 126 assessment is barred and liable to rejection under Order 7 Rule 11(d) CPC.</p>""",
 reasoning=[
  ("The dispute was one of unauthorised use, not theft.",
   """The inspection found a sanctioned domestic connection being put to a non-domestic use (PG accommodation) &mdash; the paradigm of <em>unauthorised use</em> under Section 126, assessed civilly by the assessing officer, and not a dishonest abstraction punishable as theft under Section 135."""),
  ("Section 145 bars the civil court.",
   """Section 145 ousts the jurisdiction of civil courts in matters an assessing officer or appellate authority is empowered to determine; a Section 126 assessment is exactly such a matter, so a civil suit to challenge it does not lie."""),
  ("The statutory appeal under Section 127 is the exclusive remedy.",
   """The Act provides a complete code: an aggrieved consumer must appeal under Section 127 before the appellate authority. On <span class="cn">Yogesh Nayyar</span>, <span class="cn">Deepak Santiya</span>, <span class="cn">Joginder Kumar Goyal</span> and <span class="cn">B L Kantroo</span>, and the scheme explained in <span class="cn">Sarjiwan Singh</span>, the civil suit was not maintainable."""),
  ("The plaint was rightly rejected under Order 7 Rule 11(d).",
   """A plaint barred by law is to be rejected under Order 7 Rule 11(d) CPC; the trial court&rsquo;s rejection was correct, and the first appeal against it fails."""),
 ],
 mode_desc="",
 bill="1,40,000+",
 held="<p>The suit challenging the Section 126 assessment was barred by Section 145 of the Electricity Act, the appellant&rsquo;s remedy lying in the statutory appeal under Section 127. The trial court&rsquo;s rejection of the plaint under Order 7 Rule 11(d) CPC is affirmed. <strong>The appeal is dismissed.</strong></p>",
 sig_intro="The set&rsquo;s only appellate decision and its clearest statement of the Section 126/135 boundary. Four propositions stand out:",
 significance=[
  ("Unauthorised use is not theft.",
   """Diverting a sanctioned domestic connection to a non-domestic use (PG accommodation) is Section 126 unauthorised use &mdash; civil and assessment-based &mdash; not Section 135 theft."""),
  ("Section 145 ousts the civil court.",
   """Civil courts have no jurisdiction over matters the assessing/appellate authority is empowered to decide."""),
  ("Section 127 is the exclusive remedy.",
   """An aggrieved consumer must pursue the statutory appeal, not a civil suit (<span class="cn">Yogesh Nayyar</span>; <span class="cn">B L Kantroo</span>)."""),
  ("A barred plaint is rejected under Order 7 Rule 11(d).",
   """Where the suit is barred by Section 145, rejection of the plaint is the correct course."""),
 ],
 cit_preamble="The authorities below were relied on by the Court in dismissing the appeal.",
 cites=[SARJIWAN] + S126_GRP)
build(c029, "case_029.html")

# ===== 039 Harvinder Singh Matharu v. BSES Rajdhani (civil suit; declaration/injunction) =====
c039 = dict(
 title="Harvinder Singh Matharu v. BSES Rajdhani Power Ltd.",
 subcite="CS (DJ) No.&nbsp;777/2022 &nbsp;|&nbsp; CNR DLWT01-008341-2022 &nbsp;|&nbsp; Civil Court, West District, Tis Hazari Courts, Delhi",
 court="Court of the Civil Judge, West District, Tis Hazari Courts, Delhi",
 judge="Ms. Susheel Bala Dagar, Civil Judge",
 doj="date of judgment", dooff="&mdash;",
 parties="Harvinder Singh Matharu (plaintiff/consumer) <em>v.</em> BSES Rajdhani Power Ltd. (defendant licensee)",
 statutes="Sections 126 &amp; 145, Electricity Act, 2003; Specific Relief Act, 1963 (declaration and injunction); Code of Civil Procedure, 1908",
 result="<strong>Civil suit for declaration and injunction.</strong> A consumer&rsquo;s civil action against the licensee &mdash; seeking a declaration and a mandatory/permanent injunction in respect of his connection &mdash; included for comparison as the civil counterpart to the criminal Section 135 prosecutions in this set.",
 charge="<p><strong>Nature of the proceeding:</strong> A consumer&rsquo;s civil suit against the distribution licensee seeking a declaration and a mandatory and permanent injunction in relation to his electricity connection and the demand raised against him &mdash; the civil, consumer-initiated mirror image of the criminal theft complaints that make up the rest of this set.</p>",
 facts="""<p>The plaintiff, a consumer of BSES Rajdhani Power Ltd., instituted a civil suit seeking a declaration and mandatory and permanent injunctions against the licensee in respect of his connection and the demand/action taken against him. Unlike the Section 135 prosecutions elsewhere in this set &mdash; where the licensee is the complainant and the consumer the accused &mdash; here the consumer is the plaintiff and the licensee the defendant.</p>
<p>The proceeding is a civil one governed by the Code of Civil Procedure and the Specific Relief Act, and it engages the electricity statute chiefly through the boundary between civil disputes (assessment/unauthorised use, and the Section 145 bar) and the criminal remedy of a theft prosecution.</p>""",
 headnote="""A consumer&rsquo;s civil suit for declaration and injunction against the licensee &mdash; the civil counterpart to a Section 135 prosecution. It is included in this digest set to mark the contrast: where the dispute is about assessment or unauthorised use rather than dishonest abstraction, the forum is civil (subject to the Section 145 bar and the Section 127 statutory appeal), not the criminal Electricity Court.""",
 interp="""  <h3 class="grp">Electricity Act, 2003</h3>
  <h3>Civil Remedy <em>vs</em> Criminal Prosecution</h3>
  <p>This proceeding marks the civil end of the spectrum. A consumer aggrieved by a demand or by the licensee&rsquo;s action may, in an appropriate case, seek civil relief (declaration/injunction); but where the dispute concerns an assessment for unauthorised use under Section 126, Section 145 bars the civil court and the remedy is the statutory appeal under Section 127. The criminal machinery of Section 135 is reserved for dishonest abstraction &mdash; theft &mdash; and is distinct from the consumer&rsquo;s civil grievances.</p>""",
 reasoning=[
  ("The consumer is the plaintiff, not the accused.",
   """The proceeding inverts the usual alignment of the theft cases: the consumer sues the licensee for a declaration and injunction, rather than defending a Section 135 complaint. It is a civil action, tried by a civil court under the CPC and the Specific Relief Act."""),
  ("The electricity statute enters through the civil/criminal boundary.",
   """The matter engages the Electricity Act mainly at the boundary between civil disputes &mdash; assessments, unauthorised use and the Section 145 bar &mdash; and the criminal remedy of a theft prosecution, illustrating that not every electricity dispute is a Section 135 case."""),
  ("Included for comparative completeness.",
   """As the sole civil, consumer-initiated matter among the fifty, it is digested briefly to complete the picture and to contrast the civil forum with the criminal Electricity Court that decides the theft complaints."""),
 ],
 mode_desc="",
 bill="&mdash;",
 held="<p>The matter is a civil suit for declaration and injunction and is recorded here for comparative completeness within the set. Its significance lies in marking the civil/criminal boundary rather than in any finding on a Section 135 theft charge.</p>",
 sig_intro="The only civil, consumer-initiated matter in the set &mdash; the mirror image of the theft prosecutions. Three propositions stand out:",
 significance=[
  ("Not every electricity dispute is a theft case.",
   """Assessment and unauthorised-use grievances are civil; only dishonest abstraction is Section 135 theft."""),
  ("The consumer&rsquo;s civil remedies are limited by the statutory scheme.",
   """Where Section 126 is engaged, Section 145 bars the civil court and Section 127 provides the appeal."""),
  ("Comparative value.",
   """The case anchors the civil end of the spectrum against which the criminal prosecutions can be read."""),
 ],
 cites=[], out="case_039.html")
build(c039, "case_039.html")

# ===== 040 State v. Kumari Devi (meter tampering / meter-jumping; retained meter; conviction) =====
c040 = dict(
 title="State v. Kumari Devi",
 subcite="Ct. Case No.&nbsp;178/2020 &nbsp;|&nbsp; PS Mangol Puri &nbsp;|&nbsp; CNR DLNW010015012020",
 court=ROHINI, judge=J_PK,
 doj="date of judgment", dooff="date of inspection",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Kumari Devi (registered consumer of the inspected premises)",
 statutes="Section 135 (clauses (b)/(c) and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Sections 65B &amp; 106, Indian Evidence Act, 1872; Sections 251 &amp; 313, Cr.P.C.",
 result="<strong>Convicted under Section 135, Electricity Act, 2003.</strong> A meter-tampering (&ldquo;meter-jumping&rdquo;) case in which the tampered meter was retained as case property. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Kumari Devi dishonestly abstracted electricity by tampering with the meter (meter-jumping) so that it did not register the true consumption, attracting the meter-tampering limbs of Section 135(1) of the Electricity Act, 2003; and whether, tampering being shown, she rebutted the presumption in the third proviso.</p>",
 facts="""<p>On inspection of the accused&rsquo;s premises, an enforcement team of TPDDL found the meter tampered &mdash; a &ldquo;meter-jumping&rdquo; arrangement causing the meter not to record the true consumption. Unlike the direct-hooking cases, the abstraction here was achieved through the meter itself; the tampered meter was retained and sealed as case property. The usual inspection documents were prepared and the proceedings videographed with a Section 65B certificate.</p>
<p>On a complaint under Section 135, the accused pleaded not guilty. The inspecting officials and the Investigating Officer were examined and the retained meter and electronic record proved. Under Section 313 Cr.P.C. the accused denied the allegations and led no defence evidence.</p>""",
 headnote="""Abstraction achieved by tampering with the meter itself &mdash; &ldquo;meter-jumping&rdquo; so that it under-records consumption &mdash; is theft under the meter-tampering limbs of Section 135(1); the tampered meter, retained as case property, is the material proof, and the unrebutted third-proviso presumption convicts the registered consumer who leads no evidence of lawful, correctly-metered use.""",
 interp="""  <h3 class="grp">Electricity Act, 2003</h3>
  <h3>Section 135(1)(b)/(c) &mdash; Theft by Tampering with the Meter</h3>
  <p>Where the abstraction is achieved not by an external hook but by tampering with the meter itself &mdash; here a &ldquo;meter-jumping&rdquo; arrangement causing the meter not to register the true consumption &mdash; the offence falls under the meter-tampering limbs of Section 135(1) (interfering with, or preventing the correct registration by, a meter). It is as much a dishonest abstraction as a direct tap; the retained meter is the material evidence of the manner of theft.</p>
  <h3>Third Proviso to Section 135(1) &mdash; Presumption of Dishonest Use</h3>
  <p>Proof that the meter was tampered raises the reverse-onus presumption of dishonest use. The accused must adduce evidence making an innocent explanation reasonably probable &mdash; a bare denial, without proof of lawful, correctly-metered consumption, does not displace it.</p>""",
 reasoning=[
  ("The abstraction was by tampering with the meter.",
   """The theft was achieved through the meter itself &mdash; a meter-jumping arrangement causing it to under-record consumption &mdash; falling within the meter-tampering limbs of Section 135(1); the manner of abstraction differed from a direct hook but was equally a dishonest abstraction."""),
  ("The retained meter was the material proof.",
   """The tampered meter was retained and sealed as case property; it, with the inspection report and the certified videography, established the tampering and the manner of theft, and fixed the registered consumer as answerable."""),
  ("The absence of a public witness did not weaken the prosecution.",
   """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> non-examination of an independent witness is no infirmity."""),
  ("The presumption was compulsory and, unrebutted, convicted.",
   """Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court held that the accused, leading no defence evidence and producing no proof of lawful metered use (<span class="cn">Mukesh Rastogi</span>; Section 106 onus), failed to rebut the presumption."""),
 ],
 mode_desc="the tampering of the meter (meter-jumping) so that it did not register the true consumption",
 bill="&mdash;",
 held="<p>The prosecution proved beyond reasonable doubt that the meter at the accused&rsquo;s premises was tampered so as to abstract electricity, an offence punishable under Section 135 of the Electricity Act, 2003, and that the accused led no evidence to rebut the statutory presumption. <strong>Kumari Devi is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>",
 sig_intro="A meter-tampering conviction &mdash; theft through the meter rather than around it. Four propositions stand out:",
 significance=[
  ("Meter-jumping is theft under Section 135.",
   """Causing the meter to under-record consumption is a dishonest abstraction within the meter-tampering limbs of Section 135(1)."""),
  ("The retained meter is the material proof.",
   """Unlike a hooked wire, the tampered meter itself, retained as case property, evidences the manner of theft."""),
  ("The presumption applies to tampering.",
   """Proof of tampering raises the reverse-onus presumption just as a direct tap does."""),
  ("A public witness is not essential.",
   """Official inspection testimony suffices absent shown enmity (<span class="cn">Ashwani Kumar</span>; <span class="cn">Sushil Sharma</span>)."""),
 ],
 cites=STD_CITES)
build(c040, "case_040.html")

# ===== 041 State v. Jameed & Anr. (s.135 + s.138 interference + s.150; two accused; conviction) =====
c041 = dict(
 title="State v. Jameed &amp; Anr.",
 subcite="Ct. Case No.&nbsp;184/2018 &nbsp;|&nbsp; PS Bhalswa Dairy &nbsp;|&nbsp; CNR DLNW010037562018",
 court=ROHINI, judge=J_PK,
 doj="date of judgment", dooff="date of inspection",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> (1) Jameed and (2) Rasheed Ahmad",
 statutes="Sections 135, 138 &amp; 150 (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Sections 65B &amp; 106, Indian Evidence Act, 1872; Sections 251 &amp; 313, Cr.P.C.",
 result="<strong>Convicted under Sections 135, 138 and 150, Electricity Act, 2003.</strong> A direct-theft case in which the mode of abstraction also involved interference with the licensee&rsquo;s works (Section 138), with two accused. Matter posted for hearing on quantum of sentence.",
 charge="<p>Whether the accused Jameed and Rasheed Ahmad dishonestly abstracted electricity by directly tapping the licensee&rsquo;s network (Section 135), whether the mode involved unauthorised interference with the licensee&rsquo;s meters/works (Section 138), and whether either accused abetted the other&rsquo;s offence (Section 150); and whether, an unauthorised abstraction being proved, the accused rebutted the third-proviso presumption.</p>",
 facts="""<p>On inspection, an enforcement team of TPDDL found a direct abstraction of electricity at the premises, the mode involving interference with the licensee&rsquo;s works/apparatus. Two persons, Jameed and Rasheed Ahmad, were arrayed as accused &mdash; the case proceeding on both direct theft (Section 135) and unauthorised interference with the licensee&rsquo;s meters/works (Section 138), with abetment under Section 150. The usual inspection documents were prepared and the proceedings videographed with a Section 65B certificate.</p>
<p>On a complaint under Sections 135/138/150, both accused pleaded not guilty. The inspecting officials and the Investigating Officer were examined and the electronic record proved. Under Section 313 Cr.P.C. the accused denied the allegations and led no defence evidence.</p>""",
 headnote="""Direct abstraction of electricity is theft under Section 135; where the mode involves unauthorised interference with the licensee&rsquo;s meters or works, Section 138 applies alongside; and a co-accused who assists the abstraction abets it under Section 150. On proof of the unauthorised means the third-proviso presumption arises, and both accused, leading no evidence, are convicted.""",
 interp="""  <h3 class="grp">Electricity Act, 2003</h3>
  <h3>Section 135 &amp; Section 150 &mdash; Theft and Abetment</h3>
  <p>Direct abstraction of electricity is theft under Section 135; a person who consciously assists or permits it abets the offence under Section 150 and is liable to the same punishment. Where two persons act together in the abstraction, each may be principal or abettor.</p>
  <h3>Section 138 &mdash; Interference with Meters or Works</h3>
  <p>Section 138 punishes unauthorised interference with the licensee&rsquo;s meters, works or apparatus &mdash; including unauthorised connection, reconnection, or interference with the equipment. It applies alongside Section 135 where the mode of theft is effected by interfering with the licensee&rsquo;s works, adding a distinct head of liability to the dishonest abstraction.</p>""",
 reasoning=[
  ("The direct abstraction was theft under Section 135.",
   """The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated the direct abstraction at the premises as a clause (a) taking from the licensee&rsquo;s network; on proof of that artificial means the third proviso&rsquo;s presumption arose."""),
  ("The mode engaged Section 138.",
   """Because the abstraction was effected by interfering with the licensee&rsquo;s works/apparatus, Section 138 &mdash; unauthorised interference with meters or works &mdash; applied alongside Section 135, adding a distinct head of liability."""),
  ("Two accused; abetment under Section 150.",
   """With two persons arrayed, the one who assisted or permitted the abstraction abetted it under Section 150, which carries the punishment of the principal offence; the liability of each did not depend on the other&rsquo;s conviction."""),
  ("The presumption was compulsory and, unrebutted, convicted.",
   """No public-witness infirmity being shown (<span class="cn">Ashwani Kumar</span>; <span class="cn">Sushil Sharma</span>), and following <span class="cn">Neeraj Dutt</span> and <span class="cn">Hiten P. Dalal</span> on the compulsory presumption, the accused &mdash; leading no defence evidence and producing no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106) &mdash; failed to rebut it."""),
 ],
 mode_desc="the direct abstraction of electricity effected by interfering with the licensee&rsquo;s works",
 bill="&mdash;",
 held="<p>The prosecution proved beyond reasonable doubt that electricity was dishonestly abstracted at the premises by interfering with the licensee&rsquo;s works, and that the accused led no evidence to rebut the statutory presumption. <strong>Jameed and Rasheed Ahmad are accordingly convicted under Sections 135, 138 and 150 of the Electricity Act, 2003</strong>, and are to be heard on the quantum of sentence.</p>",
 sig_intro="A conviction combining theft (Section 135), interference with the licensee&rsquo;s works (Section 138) and abetment (Section 150), with two accused. Four propositions stand out:",
 significance=[
  ("Section 138 can apply alongside Section 135.",
   """Where the theft is effected by interfering with the licensee&rsquo;s meters or works, Section 138 adds a distinct head of liability to the Section 135 abstraction."""),
  ("Abetment reaches the assisting co-accused.",
   """A second person who assists or permits the abstraction abets it under Section 150 and shares the principal&rsquo;s punishment."""),
  ("The presumption operates against each accused.",
   """Once the unauthorised means is proved, each must displace the reverse-onus presumption with evidence of lawful use."""),
  ("Silence and no paid bills convict.",
   """Leading no evidence, the accused leave the compulsory presumption unrebutted (<span class="cn">Neeraj Dutt</span>; <span class="cn">Mukesh Rastogi</span>)."""),
 ],
 cites=STD_CITES)
build(c041, "case_041.html")
print("Specials 029,039,040,041 generated.")
