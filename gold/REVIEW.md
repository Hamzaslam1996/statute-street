# Review pack for Hamza — independent gold key (v0.3, 2026-10-04)

Internal test material, not legal advice. Every row is still `verifier: AI-draft`; set it to your name as you clear each row. Rows sorted **weakest confidence first**. Decided items are marked in `open_questions.md` and `adjudication_log.csv`; 94 log rows with "no change"/"keep" recommendations await a blanket OK.

## 1. All independent rows, weakest first

| conf | gold_id | jurisdiction | category | status | key_value | citation | effective_date | quote_verified | what to check | primary source |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.50 | BOS-SCRN-02 | Boston, MA | screening_restrictions | in_force | no blanket criminal-history denials; 5-year look-back (city-funded/IDP | Boston Fair Chance Tenant Selection Policy (DND, February 20 | 2017-02 | True | Confirm D010 is the current DND policy; city-funded scope | https://drive.google.com/file/d/1j4U3fDtmnYuwcUWhx5BMUcXc1bnKT8Ku/view?usp=sharing |
| 0.50 | MA-SCRN-02 | MA | screening_restrictions | in_force | regulated access to and use of CORI by housing providers | 803 CMR 5.00 | — | False | Obtain 803 CMR 5.00 text (mass.gov 403) for a span | https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download |
| 0.50 | SA-ALG-01 | Santa Ana, CA | algorithmic_rent_setting | in_force | ban on sale/use of algorithmic rent-setting software | Santa Ana Ordinance No. NS-3090 (code section not verified) | — | False | Retrieve NS-3090 text; confirm adoption 2026-03-03 / effective 2026-04-02 | https://www.publicceo.com/2026/02/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/ |
| 0.60 | BERK-FEE-01 | Berkeley, CA | application_screening_fees | in_force | disclosure of state fee cap required; no non-refundable renewal/roomma | Berkeley Mun. Code §§ 13.78.010, 13.78.016 | — | True | Categorisation (Q6); BMC 13.78 date | https://rentboard.berkeleyca.gov/laws-regulations/city-berkeley-ordinances-affecting-rental-properties/tenant-screening-and |
| 0.60 | BOS-JUST-01 | Boston, MA | just_cause_eviction | in_force | notice-of-rights duty on termination (no just-cause requirement) | Boston Code of Ordinances ch. 9, § 9-20 (Housing Stability N | 2020-11-06 | True | Code section (ch.9 §9-20 vs ch.10 §10-14) unverified | https://www.boston.gov/housing-stability-notification-act |
| 0.60 | BOS-SCRN-01 | Boston, MA | screening_restrictions | in_force | rental assistance / Section 8 voucher use is a protected class locally | Boston Fair Housing Commission regulations (Boston Code ch.  | — | True | Verify Boston Fair Housing Ordinance section (ch. 10 § 10-3?) and regulation text | https://www.boston.gov/departments/fair-housing-and-equity/boston-fair-housing-regulations |
| 0.60 | CAM-JUST-01 | Cambridge, MA | just_cause_eviction | in_force | notice-of-rights duty at tenancy start and termination (no just-cause  | Cambridge Mun. Code ch. 8.71 | — | True | ch. 8.71 effective date | https://www.cambridgema.gov/tenantrights |
| 0.60 | HOB-SCRN-00 | Hoboken, NJ | screening_restrictions | n/a | — | none (N.J.S.A. 46:8-52 et seq.; 10:5-12 govern) | — | False | Spot-check span and citation | https://ecode360.com/15252438 |
| 0.60 | JC-ALG-01 | Jersey City, NJ | algorithmic_rent_setting | in_force | ban on landlord use of algorithmic rent-setting with nonpublic competi | Jersey City Code § 218-12 (Ord. 25-057) | 2025-06 | False | Read civicweb PDF: § 218-12 text, penalties, effective date | https://hudsoncountyview.com/jersey-city-council-approves-realpage-ban-and-increasing-benefits-for-laborers/ |
| 0.60 | JC-SCRN-00 | Jersey City, NJ | screening_restrictions | n/a | — | none (N.J.S.A. 46:8-52 et seq.; 10:5-12 govern) | — | False | Spot-check span and citation | https://www.jerseycitynj.gov/landlordtenant |
| 0.60 | LA-ALG-00 | Los Angeles, CA | algorithmic_rent_setting | n/a | — | L.A. City Council motion CF 24-1031 (2024-09-03) – no ordina | — | True | Confirm no LA ordinance enacted by 2026-10-01 | https://cityclerk.lacity.org/onlinedocs/2024/24-1031_misc_9-03-24.pdf |
| 0.60 | SA-SCRN-00 | Santa Ana, CA | screening_restrictions | n/a | — | none (state Gov. Code § 12955 governs) | — | False | Spot-check span and citation | https://santa-ana.gov/departments/rent-stabilization |
| 0.60 | SD-SCRN-01 | San Diego, CA | screening_restrictions | in_force | source of income (incl. vouchers) protected | San Diego Mun. Code § 98.0803 (O-20986 N.S.) | 2019-08-01 | False | Fetch official SDMC Div. 8 text for a span; operative 2019-08-01 vs code history 2018-10-18 | https://www.nhlp.org/wp-content/uploads/SD-Municipal-Code-SOI-Article-08-Housing-1.pdf |
| 0.60 | SF-SCRN-01 | San Francisco, CA | screening_restrictions | in_force | criminal-history limits for affordable housing providers | S.F. Police Code art. 49 (§§ 4901 et seq.) | — | True | Confirm Police Code art. 49 housing scope and effective date | https://sf-hrc.org/fair-chance-ordinance |
| 0.65 | LA-SCRN-01 | Los Angeles, CA | screening_restrictions | in_force | source of income (incl. housing vouchers) protected | L.A. Mun. Code § 45.67 | 2020-01-01 | True | Confirm enacting ordinance and 2020-01-01 date | https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-322208 |
| 0.65 | SA-DEP-00 | Santa Ana, CA | security_deposits | n/a | — | none (state Civ. Code § 1950.5 governs) | — | False | Spot-check span and citation | https://santa-ana.gov/departments/rent-stabilization |
| 0.65 | SA-FEE-00 | Santa Ana, CA | application_screening_fees | n/a | — | none (state Civ. Code § 1950.6 governs) | — | False | Spot-check span and citation | https://santa-ana.gov/departments/rent-stabilization |
| 0.70 | BERK-ALG-01 | Berkeley, CA | algorithmic_rent_setting | in_force | ban on sale/use of coordinated pricing algorithms | Berkeley Mun. Code § 13.63.030 (Ord. 7992-NS) | 2026-01-01 | True | Decided 2026-01-01; conflict_flag kept | https://berkeleyca.gov/sites/default/files/documents/2025-12-02%20Item%2001%20Ordinance%207992.pdf |
| 0.70 | CAM-ALG-00 | Cambridge, MA | algorithmic_rent_setting | n/a | — | none (policy order June 2026; MA bills pending) | — | True | Negative vs pending (Q10) | https://www.cambridgeday.com/?p=158097 |
| 0.70 | CAM-SCRN-01 | Cambridge, MA | screening_restrictions | in_force | source of income (incl. Section 8) protected locally | Cambridge Mun. Code ch. 14.04 | — | True | Spot-check span and citation | https://www.cambridgema.gov/departments/humanrightscommission |
| 0.70 | HOB-DEP-00 | Hoboken, NJ | security_deposits | n/a | — | none (N.J.S.A. 46:8-21.2 governs) | — | False | Spot-check span and citation | https://ecode360.com/15252438 |
| 0.70 | HOB-FEE-00 | Hoboken, NJ | application_screening_fees | n/a | — | none (N.J.S.A. 46:8-18.1 governs) | — | False | Spot-check span and citation | https://ecode360.com/15252438 |
| 0.70 | HOB-JUST-00 | Hoboken, NJ | just_cause_eviction | n/a | — | none (N.J.S.A. 2A:18-61.1 governs) | — | False | Spot-check span and citation | https://ecode360.com/15252438 |
| 0.70 | HOB-RENT-02 | Hoboken, NJ | rent_increase_limits | in_force | disclosures required for renewal increases > 10% (not a cap) | Hoboken Code ch. 158, art. I (Ord. No. B-750, adopted 2025-0 | 2025-04 | True | Confirm B-750 effective date; categorisation accepted | https://ecode360.com/46833413 |
| 0.70 | JC-DEP-00 | Jersey City, NJ | security_deposits | n/a | — | none (N.J.S.A. 46:8-21.2 governs) | — | False | Spot-check span and citation | https://www.jerseycitynj.gov/landlordtenant |
| 0.70 | JC-FEE-00 | Jersey City, NJ | application_screening_fees | n/a | — | none (N.J.S.A. 46:8-18.1 governs) | — | False | Spot-check span and citation | https://www.jerseycitynj.gov/landlordtenant |
| 0.70 | JC-JUST-00 | Jersey City, NJ | just_cause_eviction | n/a | — | none (N.J.S.A. 2A:18-61.1 governs) | — | False | Spot-check span and citation | https://www.jerseycitynj.gov/landlordtenant |
| 0.70 | JC-RENT-01 | Jersey City, NJ | rent_increase_limits | in_force | lesser of 4% or CPI | Jersey City Code § 260-3 | — | True | Read ch. 260 exemptions beyond 1–4 units | https://www.jerseycitynj.gov/landlordtenant |
| 0.70 | LA-DEP-01 | Los Angeles, CA | security_deposits | in_force | annual interest on deposits (RSO units) | L.A. Mun. Code § 151.06.02 | — | True | Confirm LAMC 151.06.02 text (Q8) | https://housing.lacity.gov/residents/rso-overview |
| 0.70 | LA-FEE-00 | Los Angeles, CA | application_screening_fees | n/a | — | none (state Civ. Code § 1950.6 governs) | — | False | Spot-check span and citation | https://housing.lacity.gov/residents/rso-overview |
| 0.70 | MA-RENT-P1 | MA | rent_increase_limits | failed | — | Initiative Petition 25-21 (Mass. 2026); Cella v. Attorney Ge | — | True | Add SJC citation from a primary source | https://www.wbur.org/news/2026/06/23/massachusetts-high-court-rent-control-ballot-question-struck |
| 0.70 | NWK-DEP-00 | Newark, NJ | security_deposits | n/a | — | none (N.J.S.A. 46:8-21.2 governs) | — | False | Spot-check span and citation | https://ecode360.com/36623772 |
| 0.70 | NWK-FEE-00 | Newark, NJ | application_screening_fees | n/a | — | none (N.J.S.A. 46:8-18.1 governs) | — | False | Spot-check span and citation | https://ecode360.com/36623772 |
| 0.70 | NWK-JUST-00 | Newark, NJ | just_cause_eviction | n/a | — | none (N.J.S.A. 2A:18-61.1 governs) | — | False | Spot-check span and citation | https://ecode360.com/36623772 |
| 0.70 | NWK-SCRN-01 | Newark, NJ | screening_restrictions | in_force | criminal-record inquiry limited to post-qualification stage; individua | Newark Code § 2:31-2 (Ord. 6 PSF-B, 4-15-2015) | — | True | Effective date of Ord. 6 PSF-B (2015) | https://ecode360.com/36642000 |
| 0.70 | SD-DEP-00 | San Diego, CA | security_deposits | n/a | — | none (state Civ. Code § 1950.5 governs) | — | False | Spot-check span and citation | https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf |
| 0.70 | SD-FEE-00 | San Diego, CA | application_screening_fees | n/a | — | none (state Civ. Code § 1950.6 governs) | — | False | Spot-check span and citation | https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf |
| 0.70 | SF-FEE-00 | San Francisco, CA | application_screening_fees | n/a | — | none (state Civ. Code § 1950.6 governs) | — | False | Spot-check span and citation | https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit |
| 0.75 | BERK-DEP-01 | Berkeley, CA | security_deposits | in_force | annual interest on deposits (covered units) | Berkeley Mun. Code § 13.76.070 | — | True | Confirm BMC 13.76.070 (Q8) | https://rentboard.berkeleyca.gov/rights-responsibilities/security-deposits |
| 0.75 | BERK-SCRN-01 | Berkeley, CA | screening_restrictions | in_force | ban on criminal-history inquiry and use in housing decisions | Berkeley Mun. Code § 13.106.040 (Ord. 7692-NS) | 2020-04 | True | Decided 2020-04; adoption 2020-04-14 | https://rentboard.berkeleyca.gov/Fair_Chance |
| 0.75 | BOS-ALG-00 | Boston, MA | algorithmic_rent_setting | n/a | — | none (MA bills S.2983/H.5222 pending) | — | False | Spot-check span and citation | https://malegislature.gov/Bills/194/S2983 |
| 0.75 | BOS-DEP-00 | Boston, MA | security_deposits | n/a | — | none (M.G.L. c.186 § 15B governs) | — | False | Spot-check span and citation | https://www.boston.gov/housing-stability-notification-act |
| 0.75 | BOS-FEE-00 | Boston, MA | application_screening_fees | n/a | — | none (M.G.L. c.186 § 15B governs) | — | False | Spot-check span and citation | https://www.boston.gov/housing-stability-notification-act |
| 0.75 | CAM-DEP-00 | Cambridge, MA | security_deposits | n/a | — | none (M.G.L. c.186 § 15B governs) | — | False | Spot-check span and citation | https://www.cambridgema.gov/tenantrights |
| 0.75 | CAM-FEE-00 | Cambridge, MA | application_screening_fees | n/a | — | none (M.G.L. c.186 § 15B governs) | — | False | Spot-check span and citation | https://www.cambridgema.gov/tenantrights |
| 0.75 | HOB-ALG-01 | Hoboken, NJ | algorithmic_rent_setting | in_force | ban on algorithmic price fixing using nonpublic competitor information | Hoboken Code ch. 158 (Ord. No. B-781, adopted 2025-07-09) | 2025-07 | True | Decided 2025-07; adoption 2025-07-09 | https://ecode360.com/46833413 |
| 0.75 | LA-JUST-02 | Los Angeles, CA | just_cause_eviction | in_force | RSO just-cause grounds + relocation assistance | L.A. Mun. Code § 151.09 | — | True | Merge with LA-JUST-01? (Q9) | https://housing.lacity.gov/residents/rso-overview |
| 0.75 | LA-RENT-01 | Los Angeles, CA | rent_increase_limits | in_force | 3% (Jul 2025–Jun 2026); from Jul 2026 formula = 90% of CPI, floor 1%,  | L.A. Mun. Code § 151.06 (as amended by Ord. No. 188795) | 2026-02-02 | True | Formula date (Q2); 2026-27 % on an official page | https://housing.lacity.gov/residents/rso-overview |
| 0.75 | NJ-RENT-00 | NJ | rent_increase_limits | n/a | — | N.J.S.A. 2A:18-61.1(f) (no statewide cap) | — | True | Judges may treat unconscionability as a rule | https://law.justia.com/codes/new-jersey/title-2a/section-2a-18-61-1/ |
| 0.75 | NJ-SCRN-02 | NJ | screening_restrictions | in_force | source of lawful income (incl. vouchers) is a protected category | N.J.S.A. 10:5-12(g)(1) | — | True | Spot-check span and citation | https://law.justia.com/codes/new-jersey/title-10/section-10-5-12/ |
| 0.75 | NWK-ALG-00 | Newark, NJ | algorithmic_rent_setting | n/a | — | none (NJ FAIR Act P.L.2026 c.43 from 2027-07-01) | — | False | Spot-check span and citation | https://www.morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws |
| 0.75 | SF-DEP-01 | San Francisco, CA | security_deposits | in_force | 4.2% annual interest (2026-03-01 to 2027-02-28) | S.F. Admin. Code ch. 49 (§ 49.2) | — | True | Confirm Admin. Code ch. 49 cite (Q8) | https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit |
| 0.80 | BOS-RENT-P1 | Boston, MA | rent_increase_limits | failed | — | Mass. H.3744 (193rd General Court) – study order H.5035 (202 | — | True | failed vs pending (Q11) | https://malegislature.gov/Bills/193/H3744 |
| 0.80 | CA-SCRN-01 | CA | screening_restrictions | in_force | source of income (incl. Section 8 vouchers) is a protected characteris | Cal. Gov. Code § 12955(a), (p) | 2020-01-01 | True | Confirm SB 329 enactment date | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=12955 |
| 0.80 | HOB-RENT-01 | Hoboken, NJ | rent_increase_limits | in_force | lesser of 5% or CPI per 12 months | Hoboken Code § 155-5 | — | True | Confirm no owner-occupancy exemption | https://ecode360.com/15252470 |
| 0.80 | MA-FEE-01 | MA | application_screening_fees | in_force | $0 – landlords may not charge application fees | M.G.L. c.186, § 15B(1)(b) | — | True | Spot-check span and citation | https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B |
| 0.80 | NJ-JUST-01 | NJ | just_cause_eviction | in_force | statutory good cause required for removal | N.J.S.A. 2A:18-61.1 | — | True | Owner-occupied wording | https://law.justia.com/codes/new-jersey/title-2a/section-2a-18-61-1/ |
| 0.80 | NWK-RENT-01 | Newark, NJ | rent_increase_limits | in_force | CPI change, capped at 4% per 12 months | Newark Code § 19:2-3.1 (Ord. 6 PSF-A(S), 9-5-2017; amended 9 | — | True | Confirm no small-building exemption | https://ecode360.com/36623772 |
| 0.80 | SA-JUST-01 | Santa Ana, CA | just_cause_eviction | in_force | just cause after 30 days; 3 months relocation for no-fault | Santa Ana Mun. Code (Just Cause Eviction Ordinance, 2021) | 2021-11-19 | True | Ordinance numbers (silver: NS-3012) | https://santa-ana.gov/santa-ana-city-council-adopts-rent-stabilization-and-just-cause-eviction-ordinances-effective-nov-19 |
| 0.80 | SA-RENT-01 | Santa Ana, CA | rent_increase_limits | in_force | lesser of 3% or 80% of CPI; 2.87% for Sep 2026–Aug 2027 | Santa Ana Mun. Code § 8-1998 et seq. (Rent Stabilization Ord | 2021-11-19 | True | Ordinance numbers (silver: NS-3011) | https://santa-ana.gov/departments/rent-stabilization |
| 0.80 | SD-RENT-00 | San Diego, CA | rent_increase_limits | n/a | — | none (state Civ. Code § 1947.12 governs) | — | True | Spot-check span and citation | https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf |
| 0.85 | BERK-JUST-01 | Berkeley, CA | just_cause_eviction | in_force | enumerated just causes; non-payment eviction only if debt ≥ 1 month FM | Berkeley Mun. Code § 13.76.130 | — | True | Spot-check span and citation | https://rentboard.berkeleyca.gov/laws-regulations/measure-bb-changes-berkeleys-rent-ordinance |
| 0.85 | BERK-RENT-01 | Berkeley, CA | rent_increase_limits | in_force | 1.0% for 2026 (65% of CPI; 5% cap) | Berkeley Mun. Code § 13.76.110(A) | — | True | Spot-check span and citation | https://rentboard.berkeleyca.gov/sites/default/files/documents/AGA%20Public%20Notice.pdf |
| 0.85 | CA-ALG-01 | CA | algorithmic_rent_setting | in_force | prohibition on use/distribution of common pricing algorithms in restra | Cal. Bus. & Prof. Code § 16729 (added by AB 325, Stats. 2025 | 2026-01-01 | True | Confirm no urgency clause | https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB325 |
| 0.85 | CA-FEE-01 | CA | application_screening_fees | in_force | $30 (1997 base) adjusted annually by CPI from 1998-01-01; no single of | Cal. Civ. Code § 1950.6 | — | True | Dollar figure policy (Q4) | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1950.6 |
| 0.85 | LA-JUST-01 | Los Angeles, CA | just_cause_eviction | in_force | just cause required after 6 months or lease expiry; relocation assista | L.A. Mun. Code § 165.03 (Art. 5.3, Ch. XVI; Ord. No. 187737) | 2023-01-27 | True | Spot-check span and citation | https://housing.lacity.gov/residents/just-cause-for-eviction-ordinance-jco |
| 0.85 | MA-FEE-02 | MA | application_screening_fees | in_force | broker fee payable only by the party who engaged the broker | M.G.L. c.112, § 87DDD½ (St. 2025, c.9, § 43, eff. 2025-08-01 | 2025-08-01 | True | Category fit (broker fee vs application fee) | https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVI/Chapter112/Section87DDD%201~2 |
| 0.85 | MA-JUST-00 | MA | just_cause_eviction | n/a | — | M.G.L. c.186, §§ 11, 12 (notice to quit; no just-cause requi | — | True | Spot-check span and citation | https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section12 |
| 0.85 | MA-SCRN-01 | MA | screening_restrictions | in_force | recipients of public assistance / housing subsidies are protected | M.G.L. c.151B, § 4(10) | — | True | Spot-check span and citation | https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXXI/Chapter151B/Section4 |
| 0.85 | NJ-DEP-01 | NJ | security_deposits | in_force | 1.5 months' rent | N.J.S.A. 46:8-21.2 | — | True | Spot-check span and citation | https://law.justia.com/codes/new-jersey/title-46/section-46-8-21-2/ |
| 0.85 | NJ-FEE-01 | NJ | application_screening_fees | in_force | $50 (CPI-adjusted from January 2027) | N.J.S.A. 46:8-18.1 (P.L.2025, c.405, § 1) | 2026-05-01 | True | Spot-check span and citation | https://pub.njleg.gov/bills/2024/PL25/405_.HTM |
| 0.85 | NJ-SCRN-01 | NJ | screening_restrictions | in_force | no criminal-record inquiry before conditional offer; individualised as | N.J.S.A. 46:8-55 (P.L.2021, c.110) | 2022-01-01 | True | Spot-check span and citation | https://pub.njleg.gov/bills/2020/PL21/110_.HTM |
| 0.85 | SD-ALG-01 | San Diego, CA | algorithmic_rent_setting | in_force | ban on sale/use of algorithmic rent-setting devices | San Diego Mun. Code § 98.1103 (O-21955 N.S.) | 2025-06-21 | True | Spot-check span and citation | https://gocodebook.com/library/us/ca/san-diego-zoning/division-11-prohibition-of-anti-competitive-automated-rent-price-fixing/98.1103-use-and-sale-of-algorithmic-devices-prohibited |
| 0.85 | SF-ALG-01 | San Francisco, CA | algorithmic_rent_setting | in_force | ban on sale/use of algorithmic rent-setting devices | S.F. Admin. Code § 37.10C | 2024-10-14 | True | enacted_date 2024-09-13 unverified | https://www.sf.gov/news/new-law-prohibits-algorithmic-devices-used-set-rents-san-francisco |
| 0.85 | SF-RENT-01 | San Francisco, CA | rent_increase_limits | in_force | 1.6% (2026-03-01 to 2027-02-28); formula 60% of CPI | S.F. Admin. Code § 37.3(a) | 2026-03-01 | True | Decided 2026-03-01 (rate period) | https://www.sf.gov/news--annual-rent-increase-3126-22827-announced |
| 0.90 | BOS-RENT-00 | Boston, MA | rent_increase_limits | n/a | — | M.G.L. c.40P, § 4; Mass. H.3744 (193rd) – study order | — | True | Spot-check span and citation | https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40P/Section4 |
| 0.90 | CA-DEP-01 | CA | security_deposits | in_force | 1 month's rent (2 months for qualifying small landlords) | Cal. Civ. Code § 1950.5(c) | 2024-07-01 | True | Spot-check span and citation | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1950.5 |
| 0.90 | CA-JUST-01 | CA | just_cause_eviction | in_force | just cause required after 12 months of occupancy; 1 month relocation a | Cal. Civ. Code § 1946.2 | 2020-01-01 | True | Spot-check span and citation | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1946.2 |
| 0.90 | CA-RENT-01 | CA | rent_increase_limits | in_force | lesser of 5% + CPI or 10% per 12 months | Cal. Civ. Code § 1947.12 | 2020-01-01 | True | 2020-01-01 vs operative 2024-04-01 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12 |
| 0.90 | CAM-RENT-00 | Cambridge, MA | rent_increase_limits | n/a | — | M.G.L. c.40P, § 4 | — | True | Spot-check span and citation | https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40P/Section4 |
| 0.90 | MA-ALG-P1 | MA | algorithmic_rent_setting | pending | — | Mass. S.2983 (194th General Court) | — | True | Spot-check span and citation | https://malegislature.gov/Bills/194/S2983 |
| 0.90 | MA-ALG-P2 | MA | algorithmic_rent_setting | pending | — | Mass. H.5222 (194th General Court) | — | True | Spot-check span and citation | https://malegislature.gov/Bills/194/H5222 |
| 0.90 | MA-DEP-01 | MA | security_deposits | in_force | 1 month's rent (security deposit) | M.G.L. c.186, § 15B(1)(b)(iii) | — | True | Spot-check span and citation | https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B |
| 0.90 | NJ-ALG-01 | NJ | algorithmic_rent_setting | not_yet_effective | ban on use of algorithmic rent-setting coordinators (effective 2027-07 | N.J.S.A. 56:9-20 to 56:9-26 (P.L.2026, c.43) | 2027-07-01 | True | Possible preemption of Jersey City and Hoboken algorithmic-pricing ordinances when the FAIR Act takes effect (P.L.2026 c | https://pub.njleg.state.nj.us/Bills/2026/AL26/43_.HTM |
| 0.90 | SD-JUST-01 | San Diego, CA | just_cause_eviction | in_force | just cause required; 2 months relocation (3 for elderly/disabled) | San Diego Mun. Code § 98.0704 (O-21647 N.S.) | 2023-06-24 | True | Spot-check span and citation | https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf |
| 0.90 | SF-JUST-01 | San Francisco, CA | just_cause_eviction | in_force | 17 enumerated just causes | S.F. Admin. Code § 37.9(a) | — | True | Spot-check span and citation | https://sf.gov/information/overview-just-cause-evictions |
| 0.95 | MA-RENT-00 | MA | rent_increase_limits | n/a | — | M.G.L. c.40P, § 4 | — | True | Spot-check span and citation | https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40P/Section4 |

## 2. Open legal questions (decisions)


Each item is framed as a decision. "Scoring consequence" = what changes in the key if you choose each option. All affected rows carry `conflict_flag: true` in `rules/all.json`.

## Q1. Berkeley ch. 13.63 effective date (BERK-ALG-01) — organisers' open question — **DECIDED 2026-10-04: (a) 2026-01-01, conflict_flag kept**
- Evidence: Ord. 7956-NS added ch. 13.63 (adopted 2025-03-25, eff. 2025-04-24). Ord. 7974-NS (adopted 2025-07-08, eff. 2025-08-07) inserted "The provisions of this Chapter shall not take effect until March 1, 2026." Ord. 7992-NS (adopted 2025-12-02; berkeley.municipal.codes: effective **2026-01-01**) re-enacted the chapter; the corpus text (D001) has no delayed-effect clause. Morgan Lewis (Aug 2026): "effective January 2026".
- Options: (a) **2026-01-01** [key as drafted]; (b) 2026-03-01 (organisers' "ordinance text" date); (c) record `2026-01` month-precision.
- Scoring consequence: as-of tests between 2026-01-01 and 2026-02-28 flip between applies / not_yet_effective. No T-test depends on it; the judges' key may use either date.

## Q2. LA RSO new-formula effective date (LA-RENT-01) — organisers' open question
- Evidence: City Clerk CF 23-1134: Ord. 188795 adopted 2025-12-12, Mayor 2025-12-24, published 2025-12-26, "Ordinance effective date: February 2, 2026"; LAHD pages: "Effective February 2, 2026". AAGLA: "effective January 24, 2026".
- Options: (a) **2026-02-02** [key as drafted]; (b) 2026-01-24.
- Scoring consequence: only affects as-of queries in late Jan 2026. Separate point: should `effective_date` for LA-RENT-01 be the formula-ordinance date at all, or null (RSO dates from 1979)?

## Q3. NJ FAIR Act preemption of Jersey City § 218-12 and Hoboken ch. 158 (NJ-ALG-01, JC-ALG-01, HOB-ALG-01) — organisers' open question
- Key as drafted: local bans **apply** now; `conflict_flag=true` on NJ-ALG-01 for JC/Hoboken addresses (T3) and on both local rules; no preemption conclusion.
- Decision: after 2027-07-01 should the local rules be recorded as `superseded`/preempted? (Only matters for as-of ≥ 2027-07-01 queries.)

## Q4. CA screening-fee cap dollar figure (CA-FEE-01) — organisers' open question
- Key as drafted: `key_value` = statutory formula ($30 base, CPI-adjusted from 1998-01-01), `conflict_flag=true`; Berkeley Rent Board publishes $68.96 for 2026 (official-agency, local computation).
- Options: (a) keep formula only [drafted]; (b) add "$68.96 (2026, per Berkeley Rent Board)" as an illustrative figure.

## Q5. Notice-of-rights ordinances recorded as just_cause_eviction rules (BOS-JUST-01 Boston HSNA; CAM-JUST-01 Cambridge ch. 8.71) — **DECIDED 2026-10-04: (a) keep as notice-only just_cause_eviction rules, conflict_flag kept**
- These impose notice duties on termination, not just cause. Drafted as **rules with conflict_flag** because the organisers put both documents in the corpus (likely extracted by the judges).
- Options: (a) keep as rules [drafted]; (b) convert to negative findings BOS-JUST-00 / CAM-JUST-00 ("no just-cause rule at city level"); (c) keep rule but change requirement text.
- Scoring consequence: 2 rule rows ↔ 2 negative findings; every Boston/Cambridge address loses/gains one `applies` entry.

## Q6. Berkeley BMC 13.78 screening-fee disclosure duty (BERK-FEE-01)
- A disclosure/renewal-fee rule, not a cap. Options: (a) keep as rule [drafted, conflict_flag]; (b) negative finding BERK-FEE-00 with the state cap governing.

## Q7. Boston Fair Chance Tenant Selection Policy (BOS-SCRN-01) — **DECIDED 2026-10-04 (L088): BOS-SCRN-01 = Fair Housing Commission regs; Fair Chance policy added as BOS-SCRN-02 (city-funded only, conflict_flag, confidence 0.5)**
- A 2017 DND funding-conditioned **policy**, not legislation; coverage (DND funding / IDP units) is not in the data → all Boston addresses `unknown`.
- Options: (a) keep as rule with coverage condition [drafted]; (b) negative finding BOS-SCRN-00 (state c.151B governs); (c) keep but set status to n/a-policy.

## Q8. Deposit-interest ordinances under security_deposits (LA-DEP-01, SF-DEP-01, BERK-DEP-01)
- Interest-payment duties rather than caps. Options: (a) keep [drafted]; (b) negative findings (state cap governs). Judges' category description ("security_deposits") is broad enough for (a).

## Q9. Two LA just-cause rows (LA-JUST-01 JCO; LA-JUST-02 RSO § 151.09)
- Options: (a) keep two rows (disjoint coverage) [drafted]; (b) merge into one LA just-cause rule. Affects count-based matching against a judges' key that probably has one LA just-cause row.

## Q10. Cambridge algorithmic pricing (CAM-ALG-00)
- June 2026 policy order asks the City Manager to draft options; no ordinance text. Drafted as a **negative finding** with conflict_flag. Option: record `CAM-ALG-P1` as `pending` instead.

## Q11. Boston H.3744 status (BOS-RENT-P1)
- Drafted `failed` (study order 2024-09-09 ended the 193rd-session petition). Option: `pending` if a refiled 194th-session petition exists (not checked).

## Q12. San Diego source-of-income effective date (SD-SCRN-01) — **DECIDED 2026-10-04 (L033): 2019-08-01, conflict_flag, confidence ≤ 0.7**
- Code history: O-20986 N.S. effective **2018-10-18** [drafted]; SDAR reported an operative date of 2019-08-01. No quoted_span (official Division 8 text not captured; gocodebook returned HTTP 500).

## Q13. Santa Ana algorithmic ordinance (SA-ALG-01) — secondary sources only — **DECIDED 2026-10-04 (L042): effective_date null; note news reports April 2026**
- Status `in_force` rests on PublicCEO / Voice of OC / OCBJ / Morgan Lewis (NS-3090, "effective April 2, 2026"); official text not reachable (Laserfiche cookie wall). `effective_date` left null per the two-source rule. Decision: accept secondary-only status, or downgrade to `pending`/exclude until the ordinance is retrieved. Extraction-only (no Santa Ana addresses).

## Q14. Jersey City § 218-12 details (JC-ALG-01)
- Ord. 25-057 adopted 2025-05-21 (news/press release); effective month 2025-06 (Morgan Lewis); official PDF blocked by robots.txt → no quoted_span. Decision: fetch the civicweb PDF manually and add the span.

## Q15. Hoboken ch. 158 B-750 disclosure duty for >10% increases — **DECIDED 2026-10-04 (L095): added HOB-RENT-02 with conflict_flag**
- Not recorded as a rent_increase_limits rule (it is a disclosure duty, not a cap). Option: add HOB-RENT-02 with conflict_flag.

## Q16. Unit counts inferred from use_description
- For Berkeley (Alameda use code "5+ units") and Boston ("APT 7-30 UNITS") the address key uses the description to defeat small-landlord exceptions (e.g. CA-DEP-01 → applies at A0005). Decision: allow this inference (drafted, marked) or treat units as strictly missing (→ unknown).

## Q17. Long-standing statutes: `effective_date` null vs original enactment date — **DECIDED 2026-10-04 (L046): null unless the source text states an effective date**
- Drafted null for NJ 2A:18-61.1, NJ 46:8-21.2, MA c.186 § 15B, MA c.151B § 4, SF 37.3/37.9, Berkeley 13.76 etc., following the organisers' sample record. Option: fill original enactment years from session laws (would need primary verification).


## 3. Rows whose quoted_span is NOT verbatim in the organisers' corpus (`quoted_span_in_corpus=false`)

These rows may lose citation points even when correct. (supp) = span from a team supplementary capture, verified; (null) = no span.

| gold_id | span source | quote_verified | note |
|---|---|---|---|
| NJ-RENT-00 | supp D062 | True | negative finding |
| NJ-JUST-01 | supp D062 | True | effective_date null: long-standing statute (L.1974, c.49) with many amendments; enacted_date taken from the statutory hi |
| NJ-DEP-01 | supp D063,D064 | True | Quoted span taken from the Justia mirror (D063) because the organisers' corpus has no statute copy; matches the organise |
| NJ-SCRN-02 | supp D061 | True | effective_date null: source-of-lawful-income protection added by L.2002, c.82 (not verified against a primary source thi |
| MA-RENT-P1 | supp D059 | True | Change test T5: status failed; affected address set empty; no rent cap reported for any Boston or Cambridge address. Sta |
| MA-SCRN-02 | null | False | Decided by Hamza 2026-10-04 (L097): added with null span, quote_verified false, confidence 0.5; source text never retrie |
| LA-FEE-00 | null | False | negative finding |
| LA-SCRN-01 | supp D038 | True | Effective date 2020-01-01 rests on the code publisher text plus a secondary source (CAA); the enacting ordinance number  |
| SF-FEE-00 | null | False | negative finding |
| SD-DEP-00 | null | False | negative finding |
| SD-FEE-00 | null | False | negative finding |
| SD-SCRN-01 | null | False | quoted_span null: no saved copy of the operative text (official SDMC PDF for Division 8 not retrieved; 500 error from co |
| SD-ALG-01 | supp D074 | True | The organisers' corpus has only the pre-adoption draft (D076); the adopted code text with dates is in the team capture D |
| SA-DEP-00 | null | False | negative finding |
| SA-FEE-00 | null | False | negative finding |
| SA-SCRN-00 | null | False | negative finding |
| SA-ALG-01 | null | False | effective_date null per rule 5.1/5.2 (no primary source); secondary sources give 2026-04-02. enacted_date 2026-03-03 (se |
| JC-JUST-00 | null | False | negative finding |
| JC-DEP-00 | null | False | negative finding |
| JC-FEE-00 | null | False | negative finding |
| JC-SCRN-00 | null | False | negative finding |
| JC-ALG-01 | null | False | quoted_span null: no official text saved (civicweb PDF blocked). Change test T2: applies only to Jersey City addresses;  |
| HOB-RENT-01 | supp D032,D033 | True | NJ construction years are mostly missing and 39/40 Hoboken rows lack units → new-construction exemption untestable → unk |
| HOB-JUST-00 | null | False | negative finding |
| HOB-DEP-00 | null | False | negative finding |
| HOB-FEE-00 | null | False | negative finding |
| HOB-SCRN-00 | null | False | negative finding |
| HOB-ALG-01 | supp D034,D002 | True | Change test T2: applies only to Hoboken addresses; never to Jersey City or Newark. Decided by Hamza 2026-10-04 (L059): e |
| HOB-RENT-02 | supp D034 | True | effective_date month precision (NJ ordinances take effect ~20 days after final passage/publication); adoption 2025-04-02 |
| NWK-RENT-01 | supp D070 | True | Newark rows have no units and few construction years → new-construction exemption untestable → unknown unless year_built |
| NWK-JUST-00 | null | False | negative finding |
| NWK-DEP-00 | null | False | negative finding |
| NWK-FEE-00 | null | False | negative finding |
| NWK-SCRN-01 | supp D072 | True | effective_date null (adoption 2015-04-15 known; effective date not stated). Owner-occupancy exemptions cannot be resolve |
| NWK-ALG-00 | null | False | negative finding |
| BOS-DEP-00 | null | False | negative finding |
| BOS-FEE-00 | null | False | negative finding |
| BOS-ALG-00 | null | False | negative finding |
| CAM-DEP-00 | null | False | negative finding |
| CAM-FEE-00 | null | False | negative finding |
| CAM-ALG-00 | supp D030 | True | negative finding |

## 4. Address key and change key
- `addresses/seed20.json`: 20 addresses, 190 expected entries, 62 `unknown` (each names the missing fact). Sample gaps: no SF 1979 row; no LA row with a non-"Los Angeles" postal_city.
- `changes/T1-T5.json`: T1 250 CA rows; T2 Hoboken 40 / Jersey City 50 / Newark 0; T3 140 NJ rows with 90 conflict flags; T4 110 MA rows; T5 empty. City totals match the README.
