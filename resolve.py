"""
resolve.py - Module B, step 1: the LEGAL jurisdiction of each sample address.

Plain-language summary
----------------------
The sample file gives a postal city ("Dorchester", "Van Nuys") which is not
always the legal city (Boston, Los Angeles). We send all 500 addresses to the
U.S. Census Geocoder in one batch (free, no key) to get coordinates, state and
county, then ask the geocoder which incorporated place each point falls in.
Results are cached in out/geocode.csv so re-runs cost nothing. Where the
geocoder cannot match an address we fall back to a small, documented table of
postal names -> legal city and say so (method "fallback"); we never guess
silently.

Output: out/jurisdictions.json  { address_id: {state, county, city, method, confidence} }

Usage:  python resolve.py            (uses the cache)
        python resolve.py --force    (re-geocode everything)
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from common import OUT, STARTER

ADDRESSES_CSV = STARTER / "data" / "sample_addresses.csv"
GEOCODE_CSV = OUT / "geocode.csv"
JURIS_JSON = OUT / "jurisdictions.json"

BATCH_URL = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch"
POINT_URL = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
BENCHMARK, VINTAGE = "Public_AR_Current", "Current_Current"

# Postal names that are neighbourhoods of a legal city in our sample. Used only when
# the geocoder gives no answer, and always marked method="fallback".
POSTAL_TO_LEGAL = {
    "MA": {"Dorchester": "Boston", "Roxbury": "Boston", "East Boston": "Boston", "Brighton": "Boston",
           "Allston": "Boston", "South Boston": "Boston", "Jamaica Plain": "Boston", "Hyde Park": "Boston",
           "Mattapan": "Boston", "Charlestown": "Boston", "Roslindale": "Boston", "West Roxbury": "Boston",
           "Boston": "Boston", "Cambridge": "Cambridge"},
    "CA": {"Van Nuys": "Los Angeles", "North Hollywood": "Los Angeles", "Hollywood": "Los Angeles",
           "Sherman Oaks": "Los Angeles", "Encino": "Los Angeles", "Tujunga": "Los Angeles",
           "Sylmar": "Los Angeles", "Reseda": "Los Angeles", "Canoga Park": "Los Angeles",
           "San Pedro": "Los Angeles", "Wilmington": "Los Angeles", "Venice": "Los Angeles",
           "San Ysidro": "San Diego", "La Jolla": "San Diego",
           "Los Angeles": "Los Angeles", "San Francisco": "San Francisco", "San Diego": "San Diego",
           "Berkeley": "Berkeley", "Santa Ana": "Santa Ana"},
    "NJ": {"Jersey City": "Jersey City", "Hoboken": "Hoboken", "Newark": "Newark"},
}
STATE_FIPS = {"06": "CA", "25": "MA", "34": "NJ"}
GEO_FIELDS = ["address_id", "match", "matched_address", "lon", "lat", "state_fips", "county_fips",
              "place", "method"]


def load_addresses() -> list[dict]:
    with open(ADDRESSES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_cache() -> dict[str, dict]:
    if not GEOCODE_CSV.exists():
        return {}
    with open(GEOCODE_CSV, newline="", encoding="utf-8") as f:
        return {r["address_id"]: r for r in csv.DictReader(f)}


def save_cache(rows: dict[str, dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with open(GEOCODE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=GEO_FIELDS)
        w.writeheader()
        for r in rows.values():
            w.writerow({k: r.get(k, "") for k in GEO_FIELDS})


def batch_geocode(addresses: list[dict]) -> dict[str, dict]:
    """One batch call: id, street, city, state, zip -> match, coordinates, state & county FIPS."""
    buf = io.StringIO()
    w = csv.writer(buf)
    for a in addresses:
        w.writerow([a["address_id"], a["street_address"], a["postal_city"], a["state"], a["zip"]])
    resp = requests.post(BATCH_URL, data={"benchmark": BENCHMARK, "vintage": VINTAGE},
                         files={"addressFile": ("addresses.csv", buf.getvalue().encode("utf-8"), "text/csv")},
                         timeout=600)
    resp.raise_for_status()
    out = {}
    # Batch output: id, input, match, match type, matched address, "lon,lat", tiger id, side, state, county, tract, block
    for row in csv.reader(io.StringIO(resp.text)):
        if len(row) < 3:
            continue
        rec = {"address_id": row[0], "match": row[2], "matched_address": "", "lon": "", "lat": "",
               "state_fips": "", "county_fips": "", "place": "", "method": ""}
        if row[2] == "Match" and len(row) >= 10:
            rec["matched_address"] = row[4]
            lon, lat = row[5].split(",")
            rec["lon"], rec["lat"] = lon.strip(), lat.strip()
            rec["state_fips"], rec["county_fips"] = row[8], row[9]
        out[row[0]] = rec
    return out


def place_for_point(lon: str, lat: str) -> str:
    """Incorporated place containing a point (e.g. 'Boston city'), or '' if none / unincorporated."""
    for attempt in range(3):
        try:
            r = requests.get(POINT_URL, params={"x": lon, "y": lat, "benchmark": BENCHMARK, "vintage": VINTAGE,
                                                "layers": "Incorporated Places", "format": "json"}, timeout=60)
            if r.status_code == 200:
                places = r.json().get("result", {}).get("geographies", {}).get("Incorporated Places", [])
                return places[0]["NAME"] if places else ""
        except (requests.RequestException, ValueError):
            pass
        time.sleep(1 + attempt)
    return "ERROR"


def legal_city(place: str) -> str:
    """'Boston city' -> 'Boston'; 'Los Angeles city' -> 'Los Angeles'."""
    for suffix in (" city", " town", " village", " borough"):
        if place.endswith(suffix):
            return place[: -len(suffix)]
    return place


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    addresses = load_addresses()
    cache = {} if args.force else load_cache()
    todo = [a for a in addresses if a["address_id"] not in cache]
    print(f"{len(addresses)} addresses, {len(cache)} cached, {len(todo)} to geocode")

    if todo:
        got = batch_geocode(todo)
        for a in todo:
            cache[a["address_id"]] = got.get(a["address_id"], {"address_id": a["address_id"], "match": "No_Match"})
        save_cache(cache)
        matched = [r for r in cache.values() if r["match"] == "Match" and not r.get("place")]
        print(f"batch done: {sum(1 for r in cache.values() if r['match'] == 'Match')} matched; "
              f"looking up incorporated place for {len(matched)} points ...")
        with ThreadPoolExecutor(max_workers=6) as ex:
            for rec, place in zip(matched, ex.map(lambda r: place_for_point(r["lon"], r["lat"]), matched)):
                rec["place"] = place
                rec["method"] = "census" if place and place != "ERROR" else "census_no_place"
        save_cache(cache)

    # Decide the legal jurisdiction for every address.
    juris, counts = {}, {"census": 0, "fallback": 0, "unresolved": 0}
    for a in addresses:
        rec = cache.get(a["address_id"], {})
        state = STATE_FIPS.get(rec.get("state_fips", ""), a["state"])
        place = rec.get("place", "")
        if rec.get("match") == "Match" and place and place != "ERROR":
            city, method, conf = legal_city(place), "census", "high"
            counts["census"] += 1
        else:
            fb = POSTAL_TO_LEGAL.get(a["state"], {}).get(a["postal_city"])
            if fb:
                city, method, conf = fb, "fallback", "fallback"
                counts["fallback"] += 1
            else:
                city, method, conf = None, "unresolved", "none"
                counts["unresolved"] += 1
        juris[a["address_id"]] = {"state": state, "county_fips": rec.get("county_fips", ""),
                                  "city": city, "postal_city": a["postal_city"], "method": method,
                                  "confidence": conf, "matched_address": rec.get("matched_address", "")}
    JURIS_JSON.write_text(json.dumps(juris, indent=1), encoding="utf-8")

    # Where did the postal city differ from the legal city?
    fixes = {}
    for a in addresses:
        j = juris[a["address_id"]]
        if j["city"] and j["city"] != a["postal_city"]:
            fixes[(a["postal_city"], j["city"])] = fixes.get((a["postal_city"], j["city"]), 0) + 1
    print(f"resolved: {counts} -> {JURIS_JSON}")
    print("postal -> legal corrections:", fixes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
