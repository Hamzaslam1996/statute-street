## 4. Reproducibility

Fresh `git clone` of the navigator repository into a sibling folder (`../navigator_repro`, HEAD db0b61b), new
virtual environment from `requirements.txt`, `ANTHROPIC_API_KEY` set to an invalid value so that any model call
would fail loudly. Pipeline run in cache-only mode:

`verify.py --no-retry` → `date_resolve.py --no-model` → `derive_negatives.py` → `translate_es.py --no-model` →
`coverage.py --no-model` → `engine.py` → `engine.py --use-derived-units` → `changes.py` (+ the two `--diff` runs) →
`open_questions.py` → `publish.py --in-place`.

Result: pipeline exit 0; no model call was made (log contains no API or authentication message; coverage and
date caches served every record). Byte comparison against the committed files:

| File | Result |
|---|---|
| out/rules.json, rules_full.json, negatives.json | identical |
| out/lookups.json, lookups_derived.json | identical |
| out/changes.json, changes_detail.json | identical |
| out/coverage.json, open_questions.json | identical |
| out/public/rules.json, lookups.json, changes.json | identical |
| out/diff_2025-12-31_2026-01-02.json, diff_2026-10-01_2027-07-02.json | identical |

14 of 14 files identical. The repository therefore reproduces the submission from its committed caches
without network access to the model API.
