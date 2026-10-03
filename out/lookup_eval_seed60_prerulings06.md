# Module B lookup evaluation (seed60, after manual sources + D088-D095, with units floor)

Gold: `gold/addresses/seed60.json` (60 addresses, 569 expectations, verifier AI-draft)  
Ours: `/Users/hamzaaslamkhan/Downloads/03 RealPage - Codebase and Data/navigator/out/lookups.json`

| Metric | Value |
|---|---|
| Exact result agreement | 480/569 = 84.4% |
| Weighted score (missed 'applies' count double) | 739/883 = 83.7% |
| Missed 'applies' (gold applies, ours not) | 55 |
| Expectations we did not report at all | 5 |
| Our unknown rate (these addresses) | 265/653 = 40.6% |

## Confusion (gold → ours)

| gold \ ours | applies | superseded | not_yet_effective | pending | unknown | not_reported |
|---|---|---|---|---|---|---|
| applies | 259 | 0 | 0 | 0 | 55 | 0 |
| superseded | 0 | 10 | 0 | 0 | 19 | 2 |
| not_yet_effective | 0 | 0 | 18 | 0 | 0 | 0 |
| pending | 0 | 0 | 0 | 30 | 0 | 0 |
| unknown | 10 | 0 | 0 | 0 | 163 | 3 |

## Disagreement types

- gold applies → ours unknown: 55
- gold superseded → ours unknown: 19
- gold unknown → ours applies: 10
- gold unknown → ours not_reported: 3
- gold superseded → ours not_reported: 2

## Top disagreements (gold reason vs ours)

| Address | Gold id | Gold | Ours | Gold reason | Our explanation |
|---|---|---|---|---|---|
| A0005 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0018 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0430 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0103 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0193 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0263 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data (nonprofit cooperatives) |
| A0005 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data (owner shares kitchen or bath with tenant if owner lived on t) |
| A0018 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data (owner shares kitchen or bath with tenant if owner lived on t) |
| A0430 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data (owner shares kitchen or bath with tenant if owner lived on t) |
| A0103 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data (owner shares kitchen or bath with tenant if owner lived on t) |

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
