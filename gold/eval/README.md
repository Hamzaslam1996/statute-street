# Scoring approach (placeholder — no code yet)

Planned scorer (to be written after Hamza adjudicates the key):
1. **Rules (Module A)** — match submitted `rules.json` to `gold/rules/all.json` by (jurisdiction, category, citation-normalised); score status, effective_date (exact / month / year tolerance), key_value (normalised), coverage fields, and citation. Negative findings score when the submission reports no rule for that cell.
2. **Citations** — quoted_span must be an exact substring of the cited corpus document; `quoted_span_in_corpus=false` rows are reported separately because they cannot earn citation points from the organisers' corpus.
3. **Addresses (Module B)** — for each of the 20 seed addresses compare the submitted result for every gold rule in the stack (applies / unknown / superseded / not_yet_effective / pending); rules in `not_covered` must be absent.
4. **Changes (Module C)** — set equality of affected_address_ids and conflict_flag_address_ids per test; T5 must be empty.
5. Report per-state and per-category breakdowns on `dev.json` first; `test.json` only at the final run.
