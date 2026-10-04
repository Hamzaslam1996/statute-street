"""
scale/run.py - the unchanged pipeline on real open-data addresses (instructions/scale.md sections 2 and 3).

Steps
-----
1. Geocode scale/data/<city>.csv with the Census batch geocoder, then look up the incorporated place of
   each matched point (the same code path as resolve.py, separate cache out/scale/geocode_<city>.csv).
2. Run the unchanged engine (engine.evaluate_address) at 2026-10-01 and 2027-07-02 and write
   out/scale/lookups_<city>.json.
3. Summaries per city (addresses, legal city match rate, result distribution, top missing facts, runtime),
   sanity checks (pass/fail, never tuned), and a throughput benchmark at 10,000 and 100,000 determinations.

Writes out/scale/summary.json and out/scale/summary.md. No model calls; the only network use is the
Census Geocoder (free, no key).

Usage:  .venv/bin/python scale/run.py [--city sf boston cambridge] [--skip-geocode]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import engine                       # noqa: E402
import resolve                      # noqa: E402  (batch_geocode, place_for_point, legal_city, POSTAL_TO_LEGAL)

DATA = ROOT / "scale" / "data"
OUT = ROOT / "out" / "scale"
DATES = ["2026-10-01", "2027-07-02"]
CITY_NAME = {"sf": "San Francisco", "boston": "Boston", "cambridge": "Cambridge"}


def load_city(slug: str) -> list[dict]:
    with open(DATA / f"{slug}.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ----------------------------------------------------------------------------- geocoding
def geocode(slug: str, addresses: list[dict], skip: bool) -> dict[str, dict]:
    cache_path = OUT / f"geocode_{slug}.csv"
    cache = {}
    if cache_path.exists():
        with open(cache_path, newline="", encoding="utf-8") as f:
            cache = {r["address_id"]: r for r in csv.DictReader(f)}
    todo = [a for a in addresses if a["address_id"] not in cache]
    if todo and not skip:
        print(f"  {slug}: geocoding {len(todo)} addresses in batches of 1000 ...")
        for i in range(0, len(todo), 1000):
            chunk = todo[i:i + 1000]
            got = resolve.batch_geocode(chunk)
            for a in chunk:
                cache[a["address_id"]] = got.get(a["address_id"], {"address_id": a["address_id"], "match": "No_Match"})
            save(cache_path, cache)
        matched = [r for r in cache.values() if r.get("match") == "Match" and not r.get("place")]
        print(f"  {slug}: incorporated place for {len(matched)} points ...")
        with ThreadPoolExecutor(max_workers=6) as ex:
            for rec, place in zip(matched, ex.map(lambda r: resolve.place_for_point(r["lon"], r["lat"]), matched)):
                rec["place"] = place
                rec["method"] = "census" if place and place != "ERROR" else "census_no_place"
        save(cache_path, cache)
    return cache


def save(path: Path, cache: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=resolve.GEO_FIELDS)
        w.writeheader()
        for r in cache.values():
            w.writerow({k: r.get(k, "") for k in resolve.GEO_FIELDS})


def jurisdictions(addresses: list[dict], cache: dict) -> dict[str, dict]:
    """Same decision as resolve.main: Census place -> legal city; documented postal fallback; else unresolved."""
    juris = {}
    for a in addresses:
        rec = cache.get(a["address_id"], {})
        state = resolve.STATE_FIPS.get(rec.get("state_fips", ""), a["state"])
        place = rec.get("place", "")
        if rec.get("match") == "Match" and place and place != "ERROR":
            city, method, conf = resolve.legal_city(place), "census", "high"
        else:
            fb = resolve.POSTAL_TO_LEGAL.get(a["state"], {}).get(a["postal_city"])
            city, method, conf = (fb, "fallback", "fallback") if fb else (None, "unresolved", "none")
        juris[a["address_id"]] = {"state": state, "county_fips": rec.get("county_fips", ""), "city": city,
                                  "postal_city": a["postal_city"], "method": method, "confidence": conf,
                                  "matched_address": rec.get("matched_address", "")}
    return juris


# ----------------------------------------------------------------------------- engine + summaries
def missing_fact(explanation: str) -> str | None:
    m = re.match(r"Unknown: needs ([^.]+)\.", explanation or "")
    return m.group(1).strip() if m else ("exemption status" if (explanation or "").startswith("Unknown:") else None)


def run_city(slug: str, addresses: list[dict], juris: dict, rules, coverage) -> tuple[dict, dict]:
    by_id = {r["team_rule_id"]: r for r in rules}
    lookups = {d: {} for d in DATES}
    t0 = time.time()
    for a in addresses:
        facts = engine.address_facts(a, juris[a["address_id"]])
        for d in DATES:
            lookups[d][a["address_id"]] = engine.evaluate_address(facts, rules, coverage, date.fromisoformat(d))
    runtime = time.time() - t0

    dist = {d: collections.Counter() for d in DATES}
    facts_missing = collections.Counter()
    n_rows = 0
    for d in DATES:
        for rows in lookups[d].values():
            for r in rows:
                n_rows += 1
                key = "applies unless" if r["result"] == "applies" and r.get("assumptions") else r["result"]
                dist[d][key] += 1
                if r["result"] == "unknown":
                    facts_missing[missing_fact(r["explanation"]) or "other"] += 1
    portal_city = CITY_NAME[slug]
    geocoded_same = sum(1 for a in addresses if juris[a["address_id"]]["city"] == portal_city)
    by_method = collections.Counter(juris[a["address_id"]]["method"] for a in addresses)
    legal_cities = collections.Counter(juris[a["address_id"]]["city"] or "unresolved" for a in addresses)

    # Sanity checks (report, never tune)
    checks = {}
    rent_titles = {rid: by_id[rid]["title"] for rid in by_id if by_id[rid]["category"] == "rent_increase_limits"}
    if slug in ("boston", "cambridge"):
        bad = [(aid, r["team_rule_id"]) for aid, rows in lookups[DATES[0]].items() for r in rows
               if by_id[r["team_rule_id"]]["category"] == "rent_increase_limits" and r["result"] == "applies"]
        checks["no_rent_cap_in_ma_city"] = {"pass": not bad, "violations": len(bad), "sample": bad[:5]}
    if slug == "sf":
        sf_rent = [rid for rid, t in rent_titles.items() if "San Francisco" in t and "allowable" in t]
        rid = sf_rent[0] if sf_rent else None
        old = [a for a in addresses if a["year_built"] and int(a["year_built"]) < 1979 and a["units"] and int(a["units"]) >= 2
               and juris[a["address_id"]]["city"] == "San Francisco"]
        bad = [a["address_id"] for a in old if not any(r["team_rule_id"] == rid and r["result"] == "applies"
                                                     for r in lookups[DATES[0]][a["address_id"]])]
        checks["sf_pre_1979_multiunit_rent_control_applies"] = {"pass": not bad, "checked": len(old), "violations": len(bad), "sample": bad[:5], "rule": rid}
        cut = [a for a in addresses if a["year_built"] == "1979" and juris[a["address_id"]]["city"] == "San Francisco"]
        bad = [a["address_id"] for a in cut if not any(r["team_rule_id"] == rid and r["result"] == "unknown"
                                                     for r in lookups[DATES[0]][a["address_id"]])]
        checks["sf_cutoff_year_1979_unknown"] = {"pass": not bad, "checked": len(cut), "violations": len(bad), "sample": bad[:5]}
        if not cut:
            # no 1979 parcel among the downloaded rows: check the rule on a synthetic 1979 row instead
            syn = {"address_id": "SYN1979", "street_address": "1 Test St", "postal_city": "San Francisco", "state": "CA", "zip": "",
                   "year_built": "1979", "units": "6", "use_code": "F5", "use_description": "Flats 5 to 14 units"}
            res = engine.evaluate_address(engine.address_facts(syn, {"state": "CA", "city": "San Francisco", "method": "census"}),
                                          rules, coverage, date.fromisoformat(DATES[0]))
            got = next((r["result"] for r in res if r["team_rule_id"] == rid), None)
            checks["sf_cutoff_year_1979_unknown"].update({"synthetic_1979_row": got, "pass": got == "unknown"})
    unknown_ids = {r["team_rule_id"] for d in DATES for rows in lookups[d].values() for r in rows} - set(by_id)
    checks["every_row_cites_existing_rule"] = {"pass": not unknown_ids, "violations": sorted(unknown_ids)}

    summary = {"city": portal_city, "addresses": len(addresses), "determinations": n_rows,
               "legal_city_match_rate": round(geocoded_same / len(addresses), 4) if addresses else None,
               "legal_city_counts": dict(legal_cities.most_common(8)), "geocode_method": dict(by_method),
               "year_built_present": sum(1 for a in addresses if a["year_built"]),
               "units_present": sum(1 for a in addresses if a["units"]),
               "result_distribution": {d: dict(dist[d]) for d in DATES},
               "top_missing_facts": facts_missing.most_common(5),
               "engine_seconds_both_dates": round(runtime, 2),
               "addresses_per_second": round(len(addresses) * len(DATES) / runtime, 1) if runtime else None,
               "sanity_checks": checks}
    return lookups, summary


def throughput(addresses: list[dict], juris: dict, rules, coverage) -> dict:
    """Time the engine at 10,000 and 100,000 determinations by cycling the addresses across as-of dates."""
    dates = [date(2026, 10, 1), date(2027, 7, 2), date(2026, 1, 2), date(2025, 12, 31), date(2026, 6, 1)]
    facts = [engine.address_facts(a, juris[a["address_id"]]) for a in addresses]
    out = {}
    for target in (10_000, 100_000):
        n_det = n_addr = 0
        i = 0
        t0 = time.time()
        while n_det < target:
            f = facts[i % len(facts)]
            n_det += len(engine.evaluate_address(f, rules, coverage, dates[(i // len(facts)) % len(dates)]))
            n_addr += 1
            i += 1
        dt = time.time() - t0
        out[str(target)] = {"determinations": n_det, "address_evaluations": n_addr, "seconds": round(dt, 2),
                            "addresses_per_second": round(n_addr / dt, 1), "determinations_per_second": round(n_det / dt, 1)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", nargs="*", default=["sf", "boston", "cambridge"])
    ap.add_argument("--skip-geocode", action="store_true", help="use the geocode cache only")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rules, coverage, _, _ = engine.load_inputs()
    engine.attach_phrases(coverage)

    summaries, all_addr, all_juris = {}, [], {}
    for slug in args.city:
        if not (DATA / f"{slug}.csv").exists():
            print(f"{slug}: no data file, skipped"); continue
        addresses = load_city(slug)
        t0 = time.time()
        cache = geocode(slug, addresses, args.skip_geocode)
        geo_seconds = time.time() - t0
        juris = jurisdictions(addresses, cache)
        lookups, summary = run_city(slug, addresses, juris, rules, coverage)
        prev = (json.loads((OUT / "summary.json").read_text()).get("cities", {}).get(slug, {}) if (OUT / "summary.json").exists() else {})
        summary["geocode_seconds"] = prev.get("geocode_seconds") if args.skip_geocode and prev.get("geocode_seconds") else round(geo_seconds, 1)
        (OUT / f"lookups_{slug}.json").write_text(json.dumps({"as_of": DATES, "lookups": lookups}, indent=0), encoding="utf-8")
        (OUT / f"jurisdictions_{slug}.json").write_text(json.dumps(juris, indent=0), encoding="utf-8")
        summaries[slug] = summary
        all_addr += addresses; all_juris.update(juris)
        print(f"{slug}: {summary['addresses']} addresses, match rate {summary['legal_city_match_rate']}, "
              f"{summary['determinations']} determinations in {summary['engine_seconds_both_dates']}s; "
              f"checks: {[(k, v['pass']) for k, v in summary['sanity_checks'].items()]}")
    bench = throughput(all_addr, all_juris, rules, coverage) if all_addr else {}
    print("throughput:", bench)
    result = {"cities": summaries, "throughput": bench, "dates": DATES}
    (OUT / "summary.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
