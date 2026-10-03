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


def normalise_citation(cite: str) -> str:
    """Looser normalisation for comparing citations: lowercase, no § or punctuation noise."""
    c = normalise(cite or "").lower()
    c = c.replace("§§", " ").replace("§", " ").replace("sec.", " ").replace("section", " ")
    c = re.sub(r"[^\w\s:.\-]", " ", c)
    c = re.sub(r"\s+", " ", c)
    return c.strip()
