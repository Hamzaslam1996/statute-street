# Rulings from Hamza — after batch 2 (14 docs)

## A. D024 "March 15, 2019" is not an effective date
That clause is a retroactive look-back (it reaches back to increases made after 15 March 2019); it is not the date the statute took effect.
Rule: look-back, application or "applies to increases on or after" dates are NOT effective dates. Only text that says the provision "takes effect", "becomes operative", is "effective" or "operative" on a date counts.
If none exists in the document, effective_date = null with a note. An enacted section in the official code with null effective_date is still status in_force.
Do not hand-code 2020-01-01. The gold set will carry it; the date-field mismatch is acceptable.

## B. Ordinances that state only an adoption date
The schema allows month precision (YYYY-MM), and the challenge brief itself cites local bans by month ("Jersey City §218-12 (Jun 2025)", "Hoboken ch. 158, Art. II (Jul 2025)").
Rule: if a local ordinance gives an adoption date but no effective date, set effective_date to the adoption MONTH (YYYY-MM) and add a note: "Month of adoption; exact effective date not stated in source (NJ ordinances generally take effect after final passage and publication)." Add a field adoption_date with the full date.
- D034 Hoboken: art. I (Ord. B-750) -> "2025-04", adoption_date 2025-04-02; art. II (Ord. B-781) -> "2025-07", adoption_date 2025-07-09.
- D001 Berkeley: search the full text for any "effective", "operative" or "take effect" phrase. If none, null and conflict_note: "README: ordinance text states 2026-03-01; Morgan Lewis alert (Aug 2026) states January 2026. Not found in this capture." Set conflict_flag true.
- D041 LA: "Effective February 2, 2026" for the formula changes is an explicit effective date tied to a change in the key value -> use 2026-02-02 for that rule (ruling 1 exception). conflict_flag true, conflict_note: "Landlord association source states 2026-01-24 (README open question)."
Status rule: an ordinance adopted more than 60 days before the query date with no stated effective date -> in_force. Within 60 days -> unknown, with a note.

## C. Fragment spans
Agreed. Quote the complete sentence where one exists. For list-form provisions, quote the lead-in plus the relevant item (e.g. "It shall be unlawful for any person to ... (e) ..."). Raise the max span length to 800 characters. Re-run D069 and D041.

## D. Granularity: one record per headline requirement
Target: one record per jurisdiction x category x section, holding the headline requirement (the number or prohibition a renter or landlord would act on). Fold procedural sub-duties into `requirement` or `notes` (21-day return, photographs, itemised statements, "no non-refundable deposits").
Keep separate records only when they fall in a DIFFERENT category or carry a DIFFERENT key value that changes an address-level answer.
- D025: one security_deposits record (1 month; 2 months for qualifying small landlords; eff. 2024-07-01). Sub-duties into notes.
- D083: rent increase 1.6% -> rent_increase_limits; deposit interest -> security_deposits; relocation schedules -> fold into the SF just_cause_eviction record's notes (relocation follows a no-fault eviction), not separate records.

## E. Massachusetts
- M.G.L. c.40P § 4: keep it, but as a NEGATIVE finding. Fields: category rent_increase_limits, negative_finding: true, title "No local rent control permitted (state bar)", key_value "No rent cap: state law bars local rent control", status in_force. Module B must display this as "No rent cap applies" and must never output it as a cap that "applies".
- Ballot question IP 25-21 (D059): keep, status failed, negative_finding: true. Module B excludes failed records from address answers except as a change-history note. This is exactly T5.
- Add negative_finding (bool, default false) as an extra field on all records. The schema does not forbid extra fields; confirm that, then proceed.

## Then
1. Apply A-E to the prompt and verify.py, re-run only the affected docs (D001 D024 D025 D034 D041 D048 D059 D069 D083), and show the table plus the eval.
2. If quotes still pass and nothing new needs my ruling, run --all on the remaining docs with a hard budget stop at $5.00 total session spend. Report: rules per doc, quote pass rate, docs with zero rules, total cost.
3. Commit after the --all run. Still do not commit gold/.
