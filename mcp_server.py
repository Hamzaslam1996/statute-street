"""
mcp_server.py - Statute Street as an MCP server (instructions/agent_mcp.md).

Plain-language summary
----------------------
Any AI agent (a leasing or operations agent, Claude, a pricing engine's assistant) can ask
Statute Street before it acts. The agent never decides the law: the deterministic engine does,
and the agent quotes the answer. Five read-only tools, stdio transport, no network, no model
calls, no writes. Every answer carries the as-of date, the citation, the quoted span and the
source URL, and ends with the standing notice.

Run:        .venv/bin/python mcp_server.py
Register:   claude mcp add statute-street -- <abs path>/.venv/bin/python <abs path>/mcp_server.py
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import date
from functools import lru_cache
from pathlib import Path

from mcp.server.mcpserver import MCPServer

import engine
import export_ui   # tidy(): public text filter and dash punctuation; build_change_register(): the UI's five rows
from common import DEFAULT_QUERY_DATE, OUT, ROOT

NOTICE = ("Legal information, not legal advice. Determinations are computed by the Statute Street engine; "
          "quote them, do not reinterpret them.")
INSTRUCTIONS = (
    "Statute Street answers which rental housing rules bind a specific US apartment address on a given date "
    "(California, New Jersey, Massachusetts portfolio of 500 sample addresses). Call check_action before any rent, "
    "fee, screening or termination step. Never state a rule without its citation. If a verdict is unknown or "
    "needs_human_review, stop and ask a human. " + NOTICE
)
RULES_VERSION = "1.0"

# The same action to category mapping as the UI's Action check page.
ACTIONS = {
    "raise_rent": ["rent_increase_limits"],
    "use_pricing_software": ["algorithmic_rent_setting"],
    "screen_applicant": ["screening_restrictions"],
    "charge_fee": ["application_screening_fees"],
    "take_deposit": ["security_deposits"],
    "end_tenancy": ["just_cause_eviction"],
}
# Rules that state the absence of a restriction ("No rent cap: state law bars local rent control")
# bind nothing; they are reported but never make an action "restricted".
PERMISSIVE_RE = re.compile(r"^No (rent cap|local rent control|rent control|statewide rent control|city rule|state rule)\b", re.I)

RULE_FIELDS = ("team_rule_id", "jurisdiction", "level", "category", "status", "title", "key_value", "citation",
               "quoted_span", "source_url", "retrieved_at", "effective_date", "requirement", "requirement_es")

mcp = MCPServer("statute-street", instructions=INSTRUCTIONS, version=RULES_VERSION)


# ----------------------------------------------------------------------------- data (loaded once)
@lru_cache(maxsize=1)
def data() -> dict:
    rules, coverage, juris, addresses = engine.load_inputs()
    engine.attach_phrases(coverage)
    shorts_path = ROOT / "data" / "key_value_short.json"
    shorts = json.loads(shorts_path.read_text(encoding="utf-8")).get("rules", {}) if shorts_path.exists() else {}
    lookups = json.loads((OUT / "lookups.json").read_text(encoding="utf-8"))
    changes = json.loads((OUT / "changes.json").read_text(encoding="utf-8")) if (OUT / "changes.json").exists() else {}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True,
                                         stderr=subprocess.DEVNULL).strip()
    except Exception:
        commit = "unknown"
    return {"rules": rules, "by_id": {r["team_rule_id"]: r for r in rules}, "coverage": coverage, "juris": juris,
            "addresses": {a["address_id"]: a for a in addresses}, "shorts": shorts, "lookups": lookups,
            "changes": changes, "commit": commit}


def key_value_short(rule: dict) -> str | None:
    if rule.get("derived"):
        return "No city rule; state law applies" if rule.get("level") == "city" else "No state rule"
    sv = data()["shorts"].get(rule["team_rule_id"])
    if sv and sv.get("title_hint", "").lower() in (rule.get("title") or "").lower():
        return sv["text"]
    kv = rule.get("key_value") or ""
    return kv if len(kv) <= 70 else kv[:67].rstrip() + "..."


def address_summary(aid: str) -> dict:
    d = data()
    a, j = d["addresses"][aid], d["juris"].get(aid, {})
    return {"address_id": aid, "street": a.get("street_address"), "postal_city": a.get("postal_city"),
            "legal_city": j.get("city") or a.get("postal_city"), "state": a.get("state"), "zip": a.get("zip") or None,
            "year_built": a.get("year_built") or None, "units": a.get("units") or None,
            "use_description": a.get("use_description") or None}


def parse_date(as_of: str | None) -> date:
    return date.fromisoformat((as_of or DEFAULT_QUERY_DATE)[:10])


def rows_for(aid: str, as_of: date) -> list[dict]:
    """Engine rows for one address: the cached file for the default date, the engine in-process otherwise."""
    d = data()
    if aid not in d["addresses"]:
        raise ValueError(f"unknown address_id {aid}; use find_address first")
    if as_of.isoformat() == d["lookups"].get("as_of", DEFAULT_QUERY_DATE):
        rows = d["lookups"]["lookups"].get(aid, [])
    else:
        facts = engine.address_facts(d["addresses"][aid], d["juris"].get(aid, {}))
        rows = engine.evaluate_address(facts, d["rules"], d["coverage"], as_of)
    out = []
    for r in rows:
        rule = d["by_id"][r["team_rule_id"]]
        row = {k: (export_ui.tidy(rule.get(k)) if k in ("title", "requirement", "key_value") else rule.get(k)) for k in RULE_FIELDS}
        row.update({"result": r["result"], "explanation": export_ui.tidy(r.get("explanation") or ""), "assumptions": r.get("assumptions") or [],
                    "conflict_flag": bool(r.get("conflict_flag")), "governed_by": r.get("governed_by"),
                    "key_value_short": key_value_short(rule), "as_of": as_of.isoformat()})
        out.append(row)
    return out


def context_rules(aid: str, categories: list[str], rows: list[dict]) -> tuple[list[str], list[str]]:
    """
    Rules the engine never lists as applying but an operator still wants to see: negative findings and
    'no rent cap' statements for the address's state and legal city, and pending or failed measures.
    """
    d = data()
    s = address_summary(aid)
    places = {s["state"], f"{s['legal_city']}, {s['state']}"}
    shown = {r["team_rule_id"] for r in rows}
    none_here, measures = [], []
    for r in d["rules"]:
        if r["category"] not in categories or r["jurisdiction"] not in places or r["team_rule_id"] in shown:
            continue
        label = f"{r['team_rule_id']} {export_ui.tidy(key_value_short(r) or r['title'])} ({r['citation']}; {r['jurisdiction']})"
        if r["status"] in ("pending", "failed"):
            measures.append(f"{r['status']}: {r['team_rule_id']} {export_ui.tidy(r['title'])} ({r['citation']})")
        elif r.get("negative_finding") or PERMISSIVE_RE.match(r.get("key_value") or r.get("title") or ""):
            none_here.append(label)
    return none_here, measures


def finish(payload) -> str:
    """Every tool answer is JSON followed by the standing notice."""
    return json.dumps(payload, indent=1, ensure_ascii=False) + "\n\n" + NOTICE


def missing_fact_of(explanation: str) -> str:
    m = re.match(r"Unknown: needs ([^.]+)\.", explanation or "")
    if m:
        return m.group(1).strip()
    return "the deciding fact (see explanation)"


# ----------------------------------------------------------------------------- tools
@mcp.tool()
def find_address(query: str) -> str:
    """Find up to 5 portfolio addresses by id, street, postal or legal city, state or ZIP. Returns address_id, street, legal city, state."""
    q = (query or "").strip().lower()
    toks = [t for t in re.split(r"[\s,]+", q) if t]
    hits = []
    for aid in data()["addresses"]:
        s = address_summary(aid)
        hay = " ".join(str(v) for v in (aid, s["street"], s["postal_city"], s["legal_city"], s["state"], s["zip"]) if v).lower()
        if q == aid.lower():
            score = 100
        else:
            score = sum(1 for t in toks if t in hay)
            if toks and score < len(toks):
                continue
        hits.append((score, aid, s))
    hits.sort(key=lambda h: (-h[0], h[1]))
    return finish({"query": query, "matches": [s for _, _, s in hits[:5]]})


@mcp.tool()
def get_determinations(address_id: str, as_of: str = DEFAULT_QUERY_DATE, category: str | None = None) -> str:
    """All rule determinations for an address on a date (YYYY-MM-DD), optionally one category. Each row: result (applies, unknown, superseded, not_yet_effective, pending), explanation, assumptions, conflict_flag, key_value_short, citation, quoted_span, source_url, retrieved_at."""
    d = parse_date(as_of)
    rows = rows_for(address_id, d)
    if category:
        rows = [r for r in rows if r["category"] == category]
    return finish({"address": address_summary(address_id), "as_of": d.isoformat(), "category": category,
                   "rules_version": RULES_VERSION, "engine_commit": data()["commit"], "determinations": rows})


def verdict_for(rows: list[dict]) -> dict:
    binding = [r for r in rows if r["result"] == "applies" and not PERMISSIVE_RE.match(r.get("key_value") or r.get("title") or "")]
    permissive = [r for r in rows if r["result"] == "applies" and r not in binding]
    future = sorted([r for r in rows if r["result"] == "not_yet_effective"], key=lambda r: r.get("effective_date") or "9999")
    unknown = [r for r in rows if r["result"] == "unknown"]
    pending = [r for r in rows if r["result"] == "pending"]
    review = any(r["conflict_flag"] for r in rows)
    if binding:
        verdict = "restricted"
    elif future:
        verdict = f"permitted_now_restricted_from:{future[0].get('effective_date')}"
    elif unknown:
        verdict = f"unknown_needs:{missing_fact_of(unknown[0]['explanation'])}"
    elif review:
        verdict = "needs_human_review"
    else:
        verdict = "no_rule_found"
    return {"verdict": verdict, "needs_human_review": review,
            "binding_rules": [f"{r['team_rule_id']} {r['title']} ({r['citation']})" for r in binding],
            "no_restriction_rules": [f"{r['team_rule_id']} {r['key_value_short']} ({r['citation']})" for r in permissive],
            "future_rules": [f"{r['team_rule_id']} {r['title']} from {r.get('effective_date')}" for r in future],
            "pending_bills": [f"{r['team_rule_id']} {r['title']} ({r['citation']})" for r in pending],
            "unknown_rules": [f"{r['team_rule_id']} {r['explanation']}" for r in unknown]}


@mcp.tool()
def check_action(address_id: str, action: str, as_of: str = DEFAULT_QUERY_DATE) -> str:
    """Check one planned action at an address on a date. action: raise_rent, use_pricing_software, screen_applicant, charge_fee, take_deposit, end_tenancy. Verdict: restricted, permitted_now_restricted_from:<date>, unknown_needs:<fact>, no_rule_found or needs_human_review, with the binding rows."""
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {', '.join(ACTIONS)}")
    d = parse_date(as_of)
    rows = [r for r in rows_for(address_id, d) if r["category"] in ACTIONS[action]]
    v = verdict_for(rows)
    none_here, measures = context_rules(address_id, ACTIONS[action], rows)
    v["no_restriction_rules"] += none_here
    v["pending_or_failed_measures"] = measures
    return finish({"address": address_summary(address_id), "action": action, "as_of": d.isoformat(), **v,
                   "rows": rows, "rules_version": RULES_VERSION, "engine_commit": data()["commit"]})


def change_register() -> list[dict]:
    import export_ui   # the same five rows the UI shows
    return export_ui.build_change_register(data()["rules"], data()["changes"])


@mcp.tool()
def upcoming_changes(address_id: str | None = None, after: str = DEFAULT_QUERY_DATE) -> str:
    """Change register rows (the five tracked changes T1 to T5) and any rule not yet in force after the given date, optionally only those touching one address."""
    d = parse_date(after)
    reg = change_register()
    ch = data()["changes"]
    if address_id:
        reg = [r for r in reg if address_id in ch.get(r["test_id"], {}).get("affected_address_ids", [])]
        future = [{k: r[k] for k in ("team_rule_id", "title", "jurisdiction", "category", "citation", "effective_date", "source_url")}
                  for r in rows_for(address_id, d) if r["result"] == "not_yet_effective"]
    else:
        future = [{k: r.get(k) for k in ("team_rule_id", "title", "jurisdiction", "category", "citation", "effective_date", "source_url")}
                  for r in data()["rules"] if r.get("effective_date") and r["effective_date"][:10] > d.isoformat() and r["status"] != "failed"]
    return finish({"after": d.isoformat(), "address_id": address_id, "change_register": reg, "rules_not_yet_in_force": future})


@mcp.tool()
def reliance_record(address_id: str, action: str, as_of: str = DEFAULT_QUERY_DATE) -> str:
    """Markdown reliance record for one action at an address on a date: Relied on / Not applicable on this date / Unresolved, with citations, quoted text, engine commit and rules version."""
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {', '.join(ACTIONS)}")
    d = parse_date(as_of)
    s = address_summary(address_id)
    rows = [r for r in rows_for(address_id, d) if r["category"] in ACTIONS[action]]
    v = verdict_for(rows)
    relied = [r for r in rows if r["result"] == "applies"]
    not_now = [r for r in rows if r["result"] in ("not_yet_effective", "pending", "superseded")]
    unresolved = [r for r in rows if r["result"] == "unknown" or r["conflict_flag"]]

    def block(r: dict) -> str:
        lines = [f"- **{r['title']}** ({r['citation']}), {r['jurisdiction']}: {r['result'].replace('_', ' ')}.",
                 f"  {r['explanation']}"]
        if r.get("assumptions"):
            lines.append("  Presumed: " + "; ".join(r["assumptions"]) + ".")
        if r.get("quoted_span"):
            lines.append(f"  > {r['quoted_span'][:400]}")
        if r.get("source_url"):
            lines.append(f"  Source: {r['source_url']} (retrieved {r.get('retrieved_at') or 'date not stated'})")
        return "\n".join(lines)

    def section(title: str, rows_: list[dict]) -> list[str]:
        return [f"## {title}"] + ([block(r) for r in rows_] or ["- None."]) + [""]

    md = [f"# Reliance record: {action.replace('_', ' ')} at {s['street']}, {s['legal_city']}, {s['state']}",
          f"Address id {address_id}. As of {d.isoformat()}. Verdict: {v['verdict']}"
          + (" (needs human review)" if v["needs_human_review"] else "") + ".", ""]
    md += section("Relied on", relied) + section("Not applicable on this date", not_now) + section("Unresolved", unresolved)
    none_here, measures = context_rules(address_id, ACTIONS[action], rows)
    if none_here or measures:
        md += ["## Checked and found no restriction"] + [f"- {x}" for x in none_here + measures] + [""]
    md += [f"Statute Street rules version {RULES_VERSION}, engine commit {data()['commit']}. {NOTICE}"]
    return "\n".join(md)


if __name__ == "__main__":
    mcp.run(transport="stdio")
