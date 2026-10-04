# Statute Street: Rental Housing Law Navigator

For any apartment address in the sample (California, New Jersey, Massachusetts; ten cities), Statute Street reports which rental housing rules apply on a given date, each cited to the source text, and tracks what changes and when. Built for the Hack-Nation 7th Global AI Hackathon, Challenge 02 (sponsor RealPage).

**Legal information, not legal advice. Check the source or ask a lawyer before acting.**

Live demo: `<LIVE_DEMO_URL>`. User interface repository: `<UI_REPO_URL>`.

## What it does

- **Module A, rule extraction.** Claude (Sonnet 5.5) reads every document in the supplied corpus plus our single-page captures and returns structured rule records in six categories (rent increase limits, just cause eviction, security deposits, application screening fees, screening restrictions, algorithmic rent setting). Every record must carry a quoted span that is an exact passage of its source document; records whose quote cannot be verified are retried once and otherwise dropped. Status is computed in code from stated effective dates, never taken from the model. Duplicates across documents are merged, with the folded sources kept as supporting documents. Where a category has no rule at a level, a negative finding says so.
- **Module B, address lookup.** Each address is resolved to its legal city with the Census Geocoder (Dorchester is Boston, Van Nuys is Los Angeles). Each rule's coverage text is turned once into machine checkable tests; a deterministic engine then decides, for each address and rule, applies, unknown, superseded, not yet effective or pending, with a one sentence explanation naming the deciding fact or the missing one.
- **Module C, change tracking.** The engine is run at the dates named by the five change tests (T1 to T5); affected address sets are plain set arithmetic. No model is involved.

## Quick start (cache-only reproduction, no model calls)

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export ANTHROPIC_API_KEY=invalid        # proves that nothing below calls the model
P=.venv/bin/python
$P verify.py --no-retry                 # verified rules from the cached extractions in out/raw/
$P date_resolve.py --no-model           # cached effective date decisions
$P derive_negatives.py                  # "no rule at this level" findings
$P translate_es.py --no-model           # cached Spanish summaries
$P coverage.py --no-model               # cached coverage tests (+ reviewer overrides)
$P engine.py                            # out/lookups.json, 500 addresses as of 2026-10-01
$P engine.py --use-derived-units        # variant that trusts NJ unit counts parsed from building codes
$P changes.py                           # out/changes.json (T1 to T5) and the score against the change key
$P changes.py --diff --before 2025-12-31 --after 2026-01-02
$P changes.py --diff --before 2026-10-01 --after 2027-07-02
$P open_questions.py && $P publish.py --in-place
```

A fresh clone run this way reproduced all fourteen output files byte for byte (out/stress/repro.md). To re-extract from scratch, add an `ANTHROPIC_API_KEY` in `.env` and run `python extract.py --all`.

## Pipeline

```
corpus/text (54 docs)  +  corpus_supplementary (33 captures)  +  sources/manual (11 pages)
        |
   extract.py  (Claude, structured output, cached per document in out/raw/)
        |
   verify.py   (exact quote check, status from dates, dedupe, evidence basis)  -> out/rules.json
        |
   date_resolve.py (stated dates elsewhere in the corpus)  ->  derive_negatives.py  ->  translate_es.py
        |
   resolve.py (Census Geocoder: legal city)      coverage.py (coverage text -> tests, reviewer overrides)
        |                                                 |
        +------------------------>  engine.py  <----------+        -> out/lookups.json
                                        |
                                   changes.py  -> out/changes.json      export_ui.py -> UI data files
