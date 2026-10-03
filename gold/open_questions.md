# Open questions for Hamza (contested points — not resolved unilaterally)

Each item is framed as a decision. "Scoring consequence" = what changes in the key if you choose each option. All affected rows carry `conflict_flag: true` in `rules/all.json`.

## Q1. Berkeley ch. 13.63 effective date (BERK-ALG-01) — organisers' open question — **DECIDED 2026-10-04: (a) 2026-01-01, conflict_flag kept**
- Evidence: Ord. 7956-NS added ch. 13.63 (adopted 2025-03-25, eff. 2025-04-24). Ord. 7974-NS (adopted 2025-07-08, eff. 2025-08-07) inserted "The provisions of this Chapter shall not take effect until March 1, 2026." Ord. 7992-NS (adopted 2025-12-02; berkeley.municipal.codes: effective **2026-01-01**) re-enacted the chapter; the corpus text (D001) has no delayed-effect clause. Morgan Lewis (Aug 2026): "effective January 2026".
- Options: (a) **2026-01-01** [key as drafted]; (b) 2026-03-01 (organisers' "ordinance text" date); (c) record `2026-01` month-precision.
- Scoring consequence: as-of tests between 2026-01-01 and 2026-02-28 flip between applies / not_yet_effective. No T-test depends on it; the judges' key may use either date.

## Q2. LA RSO new-formula effective date (LA-RENT-01) — organisers' open question
- Evidence: City Clerk CF 23-1134: Ord. 188795 adopted 2025-12-12, Mayor 2025-12-24, published 2025-12-26, "Ordinance effective date: February 2, 2026"; LAHD pages: "Effective February 2, 2026". AAGLA: "effective January 24, 2026".
- Options: (a) **2026-02-02** [key as drafted]; (b) 2026-01-24.
- Scoring consequence: only affects as-of queries in late Jan 2026. Separate point: should `effective_date` for LA-RENT-01 be the formula-ordinance date at all, or null (RSO dates from 1979)?

## Q3. NJ FAIR Act preemption of Jersey City § 218-12 and Hoboken ch. 158 (NJ-ALG-01, JC-ALG-01, HOB-ALG-01) — organisers' open question
- Key as drafted: local bans **apply** now; `conflict_flag=true` on NJ-ALG-01 for JC/Hoboken addresses (T3) and on both local rules; no preemption conclusion.
- Decision: after 2027-07-01 should the local rules be recorded as `superseded`/preempted? (Only matters for as-of ≥ 2027-07-01 queries.)

## Q4. CA screening-fee cap dollar figure (CA-FEE-01) — organisers' open question
- Key as drafted: `key_value` = statutory formula ($30 base, CPI-adjusted from 1998-01-01), `conflict_flag=true`; Berkeley Rent Board publishes $68.96 for 2026 (official-agency, local computation).
- Options: (a) keep formula only [drafted]; (b) add "$68.96 (2026, per Berkeley Rent Board)" as an illustrative figure.

## Q5. Notice-of-rights ordinances recorded as just_cause_eviction rules (BOS-JUST-01 Boston HSNA; CAM-JUST-01 Cambridge ch. 8.71) — **DECIDED 2026-10-04: (a) keep as notice-only just_cause_eviction rules, conflict_flag kept**
- These impose notice duties on termination, not just cause. Drafted as **rules with conflict_flag** because the organisers put both documents in the corpus (likely extracted by the judges).
- Options: (a) keep as rules [drafted]; (b) convert to negative findings BOS-JUST-00 / CAM-JUST-00 ("no just-cause rule at city level"); (c) keep rule but change requirement text.
- Scoring consequence: 2 rule rows ↔ 2 negative findings; every Boston/Cambridge address loses/gains one `applies` entry.

## Q6. Berkeley BMC 13.78 screening-fee disclosure duty (BERK-FEE-01)
- A disclosure/renewal-fee rule, not a cap. Options: (a) keep as rule [drafted, conflict_flag]; (b) negative finding BERK-FEE-00 with the state cap governing.

## Q7. Boston Fair Chance Tenant Selection Policy (BOS-SCRN-01) — **DECIDED 2026-10-04 (L088): BOS-SCRN-01 = Fair Housing Commission regs; Fair Chance policy added as BOS-SCRN-02 (city-funded only, conflict_flag, confidence 0.5)**
- A 2017 DND funding-conditioned **policy**, not legislation; coverage (DND funding / IDP units) is not in the data → all Boston addresses `unknown`.
- Options: (a) keep as rule with coverage condition [drafted]; (b) negative finding BOS-SCRN-00 (state c.151B governs); (c) keep but set status to n/a-policy.

## Q8. Deposit-interest ordinances under security_deposits (LA-DEP-01, SF-DEP-01, BERK-DEP-01)
- Interest-payment duties rather than caps. Options: (a) keep [drafted]; (b) negative findings (state cap governs). Judges' category description ("security_deposits") is broad enough for (a).

## Q9. Two LA just-cause rows (LA-JUST-01 JCO; LA-JUST-02 RSO § 151.09)
- Options: (a) keep two rows (disjoint coverage) [drafted]; (b) merge into one LA just-cause rule. Affects count-based matching against a judges' key that probably has one LA just-cause row.

## Q10. Cambridge algorithmic pricing (CAM-ALG-00)
- June 2026 policy order asks the City Manager to draft options; no ordinance text. Drafted as a **negative finding** with conflict_flag. Option: record `CAM-ALG-P1` as `pending` instead.

## Q11. Boston H.3744 status (BOS-RENT-P1)
- Drafted `failed` (study order 2024-09-09 ended the 193rd-session petition). Option: `pending` if a refiled 194th-session petition exists (not checked).

## Q12. San Diego source-of-income effective date (SD-SCRN-01) — **DECIDED 2026-10-04 (L033): 2019-08-01, conflict_flag, confidence ≤ 0.7**
- Code history: O-20986 N.S. effective **2018-10-18** [drafted]; SDAR reported an operative date of 2019-08-01. No quoted_span (official Division 8 text not captured; gocodebook returned HTTP 500).

## Q13. Santa Ana algorithmic ordinance (SA-ALG-01) — secondary sources only — **DECIDED 2026-10-04 (L042): effective_date null; note news reports April 2026**
- Status `in_force` rests on PublicCEO / Voice of OC / OCBJ / Morgan Lewis (NS-3090, "effective April 2, 2026"); official text not reachable (Laserfiche cookie wall). `effective_date` left null per the two-source rule. Decision: accept secondary-only status, or downgrade to `pending`/exclude until the ordinance is retrieved. Extraction-only (no Santa Ana addresses).

## Q14. Jersey City § 218-12 details (JC-ALG-01)
- Ord. 25-057 adopted 2025-05-21 (news/press release); effective month 2025-06 (Morgan Lewis); official PDF blocked by robots.txt → no quoted_span. Decision: fetch the civicweb PDF manually and add the span.

## Q15. Hoboken ch. 158 B-750 disclosure duty for >10% increases — **DECIDED 2026-10-04 (L095): added HOB-RENT-02 with conflict_flag**
- Not recorded as a rent_increase_limits rule (it is a disclosure duty, not a cap). Option: add HOB-RENT-02 with conflict_flag.

## Q16. Unit counts inferred from use_description
- For Berkeley (Alameda use code "5+ units") and Boston ("APT 7-30 UNITS") the address key uses the description to defeat small-landlord exceptions (e.g. CA-DEP-01 → applies at A0005). Decision: allow this inference (drafted, marked) or treat units as strictly missing (→ unknown).

## Q17. Long-standing statutes: `effective_date` null vs original enactment date — **DECIDED 2026-10-04 (L046): null unless the source text states an effective date**
- Drafted null for NJ 2A:18-61.1, NJ 46:8-21.2, MA c.186 § 15B, MA c.151B § 4, SF 37.3/37.9, Berkeley 13.76 etc., following the organisers' sample record. Option: fill original enactment years from session laws (would need primary verification).
