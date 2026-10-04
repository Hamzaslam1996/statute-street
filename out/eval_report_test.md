# Module A evaluation

Gold set: `gold/rules/test.json` — custom  
Our rules: 61 from 104 extracted document(s)  
Gold rules in scope (source doc extracted): 15 of 15 positive, 11 of 11 negative findings

| Metric | Value |
|---|---|
| Found (recall) | 15/15 = 100% |
| Missed | 0 |
| Extra (no gold match) | 46 |
| Extra colliding with a negative finding | 1 |
| Negative findings found / missed / extra | 11 / 0 / 26 |
| Status agrees | 15/15 = 100% |
| Effective date agrees (exact or both null) | 9/15 = 60% (3 exact dates, 6 both null, 6 differ, of which 1 same year) |
| Citation similarity (mean) | 88/100 |
| Key value similarity (mean) | 66/100 |
| Quote check pass rate (first attempt) | 141/141 = 100% |
| Records dropped for bad quotes | 0 |

## Matched rules

| Gold id | Ours | Status (gold / ours) | Eff. date (gold / ours) | Cite score | Key value (gold / ours) |
|---|---|---|---|---|---|
| BOS-SCRN-01 | r-0012 | in_force / in_force | None / None | 78 | rental assistance / Section 8 voucher use is a protected cla / Ban on refusing rental assistance (Section 8, SSDI and veter |
| CA-DEP-01 | r-0019 | in_force / in_force | 2024-07-01 / None | 100 | 1 month's rent (2 months for qualifying small landlords) / Maximum deposit of 1 month's rent (2 months' rent for qualif |
| CA-FEE-01 | r-0014 | in_force / in_force | None / None | 100 | $30 (1997 base) adjusted annually by CPI from 1998-01-01; no / $30 per applicant, adjustable annually for CPI increases beg |
| CA-JUST-01 | r-0015 | in_force / in_force | 2020-01-01 / 2024-04-01 | 100 | just cause required after 12 months of occupancy; 1 month re / Just cause required after 12 months' occupancy; no-fault rel |
| LA-JUST-02 | r-0028 | in_force / in_force | None / None | 62 | Landlord may not evict from an RSO unit except on the legal  / Eviction only for listed at-fault or no-fault just causes; r |
| LA-SCRN-01 | r-0031 | in_force / in_force | 2020-01-01 / None | 71 | source of income (incl. housing vouchers) protected / Prohibition on source-of-income discrimination in renting, t |
| MA-FEE-02 | r-0035 | in_force / in_force | 2025-08-01 / 2025-08-01 | 70 | broker fee payable only by the party who engaged the broker / Broker fee payable only by the party (lessor or tenant) who  |
| MA-SCRN-01 | r-0041 | in_force / in_force | None / None | 86 | recipients of public assistance / housing subsidies are prot / Ban on refusing or discriminating against tenants/applicants |
| NJ-DEP-01 | r-0051 | in_force / in_force | None / None | 100 | 1.5 months' rent / 1.5 months' rent maximum; annual increases limited to 10% of |
| NJ-SCRN-02 | r-0049 | in_force / in_force | None / None | 89 | source of lawful income (incl. vouchers) is a protected cate / Ban on refusing tenants based on source of lawful income (in |
| NWK-RENT-01 | r-0052 | in_force / in_force | None / 2024-09 | 89 | CPI change, capped at 4% per 12 months / CPI-U increase (NY-Northern NJ-Long Island), max 4% in any c |
| SA-ALG-01 | r-0062 | in_force / in_force | 2026-04 / 2026-04-02 | 100 | Ban on sale, licensing, provision and use of algorithmic ren / Ban on automated rent price-fixing |
| SD-ALG-01 | r-0054 | in_force / in_force | 2025-06-21 / 2025-06-21 | 93 | ban on sale/use of algorithmic rent-setting devices / Ban on selling, licensing, or using algorithmic rent-setting |
| SD-SCRN-01 | r-0056 | in_force / in_force | 2019-08-01 / 2018-10-18 | 81 | source of income (incl. vouchers) protected / Ban on source-of-income discrimination (includes federal, st |
| SF-RENT-01 | r-0059 | in_force / in_force | 2026-03-01 / 2026-03-01 | 95 | 1.6% (2026-03-01 to 2027-02-28); formula 60% of CPI / 1.6% annual allowable increase (3/1/2026–2/28/2027) |

## Missed gold rules (in scope)

- none

## Extra rules (no gold match)

- r-0001 — Berkeley, CA / algorithmic_rent_setting / Berkeley Municipal Code § 13.63.030 (Ord. No. 7,992-N.S.) (D001): Prohibition on coordinated pricing algorithms to set rents or manage occupancy (BMC ch. 13.63)
- r-0002 — Berkeley, CA / application_screening_fees / BMC 13.78.010 (D005): Notification of state law limitation on tenant screening fees (BMC 13.78.010)
- r-0003 — Berkeley, CA / application_screening_fees / BMC 13.78.016 (D005): Prohibition of non-refundable application fees for existing tenancies (BMC 13.78.016)
- r-0004 — Berkeley, CA / just_cause_eviction / Berkeley Municipal Code ch. 13.76 (Rent Stabilization and Eviction for Good Cause Ordinance), as amended by Measure BB (Nov. 2024) (D006): Berkeley just cause eviction rules as amended by Measure BB
- r-0005 — Berkeley, CA / rent_increase_limits / Berkeley Municipal Code § 13.76.110(A); Berkeley Rent Stabilization Board Regulation 1148 (D008): Berkeley 2026 Annual General Adjustment (AGA), Rent Board Regulation 1148
- r-0006 — Berkeley, CA / screening_restrictions / Berkeley Municipal Code ch. 13.106 (D003): Ronald V. Dellums Fair Chance Access to Housing Ordinance
- r-0007 — Berkeley, CA / security_deposits / Berkeley Municipal Code ch. 13.76 (Rent Stabilization and Eviction for Good Cause Ordinance) (D009): Berkeley security deposit interest coverage
- r-0008 — Boston, MA / just_cause_eviction / Boston Municipal Code § 10-11.7 (Housing Stability Notification Act) (D014): Boston Housing Stability Notification Act
- r-0009 — Boston, MA / just_cause_eviction / Mass. H.3744 (193rd General Court, 2023-2024) (D011): H.3744 Boston tenant eviction protections home rule petition (not enacted)
- r-0010 — Boston, MA / rent_increase_limits / Mass. H.3744 (193rd General Court, 2023-2024) (D011): H.3744 Boston rent stabilization home rule petition (not enacted)
- r-0011 — Boston, MA / screening_restrictions / Boston DND Fair Chance Tenant Selection Policy (Feb. 2017) (D010): Boston Fair Chance Tenant Selection Policy (criminal history)
- r-0013 — CA / algorithmic_rent_setting / Cal. Bus. & Prof. Code § 16729 (D022): Cartwright Act ban on common pricing algorithms (AB 325)
- r-0016 — CA / rent_increase_limits / Cal. Civ. Code § 1947.12 (D024): Statewide rent cap (Tenant Protection Act), Civ. Code § 1947.12
- r-0017 — CA / screening_restrictions / Cal. Code Regs. tit. 2, § 12265 (Civil Rights Council regulations, eff. 2020-01-01) (D015): Criminal history screening limits (Civil Rights Council regulations)
- r-0018 — CA / screening_restrictions / Cal. Gov. Code § 12955 (D027): Source-of-income discrimination ban and subsidy-tenant credit/income screening limits (FEHA)
- r-0020 — Cambridge, MA / algorithmic_rent_setting / Cambridge City Council policy order (June 2026), directing city manager to draft ordinance language; no ordinance cited (D030): Cambridge policy order initiating ban on algorithmic rent-setting services
- r-0021 — Cambridge, MA / just_cause_eviction / Cambridge Municipal Code ch. 8.71 (D031): Tenants Rights and Resources Notification Ordinance (Cambridge M.C. ch. 8.71)
- r-0022 — Cambridge, MA / screening_restrictions / Cambridge Municipal Code ch. 14.04 (Fair Housing Ordinance) (D029): Cambridge Fair Housing Ordinance: source-of-income protection (incl. Section 8)
- r-0023 — Hoboken, NJ / algorithmic_rent_setting / Hoboken Code § 158-2 (Ord. No. B-781) (M_HOB-ALG-01_Hoboken_ch158_ecode360): Algorithmic rent fixing in rental housing market prohibited
- r-0024 — Hoboken, NJ / rent_increase_limits / Hoboken City Code § 158-1 (Ord. No. B-750) (D034): Mandatory disclosures for rental increases over 10%
- r-0025 — Hoboken, NJ / rent_increase_limits / Hoboken Code § 155-5 (D032): Hoboken Rent Control: annual rent increase cap (§ 155-5)
- r-0026 — Jersey City, NJ / algorithmic_rent_setting / Jersey City Code § 218-12 (Ord. 25-057) (M_JC-ALG-01_Ord_25-057_adopted): Preventing Algorithmic Rent-Fixing in the Rental Housing Market (Ord. 25-057, § 218-12)
- r-0027 — Jersey City, NJ / rent_increase_limits / Jersey City Municipal Code ch. 260 (D036): Jersey City Rent Control Ordinance (Municipal Code Chapter 260)
- r-0029 — Los Angeles, CA / just_cause_eviction / L.A.M.C. §§ 151.09, 165.03, 165.06; L.A.M.C. §§ 47.06-47.07 (D043): Relocation assistance for no-fault evictions under the RSO and JCO
- r-0030 — Los Angeles, CA / rent_increase_limits / L.A.M.C. ch. XV, art. 1, § 151.00 et seq. (Rent Stabilization Ordinance) (D041): Los Angeles Rent Stabilization Ordinance (RSO) allowable rent increases
- r-0032 — Los Angeles, CA / security_deposits / L.A.M.C. § 151.06.02 B (M_LA-JUST-02_LAMC_ch15_art1_151): LA payment of interest on security deposits (LAMC § 151.06.02)
- r-0033 — MA / algorithmic_rent_setting / H.5222, 194th Gen. Court (Mass. 2025-2026) (new draft of H.1564) (D045): H.5222 - An Act relative to preventing algorithmic rent fixing in the rental housing market
- r-0034 — MA / algorithmic_rent_setting / Mass. S. 2983, 194th Gen. Ct. (2025-2026) (D046): An Act prohibiting algorithmic rent setting (S.2983)
- r-0036 — MA / application_screening_fees / M.G.L. c. 186, § 15B; 254 C.M.R. 7 (D054): No application fees by landlords (M.G.L. c. 186, § 15B)
- r-0037 — MA / rent_increase_limits / Initiative Petition 25-21; Mass. Const. Amend. art. 48, The Initiative, II, § 2; Cella v. Attorney General, SJC-13893 (2026) (M_MA-RENT-P1_Cella_v_AG_SJC-13893): Initiative Petition 25-21 (statewide rent increase limit) barred from ballot
- r-0040 — MA / rent_increase_limits / Mass. Const. amend. art. 48, The Initiative, Pt. II, § 2 (SJC ruling, June 2026) (D059): 2026 statewide rent control ballot question (struck by SJC)
- r-0042 — MA / screening_restrictions / M.G.L. c. 6, § 172(a)(3), (c) (D094): CORI access limits for evaluating rental housing applicants
- r-0043 — MA / security_deposits / M.G.L. c. 186, § 15B (D052): Massachusetts security deposit limits and handling (M.G.L. c. 186, § 15B)
- r-0044 — NJ / algorithmic_rent_setting / P.L. 2026, c.43 (C.56:9-20 to 56:9-26) (D069): Forbidding the Algorithmic Inflation of Rent (FAIR) Act
- r-0045 — NJ / application_screening_fees / N.J.S.A. 46:8-18.1; P.L. 2025, c.405 (D066): Residential rental application fee cap (P.L. 2025, c.405)
- r-0046 — NJ / just_cause_eviction / N.J.S.A. 2A:18-61.1 et seq.; N.J.S.A. 2A:18-53 (D067): Anti-Eviction Act (good cause required)
- r-0047 — NJ / just_cause_eviction / N.J.S.A. 2A:18-61.3 (D067): Anti-Eviction Act: good cause required for lease non-renewal
- r-0050 — NJ / screening_restrictions / N.J.S.A. 46:8-52 et seq. (P.L. 2021, c.110) (D065): Fair Chance in Housing Act (criminal record screening limits)
- r-0053 — Newark, NJ / screening_restrictions / Newark Municipal Code § 2:31-1 to 2:31-9 (Ord. 6 PSF-B, 4-15-2015) (D072): Newark Ban the Box - Housing (criminal record check practices)
- r-0055 — San Diego, CA / just_cause_eviction / San Diego Municipal Code §§ 98.0701–98.0710 (D073): San Diego Residential Tenant Protections (just cause for termination of tenancy)
- r-0057 — San Francisco, CA / algorithmic_rent_setting / S.F. Admin. Code § 37.10C (D081): S.F. Rent Ordinance Section 37.10C - Prohibition on Algorithmic Rent-Setting Devices
- r-0058 — San Francisco, CA / just_cause_eviction / S.F. Admin. Code § 37.9(a) (D079): San Francisco Rent Ordinance just cause eviction (S.F. Admin. Code § 37.9(a))
- r-0060 — San Francisco, CA / screening_restrictions / S.F. Police Code art. 49 (Fair Chance Ordinance) (D078): Fair Chance Ordinance (affordable housing)
- r-0061 — San Francisco, CA / security_deposits / S.F. Admin. Code § 49.2 (D083): SF security deposit interest rate
- r-0063 — Santa Ana, CA / just_cause_eviction / Santa Ana Municipal Code, Just Cause Eviction Ordinance (section number not stated in source) (D085): Santa Ana Just Cause Eviction Ordinance
- r-0064 — Santa Ana, CA / rent_increase_limits / Santa Ana Municipal Code, Rent Stabilization Ordinance (section number not stated in source) (D085): Santa Ana Rent Stabilization Ordinance

## Collisions with negative findings (gold says: no rule at this level)

- r-0020 Cambridge City Council policy order (June 2026), directing city manager to draft ordinance language; no ordinance cited vs CAM-ALG-00: No algorithmic_rent_setting rule at city level

## Negative findings

- found: CAM-ALG-00 ← n-0030 (in_force) No rule at this level
- found: CAM-DEP-00 ← n-0028 (in_force) No rule at this level
- found: CAM-RENT-00 ← n-0027 (in_force) No rule at this level
- found: JC-JUST-00 ← n-0012 (in_force) No rule at this level
- found: JC-SCRN-00 ← n-0015 (in_force) No rule at this level
- found: MA-JUST-00 ← n-0001 (in_force) No rule at this level
- found: NJ-RENT-00 ← r-0048 (in_force) No statewide rent control (municipal option); rent increase notice and unconscionability standard
- found: NWK-FEE-00 ← n-0022 (in_force) No rule at this level
- found: SA-DEP-00 ← n-0009 (in_force) No rule at this level
- found: SD-RENT-00 ← n-0006 (in_force) No rule at this level
- found: SF-FEE-00 ← n-0005 (in_force) No rule at this level
- extra: r-0009 — Boston, MA / just_cause_eviction / H.3744 Boston tenant eviction protections home rule petition (not enacted) (D011)
- extra: r-0010 — Boston, MA / rent_increase_limits / H.3744 Boston rent stabilization home rule petition (not enacted) (D011)
- extra: r-0037 — MA / rent_increase_limits / Initiative Petition 25-21 (statewide rent increase limit) barred from ballot (M_MA-RENT-P1_Cella_v_AG_SJC-13893)
- extra: r-0038 — MA / rent_increase_limits / No local rent control permitted (state bar), G.L. c. 40P, § 4 (D048)
- extra: r-0039 — MA / rent_increase_limits / No rent control permitted (state bar, G. L. c. 40P) (M_MA-RENT-P1_Cella_v_AG_SJC-13893)
- extra: r-0040 — MA / rent_increase_limits / 2026 statewide rent control ballot question (struck by SJC) (D059)
- extra: n-0002 — MA / algorithmic_rent_setting / No rule at this level (None)
- extra: n-0003 — Los Angeles, CA / application_screening_fees / No rule at this level (None)
- extra: n-0004 — Los Angeles, CA / algorithmic_rent_setting / No rule at this level (None)
- extra: n-0007 — San Diego, CA / security_deposits / No rule at this level (None)
- extra: n-0008 — San Diego, CA / application_screening_fees / No rule at this level (None)
- extra: n-0010 — Santa Ana, CA / application_screening_fees / No rule at this level (None)
- extra: n-0011 — Santa Ana, CA / screening_restrictions / No rule at this level (None)
- extra: n-0013 — Jersey City, NJ / security_deposits / No rule at this level (None)
- extra: n-0014 — Jersey City, NJ / application_screening_fees / No rule at this level (None)
- extra: n-0016 — Hoboken, NJ / just_cause_eviction / No rule at this level (None)
- extra: n-0017 — Hoboken, NJ / security_deposits / No rule at this level (None)
- extra: n-0018 — Hoboken, NJ / application_screening_fees / No rule at this level (None)
- extra: n-0019 — Hoboken, NJ / screening_restrictions / No rule at this level (None)
- extra: n-0020 — Newark, NJ / just_cause_eviction / No rule at this level (None)
- extra: n-0021 — Newark, NJ / security_deposits / No rule at this level (None)
- extra: n-0023 — Newark, NJ / algorithmic_rent_setting / No rule at this level (None)
- extra: n-0024 — Boston, MA / security_deposits / No rule at this level (None)
- extra: n-0025 — Boston, MA / application_screening_fees / No rule at this level (None)
- extra: n-0026 — Boston, MA / algorithmic_rent_setting / No rule at this level (None)
- extra: n-0029 — Cambridge, MA / application_screening_fees / No rule at this level (None)
