"""
recapture.py - re-fetch ONE source page whose first capture was unusable
(e.g. a table-of-contents page instead of the ordinance text).

Organiser ruling: single-page fetches of link-only sources are allowed, with
the retrieval date recorded. No bulk scraping.

Usage:
    python recapture.py D075 https://docs.sandiego.gov/municode/municodechapter09/ch09art08division08.pdf --source-type official
    python recapture.py D071 https://ecode360.com/42427482 --source-type "code publisher"

The old file is moved to corpus_supplementary/_to_delete/<doc>_toc.txt (never deleted),
the new text is written to corpus_supplementary/text/<doc>.txt with the usual header,
and a row is appended to corpus_supplementary/capture_log.csv.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from capture_links import fetch  # same Bright Data single-page fetch used for the first captures
from common import SUPP_TEXT, load_manifest

LOG = Path("corpus_supplementary/capture_log.csv")
TO_DELETE = Path("corpus_supplementary/_to_delete")


def fetch_direct(url: str):
    """One ordinary HTTPS GET (no proxy). PDF -> text with pypdf; HTML -> stripped text."""
    import io
    import re
    import requests
    from pypdf import PdfReader
    from capture_links import _Text
    r = requests.get(url, timeout=120, allow_redirects=True,
                     headers={"User-Agent": "Mozilla/5.0 (Macintosh) StatuteStreet/0.1 single-page fetch"})
    if r.status_code != 200:
        return r.status_code, r.text, "direct"
    if r.content[:4] == b"%PDF":
        reader = PdfReader(io.BytesIO(r.content))
        return 200, "\n".join((pg.extract_text() or "") for pg in reader.pages), "direct-pdf"
    t = _Text(); t.feed(r.text)
    return 200, re.sub(r"\n\s*\n+", "\n\n", "".join(t.out)), "direct-html-stripped"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("doc_id")
    ap.add_argument("url")
    ap.add_argument("--source-type", default=None, help="override the manifest source_type")
    ap.add_argument("--note", default="recaptured: first capture was a table-of-contents page")
    ap.add_argument("--direct", action="store_true",
                    help="fetch with a plain HTTPS request instead of Bright Data (for public PDFs the proxy returns empty)")
    args = ap.parse_args()

    manifest = load_manifest()
    row = manifest.get(args.doc_id, {})
    source_type = args.source_type or row.get("source_type", "unknown")
    retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if args.direct:
        status, body, method = fetch_direct(args.url)
    else:
        status, body, method = fetch(args.url)
    body = (body or "").strip()
    print(f"{args.doc_id}: HTTP {status} via {method}, {len(body):,} chars")
    print("--- preview ---")
    print(body[:800])
    print("--- end preview ---")
    if status != 200 or len(body) < 300:
        print("Capture unusable; nothing changed.", file=sys.stderr)
        return 1

    new_path = SUPP_TEXT / f"{args.doc_id}.txt"
    if new_path.exists():
        TO_DELETE.mkdir(parents=True, exist_ok=True)
        old = TO_DELETE / f"{args.doc_id}_toc.txt"
        shutil.move(str(new_path), str(old))
        print(f"old capture moved to {old}")

    via = ("direct HTTPS request" if method.startswith("direct") else "Bright Data Web Unlocker")
    text = (f"SOURCE: {args.url}\nRETRIEVED: {retrieved}\n"
            f"CAPTURED_VIA: {via} ({method}; single page, team capture)\n"
            f"SOURCE_TYPE: {source_type}\n"
            f"MANIFEST_URL: {row.get('url', '')}\n"
            f"NOTE: {args.note}\n\n{body}\n")
    new_path.write_text(text, encoding="utf-8")
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([args.doc_id, row.get("jurisdictions", ""), source_type, args.url,
                                retrieved, status, len(body),
                                hashlib.sha256(text.encode()).hexdigest(), f"recaptured ({args.note})"])
    print(f"written {new_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
