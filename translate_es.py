"""
translate_es.py - Spanish summaries (requirement_es) for every kept rule and negative finding.

Runs after derive_negatives.py. One Claude call (claude-sonnet-5-5) per batch of 20 records,
cached per record in out/raw/es/ by a hash of the English text, so a rebuild only pays for
requirements that changed. Legal terms are translated accurately (rent control, just cause,
security deposit, tenant screening); citations, section numbers, dates and dollar amounts
are kept unchanged and checked after translation; no dashes are used as punctuation.

Writes requirement_es into out/rules_full.json, out/negatives.json and out/rules.json (the
organisers' schema has no additionalProperties restriction, so the extra field is allowed).

Usage:  python translate_es.py [--batch 20] [--budget 1.00] [--no-model]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

import anthropic
from dotenv import load_dotenv

from common import OUT

load_dotenv()
MODEL = os.environ.get("TRANSLATE_MODEL", "claude-sonnet-5-5")
PRICE_IN, PRICE_OUT = 2.00, 10.00
ES_DIR = OUT / "raw" / "es"
CACHE = ES_DIR / "cache.json"

SYSTEM = """You are a legal translator producing Spanish summaries of U.S. rental-housing rules for a bilingual tenant and landlord information tool. Not legal advice.
Translate each English requirement into clear, neutral Spanish for a U.S. audience, with exactly the same meaning: add nothing, drop nothing, soften nothing.
Legal terms: rent control / rent stabilization = control de rentas (estabilización de rentas); just cause (eviction) = causa justa (de desalojo); security deposit = depósito de garantía; tenant screening = evaluación de solicitantes; application fee = cuota de solicitud; source of income = fuente de ingresos; criminal history = antecedentes penales; algorithmic rent setting = fijación algorítmica de rentas; landlord = arrendador; tenant = inquilino; lease = contrato de arrendamiento.
Keep unchanged, exactly as written: citations, section numbers and section signs, statute and ordinance names in their original form, dates, dollar amounts, percentages, unit counts, record ids such as A0016 or r-0012.
Punctuation: never use em dashes or en dashes; use commas, colons or full stops. Write numerals as in the English.
Respond only with JSON."""

SCHEMA = {
    "type": "object",
    "properties": {
        "translations": {
            "type": "array",
            "items": {"type": "object",
                      "properties": {"team_rule_id": {"type": "string"}, "requirement_es": {"type": "string"}},
                      "required": ["team_rule_id", "requirement_es"], "additionalProperties": False},
        }
    },
    "required": ["translations"],
    "additionalProperties": False,
}

NUMBERISH = re.compile(r"\$[\d,]+(?:\.\d+)?|\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)?%|§+\s?[\dA-Za-z.:\-()]+|\b\d[\d,./:-]*\b")


def key_of(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:16]


def tidy(es: str) -> str:
    es = re.sub(r"\s+[—–]\s+", ", ", es)
    es = re.sub(r"(?<=\D)[—–](?=\D)", ", ", es)
    es = re.sub(r"(\d)\s*[—–]\s*(\d)", r"\1 a \2", es)
    return re.sub(r"\s+,", ",", es).strip()


def check_numbers(en: str, es: str) -> list[str]:
    """Numbers, amounts, dates and section references in the English that are missing from the Spanish."""
    want = set(NUMBERISH.findall(en))
    have = set(NUMBERISH.findall(es))
    return sorted(w for w in want if w not in have and re.search(r"\d", w))


def translate_batch(client, batch: list[dict]) -> tuple[dict, float]:
    lines = ["Translate the `requirement` of each record. Return one translation per team_rule_id.", ""]
    for r in batch:
        lines.append(json.dumps({"team_rule_id": r["team_rule_id"], "jurisdiction": r["jurisdiction"],
                                 "category": r["category"], "requirement": r["requirement"]}, ensure_ascii=False))
    resp = client.messages.create(
        model=MODEL, max_tokens=8000, system=SYSTEM,
        messages=[{"role": "user", "content": "\n".join(lines)}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
    )
    cost = (resp.usage.input_tokens * PRICE_IN + resp.usage.output_tokens * PRICE_OUT) / 1e6
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"model stopped: {resp.stop_reason}")
    data = json.loads(next(b.text for b in resp.content if b.type == "text"))
    ES_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (ES_DIR / f"batch_{stamp}_{batch[0]['team_rule_id']}.json").write_text(
        json.dumps({"model": MODEL, "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
                    "cost_usd": round(cost, 4), "records": [r["team_rule_id"] for r in batch], "response": data},
                   indent=1, ensure_ascii=False), encoding="utf-8")
    return {t["team_rule_id"]: t["requirement_es"] for t in data["translations"]}, cost


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--budget", type=float, default=1.00)
    ap.add_argument("--no-model", action="store_true", help="apply cached translations only")
    args = ap.parse_args()

    full = json.loads((OUT / "rules_full.json").read_text(encoding="utf-8"))["rules"]
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    # Derived negative findings carry a fixed Spanish line written by derive_negatives.py (no model needed).
    def needs_model(r):
        return r.get("requirement") and key_of(r["requirement"]) not in cache and not (r.get("derived") and r.get("requirement_es"))
    todo = [r for r in full if needs_model(r)]
    spent, warnings = 0.0, []
    if todo and not args.no_model:
        client = anthropic.Anthropic()
        for i in range(0, len(todo), args.batch):
            batch = todo[i:i + args.batch]
            if spent >= args.budget:
                print(f"budget ${args.budget:.2f} reached; {len(todo) - i} records left untranslated", file=sys.stderr)
                break
            got, cost = translate_batch(client, batch)
            spent += cost
            for r in batch:
                es = got.get(r["team_rule_id"])
                if not es:
                    warnings.append(f"{r['team_rule_id']}: no translation returned")
                    continue
                es = tidy(es)
                missing = check_numbers(r["requirement"], es)
                if missing:
                    warnings.append(f"{r['team_rule_id']}: numbers/citations missing in Spanish: {missing}")
                cache[key_of(r["requirement"])] = {"requirement_es": es, "team_rule_id": r["team_rule_id"], "model": MODEL,
                                                   "missing_tokens": missing}
            print(f"  batch {i // args.batch + 1}: {len(batch)} records, ${cost:.4f}")
        ES_DIR.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")

    # Apply to the three files that carry rules.
    done = 0
    for name in ("rules_full.json", "rules.json", "negatives.json"):
        path = OUT / name
        data = json.loads(path.read_text(encoding="utf-8"))
        key = "negatives" if name == "negatives.json" else "rules"
        for r in data[key]:
            hit = cache.get(key_of(r.get("requirement") or ""))
            if hit:
                r["requirement_es"] = hit["requirement_es"]
            if r.get("requirement_es"):
                done += name == "rules_full.json"
        path.write_text(json.dumps(data, indent=(2 if name.startswith("rules") else 1), ensure_ascii=False), encoding="utf-8")
    missing = [r["team_rule_id"] for r in full if needs_model(r)]
    print(f"Spanish summaries: {done}/{len(full)} records have requirement_es; {len(todo)} translated this run; "
          f"spend ${spent:.4f}; untranslated: {missing or 'none'}")
    for w in warnings:
        print("  warning:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
