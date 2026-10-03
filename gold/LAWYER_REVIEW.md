# Statute Street — Lawyer review pack (gold key v0.3)

*Internal test material for the Hack-Nation Challenge 02 build. Not legal advice. Prepared 2026-10-04 from gold/rules/all.json (every row still verifier: AI-draft). 15 rows: 5 weakest-confidence rules, the 5 change-test rules (CA AB 325, Hoboken ban, Jersey City ban, NJ FAIR Act, MA S.2983), and the MA ballot question plus 4 random others.*

## How to review (4 points per row)

For each row, mark ✅ (correct), ❌ (wrong — write the correct value) or ❓ (cannot confirm) and answer:

1. **Citation right?** — Is this the operative section of the law named?
2. **Key value right?** — Is the headline number / formula / prohibition stated correctly?
3. **Date right?** — Is the effective date correct (null = long-standing statute with no stated effective date)?
4. **Status right?** — As of **2026-10-01**: in_force / not_yet_effective / pending / failed?

Open the official source link before answering; where the source is a corpus copy the URL is the organisers' original. Return the file (or a photo of the printed table) to Hamza; decisions are then logged in `gold/adjudication_log.csv`.

## A. Weakest confidence (5)

| # | Rule (gold_id) | Citation | Key value | Effective date | Status | Official source | Check (✅/❌/❓ + note) |
|---|---|---|---|---|---|---|---|
| 1 | **BOS-SCRN-02**<br>Boston Fair Chance Tenant Selection Policy (DND-funded and IDP housing) – Feb 2017 (conf 0.50) | Boston Fair Chance Tenant Selection Policy (DND, February 2017) – policy, not ordinance | no blanket criminal-history denials; 5-year look-back (city-funded/IDP housing) | 2017-02 | in_force | [https://drive.google.com/file/d/1j4U3fDtmnYuwcUWhx5BMUcXc1bnKT8Ku/view?usp=sharing](https://drive.google.com/file/d/1j4U3fDtmnYuwcUWhx5BMUcXc1bnKT8Ku/view?usp=sharing) |  |
| 2 | **MA-SCRN-02**<br>CORI in housing – 803 CMR 5.00 (Criminal Offender Record Information: housing) (conf 0.50) | 803 CMR 5.00 | regulated access to and use of CORI by housing providers | null | in_force | [https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download](https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download) |  |
| 3 | **SA-ALG-01**<br>Prohibition on anticompetitive rent-setting software – Santa Ana Ordinance No. NS-3090 (2026) (conf 0.50) | Santa Ana Ordinance No. NS-3090 (code section not verified) | ban on sale/use of algorithmic rent-setting software | null | in_force | [https://www.publicceo.com/2026/02/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/](https://www.publicceo.com/2026/02/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/) |  |
| 4 | **BERK-FEE-01**<br>Tenant screening fee disclosure and renewal-fee ban – BMC ch. 13.78 (conf 0.60) | Berkeley Mun. Code §§ 13.78.010, 13.78.016 | disclosure of state fee cap required; no non-refundable renewal/roommate fees | null | in_force | [https://rentboard.berkeleyca.gov/laws-regulations/city-berkeley-ordinances-affecting-rental-properties/tenant-screening-and](https://rentboard.berkeleyca.gov/laws-regulations/city-berkeley-ordinances-affecting-rental-properties/tenant-screening-and) |  |
| 5 | **BOS-JUST-01**<br>Housing Stability Notification Act (notice of tenants' rights on termination) – Boston Ordinance (2020) [notice-only] (conf 0.60) | Boston Code of Ordinances ch. 9, § 9-20 (Housing Stability Notification Act) | notice-of-rights duty on termination (no just-cause requirement) | 2020-11-06 | in_force | [https://www.boston.gov/housing-stability-notification-act](https://www.boston.gov/housing-stability-notification-act) |  |

## B. Change-test rules T1–T4 (5)

| # | Rule (gold_id) | Citation | Key value | Effective date | Status | Official source | Check (✅/❌/❓ + note) |
|---|---|---|---|---|---|---|---|
| 6 | **CA-ALG-01**<br>Common pricing algorithm prohibition (AB 325, Cartwright Act) – Cal. Bus. & Prof. Code § 16729 (conf 0.85) | Cal. Bus. & Prof. Code § 16729 (added by AB 325, Stats. 2025 ch. 338) | prohibition on use/distribution of common pricing algorithms in restraint of trade | 2026-01-01 | in_force | [https://www.clearygottlieb.com/news-and-insights/publication-listing/californias-antitrust-law-amendments-kick-in-targeting-algorithmic-pricing](https://www.clearygottlieb.com/news-and-insights/publication-listing/californias-antitrust-law-amendments-kick-in-targeting-algorithmic-pricing) |  |
| 7 | **HOB-ALG-01**<br>Prohibition on price fixing using algorithmic pricing – Hoboken Code ch. 158 (Ord. B-781) (conf 0.75) | Hoboken Code ch. 158 (Ord. No. B-781, adopted 2025-07-09) | ban on algorithmic price fixing using nonpublic competitor information | 2025-07 | in_force | [https://ecode360.com/46833413](https://ecode360.com/46833413) |  |
| 8 | **JC-ALG-01**<br>Ban on algorithmic rent-setting using nonpublic competitor data – Jersey City Code § 218-12 (Ord. 25-057) (conf 0.60) | Jersey City Code § 218-12 (Ord. 25-057) | ban on landlord use of algorithmic rent-setting with nonpublic competitor data | 2025-06 | in_force | [https://hudsoncountyview.com/jersey-city-council-approves-realpage-ban-and-increasing-benefits-for-laborers/](https://hudsoncountyview.com/jersey-city-council-approves-realpage-ban-and-increasing-benefits-for-laborers/) |  |
| 9 | **NJ-ALG-01**<br>Forbidding the Algorithmic Inflation of Rent (FAIR) Act – P.L.2026, c.43 (conf 0.90) | N.J.S.A. 56:9-20 to 56:9-26 (P.L.2026, c.43) | ban on use of algorithmic rent-setting coordinators (effective 2027-07-01) | 2027-07-01 | not_yet_effective | [https://pub.njleg.state.nj.us/Bills/2026/AL26/43_.HTM](https://pub.njleg.state.nj.us/Bills/2026/AL26/43_.HTM) |  |
| 10 | **MA-ALG-P1**<br>S.2983 – An Act prohibiting algorithmic rent setting (pending) (conf 0.90) | Mass. S.2983 (194th General Court) | — | null | pending | [https://malegislature.gov/Bills/194/S2983](https://malegislature.gov/Bills/194/S2983) |  |

## C. T5 ballot question + 4 random others (seed 20261004)

| # | Rule (gold_id) | Citation | Key value | Effective date | Status | Official source | Check (✅/❌/❓ + note) |
|---|---|---|---|---|---|---|---|
| 11 | **MA-RENT-P1**<br>Rent-control ballot initiative IP 25-21 (struck by the SJC 2026-06-23) (conf 0.70) | Initiative Petition 25-21 (Mass. 2026); Cella v. Attorney General (SJC, decided 2026-06-23) | — | null | failed | [https://www.wbur.org/news/2026/06/23/massachusetts-high-court-rent-control-ballot-question-struck](https://www.wbur.org/news/2026/06/23/massachusetts-high-court-rent-control-ballot-question-struck) |  |
| 12 | **CA-SCRN-01**<br>FEHA source-of-income protection (incl. Section 8 vouchers) – Cal. Gov. Code § 12955 (conf 0.80) | Cal. Gov. Code § 12955(a), (p) | source of income (incl. Section 8 vouchers) is a protected characteristic | 2020-01-01 | in_force | [https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=12955](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=12955) |  |
| 13 | **BERK-RENT-01**<br>Rent Stabilization Ordinance annual general adjustment – BMC § 13.76.110 (conf 0.85) | Berkeley Mun. Code § 13.76.110(A) | 1.0% for 2026 (65% of CPI; 5% cap) | null | in_force | [https://rentboard.berkeleyca.gov/sites/default/files/documents/AGA%20Public%20Notice.pdf](https://rentboard.berkeleyca.gov/sites/default/files/documents/AGA%20Public%20Notice.pdf) |  |
| 14 | **LA-JUST-02**<br>RSO legal reasons for eviction and relocation assistance – LAMC § 151.09 (conf 0.75) | L.A. Mun. Code § 151.09 | RSO just-cause grounds + relocation assistance | null | in_force | [https://housing.lacity.gov/residents/rso-overview](https://housing.lacity.gov/residents/rso-overview) |  |
| 15 | **MA-FEE-02**<br>Broker fee reform – M.G.L. c.112, § 87DDD½ (as amended by St. 2025, c.9, § 43) (conf 0.85) | M.G.L. c.112, § 87DDD½ (St. 2025, c.9, § 43, eff. 2025-08-01) | broker fee payable only by the party who engaged the broker | 2025-08-01 | in_force | [https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVI/Chapter112/Section87DDD%201~2](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVI/Chapter112/Section87DDD%201~2) |  |

---
Reviewer: ______________________  Date: __________  Signature: ______________________
