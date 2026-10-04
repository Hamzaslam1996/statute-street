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
NO_UNITS_FLOOR = False   # set by --no-units-floor: ignore unit minimums stated in assessor descriptions

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
    # New Jersey property class 4C ("apartments") is NOT a unit-count statement: the MOD-IV
    # building codes under it include 2-unit buildings ("2SF2UG"), so a 4C row's building type
    # stays unknown unless the description says so in words (rulings_06 #1, class C).
    if c.startswith("4C") and "apartment" not in d:
        return None
    if ("apartment" in d or "apt" in d or "five or more" in d or "5+ units" in d or "multi" in d
            or "flat" in d or "subsd housing" in d or c.startswith("A/")
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


MODIV_UNITS_RE = re.compile(r"(\d+)U(?=[-/A-Z]|$)")


def derive_units(use_description: str) -> int | None:
    """
    NJ MOD-IV building codes encode the unit count: '3S-B-A-13U-H' -> 13, '6B-20U-G' -> 20,
    '2SF2UG' -> 2, '4F-8U-C/3F-2U' -> 10 (two buildings on the parcel, summed).
    This is a DERIVED value (Hamza rulings_05 #3): shown in explanations, never asserted
    in the submission unless --use-derived-units is given.
    """
    d = (use_description or "").upper()
    if not re.search(r"\d+U(?=[-/A-Z]|$)", d) or "UNIT" in d or "APARTMENT" in d:
        return None
    nums = [int(n) for n in MODIV_UNITS_RE.findall(d)]
    return sum(nums) if nums else None


def units_floor(use_description: str) -> int | None:
    """
    A MINIMUM unit count stated in words by the assessor's own description column:
    "Five or more apartments" -> 5, "SANDAG asr_landuse 14-16 (5+ units)" -> 5,
    "Apartment 5 to 14 Units" -> 5, "Apartment 15 Units or more" -> 15, "4-8-UNIT-APT" -> 4,
    ">8-UNIT-APT" -> 9, "APT 7-30 UNITS" -> 7. Used only to decide tests like units > 4
    (a floor of 5 settles them); never treated as the exact count.
    """
    d = (use_description or "").lower()
    if "five or more" in d:
        return 5
    m = re.search(r"(\d+)\+ ?units", d) or re.search(r"(\d+) units? or more", d)
    if m:
        return int(m.group(1))
    m = re.search(r">(\d+)-unit", d)
    if m:
        return int(m.group(1)) + 1
    m = re.search(r"(\d+)\s*(?:to|-)\s*(\d+)\s*-?\s*units?", d)
    if m:
        return int(m.group(1))
    return None


def compare_with_floor(floor: int, op: str, value) -> bool | None:
    """Can a 'units' test be settled knowing only that units >= floor?"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if op in (">", ">=") and compare(floor, op, v):
        return True          # the floor already clears the threshold
    if op in ("<", "<=") and not compare(floor, op, v):
        return False         # even the floor is too many
    return None


def address_facts(row: dict, juris: dict, use_derived_units: bool = False) -> dict:
    def num(x):
        try:
            return int(float(x)) if x not in (None, "") else None
        except ValueError:
            return None
    units = num(row.get("units"))
    derived = derive_units(row.get("use_description")) if units is None else None
    return {
        "address_id": row["address_id"],
        "state": juris.get("state") or row["state"],
        "city": juris.get("city"),
        "jurisdiction_method": juris.get("method"),
        "year_built": num(row.get("year_built")),
        "units": derived if (use_derived_units and units is None and derived) else units,
        "units_min": units_floor(row.get("use_description")) if units is None else None,
        "units_derived": derived,
        "units_derived_source": row.get("use_description") if derived else None,
        "building_type": building_type(row.get("use_code"), row.get("use_description")),
        # Funding is only visible when the assessor says so in words (Boston "SUBSD HOUSING S- 8");
        # a cryptic NJ MOD-IV suffix ("-AFFORDABL") is derived data and is not asserted (rulings_05 #3).
        # Otherwise unknown, never assumed market-rate.
        "funding": "subsidized" if re.search(r"subsd|s- ?8|section 8", (row.get("use_description") or ""), re.I) else None,
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
        return "pending", "Bill, not law: a pending bill or proposal, not yet enacted."
    bounds = parse_partial(rule.get("effective_date"))
    if bounds and bounds[0] > as_of:
        return "not_yet_effective", f"Not yet in force: takes effect {fmt_date(rule['effective_date'])}."
    if bounds and bounds[0] <= as_of < bounds[1] and len(rule.get("effective_date") or "") < 10:
        return "unknown", (f"Unknown: needs the exact effective date. The rule took effect in {fmt_date(rule['effective_date'])} "
                           f"and the query date falls inside that period.")
    note = (rule.get("conflict_note") or "") + " " + (rule.get("notes") or "")
    if "within 60 days" in note.lower():
        return "unknown", "Unknown: needs the effective date. The ordinance was adopted within 60 days of the query date."
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
            return None, "year built not in data"
        return compare(yb, op, value), f"built {yb}"

    if field in ("coo_date", "coo_age_years"):
        # year built stands in for the certificate-of-occupancy date (not the same thing):
        # strictly before the cutoff year -> true, strictly after -> false, same year -> unknown
        if yb is None:
            return None, "year built not in data"
        if field == "coo_date":
            cutoff_year = int(str(value)[:4])
            label = f"{fmt_date(str(value)[:10])} certificate of occupancy cutoff"
        else:
            cutoff_year = as_of.year - int(float(value))
            label = f"{int(float(value))} year certificate of occupancy window (built before {cutoff_year})"
        # Which side does the rule cover? coo_date <= 1979-06-13 covers OLDER buildings;
        # coo_age_years >= 15 ("certificate at least 15 years old") also covers OLDER buildings.
        older_ok = op in ("<", "<=") if field == "coo_date" else op in (">", ">=")
        if yb == cutoff_year:
            if CUTOFF_YEAR_APPLIES:
                return True, f"built {yb}, the cutoff year, resolved as covered (stress key)"
            return None, f"built {yb}, the cutoff year itself; year built is not the certificate date"
        is_older = yb < cutoff_year
        return (is_older if older_ok else not is_older), f"built {yb}, {'before' if is_older else 'after'} the {label}"

    if field == "units":
        if units is None and facts.get("units_min") and not NO_UNITS_FLOOR:
            settled = compare_with_floor(facts["units_min"], op, value)
            if settled is not None:
                side = "above" if op in (">", ">=") else "within"
                return settled, f"at least {facts['units_min']} units per the assessor description, {side} the coverage threshold"
        if units is None:
            if facts.get("units_derived"):
                return None, (f"units not in data; the assessor building code "
                              f"'{facts['units_derived_source']}' suggests {facts['units_derived']} units (derived, unconfirmed)")
            return None, "units not in data"
        ok = compare(units, op, value)
        side = ("above" if op in (">", ">=") else "within" if op in ("<", "<=") else "at") if ok else "outside"
        return ok, f"{units} units, {side} the coverage threshold"

    if field == "building_type":
        vals = [str(v).lower() for v in (value if isinstance(value, list) else [value])]
        # A "one- or two-family dwelling" exemption written as a building-type test is really a
        # unit-count exemption: only unit evidence (count or stated floor) can beat it, not the
        # label "apartments" (rulings_06 #1, class C).
        small = {"single_family": 1, "one_family": 1, "duplex": 2, "two_family": 2, "triplex": 3, "fourplex": 4}
        if test_kind(test) == "plausible_exemption" and op in ("not_in", "!=") and vals and all(v in small for v in vals):
            threshold = max(small[v] for v in vals)
            n = units if units is not None else (facts.get("units_min") if not NO_UNITS_FLOOR else None)
            names = " or ".join(v.replace("_", " ") for v in vals)
            if n is not None and n > threshold:
                return True, f"{'at least ' if units is None else ''}{n} units, so not a {names} building"
            return None, "units not in data"
        if btype is None:
            return None, "the building type not in data"
        return compare(btype, op, value), f"{btype.replace('_', ' ')} per the assessor"

    if field == "funding" and facts.get("funding") == "subsidized":
        # The assessor says the building is subsidised. Test values are free text
        # ("deed_restricted", "public_housing", "market_rate"); map them to our two categories.
        def canon(v):
            v = str(v).lower()
            return "subsidized" if re.search(r"subsid|afford|deed|public|section|government|regulated", v) else \
                   "market_rate" if "market" in v else v
        vals = [canon(v) for v in value] if isinstance(value, list) else canon(value)
        known = {"subsidized", "market_rate"}
        if (set(vals) <= known) if isinstance(vals, list) else (vals in known):
            ok = compare("subsidized", op, vals)
            return ok, f"assessor marks the building as subsidised housing ('{facts.get('use_description')}')"
        # A specific programme (e.g. "DND-funded / IDP units") is not the same as "subsidised": unknown.

    # owner_type, tenancy_months, funding, other: not in the data
    d = test.get("defeated_if")
    if d:
        actual = {"units": units, "year_built": yb, "building_type": btype}.get(d["field"])
        exc = test.get("phrase") or field.replace("_", " ")
        if actual is not None and compare(actual, d["op"], d["value"]):
            what = f"{actual} units" if d["field"] == "units" else f"built {actual}" if d["field"] == "year_built" else f"{actual} per the assessor"
            return True, f"{what}, so the exemption for {exc} cannot apply"
        if d["field"] == "units" and units is None and facts.get("units_min") and not NO_UNITS_FLOOR \
                and compare_with_floor(facts["units_min"], d["op"], d["value"]):
            return True, f"at least {facts['units_min']} units per the assessor description, so the exemption for {exc} cannot apply"
    return None, f"{missing_fact(field)} not in data"


STRICT_UNKNOWN = False   # --strict-unknown: use/funding niche exemptions also answer unknown when data is silent
# Stress-test switches (instructions/stress_test.md): alternative keys, never the default policy.
LENIENT_PLAUSIBLE = False     # --lenient-plausible: plausible exemptions resolve as applies instead of unknown
CUTOFF_YEAR_APPLIES = False   # --cutoff-year-applies: a building from the cutoff year itself counts as covered
NO_PRECEDENCE = False         # --no-precedence: state rules keep their own result instead of 'superseded'
SHARED_RE = re.compile(r"shar\w*[^.;]{0,30}(kitchen|bath)|(kitchen|bath)[^.;]{0,30}shar", re.I)
# rulings_11 #3: TRUE owner-identity tests only (natural person, small landlord, owner-occupied 2-4 unit)
OWNER_RE = re.compile(r"natural person|small[- ]landlord|owner.?occup\w*|owner[- ]occupant|owns? (no more than|fewer than|not more than|"
                      r"one|two|three|four|\d)|individual owner|owner is an? (natural person|individual)|real estate investment trust|"
                      r"separately alienable|single.family", re.I)
# rulings_11 #1: a resident-owned cooperative or government-owned unit is a tenure/funding class, not an owner test
COOP_GOV_RE = re.compile(r"co-?operative|resident[- ](owned|controlled)|government[- ]owned|publicly[- ]owned|housing authority|hacla", re.I)
# rulings_11 #2: carve-outs inside the owner's own dwelling (shared kitchen/bath, roommate, room in an owner-occupied home)
OWN_UNIT_RE = re.compile(r"shar\w*[^.;]{0,30}(kitchen|bath)|(kitchen|bath)[^.;]{0,30}shar|roommate|"
                         r"room[s]? (rented|let|in)[^.;]{0,40}(owner|landlord)|owner.?occupied (home|house|single.family)|"
                         r"(owner|landlord)[^.;]{0,20}(principal residence|lives? in the (same )?unit)", re.I)


def niche_class(t: dict) -> str:
    """
    Which kind of niche exemption (rulings_09 refined by rulings_11):
      'use_or_funding'  use or funding of the building (hotels, dormitories, hospitals, public or
                        deed-restricted housing) and tenure classes that are not rental tenancies
                        (resident-owned cooperatives, government-owned units) -> applies with an assumption
      'own_unit'        a carve-out that can remove at most the owner's own dwelling (shared kitchen or
                        bath, a roommate, a room in an owner-occupied home) -> applies when the use code
                        shows 2+ units / apartments, unknown for single-family or unknown building type
      'owner_type'      a true owner-identity test (small-landlord, natural-person single-family/condo,
                        owner-occupied 2-4 unit within the threshold) -> unknown unless the use code defeats it
    """
    text = f"{t.get('source_text') or ''} {t.get('note') or ''} {t.get('value') or ''}"
    if t.get("field") == "funding":
        return "use_or_funding"
    if COOP_GOV_RE.search(text) and not OWNER_RE.search(re.sub(COOP_GOV_RE, "", text)):
        return "use_or_funding"
    if OWN_UNIT_RE.search(text):
        return "own_unit"
    if t.get("field") == "owner_type" or OWNER_RE.search(text):
        return "owner_type"
    return "use_or_funding"


PLACE = {"CA": "California", "NJ": "New Jersey", "MA": "Massachusetts"}
CATEGORY_NOUN = {"rent_increase_limits": "rent increase", "just_cause_eviction": "eviction", "security_deposits": "deposit",
                 "application_screening_fees": "fee", "screening_restrictions": "screening", "algorithmic_rent_setting": "algorithm"}
_MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def place(jurisdiction: str) -> str:
    """'CA' -> 'California'; 'San Francisco, CA' -> 'San Francisco'."""
    return PLACE.get(jurisdiction, jurisdiction.split(",")[0])


def fmt_date(iso: str | None) -> str:
    """'1978-10-01' -> '1 Oct 1978'; '2026-01' -> 'Jan 2026'; '2026' -> '2026'."""
    if not iso:
        return ""
    p = iso.split("-")
    try:
        if len(p) == 3:
            return f"{int(p[2])} {_MONTHS[int(p[1])]} {p[0]}"
        if len(p) == 2:
            return f"{_MONTHS[int(p[1])]} {p[0]}"
    except (ValueError, IndexError):
        pass
    return iso


def prose_dates(s: str) -> str:
    """Rewrite any ISO date inside prose as '1 Oct 1978'."""
    return re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", lambda m: fmt_date(m.group(0)), s or "")


def missing_fact(field: str) -> str:
    return {"year_built": "year built", "coo_date": "year built", "coo_age_years": "year built", "units": "the unit count",
            "owner_type": "owner identity", "funding": "affordable housing status", "building_type": "the building type",
            "tenancy_months": "the tenancy length"}.get(field, field.replace("_", " "))


def test_kind(t: dict) -> str:
    """The test's kind (rulings_06 #1); older cached tests without one are classified by field."""
    k = t.get("kind")
    if k:
        return k
    f = t.get("field")
    if f == "tenancy_months":
        return "timing"
    if f == "funding":
        return "niche_exemption"
    if f == "owner_type":
        return "plausible_exemption"
    return "coverage"


