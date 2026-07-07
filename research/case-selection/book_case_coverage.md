# Coverage check — cases cited in the two commentary books vs. the top 80

The two uploaded PDFs are scanned pages of a bare-act **commentary**
("Electricity Laws of India"), covering **§§126–157** (assessment, appeal,
theft/offences, civil-court bar, compounding, Special Courts) — squarely our
scope. They were image-only, so both were **OCR'd** (tesseract, 300 dpi;
48 + 20 pages; full text saved in `ocr/`). Case citations sit mostly in
footnotes as `Party v. Party, A.I.R. YYYY <Court> <page>`.

**Caveat:** extraction is best-effort — OCR mangles some names and wraps
footnotes across lines, so this is a high-confidence subset (~24 distinct
judgments), not guaranteed-exhaustive. Matching to the pool is by party
surname with court/date disambiguation; every match was eyeballed.

## Where the book's cases land

| Bucket | Count | Cases |
|---|--:|---|
| **In top 80** | **3** | Accounts Officer, Jharkhand SEB v. **Anwar Ali** (#10, SC); UPPCL v. **Anis Ahmad** (#1); Kerala SEB v. **Thomas Joseph** (#22) |
| In 81–200 | 1 | M/s Jindal Resources v. Exec. Engr WESCO (#200) |
| In pool but >200 | 5 | Harvinder Motors v. BSES Rajdhani; K. Dominic v. AEE (TNEB); J. Madhavan v. Supt. Engineer; Himadri Steel v. Jharkhand Urja Vikas Nigam; (Sri Kanaka Durga — weak) |
| Not harvested | ~15 | Bihar SEB v. Snehlata Gupta (Pat); N.B. Hi-Tech Industries v. TNEB (Mad); Ayyanar v. SEB (JCR); **Ashok Kumar v. State of U.P.** (2008 All); Deoghar v. Jharkhand SEB; Rishi Cement v. Jharkhand SEB; Ganpat Sheth v. Matariya Textiles; **Jiyajeerao Cotton Mills v. M.P. Elec. Board** (AIR 1989 SC 788); Kawsar Ali v. State of W.B. (Cal); Kulwinder Singh v. SDM Patiala (P&H); M. Paramaivam v. UOI (Ker); FEDCO v. Commr-cum-Secy, Odisha; Shree Shyam Ispat v. Assam Power (Gau); Ramasubbu Ginning v. Supt. Engineer (Mad); Vijay Shankar Singh v. State of U.P.; Sri Rice Mill, Baheri v. Madhyanchal VVN; Devabhai Memabhai Myatra (Guj) |

**So only 3 of the book's ~24 cited judgments are in the current top 80** — and
two of those (Anis Ahmad, Thomas Joseph) are SC landmarks already known. The
book is overwhelmingly **new material**: mostly older AIR-reported High Court
cases (Pat/Cal/Mad/Ori/Gau/P&H/Guj/Jhar) that a relevance+citation IK search
never surfaces because they are lightly cited on Indian Kanoon and pre-date the
recent case flow.

## Two findings

1. **The book is a high-value new seed.** ~20 of its cases are outside the top
   80 (15 not even harvested). As agreed, tag all of them `expert-cited`
   (a scoring bonus) and fetch metadata so they compete in the re-rank. Note one
   apex case worth force-checking: **Jiyajeerao Cotton Mills v. M.P. Electricity
   Board (AIR 1989 SC 788)** — an old SC authority the search missed entirely.

2. **A real pipeline bug the book exposed — topicality filter too narrow.**
   *Harvinder Motors v. BSES Rajdhani Power* (Delhi, **citedby = 59**) sits in the
   pool but was flagged `topical=False` and dropped from ranking, because the
   filter's electricity-term list didn't include bare "power" / "BSES" /
   "vidyut" / discom names. A citedby-59 case should be top-5 among HC — it was
   silently excluded. **Fix: broaden the electricity-term list and re-run the
   topicality pass before the final re-rank** (this likely rescues several other
   wrongly-excluded cases too).

## Next (deferred, per your "hold your horses")
Fold these book cases + the three-document cited cases into the pool as
`expert-cited`, add the **§56(2) limitation** taxonomy node (accepted), fix the
topicality filter, then re-rank and re-cut the ~80.
