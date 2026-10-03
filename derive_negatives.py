"""
derive_negatives.py - Module A, step 2b: say explicitly where NO rule was found.

Plain-language summary
----------------------
The challenge covers 13 jurisdictions (3 states, 10 cities) x 6 categories =
78 cells. For every cell where verify.py left no rule in force, this script
writes a "negative finding": a record saying "No rule at this level". If a
state law in the corpus expressly bars local rules in that category (e.g.
M.G.L. c. 40P bars local rent control in Massachusetts), the negative finding
cites and quotes that law with confidence 0.8; otherwise it says "None found
in corpus" with confidence 0.5. Pending bills and failed measures in the cell
are mentioned in the note and are always kept as their own records.

This is automated reasoning over the extracted corpus, not hand-coded law.
(Hamza ruling 2026-10-04 #6.)

Outputs
-------
  out/negatives.json      all derived negative findings
  out/rules_full.json     verified rules + all derived negatives (for Module B)
  out/rules.json          updated: derived negatives that satisfy the schema
                          (those with a quoted span and URL) are appended

Usage:  python derive_negatives.py
"""

from __future__ import annotations

import json
import re
import sys

from jsonschema import Draft202012Validator

from common import CATEGORIES, OUT, SCHEMA_JSON

RULES_JSON = OUT / "rules.json"
NEGATIVES_JSON = OUT / "negatives.json"
FULL_JSON = OUT / "rules_full.json"

STATES = ["CA", "NJ", "MA"]
CITIES = {
    "Los Angeles, CA": "CA", "San Francisco, CA": "CA", "San Diego, CA": "CA",
    "Berkeley, CA": "CA", "Santa Ana, CA": "CA",
    "Jersey City, NJ": "NJ", "Hoboken, NJ": "NJ", "Newark, NJ": "NJ",
    "Boston, MA": "MA", "Cambridge, MA": "MA",
}
ENACTED = ("in_force", "not_yet_effective")

# A state rule "bars local rules" if it talks about local government AND about
# prohibiting / preempting. Checked against the rule's text fields.
LOCAL_RE = re.compile(r"\b(local|municipal\w*|city|cities|town|towns|county|counties)\b", re.I)
BAR_RE = re.compile(r"\b(bar|bars|barred|prohibit\w*|pre-?empt\w*|may not (enact|adopt)|shall not (enact|adopt)|"
                    r"no (city|town|municipality)|supersede\w*)\b", re.I)


def rule_text(r: dict) -> str:
    return " ".join(str(r.get(k) or "") for k in ("title", "requirement", "key_value", "interaction", "notes"))


def find_preempting_state_rule(rules: list[dict], state: str, category: str) -> dict | None:
    """A state-level record in the same category whose text says it bars local rules."""
    cands = [r for r in rules
             if r["jurisdiction"] == state and r["category"] == category and r["status"] in ENACTED]
    for r in cands:
        t = rule_text(r)
        if LOCAL_RE.search(t) and BAR_RE.search(t):
            return r
    return None


def label(category: str) -> str:
    return category.replace("_", " ")


def main() -> int:
    if not RULES_JSON.exists():
        print("out/rules.json missing; run verify.py first", file=sys.stderr)
        return 1
    rules = json.loads(RULES_JSON.read_text(encoding="utf-8"))["rules"]
    # Idempotent: drop any derived negatives from a previous run before re-deriving.
    rules = [r for r in rules if not r.get("derived")]
    validator = Draft202012Validator(json.loads(SCHEMA_JSON.read_text(encoding="utf-8")))

    cells = [(s, "state", s) for s in STATES] + [(c, "city", st) for c, st in CITIES.items()]
    negatives, n = [], 0
    for jurisdiction, level, state in cells:
        for category in CATEGORIES:
            here = [r for r in rules if r["jurisdiction"] == jurisdiction and r["category"] == category]
            if any(r["status"] in ENACTED and not r.get("negative_finding") for r in here):
                continue  # a rule applies here
            if any(r.get("negative_finding") for r in here):
                continue  # the model already documented the absence from a source
            pending = [r for r in here if r["status"] == "pending"]
            failed = [r for r in here if r["status"] == "failed"]

            n += 1
            rec = {
                "team_rule_id": f"n-{n:04d}",
                "jurisdiction": jurisdiction, "level": level, "category": category,
                "status": "in_force",
                "title": "No rule at this level",
                "requirement": f"No {label(category)} rule at the {jurisdiction} level was found in the corpus.",
                "key_value": f"No {label(category)} rule found at {jurisdiction} level in the corpus",
                "coverage_conditions": None, "exemptions": None, "overrides": [], "interaction": None,
                "effective_date": None,
                "citation": "None found in corpus", "source_doc_id": None, "source_url": None,
                "quoted_span": None, "confidence": 0.5, "conflict_flag": False, "conflict_note": None,
                "negative_finding": True, "derived": True, "notes": None,
            }
            bar = find_preempting_state_rule(rules, state, category) if level == "city" else None
            if bar:
                rec.update({
                    "requirement": f"State law bars local {label(category)} rules: {bar['title']}.",
                    "citation": bar["citation"], "source_doc_id": bar["source_doc_id"],
                    "source_url": bar["source_url"], "quoted_span": bar["quoted_span"],
                    "confidence": 0.8, "interaction": f"Derived from state rule {bar['team_rule_id']}.",
                    "overrides": [bar["team_rule_id"]],
                })
            notes = []
            if pending:
                notes.append("Pending: " + "; ".join(f"{r['citation']} ({r['team_rule_id']})" for r in pending))
            if failed:
                notes.append("Failed/struck: " + "; ".join(f"{r['citation']} ({r['team_rule_id']})" for r in failed))
            if notes:
                rec["notes"] = " ".join(notes)
                rec["conflict_flag"] = bool(pending)
                rec["conflict_note"] = "A pending measure could change this." if pending else None
            negatives.append(rec)

    schema_ok = [r for r in negatives if not list(validator.iter_errors(r))]
    OUT.mkdir(parents=True, exist_ok=True)
    NEGATIVES_JSON.write_text(json.dumps({"negatives": negatives}, indent=2, ensure_ascii=False), encoding="utf-8")
    FULL_JSON.write_text(json.dumps({"rules": rules + negatives}, indent=2, ensure_ascii=False), encoding="utf-8")
    RULES_JSON.write_text(json.dumps({"rules": rules + schema_ok}, indent=2, ensure_ascii=False), encoding="utf-8")

    backed = sum(1 for r in negatives if r["confidence"] == 0.8)
    print(f"Cells: {len(cells) * len(CATEGORIES)}; derived negative findings: {len(negatives)} "
          f"({backed} backed by a state pre-emption rule, {len(negatives) - backed} 'none found in corpus')")
    print(f"  -> {NEGATIVES_JSON.name} (all), {FULL_JSON.name} (rules + all negatives), "
          f"{RULES_JSON.name} (+{len(schema_ok)} schema-valid negatives)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
