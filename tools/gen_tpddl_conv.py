#!/usr/bin/env python3
"""TPDDL / BRPL direct-theft convictions (Section 135) before the North-West (Rohini)
   Electricity Court (Sh. Prashant Kumar) and, for 050, the South (Saket) Electricity Court.
   These add the new authority State v. N.M.T Joy Immaculate (search/seizure irregularity)."""
from gen_08_11 import build, STD_CITES

NMT = ("State v. N.M.T Joy Immaculate", "2004 (5) SCC 729",
       "An irregularity or illegality in the search, seizure or investigation does not by itself vitiate the trial or render the recovered material inadmissible; absent resulting prejudice or failure of justice, the Court may act on the evidence.")
# TPDDL direct-conviction citation set: Ashwani, Sushil, N.M.T Joy Immaculate, Neeraj, Hiten, Mukesh
CITES_TPDDL = [STD_CITES[0], STD_CITES[1], NMT, STD_CITES[2], STD_CITES[3], STD_CITES[4]]

ROHINI = "Court of the Additional Sessions Judge (Electricity), North&#8209;West District, Rohini Courts, Delhi"
J_PK = "Sh. Prashant Kumar, Addl. Sessions Judge (Electricity)"

def tconv(*, title, docket, court=ROHINI, judge=J_PK, complainant="Tata Power Delhi Distribution Ltd.",
          doj, dooff, parties, accused_name, team_head, mode_short, mode_full, section_label,
          load, bill=None, defence, court_answer, settled=False, s313_admission=False,
          extra_reasoning=None, extra_sig=None, sig_intro=None, statutes=None, out):
    disc_short = "TPDDL" if "Tata" in complainant else "BSES Rajdhani"
    if bill:
        assess = f"Following the applicable tariff the company assessed a theft demand of Rs.&nbsp;{bill}/&#8209;, which went unpaid, and its Authorised Officer filed the complaint under Section 135 of the Act."
        result_civil = (f" Civil liability on the theft bill (Rs.&nbsp;{bill}/&#8209;) settled and the amount deposited during trial."
                        if settled else f" The theft demand of Rs.&nbsp;{bill}/&#8209; remained unpaid.")
        bill_disp = f"Rs.&nbsp;{bill}/&#8209;"
    else:
        assess = "The company assessed the theft demand on the connected load and filed the complaint through its Authorised Officer under Section 135 of the Act; the demand went unpaid."
        result_civil = ""
        bill_disp = "the assessed theft demand"
    result = (f"<strong>Convicted under Section 135, Electricity Act, 2003.</strong>{result_civil} Matter posted for hearing on quantum of sentence.")
    charge = (f"<p>Whether the accused {accused_name} dishonestly abstracted electricity {mode_short}, so as to attract Section 135(1)(a) of the Electricity Act, 2003; and whether, an unauthorised means of abstraction having been proved, {accused_name} discharged the onus cast by the presumption in the third proviso to Section 135(1).</p>")
    admit = (f" In the statement under Section 313 Cr.P.C. the accused admitted presence at the inspection and the fact of the direct connection." if s313_admission else "")
    facts = (f"""<p>On {dooff}, an enforcement team of {complainant} headed by {team_head} inspected the premises. {mode_full} The connected load was {load}&nbsp;KW. The proceedings were videographed with a Section 65B certificate, and an Inspection Report, Load Report and Seizure Memo (with an advisory notice) were prepared at the spot. {assess}</p>
<p>A notice under Section 251 Cr.P.C. was served and {accused_name} pleaded not guilty.{admit} The inspecting officials and the Investigating Officer were examined and the electronic record proved. {defence} Under Section 313 Cr.P.C. the accused denied the substance of the allegations and led no defence evidence.</p>""")
    headnote = (f"Directly tapping the licensee&rsquo;s network to draw an unmetered supply is theft under Section 135(1)(a); the accused being identified at the videographed inspection, and the routine objections &mdash; no public witness, market-available case property, alleged defects in sealing or investigation &mdash; being no answer (an irregularity in search or seizure does not vitiate the trial: <span class=\"cn\">N.M.T Joy Immaculate</span>), the unrebutted third-proviso presumption convicts.")
    reasoning = [
      ("The direct tap was a clause (a) abstraction attracting the presumption.",
       f"""The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated {mode_short} as {section_label}. On proof of that artificial means the third proviso&rsquo;s presumption of dishonest use arose."""),
      ("The accused was identified at the inspection and shown to be consuming.",
       f"""{court_answer}"""),
      ("The objections to the investigation did not vitiate the case.",
       """The Court rejected the defence that the case property was freely available in the market, that the seizure/sealing was defective or that no duty roster was proved: on <span class="cn">State v. N.M.T Joy Immaculate</span>, 2004 (5) SCC 729, an irregularity or illegality in the search, seizure or investigation does not by itself vitiate the trial or render the recovered material inadmissible, absent resulting prejudice."""),
      ("The absence of a public witness did not weaken the prosecution.",
       """No animosity of the officials was shown, and the site being in a thickly populated area where the public declined to join, on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> non-examination of an independent witness is no infirmity."""),
      ("The presumption was compulsory and, unrebutted, convicted.",
       f"""Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court held that {accused_name}, having led no defence evidence and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus), failed to rebut the presumption and was guilty under Section 135."""),
    ]
    if extra_reasoning:
        reasoning.insert(4, extra_reasoning)
    significance = [
      ("Directly tapping the network is theft under clause (a).",
       """A hooked or tapped connection drawing unmetered supply from the licensee&rsquo;s pole, mains or feeder pillar is a direct, artificial abstraction &mdash; no meter tampering need be shown."""),
      ("Identification at the videographed inspection fixes the accused.",
       """Presence in the photographs/video, undisputed signatures on the inspection report and appliances in use place the abstraction on the accused; a disconnected earlier connection makes the continued consumption dishonest."""),
      ("An irregular search or seizure does not vitiate the trial.",
       """Market-available case property, imperfect sealing or a missing duty roster go only to weight, not admissibility (<span class="cn">N.M.T Joy Immaculate</span>); absent prejudice the Court acts on the evidence."""),
      ("A public witness is not essential in a populated locality.",
       """Where the public decline to join in a crowded area, the officials&rsquo; consistent testimony and the presumption of regularity suffice (<span class="cn">Ashwani Kumar</span>; <span class="cn">Sushil Sharma</span>)."""),
      ("The reverse-onus presumption convicts the silent accused.",
       """No paid bills and no defence evidence leave the compulsory presumption unrebutted (<span class="cn">Neeraj Dutt</span>; <span class="cn">Hiten P. Dalal</span>; <span class="cn">Mukesh Rastogi</span>; Section 106)."""),
    ]
    if extra_sig:
        significance.insert(3, extra_sig)
    c = dict(
      title=title, subcite=f"{docket} &nbsp;|&nbsp; {court}", court=court, judge=judge,
      doj=doj, dooff=dooff, parties=parties, result=result, charge=charge, facts=facts, headnote=headnote,
      statutes=statutes or "Section 135 (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Sections 65B &amp; 106, Indian Evidence Act, 1872; Sections 251, 313 &amp; 41A, Cr.P.C.",
      reasoning=reasoning, mode_desc=mode_short, bill=(bill or "&mdash;"),
      held=(f"<p>The prosecution proved beyond reasonable doubt that {accused_name} abstracted electricity {mode_short}, an offence punishable under Section 135 of the Electricity Act, 2003, and led no evidence to rebut the statutory presumption. <strong>{accused_name} is accordingly convicted under Section 135 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>"),
      sig_intro=sig_intro or f"A direct-theft conviction on a hooked connection, the routine investigative objections rejected. Five propositions stand out:",
      significance=significance, cites=CITES_TPDDL)
    build(c, out)

