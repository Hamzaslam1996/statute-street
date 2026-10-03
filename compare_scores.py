"""
compare_scores.py - put several lookup_eval reports side by side.

Usage: python compare_scores.py "label=out/lookup_eval_a.md" "label2=out/lookup_eval_b.md" ...
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROWS = ["Exact result agreement", "Weighted score", "Missed 'applies'", "Expectations we did not report", "Our unknown rate"]


def metrics(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    out = {}
    for key in ROWS:
        m = re.search(r"^\| " + re.escape(key) + r"[^|]*\| ([^|]+) \|", text, re.M)
        out[key] = m.group(1).strip() if m else "?"
    m = re.search(r"unknown rate: (\S+ = [\d.]+%)", text)
    out["Whole-sample unknown rate"] = m.group(1) if m else "?"
    m = re.search(r"presumption \(`assumptions` non-empty\): (\d+)", text)
    out["Rows relying on a presumption"] = m.group(1) if m else "?"
    return out


def main() -> int:
    cols = [(a.split("=", 1)[0], a.split("=", 1)[1]) for a in sys.argv[1:]]
    ms = [(label, metrics(path)) for label, path in cols]
    keys = ROWS + ["Whole-sample unknown rate", "Rows relying on a presumption"]
    print("| Metric | " + " | ".join(l for l, _ in ms) + " |")
    print("|---|" + "---|" * len(ms))
    for k in keys:
        print(f"| {k} | " + " | ".join(m[k] for _, m in ms) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
