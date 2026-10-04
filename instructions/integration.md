# Integration: make the platform fit visible (Hamza, 4 Oct)

No API calls. Run after rulings_12. Facts only; no claims about any company's products beyond what is stated here. Do not put any company name or logo into the product UI; the README and deck may describe the fit factually.

## 1. README: new section "Where it fits in a property operating system" (after "Determinations as data")
Positioning sentence: "Statute Street is the legal layer for a property operating system: dated, evidence-backed determinations for every address, so pricing, leasing and screening act within local, state and federal law."
Three touchpoints, each 2 to 3 sentences:
1. Pricing gate. Before a rent recommendation is issued for a unit, the pricing engine queries the determination for that address and date in the category algorithmic_rent_setting and rent_increase_limits: permitted, permitted with conditions, restricted, or unknown with the missing fact. The operator keeps the final say; the determination carries the rule, the quote and the as-of date.
2. Property record. Determinations are stored against the unit in the system of record with their as-of date, citation and quoted text, and refreshed when the change register posts a new effective date.
3. Lease administration. A reliance record is generated at each lease event (increase notice, renewal, termination) and kept with the lease, so an audit shows what was known on the day.
Distribution: certified integration marketplaces of property management platforms (for example RealPage Exchange), where partner apps connect through standardised APIs. One sentence, no more.

## 2. README: "Pricing gate example" (code block)
Show a worked example from out/lookups.json using A0002 (Hoboken) on 2026-10-01 and on 2027-07-02: the rows for the algorithmic_rent_setting category, as the integrator would read them: address_id, legal city, as_of, then for each row team_rule_id, title, result, explanation, conflict_flag. Then a 6 line pseudo-code "gate" function: if any row in the category has result applies with a prohibition, return restricted with the rule; if not_yet_effective, return permitted now, restricted from <date>; if unknown, return review with the missing fact; include conflict_flag as needs_review. State plainly that this is a static file today and would be an API in production.

## 3. Method page (UI) and public door
- Add a short "Where it fits" paragraph to src/data/method.json (create it; the UI reads method text from data if the Method page supports it; otherwise write it into docs/UI_FIXES_02.md as a one-line change request for Lovable with the exact text) containing the positioning sentence and the three touchpoints as three short lines.
- Early-access band on the public door: change the label line to "Built to sit inside the systems operators already run: a compliance gate for pricing, a legal layer for the property record." Put this in docs/UI_FIXES_02.md for Lovable (do not edit UI components yourself).

## 4. Method note PDF
Add one sentence to submission/METHOD_NOTE.md under Approach: "Determinations are data: a pricing engine or leasing agent can query them for an address and date before acting." Hamza re-renders the PDF.

## 5. Commit by name, push, report.