def run_group(t: dict, facts: dict, as_of: date) -> tuple[bool | None, str]:
    """An 'any_of' group passes if any member passes; fails only if every member fails."""
    results = [run_test(s, facts, as_of) for s in t.get("tests", [])]
    for ok, why in results:
        if ok is True:
            return True, why
    if results and all(ok is False for ok, _ in results):
        return False, "; ".join(why for _, why in results)
    return None, next((why for ok, why in results if ok is None), "no facts to test")


PHRASES_JSON = OUT.parent / "data" / "exemption_phrases.json"


def attach_phrases(coverage: dict) -> int:
    """
    rulings_12 section 7e: every coverage test carries a reviewed plain-language phrase from
    data/exemption_phrases.json (keyed rule id / test index, guarded by the start of the source text).
    Explanations and assumptions are composed from these phrases, never from raw spans. A test
    without a phrase, or whose source text no longer matches, stops the build.
    """
    phrases = json.loads(PHRASES_JSON.read_text(encoding="utf-8"))["phrases"]
    problems = []
    for rid, cov in coverage.items():
        for i, t in enumerate((cov or {}).get("tests") or []):
            entry = phrases.get(f"{rid}/{i}")
            hint = (t.get("source_text") or "")[:50]
            if not entry:
                problems.append(f"{rid}/{i}: no phrase (source: {hint!r})")
            elif not hint.startswith(entry["source_hint"][:len(hint)]):
                problems.append(f"{rid}/{i}: source text changed ({hint!r} vs hint {entry['source_hint']!r})")
            else:
                t["phrase"] = entry["phrase"]
    if problems:
        raise SystemExit("data/exemption_phrases.json is out of step with out/coverage.json:\n  " + "\n  ".join(problems))
    return len(phrases)


