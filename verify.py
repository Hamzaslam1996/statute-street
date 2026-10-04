"""
verify.py - Module A, step 2: check Claude's raw output and build rules.json.

Plain-language summary
----------------------
Claude's answers in out/raw/ are drafts. This script:
  1. Rejects any record whose quoted_span is not an exact passage of the
     source document (we forgive only whitespace, quote-mark and dash styles).
     If a document has rejected records we ask Claude once more, telling it
     which quotes failed; anything still failing is dropped and logged.
  2. Works out `status` itself from the effective date and the query date,
     instead of trusting the model (pending bills and failed measures keep
     the model's label, since there is no date to compute from).
  3. Attaches the document id, URL and retrieval date from the file header.
  4. Lowers confidence for secondary sources (law firm, news, mirrors).
  5. Validates every record against the organisers' schema.
  6. Removes duplicates (same jurisdiction + category + citation) and writes
     out/rules.json in the submission format {"rules": [...]}.

Usage
-----
    python verify.py                 # all cached docs, query date 2026-10-01
    python verify.py --no-retry      # never call the API
    python verify.py --query-date 2027-07-02
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date

from jsonschema import Draft202012Validator
from rapidfuzz import fuzz

from common import (DEFAULT_QUERY_DATE, OUT, RAW_DIR, SCHEMA_JSON, Doc,
                    citation_sections, has_sections, list_docs, normalise,
                    normalise_citation, sections_match, source_rank)

RULES_JSON = OUT / "rules.json"
VERIFY_CSV = OUT / "verify_log.csv"
SUMMARY_JSON = OUT / "verify_summary.json"
DEDUPE_CSV = OUT / "dedupe_log.csv"
OUT_OF_SCOPE_CSV = OUT / "out_of_scope_log.csv"

# Confidence ceiling for records whose only support is a secondary source.
SECONDARY_CONFIDENCE_CAP = 0.7


# ---------------------------------------------------------------------------
# 1. Quote check
# ---------------------------------------------------------------------------
def span_in_doc(span: str, doc_norm: str) -> tuple[bool, float]:
    """
    Is the quoted span really in the document?
    Returns (exact match after normalisation, fuzzy score 0-100 for diagnostics).
    """
    s = normalise(span or "")
    if len(s) < 20:
        return False, 0.0
    if s in doc_norm:
        return True, 100.0
    # Not exact. Compute how close it was, so the log explains the failure.
    score = fuzz.partial_ratio(s, doc_norm) if len(s) < 2000 else 0.0
    return False, round(float(score), 1)


# ---------------------------------------------------------------------------
# 2. Status from dates
# ---------------------------------------------------------------------------
DATE_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")


def date_bounds(eff: str) -> tuple[date, date] | None:
    """'2026' -> (2026-01-01, 2026-12-31); '2026-04' -> (2026-04-01, 2026-04-30); full date -> (d, d)."""
    m = DATE_RE.match(eff or "")
    if not m:
        return None
    y, mo, d = int(m.group(1)), m.group(2), m.group(3)
    try:
        if d:
            dt = date(y, int(mo), int(d))
            return dt, dt
        if mo:
            mo_i = int(mo)
            last = date(y + (mo_i == 12), (mo_i % 12) + 1, 1).toordinal() - 1
            return date(y, mo_i, 1), date.fromordinal(last)
        return date(y, 1, 1), date(y, 12, 31)
    except ValueError:
        return None


def compute_status(rec: dict, query: date) -> tuple[str, str | None]:
    """
    Decide the status of an enacted rule from its effective date.
    Returns (status, note). The note explains any uncertainty.
    """
    model_status = rec.get("status")
    if model_status in ("pending", "failed"):
        return model_status, None            # nothing to compute: not an enacted law

    eff = rec.get("effective_date")
    adopted = date_bounds(rec.get("adoption_date") or "")

    # Ordinance with an adoption date but no exact effective date (Hamza ruling B):
    # adopted more than 60 days before the query date -> in_force; within 60 days the
    # rule-status enum has no 'unknown', so we say in_force but flag it for review.
    if adopted and (not eff or len(eff) <= 7):
        days = (query - adopted[0]).days
        if days < 0:
            return "not_yet_effective", None
        if days <= 60:
            return "in_force", ("Adopted within 60 days of query date; treat as unknown pending "
                                "confirmation of effective date")
        return "in_force", None

    if not eff:
        if model_status == "not_yet_effective":
            return "not_yet_effective", "Model says not yet effective but gave no effective date; check."
        return "in_force", None               # enacted law with no stated start date

    bounds = date_bounds(eff)
    if bounds is None:
        return "in_force", f"Effective date '{eff}' not understood; status not recomputed."
    start, end = bounds
    if start > query:
        return "not_yet_effective", None
    if end <= query:
        return "in_force", None
    # The date is imprecise (e.g. just a year) and the query date falls inside it.
    return "in_force", f"Effective date '{eff}' is imprecise and spans the query date {query}; status uncertain."


# ---------------------------------------------------------------------------
# 3-5. Build a submission record from a raw one
# ---------------------------------------------------------------------------
_ESCAPE_RE = re.compile(r"\\u([0-9a-fA-F]{4})")
_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*")


def decode_escapes(s):
    """The model sometimes writes '\\u2013' as six literal characters; turn them back into the character."""
    return _ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 16)), s) if isinstance(s, str) else s


def build_record(raw: dict, doc: Doc, query: date) -> dict:
    # Text hygiene at source: decode literal escapes (not in the verified quote) and move a
    # leading "[tag]" out of the title into the notes.
    for k in ("title", "requirement", "key_value", "coverage_conditions", "exemptions", "interaction",
              "citation", "conflict_note", "extraction_notes"):
        if isinstance(raw.get(k), str):
            raw[k] = decode_escapes(raw[k])
    tag = _TAG_RE.match(raw.get("title") or "")
    if tag:
        raw["title"] = _TAG_RE.sub("", raw["title"], count=1)
        raw["extraction_notes"] = f"Tag: {tag.group(1)}. {raw.get('extraction_notes') or ''}".strip()
    status, note = compute_status(raw, query)
    confidence = raw.get("confidence")
    notes = [n for n in [raw.get("conflict_note"), note] if n]
    if doc.is_secondary:
        if confidence is None or confidence > SECONDARY_CONFIDENCE_CAP:
            confidence = SECONDARY_CONFIDENCE_CAP
        notes.append("Based on a secondary source; confirm against the official text.")
    # Key values are operator-facing: extraction commentary in parentheses moves to the notes.
    key_value = raw.get("key_value")
    if isinstance(key_value, str):
        moved = re.findall(r"\s*\(([^()]*(?:not stated|not in this|linked PDF|not given|not reproduced|not shown|not specified)[^()]*)\)", key_value, re.I)
        if moved:
            key_value = re.sub(r"\s*\(([^()]*(?:not stated|not in this|linked PDF|not given|not reproduced|not shown|not specified)[^()]*)\)", "", key_value, flags=re.I).strip(" ;,")
            raw["extraction_notes"] = f"{raw.get('extraction_notes') or ''} " + " ".join(m[0].upper() + m[1:] + "." for m in moved)
        raw["key_value"] = key_value or None

    eff = raw.get("effective_date")
    if eff and not DATE_RE.match(eff):
        eff = None  # schema requires YYYY, YYYY-MM or YYYY-MM-DD
    adopted = raw.get("adoption_date")
    if adopted and not DATE_RE.match(adopted):
        adopted = None

    return {
        "team_rule_id": None,  # assigned after dedupe
        "jurisdiction": raw.get("jurisdiction"),
        "level": raw.get("level"),
        "category": raw.get("category"),
        "status": status,
        "title": raw.get("title"),
        "requirement": raw.get("requirement"),
        "key_value": raw.get("key_value"),
        "coverage_conditions": raw.get("coverage_conditions"),
        "exemptions": raw.get("exemptions"),
        "overrides": [],
        "interaction": raw.get("interaction"),
        "effective_date": eff,
        "citation": raw.get("citation"),
        "source_doc_id": doc.doc_id,
        # The manifest URL is the citable source; where our single-page capture came from a
        # different address (e.g. the official PDF behind a publisher's TOC page) it is kept too.
        "source_url": doc.manifest.get("url") or doc.source_url,
        **({"capture_url": doc.source_url} if doc.manifest.get("url") and doc.source_url
           and doc.source_url.split(" ")[0] != doc.manifest["url"] else {}),
        "quoted_span": raw.get("quoted_span"),
        "confidence": confidence,
        "conflict_flag": bool(raw.get("conflict_flag")) or bool(note),
        "conflict_note": " ".join(notes) if notes else None,
        # Extra fields (the schema permits them): see instructions/rulings_02.md
        "negative_finding": bool(raw.get("negative_finding", False)),
        "record_role": raw.get("record_role") or "headline",
        "adoption_date": adopted,
        "notes": raw.get("extraction_notes"),
        "retrieved_at": doc.retrieved_date,
    }


ENACTED = ("in_force", "not_yet_effective")


def same_rule(a: dict, b: dict) -> str | None:
    """
    Are two records in the same jurisdiction + category the same rule?
    Returns the reason, or None. (Hamza ruling 2026-10-04 #1, with two guards
    found by testing: similarity alone never merges two DIFFERENT section
    numbers, and citations with no section number at all compare at >= 75.)
    """
    ca, cb = a["citation"] or "", b["citation"] or ""
    if sections_match(ca, cb):
        return "same section"
    sim = fuzz.token_set_ratio(normalise_citation(ca), normalise_citation(cb))
    if has_sections(ca) and has_sections(cb):
        return None  # two distinct provisions (e.g. BMC 13.78.010 vs 13.78.016)
    # At least one citation has no section number (news / agency summaries): compare
    # the citation wording, and failing that the title + key value.
    if not has_sections(ca) and not has_sections(cb) and sim >= 75:
        return f"citation similarity {sim:.0f} (no section numbers)"
    if sim >= 85:
        return f"citation similarity {sim:.0f}"
    kv = fuzz.token_set_ratio(normalise(f"{a['title']} {a['key_value'] or ''}").lower(),
                              normalise(f"{b['title']} {b['key_value'] or ''}").lower())
    if kv >= 80:
        return f"title/key-value similarity {kv:.0f} (citation lacks section number)"
    return None


def dedupe(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Second-pass merge. Within each jurisdiction + category bucket, records are
    taken best-source-first (official statute > agency page > code publisher >
    secondary; then enacted before proposals; then confidence). Each record is
    compared with the records already kept in that bucket; if it is the same
    rule it is folded in: its doc id goes to `supporting_doc_ids` and the
    merge is logged. A proposal is always folded into the enacted version.
    Returns (kept, merge_log_rows).
    """
    # Enacted law always outranks a proposal, whatever the source; then best source, then confidence.
    order = sorted(records, key=lambda r: (r["status"] not in ENACTED, r["_rank"],
                                           -(r["confidence"] or 0)))
    buckets: dict[tuple, list[dict]] = {}
    log = []
    for r in order:
        key = ((r["jurisdiction"] or "").lower(), r["category"])
        kept_here = buckets.setdefault(key, [])
        target, reason = None, None
        for k in kept_here:
            reason = same_rule(k, r)
            if reason:
                target = k
                break
        if target is None:
            r.setdefault("supporting_doc_ids", [])
            kept_here.append(r)
            continue
        # fold r into target, keeping r's evidence for the evidence-basis pass
        target.setdefault("_folded", []).append(evidence_of(r))
        target["_folded"] += r.get("_folded", [])
        if r["status"] == "pending" and target["status"] in ENACTED:
            reason += "; proposal folded into enacted rule"
            note = f"Proposal ({r['citation']}, {r['source_doc_id']}) adopted as {target['citation']}."
            target["notes"] = f"{target['notes'] or ''} {note}".strip()
        if r["source_doc_id"] not in target["supporting_doc_ids"]:
            target["supporting_doc_ids"].append(r["source_doc_id"])
        # Keep coverage knowledge from the folded record: a rate notice says little about
        # who is covered, while the folded ordinance summary may carry the COO cutoff.
        for fld in ("coverage_conditions", "exemptions"):
            extra = (r.get(fld) or "").strip()
            if extra and extra.lower() not in (target.get(fld) or "").lower():
                target[fld] = f"{target.get(fld) or ''} | [{r['source_doc_id']}] {extra}".strip(" |")
        log.append({"kept_doc": target["source_doc_id"], "kept_citation": target["citation"],
                    "dropped_doc": r["source_doc_id"], "dropped_citation": r["citation"],
                    "dropped_status": r["status"], "jurisdiction": r["jurisdiction"],
                    "category": r["category"], "reason": reason})
    # Supplementary provisions (scope / exemption / ceiling sections) fold into the
    # headline rule of the same act in the same bucket (Hamza rulings_04 #3). If the
    # bucket has no headline to fold into, the record stays, so nothing is lost.
    kept = []
    for key, rs in buckets.items():
        heads = [r for r in rs if r.get("record_role") != "supplementary"]
        for r in rs:
            if r.get("record_role") != "supplementary":
                continue
            target = None
            same_act = [h for h in heads if act_prefix(h["citation"]) and act_prefix(h["citation"]) == act_prefix(r["citation"])]
            if same_act:
                target = same_act[0]
            elif len(heads) == 1:
                target = heads[0]
            if target is None:
                # Nothing to fold into: a scope/exemption/ceiling provision is not a rule on
                # its own, so it is logged rather than published (e.g. Newark § 19:2-14).
                log.append({"kept_doc": "", "kept_citation": "", "dropped_doc": r["source_doc_id"],
                            "dropped_citation": r["citation"], "dropped_status": r["status"],
                            "jurisdiction": r["jurisdiction"], "category": r["category"],
                            "reason": "supplementary provision with no headline rule in this jurisdiction/category; not published"})
                continue
            add = f"{r['citation']}: {r['requirement']}"
            if r.get("exemptions"):
                target["exemptions"] = f"{target['exemptions'] or ''} {r['exemptions']}".strip()
            target["notes"] = f"{target['notes'] or ''} Supplementary provision folded in ({add})".strip()
            if r["source_doc_id"] not in target["supporting_doc_ids"] and r["source_doc_id"] != target["source_doc_id"]:
                target["supporting_doc_ids"].append(r["source_doc_id"])
            log.append({"kept_doc": target["source_doc_id"], "kept_citation": target["citation"],
                        "dropped_doc": r["source_doc_id"], "dropped_citation": r["citation"],
                        "dropped_status": r["status"], "jurisdiction": r["jurisdiction"],
                        "category": r["category"], "reason": "supplementary provision folded into headline rule"})
        kept.extend(heads)
    return kept, log


