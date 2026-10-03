"""
lookup_eval.py - Module B, step 7: score out/lookups.json against a gold address file.

The gold lists, per address, the expected result for each gold rule id
(e.g. CA-ALG-01 -> applies). We map gold ids to our team_rule_ids via the
Module A matches (out/eval_matches.json, built against gold/rules/dev.json),
then by the id's jurisdiction/category prefix plus section numbers quoted in
the gold reasons. gold/rules/test.json and all.json are never read.

Scores (per the judges' description): per-result accuracy, missed "applies"
counted double, our unknown rate, confusion table, top disagreements with the
gold reason text. Writes out/lookup_eval.md (or --out).

Usage:  python lookup_eval.py --gold gold/addresses/seed60.json
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

from common import OUT, sections_match

JUR = {"CA": "CA", "NJ": "NJ", "MA": "MA", "SF": "San Francisco, CA", "LA": "Los Angeles, CA",
       "SD": "San Diego, CA", "BERK": "Berkeley, CA", "SA": "Santa Ana, CA", "JC": "Jersey City, NJ",
       "HOB": "Hoboken, NJ", "NWK": "Newark, NJ", "BOS": "Boston, MA", "CAM": "Cambridge, MA"}
CAT = {"ALG": "algorithmic_rent_setting", "DEP": "security_deposits", "FEE": "application_screening_fees",
       "JUST": "just_cause_eviction", "JC": "just_cause_eviction", "RENT": "rent_increase_limits",
       "SCRN": "screening_restrictions"}
RANK = {"applies": 0, "superseded": 1, "not_yet_effective": 2, "pending": 3, "unknown": 4}


def bucket_of(gold_id: str) -> tuple[str, str] | None:
    m = re.match(r"^([A-Z]+)-([A-Z]+)-", gold_id)
    if not m or m.group(1) not in JUR or m.group(2) not in CAT:
        return None
    return JUR[m.group(1)], CAT[m.group(2)]


def build_mapping(gold: dict, rules: list[dict]) -> tuple[dict, list[str]]:
    """gold_id -> team_rule_id. Dev matches first, then reasons' section numbers, then unique bucket."""
    mapping, notes = {}, []
    matches_path = OUT / "eval_matches.json"
    if matches_path.exists():
        for m in json.loads(matches_path.read_text(encoding="utf-8")):
            mapping[m["gold_id"]] = m["team_rule_id"]
    by_id = {r["team_rule_id"]: r for r in rules}
    reasons = collections.defaultdict(set)
    gold_ids = set()
    for a in gold["addresses"]:
        for e in a["expected"]:
            gold_ids.add(e["gold_id"])
            reasons[e["gold_id"]].add(e.get("reason") or "")
    for gid in sorted(gold_ids):
        if gid in mapping and mapping[gid] in by_id:
            continue
        b = bucket_of(gid)
        if not b:
            notes.append(f"{gid}: unrecognised id pattern")
            continue
        cands = [r for r in rules if (r["jurisdiction"], r["category"]) == b and not r.get("derived")
                 and r["team_rule_id"] not in mapping.values()]
        if not cands:
            cands = [r for r in rules if (r["jurisdiction"], r["category"]) == b and not r.get("derived")]
        # section numbers quoted in the gold reasons ("Civ. Code § 1946.2(i)") pick among candidates
        hit = [r for r in cands if any(sections_match(r["citation"], txt) for txt in reasons[gid] if re.search(r"\d", txt))]
        if len(hit) == 1:
            mapping[gid] = hit[0]["team_rule_id"]; notes.append(f"{gid} -> {hit[0]['team_rule_id']} (section in reason)")
        elif len(cands) == 1:
            mapping[gid] = cands[0]["team_rule_id"]; notes.append(f"{gid} -> {cands[0]['team_rule_id']} (only rule in bucket)")
        elif cands:
            # several of ours, nothing to pick by: take the highest-confidence enacted one
            best = sorted(cands, key=lambda r: (r["status"] not in ("in_force", "not_yet_effective"), -(r.get("confidence") or 0)))[0]
            mapping[gid] = best["team_rule_id"]; notes.append(f"{gid} -> {best['team_rule_id']} (ambiguous bucket of {len(cands)})")
        else:
            notes.append(f"{gid}: no rule of ours in {b}")
    return mapping, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default="gold/addresses/seed60.json")
    ap.add_argument("--lookups", default=str(OUT / "lookups.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    gold = json.loads(Path(args.gold).read_text(encoding="utf-8"))
    lookups = json.loads(Path(args.lookups).read_text(encoding="utf-8"))["lookups"]
    rules = json.loads((OUT / "rules_full.json").read_text(encoding="utf-8"))["rules"]
    by_id = {r["team_rule_id"]: r for r in rules}
    mapping, map_notes = build_mapping(gold, rules)

    rows, confusion = [], collections.Counter()
    total, exact, missed_applies, our_unknown, our_total, not_reported = 0, 0, 0, 0, 0, 0
    for a in gold["addresses"]:
        ours = {r["team_rule_id"]: r for r in lookups.get(a["address_id"], [])}
        our_total += len(ours)
        our_unknown += sum(1 for r in ours.values() if r["result"] == "unknown")
        for e in a["expected"]:
            total += 1
            rid = mapping.get(e["gold_id"])
            mine = ours.get(rid) if rid else None
            got = mine["result"] if mine else "not_reported"
            confusion[(e["result"], got)] += 1
            if got == e["result"]:
                exact += 1
            else:
                if e["result"] == "applies":
                    missed_applies += 1
                if got == "not_reported":
                    not_reported += 1
                rows.append({"address": a["address_id"], "city": a.get("legal_city"), "gold_id": e["gold_id"],
                             "rule": rid, "gold": e["result"], "ours": got,
                             "gold_reason": e.get("reason", ""), "our_reason": (mine or {}).get("explanation", "")})
    weighted_den = total + sum(1 for a in gold["addresses"] for e in a["expected"] if e["result"] == "applies")
    weighted_num = weighted_den - (len(rows) + missed_applies)  # misses count once, missed applies twice

    def pct(x, d):
        return f"{100 * x / d:.1f}%" if d else "n/a"

    lines = [f"# Module B lookup evaluation {args.label}".rstrip(), "",
             f"Gold: `{args.gold}` ({len(gold['addresses'])} addresses, {total} expectations, verifier {gold.get('verifier')})  ",
             f"Ours: `{args.lookups}`", "",
             "| Metric | Value |", "|---|---|",
             f"| Exact result agreement | {exact}/{total} = {pct(exact, total)} |",
             f"| Weighted score (missed 'applies' count double) | {weighted_num}/{weighted_den} = {pct(weighted_num, weighted_den)} |",
             f"| Missed 'applies' (gold applies, ours not) | {missed_applies} |",
             f"| Expectations we did not report at all | {not_reported} |",
             f"| Our unknown rate (these addresses) | {our_unknown}/{our_total} = {pct(our_unknown, our_total)} |",
             "", "## Confusion (gold → ours)", "", "| gold \\ ours | " + " | ".join(RANK) + " | not_reported |", "|---|" + "---|" * (len(RANK) + 1)]
    for g in RANK:
        lines.append(f"| {g} | " + " | ".join(str(confusion[(g, o)]) for o in RANK) + f" | {confusion[(g, 'not_reported')]} |")
    per_type = collections.Counter((r["gold"], r["ours"]) for r in rows)
    lines += ["", "## Disagreement types", ""] + [f"- gold {g} → ours {o}: {n}" for (g, o), n in per_type.most_common()]
    lines += ["", "## Top disagreements (gold reason vs ours)", "",
              "| Address | Gold id | Gold | Ours | Gold reason | Our explanation |", "|---|---|---|---|---|---|"]
    rows.sort(key=lambda r: (r["gold"] != "applies", r["gold_id"]))
    for r in rows[:10]:
        lines.append(f"| {r['address']} ({r['city']}) | {r['gold_id']} → {r['rule']} | {r['gold']} | {r['ours']} | "
                     f"{r['gold_reason'][:110].replace('|', '/')} | {r['our_reason'][:110].replace('|', '/')} |")
    # Every "gold unknown -> ours applies" row in full: these are the risky new assertions.
    risky = [r for r in rows if r["gold"] == "unknown" and r["ours"] == "applies"]
    lines += ["", f"## All gold unknown → ours applies ({len(risky)})", "",
              "| Address | Gold id | Gold reason | Our explanation |", "|---|---|---|---|"]
    lines += [f"| {r['address']} ({r['city']}) | {r['gold_id']} → {r['rule']} | {r['gold_reason'][:120].replace('|', '/')} | "
              f"{r['our_reason'][:140].replace('|', '/')} |" for r in risky]
    # Whole-sample statistics from the lookups file itself.
    all_rows = [r for v in lookups.values() for r in v]
    n_unk = sum(1 for r in all_rows if r["result"] == "unknown")
    n_ass = sum(1 for r in all_rows if r.get("assumptions"))
    lines += ["", "## Whole sample", "",
              f"- addresses: {len(lookups)}; rows: {len(all_rows)}; unknown rate: {n_unk}/{len(all_rows)} = {pct(n_unk, len(all_rows))}",
              f"- rows relying on a presumption (`assumptions` non-empty): {n_ass}"]
    lines += ["", "## Gold id → our rule mapping notes", ""] + [f"- {n}" for n in map_notes]
    out = Path(args.out) if args.out else OUT / "lookup_eval.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[: 12 + len(RANK) + 4]))
    print(f"\nfull report: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
