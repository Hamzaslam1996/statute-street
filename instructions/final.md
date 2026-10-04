# Final: lock, score once, document, package (Hamza, 4 Oct)

No API calls. Decision from the stress test: KEEP THE CURRENT POLICY (best worst-case and best mean exact agreement across the six alternative keys). Do not change engine policy from here on.

## 1. Lock
Tag the current navigator HEAD as `v1.0-submission-candidate` (lightweight tag, push it).

## 2. Test split, ONE run
Run Module A eval against gold/rules/test.json exactly once (eval.py --gold gold/rules/test.json --out out/eval_report_test.md). This is the first and only time test.json is read. Do not change anything in response to the result. Record in the README that it was a single run at the tagged commit.

## 3. README final pass (navigator/README.md), plain English, no dashes as punctuation
Order: one-line summary and disclaimer; What it does (Modules A, B, C); Quick start (cache-only reproduction commands, as in out/stress/repro.md); Pipeline diagram in text; Results table (dev split, test split single run, seed60, seed20, holdout20 single blind run, T1 to T5, unknown rate, presumption count) with the honesty sentence; Stress test summary (the decision table, one paragraph on why the current policy was kept); Exemptions and presumptions; Evidence basis (organiser ruling, counts); Known open questions; Determinations as data (lookups.json as a static API a pricing engine can query before suggesting a price); Limits (what we do not do: no amounts computed, no case decisions, no owner data, NJ unit counts absent); Audit trail; Responsible use; Repository map; Credits (Hamza Aslam). Link the UI repo and live demo URL as placeholders `<UI_REPO_URL>` and `<LIVE_DEMO_URL>`.

## 4. One-page method note
Write submission/METHOD_NOTE.md: one page, about 450 words, headings: Problem; Approach (extraction with verified quotes, deterministic engine, change tracking); Validation (the numbers, single runs named, honesty sentence); Responsible design (unknown names the missing fact, conflicts flagged, not legal advice, public data only, evidence basis); Limits. Also render it to submission/METHOD_NOTE.pdf if a converter is available locally (pandoc or python markdown + weasyprint/reportlab); if none, say so.

## 5. Submission package
Create submission/ with exact copies of out/rules.json, out/lookups.json, out/changes.json (the filtered submission files), METHOD_NOTE.md/.pdf, and a SHA256SUMS file. Validate again with the format check. Commit by name, push, push the tag, stop and report: test split result, file hashes, README section list.
