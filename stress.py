"""
stress.py - pre-submission stress test (instructions/stress_test.md). Measure only: nothing in
out/ is changed; everything is written under out/stress/.

  python stress.py keys      # build the six alternative keys with engine policy switches
  python stress.py matrix    # agreement of the current submission against each key + decision table
  python stress.py format    # submission format check (schema, ids, allowed values, template shapes)
  python stress.py report    # assemble out/stress/REPORT.md from the pieces (tests + repro results included if present)
"""

from __future__ import annotations

import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from common import OUT, ROOT, SCHEMA_JSON, STARTER

STRESS = OUT / "stress"
KEYS = {
    "K_strict": ["--strict-unknown"],
    "K_lenient": ["--lenient-plausible"],
    "K_cutoff": ["--cutoff-year-applies"],
    "K_derivedunits": ["--use-derived-units"],
    "K_noprecedence": ["--no-precedence"],
    "K_omit": ["--report-not-covered"],
}
RESULTS = ["applies", "unknown", "superseded", "not_yet_effective", "pending"]


def load_lookups(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["lookups"]


def rows_of(lk: dict) -> dict:
    return {(a, r["team_rule_id"]): r["result"] for a, rows in lk.items() for r in rows}


# ---------------------------------------------------------------------------
def build_keys() -> None:
    STRESS.mkdir(parents=True, exist_ok=True)
    for name, flags in KEYS.items():
        d = STRESS / name
        d.mkdir(exist_ok=True)
        out = subprocess.run([sys.executable, "engine.py", *flags, "--out", str(d / "lookups.json")],
                             cwd=ROOT, capture_output=True, text=True)
        (d / "engine_stdout.txt").write_text(out.stdout + out.stderr, encoding="utf-8")
        print(name, flags, "->", out.stdout.strip().split("\n")[0][:160])


def compare(ours: dict, key: dict, rules: dict, juris: dict) -> dict:
    """Agreement of OUR rows against a key: a row present in only one side is a mismatch."""
    a, b = rows_of(ours), rows_of(key)
    keys = set(a) | set(b)
    exact = sum(1 for k in keys if a.get(k) == b.get(k))
    missed_applies = sum(1 for k in keys if b.get(k) == "applies" and a.get(k) != "applies")
    extra_applies = sum(1 for k in keys if a.get(k) == "applies" and b.get(k) != "applies")
    swaps = sum(1 for k in keys if {a.get(k), b.get(k)} == {"applies", "unknown"})
    weighted_den = len(keys) + sum(1 for k in keys if b.get(k) == "applies")
    weighted_num = weighted_den - (len(keys) - exact) - missed_applies
    per_cat, per_city = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0])
    diffs = []
    for k in keys:
        cat = rules.get(k[1], {}).get("category", "?")
        city = juris.get(k[0], {}).get("city") or juris.get(k[0], {}).get("state") or "?"
        same = a.get(k) == b.get(k)
        per_cat[cat][1] += 1; per_city[city][1] += 1
        if same:
            per_cat[cat][0] += 1; per_city[city][0] += 1
        else:
            diffs.append({"address_id": k[0], "team_rule_id": k[1], "ours": a.get(k), "key": b.get(k)})
    return {"total": len(keys), "exact": exact, "exact_pct": round(100 * exact / len(keys), 1),
            "weighted_pct": round(100 * weighted_num / weighted_den, 1), "missed_applies": missed_applies,
            "extra_applies": extra_applies, "unknown_applies_swaps": swaps,
            "per_category": {c: f"{v[0]}/{v[1]}" for c, v in sorted(per_cat.items())},
            "per_city": {c: f"{v[0]}/{v[1]}" for c, v in sorted(per_city.items())}, "diffs": diffs}


