# Lawyer review — batch 2 (rows 3, 4, 5), verified by Hamza 2026-10-04

First capture these official pages as single pages via Bright Data (same method as capture_links.py; new ids D088+ in corpus_supplementary with SOURCE/RETRIEVED headers; register in source_register.csv):
- D088 https://santa-ana.gov/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/  (official city news)
- D089 https://santa-ana.gov/rent-stabilization-newsletter-march-2026/  (official city newsletter)
- D090 https://www.boston.gov/sites/default/files/file/2021/03/Housing%20Stability%20Notification%20Act.pdf  (official ordinance text, PDF -> text)
- D091 https://berkeley.municipal.codes/BMC/13.78.016 and https://berkeley.municipal.codes/BMC/13.78.010 (code publisher)
If a fetch fails, say so; Hamza will save the page manually to sources/manual/.

## Row 3 — SA-ALG-01
- citation: "Santa Ana Ordinance No. NS-3090 (uncodified; number per challenge brief and OCBJ, not yet seen on an official page)"
- key_value: "Ban on sale, licensing, provision and use of algorithmic rent-setting software that uses nonpublic competitor data; tenant civil action, up to $1,000 per violation plus attorney's fees"
- exemptions: "Software relying solely on publicly available data, aggregate historical data, or tools used to comply with affordable-housing programme requirements"
- quoted_span: from D088, the sentence containing "prohibits the sale, licensing, provision and use of certain algorithmic rent-setting software for residential rental properties" (verify substring after capture)
- adoption: "Approved on March 3, 2026" (D088/D089; news page says this approval was for a second reading and final vote, so final adoption may be later in March). effective_date: null. notes: "Hamza: effective date reported as 2026-04-02 (30 days after adoption) — unverified; no official effective date found." status in_force (adopted > 60 days before 2026-10-01). conflict_flag true. confidence 0.6. verifier Hamza.

## Row 4 — BERK-FEE-01
- citation: "Berkeley Mun. Code §§ 13.78.010 (fee-cap disclosure duty), 13.78.016 (ban on non-refundable renewal/roommate fees) (Ord. 7697-NS § 1, 2020)"
- key_value: "No separate local fee cap: landlord must give a written Tenant Screening Fee Rights Statement and disclose the current Cal. Civ. Code § 1950.6(b) cap; non-refundable fees to existing tenants for renewal or adding/replacing a roommate are unlawful"
- quoted_span (verbatim, § 13.78.016): "It is unlawful for an owner of residential rental property or the owner's agent to charge a non-refundable fee to any existing tenant for the purpose of renewing a tenancy, in whole or in part, including any fee associated with the departure of a roommate or to request to add or replace a roommate in a pre-existing household."
- effective_date: "2020" (year only; Ord. 7697-NS). status in_force. confidence 0.85. verifier Hamza.

## Row 5 — BOS-JUST-01 (citation correction)
- citation: "Boston Code of Ordinances ch. X, § 10-11 (Housing Stability Notification Act), Ord. 2020 (Docket filed 2020-10-21)" — NOT ch. 9 § 9-20. Fix in all.json, dev/test, seed20/seed60 and the review pack.
- key_value unchanged: "[notice-only] With any notice to quit or notice of lease non-renewal, landlord must serve a copy on the Office of Housing Stability and give the tenant a notice of basic housing rights and resources; no just-cause requirement".
- quoted_span: from D090, the operative sentence requiring service of the notice on the Office of Housing Stability and the notice of basic housing rights (verify after capture).
- effective_date: 2020-11-06 (city FAQ D014); notes: "Ordinance text: 'shall become effective immediately'." status in_force. conflict_flag stays true (category judgement). confidence 0.8. verifier Hamza.
- Also fix the LAWYER_REVIEW link for this row to the ordinance PDF above and to https://codelibrary.amlegal.com/codes/boston/latest/boston_ma/0-0-0-7149.

Log all three in adjudication_log.csv (decided_by Hamza). No git.
