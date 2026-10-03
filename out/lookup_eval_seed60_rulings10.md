# Module B lookup evaluation (seed60, after rulings_10)

Gold: `gold/addresses/seed60.json` (60 addresses, 569 expectations, verifier AI-draft)  
Ours: `/Users/hamzaaslamkhan/Downloads/03 RealPage - Codebase and Data/navigator/out/lookups.json`

| Metric | Value |
|---|---|
| Exact result agreement | 541/569 = 95.1% |
| Weighted score (missed 'applies' count double) | 839/887 = 94.6% |
| Missed 'applies' (gold applies, ours not) | 20 |
| Expectations we did not report at all | 0 |
| Our unknown rate (these addresses) | 222/631 = 35.2% |

## Confusion (gold → ours)

| gold \ ours | applies | superseded | not_yet_effective | pending | unknown | not_reported |
|---|---|---|---|---|---|---|
| applies | 298 | 0 | 0 | 0 | 20 | 0 |
| superseded | 0 | 23 | 0 | 0 | 8 | 0 |
| not_yet_effective | 0 | 0 | 18 | 0 | 0 | 0 |
| pending | 0 | 0 | 0 | 30 | 0 | 0 |
| unknown | 0 | 0 | 0 | 0 | 172 | 0 |

## Disagreement types

- gold applies → ours unknown: 20
- gold superseded → ours unknown: 8

## Top disagreements (gold reason vs ours)

| Address | Gold id | Gold | Ours | Gold reason | Our explanation |
|---|---|---|---|---|---|
| A0005 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0018 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0430 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0103 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0193 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0263 (Berkeley) | BERK-DEP-01 → r-0007 | applies | unknown | deposit interest covers fully and partially covered units | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0005 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0018 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0430 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |
| A0103 (Berkeley) | BERK-JUST-01 → r-0004 | applies | unknown | just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the ex | Unknown: owner type not in the data; the exception for nonprofit cooperatives cannot be ruled out |

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
