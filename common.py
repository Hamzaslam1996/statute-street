"""
Shared helpers for Module A (extract.py, verify.py, eval.py).

Plain-language summary: this file knows where the documents live, how to read
the header lines at the top of each document, how to look up a document in the
organisers' manifest, and how to "normalise" text so that two copies of the
same sentence compare equal even if the quote marks or spacing differ.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Folder layout (see CLAUDE.md)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent                      # navigator/
STARTER = ROOT.parent / "participant-final-no-hour16 3"      # organisers' pack (read-only)
STARTER_TEXT = STARTER / "corpus" / "text"
MANIFEST_CSV = STARTER / "corpus" / "corpus_manifest.csv"
SCHEMA_JSON = STARTER / "schema" / "rule_record.schema.json"
SUPP_TEXT = ROOT / "corpus_supplementary" / "text"           # pages we captured ourselves
OUT = ROOT / "out"
RAW_DIR = OUT / "raw"
GOLD_DIR = ROOT / "gold"

# The challenge's default "as of" date. Rules are in force or not relative to this.
DEFAULT_QUERY_DATE = "2026-10-01"

CATEGORIES = [
    "rent_increase_limits",
    "just_cause_eviction",
    "security_deposits",
    "application_screening_fees",
    "screening_restrictions",
    "algorithmic_rent_setting",
]


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
@dataclass
class Doc:
    doc_id: str                     # e.g. "D024"
    path: Path                      # where the .txt file is
    source_url: str                 # from the SOURCE: header line
    retrieved: str                  # from the RETRIEVED: header line (raw string)
    header: dict = field(default_factory=dict)   # all KEY: value header lines
    body: str = ""                  # document text with the header removed
    manifest: dict = field(default_factory=dict) # the matching row of corpus_manifest.csv
    supplementary: bool = False     # True if we captured it (corpus_supplementary/)

    @property
    def source_type(self) -> str:
        """'official' or 'secondary (law firm / news / mirror)' etc."""
        return (self.header.get("SOURCE_TYPE")
                or self.manifest.get("source_type")
                or "unknown")

    @property
    def is_secondary(self) -> bool:
        return "secondary" in self.source_type.lower()

    @property
    def jurisdiction_hint(self) -> str:
        return self.manifest.get("jurisdictions", "")

    @property
    def retrieved_date(self) -> str | None:
        """Just the YYYY-MM-DD part of the RETRIEVED header."""
        m = re.match(r"(\d{4}-\d{2}-\d{2})", self.retrieved or "")
        return m.group(1) if m else None


def load_manifest() -> dict[str, dict]:
    """Return {doc_id: row} from the organisers' corpus_manifest.csv."""
    with open(MANIFEST_CSV, newline="", encoding="utf-8") as f:
        return {row["doc_id"]: row for row in csv.DictReader(f)}


def parse_header(text: str) -> tuple[dict, str]:
    """
    Split a document into (header dict, body).

    Every document starts with lines like
        SOURCE: https://...
        RETRIEVED: 2026-10-01 22:35 UTC
    followed by a blank line. Everything after the blank line is the body.
    """
    header: dict[str, str] = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Z_]+):\s*(.*)$", line)
        if m:
            header[m.group(1)] = m.group(2).strip()
            i += 1
        elif line.strip() == "" and header:
            i += 1
            break
        else:
            break
    body = "\n".join(lines[i:])
    return header, body


def list_docs() -> dict[str, Doc]:
    """
    Find every document we may extract from: the starter-pack text files plus
    our own supplementary captures. Anything under '_to_delete/' is skipped.
    If a doc_id exists in both places the starter-pack copy wins.
    """
    manifest = load_manifest()
    docs: dict[str, Doc] = {}

    def add(path: Path, supplementary: bool):
        if "_to_delete" in path.parts:
            return
        doc_id = path.stem
        if doc_id in docs:
            return  # starter pack takes precedence (it is added first)
        text = path.read_text(encoding="utf-8", errors="replace")
        header, body = parse_header(text)
        docs[doc_id] = Doc(
            doc_id=doc_id,
            path=path,
            source_url=header.get("SOURCE", manifest.get(doc_id, {}).get("url", "")),
            retrieved=header.get("RETRIEVED", manifest.get(doc_id, {}).get("retrieved_at", "")),
            header=header,
            body=body,
            manifest=manifest.get(doc_id, {}),
            supplementary=supplementary,
        )

    for p in sorted(STARTER_TEXT.glob("D*.txt")):
        add(p, supplementary=False)
    if SUPP_TEXT.exists():
        for p in sorted(SUPP_TEXT.glob("D*.txt")):
            add(p, supplementary=True)
    return docs


