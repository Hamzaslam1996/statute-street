"""
eval.py - Module A, step 3: compare out/rules.json with the gold answer key.

Plain-language summary
----------------------
The gold set lists the rules a careful lawyer expects to find. We line up our
extracted rules against it (same jurisdiction, same category, similar
citation) and report:
  - found / missed / extra rules,
  - how often status, effective date, key value and citation agree,
  - the quoted-span pass rate from verify.py.

Only gold rules whose source documents were actually extracted are counted as
"in scope", so a 3-document test run is not penalised for the other 80.
Gold entries marked `negative_finding` ("no rule at this level") are reported
separately: producing a rule that matches one of them is a warning.

Usage
-----
    python eval.py
    python eval.py --gold gold/gold_rules.json --min-cite-score 60
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rapidfuzz import fuzz

from common import GOLD_DIR, OUT, normalise, normalise_citation

RULES_JSON = OUT / "rules.json"
SUMMARY_JSON = OUT / "verify_summary.json"
REPORT_MD = OUT / "eval_report.md"


def pick_gold(explicit: str | None) -> tuple[Path, str]:
    """Prefer the independent gold set if it exists, else the silver AI draft."""
    if explicit:
        return Path(explicit), "custom"
    dev = GOLD_DIR / "rules" / "dev.json"
    if dev.exists():
        return dev, "gold (independent)"
    return GOLD_DIR / "gold_rules.json", "SILVER (AI draft, unverified)"


def cite_score(a: str, b: str) -> float:
    return fuzz.token_set_ratio(normalise_citation(a), normalise_citation(b))


def value_score(a, b) -> float | None:
    if a is None or b is None:
        return None
    return fuzz.token_set_ratio(normalise(str(a)).lower(), normalise(str(b)).lower())


def same_date(a, b) -> str:
    """'exact', 'year', or 'diff' (or 'n/a' if either side is missing)."""
    if not a or not b:
        return "n/a" if not a and not b else "one missing"
    if a == b:
        return "exact"
    return "year" if a[:4] == b[:4] else "diff"


def main() -> int:
    ap = argparse.ArgumentParser(description="Score out/rules.json against the gold set.")
    ap.add_argument("--gold", default=None)
    ap.add_argument("--rules", default=str(RULES_JSON))
    ap.add_argument("--min-cite-score", type=float, default=60.0,
                    help="fuzzy citation similarity (0-100) needed to count as the same rule")
    args = ap.parse_args()

    gold_path, gold_label = pick_gold(args.gold)
    if not gold_path.exists():
        print(f"No gold file at {gold_path}", file=sys.stderr)
        return 1
    gold_all = json.loads(gold_path.read_text(encoding="utf-8"))["rules"]
    ours = json.loads(Path(args.rules).read_text(encoding="utf-8"))["rules"]
    summary = json.loads(SUMMARY_JSON.read_text()) if SUMMARY_JSON.exists() else {}

    extracted_docs = {r["source_doc_id"] for r in ours}
    # Which documents did we run? Use the raw cache, not just the surviving rules.
    raw_docs = {p.stem for p in (OUT / "raw").glob("D*.json") if ".attempt" not in p.name}
    extracted_docs |= raw_docs

    def in_scope(g: dict) -> bool:
        return any(d in extracted_docs for d in g.get("source_doc_ids", []))

    gold_pos = [g for g in gold_all if not g.get("negative_finding")]
    gold_neg = [g for g in gold_all if g.get("negative_finding")]
    scope_pos = [g for g in gold_pos if in_scope(g)]
    scope_neg = [g for g in gold_neg if in_scope(g)]

    # --- matching: greedy, best citation score first -----------------------
    pairs = []
    for gi, g in enumerate(scope_pos):
        for oi, o in enumerate(ours):
            if (o["jurisdiction"] or "").lower() != (g["jurisdiction"] or "").lower():
                continue
            if o["category"] != g["category"]:
                continue
            s = cite_score(o["citation"], g["citation"])
            if s >= args.min_cite_score:
                pairs.append((s, gi, oi))
    pairs.sort(reverse=True)
    matched_g, matched_o, matches = {}, set(), []
    for s, gi, oi in pairs:
        if gi in matched_g or oi in matched_o:
            continue
        matched_g[gi] = oi
        matched_o.add(oi)
        matches.append((scope_pos[gi], ours[oi], s))

    # Fallback: citations are written many ways ("L.A.M.C. § 151.00" vs "L.A. Mun.
    # Code ch. XV"). If a gold rule is still unmatched and exactly one unmatched
    # extracted rule sits in the same jurisdiction + category, pair them and say so.
    fallback_ids = set()
    for gi, g in enumerate(scope_pos):
        if gi in matched_g:
            continue
        cands = [oi for oi, o in enumerate(ours)
                 if oi not in matched_o
                 and (o["jurisdiction"] or "").lower() == (g["jurisdiction"] or "").lower()
                 and o["category"] == g["category"]]
        if len(cands) == 1:
            oi = cands[0]
            matched_g[gi] = oi
            matched_o.add(oi)
            matches.append((g, ours[oi], cite_score(ours[oi]["citation"], g["citation"])))
            fallback_ids.add(g["gold_id"])

    missed = [g for gi, g in enumerate(scope_pos) if gi not in matched_g]
    extra = [o for oi, o in enumerate(ours) if oi not in matched_o]

    # extras that collide with a "no rule here" finding
    neg_hits = []
    for o in extra:
        for g in scope_neg:
            if ((o["jurisdiction"] or "").lower() == (g["jurisdiction"] or "").lower()
                    and o["category"] == g["category"]):
                neg_hits.append((o, g))

    # --- field accuracy over matched pairs -----------------------------------
    n = len(matches)
    status_ok = sum(1 for g, o, _ in matches if g.get("status") == o.get("status"))
    date_tags = [same_date(g.get("effective_date"), o.get("effective_date")) for g, o, _ in matches]
    date_exact = date_tags.count("exact")
    date_year = date_tags.count("year")
    cite_scores = [s for _, _, s in matches]
    kv_scores = [v for v in (value_score(g.get("key_value"), o.get("key_value")) for g, o, _ in matches)
                 if v is not None]

    def pct(x, d):
        return f"{100 * x / d:.0f}%" if d else "n/a"

    lines = []
    lines.append(f"# Module A evaluation\n")
    lines.append(f"Gold set: `{gold_path.relative_to(GOLD_DIR.parent)}` — {gold_label}  ")
    lines.append(f"Our rules: {len(ours)} from {len(raw_docs)} extracted document(s)  ")
    lines.append(f"Gold rules in scope (source doc extracted): {len(scope_pos)} of {len(gold_pos)} positive, "
                 f"{len(scope_neg)} of {len(gold_neg)} negative findings\n")
    lines.append("| Metric | Value |\n|---|---|")
    lines.append(f"| Found (recall) | {n}/{len(scope_pos)} = {pct(n, len(scope_pos))}"
                 + (f" ({len(fallback_ids)} by jurisdiction+category only, marked †)" if fallback_ids else "") + " |")
    lines.append(f"| Missed | {len(missed)} |")
    lines.append(f"| Extra (no gold match) | {len(extra)} |")
    lines.append(f"| Extra colliding with a negative finding | {len(neg_hits)} |")
    lines.append(f"| Status agrees | {status_ok}/{n} = {pct(status_ok, n)} |")
    lines.append(f"| Effective date exact / same year | {date_exact}/{n} = {pct(date_exact, n)} / "
                 f"{date_exact + date_year}/{n} |")
    lines.append(f"| Citation similarity (mean) | {sum(cite_scores) / n:.0f}/100 |" if n else "| Citation similarity | n/a |")
    lines.append(f"| Key value similarity (mean) | {sum(kv_scores) / len(kv_scores):.0f}/100 |" if kv_scores else "| Key value similarity | n/a |")
    if summary:
        lines.append(f"| Quote check pass rate (first attempt) | {summary.get('span_pass')}/{summary.get('raw_records')} = "
                     f"{pct(summary.get('span_pass', 0), summary.get('raw_records', 0))} |")
        lines.append(f"| Records dropped for bad quotes | {summary.get('dropped_span')} |")

    lines.append("\n## Matched rules\n")
    lines.append("| Gold id | Ours | Status (gold / ours) | Eff. date (gold / ours) | Cite score | Key value (gold / ours) |\n|---|---|---|---|---|---|")
    for g, o, s in sorted(matches, key=lambda m: m[0]["gold_id"]):
        flag = "" if g.get("status") == o.get("status") else " ⚠"
        gid = g["gold_id"] + (" †" if g["gold_id"] in fallback_ids else "")
        lines.append(f"| {gid} | {o['team_rule_id']} | {g.get('status')} / {o.get('status')}{flag} | "
                     f"{g.get('effective_date')} / {o.get('effective_date')} | {s:.0f} | "
                     f"{str(g.get('key_value'))[:60]} / {str(o.get('key_value'))[:60]} |")

    lines.append("\n## Missed gold rules (in scope)\n")
    lines += [f"- {g['gold_id']} — {g['jurisdiction']} / {g['category']} / {g['citation']} (docs {', '.join(g['source_doc_ids'])})"
              for g in missed] or ["- none"]

    lines.append("\n## Extra rules (no gold match)\n")
    lines += [f"- {o['team_rule_id']} — {o['jurisdiction']} / {o['category']} / {o['citation']} ({o['source_doc_id']}): {o['title']}"
              for o in extra] or ["- none"]

    if neg_hits:
        lines.append("\n## Collisions with negative findings (gold says: no rule at this level)\n")
        lines += [f"- {o['team_rule_id']} {o['citation']} vs {g['gold_id']}: {g['title']}" for o, g in neg_hits]

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:16]))
    print(f"\nFull report: {REPORT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
