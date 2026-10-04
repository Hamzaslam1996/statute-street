# Stress test report (pre-submission)

Code state: db0b61b. Measure only: no engine policy or submission file was changed in this step; alternative keys were built with opt-in engine switches into out/stress/.

## 1. Policy sensitivity: current submission vs alternative keys

| Key | Rows (union) | Exact | Exact % | Weighted % | Missed applies | Extra applies | Unknown/applies swaps |
|---|---|---|---|---|---|---|---|
| K_strict | 5298 | 4688 | 88.5 | 92.3 | 0 | 448 | 448 |
| K_lenient | 5298 | 4395 | 83.0 | 81.0 | 853 | 0 | 853 |
| K_cutoff | 5298 | 5288 | 99.8 | 99.8 | 8 | 0 | 8 |
| K_derivedunits | 5298 | 4777 | 90.2 | 88.3 | 521 | 0 | 521 |
| K_noprecedence | 5298 | 4928 | 93.0 | 92.6 | 267 | 0 | 2 |
| K_omit | 5380 | 5298 | 98.5 | 99.0 | 0 | 0 | 0 |

Per category (exact/rows) and per city, by key:

- **K_strict**: algorithmic_rent_setting 740/920; application_screening_fees 690/690; just_cause_eviction 718/945; rent_increase_limits 475/598; screening_restrictions 1430/1470; security_deposits 635/675
  cities: Berkeley 360/560; Boston 600/600; Cambridge 500/500; Hoboken 360/400; Jersey City 400/450; Los Angeles 673/885; Newark 448/450; San Diego 400/500; San Francisco 947/953
- **K_lenient**: algorithmic_rent_setting 920/920; application_screening_fees 550/690; just_cause_eviction 755/945; rent_increase_limits 495/598; screening_restrictions 1140/1470; security_deposits 535/675
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 200/400; Jersey City 200/450; Los Angeles 881/885; Newark 102/450; San Diego 400/500; San Francisco 952/953
- **K_cutoff**: algorithmic_rent_setting 920/920; application_screening_fees 690/690; just_cause_eviction 941/945; rent_increase_limits 594/598; screening_restrictions 1470/1470; security_deposits 673/675
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 400/400; Jersey City 450/450; Los Angeles 875/885; Newark 450/450; San Diego 500/500; San Francisco 953/953
- **K_derivedunits**: algorithmic_rent_setting 920/920; application_screening_fees 595/690; just_cause_eviction 853/945; rent_increase_limits 548/598; screening_restrictions 1278/1470; security_deposits 583/675
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 210/400; Jersey City 150/450; Los Angeles 885/885; Newark 419/450; San Diego 500/500; San Francisco 953/953
- **K_noprecedence**: algorithmic_rent_setting 920/920; application_screening_fees 690/690; just_cause_eviction 695/945; rent_increase_limits 478/598; screening_restrictions 1470/1470; security_deposits 675/675
  cities: Berkeley 520/560; Boston 600/600; Cambridge 500/500; Hoboken 400/400; Jersey City 450/450; Los Angeles 756/885; Newark 450/450; San Diego 450/500; San Francisco 802/953
- **K_omit**: algorithmic_rent_setting 920/920; application_screening_fees 690/690; just_cause_eviction 945/970; rent_increase_limits 598/630; screening_restrictions 1470/1470; security_deposits 675/700
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 400/400; Jersey City 450/450; Los Angeles 885/960; Newark 450/450; San Diego 500/500; San Francisco 953/960

## Decision table: candidate policy P scored against each key K (exact %, weighted % in brackets)

| P \ K | current | K_strict | K_lenient | K_cutoff | K_derivedunits | K_noprecedence | K_omit | worst exact | mean exact | worst weighted | mean weighted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| current | 100.0 (100.0) | 88.5 (92.3) | 83.0 (81.0) | 99.8 (99.8) | 90.2 (88.3) | 93.0 (92.6) | 98.5 (99.0) | 83.0 | 93.3 | 81.0 | 93.3 |
| strict | 88.5 (87.4) | 100.0 (100.0) | 73.3 (70.6) | 88.3 (87.2) | 78.7 (76.4) | 86.3 (83.3) | 87.1 (86.5) | 73.3 | 86.0 | 70.6 | 84.5 |
| lenient | 83.0 (89.2) | 73.3 (82.2) | 100.0 (100.0) | 82.8 (89.0) | 90.9 (94.0) | 77.9 (83.3) | 81.7 (88.4) | 73.3 | 84.2 | 82.2 | 89.4 |

