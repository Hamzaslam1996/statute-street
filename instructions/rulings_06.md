# Rulings 06 — seed60 disagreements (Hamza, 4 Oct)

Apply AFTER the current rebuild finishes. Do not start Module C.
Never read gold/rules/test.json. Do not tune to individual addresses: implement the principles below and let the scores fall where they fall.

## 0. Git
- The gold v0.4 files already went out inside commit 84c4030. Do NOT rewrite history or force-push. Just note it in the README audit trail.
- D094 is missing from corpus_supplementary/text/. Do not recreate it; list it as missing in your report (the gold session will redeliver).

## 1. Core principle: coverage condition vs exemption (fixes ~50 of 80 misses)
Tag every condition the engine tests with one of three kinds:

A. **coverage** — the law reaches the property only if the condition holds (e.g. Boston Fair Chance applies only to DND/IDP-funded providers; NJ unit-count thresholds). Data missing → `unknown`. (Unchanged.)

B. **niche_exemption** — an exception for a narrow ownership/funding/use class that the party claiming it must prove. Legal basis: exemptions to remedial housing statutes are construed narrowly, and the burden is on the person claiming them. Data missing → `applies`, with the explanation starting "Applies unless …" and the exemption listed in a new `assumptions` array on the lookup row. Classes:
   - nonprofit / resident-controlled cooperatives
   - public housing, government-owned units, units under a government contract, Section 8 project-based exemptions
   - deed-restricted / subsidised affordable housing (incl. software used to set rents under affordable programmes, e.g. SD-ALG-01)
   - transient / vacation occupancy (e.g. MA c.186 §15B: tenancies of 100 days or less for vacation purposes; hotels/motels)
   - owner shares kitchen or bath with the tenant, **when the use code shows 3+ units**
   - hospitals, dormitories, religious facilities, care facilities

C. **plausible_exemption** — an exception the data cannot rule out and that is common for this property type. Data missing → `unknown`. Includes:
   - owner-occupied 2-family (MA c.151B) or owner-occupied 1–4 unit exemptions, when unit count is within the threshold or unknown
   - AB 1482 single-family / condo owned by a natural person, when the use code is SFR/condo
   - new-construction cutoffs where year_built is inside the window or equals the cutoff year
   If the use code makes the exemption impossible (e.g. 5+ unit apartments vs a 1–4 unit owner-occupied exemption), it's not an issue: `applies`.

Tenancy-timing conditions (e.g. LA-JUST-01 "after 6 months of tenancy") are NOT coverage conditions. They set when a tenant's protection starts, not whether the property is covered → `applies` + assumption "protection begins after 6 months' tenancy".

## 2. Specific fixes
1. **Precedence before cutoff tests (CA-JUST-01, 18 rows).** Evaluate Civ. Code §1946.2(i) precedence first. In Los Angeles, LA RSO + LA JCO together cover every residential rental unit, so state AB 1482 just cause is `superseded` for every LA residential address whatever the year built. Apply the same pattern wherever a local just-cause rule `applies` (SF, Berkeley, San Diego TPO): state = `superseded`. Only fall back to the COO test when the local rule is `unknown`.
2. **Always report every in-jurisdiction rule** (BOS-SCRN-02, NJ-FEE-01, the 2 CA-JUST-01 rows): never drop a row; emit `unknown` with a reason instead of omitting it.
3. **LA RSO cutoff year (LA-JUST-02).** RSO covers units with a certificate of occupancy before 1 Oct 1978. year_built < 1978 → applies; year_built == 1978 → `unknown` (cutoff year); > 1978 → does not apply (JCO instead). Fix the `<=` bug.
4. **SD-SCRN-01 "applicability text not available".** Check which document the rule came from. If its source text has no coverage limitation for residential rentals → `applies` (citywide). Only keep `unknown` if we genuinely never captured the operative text; say which.
5. **MA-SCRN-01** is a plausible_exemption case (owner-occupied two-family, c.151B §4(6)): `unknown` when unit count ≤ 2 or unknown; `applies` when the use code shows 3+ units. Do NOT apply that exemption to source-of-income / public-assistance discrimination if the rule is §4(10).

## 3. Then
- Rebuild lookups.json for all 500 addresses.
- Re-score seed60 AND seed20 and show before/after tables side by side, plus: our unknown rate across all 500, count of rows that rely on an `assumptions` presumption, and any NEW disagreements (gold unknown → ours applies) introduced by this change, listed in full.
- Add unit tests for: niche exemption → applies with assumption; plausible exemption → unknown; 1978 cutoff; LA precedence; no dropped rows.
- README: short "Exemptions and presumptions" section explaining A/B/C in plain words.
- Commit and push. Stop and wait for me before Module C.

## 4. Addendum — gold v0.4.1 (Hoboken) and the Hoboken engine test
- FIRST, before any rebuild or re-score: commit and push the gold v0.4.1 files on their own, message "gold v0.4.1 (Hoboken ch. 155)": gold/rules/{all,dev,test}.json, gold/adjudication_log.csv, gold/addresses/seed{20,60}.json, gold/build_addresses.py, gold/apply_v041.py, gold/README.md, sources/source_register.csv, sources/official/S-MAN-15.txt. Do not open gold/rules/test.json — just stage it.
- Hoboken rent control (§ 155-2 / § 155-5) in the engine must use the query date (--as-of), not a fixed year:
  - year_built ≤ 1987 (built on/before 1987-06-25) → applies
  - built after 1987-06-25 and as_of − year_built ≥ 30 full years (use year_built + 31 ≤ as_of year to be safe) → applies
  - otherwise post-1987 → unknown (exemption lasts the shorter of the mortgage term or 30 years; mortgage term is not in the data)
  - year missing → unknown
  - cap value: lesser of 5% or CPI change, once per 12 months; citation Hoboken Code § 155-5, applicability § 155-2.
