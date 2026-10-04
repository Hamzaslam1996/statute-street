# Stress test before submission (Hamza, 4 Oct)

No API calls (budget is at the stop). No changes to engine policy or submission files in this step: measure only, write out/stress/, report, stop. Never read gold/rules/test.json.

## 1. Policy sensitivity: score our submission against alternative keys
We do not know how the organisers' hidden key treats exemptions. Build alternative keys DETERMINISTICALLY by re-running engine.py with policy switches into out/stress/<name>/lookups.json (never overwrite out/):
- K_strict: every "applies unless" (use_or_funding) row becomes unknown (= --strict-unknown).
- K_lenient: plausible exemptions (owner-occupied small buildings, AB 1482 natural-person SFR/condo) become applies; true owner tests stay unknown.
- K_cutoff: cutoff-year buildings (SF 1979, LA 1978, 15-year AB 1482 window year) resolved as applies instead of unknown.
- K_derivedunits: NJ derived unit counts treated as real (--use-derived-units).
- K_noprecedence: state rules reported as applies instead of superseded where a local rule applies.
- K_omit: rules that "don't apply" omitted vs reported (check our current behaviour matches the README instruction "leave out rules that don't apply").
For each key K: agreement of our CURRENT out/lookups.json against K (exact rows / total, and per category, per city), plus rows that differ. Output a matrix table: rows = keys, columns = exact %, missed applies, extra applies, unknown-vs-applies swaps.
Then the decision table: for each candidate submission policy P in {current, strict, lenient}, its score against each key K; report worst case and average per P (minimax). Recommend nothing; I decide.

## 2. Adversarial perturbations (engine robustness)
Write tests in tests/test_stress.py and run them, no data files changed:
- Year built at each cutoff: cutoff-1, cutoff, cutoff+1 for SF (1979), LA (1978), AB 1482 15-year window, Hoboken 1987 and 30-year rule, Newark 30-year rule. Expect applies / unknown / not-covered correctly.
- Missing year, missing units, units "0", non-numeric units: never crash, always a reason.
- Mailing city differs from legal city (Dorchester, Brighton, South Boston, Hollywood): legal city decides.
- As-of dates: day before and day of every effective date in rules.json (not_yet_effective then applies). Rules with month-only dates: behaviour documented.
- Pending and failed instruments: never applies at any date in 2025 to 2028.
- Boston and Cambridge: no rent cap result at any date.
- Every lookup row references an existing rule; every rule cited in a lookup has quoted_span that is an exact substring of its source text.

## 3. Submission format check
Validate out/rules.json against schema/rule_record.schema.json; out/lookups.json has all 500 address_ids, as_of present, result values only from the allowed five; out/changes.json has T1 to T5 with affected_address_ids, conflict_flag_address_ids, notes; all ids exist in the address sample. Compare key shapes with submission_templates/.

## 4. Reproducibility
Fresh clone of the navigator repo into /tmp (or a sibling folder), create venv, run the documented pipeline in cache-only mode (fail if any model call would be made), and diff out/*.json against the committed files. Report identical or the diff.

## 5. Report
out/stress/REPORT.md with the tables above, failing tests (if any), format check result, reproducibility result. Commit out/stress/ and tests by name, push, stop.
