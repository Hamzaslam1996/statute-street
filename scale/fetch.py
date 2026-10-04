"""
scale/fetch.py - real addresses from official open data portals (instructions/scale.md section 1).

Plain-language summary
----------------------
Downloads up to 2,000 multi-unit residential parcels per city from each city's own open data
API (documented public endpoints, normal rate limits, no scraping), keeps only the fields the
engine needs plus provenance, and writes scale/data/<city>.csv in the same shape as the
organisers' sample_addresses.csv so the unchanged pipeline can run on them.

PRIVACY: owner names, mailing addresses and every other person field are dropped at download
time and never written to disk. Kept: address, ZIP, year built, units, use description, the
portal's record id and URL.

Provenance per city (endpoint, dataset, retrieved timestamp, rows, sha256, licence) goes to
scale/data/provenance.json.

Usage:  .venv/bin/python scale/fetch.py [--cap 2000] [--city sf boston cambridge]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIELDS = ["address_id", "street_address", "postal_city", "state", "zip", "year_built", "units", "use_code",
          "use_description", "source_dataset", "retrieved_at", "record_id", "record_url"]

SF_URL = "https://data.sf.gov/resource/wv5m-vpq2.json"
SF_META = "https://data.sf.gov/api/views/wv5m-vpq2.json"
BOS_SQL = "https://data.boston.gov/api/3/action/datastore_search_sql"
BOS_PKG = "https://data.boston.gov/api/3/action/package_show?id=property-assessment"
BOS_RES = "ee73430d-96c0-423e-ad21-c4cfb54c8961"        # fy2026-property-assessment-data_rev.csv
CAM_URL = "https://data.cambridgema.gov/resource/waa7-ibdu.json"
CAM_META = "https://data.cambridgema.gov/api/views/waa7-ibdu.json"
CAM_CLASSES = ["TWO-FAM-RES", "THREE-FM-RES", "4-8-UNIT-APT", ">8-UNIT-APT", "MULT-RES-2FAM", "MULT-RES-3FAM",
               "MULTIUSE-RES", "AFFORDABLE APT", "CONDO-BLDG", "MULT-RES-4-8-APT", "MULT-RES->8 APT"]
UA = {"User-Agent": "statute-street-scale/1.0 (hackathon research; single pass, paged, rate limited)"}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def get_json(url: str, params: dict | None = None, tries: int = 3):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=120)
            if r.status_code == 200:
                return r.json()
            print(f"  {url.split('/')[2]}: HTTP {r.status_code}, retrying", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  {url.split('/')[2]}: {e}, retrying", file=sys.stderr)
        time.sleep(2 + 2 * i)
    raise SystemExit(f"endpoint unavailable: {url}")


def socrata_pages(url: str, where: str, select: str, cap: int, order: str) -> list[dict]:
    """Page through a Socrata dataset 1,000 rows at a time (the documented $limit/$offset pattern)."""
    rows, offset = [], 0
    while len(rows) < cap:
        page = get_json(url, {"$select": select, "$where": where, "$order": order, "$limit": min(1000, cap - len(rows)),
                              "$offset": offset})
        rows.extend(page)
        if len(page) < min(1000, cap - len(rows) + len(page)):
            break
        offset += len(page)
        time.sleep(0.5)
    return rows[:cap]


def sf_location(loc: str) -> str:
    """'0000 0704 NORTH POINT         ST0000' -> '704 NORTH POINT ST' (first field is a unit/second number)."""
    s = re.sub(r"\s+", " ", (loc or "").strip())
    m = re.match(r"^(\d{4}) (\d{4}) (.+?)\s*(\d{4})?$", s)
    if m:
        num = str(int(m.group(2))) if m.group(2) != "0000" else str(int(m.group(1)))
        street = m.group(3).strip()
        return f"{num} {street}"
    return s


def fetch_sf(cap: int) -> tuple[list[dict], dict]:
    meta = get_json(SF_META)
    where = "closed_roll_year='2025' AND number_of_units>=2 AND use_code='MRES'"
    select = ("property_location,parcel_number,use_code,use_definition,property_class_code,"
              "property_class_code_definition,year_property_built,number_of_units,row_id")
    raw = socrata_pages(SF_URL, where, select, cap, "parcel_number")
    ts = now()
    rows = []
    for r in raw:
        street = sf_location(r.get("property_location"))
        if not re.match(r"^\d+ ", street):
            continue
        yb = r.get("year_property_built")
        rows.append({"street_address": street, "postal_city": "San Francisco", "state": "CA", "zip": "",
                     "year_built": str(int(float(yb))) if yb and float(yb) > 0 else "",
                     "units": str(int(float(r.get("number_of_units") or 0))) or "",
                     "use_code": r.get("property_class_code") or r.get("use_code"),
                     "use_description": r.get("property_class_code_definition") or r.get("use_definition"),
                     "source_dataset": "DataSF wv5m-vpq2 (2025 roll)", "retrieved_at": ts,
                     "record_id": r.get("row_id"), "record_url": f"https://data.sf.gov/d/wv5m-vpq2?row_id={r.get('row_id')}"})
    prov = {"city": "San Francisco", "endpoint": SF_URL, "dataset": meta.get("name"),
            "filter": where, "licence": f"{(meta.get('license') or {}).get('name')} ({(meta.get('license') or {}).get('termsLink')})",
            "retrieved_at": ts, "owner_fields_in_source": "none (the roll carries no owner names)"}
    return rows, prov


def fetch_boston(cap: int) -> tuple[list[dict], dict]:
    pkg = get_json(BOS_PKG)["result"]
    # Building-level residential land uses: two-family, three-family, 4-6 unit and 7+ unit apartments
    # (condo units are per-unit records and are skipped). Owner and mailing columns are not selected.
    sql = (f'SELECT "PID","ST_NUM","ST_NAME","CITY","ZIP_CODE","LU","LU_DESC","YR_BUILT","RES_UNITS" '
           f'FROM "{BOS_RES}" WHERE "LU" IN (\'R2\',\'R3\',\'R4\',\'A\') AND "BLDG_SEQ" = \'1\' ORDER BY "PID" LIMIT {cap}')
    res = get_json(BOS_SQL, {"sql": sql})["result"]["records"]
    ts = now()
    rows = []
    for r in res:
        num = (r.get("ST_NUM") or "").strip()
        name = (r.get("ST_NAME") or "").strip()
        if not num or not name:
            continue
        yb = (r.get("YR_BUILT") or "").strip()
        rows.append({"street_address": f"{num} {name}", "postal_city": (r.get("CITY") or "Boston").title(), "state": "MA",
                     "zip": (r.get("ZIP_CODE") or "").strip(), "year_built": yb if yb and yb != "0" else "",
                     "units": (r.get("RES_UNITS") or "").strip() or "",
                     "use_code": r.get("LU"), "use_description": r.get("LU_DESC"),
                     "source_dataset": "Analyze Boston property-assessment FY2026 (rev)", "retrieved_at": ts,
                     "record_id": r.get("PID"), "record_url": f"https://data.boston.gov/dataset/property-assessment/resource/{BOS_RES}?q=PID%3A{r.get('PID')}"})
    prov = {"city": "Boston", "endpoint": BOS_SQL, "dataset": f"{pkg.get('title')} FY2026 (resource {BOS_RES})",
            "filter": "LU in (R2, R3, R4, A), BLDG_SEQ = 1", "licence": f"{pkg.get('license_title')} ({pkg.get('license_url')})",
            "retrieved_at": ts, "owner_fields_in_source": "OWNER, MAIL_ADDRESSEE, MAIL_* exist in the source and were not selected"}
    return rows, prov


def fetch_cambridge(cap: int) -> tuple[list[dict], dict]:
    meta = get_json(CAM_META)
    classes = ",".join(f"'{c}'" for c in CAM_CLASSES)
    where = f"propertyclass in({classes}) AND bldgnum='1'"
    # owner_* columns exist in the source and are deliberately not selected.
    select = "pid,address,propertyclass,stateclasscode,condition_yearbuilt,interior_numunits,unit"
    raw = socrata_pages(CAM_URL, where, select, cap, "pid")
    ts = now()
    rows, seen = [], set()
    for r in raw:
        addr = re.sub(r"\s+", " ", (r.get("address") or "").strip())
        if not re.match(r"^\d+", addr) or r.get("unit"):
            continue
        key = addr.upper()
        if key in seen:
            continue
        seen.add(key)
        yb = (r.get("condition_yearbuilt") or "").strip()
        rows.append({"street_address": addr, "postal_city": "Cambridge", "state": "MA", "zip": "",
                     "year_built": yb if yb and yb != "0" else "", "units": (r.get("interior_numunits") or "").strip(),
                     "use_code": r.get("stateclasscode"), "use_description": r.get("propertyclass"),
                     "source_dataset": "Cambridge Property Database FY2026 (waa7-ibdu)", "retrieved_at": ts,
                     "record_id": r.get("pid"), "record_url": f"https://data.cambridgema.gov/d/waa7-ibdu?pid={r.get('pid')}"})
    lic = (meta.get("license") or {}).get("name")
    prov = {"city": "Cambridge", "endpoint": CAM_URL, "dataset": meta.get("name"), "filter": where,
            "licence": lic or "No licence field on the dataset page (metadata license empty); attribution: "
                              f"{meta.get('attribution')} ({meta.get('attributionLink')}). Flagged for Hamza to confirm reuse terms.",
            "retrieved_at": ts, "owner_fields_in_source": "owner_name, owner_coownername, owner_address* exist in the source and were not selected"}
    return rows, prov


def write_city(slug: str, rows: list[dict], prov: dict) -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / f"{slug}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            r = dict(r); r["address_id"] = f"{slug.upper()[:3]}{i:05d}"
            w.writerow({k: r.get(k, "") for k in FIELDS})
    prov["rows"] = len(rows)
    prov["file"] = str(path.relative_to(HERE.parent))
    prov["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    prov["size_bytes"] = path.stat().st_size
    return prov


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=2000)
    ap.add_argument("--city", nargs="*", default=["sf", "boston", "cambridge"])
    args = ap.parse_args()
    fetchers = {"sf": fetch_sf, "boston": fetch_boston, "cambridge": fetch_cambridge}
    provenance = json.loads((DATA / "provenance.json").read_text()) if (DATA / "provenance.json").exists() else {}
    for slug in args.city:
        t0 = time.time()
        try:
            rows, prov = fetchers[slug](args.cap)
        except SystemExit as e:
            print(f"{slug}: skipped ({e})")
            provenance[slug] = {"city": slug, "skipped": str(e)}
            continue
        prov["fetch_seconds"] = round(time.time() - t0, 1)
        provenance[slug] = write_city(slug, rows, prov)
        print(f"{slug}: {len(rows)} rows in {prov['fetch_seconds']}s -> {provenance[slug]['file']} sha256 {provenance[slug]['sha256'][:12]}")
    (DATA / "provenance.json").write_text(json.dumps(provenance, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
