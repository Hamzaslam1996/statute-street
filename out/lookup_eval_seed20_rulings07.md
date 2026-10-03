# Module B lookup evaluation (seed20, after rulings_07)

Gold: `gold/addresses/seed20.json` (20 addresses, 190 expectations, verifier AI-draft)  
Ours: `/Users/hamzaaslamkhan/Downloads/03 RealPage - Codebase and Data/navigator/out/lookups.json`

| Metric | Value |
|---|---|
| Exact result agreement | 190/190 = 100.0% |
| Weighted score (missed 'applies' count double) | 293/293 = 100.0% |
| Missed 'applies' (gold applies, ours not) | 0 |
| Expectations we did not report at all | 0 |
| Our unknown rate (these addresses) | 69/214 = 32.2% |

## Confusion (gold → ours)

| gold \ ours | applies | superseded | not_yet_effective | pending | unknown | not_reported |
|---|---|---|---|---|---|---|
| applies | 103 | 0 | 0 | 0 | 0 | 0 |
| superseded | 0 | 12 | 0 | 0 | 0 | 0 |
| not_yet_effective | 0 | 0 | 6 | 0 | 0 | 0 |
| pending | 0 | 0 | 0 | 8 | 0 | 0 |
| unknown | 0 | 0 | 0 | 0 | 61 | 0 |

## Disagreement types


## Top disagreements (gold reason vs ours)

| Address | Gold id | Gold | Ours | Gold reason | Our explanation |
|---|---|---|---|---|---|

## All gold unknown → ours applies (0)

| Address | Gold id | Gold reason | Our explanation |
|---|---|---|---|

## Whole sample

- addresses: 500; rows: 5408; unknown rate: 1444/5408 = 26.7%
- rows relying on a presumption (`assumptions` non-empty): 2081

## Gold id → our rule mapping notes

- BOS-SCRN-01 -> r-0012 (only rule in bucket)
- CA-DEP-01 -> r-0019 (only rule in bucket)
- CA-FEE-01 -> r-0014 (only rule in bucket)
- CA-JUST-01 -> r-0015 (section in reason)
- LA-JUST-02 -> r-0029 (only rule in bucket)
- LA-SCRN-01 -> r-0031 (only rule in bucket)
- MA-FEE-02 -> r-0035 (ambiguous bucket of 2)
- MA-SCRN-01 -> r-0042 (section in reason)
- MA-SCRN-02 -> r-0043 (only rule in bucket)
- NJ-DEP-01 -> r-0052 (only rule in bucket)
- NJ-SCRN-02 -> r-0050 (only rule in bucket)
- NWK-RENT-01 -> r-0053 (only rule in bucket)
- SD-ALG-01 -> r-0055 (only rule in bucket)
- SD-SCRN-01 -> r-0057 (only rule in bucket)
- SF-RENT-01 -> r-0060 (only rule in bucket)
