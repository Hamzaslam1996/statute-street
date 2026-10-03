"""
date_mismatch.py - explain every effective-date disagreement with the gold set.

For each matched gold/ours pair whose dates differ, search the corpus for the
GOLD date stated as an effective date near the rule's section, and classify:
  (a) the date is stated in another corpus document for the same section
  (b) ours is null because no document states a date
  (c) different date convention (adoption month vs effective day, rate-period start, ...)
  (d) genuine error (a document states the gold date and we gave a different one)
Writes out/date_mismatch.md. No API calls. (Hamza rulings_04 #2 step A.)
"""

from __future__ import annotations

import json
import re
import sys

from common import OUT, list_docs
from dates import find_effective_dates, mentions_near_section


def gold_date_mentions(docs, gold_iso: str, citation: str, title: str) -> list[tuple[str, str]]:
    """Documents that mention the gold date (any wording) near the rule's section or bill number."""
    out = []
    if not gold_iso:
        return out
    for d in docs.values():
        snip = mentions_near_section(d.body, gold_iso, citation, title)
        if snip:
            out.append((d.doc_id, snip))
    return out


def main() -> int:
    matches = json.loads((OUT / "eval_matches.json").read_text(encoding="utf-8"))
    docs = list_docs()
    rows = []
    for x in matches:
        g, o = x["gold_effective_date"], x["our_effective_date"]
        if (g or None) == (o or None):
            continue
        cite = x["our_citation"] or x["gold_citation"]
        title = x.get("our_title") or ""
        stated = [h for d in docs.values() for h in find_effective_dates(d.body, d.doc_id, cite, title) if h.near_section]
        stated_gold = [h for h in stated if g and (h.date == g or (len(g) < 10 and h.date.startswith(g)))]
        mentions = gold_date_mentions(docs, g, cite, title)
        if g is None:
            cls = "c"  # gold has no date; ours came from a convention (adoption month, rate period, ...)
            why = "gold null; ours from adoption month / rate-period start / amendment note"
        elif o is None and stated_gold:
            cls, why = "a", f"gold date stated as effective in {', '.join(sorted({h.doc_id for h in stated_gold}))}"
        elif o is None and mentions:
            cls, why = "a", f"gold date appears (not as an explicit effective statement) in {', '.join(sorted({m[0] for m in mentions}))}"
        elif o is None:
            cls, why = "b", "no corpus document states this date"
        elif o[:7] == g[:7] or (len(o) == 7 and g.startswith(o)):
            cls, why = "c", "same month, different precision"
        elif stated_gold or mentions:
            src = sorted({h.doc_id for h in stated_gold} or {m[0] for m in mentions})
            cls, why = "d", f"gold date is in {', '.join(src)}; ours differs (which amendment governs?)"
        else:
            cls, why = "c", "neither date confirmable; convention difference"
        evidence = (stated_gold[0].sentence if stated_gold else (mentions[0][1] if mentions else ""))[:200]
        rows.append((cls, x, why, evidence))

    rows.sort(key=lambda r: r[0])
    lines = ["# Effective-date mismatches vs gold (dev)\n",
             f"{len(matches)} matched rules; {len(rows)} disagree on effective_date "
             f"(pairs where both are null count as agreement).\n",
             "Classes: (a) stated in another corpus doc · (b) no doc states it · (c) convention difference · (d) genuine error\n",
             "| Class | Rule | Gold | Ours | Why | Evidence |", "|---|---|---|---|---|---|"]
    for cls, x, why, ev in rows:
        lines.append(f"| {cls} | {x['gold_id']} / {x['team_rule_id']} ({x['our_citation'][:40]}) | {x['gold_effective_date']} | "
                     f"{x['our_effective_date']} | {why} | {ev.replace('|', '/')} |")
    counts = {c: sum(1 for r in rows if r[0] == c) for c in "abcd"}
    lines.append(f"\nBy class: {counts}")
    (OUT / "date_mismatch.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
