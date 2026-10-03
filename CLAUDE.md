# Statute Street — project briefing for Claude Code

Hackathon: Hack-Nation 7th Global AI Hackathon, Challenge 02 "Rental Housing Law Navigator" (sponsor RealPage).
Owner: Hamza (commercial/IP lawyer). Explain things in plain language; he is not a career developer.
Product: for any U.S. apartment address, report which housing rules apply as of a date, each cited to source text. Not legal advice.

## Folder layout (repo root = this folder, `navigator/`)
- `../participant-final-no-hour16 3/` — organisers' starter pack. **READ-ONLY. Never modify.**
  - `corpus/text/D###.txt` (54 docs; header lines `SOURCE:` and `RETRIEVED:`), `corpus/corpus_manifest.csv` (87 rows)
  - `data/sample_addresses.csv` (500 rows), `schema/rule_record.schema.json`, `dev/change_tests.json` (T1–T5)
  - `submission_templates/{rules,lookups,changes}.json`, `README.md` (participant guide — read first)
- `corpus_supplementary/text/D###.txt` — 31 link-only pages we captured (same header + `CAPTURED_VIA:`); `capture_log.csv`
- `gold/` — answer keys. `gold_rules.json` is a SILVER AI draft; an independent gold set is being built in another session into `gold/rules/`, `gold/addresses/`, `gold/changes/`. Do not edit gold files unless Hamza asks.
- `.env` — API keys (`ANTHROPIC_API_KEY`, `BRIGHTDATA_API_TOKEN`, `BRIGHTDATA_ZONE`). **Never open, print, copy or commit.** Code loads it with python-dotenv.
- Python: `.venv` (Python 3.13). Activate with `source .venv/bin/activate`. Install new packages with pip and add them to `requirements.txt`.

## Fixed rules of the challenge
- Default query date **2026-10-01**. Scope: CA, NJ, MA; cities LA, SF, San Diego, Berkeley, Santa Ana (extraction only), Jersey City, Hoboken, Newark, Boston, Cambridge.
- Categories (exact slugs): rent_increase_limits, just_cause_eviction, security_deposits, application_screening_fees, screening_restrictions, algorithmic_rent_setting.
- Rule status: in_force | not_yet_effective | pending | failed. Address result: applies | unknown | superseded | not_yet_effective | pending.
- **Extraction must be automated** (judges rerun it live). No hand-coded rules.
- "unknown" is a valid answer when a needed fact is missing. Never guess.
- Organiser rulings: no score.py or dev key will be shared; T6 removed; single-page fetches of link-only sources allowed with retrieval date; no bulk scraping.
- Traps: year built ≠ certificate-of-occupancy (SF cutoff 1979-06-13, LA 1978-10-01; cutoff year → unknown); postal city ≠ legal city (Dorchester = Boston); no owner data; many missing unit counts and years.

## Current task: Module A (rule extraction)
Build three scripts, test on 3–5 documents first, then scale.

1. `extract.py`
   - Input: every `.txt` in the starter-pack corpus and `corpus_supplementary/text/`. Skip `_to_delete/`.
   - For each document, call the Claude API (model from env/CLI flag; **default `claude-sonnet-5-5`**) with the rule schema; return a JSON list of rule records (zero or more per doc).
   - Use tool use / structured output so the response is valid JSON matching `rule_record.schema.json`.
   - Long docs: chunk by section with overlap; dedupe records afterwards.
   - Cache: save raw model output per doc to `out/raw/D###.json`; skip docs already cached unless `--force`. This protects the $25 API budget.
   - Log every call (doc, model, input/output tokens, time) to `out/extract_log.csv`.
   - CLI: `python extract.py --docs D024 D063 D069` and `python extract.py --all`.
2. `verify.py`
   - Reject any record whose `quoted_span` is not an exact substring of its source doc (normalise whitespace and quotes only). Retry the doc once with feedback, else drop and log.
   - Compute `status` in code from `effective_date` vs query date (never trust the model's status for enacted laws); pending bills and failed measures keep pending/failed.
   - Attach `source_doc_id`, `source_url` and retrieval date from the file header.
   - Mark records from secondary sources (law firm/news) with lower confidence.
   - Validate against the schema; dedupe (same jurisdiction + category + citation); write `out/rules.json` in the submission format `{"rules": [...]}`.
3. `eval.py`
   - Compare `out/rules.json` to the gold set (`gold/rules/dev.json` if present, else `gold/gold_rules.json`, labelled silver).
   - Match on jurisdiction + category + citation (fuzzy citation match allowed). Report: found/missed/extra, field accuracy (status, effective_date, key_value, citation), citation-span pass rate. Print a short table and write `out/eval_report.md`.

Done when: `python extract.py --all && python verify.py && python eval.py` runs end to end, the eval report exists, and Hamza has seen the numbers.

## Model use
- Coding sessions: Fable 5.1 or Opus 5.5 (subscription).
- Inside `extract.py`: Sonnet 5.5 by default (API credit, ~$25 total). Optional `--model claude-opus-5-5` for a second pass on hard docs only (D069 FAIR Act, D001 Berkeley, D034 Hoboken, D041/D042 LA RSO).
- Always run a small batch before `--all`, and report token usage.

## Working rules
- Ask before deleting or overwriting files, before git push, and before any run over ~50 documents.
- You own git: after each working milestone, `git add` the changed code/out files (never .env), commit with a clear message, and `git push`. Also commit any new files Hamza or other sessions add under gold/, sources/, data/ or instructions/. If .git/index.lock exists and no git process is running (check with `pgrep -fl git`), remove it and retry.
- Never put secrets in code, logs or commits. Never edit the starter pack.
- Prefer simple, readable Python with comments a lawyer can follow.
- When unsure about a legal point (preemption, categories, which date governs), flag it for Hamza instead of deciding.