def join_or(items: list[str]) -> str:
    items = list(dict.fromkeys(items))
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} or {items[1]}"
    return "; ".join(items[:-1]) + f"; or {items[-1]}"


def evaluate_coverage(rule: dict, cov: dict | None, facts: dict, as_of: date) -> tuple[str, str, list[str]]:
    """
    Does this rule reach this property? Returns (result, explanation, assumptions, unknown_fields).

    Composition (rulings_12 sections 6, 7c, 7e), from reviewed phrases only:
      applies, nothing tested      "Applies to all residential rentals in <place>."
      applies, facts known         "Applies: 32 units, above the coverage threshold."
      applies with presumptions    "Applies unless the property is <phrase>. Built 1927, before the ... cutoff."
      timing                       "... Protection begins once <phrase>."
      unknown                      "Unknown: needs <fact>. Exemption that depends on it: <phrase>."
    assumptions carry "Not <phrase>" / "Once <phrase>" so the UI can list them.
    """
    tests = (cov or {}).get("tests") or []
    note = (cov or {}).get("explanation_note")
    unknown_fields: list[str] = []   # which facts left the answer unknown (used by the precedence step)
    everyone = f"Applies to all residential rentals in {place(rule['jurisdiction'])}."
    if (cov or {}).get("coverage_incomplete"):
        return "unknown", "Unknown: needs the ordinance's applicability text. Who the ordinance covers is not stated in the texts we hold.", [], ["coverage_text"]
    if not tests:
        return "applies", everyone + (f" {note[0].upper() + note[1:]}." if note else ""), [], []
    facts_true, unknowns, presumed, timing = [], [], [], []   # unknowns: (fact, why-it-matters)

    for t in tests:
        kind = test_kind(t)
        phrase = t.get("phrase") or "(phrase missing)"
        ok, why = (run_group if t.get("field") == "any_of" else run_test)(t, facts, as_of)
        sig = f"{t.get('field')} {t.get('op')} {t.get('value')}"
        if ok is False and t.get("on_fail") == "unknown":
            yb = facts.get("year_built")
            if t.get("field") == "coo_date" and t.get("op") in (">", ">=") and yb is not None:
                # The rule covers the NEWER side of a cutoff; this older building falls under the older-building
                # rule unless it is exempt from it, and that exemption status is not in parcel data.
                if rule["jurisdiction"] == "Los Angeles, CA" and rule["category"] == "just_cause_eviction":
                    reason = (f"this building is under the RSO (built {yb}), so the JCO applies only if the unit is exempt "
                              f"from the RSO; RSO exemption status is not in the data")
                else:
                    reason = (f"this building predates the {fmt_date(str(t.get('value'))[:10])} cutoff (built {yb}), so this rule "
                              f"applies only if the unit is exempt from the rule for older buildings; that exemption status is not in the data")
                ok, why = None, ("exemption status", reason)
            else:
                ok, why = None, ("the exemption details", f"{why[0].upper() + why[1:]}. The rule covers {phrase}, and whether the exemption has ended is not in the data")
        if ok is False and kind == "plausible_exemption":
            # The proxy says the exemption is possible (e.g. 2 units under a 1-2 unit owner-occupied
            # exemption); owner occupancy itself is not in the data, so the answer is unknown.
            ok, why = None, ("owner identity", f"Exemption that depends on it: {phrase}")
        if ok is False:
            return "exclude", why if isinstance(why, str) else why[1], [], []
        if ok is None:
            if kind == "plausible_exemption" and LENIENT_PLAUSIBLE:
                presumed.append(phrase)
                continue
            if kind == "timing":
                timing.append(phrase)
                continue
            if kind == "niche_exemption":
                cls = niche_class(t)
                if cls == "own_unit":
                    # rulings_11 #2: the carve-out removes at most the owner's own dwelling. A building the
                    # use code shows as 2+ units / apartments is still covered.
                    n = facts.get("units") if facts.get("units") is not None else (None if NO_UNITS_FLOOR else facts.get("units_min"))
                    multi = (n is not None and n >= 2) or facts.get("building_type") in ("apartments", "duplex", "mixed")
                    if multi:
                        presumed.append(phrase)
                        continue
                    unknowns.append(("the building type", f"Carve-out that depends on it: {phrase}"))
                    unknown_fields.append(sig)
                    continue
                if cls == "owner_type":
                    # Organisers' README section 4: owner names are excluded, so a true owner-type
                    # test is unknown unless something explains why the exception cannot apply.
                    unknowns.append(("owner identity", f"Exemption that depends on it: {phrase}"))
                    unknown_fields.append(sig)
                    continue
                if STRICT_UNKNOWN:
                    fact = "the tenure type" if COOP_GOV_RE.search(f"{t.get('source_text') or ''} {t.get('value') or ''}") else missing_fact(t.get("field"))
                    unknowns.append((fact, f"Exemption that depends on it: {phrase}"))
                    unknown_fields.append(sig)
                    continue
                presumed.append(phrase)
                continue
            if isinstance(why, tuple):
                unknowns.append(why)
            else:
                fact = missing_fact((t.get("tests") or [t])[0].get("field") if t.get("field") == "any_of" else t.get("field"))
                matters = f"The rule covers {phrase}" if kind == "coverage" else f"Exemption that depends on it: {phrase}"
                if facts.get("units_derived") and t.get("field") == "units":
                    matters += (f". The assessor building code '{facts['units_derived_source']}' suggests "
                                f"{facts['units_derived']} units (derived, unconfirmed)")
                unknowns.append((fact, matters))
            # signature of the unresolved test, so the precedence step can tell "the same
            # condition" (both 15-year windows) from "a different cutoff on the same fact"
            unknown_fields.append(sig)
            continue
        if why not in facts_true:
            facts_true.append(why)

    assumptions = [f"Not {p}" for p in dict.fromkeys(presumed)] + [f"Once {p}" for p in dict.fromkeys(timing)]
    if unknowns:
        fact, matters = unknowns[0]
        if fact == "exemption status":
            return "unknown", f"Unknown: {matters.rstrip('.')}.", assumptions, unknown_fields
        return "unknown", f"Unknown: needs {fact}. {matters.rstrip('.')}.", assumptions, unknown_fields
    facts_sentence = ("; ".join(facts_true[:2])[0].upper() + "; ".join(facts_true[:2])[1:] + ".") if facts_true else ""
    if presumed:
        text = f"Applies unless the property is {join_or(presumed)}."
        if facts_sentence:
            text += f" {facts_sentence}"
    elif facts_true:
        text = "Applies: " + "; ".join(facts_true[:2]).rstrip(".") + "."
    else:
        text = everyone
    if timing:
        text += f" Protection begins once {join_or(timing)}."
    if note:
        text += f" {note[0].upper() + note[1:]}."
    return "applies", prose_dates(text), assumptions, []

