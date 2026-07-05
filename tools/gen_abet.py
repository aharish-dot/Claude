#!/usr/bin/env python3
"""Abetment-variant builder: owner/registered consumer convicted u/s 135 r/w 150
   where the actual user/tenant absconded (not arrested). Reusable for such cases."""
from gen_08_11 import build, STD_CITES

LOKESH = ("Lokesh Chandela v. State of NCT &amp; Ors.", "Delhi HC, Crl. A. 479/2011",
          "Both the user of electricity and the owner/registered consumer of the premises fall within &ldquo;consumer&rdquo; under Section 2(15), making the owner answerable for illegal abstraction found at the premises.")
# abetment citation set: Ashwani, Sushil, Lokesh, Neeraj, Hiten, Mukesh
CITES_ABET = [STD_CITES[0], STD_CITES[1], LOKESH, STD_CITES[2], STD_CITES[3], STD_CITES[4]]

def abet(*, case_no, title, sc, fir, ps, doj, dooff, owner, accused_name, user, team_head,
         mode_short, mode_full, section_label, load, bill, noc,
         extra_reasoning=None, extra_sig=None, settlement_txt=None, out):
    owner_first = accused_name
    noc_clause = (" and an NOC issued by the complainant company" if noc else "")
    settle = settlement_txt or (f"the theft bill had been settled, the settlement amount deposited{noc_clause}")
    result = (f"<strong>Convicted under Section 135 read with Section 150 (abetment), Electricity Act, 2003.</strong> "
              f"Civil liability on the theft bill (Rs.&nbsp;{bill}/&#8209;) settled and the amount deposited during trial"
              f"{' and an NOC issued' if noc else ''}. Matter posted for hearing on quantum of sentence.")
    charge = (f"<p>Whether {user} &mdash; the user/tenant who abstracted electricity at the inspected premises but was "
              f"not arrested &mdash; dishonestly abstracted electricity {mode_short}; whether the accused {owner_first}, "
              f"the registered consumer/owner of those premises, abetted that theft by consciously permitting it, so as "
              f"to be guilty under Section 135 read with Section 150 of the Electricity Act, 2003; and whether, once the "
              f"prosecution proved an unauthorised means of abstraction, {owner_first} discharged the onus cast by the "
              f"presumption in the third proviso to Section 135(1).</p>")
    facts = (f"""<p>On {dooff}, an inspection team of BSES Yamuna Power Ltd. (the complainant company) headed by {team_head} """
             f"""inspected the premises. {mode_full} The connected load was {load}&nbsp;KW, used for domestic purposes; """
             f"""the proceedings were videographed and an Inspection Report, Load Report and Seizure Memo (with an advisory """
             f"""notice) were prepared at the spot. Following DERC guidelines the company assessed a theft demand of """
             f"""Rs.&nbsp;{bill}/&#8209;, which went unpaid, and its Authorised Officer filed a complaint under Section 135 """
             f"""read with Section 150 of the Act.</p>
<p>The user/tenant {user} was not arrested; the prosecution proceeded against {owner_first} as the registered consumer/owner """
             f"""of the premises. A notice under Section 251 Cr.P.C. was served and {owner_first} pleaded not guilty. The """
             f"""inspecting officials and the Investigating Officer were examined; the ownership of the premises was proved """
             f"""through the seized ownership documents. Under Section 313 Cr.P.C. {owner_first} denied the allegations and """
             f"""pleaded false implication, and led no defence evidence. Counsel submitted that {settle}.</p>""")
    headnote = (f"A registered consumer/owner who consciously permits a tenant to draw an unauthorised supply from the "
                f"licensee&rsquo;s network abets the theft and is guilty under Section 135 read with Section 150 &mdash; and "
                f"the abettor can be convicted even though the actual user has absconded and is never tried. &ldquo;Consumer&rdquo; "
                f"in Section 2(15) reaches the owner (<span class=\"cn\">Lokesh Chandela</span>), and the compulsory presumption "
                f"in the third proviso to Section 135(1) convicts the owner who leads no evidence of lawful, metered use.")
    reasoning = [
      ("The offence was made out on proof of an unauthorised abstraction at the owner&rsquo;s premises.",
       f"""The Court set out the ingredients of Section 135(1), importing Section 24 IPC for &ldquo;dishonestly,&rdquo; and treated {mode_short} as {section_label}. On proof of that artificial means the third proviso&rsquo;s presumption of dishonest use arose."""),
      ("The owner is a &ldquo;consumer&rdquo; under Section 2(15) and answerable for abstraction at the premises.",
       f"""Reproducing Section 2(15), the Court held that both the user and the owner/registered consumer fall within &ldquo;consumer,&rdquo; so {owner_first} was answerable once illegal abstraction was found at the premises &mdash; drawing support from <span class="cn">Lokesh Chandela v. State of NCT &amp; Ors.</span> (Delhi HC, Crl. A. 479/2011)."""),
      ("The owner&rsquo;s conscious permission was abetment, and the user&rsquo;s absconding did not absolve the abettor.",
       f"""As registered consumer/owner, {owner_first} knew the premises had no lawful metered supply, yet permitted {user} to occupy and draw electricity through the unauthorised connection. That conscious allowance constituted abetment under Section 150, which carries the punishment of the principal offence. That {user} had absconded and was never arrested or tried did not absolve the abettor: the abettor&rsquo;s liability is independent of whether the principal is in the dock."""),
      ("The absence of a public witness did not weaken the prosecution.",
       """No animosity of the officials was shown; on <span class="cn">Punjab State Electricity Board v. Ashwani Kumar</span>, 2010 (7) SCC 569, the official inspection report carries a presumption of regularity, and on <span class="cn">Sushil Sharma v. BSES Rajdhani Power Ltd.</span> (Delhi HC, Crl. A. 1060/2010), non-examination of an independent witness is no infirmity. No procedural lapse under DERC Regulations 60&#8211;63 was suggested."""),
      ("The presumption was compulsory, and settlement of the bill fortified the case.",
       f"""Following <span class="cn">Neeraj Dutt</span> (compulsory &ldquo;shall presume&rdquo;) and <span class="cn">Hiten P. Dalal</span> (prudent-man standard), the Court held that {owner_first}, having led no defence evidence and produced no paid bills (<span class="cn">Mukesh Rastogi</span>; Section 106 onus), failed to rebut the presumption; and the settlement of the Rs.&nbsp;{bill}/&#8209; bill{', with deposit and NOC,' if noc else ' and its deposit'} corroborated the theft rather than closing the criminal case."""),
    ]
    if extra_reasoning:
        reasoning.insert(3, extra_reasoning)
    interp_provision = "Section 135(1)(a) &mdash; Theft of Electricity" if "(a)" in section_label else "Section 135(1) &mdash; Theft of Electricity"
    significance = [
      ("An owner can be convicted of abetment even where the user has absconded.",
       f"""The registered consumer/owner who consciously permits an (unarrested, untried) tenant to draw an unauthorised supply is guilty under Section 135 r/w Section 150; the principal&rsquo;s absence from the dock does not absolve the abettor."""),
      ("&ldquo;Consumer&rdquo; under Section 2(15) reaches the owner.",
       """The owner cannot disown liability for illegal abstraction at the premises merely because a tenant was the user (<span class="cn">Lokesh Chandela</span>)."""),
      ("The reverse-onus presumption binds the owner-abettor.",
       """Once the unauthorised means is proved, the owner must show lawful, metered use &mdash; paid bills under the Section 106 onus (<span class="cn">Mukesh Rastogi</span>) &mdash; failing which the compulsory presumption convicts."""),
      (("Settlement, deposit and even an NOC are not immunity." if noc else "Settlement corroborates guilt."),
       ("""Closing the civil account &mdash; paying the settled bill and taking an NOC &mdash; does not answer the Section 135 charge; the settlement is read as conduct corroborating the theft.""" if noc else """Settling and depositing the theft bill was read as conduct inconsistent with innocence, not neutral compromise.""")),
      ("A public witness is not essential.",
       """Official inspection testimony suffices absent shown enmity (<span class="cn">Ashwani Kumar</span>; <span class="cn">Sushil Sharma</span>)."""),
    ]
    if extra_sig:
        significance.insert(4, extra_sig)
    c = dict(
      title=title, subcite=f"{sc} &nbsp;|&nbsp; {fir}, {ps} &nbsp;|&nbsp; Court of the Addl. Sessions Judge&#8209;05 (Electricity), East, Karkardooma Courts, Delhi",
      doj=doj, dooff=dooff, parties=owner, result=result, charge=charge, facts=facts, headnote=headnote,
      statutes="Sections 135, 150 &amp; 2(15) (and third proviso to s.&nbsp;135(1)), Electricity Act, 2003; Section 24, IPC; Section 106, Indian Evidence Act, 1872; Sections 251, 313 &amp; 41A, Cr.P.C.; Regulations 60&#8211;63, DERC (Supply Code) Regulations, 2007",
      reasoning=reasoning, mode_desc=mode_short, bill=bill,
      held=(f"<p>The prosecution proved beyond reasonable doubt that no lawful metered supply existed at the inspected premises and that electricity was being abstracted through an unauthorised connection, which {accused_name}, as registered consumer/owner, consciously permitted. <strong>{accused_name} is accordingly convicted under Section 135 read with Section 150 of the Electricity Act, 2003</strong>, and is to be heard on the quantum of sentence.</p>"),
      sig_intro=f"An owner-as-abettor conviction where the actual user ({user}) absconded and was never tried. Five propositions stand out:",
      significance=significance, cites=CITES_ABET)
    build(c, out)

