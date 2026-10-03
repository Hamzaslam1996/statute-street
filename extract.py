"""
extract.py - Module A, step 1: ask Claude to turn each source document into
structured rule records.

Plain-language summary
----------------------
For every document in the corpus we send the text to Claude with a strict
answer template (a JSON schema). Claude returns zero or more "rule records":
jurisdiction, category, what the rule requires, the headline number, the
citation, and an exact quote from the document that supports it. We save the
raw answer to out/raw/D###.json so we never pay twice for the same document,
and we log every call (tokens, cost, time) to out/extract_log.csv.

Nothing here is hand-coded law. The checks that the quote really appears in
the document, the status calculation, and schema validation live in verify.py.

Usage
-----
    python extract.py --docs D024 D063 D069
    python extract.py --all
    python extract.py --docs D069 --model claude-opus-5-5 --force
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from common import (CATEGORIES, DEFAULT_QUERY_DATE, OUT, RAW_DIR, Doc,
                    list_docs)

load_dotenv()  # reads ANTHROPIC_API_KEY from .env (never printed or logged)

DEFAULT_MODEL = os.environ.get("EXTRACT_MODEL", "claude-sonnet-5-5")

# US$ per million tokens, used only to estimate spend in the log.
PRICES = {
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-fable-5-1": (10.00, 50.00),
}

# Documents longer than this (in characters) are split into overlapping chunks.
# Most documents are far shorter; only one or two in the corpus exceed it.
MAX_TOKENS = 32_000      # output cap per call; thinking tokens count towards it

CHUNK_THRESHOLD = 80_000
CHUNK_SIZE = 60_000
CHUNK_OVERLAP = 4_000

LOG_CSV = OUT / "extract_log.csv"
LOG_FIELDS = ["timestamp", "doc_id", "chunk", "model", "attempt", "input_tokens",
              "output_tokens", "cache_read_tokens", "cost_usd", "seconds",
              "n_rules", "stop_reason", "request_id"]


# ---------------------------------------------------------------------------
# The answer template Claude must follow (a JSON schema).
# It mirrors rule_record.schema.json but leaves out fields we fill in code
# (team_rule_id, source_doc_id, source_url, overrides) and adds a notes field.
# ---------------------------------------------------------------------------
def nullable(t: str) -> dict:
    return {"type": [t, "null"]}


RULE_PROPERTIES = {
    "jurisdiction": {
        "type": "string",
        "description": "State code ('CA','NJ','MA') or 'City, ST' (e.g. 'San Francisco, CA').",
    },
    "level": {"type": "string", "enum": ["state", "city"]},
    "category": {"type": "string", "enum": CATEGORIES},
    "status": {
        "type": "string",
        "enum": ["in_force", "not_yet_effective", "pending", "failed"],
        "description": "Your best reading as of the query date. 'pending' = a bill or "
                       "proposal that is not law; 'failed' = defeated, vetoed or struck down.",
    },
    "title": {"type": "string", "description": "Short name of the law or rule."},
    "requirement": {
        "type": "string",
        "description": "One or two plain-language sentences stating what the rule requires.",
    },
    "key_value": {
        **nullable("string"),
        "description": "The headline number, formula or prohibition a renter or landlord would act on, "
                       "e.g. '1.5 months rent', '5% + CPI, max 10%', 'Ban on algorithmic rent-setting "
                       "devices'. Never the penalty for breaking the rule.",
    },
    "coverage_conditions": {
        **nullable("string"),
        "description": "Who/what is covered: year-built or certificate-of-occupancy cutoffs, "
                       "unit counts, owner type, tenancy length. Quote thresholds exactly.",
    },
    "exemptions": nullable("string"),
    "interaction": {
        **nullable("string"),
        "description": "How this rule interacts with rules at other levels (e.g. yields to "
                       "stricter local rent control; preempts conflicting municipal ordinances).",
    },
    "effective_date": {
        **nullable("string"),
        "description": "YYYY-MM-DD, YYYY-MM or YYYY. The date the requirement took or takes effect, "
                       "only from text saying it 'takes effect', 'becomes operative', is 'effective' "
                       "or 'operative' on a date. If the document gives a formula (e.g. 'first day of "
                       "the twelfth month after enactment') compute it and explain in extraction_notes. "
                       "For a local ordinance that states only an adoption date, give the adoption "
                       "MONTH as YYYY-MM. null if the document states nothing.",
    },
    "adoption_date": {
        **nullable("string"),
        "description": "YYYY-MM-DD the ordinance or act was adopted/approved/passed, if stated. "
                       "null otherwise.",
    },
    "negative_finding": {
        "type": "boolean",
        "description": "true when this record documents that NO rule applies at this level in this "
                       "category (e.g. a state law barring local rent control, or a defeated / struck "
                       "measure). false for an ordinary rule.",
    },
    "citation": {
        "type": "string",
        "description": "Official cite of the underlying law, e.g. 'Cal. Civ. Code § 1947.12', "
                       "'N.J.S.A. 46:8-21.2', 'S.F. Admin. Code § 37.10C'.",
    },
    "quoted_span": {
        "type": "string",
        "description": "A single contiguous passage copied EXACTLY, character for character, "
                       "from the document text below (20-800 characters). Do not paraphrase, "
                       "fix typos, add ellipses, or join separate sentences.",
    },
    "confidence": {"type": "number", "description": "0 to 1."},
    "conflict_flag": {
        "type": "boolean",
        "description": "true if the document reveals a conflict or open question (two published "
                       "effective dates, possible preemption, litigation, etc.).",
    },
    "conflict_note": nullable("string"),
    "extraction_notes": {
        **nullable("string"),
        "description": "Anything the reviewer should know: how a date was computed, last-amended "
                       "info (e.g. 'as amended by SB 567, eff. 2024-04-01'), why effective_date is "
                       "null, ambiguity, whether this document is a summary of law found elsewhere.",
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "document_summary": {
            "type": "string",
            "description": "One sentence: what this document is and which jurisdiction(s) it covers.",
        },
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": RULE_PROPERTIES,
                "required": list(RULE_PROPERTIES.keys()),
                "additionalProperties": False,
            },
        },
    },
    "required": ["document_summary", "rules"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = f"""You are a careful legal research assistant extracting rental-housing rules from source documents for a prototype that tells users which rules apply to a U.S. apartment address. This is not legal advice.

