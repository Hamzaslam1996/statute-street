"""
Module B acceptance tests (instructions/module_b.md step 5). Run: python -m pytest tests/ -q
They use the real out/rules_full.json and out/coverage.json with synthetic addresses.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import engine  # noqa: E402

RULES = json.loads((ROOT / "out" / "rules_full.json").read_text(encoding="utf-8"))["rules"]
COVERAGE = json.loads((ROOT / "out" / "coverage.json").read_text(encoding="utf-8"))
BY_ID = {r["team_rule_id"]: r for r in RULES}


def facts(state, city, year_built=None, units=None, btype="apartments"):
    return {"address_id": "T", "state": state, "city": city, "year_built": year_built, "units": units,
            "building_type": btype, "use_description": "test"}


def run(f, as_of="2026-10-01"):
    res = engine.evaluate_address(f, RULES, COVERAGE, date.fromisoformat(as_of))
    return {r["team_rule_id"]: r for r in res}


def find(jurisdiction, category, **match):
    """The rule ids in a jurisdiction + category, optionally filtered by a substring of the citation."""
    out = []
    for r in RULES:
        if r["jurisdiction"] == jurisdiction and r["category"] == category and not r.get("negative_finding"):
            if all(v.lower() in (r.get(k) or "").lower() for k, v in match.items()):
                out.append(r["team_rule_id"])
    return out


def test_sf_1979_is_unknown():
    sf_rent = find("San Francisco, CA", "rent_increase_limits")
    assert sf_rent, "no SF rent rule extracted"
    res = run(facts("CA", "San Francisco", year_built=1979, units=20))
    assert any(res[r]["result"] == "unknown" for r in sf_rent if r in res), \
        [(r, res.get(r, {}).get("result"), res.get(r, {}).get("explanation")) for r in sf_rent]


def test_sf_1962_applies_and_state_cap_superseded():
    sf_rent = find("San Francisco, CA", "rent_increase_limits")
    ca_cap = find("CA", "rent_increase_limits", citation="1947.12")
    assert ca_cap
    res = run(facts("CA", "San Francisco", year_built=1962, units=20))
    assert any(res[r]["result"] == "applies" for r in sf_rent if r in res), \
        [(r, res.get(r, {})) for r in sf_rent]
    assert res[ca_cap[0]]["result"] == "superseded", res[ca_cap[0]]


def test_dorchester_is_boston_with_no_rent_cap():
    juris = json.loads((ROOT / "out" / "jurisdictions.json").read_text())
    dorchester = [a for a, j in juris.items() if j["postal_city"] == "Dorchester"]
    assert dorchester and all(juris[a]["city"] == "Boston" for a in dorchester)
    res = run(facts("MA", "Boston", year_built=1920, units=6))
    rent = [r for r in res.values() if BY_ID[r["team_rule_id"]]["category"] == "rent_increase_limits"
            and r["result"] == "applies"]
    assert rent == [], rent


def test_newark_has_no_hoboken_or_jersey_city_ban():
    res = run(facts("NJ", "Newark", year_built=1950, units=10))
    for rid in res:
        assert BY_ID[rid]["jurisdiction"] in ("NJ", "Newark, NJ"), BY_ID[rid]["jurisdiction"]


def test_fair_act_dates():
    fair = find("NJ", "algorithmic_rent_setting")
    assert fair
    assert run(facts("NJ", "Newark", 1950, 10), "2026-10-01")[fair[0]]["result"] == "not_yet_effective"
    assert run(facts("NJ", "Newark", 1950, 10), "2027-07-02")[fair[0]]["result"] == "applies"


def test_ab325_dates():
    ab = find("CA", "algorithmic_rent_setting")
    assert ab
    assert run(facts("CA", "San Diego", 1990, 10), "2025-12-31")[ab[0]]["result"] == "not_yet_effective"
    assert run(facts("CA", "San Diego", 1990, 10), "2026-01-02")[ab[0]]["result"] == "applies"


RULE = {"team_rule_id": "x", "jurisdiction": "Test, CA", "level": "city", "category": "security_deposits",
        "status": "in_force", "effective_date": None, "interaction": None, "title": "t", "citation": "c"}
AS_OF = date(2026, 10, 1)


def test_niche_exemption_applies_with_assumption():
    cov = {"tests": [{"field": "owner_type", "op": "!=", "value": "nonprofit_cooperative", "kind": "niche_exemption",
                      "source_text": "nonprofit cooperatives", "on_fail": "exclude", "defeated_if": None}]}
    res, why, assumptions, _ = engine.evaluate_coverage(RULE, cov, facts("CA", "Test", 1950, 12), AS_OF)
    assert res == "applies" and why.startswith("Applies unless") and assumptions, (res, why, assumptions)


def test_plausible_exemption_unknown_unless_defeated():
    cov = {"tests": [{"field": "owner_type", "op": "!=", "value": "owner_occupied_two_family", "kind": "plausible_exemption",
                      "source_text": "owner-occupied two-family", "on_fail": "exclude",
                      "defeated_if": {"field": "units", "op": ">", "value": 2}}]}
    assert engine.evaluate_coverage(RULE, cov, facts("MA", "Test", 1950, None), AS_OF)[0] == "unknown"
    assert engine.evaluate_coverage(RULE, cov, facts("MA", "Test", 1950, 6), AS_OF)[0] == "applies"


def test_timing_condition_never_unknown():
    cov = {"tests": [{"field": "tenancy_months", "op": ">=", "value": 6, "kind": "timing",
                      "source_text": "after six months of tenancy", "on_fail": "exclude", "defeated_if": None}]}
    res, why, assumptions, _ = engine.evaluate_coverage(RULE, cov, facts("CA", "Test", 1990, 10), AS_OF)
    assert res == "applies" and assumptions


def test_la_rso_1978_cutoff():
    la_rent = find("Los Angeles, CA", "rent_increase_limits")
    assert la_rent
    results = {yb: run(facts("CA", "Los Angeles", yb, 20)) for yb in (1977, 1978, 1979)}
    assert any(results[1977][r]["result"] == "applies" for r in la_rent if r in results[1977])
    assert any(results[1978][r]["result"] == "unknown" for r in la_rent if r in results[1978]), results[1978]
    assert not any(results[1979].get(r, {}).get("result") == "applies" for r in la_rent)


def test_la_precedence_state_just_cause_superseded_whatever_the_year():
    ca_jc = find("CA", "just_cause_eviction", citation="1946.2")
    assert ca_jc
    for yb in (1950, 1978, 2015):
        res = run(facts("CA", "Los Angeles", yb, 20))
        assert res[ca_jc[0]]["result"] == "superseded", (yb, res.get(ca_jc[0]))


def test_no_dropped_rows_for_reported_rules():
    """Every in-jurisdiction rule that is not failed/negative and not excluded by a hard coverage fact appears."""
    f = facts("NJ", "Newark", None, None)
    res = run(f)
    expected = [r for r in engine.rules_for(f, RULES) if r["status"] != "failed" and not r.get("negative_finding")]
    missing = [r["team_rule_id"] for r in expected if r["team_rule_id"] not in res]
    assert not missing, missing


def test_hoboken_rent_control_uses_query_date():
    hob = find("Hoboken, NJ", "rent_increase_limits", citation="155")
    assert hob
    rid = hob[0]
    assert run(facts("NJ", "Hoboken", 1980, None))[rid]["result"] == "applies"            # pre-1987
    assert run(facts("NJ", "Hoboken", 1990, None))[rid]["result"] == "applies"            # 36 years old
    assert run(facts("NJ", "Hoboken", 2001, None))[rid]["result"] == "unknown"            # inside the 30-year window
    assert run(facts("NJ", "Hoboken", 1990, None), "2015-01-01")[rid]["result"] == "unknown"  # only 25 years old then
    assert run(facts("NJ", "Hoboken", None, None))[rid]["result"] == "unknown"


def test_shared_condition_state_rule_superseded_when_year_missing():
    ca_jc = find("CA", "just_cause_eviction", citation="1946.2")
    res = run(facts("CA", "San Diego", None, 16))
    assert res[ca_jc[0]]["result"] == "superseded", res[ca_jc[0]]


def test_nj_class_4c_is_not_a_unit_count():
    assert engine.building_type("4C", "3S-B-A-13U-H") is None
    assert engine.building_type("4C", "Apartments (class 4C)") == "apartments"
    assert engine.building_type("A/112", "APT 7-30 UNITS") == "apartments"


def test_ma_bills_pending_and_ballot_question_absent():
    res = run(facts("MA", "Cambridge", 1960, 12))
    alg = [r for r in res.values() if BY_ID[r["team_rule_id"]]["category"] == "algorithmic_rent_setting"
           and BY_ID[r["team_rule_id"]]["jurisdiction"] == "MA"]
    assert alg and all(r["result"] == "pending" for r in alg), alg
    failed_ids = {r["team_rule_id"] for r in RULES if r["status"] == "failed"}
    assert not failed_ids & set(res), failed_ids & set(res)
