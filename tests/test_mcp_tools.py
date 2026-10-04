"""
tests/test_mcp_tools.py - the five MCP tools (instructions/agent_mcp.md), called directly and once over stdio.

Fixed facts checked here:
  A0016  3515 Fillmore St, San Francisco (built 1926, 21 units): SF rent cap binds a rent increase.
  A0002  1031-1035 Clinton St, Hoboken: pricing software restricted by Hoboken ch. 158 today, flagged for human
         review (FAIR Act preemption question); from 2027-07-02 the FAIR Act binds as well.
  A0010  134 Oxford St, Cambridge: no rent cap rule (state law bars local rent control); failed ballot measures listed.
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mcp_server as m  # noqa: E402

NOTICE_TAIL = "quote them, do not reinterpret them."


def payload(text: str) -> dict:
    assert text.strip().endswith(NOTICE_TAIL), "every answer ends with the standing notice"
    return json.loads(text.rsplit("\n\n", 1)[0])


def test_find_address_by_street_and_id():
    assert payload(m.find_address("3515 Fillmore"))["matches"][0]["address_id"] == "A0016"
    hits = payload(m.find_address("A0002"))["matches"]
    assert hits[0]["address_id"] == "A0002" and hits[0]["legal_city"] == "Hoboken"
    assert len(payload(m.find_address("Cambridge"))["matches"]) <= 5


def test_get_determinations_carries_evidence_fields():
    out = payload(m.get_determinations("A0016", "2026-10-01"))
    assert out["as_of"] == "2026-10-01" and out["determinations"]
    for row in out["determinations"]:
        for k in ("citation", "quoted_span", "source_url", "retrieved_at", "result", "explanation", "key_value_short"):
            assert k in row
    rent = payload(m.get_determinations("A0016", "2026-10-01", "rent_increase_limits"))["determinations"]
    assert {r["category"] for r in rent} == {"rent_increase_limits"}
    assert any(r["result"] == "applies" and "San Francisco" in r["title"] for r in rent)


def test_a0016_raise_rent_restricted_by_sf_cap():
    out = payload(m.check_action("A0016", "raise_rent", "2026-10-01"))
    assert out["verdict"] == "restricted"
    assert any("37.3" in b or "San Francisco" in b for b in out["binding_rules"])


def test_a0002_pricing_software_today_and_after_fair_act():
    today = payload(m.check_action("A0002", "use_pricing_software", "2026-10-01"))
    assert today["verdict"] == "restricted"
    assert any("158" in b for b in today["binding_rules"]), today["binding_rules"]
    assert today["needs_human_review"] is True
    assert any("FAIR" in f and "2027-07-01" in f for f in today["future_rules"])
    later = payload(m.check_action("A0002", "use_pricing_software", "2027-07-02"))
    assert later["verdict"] == "restricted" and len(later["binding_rules"]) == 2
    assert any("FAIR" in b for b in later["binding_rules"])


def test_a0010_raise_rent_no_rent_cap_rule_measures_listed():
    out = payload(m.check_action("A0010", "raise_rent", "2026-10-01"))
    assert out["verdict"] == "no_rule_found" and out["binding_rules"] == []
    assert any("No rent cap" in x or "No city rule" in x for x in out["no_restriction_rules"]), out["no_restriction_rules"]
    assert out["pending_or_failed_measures"], "the struck ballot question is listed as a failed measure"


def test_bad_action_is_rejected():
    with pytest.raises(ValueError):
        m.check_action("A0016", "paint_the_lobby", "2026-10-01")


def test_upcoming_changes_for_hoboken_address():
    out = payload(m.upcoming_changes("A0002", "2026-10-01"))
    ids = {c["test_id"] for c in out["change_register"]}
    assert {"T2", "T3"} <= ids and "T1" not in ids
    assert any("FAIR" in r["title"] for r in out["rules_not_yet_in_force"])
    everything = payload(m.upcoming_changes(None, "2026-10-01"))
    assert len(everything["change_register"]) == 5


def test_reliance_record_sections():
    md = m.reliance_record("A0002", "use_pricing_software", "2026-10-01")
    for heading in ("## Relied on", "## Not applicable on this date", "## Unresolved"):
        assert heading in md
    assert "needs human review" in md and md.strip().endswith(NOTICE_TAIL)
    assert "rules version 1.0" in md and "engine commit" in md
    cam = m.reliance_record("A0010", "raise_rent", "2026-10-01")
    assert "## Checked and found no restriction" in cam


def test_server_answers_over_stdio():
    from mcp.client import Client
    from mcp.client.stdio import StdioServerParameters

    async def go():
        params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "mcp_server.py")], cwd=str(ROOT))
        async with Client(params) as c:
            names = {t.name for t in (await c.list_tools()).tools}
            assert names == {"find_address", "get_determinations", "check_action", "upcoming_changes", "reliance_record"}
            assert "check_action" in (c.instructions or "")
            r = await c.call_tool("check_action", {"address_id": "A0002", "action": "use_pricing_software"})
            return payload(r.content[0].text)

    out = asyncio.run(asyncio.wait_for(go(), 90))
    assert out["verdict"] == "restricted" and out["needs_human_review"] is True
