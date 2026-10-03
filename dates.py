"""
dates.py - find sentences in the corpus that explicitly state when a provision
took effect, and parse the date they give.

Plain-language summary: statutes and agency pages say things like
"(SB 567) Effective January 1, 2024", "This section shall become operative on
April 1, 2024", "went into effect on October 14, 2024", "The Ordinance goes into
effect June 24, 2023". These are STATED dates and may be used (Hamza rulings_04
#2 step B). "Approved", "adopted", "amended by Ord. ..." are NOT effective
statements and are ignored here; sunset clauses ("remain in effect until") too.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from common import citation_sections, normalise

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}
MONTHS.update({"jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
               "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12})

_MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.?"
DATE_RE = re.compile(rf"(?P<mon>{_MONTH})\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?,?\s+(?P<year>\d{{4}})"
                     rf"|(?P<m>\d{{1,2}})[/-](?P<d>\d{{1,2}})[/-](?P<y>\d{{2,4}})", re.I)

# Words that introduce a statement about when a provision started to apply.
TRIGGER_RE = re.compile(
    r"\b(?:effective|operative|becomes? effective|became effective|shall (?:take|become) effect(?:ive)?|"
    r"takes? effect|took effect|went into effect|goes? into effect|will go into effect|"
    r"in force|eff\.)\b", re.I)
# ... unless the sentence is a sunset / repeal / unrelated usage.
EXCLUDE_RE = re.compile(r"\b(?:remain(?:s)? in effect|until|repealed|sunset|expires?|for tenancies in effect|"
                        r"in effect at the time|rate in effect|prior to|before)\b", re.I)


def parse_date(m: re.Match) -> str | None:
    """Return YYYY-MM-DD for a DATE_RE match, or None if it is not a real date."""
    try:
        if m.group("mon"):
            mon = MONTHS[m.group("mon").lower().rstrip(".")]
            d = date(int(m.group("year")), mon, int(m.group("day")))
        else:
            y = int(m.group("y"))
            y = y + 2000 if y < 100 else y
            d = date(y, int(m.group("m")), int(m.group("d")))
        return d.isoformat()
    except (ValueError, KeyError):
        return None


@dataclass
class DateHit:
    doc_id: str
    date: str          # YYYY-MM-DD
    sentence: str      # the stating sentence (normalised)
    near_section: bool # a section number of the rule appears within reach of the sentence


def _sentences(text: str):
    """Yield (start, sentence) over a normalised text, splitting on . ; and ) boundaries loosely."""
    for m in re.finditer(r"[^.;\n]+(?:\.\d+[^.;\n]*)*[.;]?", text):
        s = m.group(0).strip()
        if len(s) > 12:
            yield m.start(), s


BILL_RE = re.compile(r"\b(?:AB|SB|A\.B\.|S\.B\.|H|S)\.?\s?-?\s?(\d{2,5})\b|\b(?:Ord(?:inance)?\.? (?:No\.? )?)([A-Z]{0,3}-?\d{2,6}(?:-[A-Z]+)?)\b|\bO-(\d{4,6})\b")
MONTH_YEAR_RE = re.compile(rf"(?P<mon>{_MONTH})\s+(?P<year>\d{{4}})\b(?!\s*,?\s*\d)", re.I)
ADOPT_RE = re.compile(r"\b(?:adopted|passed|approved|enacted)\b", re.I)


def search_tokens(citation: str, *more_text: str) -> list[str]:
    """
    Strings whose presence in a document means it talks about this rule: section numbers
    from the citation ('1947.12', '13.63', '2a:18-61.1') and bill / ordinance numbers from the
    citation or title ('ab 1482' -> '1482', 'Ord. 7992' -> '7992').
    """
    toks = {t for tup in citation_sections(citation or "") for t in tup if len(t) >= 3}
    for text in (citation or "",) + more_text:
        for m in BILL_RE.finditer(text or ""):
            num = m.group(1) or m.group(2) or m.group(3)
            if num and len(num) >= 3:
                toks.add(num.lower())
    return sorted(toks, key=len, reverse=True)


def _positions(low: str, toks: list[str]) -> list[int]:
    pos = []
    for t in toks:
        pos += [m.start() for m in re.finditer(r"(?<![\w.])" + re.escape(t) + r"(?![\d])", low)]
    return pos


def _date_after_trigger(s: str, trig_re: re.Pattern, reach: int = 90) -> str | None:
    """The first date that follows the trigger word closely, as ISO (day or month precision)."""
    trig = trig_re.search(s)
    if not trig:
        return None
    for dm in DATE_RE.finditer(s):
        if dm.start() >= trig.start() and dm.start() - trig.end() <= reach:
            iso = parse_date(dm)
            if iso:
                return iso
    for mm in MONTH_YEAR_RE.finditer(s):  # "effective January 2026" -> 2026-01
        if mm.start() >= trig.start() and mm.start() - trig.end() <= reach:
            mon = MONTHS.get(mm.group("mon").lower().rstrip("."))
            if mon:
                return f"{mm.group('year')}-{mon:02d}"
    return None


def find_effective_dates(doc_body: str, doc_id: str, citation: str, *more_text: str,
                         window: int = 800) -> list[DateHit]:
    """All explicit effective-date statements in one document, flagged by proximity to the rule's section/bill."""
    text = normalise(doc_body)
    positions = _positions(text.lower(), search_tokens(citation, *more_text))
    hits = []
    for start, s in _sentences(text):
        if not TRIGGER_RE.search(s) or EXCLUDE_RE.search(s):
            continue
        iso = _date_after_trigger(s, TRIGGER_RE)
        if iso:
            near = any(abs(p - start) <= window for p in positions)
            hits.append(DateHit(doc_id, iso, s[:300], near))
    return hits


