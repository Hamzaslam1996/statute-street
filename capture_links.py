"""
capture_links.py — fetches the "link-only" sources from the starter pack, one page at a time,
and saves each as plain text with its source URL and retrieval date (organiser ruling:
individual public pages OK, record retrieval date, no bulk scraping).

Run:   python capture_links.py            (all missing pages)
       python capture_links.py D032 D033  (only these)
Output: corpus_supplementary/text/Dxxx.txt  +  corpus_supplementary/capture_log.csv
"""
import csv, hashlib, io, os, sys, time, glob, re
from html.parser import HTMLParser
from pypdf import PdfReader
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ["BRIGHTDATA_API_TOKEN"]
ZONE = os.environ["BRIGHTDATA_ZONE"]

# Find the starter pack's manifest (folder name has a space and a number in it)
MANIFEST = glob.glob("../participant-final-no-hour16*/corpus/corpus_manifest.csv")[0]
OUT_DIR = "corpus_supplementary/text"
LOG = "corpus_supplementary/capture_log.csv"
PAUSE_SECONDS = 3  # polite gap between requests: one page at a time, never bulk
os.makedirs(OUT_DIR, exist_ok=True)


class _Text(HTMLParser):
    """Strips HTML tags, keeps readable text (skips scripts/styles/menus)."""
    def __init__(self):
        super().__init__(); self.out=[]; self.skip=0
    def handle_starttag(self, tag, a):
        if tag in ("script","style","nav","header","footer","noscript"): self.skip+=1
        if tag in ("p","div","li","br","h1","h2","h3","h4","tr","section"): self.out.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script","style","nav","header","footer","noscript") and self.skip: self.skip-=1
    def handle_data(self, d):
        if not self.skip: self.out.append(d)


def _call(url, markdown):
    body = {"zone": ZONE, "url": url, "format": "raw"}
    if markdown:
        body["data_format"] = "markdown"
    return requests.post(
        "https://api.brightdata.com/request",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json=body, timeout=180)


def fetch(url):
    """Try 1: clean markdown. Try 2: raw page -> PDF text or stripped HTML."""
    r = _call(url, markdown=True)
    if r.status_code == 200 and len(r.text.strip()) > 300:
        return 200, r.text, "markdown"
    r = _call(url, markdown=False)
    if r.status_code != 200:
        return r.status_code, r.text, "raw"
    if r.content[:4] == b"%PDF":
        reader = PdfReader(io.BytesIO(r.content))
        return 200, "\n".join((pg.extract_text() or "") for pg in reader.pages), "pdf"
    t = _Text(); t.feed(r.text)
    text = re.sub(r"\n\s*\n+", "\n\n", "".join(t.out))
    return 200, text, "html-stripped"


def main():
    only = set(sys.argv[1:])
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    targets = [r for r in rows if not r["text_file"]]          # link-only = no text supplied
    if only:
        targets = [r for r in targets if r["doc_id"] in only]

    new_log = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as lf:
        log = csv.writer(lf)
        if new_log:
            log.writerow(["doc_id", "jurisdictions", "source_type", "url",
                          "retrieved_at", "http_status", "chars", "sha256", "result"])

        print(f"{len(targets)} link-only sources to check.\n")
        for r in targets:
            doc, url = r["doc_id"], r["url"]
            path = f"{OUT_DIR}/{doc}.txt"
            if os.path.exists(path):
                print(f"{doc}: already captured, skipping")
                continue

            retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            try:
                status, body, method = fetch(url)
            except Exception as e:
                status, body, method = "error", str(e), "-"

            ok = status == 200 and len(body.strip()) > 300
            if ok:
                text = (f"SOURCE: {url}\nRETRIEVED: {retrieved}\n"
                        f"CAPTURED_VIA: Bright Data Web Unlocker ({method}; single page, team capture)\n"
                        f"SOURCE_TYPE: {r['source_type']}\n\n{body.strip()}\n")
                open(path, "w", encoding="utf-8").write(text)
                sha = hashlib.sha256(text.encode()).hexdigest()
                print(f"{doc}: OK via {method} ({len(body):,} chars)  {url[:60]}")
                log.writerow([doc, r["jurisdictions"], r["source_type"], url,
                              retrieved, status, len(body), sha, "captured"])
            else:
                reason = re.sub(r"\s+", " ", str(body))[:120]
                print(f"{doc}: FAILED ({status})  {reason}")
                log.writerow([doc, r["jurisdictions"], r["source_type"], url,
                              retrieved, status, 0, "", f"failed: {reason}"])
            lf.flush()
            time.sleep(PAUSE_SECONDS)

    print(f"\nDone. Text files in {OUT_DIR}/, log in {LOG}")


if __name__ == "__main__":
    main()
