# Module A evaluation

Gold set: `gold/rules/dev.json` — gold (independent, dev split)  
Our rules: 62 from 104 extracted document(s)  
Gold rules in scope (source doc extracted): 39 of 40 positive, 21 of 21 negative findings

| Metric | Value |
|---|---|
| Found (recall) | 39/39 = 100% (2 by jurisdiction+category only, marked †) |
| Missed | 0 |
| Extra (no gold match) | 23 |
| Extra colliding with a negative finding | 1 |
| Negative findings found / missed / extra | 21 / 0 / 16 |
| Status agrees | 39/39 = 100% |
| Effective date agrees (exact or both null) | 30/39 = 77% (14 exact dates, 16 both null, 9 differ, of which 2 same year) |
| Citation similarity (mean) | 83/100 |
| Key value similarity (mean) | 66/100 |
| Quote check pass rate (first attempt) | 141/141 = 100% |
| Records dropped for bad quotes | 0 |

## Matched rules

| Gold id | Ours | Status (gold / ours) | Eff. date (gold / ours) | Cite score | Key value (gold / ours) |
|---|---|---|---|---|---|
| BERK-ALG-01 | r-0001 | in_force / in_force | 2026-01-01 / 2026-01 | 87 | ban on sale/use of coordinated pricing algorithms / Ban on sale or use of coordinated pricing algorithms (using  |
| BERK-DEP-01 | r-0007 | in_force / in_force | None / None | 63 | annual interest on deposits (covered units) / Security deposit interest required for fully and partially c |
| BERK-FEE-01 | r-0003 | in_force / in_force | 2020 / None | 82 | No separate local fee cap: landlord must give a written Tena / Ban on non-refundable renewal and roommate-change fees charg |
| BERK-JUST-01 | r-0004 | in_force / in_force | None / None | 63 | enumerated just causes; non-payment eviction only if debt ≥  / Nonpayment eviction only if rent debt is at least one month  |
| BERK-RENT-01 | r-0005 | in_force / in_force | 2026-01-01 / 2026-01-01 | 91 | AGA for 2026 is 1.0% (65% of Bay Area CPI July–June, capped  / 1.0% (65% of 1.5% Bay Area CPI-U, July 1, 2024 - June 30, 20 |
| BERK-SCRN-01 | r-0006 | in_force / in_force | 2020-04 / 2020-04 | 66 | ban on criminal-history inquiry and use in housing decisions / Ban on inquiring about or using criminal history in rental h |
| BOS-JUST-01 | r-0008 | in_force / in_force | 2020-11-06 / 2020-11-06 | 84 | [notice-only] With any notice to quit or notice of lease non / Notice-of-rights requirement only; no just-cause protection |
| BOS-RENT-P1 | r-0010 | failed / failed | None / None | 86 | None / Would have authorized Boston rent stabilization; no rent cap |
| BOS-SCRN-02 | r-0011 | in_force / in_force | None / None | 91 | No blanket denial for arrests/convictions; may not consider  / No blanket bans; exclude non-conviction arrests, sealed/expu |
| CA-ALG-01 | r-0013 | in_force / in_force | 2026-01-01 / 2026-01-01 | 100 | Unlawful to use or distribute a common pricing algorithm (a) / Ban on using or distributing a common pricing algorithm in a |
| CA-RENT-01 | r-0016 | in_force / in_force | 2020-01-01 / 2024-04-01 | 100 | lesser of 5% + CPI or 10% per 12 months / 5% + CPI change, max 10% (whichever is lower), per 12 months |
| CA-SCRN-01 | r-0018 | in_force / in_force | 2020-01-01 / 2024-01-01 | 100 | 'Source of income' includes federal, state or local housing  / Ban on source-of-income discrimination (incl. Section 8 / HU |
| CAM-JUST-01 | r-0021 | in_force / in_force | None / None | 90 | notice-of-rights duty at tenancy start and termination (no j / Notice-of-rights requirement only; no just-cause protection |
| CAM-SCRN-01 | r-0022 | in_force / in_force | None / None | 91 | source of income (incl. Section 8) protected locally / Source of income (including Section 8 and public benefits) i |
| HOB-ALG-01 | r-0023 | in_force / in_force | 2025-07 / 2025-07 | 100 | Landlords of residential dwelling units in Hoboken prohibite / Ban on algorithmic rent-fixing using nonpublic competitor in |
| HOB-RENT-01 | r-0025 | in_force / in_force | None / None | 100 | lesser of 5% or CPI change, once per 12 months / Lesser of 5% or CPI change; one increase per 12 months |
| HOB-RENT-02 | r-0024 | in_force / in_force | 2025-04 / 2025-04 | 93 | For renewal rent increases over 10% year over year, landlord / Disclosures required for renewal rent increases of more than |
| JC-ALG-01 | r-0026 | in_force / in_force | 2025-06 / 2025-05 | 100 | Unlawful for any real estate lessor (or agent/subcontractor) / Ban on contracting with algorithmic rent-setting service pro |
| JC-RENT-01 | r-0027 | in_force / in_force | None / None | 84 | lesser of 4% or CPI / Rent control under Ch. 260; all 1-4 unit properties are exem |
| LA-DEP-01 | r-0032 | in_force / in_force | None / 2003-02-01 | 62 | annual interest on deposits (RSO units) / Annual interest on deposits held 1+ year at the RAC-set rate |
| LA-JUST-01 † | r-0028 | in_force / in_force | 2023-01-27 / None | 55 | just cause required after 6 months or lease expiry; relocati / Eviction only for listed at-fault or no-fault just causes; r |
| LA-RENT-01 † | r-0030 | in_force / in_force | 2026-02-02 / 2026-02-02 | 39 | 3% (Jul 2025–Jun 2026); from Jul 2026 formula = 90% of CPI,  / Once per 12 months by the allowable rent increase percentage |
| MA-ALG-P1 | r-0034 | pending / pending | None / None | 60 | None / None |
| MA-ALG-P2 | r-0033 | pending / pending | None / None | 86 | None / None |
| MA-DEP-01 | r-0044 | in_force / in_force | None / None | 74 | 1 month's rent (security deposit) / Security deposit capped at 1 month's rent (plus first month, |
| MA-FEE-01 | r-0037 | in_force / in_force | None / None | 67 | $0 – landlords may not charge application fees / Landlords may not charge application fees; only first, last, |
| MA-RENT-P1 | r-0038 | failed / failed | None / None | 82 | NO RULE: petition barred from the November 2026 ballot (art. / Would have capped annual rent increases at the lower of CPI  |
| NJ-ALG-01 | r-0045 | not_yet_effective / not_yet_effective | 2027-07-01 / 2027-07-01 | 74 | ban on use of algorithmic rent-setting coordinators (effecti / Ban on algorithmic rent-setting coordination (use of coordin |
| NJ-FEE-01 | r-0046 | in_force / in_force | 2026-05-01 / 2026-05-01 | 87 | $50 (CPI-adjusted from January 2027) / $50 maximum, adjusted annually for CPI increases (NY-Norther |
| NJ-JUST-01 | r-0047 | in_force / in_force | None / None | 100 | statutory good cause required for removal / Good cause required to evict or fail to renew a residential  |
| NJ-SCRN-01 | r-0051 | in_force / in_force | 2022-01-01 / 2022-01-01 | 73 | no criminal-record inquiry before conditional offer; individ / No criminal-record inquiry before conditional offer; after o |
| NWK-SCRN-01 | r-0054 | in_force / in_force | None / 2015-04 | 91 | criminal-record inquiry limited to post-qualification stage; / No criminal history inquiry until after formal application;  |
| SA-JUST-01 | r-0064 | in_force / in_force | 2021-11-19 / 2021-11-19 | 90 | just cause after 30 days; 3 months relocation for no-fault / Just cause required after 30 days; no-fault termination requ |
| SA-RENT-01 | r-0065 | in_force / in_force | 2021-11-19 / 2021-11-19 | 81 | lesser of 3% or 80% of CPI; 2.87% for Sep 2026–Aug 2027 / Lower of 3% per year or 80% of CPI change (12 months); no in |
| SD-JUST-01 | r-0056 | in_force / in_force | 2023-06-24 / 2023-06-24 | 62 | just cause required; 2 months relocation (3 for elderly/disa / Just cause required; no-fault relocation assistance = 2 mont |
| SF-ALG-01 | r-0058 | in_force / in_force | 2024-10-14 / 2024-10-14 | 100 | ban on sale/use of algorithmic rent-setting devices / Ban on sale or use of algorithmic rent-setting devices |
| SF-DEP-01 | r-0062 | in_force / in_force | None / 2026-03-01 | 100 | 4.2% annual interest (2026-03-01 to 2027-02-28) / 4.2% interest for March 1, 2026 – February 28, 2027 |
| SF-JUST-01 | r-0059 | in_force / in_force | None / None | 100 | 17 enumerated just causes / Eviction only for one of 17 enumerated just causes (Section  |
| SF-SCRN-01 | r-0061 | in_force / in_force | None / None | 79 | criminal-history limits for affordable housing providers / Protection against use of arrest or conviction history in af |

## Missed gold rules (in scope)

- none

## Extra rules (no gold match)

- r-0002 — Berkeley, CA / application_screening_fees / BMC 13.78.010 (D005): Notification of state law limitation on tenant screening fees (BMC 13.78.010)
- r-0009 — Boston, MA / just_cause_eviction / Mass. H.3744 (193rd General Court, 2023-2024) (D011): H.3744 Boston tenant eviction protections home rule petition (not enacted)
- r-0012 — Boston, MA / screening_restrictions / Boston Fair Housing Commission regulations; see also M.G.L. c. 151B, § 4(10) (D012): Boston fair housing protection for renters using rental assistance
- r-0014 — CA / application_screening_fees / Cal. Civ. Code § 1950.6 (D026): California application screening fee cap and conditions (Civ. Code § 1950.6)
- r-0015 — CA / just_cause_eviction / Cal. Civ. Code § 1946.2 (D023): California Tenant Protection Act - just cause for termination
- r-0017 — CA / screening_restrictions / Cal. Code Regs. tit. 2, § 12265 (Civil Rights Council regulations, eff. 2020-01-01) (D015): Criminal history screening limits (Civil Rights Council regulations)
- r-0019 — CA / security_deposits / Cal. Civ. Code § 1950.5 (D025): California residential security deposit cap and return rules (Civ. Code § 1950.5)
- r-0020 — Cambridge, MA / algorithmic_rent_setting / Cambridge City Council policy order (June 2026), directing city manager to draft ordinance language; no ordinance cited (D030): Cambridge policy order initiating ban on algorithmic rent-setting services
- r-0029 — Los Angeles, CA / just_cause_eviction / L.A.M.C. §§ 151.09, 165.03, 165.06; L.A.M.C. §§ 47.06-47.07 (D043): Relocation assistance for no-fault evictions under the RSO and JCO
- r-0031 — Los Angeles, CA / screening_restrictions / L.A.M.C. § 45.67 (D038): LAMC Sec. 45.67 Prohibited Activities (source-of-income discrimination)
- r-0035 — MA / application_screening_fees / M.G.L. c. 112, § 87DDD-1/2 (M_MA-FEE-02_c112_87DDD-half_masslaw): Rental broker fees payable only by the party who engaged the broker
- r-0036 — MA / application_screening_fees / M.G.L. c. 112, § 87DDD½, as amended by St. 2025, c. 9, § 43 (D057): Broker fee payable only by the party who engaged the broker
- r-0041 — MA / rent_increase_limits / Mass. Const. amend. art. 48, The Initiative, Pt. II, § 2 (SJC ruling, June 2026) (D059): 2026 statewide rent control ballot question (struck by SJC)
- r-0042 — MA / screening_restrictions / M.G.L. c. 151B, § 4(10) (D049): Source-of-income / housing subsidy discrimination ban (M.G.L. c. 151B, § 4(10))
- r-0043 — MA / screening_restrictions / M.G.L. c. 6, § 172(a)(3), (c) (D094): CORI access limits for evaluating rental housing applicants
- r-0048 — NJ / just_cause_eviction / N.J.S.A. 2A:18-61.3 (D067): Anti-Eviction Act: good cause required for lease non-renewal
- r-0050 — NJ / screening_restrictions / N.J.S.A. 10:5-12 (NJ Law Against Discrimination) (D068): NJ Law Against Discrimination: source of lawful income / rent payment protection
- r-0052 — NJ / security_deposits / N.J.S.A. 46:8-21.2; N.J.S.A. 46:8-19; N.J.S.A. 46:8-21.1 (D067): NJ Security Deposit Law: cap of 1.5 months' rent
- r-0053 — Newark, NJ / rent_increase_limits / Newark, N.J., Code § 19:2-3.1 (D070): Newark Rent Control: annual CPI-based rent increase cap
- r-0055 — San Diego, CA / algorithmic_rent_setting / San Diego Municipal Code § 98.1103 (Ord. O-21955 N.S.) (D074): San Diego Prohibition of Anti-Competitive Automated Rent Price Fixing (SDMC §98.1103)
- r-0057 — San Diego, CA / screening_restrictions / San Diego Municipal Code §§ 98.0801-98.0806 (Ord. O-20986 N.S.) (D075): San Diego Prohibition of Discrimination Based on a Tenant's Source of Income
- r-0060 — San Francisco, CA / rent_increase_limits / S.F. Admin. Code ch. 37 (Rent Ordinance), § 37.3 (D080): San Francisco annual allowable rent increase (3/1/2026\u20132/28/2027)
- r-0063 — Santa Ana, CA / algorithmic_rent_setting / Santa Ana Ordinance No. NS-3090 (D002): Santa Ana Ordinance NS-3090 (automated rent price-fixing)

## Collisions with negative findings (gold says: no rule at this level)

- r-0041 Mass. Const. amend. art. 48, The Initiative, Pt. II, § 2 (SJC ruling, June 2026) vs MA-RENT-00: No rent_increase_limits rule at state level

## Negative findings

- found: BOS-ALG-00 ← n-0026 (in_force) No rule at this level
- found: BOS-DEP-00 ← n-0024 (in_force) No rule at this level
- found: BOS-FEE-00 ← n-0025 (in_force) No rule at this level
- found: BOS-RENT-00 ← r-0010 (failed) H.3744 Boston rent stabilization home rule petition (not enacted)
- found: CAM-FEE-00 ← n-0029 (in_force) No rule at this level
- found: HOB-DEP-00 ← n-0017 (in_force) No rule at this level
- found: HOB-FEE-00 ← n-0018 (in_force) No rule at this level
- found: HOB-JUST-00 ← n-0016 (in_force) No rule at this level
- found: HOB-SCRN-00 ← n-0019 (in_force) No rule at this level
- found: JC-DEP-00 ← n-0013 (in_force) No rule at this level
- found: JC-FEE-00 ← n-0014 (in_force) No rule at this level
- found: LA-ALG-00 ← n-0004 (in_force) No rule at this level
- found: LA-FEE-00 ← n-0003 (in_force) No rule at this level
- found: MA-RENT-00 ← r-0038 (failed) Initiative Petition 25-21 (statewide rent increase limit) barred from ballot
- found: NWK-ALG-00 ← n-0023 (in_force) No rule at this level
- found: NWK-DEP-00 ← n-0021 (in_force) No rule at this level
- found: NWK-JUST-00 ← n-0020 (in_force) No rule at this level
- found: SA-FEE-00 ← n-0010 (in_force) No rule at this level
- found: SA-SCRN-00 ← n-0011 (in_force) No rule at this level
- found: SD-DEP-00 ← n-0007 (in_force) No rule at this level
- found: SD-FEE-00 ← n-0008 (in_force) No rule at this level
- extra: r-0009 — Boston, MA / just_cause_eviction / H.3744 Boston tenant eviction protections home rule petition (not enacted) (D011)
- extra: r-0039 — MA / rent_increase_limits / No local rent control permitted (state bar), G.L. c. 40P, § 4 (D048)
- extra: r-0040 — MA / rent_increase_limits / No rent control permitted (state bar, G. L. c. 40P) (M_MA-RENT-P1_Cella_v_AG_SJC-13893)
- extra: r-0041 — MA / rent_increase_limits / 2026 statewide rent control ballot question (struck by SJC) (D059)
- extra: r-0049 — NJ / rent_increase_limits / No statewide rent control (municipal option); rent increase notice and unconscionability standard (D067)
- extra: n-0027 — Cambridge, MA / rent_increase_limits / No rule at this level (D048)
- extra: n-0001 — MA / just_cause_eviction / No rule at this level (None)
- extra: n-0002 — MA / algorithmic_rent_setting / No rule at this level (None)
- extra: n-0005 — San Francisco, CA / application_screening_fees / No rule at this level (None)
- extra: n-0006 — San Diego, CA / rent_increase_limits / No rule at this level (None)
- extra: n-0009 — Santa Ana, CA / security_deposits / No rule at this level (None)
- extra: n-0012 — Jersey City, NJ / just_cause_eviction / No rule at this level (None)
- extra: n-0015 — Jersey City, NJ / screening_restrictions / No rule at this level (None)
- extra: n-0022 — Newark, NJ / application_screening_fees / No rule at this level (None)
- extra: n-0028 — Cambridge, MA / security_deposits / No rule at this level (None)
- extra: n-0030 — Cambridge, MA / algorithmic_rent_setting / No rule at this level (None)
