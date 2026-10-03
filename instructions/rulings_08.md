# Rulings 08 — cleanup + UI export prep (Hamza, 4 Oct)

No API calls. From now on stage files BY NAME (never `git add -A`), so other sessions' files are committed in their own commits.

1. **MA-FEE-02 duplicate:** two of our records cite c.112 § 87DDD½ differently ("87DDD-1/2" and "87DDD½"). Fold into one (keep the one whose quote comes from the mass.gov primary text), log in dedupe_overrides.json / dedupe_log.csv. Re-run Module A eval (39/39), rebuild lookups/changes, re-score seed60/seed20/holdout20 — report only if anything moves. (Holdout re-score here is a regression check after a dedupe, not tuning; say so in the README.)
2. **README honesty line** in the scores section: "Agreement figures measure our engine against an independently built key that applies the same reviewed legal rulings; they test faithful implementation, not legal correctness beyond those rulings. The organisers' hidden key is the real test." Also state the whole-sample unknown rate (26.7%) and presumption count (2,081 rows "applies unless …").
3. **Public-facing text:** write out/public/ copies of rules.json, lookups.json, changes.json in which explanations/notes contain no internal reviewer text: strip phrases like "Decided by Hamza…", "(Q5)", "ruling #", "rulings_0x", "L1xx", "gold". Keep citations, quotes, dates, assumptions, "Applies unless …" and "flagged for human review" wording. Do NOT change the submission files in out/ except by the same filter if they contain such text — show me a count of strings removed.
4. Commit (by name) and push. Stop.

UI export to the Lovable repo comes next in ui_export.md once I have the repo name and the UI's field contract.
