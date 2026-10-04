# Module B lookup evaluation (seed60, after rulings_11, regression check)

Gold: `gold/addresses/seed60.json` (60 addresses, 569 expectations, verifier AI-draft)  
Ours: `/Users/hamzaaslamkhan/Downloads/03 RealPage - Codebase and Data/navigator/out/lookups.json`

| Metric | Value |
|---|---|
| Exact result agreement | 569/569 = 100.0% |
| Weighted score (missed 'applies' count double) | 887/887 = 100.0% |
| Missed 'applies' (gold applies, ours not) | 0 |
| Expectations we did not report at all | 0 |
| Our unknown rate (these addresses) | 194/631 = 30.7% |

## Confusion (gold → ours)

| gold \ ours | applies | superseded | not_yet_effective | pending | unknown | not_reported |
|---|---|---|---|---|---|---|
| applies | 318 | 0 | 0 | 0 | 0 | 0 |
| superseded | 0 | 31 | 0 | 0 | 0 | 0 |
| not_yet_effective | 0 | 0 | 18 | 0 | 0 | 0 |
| pending | 0 | 0 | 0 | 30 | 0 | 0 |
| unknown | 0 | 0 | 0 | 0 | 172 | 0 |

## Disagreement types


## Top disagreements (gold reason vs ours)

| Address | Gold id | Gold | Ours | Gold reason | Our explanation |
|---|---|---|---|---|---|

## All gold unknown → ours applies (0)

| Address | Gold id | Gold reason | Our explanation |
|---|---|---|---|

## Whole sample

- addresses: 500; rows: 5298; unknown rate: 1444/5298 = 27.3%
- rows relying on a presumption (`assumptions` non-empty): 2079

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
