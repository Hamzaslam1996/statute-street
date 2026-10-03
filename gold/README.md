# Statute Street — Independent Gold Set (answer key)

**Status:** v0.4.3 (2026-10-04): MA-SCRN-01 adjudicated (§ 4(10) has no owner-occupied two-family exemption → applies); holdout20.json built and frozen. v0.4.2: MA-SCRN-02 re-based on the official M.G.L. c.6 § 172 page (D094 = S-MA-12). v0.4.1: `instructions/rulings_05.md` §4a applied to HOB-RENT-01 (full ch. 155 text, `sources/manual/HOB-RENT-01_Hoboken_ch155_ecode360.txt` = S-MAN-15; verifier Hamza, 16 rows now cleared). v0.4: lawyer review batches 1–4 (`instructions/lawyer_review_01–04.md`) applied — 15 rows `verifier: Hamza` at v0.4; 14 manual primary/secondary sources (`sources/manual/`) and 8 new captures (D088–D093, D095; D075 re-captured) registered; quoted spans re-verified. Rows remain `verifier: "AI-draft"` until individually cleared. Every row carries `verifier: "AI-draft"` until Hamza upgrades it.
**This is internal test material, not legal advice.**

## Purpose
An independent, verifiable answer key used to score the Statute Street system (Hack-Nation Challenge 02, "Rental Housing Law Navigator"). It was built from primary sources and the organisers' corpus **without reading** the earlier AI-drafted "silver" key (`gold/gold_rules.json`, `gold/GOLD_REVIEW.md`) until the comparison step (Step 7). Default query date: **2026-10-01**.

## Contents
| Path | What |
|---|---|
| `schema/gold_rule.schema.json`, `gold_address.schema.json`, `gold_change.schema.json` | Schemas (all three keys validate) |
| `rules/all.json` | 87 rows: 55 rules/pending/failed entries + 32 negative findings ("no rule at this level"); every cell of the 13 × 6 matrix resolved |
| `rules/dev.json`, `rules/test.json` | Stratified split (61 / 26) — see below |
| `addresses/seed20.json` | 20 trap-exercising addresses with expected result for every rule in the jurisdiction stack (frozen; unchanged since v0.3) |
| `addresses/seed60.json` | seed20 + 40 more (60 total, every city ≥ 5) — selection method below |
| `changes/T1-T5.json` | Change-test key with affected address ids computed from `data/addresses_raw.csv` |
| `adjudication_log.csv` | Field-level disagreements with the silver key (Step 7); `decided_by` blank until Hamza decides |
| `open_questions.md` | Contested legal/categorisation questions framed as decisions |
| `silver_vs_independent.md` | Comparison report (Step 7) |
| `REVIEW.md` | Review pack sorted weakest-confidence first |
| `../sources/source_register.csv`, `../sources/official/*.txt` | 101 sources (incl. `sources/manual/` copies) with URL, retrieval time, SHA256 and saved text/excerpt |

## Method
1. Read README, change tests, schema, manifest and every corpus/supplementary header; built a 78-cell jurisdiction × category matrix with provisional labels.
2. Verified each cell against the order of authority in the brief: official statute/ordinance text → organisers' corpus copy → team supplementary capture → law-firm/news (support only). Single-page fetches only, retrieval time recorded; leginfo and sf.gov block fetching (corpus copies used, noted per row).
3. Wrote one object per rule and per negative finding. **Every `quoted_span` was checked by exact substring match against the saved source text before writing** (`build_rules.py` aborts on any mismatch). `quoted_span_in_corpus` = true only if the same span exists verbatim in the organisers' `corpus/text`.
4. `effective_date` is given only where a primary source supports it (or can be computed from an enactment clause); `YYYY-MM` where the day is unverifiable; otherwise null with the reason in `notes`. **Q17 rule (Hamza, 2026-10-04): long-standing statutes carry null unless the source text itself states an effective date.** Adoption dates go in `enacted_date`.
5. Address expectations follow the README traps: year_built ≠ certificate-of-occupancy date (cutoff-year rows → unknown); postal_city ≠ legal city; owner-type conditions → unknown unless units make the exception impossible; missing year/units → unknown. Where `units` is empty but `use_description` states a unit range (e.g. "5+ units", "APT 7-30 UNITS") the record says so and marks the inference.