# -------- 019 Devanand (meter bypass; 4 disconnected meters; user Jagdish) --------
abet(case_no="019", title="State v. Devanand", sc="SC No.&nbsp;262/2020", fir="FIR No.&nbsp;198/2019", ps="PS Gandhi Nagar",
 doj="13 March 2026", dooff="4 July 2019 at about 16.20 hours",
 owner="State (BSES Yamuna Power Ltd.) <em>v.</em> Devanand S/o Sher Singh, R/o H. No.&nbsp;9/5323, Old Seelampur, Gandhi Nagar, Delhi&#8209;110031 (registered consumer/owner of the inspected premises, H. No.&nbsp;9/5512, 2nd Floor, Old Seelampur)",
 accused_name="Devanand", user="Jagdish", team_head="Sh. Anil Kumar (Assistant Manager)",
 mode_short="by bypassing the metering system &mdash; the premises&rsquo; four installed meters standing with their outgoing supply disconnected while the second-floor load ran directly through a service cable joined with an illegal wire",
 mode_full="Four electricity meters were installed at the premises but their outgoing supply stood disconnected, and the second-floor supply was found running directly through a service cable joined with an illegal wire; the user/tenant Jagdish did not allow the inspection team to check the (locked) meters.",
 section_label="a bypass of the metering system amounting to a dishonest abstraction under Section 135(1)",
 load="3.692", bill="3,15,653", noc=False,
 extra_sig=("A meter-bypass with disconnected meters is direct theft.",
   """That four meters stood installed did not help the owner where their outgoing supply was disconnected and the load ran through a service-cable tap &mdash; the presence of dead meters underscored, rather than excused, the unauthorised abstraction."""),
 out="case_019.html")

