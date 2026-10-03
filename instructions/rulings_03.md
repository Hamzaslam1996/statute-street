# Rulings from Hamza — after the full run (rulings_03)

## 1. Near-duplicates: YES, add the second dedupe pass
- Merge within a jurisdiction + category bucket when section numbers intersect or citation similarity >= 85.
- Keep the record from the best source: official statute/ordinance > official agency page > code publisher > secondary (law firm / news). Put the other doc ids in `supporting_doc_ids`. Keep the best quoted_span (must still pass the substring check against its own source doc).
- Santa Ana duplicates in every category: merge the same way.
- Proposals vs enacted (San Diego D076 proposal vs D074 adopted): when an enacted record and a proposal cover the same jurisdiction + category + subject, keep ONLY the enacted record; add the proposal doc to `supporting_doc_ids` and a note "Proposal adopted as O-21955". `pending` is reserved for bills/proposals that have NOT been enacted (e.g. MA S.2983, H.5222).
- Log every merge to out/dedupe_log.csv (kept id, dropped ids, reason).

## 2. just_cause_eviction scope: AGREED, with one carve-in
- In scope: provisions that limit the grounds for eviction or non-renewal, plus their relocation-assistance duties.
- Also in scope (as already decided in the gold set): LOCAL notice-of-rights ordinances tied to eviction/non-renewal (Boston HSNA, Cambridge ch. 8.71). Title them "[notice-only]", key_value "Notice-of-rights requirement only; no just-cause protection", conflict_flag true.
- Out of scope: general notice-to-quit periods (M.G.L. c.186 § 11, § 12) and anti-retaliation provisions (c.186 § 18; Newark § 19:2-14 = r-0074). Drop them from rules.json (log them in out/out_of_scope_log.csv so we can show the judges we considered them).
- Re-run the ~5 MA docs (~$0.15) after updating the prompt.

## 3. Newark (r-0075 to r-0078): ONE headline record
Legal reading of D070:
- r-0075 (CPI cap, max 4% per year at lease renewal) is the headline rent_increase_limits rule. Keep it.
- r-0076 (new construction exempt for the lesser of the initial mortgage amortisation period or 30 years) is a COVERAGE condition of r-0075, not a separate rule. Fold into r-0075 `exemptions` and `coverage_conditions` (structured: exempt if construction completed within 30 years; Module B: NJ year_built is often missing -> unknown).
- r-0077 (10% one-off increase after rehabilitating a vacant unit) is a narrow vacancy exception. Fold into r-0075 notes.
- r-0078 (25% in any one year) is a ceiling on increases the Rent Control Board itself may GRANT (combined CPI, capital-improvement and hardship surcharges within 12 months). It is not the tenant-facing annual cap. Fold into r-0075 notes as "Board-granted surcharges (major improvements, hardship) plus CPI increases may not exceed 25% in any 12 months (§ 19:2-22)".
- Apply the same pattern to Jersey City and Hoboken rent control if they produced similar sub-records.

## 4. 60-day status: CONFIRMED
in_force + conflict_flag true + note "Adopted within 60 days of query date; treat as unknown pending confirmation of effective date". Module B will translate this into the address result `unknown`.

## 5. Recapture: YES, single pages via Bright Data (organiser-approved; log retrieval date)
- San Diego source of income (Div. 8): try the official PDF first: https://docs.sandiego.gov/municode/municodechapter09/ch09art08division08.pdf (same pattern as D073). Save as corpus_supplementary/text/D075.txt (move the old TOC-only file to corpus_supplementary/_to_delete/D075_toc.txt; do not delete).
- Newark D071: recapture the intended page; same handling.
- Then extract only those docs.

## 6. Negative findings: add an automated derivation step
The judges' key contains 19 "no rule at this level" findings, so these count. Add derive_negatives.py (runs after verify.py, before eval.py):
- For every in-scope jurisdiction x category cell (3 states + 10 cities x 6 categories) with NO surviving rule, emit a record with negative_finding true, derived true, status in_force, title "No rule at this level", key_value "No [category] rule found at [jurisdiction] level in the corpus".
- If an extracted rule expressly bars or pre-empts local rules in that category (e.g. M.G.L. c.40P bars local rent control), cite and quote it in the derived record and set confidence 0.8; otherwise citation "None found in corpus", quoted_span null, confidence 0.5.
- Never derive a negative finding for a cell where a pending bill exists without also keeping the pending record.
This is automated reasoning over the corpus, not hand-coding.

## 7. Scoring
The independent v0.3 gold set is being copied to my Mac now (gold/rules/dev.json etc.). When gold/rules/dev.json exists, point eval.py at it (not the silver gold_rules.json) and re-score. Never read gold/rules/test.json.

## Then
Apply 1-6, re-run only what changed (MA docs, D075, D071), run verify -> derive_negatives -> eval, show the table, commit (still not gold/).