## Address selection (seed60)
seed60 = the 20 seed20 rows (identical, same order) + 40 rows chosen per legal city so that every city has at least 5: SF 7, LA 7, SD 7, Berkeley 6, Hoboken 6, Jersey City 6, Newark 6, Boston 8, Cambridge 7. Within each city the picks are, in order: (1) every available cutoff-year neighbour (SF 1986 post-cutoff, LA 1977 pre-cutoff; no SF 1979 or LA 1979–80 rows exist), (2) rows missing year_built and/or units, (3) postal_city ≠ legal city (Allston, Jamaica Plain, East Boston, Roxbury), (4) recent construction that trips the 15-year COO exemption (SF 2019, Boston 2013) and NJ post-1987 new construction (Hoboken 2000/2001/2007), (5) unit-count variety for owner-type exemptions (Cambridge 6 vs 32/44/84 units), then (6) fillers drawn with `random.Random(20261004).sample(sorted(remaining ids), k)` where a city still needed rows (San Diego 5, Berkeley 3). The exact 40 ids and the reason for each are in `build_addresses.py` (`PICK40`); run `python3 build_addresses.py seed60` to regenerate. Expected results use the same coverage logic as seed20. Totals: 569 expected entries, 176 unknown (each names the missing fact); 27 rows lack year_built, 33 lack units, 9 have postal_city ≠ legal city.

## Independence rules
- Silver key quarantined until Step 7; opened only after `rules/all.json`, `addresses/seed20.json` and `changes/T1-T5.json` were frozen (see commit/mtime).
- After comparison the independent key is **not** edited silently; disagreements go to `adjudication_log.csv` for Hamza.
- Secondary sources never establish a rule, a date or a quote on their own (rows that rest on secondary sources say so and carry confidence ≤ 0.6).

## Dev/test split
Seed `20261003` (Python `random`), stratified by (state, category), ~70/30, with all T1–T5 rules (and NWK-ALG-00, which T2 relies on) forced into dev. Hamza does not look at `test.json` until the final scoring run.

| stratum | value | dev | test |
|---|---|---|---|
| category | algorithmic_rent_setting | 11 | 3 |
| category | application_screening_fees | 10 | 4 |
| category | just_cause_eviction | 10 | 4 |
| category | rent_increase_limits | 11 | 5 |
| category | screening_restrictions | 10 | 6 |
| category | security_deposits | 9 | 4 |
| state | CA | 25 | 12 |
| state | MA | 17 | 7 |
| state | NJ | 19 | 7 |

## Status / result vocabulary
Rule `status` (as of 2026-10-01): in_force | not_yet_effective | pending | failed | n/a (negative findings). Address `result`: applies | unknown | superseded | not_yet_effective | pending; rules that do not cover an address are listed under `not_covered` (the submission format omits them).

## How to update
Edit the builder scripts (`build_rules.py`, `build_addresses.py`, `compare_silver.py`) — not the JSON by hand — re-run, and re-validate against `schema/`. The scripts were run in a cloud workspace with `ROOT` pointing at copies of `participant-final-no-hour16 3/corpus/text`, `corpus_supplementary/text`, `sample_addresses.csv` and `corpus_manifest.csv`, and `OUT` at this `navigator/` tree; set those two constants to local paths before re-running (Python 3.10+, `jsonschema`). Bump the version line above and record the change in `adjudication_log.csv` with `decided_by`.

