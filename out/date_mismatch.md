# Effective-date mismatches vs gold (dev)

39 matched rules; 9 disagree on effective_date (pairs where both are null count as agreement).

Classes: (a) stated in another corpus doc · (b) no doc states it · (c) convention difference · (d) genuine error

| Class | Rule | Gold | Ours | Why | Evidence |
|---|---|---|---|---|---|
| b | BOS-SCRN-02 / r-0011 (Boston DND Fair Chance Tenant Selection ) | 2017-02 | None | no corpus document states this date |  |
| b | LA-JUST-01 / r-0029 (L.A. Mun. Code § 165.00 et seq. (Just Ca) | 2023-01-27 | None | no corpus document states this date |  |
| c | SF-DEP-01 / r-0059 (S.F. Admin. Code § 49.2) | None | 2026-03-01 | gold null; ours from adoption month / rate-period start / amendment note |  |
| c | HOB-RENT-01 / r-0025 (Hoboken, N.J., Code § 155-5) | None | 2023-02 | gold null; ours from adoption month / rate-period start / amendment note |  |
| c | CA-SCRN-01 / r-0018 (Cal. Gov. Code § 12955) | 2020-01-01 | 2024-01-01 | neither date confirmable; convention difference |  |
| c | CA-RENT-01 / r-0016 (Cal. Civ. Code § 1947.12) | 2020-01-01 | 2024-04-01 | neither date confirmable; convention difference |  |
| c | BERK-RENT-01 / r-0005 (Berkeley Municipal Code § 13.76.110(A); ) | None | 2026-01-01 | gold null; ours from adoption month / rate-period start / amendment note |  |
| c | NWK-SCRN-01 / r-0051 (Newark Municipal Code § 2:31-1 to 2:31-9) | None | 2015-04 | gold null; ours from adoption month / rate-period start / amendment note |  |
| c | BERK-ALG-01 / r-0001 (Berkeley Municipal Code § 13.63.030 (Ord) | 2026-01-01 | 2026-01 | same month, different precision |  |

By class: {'a': 0, 'b': 2, 'c': 7, 'd': 0}
