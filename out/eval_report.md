# Module A evaluation

Gold set: `gold/gold_rules.json` — SILVER (AI draft, unverified)  
Our rules: 3 from 3 extracted document(s)  
Gold rules in scope (source doc extracted): 3 of 44 positive, 0 of 9 negative findings

| Metric | Value |
|---|---|
| Found (recall) | 3/3 = 100% |
| Missed | 0 |
| Extra (no gold match) | 0 |
| Extra colliding with a negative finding | 0 |
| Status agrees | 3/3 = 100% |
| Effective date exact / same year | 1/3 = 33% / 1/3 |
| Citation similarity (mean) | 90/100 |
| Key value similarity (mean) | 78/100 |
| Quote check pass rate (first attempt) | 3/3 = 100% |
| Records dropped for bad quotes | 0 |

## Matched rules

| Gold id | Ours | Status (gold / ours) | Eff. date (gold / ours) | Cite score | Key value (gold / ours) |
|---|---|---|---|---|---|
| CA-RENT-01 | r-0001 | in_force / in_force | 2020-01-01 / 2024-04-01 | 100 | 5% + CPI, max 10% per 12 months / 5% + CPI change, max 10% (whichever is lower), in any 12-mon |
| NJ-ALG-01 | r-0002 | not_yet_effective / not_yet_effective | 2027-07-01 / 2027-07-01 | 69 | Prohibits use/sale of rent-setting algorithms using nonpubli / Ban on algorithmic coordination of rents, material lease ter |
| NJ-DEP-01 | r-0003 | in_force / in_force | None / 2003 | 100 | 1.5 months' rent / 1.5 months' rent maximum; additional annual security max 10% |

## Missed gold rules (in scope)

- none

## Extra rules (no gold match)

- none
