# Module B lookup evaluation (seed20, after manual sources)

Gold: `gold/addresses/seed20.json` (20 addresses, 190 expectations, verifier AI-draft)  
Ours: `/Users/hamzaaslamkhan/Downloads/03 RealPage - Codebase and Data/navigator/out/lookups.json`

| Metric | Value |
|---|---|
| Exact result agreement | 164/190 = 86.3% |
| Weighted score (missed 'applies' count double) | 251/292 = 86.0% |
| Missed 'applies' (gold applies, ours not) | 15 |
| Expectations we did not report at all | 2 |
| Our unknown rate (these addresses) | 89/216 = 41.2% |

## Confusion (gold → ours)

| gold \ ours | applies | superseded | not_yet_effective | pending | unknown | not_reported |
|---|---|---|---|---|---|---|
| applies | 87 | 0 | 0 | 0 | 15 | 0 |
| superseded | 0 | 5 | 0 | 0 | 6 | 1 |
| not_yet_effective | 0 | 0 | 6 | 0 | 0 | 0 |
| pending | 0 | 0 | 0 | 8 | 0 | 0 |
| unknown | 3 | 0 | 0 | 0 | 58 | 1 |

## Disagreement types

- gold applies → ours unknown: 15
- gold superseded → ours unknown: 6
- gold unknown → ours applies: 3
- gold superseded → ours not_reported: 1
- gold unknown → ours not_reported: 1

## Top disagreements (gold reason vs ours)

| Address | Gold id | Gold | Ours | Gold reason | Our explanation |
|---|---|---|---|---|---|
| A0005 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0005 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data (owner shares kitchen or bath with tenant if owner lived on t) |
| A0005 (Berkeley) | BERK-SCRN-01 → r-0006 | applies | unknown | owner-occupied 1–3 unit exemption impossible for a 5+ unit building (use code) | Unknown: funding not in the data (limited exemptions for public housing/Section 8 properties) |
| A0050 (San Francisco) | CA-RENT-01 → r-0016 | applies | unknown | no local rent control for this unit; year_built 1986 is more than 15 years old so the COO exemption cannot app | Unknown: funding not in the data (Deed-restricted or subsidized affordable housing) |
| A0012 (Jersey City) | JC-ALG-01 → r-0027 | applies | unknown | citywide; conflict flag for possible FAIR Act preemption from 2027-07-01 | Unknown: owner type not in the data (licensed real estate agents operating in accordance with sta); possible c |
| A0008 (Jersey City) | JC-ALG-01 → r-0027 | applies | unknown | citywide; conflict flag for possible FAIR Act preemption from 2027-07-01 | Unknown: owner type not in the data (licensed real estate agents operating in accordance with sta); possible c |
| A0022 (Los Angeles) | LA-JUST-01 → r-0030 | applies | unknown | non-RSO residential unit (year_built 2012); tenancy length (6 months) not in data but the rule attaches to the | Unknown: tenancy months not in the data (Applies once the tenant has lived in the unit at least six m) |
| A0001 (Los Angeles) | LA-JUST-02 → r-0031 | applies | unknown | RSO unit → RSO eviction grounds and relocation rules | Unknown: owner type not in the data (No relocation payment when evicting a resident manager to re) |
| A0065 (Boston) | MA-DEP-01 → r-0046 | applies | unknown | statewide; no coverage condition | Unknown: other not in the data (does not apply to any lease, rental, occupancy or tenancy of) |
| A0036 (Boston) | MA-DEP-01 → r-0046 | applies | unknown | statewide; no coverage condition | Unknown: other not in the data (does not apply to any lease, rental, occupancy or tenancy of) |

## Gold id → our rule mapping notes

- BOS-SCRN-01 -> r-0012 (only rule in bucket)
- CA-DEP-01 -> r-0019 (only rule in bucket)
- CA-FEE-01 -> r-0014 (only rule in bucket)
- CA-JUST-01 -> r-0015 (section in reason)
- LA-JUST-02 -> r-0031 (only rule in bucket)
- LA-SCRN-01 -> r-0033 (only rule in bucket)
- MA-FEE-02 -> r-0037 (ambiguous bucket of 2)
- MA-SCRN-01 -> r-0045 (ambiguous bucket of 2)
- MA-SCRN-02 -> r-0044 (only rule in bucket)
- NJ-DEP-01 -> r-0054 (only rule in bucket)
- NJ-SCRN-02 -> r-0052 (only rule in bucket)
- NWK-RENT-01 -> r-0055 (only rule in bucket)
- SD-ALG-01 -> r-0057 (only rule in bucket)
- SD-SCRN-01 -> r-0059 (only rule in bucket)
- SF-RENT-01 -> r-0062 (only rule in bucket)