```

## Results

| Measure | Result |
|---|---|
| Module A, dev split of the independent key (39 rules) | 39/39 found, status 39/39 |
| Module A, test split, single run at tag v1.0-submission-candidate | 15/15 found, status 15/15, negative findings 11/11, effective dates 9/15 agree |
| Module B, seed60 (60 addresses, 569 expectations) | 569/569 exact |
| Module B, seed20 | 190/190 exact |
| Module B, holdout20, single blind run | 192/192 exact |
| Module C, change tests T1 to T5 | 5 of 5 exact (affected and conflict sets) |
| Whole sample | 500 addresses, 5,298 rule rows, unknown rate 27.3%, 2,079 rows rest on a stated presumption, 300 rows flagged for review |

Agreement figures measure our engine against an independently built key that applies the same reviewed legal rulings; they test faithful implementation, not legal correctness beyond those rulings. The organisers' hidden key is the real test.

## Stress test

Because the hidden key's treatment of exemptions is unknown, six alternative keys were built deterministically from engine policy switches (out/stress/): strict (every presumption becomes unknown), lenient (plausible exemptions become applies), cutoff year buildings as applies, New Jersey unit counts parsed from building codes treated as real, no precedence, and not covered rows reported. Each candidate policy was scored against every key:

| Policy | Worst case exact | Mean exact | Worst case weighted | Mean weighted |
|---|---|---|---|---|
| current | 83.0 | 93.3 | 81.0 | 93.3 |
| strict | 73.3 | 86.0 | 70.6 | 84.5 |
| lenient | 73.3 | 84.2 | 82.2 | 89.4 |

The current policy was kept: it has the best worst case and the best mean exact agreement across the six keys, so it loses least whatever the hidden key assumes. Forty nine perturbation tests (cutoff years, missing or malformed facts, mailing versus legal city, effective date boundaries, pending and failed instruments) pass; the submission files pass the schema and format check. Full report: out/stress/REPORT.md.

## Exemptions and presumptions (how "unknown" is decided)

Every condition the engine tests is one of these kinds:

- **Coverage condition.** The law reaches the property only if the condition holds (a unit count threshold, a funding requirement, a certificate of occupancy cutoff). If the data cannot show it, the answer is unknown. Year built is only a proxy for the certificate date, so a building from the cutoff year itself is unknown.
- **Owner identity test.** A natural person or small landlord exception, the AB 1482 natural person single family or condo exception, an owner occupied two to four unit exemption where the unit count is within the threshold or unknown. The organisers' README section 4 says owner names are excluded and such exceptions must be answered unknown unless we can explain why they cannot apply; so the answer is unknown ("owner identity is not in the data") unless the use code makes the exception impossible, when it applies with that reason.
- **Carve-out inside the owner's own dwelling.** An owner sharing kitchen or bath, a roommate in the owner's unit, a room let in an owner occupied home: these remove at most the owner's own unit, so a building shown as two or more units or apartments is still covered (applies, carve-out listed in `assumptions`); only a single family or unknown building type stays unknown.
- **Use, funding or tenure.** Hotels and vacation lets, dormitories, hospitals, care facilities, public housing and government contract units, deed restricted or subsidised housing, resident owned cooperatives, government owned units. Exemptions to remedial housing statutes are read narrowly, so when the data is silent the answer is applies, the explanation starts "Applies unless", and the exemption is listed in `assumptions`. `engine.py --strict-unknown` turns these to unknown.
- **Timing condition.** Protection that starts after six months of tenancy is about the tenancy, not the property; never unknown, recorded as an assumption.

Precedence is decided before coverage: a state rule that yields to stricter local law is superseded wherever a local rule in the same category applies, including where two local rules split a cutoff between them (Los Angeles RSO on or before 1 October 1978, JCO after it) and where the local rule turns on the very same unresolved condition.

## Evidence basis

Organiser ruling (Discord, 4 October 2026): self saved link-only texts may be used for research but do not count toward the citation metric, which is based on the supplied corpus text. Every rule carries `evidence_basis`: 47 rules cite a supplied corpus document as primary evidence, 12 rest on our single page capture of a link-only source, 5 on a hand saved page. Wherever a supplied document supports a rule it is the primary evidence (URL, citation and verified quote); our captures are supporting documents in `rules_full.json` and the audit trail (out/evidence_log.csv, out/evidence_report.md). Rules with no supplied corpus text are kept, the law being real and verified, with the official manifest URL as `source_url`.

## Known open questions (organisers' brief section 9)

out/open_questions.json lists each with both sources and dates. Berkeley's algorithmic ban: 1 March 2026 in the ordinance text versus January 2026 in an August 2026 law firm alert; we record the stated date we have and flag the conflict. New Jersey's FAIR Act may pre-empt the Jersey City and Hoboken ordinances from 1 July 2027; flagged on every affected row for human review, not decided. Los Angeles RSO formula: 2 February 2026 (housing department) versus 24 January 2026 (landlord association); we use the agency date and flag the other. California's screening fee cap: the statute gives $30 adjusted by CPI and no single 2026 figure; we keep the formula.

## Determinations as data

out/lookups.json is a static API: for each address id, the list of rules with result, explanation, assumptions and conflict flag, as of a date. A pricing or revenue management engine can read it before suggesting a price (is a rent cap in force here, is rent setting software banned here, is the answer unknown and why), and changes.json tells it which addresses a pending or future change will touch. The Spanish `requirement_es` on every rule supports tenant facing notices.

## Where it fits in a property operating system

Statute Street is the legal layer for a property operating system: dated, evidence-backed determinations for every address, so pricing, leasing and screening act within local, state and federal law.

1. **Pricing gate.** Before a rent recommendation is issued for a unit, the pricing engine queries the determination for that address and date in the categories algorithmic_rent_setting and rent_increase_limits: permitted, permitted with conditions, restricted, or unknown with the missing fact. The operator keeps the final say; the determination carries the rule, the quote and the as-of date.
2. **Property record.** Determinations are stored against the unit in the system of record with their as-of date, citation and quoted text, and refreshed when the change register posts a new effective date.
3. **Lease administration.** A reliance record is generated at each lease event (increase notice, renewal, termination) and kept with the lease, so an audit shows what was known on the day.

Distribution: certified integration marketplaces of property management platforms (for example RealPage Exchange), where partner apps connect through standardised APIs.

### Pricing gate example

The rows an integrator would read from out/lookups.json for A0002 (1031-1035 Clinton St, legal city Hoboken, NJ) in the category algorithmic_rent_setting, on the default date and on the day after the FAIR Act takes effect:

```
address_id: A0002   legal_city: Hoboken, NJ   as_of: 2026-10-01
  r-0023  Algorithmic rent fixing in rental housing market prohibited (Hoboken Code ch. 158)
          result: applies            conflict_flag: true
          explanation: Applies unless the property is a medical, long-term care or detention facility.
                       Possible preemption: from 1 July 2027 the NJ FAIR Act may preempt the Hoboken and
                       Jersey City algorithmic rent ordinances. Flagged for human review; not decided here.
  r-0044  Forbidding the Algorithmic Inflation of Rent (FAIR) Act (P.L. 2026, c. 43)
          result: not_yet_effective  conflict_flag: true
          explanation: Not yet in force: takes effect 1 Jul 2027. Possible preemption: ... (same note)