Scope
- Jurisdictions: the states of California (CA), New Jersey (NJ) and Massachusetts (MA), and the cities of Los Angeles, San Francisco, San Diego, Berkeley, Santa Ana (CA); Jersey City, Hoboken, Newark (NJ); Boston, Cambridge (MA). Ignore rules of any other state or city.
- Categories (use these exact slugs only): {", ".join(CATEGORIES)}.
  * rent_increase_limits: caps or formulas on rent increases (rent control / stabilisation, anti-gouging caps), including annual allowable increase notices.
  * just_cause_eviction: limits on the grounds for eviction or non-renewal, and attached relocation-assistance duties.
  * security_deposits: limits on deposit amount, interest, holding and return.
  * application_screening_fees: caps on, or rules about, fees charged to rental applicants.
  * screening_restrictions: limits on what a landlord may consider about an applicant (criminal history, source of income / vouchers, credit, eviction history).
  * algorithmic_rent_setting: bans or limits on algorithmic / software-based rent setting or price coordination.

What counts as a rule (granularity)
- One record per jurisdiction x category x section, holding the HEADLINE requirement: the number or prohibition a renter or landlord would act on. Fold procedural sub-duties (return deadlines, itemised statements, photographs, "no non-refundable deposits", notice mechanics) into `requirement` or `extraction_notes`, not separate records.
- Keep separate records only when they fall in a DIFFERENT category or carry a DIFFERENT key value that would change the answer for an address.
- Relocation-assistance payments that follow a no-fault eviction belong in ONE just_cause_eviction record for that jurisdiction (amounts in `key_value` or `extraction_notes`), not one record per payment schedule.
- Do not split a single cap and its exemptions into several records; put exemptions in `exemptions` and thresholds in `coverage_conditions`.
- A document may yield zero rules (e.g. a navigation page or a document about another topic). Return an empty list rather than inventing anything.

Negative findings
- When a document establishes that NO rule exists at a level in a category, record that as a record with `negative_finding` true. Two cases:
  (a) a law that bars rules at a lower level (e.g. a state statute prohibiting local rent control): status `in_force`, title like "No local rent control permitted (state bar)", key_value like "No rent cap: state law bars local rent control".
  (b) a measure that was defeated, vetoed or struck down: status `failed`, key_value describing what it would have done.