## Versioning
v0.1 — initial independent draft (AI-draft), frozen before the silver comparison (`FREEZE_before_step7.sha256`).
v0.2 — post-adjudication: `quote_verified` added (true = span substring-matched against a saved full text; false = null span or excerpt-only basis — 27 rows, all null-span); Q1 Berkeley 13.63 = 2026-01-01 (conflict_flag kept); Q5 Boston HSNA / Cambridge 8.71 kept as notice-only just_cause_eviction rules (conflict_flag kept); 23 citation/value disagreements adopted. 12 adjudication rows still open.
v0.3 — Hamza's L009–L097 verdicts applied (see `adjudication_log.csv`); added BOS-SCRN-02 (Fair Chance policy, city-funded scope), HOB-RENT-02 (B-750 disclosure duty), MA-FEE-02 (broker fee reform), MA-SCRN-02 (803 CMR 5.00, null span); BOS-SCRN-01 re-identified as the Fair Housing Commission rule; address key regenerated for the new rows; dev/test re-split (seed unchanged). The 94 "no change"/"keep" rows were closed in bulk ("accepted in bulk as no-change; not individually reviewed (Hamza, 2026-10-04)"); adjudication_log has 0 open rows. D075 re-checked: no Division 8 text, SD-SCRN-01 span remains null.
v0.4 — lawyer review batches 1–4 applied (63 adjudication-log rows, all decided_by Hamza unless marked AI-draft): BOS-SCRN-02, MA-SCRN-02, SA-ALG-01 (+addendum: 2026-04), BERK-FEE-01, BOS-JUST-01 (citation → ch. X § 10-11), JC-ALG-01 (official adopted ordinance; 20-day NJ effective-date basis applied to JC/HOB rows), HOB-ALG-01, HOB-RENT-02, CA-ALG-01 (official leginfo page D093: "Effective January 1, 2026."), MA-RENT-P1 (SJC-13893 slip opinion), MA-FEE-02, BERK-RENT-01 (eff. 2026-01-01), CA-SCRN-01, NJ-ALG-01 (secondary added), LA-JUST-02 (official LAMC text). AI-draft additions from the same material: LA-RENT-01/LA-DEP-01 citations + official LAMC text in notes (corpus spans kept); SD-SCRN-01 span from the re-captured official Division 8 PDF (D075). Not achieved: official malegislature.gov c.6 § 172 page (timed out; FindLaw mirror used); Santa Ana ordinance number still unseen on an official page. `quoted_span_in_corpus` is now a whitespace-normalised match. dev/test split unchanged (same seed, same ids). seed20/seed60 regenerated (expected results unchanged).
v0.4.1 — rulings_05.md §4a (Hamza): HOB-RENT-01 re-extracted from the full Hoboken ch. 155 chapter text (manual ecode360 PDF download, registered as S-MAN-15; sources/official/S-MAN-15.txt). Citation "Hoboken Code § 155-5; applicability § 155-2"; key_value "lesser of 5% or CPI change, once per 12 months"; quoted_span = full § 155-5 first sentence; exemptions § 155-2(A)–(H) spelled out; coverage records that there is NO minimum-unit-count or owner-occupancy test (unlike Jersey City/Newark). Address-key coverage test for HOB-RENT-01: built ≤ 1987-06-25 → applies; built after 1987-06-25 and < 30 years before the 2026-10-01 query date → unknown (N.J.S.A. 2A:42-84.1 exemption depends on mortgage term and compliance filings); built after 1987-06-25 and ≥ 30 years ago → applies (year_built ≤ 1995; 1996 → unknown); year missing → unknown. Building-type exemptions (hotel/commercial/institutional/government) are not testable from MOD-IV codes and are not applied. Adjudication log L194–L202 (decided_by Hamza). verifier Hamza 16; confidence 0.9. dev/test ids unchanged (row set unchanged; rows patched in place). seed20/seed60 regenerated: expected results unchanged (all 6 Hoboken addresses stay unknown — 2000/2001/2007/2010 builds are < 30 years old, the rest lack year_built); only the HOB-RENT-01 reason text changed.
v0.4.2 — MA-SCRN-02 (approved by Hamza in chat): quoted_span replaced by the look-back sentence of § 172(a)(3) (10-year felony / 5-year misdemeanour; the housing-applicant purpose is the preceding sentence) from the official malegislature.gov page, captured as D094 after the earlier TLS failures and registered as S-MA-12 (sources/official/S-MA-12.txt). quote_verified true, confidence 0.8, verifier Hamza; FindLaw mirror (S-MAN-04) kept in verified_against as secondary; the former 803 CMR 5.10 span is preserved in notes. Citation re-ordered to put § 172(a)(3) first. Log L203–L208 (L208 = trim to one sentence; confidence already 0.8 at v0.4, so no change row). No address results changed; dev/test ids unchanged. Known stale text not changed this round: the MA-SCRN-02 reason string in build_addresses.py still says "text not captured; low confidence".
v0.4.3 — (1) MA-SCRN-01 (c.151B § 4(10)) adjudicated after comparison by Hamza: § 4(10) has no owner-occupied two-family exemption (proviso is in § 4(7) and § 4(11)(3), official text D049). build_addresses.py now returns applies for every MA address; expected results changed only at A0065 (seed20+seed60), A0093, A0123, A0083 (seed60) — unknown → applies. Rule row coverage/exemptions text corrected. Log L209–L214. (2) addresses/holdout20.json: 20 addresses not in seed20/seed60 (SF 3, LA 3, every other city 2), selected mechanically by holdout_picks() in build_addresses.py (one edge case per city first where the pool is non-empty, then fillers; random.Random(20261005)). Frozen in addresses/holdout20.sha256 (with hashes of build_addresses.py and rules/all.json) before any engine scoring. Do not tune the engine against it.
