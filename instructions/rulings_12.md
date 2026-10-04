# Rulings 12: shipping-grade data for the UI (Hamza, 4 Oct)

No API calls. Data and export only; do not touch UI code (Lovable handles docs/UI_FIXES_01.md). Submission files in submission/ stay as they are unless a change below alters out/rules.json or out/lookups.json; if it does, regenerate submission/ and SHA256SUMS and say so.

## 1. Conflict flags: only genuine open questions
A flag means "a human must review a legal question we do not decide". Apply:
- KEEP flagged, with these exact public notes (rule conflict_note and lookup explanations):
  - r-0044 NJ FAIR Act, r-0023 Hoboken, r-0026 Jersey City: "Possible preemption: from 1 July 2027 the NJ FAIR Act may preempt the Hoboken and Jersey City algorithmic rent ordinances. Flagged for human review; not decided here."
  - r-0001 Berkeley algorithm ban: "Open question: two published effective dates (1 March 2026 in the ordinance text; January 2026 in an August 2026 law firm alert). Flagged for human review."
  - r-0030 LA RSO allowable increase: "Open question: two published effective dates for the new formula (2 February 2026 per LAHD; 24 January 2026 per a landlord association). Flagged for human review."
- UNFLAG (conflict_flag false; keep the text as a plain note, rewritten for the public):
  - r-0008 Boston HSNA and r-0021 Cambridge notification ordinance: note "Notice of rights requirement only; it does not limit the grounds for eviction."
  - n-0002, n-0030: note "A pending bill could change this; see the change register."
  - r-0002, r-0003 (Berkeley BMC 13.78) and r-0014 (CA Civ. Code 1950.6) lookup flags: this is not a conflict. State law sets a ceiling and Berkeley adds stricter local limits; both apply. Remove the cross-rule flag for this pair in the engine's conflict pass (narrow the pass so it only flags where a rule's own text or the rule record states possible preemption), with explanation on the Berkeley rows "State fee rules apply; Berkeley adds stricter local limits."
- Report how many addresses are flagged before and after (expected about 90 plus the Berkeley and LA open-question rows).

## 2. Public text hygiene on every rule
In out/public and the UI export, conflict_note and notes must read as public product text: no "this capture", "this document", "the brief", "our team", "flagged by our team", model or pipeline language, ids like HOB-ALG-01 or r-0023 inside prose, raw enum words (not_yet_effective, applies) inside sentences. Write a filter plus a hand-written override map for anything the filter cannot fix cleanly; list every changed note in the report.

## 3. Change register display data
Write src/data/change_register.json in the UI repo (via export_ui.py, so it is reproducible) with exactly these five rows; keep affected and review counts computed from changes.json:
- T1: title "California bans common pricing algorithms"; instrument "AB 325 (Stats. 2025, ch. 338), Cal. Bus. & Prof. Code § 16729"; jurisdiction "California"; enacted: the adoption date from our rule record if stated, else "Not stated"; effective "2026-01-01"; status in force; summary "From 1 January 2026, using or distributing a common pricing algorithm as part of a price-fixing arrangement is unlawful. Applies to every California address in the portfolio."
- T2: title "Hoboken and Jersey City algorithm bans"; instrument "Hoboken Code ch. 158; Jersey City Ord. 25-057"; jurisdiction "Hoboken, NJ; Jersey City, NJ"; enacted/effective from our rule records; status in force; summary "Each city's ban applies only inside its own boundary, decided by the geocoded legal city, never the mailing address. Newark has no such ordinance."
- T3: title "New Jersey FAIR Act"; instrument "P.L. 2026, c. 43"; jurisdiction "New Jersey"; enacted "2026-07-20"; effective "2027-07-01"; status not yet effective; summary "Statewide ban on algorithmic rent setting from 1 July 2027. It may preempt the Hoboken and Jersey City ordinances; those addresses are flagged for human review."
- T4: title "Massachusetts algorithm bills"; instrument "S.2983 and H.5222 (194th General Court)"; jurisdiction "Massachusetts"; enacted "Not enacted"; effective "Not set"; status pending; summary "Pending bills, not law. If enacted they would reach every Massachusetts address in the portfolio."
- T5: title "Massachusetts rent control ballot question"; instrument "Initiative Petition 25-21"; jurisdiction "Massachusetts"; enacted "Not enacted"; effective "None"; status failed; summary "Struck from the ballot by the Supreme Judicial Court on 23 June 2026 (Cella v. Attorney General). No rent cap is reported for any Boston or Cambridge address."
Use "Not stated" or "Not enacted" wording, never "Not in data".

## 4. Meta counts
meta.json: add rules_in_force (positive rules) and negative_findings separately, so the footer can read "64 rules · 30 negative findings".

