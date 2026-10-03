# Lawyer review — batch 4 (rows 9, 11, 12, 13, 14, 15), verified by Hamza 2026-10-04
Files in navigator/sources/manual/. Register, set verifier Hamza, log in adjudication_log.csv, regenerate seed20/seed60. No git.

## Row 11 — MA-RENT-P1 (ballot question) — CONFIRMED from the slip opinion
Source: MA-RENT-P1_Cella_v_AG_SJC-13893.pdf/.txt (official SJC slip opinion).
- citation: "Cella v. Attorney General, SJC-13893 (Mass. June 23, 2026) (Initiative Petition 25-21, 'An Initiative Petition to Protect Tenants by Limiting Rent Increases')"
- key_value: "NO RULE: petition barred from the November 2026 ballot (art. 48 excluded matter — relates to religion); no statewide rent cap exists; M.G.L. c.40P continues to prohibit rent control"
- quoted_span (verbatim, p. 2): "Accordingly, art. 48 bars placement of the petition on the November 2026 Statewide election ballot."
- Also add to MA-RENT-00 (c.40P negative finding) a supporting quote from the opinion p. 3: General Laws c. 40P, § 2, "broadly prohibits any regulatory scheme based upon or implementing rent control." (secondary restatement of the statute; keep D048 as the primary source).
- status failed; decided 2026-06-23; argued 2026-05-06; confidence 0.95; verifier Hamza.

## Row 15 — MA-FEE-02 (broker fee) — CONFIRMED
Source: MA-FEE-02_c112_87DDD-half_masslaw.pdf/.txt (mass.gov Trial Court Law Libraries text; official D057 remains primary).
- effective_date 2025-08-01 confirmed by the stated line "Amended by St. 2025, c. 9, § 43, effective August 1, 2025" (stated date -> satisfies rulings_04 §2B). quoted_span: use the operative sentence from D057/this file on who pays the broker fee (verify substring). confidence 0.9. verifier Hamza.

## Row 13 — BERK-RENT-01 (Berkeley AGA) — CONFIRMED
Source: BERK-RENT-01_AGA_page.pdf/.txt (official Rent Board page).
- key_value: "AGA for 2026 is 1.0% (65% of Bay Area CPI July–June, capped at 5% under Measure BB); applies to units fully covered by the Rent Ordinance; no increase in the year the tenancy began plus one further calendar year"
- quoted_span (verbatim): "The AGA for 2026 is 1.0%"  (20+ chars after normalisation? It is 24 chars — OK) — better: "On January 1, the rent ceilings for most units fully covered by the Rent Ordinance increase by the AGA, which allows landlords to raise rents (with proper notice) up to the new rent ceiling."
- effective_date: 2026-01-01 (stated: "On January 1, the rent ceilings ... increase by the AGA"). This is the current key-value date (same treatment as SF-RENT-01). confidence 0.9. verifier Hamza.
- notice: 30-day written notice for increases ≤10%, 90-day for >10% (state law; put in notes).

## Row 12 — CA-SCRN-01 (Gov. Code § 12955 source of income) — CONFIRMED with a date note
Source: CA-SCRN-01_Gov_12955_justia.pdf/.txt (mirror; official corpus copy D027 is primary).
- key_value: "'Source of income' includes federal, state or local housing subsidies incl. Section 8 vouchers; discrimination based on source of income is unlawful"
- quoted_span (verbatim § 12955(p)(1), from D027 if present, else this file): the sentence beginning "For the purposes of this section, “source of income” means lawful, verifiable" ... through "(42 U.S.C. Sec. 1437f)." (verify substring)
- effective_date: keep 2020-01-01 for the voucher protection (SB 329, Stats. 2019, ch. 600). notes: "History note in current text states only the latest amendment: 'Amended by Stats. 2023, Ch. 776, Sec. 1. (SB 267) Effective January 1, 2024.' SB 329's 2020-01-01 date is the standard 1 January effective date for a non-urgency statute chaptered 2019-10-08 (Cal. Const. art. IV, § 8(c)); not stated in the saved text." conflict_flag false; confidence 0.85. The extractor will likely return 2024-01-01 or null — accept that mismatch.

## Row 9 — NJ-ALG-01 (FAIR Act) — corroborated
Secondary: NJ-ALG-01_secondary_NJ_State_Policy_Lab_2026-07-27.pdf (NJ State Policy Lab, 27 Jul 2026): signed 20 Jul 2026 as P.L.2026, c.43; effective 1 Jul 2027. Primary D069 unchanged. Add as supporting source; no field changes; verifier Hamza.

## Row 14 — LA-JUST-02 (LAMC § 151.09) — PRIMARY TEXT NOW IN HAND
Source: LA-JUST-02_LAMC_ch15_art1_151.txt (full LAMC ch. XV art. 1 text, incl. § 151.09 Evictions, from American Legal).
- citation: "L.A. Mun. Code § 151.09 (Evictions)"; key_value: "Landlord may not evict from an RSO unit except on the legal grounds listed in § 151.09.A (e.g. non-payment, lease violation, nuisance, owner/family occupancy, demolition/withdrawal); relocation assistance due for no-fault evictions (§ 151.09.G)". quoted_span: the lead-in sentence of § 151.09.A (verify substring in the file). effective_date null (ordinance history notes give amendment dates; e.g. "Added by Ord. No. 165,251, Eff. 11/20/89" for A.9 — record in notes, not as the rule's date). confidence 0.85. verifier Hamza.
- This file also contains § 151.06 (rent increases) and § 151.04/151.05 (coverage); use it to tighten LA-RENT-01's quoted_span and coverage (COO on or before 1978-10-01) if the official text is clearer than D041.

## Not used
- Source_of_Income_Protection_-_San_Rafael.pdf: another city's page (secondary, out of scope).
- https://blog.nextgencoastal.com/dba2: blog, not a legal source; do not register.

For Claude Code (Module A): add these .txt files to the extractor inputs (sources/manual/*.txt) and re-extract only them; LA-JUST-02 and LA-RENT-01 should gain official quotes.

## Row 3 — SA-ALG-01 (Santa Ana) — ADDENDUM (Hamza, 2026-10-04 03:31)
Supersedes the effective_date instruction in lawyer_review_02.md.
- effective_date: "2026-04" (month precision). Basis note: "Adopted 2026-03-03 per santa-ana.gov (D088/D089); Santa Ana ordinances take effect 30 days after adoption (City Charter; cf. Cal. Gov. Code § 36937) → on or about 2026-04-02; the challenge brief lists 'Santa Ana Ord. NS-3090 (Apr 2026)'. Computed from the adoption date, not stated in a saved document." adoption_date 2026-03-03.
- status in_force; conflict_flag true (ordinance number and exact effective date not yet seen on an official page); confidence 0.7; verifier Hamza.
- If Hamza supplies an official agenda/ordinance PDF showing "NS-3090", raise confidence to 0.9 and clear the conflict note about the number.