# ---- 030 Neelam (LV-mains tap; bill not stated) ----
tconv(title="State v. Neelam", docket="S.C. No.&nbsp;676/2023 &nbsp;|&nbsp; PS S.P. Badli &nbsp;|&nbsp; CNR DLNW010074462023",
 doj="17 April 2026", dooff="1 September 2022",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Neelam W/o Sh. Madan, R/o H. No.&nbsp;750, Badli MCD Colony, Prem Nagar, Village Samaipur, Delhi&#8209;110042",
 accused_name="Neelam", team_head="Sh. Sudesh Sharma (HOD, MMG Enforcement, TPDDL)",
 mode_short="by directly tapping the licensee&rsquo;s LV mains through illegal wires, the supply drawn without a meter",
 mode_full="The premises were found drawing supply by a direct tap from the licensee&rsquo;s LV mains through illegal wires, without a functioning meter.",
 section_label="a clause (a) tapping of the licensee&rsquo;s mains",
 load="9.754", bill=None,
 defence="The accused pleaded false implication and non-joining of public witnesses.",
 court_answer="The accused was identified with the inspected premises and the direct tap on the LV mains was established by the inspection report and the certified videography; the consistent testimony of the officials proved the factum and manner of the abstraction.",
 out="case_030.html")

# ---- 031 Sukh Chain (LT-mains hooking; dhaba; bill not stated) ----
tconv(title="State v. Sukh Chain", docket="S.C. No.&nbsp;44/2023 &nbsp;|&nbsp; FIR No.&nbsp;1057/2022, PS Mangol Puri",
 doj="16 January 2026", dooff="9 December 2019",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Sukh Chain S/o Sh. Bawa Singh, R/o H. No.&nbsp;738, F-Block, Punjabi Camp, Mangolpuri, Delhi",
 accused_name="Sukh Chain", team_head="Sh. Mukesh Kumar (HOG, CEG, TPDDL)",
 mode_short="by hooking the licensee&rsquo;s LT mains through PVC wires to run a dhaba, the supply drawn without a meter",
 mode_full="The premises &mdash; used to run a dhaba/eatery &mdash; were found drawing supply by direct hooking from the licensee&rsquo;s LT mains through PVC-insulated wires, without a functioning meter.",
 section_label="a clause (a) hooking of the licensee&rsquo;s mains",
 load="2.985", bill=None,
 defence="The accused pleaded false implication and non-joining of public witnesses.",
 court_answer="The accused was identified with the dhaba premises and the direct hooking on the LT mains was established by the inspection report and the certified videography; running a commercial eatery on an unmetered tap underscored the dishonest abstraction.",
 extra_sig=("A commercial tap for an eatery is squarely within clause (a).",
   """Running a dhaba on an unmetered direct hook from the LT mains is a dishonest abstraction; the commercial use aggravates rather than explains the draw."""),
 out="case_031.html")

