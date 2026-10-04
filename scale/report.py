"""
scale/report.py - assemble out/scale/REPORT.md from summary.json, cost.json, derived_units_proxy.md and
scale/data/provenance.json (instructions/scale.md section 5). Reads only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "scale"


def main() -> int:
    s = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    c = json.loads((OUT / "cost.json").read_text(encoding="utf-8"))
    prov = json.loads((ROOT / "scale" / "data" / "provenance.json").read_text(encoding="utf-8"))
    proxy = (OUT / "derived_units_proxy.md").read_text(encoding="utf-8")
    L = ["# Scale report: real addresses, throughput, cost of adding law", "",
         "Produced by scale/fetch.py, scale/run.py, scale/cost.py and scale/derived_units_proxy.py. No Claude API calls. "
         "The engine, rules and coverage tests are the submitted ones, unchanged; nothing in out/*.json, submission/ or the UI "
         "repository was touched.", "",
         "## 1. Real addresses from official open data", "",
         "| City | Dataset | Endpoint | Filter | Rows | Retrieved | sha256 (scale/data) | Licence |", "|---|---|---|---|---|---|---|---|"]
    for slug, p in prov.items():
        if p.get("skipped"):
            L.append(f"| {p['city']} | skipped: {p['skipped']} | | | | | | |"); continue
        L.append(f"| {p['city']} | {p['dataset']} | {p['endpoint']} | {p['filter']} | {p['rows']} | {p['retrieved_at']} | "
                 f"{p['sha256'][:16]}… | {p['licence']} |")
    L += ["", "Privacy: owner names, mailing addresses and every other person field were excluded from the API selection and never "
          "written to disk (see `owner_fields_in_source` in scale/data/provenance.json). Kept: address, ZIP, year built, units, "
          "use description, record id and record URL.", "",
          "## 2. Same pipeline, unchanged", ""]
    for slug, m in s["cities"].items():
        d0, d1 = s["dates"]
        L += [f"### {m['city']}", "",
              f"- Addresses: {m['addresses']}; year built present {m['year_built_present']}, units present {m['units_present']}",
              f"- Legal city match rate (geocoded incorporated place = portal city): {m['legal_city_match_rate']:.1%}; "
              f"geocode method {m['geocode_method']}; legal cities seen {m['legal_city_counts']}",
              f"- Determinations: {m['determinations']} over two dates; engine time {m['engine_seconds_both_dates']}s "
              f"({m['addresses_per_second']} address evaluations per second); geocoding {m.get('geocode_seconds')}s",
              f"- Result distribution {d0}: {m['result_distribution'][d0]}",
              f"- Result distribution {d1}: {m['result_distribution'][d1]}",
              f"- Top missing facts: {m['top_missing_facts']}",
              "- Sanity checks:"]
        for k, v in m["sanity_checks"].items():
            L.append(f"  - {k}: {'PASS' if v['pass'] else 'FAIL'} ({ {kk: vv for kk, vv in v.items() if kk != 'pass'} })")
        L.append("")
    L += ["Geocoding, not the engine, was the slow step: the free Census batch geocoder plus one incorporated-place lookup per point "
          "took 6.4 minutes for San Francisco, 2.1 hours for Boston and 4.1 hours for Cambridge (server-side queueing on 4 Oct 2026). "
          "In production the legal city would come from a cached or commercial geocoder, or from the property record itself.", "",
          "San Francisco's sanity check on the 1979 cutoff year had no 1979 parcel among the downloaded rows, so it was run on a "
          "synthetic 1979 row (result: unknown, as required).", "",
          "Two wording follow-ups noticed while reading these rows (results are right, the sentence is not; nothing changed, flagged "
          "for Hamza): (a) a cutoff-year building (built 1978 in Los Angeles, 10 rows in the sample) reads 'Unknown: needs year built' "
          "although the year is known; it should read 'built 1978, the cutoff year; year built is not the certificate date'. (b) A "
          "small building under an owner-occupied exemption with on_fail unknown (SF r-0018 with 2 units, 600 rows here; r-0025 and "
          "r-0049 in the sample) reads 'needs the exemption details ... whether the exemption has ended', which is the wording for "
          "expiring new-construction exemptions, not owner-occupancy.", "",
          "## 3. Throughput benchmark", "", "| Target determinations | Address evaluations | Seconds | Addresses per second | Determinations per second |",
          "|---|---|---|---|---|"]
    for t, b in s["throughput"].items():
        L.append(f"| {int(t):,} | {b['address_evaluations']:,} | {b['seconds']} | {b['addresses_per_second']:,} | {b['determinations_per_second']:,} |")
    L += ["", "Measured on this laptop, single process, pure Python; the engine is a deterministic join of address facts and rules, "
          "so it needs no model call per address.", "",
          "## 4. Cost of adding law", "",
          f"- Documents extracted: {c['documents_extracted']} ({c['extraction_calls']} calls, {c['raw_records']} raw records, "
          f"{c['kept_rules']} kept rules)",
          f"- Extraction model cost: ${c['extraction_cost_usd']} total, ${c['cost_per_document_usd']} per document, "
          f"{c['seconds_per_document']}s wall time per document",
          f"- Spanish summaries: ${c['spanish_cost_usd']}; model-confirmed date decisions: {c['date_decisions_model_confirmed']}; "
          f"coverage test calls: {c['coverage_model_calls']} (one per rule)",
          f"- Model cost per kept rule (extraction plus Spanish): ${c['model_cost_per_kept_rule_usd']}",
          f"- Human review: {c['human_rulings_in_instructions']} numbered rulings in instructions/; reviewer overrides "
          f"{c['reviewer_overrides']}; {c['rules_touched_by_a_reviewer_override']} of {c['kept_rules']} kept rules carry a reviewer "
          f"override ({c['share_of_rules_with_a_human_ruling']:.0%}); gold key adjudications by the lawyer: "
          f"{c['gold_adjudications_by_lawyer']} ({c['gold_adjudications_individual']} individually decided)",
          f"- {c['note']}", "", f"**{c['sentence']}**", "",
          "## 5. Architecture in three sentences", "",
          "Rules are compiled once per jurisdiction: a document is read by the model once, verified against its own text, and turned "
          "into coverage tests that are cached. Determinations are a deterministic join of address facts and rules, so more addresses "
          "cost no model calls; the engine above handled real city rolls at thousands of addresses per second. Refresh is event driven, "
          "when the change register posts a new effective date, not per query.", "",
          "## 6. Unit counts as a PMS proxy (the 500 sample addresses)", ""]
    L += proxy.split("\n", 2)[2].split("\n")
    (OUT / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"-> {OUT / 'REPORT.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
