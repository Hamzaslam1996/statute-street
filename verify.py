"""
verify.py - Module A, step 2: check Claude's raw output and build rules.json.

Plain-language summary
----------------------
Claude's answers in out/raw/ are drafts. This script:
  1. Rejects any record whose quoted_span is not an exact passage of the
     source document (we forgive only whitespace, quote-mark and dash styles).
     If a document has rejected records we ask Claude once more, telling it
     which quotes failed; anything still failing is dropped and logged.
  2. Works out `status` itself from the effective date and the query date,
     instead of trusting the model (pending bills and failed measures keep
     the model's label, since there is no date to compute from).
  3. Attaches the document id, URL and retrieval date from the file header.
  4. Lowers confidence for secondary sources (law firm, news, mirrors).
  5. Validates every record against the organisers' schema.
  6. Removes duplicates (same jurisdiction + category + citation) and writes
     out/rules.json in the submission format {"rules": [...]}.

Usage
-----
    python verify.py                 # all cached docs, query date 2026-10-01
    python verify.py --no-retry      # never call the API
    python verify.py --query-date 2027-07-02
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date

from jsonschema import Draft202012Validator
from rapidfuzz import fuzz

from common import (DEFAULT_QUERY_DATE, OUT, RAW_DIR, SCHEMA_JSON, Doc,
                    list_docs, normalise, normalise_citation)

RULES_JSON = OUT / "rules.json"
VERIFY_CSV = OUT / "verify_log.csv"
SUMMARY_JSON = OUT / "verify_summary.json"

# Confidence ceiling for records whose only support is a secondary source.
SECONDARY_CONFIDENCE_CAP = 0.7


# ---------------------------------------------------------------------------
# 1. Quote check
# ---------------------------------------------------------------------------
def span_in_doc(span: str, doc_norm: str) -> tuple[bool, float]:
    """
    Is the quoted span really in the document?
    Returns (exact match after normalisation, fuzzy score 0-100 for diagnostics).
    """
    s = normalise(span or "")
    if len(s) < 20:
        return False, 0.0
    if s in doc_norm:
        return True, 100.0
    # Not exact. Compute how close it was, so the log explains the failure.
    score = fuzz.partial_ratio(s, doc_norm) if len(s) < 2000 else 0.0
    return False, round(float(score), 1)


# ---------------------------------------------------------------------------
# 2. Status from dates
# ---------------------------------------------------------------------------
DATE_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")


def date_bounds(eff: str) -> tuple[date, date] | None:
    """'2026' -> (2026-01-01, 2026-12-31); '2026-04' -> (2026-04-01, 2026-04-30); full date -> (d, d)."""
    m = DATE_RE.match(eff or "")
    if not m:
        return None
    y, mo, d = int(m.group(1)), m.group(2), m.group(3)
    try:
        if d:
            dt = date(y, int(mo), int(d))
            return dt, dt
        if mo:
            mo_i = int(mo)
            last = date(y + (mo_i == 12), (mo_i % 12) + 1, 1).toordinal() - 1
            return date(y, mo_i, 1), date.fromordinal(last)
        return date(y, 1, 1), date(y, 12, 31)
    except ValueError:
        return None


def compute_status(rec: dict, query: date) -> tuple[str, str | None]:
    """
    Decide the status of an enacted rule from its effective date.
    Returns (status, note). The note explains any uncertainty.
    """
    model_status = rec.get("status")
    if model_status in ("pending", "failed"):
        return model_status, None            # nothing to compute: not an enacted law

    eff = rec.get("effective_date")
    if not eff:
        if model_status == "not_yet_effective":
            return "not_yet_effective", "Model says not yet effective but gave no effective date; check."
        return "in_force", None               # long-standing law with no stated start date

    bounds = date_bounds(eff)
    if bounds is None:
        return "in_force", f"Effective date '{eff}' not understood; status not recomputed."
    start, end = bounds
    if start > query:
        return "not_yet_effective", None
    if end <= query:
        return "in_force", None
    # The date is imprecise (e.g. just a year) and the query date falls inside it.
    return "in_force", f"Effective date '{eff}' is imprecise and spans the query date {query}; status uncertain."


# ---------------------------------------------------------------------------
# 3-5. Build a submission record from a raw one
# ---------------------------------------------------------------------------
def build_record(raw: dict, doc: Doc, query: date) -> dict:
    status, note = compute_status(raw, query)
    confidence = raw.get("confidence")
    notes = [n for n in [raw.get("conflict_note"), note] if n]
    if doc.is_secondary:
        if confidence is None or confidence > SECONDARY_CONFIDENCE_CAP:
            confidence = SECONDARY_CONFIDENCE_CAP
        notes.append(f"Secondary source ({doc.source_type}); confirm against the official text.")

    eff = raw.get("effective_date")
    if eff and not DATE_RE.match(eff):
        eff = None  # schema requires YYYY, YYYY-MM or YYYY-MM-DD

    return {
        "team_rule_id": None,  # assigned after dedupe
        "jurisdiction": raw.get("jurisdiction"),
        "level": raw.get("level"),
        "category": raw.get("category"),
        "status": status,
        "title": raw.get("title"),
        "requirement": raw.get("requirement"),
        "key_value": raw.get("key_value"),
        "coverage_conditions": raw.get("coverage_conditions"),
        "exemptions": raw.get("exemptions"),
        "overrides": [],
        "interaction": raw.get("interaction"),
        "effective_date": eff,
        "citation": raw.get("citation"),
        "source_doc_id": doc.doc_id,
        "source_url": doc.source_url,
        "quoted_span": raw.get("quoted_span"),
        "confidence": confidence,
        "conflict_flag": bool(raw.get("conflict_flag")) or bool(note),
        "conflict_note": " ".join(notes) if notes else None,
        "retrieved_at": doc.retrieved_date,
    }


def dedupe(records: list[dict]) -> tuple[list[dict], list[tuple[dict, dict]]]:
    """
    Keep one record per (jurisdiction, category, citation). Prefer official
    sources, then higher confidence. Returns (kept, [(dropped, kept_instead)]).
    """
    kept: dict[tuple, dict] = {}
    dropped = []
    for r in records:
        key = ((r["jurisdiction"] or "").lower(), r["category"], normalise_citation(r["citation"]))
        if key not in kept:
            kept[key] = r
            continue
        cur = kept[key]
        better = ((not r["_secondary"], r["confidence"] or 0) >
                  (not cur["_secondary"], cur["confidence"] or 0))
        if better:
            dropped.append((cur, r))
            kept[key] = r
        else:
            dropped.append((r, cur))
    return list(kept.values()), dropped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Verify raw extractions and write out/rules.json.")
    ap.add_argument("--query-date", default=DEFAULT_QUERY_DATE)
    ap.add_argument("--no-retry", action="store_true", help="do not call the API for failed quotes")
    ap.add_argument("--model", default=None, help="model for the retry (default: same as original)")
    args = ap.parse_args()
    query = date.fromisoformat(args.query_date)

    docs = list_docs()
    schema = json.loads(SCHEMA_JSON.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    raw_files = sorted(p for p in RAW_DIR.glob("D*.json") if ".attempt" not in p.name)
    if not raw_files:
        print("No raw output in out/raw/. Run extract.py first.", file=sys.stderr)
        return 1

    log_rows, candidates = [], []
    counts = {"docs": 0, "raw_records": 0, "span_pass": 0, "span_fail_first": 0,
              "span_pass_after_retry": 0, "dropped_span": 0, "dropped_schema": 0,
              "dropped_duplicate": 0, "retries": 0}

    for path in raw_files:
        raw = json.loads(path.read_text(encoding="utf-8"))
        doc = docs.get(raw["doc_id"])
        if doc is None:
            print(f"  {raw['doc_id']}: source text not found, skipping", file=sys.stderr)
            continue
        counts["docs"] += 1
        doc_norm = normalise(doc.body)

        def check(records: list[dict], attempt: int) -> tuple[list[dict], list[dict]]:
            good, bad = [], []
            for r in records:
                ok, score = span_in_doc(r.get("quoted_span", ""), doc_norm)
                log_rows.append({"doc_id": doc.doc_id, "attempt": attempt, "citation": r.get("citation"),
                                 "title": r.get("title"), "span_ok": ok, "fuzzy_score": score,
                                 "span_preview": (r.get("quoted_span") or "")[:80]})
                (good if ok else bad).append(r)
            return good, bad

        records = raw.get("rules", [])
        counts["raw_records"] += len(records)
        good, bad = check(records, attempt=raw.get("attempt", 1))
        counts["span_pass"] += len(good)
        counts["span_fail_first"] += len(bad)

        # One retry per document, telling the model which quotes failed.
        if bad and not args.no_retry and raw.get("attempt", 1) < 2:
            from extract import extract_doc  # imported here so --no-retry never needs the API
            counts["retries"] += 1
            feedback = "\n".join(f"- NOT FOUND: {json.dumps(r.get('quoted_span'))}" for r in bad)
            print(f"  {doc.doc_id}: {len(bad)} span(s) failed; retrying once with feedback ...")
            raw2 = extract_doc(doc, args.model or raw.get("model"), attempt=2, feedback=feedback)
            good2, bad2 = check(raw2.get("rules", []), attempt=2)
            counts["span_pass_after_retry"] += len(good2)
            counts["dropped_span"] += len(bad2)
            good, bad = good2, bad2   # the retry replaces the first attempt wholesale
        else:
            counts["dropped_span"] += len(bad)

        for r in good:
            rec = build_record(r, doc, query)
            rec["_secondary"] = doc.is_secondary
            candidates.append(rec)

    kept, dropped_dups = dedupe(candidates)
    counts["dropped_duplicate"] = len(dropped_dups)
    for d, k in dropped_dups:
        log_rows.append({"doc_id": d["source_doc_id"], "attempt": "-", "citation": d["citation"],
                         "title": d["title"], "span_ok": True, "fuzzy_score": 100.0,
                         "span_preview": f"DUPLICATE of {k['source_doc_id']} {k['citation']}"})

    # Stable ordering and ids, then schema validation.
    kept.sort(key=lambda r: ((r["jurisdiction"] or ""), r["category"], (r["citation"] or "")))
    final = []
    for i, rec in enumerate(kept, start=1):
        rec.pop("_secondary", None)
        rec["team_rule_id"] = f"r-{i:04d}"
        errors = sorted(validator.iter_errors(rec), key=lambda e: list(e.path))
        if errors:
            counts["dropped_schema"] += 1
            msg = "; ".join(f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors)
            print(f"  {rec['source_doc_id']} {rec['citation']}: schema error -> {msg}", file=sys.stderr)
            continue
        final.append(rec)

    OUT.mkdir(parents=True, exist_ok=True)
    # Exactly the submission template shape: {"rules": [...]}
    RULES_JSON.write_text(json.dumps({"rules": final}, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    with open(VERIFY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["doc_id", "attempt", "citation", "title", "span_ok",
                                          "fuzzy_score", "span_preview"])
        w.writeheader()
        w.writerows(log_rows)
    counts["final_rules"] = len(final)
    counts["query_date"] = args.query_date
    attempted = counts["raw_records"]
    counts["span_pass_rate_first_attempt"] = round(counts["span_pass"] / attempted, 3) if attempted else None
    SUMMARY_JSON.write_text(json.dumps(counts, indent=2), encoding="utf-8")

    print(f"\nDocuments: {counts['docs']}   raw records: {attempted}")
    print(f"Quote check: {counts['span_pass']} passed, {counts['span_fail_first']} failed on first attempt"
          + (f"; {counts['retries']} doc(s) retried, {counts['span_pass_after_retry']} passed after retry"
             if counts["retries"] else ""))
    print(f"Dropped: {counts['dropped_span']} bad quote, {counts['dropped_duplicate']} duplicate, "
          f"{counts['dropped_schema']} schema")
    print(f"Final rules: {len(final)} -> {RULES_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
