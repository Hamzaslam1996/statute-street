# Rulings from Hamza — after scoring against the independent gold (rulings_04)

## 1. Negative findings and the schema: keep rules.json schema-valid
- out/rules.json (the submission file) = schema-valid records only (positive rules + negatives that have a real citation and quoted span, e.g. the M.G.L. c.40P one).
- out/negatives.json = all derived "no rule at this level" findings, for Module B, the UI and the README.
- Do NOT put schema-invalid records into the submission. Mention negatives.json in the README as an extra file.

## 2. Effective dates (12/39 exact): diagnose, then improve with stated dates only
Step A (no API cost): list the 27 date mismatches in out/date_mismatch.md, one line each: rule, gold date, our date, and the reason class:
  (a) date is in another corpus doc for the same section (history note / bill page / agency page),
  (b) ours null because no doc states it,
  (c) different date convention (adoption month vs effective day, rate-period start, etc.),
  (d) genuine error.
Step B: refine ruling 2 of rulings_01. A statutory HISTORY NOTE or bill/agency text that EXPLICITLY states an effective or operative date (e.g. "Added by Stats. 2019, Ch. 597 (AB 1482), effective January 1, 2020", "This act shall take effect January 1, 2020") IS a stated date and may be used. Still never compute a date from a chapter number or enactment year alone.
Step C: add date_resolve.py, run after verify.py: for each rule with null or doubtful effective_date, search ALL corpus + supplementary docs that cite the same section/act for such explicit statements; take the date that matches ruling 1 (date the extracted requirement first took effect, or the amendment that changed the key value). Record date_source_doc_id and the quoted date sentence in notes. Pure text search + regex first; use a small Sonnet call only to pick between candidate sentences. Budget cap $1.
Step D: re-score and show me the new date accuracy and what remains in class (b)/(c)/(d).

## 3. Small folds
- Newark § 19:2-22 (25% board ceiling) -> fold into the Newark CPI-cap record's notes (one targeted prompt line, ~$0.17 OK).
- NJ N.J.S.A. 46:8-26 ("application of act") -> fold into the NJ security-deposit record's exemptions (owner-occupied <= 2 units, seasonal), not a separate rule.

## 4. Then commit and push
git add the code and out/ files (not .env). Push.

## 5. Then start Module B
Read instructions/module_b.md and follow it. Use out/rules_full.json (rules + negatives) as the rule input. Stop and show me out/coverage.json for the rent-control rules before the full 500-address run.
