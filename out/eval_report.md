# Module A evaluation

Gold set: `gold/rules/dev.json` — gold (independent, dev split)  
Our rules: 60 from 85 extracted document(s)  
Gold rules in scope (source doc extracted): 39 of 40 positive, 21 of 21 negative findings

| Metric | Value |
|---|---|
| Found (recall) | 37/39 = 95% (2 by jurisdiction+category only, marked †) |
| Missed | 2 |
| Extra (no gold match) | 23 |
| Extra colliding with a negative finding | 0 |
| Negative findings found / missed / extra | 21 / 0 / 15 |
| Status agrees | 37/37 = 100% |
| Effective date exact / same year | 12/37 = 32% / 12/37 |
| Citation similarity (mean) | 84/100 |
| Key value similarity (mean) | 67/100 |
| Quote check pass rate (first attempt) | 113/113 = 100% |
| Records dropped for bad quotes | 0 |

## Matched rules

| Gold id | Ours | Status (gold / ours) | Eff. date (gold / ours) | Cite score | Key value (gold / ours) |
|---|---|---|---|---|---|
| BERK-ALG-01 | r-0001 | in_force / in_force | 2026-01-01 / None | 87 | ban on sale/use of coordinated pricing algorithms / Ban on sale or use of coordinated pricing algorithms (using  |
| BERK-DEP-01 | r-0007 | in_force / in_force | None / None | 63 | annual interest on deposits (covered units) / Security deposit interest required for fully and partially c |
| BERK-FEE-01 | r-0003 | in_force / in_force | None / None | 82 | disclosure of state fee cap required; no non-refundable rene / Ban on non-refundable renewal and roommate-change fees charg |
| BERK-JUST-01 | r-0004 | in_force / in_force | None / None | 63 | enumerated just causes; non-payment eviction only if debt ≥  / Nonpayment eviction only if rent debt is at least one month  |
| BERK-RENT-01 | r-0005 | in_force / in_force | None / 2026-01-01 | 91 | 1.0% for 2026 (65% of CPI; 5% cap) / 1.0% (65% of 1.5% Bay Area CPI-U, July 1, 2024 - June 30, 20 |
| BERK-SCRN-01 | r-0006 | in_force / in_force | 2020-04 / None | 66 | ban on criminal-history inquiry and use in housing decisions / Ban on inquiring about or using criminal history in rental h |
| BOS-JUST-01 | r-0008 | in_force / in_force | 2020-11-06 / 2020-11-06 | 84 | notice-of-rights duty on termination (no just-cause requirem / Notice-of-rights requirement only; no just-cause protection |
| BOS-SCRN-02 | r-0011 | in_force / in_force | 2017-02 / None | 95 | no blanket criminal-history denials; 5-year look-back (city- / No consideration of non-conviction arrests, expunged/sealed  |
| CA-ALG-01 | r-0013 | in_force / in_force | 2026-01-01 / None | 100 | prohibition on use/distribution of common pricing algorithms / Ban on using or distributing a common pricing algorithm in a |
| CA-RENT-01 | r-0016 | in_force / in_force | 2020-01-01 / 2024-04-01 | 100 | lesser of 5% + CPI or 10% per 12 months / 5% + CPI change, max 10% (whichever is lower), per 12 months |
| CA-SCRN-01 | r-0018 | in_force / in_force | 2020-01-01 / 2024-01-01 | 100 | source of income (incl. Section 8 vouchers) is a protected c / Ban on source-of-income discrimination (incl. Section 8 / HU |
| CAM-JUST-01 | r-0021 | in_force / in_force | None / None | 90 | notice-of-rights duty at tenancy start and termination (no j / Notice-of-rights requirement only; no just-cause protection |
| CAM-SCRN-01 | r-0022 | in_force / in_force | None / None | 91 | source of income (incl. Section 8) protected locally / Source of income (including Section 8 and public benefits) i |
| HOB-ALG-01 | r-0023 | in_force / in_force | 2025-07 / 2025-07 | 83 | ban on algorithmic price fixing using nonpublic competitor i / Ban on price fixing using algorithmic pricing (software or d |
| HOB-RENT-01 | r-0025 | in_force / in_force | None / 2023-02 | 100 | lesser of 5% or CPI per 12 months / Lesser of 5% or CPI change; one increase per 12 months |
| HOB-RENT-02 | r-0024 | in_force / in_force | 2025-04 / 2025-04 | 83 | disclosures required for renewal increases > 10% (not a cap) / Disclosures required for renewal rent increases of more than |
| JC-ALG-01 | r-0026 | in_force / in_force | 2025-06 / 2025-06 | 100 | ban on landlord use of algorithmic rent-setting with nonpubl / Ban on landlord use of algorithmic rent coordination service |
| JC-RENT-01 | r-0028 | in_force / in_force | None / None | 84 | lesser of 4% or CPI / Rent control under Ch. 260; all 1-4 unit properties are exem |
| LA-DEP-01 | r-0033 | in_force / in_force | None / None | 76 | annual interest on deposits (RSO units) / Interest paid monthly or yearly at the City-set annual rate  |
| LA-JUST-01 † | r-0029 | in_force / in_force | 2023-01-27 / None | 55 | just cause required after 6 months or lease expiry; relocati / Eviction only for listed at-fault or no-fault just causes; r |
| LA-RENT-01 † | r-0031 | in_force / in_force | 2026-02-02 / 2026-02-02 | 39 | 3% (Jul 2025–Jun 2026); from Jul 2026 formula = 90% of CPI,  / Once per 12 months by the allowable rent increase percentage |
| MA-ALG-P1 | r-0035 | pending / pending | None / None | 100 | None / Would prohibit algorithmic rent setting (bill text not in th |
| MA-ALG-P2 | r-0034 | pending / pending | None / None | 86 | None / None |
| MA-DEP-01 | r-0041 | in_force / in_force | None / None | 74 | 1 month's rent (security deposit) / Security deposit capped at 1 month's rent (plus first month, |
| MA-FEE-01 | r-0037 | in_force / in_force | None / None | 67 | $0 – landlords may not charge application fees / Landlords may not charge application fees; only first, last, |
| NJ-ALG-01 | r-0042 | not_yet_effective / not_yet_effective | 2027-07-01 / 2027-07-01 | 74 | ban on use of algorithmic rent-setting coordinators (effecti / Ban on algorithmic rent-setting coordination (use of coordin |
| NJ-FEE-01 | r-0043 | in_force / in_force | 2026-05-01 / 2026-05-01 | 87 | $50 (CPI-adjusted from January 2027) / $50 maximum, adjusted annually for CPI increases (NY-Norther |
| NJ-JUST-01 | r-0044 | in_force / in_force | None / None | 100 | statutory good cause required for removal / Good cause required to evict or fail to renew a residential  |
| NJ-SCRN-01 | r-0048 | in_force / in_force | 2022-01-01 / 2022-01-01 | 73 | no criminal-record inquiry before conditional offer; individ / No criminal-record inquiry before conditional offer; after o |
| NWK-SCRN-01 | r-0053 | in_force / in_force | None / 2015-04 | 91 | criminal-record inquiry limited to post-qualification stage; / No criminal history inquiry until after formal application;  |
| SA-JUST-01 | r-0064 | in_force / in_force | 2021-11-19 / 2021-11-19 | 90 | just cause after 30 days; 3 months relocation for no-fault / Just cause required after 30 days; no-fault termination requ |
| SA-RENT-01 | r-0065 | in_force / in_force | 2021-11-19 / 2021-11-19 | 81 | lesser of 3% or 80% of CPI; 2.87% for Sep 2026–Aug 2027 / Lower of 3% per year or 80% of CPI change (12 months); no in |
| SD-JUST-01 | r-0055 | in_force / in_force | 2023-06-24 / 2023-06-24 | 62 | just cause required; 2 months relocation (3 for elderly/disa / Just cause required; no-fault relocation assistance = 2 mont |
| SF-ALG-01 | r-0057 | in_force / in_force | 2024-10-14 / 2024-10-14 | 100 | ban on sale/use of algorithmic rent-setting devices / Ban on sale or use of algorithmic rent-setting devices |
| SF-DEP-01 | r-0061 | in_force / in_force | None / 2026-03-01 | 100 | 4.2% annual interest (2026-03-01 to 2027-02-28) / 4.2% interest for March 1, 2026 – February 28, 2027 |
| SF-JUST-01 | r-0058 | in_force / in_force | None / None | 100 | 17 enumerated just causes / Eviction only for one of 17 enumerated just causes (Section  |
| SF-SCRN-01 | r-0060 | in_force / in_force | None / None | 79 | criminal-history limits for affordable housing providers / Protection against use of arrest or conviction history in af |

## Missed gold rules (in scope)

- BOS-RENT-P1 — Boston, MA / rent_increase_limits / Mass. H.3744 (193rd General Court) – study order H.5035 (2024-09-09) (docs D011)
- MA-RENT-P1 — MA / rent_increase_limits / Initiative Petition 25-21 (Mass. 2026); Cella v. Attorney General (SJC, decided 2026-06-23) (docs )

## Extra rules (no gold match)

- r-0002 — Berkeley, CA / application_screening_fees / BMC 13.78.010 (D005): Notification of state law limitation on tenant screening fees (BMC 13.78.010)
- r-0012 — Boston, MA / screening_restrictions / Boston Fair Housing Commission regulations; see also M.G.L. c. 151B, § 4(10) (D012): Boston fair housing protection for renters using rental assistance
- r-0014 — CA / application_screening_fees / Cal. Civ. Code § 1950.6 (D026): California application screening fee cap and conditions (Civ. Code § 1950.6)
- r-0015 — CA / just_cause_eviction / Cal. Civ. Code § 1946.2 (D023): California Tenant Protection Act - just cause for termination
- r-0017 — CA / screening_restrictions / Cal. Code Regs. tit. 2, § 12265 (Civil Rights Council regulations, eff. 2020-01-01) (D015): Criminal history screening limits (Civil Rights Council regulations)
- r-0019 — CA / security_deposits / Cal. Civ. Code § 1950.5 (D025): California residential security deposit cap and return rules (Civ. Code § 1950.5)
- r-0020 — Cambridge, MA / algorithmic_rent_setting / Cambridge City Council policy order (June 2026), directing city manager to draft ordinance language; no ordinance cited (D030): Cambridge policy order initiating ban on algorithmic rent-setting services
- r-0027 — Jersey City, NJ / algorithmic_rent_setting / Jersey City ordinance banning rent-setting algorithms (sponsor Councilman James Solomon), approved May 2025; ordinance number not stated in source (D035): Jersey City ban on rent-setting algorithms (RealPage-type software)
- r-0030 — Los Angeles, CA / just_cause_eviction / L.A.M.C. §§ 151.09, 165.03, 165.06; L.A.M.C. §§ 47.06-47.07 (D043): Relocation assistance for no-fault evictions under the RSO and JCO
- r-0032 — Los Angeles, CA / screening_restrictions / L.A.M.C. § 45.67 (D038): LAMC Sec. 45.67 Prohibited Activities (source-of-income discrimination)
- r-0036 — MA / application_screening_fees / M.G.L. c. 112, § 87DDD½, as amended by St. 2025, c. 9, § 43 (D057): Broker fee payable only by the party who engaged the broker
- r-0040 — MA / screening_restrictions / M.G.L. c. 151B, § 4(10) (D049): Source-of-income / housing subsidy discrimination ban (M.G.L. c. 151B, § 4(10))
- r-0045 — NJ / just_cause_eviction / N.J.S.A. 2A:18-61.3 (D067): Anti-Eviction Act: good cause required for lease non-renewal
- r-0047 — NJ / screening_restrictions / N.J.S.A. 10:5-12 (NJ Law Against Discrimination) (D068): NJ Law Against Discrimination: source of lawful income / rent payment protection
- r-0049 — NJ / security_deposits / N.J.S.A. 46:8-21.2; N.J.S.A. 46:8-19; N.J.S.A. 46:8-21.1 (D067): NJ Security Deposit Law: cap of 1.5 months' rent
- r-0050 — NJ / security_deposits / N.J.S.A. 46:8-26 (D064): NJ Security Deposit Act: application of act
- r-0051 — Newark, NJ / rent_increase_limits / Newark Rev. Gen. Ord. § 19:2-22 (D070): Newark Rent Control - limitation on increases (25% ceiling) and exemptions
- r-0052 — Newark, NJ / rent_increase_limits / Newark, N.J. Code § 19:2-3.1 (D070): Newark Rent Control: annual CPI-based rent increase cap
- r-0054 — San Diego, CA / algorithmic_rent_setting / S.D. Mun. Code § 98.1103 (proposed; Ord. O-2025-107) (D076): Prohibition of Anti-Competitive Automated Rent Price-Fixing Ordinance (proposed SDMC Div. 11)
- r-0056 — San Diego, CA / screening_restrictions / San Diego Municipal Code §§ 98.0801-98.0806 (Ord. O-20986 N.S.) (D075): San Diego Prohibition of Discrimination Based on a Tenant's Source of Income
- r-0059 — San Francisco, CA / rent_increase_limits / S.F. Admin. Code ch. 37 (Rent Ordinance), § 37.3 (D080): San Francisco annual allowable rent increase (3/1/2026\u20132/28/2027)
- r-0062 — Santa Ana, CA / algorithmic_rent_setting / Santa Ana Municipal Code (algorithmic rent-setting ordinance; ordinance number not stated in source) (D086): Santa Ana ban on algorithmic rent-setting devices
- r-0063 — Santa Ana, CA / algorithmic_rent_setting / Santa Ana Ordinance No. NS-3090 (D002): Santa Ana Ordinance NS-3090 (automated rent price-fixing)

## Negative findings

- found: BOS-ALG-00 ← n-0027 (in_force) No rule at this level
- found: BOS-DEP-00 ← n-0025 (in_force) No rule at this level
- found: BOS-FEE-00 ← n-0026 (in_force) No rule at this level
- found: BOS-RENT-00 ← r-0010 (failed) H.3744 Boston rent stabilization home rule petition (not enacted)
- found: CAM-FEE-00 ← n-0030 (in_force) No rule at this level
- found: HOB-DEP-00 ← n-0018 (in_force) No rule at this level
- found: HOB-FEE-00 ← n-0019 (in_force) No rule at this level
- found: HOB-JUST-00 ← n-0017 (in_force) No rule at this level
- found: HOB-SCRN-00 ← n-0020 (in_force) No rule at this level
- found: JC-DEP-00 ← n-0014 (in_force) No rule at this level
- found: JC-FEE-00 ← n-0015 (in_force) No rule at this level
- found: LA-ALG-00 ← n-0004 (in_force) No rule at this level
- found: LA-FEE-00 ← n-0003 (in_force) No rule at this level
- found: MA-RENT-00 ← r-0038 (in_force) No local rent control permitted (state bar), G.L. c. 40P, § 4
- found: NWK-ALG-00 ← n-0024 (in_force) No rule at this level
- found: NWK-DEP-00 ← n-0022 (in_force) No rule at this level
- found: NWK-JUST-00 ← n-0021 (in_force) No rule at this level
- found: SA-FEE-00 ← n-0011 (in_force) No rule at this level
- found: SA-SCRN-00 ← n-0012 (in_force) No rule at this level
- found: SD-DEP-00 ← n-0007 (in_force) No rule at this level
- found: SD-FEE-00 ← n-0008 (in_force) No rule at this level
- extra: r-0009 — Boston, MA / just_cause_eviction / H.3744 Boston tenant eviction protections home rule petition (not enacted) (D011)
- extra: r-0039 — MA / rent_increase_limits / 2026 statewide rent control ballot question (struck by SJC) (D059)
- extra: r-0046 — NJ / rent_increase_limits / No statewide rent control (municipal option); rent increase notice and unconscionability standard (D067)
- extra: n-0023 — Newark, NJ / application_screening_fees / No rule at this level (D066)
- extra: n-0028 — Cambridge, MA / rent_increase_limits / No rule at this level (D048)
- extra: n-0001 — MA / just_cause_eviction / No rule at this level (None)
- extra: n-0002 — MA / algorithmic_rent_setting / No rule at this level (None)
- extra: n-0005 — San Francisco, CA / application_screening_fees / No rule at this level (None)
- extra: n-0006 — San Diego, CA / rent_increase_limits / No rule at this level (None)
- extra: n-0009 — San Diego, CA / algorithmic_rent_setting / No rule at this level (None)
- extra: n-0010 — Santa Ana, CA / security_deposits / No rule at this level (None)
- extra: n-0013 — Jersey City, NJ / just_cause_eviction / No rule at this level (None)
- extra: n-0016 — Jersey City, NJ / screening_restrictions / No rule at this level (None)
- extra: n-0029 — Cambridge, MA / security_deposits / No rule at this level (None)
- extra: n-0031 — Cambridge, MA / algorithmic_rent_setting / No rule at this level (None)
