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
