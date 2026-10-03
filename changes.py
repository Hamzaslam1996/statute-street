"""
changes.py - Module C: change tracking. Deterministic: the rule engine is run at the
dates each test names and the results are compared with set arithmetic. No model calls.

Outputs
-------
  out/changes.json           organisers' format {test_id: {affected_address_ids, conflict_flag_address_ids, notes}}
  out/changes_detail.json    per test: rule mapping, per-rule address sets, status transitions, assertions
  out/changes_rule_map.json  organiser rule id -> our team_rule_ids
  out/changes_eval.md        score against gold/changes/T1-T5.json
  out/diff_<before>_<after>.json   with --diff: per address, per rule, old result -> new result

Usage
-----
  python changes.py
  python changes.py --diff --before 2025-12-31 --after 2026-01-02
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import engine
from common import OUT, STARTER
from lookup_eval import bucket_of

TESTS_JSON = STARTER / "dev" / "change_tests.json"
GOLD_CHANGES = Path("gold/changes/T1-T5.json")
RENT_CAP_RESULTS = {"applies", "not_yet_effective", "pending"}

# How the organisers describe each test, used for the notes (facts come from our rules).
NOTE_FACTS = {
    "T1": "AB 325 (Stats. 2025, ch. 338; Cal. Bus. & Prof. Code § 16729) effective 2026-01-01. Before that date every "
          "California address reports not_yet_effective; from 2026-01-02 applies.",
    "T2": "Boundary test decided by the geocoded legal city (Census incorporated place), never the mailing city.",
    "T3": "FAIR Act, P.L. 2026, c.43 (N.J.S.A. 56:9-20 to 56:9-26): approved 2026-07-20, effective 2027-07-01 (first day "
          "of the twelfth month after enactment). not_yet_effective on 2026-10-01, applies on 2027-07-02 for every NJ "
          "address. Section 6(b) bars conflicting municipal ordinances, so the Jersey City (§ 218-12) and Hoboken (ch. 158) "
          "bans carry a conflict flag for human review; we flag the possible preemption, we do not decide it.",
    "T4": "S.2983 and H.5222 (194th General Court) are pending bills, not law: reported as pending for every Boston and "
          "Cambridge address. The affected set is every Massachusetts address, i.e. who would be affected if enacted.",
    "T5": "Initiative Petition 25-21 (statewide rent increase limit) was struck from the ballot by the SJC on 2026-06-23 "
          "(Cella v. Attorney General, SJC-13893) and is recorded as failed. Failed measures are never reported for an "
          "address, so the affected set is empty; no rent cap is reported for any Boston or Cambridge address "
          "(M.G.L. c. 40P bars local rent control).",
}


# ---------------------------------------------------------------------------
# Engine runs
# ---------------------------------------------------------------------------
class Runner:
    """Runs the engine for all addresses at a date, once per date."""

    def __init__(self):
        self.rules, self.coverage, self.juris, self.addresses = engine.load_inputs()
        self.by_id = {r["team_rule_id"]: r for r in self.rules}
        self._cache: dict[str, dict] = {}

    def run(self, as_of: str) -> dict[str, list[dict]]:
        if as_of not in self._cache:
            d = date.fromisoformat(as_of)
            out = {}
            for row in self.addresses:
                facts = engine.address_facts(row, self.juris.get(row["address_id"], {}))
                out[row["address_id"]] = engine.evaluate_address(facts, self.rules, self.coverage, d)
            self._cache[as_of] = out
        return self._cache[as_of]

    def city_of(self, address_id: str) -> str | None:
        return self.juris.get(address_id, {}).get("city")

    def state_of(self, address_id: str) -> str | None:
        return self.juris.get(address_id, {}).get("state")


# ---------------------------------------------------------------------------
# Organiser rule ids -> our rules
# ---------------------------------------------------------------------------
def map_rule_ids(test: dict, rules: list[dict]) -> dict[str, list[str]]:
    """
    'CA-ALG-01' -> our rules in the CA / algorithmic bucket. Ids ending -P<n> are proposals or
    failed measures: they map to pending/failed records, in the order the bills are named in
    the test title (S.2983 -> P1, H.5222 -> P2).
    """
    mapping: dict[str, list[str]] = {}
    bills = re.findall(r"\b([HS]\.\s?\d{3,5})\b", test.get("title", ""))
    for i, gid in enumerate(test["rule_ids"]):
        b = bucket_of(gid)
        if not b:
            mapping[gid] = []
            continue
        cands = [r for r in rules if (r["jurisdiction"], r["category"]) == b and not r.get("derived")]
        if re.search(r"-P\d+$", gid):
            cands = [r for r in cands if r["status"] in ("pending", "failed")]
            if bills and i < len(bills):
                num = re.sub(r"\D", "", bills[i])
                by_bill = [r for r in cands if num in (r.get("citation") or "") or num in (r.get("title") or "")]
                cands = by_bill or cands
        else:
            cands = [r for r in cands if not r.get("negative_finding")]
        mapping[gid] = [r["team_rule_id"] for r in cands]
    return mapping


# ---------------------------------------------------------------------------
# Build changes.json
# ---------------------------------------------------------------------------
def build(runner: Runner, tests: list[dict]) -> tuple[dict, dict, dict]:
    changes, detail, rule_map = {}, {}, {}
    for test in tests:
        tid = test["test_id"]
        dates = [test[k] for k in ("as_of_before", "as_of_after") if k in test] or [test["as_of"]]
        mapping = map_rule_ids(test, runner.rules)
        rule_map[tid] = mapping
        ours = {rid for ids in mapping.values() for rid in ids}

        affected, conflicts, per_rule, transitions = set(), set(), {}, {}
        for d in dates:
            res = runner.run(d)
            for aid, rows in res.items():
                for r in rows:
                    if r["team_rule_id"] in ours:
                        affected.add(aid)
                        per_rule.setdefault(r["team_rule_id"], {}).setdefault(d, set()).add(aid)
                        transitions.setdefault(aid, {}).setdefault(r["team_rule_id"], {})[d] = r["result"]
                        if r.get("conflict_flag"):
                            conflicts.add(aid)

        # per-rule sets by legal city (T2 wants these spelled out)
        per_rule_cities = {rid: {d: sorted({runner.city_of(a) for a in aids}) for d, aids in by_date.items()}
                           for rid, by_date in per_rule.items()}
        status_counts = {}
        for d in dates:
            c = {}
            for aid, by_rule in transitions.items():
                for rid, by_date in by_rule.items():
                    if d in by_date:
                        c[by_date[d]] = c.get(by_date[d], 0) + 1
            status_counts[d] = c

        notes = [NOTE_FACTS.get(tid, ""), test.get("expected_behavior", "")]
        for gid, ids in mapping.items():
            for rid in ids:
                r = runner.by_id[rid]
                cities = per_rule_cities.get(rid, {})
                where = "; ".join(f"{d}: {', '.join(x or '?' for x in cs)} ({len(per_rule[rid][d])} addresses)"
                                  for d, cs in cities.items()) or "no address reports this rule"
                notes.append(f"{gid} -> {rid} ({r['citation']}; status {r['status']}, effective {r.get('effective_date')}): {where}.")
        for d, c in status_counts.items():
            notes.append(f"Results on {d}: {c}.")

        entry = {"affected_address_ids": sorted(affected), "conflict_flag_address_ids": sorted(conflicts),
                 "notes": " ".join(n for n in notes if n)}
        changes[tid] = entry
        detail[tid] = {"dates": dates, "rule_map": mapping,
                       "affected_by_rule": {rid: {d: sorted(a) for d, a in by_date.items()} for rid, by_date in per_rule.items()},
                       "status_counts": status_counts,
                       "transitions_sample": dict(list(transitions.items())[:3])}
    return changes, detail, rule_map


def check_assertions(runner: Runner, changes: dict, detail: dict) -> list[str]:
    """The hard checks from instructions/module_c.md. Returns a list of failures (empty = all good)."""
    fails = []
    res = runner.run("2026-10-01")
    cities = {a: runner.city_of(a) for a in res}
    # T2: Hoboken rule only in Hoboken, Jersey City rule only in Jersey City, Newark neither.
    for rid, by_date in detail["T2"]["affected_by_rule"].items():
        jur = runner.by_id[rid]["jurisdiction"].split(",")[0]
        for d, aids in by_date.items():
            wrong = [a for a in aids if cities.get(a) != jur]
            if wrong:
                fails.append(f"T2: {rid} ({jur}) reported for non-{jur} addresses {wrong[:5]}")
    newark = [a for a, c in cities.items() if c == "Newark"]
    for a in newark:
        for r in res[a]:
            if runner.by_id[r["team_rule_id"]]["jurisdiction"] in ("Hoboken, NJ", "Jersey City, NJ"):
                fails.append(f"T2: Newark address {a} carries {r['team_rule_id']}")
    # T5: no rent cap for Boston / Cambridge.
    for a, rows in res.items():
        if cities.get(a) in ("Boston", "Cambridge"):
            for r in rows:
                rule = runner.by_id[r["team_rule_id"]]
                if rule["category"] == "rent_increase_limits" and not rule.get("negative_finding") \
                        and r["result"] in RENT_CAP_RESULTS:
                    fails.append(f"T5: {a} ({cities[a]}) reports rent cap {r['team_rule_id']} as {r['result']}")
    if changes["T5"]["affected_address_ids"]:
        fails.append("T5: affected set is not empty")
    return fails


# ---------------------------------------------------------------------------
# Diff view
# ---------------------------------------------------------------------------
def diff(runner: Runner, before: str, after: str) -> dict:
    a, b = runner.run(before), runner.run(after)
    out, counts = {}, {}
    for aid in a:
        ra = {r["team_rule_id"]: r for r in a[aid]}
        rb = {r["team_rule_id"]: r for r in b.get(aid, [])}
        rows = []
        for rid in sorted(set(ra) | set(rb)):
            old = ra.get(rid, {}).get("result")
            new = rb.get(rid, {}).get("result")
            if old != new:
                rows.append({"team_rule_id": rid, "title": runner.by_id[rid]["title"], "before": old, "after": new,
                             "explanation_after": rb.get(rid, ra.get(rid, {})).get("explanation")})
                counts[f"{old} -> {new}"] = counts.get(f"{old} -> {new}", 0) + 1
        if rows:
            out[aid] = rows
    return {"before": before, "after": after, "addresses_changed": len(out), "transitions": counts, "changes": out}


# ---------------------------------------------------------------------------
# Score against the independent change key
# ---------------------------------------------------------------------------
def score(changes: dict, detail: dict, runner: Runner) -> str:
    gold = json.loads(GOLD_CHANGES.read_text(encoding="utf-8"))
    lines = ["# Module C evaluation vs gold/changes/T1-T5.json", "",
             f"verifier: {gold.get('verifier')}; as_of default {gold.get('as_of_default')}", "",
             "| Test | Expected affected | Ours | Missing | Extra | Exact | Expected conflicts | Ours | Exact |",
             "|---|---|---|---|---|---|---|---|---|"]
    mismatch_lines = []
    for g in gold["tests"]:
        tid = g["test_id"]
        exp_a, our_a = set(g.get("expected_affected_address_ids", [])), set(changes[tid]["affected_address_ids"])
        exp_c, our_c = set(g.get("conflict_flag_address_ids", [])), set(changes[tid]["conflict_flag_address_ids"])
        lines.append(f"| {tid} | {len(exp_a)} | {len(our_a)} | {len(exp_a - our_a)} | {len(our_a - exp_a)} | "
                     f"{'yes' if exp_a == our_a else 'NO'} | {len(exp_c)} | {len(our_c)} | {'yes' if exp_c == our_c else 'NO'} |")
        for aid in sorted(exp_a - our_a):
            mismatch_lines.append(f"- {tid} missing {aid} ({runner.city_of(aid)}): gold says affected ({g.get('method_note', '')[:90]}); "
                                  f"ours reports no mapped rule for it")
        for aid in sorted(our_a - exp_a):
            why = "; ".join(f"{rid}: {by_date}" for rid, by_date in detail[tid]["transitions_sample"].get(aid, {}).items())
            mismatch_lines.append(f"- {tid} extra {aid} ({runner.city_of(aid)}): ours reports a mapped rule; gold does not list it. {why}")
        for aid in sorted(exp_c - our_c):
            mismatch_lines.append(f"- {tid} conflict missing {aid} ({runner.city_of(aid)})")
        for aid in sorted(our_c - exp_c):
            mismatch_lines.append(f"- {tid} conflict extra {aid} ({runner.city_of(aid)})")
        # expected statuses per date
        exp_status = g.get("expected_status", {})
        for d, want in exp_status.items():
            if not re.match(r"\d{4}-\d{2}-\d{2}", d):
                continue
            want = want.split()[0]
            got = detail[tid]["status_counts"].get(d, {})
            # a 'failed' measure is correctly observed as NOT reported for any address
            ok = (not got) if want == "failed" else (list(got) == [want])
            lines_status = f"| {tid} status on {d} | expected {want} | ours {got or 'not reported (failed measures are never listed)'} |"
            mismatch_lines.append(("OK " if ok else "CHECK ") + lines_status)
    lines += ["", "## Mismatching addresses and status checks", ""] + (mismatch_lines or ["- none"])
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff", action="store_true")
    ap.add_argument("--before"); ap.add_argument("--after")
    args = ap.parse_args()
    runner = Runner()
    OUT.mkdir(parents=True, exist_ok=True)

    if args.diff:
        d = diff(runner, args.before, args.after)
        p = OUT / f"diff_{args.before}_{args.after}.json"
        p.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"diff {args.before} -> {args.after}: {d['addresses_changed']} addresses changed; transitions {d['transitions']} -> {p}")
        return 0

    tests = json.loads(TESTS_JSON.read_text(encoding="utf-8"))
    changes, detail, rule_map = build(runner, tests)
    fails = check_assertions(runner, changes, detail)
    (OUT / "changes.json").write_text(json.dumps(changes, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / "changes_detail.json").write_text(json.dumps(detail, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / "changes_rule_map.json").write_text(json.dumps(rule_map, indent=1), encoding="utf-8")
    report = score(changes, detail, runner)
    (OUT / "changes_eval.md").write_text(report, encoding="utf-8")
    for tid, e in changes.items():
        print(f"{tid}: affected {len(e['affected_address_ids'])}, conflicts {len(e['conflict_flag_address_ids'])}, "
              f"rules {rule_map[tid]}")
    print("assertions:", "all passed" if not fails else fails)
    print(report)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