## 5. Re-run engine, changes, publish, export_ui; re-run tests and the seed60 / seed20 / holdout20 regression check (results must not change except conflict flags). Commit by name in both repos, push, stop, report.

## 6. Also (from the user-perspective review)
- Check every lookup `explanation` sentence for public readability: starts with a capital, no ids, no enum words inside prose, names the missing fact in plain words ("units not in data", "year built not in data", "owner identity not in data", "affordable housing status not in data"). Where the engine writes "Unknown: X not in the data (Y)", rewrite to "Unknown: needs <fact>. Exemption that depends on it: <Y in plain words>." Report the distinct explanation templates before and after.
- export_ui.py: write `use_description` into addresses.json (already present) and confirm `key_value` is present on every positive rule where the record has one; list rules with no key_value.
- Commit ../statute-street-ui/docs/UI_FIXES_01.md by name in the UI repo and push, before the Lovable step.

## 7. Row text that a user can read (from the five address, record and notice screenshots)
Do all of this in the engine / publish / export layer (no API calls). The user is an operator reading one row in two seconds.

7a. `key_value_short`: author, by hand, in a reviewed file `data/key_value_short.json` (team_rule_id to text), one line of at most 70 characters per positive rule, operator facing, numbers and dates kept, no extraction commentary. Examples:
  r-0016 "Cap: 5% + CPI, max 10%, per 12 months; max two increases"; r-0030 "Once per 12 months at the LAHD allowable percentage; no utilities add-on"; r-0059 "Cap: 1.6% per year (1 Mar 2026 to 28 Feb 2027)"; r-0014 "Fee cap: $30 per applicant, CPI adjusted"; r-0019 "Deposit cap: 1 month's rent (2 for small landlords)"; r-0029 "Relocation: $11,000 to $27,400 by tenant status"; r-0008 "Notice of rights required at termination"; r-0027 "Rent control; 1 to 4 unit buildings exempt"; r-0033, r-0034 (pending bills, no key value): "Bill, not law: would ban algorithmic rent setting".
  Export it on every UI rule record; keep the long `key_value` for the expanded panel. Also clean the long key values: remove parentheticals like "(percentage is in a linked PDF, not in this text)" and "(the specific cap formula is not stated on this page)"; move that information to `notes`.

7b. Superseded rows: add `governed_by` (team_rule_id of the governing rule) to the lookup row and write the explanation as "Governed instead by <full title of governing rule>; the stricter local rule applies here." Never print an id inside prose.

7c. Explanation templates (public):
  - applies with a tested fact: "Applies: <fact in plain words>." e.g. "Applies: 32 units, above the coverage threshold." Never a bare "32 units" or a lowercase fragment like "covers all residential rentals in CA" (make it "Applies to all residential rentals in California.").
  - applies with presumption: "Applies unless <exemption in plain words>. Built 1927, before the 1 Oct 1978 certificate of occupancy cutoff; apartments per the assessor."
  - unknown: "Unknown: needs <fact>. <one sentence on why it matters>." For the LA JCO at pre-1978 buildings specifically: "Unknown: this building is under the RSO (built 1927), so the JCO applies only if the unit is exempt from the RSO; RSO exemption status is not in the data."
  - negative findings: explanation "No <category in plain words> rule at the <city> level; state law applies." and key_value_short "No city rule; state law applies". Never the word "corpus" in public text.
  - Dates inside prose in "1 Oct 1978" form, never ISO.
  Report the distinct templates before and after and 10 random rows.

7d. index.ts contract: tell the UI (docs/UI_FIXES_01.md already permits) optional fields `key_value_short` on rules and `governed_by` on lookup rows.

## 8. Order of work
rulings_12 §1 to §7, rebuild, regression check (seed60 / seed20 / holdout20 unchanged except conflict flags), regenerate submission/ only if out/rules.json or out/lookups.json changed (they will, because of explanations and flags; say so and refresh SHA256SUMS), export_ui, commit by name in both repos, push, report.

## 7e. Exemption phrases are curated, never raw spans
Lookup explanations and `assumptions` currently splice raw coverage text, giving broken sentences such as "Applies unless the property falls within the exemption for Medical/long-term care and detention facilities are excluded from the definition." and truncated ones such as "(May not apply to owner-occupied premises with two (2) or few)". Fix: a hand-written map `data/exemption_phrases.json` from each coverage test id (or rule id plus test index) to a plain noun phrase, e.g. "a medical, long-term care or detention facility", "an owner-occupied building with two or fewer rental units", "a hotel, motel or seasonal rental", "a resident-owned cooperative or government-owned housing". The engine composes: "Applies unless the property is <phrase>." / "Unknown: needs owner identity. Exemption that depends on it: <phrase>." / assumptions list items "Not <phrase>". Every phrase in the map is reviewed text; fail the build if a test lacks a phrase. Report the map size and 10 random composed sentences.
