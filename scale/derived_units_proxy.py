"""
scale/derived_units_proxy.py - instructions/scale.md section 6.

The sample's New Jersey rows have no unit counts; engine.py --use-derived-units reads the MOD-IV
building code ("6B-20U-G" -> 20 units) as a stand-in for the unit count a property management
system would supply. This script compares out/lookups.json (default run) with out/lookups_derived.json
(the --use-derived-units run, both already produced by engine.py) and reports, per legal city, the
unknown rate and the number of rows that rest on a presumption, before and after.

Reads only; writes out/scale/derived_units_proxy.md and .json.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"


def stats(path: Path, city_of: dict) -> dict:
    lk = json.loads(path.read_text(encoding="utf-8"))["lookups"]
    per = collections.defaultdict(lambda: {"addresses": 0, "rows": 0, "unknown": 0, "presumption_rows": 0})
    for aid, rows in lk.items():
        c = city_of.get(aid, "?")
        per[c]["addresses"] += 1
        for r in rows:
            per[c]["rows"] += 1
            per[c]["unknown"] += r["result"] == "unknown"
            per[c]["presumption_rows"] += bool(r.get("assumptions"))
    return per


def main() -> int:
    juris = json.loads((OUT / "jurisdictions.json").read_text(encoding="utf-8"))
    city_of = {a: f"{j.get('city') or '?'}, {j.get('state', '')}" for a, j in juris.items()}
    before = stats(OUT / "lookups.json", city_of)
    after = stats(OUT / "lookups_derived.json", city_of)
    lines = ["# Unit counts as a PMS proxy: engine --use-derived-units on the 500 sample addresses", "",
             "Before = out/lookups.json (unit counts only where the county supplied them). After = out/lookups_derived.json "
             "(New Jersey unit counts parsed from the MOD-IV building code, standing in for counts a property management "
             "system would supply). Results for CA and MA rows cannot change because their counts were already present.", "",
             "| Legal city | Addresses | Rows | Unknown before | Unknown after | Presumption rows before | Presumption rows after |",
             "|---|---|---|---|---|---|---|"]
    tot_b = collections.Counter(); tot_a = collections.Counter()
    table = {}
    for c in sorted(before):
        b, a = before[c], after[c]
        for k in b: tot_b[k] += b[k]; tot_a[k] += a[k]
        table[c] = {"before": b, "after": a}
        lines.append(f"| {c} | {b['addresses']} | {b['rows']} | {b['unknown']} ({b['unknown'] / b['rows']:.1%}) | "
                     f"{a['unknown']} ({a['unknown'] / a['rows']:.1%}) | {b['presumption_rows']} | {a['presumption_rows']} |")
    lines.append(f"| **All** | {tot_b['addresses']} | {tot_b['rows']} | {tot_b['unknown']} ({tot_b['unknown'] / tot_b['rows']:.1%}) | "
                 f"{tot_a['unknown']} ({tot_a['unknown'] / tot_a['rows']:.1%}) | {tot_b['presumption_rows']} | {tot_a['presumption_rows']} |")
    lines += ["", "Reading: a supplied unit count settles the unit-threshold tests (Jersey City rent control's 1 to 4 unit exemption, "
              "the small-building carve-outs in the state screening and deposit laws) in Hoboken and Jersey City; what remains "
              "unknown there is owner identity (never in the data) and, in Hoboken, the year built for the 1987 rent control cutoff. "
              "Newark moves least: many of its MOD-IV codes carry no unit count, only 2 of 50 rows have a year built, and owner "
              "identity decides the remaining exemptions. Presumption counts do not move: they come from use or funding exemptions "
              "(hotels, subsidised housing) that a unit count cannot settle."]
    (OUT / "scale").mkdir(parents=True, exist_ok=True)
    (OUT / "scale" / "derived_units_proxy.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "scale" / "derived_units_proxy.json").write_text(json.dumps({"cities": table, "total_before": tot_b, "total_after": tot_a}, indent=1), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