address_id: A0002   legal_city: Hoboken, NJ   as_of: 2027-07-02
  r-0023  result: applies            conflict_flag: true   (as above)
  r-0044  result: applies            conflict_flag: true
          explanation: Applies unless the property is an inpatient medical, licensed long-term care or
                       detention facility or housing under a government-administered affordability programme.
                       Possible preemption: ... (same note)
```

A gate over those rows, in pseudo-code:

```
def gate(rows):                                   # rows: one category for one address and date
    if any(r.result == "applies" and r.prohibits for r in rows):   return "restricted", binding_rules(rows)
    if any(r.result == "not_yet_effective" for r in rows):         return "permitted now, restricted from " + earliest_effective_date(rows)
    if any(r.result == "unknown" for r in rows):                   return "review", missing_fact(rows)
    needs_review = any(r.conflict_flag for r in rows)              # carried on every verdict above as well
    return "permitted", needs_review
```

Today this is a static file (out/lookups.json, regenerated by engine.py); in production it would be an API answering the same query for any address and date.

## Agent guardrail (MCP)

`mcp_server.py` exposes the determinations to any AI agent through the Model Context Protocol (stdio transport, official `mcp` Python SDK). The agent never decides the law: the deterministic engine does, and the agent quotes it. The server makes no network or model calls and writes nothing. Every answer carries the as-of date, citation, quoted span and source URL, and ends with: "Legal information, not legal advice. Determinations are computed by the Statute Street engine; quote them, do not reinterpret them." The server instructions tell the agent to call `check_action` before any rent, fee, screening or termination step, never to state a rule without its citation, and to stop and ask a human when a verdict is unknown or needs human review.

Five read-only tools:

| Tool | Answers |
|---|---|
| `find_address(query)` | up to 5 portfolio matches by id, street, postal or legal city, state or ZIP |
| `get_determinations(address_id, as_of, category)` | every rule row for the address on that date (the cached file for 2026-10-01, the engine in-process for any other date) with result, explanation, assumptions, conflict_flag, key_value_short, citation, quoted_span, source_url, retrieved_at |
| `check_action(address_id, action, as_of)` | action in raise_rent, use_pricing_software, screen_applicant, charge_fee, take_deposit, end_tenancy (the UI's Action check mapping); verdict restricted, permitted_now_restricted_from:<date>, unknown_needs:<fact>, no_rule_found or needs_human_review, with the binding rows, the "no restriction" rules and pending or failed measures |
| `upcoming_changes(address_id, after)` | the change register rows (T1 to T5) and rules not yet in force that touch the address |
| `reliance_record(address_id, action, as_of)` | markdown: Relied on / Not applicable on this date / Unresolved / Checked and found no restriction, with engine commit and rules version |

Add it to an MCP client (Claude Code shown; any client that speaks stdio works the same way):

```
claude mcp add statute-street -- <repo>/.venv/bin/python <repo>/mcp_server.py
```

or, in a client's JSON config:

```
{ "mcpServers": { "statute-street": { "command": "<repo>/.venv/bin/python", "args": ["<repo>/mcp_server.py"] } } }
```

Example, answered through the tools (full transcript of three questions in docs/agent_demo.md):

```
User:   Can we run our pricing software at 1031 Clinton St, Hoboken, and does that change next year?
Agent:  find_address("1031 Clinton St Hoboken")            -> A0002, legal city Hoboken, NJ
        check_action("A0002", "use_pricing_software", "2026-10-01")
          verdict: restricted   needs_human_review: true
          binding: r-0023 Algorithmic rent fixing in rental housing market prohibited (Hoboken Code § 158-2)
          future:  r-0044 Forbidding the Algorithmic Inflation of Rent (FAIR) Act from 2027-07-01
        check_action("A0002", "use_pricing_software", "2027-07-02")
          verdict: restricted   binding: r-0023 (Hoboken Code § 158-2) and r-0044 FAIR Act (P.L. 2026, c. 43)