# ---------------------------------------------------------------------------
# Text normalisation (used to check that a quoted span really is in the doc)
# ---------------------------------------------------------------------------
_QUOTE_MAP = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",   # curly single quotes
    "“": '"', "”": '"', "„": '"', "‟": '"',   # curly double quotes
    "–": "-", "—": "-", "−": "-", "‐": "-",   # dashes
    " ": " ", " ": " ", " ": " ",                  # odd spaces
    "­": "",                                                # soft hyphen
}


def normalise(text: str) -> str:
    """
    Make text comparable: straight quotes, plain hyphens, single spaces, and
    markdown noise (backslash escapes, bold markers) removed. Case is kept.
    Applied identically to the document and to the model's quoted span, so
    only cosmetic differences are forgiven.
    """
    text = unicodedata.normalize("NFKC", text)
    for k, v in _QUOTE_MAP.items():
        text = text.replace(k, v)
    text = text.replace("\\", "")          # markdown escapes like "4\. An owner"
    text = text.replace("*", "")           # markdown bold/italic markers
    text = re.sub(r"\s+", " ", text)       # newlines, tabs, double spaces -> one space
    return text.strip()


def source_rank(doc) -> int:
    """
    How authoritative is a document? Lower is better (Hamza ruling 2026-10-04 #1):
      0 official statute / ordinance / bill text (legislature and code sites, ordinance PDFs)
      1 official agency page (rent board, housing department, city hall)
      2 code publisher (ecode360, American Legal, GoCodebook)
      3 secondary (law firm, news, Justia mirror)
    """
    st = (doc.source_type or "").lower()
    if "secondary" in st:
        return 3
    if "code publisher" in st:
        return 2
    url = (doc.source_url or "").lower()
    primary_markers = ("leginfo.legislature", "/laws/", "/bills/", "njleg", "municode",
                       "codes_display", "billnav", "ordinance", ".pdf")
    if "official" in st and any(m in url for m in primary_markers):
        return 0
    return 1


# --- citation section numbers (used to decide when two citations are the same rule) ---
_YEARISH = re.compile(r"^(19|20)\d\d(-(19|20)\d\d)?$|^\d+(st|nd|rd|th)$")
# A section-like token: optional short letter prefix glued on ('c.43', 's.2983', 'o-21955',
# 'ns-3090'), digits, optional letter, then any ':' '.' '-' joined parts ('2a:18-61.1', '13.63.030').
# The lookbehind stops the 'c.' of 'L.A.M.C.' or the 'a.' of 'N.J.S.A.' being taken as a prefix.
_SECTION_TOKEN = re.compile(r"(?<![a-z.])(?:[a-z]{1,2}[.\-])?\d+[a-z]?(?:[:.\-]\d+[a-z]?)*\b")
_SHORT_BARE = re.compile(r"^\d{1,2}$")   # article / title / division numbers like 'art. 1', 'tit. 2'