# ---- 033 Saroj Devi (pole tap; bill 2,87,844) ----
tconv(title="State v. Saroj Devi", docket="S.C. No.&nbsp;531/2024 &nbsp;|&nbsp; FIR No.&nbsp;1155/2023, PS Mangol Puri",
 doj="14 January 2026", dooff="20 April 2023",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Saroj Devi W/o Sh. Rajesh Kumar, R/o H. No.&nbsp;247/285, Jhuggi C, N-Block, Dera Gazi Khan, Pitampura, Delhi",
 accused_name="Saroj Devi", team_head="Sh. Bharat Bhushan (HOG, CEG, TPDDL)",
 mode_short="by directly tapping the licensee&rsquo;s pole through illegal wires, the supply drawn without a meter",
 mode_full="The premises were found drawing supply by a direct tap from the licensee&rsquo;s pole through illegal wires, without a functioning meter; the connected load was substantial.",
 section_label="a clause (a) tapping of the licensee&rsquo;s pole",
 load="12.306", bill="2,87,844",
 defence="The accused submitted that the site was in a thickly populated area where public persons refused to join, and pleaded false implication.",
 court_answer="The accused was identified with the inspected premises; the direct pole-tap and the 12.306&nbsp;KW load were established by the inspection report, the load report and the certified videography, the officials&rsquo; consistent testimony proving the manner of the abstraction.",
 out="case_033.html")

