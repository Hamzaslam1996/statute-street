"""
open_questions.py - write out/open_questions.json: the organisers' known open questions
(README §9), each with both sources (from our corpus), their dates, and how our system
answers. We flag these; we do not resolve them.
"""

from __future__ import annotations

import json
import sys

from common import OUT, list_docs

ITEMS = [
    {
        "id": "OQ1",
        "question": "Berkeley algorithmic-rent ban (BMC ch. 13.63, Ord. 7992): two published effective dates.",
        "positions": [
            {"claim": "1 March 2026 (ordinance text, per the organisers' brief)", "doc_ids": ["D001"]},
            {"claim": "January 2026 (law-firm alert, August 2026)", "doc_ids": ["D002", "D037"]},
        ],
        "jurisdiction": "Berkeley, CA", "category": "algorithmic_rent_setting",
    },
    {
        "id": "OQ2",
        "question": "New Jersey FAIR Act (P.L. 2026, c.43) may pre-empt the Jersey City (§ 218-12) and Hoboken (ch. 158) algorithmic-rent ordinances once effective on 2027-07-01.",
        "positions": [
            {"claim": "FAIR Act § 6(b): municipalities may not enact conflicting ordinances", "doc_ids": ["D069", "D060"]},
            {"claim": "Local bans adopted 2025 remain on the books", "doc_ids": ["M_JC-ALG-01_Ord_25-057_adopted", "M_HOB-ALG-01_Hoboken_ch158_ecode360", "D034"]},
        ],
        "jurisdiction": "NJ", "category": "algorithmic_rent_setting",
    },
    {
        "id": "OQ3",
        "question": "Los Angeles RSO new allowable-increase formula: two published effective dates.",
        "positions": [
            {"claim": "2026-02-02 (Los Angeles Housing Department)", "doc_ids": ["D041", "D042"]},
            {"claim": "2026-01-24 (landlord association)", "doc_ids": ["D044"]},
        ],
        "jurisdiction": "Los Angeles, CA", "category": "rent_increase_limits",
    },
    {
        "id": "OQ4",
        "question": "California application screening-fee cap (Civ. Code § 1950.6): no single official 2026 dollar figure.",
        "positions": [
            {"claim": "Statute: $30 base adjusted annually by CPI since 1998; the current figure is not stated", "doc_ids": ["D026", "D017"]},
        ],
        "jurisdiction": "CA", "category": "application_screening_fees",
    },
]


def main() -> int:
    docs = list_docs()
    rules = json.loads((OUT / "rules_full.json").read_text(encoding="utf-8"))["rules"]
    out = []
    for item in ITEMS:
        for p in item["positions"]:
            p["sources"] = [{"doc_id": d, "url": docs[d].source_url, "retrieved": docs[d].retrieved_date,
                             "source_type": docs[d].source_type} for d in p["doc_ids"] if d in docs]
        ours = [r for r in rules if r["jurisdiction"] == item["jurisdiction"] and r["category"] == item["category"]
                and not r.get("negative_finding") and not r.get("derived")]
        item["our_answer"] = [{"team_rule_id": r["team_rule_id"], "effective_date": r.get("effective_date"),
                               "key_value": r.get("key_value"), "conflict_flag": r.get("conflict_flag"),
                               "conflict_note": r.get("conflict_note"), "date_source_doc_id": r.get("date_source_doc_id")}
                              for r in ours]
        item["how_we_handle_it"] = {
            "OQ1": "We record the date stated in a corpus document (January 2026 from the law-firm alert, month precision) and set conflict_flag with a note naming both dates; the rule is in force on the default query date either way.",
            "OQ2": "The engine flags every Jersey City and Hoboken algorithmic-ban row and the FAIR Act row with conflict_flag and 'Possible preemption by the NJ FAIR Act from 2027-07-01 — flagged for human review'. We do not decide preemption.",
            "OQ3": "We use the LAHD date (official agency page) as effective_date and set conflict_flag with a note recording the landlord-association date.",
            "OQ4": "key_value stays the statutory formula ($30 adjusted by CPI) rather than a dollar figure; the statute states no 2026 amount.",
        }[item["id"]]
        out.append(item)
    (OUT / "open_questions.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for item in out:
        print(item["id"], item["question"][:80], "| ours:", [(a["team_rule_id"], a["effective_date"], a["conflict_flag"]) for a in item["our_answer"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
