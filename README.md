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
`capture_log.csv`) and `sources/manual/` (pages saved by hand from a browser,
same header format; the extractor reads them as `M_<file name>`).

## Module B — address lookup

```
python resolve.py                  # Census Geocoder: legal city for each address -> out/jurisdictions.json
python coverage.py                 # one Claude call per rule: coverage text -> machine tests -> out/coverage.json
python engine.py [--as-of DATE]    # deterministic rule engine -> out/lookups.json, out/lookup_audit.csv
python -m pytest tests/ -q         # acceptance tests (SF 1979 trap, Dorchester = Boston, FAIR Act dates, ...)
python lookup_eval.py --gold gold/addresses/seed60.json   # score -> out/lookup_eval.md
```

`coverage_overrides.json` records the reviewer's (Hamza's) rulings that sit on
top of the model-written tests, each naming the ruling it implements.

### Exemptions and presumptions (how "unknown" is decided)

Every condition the engine tests is one of three kinds:

- **Coverage condition** — the law reaches the property only if the condition
  holds (a unit-count threshold, a funding requirement, a certificate-of-occupancy
  cutoff). If the data cannot show it, the answer is **unknown**. Year built is
  only a proxy for the certificate date, so a building from the cutoff year
  itself is unknown.
- **Niche exemption** — a narrow carve-out that whoever claims it must prove.
  Two classes:
  - *Owner type* (who the owner is or how they occupy the building: non-profit
    or resident-controlled co-operatives, government-owned units, natural-person
    owners, small-landlord exceptions, an owner sharing kitchen or bath). The
    organisers' README §4 states that owner names are excluded from the data and
    that owner-type exceptions must be answered "unknown" unless we can explain
    why the exception cannot apply. So the answer is **unknown**, naming the
    missing fact, unless the use code makes the exception impossible (a 5+ unit
    building cannot be an owner-occupied 1–4 unit property), in which case it
    **applies** with that reason.
  - *Use or funding* (hotels and vacation lets, dormitories, hospitals, care
    facilities, public housing and government-contract units, deed-restricted
    or subsidised housing, software used under affordable programmes). Exemptions
    to remedial housing statutes are read narrowly, so when the data is silent the
    answer is **applies**, the explanation starts "Applies unless …", and the
    exemption is listed in the row's `assumptions`. `engine.py --strict-unknown`
    turns these to unknown as well, pending the organisers' answer on funding cases.
- **Plausible exemption** — an exception the data cannot rule out and that is
  common for the property type (an owner-occupied two-family; a single-family
  home or condo owned by a natural person; a new-construction window the year
  built falls inside). The answer is **unknown**, unless the assessor's use code
  makes the exemption impossible (a 5+ unit apartment building cannot be an
  owner-occupied two-family), in which case it **applies**.

Conditions about the tenancy itself (protection starts after six months of
occupancy) are not about the property and never make a rule unknown; they are
recorded as assumptions.

Precedence is decided before coverage: a state rule that yields to stricter
local law (Civ. Code §§ 1946.2(i), 1947.12(d)(3)) is **superseded** wherever a
local rule in the same category applies, including where two local rules split
a cutoff between them (LA RSO on/before 1 Oct 1978, LA JCO after it) and where
the local rule turns on the very same unresolved condition (San Diego's TPO and
the state just-cause rule share the 15-year new-construction test). It falls
back to its own tests only when the local rule is genuinely unknown.

`--use-derived-units` treats unit counts parsed from New Jersey MOD-IV building
codes ("3S-B-A-13U-H" → 13) as real; the submission does not, because the
organisers state that those rows have no unit counts (see `out/derived_units.csv`).

### A note on M.G.L. c. 151B § 4(10)

Our engine reports the Massachusetts ban on discriminating against recipients of
public or rental assistance (c. 151B § 4(10)) as applying to every Massachusetts
rental. In the official text (D049) the owner-occupied two-family exemption is
written into § 4(7) and § 4(11)(3) only; § 4(10) contains no such exemption, so
no exemption test is applied to it.

### Reviewer folds (rulings_07)

