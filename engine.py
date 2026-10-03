"""
engine.py - Module B, step 3: deterministic rule engine. No AI here.

Plain-language summary
----------------------
For every address and every rule in its state or city, decide:
  applies | unknown | superseded | not_yet_effective | pending
following the organisers' definitions and Hamza's rulings (instructions/module_b.md):
  1. Status first, as of the query date (pending bills -> pending; failed measures
     and negative findings are excluded; effective date after the query date ->
     not_yet_effective; an ordinance adopted within 60 days of the query date -> unknown).
  2. Coverage tests from out/coverage.json, each true / false / unknown. Year built is
     only a proxy for the certificate-of-occupancy date: before the cutoff year ->
     true, after -> false, the cutoff year itself or missing -> unknown. Owner type,
     tenancy length and funding are never in the data -> unknown unless another fact
     defeats the exception (e.g. more than 4 units).
     All true -> applies; any false -> left out; otherwise unknown.
  3. Precedence: a state rule that yields to stricter local rules is "superseded"
     where a local rule in the same category applies (unknown where it is unknown).
  4. Conflict flags where a state rule with pre-emption language meets a local rule
     in the same category (e.g. FAIR Act vs Jersey City / Hoboken bans).
Every answer carries a one-sentence explanation naming the deciding fact.

Usage:
    python engine.py                      # all 500 addresses, as of 2026-10-01 -> out/lookups.json
    python engine.py --as-of 2027-07-02   # another query date (Module C reuses this)
    python engine.py --address A0001 A0002
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date

from common import DEFAULT_QUERY_DATE, OUT, STARTER

ADDRESSES_CSV = STARTER / "data" / "sample_addresses.csv"
RULES_FULL = OUT / "rules_full.json"
COVERAGE_JSON = OUT / "coverage.json"
JURIS_JSON = OUT / "jurisdictions.json"
LOOKUPS_JSON = OUT / "lookups.json"
AUDIT_CSV = OUT / "lookup_audit.csv"

UNKNOWABLE = {"owner_type", "tenancy_months", "funding", "other"}

# A state rule "yields" to local law when its interaction text says so.
YIELDS_RE = re.compile(r"\b(yield\w*|does not apply (where|to housing subject to)|local (rent|price) control|"
                       r"more protective|stricter|restricts annual increases to an amount less)\b", re.I)
# A state rule pre-empts local law when its interaction text says so.
PREEMPT_RE = re.compile(r"\b(pre-?empt\w*|conflict\w* (with|municipal)|municipalit\w+ (shall be |is )?prohibited|"
                        r"bars? (conflicting )?(local|municipal))\b", re.I)


# ---------------------------------------------------------------------------
# Address facts
# ---------------------------------------------------------------------------
def building_type(use_code: str, use_description: str) -> str | None:
    """
    Map assessor wording to a coarse type the coverage tests understand. The sample's
    descriptions: LA "Five or more apartments", SANDAG "(5+ units)", Alameda "(5+ units)",
    SF "Apartment 5 to 14 Units" / "Flats 5 to 14 units" / "Flat & Store", Cambridge
    "4-8-UNIT-APT" / ">8-UNIT-APT", Boston "APT 7-30 UNITS" / "LUXURY APARTMENT" /
    "SUBSD HOUSING S- 8", NJ class 4C (apartments) with MOD-IV codes like "3S-B-A-13U-H".
    """
    d = (use_description or "").lower()
    c = (use_code or "").upper()
    if ("apartment" in d or "apt" in d or "five or more" in d or "5+ units" in d or "multi" in d
            or "flat" in d or "subsd housing" in d or "class 4c" in d or c.startswith("4C") or c.startswith("A/")
            or re.search(r"\d\s*(?:to\s*\d+\s*)?units?", d) or "residential income" in d or "dwelling units" in d):
        return "apartments"
    if "condo" in d:
        return "condo"
    if "single" in d or "one family" in d or "1 family" in d:
        return "single_family"
    if "duplex" in d or "two units" in d or "2 units" in d or "two family" in d or "2 family" in d:
        return "duplex"
    if "mixed" in d or "store" in d or "commercial" in d:
        return "mixed"
    return None


def address_facts(row: dict, juris: dict) -> dict:
    def num(x):
        try:
            return int(float(x)) if x not in (None, "") else None
        except ValueError:
            return None
    return {
        "address_id": row["address_id"],
        "state": juris.get("state") or row["state"],
        "city": juris.get("city"),
        "jurisdiction_method": juris.get("method"),
        "year_built": num(row.get("year_built")),
        "units": num(row.get("units")),
        "building_type": building_type(row.get("use_code"), row.get("use_description")),
        # Funding is only visible when the assessor says so (Boston "SUBSD HOUSING S- 8",
        # NJ "...-AFFORDABL"); otherwise unknown, never assumed market-rate.
        "funding": "subsidized" if re.search(r"subsd|s- ?8|section 8|affordabl", (row.get("use_description") or ""), re.I) else None,
        "use_description": row.get("use_description"),
    }


# ---------------------------------------------------------------------------
# Status as of a date
# ---------------------------------------------------------------------------
def parse_partial(d: str | None) -> tuple[date, date] | None:
    if not d:
        return None
    parts = d.split("-")
    try:
        y = int(parts[0])
        if len(parts) == 3:
            x = date(y, int(parts[1]), int(parts[2])); return x, x
        if len(parts) == 2:
            m = int(parts[1]); end = date(y + (m == 12), m % 12 + 1, 1).toordinal() - 1
            return date(y, m, 1), date.fromordinal(end)
        return date(y, 1, 1), date(y, 12, 31)
    except ValueError:
        return None


def status_as_of(rule: dict, as_of: date) -> tuple[str | None, str]:
    """
    Returns (result-or-None, explanation). None means 'go on to the coverage tests'.
    'exclude' means the rule never appears for this address.
    """
    st = rule.get("status")
    if rule.get("negative_finding") or rule.get("derived"):
        return "exclude", "negative finding: shown as 'no rule at this level', never as applying"
    if st == "failed":
        return "exclude", "failed / struck measure: kept only as change history"
    if st == "pending":
        return "pending", f"{rule['citation']} is a pending bill or proposal, not law"
    bounds = parse_partial(rule.get("effective_date"))
    if bounds and bounds[0] > as_of:
        return "not_yet_effective", f"effective {rule['effective_date']}, after the query date {as_of}"
    if bounds and bounds[0] <= as_of < bounds[1] and len(rule.get("effective_date") or "") < 10:
        return "unknown", f"effective date only known as {rule['effective_date']}; query date {as_of} falls inside it"
    note = (rule.get("conflict_note") or "") + " " + (rule.get("notes") or "")
    if "within 60 days" in note.lower():
        return "unknown", "adopted within 60 days of the query date; effective date unconfirmed"
    return None, ""


# ---------------------------------------------------------------------------
# Coverage tests
# ---------------------------------------------------------------------------
def compare(actual, op: str, value) -> bool | None:
    try:
        if op in ("in", "not_in"):
            vals = value if isinstance(value, list) else [value]
            vals = [str(v).lower() for v in vals]
            hit = str(actual).lower() in vals
            return hit if op == "in" else not hit
        if isinstance(value, str) and isinstance(actual, (int, float)):
            value = float(value)
        if isinstance(actual, str) or isinstance(value, str):
            a, v = str(actual).lower(), str(value).lower()
            return {"==": a == v, "!=": a != v}.get(op)
        return {"<": actual < value, "<=": actual <= value, ">": actual > value, ">=": actual >= value,
                "==": actual == value, "!=": actual != value}[op]
    except (TypeError, ValueError, KeyError):
        return None


def run_test(test: dict, facts: dict, as_of: date) -> tuple[bool | None, str]:
    field, op, value = test["field"], test["op"], test["value"]
    yb, units, btype = facts.get("year_built"), facts.get("units"), facts.get("building_type")

    if field == "year_built":
        if yb is None:
            return None, "year built missing from county records"
        return compare(yb, op, value), f"built {yb}"

    if field in ("coo_date", "coo_age_years"):
        # year built stands in for the certificate-of-occupancy date (not the same thing):
        # strictly before the cutoff year -> true, strictly after -> false, same year -> unknown
        if yb is None:
            return None, "year built missing, so the certificate-of-occupancy cutoff cannot be tested"
        if field == "coo_date":
            cutoff_year = int(str(value)[:4])
            label = f"{str(value)[:10]} certificate-of-occupancy cutoff"
        else:
            cutoff_year = as_of.year - int(float(value))
            label = f"{int(float(value))}-year certificate-of-occupancy window (built before {cutoff_year})"
        # Which side does the rule cover? coo_date <= 1979-06-13 covers OLDER buildings;
        # coo_age_years >= 15 ("certificate at least 15 years old") also covers OLDER buildings.
        older_ok = op in ("<", "<=") if field == "coo_date" else op in (">", ">=")
        if yb == cutoff_year:
            return None, f"built {yb}, the cutoff year itself: year built is not the certificate date"
        is_older = yb < cutoff_year
        return (is_older if older_ok else not is_older), f"built {yb}, {'before' if is_older else 'after'} the {label}"

    if field == "units":
        if units is None:
            return None, "unit count missing from county records"
        return compare(units, op, value), f"{units} units"

    if field == "building_type":
        if btype is None:
            return None, f"building type unclear from assessor description '{facts.get('use_description')}'"
        return compare(btype, op, value), f"assessor type {btype}"

    if field == "funding" and facts.get("funding") == "subsidized":
        # The assessor says the building is subsidised. Test values are free text
        # ("deed_restricted", "public_housing", "market_rate"); map them to our two categories.
        def canon(v):
            v = str(v).lower()
            return "subsidized" if re.search(r"subsid|afford|deed|public|section|government|regulated", v) else \
                   "market_rate" if "market" in v else v
        vals = [canon(v) for v in value] if isinstance(value, list) else canon(value)
        ok = compare("subsidized", op, vals)
        return ok, f"assessor marks the building as subsidised housing ('{facts.get('use_description')}')"

    # owner_type, tenancy_months, funding, other: not in the data
    d = test.get("defeated_if")
    if d:
        actual = {"units": units, "year_built": yb, "building_type": btype}.get(d["field"])
        if actual is not None and compare(actual, d["op"], d["value"]):
            return True, f"{field} exception cannot apply ({d['field']} {d['op']} {d['value']}: {actual})"
    return None, f"{field.replace('_', ' ')} not in the data ({test.get('source_text', '')[:60]})"


def evaluate_coverage(rule: dict, cov: dict | None, facts: dict, as_of: date) -> tuple[str, str]:
    """-> ('applies' | 'unknown' | 'exclude', explanation)."""
    tests = (cov or {}).get("tests") or []
    if (cov or {}).get("coverage_incomplete"):
        return "unknown", "Unknown: who the ordinance covers is defined in text not in the corpus"
    if not tests:
        return "applies", f"covers all residential rentals in {rule['jurisdiction']}"
    reasons_true, reasons_unknown = [], []
    for t in tests:
        ok, why = run_test(t, facts, as_of)
        if ok is False:
            return "exclude", why
        (reasons_true if ok else reasons_unknown).append(why)
    if reasons_unknown:
        return "unknown", "Unknown: " + reasons_unknown[0]
    return "applies", "; ".join(reasons_true[:2]).capitalize()


# ---------------------------------------------------------------------------
# One address
# ---------------------------------------------------------------------------
def rules_for(facts: dict, rules: list[dict]) -> list[dict]:
    local = f"{facts['city']}, {facts['state']}" if facts.get("city") else None
    return [r for r in rules if r["jurisdiction"] == facts["state"] or (local and r["jurisdiction"] == local)]


def evaluate_address(facts: dict, rules: list[dict], coverage: dict, as_of: date) -> list[dict]:
    results = []
    for rule in rules_for(facts, rules):
        status, why = status_as_of(rule, as_of)
        if status == "exclude":
            continue
        if status is None:
            status, why = evaluate_coverage(rule, coverage.get(rule["team_rule_id"]), facts, as_of)
            if status == "exclude":
                continue
        results.append({"team_rule_id": rule["team_rule_id"], "result": status, "explanation": why,
                        "conflict_flag": False, "_rule": rule})

    # Precedence: a yielding state rule is superseded by an applying local rule in the same category.
    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["_rule"]["category"], []).append(r)
    for cat, rs in by_cat.items():
        states = [r for r in rs if r["_rule"]["level"] == "state" and r["result"] in ("applies", "unknown")]
        locals_ = [r for r in rs if r["_rule"]["level"] == "city" and r["result"] in ("applies", "unknown")]
        for s in states:
            if not YIELDS_RE.search(s["_rule"].get("interaction") or ""):
                continue
            for loc in locals_:
                if loc["result"] == "applies":
                    # A stricter local rule governs, whatever the state rule's own answer was.
                    s["result"] = "superseded"
                    s["explanation"] = f"Stricter local rule {loc['team_rule_id']} ({loc['_rule']['title'][:50]}) governs here"
                elif loc["result"] == "unknown" and s["result"] == "applies":
                    s["result"] = "unknown"
                    s["explanation"] = f"Unknown: whether local rule {loc['team_rule_id']} governs depends on facts not in the data"
        # Conflict: pre-empting state rule meets a local rule in the same category.
        for s in [r for r in rs if r["_rule"]["level"] == "state"]:
            if PREEMPT_RE.search(s["_rule"].get("interaction") or "") and locals_:
                s["conflict_flag"] = True
                for loc in locals_:
                    loc["conflict_flag"] = True
                    loc["explanation"] += f"; possible conflict with state rule {s['team_rule_id']} (pre-emption language)"
                s["explanation"] += f"; may pre-empt local rule(s) {', '.join(l['team_rule_id'] for l in locals_)}"
    for r in results:
        r.pop("_rule")
    return results


def load_inputs():
    rules = json.loads(RULES_FULL.read_text(encoding="utf-8"))["rules"]
    coverage = json.loads(COVERAGE_JSON.read_text(encoding="utf-8")) if COVERAGE_JSON.exists() else {}
    juris = json.loads(JURIS_JSON.read_text(encoding="utf-8"))
    with open(ADDRESSES_CSV, newline="", encoding="utf-8") as f:
        addresses = list(csv.DictReader(f))
    return rules, coverage, juris, addresses


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=DEFAULT_QUERY_DATE)
    ap.add_argument("--address", nargs="*", help="only these address ids")
    ap.add_argument("--out", default=str(LOOKUPS_JSON))
    args = ap.parse_args()
    as_of = date.fromisoformat(args.as_of)

    rules, coverage, juris, addresses = load_inputs()
    if args.address:
        addresses = [a for a in addresses if a["address_id"] in set(args.address)]
    lookups, audit, counts = {}, [], {}
    for row in addresses:
        facts = address_facts(row, juris.get(row["address_id"], {}))
        res = evaluate_address(facts, rules, coverage, as_of)
        lookups[row["address_id"]] = res
        for r in res:
            counts[r["result"]] = counts.get(r["result"], 0) + 1
            audit.append({"address_id": row["address_id"], "city": facts["city"], "team_rule_id": r["team_rule_id"],
                          "result": r["result"], "conflict_flag": r["conflict_flag"], "deciding_facts": r["explanation"]})
    out = {"as_of": args.as_of, "lookups": lookups}
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = args.out if args.out != str(LOOKUPS_JSON) or args.as_of == DEFAULT_QUERY_DATE \
        else str(OUT / f"lookups_{args.as_of}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    if not args.address and args.as_of == DEFAULT_QUERY_DATE:
        with open(AUDIT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["address_id", "city", "team_rule_id", "result", "conflict_flag", "deciding_facts"])
            w.writeheader(); w.writerows(audit)
    print(f"{len(lookups)} addresses as of {args.as_of}: {counts} -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
