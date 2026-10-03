"""
coverage.py - Module B, step 2: turn each rule's coverage text into machine-checkable tests.

Plain-language summary
----------------------
A rule says in words who it covers ("units with a certificate of occupancy
issued before June 13, 1979", "owners of more than two units", "not housing
built within the previous 15 years"). The engine needs those as tests it can
run against an address record (year_built, units, use code). This script asks
Claude ONCE per rule to translate the words into tests, quoting the words each
test came from, and caches the result in out/coverage.json. Hamza reviews the
rent-control entries before the full run.

A test is {field, op, value, source_text, note}. Fields the engine knows:
  year_built      the assessor's year built (a number)
  coo_date        certificate-of-occupancy cutoff (ISO date) - the engine treats year_built
                  as a proxy: TRUE if year_built < cutoff year, FALSE if >, UNKNOWN if equal
  coo_age_years   rolling window: certificate of occupancy at least N years before the query date
  units           number of dwelling units
  owner_type      never in our data -> unknown (unless another test decides)
  tenancy_months  never in our data -> unknown
  building_type   from use_code / use_description ("apartments", "single_family", "condo", "duplex")
  funding         subsidised / deed-restricted -> never in our data -> unknown
  other           anything else -> unknown
ops: <, <=, >, >=, ==, !=, in, not_in.  All tests must be TRUE for the rule to apply.

Usage:  python coverage.py           (only rules not yet cached)
        python coverage.py --force   (redo all)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import anthropic
from dotenv import load_dotenv

from common import DEFAULT_QUERY_DATE, OUT

load_dotenv()
RULES_FULL = OUT / "rules_full.json"
COVERAGE_JSON = OUT / "coverage.json"
MODEL = os.environ.get("EXTRACT_MODEL", "claude-sonnet-5-5")
PRICE_IN, PRICE_OUT = 2.00, 10.00

FIELDS = ["year_built", "coo_date", "coo_age_years", "units", "owner_type", "tenancy_months",
          "building_type", "funding", "other"]
OPS = ["<", "<=", ">", ">=", "==", "!=", "in", "not_in"]

SCHEMA = {
    "type": "object",
    "properties": {
        "tests": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string", "enum": FIELDS},
                    "op": {"type": "string", "enum": OPS},
                    "value": {"type": ["number", "string", "array"], "items": {"type": "string"},
                              "description": "number, ISO date string, category string, or list of strings"},
                    "source_text": {"type": "string", "description": "the coverage/exemption words this test comes from"},
                    "note": {"type": ["string", "null"]},
                    "kind": {
                        "type": "string", "enum": ["coverage", "niche_exemption", "plausible_exemption", "timing"],
                        "description": "coverage: the law reaches the property only if this holds (missing data -> unknown). "
                                       "niche_exemption: a narrow ownership/funding/use carve-out the claimant must prove "
                                       "(missing data -> applies, with an assumption). plausible_exemption: an exception the "
                                       "data cannot rule out and that is common for the property type (missing data -> unknown; "
                                       "defeated_if can settle it). timing: when a tenant's protection starts, not whether the "
                                       "property is covered (never unknown; recorded as an assumption).",
                    },
                    "on_fail": {
                        "type": "string", "enum": ["exclude", "unknown"],
                        "description": "What a FALSE result means. 'exclude' (normal): the address is outside the rule. "
                                       "'unknown': the exemption depends on further facts not in the data (mortgage term, "
                                       "statutory filings, owner elections), so failing the proxy test leaves the answer unknown.",
                    },
                    "defeated_if": {
                        "type": ["object", "null"],
                        "description": "Only for owner_type / tenancy_months / funding exceptions the data cannot see: an "
                                       "address-level fact that makes the exception impossible, so the test counts as "
                                       "satisfied (e.g. CA small-landlord deposit exception is impossible if units > 4).",
                        "properties": {"field": {"type": "string", "enum": ["units", "year_built", "building_type"]},
                                       "op": {"type": "string", "enum": OPS},
                                       "value": {"type": ["number", "string", "array"], "items": {"type": "string"}}},
                        "required": ["field", "op", "value"],
                        "additionalProperties": False,
                    },
                },
                "required": ["field", "op", "value", "source_text", "note", "kind", "on_fail", "defeated_if"],
                "additionalProperties": False,
            },
        },
        "applies_to_all_residential": {"type": "boolean",
                                       "description": "true if the rule covers every residential rental in the jurisdiction with no building-level limits"},
        "coverage_incomplete": {"type": "boolean",
                                "description": "true when the texts say coverage/applicability is defined somewhere NOT in the corpus "
                                               "(e.g. 'applicability defined elsewhere in the chapter, not in this capture'), so the "
                                               "engine should answer unknown rather than applies"},
        "notes": {"type": ["string", "null"]},
    },
    "required": ["tests", "applies_to_all_residential", "coverage_incomplete", "notes"],
    "additionalProperties": False,
}

SYSTEM = f"""You convert the coverage conditions and exemptions of a rental-housing rule into machine-checkable tests for a rule engine. Not legal advice.