def apply_dedupe_overrides(kept: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Reviewer-ruled folds from dedupe_overrides.json (rulings_07): the record extracted from
    `from_doc` is folded into the record whose citation contains `into_citation_contains`,
    within the same jurisdiction + category. Logged with the reviewer's reason.
    """
    path = OUT.parent / "dedupe_overrides.json"
    if not path.exists():
        return kept, []
    log = []
    for ov in json.loads(path.read_text(encoding="utf-8")).get("folds", []):
        bucket = [r for r in kept if r["jurisdiction"] == ov["jurisdiction"] and r["category"] == ov["category"]]
        src = [r for r in bucket if r["source_doc_id"] == ov["from_doc"]]
        tgt = [r for r in bucket if ov["into_citation_contains"].lower() in (r["citation"] or "").lower()
               and r["source_doc_id"] != ov["from_doc"]]
        if not src or not tgt:
            print(f"  dedupe override not applicable ({ov['from_doc']} -> *{ov['into_citation_contains']}*): "
                  f"{'source' if not src else 'target'} not found", file=sys.stderr)
            continue
        s, t = src[0], tgt[0]
        t.setdefault("_folded", []).append(evidence_of(s))
        t["_folded"] += s.get("_folded", [])
        for d in [s["source_doc_id"], *s.get("supporting_doc_ids", [])]:
            if d != t["source_doc_id"] and d not in t["supporting_doc_ids"]:
                t["supporting_doc_ids"].append(d)
        for fld in ("coverage_conditions", "exemptions"):
            extra = (s.get(fld) or "").strip()
            if extra and extra.lower() not in (t.get(fld) or "").lower():
                t[fld] = f"{t.get(fld) or ''} | [{s['source_doc_id']}] {extra}".strip(" |")
        # Public note stays neutral; the ruling reference lives in dedupe_log.csv only.
        public_reason = re.sub(r"^rulings?_?\d+\s*#?\d*:\s*", "", ov["reason"])
        t["notes"] = f"{t.get('notes') or ''} Also documented in {s['source_doc_id']}: {public_reason}".strip()
        kept = [r for r in kept if r is not s]
        log.append({"kept_doc": t["source_doc_id"], "kept_citation": t["citation"], "dropped_doc": s["source_doc_id"],
                    "dropped_citation": s["citation"], "dropped_status": s["status"], "jurisdiction": s["jurisdiction"],
                    "category": s["category"], "reason": f"reviewer fold ({ov['reviewer']}): {ov['reason']}"})
    return kept, log


def evidence_of(r: dict) -> dict:
    """The evidence a record carries: where its verified quote came from."""
    return {k: r.get(k) for k in ("source_doc_id", "source_url", "capture_url", "citation", "quoted_span",
                                  "retrieved_at", "status", "_rank")}


def evidence_basis(doc: Doc) -> str:
    """Organiser ruling (Discord, 4 Oct): only the starter pack's corpus/text counts toward the citation metric."""
    if not doc.supplementary:
        return "supplied_corpus"
    return "manual_primary" if doc.doc_id.startswith("M_") else "link_only_capture"


def prefer_supplied_corpus(kept: list[dict], docs: dict) -> tuple[list[dict], list[dict]]:
    """
    rulings_10: make a supplied-corpus document the primary evidence whenever one supports the
    rule. Order of preference: (1) an enacted folded duplicate extracted from a starter-pack text
    (its verified quote, citation and URL take over; the former primary becomes a supporting doc);
    (2) the kept quote itself is an exact passage of some starter-pack text (re-sourced to it).
    Proposal texts (pending) never replace an enacted rule's evidence. Every record gets
    `evidence_basis`. Returns (kept, log rows).
    """
    starter_norm = {d.doc_id: normalise(d.body) for d in docs.values() if not d.supplementary}
    log = []
    for r in kept:
        doc = docs.get(r["source_doc_id"])
        before = r["source_doc_id"]
        how = "primary already from supplied corpus" if doc and not doc.supplementary else None
        if how is None:
            cands = [f for f in r.get("_folded", []) if f.get("source_doc_id") in starter_norm
                     and (f.get("status") in ENACTED or r["status"] not in ENACTED)]
            cands.sort(key=lambda f: (f.get("_rank") or 9))
            if cands:
                f = cands[0]
                old = {k: r.get(k) for k in ("source_doc_id", "source_url", "capture_url", "citation", "quoted_span", "retrieved_at")}
                for k in ("source_doc_id", "source_url", "citation", "quoted_span", "retrieved_at"):
                    r[k] = f.get(k)
                r.pop("capture_url", None)
                if old["source_doc_id"] not in r["supporting_doc_ids"]:
                    r["supporting_doc_ids"].insert(0, old["source_doc_id"])
                r["supporting_doc_ids"] = [d for d in r["supporting_doc_ids"] if d != r["source_doc_id"]]
                r["notes"] = (f"{r.get('notes') or ''} Primary evidence is the supplied corpus text {f['source_doc_id']}; "
                              f"{old['source_doc_id']} (cited as {old['citation']}) is kept as a supporting document.").strip()
                how = f"switched to folded corpus record {f['source_doc_id']}"
            else:
                span = normalise(r.get("quoted_span") or "")
                hits = [d for d, body in starter_norm.items() if span and span in body]
                if hits:
                    d = docs[hits[0]]
                    if before not in r["supporting_doc_ids"]:
                        r["supporting_doc_ids"].insert(0, before)
                    r["source_doc_id"], r["source_url"], r["retrieved_at"] = d.doc_id, d.manifest.get("url") or d.source_url, d.retrieved_date
                    r.pop("capture_url", None)
                    r["notes"] = f"{r.get('notes') or ''} The quoted passage also appears verbatim in supplied corpus text {d.doc_id}, which is cited as primary.".strip()
                    if any(f.get("source_doc_id") == d.doc_id and f.get("status") == "pending" for f in r.get("_folded", [])):
                        # rulings_11 #5: the organisers supplied the proposal text; the rule itself is the enacted ordinance
                        r["notes"] += f" Corpus copy {d.doc_id} is the proposed text; enacted as {r['citation']}."
                    how = f"quote found verbatim in corpus doc {d.doc_id}"
                else:
                    only = [f["source_doc_id"] for f in r.get("_folded", []) if f.get("source_doc_id") in starter_norm]
                    how = ("no supplied-corpus text supports this rule" if not only
                           else f"supplied corpus has only a proposal/non-enacted text ({', '.join(only)}); kept primary")
        r["evidence_basis"] = evidence_basis(docs[r["source_doc_id"]])
        log.append({"team_rule_id": None, "jurisdiction": r["jurisdiction"], "category": r["category"],
                    "citation": r["citation"], "primary_before": before, "primary_after": r["source_doc_id"],
                    "evidence_basis": r["evidence_basis"], "how": how})
    return kept, log


def apply_rule_overrides(final: list[dict]) -> list[dict]:
    """
    Reviewer rulings on individual rule records (data/rule_overrides.json, rulings_12 section 1):
    which records carry a review flag and the public wording of the flag. Keyed by team_rule_id,
    guarded by a title check so that a renumbering is reported instead of silently misapplied.
    """
    path = OUT.parent / "data" / "rule_overrides.json"
    if not path.exists():
        return final
    by_id = {r["team_rule_id"]: r for r in final}
    for rid, ov in json.loads(path.read_text(encoding="utf-8")).get("overrides", {}).items():
        r = by_id.get(rid)
        if not r or ov.get("title_contains", "").lower() not in (r.get("title") or "").lower():
            print(f"  rule override {rid} skipped: id missing or title does not contain '{ov.get('title_contains')}'", file=sys.stderr)
            continue
        if "conflict_flag" in ov:
            r["conflict_flag"] = ov["conflict_flag"]
        if "conflict_note" in ov:
            r["conflict_note"] = ov["conflict_note"]
        if ov.get("note_append") and ov["note_append"] not in (r.get("notes") or ""):
            r["notes"] = f"{r.get('notes') or ''} {ov['note_append']}".strip()
    return final


def act_prefix(cite: str) -> str | None:
    """'N.J.S.A. 46:8-26' -> '46:8'; 'Newark § 19:2-22' -> '19:2'; 'Cal. Civ. Code § 1950.5' -> '1950'."""
    for tup in citation_sections(cite or ""):
        for t in tup:
            m = re.match(r"^([a-z]{0,2}\.?\d+[a-z]?(?::\d+[a-z]?)?)[.\-]\d", t)
            if m:
                return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Verify raw extractions and write out/rules.json.")
    ap.add_argument("--query-date", default=DEFAULT_QUERY_DATE)
    ap.add_argument("--no-retry", action="store_true", help="do not call the API for failed quotes")
    ap.add_argument("--model", default=None, help="model for the retry (default: same as original)")
    args = ap.parse_args()
    query = date.fromisoformat(args.query_date)

    docs = list_docs()
    schema = json.loads(SCHEMA_JSON.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    raw_files = sorted(p for p in RAW_DIR.glob("*.json")
                       if ".attempt" not in p.name and ".truncated" not in p.name)
    if not raw_files:
        print("No raw output in out/raw/. Run extract.py first.", file=sys.stderr)
        return 1

    log_rows, candidates, out_of_scope_rows = [], [], []
    counts = {"docs": 0, "raw_records": 0, "out_of_scope": 0, "span_pass": 0, "span_fail_first": 0,
              "span_pass_after_retry": 0, "dropped_span": 0, "dropped_schema": 0,
              "dropped_duplicate": 0, "retries": 0}

    for path in raw_files:
        raw = json.loads(path.read_text(encoding="utf-8"))
        doc = docs.get(raw["doc_id"])
        if doc is None:
            print(f"  {raw['doc_id']}: source text not found, skipping", file=sys.stderr)
            continue
        counts["docs"] += 1
        doc_norm = normalise(doc.body)

        def check(records: list[dict], attempt: int) -> tuple[list[dict], list[dict]]:
            good, bad = [], []
            for r in records:
                ok, score = span_in_doc(r.get("quoted_span", ""), doc_norm)
                log_rows.append({"doc_id": doc.doc_id, "attempt": attempt, "citation": r.get("citation"),
                                 "title": r.get("title"), "span_ok": ok, "fuzzy_score": score,
                                 "span_preview": (r.get("quoted_span") or "")[:80]})
                (good if ok else bad).append(r)
            return good, bad

        records = raw.get("rules", [])
        # Provisions the model flagged as adjacent-but-outside a category (notice-to-quit
        # periods, anti-retaliation) are logged for the judges, not published.
        for r in [r for r in records if r.get("out_of_scope")]:
            out_of_scope_rows.append({"doc_id": doc.doc_id, "jurisdiction": r.get("jurisdiction"),
                                      "category": r.get("category"), "citation": r.get("citation"),
                                      "title": r.get("title"), "reason": r.get("out_of_scope_reason")})
        records = [r for r in records if not r.get("out_of_scope")]
        counts["raw_records"] += len(records)
        good, bad = check(records, attempt=raw.get("attempt", 1))
        counts["span_pass"] += len(good)
        counts["span_fail_first"] += len(bad)

        # One retry per document, telling the model which quotes failed.
        if bad and not args.no_retry and raw.get("attempt", 1) < 2:
            from extract import extract_doc  # imported here so --no-retry never needs the API
            counts["retries"] += 1
            feedback = "\n".join(f"- NOT FOUND: {json.dumps(r.get('quoted_span'))}" for r in bad)
            print(f"  {doc.doc_id}: {len(bad)} span(s) failed; retrying once with feedback ...")
            raw2 = extract_doc(doc, args.model or raw.get("model"), attempt=2, feedback=feedback)
            good2, bad2 = check(raw2.get("rules", []), attempt=2)
            counts["span_pass_after_retry"] += len(good2)
            counts["dropped_span"] += len(bad2)
            good, bad = good2, bad2   # the retry replaces the first attempt wholesale
        else:
            counts["dropped_span"] += len(bad)

        for r in good:
            rec = build_record(r, doc, query)
            rec["_rank"] = source_rank(doc)
            candidates.append(rec)

    kept, merge_log = dedupe(candidates)
    kept, override_log = apply_dedupe_overrides(kept)
    merge_log += override_log
    kept, evidence_log = prefer_supplied_corpus(kept, docs)
    with open(DEDUPE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["kept_doc", "kept_citation", "dropped_doc", "dropped_citation",
                                          "dropped_status", "jurisdiction", "category", "reason"])
        w.writeheader()
        w.writerows(merge_log)
    with open(OUT_OF_SCOPE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["doc_id", "jurisdiction", "category", "citation", "title", "reason"])
        w.writeheader()
        w.writerows(out_of_scope_rows)
    counts["out_of_scope"] = len(out_of_scope_rows)

    # TODO (Hamza ruling 2026-10-04, #3): cross-rule conflict pass after extraction.
    # Where a state rule's `interaction` contains preemption language ("preempt",
    # "conflict", "municipality shall be prohibited") and a city rule exists in the
    # same category within that state, set conflict_flag on both and cross-reference
    # them in conflict_note / overrides. Example: NJ FAIR Act vs Jersey City and
    # Hoboken algorithmic-rent ordinances (README T3).
    counts["dropped_duplicate"] = len(merge_log)

    # Stable ordering and ids, then schema validation.
    kept.sort(key=lambda r: ((r["jurisdiction"] or ""), r["category"], (r["citation"] or "")))
    final = []
    for i, rec in enumerate(kept, start=1):
        rec.pop("_rank", None)
        rec.pop("_folded", None)
        rec["team_rule_id"] = f"r-{i:04d}"
        for row in evidence_log:
            if row["team_rule_id"] is None and row["citation"] == rec["citation"] and row["jurisdiction"] == rec["jurisdiction"] \
                    and row["category"] == rec["category"]:
                row["team_rule_id"] = rec["team_rule_id"]
                break
        errors = sorted(validator.iter_errors(rec), key=lambda e: list(e.path))
        if errors:
            counts["dropped_schema"] += 1
            msg = "; ".join(f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors)
            print(f"  {rec['source_doc_id']} {rec['citation']}: schema error -> {msg}", file=sys.stderr)
            continue
        final.append(rec)

    final = apply_rule_overrides(final)
    OUT.mkdir(parents=True, exist_ok=True)
    # Exactly the submission template shape: {"rules": [...]}
    RULES_JSON.write_text(json.dumps({"rules": final}, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    with open(VERIFY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["doc_id", "attempt", "citation", "title", "span_ok",
                                          "fuzzy_score", "span_preview"])
        w.writeheader()
        w.writerows(log_rows)
    counts["final_rules"] = len(final)
    counts["query_date"] = args.query_date
    # Evidence-basis audit (rulings_10)
    with open(OUT / "evidence_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["team_rule_id", "jurisdiction", "category", "citation", "primary_before",
                                          "primary_after", "evidence_basis", "how"])
        w.writeheader(); w.writerows(evidence_log)
    basis_counts = {}
    for r in final:
        basis_counts[r["evidence_basis"]] = basis_counts.get(r["evidence_basis"], 0) + 1
    switched = [row for row in evidence_log if row["primary_before"] != row["primary_after"]]
    non_corpus = [r for r in final if r["evidence_basis"] != "supplied_corpus"]
    rep = ["# Evidence basis (rulings_10)", "",
           "Organiser ruling (Discord, 4 Oct): self-saved link-only texts may be used for research but do not count "
           "toward the citation metric; the metric is based on the supplied corpus text.", "",
           "| evidence_basis | rules |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(basis_counts.items())]
    rep += ["", f"Primaries switched to a supplied-corpus document: {len(switched)}", ""]
    rep += [f"- {row['team_rule_id']} {row['jurisdiction']} / {row['category']}: {row['primary_before']} -> {row['primary_after']} ({row['how']})" for row in switched]
    rep += ["", f"Rules whose only verified quote is NOT from the supplied corpus: {len(non_corpus)}", ""]
    rep += [f"- {r['team_rule_id']} [{r['evidence_basis']}] {r['jurisdiction']} / {r['category']}: {r['citation'][:60]} (doc {r['source_doc_id']})" for r in non_corpus]
    (OUT / "evidence_report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    counts["evidence_basis"] = basis_counts
    print(f"Evidence basis: {basis_counts}; {len(switched)} primaries switched to supplied corpus -> evidence_report.md")
    attempted = counts["raw_records"]
    counts["span_pass_rate_first_attempt"] = round(counts["span_pass"] / attempted, 3) if attempted else None
    SUMMARY_JSON.write_text(json.dumps(counts, indent=2), encoding="utf-8")

    print(f"\nDocuments: {counts['docs']}   raw records: {attempted}")
    print(f"Quote check: {counts['span_pass']} passed, {counts['span_fail_first']} failed on first attempt"
          + (f"; {counts['retries']} doc(s) retried, {counts['span_pass_after_retry']} passed after retry"
             if counts["retries"] else ""))
    print(f"Dropped: {counts['dropped_span']} bad quote, {counts['dropped_duplicate']} merged as duplicates "
          f"(see {DEDUPE_CSV.name}), {counts['dropped_schema']} schema, "
          f"{counts['out_of_scope']} out of scope (see {OUT_OF_SCOPE_CSV.name})")
    print(f"Final rules: {len(final)} -> {RULES_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
