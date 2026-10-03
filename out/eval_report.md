# Module A evaluation

Gold set: `gold/gold_rules.json` — SILVER (AI draft, unverified)  
Our rules: 94 from 85 extracted document(s)  
Gold rules in scope (source doc extracted): 43 of 44 positive, 7 of 9 negative findings

| Metric | Value |
|---|---|
| Found (recall) | 42/43 = 98% (5 by jurisdiction+category only, marked †) |
| Missed | 1 |
| Extra (no gold match) | 52 |
| Extra colliding with a negative finding | 2 |
| Negative findings found / missed / extra | 4 / 3 / 1 |
| Status agrees | 42/42 = 100% |
| Effective date exact / same year | 11/42 = 26% / 16/42 |
| Citation similarity (mean) | 85/100 |
| Key value similarity (mean) | 63/100 |
| Quote check pass rate (first attempt) | 114/115 = 99% |
| Records dropped for bad quotes | 0 |

## Matched rules

| Gold id | Ours | Status (gold / ours) | Eff. date (gold / ours) | Cite score | Key value (gold / ours) |
|---|---|---|---|---|---|
| BK-ALG-01 | r-0001 | in_force / in_force | 2026-03-01 / 2026-01 | 100 | Prohibits use of algorithmic devices to set rents/occupancy / Ban on coordinated rent-pricing algorithms |
| BK-RENT-01 | r-0009 | in_force / in_force | None / None | 94 | Annual General Adjustment set by Rent Board / AGA is CPI-based, maximum 5% |
| BK-SCR-01 | r-0011 | in_force / in_force | 2020-03-12 / None | 91 | Prohibits asking about or using criminal history in rental d / Ban on inquiring about or using criminal history in rental h |
| BOS-JC-01 | r-0013 | in_force / in_force | 2021-01-01 / 2020-11-06 | 82 | Landlords must give tenants a notice of rights with any noti / Notice of Tenants' Rights and Resources delivered with the N |
| BOS-SCR-01 | r-0017 | in_force / in_force | None / None | 100 | Prohibits discrimination incl. based on source of income / h / Ban on refusing rental assistance (Section 8, SSDI and veter |
| CA-ALG-01 | r-0019 | in_force / in_force | 2026-01-01 / 2026-01-01 | 87 | Unlawful to use/distribute a common pricing algorithm in res / Ban on using or distributing common pricing algorithms to re |
| CA-DEP-01 | r-0029 | in_force / in_force | 2024-07-01 / None | 100 | 1 month's rent; 2 months for qualifying small landlords / Maximum deposit of 1 month's rent (2 months' rent for qualif |
| CA-FEE-01 | r-0020 | in_force / in_force | None / None | 100 | Actual out-of-pocket cost, capped at CPI-adjusted statutory  / $30 per applicant, adjustable annually for CPI increases beg |
| CA-JC-01 | r-0021 | in_force / in_force | 2020-01-01 / 2024-04-01 | 100 | Just cause required after 12 months' continuous occupancy / Just cause required after 12 months' occupancy; no-fault rel |
| CA-RENT-01 | r-0022 | in_force / in_force | 2020-01-01 / 2024-04-01 | 100 | 5% + CPI, max 10% per 12 months / 5% + CPI change, max 10% (whichever is lower), per 12 months |
| CA-SCR-01 | r-0025 | in_force / in_force | 2020-01-01 / None | 100 | Housing vouchers count as income; refusal based on source of / Ban on source-of-income discrimination, including Section 8  |
| CAM-SCR-01 | r-0032 | in_force / in_force | None / None | 72 | Local enforcement of housing discrimination protections incl / Source of income (including Section 8 and public benefits) i |
| HOB-ALG-01 | r-0033 | in_force / in_force | 2025-07-09 / 2025-07 | 90 | Prohibits landlords from using rent algorithms with nonpubli / Ban on software/algorithm/data-sharing coordination of rents |
| HOB-FEE-01 | r-0035 | in_force / in_force | 2025-04-02 / 2025-04 | 82 | Landlord must itemise costs and state whether a rent algorit / Disclosures required for renewal rent increases of more than |
| HOB-RENT-01 | r-0036 | in_force / in_force | None / 2023-02 | 84 | Annual increase capped at CPI, max 5% / Lesser of 5% or CPI change; one increase per 12 months |
| JC-ALG-01 | r-0037 | in_force / in_force | 2025-06 / 2025-06 | 100 | Prohibits use of rent-setting algorithms (e.g., RealPage); p / Ban on landlord use of algorithmic rent coordination service |
| JC-RENT-01 | r-0039 | in_force / in_force | None / None | 100 | Annual increase capped at CPI, max 4% (verify) / Rent control under Ch. 260; all 1-4 unit properties are exem |
| LA-DEP-01 | r-0046 | in_force / in_force | None / None | 76 | Landlord must pay interest on security deposits for RSO unit / Interest paid monthly or yearly at the City-set annual rate  |
| LA-JC-01 | r-0040 | in_force / in_force | 2023-01-27 / None | 94 | Just cause required after 6 months or first lease expiry, wh / Eviction only for listed at-fault or no-fault just causes; r |
| LA-RENT-01 † | r-0043 | in_force / in_force | 2026-02-02 / 2026-02-02 | 55 | Annual allowable increase set by LAHD formula (2026 formula; / Once per 12 months by the allowable rent increase percentage |
| MA-ALG-P1 | r-0050 | pending / pending | None / None | 96 | Would prohibit algorithmic rent setting statewide / Would prohibit algorithmic rent setting (bill text not in th |
| MA-ALG-P2 | r-0047 | pending / pending | None / None | 64 | Would prohibit algorithmic rent fixing in the rental housing / Pending bills to ban algorithmic rent-setting |
| MA-DEP-01 | r-0058 | in_force / in_force | None / None | 74 | First month's rent / Security deposit capped at 1 month's rent (plus first month, |
| MA-FEE-01 | r-0052 | in_force / in_force | None / None | 67 | Only first month's rent, last month's rent, security deposit / Landlords may not charge application fees; only first, last, |
| MA-FEE-02 | r-0051 | in_force / in_force | 2025-08-01 / 2025-08-01 | 83 | Tenant pays a broker fee only if the tenant engaged the brok / Broker fee payable only by the party (lessor or tenant) who  |
| MA-SCR-01 | r-0057 | in_force / in_force | None / None | 86 | Unlawful to discriminate against recipients of public assist / Ban on refusing or discriminating against tenants/applicants |
| NJ-ALG-01 † | r-0060 | not_yet_effective / not_yet_effective | 2027-07-01 / 2027-07-01 | 54 | Prohibits use/sale of rent-setting algorithms using nonpubli / Ban on algorithmic rent-setting coordination (use of coordin |
| NJ-DEP-01 | r-0072 | in_force / in_force | None / None | 100 | 1.5 months' rent / 1.5 months' rent maximum; annual increases limited to 10% of |
| NJ-FEE-01 | r-0061 | in_force / in_force | 2026-05-01 / 2026-05-01 | 79 | $50 cap; penalty up to $500 per violation / $50 maximum, adjusted annually for CPI increases (NY-Norther |
| NJ-JC-01 | r-0064 | in_force / in_force | 1974-06-25 / None | 100 | Eviction only on enumerated good-cause grounds / Good cause required to evict or fail to renew a residential  |
| NJ-SCR-01 | r-0070 | in_force / in_force | 2022-01-01 / 2022-01-01 | 89 | No criminal-history inquiry before conditional offer; limits / No criminal-record inquiry before conditional offer; after o |
| NJ-SCR-02 | r-0069 | in_force / in_force | None / None | 100 | Unlawful to refuse rental based on lawful source of income i / Source of lawful income may not be a basis for refusing to r |
| NWK-RENT-01 † | r-0075 | in_force / in_force | None / 2024-09 | 51 | Annual increase capped at CPI, max 4% (verify) / CPI-U increase (NY-Northern NJ-Long Island), max 4% |
| SA-ALG-01 | r-0095 | in_force / in_force | 2026-04 / 2026-04-02 | 87 | Prohibits use of anticompetitive rent-setting software / Ban on automated rent price-fixing |
| SA-JC-01 † | r-0096 | in_force / in_force | 2021-11-19 / 2021-11-19 | 47 | Eviction only for enumerated causes; relocation assistance / Just cause required after 30 days; no-fault termination requ |
| SA-RENT-01 † | r-0099 | in_force / in_force | 2021-11-19 / None | 47 | Lesser of 3% or 80% of CPI per year / Lesser of 3% or 80% of CPI change; currently 2.87% (9/1/2026 |
| SD-ALG-01 | r-0081 | in_force / in_force | 2025-06-21 / 2025-06 | 83 | Prohibits sale and use of algorithmic devices to set rents / Ban on algorithmic rent-setting devices (similar to San Fran |
| SD-JC-01 | r-0083 | in_force / in_force | 2023-06-24 / 2023-06-24 | 89 | Just cause and relocation assistance beyond state law / Just cause required; no-fault relocation assistance = 2 mont |
| SF-ALG-01 | r-0085 | in_force / in_force | 2024-10-14 / 2024-10-14 | 100 | Prohibits sale or use of algorithmic devices to set rents or / Ban on sale or use of algorithmic rent-setting devices |
| SF-JC-01 | r-0086 | in_force / in_force | None / None | 100 | Eviction only for the enumerated just causes / Eviction only for one of 17 enumerated just causes (Section  |
| SF-RENT-01 | r-0090 | in_force / in_force | 2026-03-01 / 2026-03-01 | 82 | 1.6% for 1 Mar 2026 - 28 Feb 2027 (60% of CPI) / 1.6% for March 1, 2026 – February 28, 2027 |
| SF-SCR-01 | r-0091 | in_force / in_force | None / None | 100 | Limits use of criminal history in affordable-housing decisio / Protection against use of arrest or conviction history in af |

## Missed gold rules (in scope)

- SD-SCR-01 — San Diego, CA / screening_restrictions / S.D. Mun. Code ch. 9, art. 8, div. 8 (docs D075)

## Extra rules (no gold match)

- r-0002 — Berkeley, CA / algorithmic_rent_setting / Berkeley Municipal Code § 13.63.030 (Ord. No. 7,992-N.S.) (D001): Prohibition on coordinated pricing algorithms to set rents or manage occupancy (BMC ch. 13.63)
- r-0003 — Berkeley, CA / application_screening_fees / BMC 13.78.010 (D005): Notification of state law limitation on tenant screening fees (BMC 13.78.010)
- r-0004 — Berkeley, CA / application_screening_fees / BMC 13.78.016 (D005): Prohibition of non-refundable application fees for existing tenancies (BMC 13.78.016)
- r-0005 — Berkeley, CA / just_cause_eviction / Berkeley Municipal Code ch. 13.76 (Rent Stabilization and Eviction for Good Cause Ordinance) (D009): Berkeley Eviction for Good Cause coverage
- r-0006 — Berkeley, CA / just_cause_eviction / Berkeley Municipal Code ch. 13.76 (Rent Stabilization and Eviction for Good Cause Ordinance), as amended by Measure BB (Nov. 2024) (D006): Berkeley just cause eviction rules as amended by Measure BB
- r-0007 — Berkeley, CA / just_cause_eviction / Berkeley Municipal Code ch. 13.76 (Rent Stabilization and Good Cause for Eviction Ordinance); Berkeley Ellis Implementation Ordinance (BMC ch. 13.77) (D004): Berkeley relocation assistance for owner move-in and Ellis Act evictions (2026 adjustment)
- r-0008 — Berkeley, CA / rent_increase_limits / Berkeley Municipal Code ch. 13.76 (Rent Stabilization and Eviction for Good Cause Ordinance) (D009): Berkeley Rent Stabilization Ordinance coverage (rent control)
- r-0010 — Berkeley, CA / rent_increase_limits / Berkeley Municipal Code § 13.76.110(A); Berkeley Rent Stabilization Board Regulation 1148 (D008): Berkeley 2026 Annual General Adjustment (AGA), Rent Board Regulation 1148
- r-0012 — Berkeley, CA / security_deposits / Berkeley Municipal Code ch. 13.76 (Rent Stabilization and Eviction for Good Cause Ordinance) (D007): Berkeley security deposit interest requirement
- r-0016 — Boston, MA / screening_restrictions / Boston DND Fair Chance Tenant Selection Policy (Feb. 2017) (D010): Boston Fair Chance Tenant Selection Policy - criminal history
- r-0018 — CA / algorithmic_rent_setting / Cal. Bus. & Prof. Code § 16729 (D022): Cartwright Act ban on common pricing algorithms (AB 325)
- r-0023 — CA / screening_restrictions / Cal. Code Regs. tit. 2, § 12265 (Civil Rights Council regulations, eff. 2020-01-01) (D015): Criminal history screening limits (Civil Rights Council regulations)
- r-0024 — CA / screening_restrictions / Cal. Gov. Code § 12955 (D027): Source-of-income discrimination ban and subsidy-tenant credit/income screening limits (FEHA)
- r-0026 — CA / screening_restrictions / Cal. Gov. Code § 12955 (as amended by SB 267 (2023)) (D015): Credit history use for subsidy holders (SB 267)
- r-0027 — CA / screening_restrictions / Cal. Gov. Code § 12955 (as amended by SB 329 (2019)) (D015): Source of income protection: 'No Section 8' policies prohibited (SB 329)
- r-0028 — CA / screening_restrictions / Cal. Gov. Code § 12955; 2 C.C.R. § 12265 (D016): FEHA limits on use of criminal history in tenant screening
- r-0030 — CA / security_deposits / Cal. Civ. Code § 1950.5 (as amended by AB 12) (D007): California security deposit cap (AB 12)
- r-0031 — Cambridge, MA / algorithmic_rent_setting / Cambridge City Council policy order (June 2026), directing city manager to draft ordinance language; no ordinance cited (D030): Cambridge policy order initiating ban on algorithmic rent-setting services
- r-0034 — Hoboken, NJ / algorithmic_rent_setting / Hoboken City Code § 158-2 (Ord. No. B-781) (D034): Algorithmic rent fixing in rental housing market prohibited
- r-0038 — Jersey City, NJ / algorithmic_rent_setting / Jersey City ordinance banning rent-setting algorithms (sponsor Councilman James Solomon), approved May 2025; ordinance number not stated in source (D035): Jersey City ban on rent-setting algorithms (RealPage-type software)
- r-0041 — Los Angeles, CA / just_cause_eviction / L.A.M.C. § 151.09 (D041): Los Angeles RSO just cause eviction and relocation assistance
- r-0042 — Los Angeles, CA / just_cause_eviction / L.A.M.C. §§ 151.09, 165.03, 165.06; L.A.M.C. §§ 47.06-47.07 (D043): Relocation assistance for no-fault evictions under the RSO and JCO
- r-0044 — Los Angeles, CA / rent_increase_limits / L.A.M.C. § 151.06 (Rent Stabilization Ordinance, annual allowable rent increase) (D042): Los Angeles RSO annual allowable rent increase
- r-0045 — Los Angeles, CA / screening_restrictions / L.A.M.C. § 45.67 (D038): LAMC Sec. 45.67 Prohibited Activities (source-of-income discrimination)
- r-0048 — MA / algorithmic_rent_setting / H.5222, 194th Gen. Court (Mass. 2025-2026) (new draft of H.1564) (D045): H.5222 - An Act relative to preventing algorithmic rent fixing in the rental housing market
- r-0049 — MA / algorithmic_rent_setting / Mass. S. 2983, 194th Gen. Ct. (2025-2026) (D046): An Act prohibiting algorithmic rent setting (S.2983)
- r-0053 — MA / just_cause_eviction / M.G.L. c. 186, § 11 (D050): Notice to quit for nonpayment of rent under written lease (M.G.L. c. 186, § 11)
- r-0054 — MA / just_cause_eviction / M.G.L. c. 186, § 18 (D053): Tenant reprisal (retaliation) protection, M.G.L. c. 186, § 18
- r-0059 — NJ / algorithmic_rent_setting / P.L. 2026, c. 43 (D060): New Jersey FAIR Act (Forbidding the Algorithmic Inflation of Rent)
- r-0062 — NJ / just_cause_eviction / N.J.S.A. 2A:18-61.1 (D062): NJ Anti-Eviction Act: grounds for removal of tenants
- r-0063 — NJ / just_cause_eviction / N.J.S.A. 2A:18-61.1 et seq. (D067): NJ Anti-Eviction Statute (statutory grounds for eviction)
- r-0065 — NJ / just_cause_eviction / N.J.S.A. 2A:18-61.3 (D067): Anti-Eviction Act: good cause required for lease non-renewal
- r-0067 — NJ / screening_restrictions / N.J.S.A. 10:5-12 (NJ Law Against Discrimination) (D068): NJ Law Against Discrimination: source of lawful income / rent payment protection
- r-0068 — NJ / screening_restrictions / N.J.S.A. 10:5-12(g)(4), (h)(4) (D061): NJ Law Against Discrimination: source-of-income protection in rental housing
- r-0071 — NJ / security_deposits / N.J.S.A. 46:8-21.2 (D063): NJ Security Deposit Limitation (N.J.S.A. 46:8-21.2)
- r-0073 — NJ / security_deposits / N.J.S.A. 46:8-26 (D064): NJ Security Deposit Act: application of act
- r-0074 — Newark, NJ / just_cause_eviction / Newark, N.J. Rev. Gen. Ord. § 19:2-14 (D070): Newark Rent Control: retaliatory eviction prohibited
- r-0076 — Newark, NJ / rent_increase_limits / Newark, N.J. Rev. Gen. Ord. § 19:2-18.1 (D070): Newark Rent Control: new construction exemption from increase limits
- r-0077 — Newark, NJ / rent_increase_limits / Newark, N.J. Rev. Gen. Ord. § 19:2-18.4 (D070): Newark Rent Control: rehabilitated vacant unit increase (10% max)
- r-0078 — Newark, NJ / rent_increase_limits / Newark, N.J. Rev. Gen. Ord. § 19:2-22 (D070): Newark Rent Control: 25% annual cap on rent increases
- r-0079 — Newark, NJ / screening_restrictions / Newark Municipal Code § 2:31-1 to 2:31-9 (Ord. 6 PSF-B, 4-15-2015) (D072): Newark Ban the Box - Housing (criminal record check practices)
- r-0080 — San Diego, CA / algorithmic_rent_setting / S.D. Mun. Code § 98.1103 (proposed; Ord. O-2025-107) (D076): Prohibition of Anti-Competitive Automated Rent Price-Fixing Ordinance (proposed SDMC Div. 11)
- r-0082 — San Diego, CA / algorithmic_rent_setting / San Diego Municipal Code § 98.1103 (Ord. O-21955 N.S.) (D074): San Diego Prohibition of Anti-Competitive Automated Rent Price Fixing (SDMC §98.1103)
- r-0084 — San Diego, CA / just_cause_eviction / San Diego Municipal Code §§ 98.0701–98.0710 (D073): San Diego Residential Tenant Protections (just cause for termination of tenancy)
- r-0087 — San Francisco, CA / just_cause_eviction / S.F. Admin. Code § 37.9C (D083): SF relocation payments for no-fault evictions
- r-0088 — San Francisco, CA / just_cause_eviction / S.F. Admin. Code § 37.9C; § 37.9A (Ellis Act relocation) (D082): San Francisco relocation payments for no-fault evictions (Rent Ordinance § 37.9C)
- r-0089 — San Francisco, CA / rent_increase_limits / S.F. Admin. Code ch. 37 (Rent Ordinance), § 37.3 (D080): San Francisco annual allowable rent increase (3/1/2026\u20132/28/2027)
- r-0092 — San Francisco, CA / security_deposits / S.F. Admin. Code § 49.2 (D083): SF security deposit interest rate
- r-0093 — Santa Ana, CA / algorithmic_rent_setting / Santa Ana Municipal Code (algorithmic rent-setting ordinance; ordinance number not stated in source) (D086): Santa Ana ban on algorithmic rent-setting devices
- r-0094 — Santa Ana, CA / algorithmic_rent_setting / Santa Ana Municipal Code, algorithmic rent-setting software ordinance (ordinance number and section not stated in source) (D087): Santa Ana ban on algorithmic rent-setting software
- r-0097 — Santa Ana, CA / just_cause_eviction / Santa Ana Municipal Code, Rent Stabilization and Just Cause Eviction Ordinance (D084): Santa Ana Just Cause Eviction Ordinance
- r-0098 — Santa Ana, CA / rent_increase_limits / Santa Ana Municipal Code, Rent Stabilization Ordinance (section number not stated in source) (D085): Santa Ana Rent Stabilization Ordinance

## Collisions with negative findings (gold says: no rule at this level)

- r-0053 M.G.L. c. 186, § 11 vs MA-JC-00: No statewide just-cause eviction statute
- r-0054 M.G.L. c. 186, § 18 vs MA-JC-00: No statewide just-cause eviction statute

## Negative findings

- found: NJ-RENT-00 ← r-0066 (in_force) No statewide rent control (municipal option); rent increase notice and unconscionability standard
- found: MA-RENT-00 ← r-0055 (in_force) No local rent control permitted (state bar), G.L. c. 40P, § 4
- found: MA-RENT-P1 ← r-0056 (failed) 2026 statewide rent control ballot question (struck by SJC)
- found: BOS-RENT-00 ← r-0015 (failed) H.3744 Boston rent stabilization home-rule petition (not enacted)
- missed: MA-JC-00 — No statewide just-cause eviction statute (docs D050, D051)
- missed: CAM-RENT-00 — No rent control in Cambridge (docs D048, D031)
- missed: LA-ALG-00 — No local algorithmic ban in force in Los Angeles (docs D039, D038)
- extra: r-0014 — Boston, MA / just_cause_eviction / H.3744 Boston tenant eviction protections home-rule petition (not enacted) (D011)