def find_adoption_dates(doc_body: str, doc_id: str, citation: str, *more_text: str,
                        window: int = 800) -> list[DateHit]:
    """Statements that an ordinance was adopted/passed on a date (ruling B fallback for local ordinances)."""
    text = normalise(doc_body)
    positions = _positions(text.lower(), search_tokens(citation, *more_text))
    hits = []
    for start, s in _sentences(text):
        if not ADOPT_RE.search(s) or re.search(r"\bgovernor\b", s, re.I):
            continue
        iso = _date_after_trigger(s, ADOPT_RE, reach=60)
        if not iso:  # "On April 14, 2020, Berkeley City Council passed ..." : date before the trigger
            dm = DATE_RE.search(s)
            if dm and ADOPT_RE.search(s).start() - dm.end() <= 120 and dm.end() < ADOPT_RE.search(s).start():
                iso = parse_date(dm)
        if iso and len(iso) == 10:
            near = any(abs(p - start) <= window for p in positions)
            hits.append(DateHit(doc_id, iso, s[:300], near))
    return hits


def mentions_near_section(doc_body: str, iso_date: str, citation: str, *more_text: str,
                          window: int = 800) -> str | None:
    """Does the document mention this date (any wording) near the rule's section/bill? Returns the snippet."""
    text = normalise(doc_body)
    positions = _positions(text.lower(), search_tokens(citation, *more_text))
    if not positions:
        return None
    for dm in DATE_RE.finditer(text):
        iso = parse_date(dm)
        if iso and (iso == iso_date or (len(iso_date) < 10 and iso.startswith(iso_date))):
            if any(abs(p - dm.start()) <= window for p in positions):
                return text[max(0, dm.start() - 120): dm.end() + 60]
    if len(iso_date) == 7:
        mon = [k for k, v in MONTHS.items() if v == int(iso_date[5:7]) and len(k) > 4][0]
        for mm in re.finditer(rf"\b{mon}\.?,?\s+{iso_date[:4]}\b", text, re.I):
            if any(abs(p - mm.start()) <= window for p in positions):
                return text[max(0, mm.start() - 120): mm.end() + 60]
    return None