# -------- 021 Archna Shukla (LV-mains tap; user Amit; NOC) --------
abet(case_no="021", title="State v. Archna Shukla", sc="SC No.&nbsp;1151/2023", fir="FIR No.&nbsp;349/2020", ps="PS Sonia Vihar",
 doj="11 April 2026", dooff="19 October 2020 at about 8.34 a.m.",
 owner="State (BSES Yamuna Power Ltd.) <em>v.</em> Archna Shukla W/o Hardesh Shukla, R/o Khasra No.&nbsp;48-51, Ground Floor, Ambey Enclave, Gali No.&nbsp;4, Chauhan Patti, Delhi (owner of the inspected first-floor premises)",
 accused_name="Archna Shukla", user="Amit", team_head="Sh. Mriganka Ghosh (DGM), with a five-member team",
 mode_short="through a two-core black aluminium cable tapped directly from the licensee&rsquo;s LV mains, the premises having no meter",
 mode_full="No electricity meter was installed at the inspected premises; one Amit, who claimed to be a tenant of the accused, was found drawing supply through a two-core black aluminium cable connected from the BSES YPL LV Mains.",
 section_label="a clause (a) connection with the licensee&rsquo;s mains",
 load="3.467", bill="56,506", noc=True, out="case_021.html")

# -------- 023 Nikhat (distribution-box tap; user Naseem Bano; videography obstructed by Farhad; NOC) --------
abet(case_no="023", title="State v. Nikhat", sc="SC No.&nbsp;1069/2023", fir="FIR No.&nbsp;210/2022", ps="PS Seelampur",
 doj="6 April 2026", dooff="20 December 2021 at about 8.00 a.m.",
 owner="State (BSES Yamuna Power Ltd.) <em>v.</em> Nikhat W/o Late Sayed Fasihuddin, R/o H. No.&nbsp;6A/26 (New No.&nbsp;760), Khasra No.&nbsp;234, Main Road, Chauhan Bangar, Delhi&#8209;110053 (owner of the inspected third-floor premises)",
 accused_name="Nikhat", user="Naseem Bano", team_head="Sh. R.B. Yadav (Assistant Manager)",
 mode_short="through a single-core black-and-red wire joined to a yellow cable tapped from the licensee&rsquo;s distribution box, the premises having no meter",
 mode_full="No electricity meter was installed at the inspected premises; one lady, Naseem Bano, who claimed to be a tenant of the accused, was found drawing supply through a single-core black-and-red wire joined to a yellow cable connected from the Distribution Box of BSES YPL. Complete videography could not be captured because of resistance created by one Farhad present at the spot; the illegal wire was nonetheless removed and seized.",
 section_label="a clause (a) connection with the licensee&rsquo;s distribution box",
 load="2.740", bill="50,033", noc=True,
 extra_sig=("Third-party obstruction of the videography does not defeat the case.",
   """That a person at the spot (Farhad) prevented complete videography did not weaken the prosecution, the seizure and the officials&rsquo; consistent testimony independently proving the tap."""),
 out="case_023.html")