def matrix() -> None:
    rules = {r["team_rule_id"]: r for r in json.loads((OUT / "rules_full.json").read_text(encoding="utf-8"))["rules"]}
    juris = json.loads((OUT / "jurisdictions.json").read_text(encoding="utf-8"))
    current = load_lookups(OUT / "lookups.json")
    keys = {k: load_lookups(STRESS / k / "lookups.json") for k in KEYS}
    lines = ["## 1. Policy sensitivity: current submission vs alternative keys", "",
             "| Key | Rows (union) | Exact | Exact % | Weighted % | Missed applies | Extra applies | Unknown/applies swaps |",
             "|---|---|---|---|---|---|---|---|"]
    detail = {}
    for k, lk in keys.items():
        c = compare(current, lk, rules, juris)
        detail[k] = c
        lines.append(f"| {k} | {c['total']} | {c['exact']} | {c['exact_pct']} | {c['weighted_pct']} | {c['missed_applies']} | "
                     f"{c['extra_applies']} | {c['unknown_applies_swaps']} |")
        with open(STRESS / k / "diff_vs_current.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["address_id", "team_rule_id", "ours", "key"]); w.writeheader(); w.writerows(c["diffs"])
    lines += ["", "Per category (exact/rows) and per city, by key:", ""]
    for k, c in detail.items():
        lines.append(f"- **{k}**: " + "; ".join(f"{cat} {v}" for cat, v in c["per_category"].items()))
        lines.append(f"  cities: " + "; ".join(f"{city} {v}" for city, v in c["per_city"].items()))
    # Decision table: candidate submission policies vs every key (minimax)
    policies = {"current": current, "strict": keys["K_strict"], "lenient": keys["K_lenient"]}
    all_keys = {"current": current, **keys}
    lines += ["", "## Decision table: candidate policy P scored against each key K (exact %, weighted % in brackets)", "",
              "| P \\ K | " + " | ".join(all_keys) + " | worst exact | mean exact | worst weighted | mean weighted |",
              "|---|" + "---|" * (len(all_keys) + 4)]
    for p, plk in policies.items():
        cells, ex, wt = [], [], []
        for k, klk in all_keys.items():
            c = compare(plk, klk, rules, juris)
            cells.append(f"{c['exact_pct']} ({c['weighted_pct']})"); ex.append(c["exact_pct"]); wt.append(c["weighted_pct"])
        lines.append(f"| {p} | " + " | ".join(cells) + f" | {min(ex)} | {round(sum(ex) / len(ex), 1)} | {min(wt)} | {round(sum(wt) / len(wt), 1)} |")
    lines += ["", "No recommendation is made here; the policy choice is the reviewer's."]
    (STRESS / "matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


# ---------------------------------------------------------------------------
def format_check() -> None:
    lines = ["## 3. Submission format check", ""]
    ok_all = True
    schema = json.loads(SCHEMA_JSON.read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    rules = json.loads((OUT / "rules.json").read_text(encoding="utf-8"))
    errs = [(r.get("team_rule_id"), e.message) for r in rules["rules"] for e in v.iter_errors(r)]
    lines.append(f"- rules.json: {len(rules['rules'])} records, schema errors: {len(errs)}" + (f" {errs[:5]}" if errs else ""))
    ok_all &= not errs
    ids = {r["team_rule_id"] for r in rules["rules"]}
    lines.append(f"- rules.json: duplicate team_rule_ids: {len(rules['rules']) - len(ids)}")
    with open(STARTER / "data" / "sample_addresses.csv", newline="", encoding="utf-8") as f:
        sample = {row["address_id"] for row in csv.DictReader(f)}
    lk = json.loads((OUT / "lookups.json").read_text(encoding="utf-8"))
    bad_results = [(a, r["team_rule_id"], r["result"]) for a, rows in lk["lookups"].items() for r in rows if r["result"] not in RESULTS]
    unknown_rules = [(a, r["team_rule_id"]) for a, rows in lk["lookups"].items() for r in rows if r["team_rule_id"] not in ids]
    lines.append(f"- lookups.json: as_of={lk.get('as_of')!r}; addresses {len(lk['lookups'])} (sample {len(sample)}; "
                 f"missing {len(sample - set(lk['lookups']))}, extra {len(set(lk['lookups']) - sample)}); "
                 f"invalid result values {len(bad_results)}; rows citing unknown rules {len(unknown_rules)}")
    ok_all &= lk.get("as_of") == "2026-10-01" and sample == set(lk["lookups"]) and not bad_results and not unknown_rules
    ch = json.loads((OUT / "changes.json").read_text(encoding="utf-8"))
    tests = sorted(ch)
    shape_ok = all(set(("affected_address_ids", "conflict_flag_address_ids", "notes")) <= set(ch[t]) for t in tests)
    bad_ids = [(t, a) for t in tests for a in ch[t]["affected_address_ids"] + ch[t]["conflict_flag_address_ids"] if a not in sample]
    lines.append(f"- changes.json: tests {tests}; required keys present: {shape_ok}; address ids not in sample: {len(bad_ids)}")
    ok_all &= tests == ["T1", "T2", "T3", "T4", "T5"] and shape_ok and not bad_ids
    # template shapes
    tdir = STARTER / "submission_templates"
    t_rules = json.loads((tdir / "rules.json").read_text(encoding="utf-8"))["rules"][0]
    missing_keys = set(t_rules) - set(rules["rules"][0])
    lines.append(f"- template rules.json keys missing from ours: {sorted(missing_keys) or 'none'}; "
                 f"extra keys in ours (allowed, schema has no additionalProperties): {sorted(set(rules['rules'][0]) - set(t_rules))}")
    t_lk = json.loads((tdir / "lookups.json").read_text(encoding="utf-8"))
    first_row = next(iter(lk["lookups"].values()))[0]
    t_row = next(iter(t_lk["lookups"].values()))[0]
    lines.append(f"- template lookups.json: top-level keys {sorted(t_lk)} vs ours {sorted(lk)}; row keys missing: "
                 f"{sorted(set(t_row) - set(first_row)) or 'none'}; extra row keys: {sorted(set(first_row) - set(t_row))}")
    t_ch = json.loads((tdir / "changes.json").read_text(encoding="utf-8"))
    lines.append(f"- template changes.json entry keys {sorted(next(iter(t_ch.values())))} vs ours {sorted(ch['T1'])}")
    lines.append(f"\n**Format check: {'PASS' if ok_all else 'FAIL'}**")
    (STRESS / "format_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


# ---------------------------------------------------------------------------
def report() -> None:
    parts = ["# Stress test report (pre-submission)", "",
             f"Code state: {subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip()}. "
             "Measure only: no engine policy or submission file was changed in this step; alternative keys were built with "
             "opt-in engine switches into out/stress/.", ""]
    for name in ("matrix.md", "tests.md", "format_check.md", "repro.md"):
        p = STRESS / name
        if p.exists():
            parts.append(p.read_text(encoding="utf-8"))
        else:
            parts.append(f"## {name}: not available\n")
    (STRESS / "REPORT.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"-> {STRESS / 'REPORT.md'}")


if __name__ == "__main__":
    {"keys": build_keys, "matrix": matrix, "format": format_check, "report": report}[sys.argv[1]]()