- Ordinary rules have `negative_finding` false.
- If the document is a secondary source (law firm alert, news article, Justia mirror), still extract what it says, cite the underlying law in `citation`, but the `quoted_span` must come from THIS document.
- Bills that have not been enacted are `pending`. Measures that were defeated, vetoed, or struck down by a court are `failed`. Enacted laws are `in_force` or `not_yet_effective` depending on whether their effective date is on or before the query date {DEFAULT_QUERY_DATE}.
- `effective_date` means the date the specific extracted requirement first took effect. If a later amendment changed the key value itself (e.g. a lower cap), use the amendment date instead, and record the amendment in `extraction_notes` (e.g. "as amended by SB 567, eff. 2024-04-01"). A re-enactment that kept the same requirement does NOT reset the date.
- Record effective dates as precisely as the text allows. If the text says the act takes effect a set time after enactment and gives the enactment date, compute the date and say how in `extraction_notes`.
- Never infer an effective date from amendment history, legislative history notes, or the citations at the end of a statute (e.g. "L.1971,c.223; amended 2003, c.188"). If the text does not state when the requirement took effect, return null and explain in `extraction_notes`.
- Only text saying a provision "takes effect", "becomes operative", is "effective" or "operative" on a date counts as an effective date. Look-back, application or "applies to increases on or after" dates are NOT effective dates (they say what the rule reaches, not when it started). An enacted section in the official code with no stated effective date is still `in_force`.
- Local ordinances that state only an adoption date (e.g. "Adopted 7-9-2025 by Ord. No. B-781"): set `adoption_date` to the full date, set `effective_date` to the adoption MONTH (YYYY-MM), and add to `extraction_notes`: "Month of adoption; exact effective date not stated in source (NJ ordinances generally take effect after final passage and publication)." (adapt the state name).
- If a document states an explicit effective date for a CHANGE to the key value (e.g. "Effective February 2, 2026, the landlord can no longer include ..."), that date is the record's `effective_date` (the amendment exception above).

