# Silver vs independent key — comparison (Step 7)

Opened `gold/gold_rules.json` (53 rows: 44 rules + 9 negatives) and `gold/GOLD_REVIEW.md` **after** freezing the independent key (see `FREEZE_before_step7.sha256`). Independent key: 83 rows (51 rules/pending/failed + 32 negative findings). Neither key was edited. Every disagreement below is also a row in `adjudication_log.csv` with `decided_by` blank.

**Accounting of silver rows:** matched 50 (agree 1, field-level disagreements 49), silver-only 3. Independent-only rows: 33.

## (a) Rules in independent but not in silver

| gold_id | category | status | citation | why it exists |
|---|---|---|---|---|
| LA-JUST-02 | just_cause_eviction | in_force | L.A. Mun. Code § 151.09 | RSO legal reasons for eviction and relocation assistance – LAMC § 151.09 |
| LA-FEE-00 | application_screening_fees | n/a | none (state Civ. Code § 1950.6 governs) | No Los Angeles ordinance caps application screening fees; Cal. Civ. Code § 1950.6 (CA-FEE-01) governs. |
| LA-SCRN-01 | screening_restrictions | in_force | L.A. Mun. Code § 45.67 | Source of income discrimination prohibition – LAMC § 45.67 (Art. 5.6, Ch. IV) |
| SF-DEP-01 | security_deposits | in_force | S.F. Admin. Code ch. 49 (§ 49.2) | Interest on security deposits – S.F. Admin. Code ch. 49 |
| SF-FEE-00 | application_screening_fees | n/a | none (state Civ. Code § 1950.6 governs) | No San Francisco ordinance caps application screening fees; Cal. Civ. Code § 1950.6 (CA-FEE-01) governs. |
| SD-RENT-00 | rent_increase_limits | n/a | none (state Civ. Code § 1947.12 governs) | The City of San Diego has no local rent-increase cap; Cal. Civ. Code § 1947.12 (CA-RENT-01) governs San Diego addresses. |
| SD-DEP-00 | security_deposits | n/a | none (state Civ. Code § 1950.5 governs) | No San Diego ordinance regulates security deposits; Cal. Civ. Code § 1950.5 (CA-DEP-01) governs. |
| SD-FEE-00 | application_screening_fees | n/a | none (state Civ. Code § 1950.6 governs) | No San Diego ordinance caps application screening fees; Cal. Civ. Code § 1950.6 (CA-FEE-01) governs. |
| BERK-JUST-01 | just_cause_eviction | in_force | Berkeley Mun. Code § 13.76.130 | Rent Stabilization and Eviction for Just Cause Ordinance – BMC § 13.76.130 |
| BERK-DEP-01 | security_deposits | in_force | Berkeley Mun. Code § 13.76.070 | Interest on security deposits – Berkeley Rent Ordinance (BMC § 13.76.070) |
| BERK-FEE-01 | application_screening_fees | in_force | Berkeley Mun. Code §§ 13.78.010, 13.78.016 | Tenant screening fee disclosure and renewal-fee ban – BMC ch. 13.78 |
| SA-DEP-00 | security_deposits | n/a | none (state Civ. Code § 1950.5 governs) | No Santa Ana ordinance regulates security deposits; Cal. Civ. Code § 1950.5 governs. |
| SA-FEE-00 | application_screening_fees | n/a | none (state Civ. Code § 1950.6 governs) | No Santa Ana ordinance caps application screening fees; Cal. Civ. Code § 1950.6 governs. |
| SA-SCRN-00 | screening_restrictions | n/a | none (state Gov. Code § 12955 governs) | No Santa Ana screening-restriction ordinance identified; Cal. Gov. Code § 12955 (CA-SCRN-01) governs. |
| JC-JUST-00 | just_cause_eviction | n/a | none (N.J.S.A. 2A:18-61.1 governs) | Jersey City has no local just-cause ordinance; the state Anti-Eviction Act (NJ-JUST-01) governs. |
| JC-DEP-00 | security_deposits | n/a | none (N.J.S.A. 46:8-21.2 governs) | No Jersey City deposit ordinance; N.J.S.A. 46:8-21.2 (NJ-DEP-01) governs. |
| JC-FEE-00 | application_screening_fees | n/a | none (N.J.S.A. 46:8-18.1 governs) | No Jersey City application-fee ordinance; N.J.S.A. 46:8-18.1 (NJ-FEE-01) governs. |
| JC-SCRN-00 | screening_restrictions | n/a | none (N.J.S.A. 46:8-52 et seq.; 10:5-12 govern) | No Jersey City screening-restriction ordinance identified; the NJ Fair Chance in Housing Act and LAD (NJ-SCRN-01/02) govern. |
| HOB-JUST-00 | just_cause_eviction | n/a | none (N.J.S.A. 2A:18-61.1 governs) | Hoboken has no local just-cause ordinance; the state Anti-Eviction Act (NJ-JUST-01) governs. |
| HOB-DEP-00 | security_deposits | n/a | none (N.J.S.A. 46:8-21.2 governs) | No Hoboken deposit ordinance; N.J.S.A. 46:8-21.2 (NJ-DEP-01) governs. |
| HOB-FEE-00 | application_screening_fees | n/a | none (N.J.S.A. 46:8-18.1 governs) | No Hoboken application-fee ordinance; N.J.S.A. 46:8-18.1 (NJ-FEE-01) governs. |
| HOB-SCRN-00 | screening_restrictions | n/a | none (N.J.S.A. 46:8-52 et seq.; 10:5-12 govern) | No Hoboken screening-restriction ordinance identified; NJ Fair Chance in Housing Act and LAD govern. |
| NWK-JUST-00 | just_cause_eviction | n/a | none (N.J.S.A. 2A:18-61.1 governs) | Newark has no local just-cause ordinance; the state Anti-Eviction Act (NJ-JUST-01) governs. |
| NWK-DEP-00 | security_deposits | n/a | none (N.J.S.A. 46:8-21.2 governs) | No Newark deposit ordinance; N.J.S.A. 46:8-21.2 (NJ-DEP-01) governs. |
| NWK-FEE-00 | application_screening_fees | n/a | none (N.J.S.A. 46:8-18.1 governs) | No Newark application-fee ordinance; N.J.S.A. 46:8-18.1 (NJ-FEE-01) governs. |
| NWK-SCRN-01 | screening_restrictions | in_force | Newark Code § 2:31-2 (Ord. 6 PSF-B, 4-15-2015) | Ban the Box – housing (criminal record check practices) – Newark Code Title II, ch. 2:31, art. 1 |
| BOS-RENT-P1 | rent_increase_limits | failed | Mass. H.3744 (193rd General Court) – study order H.5035 (2024-09-09) | H.3744 – Boston home-rule petition for rent stabilization and eviction protections (died in study) |
| BOS-DEP-00 | security_deposits | n/a | none (M.G.L. c.186 § 15B governs) | No Boston deposit ordinance; M.G.L. c.186, § 15B (MA-DEP-01) governs. |
| BOS-FEE-00 | application_screening_fees | n/a | none (M.G.L. c.186 § 15B governs) | No Boston application-fee ordinance; M.G.L. c.186, § 15B (MA-FEE-01) governs. |
| CAM-JUST-01 | just_cause_eviction | in_force | Cambridge Mun. Code ch. 8.71 | Tenants' Rights and Resources Notification Ordinance – Cambridge Mun. Code ch. 8.71 |
| CAM-DEP-00 | security_deposits | n/a | none (M.G.L. c.186 § 15B governs) | No Cambridge deposit ordinance; M.G.L. c.186, § 15B (MA-DEP-01) governs. |
| CAM-FEE-00 | application_screening_fees | n/a | none (M.G.L. c.186 § 15B governs) | No Cambridge application-fee ordinance; M.G.L. c.186, § 15B (MA-FEE-01) governs. |
| CAM-ALG-00 | algorithmic_rent_setting | n/a | none (policy order June 2026; MA bills pending) | Cambridge has no algorithmic rent-setting ordinance; on 2026-06-22 the City Council passed only a policy order asking the City Manager to draft options. The pen |

