# Scale: real addresses beyond the sample, plus measured cost (Hamza, 4 Oct)

Run LAST, after rulings_12, integration.md and agent_mcp.md. Never touch out/*.json used for submission, submission/, or the UI repo. Everything goes to scale/ and out/scale/. No Claude API calls.

## 1. Real addresses from official open data (cap 6,000)
Use each city's official open data portal API (Socrata or ArcGIS REST, documented public endpoints, normal rate limits, no scraping, no Bright Data):
- San Francisco: DataSF assessor historical secured property tax rolls (latest year): address, year built, number of units, use code. Up to 2,000 residential rows with units >= 2.
- Boston: Analyze Boston property assessment (latest fiscal year): address, year built, units (if present), land use. Up to 2,000 residential rows.
- Cambridge: Cambridge open data property database / assessor: address, year built, units, use. Up to 2,000 residential rows.
If an endpoint is unavailable or the terms do not allow reuse, skip that city and say so. Do not substitute other sources.
PRIVACY: drop every owner name, mailing address and any person field at download time; never write them to disk. Keep only address, ZIP, year built, units, use description, and the portal's record id and URL for provenance.
Record per city: endpoint URL, dataset name, retrieved timestamp, row count, sha256 of the saved CSV (scale/data/<city>.csv), licence line from the portal.

## 2. Same pipeline, unchanged
Geocode with the Census batch geocoder (same resolve.py code path, separate output), then run the unchanged engine at as_of 2026-10-01 and 2027-07-02. Write out/scale/lookups_<city>.json and a summary: addresses, legal city match rate (geocoded city vs portal city), determinations, result distribution (applies / applies unless / unknown / superseded / not yet effective / pending), top 5 missing facts, runtime.
Sanity checks (report pass/fail, do not tune): no Boston or Cambridge address gets a rent cap; every SF row built before 1979 with 2+ units gets SF rent control applies; cutoff year 1979 gives unknown; every row cites an existing rule.

## 3. Throughput benchmark
Time the engine on 10,000 and 100,000 determinations (the scale addresses replicated across as-of dates); report addresses per second on this laptop.

## 4. Cost of adding law
From out/extract_log.csv and the date/coverage/translation logs: average model cost and wall time per document, per rule, and the share of rules that needed a human ruling (count rulings in instructions/ and gold/adjudication_log.csv decided_by Hamza). Express as "adding one jurisdiction of about N documents costs about $X of model time plus Y lawyer review items".

## 5. Report
out/scale/REPORT.md and a README section "Scalability" with: real addresses run, match rate, runtime, throughput, cost per document, human review share, and three plain sentences on the architecture: rules are compiled once per jurisdiction; determinations are a deterministic join of address facts and rules, so more addresses cost no model calls; refresh is event driven (when the change register posts a new effective date), not per query. Commit scale/ (code and provenance, CSVs only if under 5 MB each), out/scale/, README by name; push; stop.
