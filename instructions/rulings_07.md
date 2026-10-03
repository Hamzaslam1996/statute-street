# Rulings 07 — stale algorithmic-rent twins (Hamza, 4 Oct)

Deterministic folds only. No API calls. Record each in out/dedupe_log.csv with the reason below; keep the folded rule's source as a supporting document on the kept rule; do not delete raw outputs.

1. **r-0024 (Hoboken, "proposed ordinance", D095 press release, June 2025) → fold into r-0023 (Hoboken ch. 158, in force).** The proposal was introduced and then enacted as ch. 158; it is no longer pending. D095 becomes legislative-history support for r-0023. T2 uses r-0023 only. No Hoboken address should show a "pending" algorithmic rule.
2. **r-0028 (Jersey City, news article, secondary) → fold into r-0027 (Ord. 25-057, official adopted copy).** Same ordinance. Keep r-0027's citation, quote and date.
3. **r-0065 (Santa Ana, March 2026 newsletter, eff "2026-03") → fold into r-0066 (Ord. NS-3090, eff 2026-04-02, adopted 2026-03-03, 30-day rule basis note).** Same ordinance. Keep r-0066.
4. Keep r-0020 (Cambridge policy order, pending): it is a council policy order, not a bill; show it as pending for Cambridge addresses only, outside T4 (T4 = S.2983 + H.5222).
5. Check the lookup_eval mapping note "MA-FEE-02 → r-0036": r-0036 is now S.2983 (algorithmic). If the mapper is matching on stale ids, fix it so MA-FEE-02 maps to the c.112 § 87DDD½ rule. Report if any score moves.
6. Re-run Module A eval (must stay 39/39), rebuild lookups, re-score seed60/seed20, and continue with module_c.md.
