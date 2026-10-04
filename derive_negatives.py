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
# Sentences that say a law does NOT bar local rules ("no stated preemption", "does not preempt",
# "local ordinances are not addressed"). Written so that "No city or town may enact" still counts.
NEGATED_RE = re.compile(r"\b(no (stated|express|explicit)? ?pre-?emption|not pre-?empt\w*|does not|do not|"
                        r"not addressed|not stated|without pre-?empt\w*|silent on)\b", re.I)


def rule_text(r: dict) -> str:
    return " ".join(str(r.get(k) or "") for k in ("title", "requirement", "key_value", "interaction", "notes"))


def find_preempting_state_rule(rules: list[dict], state: str, category: str) -> dict | None:
    """
    A state-level record in the same category, already in force, with a sentence
    that both mentions local government and bars/pre-empts it (e.g. "No city or
    town may enact ... rent control"). A law that is not yet in force cannot bar
    anything today, so not_yet_effective rules do not count.
    """
    cands = [r for r in rules
             if r["jurisdiction"] == state and r["category"] == category and r["status"] == "in_force"]
    for r in cands:
        for sentence in re.split(r"(?<=[.;])\s+", rule_text(r)):
            if NEGATED_RE.search(sentence):
                continue  # "no stated preemption of local rules" is the opposite of a bar
            if LOCAL_RE.search(sentence) and BAR_RE.search(sentence):
                return r
    return None


def label(category: str) -> str:
    return category.replace("_", " ")


STATE_NAME = {"CA": "California", "NJ": "New Jersey", "MA": "Massachusetts"}
STATE_ES = {"CA": "California", "NJ": "Nueva Jersey", "MA": "Massachusetts"}
LABEL_ES = {"rent_increase_limits": "límites a los aumentos de renta", "just_cause_eviction": "causa justa de desalojo",
            "security_deposits": "depósitos de garantía", "application_screening_fees": "cuotas de solicitud",
            "screening_restrictions": "evaluación de solicitantes", "algorithmic_rent_setting": "fijación algorítmica de rentas"}


def city_name(jurisdiction: str) -> str:
    return jurisdiction.split(",")[0]


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
            # Public wording (rulings_12 section 7c): never the word "corpus", plain category names.
            if level == "city":
                requirement = f"No {label(category)} rule at the {city_name(jurisdiction)} level; state law applies."
                requirement_es = f"No hay ninguna regla de {LABEL_ES[category]} a nivel de {city_name(jurisdiction)}; se aplica la ley estatal."
                key_value = "No city rule; state law applies"
            else:
                requirement = f"No {label(category)} rule at the state level in {STATE_NAME.get(state, state)}."
                requirement_es = f"No hay ninguna regla estatal de {LABEL_ES[category]} en {STATE_ES.get(state, state)}."
                key_value = "No state rule"
            rec = {
                "team_rule_id": f"n-{n:04d}",
                "jurisdiction": jurisdiction, "level": level, "category": category,
                "status": "in_force",
                "title": "No rule at this level",
                "requirement": requirement, "requirement_es": requirement_es,
                "key_value": key_value,
                "coverage_conditions": None, "exemptions": None, "overrides": [], "interaction": None,
                "effective_date": None,
                "citation": "No citing text", "source_doc_id": None, "source_url": None,
                "quoted_span": None, "confidence": 0.5, "conflict_flag": False, "conflict_note": None,
                "negative_finding": True, "derived": True, "notes": None,
            }
            bar = find_preempting_state_rule(rules, state, category) if level == "city" else None
            if bar:
                rec.update({
                    "requirement": f"No {label(category)} rule at the {city_name(jurisdiction)} level; state law bars local rules "
                                   f"({bar['citation']}).",
                    "requirement_es": f"No hay ninguna regla de {LABEL_ES[category]} a nivel de {city_name(jurisdiction)}; "
                                      f"la ley estatal prohíbe las reglas locales ({bar['citation']}).",
                    "citation": bar["citation"], "source_doc_id": bar["source_doc_id"],
                    "source_url": bar["source_url"], "quoted_span": bar["quoted_span"],
                    "confidence": 0.8, "interaction": f"Derived from the state rule {bar['title']}.",
                    "overrides": [bar["team_rule_id"]],
                })
            if pending:
                rec["notes"] = "A pending bill could change this; see the change register."
            if failed:
                rec["notes"] = f"{rec.get('notes') or ''} A proposed measure in this category failed or was struck.".strip()
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
