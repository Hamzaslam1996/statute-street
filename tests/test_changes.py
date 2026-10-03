"""Module C acceptance tests (instructions/module_c.md). Run: python -m pytest tests/ -q"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import changes  # noqa: E402

RUNNER = changes.Runner()
TESTS = json.loads((ROOT.parent / "participant-final-no-hour16 3" / "dev" / "change_tests.json").read_text())
CHANGES, DETAIL, RULE_MAP = changes.build(RUNNER, TESTS)
CITY = {a: RUNNER.city_of(a) for a in RUNNER.juris}
STATE = {a: RUNNER.state_of(a) for a in RUNNER.juris}


def results(as_of, address_id):
    return {r["team_rule_id"]: r for r in RUNNER.run(as_of)[address_id]}


def test_t1_ab325_flips_for_every_ca_address():
    ca = {a for a, s in STATE.items() if s == "CA"}
    assert set(CHANGES["T1"]["affected_address_ids"]) == ca
    rids = RULE_MAP["T1"]["CA-ALG-01"]
    assert rids
    for a in list(ca)[:25]:
        assert results("2025-12-31", a)[rids[0]]["result"] == "not_yet_effective"
        assert results("2026-01-02", a)[rids[0]]["result"] == "applies"


def test_t2_boundary_hoboken_jersey_city_newark():
    hob = {a for a, c in CITY.items() if c == "Hoboken"}
    jc = {a for a, c in CITY.items() if c == "Jersey City"}
    newark = {a for a, c in CITY.items() if c == "Newark"}
    assert set(CHANGES["T2"]["affected_address_ids"]) == hob | jc
    for rid in RULE_MAP["T2"]["HOB-ALG-01"]:
        for aids in DETAIL["T2"]["affected_by_rule"].get(rid, {}).values():
            assert set(aids) <= hob
    for rid in RULE_MAP["T2"]["JC-ALG-01"]:
        for aids in DETAIL["T2"]["affected_by_rule"].get(rid, {}).values():
            assert set(aids) <= jc
    for a in newark:
        for rid in results("2026-10-01", a):
            assert RUNNER.by_id[rid]["jurisdiction"] not in ("Hoboken, NJ", "Jersey City, NJ")


def test_t3_fair_act_dates_and_conflicts():
    nj = {a for a, s in STATE.items() if s == "NJ"}
    assert set(CHANGES["T3"]["affected_address_ids"]) == nj
    rid = RULE_MAP["T3"]["NJ-ALG-01"][0]
    for a in list(nj)[:25]:
        assert results("2026-10-01", a)[rid]["result"] == "not_yet_effective"
        assert results("2027-07-02", a)[rid]["result"] == "applies"
    jc_hob = {a for a, c in CITY.items() if c in ("Jersey City", "Hoboken")}
    assert set(CHANGES["T3"]["conflict_flag_address_ids"]) == jc_hob


def test_t4_ma_bills_pending_everywhere_in_ma():
    ma = {a for a, s in STATE.items() if s == "MA"}
    assert set(CHANGES["T4"]["affected_address_ids"]) == ma
    for a in list(ma)[:25]:
        res = results("2026-10-01", a)
        for gid in ("MA-ALG-P1", "MA-ALG-P2"):
            for rid in RULE_MAP["T4"][gid]:
                assert res[rid]["result"] == "pending"


def test_t5_struck_ballot_question_affects_nobody_and_no_rent_cap():
    assert CHANGES["T5"]["affected_address_ids"] == []
    for a, c in CITY.items():
        if c in ("Boston", "Cambridge"):
            for rid, r in results("2026-10-01", a).items():
                rule = RUNNER.by_id[rid]
                if rule["category"] == "rent_increase_limits" and not rule.get("negative_finding"):
                    assert r["result"] not in changes.RENT_CAP_RESULTS, (a, rid, r)


def test_module_c_assertions_pass():
    assert changes.check_assertions(RUNNER, CHANGES, DETAIL) == []
