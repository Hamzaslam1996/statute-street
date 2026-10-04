# UI export — real engine output into the Lovable app (Hamza, 4 Oct)

Do this AFTER rulings_08, 09 and 10 are committed. No API calls.
The Lovable app currently runs on gold/ sample data. It must show OUR engine output only (never gold/ files).

UI repo: provided by Hamza in the chat message that pointed you here (Lovable-created, two-way synced on `main`).

1. Clone the UI repo as a sibling: `../statute-street-ui` (same Keychain credentials). Do not touch anything outside `src/data/` and the README unless step 4 needs it.
2. Read `src/data/index.ts` and the current files in `src/data/` to learn the exact contract (rules.json, lookups.json, changes.json, addresses.json, sources.json; field names, required fields, how invalid records are skipped and listed on /audit).
3. Write `export_ui.py` in navigator/ that converts, deterministically:
   - rules.json ← out/public/rules.json (plus negatives: "no rule at this level" records, plain-English reason in `requirement`)
   - lookups.json ← out/public/lookups.json (all 500 addresses; keep result, explanation, assumptions, conflict_flag)
   - changes.json ← out/public/changes.json (T1–T5) plus the T1/T3 diff files if the UI uses them
   - addresses.json ← data/sample_addresses.csv + out/jurisdictions.json (legal city/state from geocoding)
   - sources.json ← sources/source_register.csv + evidence_basis from rulings_10
   No internal reviewer text ("Decided by", "(Q", "ruling", "gold", log ids). Run the same filter as rulings_08 §3 and print counts.
   If lookups.json is too large for the UI bundle, report its size and split it per city only if index.ts can load that; otherwise leave it whole.
4. Validate: run the converter's own check that every record passes the index.ts contract (mirror its rules in Python), 0 skipped. If the repo has `npm` tests/build, run `npm ci && npm run build` (and tests) locally; report.
5. Commit in the UI repo (by name): "Real engine output (rules/lookups/changes from navigator <short sha>)", push to `main`. Commit export_ui.py in navigator. Stop and report: record counts per file, bytes, build result, and 3 spot-check addresses (one CA, one NJ, one MA) with their results as they will show in the UI.

## Addendum (Hamza)
- UI repo name: `rule-navigator` (Hamzaslam1996). If the clone fails, run `git ls-remote https://github.com/Hamzaslam1996/rule-navigator` and report; do not guess other names.
- Lovable credits are limited: do all data and code changes in the repo yourself (they sync into Lovable for free). Lovable chat is only for visual design.
- In any user-facing text you write (converter output strings, README UI section), do not use em dashes or en dashes as punctuation; use commas, colons or full stops. Dates and ids keep their hyphens.