The engine knows these facts about an address: year_built (assessor's year, may be missing), units (count, may be missing), building_type from the assessor's use code (apartments, condo, single_family, duplex, mixed), state and city. It does NOT know the owner's identity, the tenancy length, subsidy status, or the certificate-of-occupancy date (year_built is used as a proxy with the cutoff year treated as unknown).

Write tests such that the rule APPLIES to an address only when ALL tests are true. Exemptions become tests that exclude the exempt case.

Tag every test with its kind (reviewer ruling, instructions/rulings_06.md):
- coverage: the law reaches the property only if the condition holds (a funding or programme requirement such as "applies to DND/IDP-funded providers"; unit-count thresholds; certificate-of-occupancy or construction cutoffs). Missing data -> unknown.
- niche_exemption: a narrow carve-out for an ownership, funding or use class that whoever claims it must prove; exemptions to remedial housing statutes are read narrowly. Missing data -> the rule applies, with the exemption recorded as an assumption. Classes: non-profit or resident-controlled cooperatives; public housing, government-owned units, units under a government contract, project-based Section 8; deed-restricted or subsidised affordable housing (including software used to set rents under affordable programmes); transient or vacation occupancy (hotels, motels, tenancies of 100 days or less for vacation purposes); hospitals, dormitories, religious and care facilities; an owner who shares kitchen or bath with the tenant when the building has 3 or more units.
- plausible_exemption: an exception the data cannot rule out and that is common for the property type. Missing data -> unknown, unless defeated_if settles it from the use code. Classes: owner-occupied two-family or owner-occupied 1-4 unit exemptions (defeated_if MUST be a unit count, e.g. units > 2; a building_type of "apartments" alone does not rule out a small owner-occupied building); AB 1482-style single-family / condo owned by a natural person (defeated_if building_type in [apartments, mixed, duplex]); new-construction windows where the year built may fall inside.
- timing: when a tenant's protection starts ("after 6 months of tenancy", "after the first 30 days"), not whether the property is covered. Never makes the rule unknown; recorded as an assumption.
A cross-reference to a definitions section ("as defined in section 98.0720") is NOT a coverage limitation and does not make coverage incomplete.

How to express common conditions
- A cutoff given with a full month/day date ("first built on or before October 1, 1978", "certificate of occupancy after June 13, 1979", "constructed after February 1, 1995") is a certificate-of-occupancy cutoff -> field coo_date, op <= (rule covers buildings up to that date), value the ISO date. A year-only statement ("built before 1995") -> field year_built.
- "exempt if built / certificate of occupancy within the previous N years" or "new construction exempt for N years" -> field coo_age_years, op >=, value N.
- Exclusions of hotels, motels, transient occupancy, hospitals, care facilities, dormitories, fraternity houses, religious facilities, shelters -> ONE test field building_type, op not_in, value a list of those categories (an apartment building passes it). Do NOT put these under other.
- Unit-count thresholds -> field units. Single-family / condo / duplex limits -> building_type.
- Owner identity, owner occupancy, tenancy length, subsidy / deed restriction -> owner_type / tenancy_months / funding (the engine will say unknown and needs the test to explain why). Where another visible fact makes the exception impossible, set defeated_if (e.g. CA small-landlord deposit exception: units > 4).
- Read direction carefully: "this includes units that obtained a certificate of occupancy after June 13, 1979" is an INCLUSION (those units ARE covered) and must not become an exclusion test. Only words like "exempt", "does not apply", "not subject", "excluded" create exclusion tests.
- Do not add a test for a sub-population that another test already excludes (e.g. units exempt under Costa-Hawkins are the new-construction, single-family and condominium units; if those are already tested, no extra tenancy test is needed).
- NEVER write a test that merely restates that the unit is "covered by / subject to the ordinance" or "a rent-controlled unit" - that is circular. Instead look in the related records below for the ordinance's actual coverage criteria and use those. If none are stated anywhere, give no test for it.
- When an exemption is CONDITIONAL on facts the data cannot show (e.g. "newly constructed dwellings exempt for the lesser of the mortgage amortisation period or 30 years, if the landlord filed the statutory notices"), write the proxy test (coo_age_years >= 30) with on_fail "unknown": a newer building is then unknown, not excluded. Ordinary exemptions use on_fail "exclude".
- Use field other only for a genuine condition none of the fields can carry. If the texts say coverage is defined somewhere not captured in the corpus, set coverage_incomplete true (the engine will answer unknown).

Related records from the same jurisdiction are provided for context. Use a statement from them ONLY when it explicitly describes who is exempt from or covered by THIS rule's category (e.g. a just-cause page saying "units exempt from rent increase limits: those with a certificate of occupancy after June 13, 1979" tells you the rent-limit rule's cutoff). Quote in source_text the exact words each test comes from. Do not invent limits that no text states. If no building-level limits are stated, return tests [] and applies_to_all_residential true. The query date is {DEFAULT_QUERY_DATE}.
Respond only with JSON."""


def rule_key(rule: dict) -> str:
    """Content key, independent of the team_rule_id (ids shift when rules merge)."""
    h = hashlib.sha1(json.dumps([rule["jurisdiction"], rule["category"], rule.get("citation"), rule.get("coverage_conditions"),
                                 rule.get("exemptions"), rule.get("requirement"), rule.get("interaction")],
                                ensure_ascii=False).encode()).hexdigest()[:12]
    return f"c:{h}"


def cite_key(rule: dict) -> str:
    return f"{rule['jurisdiction']}|{rule['category']}|{(rule.get('citation') or '').strip().lower()}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", nargs="*", help="redo only these team_rule_ids")
    ap.add_argument("--budget", type=float, default=1.50)
    ap.add_argument("--no-model", action="store_true",
                    help="never call the API: reuse cached tests by content, else carry the previous tests of the same citation")
    args = ap.parse_args()

    rules = json.loads(RULES_FULL.read_text(encoding="utf-8"))["rules"]
    old = json.loads(COVERAGE_JSON.read_text(encoding="utf-8")) if COVERAGE_JSON.exists() and not args.force else {}
    # Index the previous run by content key and by citation, so a rule that was renumbered
    # (ids shift when rules merge) still finds its tests.
    by_key = {e.get("key"): e for e in old.values()}
    by_cite = {f"{e['jurisdiction']}|{e['category']}|{(e.get('citation') or '').strip().lower()}": e
               for e in old.values() if e.get("citation")}
    by_title = {(e["jurisdiction"], e["category"], e.get("title")): e for e in old.values()}
    by_bucket: dict = {}
    for e in old.values():
        by_bucket.setdefault((e["jurisdiction"], e["category"]), []).append(e)

    def previous_entry(rule: dict):
        """The old entry for this rule, found WITHOUT using the (shifting) team_rule_id."""
        return (by_title.get((rule["jurisdiction"], rule["category"], rule["title"]))
                or by_cite.get(cite_key(rule))
                or (by_bucket.get((rule["jurisdiction"], rule["category"]), [None] * 2)[0]
                    if len(by_bucket.get((rule["jurisdiction"], rule["category"]), [])) == 1 else None))
    cache: dict = {}
    client = None if args.no_model else anthropic.Anthropic()
    spent, calls, carried = 0.0, 0, 0
    for rule in rules:
        if rule.get("negative_finding") or rule.get("derived"):
            continue  # negative findings never "apply"; no coverage tests needed
        key = rule_key(rule)
        rid = rule["team_rule_id"]
        if args.only and rid not in args.only:
            prev = previous_entry(rule)
            if prev:
                cache[rid] = {**prev, "key": prev.get("key"), "citation": rule.get("citation")}
            continue
        hit = by_key.get(key) if not args.only else None
        if hit is not None:
            cache[rid] = {**hit, "key": key, "citation": rule.get("citation")}
            continue
        if client is None:
            prev = previous_entry(rule)
            if prev:
                cache[rid] = {**prev, "key": key, "citation": rule.get("citation"),
                              "carried_over": "tests reused from the previous coverage of this citation; rule text "
                                              "changed since (no model call allowed in this run)"}
                carried += 1
            else:
                print(f"  {rid} {rule['jurisdiction']}/{rule['category']}: no cached tests and no model allowed; "
                      f"engine will treat as applies-to-all", file=sys.stderr)
            continue
        if spent >= args.budget:
            print("budget reached; stopping", file=sys.stderr)
            break
        related = [x for x in rules if x["jurisdiction"] == rule["jurisdiction"] and x is not rule
                   and not x.get("negative_finding")]
        msg = "\n".join([
            f"Rule: {rule['title']}", f"Jurisdiction: {rule['jurisdiction']} ({rule['level']})",
            f"Category: {rule['category']}", f"Requirement: {rule['requirement']}",
            f"Key value: {rule.get('key_value')}", f"Coverage conditions: {rule.get('coverage_conditions')}",
            f"Exemptions: {rule.get('exemptions')}", f"Interaction: {rule.get('interaction')}",
            f"Notes: {rule.get('notes') or ''}",
            "", "Related records in the same jurisdiction (context only):",
        ] + [f"- [{x['category']}] {x['title'][:80]} | coverage: {(x.get('coverage_conditions') or '')[:400]} "
             f"| exemptions: {(x.get('exemptions') or '')[:300]}" for x in related[:12]])
        resp = client.messages.create(
            model=MODEL, max_tokens=4000, system=SYSTEM,
            messages=[{"role": "user", "content": msg}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        )
        spent += (resp.usage.input_tokens * PRICE_IN + resp.usage.output_tokens * PRICE_OUT) / 1e6
        calls += 1
        if resp.stop_reason != "end_turn":
            print(f"  {rule['team_rule_id']}: stop_reason {resp.stop_reason}; skipped", file=sys.stderr)
            continue
        data = json.loads(next(b.text for b in resp.content if b.type == "text"))
        cache[rule["team_rule_id"]] = {"key": key, "jurisdiction": rule["jurisdiction"], "category": rule["category"],
                                      "title": rule["title"], "citation": rule.get("citation"), **data}
        print(f"  {rule['team_rule_id']} {rule['jurisdiction']}/{rule['category']}: {len(data['tests'])} test(s)")
    applied = apply_overrides(cache, rules)
    COVERAGE_JSON.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"coverage: {len(cache)} rules cached, {calls} call(s) this run, ${spent:.3f}, {carried} carried over by citation, "
          f"{applied} reviewer override(s) applied -> {COVERAGE_JSON}")
    return 0


def apply_overrides(cache: dict, rules: list[dict]) -> int:
    """
    Reviewer rulings from coverage_overrides.json, applied after the model's tests.
    Each is recorded on the entry (reviewed_by, review_ruling) so it is traceable.
    """
    path = OUT.parent / "coverage_overrides.json"
    if not path.exists():
        return 0
    n = 0
    for ov in json.loads(path.read_text(encoding="utf-8")).get("overrides", []):
        for rule in rules:
            if rule["jurisdiction"] != ov["jurisdiction"] or rule["category"] != ov["category"]:
                continue
            if ov.get("citation_contains") and ov["citation_contains"].lower() not in (rule.get("citation") or "").lower():
                continue
            entry = cache.get(rule["team_rule_id"])
            if not entry:
                continue
            if "set" in ov:
                entry.update(ov["set"])
            if "add_tests" in ov:
                have = {(t["field"], t["op"], str(t["value"])) for t in entry.get("tests", [])}
                entry["tests"] = entry.get("tests", []) + [t for t in ov["add_tests"]
                                                           if (t["field"], t["op"], str(t["value"])) not in have]
                entry["applies_to_all_residential"] = False
            if "drop_tests_where" in ov:
                cond = ov["drop_tests_where"]
                entry["tests"] = [t for t in entry.get("tests", []) if not all(t.get(k) == v for k, v in cond.items())]
            entry["reviewed_by"] = ov["reviewer"]
            entry["review_ruling"] = ov["ruling"]
            n += 1
    return n


if __name__ == "__main__":
    sys.exit(main())