No recommendation is made here; the policy choice is the reviewer's.

## 2. Adversarial perturbations (tests/test_stress.py)

Result: 49 passed in 0.08s

Documented behaviours encoded in the tests:
- SF rent ordinance: 1978 applies, 1979 unknown (cutoff year), 1980 not covered. LA RSO: 1977 applies, 1978 unknown, 1979 not covered.
- LA JCO for a pre-1978 building answers unknown, not 'not covered': its 'not regulated by the RSO' condition is conditional and RSO exemption is not in parcel data.
- AB 1482 15-year window (query 2026): 2010 applies, 2011 unknown, 2012 unknown or not covered (the model marked the window on_fail unknown).
- Hoboken ch. 155: on or before 1987 applies; 1988 to 1995 applies (30 full years before the query date); 1996 and later unknown; missing year unknown. Newark 30-year rule: cutoff year unknown.
- Missing year, missing units, units '0' and non-numeric units never crash; every row carries a reason.
- Mailing city differs from legal city: the geocoded legal city decides (Dorchester, Brighton, South Boston, Roxbury, East Boston rows resolve to Boston; fallback table covers Hollywood, Van Nuys, San Ysidro).
- Every full effective date: the day before is not_yet_effective, the day itself proceeds to coverage. Month-only dates: a query date inside that month is unknown, the day before not_yet_effective, the following month in force.
- Pending instruments are always pending and failed instruments never appear at any date from 2025 to 2028; Boston and Cambridge never show a rent cap at any date.
- Every lookup row references an existing rule; every cited rule's quote is an exact substring of its source text.

Passed (49):
- tests/test_stress.py::test_sf_rent_cutoff_1979[1978-applies]
- tests/test_stress.py::test_sf_rent_cutoff_1979[1979-unknown]
- tests/test_stress.py::test_sf_rent_cutoff_1979[1980-not_covered]
- tests/test_stress.py::test_la_rso_rent_cutoff_1978[1977-applies]
- tests/test_stress.py::test_la_rso_rent_cutoff_1978[1978-unknown]
- tests/test_stress.py::test_la_rso_rent_cutoff_1978[1979-not_covered]
- tests/test_stress.py::test_la_jco_cutoff_1978_other_side[1977-expect0]
- tests/test_stress.py::test_la_jco_cutoff_1978_other_side[1978-expect1]
- tests/test_stress.py::test_la_jco_cutoff_1978_other_side[1979-expect2]
- tests/test_stress.py::test_ab1482_15_year_window[2010-applies]
- tests/test_stress.py::test_ab1482_15_year_window[2011-unknown]
- tests/test_stress.py::test_ab1482_15_year_window[2012-unknown_or_not_covered]
- tests/test_stress.py::test_hoboken_1987_and_30_year_rule[1986-applies]
- tests/test_stress.py::test_hoboken_1987_and_30_year_rule[1987-applies]
- tests/test_stress.py::test_hoboken_1987_and_30_year_rule[1988-applies]
- tests/test_stress.py::test_hoboken_1987_and_30_year_rule[1995-applies]
- tests/test_stress.py::test_hoboken_1987_and_30_year_rule[1996-unknown]
- tests/test_stress.py::test_hoboken_1987_and_30_year_rule[1997-unknown]
- tests/test_stress.py::test_hoboken_1987_and_30_year_rule[None-unknown]
- tests/test_stress.py::test_newark_30_year_rule[1995]
- tests/test_stress.py::test_newark_30_year_rule[1996]
- tests/test_stress.py::test_newark_30_year_rule[1997]
- tests/test_stress.py::test_newark_30_year_rule[None]
- tests/test_stress.py::test_missing_or_malformed_facts_never_crash[-]
- tests/test_stress.py::test_missing_or_malformed_facts_never_crash[None-None]
- tests/test_stress.py::test_missing_or_malformed_facts_never_crash[1950-0]
- tests/test_stress.py::test_missing_or_malformed_facts_never_crash[abc-n/a]
- tests/test_stress.py::test_missing_or_malformed_facts_never_crash[-6]
- tests/test_stress.py::test_missing_or_malformed_facts_never_crash[1979-]
- tests/test_stress.py::test_postal_city_fallback_table[Dorchester-Boston]
- tests/test_stress.py::test_postal_city_fallback_table[Brighton-Boston]
- tests/test_stress.py::test_postal_city_fallback_table[South Boston-Boston]
- tests/test_stress.py::test_postal_city_fallback_table[Hollywood-Los Angeles]
- tests/test_stress.py::test_postal_city_fallback_table[Van Nuys-Los Angeles]
- tests/test_stress.py::test_postal_city_fallback_table[San Ysidro-San Diego]
- tests/test_stress.py::test_sample_neighbourhoods_resolved_to_boston
- tests/test_stress.py::test_status_flips_on_effective_date
- tests/test_stress.py::test_month_only_dates_are_unknown_inside_the_month
- tests/test_stress.py::test_pending_and_failed_never_apply[as_of0]
- tests/test_stress.py::test_pending_and_failed_never_apply[as_of1]
- tests/test_stress.py::test_pending_and_failed_never_apply[as_of2]
- tests/test_stress.py::test_pending_and_failed_never_apply[as_of3]
- tests/test_stress.py::test_pending_and_failed_never_apply[as_of4]
- tests/test_stress.py::test_boston_cambridge_never_show_a_rent_cap[as_of0]
- tests/test_stress.py::test_boston_cambridge_never_show_a_rent_cap[as_of1]
- tests/test_stress.py::test_boston_cambridge_never_show_a_rent_cap[as_of2]
- tests/test_stress.py::test_boston_cambridge_never_show_a_rent_cap[as_of3]
- tests/test_stress.py::test_every_lookup_row_references_an_existing_rule
- tests/test_stress.py::test_every_cited_rule_quote_is_exact_substring_of_its_source