# ---- 034 Arjun (LT-ABC hooking; bill 3,31,798; strong defence rejected) ----
tconv(title="State v. Arjun", docket="Ct. Case No.&nbsp;218/2024 (orig. 242/2023) &nbsp;|&nbsp; PS Sultanpuri",
 doj="18 March 2026", dooff="6 January 2024",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Arjun S/o Sh. Sant Ram, R/o H. No.&nbsp;415, Block B-4, Sultanpuri, Delhi&#8209;110041",
 accused_name="Arjun", team_head="the enforcement team of TPDDL",
 mode_short="by hooking the licensee&rsquo;s LT aerial-bunched conductor, an earlier connection in his father&rsquo;s name having been disconnected",
 mode_full="The premises were found drawing supply by direct hooking from the licensee&rsquo;s LT aerial-bunched conductor; an earlier legal connection in the accused&rsquo;s father&rsquo;s name had been disconnected and no fresh connection taken, yet electricity was being consumed.",
 section_label="a clause (a) hooking of the licensee&rsquo;s conductor",
 load="15.221", bill="3,31,798",
 defence="The accused argued that the case property was freely available in the market, that no duty roster proved the team on duty, that the property was jointly owned, that the case property bore only a paper seal, and that no public witnesses were joined.",
 court_answer="The Court found each ingredient established: the accused&rsquo;s presence was visible in the photographs and his signatures on the inspection report were not disputed; the earlier connection in his father&rsquo;s name having been disconnected with no valid restoration, his continued consumption showed dishonest intention; and the photographed electrical appliances proved use.",
 s313_admission=False,
 extra_sig=("A disconnected prior connection makes continued use dishonest.",
   """Where the earlier legal connection (here in the father&rsquo;s name) stands disconnected and none is restored, continuing to consume electricity is itself evidence of dishonest abstraction."""),
 out="case_034.html")

# ---- 036 Shekh Rabibul (pole tap; e-rickshaw defence rejected; bill 3,32,751) ----
tconv(title="State v. Shekh Rabibul", docket="S.C. No.&nbsp;683/2019 &nbsp;|&nbsp; FIR No.&nbsp;687/2018, PS Bhalaswa Dairy",
 doj="5 February 2026", dooff="13 June 2018",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Shekh Rabibul S/o Sh. Shekh Rafik, R/o Jhuggi No.&nbsp;N-38-274, CD Park, Jahangirpuri, Delhi",
 accused_name="Shekh Rabibul", team_head="the enforcement team of TPDDL",
 mode_short="by directly tapping the licensee&rsquo;s pole through a two-core wire to charge e-rickshaws, the supply drawn without a meter",
 mode_full="The premises were found drawing supply by a direct tap from the licensee&rsquo;s pole through a two-core wire, used for charging e-rickshaws, without a functioning meter.",
 section_label="a clause (a) tapping of the licensee&rsquo;s pole",
 load="5.2", bill="3,32,751",
 defence="The accused claimed he was present only to charge an e-rickshaw and that he paid the charges to one &ldquo;Deepak,&rdquo; not running the charging point himself.",
 court_answer="The Court rejected the &ldquo;mere customer&rdquo; plea: the accused was identified with the premises where the tap and the charging setup were found, and the inspection report, load report and certified videography established that the abstraction was being carried on at his jhuggi &mdash; an unnamed &ldquo;Deepak&rdquo; to whom charges were allegedly paid being neither produced nor supported by any evidence.",
 extra_sig=("The &lsquo;I only paid a third party&rsquo; e-rickshaw plea fails without proof.",
   """A bare claim of paying charges to an unnamed operator does not displace the accused&rsquo;s identification with the premises where the tap and charging point were found."""),
 out="case_036.html")

# ---- 037 Sunil Kumar (Tyco-box feeder-pillar tap; bill not stated) ----
tconv(title="State v. Sunil Kumar", docket="Ct. Case No.&nbsp;16/2019 &nbsp;|&nbsp; PS Adarsh Nagar",
 doj="27 January 2026", dooff="22 June 2018",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Sunil Kumar, R/o Adarsh Nagar, Delhi",
 accused_name="Sunil Kumar", team_head="the enforcement team of TPDDL",
 mode_short="by tapping the phase from the licensee&rsquo;s Tyco-box feeder pillar and taking the neutral from earthing, the supply drawn without a meter",
 mode_full="The premises were found drawing supply by tapping the phase wire from the licensee&rsquo;s Tyco-box feeder pillar (No.&nbsp;412-6/9/1/1/1) and taking the neutral from earthing, without a functioning meter.",
 section_label="a clause (a) tapping of the licensee&rsquo;s feeder pillar",
 load="4.958", bill=None,
 defence="The accused pleaded false implication and non-joining of public witnesses.",
 court_answer="The accused was identified with the inspected premises and the tapping of the phase from the feeder pillar, with the neutral drawn from earthing, was established by the inspection report and the certified videography.",
 out="case_037.html")

