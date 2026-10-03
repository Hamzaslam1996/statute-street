# Module B — address lookup (build after rulings_03 is done)

Goal: for every one of the 500 sample addresses, decide for every rule in out/rules.json whether it applies, and write out/lookups.json in the organisers' format:
{"as_of": "2026-10-01", "lookups": {address_id: [{team_rule_id, result, explanation, conflict_flag}]}}
result is one of: applies | unknown | superseded | not_yet_effective | pending. Leave out rules that clearly do not apply (other states/cities, clearly excluded buildings).

Do NOT read gold/addresses/seed20.json, gold/addresses/seed60.json or gold/rules/test.json while building. Only use them in step 7 to score.

## Step 1 — resolve.py: legal jurisdiction for each address
- Use the U.S. Census Geocoder batch endpoint (geocoding.geo.census.gov, benchmark Public_AR_Current, vintage Current_Current, returntype geographies; up to 10,000 rows, no key). One batch call for all 500.
- From the response take state, county and incorporated place (the legal city). This fixes postal names: Dorchester/Roxbury/Brighton etc. -> Boston; Van Nuys -> Los Angeles; San Ysidro -> San Diego.
- Fallback when the geocoder returns no match: map postal_city to the legal city with a small, documented table of Boston neighbourhoods and LA communities, and mark jurisdiction_confidence "fallback". Never silently guess.
- Cache to out/geocode.csv (address_id, matched_address, lat, lon, state, county, place, method). Rerun skips cached rows.
- Output out/jurisdictions.json: address_id -> {state, county, city, method}.

## Step 2 — structure the coverage tests (one-off, cached)
- Rules store coverage_conditions and exemptions as text. Convert each rule ONCE into machine-checkable tests with a small Claude call (Sonnet), saved to out/coverage.json, e.g.:
  {team_rule_id, tests: [{field: "coo_date"|"year_built"|"units"|"owner_type"|"tenancy_months"|"building_type"|"funding", op: "<=", ">=", "==", "in", value, source_text}], notes}
- The model must quote the coverage text each test came from. Rules with no limits -> tests: [] (applies to all residential rentals in that jurisdiction).
- Hamza reviews out/coverage.json for the rent-control rules (SF, LA, Berkeley, Hoboken, Jersey City, Newark, Santa Ana) before final run.

## Step 3 — engine.py: deterministic rule engine (no AI here)
For each address and each rule whose jurisdiction matches the address's state or city:
1. Status first (as of the query date):
   - status pending -> result pending
   - status failed -> exclude from the address answer (keep in a change-history note only)
   - negative_finding -> never "applies". Exclude negative findings from lookups.json; the UI shows them as "No rule at this level".
   - effective_date after query date -> not_yet_effective
   - in_force with the 60-day conflict note -> unknown
2. Coverage tests, each returns true / false / unknown:
   - year built is not the certificate-of-occupancy date: a COO cutoff test is TRUE only if year_built < cutoff year, FALSE if year_built > cutoff year, UNKNOWN if equal (SF 1979, LA 1978) or missing.
   - missing field (year_built, units, owner type, funding, tenancy length) -> unknown.
   - owner type is never in the data -> any owner-type exception is unknown UNLESS another fact defeats it (e.g. units > 4 defeats the CA small-landlord deposit exception -> 1-month cap applies).
   - all tests true -> applies; any false -> exclude; otherwise unknown.
3. Precedence (superseded): in the same category, if a local rule applies (or is unknown) and the rule's interaction says the state rule yields to it (e.g. CA § 1947.12 yields to local rent control), mark the state rule superseded where the local rule applies, unknown where the local rule is unknown. Explanation names the governing rule.
4. Conflict pass: if a state rule has preemption language in `interaction` and a local rule in the same category exists for the address, set conflict_flag true on both (FAIR Act vs Jersey City / Hoboken bans).
5. explanation: one plain-English sentence naming the deciding fact, e.g. "Built 1962, before SF's 1979 cutoff" or "Unknown: unit count missing from county records".

## Step 4 — write out/lookups.json for ALL 500 addresses, plus out/lookup_audit.csv (address_id, team_rule_id, result, deciding_facts).

## Step 5 — tests (tests/test_engine.py), must all pass:
- SF building year_built 1979 -> SF rent ordinance unknown.
- SF building 1962, 20 units -> SF rent ordinance applies; CA § 1947.12 superseded.
- Dorchester address -> Boston rules, no rent cap.
- Newark address -> neither Hoboken nor Jersey City algorithmic ban.
- Any NJ address as of 2026-10-01 -> FAIR Act not_yet_effective; as of 2027-07-02 -> applies.
- Any CA address as of 2025-12-31 -> AB 325 not_yet_effective; as of 2026-01-02 -> applies.
- MA address -> S.2983 and H.5222 pending; failed ballot question never appears.

## Step 6 — make the query date a parameter: python engine.py --as-of 2027-07-02 (Module C will reuse this).

## Step 7 — score against gold/addresses/seed60.json (report seed20 separately too): per-result accuracy, missed "applies" (count double, as judges do), unknown rate. Write out/lookup_eval.md. Show me the table.

Budget: Step 2 is the only API spend (~70 rules, well under $1). Ask before anything larger. Commit after tests pass.
