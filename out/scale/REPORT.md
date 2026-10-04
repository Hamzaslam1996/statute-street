# Scale report: real addresses, throughput, cost of adding law

Produced by scale/fetch.py, scale/run.py, scale/cost.py and scale/derived_units_proxy.py. No Claude API calls. The engine, rules and coverage tests are the submitted ones, unchanged; nothing in out/*.json, submission/ or the UI repository was touched.

## 1. Real addresses from official open data

| City | Dataset | Endpoint | Filter | Rows | Retrieved | sha256 (scale/data) | Licence |
|---|---|---|---|---|---|---|---|
| San Francisco | Assessor Historical Secured Property Tax Rolls | https://data.sf.gov/resource/wv5m-vpq2.json | closed_roll_year='2025' AND number_of_units>=2 AND use_code='MRES' | 1972 | 2026-10-04T04:36Z | 9a1d3679ec16f2d4… | Open Data Commons Public Domain Dedication and License (http://opendatacommons.org/licenses/pddl/1.0/) |
| Boston | Property Assessment FY2026 (resource ee73430d-96c0-423e-ad21-c4cfb54c8961) | https://data.boston.gov/api/3/action/datastore_search_sql | LU in (R2, R3, R4, A), BLDG_SEQ = 1 | 1993 | 2026-10-04T04:36Z | 1a7ec9e7949784b9… | Open Data Commons Public Domain Dedication and License (PDDL) (http://www.opendefinition.org/licenses/odc-pddl) |
| Cambridge | Cambridge Property Database FY2026 | https://data.cambridgema.gov/resource/waa7-ibdu.json | propertyclass in('TWO-FAM-RES','THREE-FM-RES','4-8-UNIT-APT','>8-UNIT-APT','MULT-RES-2FAM','MULT-RES-3FAM','MULTIUSE-RES','AFFORDABLE APT','CONDO-BLDG','MULT-RES-4-8-APT','MULT-RES->8 APT') AND bldgnum='1' | 2000 | 2026-10-04T04:37Z | 9ab46111bb337a0e… | No licence field on the dataset page (metadata license empty); attribution: Cambridge Assessing Dept (https://www.cambridgema.gov/assess). Flagged for Hamza to confirm reuse terms. |

Privacy: owner names, mailing addresses and every other person field were excluded from the API selection and never written to disk (see `owner_fields_in_source` in scale/data/provenance.json). Kept: address, ZIP, year built, units, use description, record id and record URL.

## 2. Same pipeline, unchanged

### San Francisco

- Addresses: 1972; year built present 1966, units present 1972
- Legal city match rate (geocoded incorporated place = portal city): 100.0%; geocode method {'census': 1941, 'fallback': 31}; legal cities seen {'San Francisco': 1972}
- Determinations: 47268 over two dates; engine time 0.6s (6562.2 address evaluations per second); geocoding 385.2s
- Result distribution 2026-10-01: {'applies': 15140, 'superseded': 3908, 'unknown': 2601, 'applies unless': 1985}
- Result distribution 2027-07-02: {'applies': 15140, 'superseded': 3908, 'unknown': 2600, 'applies unless': 1986}
- Top missing facts: [['affordable housing status', 3944], ['the exemption details', 1200], ['owner identity', 32], ['year built', 25]]
- Sanity checks:
  - sf_pre_1979_multiunit_rent_control_applies: PASS ({'checked': 1936, 'violations': 0, 'sample': [], 'rule': 'r-0059'})
  - sf_cutoff_year_1979_unknown: PASS ({'checked': 0, 'violations': 0, 'sample': [], 'synthetic_1979_row': 'unknown'})
  - every_row_cites_existing_rule: PASS ({'violations': []})

### Boston

- Addresses: 1993; year built present 1987, units present 0
- Legal city match rate (geocoded incorporated place = portal city): 100.0%; geocode method {'census': 1986, 'fallback': 7}; legal cities seen {'Boston': 1993}
- Determinations: 39860 over two dates; engine time 1.05s (3791.7 address evaluations per second); geocoding 7597.0s
- Result distribution 2026-10-01: {'applies unless': 5391, 'unknown': 1993, 'applies': 8560, 'pending': 3986}
- Result distribution 2027-07-02: {'applies unless': 5391, 'unknown': 1993, 'applies': 8560, 'pending': 3986}
- Top missing facts: [['affordable housing status', 3986]]
- Sanity checks:
  - no_rent_cap_in_ma_city: PASS ({'violations': 0, 'sample': []})
  - every_row_cites_existing_rule: PASS ({'violations': []})

### Cambridge

- Addresses: 2000; year built present 1406, units present 2000
- Legal city match rate (geocoded incorporated place = portal city): 99.9%; geocode method {'census': 1973, 'fallback': 27}; legal cities seen {'Cambridge': 1998, 'Somerville': 2}
- Determinations: 39988 over two dates; engine time 0.77s (5198.2 address evaluations per second); geocoding 14796.6s
- Result distribution 2026-10-01: {'pending': 5998, 'applies': 9827, 'unknown': 1192, 'applies unless': 2977}
- Result distribution 2027-07-02: {'pending': 5998, 'applies': 9827, 'unknown': 1192, 'applies unless': 2977}
- Top missing facts: [['owner identity', 2384]]
- Sanity checks:
  - no_rent_cap_in_ma_city: PASS ({'violations': 0, 'sample': []})
  - every_row_cites_existing_rule: PASS ({'violations': []})

Geocoding, not the engine, was the slow step: the free Census batch geocoder plus one incorporated-place lookup per point took 6.4 minutes for San Francisco, 2.1 hours for Boston and 4.1 hours for Cambridge (server-side queueing on 4 Oct 2026). In production the legal city would come from a cached or commercial geocoder, or from the property record itself.

San Francisco's sanity check on the 1979 cutoff year had no 1979 parcel among the downloaded rows, so it was run on a synthetic 1979 row (result: unknown, as required).

Two wording follow-ups noticed while reading these rows (results are right, the sentence is not; nothing changed, flagged for Hamza): (a) a cutoff-year building (built 1978 in Los Angeles, 10 rows in the sample) reads 'Unknown: needs year built' although the year is known; it should read 'built 1978, the cutoff year; year built is not the certificate date'. (b) A small building under an owner-occupied exemption with on_fail unknown (SF r-0018 with 2 units, 600 rows here; r-0025 and r-0049 in the sample) reads 'needs the exemption details ... whether the exemption has ended', which is the wording for expiring new-construction exemptions, not owner-occupancy.

## 3. Throughput benchmark

| Target determinations | Address evaluations | Seconds | Addresses per second | Determinations per second |
|---|---|---|---|---|
| 10,000 | 835 | 0.12 | 7,014.2 | 84,018.8 |
| 100,000 | 9,218 | 1.77 | 5,206.1 | 56,478.7 |

Measured on this laptop, single process, pure Python; the engine is a deterministic join of address facts and rules, so it needs no model call per address.

## 4. Cost of adding law

- Documents extracted: 104 (150 calls, 196 raw records, 64 kept rules)
- Extraction model cost: $5.93 total, $0.057 per document, 16.3s wall time per document
- Spanish summaries: $0.15; model-confirmed date decisions: 3; coverage test calls: 57 (one per rule)
- Model cost per kept rule (extraction plus Spanish): $0.095
- Human review: 58 numbered rulings in instructions/; reviewer overrides {'dedupe_folds': 4, 'coverage_overrides': 4, 'rule_flag_or_note_overrides': 7, 'public_note_rewrites': 4}; 18 of 64 kept rules carry a reviewer override (28%); gold key adjudications by the lawyer: 212 (118 individually decided)
- Date resolution and coverage calls were made once each and are not itemised with a cost column in the logs; the session's total API spend including them was about $9.75 (extract.py session_spend()).

**Adding one jurisdiction of about 8 documents costs about $0.46 of model time (about 2 minutes of extraction wall time) plus about 2 lawyer review items (28% of kept rules needed a reviewer override; one in roughly 4 rules).**

## 5. Architecture in three sentences

Rules are compiled once per jurisdiction: a document is read by the model once, verified against its own text, and turned into coverage tests that are cached. Determinations are a deterministic join of address facts and rules, so more addresses cost no model calls; the engine above handled real city rolls at thousands of addresses per second. Refresh is event driven, when the change register posts a new effective date, not per query.

## 6. Unit counts as a PMS proxy (the 500 sample addresses)

Before = out/lookups.json (unit counts only where the county supplied them). After = out/lookups_derived.json (New Jersey unit counts parsed from the MOD-IV building code, standing in for counts a property management system would supply). Results for CA and MA rows cannot change because their counts were already present.

| Legal city | Addresses | Rows | Unknown before | Unknown after | Presumption rows before | Presumption rows after |
|---|---|---|---|---|---|---|
| Berkeley, CA | 40 | 560 | 80 (14.3%) | 80 (14.3%) | 320 | 320 |
| Boston, MA | 60 | 600 | 60 (10.0%) | 60 (10.0%) | 0 | 0 |
| Cambridge, MA | 50 | 500 | 0 (0.0%) | 0 (0.0%) | 0 | 0 |
| Hoboken, NJ | 40 | 400 | 280 (70.0%) | 90 (22.5%) | 240 | 240 |
| Jersey City, NJ | 50 | 450 | 350 (77.8%) | 50 (11.1%) | 250 | 250 |
| Los Angeles, CA | 80 | 885 | 91 (10.3%) | 91 (10.3%) | 485 | 485 |
| Newark, NJ | 50 | 450 | 398 (88.4%) | 367 (81.6%) | 294 | 294 |
| San Diego, CA | 50 | 500 | 100 (20.0%) | 100 (20.0%) | 250 | 250 |
| San Francisco, CA | 80 | 953 | 85 (8.9%) | 85 (8.9%) | 240 | 240 |
| **All** | 500 | 5298 | 1444 (27.3%) | 923 (17.4%) | 2079 | 2079 |

Reading: a supplied unit count settles the unit-threshold tests (Jersey City rent control's 1 to 4 unit exemption, the small-building carve-outs in the state screening and deposit laws) in Hoboken and Jersey City; what remains unknown there is owner identity (never in the data) and, in Hoboken, the year built for the 1987 rent control cutoff. Newark moves least: many of its MOD-IV codes carry no unit count, only 2 of 50 rows have a year built, and owner identity decides the remaining exemptions. Presumption counts do not move: they come from use or funding exemptions (hotels, subsidised housing) that a unit count cannot settle.

