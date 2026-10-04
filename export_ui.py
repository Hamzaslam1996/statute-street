"""
export_ui.py - convert the engine's public output into the Lovable UI's bundled data files.

Deterministic, no model calls. Writes to ../statute-street-ui/src/data/ (or --out):
  rules.json      <- out/public/rules.json + out/negatives.json ("no rule at this level" records)
  lookups.json    <- out/public/lookups.json (all 500 addresses; result, explanation, assumptions, conflict_flag)
  changes.json    <- out/public/changes.json (T1-T5)
  addresses.json  <- starter pack sample_addresses.csv + out/jurisdictions.json (geocoded legal city)
  sources.json    <- the corpus documents our rules cite (with evidence_basis) + sources/source_register.csv

Every record is checked against a Python mirror of the zod contract in src/data/index.ts; the
converter refuses to write if any record would be skipped by the UI. The rulings_08 filter is
applied to all strings (no internal review text), and dashes used as punctuation in exported
strings are replaced by commas or colons (dates and ids keep their hyphens).

Usage:  python export_ui.py [--out ../statute-street-ui/src/data]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import publish
from common import CATEGORIES, OUT, ROOT, STARTER, list_docs

UI_DATA = ROOT.parent / "statute-street-ui" / "src" / "data"
RESULTS = {"applies", "unknown", "superseded", "not_yet_effective", "pending"}
STATUSES = {"in_force", "not_yet_effective", "pending", "failed"}

removed_dashes = 0


def tidy(s, prose=True):
    """Apply the internal-text filter (prose fields only) and replace dash punctuation (ids and dates keep hyphens)."""
    global removed_dashes
    if not isinstance(s, str):
        return s
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)   # literal "–" -> character
    if prose:
        s = publish.clean_text(s)
    n = len(re.findall(r"\s[—–-]\s|[—–]", s))
    removed_dashes += n
    date = r"(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})"
    s = re.sub(date + r"\s*[—–-]\s*" + date, r"\1 to \2", s)   # date ranges -> "3/1/2026 to 2/28/2027"
    s = re.sub(r"\s+[—–-]\s+", ", ", s)          # " — " / " – " / " - " between words -> ", "
    s = re.sub(r"(?<=\D)[—–](?=\D)", ", ", s)     # remaining em/en dashes between words
    s = re.sub(r"(\d)\s*[—–]\s*(\d)", r"\1 to \2", s)   # any remaining dash between numbers -> "to"
    return re.sub(r"\s+,", ",", s).strip()


def walk(obj, key=None):
    if isinstance(obj, dict):
        return {k: walk(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v, key) for v in obj]
    if not isinstance(obj, str) or key in ("team_rule_id", "address_id", "source_doc_id", "source_url", "url",
                                           "effective_date", "retrieved_at", "sha256", "governed_by"):
        return obj
    return tidy(obj, prose=key in publish.TEXT_FIELDS or key in ("summary", "instrument", "jurisdiction", "citation", "title"))


# ---------------------------------------------------------------------------
# Python mirror of src/data/index.ts (zod) - a record failing here would be skipped by the UI
# ---------------------------------------------------------------------------
def _nstr(v):
    return v is None or isinstance(v, str)


def check_rule(r: dict) -> list[str]:
    e = []
    for k in ("team_rule_id", "jurisdiction", "title", "requirement"):
        if not (isinstance(r.get(k), str) and r[k].strip()):
            e.append(f"{k}: non-empty string required")
    if r.get("level") not in ("state", "city"):
        e.append("level")
    if r.get("category") not in CATEGORIES:
        e.append("category")
    if r.get("status") not in STATUSES:
        e.append("status")
    for k in ("key_value", "coverage_conditions", "exemptions", "effective_date", "citation", "source_doc_id",
              "source_url", "quoted_span", "conflict_note"):
        if not _nstr(r.get(k)):
            e.append(f"{k}: string or null")
    c = r.get("confidence")
    if not (isinstance(c, (int, float)) and 0 <= c <= 1):
        e.append("confidence: number 0..1 required")
    for k in ("conflict_flag", "negative_finding"):
        if not isinstance(r.get(k), bool):
            e.append(f"{k}: boolean required")
    return e


def check_lookup_row(row: dict, rule_ids: set) -> list[str]:
    e = []
    if not (isinstance(row.get("team_rule_id"), str) and row["team_rule_id"]):
        e.append("team_rule_id")
    elif row["team_rule_id"] not in rule_ids:
        e.append(f"unknown rule {row['team_rule_id']}")
    if row.get("result") not in RESULTS:
        e.append("result")
    if not _nstr(row.get("explanation")):
        e.append("explanation")
    if "conflict_flag" in row and not isinstance(row["conflict_flag"], bool):
        e.append("conflict_flag")
    return e


def check_address(a: dict) -> list[str]:
    e = []
    for k in ("address_id", "street_address"):
        if not (isinstance(a.get(k), str) and a[k].strip()):
            e.append(k)
    if not (isinstance(a.get("state"), str) and len(a["state"]) >= 2):
        e.append("state")
    for k in ("postal_city", "zip", "year_built", "units"):
        if not _nstr(a.get(k)):
            e.append(k)
    return e


def check_source(s: dict) -> list[str]:
    e = []
    if not (isinstance(s.get("source_id"), str) and s["source_id"]):
        e.append("source_id")
    for k in ("jurisdiction", "title", "citation", "url", "retrieved_at", "sha256"):
        if not _nstr(s.get(k)):
            e.append(k)
    return e


def check_change(c: dict) -> list[str]:
    e = []
    if not (isinstance(c.get("affected_address_ids"), list) and all(isinstance(x, str) for x in c["affected_address_ids"])):
        e.append("affected_address_ids")
    if "conflict_flag_address_ids" in c and not isinstance(c["conflict_flag_address_ids"], list):
        e.append("conflict_flag_address_ids")
    if "notes" in c and not isinstance(c["notes"], str):
        e.append("notes")
    return e


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def load_short_values() -> dict:
    p = ROOT / "data" / "key_value_short.json"
    return json.loads(p.read_text(encoding="utf-8")).get("rules", {}) if p.exists() else {}


def build_rules() -> list[dict]:
    rules = json.loads((OUT / "public" / "rules.json").read_text(encoding="utf-8"))["rules"]
    have = {r["team_rule_id"] for r in rules}
    negs = json.loads((OUT / "negatives.json").read_text(encoding="utf-8"))["negatives"]
    shorts = load_short_values()
    out = []
    for r in rules + [n for n in negs if n["team_rule_id"] not in have]:
        r = dict(r)
        if r.get("negative_finding") and r.get("derived"):
            if r.get("notes"):
                r["requirement"] = f"{r['requirement'].rstrip('.')}. {r['notes']}".strip()
            r["key_value_short"] = "No city rule; state law applies" if r.get("level") == "city" else "No state rule"
        else:
            sv = shorts.get(r["team_rule_id"])
            if sv and sv.get("title_hint", "").lower() in (r.get("title") or "").lower():
                r["key_value_short"] = sv["text"]
            else:
                if sv:
                    print(f"  key_value_short for {r['team_rule_id']} skipped: title does not contain '{sv.get('title_hint')}'", file=sys.stderr)
                kv = r.get("key_value") or ""
                r["key_value_short"] = (kv if len(kv) <= 70 else kv[:67].rstrip() + "...") or None
            if r["key_value_short"] and len(r["key_value_short"]) > 70:
                print(f"  key_value_short for {r['team_rule_id']} is {len(r['key_value_short'])} chars (limit 70)", file=sys.stderr)
        if not isinstance(r.get("confidence"), (int, float)):
            r["confidence"] = 0.5
        m = re.match(r"^\s*\[([^\]]+)\]\s*", r.get("title") or "")   # safety: "[notice-only] ..." -> notes
        if m:
            r["title"] = r["title"][m.end():]
            r["notes"] = f"Tag: {m.group(1)}. {r.get('notes') or ''}".strip()
        r["negative_finding"] = bool(r.get("negative_finding", False))
        r["conflict_flag"] = bool(r.get("conflict_flag", False))
        for k in ("key_value", "coverage_conditions", "exemptions", "effective_date", "citation", "source_doc_id",
                  "source_url", "quoted_span", "conflict_note"):
            r.setdefault(k, None)
        out.append(r)
    return out


def build_lookups() -> dict:
    lk = json.loads((OUT / "public" / "lookups.json").read_text(encoding="utf-8"))
    out = {}
    for aid, rows in lk["lookups"].items():
        out[aid] = [{"team_rule_id": r["team_rule_id"], "result": r["result"], "explanation": r.get("explanation"),
                     "assumptions": r.get("assumptions") or [], "conflict_flag": bool(r.get("conflict_flag", False)),
                     **({"governed_by": r["governed_by"]} if r.get("governed_by") else {})}
                    for r in rows]
    return {"as_of": lk.get("as_of", "2026-10-01"), "lookups": out}


def build_change_register(rules: list[dict], changes: dict) -> list[dict]:
    """Display rows for the change register (rulings_12 section 3); counts from changes.json."""
    by_id = {r["team_rule_id"]: r for r in rules}

    def rule(jur, cat, cite_part=None, status=None):
        cands = [r for r in rules if r["jurisdiction"] == jur and r["category"] == cat and not r.get("negative_finding")
                 and (cite_part is None or cite_part in (r.get("citation") or "")) and (status is None or r["status"] == status)]
        return cands[0] if cands else {}

    def d(iso, fallback):
        return iso if iso else fallback

    ab325 = rule("CA", "algorithmic_rent_setting")
    hob = rule("Hoboken, NJ", "algorithmic_rent_setting", status="in_force")
    jc = rule("Jersey City, NJ", "algorithmic_rent_setting", status="in_force")
    rows = [
        {"test_id": "T1", "title": "California bans common pricing algorithms",
         "instrument": "AB 325 (Stats. 2025, ch. 338), Cal. Bus. & Prof. Code § 16729", "jurisdiction": "California",
         "enacted": d(ab325.get("adoption_date"), "Not stated"), "effective": "2026-01-01", "status": "in_force",
         "summary": "From 1 January 2026, using or distributing a common pricing algorithm as part of a price-fixing arrangement is unlawful. Applies to every California address in the portfolio."},
        {"test_id": "T2", "title": "Hoboken and Jersey City algorithm bans",
         "instrument": "Hoboken Code ch. 158; Jersey City Ord. 25-057", "jurisdiction": "Hoboken, NJ; Jersey City, NJ",
         "enacted": f"Hoboken {d(hob.get('adoption_date'), 'Not stated')}; Jersey City {d(jc.get('adoption_date'), 'Not stated')}",
         "effective": f"Hoboken {d(hob.get('effective_date'), 'Not stated')}; Jersey City {d(jc.get('effective_date'), 'Not stated')}",
         "status": "in_force",
         "summary": "Each city's ban applies only inside its own boundary, decided by the geocoded legal city, never the mailing address. Newark has no such ordinance."},
        {"test_id": "T3", "title": "New Jersey FAIR Act", "instrument": "P.L. 2026, c. 43", "jurisdiction": "New Jersey",
         "enacted": "2026-07-20", "effective": "2027-07-01", "status": "not_yet_effective",
         "summary": "Statewide ban on algorithmic rent setting from 1 July 2027. It may preempt the Hoboken and Jersey City ordinances; those addresses are flagged for human review."},
        {"test_id": "T4", "title": "Massachusetts algorithm bills", "instrument": "S.2983 and H.5222 (194th General Court)",
         "jurisdiction": "Massachusetts", "enacted": "Not enacted", "effective": "Not set", "status": "pending",
         "summary": "Pending bills, not law. If enacted they would reach every Massachusetts address in the portfolio."},
        {"test_id": "T5", "title": "Massachusetts rent control ballot question", "instrument": "Initiative Petition 25-21",
         "jurisdiction": "Massachusetts", "enacted": "Not enacted", "effective": "None", "status": "failed",
         "summary": "Struck from the ballot by the Supreme Judicial Court on 23 June 2026 (Cella v. Attorney General). No rent cap is reported for any Boston or Cambridge address."},
    ]
    for row in rows:
        c = changes.get(row["test_id"], {})
        row["addresses_affected"] = len(c.get("affected_address_ids", []))
        row["review_needed"] = len(c.get("conflict_flag_address_ids", []))
    return rows


def build_addresses() -> list[dict]:
    juris = json.loads((OUT / "jurisdictions.json").read_text(encoding="utf-8"))
    out = []
    with open(STARTER / "data" / "sample_addresses.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            j = juris.get(row["address_id"], {})
            out.append({"address_id": row["address_id"], "street_address": row["street_address"],
                        "postal_city": row["postal_city"], "state": row["state"], "zip": row["zip"],
                        "year_built": row["year_built"], "units": row["units"],
                        "legal_city": j.get("city") or "", "legal_state": j.get("state") or row["state"],
                        "jurisdiction_method": j.get("method") or "", "use_description": row.get("use_description", "")})
    return out


def build_sources(rules: list[dict]) -> list[dict]:
    docs = list_docs()
    manifest_sha = {d.doc_id: d.manifest.get("sha256") for d in docs.values()}
    cited: dict[str, dict] = {}
    for r in rules:
        for d in [r.get("source_doc_id"), *(r.get("supporting_doc_ids") or [])]:
            if not d or d not in docs:
                continue
            doc = docs[d]
            s = cited.setdefault(d, {
                "source_id": d, "jurisdiction": doc.jurisdiction_hint or r["jurisdiction"],
                "title": (doc.header.get("NOTE") or doc.body.strip().split("\n")[0][:120]).strip(),
                "citation": None, "url": doc.manifest.get("url") or doc.source_url,
                "retrieved_at": doc.retrieved_date, "sha256": manifest_sha.get(d) or hashlib.sha256(doc.body.encode("utf-8")).hexdigest(),
                "evidence_basis": ("supplied_corpus" if not doc.supplementary else
                                   "manual_primary" if d.startswith("M_") else "link_only_capture"),
                "capture_url": doc.source_url if doc.manifest.get("url") and doc.source_url != doc.manifest.get("url") else None,
                "cited_by": [],
            })
            s["cited_by"].append(r["team_rule_id"])
            if r.get("source_doc_id") == d and r.get("citation"):
                s["citation"] = r["citation"] if not s["citation"] else s["citation"]
    sources = list(cited.values())
    reg = ROOT / "sources" / "source_register.csv"
    if reg.exists():
        with open(reg, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cols = {c.lower(): c for c in (rows[0].keys() if rows else [])}
        def pick(row, *names):
            for n in names:
                if n in cols and row.get(cols[n]):
                    return row[cols[n]]
            return None
        for row in rows:
            sid = pick(row, "source_id", "id")
            if not sid or sid in cited:
                continue
            sources.append({"source_id": sid, "jurisdiction": pick(row, "jurisdiction", "jurisdictions"),
                            "title": pick(row, "title", "name", "description"), "citation": pick(row, "citation"),
                            "url": pick(row, "url", "source_url"), "retrieved_at": pick(row, "retrieved_at", "retrieved", "date"),
                            "sha256": pick(row, "sha256"), "evidence_basis": "register", "cited_by": []})
    return sources


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(UI_DATA))
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rules = build_rules()
    lookups = build_lookups()
    addresses = build_addresses()
    sources = build_sources(rules)
    changes = json.loads((OUT / "public" / "changes.json").read_text(encoding="utf-8"))

    register = build_change_register(rules, changes)
    files = {"rules.json": {"rules": rules}, "lookups.json": lookups, "changes.json": changes,
             "addresses.json": {"addresses": addresses}, "sources.json": {"sources": sources},
             "change_register.json": {"changes": register}}
    before = len(publish.removed)
    files = {k: walk(v) for k, v in files.items()}
    filtered = len(publish.removed) - before

    # Contract check (mirror of index.ts); refuse to write if the UI would skip anything.
    problems = []
    rule_ids = {r["team_rule_id"] for r in files["rules.json"]["rules"]}
    if len(rule_ids) != len(files["rules.json"]["rules"]):
        problems.append("rules.json: duplicate team_rule_id")
    for r in files["rules.json"]["rules"]:
        problems += [f"rules.json {r.get('team_rule_id')}: {m}" for m in check_rule(r)]
    for aid, rows in files["lookups.json"]["lookups"].items():
        for i, row in enumerate(rows):
            problems += [f"lookups.json {aid}[{i}]: {m}" for m in check_lookup_row(row, rule_ids)]
    for a in files["addresses.json"]["addresses"]:
        problems += [f"addresses.json {a.get('address_id')}: {m}" for m in check_address(a)]
    for s in files["sources.json"]["sources"]:
        problems += [f"sources.json {s.get('source_id')}: {m}" for m in check_source(s)]
    for tid, c in files["changes.json"].items():
        problems += [f"changes.json {tid}: {m}" for m in check_change(c)]
    for c in files["change_register.json"]["changes"]:
        for k in ("test_id", "title", "instrument", "jurisdiction", "enacted", "effective", "status", "summary"):
            if not isinstance(c.get(k), str) or not c[k]:
                problems.append(f"change_register.json {c.get('test_id')}: {k}")
        for k in ("addresses_affected", "review_needed"):
            if not isinstance(c.get(k), int):
                problems.append(f"change_register.json {c.get('test_id')}: {k}")
    if problems:
        print("CONTRACT PROBLEMS (nothing written):", file=sys.stderr)
        for p in problems[:30]:
            print("  ", p, file=sys.stderr)
        return 1

    sizes = {}
    for name, data in files.items():
        text = json.dumps(data, indent=1, ensure_ascii=False)
        (out_dir / name).write_text(text, encoding="utf-8")
        sizes[name] = len(text.encode("utf-8"))
    # Version stamp for the UI footer and reliance records (design brief v2, section 2). The UI reads
    # this file directly and falls back to "Engine version: see README" when it is absent, so
    # src/data/index.ts needs no change.
    # generated_at is the navigator HEAD commit date (not wall-clock time) so that exporting the
    # same commit twice yields byte-identical files.
    try:
        engine_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
        commit_iso = subprocess.check_output(["git", "log", "-1", "--format=%cI"], cwd=ROOT, text=True).strip()
        generated_at = datetime.fromisoformat(commit_iso).astimezone(timezone.utc).replace(microsecond=0) \
            .isoformat().replace("+00:00", "Z")
    except Exception:
        engine_commit, generated_at = "unknown", None
    n_derived = sum(1 for r in rules if r.get("derived"))
    meta = {"rules_version": "1.0", "engine_commit": engine_commit, "rules": len(rules),
            "rules_in_force": len(rules) - n_derived,     # the extracted rule records (the footer's "64 rules")
            "negative_findings": n_derived,               # derived "no rule at this level" records
            "addresses": len(addresses), "as_of": lookups.get("as_of", "2026-10-01"),
            "generated_at": generated_at}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    sizes["meta.json"] = (out_dir / "meta.json").stat().st_size
    print("meta.json:", meta)
    # Readability report (rulings_12 sections 6 and 7c): explanation templates and a seeded random sample
    import random
    rows_all = [(a, r) for a, v in files["lookups.json"]["lookups"].items() for r in v]
    def tmpl(s):
        s = re.sub(r"\d+ \w{3} \d{4}", "DATE", s); s = re.sub(r"\d+", "N", s); return re.sub(r"\(.*?\)", "(..)", s)[:80]
    import collections
    templates = collections.Counter(tmpl(r["explanation"]) for _, r in rows_all)
    rng = random.Random(42)
    sample = rng.sample(rows_all, 10)
    by_id = {r["team_rule_id"]: r for r in rules}
    bad = [(a, r["team_rule_id"], r["explanation"][:80]) for a, r in rows_all
           if not r["explanation"][:1].isupper() or re.search(r"\br-\d{4}\b|\bn-\d{4}\b|not_yet_effective|in_force|_eviction|_limits|_deposits|_fees|_restrictions|_setting|\d{4}-\d{2}-\d{2}", r["explanation"])]
    no_kv = [r["team_rule_id"] for r in rules if not r.get("negative_finding") and not r.get("key_value")]
    rep = [f"# UI export readability report", "", f"Distinct explanation templates: {len(templates)}", "",
           "| Count | Template |", "|---|---|"] + [f"| {n} | {t.replace('|', '/')} |" for t, n in templates.most_common(60)]
    rep += ["", f"Rows failing the readability checks (capital start, no ids, no enum words, no ISO dates): {len(bad)}", ""]
    rep += [f"- {a} {rid}: {e}" for a, rid, e in bad[:30]]
    rep += ["", "## 10 random rows (seed 42)", "", "| Address | Rule | Result | Explanation |", "|---|---|---|---|"]
    rep += [f"| {a} | {by_id[r['team_rule_id']]['title'][:45]} | {r['result']} | {r['explanation'].replace('|', '/')} |" for a, r in sample]
    rep += ["", f"Positive rules without key_value: {no_kv or 'none'}",
            f"Rules with key_value_short: {sum(1 for r in rules if r.get('key_value_short'))}/{len(rules)}"]
    (OUT / "ui_export_report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    print(f"readability: {len(templates)} templates, {len(bad)} rows failing checks, {len(no_kv)} positive rules without key_value -> out/ui_export_report.md")
    n_rows = sum(len(v) for v in files["lookups.json"]["lookups"].values())
    print(f"rules {len(rules)} (incl. {sum(1 for r in rules if r['negative_finding'])} negative findings) | "
          f"lookups {len(files['lookups.json']['lookups'])} addresses, {n_rows} rows | changes {len(changes)} | "
          f"addresses {len(addresses)} | sources {len(sources)}")
    print("bytes:", sizes)
    print(f"internal-text strings filtered: {filtered}; dash punctuation replaced: {removed_dashes}; contract problems: 0")
    print(f"written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