Known open questions (from the organisers' brief; if the document concerns one of these, set `conflict_flag` true and state the open question in `conflict_note`)
- Berkeley's algorithmic-rent ban (BMC ch. 13.63, Ord. 7992) has two published effective dates: 1 March 2026 in the ordinance text, January 2026 per an August 2026 law-firm alert.
- New Jersey's FAIR Act (P.L. 2026, c.43) may preempt the Jersey City and Hoboken algorithmic-rent ordinances once it takes effect.
- Los Angeles's new RSO formula has two published effective dates: 2026-02-02 per LAHD, 2026-01-24 per a landlord association.
- California's screening-fee cap (Civ. Code § 1950.6) has no single official 2026 dollar figure.
If the document does not itself contain the disputed date or figure, say so in `conflict_note` (e.g. "Not found in this capture.").
- Record coverage thresholds exactly as written (e.g. "certificate of occupancy issued before 1979-06-13" is different from "built before 1979").
- When the document shows a conflict, open question, or a possible preemption of another level of government, set `conflict_flag` true and explain in `conflict_note` and `interaction`.

Quoted spans
- `quoted_span` must be a verbatim, contiguous excerpt of the document text, 20-800 characters, that directly supports the requirement and key value. Copy it exactly as it appears, including odd spacing or line breaks within the passage. Never paraphrase. Every record is rejected automatically if its span is not found in the document.
- Choose the OPERATIVE sentence: the one that states the duty, cap or prohibition (look for "shall", "shall not", "may not", "unlawful", "prohibited") and, where possible, contains the key value. Do not quote a definition, a purpose or findings clause, a penalty or cross-reference, or a heading.
- Quote the COMPLETE sentence where one exists, not a clause from it: start at the sentence's first word and continue to its full stop, even if the document breaks the sentence across several lines (line breaks inside the quote are fine and expected; the checker ignores whitespace differences).
- For list-form provisions, quote contiguously from the lead-in ("It shall be unlawful ... for:") through the relevant item, including any intervening items, as long as the whole passage is under 800 characters. Only if that is impossible quote the item's full line. Tables with no sentence may be quoted as the relevant row.

Length
- Be concise. `requirement` is one or two sentences; `extraction_notes`, `exemptions` and `coverage_conditions` each under 800 characters. Do not restate the whole statute.

Respond only with JSON matching the schema."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def chunk_text(body: str) -> list[str]:
    """Split a long document into overlapping pieces at paragraph boundaries."""
    if len(body) <= CHUNK_THRESHOLD:
        return [body]
    chunks, start = [], 0
    while start < len(body):
        end = min(start + CHUNK_SIZE, len(body))
        if end < len(body):
            # back up to the last blank line so we do not cut mid-sentence
            cut = body.rfind("\n\n", start + CHUNK_SIZE // 2, end)
            if cut != -1:
                end = cut
        chunks.append(body[start:end])
        if end >= len(body):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def estimate_cost(model: str, usage) -> float:
    inp, outp = PRICES.get(model, (0.0, 0.0))
    cached = getattr(usage, "cache_read_input_tokens", 0) or 0
    # cache reads are billed at roughly a tenth of the input price
    return (usage.input_tokens * inp + cached * inp * 0.1 + usage.output_tokens * outp) / 1_000_000


def session_spend() -> float:
    """Total estimated US$ of every call recorded in out/extract_log.csv."""
    if not LOG_CSV.exists():
        return 0.0
    with open(LOG_CSV, newline="", encoding="utf-8") as f:
        return round(sum(float(r["cost_usd"] or 0) for r in csv.DictReader(f)), 4)


def append_log(row: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    new = not LOG_CSV.exists()
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def build_user_message(doc: Doc, chunk: str, chunk_no: int, n_chunks: int,
                       feedback: str | None) -> str:
    part = f" (part {chunk_no} of {n_chunks}; other parts are sent separately)" if n_chunks > 1 else ""
    msg = (
        f"Document id: {doc.doc_id}{part}\n"
        f"Source URL: {doc.source_url}\n"
        f"Retrieved: {doc.retrieved}\n"
        f"Source type (from manifest): {doc.source_type}\n"
        f"Jurisdiction hint (from manifest, may be incomplete): {doc.jurisdiction_hint or 'none'}\n"
        f"Query date: {DEFAULT_QUERY_DATE}\n"
    )
    if feedback:
        msg += (
            "\nIMPORTANT - a previous attempt was rejected because some quoted spans were not "
            "found verbatim in the document. Re-extract, copying each quoted_span exactly:\n"
            f"{feedback}\n"
        )
    msg += "\n===== DOCUMENT TEXT =====\n" + chunk + "\n===== END OF DOCUMENT ====="
    return msg


# ---------------------------------------------------------------------------
# The API call
# ---------------------------------------------------------------------------
def call_model(client: anthropic.Anthropic, model: str, doc: Doc, chunk: str,
               chunk_no: int, n_chunks: int, attempt: int,
               feedback: str | None = None) -> dict:
    """One request to Claude for one chunk of one document. Returns the parsed JSON."""
    t0 = time.time()
    # Streaming lets the request run longer than the SDK's 10-minute non-streaming
    # limit; we only use the final assembled message.
    with client.messages.stream(
        model=model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user",
                   "content": build_user_message(doc, chunk, chunk_no, n_chunks, feedback)}],
        output_config={"effort": "high",
                       "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
    ) as stream:
        response = stream.get_final_message()
    seconds = round(time.time() - t0, 1)

    if response.stop_reason == "refusal":
        detail = response.stop_details.explanation if response.stop_details else ""
        print(f"  !! {doc.doc_id}: model declined ({detail})", file=sys.stderr)
        data = {"document_summary": "", "rules": [], "error": f"refusal: {detail}"}
    elif response.stop_reason == "max_tokens":
        print(f"  !! {doc.doc_id}: output cut off at max_tokens", file=sys.stderr)
        # Keep whatever came back so the failure can be diagnosed.
        partial = "".join(getattr(b, "text", "") for b in response.content if b.type == "text")
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        (RAW_DIR / f"{doc.doc_id}.truncated.txt").write_text(partial, encoding="utf-8")
        data = {"document_summary": "", "rules": [], "error": "max_tokens"}
    else:
        text = next((b.text for b in response.content if b.type == "text"), "")
        data = json.loads(text)

    append_log({
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "doc_id": doc.doc_id, "chunk": f"{chunk_no}/{n_chunks}", "model": model,
        "attempt": attempt,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
        "cost_usd": round(estimate_cost(model, response.usage), 4),
        "seconds": seconds, "n_rules": len(data.get("rules", [])),
        "stop_reason": response.stop_reason,
        "request_id": getattr(response, "_request_id", None),  # absent on streamed messages
    })
    data["_usage"] = {"input_tokens": response.usage.input_tokens,
                      "output_tokens": response.usage.output_tokens,
                      "cost_usd": round(estimate_cost(model, response.usage), 4),
                      "seconds": seconds}
    return data


def dedupe_chunks(rules: list[dict]) -> list[dict]:
    """When a long doc is chunked with overlap, the same rule may come back twice."""
    seen: dict[tuple, dict] = {}
    for r in rules:
        key = (r.get("jurisdiction"), r.get("category"), (r.get("citation") or "").lower().strip())
        if key not in seen or (r.get("confidence") or 0) > (seen[key].get("confidence") or 0):
            seen[key] = r
    return list(seen.values())


def extract_doc(doc: Doc, model: str = DEFAULT_MODEL, attempt: int = 1,
                feedback: str | None = None,
                client: anthropic.Anthropic | None = None) -> dict:
    """
    Extract rules from one document (all chunks), save the raw answer to
    out/raw/<doc_id>.json and return it. verify.py calls this again with
    `feedback` when quoted spans fail the exact-match check.
    """
    client = client or anthropic.Anthropic()
    chunks = chunk_text(doc.body)
    all_rules, summaries, usage = [], [], {"input_tokens": 0, "output_tokens": 0,
                                           "cost_usd": 0.0, "seconds": 0.0}
    errors = []
    for i, chunk in enumerate(chunks, start=1):
        data = call_model(client, model, doc, chunk, i, len(chunks), attempt, feedback)
        all_rules.extend(data.get("rules", []))
        if data.get("document_summary"):
            summaries.append(data["document_summary"])
        if data.get("error"):
            errors.append(data["error"])
        for k in usage:
            usage[k] = round(usage[k] + data["_usage"][k], 4)

    result = {
        "doc_id": doc.doc_id,
        "model": model,
        "attempt": attempt,
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_url": doc.source_url,
        "retrieved": doc.retrieved,
        "source_type": doc.source_type,
        "n_chunks": len(chunks),
        "document_summary": " | ".join(summaries),
        "rules": dedupe_chunks(all_rules) if len(chunks) > 1 else all_rules,
        "usage": usage,
        "errors": errors,
    }
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"{doc.doc_id}.json"
    if attempt > 1 and out_path.exists():
        # keep the first attempt for the audit trail
        out_path.rename(RAW_DIR / f"{doc.doc_id}.attempt{attempt - 1}.json")
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Extract rule records from the corpus with Claude.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--docs", nargs="+", metavar="D###", help="document ids to process")
    g.add_argument("--all", action="store_true", help="process every document")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model id (default {DEFAULT_MODEL})")
    ap.add_argument("--force", action="store_true", help="re-run even if out/raw/D###.json exists")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation for large runs")
    ap.add_argument("--budget", type=float, default=None,
                    help="hard stop (US$) on cumulative spend recorded in out/extract_log.csv")
    args = ap.parse_args()

    spent = session_spend()
    if args.budget is not None:
        print(f"Spent so far (all runs logged): ${spent:.3f}; budget ${args.budget:.2f}.")
        if spent >= args.budget:
            print("Budget already reached; nothing run.")
            return 4

    docs = list_docs()
    if args.all:
        targets = sorted(docs)
    else:
        missing = [d for d in args.docs if d not in docs]
        if missing:
            print(f"Unknown document ids: {missing}", file=sys.stderr)
            return 2
        targets = args.docs

    todo = [d for d in targets if args.force or not (RAW_DIR / f"{d}.json").exists()]
    skipped = len(targets) - len(todo)
    print(f"{len(targets)} document(s) requested, {skipped} already cached, {len(todo)} to run "
          f"with {args.model}.")
    if len(todo) > 50 and not args.yes:
        answer = input(f"About to call the API for {len(todo)} documents. Continue? [y/N] ")
        if answer.strip().lower() != "y":
            print("Aborted.")
            return 1

    client = anthropic.Anthropic()
    total = {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
    for doc_id in todo:
        doc = docs[doc_id]
        print(f"- {doc_id} ({len(doc.body):,} chars, {doc.source_type}) ...", end=" ", flush=True)
        try:
            res = extract_doc(doc, args.model, client=client)
        except anthropic.RateLimitError as e:
            print(f"rate limited ({e.message}); stopping.", file=sys.stderr)
            return 3
        except anthropic.APIStatusError as e:
            print(f"API error {e.status_code}: {e.message}", file=sys.stderr)
            continue
        u = res["usage"]
        for k in total:
            total[k] = round(total[k] + u[k], 4)
        spent += u["cost_usd"]
        print(f"{len(res['rules'])} rule(s), {u['input_tokens']:,} in / {u['output_tokens']:,} out "
              f"tokens, ${u['cost_usd']:.4f}, {u['seconds']}s")
        if args.budget is not None and spent >= args.budget:
            remaining = todo[todo.index(doc_id) + 1:]
            print(f"\nBUDGET STOP: ${spent:.3f} spent >= ${args.budget:.2f}. "
                  f"{len(remaining)} document(s) not run: {' '.join(remaining)}")
            break

    print(f"\nRun total: {total['input_tokens']:,} input tokens, {total['output_tokens']:,} output "
          f"tokens, about ${total['cost_usd']:.4f}. Raw output in {RAW_DIR}/, log in {LOG_CSV}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