Agent:  Restricted today under Hoboken Code § 158-2 (quoted). From 1 July 2027 the New Jersey FAIR Act applies as
        well; whether it preempts the Hoboken ordinance is flagged for human review and not decided here, so I am
        stopping and asking a human before you rely on either answer. Legal information, not legal advice.
```

Tests: `tests/test_mcp_tools.py` calls each tool on A0016 (San Francisco), A0002 (Hoboken, both dates) and A0010 (Cambridge), and once over stdio with the MCP client.

## Limits

- No amounts are computed and no case is decided: the engine lists the rules that bind an action and the facts that decide coverage.
- No owner data: owner identity tests are unknown unless the use code settles them.
- New Jersey unit counts are absent from the supplied data; counts parsed from MOD-IV building codes are shown as derived and not asserted (lookups_derived.json is the variant that trusts them).
- Year built stands in for the certificate of occupancy date; cutoff year buildings are unknown.
- Coverage tests are written by the model from the rule text and reviewed for the rent control rules; other rules rely on the model's reading.
- Link-only sources that could not be captured (Newark chapter 2:10 text) are not in the corpus.

## Audit trail

- out/extract_log.csv (every model call: document, tokens, cost), out/verify_log.csv (quote checks), out/dedupe_log.csv (merges with reasons), out/out_of_scope_log.csv, out/date_resolve_log.csv, out/evidence_log.csv, out/coverage.json (tests with the words they came from), coverage_overrides.json and dedupe_overrides.json (reviewer rulings, each naming its instruction).
- The independent gold key v0.4 (gold/, sources/official/, D088 to D095) was written by a separate session and was swept into commit 84c4030 with Module B code; v0.4.1 is 772335e, v0.4.2 027c7d4, v0.4.3 inside 4dc4165. History was not rewritten.
- gold/addresses/holdout20.json (sha256 verified) was scored once, at commit b93d42f; gold/rules/test.json was read once, at tag v1.0-submission-candidate (ce42a46; a report path fix to eval.py, f604e30, was needed to write the report; the first invocation produced no score). Nothing was changed in response to either result. The three keys were re-scored after later dedupe folds as regression checks only.
- D094 (M.G.L. c. 6 s. 172, official) is the primary source for the Massachusetts CORI rule, with a FindLaw copy folded under it.

## Responsible use

Every answer carries an as-of date, a citation and the quoted text; unknown names the missing fact instead of guessing; conflicts are flagged for human review and never resolved by the system; enacted law is separated from pending bills and failed measures; only public data is used, no customer, resident or pricing data; the tool suggests no way around a rule. Internal review notes are removed from the public copies in out/public/.

## Repository map

| Path | Contents |
|---|---|
| extract.py, verify.py, date_resolve.py, derive_negatives.py, translate_es.py, eval.py | Module A |
| resolve.py, coverage.py, engine.py, lookup_eval.py | Module B |
| changes.py, open_questions.py | Module C |
| stress.py, tests/ | stress test, 74 tests |
| publish.py, export_ui.py | public copies and UI data export |
| out/ | all outputs and logs; out/public/ public copies; out/stress/ stress test |
| submission/ | the three submission files, method note, SHA256SUMS |
| mcp_server.py, docs/agent_demo.md | MCP server for agents (five read-only tools) and the three-question demo transcript |
| gold/ | the independent key built in a separate session (not used by the pipeline) |
| instructions/ | the lawyer's rulings the code implements |
| corpus_supplementary/, sources/manual/ | our single page captures and hand saved pages, with retrieval dates |

## Credits

Hamza Aslam (commercial and IP lawyer): product, legal rulings and review. Pipeline built with Claude Code. Corpus and sample data supplied by the organisers.
