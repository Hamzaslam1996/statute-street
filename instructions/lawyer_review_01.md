# Lawyer review — batch 1 (rows 1–3), verified by Hamza 2026-10-04

Files are in navigator/sources/manual/ (PDF + pdftotext .txt with SOURCE/RETRIEVED headers). Register each in sources/source_register.csv (source_type as stated), set verifier "Hamza" on the rows below, log every change in adjudication_log.csv, and regenerate affected seed20/seed60 entries. Do not touch git (Claude Code owns git).

## Row 1 — BOS-SCRN-02 (Boston Fair Chance Tenant Selection Policy)
Primary: BOS-SCRN-02_boston_fair_chance_policy_2017.pdf/.txt (DND, 3 pp., footer "February 2017"). Secondary: BOS-SCRN-02_secondary_BBJ_2023.pdf (Boston Bar Journal, 31 Aug 2023, fn. 23).
- citation: "Boston Fair Chance Tenant Selection Policy (Department of Neighborhood Development, February 2017)". It is a city POLICY adopted by agreement, not a codified ordinance. Keep level: city.
- coverage: housing providers receiving DND funding and/or land, or with income-restricted units created under the BPDA Inclusionary Development Policy. Per BBJ 2023, applies to all units in such a development incl. market-rate. Funding status is not in the address data -> Module B result "unknown".
- key_value: "No blanket denial for arrests/convictions; may not consider arrests without conviction, sealed/expunged/relieved convictions, juvenile records, or convictions more than 5 years old (case-by-case review required)".
- quoted_span (verbatim from the .txt): "Housing providers receiving Department of Neighborhood Development (DND) funding and/or land, or that have income restricted units created under the Boston Planning and Development Agency (BPDA) Inclusionary Development Policy will not impose a blanket policy that denies housing to anyone with arrests and or convictions."  (verify substring after whitespace normalisation; the .txt wraps lines)
- effective_date: null; notes "Policy document dated February 2017; no effective date stated". status in_force. conflict_flag true (policy vs ordinance; scope depends on funding). confidence 0.7. quote_verified true.

## Row 2 — MA-SCRN-02 (CORI in housing)
Primary: MA-SCRN-02_803_CMR_5.pdf/.txt (803 CMR 5.00, pages dated 6/11/21). Statute mirror: MA-SCRN-02_MGL_c6_s172_findlaw.pdf/.txt (secondary mirror; official page is malegislature.gov c.6 § 172 — capture it as a single page if reachable).
- citation: "803 CMR 5.00 (CORI – Housing), esp. 5.04, 5.10; M.G.L. c.6, § 172(a)(3)".
- key_value: "CORI may be requested only as the final step of the application; before asking about criminal history or making an adverse decision the landlord must give the applicant a copy of the CORI and disclose its source; look-back limited to felonies 10 years / misdemeanours 5 years after disposition (c.6 § 172(a)(3))".
- quoted_span (verbatim, 803 CMR 5.10(1)): "Each landlord, property management company, real estate agent, or public housing authority shall provide a copy of a housing applicant's CORI or other criminal history information, and shall disclose the source of the information, to him or her: (a) before asking the applicant any questions about the criminal history; and (b) before making an adverse housing decision based on the housing applicant's CORI or other criminal history information."
- coverage: landlords, property managers, real estate agents, PHAs that request CORI (803 CMR 5.01(2)).
- effective_date: null (regulation compiled 6/11/21; no effective date stated in the captured pages). status in_force. confidence 0.8. quote_verified true.

## Row 3 — SA-ALG-01 (Santa Ana Ord. NS-3090) — PARTIAL, still needs an official source
Hamza's notes: adopted 2026-03-03; effective 2026-04-02 (30 days after second reading); uncodified ordinance; prohibits landlords using an algorithmic device to set rents/occupancy and prohibits selling/licensing such software using nonpublic competitor data. These details are NOT yet backed by an official document in our files.
- Keep status in_force, effective_date "2026-04" (month, per adoption-month rule) ONLY if Hamza supplies the official ordinance/agenda PDF or URL; until then leave effective_date null, confidence 0.5, note the claimed dates as "reported, unverified".
- Record citation as "Santa Ana Ordinance No. NS-3090 (uncodified)" pending verification.

## Not used
Massachusetts_Employment_Screening_Laws_for_Employers_2026.pdf concerns employment screening, not housing — out of scope; do not register.