## 3. Submission format check

- rules.json: 65 records, schema errors: 0
- rules.json: duplicate team_rule_ids: 0
- lookups.json: as_of='2026-10-01'; addresses 500 (sample 500; missing 0, extra 0); invalid result values 0; rows citing unknown rules 0
- changes.json: tests ['T1', 'T2', 'T3', 'T4', 'T5']; required keys present: True; address ids not in sample: 0
- template rules.json keys missing from ours: none; extra keys in ours (allowed, schema has no additionalProperties): ['adoption_date', 'date_source_doc_id', 'evidence_basis', 'negative_finding', 'notes', 'record_role', 'requirement_es', 'retrieved_at', 'supporting_doc_ids']
- template lookups.json: top-level keys ['as_of', 'lookups'] vs ours ['as_of', 'lookups']; row keys missing: none; extra row keys: ['assumptions']
- template changes.json entry keys ['affected_address_ids', 'notes'] vs ours ['affected_address_ids', 'conflict_flag_address_ids', 'notes']

**Format check: PASS**

## 4. Reproducibility

Fresh `git clone` of the navigator repository into a sibling folder (`../navigator_repro`, HEAD db0b61b), new
virtual environment from `requirements.txt`, `ANTHROPIC_API_KEY` set to an invalid value so that any model call
would fail loudly. Pipeline run in cache-only mode:

`verify.py --no-retry` → `date_resolve.py --no-model` → `derive_negatives.py` → `translate_es.py --no-model` →
`coverage.py --no-model` → `engine.py` → `engine.py --use-derived-units` → `changes.py` (+ the two `--diff` runs) →
`open_questions.py` → `publish.py --in-place`.

Result: pipeline exit 0; no model call was made (log contains no API or authentication message; coverage and
date caches served every record). Byte comparison against the committed files:

| File | Result |
|---|---|
| out/rules.json, rules_full.json, negatives.json | identical |
| out/lookups.json, lookups_derived.json | identical |
| out/changes.json, changes_detail.json | identical |
| out/coverage.json, open_questions.json | identical |
| out/public/rules.json, lookups.json, changes.json | identical |
| out/diff_2025-12-31_2026-01-02.json, diff_2026-10-01_2027-07-02.json | identical |

14 of 14 files identical. The repository therefore reproduces the submission from its committed caches
without network access to the model API.