Most of these are **negative findings** that fill the remaining cells of the 13 × 6 matrix (the judges' key has 19 such findings; silver has 9). Substantive additions: SF-DEP-01 (deposit interest, S.F. Admin. Code ch. 49), LA-SCRN-01 (LAMC § 45.67 source of income — silver noted "check D038" but did not add it), LA-JUST-02 (RSO eviction grounds), BERK-JUST-01, BERK-DEP-01, BERK-FEE-01, NWK-SCRN-01 (Ban the Box housing, 2015), CAM-JUST-01, BOS-RENT-P1.

## (b) Rules in silver but not in independent

| silver_id | category | status | citation | independent position |
|---|---|---|---|---|
| HOB-FEE-01 | rent_increase_limits | in_force | Hoboken Code ch. 158, art. I (Ord. B-750) | Disclosure duty for >10% increases (Ord. B-750) – independent treats as not a rent cap; see open_questions Q15. |
| MA-FEE-02 | application_screening_fees | in_force | M.G.L. c.112, § 87DDD½ | Broker-fee reform (c.112 § 87DDD½, eff. 2025-08-01) – independent folded into MA-FEE-01 notes; a separate row is defensible (category fit debatable: broker fee ≠ application fee). |
| MA-SCR-02 | screening_restrictions | in_force | 803 CMR 5.00 | 803 CMR 5.00 (CORI) – source not captured (403); independent omitted because no text could be quoted; mentioned in MA-SCRN-01 interaction note. |

## (c) Field-level disagreements (matched rows)

Substantive rows first; wording-only differences are listed afterwards for completeness.

| silver_id | gold_id | field | silver | independent | evidence | recommendation |
|---|---|---|---|---|---|---|
| BK-ALG-01 | BERK-ALG-01 | effective_date | 2026-03-01 | 2026-01-01 | Silver 2026-03-01 (README text date). Independent 2026-01-01: berkeley.municipal.codes records Ord. 7992-NS adopted 2025-12-02, effective 2026-01-01, and the corpus text D001 has no delayed-effect clause; the 2026-03-01 clause belonged to the superseded Ord. 7974-NS. Organisers list this as an open question — Hamza decides (open_questions Q1). | Hamza decides |
| BK-RENT-01 | BERK-RENT-01 | key_value | Annual General Adjustment set by Rent Board | 1.0% for 2026 (65% of CPI; 5% cap) | Independent gives 1.0% for 2026 (D008 official notice) and the 65%-of-CPI / 5% cap formula (berkeley.municipal.codes 13.76.110); silver has no number. Prefer independent. | adopt independent |
| BK-SCR-01 | BERK-SCRN-01 | effective_date | 2020-03-12 | 2020 | Silver 2020-03-12 (unsourced). Independent: adopted 2020-04-14 per Rent Board page D003 ("On April 14, 2020, Berkeley City Council passed..."); exact effective date not shown by the code publisher → year precision 2020. Neither value is primary-verified to the day; recommend 2020 (or verify Ord. 7692-NS second reading/effective date). | Hamza decides |
| BK-SCR-01 | BERK-SCRN-01 | citation | Berkeley Mun. Code ch. 13.106 | Berkeley Mun. Code § 13.106.040 (Ord. 7692-NS) |  | adopt independent |
| BOS-JC-01 | BOS-JUST-01 | effective_date | 2021-01-01 | 2020-11-06 | Silver 2021-01-01 (unsourced); independent 2020-11-06 from the official FAQ D014 ("The HSNA becomes effective on November 6, 2020"). Adopt independent. | Hamza decides |
| BOS-JC-01 | BOS-JUST-01 | citation | Boston Code ch. 10, § 10-14 (Housing Stability Notification Act) | Boston Code of Ordinances ch. 9, § 9-20 (Housing Stability Notification Act) | Silver "Boston Code ch. 10, § 10-14"; independent "ch. 9, § 9-20" — BOTH from memory, neither verified. Hamza to check the Boston Code (ordinance of October 2020). | adopt independent |
| BOS-RENT-00 | BOS-RENT-00 | citation | H.3744 (2023, not enacted); M.G.L. c.40P | M.G.L. c.40P, § 4; Mass. H.3744 (193rd) – study order |  | adopt independent |
| BOS-SCR-01 | BOS-SCRN-01 | effective_date | None | 2017-02 |  | Hamza decides |
| BOS-SCR-01 | BOS-SCRN-01 | citation | Boston Fair Housing Commission regulations | Boston Fair Chance Tenant Selection Policy (DND, February 2017) – policy, not ordinance |  | adopt independent |
| BOS-SCR-01 | BOS-SCRN-01 | key_value | Prohibits discrimination incl. based on source of income / housing subsidies | no blanket criminal-history denials; 5-year look-back (city-funded/IDP housing) |  | adopt independent |
| BOS-SCR-01 | BOS-SCRN-01 | rule_identity | (see note) | (see note) | Different rules in the same cell: silver = Boston Fair Housing Commission regulations (source of income), independent = Boston Fair Chance Tenant Selection Policy (criminal history, DND-funded housing; D010 content). D012 (corpus) is only the Commission landing page and does not state a source-of-income rule. Options: keep independent; add silver's as BOS-SCRN-02 if the Commission regulation text can be sourced. | Hamza decides |
| CA-ALG-01 | CA-ALG-01 | citation | Cal. Bus. & Prof. Code § 16700 et seq., as amended by AB 325 (2025) | Cal. Bus. & Prof. Code § 16729 (added by AB 325, Stats. 2025 ch. 338) | Corpus D022 shows AB 325 adds Bus. & Prof. Code §§ 16729 and 16756.1; § 16729 is the operative prohibition. Recommend independent (specific section). | adopt independent |
| CA-FEE-01 | CA-FEE-01 | key_value | Actual out-of-pocket cost, capped at CPI-adjusted statutory amount; no fee when no unit is available | $30 (1997 base) adjusted annually by CPI from 1998-01-01; no single official 2026 dollar figure |  | adopt independent |
| CAM-SCR-01 | CAM-SCRN-01 | citation | Cambridge Mun. Code ch. 2.76 (Human Rights Ordinance) | Cambridge Mun. Code ch. 14.04 | Silver ch. 2.76 (Human Rights Ordinance); independent ch. 14.04 (Fair Housing Ordinance). D029 says the Commission enforces both and that housing discrimination is covered by the Fair Housing Ordinance ch. 14.04. Adopt independent. | adopt independent |
| HOB-ALG-01 | HOB-ALG-01 | effective_date | 2025-07-09 | 2025-07 | Silver 2025-07-09 is the adoption date (D034 "[Adopted 7-9-2025 by Ord. No. B-781]"); independent uses month precision 2025-07 because NJ ordinances take effect after publication (~20 days). Decision for Hamza. | Hamza decides |
| HOB-RENT-01 | HOB-RENT-01 | coverage | (see note) | (see note) | Independent adds § 155-2 exemptions (hotels, post-1987-06-25 new construction, etc.) read from ecode360; silver left coverage to verify. | adopt independent |
| JC-RENT-01 | JC-RENT-01 | citation | Jersey City Code ch. 260 | Jersey City Code § 260-3 | Independent § 260-3 (official notice). Adopt. | adopt independent |
| JC-RENT-01 | JC-RENT-01 | key_value | Annual increase capped at CPI, max 4% (verify) | lesser of 4% or CPI | Silver "(verify)"; independent verified the lesser-of-4%-or-CPI formula from the official Jersey City CPI notice quoting § 260-3, and the 1–4 unit exemption from D036. Adopt independent and remove "(verify)". | adopt independent |
| LA-ALG-00 | LA-ALG-00 | source | (see note) | (see note) | Both negative. Independent adds the Aug-2026 Morgan Lewis survey (no LA ordinance listed) and a 2026-10-03 web search; conflict_flag=true because absence is inferred. | adopt independent |
| LA-DEP-01 | LA-DEP-01 | source | (see note) | (see note) | Independent additionally cites official LAHD RSO overview (D041 lists "Interest Payments on Security Deposits"); silver relied on AAGLA only. | adopt independent |
| LA-RENT-01 | LA-RENT-01 | citation | L.A. Mun. Code ch. XV, art. 1 (RSO); LAHD RSO overview | L.A. Mun. Code § 151.06 (as amended by Ord. No. 188795) | Independent adds Ord. No. 188795 and § 151.06 (City Clerk CF 23-1134); silver cites the RSO generally. Prefer independent. | adopt independent |
| LA-RENT-01 | LA-RENT-01 | key_value | Annual allowable increase set by LAHD formula (2026 formula; utility and dependent add-ons removed from 2026-02-02) | 3% (Jul 2025–Jun 2026); from Jul 2026 formula = 90% of CPI, floor 1%, cap 4% | Independent records 3% (Jul 2025–Jun 2026) and the 90%-of-CPI / 1% floor / 4% cap formula (AAGLA, secondary; LAHD page confirms 2026-02-02 changes). Silver has the formula description without numbers. Prefer independent; numbers for Jul 2026–Jun 2027 not confirmed on an official page. | adopt independent |
| MA-RENT-P1 | MA-RENT-P1 | key_value | NO RULE; proposed statewide rent cap removed from Nov 2026 ballot by SJC on 2026-06-23 | None |  | adopt independent |
| NJ-ALG-01 | NJ-ALG-01 | citation | P.L.2026, c.43 (N.J.S.A. 56:9-?) | N.J.S.A. 56:9-20 to 56:9-26 (P.L.2026, c.43) | Silver "56:9-?"; independent N.J.S.A. 56:9-20 to 56:9-26 — from the chapter header of D069 ("C.56:9-20 to 56:9-26"). Adopt independent. | adopt independent |
| NJ-FEE-01 | NJ-FEE-01 | citation | N.J.S.A. 46:8-? (P.L.2025, c.405) | N.J.S.A. 46:8-18.1 (P.L.2025, c.405, § 1) | Silver "46:8-?"; independent N.J.S.A. 46:8-18.1 — verified in corpus D066 ("C.46:8-18.1 Residential rental property application fee not to exceed $50"). Adopt independent. | adopt independent |
| NJ-JC-01 | NJ-JUST-01 | effective_date | 1974-06-25 | None |  | Hamza decides |
| NWK-RENT-01 | NWK-RENT-01 | citation | Newark Code Title 19 (Rent Control) | Newark Code § 19:2-3.1 (Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord. No. 6PSF-I) | Independent § 19:2-3.1 (Ord. 6 PSF-A(S) 2017; amended 2024). Adopt. | adopt independent |
| NWK-RENT-01 | NWK-RENT-01 | key_value | Annual increase capped at CPI, max 4% (verify) | CPI change, capped at 4% per 12 months | Silver "(verify)"; independent verified "In no case shall the allowable rent increase exceed 4%" (CPI 15→3 months) from D070 § 19:2-3.1. Adopt independent. | adopt independent |
| SA-ALG-01 | SA-ALG-01 | effective_date | 2026-04 | None | Silver 2026-04 (from news/Morgan Lewis). Independent null: no primary source reached (rule 5.1/5.2); secondary sources say 2026-04-02. Decision: accept month precision from secondary sources or keep null. | Hamza decides |
| SA-JC-01 | SA-JUST-01 | citation | Santa Ana Mun. Code ch. 8, art. XX (Ord. NS-3012) | Santa Ana Mun. Code (Just Cause Eviction Ordinance, 2021) | As above (silver NS-3012 unverified by independent). | adopt independent |
| SA-RENT-01 | SA-RENT-01 | citation | Santa Ana Mun. Code ch. 8, art. XIX (Ord. NS-3011) | Santa Ana Mun. Code § 8-1998 et seq. (Rent Stabilization Ordinance) | Silver cites Ord. NS-3011; independent could not verify an ordinance/section number (press release D085 only). If NS-3011/NS-3012 can be confirmed from the Santa Ana code, adopt silver's numbers. | adopt silver if verified |
| SA-RENT-01 | SA-RENT-01 | key_value | Lesser of 3% or 80% of CPI per year | lesser of 3% or 80% of CPI; 2.87% for Sep 2026–Aug 2027 |  | adopt independent |
| SD-SCR-01 | SD-SCRN-01 | effective_date | None | 2018-10-18 | Silver null; independent 2018-10-18 from the SDMC history note "O–20986 N.S.; effective 10-18-2018" (NHLP mirror of the code). Operative date 2019-08-01 reported by SDAR (secondary) – flagged. | Hamza decides |
| SF-RENT-01 | SF-RENT-01 | effective_date | 2026-03-01 | None | Silver uses the rate-period start (2026-03-01, D080); independent leaves null because the Rent Ordinance dates from 1979 and the rate is annual. Decision for Hamza: rate-period date vs null. | Hamza decides |
| BK-ALG-01 | BERK-ALG-01 | citation | Berkeley Mun. Code ch. 13.63 (Ord. 7992) | Berkeley Mun. Code § 13.63.030 (Ord. 7992-NS) | Equivalent; independent cites § 13.63.030 (prohibition) + Ord. 7992-NS. | no change (equivalent) |
| BK-ALG-01 | BERK-ALG-01 | key_value | Prohibits use of algorithmic devices to set rents/occupancy | ban on sale/use of coordinated pricing algorithms | Wording differs; substance equivalent. | no change (wording only) |
| BK-RENT-01 | BERK-RENT-01 | citation | Berkeley Mun. Code ch. 13.76 (Rent Ordinance) | Berkeley Mun. Code § 13.76.110(A) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| BK-SCR-01 | BERK-SCRN-01 | key_value | Prohibits asking about or using criminal history in rental decisions | ban on criminal-history inquiry and use in housing decisions | Wording differs; substance equivalent. | no change (wording only) |
| BOS-ALG-00 | BOS-ALG-00 | citation | None | none (MA bills S.2983/H.5222 pending) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| BOS-JC-01 | BOS-JUST-01 | key_value | Landlords must give tenants a notice of rights with any notice to quit / non-renewal | notice-of-rights duty on termination (no just-cause requirement) | Wording differs; substance equivalent. | no change (wording only) |
| CA-ALG-01 | CA-ALG-01 | key_value | Unlawful to use/distribute a common pricing algorithm in restraint of trade or to coerce adoption of its recommended price | prohibition on use/distribution of common pricing algorithms in restraint of trade | Wording differs; substance equivalent. | no change (wording only) |
| CA-DEP-01 | CA-DEP-01 | key_value | 1 month's rent; 2 months for qualifying small landlords | 1 month's rent (2 months for qualifying small landlords) | Wording differs; substance equivalent. | no change (wording only) |
| CA-JC-01 | CA-JUST-01 | key_value | Just cause required after 12 months' continuous occupancy | just cause required after 12 months of occupancy; 1 month relocation assistance for no-fault | Wording only; both describe the 12-month trigger. No change needed. | no change (equivalent) |
| CA-RENT-01 | CA-RENT-01 | key_value | 5% + CPI, max 10% per 12 months | lesser of 5% + CPI or 10% per 12 months | Wording differs; substance equivalent. | no change (wording only) |
| CA-SCR-01 | CA-SCRN-01 | citation | Cal. Gov. Code § 12955 (FEHA), as amended by SB 329 | Cal. Gov. Code § 12955(a), (p) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| CA-SCR-01 | CA-SCRN-01 | key_value | Housing vouchers count as income; refusal based on source of income is unlawful | source of income (incl. Section 8 vouchers) is a protected characteristic | Wording differs; substance equivalent. | no change (wording only) |
| CAM-RENT-00 | CAM-RENT-00 | citation | M.G.L. c.40P | M.G.L. c.40P, § 4 | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| CAM-SCR-01 | CAM-SCRN-01 | key_value | Local enforcement of housing discrimination protections incl. source of income | source of income (incl. Section 8) protected locally | Wording differs; substance equivalent. | no change (wording only) |
| HOB-ALG-01 | HOB-ALG-01 | citation | Hoboken Code ch. 158, art. II, § 158-2 (Ord. B-781) | Hoboken Code ch. 158 (Ord. No. B-781, adopted 2025-07-09) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| HOB-ALG-01 | HOB-ALG-01 | key_value | Prohibits landlords from using rent algorithms with nonpublic competitor data; fine up to $2,000 | ban on algorithmic price fixing using nonpublic competitor information | Wording differs; substance equivalent. | no change (wording only) |
| HOB-RENT-01 | HOB-RENT-01 | citation | Hoboken Code ch. 155 | Hoboken Code § 155-5 | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| HOB-RENT-01 | HOB-RENT-01 | key_value | Annual increase capped at CPI, max 5% | lesser of 5% or CPI per 12 months | Equivalent (lesser of 5% or CPI). | no change (equivalent) |
| JC-ALG-01 | JC-ALG-01 | citation | Jersey City Code § 218-12 | Jersey City Code § 218-12 (Ord. 25-057) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| JC-ALG-01 | JC-ALG-01 | key_value | Prohibits use of rent-setting algorithms (e.g., RealPage); private right of action | ban on landlord use of algorithmic rent-setting with nonpublic competitor data | Wording differs; substance equivalent. | no change (wording only) |
| LA-ALG-00 | LA-ALG-00 | citation | L.A. Council File 24-1031 (motion, 2024) | L.A. City Council motion CF 24-1031 (2024-09-03) – no ordinance | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| LA-DEP-01 | LA-DEP-01 | key_value | Landlord must pay interest on security deposits for RSO units | annual interest on deposits (RSO units) | Wording differs; substance equivalent. | no change (wording only) |
| LA-JC-01 | LA-JUST-01 | citation | L.A. Mun. Code § 165.00 et seq. (JCO) | L.A. Mun. Code § 165.03 (Art. 5.3, Ch. XVI; Ord. No. 187737) | Equivalent (§ 165.00 et seq. vs § 165.03 / Ord. 187737, verified against the City Clerk PDF). | no change (equivalent) |
| LA-JC-01 | LA-JUST-01 | key_value | Just cause required after 6 months or first lease expiry, whichever first | just cause required after 6 months or lease expiry; relocation assistance for no-fault | Wording differs; substance equivalent. | no change (wording only) |
| MA-ALG-P1 | MA-ALG-P1 | citation | MA Senate Bill S.2983 (194th General Court) | Mass. S.2983 (194th General Court) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| MA-ALG-P1 | MA-ALG-P1 | key_value | Would prohibit algorithmic rent setting statewide | None | Wording differs; substance equivalent. | no change (wording only) |
| MA-ALG-P2 | MA-ALG-P2 | citation | MA House Bill H.5222 (194th General Court) | Mass. H.5222 (194th General Court) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| MA-ALG-P2 | MA-ALG-P2 | key_value | Would prohibit algorithmic rent fixing in the rental housing market | None | Wording differs; substance equivalent. | no change (wording only) |
| MA-DEP-01 | MA-DEP-01 | key_value | First month's rent | 1 month's rent (security deposit) | Wording differs; substance equivalent. | no change (wording only) |
| MA-FEE-01 | MA-FEE-01 | key_value | Only first month's rent, last month's rent, security deposit and lock/key cost may be charged upfront; no application fee | $0 – landlords may not charge application fees | Wording differs; substance equivalent. | no change (wording only) |
| MA-JC-00 | MA-JUST-00 | citation | M.G.L. c.186, §§ 11, 12 (notice periods, not just cause) | M.G.L. c.186, §§ 11, 12 (notice to quit; no just-cause requirement) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| MA-RENT-00 | MA-RENT-00 | effective_date | 1994-12-08 | None | Silver 1994-12-08 (c.40P enactment, unsourced in corpus); independent null (negative finding). Harmless either way; prefer null for negative findings. | no change (equivalent) |
| MA-RENT-P1 | MA-RENT-P1 | negative_finding | True | False | Silver marks the failed initiative as negative_finding=true; independent records it as a failed measure (status failed, negative_finding=false) and keeps a separate MA-RENT-00 negative finding. Representational; keep both rows. | no change (equivalent) |
| MA-RENT-P1 | MA-RENT-P1 | citation | IP 25-21; SJC decision 2026-06-23 | Initiative Petition 25-21 (Mass. 2026); Cella v. Attorney General (SJC, decided 2026-06-23) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| MA-SCR-01 | MA-SCRN-01 | key_value | Unlawful to discriminate against recipients of public assistance or housing subsidies | recipients of public assistance / housing subsidies are protected | Wording differs; substance equivalent. | no change (wording only) |
| NJ-ALG-01 | NJ-ALG-01 | key_value | Prohibits use/sale of rent-setting algorithms using nonpublic competitor data | ban on use of algorithmic rent-setting coordinators (effective 2027-07-01) | Wording differs; substance equivalent. | no change (wording only) |
| NJ-FEE-01 | NJ-FEE-01 | key_value | $50 cap; penalty up to $500 per violation | $50 (CPI-adjusted from January 2027) | Independent adds CPI adjustment from January 2027 (D066 § 1(d)). Compatible. | no change (equivalent) |
| NJ-JC-01 | NJ-JUST-01 | key_value | Eviction only on enumerated good-cause grounds | statutory good cause required for removal | Wording differs; substance equivalent. | no change (wording only) |
| NJ-RENT-00 | NJ-RENT-00 | citation | N.J.S.A. 2A:18-61.1(f); municipal ordinances govern | N.J.S.A. 2A:18-61.1(f) (no statewide cap) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| NJ-SCR-01 | NJ-SCRN-01 | citation | N.J.S.A. 46:8-52 et seq. (P.L.2021, c.110) | N.J.S.A. 46:8-55 (P.L.2021, c.110) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| NJ-SCR-01 | NJ-SCRN-01 | key_value | No criminal-history inquiry before conditional offer; limits on what may be considered after | no criminal-record inquiry before conditional offer; individualised assessment required | Wording differs; substance equivalent. | no change (wording only) |
| NJ-SCR-02 | NJ-SCRN-02 | citation | N.J.S.A. 10:5-12(g) | N.J.S.A. 10:5-12(g)(1) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| NJ-SCR-02 | NJ-SCRN-02 | key_value | Unlawful to refuse rental based on lawful source of income incl. vouchers | source of lawful income (incl. vouchers) is a protected category | Wording differs; substance equivalent. | no change (wording only) |
| NWK-ALG-00 | NWK-ALG-00 | citation | None | none (NJ FAIR Act P.L.2026 c.43 from 2027-07-01) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| SA-ALG-01 | SA-ALG-01 | citation | Santa Ana Ord. NS-3090 | Santa Ana Ordinance No. NS-3090 (code section not verified) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| SA-ALG-01 | SA-ALG-01 | key_value | Prohibits use of anticompetitive rent-setting software | ban on sale/use of algorithmic rent-setting software | Wording differs; substance equivalent. | no change (wording only) |
| SA-JC-01 | SA-JUST-01 | key_value | Eviction only for enumerated causes; relocation assistance | just cause after 30 days; 3 months relocation for no-fault | Wording differs; substance equivalent. | no change (wording only) |
| SD-ALG-01 | SD-ALG-01 | citation | S.D. Mun. Code §§ 98.1101-98.1104 (O-21955 N.S.) | San Diego Mun. Code § 98.1103 (O-21955 N.S.) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| SD-ALG-01 | SD-ALG-01 | key_value | Prohibits sale and use of algorithmic devices to set rents | ban on sale/use of algorithmic rent-setting devices | Wording differs; substance equivalent. | no change (wording only) |
| SD-JC-01 | SD-JUST-01 | citation | S.D. Mun. Code ch. 9, art. 8, div. 7 (§ 98.0701 et seq.) | San Diego Mun. Code § 98.0704 (O-21647 N.S.) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| SD-JC-01 | SD-JUST-01 | key_value | Just cause and relocation assistance beyond state law | just cause required; 2 months relocation (3 for elderly/disabled) | Wording differs; substance equivalent. | no change (wording only) |
| SD-SCR-01 | SD-SCRN-01 | citation | S.D. Mun. Code ch. 9, art. 8, div. 8 | San Diego Mun. Code § 98.0803 (O-20986 N.S.) | Equivalent; independent cites § 98.0803 specifically. | no change (equivalent) |
| SD-SCR-01 | SD-SCRN-01 | key_value | Prohibits discrimination based on source of income (incl. vouchers) | source of income (incl. vouchers) protected | Wording differs; substance equivalent. | no change (wording only) |
| SF-ALG-01 | SF-ALG-01 | key_value | Prohibits sale or use of algorithmic devices to set rents or occupancy levels | ban on sale/use of algorithmic rent-setting devices | Wording differs; substance equivalent. | no change (wording only) |
| SF-JC-01 | SF-JUST-01 | citation | S.F. Admin. Code § 37.9 | S.F. Admin. Code § 37.9(a) | Equivalent (§ 37.9 vs § 37.9(a)). | no change (equivalent) |
| SF-JC-01 | SF-JUST-01 | key_value | Eviction only for the enumerated just causes | 17 enumerated just causes | Wording differs; substance equivalent. | no change (wording only) |
| SF-RENT-01 | SF-RENT-01 | citation | S.F. Admin. Code ch. 37; Rent Board rate notice | S.F. Admin. Code § 37.3(a) | Independent cites § 37.3(a) (allowable increases); silver cites ch. 37 generally. Equivalent; prefer the section. | no change (equivalent) |
| SF-RENT-01 | SF-RENT-01 | key_value | 1.6% for 1 Mar 2026 - 28 Feb 2027 (60% of CPI) | 1.6% (2026-03-01 to 2027-02-28); formula 60% of CPI | Wording differs; substance equivalent. | no change (wording only) |
| SF-SCR-01 | SF-SCRN-01 | citation | S.F. Police Code art. 49 (Fair Chance Ordinance) | S.F. Police Code art. 49 (§§ 4901 et seq.) | Same provision; independent cites the operative section. | no change (independent cite is more specific) |
| SF-SCR-01 | SF-SCRN-01 | key_value | Limits use of criminal history in affordable-housing decisions | criminal-history limits for affordable housing providers | Wording differs; substance equivalent. | no change (wording only) |

## (d) Rows that agree on all compared fields

NJ-DEP-01→NJ-DEP-01

## Representational differences (not logged per row)
- Silver gives negative findings `status: in_force`; independent uses `n/a`. Silver id prefixes differ (JC→JUST, SCR→SCRN, BK→BERK).
- Independent carries structured `coverage`, `quoted_span` (substring-verified), `quoted_span_in_corpus`, `verified_against` and `source_ids`; silver has free-text `coverage_conditions` and a `verify` hint.
- Silver T-test ids (CA-ALG-01, HOB-ALG-01, JC-ALG-01, NJ-ALG-01, MA-ALG-P1/P2, MA-RENT-P1) match the organisers' change_tests and the independent key.


## Recommendation summary
1. Adopt independent values where the silver row says "verify" or "?" and the independent key has a verified source (NJ-FEE-01, NJ-ALG-01 citations; JC-RENT-01 and NWK-RENT-01 caps; BOS-JC-01 effective date; CAM-SCR-01 citation; CA-ALG-01 section).
2. Hamza decides the dated conflicts the organisers flagged (Berkeley 13.63; LA RSO formula date — both keys already agree on 2026-02-02 for LA) and the categorisation questions (notice-of-rights ordinances; Hoboken B-750 disclosure; broker-fee reform).
3. Where neither key is primary-verified (Boston HSNA code section; Berkeley 13.106 effective day; Santa Ana ordinance numbers), verify before upgrading `verifier`.
