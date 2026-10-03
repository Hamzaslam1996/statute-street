# Module A evaluation

Gold set: `gold/gold_rules.json` — SILVER (AI draft, unverified)  
Our rules: 22 from 14 extracted document(s)  
Gold rules in scope (source doc extracted): 13 of 44 positive, 4 of 9 negative findings

| Metric | Value |
|---|---|
| Found (recall) | 13/13 = 100% (2 by jurisdiction+category only, marked †) |
| Missed | 0 |
| Extra (no gold match) | 9 |
| Extra colliding with a negative finding | 4 |
| Status agrees | 13/13 = 100% |
| Effective date exact / same year | 5/13 = 38% / 5/13 |
| Citation similarity (mean) | 82/100 |
| Key value similarity (mean) | 64/100 |
| Quote check pass rate (first attempt) | 22/22 = 100% |
| Records dropped for bad quotes | 0 |

## Matched rules

| Gold id | Ours | Status (gold / ours) | Eff. date (gold / ours) | Cite score | Key value (gold / ours) |
|---|---|---|---|---|---|
| BK-ALG-01 | r-0001 | in_force / in_force | 2026-03-01 / None | 75 | Prohibits use of algorithmic devices to set rents/occupancy / Civil penalties up to $1,000 per violation (enforceable by C |
| CA-DEP-01 | r-0004 | in_force / in_force | 2024-07-01 / 2024-07-01 | 100 | 1 month's rent; 2 months for qualifying small landlords / 1 month's rent (2 months' rent for qualifying small landlord |
| CA-FEE-01 | r-0002 | in_force / in_force | None / None | 100 | Actual out-of-pocket cost, capped at CPI-adjusted statutory  / $30 per applicant, adjustable annually for CPI increases beg |
| CA-RENT-01 | r-0003 | in_force / in_force | 2020-01-01 / 2019-03-15 | 100 | 5% + CPI, max 10% per 12 months / 5% + CPI change, max 10% (whichever is lower), over any 12-m |
| HOB-ALG-01 | r-0008 | in_force / in_force | 2025-07-09 / None | 87 | Prohibits landlords from using rent algorithms with nonpubli / Prohibition on algorithmic price fixing; penalties up to a $ |
| HOB-FEE-01 | r-0009 | in_force / in_force | 2025-04-02 / None | 82 | Landlord must itemise costs and state whether a rent algorit / Disclosure required for increases of more than 10% year over |
| LA-RENT-01 † | r-0011 | in_force / in_force | 2026-02-02 / None | 41 | Annual allowable increase set by LAHD formula (2026 formula; / Once per 12 months, by the published allowable rent increase |
| MA-ALG-P1 † | r-0012 | pending / pending | None / None | 51 | Would prohibit algorithmic rent setting statewide / None |
| NJ-ALG-01 | r-0015 | not_yet_effective / not_yet_effective | 2027-07-01 / 2027-07-01 | 69 | Prohibits use/sale of rent-setting algorithms using nonpubli / Ban on algorithmic coordination of rental prices, material l |
| NJ-DEP-01 | r-0017 | in_force / in_force | None / None | 100 | 1.5 months' rent / 1.5 months' rent; annual additional security max 10% of curr |
| NJ-FEE-01 | r-0016 | in_force / in_force | 2026-05-01 / 2026-05-01 | 79 | $50 cap; penalty up to $500 per violation / $50 maximum, adjusted annually for CPI increases (NY-Norther |
| SF-ALG-01 | r-0018 | in_force / in_force | 2024-10-14 / 2024-10-14 | 100 | Prohibits sale or use of algorithmic devices to set rents or / Ban on sale or use of algorithmic rent-setting devices |
| SF-RENT-01 | r-0021 | in_force / in_force | 2026-03-01 / 2026-03-01 | 86 | 1.6% for 1 Mar 2026 - 28 Feb 2027 (60% of CPI) / 1.6% for March 1, 2026 – February 28, 2027 |

## Missed gold rules (in scope)

- none

## Extra rules (no gold match)

- r-0005 — CA / security_deposits / Cal. Civ. Code § 1950.5(g) (D025): Cal. Civ. Code § 1950.5 – Landlord photograph requirements
- r-0006 — CA / security_deposits / Cal. Civ. Code § 1950.5(h) (D025): Cal. Civ. Code § 1950.5 – Return of deposit and itemized statement within 21 days
- r-0007 — CA / security_deposits / Cal. Civ. Code § 1950.5(n) (D025): Cal. Civ. Code § 1950.5 – No 'nonrefundable' deposits
- r-0010 — Los Angeles, CA / just_cause_eviction / L.A.M.C. § 151.09 (D041): Los Angeles RSO - legal grounds for eviction and relocation assistance
- r-0013 — MA / rent_increase_limits / M.G.L. c. 40P, § 4 (D048): Statewide prohibition on rent control (M.G.L. c. 40P, § 4)
- r-0014 — MA / rent_increase_limits / Mass. Const. amend. art. 48 (Initiative Petitions, The Initiative, II, § 2); Mass. SJC ruling on rent control ballot petition (June 2026) (D059): Massachusetts 2026 rent control ballot initiative (struck by SJC)
- r-0019 — San Francisco, CA / just_cause_eviction / S.F. Admin. Code § 37.9A (D083): San Francisco Ellis Act eviction relocation payments (Rent Ordinance 37.9A)
- r-0020 — San Francisco, CA / just_cause_eviction / S.F. Admin. Code § 37.9C (D083): San Francisco relocation payments for no-fault evictions (Rent Ordinance 37.9C)
- r-0022 — San Francisco, CA / security_deposits / S.F. Admin. Code § 49.2 (D083): San Francisco security deposit interest rate (2026-27)

## Collisions with negative findings (gold says: no rule at this level)

- r-0013 M.G.L. c. 40P, § 4 vs MA-RENT-00: State bar on local rent control; no state rent cap
- r-0013 M.G.L. c. 40P, § 4 vs MA-RENT-P1: Rent control ballot question (IP 25-21) struck
- r-0014 Mass. Const. amend. art. 48 (Initiative Petitions, The Initiative, II, § 2); Mass. SJC ruling on rent control ballot petition (June 2026) vs MA-RENT-00: State bar on local rent control; no state rent cap
- r-0014 Mass. Const. amend. art. 48 (Initiative Petitions, The Initiative, II, § 2); Mass. SJC ruling on rent control ballot petition (June 2026) vs MA-RENT-P1: Rent control ballot question (IP 25-21) struck