def rules_for(facts: dict, rules: list[dict]) -> list[dict]:
    local = f"{facts['city']}, {facts['state']}" if facts.get("city") else None
    return [r for r in rules if r["jurisdiction"] == facts["state"] or (local and r["jurisdiction"] == local)]


NOT_COVERED_MODE = "omit"   # or "unknown": report rows the coverage tests exclude, as unknown with the reason

_OPPOSITE = {"<=": ">", "<": ">=", ">": "<=", ">=": "<"}


def complementary(locals_: list[dict], coverage: dict) -> bool:
    """Do two local rules carry opposite coverage tests on the same cutoff (RSO <= 1978-10-01, JCO > 1978-10-01)?"""
    sigs = {}
    for l in locals_:
        for t in (coverage.get(l["team_rule_id"]) or {}).get("tests", []):
            if t.get("field") in ("coo_date", "year_built") and test_kind(t) == "coverage":
                sigs.setdefault((t["field"], str(t["value"])), set()).add(t["op"])
    return any(_OPPOSITE.get(op) in ops for ops in sigs.values() for op in ops)


def evaluate_address(facts: dict, rules: list[dict], coverage: dict, as_of: date) -> list[dict]:
    results, excluded = [], []
    for rule in rules_for(facts, rules):
        status, why = status_as_of(rule, as_of)
        assumptions, unknown_fields = [], []
        if status == "exclude":
            continue  # failed measures and negative findings never appear in an address answer
        if status is None:
            status, why, assumptions, unknown_fields = evaluate_coverage(rule, coverage.get(rule["team_rule_id"]), facts, as_of)
        row = {"team_rule_id": rule["team_rule_id"], "result": status, "explanation": why,
               "conflict_flag": False, "assumptions": assumptions, "_rule": rule, "_unknown": set(unknown_fields)}
        # An open legal question recorded on the rule itself (rulings_12 section 1) flags every row.
        preempt_note = rule["level"] == "state" and PREEMPT_RE.search(rule.get("interaction") or "")
        if rule.get("conflict_flag") and rule.get("conflict_note") and status != "exclude" and not preempt_note:
            row["conflict_flag"] = True
            row["explanation"] = f"{row['explanation'].rstrip('.')}. {rule['conflict_note']}"
        (excluded if status == "exclude" else results).append(row)

    # Precedence BEFORE cutoff tests (rulings_06 #2.1): where a local rule in the same category
    # applies, a yielding state rule is superseded whatever its own coverage test said, even
    # if that test excluded it (e.g. CA § 1946.2 in Los Angeles, where RSO + JCO cover everything).
    def category(r):
        return r["_rule"]["category"]
    for s in [] if NO_PRECEDENCE else [r for r in results + excluded if r["_rule"]["level"] == "state"
                                       and YIELDS_RE.search(r["_rule"].get("interaction") or "")]:
        locals_ = [r for r in results if r["_rule"]["level"] == "city" and category(r) == category(s)
                   and r["result"] in ("applies", "unknown")]
        applying = [l for l in locals_ if l["result"] == "applies"]
        if not applying and complementary(locals_, coverage):
            # Two local rules split the field between them (RSO: COO on/before 1978-10-01; JCO:
            # after it). Together they cover every residential unit, so whatever the year built
            # - even the cutoff year itself - a local rule governs (rulings_06 #2.1).
            applying = locals_
        if applying:
            loc = applying[0]
            s["result"] = "superseded"
            s["governed_by"] = loc["team_rule_id"]
            s["explanation"] = f"Governed instead by {loc['_rule']['title']}; the stricter local rule applies here."
            if len(applying) > 1 and all(l["result"] == "unknown" for l in applying):
                s["explanation"] = (f"Governed instead by {' and '.join(l['_rule']['title'] for l in applying)}; together they cover "
                                    f"every residential unit, so a local rule applies whatever the year built.")
            if s in excluded:
                excluded.remove(s); results.append(s)
        elif locals_ and s["result"] == "applies":
            loc = locals_[0]
            fact = missing_fact(next(iter(loc["_unknown"]), "the facts").split(" ")[0]) if loc["_unknown"] else "the deciding facts"
            s["result"] = "unknown"
            s["explanation"] = f"Unknown: needs {fact}. Whether {loc['_rule']['title']} governs here depends on it."
        elif locals_ and s["result"] == "unknown":
            # Both unknown for the SAME missing fact (e.g. CA § 1946.2 and the San Diego TPO both turn
            # on the 15-year new-construction test and the year built is missing): wherever the state
            # rule applies, the stricter local rule applies too, so the state rule is superseded.
            shared = [l for l in locals_ if l["_unknown"] and l["_unknown"] <= s["_unknown"]]
            if shared:
                loc = shared[0]
                s["result"] = "superseded"
                s["governed_by"] = loc["team_rule_id"]
                s["explanation"] = (f"Governed instead by {loc['_rule']['title']}; it shares the same coverage condition, so "
                                    f"wherever this rule applies the stricter local rule governs.")

    if NOT_COVERED_MODE == "unknown":
        for r in excluded:
            r["result"] = "unknown"
            r["explanation"] = "Does not appear to cover this property: " + r["explanation"]
            results.append(r)

    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(category(r), []).append(r)
    for cat, rs in by_cat.items():
        locals_ = [r for r in rs if r["_rule"]["level"] == "city" and r["result"] in ("applies", "unknown")]
        # Conflict: pre-empting state rule meets a local rule in the same category.
        # Cross-rule conflict pass, narrowed (rulings_12 section 1): only where the state rule's own
        # record states a possible preemption (conflict_flag on the record and preemption language).
        for s in [r for r in rs if r["_rule"]["level"] == "state"]:
            sr = s["_rule"]
            if sr.get("conflict_flag") and PREEMPT_RE.search(sr.get("interaction") or "") and locals_:
                s["conflict_flag"] = True
                if sr.get("conflict_note") and sr["conflict_note"] not in s["explanation"]:
                    s["explanation"] = f"{s['explanation'].rstrip('.')}. {sr['conflict_note']}"
                for loc in locals_:
                    loc["conflict_flag"] = True
                    if sr.get("conflict_note") and sr["conflict_note"] not in loc["explanation"]:
                        loc["explanation"] = f"{loc['explanation'].rstrip('.')}. {sr['conflict_note']}"
            elif locals_ and s["result"] == "applies":
                # State and city rules in the same category both apply and neither yields nor preempts:
                # not a conflict (e.g. the state fee ceiling plus Berkeley's stricter local fee limits).
                for loc in locals_:
                    if loc["result"] == "applies":
                        noun = CATEGORY_NOUN.get(cat, cat.replace('_', ' '))
                        sent = (f"State fee rules apply; {place(loc['_rule']['jurisdiction'])} adds stricter local limits."
                                if cat == "application_screening_fees" else f"State {noun} rules apply too; both are listed here.")
                        if sent not in loc["explanation"]:
                            loc["explanation"] = f"{loc['explanation'].rstrip('.')}. {sent}"
    for r in results:
        r["explanation"] = prose_dates(r["explanation"])
        r.pop("_rule"); r.pop("_unknown", None)
    return results