def citation_sections(cite: str) -> list[tuple[str, ...]]:
    """
    Turn a citation into tuples of section numbers, one tuple per ';'-separated cite.
    'Cal. Gov. Code § 12955; 2 C.C.R. § 12265' -> [('12955',), ('12265',)]
    'L.A.M.C. ch. XV, art. 1, § 151.00 et seq.' -> [('151',)]     ('.00 et seq.' = whole chapter)
    'P.L. 2026, c. 43'                          -> [('c.43',)]    (years are dropped)
    'M.G.L. c. 186, § 11'                       -> [('c.186', '11')]
    """
    out = []
    cite = re.sub(r"(\d),(\d{3})\b", r"\1\2", cite or "")                  # '7,992' -> '7992' (before commas are stripped)
    for piece in normalise_citation(cite).split(";"):
        piece = re.sub(r"(?:(?<=\s)|^)([a-z])\.\s+(\d)", r"\1.\2", piece)  # 'c. 43' -> 'c.43', 's. 2983' -> 's.2983'
        toks = []
        for t in _SECTION_TOKEN.findall(piece):
            if _YEARISH.match(t):
                continue
            t = re.sub(r"\.00$", "", t)  # '151.00' (et seq.) -> '151'
            toks.append(t)
        # 'ch. 9, art. 8, div. 7, § 98.0701': the small leading numbers are structure, not sections
        while len(toks) > 1 and _SHORT_BARE.match(toks[0]):
            toks.pop(0)
        if toks:
            out.append(tuple(toks))
    return out


def _seg_prefix(a: str, b: str) -> bool:
    """'13.76' is a prefix of '13.76.110'; '151' of '151.06'; '37.9' of '37.9c'. Not '19:2-18.1' of '19:2-18.4'."""
    if a == b:
        return True
    short, long_ = sorted((a, b), key=len)
    return long_.startswith(short) and (long_[len(short)] in ":.-" or long_[len(short):].isalpha())


def _in_range(tok: str, rng: str) -> bool:
    """'98.1103' lies in the range token '98.1101-98.1104'."""
    if "-" not in rng:
        return False
    lo, hi = rng.split("-", 1)
    if "." not in lo or "." not in hi or "." not in tok:
        return False
    try:
        plo, nlo = lo.rsplit(".", 1); phi, nhi = hi.rsplit(".", 1); pt, nt = tok.rsplit(".", 1)
        return plo == phi == pt and int(nlo) <= int(nt) <= int(nhi)
    except ValueError:
        return False


def sections_match(cite_a: str, cite_b: str) -> bool:
    """
    Do two citations point at the same provision (or one at a chapter containing the other)?
    Specific shared tokens (with a separator, e.g. '1950.5', '2a:18-61.1', '98.1103') match
    directly; otherwise the number tuples of one cite must be a prefix of the other's.
    """
    A, B = citation_sections(cite_a), citation_sections(cite_b)
    if not A or not B:
        return False
    specific = lambda t: any(ch in t for ch in ":.-") or (t.isdigit() and len(t) >= 4)

    def anchors(tup):
        # A specific token stands for the provision unless it is a chapter immediately
        # followed by its own section number ('c.186', '11'): then the pair decides.
        return [t for i, t in enumerate(tup)
                if specific(t) and (i == len(tup) - 1 or not _SHORT_BARE.match(tup[i + 1]))]

    for ta in A:
        for tb in B:
            for x in anchors(ta):
                for y in anchors(tb):
                    if _seg_prefix(x, y) or _in_range(x, y) or _in_range(y, x):
                        return True
            k = min(len(ta), len(tb))
            if ta[:k - 1] == tb[:k - 1] and _seg_prefix(ta[k - 1], tb[k - 1]):
                return True
    return False


_ORDINANCE_NO = re.compile(r"^[a-z]{1,2}-\d+(-\d+)?$")   # 'ns-3090', 'o-21955', 'b-781': an instrument, not a section


def has_sections(cite: str) -> bool:
    """Does the citation point at a specific code section (as opposed to just naming an ordinance)?"""
    return any(not _ORDINANCE_NO.match(t) for tup in citation_sections(cite) for t in tup)


def normalise_citation(cite: str) -> str:
    """Looser normalisation for comparing citations: lowercase, no § or punctuation noise."""
    c = normalise(cite or "").lower()
    c = c.replace("§§", " ").replace("§", " ").replace("sec.", " ").replace("section", " ")
    c = re.sub(r"[^\w\s:.\-]", " ", c)
    c = re.sub(r"\s+", " ", c)
    return c.strip()
