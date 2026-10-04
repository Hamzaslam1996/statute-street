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
changed_notes: list[tuple[str, str, str]] = []   # (where, before, after) for the report

# Pipeline or source-handling language that is not public product text (rulings_12 section 2).
PIPELINE = re.compile(r"our team|the model\b|pipeline|extract\w*|the corpus|in the corpus|"
                      r"corpus (copy|text|document)|\bcorpus\b|\bD\d{3}\b|\bM_[A-Za-z0-9_.-]+|\br-\d{4}\b|\bn-\d{4}\b|"
                      r"\b[A-Z]{2,4}-[A-Z]{2,5}-\d\d\b|not stated in (the )?source|primary evidence|folded|supporting document", re.I)
ENUMS = {"not_yet_effective": "not yet in force", "in_force": "in force", "rent_increase_limits": "rent increase limits",
         "just_cause_eviction": "just cause eviction", "security_deposits": "security deposits",
         "application_screening_fees": "application screening fees", "screening_restrictions": "screening restrictions",
         "algorithmic_rent_setting": "algorithmic rent setting", "negative_finding": "negative finding"}


DOC_TAG = re.compile(r"\[(?:D\d{3}|M_[^\]]+)\]\s*")   # "[D092] " prefixes on quoted coverage text


# Source-handling wording rewritten in place (keeps the legal content of the sentence).
REWRITES = [(re.compile(r",?\s*so (the )?effective_date is null", re.I), ""),
            (re.compile(r"effective_date is null", re.I), "no effective date is stated"),
            (re.compile(r"\beffective_date\b"), "effective date"),
            (re.compile(r"\b(this|the) (document|capture|page|text)\b", re.I), "the source"),
            (re.compile(r"\bthe brief\b", re.I), "the summary"),
            (re.compile(r"^Tag: [a-z-]+\.\s*", re.I), "")]


def clean_text(s: str) -> str:
    """Drop sentences carrying internal review text or pipeline language; replace enum words with plain words."""
    original = s
    s = DOC_TAG.sub("", s)
    for pat, repl in REWRITES:
        s = pat.sub(repl, s)
    for k, v in ENUMS.items():
        s = s.replace(k, v)
    if INTERNAL.search(s) or PIPELINE.search(s):
        parts = re.split(r"(?<=[.;])\s+", s)
        kept = []
        for p in parts:
            if INTERNAL.search(p) or PIPELINE.search(p):
                removed.append(p.strip()[:120])
            else:
                kept.append(p)
        s = " ".join(kept).strip()
    if s != original:
        # tidy what the rewrites leave behind: sentence starts in capitals, no dangling separators
        s = re.sub(r"(^|\.\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), s)
        s = re.sub(r"\s*[;,]\s*$", ".", s)
        s = re.sub(r";\s*;", ";", s)
    return s


def load_note_overrides() -> dict:
    p = OUT.parent / "data" / "public_notes_overrides.json"
    return json.loads(p.read_text(encoding="utf-8")).get("overrides", {}) if p.exists() else {}


NOTE_OVERRIDES = load_note_overrides()


def clean(obj, key=None, rid=None):
    if isinstance(obj, dict):
        rid = obj.get("team_rule_id", rid)
        out = {}
        ov = NOTE_OVERRIDES.get(rid) if rid and "requirement" in obj else None   # rule records only
        if ov and ov.get("title_contains", "").lower() not in (obj.get("title") or "").lower():
            ov = None
        for k, v in obj.items():
            if k in DROP_FIELDS:
                continue
            if ov and k in ov and k not in ("title_contains",):
                if v != ov[k]:
                    changed_notes.append((f"{rid}.{k}", str(v)[:140], str(ov[k])[:140]))
                out[k] = ov[k]
                continue
            out[k] = clean(v, k, rid)
        return out
    if isinstance(obj, list):
        return [clean(v, key, rid) for v in obj]
    # Only prose fields are filtered; ids, enums, citations and URLs pass through untouched.
    if isinstance(obj, str) and key in TEXT_FIELDS:
        new = clean_text(obj)
        if new != obj and key in ("notes", "conflict_note"):
            changed_notes.append((f"{rid}.{key}", obj[:140], new[:140]))
        return new
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
    # Every changed note, for the review report (rulings_12 section 2)
    seen, rows = set(), []
    for where, before, after in changed_notes:
        if (where, before) not in seen:
            seen.add((where, before)); rows.append((where, before, after))
    (pub / "text_changes.md").write_text(
        "# Public text changes (notes and conflict notes)\n\n| Field | Before | After |\n|---|---|---|\n" +
        "\n".join(f"| {w} | {b.replace('|', '/')} | {a.replace('|', '/') or '(removed)'} |" for w, b, a in rows) + "\n",
        encoding="utf-8")
    print(f"changed notes: {len(rows)} -> {pub / 'text_changes.md'}")
    print(f"public copies -> {pub}/ ({', '.join(PUBLIC_FILES)})" + ("; submission files filtered in place" if args.in_place else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
