# Module C — change tracking (Hamza, 4 Oct)

Budget: NO Claude API calls in this step. Module C must be deterministic: engine runs at different --as-of dates plus set arithmetic. If you believe a model call is unavoidable, stop and ask.
Never read gold/rules/test.json.

## 0. Two quick checks first
1. lookup_eval mapping: earlier notes mapped BOTH MA-SCRN-01 (c.151B) and MA-SCRN-02 (c.6 §172 CORI) to r-0040. Now that D094 is extracted, confirm each gold id maps to its own rule; fix the mapper if needed and re-score seed60/seed20 (report only if numbers move).
2. MA-SCRN-01 / § 4(10): keep our result (`applies`). Basis for the README: the owner-occupied two-family exemption is written into c.151B § 4(7) and § 4(11)(3) only (official text, D049); § 4(10) (public-assistance / rental-assistance discrimination) contains no such exemption. The gold session will adjudicate its side.

## 1. changes.py → out/changes.json
Format (organisers' README §5): `{test_id: {affected_address_ids: [...], conflict_flag_address_ids: [...], notes}}`, evaluated over all 500 addresses. Read tests from the starter pack `dev/change_tests.json`; map its rule_ids to our team_rule_ids (log the mapping).
"Affected" = addresses where the test's rule(s) are reported for that address in at least one of the test's dates (any result other than "rule left out"), i.e. the addresses whose answer the change touches.

- **T1 (CA-ALG-01, AB 325 / SB 763):** run engine at 2025-12-31 and 2026-01-02. Expect not_yet_effective → applies for every CA address (LA, SF, SD, Berkeley). affected = all CA addresses. notes: effective 2026-01-01, cite.
- **T2 (HOB-ALG-01, JC-ALG-01) at 2026-10-01:** boundary test. affected = Hoboken addresses ∪ Jersey City addresses; notes must state per-rule sets (HOB rule → Hoboken only; JC rule → Jersey City only; Newark none). Assert in a unit test that no Newark address and no cross-city address gets either rule. Geocoded legal city decides, never the mailing city.
- **T3 (NJ-ALG-01, FAIR Act):** run at 2026-10-01 and 2027-07-02. Expect not_yet_effective → applies for every NJ address. affected = all NJ addresses. conflict_flag_address_ids = Jersey City + Hoboken addresses. notes: enacted 2026-07-20, effective 2027-07-01; possible preemption of the local ordinances → human review, we do not decide preemption.
  Also in the default lookups.json (2026-10-01): set `conflict_flag: true` on JC-ALG-01 and HOB-ALG-01 rows with explanation "Possible preemption by the NJ FAIR Act from 2027-07-01 — flagged for human review."
- **T4 (MA-ALG-P1 S.2983, MA-ALG-P2 H.5222) at 2026-10-01:** result `pending` for every Boston and Cambridge address. affected = all MA addresses ("would be affected if enacted"). notes: pending bills, not law; last status + source.
- **T5 (MA-RENT-P1, IP 25-21) at 2026-10-01:** affected = [] (empty). notes: ballot question struck 2026-06-23 (Cella v. Attorney General, SJC-13893); recorded as failed. Add a hard assertion/test: no Boston or Cambridge address has any rent-cap rule with result applies/not_yet_effective/pending.

## 2. Diff view (for the UI and the videos)
`python changes.py --diff --before DATE --after DATE` → out/diff_<before>_<after>.json: per address, per rule, old result → new result. Generate for T1 and T3 dates.

## 3. Score against our independent change key
Compare out/changes.json with gold/changes/T1-T5.json (affected sets, conflict sets, expected statuses). Table: per test — expected count, ours, missing, extra, exact match yes/no. List every mismatching address id with both reasons. Do not edit the gold file.

## 4. Known open questions (organisers' bonus, README §9)
Write out/open_questions.json and a README section, each item with both sources and dates, and how our system answers (and that it flags rather than resolves):
- Berkeley ch. 13.63 algorithmic ban: 2026-03-01 (ordinance text) vs January 2026 (Aug 2026 law-firm alert).
- NJ FAIR Act possible preemption of JC / Hoboken ordinances.
- LA RSO new formula: 2026-02-02 (LAHD) vs 2026-01-24 (landlord association).
- CA screening-fee cap: no single official 2026 dollar figure.

## 5. Tests, commit, stop
Unit tests for T1–T5 behaviour (above assertions). Run the whole test suite. README: "Module C" section with the run commands. Commit and push. Report the §3 table, then stop and wait.

## 6. Gold v0.4.3 + blind holdout (do in this order)
1. BEFORE any scoring in §3: commit and push the gold v0.4.3 files on their own, message "gold v0.4.3 (MA-SCRN-01 adjudication; holdout20 frozen)": gold/rules/{all,dev,test}.json, gold/adjudication_log.csv, gold/README.md, gold/build_addresses.py, gold/addresses/{seed20,seed60,holdout20}.json, gold/addresses/holdout20.sha256. Stage test.json without opening it.
2. Verify holdout20.json against holdout20.sha256 and print the result.
3. After Module C is done and committed, score holdout20 ONCE: `python lookup_eval.py --gold gold/addresses/holdout20.json --out out/lookup_eval_holdout20.md`. Do NOT change any code or coverage in response to holdout results. Report the table and every disagreement verbatim; I will rule. Record in the README that this was a single blind run.
4. Re-score seed60 and seed20 after the v0.4.3 key (expect the 4 MA-SCRN-01 rows to agree now).
