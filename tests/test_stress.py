"""
Adversarial perturbations (instructions/stress_test.md section 2). Measure-only: no data files change.
Run: python -m pytest tests/test_stress.py -q
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import engine  # noqa: E402
import resolve  # noqa: E402
from common import list_docs, normalise  # noqa: E402

RULES, COVERAGE, JURIS, ADDRESSES = engine.load_inputs()
BY_ID = {r["team_rule_id"]: r for r in RULES}
LOOKUPS = json.loads((ROOT / "out" / "lookups.json").read_text(encoding="utf-8"))["lookups"]
AS_OF = date(2026, 10, 1)


def facts(state, city, year_built=None, units=None, btype="apartments", use="test"):
    return {"address_id": "T", "state": state, "city": city, "year_built": year_built, "units": units,
            "building_type": btype, "funding": None, "units_min": None, "units_derived": None,
            "units_derived_source": None, "use_description": use}


def run(f, as_of=AS_OF):
    return {r["team_rule_id"]: r for r in engine.evaluate_address(f, RULES, COVERAGE, as_of)}


def rule_ids(jur, cat, cite=None):
    return [r["team_rule_id"] for r in RULES if r["jurisdiction"] == jur and r["category"] == cat
            and not r.get("negative_finding") and (cite is None or cite in (r.get("citation") or ""))]


def result(res, rid):
    return res[rid]["result"] if rid in res else "not_covered"


# --- 1. cutoff years ---------------------------------------------------------
@pytest.mark.parametrize("yb,expect", [(1978, "applies"), (1979, "unknown"), (1980, "not_covered")])
def test_sf_rent_cutoff_1979(yb, expect):
    rid = rule_ids("San Francisco, CA", "rent_increase_limits")[0]
    assert result(run(facts("CA", "San Francisco", yb, 20)), rid) == expect


@pytest.mark.parametrize("yb,expect", [(1977, "applies"), (1978, "unknown"), (1979, "not_covered")])
def test_la_rso_rent_cutoff_1978(yb, expect):
    rid = rule_ids("Los Angeles, CA", "rent_increase_limits")[0]
    assert result(run(facts("CA", "Los Angeles", yb, 20)), rid) == expect


@pytest.mark.parametrize("yb,expect", [(1977, ("unknown", "not_covered")), (1978, ("unknown",)), (1979, ("applies",))])
def test_la_jco_cutoff_1978_other_side(yb, expect):
    """
    Documented behaviour: for a pre-1978 building the JCO answers unknown, not 'not covered', because
    its coverage condition ("properties not regulated by the RSO") is conditional: a pre-1978 unit
    that is RSO-exempt (e.g. a single-family home) is still under the JCO, and RSO exemption is not
    in the parcel data. The RSO rule carries the pre-1978 side for ordinary apartment buildings.
    """
    rid = rule_ids("Los Angeles, CA", "just_cause_eviction", cite="165")[0]
    assert result(run(facts("CA", "Los Angeles", yb, 20)), rid) in expect


@pytest.mark.parametrize("yb,expect", [(2010, "applies"), (2011, "unknown"), (2012, "unknown_or_not_covered")])
def test_ab1482_15_year_window(yb, expect):
    """CA rent cap in San Diego (no local rent control): window year 2011 for a 2026 query date."""
    rid = rule_ids("CA", "rent_increase_limits", cite="1947.12")[0]
    got = result(run(facts("CA", "San Diego", yb, 20)), rid)
    assert got == expect if expect != "unknown_or_not_covered" else got in ("unknown", "not_covered"), got


@pytest.mark.parametrize("yb,expect", [(1986, "applies"), (1987, "applies"), (1988, "applies"), (1995, "applies"),
                                       (1996, "unknown"), (1997, "unknown"), (None, "unknown")])
def test_hoboken_1987_and_30_year_rule(yb, expect):
    rid = rule_ids("Hoboken, NJ", "rent_increase_limits", cite="155")[0]
    assert result(run(facts("NJ", "Hoboken", yb, None, btype=None)), rid) == expect


@pytest.mark.parametrize("yb", [1995, 1996, 1997, None])
def test_newark_30_year_rule(yb):
    rid = rule_ids("Newark, NJ", "rent_increase_limits")[0]
    got = result(run(facts("NJ", "Newark", yb, None, btype=None)), rid)
    if yb == 1995:
        assert got in ("applies", "unknown"), got      # covered unless another silent condition intervenes
    elif yb in (1996, 1997):
        assert got in ("unknown", "not_covered"), got  # cutoff year or inside the exemption window
    else:
        assert got == "unknown"


# --- 2. missing / malformed facts never crash ----------------------------------
@pytest.mark.parametrize("year,units", [("", ""), (None, None), ("1950", "0"), ("abc", "n/a"), ("", "6"), ("1979", "")])
def test_missing_or_malformed_facts_never_crash(year, units):
    row = {"address_id": "T", "street_address": "1 Test St", "postal_city": "San Francisco", "state": "CA", "zip": "",
           "year_built": year, "units": units, "use_code": "A5", "use_description": "Apartment 5 to 14 Units"}
    f = engine.address_facts(row, {"state": "CA", "city": "San Francisco"})
    res = engine.evaluate_address(f, RULES, COVERAGE, AS_OF)
    assert res and all(r["explanation"] for r in res)
    assert all(r["result"] in ("applies", "unknown", "superseded", "not_yet_effective", "pending") for r in res)


# --- 3. mailing city vs legal city -----------------------------------------------
@pytest.mark.parametrize("postal,legal", [("Dorchester", "Boston"), ("Brighton", "Boston"), ("South Boston", "Boston"),
                                          ("Hollywood", "Los Angeles"), ("Van Nuys", "Los Angeles"), ("San Ysidro", "San Diego")])
def test_postal_city_fallback_table(postal, legal):
    state = "MA" if legal == "Boston" else "CA"
    assert resolve.POSTAL_TO_LEGAL[state][postal] == legal


def test_sample_neighbourhoods_resolved_to_boston():
    rows = [a for a in ADDRESSES if a["postal_city"] in ("Dorchester", "Brighton", "South Boston", "Roxbury", "East Boston")]
    assert rows
    for a in rows:
        assert JURIS[a["address_id"]]["city"] == "Boston", a["address_id"]
        rules_here = {r["team_rule_id"] for r in LOOKUPS[a["address_id"]]}
        assert all(BY_ID[r]["jurisdiction"] in ("MA", "Boston, MA") for r in rules_here)


# --- 4. as-of dates around every effective date -------------------------------------
def test_status_flips_on_effective_date():
    checked = 0
    for r in RULES:
        d = r.get("effective_date")
        if not d or len(d) != 10 or r.get("negative_finding") or r["status"] not in ("in_force", "not_yet_effective"):
            continue
        eff = date.fromisoformat(d)
        before = engine.status_as_of(r, eff - timedelta(days=1))[0]
        on = engine.status_as_of(r, eff)[0]
        assert before == "not_yet_effective", (r["team_rule_id"], d, before)
        assert on is None, (r["team_rule_id"], d, on)     # None = proceed to coverage (applies / unknown / superseded)
        checked += 1
    assert checked > 10


def test_month_only_dates_are_unknown_inside_the_month():
    seen = 0
    for r in RULES:
        d = r.get("effective_date")
        if d and len(d) == 7 and r["status"] == "in_force" and not r.get("negative_finding"):
            y, m = int(d[:4]), int(d[5:7])
            assert engine.status_as_of(r, date(y, m, 1) - timedelta(days=1))[0] == "not_yet_effective"
            assert engine.status_as_of(r, date(y, m, 15))[0] == "unknown"          # documented: inside the month
            nxt = date(y + (m == 12), m % 12 + 1, 1)
            assert engine.status_as_of(r, nxt)[0] is None                           # in force once the month has passed
            seen += 1
    assert seen >= 1


# --- 5. pending and failed instruments ------------------------------------------------
@pytest.mark.parametrize("as_of", [date(2025, 1, 1), date(2026, 6, 23), date(2026, 10, 1), date(2027, 7, 2), date(2028, 12, 31)])
def test_pending_and_failed_never_apply(as_of):
    pending = {r["team_rule_id"] for r in RULES if r["status"] == "pending"}
    failed = {r["team_rule_id"] for r in RULES if r["status"] == "failed"}
    for f in (facts("MA", "Cambridge", 1960, 12), facts("MA", "Boston", 1920, 8), facts("NJ", "Hoboken", 2001, None, btype=None),
              facts("CA", "San Diego", 1990, 10)):
        res = run(f, as_of)
        for rid, r in res.items():
            if rid in pending:
                assert r["result"] == "pending", (rid, as_of)
            assert rid not in failed, (rid, as_of)


@pytest.mark.parametrize("as_of", [date(2025, 6, 1), date(2026, 10, 1), date(2027, 7, 2), date(2028, 1, 1)])
def test_boston_cambridge_never_show_a_rent_cap(as_of):
    for city in ("Boston", "Cambridge"):
        res = run(facts("MA", city, 1920, 6), as_of)
        for rid, r in res.items():
            rule = BY_ID[rid]
            if rule["category"] == "rent_increase_limits" and not rule.get("negative_finding"):
                assert r["result"] not in ("applies", "not_yet_effective", "pending"), (city, as_of, rid, r)


# --- 6. referential integrity and quote verification ----------------------------------
def test_every_lookup_row_references_an_existing_rule():
    for a, rows in LOOKUPS.items():
        for r in rows:
            assert r["team_rule_id"] in BY_ID, (a, r["team_rule_id"])


def test_every_cited_rule_quote_is_exact_substring_of_its_source():
    docs = list_docs()
    cited = {r["team_rule_id"] for rows in LOOKUPS.values() for r in rows}
    checked = 0
    for rid in cited:
        rule = BY_ID[rid]
        if rule.get("derived"):
            continue
        doc = docs[rule["source_doc_id"]]
        assert normalise(rule["quoted_span"]) in normalise(doc.body), rid
        checked += 1
    assert checked > 50
