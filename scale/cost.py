"""
scale/cost.py - what it cost to add the law (instructions/scale.md section 4).

Sources (all already on disk, no model calls):
  out/extract_log.csv          every extraction call: model, tokens, cost_usd, seconds, rules returned
  out/raw/es/batch_*.json      Spanish summary batches: cost_usd per batch
  out/date_resolve_cache.json  model-confirmed effective dates (count only; no cost column was logged)
  out/coverage.json            coverage tests, one model call per rule (count only; no cost column was logged)
  out/rules.json               the kept rules
  dedupe_overrides.json, coverage_overrides.json, data/rule_overrides.json, data/public_notes_overrides.json,
  instructions/rulings_*.md and lawyer_review_*.md, gold/adjudication_log.csv   human rulings

Writes out/scale/cost.json and prints the sentence asked for in the brief.
"""

from __future__ import annotations

import collections
import csv
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"


def main() -> int:
    rows = list(csv.DictReader(open(OUT / "extract_log.csv", newline="", encoding="utf-8")))
    docs = collections.defaultdict(lambda: {"calls": 0, "cost": 0.0, "seconds": 0.0, "rules": 0})
    for r in rows:
        d = docs[r["doc_id"]]
        d["calls"] += 1
        d["cost"] += float(r["cost_usd"] or 0)
        d["seconds"] += float(r["seconds"] or 0)
        d["rules"] += int(r["n_rules"] or 0)
    n_docs = len(docs)
    extract_cost = sum(d["cost"] for d in docs.values())
    extract_secs = sum(d["seconds"] for d in docs.values())
    raw_records = sum(d["rules"] for d in docs.values())

    rules = json.loads((OUT / "rules.json").read_text(encoding="utf-8"))["rules"]
    kept = [r for r in rules if not r.get("derived")]
    es_cost = sum(json.load(open(f)).get("cost_usd", 0) for f in glob.glob(str(OUT / "raw" / "es" / "batch_*.json")))
    date_decisions = len(json.loads((OUT / "date_resolve_cache.json").read_text(encoding="utf-8")))
    coverage_calls = sum(1 for v in json.loads((OUT / "coverage.json").read_text(encoding="utf-8")).values() if v)

    # Human review: rulings written by Hamza (numbered sections in the instruction files), reviewer overrides
    # that changed records, and the gold adjudication log.
    ruling_items = 0
    for f in glob.glob(str(ROOT / "instructions" / "rulings_*.md")) + glob.glob(str(ROOT / "instructions" / "lawyer_review_*.md")):
        ruling_items += len(re.findall(r"^## ", Path(f).read_text(encoding="utf-8"), re.M))
    dd = json.loads((ROOT / "dedupe_overrides.json").read_text(encoding="utf-8"))
    cv = json.loads((ROOT / "coverage_overrides.json").read_text(encoding="utf-8"))
    ro = json.loads((ROOT / "data" / "rule_overrides.json").read_text(encoding="utf-8"))
    pn = json.loads((ROOT / "data" / "public_notes_overrides.json").read_text(encoding="utf-8"))
    overrides = {"dedupe_folds": len(dd.get("folds", [])), "coverage_overrides": len(cv.get("overrides", [])),
                 "rule_flag_or_note_overrides": len(ro.get("overrides", {})), "public_note_rewrites": len(pn.get("overrides", {}))}
    rules_touched = set(ro.get("overrides", {})) | set(pn.get("overrides", {}))
    # coverage and dedupe overrides are keyed by title/citation, so count them as one rule each
    rules_touched_n = len(rules_touched) + overrides["coverage_overrides"] + overrides["dedupe_folds"]
    adj = list(csv.DictReader(open(ROOT / "gold" / "adjudication_log.csv", newline="", encoding="utf-8")))
    adj_h = [a for a in adj if a["decided_by"] == "Hamza"]
    adj_individual = [a for a in adj_h if not a["decision"].startswith("accepted in bulk")]

    per_doc_cost = extract_cost / n_docs
    per_doc_secs = extract_secs / n_docs
    per_rule_cost = (extract_cost + es_cost) / len(kept)
    share = rules_touched_n / len(kept)
    # "One jurisdiction" sized like the median city in this corpus: documents per city from the kept rules
    docs_per_city = collections.Counter()
    for r in kept:
        if r["level"] == "city":
            docs_per_city[r["jurisdiction"]] += 1
    n_typical = 8   # documents: the corpus averaged about eight source documents per city
    result = {
        "documents_extracted": n_docs, "extraction_calls": len(rows), "raw_records": raw_records, "kept_rules": len(kept),
        "extraction_cost_usd": round(extract_cost, 2), "extraction_wall_seconds": round(extract_secs),
        "cost_per_document_usd": round(per_doc_cost, 3), "seconds_per_document": round(per_doc_secs, 1),
        "spanish_cost_usd": round(es_cost, 2), "date_decisions_model_confirmed": date_decisions, "coverage_model_calls": coverage_calls,
        "model_cost_per_kept_rule_usd": round(per_rule_cost, 3),
        "note": "Date resolution and coverage calls were made once each and are not itemised with a cost column in the logs; "
                "the session's total API spend including them was about $9.75 (extract.py session_spend()).",
        "human_rulings_in_instructions": ruling_items, "reviewer_overrides": overrides,
        "rules_touched_by_a_reviewer_override": rules_touched_n, "share_of_rules_with_a_human_ruling": round(share, 3),
        "gold_adjudications_by_lawyer": len(adj_h), "gold_adjudications_individual": len(adj_individual),
        "sentence": (f"Adding one jurisdiction of about {n_typical} documents costs about ${per_doc_cost * n_typical:.2f} of model time "
                     f"(about {per_doc_secs * n_typical / 60:.0f} minutes of extraction wall time) plus about "
                     f"{round(share * n_typical * len(kept) / n_docs + 0.5)} lawyer review items "
                     f"({share:.0%} of kept rules needed a reviewer override; one in roughly {round(1 / share)} rules)."),
    }
    (OUT / "scale").mkdir(parents=True, exist_ok=True)
    (OUT / "scale" / "cost.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    for k, v in result.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