# ---- 038 Prem Kumar Soni (LT pole two-core tap; bill 80,080) ----
tconv(title="State v. Prem Kumar Soni", docket="Ct. Case No.&nbsp;312/2023 &nbsp;|&nbsp; PS Kanjhawala",
 doj="9 April 2026", dooff="26 June 2023",
 parties="State (Tata Power Delhi Distribution Ltd.) <em>v.</em> Prem Kumar Soni, R/o Kanjhawala, Delhi",
 accused_name="Prem Kumar Soni", team_head="the enforcement team of TPDDL",
 mode_short="by directly tapping the licensee&rsquo;s LT network from a pole through two-core PVC wires, the supply drawn without a meter",
 mode_full="The premises were found drawing supply by a direct tap from the licensee&rsquo;s LT network at Pole No.&nbsp;513-23/6/2/11 through two-core PVC-insulated wires, without a functioning meter.",
 section_label="a clause (a) tapping of the licensee&rsquo;s LT network",
 load="4.8", bill="80,080",
 defence="The accused pleaded false implication and non-joining of public witnesses.",
 court_answer="The accused was identified with the inspected premises and the direct two-core tap from the pole was established by the inspection report, the load report and the certified videography.",
 out="case_038.html")

# ---- 050 Kuldeep (BSES Rajdhani; Saket; s.313 admission + video; settled) ----
tconv(title="State v. Kuldeep",
 docket="Ct. Case No.&nbsp;630/2020 &nbsp;|&nbsp; CNR DLST01-006876-2020",
 court="Special Court (Electricity), South District, Saket Courts, New Delhi",
 judge="Sh. Vivek Kumar Gulia, Addl. Sessions Judge",
 complainant="BSES Rajdhani Power Ltd.",
 doj="6 April 2026", dooff="25 August 2020",
 parties="State (BSES Rajdhani Power Ltd.) <em>v.</em> Kuldeep, R/o South District, Delhi",
 accused_name="Kuldeep", team_head="the enforcement team of BSES Rajdhani Power Ltd.",
 mode_short="by directly tapping the licensee&rsquo;s pole through a two-core aluminium cable, the premises having no meter",
 mode_full="No meter was installed at the premises; the supply was found being drawn by a direct tap from the BSES pole through a black two-core aluminium cable (10&nbsp;sq.&nbsp;mm). The co-accused Deepak was later dropped, the case against him being withdrawn.",
 section_label="a clause (a) tapping of the licensee&rsquo;s pole",
 load="6.734", bill="1,27,619", settled=True, s313_admission=True,
 defence="The accused disputed the seizure and the sufficiency of proof of his identity as the user.",
 court_answer="The accused himself admitted, in his statement under Section 313 Cr.P.C., his presence at the inspection and the fact of the direct theft, and he was clearly visible in the certified video recording; his own admission and the electronic record placed the abstraction on him beyond doubt.",
 statutes="Sections 135 &amp; 154 (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Sections 65B &amp; 106, Indian Evidence Act, 1872; Sections 251, 313 &amp; 41A, Cr.P.C.",
 sig_intro="A direct-theft conviction fortified by the accused&rsquo;s own Section 313 admission and the certified video. Five propositions stand out:",
 extra_sig=("A Section 313 admission, with the video, is decisive.",
   """Where the accused admits presence and the direct connection in his Section 313 statement and is visible in the certified recording, the identity and factum of theft are established beyond the presumption."""),
 out="case_050.html")
print("TPDDL/BRPL convictions 030,031,033,034,036,037,038,050 generated.")
