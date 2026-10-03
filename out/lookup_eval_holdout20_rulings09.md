# Module B lookup evaluation (holdout20, after rulings_09)

Gold: `gold/addresses/holdout20.json` (20 addresses, 192 expectations, verifier AI-draft)  
Ours: `/Users/hamzaaslamkhan/Downloads/03 RealPage - Codebase and Data/navigator/out/lookups.json`

| Metric | Value |
|---|---|
| Exact result agreement | 182/192 = 94.8% |
| Weighted score (missed 'applies' count double) | 283/300 = 94.3% |
| Missed 'applies' (gold applies, ours not) | 7 |
| Expectations we did not report at all | 0 |
| Our unknown rate (these addresses) | 73/213 = 34.3% |

## Confusion (gold → ours)

| gold \ ours | applies | superseded | not_yet_effective | pending | unknown | not_reported |
|---|---|---|---|---|---|---|
| applies | 101 | 0 | 0 | 0 | 7 | 0 |
| superseded | 0 | 11 | 0 | 0 | 3 | 0 |
| not_yet_effective | 0 | 0 | 6 | 0 | 0 | 0 |
| pending | 0 | 0 | 0 | 8 | 0 | 0 |
| unknown | 0 | 0 | 0 | 0 | 56 | 0 |

## Disagreement types

- gold applies → ours unknown: 7
- gold superseded → ours unknown: 3

## Top disagreements (gold reason vs ours)

| Address | Gold id | Gold | Ours | Gold reason | Our explanation |
|---|---|---|---|---|---|
| A0091 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0158 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0091 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0158 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0091 (Berkeley) | BERK-SCRN-01 → r-0006 | applies | unknown | owner-occupied 1–3 unit exemption impossible for a 5+ unit building (use code) | Unknown: owner type not in the data; the exception for units under a rental agreement allowing owners to move  |
| A0158 (Berkeley) | BERK-SCRN-01 → r-0006 | applies | unknown | owner-occupied 1–3 unit exemption impossible for a 5+ unit building (use code) | Unknown: owner type not in the data; the exception for units under a rental agreement allowing owners to move  |
| A0080 (Los Angeles) | LA-JUST-01 → r-0028 | applies | unknown | non-RSO residential unit (year_built 2002); tenancy length (6 months) not in data but the rule attaches to the | Unknown: owner type not in the data; the exception for certain cooperatives, some non-profit homeless faciliti |
| A0080 (Los Angeles) | CA-JUST-01 → r-0015 | superseded | unknown | Los Angeles just-cause ordinance governs instead (Civ. Code § 1946.2(i)) | Unknown: whether local rule r-0028 governs depends on facts not in the data |
| A0091 (Berkeley) | CA-JUST-01 → r-0015 | superseded | unknown | Berkeley just-cause ordinance governs instead (Civ. Code § 1946.2(i)) | Unknown: year built missing, so the certificate-of-occupancy cutoff cannot be tested |
| A0158 (Berkeley) | CA-JUST-01 → r-0015 | superseded | unknown | Berkeley just-cause ordinance governs instead (Civ. Code § 1946.2(i)) | Unknown: year built missing, so the certificate-of-occupancy cutoff cannot be tested |

## All gold unknown → ours applies (0)

| Address | Gold id | Gold reason | Our explanation |
|---|---|---|---|

## Whole sample

- addresses: 500; rows: 5298; unknown rate: 1654/5298 = 31.2%
- rows relying on a presumption (`assumptions` non-empty): 1919

## Gold id → our rule mapping notes

- BOS-SCRN-01 -> r-0012 (only rule in bucket)
- CA-DEP-01 -> r-0019 (only rule in bucket)
- CA-FEE-01 -> r-0014 (only rule in bucket)
- CA-JUST-01 -> r-0015 (section in reason)
- LA-JUST-02 -> r-0029 (only rule in bucket)
- LA-SCRN-01 -> r-0031 (only rule in bucket)
- MA-FEE-02 -> r-0035 (only rule in bucket)
- MA-SCRN-01 -> r-0041 (section in reason)
- MA-SCRN-02 -> r-0042 (only rule in bucket)
- NJ-DEP-01 -> r-0051 (only rule in bucket)
- NJ-SCRN-02 -> r-0049 (only rule in bucket)
- NWK-RENT-01 -> r-0052 (only rule in bucket)
- SD-ALG-01 -> r-0054 (only rule in bucket)
- SD-SCRN-01 -> r-0056 (only rule in bucket)
- SF-RENT-01 -> r-0059 (only rule in bucket)
