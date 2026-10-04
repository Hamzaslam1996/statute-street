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
        return Path(explicit).resolve(), "custom"
    dev = GOLD_DIR / "rules" / "dev.json"   # never gold/rules/test.json (Hamza ruling #7)
    if dev.exists():
        return dev, "gold (independent, dev split)"
    return GOLD_DIR / "gold_rules.json", "SILVER (AI draft, unverified)"


def load_gold(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = data["rules"] if isinstance(data, dict) else data
    for g in rules:  # the independent set names its doc list differently
        g.setdefault("source_doc_ids", g.get("corpus_doc_ids") or [])
    return rules


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
    ap.add_argument("--out", default=None,
                    help="report path (default out/eval_report.md); with a custom path the id-match file is not rewritten")
    args = ap.parse_args()

    gold_path, gold_label = pick_gold(args.gold)
    if not gold_path.exists():
        print(f"No gold file at {gold_path}", file=sys.stderr)
        return 1
    gold_all = load_gold(gold_path)
    ours = json.loads(Path(args.rules).read_text(encoding="utf-8"))["rules"]
    # Derived negative findings live in negatives.json (some lack a quote, so are
    # not in rules.json); score them too, without double counting.
    neg_path = OUT / "negatives.json"
    if neg_path.exists():
        have = {o["team_rule_id"] for o in ours}
        ours += [o for o in json.loads(neg_path.read_text(encoding="utf-8"))["negatives"]
                 if o["team_rule_id"] not in have]
    summary = json.loads(SUMMARY_JSON.read_text()) if SUMMARY_JSON.exists() else {}

    extracted_docs = {r["source_doc_id"] for r in ours if r.get("source_doc_id")}
    # Which documents did we run? Use the raw cache, not just the surviving rules.
    raw_docs = {p.stem for p in (OUT / "raw").glob("*.json") if ".attempt" not in p.name and ".truncated" not in p.name}
    extracted_docs |= raw_docs

    def in_scope(g: dict) -> bool:
        docs = g.get("source_doc_ids") or []
        return not docs or any(d in extracted_docs for d in docs)

    gold_pos = [g for g in gold_all if not g.get("negative_finding")]
    gold_neg = [g for g in gold_all if g.get("negative_finding")]
    scope_pos = [g for g in gold_pos if in_scope(g)]
    scope_neg = [g for g in gold_neg if in_scope(g)]

    # Our own negative findings ("no rule at this level") are scored against the
    # gold negative findings by jurisdiction + category, separately from real rules.
    # A failed or pending MEASURE (ballot question, home-rule petition) is flagged
    # negative_finding by our rules but is a real instrument, so it may match either
    # a gold rule or a gold negative finding. Derived "no rule" records only match negatives.
    ours_neg = [o for o in ours if o.get("negative_finding")]
    ours = [o for o in ours if not o.get("negative_finding") or o.get("status") in ("failed", "pending")]
    neg_found, neg_missed, used = [], [], set()
    for g in scope_neg:
        cands = [o for o in ours_neg
                 if id(o) not in used
                 and (o["jurisdiction"] or "").lower() == (g["jurisdiction"] or "").lower()
                 and o["category"] == g["category"]]
        # prefer the candidate whose status agrees (failed measure vs standing bar)
        cands.sort(key=lambda o: o.get("status") != g.get("status"))
        hit = cands[0] if cands else None
        if hit:
            used.add(id(hit))
        (neg_found if hit else neg_missed).append((g, hit))
    neg_extra = [o for o in ours_neg if id(o) not in used]

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
    # Code ch. XV"). If a gold rule is still unmatched and it is the ONLY gold rule
    # in its jurisdiction + category, pair it with our best-scoring unmatched rule in
    # that bucket and say so. Any further rules of ours in the bucket stay "extra",
    # which is the real signal (near-duplicates from several documents).
    fallback_ids = set()
    bucket = lambda r: ((r["jurisdiction"] or "").lower(), r["category"])
    gold_bucket_counts = {}
    for g in scope_pos:
        gold_bucket_counts[bucket(g)] = gold_bucket_counts.get(bucket(g), 0) + 1
    for gi, g in enumerate(scope_pos):
        if gi in matched_g or gold_bucket_counts[bucket(g)] != 1:
            continue
        cands = [oi for oi, o in enumerate(ours) if oi not in matched_o and bucket(o) == bucket(g)]
        if cands:
            oi = max(cands, key=lambda oi: cite_score(ours[oi]["citation"], g["citation"]))
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
    date_both_null = date_tags.count("n/a")
    cite_scores = [s for _, _, s in matches]
    kv_scores = [v for v in (value_score(g.get("key_value"), o.get("key_value")) for g, o, _ in matches)
                 if v is not None]

    def pct(x, d):
        return f"{100 * x / d:.0f}%" if d else "n/a"

    lines = []
    lines.append(f"# Module A evaluation\n")
    try:
        gold_name = gold_path.relative_to(GOLD_DIR.parent)
    except ValueError:
        gold_name = gold_path.name
    lines.append(f"Gold set: `{gold_name}` — {gold_label}  ")
    lines.append(f"Our rules: {len(ours)} from {len(raw_docs)} extracted document(s)  ")
    lines.append(f"Gold rules in scope (source doc extracted): {len(scope_pos)} of {len(gold_pos)} positive, "
                 f"{len(scope_neg)} of {len(gold_neg)} negative findings\n")
    lines.append("| Metric | Value |\n|---|---|")
    lines.append(f"| Found (recall) | {n}/{len(scope_pos)} = {pct(n, len(scope_pos))}"
                 + (f" ({len(fallback_ids)} by jurisdiction+category only, marked †)" if fallback_ids else "") + " |")
    lines.append(f"| Missed | {len(missed)} |")
    lines.append(f"| Extra (no gold match) | {len(extra)} |")
    lines.append(f"| Extra colliding with a negative finding | {len(neg_hits)} |")
    lines.append(f"| Negative findings found / missed / extra | {len(neg_found)} / {len(neg_missed)} / {len(neg_extra)} |")
    lines.append(f"| Status agrees | {status_ok}/{n} = {pct(status_ok, n)} |")
    lines.append(f"| Effective date agrees (exact or both null) | {date_exact + date_both_null}/{n} = "
                 f"{pct(date_exact + date_both_null, n)} ({date_exact} exact dates, {date_both_null} both null, "
                 f"{n - date_exact - date_both_null} differ, of which {date_year} same year) |")
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

    if scope_neg or ours_neg:
        lines.append("\n## Negative findings\n")
        lines += [f"- found: {g['gold_id']} ← {h['team_rule_id']} ({h['status']}) {h['title']}" for g, h in neg_found]
        lines += [f"- missed: {g['gold_id']} — {g['title']} (docs {', '.join(g['source_doc_ids'])})" for g, _ in neg_missed]
        lines += [f"- extra: {o['team_rule_id']} — {o['jurisdiction']} / {o['category']} / {o['title']} ({o['source_doc_id']})"
                  for o in neg_extra]

    report_path = Path(args.out) if args.out else REPORT_MD
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Machine-readable pairs for follow-up analysis (date_mismatch.py, lookup_eval.py id mapping);
    # only for the default dev-split report, so a one-off run against another key leaves them intact.
    if not args.out:
        (OUT / "eval_matches.json").write_text(json.dumps([
        {"gold_id": g["gold_id"], "team_rule_id": o["team_rule_id"], "jurisdiction": g["jurisdiction"],
         "category": g["category"], "gold_citation": g.get("citation"), "our_citation": o.get("citation"),
         "gold_effective_date": g.get("effective_date"), "our_effective_date": o.get("effective_date"),
         "gold_status": g.get("status"), "our_status": o.get("status"),
         "gold_docs": g.get("source_doc_ids"), "our_doc": o.get("source_doc_id"), "our_title": o.get("title"),
         "our_supporting": o.get("supporting_doc_ids", []), "our_notes": o.get("notes")}
            for g, o, _ in matches], indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(lines[:16]))
    print(f"\nFull report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
