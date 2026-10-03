# Statute Street — Rental Housing Law Navigator

Hack-Nation 7th Global AI Hackathon, Challenge 02 (sponsor RealPage).
For any U.S. apartment address in scope (CA, NJ, MA; ten cities), report which
rental-housing rules apply as of a date, each cited to source text.
**Not legal advice.**

## Module A — rule extraction (automated)

```
source .venv/bin/activate
python extract.py --all            # Claude reads every corpus document -> out/raw/D###.json (cached)
python verify.py                   # exact-quote check, status from dates, dedupe -> out/rules.json
python derive_negatives.py         # "no rule at this level" findings -> out/negatives.json
python eval.py                     # score against gold -> out/eval_report.md
```

| File | What it is |
|---|---|
| `out/rules.json` | **Submission file.** Schema-valid rule records only (`{"rules": [...]}`): extracted rules plus negative findings that carry a real citation and quoted span (e.g. M.G.L. c. 40P barring local rent control). |
| `out/negatives.json` | **Extra file.** All derived "no rule at this level" findings for the 13 jurisdictions x 6 categories, including those with no citing text (so not schema-valid). Used by Module B and the UI. |
| `out/rules_full.json` | `rules.json` + all of `negatives.json`, the input to Module B. |
| `out/extract_log.csv` | Every model call: document, model, tokens, cost, time. |
| `out/verify_log.csv`, `out/dedupe_log.csv`, `out/out_of_scope_log.csv` | Audit trail: quote checks, merges, provisions considered but excluded. |
| `out/eval_report.md` | Scores against `gold/rules/dev.json`. |

Rules of the pipeline (see `CLAUDE.md` and `instructions/rulings_*.md` for the
lawyer's rulings they implement): every record's `quoted_span` must be an
exact passage of its source document; `status` is computed in code from the
effective date and the query date (default 2026-10-01); effective dates are
only ever taken from text that states them, never computed from chapter
numbers; secondary sources are capped at confidence 0.7.

Corpus: the organisers' starter pack (read-only) plus `corpus_supplementary/`
(single-page captures of link-only sources, with retrieval dates in
`capture_log.csv`).
