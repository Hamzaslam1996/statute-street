"""
date_resolve.py - fill in missing or imprecise effective dates from explicit
statements elsewhere in the corpus. Runs after verify.py, before derive_negatives.py.

Plain-language summary (Hamza rulings_04 #2, steps B-C)
---------------------------------------------------------
Many statutes do not say when they took effect, but another document in the
corpus does: a history note ("(SB 567) Effective January 1, 2024"), a bill page,
a law-firm alert ("took effect on January 1, 2026") or an agency page ("went
into effect on October 14, 2024"). For every rule whose effective_date is null
or only month/year precise, this script:
  1. finds every corpus document that mentions the rule's section or bill number,
  2. collects sentences there that EXPLICITLY state an effective/operative date,
  3. if they all give one date, uses it; if they disagree, asks Claude (Sonnet,
     small call, $1 cap) which one is the date the extracted requirement first
     took effect (or the amendment that changed its key value);
  4. for a LOCAL ordinance with no effective statement at all, falls back to a
     stated adoption date -> adoption month (ruling B).
Nothing is ever computed from a chapter number or enactment year alone.
Each change records date_source_doc_id and quotes the sentence in notes;
everything is logged to out/date_resolve_log.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

import anthropic
from dotenv import load_dotenv

from common import OUT, list_docs, normalise_citation
from dates import DateHit, find_adoption_dates, find_effective_dates

load_dotenv()
RULES_JSON = OUT / "rules.json"
LOG_CSV = OUT / "date_resolve_log.csv"
CACHE_JSON = OUT / "date_resolve_cache.json"   # decisions already taken, keyed by jurisdiction|category|citation


def cache_key(rule: dict) -> str:
    return f"{rule['jurisdiction']}|{rule['category']}|{normalise_citation(rule.get('citation') or '')}"
MODEL = os.environ.get("EXTRACT_MODEL", "claude-sonnet-5-5")
PRICE_IN, PRICE_OUT = 2.00, 10.00   # US$ per million tokens (Sonnet 5.5)

PICK_SCHEMA = {
    "type": "object",
    "properties": {
        "choice": {"type": ["integer", "null"],
                   "description": "index of the candidate whose date governs, or null if none clearly does"},
        "reason": {"type": "string"},
    },
    "required": ["choice", "reason"],
    "additionalProperties": False,
}

PICK_SYSTEM = """You help a legal research tool decide a rule's effective date.
Rule: effective_date is the date the extracted requirement FIRST took effect. If a later amendment changed the key value itself (the cap, the fee, the ban), use that amendment's date instead. A re-enactment that kept the same requirement does not reset the date. Sunset or repeal dates never count. A date stated for a DIFFERENT provision (another section, another bill) does not count.
You are given the rule and numbered candidate sentences from corpus documents, each stating a date. Pick the one candidate whose date governs under this rule, or null if none clearly does. Respond only with JSON."""


def doubtful(rule: dict) -> bool:
    d = rule.get("effective_date")
    return d is None or len(d) < 10


def candidates_for(rule: dict, docs) -> tuple[list[DateHit], list[DateHit]]:
    own = {rule.get("source_doc_id"), *rule.get("supporting_doc_ids", [])}
    eff, adopt = [], []
    for doc in docs.values():
        hits = find_effective_dates(doc.body, doc.doc_id, rule["citation"], rule["title"])
        eff += [h for h in hits if h.near_section or doc.doc_id in own]
        if rule.get("level") == "city":
            ah = find_adoption_dates(doc.body, doc.doc_id, rule["citation"], rule["title"])
            adopt += [h for h in ah if h.near_section or doc.doc_id in own]
    # keep one hit per (doc, date)
    def uniq(hs):
        seen, out = set(), []
        for h in hs:
            if (h.doc_id, h.date) not in seen:
                seen.add((h.doc_id, h.date)); out.append(h)
        return out
    return uniq(eff), uniq(adopt)


PICK_ADOPTION_SYSTEM = """You help a legal research tool find when a LOCAL ordinance was adopted.
You are given a rule and numbered candidate sentences from corpus documents that mention an adoption/passage/approval date. Pick the one candidate that states the adoption of THIS ordinance or provision (the one the rule's citation and title describe). A rent board adopting an annual rate, a council approving an unrelated item, or a different ordinance does not count. Return null if none clearly does. Respond only with JSON."""


def ask_model(client, rule: dict, hits: list[DateHit], adoption: bool = False) -> tuple[int | None, str, float]:
    lines = [f"Rule: {rule['title']}", f"Jurisdiction: {rule['jurisdiction']}  Citation: {rule['citation']}",
             f"Requirement: {rule['requirement']}", f"Key value: {rule.get('key_value')}",
             f"Current effective_date: {rule.get('effective_date')}", f"Notes: {(rule.get('notes') or '')[:600]}",
             "", "Candidates:"]
    for i, h in enumerate(hits):
        lines.append(f"[{i}] ({h.doc_id}, {h.date}) {h.sentence}")
    resp = client.messages.create(
        model=MODEL, max_tokens=2000, system=PICK_ADOPTION_SYSTEM if adoption else PICK_SYSTEM,
        messages=[{"role": "user", "content": "\n".join(lines)}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": PICK_SCHEMA}},
    )
    cost = (resp.usage.input_tokens * PRICE_IN + resp.usage.output_tokens * PRICE_OUT) / 1e6
    if resp.stop_reason != "end_turn":
        return None, f"model stopped: {resp.stop_reason}", cost
    data = json.loads(next(b.text for b in resp.content if b.type == "text"))
    return data["choice"], data["reason"], cost


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=1.00, help="US$ cap on model calls")
    ap.add_argument("--no-model", action="store_true", help="never call the API; leave disagreements unresolved")
    args = ap.parse_args()

    rules = json.loads(RULES_JSON.read_text(encoding="utf-8"))["rules"]
    docs = list_docs()
    client = None if args.no_model else anthropic.Anthropic()
    spent, log, changed = 0.0, [], 0
    cache = json.loads(CACHE_JSON.read_text(encoding="utf-8")) if CACHE_JSON.exists() else {}

    for rule in rules:
        if rule.get("derived") or not doubtful(rule):
            continue
        before = rule.get("effective_date")
        hit = cache.get(cache_key(rule))
        if hit and hit.get("effective_date"):
            # A decision already taken for this provision (same jurisdiction, category, citation):
            # reuse it rather than asking the model again. Rebuilds therefore need no API calls.
            rule["effective_date"] = hit["effective_date"]
            rule["date_source_doc_id"] = hit["date_source_doc_id"]
            if hit.get("adoption_date"):
                rule["adoption_date"] = hit["adoption_date"]
            tag = hit.get("kind", "Effective date")
            if f"{tag} from {hit['date_source_doc_id']}" not in (rule.get("notes") or ""):
                rule["notes"] = f"{rule.get('notes') or ''} {tag} from {hit['date_source_doc_id']}: \"{hit.get('sentence', '')}\"".strip()
            changed += before != hit["effective_date"]
            log.append({"team_rule_id": rule["team_rule_id"], "citation": rule["citation"], "before": before,
                        "after": rule["effective_date"], "source_doc": hit["date_source_doc_id"],
                        "how": "cached decision reused (" + hit.get("decided_by", "earlier run") + ")", "candidates": ""})
            continue
        eff, adopt = candidates_for(rule, docs)
        new, source, sentence, how = None, None, None, None

        dates = sorted({h.date for h in eff})
        if dates:
            # Even a single statement needs the ruling-1 check: a history note's "Effective
            # January 1, 2026" may belong to a later amendment that left the key value alone.
            if client is None or spent >= args.budget:
                how = f"{len(dates)} candidate date(s) left unresolved (no model / budget)"
            else:
                choice, reason, cost = ask_model(client, rule, eff)
                spent += cost
                if choice is not None and 0 <= choice < len(eff):
                    h = eff[choice]; new, source, sentence = h.date, h.doc_id, h.sentence
                    how = f"model chose among {len(dates)} date(s): {reason}"
                else:
                    how = f"model: none governs ({reason})"
        elif adopt and before is None and rule.get("status") == "in_force":
            # Ruling B fallback, but the model must confirm the adoption statement is about THIS
            # ordinance (a rent board adopting its annual rate is not the deposit rule's adoption).
            if client is None or spent >= args.budget:
                how = "adoption candidates left unresolved (no model / budget)"
            else:
                choice, reason, cost = ask_model(client, rule, adopt, adoption=True)
                spent += cost
                if choice is not None and 0 <= choice < len(adopt):
                    h = adopt[choice]
                    new, source, sentence = h.date[:7], h.doc_id, h.sentence
                    how = f"adoption date -> adoption month (ruling B): {reason}"
                    rule["adoption_date"] = h.date
                else:
                    how = f"model: no adoption statement is about this provision ({reason})"
        else:
            how = "no explicit statement found"

        # Only replace a month-precision date with a full date inside that month or an explicit statement.
        if new and new != before:
            if before and len(before) == 7 and len(new) == 10 and not new.startswith(before):
                how += "; explicit date outside adoption month, kept and flagged"
                rule["conflict_flag"] = True
            rule["effective_date"] = new
            rule["date_source_doc_id"] = source
            tag = "Adoption date" if "adoption" in how else "Effective date"
            rule["notes"] = f"{rule.get('notes') or ''} {tag} from {source}: \"{sentence}\"".strip()
            changed += 1
            cache[cache_key(rule)] = {"effective_date": new, "date_source_doc_id": source, "adoption_date": rule.get("adoption_date"),
                                      "kind": tag, "sentence": sentence, "decided_by": f"{MODEL}: {how[:160]}",
                                      "team_rule_id_at_decision": rule["team_rule_id"]}
        log.append({"team_rule_id": rule["team_rule_id"], "citation": rule["citation"], "before": before,
                    "after": rule.get("effective_date"), "source_doc": source, "how": how,
                    "candidates": "; ".join(f"{h.doc_id}:{h.date}" for h in eff)})

    RULES_JSON.write_text(json.dumps({"rules": rules}, indent=2, ensure_ascii=False), encoding="utf-8")
    CACHE_JSON.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")
    with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["team_rule_id", "citation", "before", "after", "source_doc", "how", "candidates"])
        w.writeheader(); w.writerows(log)
    print(f"date_resolve: {len(log)} rules examined, {changed} dates filled/refined, model spend ${spent:.3f} "
          f"(cap ${args.budget:.2f}); log -> {LOG_CSV.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