`dedupe_overrides.json` records three deterministic folds ruled by the reviewer
after the automatic dedupe: the Hoboken press release announcing the proposal
that became ch. 158 (no longer pending), the news report of Jersey City Ord.
25-057, and the Santa Ana newsletter describing Ord. NS-3090. Each folded source
stays on the kept rule as a supporting document and the fold is logged with its
reason in `out/dedupe_log.csv`. Coverage tests and resolved effective dates are
cached by content and citation (`out/coverage.json`, `out/date_resolve_cache.json`)
so a rebuild after such folds needs no model calls.

## Module C — change tracking

```
python changes.py                                          # -> out/changes.json (T1-T5), changes_detail.json, changes_eval.md
python changes.py --diff --before 2025-12-31 --after 2026-01-02   # -> out/diff_2025-12-31_2026-01-02.json (T1)
python changes.py --diff --before 2026-10-01 --after 2027-07-02   # -> out/diff_2026-10-01_2027-07-02.json (T3)
python open_questions.py                                   # -> out/open_questions.json
python -m pytest tests/ -q
```

Module C is deterministic: the rule engine is run at the dates each test names
and the affected sets are plain set arithmetic over the 500 addresses. No model
calls. "Affected" means the addresses whose answer the change touches (the
test's rule is reported for the address on at least one of the dates). T3 also
sets conflict flags on every Jersey City and Hoboken row, because the FAIR Act's
§ 6(b) may pre-empt the local bans; we flag that for human review, we do not
decide it. T5's set is empty by construction: a struck ballot question is a
failed measure and failed measures are never reported for an address.

### Known open questions (organisers' brief §9)

`out/open_questions.json` lists each with both sources and dates:

1. Berkeley ch. 13.63 algorithmic ban: 1 March 2026 (ordinance text) vs January 2026
   (law-firm alert, Aug 2026). We record the stated date we have and flag the conflict.
2. NJ FAIR Act vs the Jersey City and Hoboken ordinances: possible preemption from
   2027-07-01, flagged on every affected row.
3. LA RSO new formula: 2026-02-02 (LAHD) vs 2026-01-24 (landlord association). We use the
   agency date and flag the other.
4. CA screening-fee cap: the statute gives $30 adjusted by CPI and no 2026 dollar figure;
   we keep the formula.

## Scores and what they mean

| Key | Addresses | Exact result agreement |
|---|---|---|
| `gold/addresses/seed60.json` | 60 | 569/569 |
| `gold/addresses/seed20.json` | 20 | 190/190 |
| `gold/addresses/holdout20.json` (blind, see below) | 20 | 192/192 |
| `gold/changes/T1-T5.json` | 500 | all five tests exact |

Agreement figures measure our engine against an independently built key that
applies the same reviewed legal rulings; they test faithful implementation, not
legal correctness beyond those rulings. The organisers' hidden key is the real
test. Across the whole sample (500 addresses, 5,298 rule rows) the unknown rate
is 27.3% and 2,081 rows rest on a presumption ("Applies unless …").

After the duplicate-rule fold of rulings_08 the three keys were re-scored as a
regression check (nothing moved); that was a check that the dedupe changed no
answer, not tuning against the holdout.

`out/public/` holds copies of `rules.json`, `lookups.json` and `changes.json` with
internal review notes removed (`publish.py`); the same filter is applied to the
submission files themselves.

## Blind holdout (single run)

`gold/addresses/holdout20.json` (20 addresses, frozen 2026-10-04 04:30 PKT, sha256 verified
against `holdout20.sha256`) was scored exactly once, at code state `b93d42f`, after Module C was
complete: exact result agreement 192/192 = 100.0%, weighted 300/300 = 100.0%. No code, coverage or rule
change was made in response to the holdout result; the full report is `out/lookup_eval_holdout20.md`.

## Audit trail notes

- The independent gold key v0.4 (`gold/`, `sources/official/`, D088–D095) was
  written by a separate session and was swept into commit `84c4030` together with
  Module B code; v0.4.1 is commit `772335e` on its own. History was not rewritten.
- `corpus_supplementary/text/D094.txt` (official malegislature.gov text of M.G.L. c. 6 § 172,
  retrieved 2026-10-03) arrived after the first v0.4 commit; it is the primary source for the
  MA CORI screening rule, with the FindLaw copy (`sources/manual/MA-SCRN-02_MGL_c6_s172_findlaw.txt`)
  folded under it as a supporting document.
