# Statute Street: method note

Hack-Nation 7th Global AI Hackathon, Challenge 02 (RealPage). Legal information, not legal advice.

## Problem

Rental housing rules in California, New Jersey and Massachusetts are set at state and city level, change on dated schedules, and turn on building facts that public records only partly hold. Whoever manages a building needs to know, for a given address and date, which rules bind, which do not, and where the answer depends on a fact nobody has recorded, with the quoted law behind each answer.

## Approach

Extraction with verified quotes. A language model reads each of 98 documents (the supplied corpus plus single page captures of link-only sources) and returns structured rule records. Every record must carry a quoted span that is an exact passage of its source; failing quotes are retried once and otherwise dropped. Status is computed in code from stated effective dates, never taken from the model. Duplicates across documents are merged with the folded sources kept as supporting evidence, and the supplied corpus is preferred as primary evidence. Where a level has no rule in a category, a negative finding says so.

Deterministic engine. Addresses are resolved to their legal city with the Census Geocoder. Each rule's coverage text is turned once into machine checkable tests, with the words each test came from. The engine then decides applies, unknown, superseded, not yet effective or pending for each address and rule, with one sentence naming the deciding fact. Year built is only a proxy for a certificate of occupancy date, so a cutoff year building is unknown. Owner identity is not in the data, so owner based exceptions are unknown unless the use code rules them out. Narrow use or funding exemptions are presumed not to apply and are listed as assumptions ("Applies unless").

Change tracking. The engine is run at the dates each change test names; affected sets are set arithmetic. No model is involved.

Determinations are data: a pricing engine or leasing agent can query them for an address and date before acting.

## Validation

Against an independently built key applying the same reviewed legal rulings: Module A 39/39 rules on the dev split and 15/15 on the test split (single run at tag v1.0-submission-candidate); Module B 569/569 on seed60, 190/190 on seed20 and 192/192 on a blind holdout of 20 addresses (single run); Module C 5 of 5 change tests exact. Across the 500 addresses the unknown rate is 27.3% and 2,079 of 5,298 rows rest on a stated presumption. These figures test faithful implementation of the reviewed rulings, not legal correctness beyond them; the organisers' hidden key is the real test. A stress test scored the submission against six alternative exemption policies; the current policy had the best worst case (83.0% exact) and the best mean (93.3%). A fresh clone reproduces all output files byte for byte without model calls.

## Responsible design

Unknown always names the missing fact. Conflicts (for example the New Jersey FAIR Act's possible pre-emption of local bans) are flagged for human review, never decided. Enacted law, pending bills and failed measures are kept apart. Only public data is used. Every rule records its evidence basis: 47 rules cite the supplied corpus, 12 our captures of link-only sources, 5 hand saved pages, per the organisers' ruling that only supplied text counts toward the citation metric. Every answer carries an as-of date, citation and quoted text; Spanish summaries accompany every rule.

## Limits

No amounts are computed and no case is decided. No owner data exists. New Jersey unit counts are absent; counts parsed from building codes are shown but not asserted. Coverage tests outside the rent control rules rely on the model's reading of the text. Newark's chapter 2:10 text could not be captured.