def load_inputs():
    rules = json.loads(RULES_FULL.read_text(encoding="utf-8"))["rules"]
    coverage = json.loads(COVERAGE_JSON.read_text(encoding="utf-8")) if COVERAGE_JSON.exists() else {}
    attach_phrases(coverage)
    juris = json.loads(JURIS_JSON.read_text(encoding="utf-8"))
    with open(ADDRESSES_CSV, newline="", encoding="utf-8") as f:
        addresses = list(csv.DictReader(f))
    return rules, coverage, juris, addresses


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=DEFAULT_QUERY_DATE)
    ap.add_argument("--address", nargs="*", help="only these address ids")
    ap.add_argument("--out", default=None)
    ap.add_argument("--use-derived-units", action="store_true",
                    help="treat unit counts parsed from NJ MOD-IV building codes as real; writes lookups_derived.json")
    ap.add_argument("--no-units-floor", action="store_true",
                    help="ignore unit minimums stated in words in the assessor description ('5+ units')")
    ap.add_argument("--report-not-covered", action="store_true",
                    help="also report rules whose coverage tests exclude the property, as unknown with the reason")
    ap.add_argument("--strict-unknown", action="store_true",
                    help="use/funding niche exemptions (hotels, subsidised housing, ...) also answer unknown when data is silent")
    ap.add_argument("--lenient-plausible", action="store_true", help="stress key: plausible exemptions resolve as applies")
    ap.add_argument("--cutoff-year-applies", action="store_true", help="stress key: cutoff-year buildings count as covered")
    ap.add_argument("--no-precedence", action="store_true", help="stress key: no 'superseded'; state rules keep their own result")
    args = ap.parse_args()
    global NO_UNITS_FLOOR, NOT_COVERED_MODE, STRICT_UNKNOWN, LENIENT_PLAUSIBLE, CUTOFF_YEAR_APPLIES, NO_PRECEDENCE
    NO_UNITS_FLOOR = args.no_units_floor
    STRICT_UNKNOWN = args.strict_unknown
    LENIENT_PLAUSIBLE = args.lenient_plausible
    CUTOFF_YEAR_APPLIES = args.cutoff_year_applies
    NO_PRECEDENCE = args.no_precedence
    NOT_COVERED_MODE = "unknown" if args.report_not_covered else "omit"
    as_of = date.fromisoformat(args.as_of)

    rules, coverage, juris, addresses = load_inputs()
    if args.address:
        addresses = [a for a in addresses if a["address_id"] in set(args.address)]
    lookups, audit, counts, derived_rows = {}, [], {}, []
    for row in addresses:
        facts = address_facts(row, juris.get(row["address_id"], {}), args.use_derived_units)
        if facts.get("units_derived"):
            derived_rows.append({"address_id": row["address_id"], "city": facts["city"], "raw_code": facts["units_derived_source"],
                                 "units_derived": facts["units_derived"], "rule": "sum of all 'NNU' groups in the MOD-IV code"})
        res = evaluate_address(facts, rules, coverage, as_of)
        lookups[row["address_id"]] = res
        for r in res:
            counts[r["result"]] = counts.get(r["result"], 0) + 1
            audit.append({"address_id": row["address_id"], "city": facts["city"], "team_rule_id": r["team_rule_id"],
                          "result": r["result"], "conflict_flag": r["conflict_flag"],
                          "assumptions": " | ".join(r.get("assumptions") or []), "deciding_facts": r["explanation"]})
    out = {"as_of": args.as_of, "lookups": lookups}
    OUT.mkdir(parents=True, exist_ok=True)
    full_run = not args.address
    if args.out:
        out_path = args.out
    elif args.use_derived_units:
        out_path = str(OUT / ("lookups_derived.json" if args.as_of == DEFAULT_QUERY_DATE else f"lookups_derived_{args.as_of}.json"))
    else:
        out_path = str(LOOKUPS_JSON if args.as_of == DEFAULT_QUERY_DATE else OUT / f"lookups_{args.as_of}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    if full_run and args.as_of == DEFAULT_QUERY_DATE and not args.use_derived_units:
        with open(AUDIT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["address_id", "city", "team_rule_id", "result", "conflict_flag", "assumptions", "deciding_facts"])
            w.writeheader(); w.writerows(audit)
        with open(OUT / "derived_units.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["address_id", "city", "raw_code", "units_derived", "rule"])
            w.writeheader(); w.writerows(derived_rows)
    n_rows = sum(len(v) for v in lookups.values())
    n_assumed = sum(1 for v in lookups.values() for r in v if r.get("assumptions"))
    print(f"{len(lookups)} addresses as of {args.as_of}" + (" (derived units)" if args.use_derived_units else "")
          + f": {counts} -> {out_path}")
    print(f"unknown rate {counts.get('unknown', 0)}/{n_rows} = {100 * counts.get('unknown', 0) / max(n_rows, 1):.1f}%; "
          f"rows relying on a presumption (assumptions): {n_assumed}")
    if args.use_derived_units and full_run and LOOKUPS_JSON.exists():
        base = json.loads(LOOKUPS_JSON.read_text(encoding="utf-8"))["lookups"]
        changed = sum(1 for a, rs in lookups.items()
                      for r in rs if next((b for b in base.get(a, []) if b["team_rule_id"] == r["team_rule_id"]), {}).get("result") != r["result"])
        print(f"results changed by derived units: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
