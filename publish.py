"""
publish.py - public-facing copies of the submission files (rulings_08 #3).

Internal reviewer text ("Decided by Hamza ...", "(Q5)", "ruling #", "rulings_07",
"L1xx", "gold", reviewer references) is removed from explanations and notes.
Citations, quotes, dates, assumptions, "Applies unless ..." and "flagged for human
review" wording are kept. Writes out/public/{rules,lookups,changes}.json and, with
--in-place, applies the same filter to the submission files in out/ (reporting
how many strings were changed).

Usage:  python publish.py [--in-place]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import OUT

FILES = ["rules.json", "lookups.json", "changes.json", "rules_full.json", "negatives.json"]
PUBLIC_FILES = ["rules.json", "lookups.json", "changes.json"]
# Any sentence containing one of these is dropped.
INTERNAL = re.compile(r"Decided by Hamza|Hamza|\(Q\d+\)|ruling #\d*|\brulings?_?\d+|\bL1\d\d\b|\bgold\b|reviewer|"
                      r"instructions/", re.I)
TEXT_FIELDS = {"explanation", "notes", "conflict_note", "interaction", "requirement", "requirement_es", "exemptions",
               "coverage_conditions", "title", "key_value"}
DROP_FIELDS = {"reviewed_by", "review_ruling"}

removed: list[str] = []


def clean_text(s: str) -> str:
    if not INTERNAL.search(s):
        return s
    parts = re.split(r"(?<=[.;])\s+", s)
    kept = []
    for p in parts:
        if INTERNAL.search(p):
            removed.append(p.strip()[:120])
        else:
            kept.append(p)
    return " ".join(kept).strip()


def clean(obj, key=None):
    if isinstance(obj, dict):
        return {k: clean(v, k) for k, v in obj.items() if k not in DROP_FIELDS}
    if isinstance(obj, list):
        return [clean(v, key) for v in obj]
    if isinstance(obj, str) and (key in TEXT_FIELDS or key is None or INTERNAL.search(obj)):
        return clean_text(obj)
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-place", action="store_true", help="also filter the submission files in out/")
    args = ap.parse_args()
    pub = OUT / "public"
    pub.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name in FILES:
        path = OUT / name
        if not path.exists():
            continue
        before = len(removed)
        data = json.loads(path.read_text(encoding="utf-8"))
        cleaned = clean(data)
        n = len(removed) - before
        counts[name] = n
        if name in PUBLIC_FILES:
            (pub / name).write_text(json.dumps(cleaned, indent=1, ensure_ascii=False), encoding="utf-8")
        if args.in_place and n:
            path.write_text(json.dumps(cleaned, indent=(2 if name.startswith("rules") else 1), ensure_ascii=False), encoding="utf-8")
    print("strings removed per file:", counts, "| total", sum(counts.values()))
    for s in removed[:12]:
        print("  -", s)
    print(f"public copies -> {pub}/ ({', '.join(PUBLIC_FILES)})" + ("; submission files filtered in place" if args.in_place else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
