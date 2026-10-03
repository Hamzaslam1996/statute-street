# Module B lookup evaluation (seed20, before manual sources)

Gold: `gold/addresses/seed20.json` (20 addresses, 190 expectations, verifier AI-draft)  
Ours: `/Users/hamzaaslamkhan/Downloads/03 RealPage - Codebase and Data/navigator/out/lookups.json`

| Metric | Value |
|---|---|
| Exact result agreement | 166/190 = 87.4% |
| Weighted score (missed 'applies' count double) | 252/292 = 86.3% |
| Missed 'applies' (gold applies, ours not) | 16 |
| Expectations we did not report at all | 2 |
| Our unknown rate (these addresses) | 89/206 = 43.2% |

## Confusion (gold → ours)

| gold \ ours | applies | superseded | not_yet_effective | pending | unknown | not_reported |
|---|---|---|---|---|---|---|
| applies | 86 | 0 | 0 | 0 | 16 | 0 |
| superseded | 0 | 7 | 0 | 0 | 4 | 1 |
| not_yet_effective | 0 | 0 | 6 | 0 | 0 | 0 |
| pending | 0 | 0 | 0 | 8 | 0 | 0 |
| unknown | 2 | 0 | 0 | 0 | 59 | 1 |

## Disagreement types

- gold applies → ours unknown: 16
- gold superseded → ours unknown: 4
- gold unknown → ours applies: 2
- gold superseded → ours not_reported: 1
- gold unknown → ours not_reported: 1

## Top disagreements (gold reason vs ours)

| Address | Gold id | Gold | Ours | Gold reason | Our explanation |
|---|---|---|---|---|---|
| A0005 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0005 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data (owner shares kitchen or bath with tenant if owner lived on t) |
| A0005 (Berkeley) | BERK-SCRN-01 → r-0006 | applies | unknown | owner-occupied 1–3 unit exemption impossible for a 5+ unit building (use code) | Unknown: owner type not in the data (owner-occupied properties (between 1-3 units) in which an ow) |
| A0235 (Los Angeles) | CA-DEP-01 → r-0019 | applies | unknown | 5 units (use_description implies 5+ units) > 4 defeats the small-landlord two-month exception; one-month cap a | Unknown: owner type not in the data (The two-month cap applies if the landlord is a natural perso) |
| A0005 (Berkeley) | CA-DEP-01 → r-0019 | applies | unknown | 5 units (use_description implies 5+ units) > 4 defeats the small-landlord two-month exception; one-month cap a | Unknown: owner type not in the data (The two-month cap applies if the landlord is a natural perso) |
| A0050 (San Francisco) | CA-RENT-01 → r-0016 | applies | unknown | no local rent control for this unit; year_built 1986 is more than 15 years old so the COO exemption cannot app | Unknown: funding not in the data (Deed-restricted or subsidized affordable housing) |
| A0022 (Los Angeles) | LA-JUST-01 → r-0029 | applies | unknown | non-RSO residential unit (year_built 2012); tenancy length (6 months) not in data but the rule attaches to the | Unknown: tenancy months not in the data (Applies once the tenant has lived in the unit at least six m) |
| A0065 (Boston) | MA-DEP-01 → r-0041 | applies | unknown | statewide; no coverage condition | Unknown: other not in the data (does not apply to any lease, rental, occupancy or tenancy of) |
| A0036 (Boston) | MA-DEP-01 → r-0041 | applies | unknown | statewide; no coverage condition | Unknown: other not in the data (does not apply to any lease, rental, occupancy or tenancy of) |
| A0015 (Cambridge) | MA-DEP-01 → r-0041 | applies | unknown | statewide; no coverage condition | Unknown: other not in the data (does not apply to any lease, rental, occupancy or tenancy of) |

## Gold id → our rule mapping notes

- BOS-SCRN-01 -> r-0012 (only rule in bucket)
- CA-DEP-01 -> r-0019 (only rule in bucket)
- CA-FEE-01 -> r-0014 (only rule in bucket)
- CA-JUST-01 -> r-0015 (section in reason)
- LA-JUST-02 -> r-0030 (only rule in bucket)
- LA-SCRN-01 -> r-0032 (only rule in bucket)
- MA-FEE-02 -> r-0036 (only rule in bucket)
- MA-SCRN-01 -> r-0040 (only rule in bucket)
- MA-SCRN-02 -> r-0040 (only rule in bucket)
- NJ-DEP-01 -> r-0049 (only rule in bucket)
- NJ-SCRN-02 -> r-0047 (only rule in bucket)
- NWK-RENT-01 -> r-0050 (only rule in bucket)
- SD-ALG-01 -> r-0052 (only rule in bucket)
- SD-SCRN-01 -> r-0054 (only rule in bucket)
- SF-RENT-01 -> r-0057 (only rule in bucket)
