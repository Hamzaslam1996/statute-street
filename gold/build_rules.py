#!/usr/bin/env python3
"""Builds the independent gold rule key for Statute Street.
Every quoted_span is verified by exact substring match against the saved source text
(organisers' corpus copy or team supplementary capture) before it is written."""
import json, os, re, hashlib, csv, sys
from collections import OrderedDict

ROOT = '/home/claude/ss'
OUT = '/mnt/user-data/outputs/navigator'
CORPUS = f'{ROOT}/corpus'; SUPP = f'{ROOT}/supp'
QDATE = '2026-10-01'
CHK = '2026-10-03T20:20Z'   # web verification window for this session (approx., UTC)
MAN = {r['doc_id']: r for r in csv.DictReader(open(f'{ROOT}/corpus_manifest.csv'))}

def text(doc):
    for fo in (CORPUS, SUPP):
        p = f'{fo}/{doc}.txt'
        if os.path.exists(p):
            return open(p, encoding='utf-8').read(), ('corpus' if fo == CORPUS else 'supp')
    return None, None

def cov(coo=None, ybmax=None, minu=None, maxu=None, owner=None, ten=None, other=None):
    return OrderedDict(coo_cutoff=coo, year_built_max=ybmax, min_units=minu, max_units=maxu,
                       owner_type=owner, tenancy_months=ten, other=other)

def inter(overrides=(), yields_to=(), note=None):
    return OrderedDict(overrides=list(overrides), yields_to=list(yields_to), note=note)

def va(*pairs):
    return [OrderedDict(url=u, checked_at_utc=c, result=r) for (u, c, r) in pairs]

RULES = []
def R(gold_id, jurisdiction, level, category, status, title, requirement, key_value, coverage,
      exemptions, effective_date, enacted_date, sunset_date, citation, source_ids, corpus_doc_ids,
      supplementary_doc_ids, quoted_span, span_doc, interaction, conflict_flag, conflict_note,
      negative_finding, negative_reason, confidence, verified_against, notes):
    RULES.append(OrderedDict(
        gold_id=gold_id, jurisdiction=jurisdiction, level=level, category=category, status=status,
        title=title, requirement=requirement, key_value=key_value, coverage=coverage, exemptions=exemptions,
        effective_date=effective_date, enacted_date=enacted_date, sunset_date=sunset_date, citation=citation,
        source_ids=source_ids, corpus_doc_ids=corpus_doc_ids, supplementary_doc_ids=supplementary_doc_ids,
        quoted_span=quoted_span, _span_doc=span_doc, quoted_span_in_corpus=False, interaction=interaction,
        conflict_flag=conflict_flag, conflict_note=conflict_note, negative_finding=negative_finding,
        negative_reason=negative_reason, confidence=confidence, verified_against=verified_against,
        verifier='AI-draft', notes=notes))

def NEG(gold_id, jurisdiction, level, category, reason, citation, source_ids, corpus_doc_ids, supp_ids,
        span, span_doc, confidence, verified_against, notes, conflict_flag=False, conflict_note=None):
    R(gold_id, jurisdiction, level, category, 'n/a', f'No {category} rule at {level} level',
      f'No {level}-level {category.replace("_"," ")} rule governs this jurisdiction as of {QDATE}; see negative_reason.',
      None, cov(), None, None, None, None, citation, source_ids, corpus_doc_ids, supp_ids, span, span_doc,
      inter(), conflict_flag, conflict_note, True, reason, confidence, verified_against, notes)

# ------------------------------------------------------------------ CALIFORNIA (state)
R('CA-RENT-01','CA','state','rent_increase_limits','in_force',
  'Tenant Protection Act rent cap (AB 1482) – Cal. Civ. Code § 1947.12',
  'Annual rent increases are capped at 5% plus the regional CPI change, or 10%, whichever is lower, measured against the lowest rent in the prior 12 months. Local rent control that is stricter supersedes this cap.',
  'lesser of 5% + CPI or 10% per 12 months',
  cov(other='Housing issued a certificate of occupancy more than 15 years before the increase (rolling); not deed-restricted affordable; not covered by stricter local rent control'),
  'Housing with a certificate of occupancy within the previous 15 years; deed-restricted affordable housing; dormitories; housing under stricter local rent control (Civ. Code § 1947.12(d)(3)); separately alienable single-family homes/condos not owned by a REIT, corporation or corporate-member LLC where notice given; owner-occupied duplexes',
  '2020-01-01', '2019-10-08', '2030-01-01', 'Cal. Civ. Code § 1947.12',
  ['S-CA-01'], ['D024'], ['D019'],
  'an owner of residential real property shall not, over the course of any 12-month period, increase the gross rental rate for a dwelling or a unit more than 5 percent plus the percentage change in the cost of living, or 10 percent, whichever is lower',
  'D024', inter(yields_to=['LA-RENT-01','SF-RENT-01','BERK-RENT-01','SA-RENT-01'], note='Civ. Code § 1947.12(d)(3): does not apply where local rent control restricts increases to less than this section; expected result at covered LA/SF/Berkeley/Santa Ana rent-controlled addresses is superseded'),
  False, None, False, None, 0.9,
  va(('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12', '2026-10-01T22:35Z', 'organisers corpus copy D024 (leginfo blocks scripted fetch; robots.txt disallowed WebFetch on 2026-10-03)'),
     ('https://law.justia.com/codes/california/code-civ/division-3/part-4/title-5/chapter-2/section-1947-12/', '2026-10-03T18:49Z', 'team supplementary capture D019 (secondary mirror) – text consistent')),
  'Original AB 1482 (Stats. 2019 ch. 597) effective 2020-01-01, applying to increases on/after 2019-03-15 (subd. (h)). Current text repealed/re-added by SB 567 (Stats. 2023 ch. 290) operative 2024-04-01; sunset 2030-01-01 (subd. (o)). 15-year COO exemption is rolling; year_built is not COO date, so expected address result where year_built within 15 years is unknown.')

R('CA-JUST-01','CA','state','just_cause_eviction','in_force',
  'Tenant Protection Act just cause for eviction – Cal. Civ. Code § 1946.2',
  'After a tenant has lawfully occupied a unit for 12 months, the owner may not end the tenancy without a stated at-fault or no-fault just cause; no-fault terminations require one month of relocation assistance or rent waiver.',
  'just cause required after 12 months of occupancy; 1 month relocation assistance for no-fault',
  cov(ten=12, other='Housing issued a certificate of occupancy more than 15 years ago; not subject to a more protective local just-cause ordinance'),
  'COO within previous 15 years; transient hotels; care facilities; dormitories; owner-shared units; owner-occupied SFR renting ≤2 units/bedrooms; owner-occupied duplex; separately alienable SFR/condo not owned by REIT/corporation/corporate LLC with notice; deed-restricted affordable housing; property subject to a local just-cause ordinance adopted on/before 2019-09-01 or a more protective later one (§ 1946.2(i))',
  '2020-01-01', '2019-10-08', '2030-01-01', 'Cal. Civ. Code § 1946.2',
  ['S-CA-02'], ['D023'], ['D018'],
  'after a tenant has continuously and lawfully occupied a residential real property for 12 months, the owner of the residential real property shall not terminate a tenancy without just cause, which shall be stated in the written notice to terminate tenancy',
  'D023', inter(yields_to=['LA-JUST-01','LA-JUST-02','SF-JUST-01','SD-JUST-01','BERK-JUST-01','SA-JUST-01'], note='§ 1946.2(i): property is not subject to both this section and a local just-cause ordinance; local ordinance applies where adopted on/before 2019-09-01 or more protective'),
  False, None, False, None, 0.9,
  va(('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1946.2', '2026-10-01T22:35Z', 'organisers corpus copy D023 (leginfo blocks scripted fetch)'),
     ('https://law.justia.com/codes/california/code-civ/division-3/part-4/title-5/chapter-2/section-1946-2/', '2026-10-03T18:49Z', 'team supplementary capture D018 – consistent')),
  'Current text amended by AB 1529 (Stats. 2025 ch. 203) effective 2026-01-01; operative 2024-04-01 per SB 567; sunset 2030-01-01. Tenancy length is not in the address data → result depends on tenancy facts; coverage by COO age is unknown from year_built.')

R('CA-DEP-01','CA','state','security_deposits','in_force',
  'Security deposit cap (AB 12) – Cal. Civ. Code § 1950.5(c)',
  'A landlord may not demand or receive a security deposit exceeding one month\'s rent (in addition to first month\'s rent). A small landlord who is a natural person (or all-natural-person LLC) owning no more than two rental properties with no more than four units in total may charge up to two months\' rent.',
  '1 month\'s rent (2 months for qualifying small landlords)',
  cov(other='All residential tenancies; 2-month exception only if landlord is a natural person/natural-person LLC owning ≤2 rental properties with ≤4 dwelling units total'),
  'Small-landlord two-month exception (Civ. Code § 1950.5(c)(5)); exception unavailable where prospective tenant is a service member; not applicable to security collected before 2024-07-01',
  '2024-07-01', '2023-10-11', None, 'Cal. Civ. Code § 1950.5(c)',
  ['S-CA-03'], ['D025'], ['D020'],
  'a landlord shall not demand or receive security, however denominated, in an amount or value in excess of an amount equal to one month’s rent, in addition to any rent for the first month paid on or before initial occupancy',
  'D025', inter(note='Local deposit-interest ordinances (LA, SF, Berkeley) add obligations but do not change the state cap; both apply'),
  False, None, False, None, 0.9,
  va(('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1950.5', '2026-10-01T22:35Z', 'organisers corpus copy D025'),
     ('https://rentboard.berkeleyca.gov/rights-responsibilities/security-deposits', '2026-10-01T22:35Z', 'official-agency corroboration D007: AB 12 one month from 2024-07-01')),
  'Owner-type condition (natural person, ≤2 properties, ≤4 units) cannot be resolved from the data → expected address result "unknown" unless units > 4 defeats the exception (then "applies" with the 1-month cap). Current text amended by AB 414 (Stats. 2025 ch. 340) eff. 2026-01-01.')

R('CA-FEE-01','CA','state','application_screening_fees','in_force',
  'Application screening fee cap – Cal. Civ. Code § 1950.6',
  'An application screening fee may not exceed the landlord\'s actual out-of-pocket screening costs and in no case more than $30 per applicant (1997 base), which may be adjusted annually for CPI since 1998-01-01; a receipt and refund of unused amounts are required.',
  '$30 (1997 base) adjusted annually by CPI from 1998-01-01; no single official 2026 dollar figure',
  cov(other='All residential rental applications'),
  'Fee may not be charged when no unit is available; reusable screening reports (§ 1950.1)',
  None, None, None, 'Cal. Civ. Code § 1950.6',
  ['S-CA-04'], ['D026'], ['D017'],
  'In no case shall the amount of the application screening fee charged by the landlord or their agent be greater than thirty dollars ($30) per applicant. The thirty dollar ($30) application screening fee may be adjusted annually by the landlord or their agent commensurate with an increase in the Consumer Price Index, beginning on January 1, 1998.',
  'D026', inter(overrides=[], yields_to=[], note='Berkeley BMC 13.78 adds disclosure duties; the state cap still applies in Berkeley'),
  True, 'Organisers\' README: the CA screening-fee cap has no single official 2026 dollar figure. Berkeley Rent Board publishes $68.96 for 2026 (D005); other calculators differ. Key value recorded as statutory formula, not a dollar figure.',
  False, None, 0.85,
  va(('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1950.6', '2026-10-01T22:35Z', 'organisers corpus copy D026'),
     ('https://rentboard.berkeleyca.gov/laws-regulations/city-berkeley-ordinances-affecting-rental-properties/tenant-screening-and', '2026-10-01T22:35Z', 'official-agency D005 corroborates cap and CPI adjustment')),
  'effective_date null: the $30 cap dates from 1997 legislation (CPI adjustment begins 1998-01-01 per statute); original enactment date not verified against a primary source in this session. Current text amended by AB 1170 (Stats. 2025 ch. 67) eff. 2026-01-01.')

R('CA-SCRN-01','CA','state','screening_restrictions','in_force',
  'FEHA source-of-income protection (incl. Section 8 vouchers) – Cal. Gov. Code § 12955',
  'Housing providers may not discriminate against applicants or tenants because of source of income, which includes federal, state or local housing subsidies such as Section 8 Housing Choice Vouchers paid to the landlord on the tenant\'s behalf.',
  'source of income (incl. Section 8 vouchers) is a protected characteristic',
  cov(other='All housing accommodations covered by FEHA'),
  None, '2020-01-01', '2019-10-08', None, 'Cal. Gov. Code § 12955(a), (p)',
  ['S-CA-05','S-CA-06'], ['D027','D016'], ['D021'],
  'federal, state, or local housing subsidies, including, but not limited to, federal housing assistance vouchers issued under Section 8 of the United States Housing Act of 1937 (42 U.S.C. Sec. 1437f)',
  'D027', inter(note='Local source-of-income ordinances (LA LAMC 45.65-45.69, San Diego SDMC 98.0801, Cambridge, etc.) operate alongside; both apply'),
  False, None, False, None, 0.8,
  va(('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=12955', '2026-10-01T22:35Z', 'organisers corpus copy D027'),
     ('https://calcivilrights.ca.gov/housing/', '2026-10-01T22:35Z', 'official-agency D016: "Refusing to rent to a tenant with a section 8 voucher" listed as unlawful')),
  'The voucher-inclusive definition of source of income was added by SB 329 (Stats. 2019 ch. 600), effective 2020-01-01; enactment date 2019-10-08 is from general knowledge of the chaptering date and was NOT verified against leginfo in this session (confidence reduced). Current text amended by SB 267 (Stats. 2023 ch. 776) eff. 2024-01-01. CRD regulations (2 CCR § 12264 et seq.) also restrict criminal-history screening; not separately recorded.')

R('CA-ALG-01','CA','state','algorithmic_rent_setting','in_force',
  'Common pricing algorithm prohibition (AB 325, Cartwright Act) – Cal. Bus. & Prof. Code § 16729',
  'It is unlawful to use or distribute a common pricing algorithm (software using competitor data to recommend or set prices) as part of a conspiracy to restrain trade, or to coerce another person to adopt a price it recommends. Applies to residential rent-setting software statewide.',
  'prohibition on use/distribution of common pricing algorithms in restraint of trade',
  cov(other='All persons (landlords and vendors) in California; not limited to housing'),
  'End consumers are not "persons" (§ 16729(d)(5))',
  '2026-01-01', '2025-10-06', None, 'Cal. Bus. & Prof. Code § 16729 (added by AB 325, Stats. 2025 ch. 338)',
  ['S-CA-07','S-CA-08'], ['D022'], ['D028'],
  'It shall be unlawful for a person to use or distribute a common pricing algorithm as part of a contract, combination in the form of a trust, or conspiracy to restrain trade or commerce in violation of this chapter.',
  'D022', inter(note='Local bans (SF 37.10C, San Diego 98.1103, Berkeley 13.63, Santa Ana) are additional; state law does not preempt them. Companion SB 763 (Stats. 2025) raised Cartwright Act penalties, also effective 2026-01-01.'),
  False, None, False, None, 0.85,
  va(('https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB325', '2026-10-01T22:35Z', 'organisers corpus copy D022: Chapter 338, approved by Governor 2025-10-06 (leginfo robots.txt disallowed WebFetch on 2026-10-03)'),
     ('https://www.clearygottlieb.com/news-and-insights/publication-listing/californias-antitrust-law-amendments-kick-in-targeting-algorithmic-pricing', '2026-10-03T18:50Z', 'team supplementary D028 (secondary): AB 325 and SB 763 "took effect on January 1, 2026"')),
  'Effective date 2026-01-01 follows from chaptering on 2025-10-06 in a regular session (Cal. Const. art. IV, § 8(c)(1): statutes enacted in regular session take effect January 1 next following a 90-day period); the bill text has no urgency clause. Fixed by change test T1: not_yet_effective as of 2025-12-31, applies as of 2026-01-02 for every CA address.')

# ------------------------------------------------------------------ NEW JERSEY (state)
NEG('NJ-RENT-00','NJ','state','rent_increase_limits',
    'New Jersey has no statewide rent cap; rent control is delegated to municipalities (Jersey City ch. 260, Hoboken ch. 155, Newark Title XIX). State law only bars "unconscionable" increases as an eviction defence (N.J.S.A. 2A:18-61.1(f)).',
    'N.J.S.A. 2A:18-61.1(f) (no statewide cap)', ['S-NJ-02'], [], ['D062'],
    'provided the increase in rent is not unconscionable and complies with any and all other laws or municipal ordinances governing rent increases', 'D062', 0.75,
    va(('https://law.justia.com/codes/new-jersey/title-2a/section-2a-18-61-1/', '2026-10-03T18:52Z', 'team supplementary D062 (secondary mirror of statute)')),
    'Negative finding; quoted span is illustrative only (statute lists unconscionable rent increase as a ground for removal, confirming absence of a cap). Local rent control at Jersey City/Hoboken/Newark is recorded at city level.')

R('NJ-JUST-01','NJ','state','just_cause_eviction','in_force',
  'Anti-Eviction Act – N.J.S.A. 2A:18-61.1',
  'A residential tenant may be removed only on one of the statutory good-cause grounds (e.g., non-payment, disorderly conduct, breach, owner occupancy of a building of three units or fewer); lease expiry alone is not a ground.',
  'statutory good cause required for removal',
  cov(other='All residential rental premises except owner-occupied buildings with not more than two rental units and transient hotel/guest-house occupancy'),
  'Owner-occupied premises with not more than two rental units; hotels/motels/guest houses rented to transients or seasonal tenants',
  None, '1974-06-25', None, 'N.J.S.A. 2A:18-61.1',
  ['S-NJ-02','S-NJ-05'], ['D067'], ['D062'],
  'other than (1) owner-occupied premises with not more than two rental units or a hotel, motel or other guest house or part thereof rented to a transient guest or seasonal tenant',
  'D062', inter(note='No local just-cause ordinances in Jersey City, Hoboken or Newark; state act governs those cities'),
  False, None, False, None, 0.8,
  va(('https://law.justia.com/codes/new-jersey/title-2a/section-2a-18-61-1/', '2026-10-03T18:52Z', 'team supplementary D062: history line "L.1974, c.49, s.2"'),
     ('https://www.nj.gov/dca/codes/publications/pdf_lti/t_i_r.pdf', '2026-10-01T22:37Z', 'official DCA Truth in Renting (corpus D067) describes the Anti-Eviction Act')),
  'effective_date null: long-standing statute (L.1974, c.49) with many amendments; enacted_date taken from the statutory history line. Owner-occupancy exemption cannot be resolved from the data → "unknown" for buildings with ≤2 units or unknown units; buildings with units ≥3 defeat the exemption → "applies".')

R('NJ-DEP-01','NJ','state','security_deposits','in_force',
  'Rent Security Deposit Act cap – N.J.S.A. 46:8-21.2',
  'A landlord may not require a security deposit of more than one and one-half times one month\'s rent; annual additional security may not exceed 10% of the current deposit.',
  '1.5 months\' rent',
  cov(other='All rental dwelling premises; owner-occupied premises with ≤2 rental units are excluded unless the tenant gives 30 days\' written notice invoking the Act (N.J.S.A. 46:8-26)'),
  'Owner-occupied premises with not more than two rental units where the tenant has not invoked the Act (N.J.S.A. 46:8-26); seasonal rentals under 125 days',
  None, None, None, 'N.J.S.A. 46:8-21.2',
  ['S-NJ-03','S-NJ-04'], ['D067'], ['D063','D064'],
  'An owner or lessee may not require more than a sum equal to 1 1/2 times 1 month\'s rental according to the terms of contract, lease, or agreement as a security for the use or rental of real property used for dwelling purposes.',
  'D063', inter(),
  False, None, False, None, 0.85,
  va(('https://law.justia.com/codes/new-jersey/title-46/section-46-8-21-2/', '2026-10-03T18:49Z', 'team supplementary D063 (secondary mirror)'),
     ('https://law.justia.com/codes/new-jersey/title-46/section-46-8-26/', '2026-10-03T18:52Z', 'team supplementary D064: owner-occupied ≤2 unit exclusion'),
     ('https://www.nj.gov/dca/codes/publications/pdf_lti/t_i_r.pdf', '2026-10-01T22:37Z', 'official DCA Truth in Renting (corpus D067)')),
  'Quoted span taken from the Justia mirror (D063) because the organisers\' corpus has no statute copy; matches the organisers\' sample_rule_record (same URL). Owner-occupancy exemption → "unknown" for ≤2-unit or unknown-unit buildings.')

R('NJ-FEE-01','NJ','state','application_screening_fees','in_force',
  'Residential rental application fee cap ($50) – P.L.2025, c.405 (N.J.S.A. 46:8-18.1)',
  'A landlord or agent may not charge an application or similar fee exceeding $50 to apply to lease a residential rental property; the cap is CPI-adjusted each January from the year after enactment.',
  '$50 (CPI-adjusted from January 2027)',
  cov(minu=3, other='Residential rental property other than units in one- or two-family dwellings'),
  'Dwelling units in a one-family or two-family dwelling; NJ Real Estate Commission licensees who are not the landlord',
  '2026-05-01', '2026-01-20', None, 'N.J.S.A. 46:8-18.1 (P.L.2025, c.405, § 1)',
  ['S-NJ-06'], ['D066'], [],
  'shall not require an application or other similar fee to apply\nto lease or sublease a residential rental property for dwelling purposes, which\nexceeds $50.',
  'D066', inter(),
  False, None, False, None, 0.85,
  va(('https://pub.njleg.gov/bills/2024/PL25/405_.HTM', '2026-10-01T22:37Z', 'organisers corpus copy D066 (official): "Approved January 20, 2026"; § 3 effective first day of fourth month after enactment')),
  'Effective date computed from the enactment clause: approved 2026-01-20 → first day of the fourth month next following = 2026-05-01. One- and two-family dwellings exempt → buildings with units ≥3 "applies"; unknown units → "unknown".')

R('NJ-SCRN-01','NJ','state','screening_restrictions','in_force',
  'Fair Chance in Housing Act (criminal-record screening) – P.L.2021, c.110 (N.J.S.A. 46:8-52 et seq.)',
  'A housing provider may not ask about an applicant\'s criminal record before making a conditional offer, may never consider certain records, and may withdraw an offer only after an individualised assessment with written notice and a chance to respond.',
  'no criminal-record inquiry before conditional offer; individualised assessment required',
  cov(other='All housing providers; limited exceptions for owner-occupied small buildings (N.J.S.A. 46:8-54 definitions)'),
  'Lifetime sex-offender registrants and methamphetamine production on federally assisted premises may be considered; owner-occupied premises with ≤4 units are excluded from "housing provider" (per Act definitions – not quoted here)',
  '2022-01-01', '2021-06-18', None, 'N.J.S.A. 46:8-55 (P.L.2021, c.110)',
  ['S-NJ-07'], ['D065'], [],
  'regarding an applicant’s criminal record prior to making a conditional offer.',
  'D065', inter(note='Newark Title II ch. 2:31 (2015) is an earlier local fair-chance rule; both apply in Newark'),
  False, None, False, None, 0.85,
  va(('https://pub.njleg.gov/bills/2020/PL21/110_.HTM', '2026-10-01T22:37Z', 'organisers corpus copy D065 (official): "Approved June 18, 2021"; § 14 effective first day of seventh month after enactment')),
  'Effective date computed: approved 2021-06-18 → first day of seventh month next following = 2022-01-01. Exemption wording for owner-occupied buildings should be checked by Hamza against the definitions section (not quoted).')

R('NJ-SCRN-02','NJ','state','screening_restrictions','in_force',
  'Law Against Discrimination – source of lawful income used for rent – N.J.S.A. 10:5-12(g)',
  'It is unlawful to refuse to rent or otherwise discriminate in housing because of a person\'s source of lawful income used for rental payments (e.g., housing vouchers).',
  'source of lawful income (incl. vouchers) is a protected category',
  cov(other='All real property rentals subject to the LAD'),
  'LAD owner-occupied small-building exemptions (N.J.S.A. 10:5-5(n)) – not quoted here',
  None, None, None, 'N.J.S.A. 10:5-12(g)(1)',
  ['S-NJ-08'], ['D068'], ['D061'],
  'or source of lawful income used for rental or mortgage payments;',
  'D061', inter(),
  False, None, False, None, 0.75,
  va(('https://law.justia.com/codes/new-jersey/title-10/section-10-5-12/', '2026-10-03T18:52Z', 'team supplementary D061 (secondary mirror)'),
     ('https://www.nj.gov/oag/dcr/downloads/kyrhousing02.pdf', '2026-10-01T22:37Z', 'official DCR Know Your Rights housing (corpus D068)')),
  'effective_date null: source-of-lawful-income protection added by L.2002, c.82 (not verified against a primary source this session). Secondary rule in the NJ screening cell; NJ-SCRN-01 is the primary.')

R('NJ-ALG-01','NJ','state','algorithmic_rent_setting','not_yet_effective',
  'Forbidding the Algorithmic Inflation of Rent (FAIR) Act – P.L.2026, c.43',
  'From 2027-07-01, rental property owners may not pay for or use a "coordinator" (algorithmic revenue-management software processing competitors\' nonpublic data), and coordinators may not facilitate parallel pricing coordination; violations are New Jersey Antitrust Act violations.',
  'ban on use of algorithmic rent-setting coordinators (effective 2027-07-01)',
  cov(other='All residential dwelling units in New Jersey'),
  'Spreadsheets without AI; databases that only query unprocessed data; public free rent estimates; brokerage databases that do not recommend prices; government affordability controls',
  '2027-07-01', '2026-07-20', None, 'N.J.S.A. 56:9-20 to 56:9-26 (P.L.2026, c.43)',
  ['S-NJ-09'], ['D069'], ['D060'],
  'This act shall take effect on the first day of\nthe twelfth month next following the date of enactment.',
  'D069', inter(overrides=[], yields_to=[], note='§ 6(b): "A municipality shall be prohibited from enacting an ordinance that conflicts with this act" – possible preemption of Jersey City § 218-12 and Hoboken ch. 158 once effective; organisers require conflict_flag=true for Jersey City and Hoboken addresses'),
  True, 'Possible preemption of Jersey City and Hoboken algorithmic-pricing ordinances when the FAIR Act takes effect (P.L.2026 c.43 § 6(b)); organisers\' README lists this as an open question. Not resolved here.',
  False, None, 0.9,
  va(('https://pub.njleg.state.nj.us/Bills/2026/AL26/43_.HTM', '2026-10-01T22:56Z', 'organisers corpus copy D069 (official): "approved July 20, 2026"; § 9 effective first day of twelfth month next following enactment'),
     ('https://daypitney.com/new-jersey-enacts-fair-act-to-prohibit-algorithmic-rent-setting-practices', '2026-10-03T18:52Z', 'team supplementary D060 (secondary law-firm alert) – corroborates enactment')),
  'Effective date computed: approved 2026-07-20 → first day of twelfth month next following = 2027-07-01. Change test T3: not_yet_effective on 2026-10-01; applies on 2027-07-02 for every NJ address; Jersey City and Hoboken addresses conflict_flag=true.')

# ------------------------------------------------------------------ MASSACHUSETTS (state)
NEG('MA-RENT-00','MA','state','rent_increase_limits',
    'State law bars local rent control: M.G.L. c.40P, § 4 ("No city or town may enact, maintain or enforce rent control of any kind"); no statewide cap exists; the 2026 rent-control ballot initiative (IP 25-21) was struck by the SJC on 2026-06-23 (see MA-RENT-P1).',
    'M.G.L. c.40P, § 4', ['S-MA-01'], ['D048'], [],
    'No city or town may enact, maintain or enforce rent control of any kind', 'D048', 0.95,
    va(('https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40P/Section4', '2026-10-01T22:36Z', 'organisers corpus copy D048 (official)')),
    'Applies to Boston and Cambridge too; recorded as the reason for BOS-RENT-00 and CAM-RENT-00.')

R('MA-RENT-P1','MA','state','rent_increase_limits','failed',
  'Rent-control ballot initiative IP 25-21 (struck by the SJC 2026-06-23)',
  'A proposed 2026 ballot question would have limited annual residential rent increases statewide; the Supreme Judicial Court ruled on 2026-06-23 that it could not go before voters because it related to religion. No rent cap results.',
  None, cov(other='Would have applied statewide if enacted; never in force'),
  None, None, None, None, 'Initiative Petition 25-21 (Mass. 2026); Cella v. Attorney General (SJC, decided 2026-06-23)',
  ['S-MA-02'], [], ['D059'],
  'The state’s Supreme Judicial Court ruled a ballot question seeking to bring rent control back to Massachusetts cannot go forward this November, because it includes a religious exemption.',
  'D059', inter(),
  False, None, False, None, 0.7,
  va(('https://www.wbur.org/news/2026/06/23/massachusetts-high-court-rent-control-ballot-question-struck', '2026-10-03T18:52Z', 'team supplementary D059 (secondary news) – only reachable source; SJC opinion not fetched'),
     ('https://massrealestatelawblog.com/tag/cella-v-attorney-general/', '2026-10-03T19:02Z', 'capture failed (0 bytes) – not verified')),
  'Change test T5: status failed; affected address set empty; no rent cap reported for any Boston or Cambridge address. Status rests on a news report (WBUR) plus the organisers\' README/change_tests; the SJC slip opinion was not retrieved — Hamza to confirm case name/date if a primary cite is wanted.')

NEG('MA-JUST-00','MA','state','just_cause_eviction',
    'Massachusetts has no statewide just-cause eviction requirement; tenancies at will may be ended by notice (M.G.L. c.186, § 12) and non-payment terminations need a 14-day notice to quit (c.186, §§ 11, 12, 31). Boston and Cambridge impose only notice-of-rights duties (see BOS-JUST-01, CAM-JUST-01).',
    'M.G.L. c.186, §§ 11, 12 (notice to quit; no just-cause requirement)', ['S-MA-03','S-MA-04'], ['D050','D051','D058'], [],
    'Estates at will may be determined by either party by three months\' notice in writing for that purpose given to the other party', 'D051', 0.85,
    va(('https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section12', '2026-10-01T22:37Z', 'organisers corpus copy D051 (official)'),
       ('https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section11', '2026-10-01T22:37Z', 'organisers corpus copy D050 (official)')),
    'Negative finding supported by the absence of any just-cause provision in the corpus MA statutes; H.3744 (Boston home-rule petition for tenant eviction protections) died in study (see BOS-RENT-P1).')

R('MA-DEP-01','MA','state','security_deposits','in_force',
  'Security deposit limit – M.G.L. c.186, § 15B(1)(b)',
  'At or before the start of a tenancy a landlord may require only first month\'s rent, last month\'s rent, a security deposit equal to the first month\'s rent, and the cost of a new lock and key; the deposit must be held in a separate interest-bearing account.',
  '1 month\'s rent (security deposit)',
  cov(other='All residential tenancies in Massachusetts'),
  None, None, None, None, 'M.G.L. c.186, § 15B(1)(b)(iii)',
  ['S-MA-05'], ['D052'], [],
  'a security deposit equal to the first month\'s rent provided that such security deposit is deposited as required by subsection (3) and that the tenant is given the statement of condition as required by subsection (2)',
  'D052', inter(),
  False, None, False, None, 0.9,
  va(('https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B', '2026-10-01T22:37Z', 'organisers corpus copy D052 (official)')),
  'effective_date null: long-standing statute (St. 1978 c.553 and later); current clause (b) wording amended by St. 2025, c.9, §§ 54-55 effective 2025-08-01 per the official annotation in the corpus copy. The same section is the basis of the MA application-fee prohibition (MA-FEE-01).')

R('MA-FEE-01','MA','state','application_screening_fees','in_force',
  'Prohibition on landlord application fees – M.G.L. c.186, § 15B(1)(b)',
  'Because a landlord may require only first month\'s rent, last month\'s rent, a security deposit and a lock/key charge at or before the start of a tenancy, landlords may not charge rental application or screening fees. (Licensed brokers are regulated separately under 254 CMR 7 and M.G.L. c.112, § 87DDD½.)',
  '$0 – landlords may not charge application fees',
  cov(other='All residential tenancies in Massachusetts (lessors and their agents)'),
  'Licensed real estate brokers acting under their own contract with the tenant (M.G.L. c.112, § 87DDD½; 254 CMR 7)',
  None, None, None, 'M.G.L. c.186, § 15B(1)(b)',
  ['S-MA-05','S-MA-06'], ['D052','D057'], ['D054'],
  'no lessor or agent of the lessor may require a tenant or prospective tenant to pay, to the lessor or to an agent of the lessor, any amount in excess of the following:',
  'D052', inter(),
  False, None, False, None, 0.8,
  va(('https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B', '2026-10-01T22:37Z', 'organisers corpus copy D052 (official)'),
     ('https://masslandlords.net/can-massachusetts-landlords-charge-an-application-fee/', '2026-10-03T18:51Z', 'team supplementary D054 (secondary): confirms interpretation; cites Perry v. Equity Residential (D. Mass. 2014)')),
  'Interpretive rule: the statute is an exhaustive list rather than an express ban on application fees; secondary sources and case law treat it as a prohibition. Broker-fee reform (St. 2025 c.9, § 43, eff. 2025-08-01; M.G.L. c.112 § 87DDD½ in corpus D057) requires the engaging party to pay the broker.')

R('MA-SCRN-01','MA','state','screening_restrictions','in_force',
  'Public-assistance / housing-subsidy discrimination ban – M.G.L. c.151B, § 4(10)',
  'A person furnishing rental accommodations may not discriminate against an applicant or tenant because they receive public assistance or federal, state or local housing subsidies (e.g., Section 8), or because of any requirement of such a program.',
  'recipients of public assistance / housing subsidies are protected',
  cov(other='All rental accommodations subject to c.151B (owner-occupied two-family exemptions in c.151B § 4(6)/(11) not quoted)'),
  'Owner-occupied two-family dwellings for certain provisions (M.G.L. c.151B, § 4(6)) – not quoted',
  None, None, None, 'M.G.L. c.151B, § 4(10)',
  ['S-MA-07'], ['D049'], [],
  'For any person furnishing credit, services or rental accommodations to discriminate against any individual who is a recipient of federal, state, or local public assistance, including medical assistance, or who is a tenant receiving federal, state, or local housing subsidies, including rental assistance or rental supplements, because the individual is such a recipient, or because of any requirement of such public assistance, rental assistance, or housing subsidy program.',
  'D049', inter(note='Boston Fair Housing Ordinance and Cambridge Fair Housing Ordinance ch. 14.04 add local source-of-income protection; CORI regulations 803 CMR 5 (D056, capture failed) restrict criminal-history use'),
  False, None, False, None, 0.85,
  va(('https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXXI/Chapter151B/Section4', '2026-10-01T22:37Z', 'organisers corpus copy D049 (official)')),
  'effective_date null: long-standing statute. 803 CMR 5 (CORI in housing) could not be captured (mass.gov 403) and is not recorded as a separate rule.')

R('MA-ALG-P1','MA','state','algorithmic_rent_setting','pending',
  'S.2983 – An Act prohibiting algorithmic rent setting (pending)',
  'A pending Senate bill would prohibit algorithmic rent setting statewide; it was reported favourably by the Joint Committee on Housing on 2026-03-12 and referred to Senate Ways and Means. It is not law.',
  None, cov(other='Would apply statewide (all MA addresses) if enacted'),
  None, None, None, None, 'Mass. S.2983 (194th General Court)',
  ['S-MA-08'], ['D046','D047'], [],
  'Bill reported favorably by committee and referred to the committee on',
  'D046', inter(),
  False, None, False, None, 0.9,
  va(('https://malegislature.gov/Bills/194/S2983', '2026-10-01T22:36Z', 'organisers corpus copy D046 (official): status "Referred to Senate Committee on Ways and Means"')),
  'Change test T4: pending, never in force; affected set if enacted = all MA addresses. Status as of corpus retrieval 2026-10-01; not re-checked live on 2026-10-03.')

R('MA-ALG-P2','MA','state','algorithmic_rent_setting','pending',
  'H.5222 – An Act relative to preventing algorithmic rent fixing in the rental housing market (pending)',
  'A pending House bill (new draft of H.1564) would prevent algorithmic rent fixing statewide; reported favourably by the Joint Committee on Housing on 2026-03-12 and referred to House Ways and Means. It is not law.',
  None, cov(other='Would apply statewide (all MA addresses) if enacted'),
  None, None, None, None, 'Mass. H.5222 (194th General Court)',
  ['S-MA-09'], ['D045'], [],
  'An Act relative to preventing algorithmic rent fixing in the rental housing market',
  'D045', inter(),
  False, None, False, None, 0.9,
  va(('https://malegislature.gov/Bills/194/H5222', '2026-10-01T22:36Z', 'organisers corpus copy D045 (official): status "Referred to House Committee on Ways and Means"')),
  'Change test T4 companion bill.')

# ------------------------------------------------------------------ LOS ANGELES
R('LA-RENT-01','Los Angeles, CA','city','rent_increase_limits','in_force',
  'Rent Stabilization Ordinance annual allowable increase – LAMC § 151.06',
  'For RSO units (generally buildings first built on or before 1978-10-01), rent may be raised once every 12 months by the published allowable percentage (3% for 2025-07-01 to 2026-06-30). Ordinance 188795 (effective 2026-02-02) changed the formula to 90% of CPI with a 1% floor and 4% cap from 2026-07-01 and removed the utility and dependent surcharges.',
  '3% (Jul 2025–Jun 2026); from Jul 2026 formula = 90% of CPI, floor 1%, cap 4%',
  cov(coo='1978-10-01', minu=2, other='Rental units with a certificate of occupancy on or before 1978-10-01 (apartments, duplexes, 2+ SFDs on one parcel, condos/townhomes with pre-1996 tenancies, ADUs, mobile homes); replacement units under § 151.28'),
  'Units first built after 1978-10-01 (unless replacement units); single-family dwellings (one per parcel); luxury exemption; government-owned/subsidised units (partial)',
  '2026-02-02', '2025-12-24', None, 'L.A. Mun. Code § 151.06 (as amended by Ord. No. 188795)',
  ['S-LA-01','S-LA-02','S-LA-03'], ['D041','D042'], ['D044'],
  'Generally, the RSO applies to rental properties that were first built on or before October 1, 1978, as well as replacement units under',
  'D041', inter(overrides=['CA-RENT-01'], note='Stricter local rent control; Civ. Code § 1947.12(d)(3) makes the state cap inapplicable to RSO units; expected state result at RSO-covered addresses is superseded'),
  True, 'Organisers\' README: LA RSO new formula has two published effective dates — 2026-02-02 (LAHD) vs 2026-01-24 (Apartment Association of Greater Los Angeles). City Clerk council file 23-1134 records Ord. 188795 "Ordinance effective date: February 2, 2026" (checked 2026-10-03). Not resolved unilaterally; primary evidence favours 2026-02-02.',
  False, None, 0.75,
  va(('https://housing.lacity.gov/residents/rso-overview', '2026-10-03T20:05Z', 'official-agency: "Effective February 2, 2026, the landlord can no longer include an additional percentage increase for utilities"; RSO applies to properties first built on or before October 1, 1978'),
     ('https://cityclerk.lacity.org/lacityclerkconnect/index.cfm?fa=ccfi.viewrecord&cfnumber=23-1134', '2026-10-03T20:10Z', 'official City Clerk council file: Ord. No. 188795 adopted 2025-12-12, Mayor 2025-12-24, published 2025-12-26, effective 2026-02-02'),
     ('https://housing.lacity.gov/rso-rent-increase-calculator', '2026-10-03T20:10Z', 'official-agency: 3% for July 1, 2025 – June 30, 2026'),
     ('https://members.aagla.org/news/news-alert-la-city-passes-severely-reduced-rso-formula-ordinance', '2026-10-03T20:08Z', 'secondary (AAGLA): "effective January 24, 2026 and the new RSO formula calculation will be implemented July 1, 2026"; 90% CPI, 1% floor, 4% cap')),
  'effective_date is the Ord. 188795 date; the RSO itself dates from 1979. Year_built is not the COO date: a 1978 year_built → unknown; year_built ≤ 1977 → applies (if ≥2 units); year_built ≥ 1979 → not covered. The LAHD calculator page still shows the 2025-26 figure (3%); a 2026-27 figure (reported 3% by Hoodline, secondary) was not confirmed on an official page.')

R('LA-JUST-01','Los Angeles, CA','city','just_cause_eviction','in_force',
  'Just Cause for Eviction Ordinance (JCO) – LAMC § 165.03 (Ord. No. 187737)',
  'For residential units in Los Angeles not covered by the RSO, a landlord may not end a tenancy without one of the listed at-fault or no-fault just causes once the tenant has lived in the unit for six months or the initial lease has expired; no-fault evictions require relocation assistance.',
  'just cause required after 6 months or lease expiry; relocation assistance for no-fault',
  cov(ten=6, other='Residential rental units in the City of Los Angeles not subject to the RSO, including single-family dwellings and post-1978 buildings'),
  'RSO units (covered instead by LAMC 151.09); transient hotels; licensed care facilities; fraternity/sorority houses; owner\'s roommate; certain cooperatives, non-profit homeless facilities and HACLA/government-owned properties',
  '2023-01-27', '2023-01-27', None, 'L.A. Mun. Code § 165.03 (Art. 5.3, Ch. XVI; Ord. No. 187737)',
  ['S-LA-04','S-LA-05'], ['D040','D043'], [],
  'The JCO covers most residential properties in the City of Los Angeles that are not regulated by the City’s Rent Stabilization Ordinance (RSO).',
  'D040', inter(overrides=['CA-JUST-01'], note='Local just-cause ordinance more protective than Civ. Code § 1946.2 (6 months vs 12, relocation amounts); state rule superseded at covered addresses (§ 1946.2(i))'),
  False, None, False, None, 0.85,
  va(('https://housing.lacity.gov/residents/just-cause-for-eviction-ordinance-jco', '2026-10-01T22:36Z', 'organisers corpus copy D040 (official agency)'),
     ('https://cityclerk.lacity.org/onlinedocs/2021/21-0042-S3_ord_187737_1-27-23.pdf', '2026-10-03T20:18Z', 'official ordinance PDF: Ord. 187737 adding Art. 5.3 to Ch. XVI; urgency ordinance effective on publication 2023-01-27'),
     ('https://housing.lacity.gov/wp-content/uploads/2023/06/LA-Renter-protections-Notification.pdf', '2026-10-03T20:18Z', 'official-agency notice referencing Ord. 187737 and 2023-01-27')),
  'Covers the non-RSO half of LA rentals; LA-JUST-02 covers RSO units. For addresses with year_built ≤ 1978 the split between JCO and RSO just cause is unknown (COO vs year_built).')

R('LA-JUST-02','Los Angeles, CA','city','just_cause_eviction','in_force',
  'RSO legal reasons for eviction and relocation assistance – LAMC § 151.09',
  'For RSO units, a landlord may evict only for the fourteen legal reasons listed in the RSO (at-fault and no-fault); no-fault evictions require relocation assistance and a Landlord Declaration of Intent to Evict filed with LAHD, and all termination notices must be filed with LAHD within three business days.',
  'RSO just-cause grounds + relocation assistance',
  cov(coo='1978-10-01', minu=2, other='RSO rental units (certificate of occupancy on or before 1978-10-01)'),
  'Non-RSO units (covered by the JCO instead)',
  None, None, None, 'L.A. Mun. Code § 151.09',
  ['S-LA-01','S-LA-05'], ['D041','D043'], [],
  'three (3) business days of service on the tenant\nper Los Angeles Municipal Code 151.09.C.9 & 165.05.B.5.',
  'D041', inter(overrides=['CA-JUST-01'], note='Local just-cause regime adopted before 2019-09-01 → applies instead of Civ. Code § 1946.2 (§ 1946.2(i)(1)(A))'),
  False, None, False, None, 0.75,
  va(('https://housing.lacity.gov/residents/rso-overview', '2026-10-01T22:36Z', 'organisers corpus copy D041 (official agency): "Legal Reasons for Eviction" and LAMC 151.09.C.9 filing duty'),
     ('https://housing.lacity.gov/wp-content/uploads/2026/08/Relocation-Assistance-Bulletins-A-and-B-Combined.pdf', '2026-10-01T22:36Z', 'official-agency bulletin (corpus D043): relocation amounts effective 2026-07-01 to 2027-06-30')),
  'effective_date null: the RSO eviction provisions date from 1979 and have been amended many times; no single effective date verified. Hamza may prefer to merge LA-JUST-01/02 into one LA just-cause rule.')

R('LA-DEP-01','Los Angeles, CA','city','security_deposits','in_force',
  'Interest on security deposits for RSO units – LAMC § 151.06.02',
  'Landlords of RSO units must pay tenants interest on security deposits, accruing monthly since 1990-11-01, paid or credited at least annually at the rate set by the city.',
  'annual interest on deposits (RSO units)',
  cov(coo='1978-10-01', minu=2, other='RSO rental units'),
  'Non-RSO units',
  None, None, None, 'L.A. Mun. Code § 151.06.02',
  ['S-LA-01'], ['D041'], ['D044'],
  'Interest Payments on Security Deposits',
  'D041', inter(note='Adds to, does not displace, the state one-month cap (CA-DEP-01)'),
  False, None, False, None, 0.7,
  va(('https://housing.lacity.gov/residents/rso-overview', '2026-10-01T22:36Z', 'organisers corpus copy D041 (official agency) lists "Interest Payments on Security Deposits" among RSO requirements'),
     ('https://members.aagla.org/news/city-of-la-security-deposit-interest-requirement', '2026-10-03T18:51Z', 'team supplementary D044 (secondary) quotes LAMC 151.06.02: interest accrues from 1990-11-01, paid monthly or yearly')),
  'quoted_span is a heading on the official LAHD page (short but ≥20 chars); the operative text is only available in the secondary AAGLA capture. Category fit (security_deposits) is reasonable but this is an interest duty, not a cap — flagged for Hamza.')

NEG('LA-FEE-00','Los Angeles, CA','city','application_screening_fees',
    'No Los Angeles ordinance caps application screening fees; Cal. Civ. Code § 1950.6 (CA-FEE-01) governs.',
    'none (state Civ. Code § 1950.6 governs)', [], [], [], None, None, 0.7,
    va(('https://housing.lacity.gov/residents/rso-overview', '2026-10-01T22:36Z', 'organisers corpus copy D041: no screening-fee provision listed among RSO/JCO requirements')),
    'Absence finding: nothing in the organisers\' LA corpus or the LAHD pages describes a local fee cap; not exhaustively verified against the full LAMC.')

R('LA-SCRN-01','Los Angeles, CA','city','screening_restrictions','in_force',
  'Source of income discrimination prohibition – LAMC § 45.67 (Art. 5.6, Ch. IV)',
  'Anyone renting or listing housing in Los Angeles may not refuse to rent, apply different terms, misrepresent availability or advertise a preference based on a person\'s source of income, including housing assistance payments such as Section 8.',
  'source of income (incl. housing vouchers) protected',
  cov(other='All housing accommodations offered for rent in the City of Los Angeles'),
  None, '2020-01-01', None, None, 'L.A. Mun. Code § 45.67',
  ['S-LA-06','S-LA-07'], [], ['D038'],
  'refuse to rent or lease, or to continue to rent or lease, a housing accommodation; refuse to enter into or renew a rental agreement, lease or housing assistance payment contract',
  'D038', inter(note='Operates alongside Cal. Gov. Code § 12955 (CA-SCRN-01)'),
  False, None, False, None, 0.65,
  va(('https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-322208', '2026-10-03T19:02Z', 'team supplementary capture D038 (code publisher, single page): text of § 45.67'),
     ('https://2021.caanet.org/kb/city-of-los-angeles-source-of-income-discrimination-law/amp', '2026-10-03T20:19Z', 'secondary (CAA): "Effective January 1, 2020 ... (Los Angeles Municipal Code Section 45.65-45.69.)"')),
  'Effective date 2020-01-01 rests on the code publisher text plus a secondary source (CAA); the enacting ordinance number was not retrieved. Confidence ≤ 0.7 accordingly. The organisers\' corpus has no LA source-of-income document, so quoted_span_in_corpus is false.')

NEG('LA-ALG-00','Los Angeles, CA','city','algorithmic_rent_setting',
    'As of 2026-10-01 the City of Los Angeles has not enacted an algorithmic rent-setting ban; the only corpus document is a 2024-09-03 Council motion (CF 24-1031) instructing LAHD to report on feasibility. State law (CA-ALG-01) governs LA addresses.',
    'L.A. City Council motion CF 24-1031 (2024-09-03) – no ordinance', ['S-LA-08'], ['D039'], [],
    'report on the number of ownership and management entities that are using algorithm-based', 'D039', 0.6,
    va(('https://cityclerk.lacity.org/onlinedocs/2024/24-1031_misc_9-03-24.pdf', '2026-10-01T22:36Z', 'organisers corpus copy D039 (official): motion only'),
       ('https://www.morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws', '2026-10-03T18:49Z', 'team supplementary D002 (secondary, Aug 2026 survey of local bans) lists SF, San Diego, Berkeley, Santa Ana but not Los Angeles')),
    'Web search on 2026-10-03 found no enacted LA ordinance (results were West Hollywood, Santa Monica, San Diego, Berkeley). Hamza should confirm; if LA enacted a ban after Aug 2026 this becomes a rule.',
    conflict_flag=True, conflict_note='Absence of an LA ordinance inferred from the corpus and an Aug-2026 law-firm survey; not confirmed against the LAMC or council files.')

# ------------------------------------------------------------------ SAN FRANCISCO
R('SF-RENT-01','San Francisco, CA','city','rent_increase_limits','in_force',
  'Rent Ordinance annual allowable increase – S.F. Admin. Code § 37.3',
  'For rent-controlled units (generally buildings with a certificate of occupancy on or before 1979-06-13), the landlord may raise rent once a year by the Rent Board\'s annual allowable increase: 1.6% for 2026-03-01 to 2027-02-28.',
  '1.6% (2026-03-01 to 2027-02-28); formula 60% of CPI',
  cov(coo='1979-06-13', other='Rental units with a certificate of occupancy on or before 1979-06-13 (Costa-Hawkins exempts separately alienable SFRs/condos from the rent limits)'),
  'Units first occupied/COO after 1979-06-13; single-family homes and condos with post-1995 tenancies (Costa-Hawkins); government-regulated rents',
  None, None, None, 'S.F. Admin. Code § 37.3(a)',
  ['S-SF-01','S-SF-02'], ['D080','D083','D079'], [],
  'For rent-controlled units, the annual allowable increase amount effective March 1, 2026 through February 28, 2027 is 1.6%.',
  'D080', inter(overrides=['CA-RENT-01'], note='Stricter local rent control; state cap superseded at covered addresses'),
  False, None, False, None, 0.85,
  va(('https://www.sf.gov/news--annual-rent-increase-3126-22827-announced', '2026-10-01T22:37Z', 'organisers corpus copy D080 (official Rent Board)'),
     ('https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit', '2026-10-01T22:37Z', 'organisers corpus copy D083 (official): 1.6% for March 1, 2026 – February 28, 2027'),
     ('https://sf.gov/information/overview-just-cause-evictions', '2026-10-01T22:37Z', 'organisers corpus copy D079: COO cutoff June 13, 1979')),
  'effective_date null: the Rent Ordinance dates from 1979; the rate changes annually. Year_built 1979 → unknown (no SF rows have year_built 1979 in the sample; two SF rows lack year_built). sf.gov blocked WebFetch on 2026-10-03, so no live re-check.')

R('SF-JUST-01','San Francisco, CA','city','just_cause_eviction','in_force',
  'Rent Ordinance just cause for eviction – S.F. Admin. Code § 37.9(a)',
  'A landlord may evict a tenant from a unit covered by the Rent Ordinance only for one of the 17 just causes listed in § 37.9(a); this applies even to newer units (post-1979 COO) that are exempt from the rent-increase limits.',
  '17 enumerated just causes',
  cov(other='All residential rental units covered by the Rent Ordinance, including post-1979 units exempt from rent limits'),
  'Units fully exempt from the Rent Ordinance (e.g., certain government-owned housing, some non-profit and institutional housing)',
  None, None, None, 'S.F. Admin. Code § 37.9(a)',
  ['S-SF-03'], ['D079'], [],
  'In order to evict a tenant from a rental unit covered by the Rent Ordinance, a landlord must have a "just cause" reason that is the dominant motive for pursuing the eviction.',
  'D079', inter(overrides=['CA-JUST-01'], note='Local ordinance adopted before 2019-09-01 → applies instead of Civ. Code § 1946.2 (§ 1946.2(i)(1)(A))'),
  False, None, False, None, 0.9,
  va(('https://sf.gov/information/overview-just-cause-evictions', '2026-10-01T22:37Z', 'organisers corpus copy D079 (official Rent Board)')),
  'effective_date null: long-standing (1979) ordinance.')

R('SF-DEP-01','San Francisco, CA','city','security_deposits','in_force',
  'Interest on security deposits – S.F. Admin. Code ch. 49',
  'Landlords must pay tenants annual interest on security deposits held for a year or more at the rate set by the Rent Board: 4.2% for 2026-03-01 to 2027-02-28.',
  '4.2% annual interest (2026-03-01 to 2027-02-28)',
  cov(other='Residential units in San Francisco where a deposit has been held for at least one year'),
  None, None, None, None, 'S.F. Admin. Code ch. 49 (§ 49.2)',
  ['S-SF-02'], ['D083'], [],
  '4.2% for March 1, 2026 – February 28, 2027',
  'D083', inter(note='Adds to the state one-month cap (CA-DEP-01)'),
  False, None, False, None, 0.75,
  va(('https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit', '2026-10-01T22:37Z', 'organisers corpus copy D083 (official Rent Board rates page)')),
  'The corpus page states the rate but not the ordinance text; the chapter 49 citation is from general knowledge and should be checked by Hamza. Category fit (interest duty vs cap) flagged.')

NEG('SF-FEE-00','San Francisco, CA','city','application_screening_fees',
    'No San Francisco ordinance caps application screening fees; Cal. Civ. Code § 1950.6 (CA-FEE-01) governs.',
    'none (state Civ. Code § 1950.6 governs)', [], [], [], None, None, 0.7,
    va(('https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit', '2026-10-01T22:37Z', 'organisers corpus copy D083: no screening-fee rate listed among Rent Board rates')),
    'Absence finding based on the organisers\' SF corpus; not exhaustively verified against the full Administrative/Police Codes.')

R('SF-SCRN-01','San Francisco, CA','city','screening_restrictions','in_force',
  'Fair Chance Ordinance (housing) – S.F. Police Code art. 49',
  'Affordable-housing providers in San Francisco may not consider certain arrest or conviction history and must follow fair-chance procedures when screening applicants.',
  'criminal-history limits for affordable housing providers',
  cov(other='Affordable housing (city-funded or inclusionary) in San Francisco; not all private market-rate rentals'),
  'Market-rate housing not covered by the Fair Chance Ordinance\'s housing provisions',
  None, None, None, 'S.F. Police Code art. 49 (§§ 4901 et seq.)',
  ['S-SF-04'], ['D078'], [],
  'San Francisco\'s Fair Chance Ordinance protects residents with arrest or conviction history in affordable housing decisions.',
  'D078', inter(),
  True, 'Coverage limited to affordable housing; whether a sample address is affordable housing is not in the data → expected result unknown. Category boundary (screening_restrictions) acceptable; coverage detail from general knowledge, not quoted.',
  False, None, 0.6,
  va(('https://sf-hrc.org/fair-chance-ordinance', '2026-10-01T22:37Z', 'organisers corpus copy D078 (official HRC page) – one sentence only; sf.gov blocked WebFetch on 2026-10-03')),
  'effective_date null (ordinance from 2014, amended 2018 — not verified). SF Police Code art. 33 (source of income) not separately recorded.')

R('SF-ALG-01','San Francisco, CA','city','algorithmic_rent_setting','in_force',
  'Prohibition on algorithmic devices to set rents – S.F. Admin. Code § 37.10C',
  'It is unlawful to sell or use an algorithmic device that analyses nonpublic competitor rental data to recommend rents or occupancy levels for residential units in San Francisco; tenants and the City Attorney may sue.',
  'ban on sale/use of algorithmic rent-setting devices',
  cov(other='All residential units in San Francisco'),
  None, '2024-10-14', '2024-09-13', None, 'S.F. Admin. Code § 37.10C',
  ['S-SF-05'], ['D081'], ['D002'],
  'The law prohibits the sale or use of algorithmic devices to set rents or manage occupancy levels for residential units in San Francisco.',
  'D081', inter(note='Additional to state AB 325 (CA-ALG-01)'),
  False, None, False, None, 0.85,
  va(('https://www.sf.gov/news/new-law-prohibits-algorithmic-devices-used-set-rents-san-francisco', '2026-10-01T22:37Z', 'organisers corpus copy D081 (official): "went into effect on October 14, 2024"'),
     ('https://www.morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws', '2026-10-03T18:49Z', 'team supplementary D002 (secondary): "S.F. Admin. Code § 37.10C (effective October 2024)"')),
  'enacted_date 2024-09-13 (Mayor\'s signature) is from general knowledge and NOT verified this session; Hamza to confirm or null it.')

# ------------------------------------------------------------------ SAN DIEGO
NEG('SD-RENT-00','San Diego, CA','city','rent_increase_limits',
    'The City of San Diego has no local rent-increase cap; Cal. Civ. Code § 1947.12 (CA-RENT-01) governs San Diego addresses.',
    'none (state Civ. Code § 1947.12 governs)', ['S-SD-01'], ['D073'], ['D077'],
    'The rights conferred by \nthis Division are in addition to any existing rights provided to tenants by state or \nfederal law.', 'D073', 0.8,
    va(('https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf', '2026-10-01T22:37Z', 'organisers corpus copy D073 (official SDMC ch. 9 art. 8 div. 7): no rent-cap provision'),
       ('https://www.lassd.org/resource/city-of-san-diego-tenant-protection-ordinance/', '2026-10-03T18:53Z', 'team supplementary D077 (secondary): TPO addresses just cause/relocation only')),
    'Negative finding; span confirms the TPO adds to (not replaces) state law and contains no rent cap.')

R('SD-JUST-01','San Diego, CA','city','just_cause_eviction','in_force',
  'Residential Tenant Protection Ordinance – SDMC § 98.0704',
  'A landlord may not terminate a tenancy without at-fault or no-fault just cause as listed in SDMC 98.0704; no-fault terminations require relocation assistance of two months\' rent (three for elderly/disabled tenants).',
  'just cause required; 2 months relocation (3 for elderly/disabled)',
  cov(other='Residential rental property in the City of San Diego other than the exemptions in § 98.0703 (incl. COO within previous 15 years)'),
  'Transient/short-term occupancy; deed-restricted affordable housing (not Section 8); mobilehomes; care facilities; dormitories; owner-shared units; owner-occupied SFR (≤2 bedrooms/ADUs rented); owner-occupied duplex; housing with COO within previous 15 years; separately alienable SFR/condo not owned by REIT/corporation/corporate LLC with notice',
  '2023-06-24', '2023-05-25', None, 'San Diego Mun. Code § 98.0704 (O-21647 N.S.)',
  ['S-SD-01'], ['D073'], ['D077'],
  'A landlord shall not terminate a tenancy without just cause. For purposes of this \nDivision, just cause includes at-fault just cause and no-fault just cause.',
  'D073', inter(overrides=['CA-JUST-01'], note='More protective local just-cause ordinance adopted after 2019-09-01 (§ 1946.2(i)(1)(B)); state rule superseded at covered addresses'),
  False, None, False, None, 0.9,
  va(('https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf', '2026-10-01T22:37Z', 'organisers corpus copy D073 (official): "added 5-25-2023 by O-21647 N.S.; effective 6-24-2023"; amended 2-27-2024 by O-21769 N.S. effective 3-28-2024'),
     ('https://www.lassd.org/resource/city-of-san-diego-tenant-protection-ordinance/', '2026-10-03T18:53Z', 'team supplementary D077 (secondary): relocation amounts and 2023-06-24 effective date')),
  'San Diego rows have no year_built → the 15-year COO exemption cannot be tested → expected address result unknown (missing fact: year_built/COO).')

NEG('SD-DEP-00','San Diego, CA','city','security_deposits',
    'No San Diego ordinance regulates security deposits; Cal. Civ. Code § 1950.5 (CA-DEP-01) governs.',
    'none (state Civ. Code § 1950.5 governs)', ['S-SD-01'], ['D073'], [], None, None, 0.7,
    va(('https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf', '2026-10-01T22:37Z', 'organisers corpus copy D073: no deposit provision in the TPO')),
    'Absence finding based on the organisers\' San Diego corpus.')

NEG('SD-FEE-00','San Diego, CA','city','application_screening_fees',
    'No San Diego ordinance caps application screening fees; Cal. Civ. Code § 1950.6 (CA-FEE-01) governs.',
    'none (state Civ. Code § 1950.6 governs)', ['S-SD-01'], ['D073'], [], None, None, 0.7,
    va(('https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf', '2026-10-01T22:37Z', 'organisers corpus copy D073: no fee provision in the TPO')),
    'Absence finding based on the organisers\' San Diego corpus.')

R('SD-SCRN-01','San Diego, CA','city','screening_restrictions','in_force',
  'Prohibition of discrimination based on a tenant\'s source of income – SDMC §§ 98.0801–98.0803',
  'Landlords in the City of San Diego may not refuse to rent, terminate, misrepresent availability or impose different terms based on a person\'s source of income, including housing vouchers, and must evaluate the applicant\'s entire source of income.',
  'source of income (incl. vouchers) protected',
  cov(other='Residential rental property in the City of San Diego'),
  None, '2018-10-18', '2018-09-18', None, 'San Diego Mun. Code § 98.0803 (O-20986 N.S.)',
  ['S-SD-02','S-SD-03'], [], ['D075'],
  None, None, inter(note='Operates alongside Cal. Gov. Code § 12955 (CA-SCRN-01)'),
  True, 'Published effective date 10-18-2018 (code history note) vs. an operative date of 2019-08-01 reported by the San Diego Association of Realtors; only the code history was quoted. Team capture D075 (gocodebook) returned only a table of contents, so no quoted_span.',
  False, None, 0.6,
  va(('https://www.nhlp.org/wp-content/uploads/SD-Municipal-Code-SOI-Article-08-Housing-1.pdf', '2026-10-03T20:14Z', 'secondary mirror (NHLP PDF of SDMC Div. 8): history "Ordinance O–20986 N.S.; effective 10-18-2018"'),
     ('https://gocodebook.com/library/us/ca/san-diego-zoning/division-8-prohibition-of-discrimination-based-on-a-tenant-s-source-of-income/98.0801-purpose-and-intent', '2026-10-03T20:13Z', 'code publisher returned HTTP 500 on fetch; team capture D075 contains only the site TOC')),
  'quoted_span null: no saved copy of the operative text (official SDMC PDF for Division 8 not retrieved; 500 error from code publisher). enacted_date 2018-09-18 from the CAA ordinance copy filename (SD_Section8Ord_091118) – low confidence.')

R('SD-ALG-01','San Diego, CA','city','algorithmic_rent_setting','in_force',
  'Prohibition of anti-competitive automated rent price-fixing – SDMC § 98.1103',
  'It is unlawful to sell, license or provide an algorithmic device (software analysing nonpublic competitor data of two or more landlords) to a landlord, or for a landlord to use one to set rents or occupancy levels for residential rental property in San Diego; tenants may sue for up to $1,000 per violation.',
  'ban on sale/use of algorithmic rent-setting devices',
  cov(other='All residential rental property in the City of San Diego'),
  'Reports from aggregated data more than 90 days old; affordable-housing rent-limit software; appraisal software',
  '2025-06-21', '2025-05-22', None, 'San Diego Mun. Code § 98.1103 (O-21955 N.S.)',
  ['S-SD-04','S-SD-05'], ['D076'], ['D074'],
  'It is unlawful for a landlord to use an algorithmic device to set rental rates or',
  'D074', inter(note='Additional to state AB 325 (CA-ALG-01)'),
  False, None, False, None, 0.85,
  va(('https://gocodebook.com/library/us/ca/san-diego-zoning/division-11-prohibition-of-anti-competitive-automated-rent-price-fixing/98.1103-use-and-sale-of-algorithmic-devices-prohibited', '2026-10-03T19:03Z', 'team supplementary capture D074 (code publisher): "added 5-22-2025 by O-21955 N.S.; effective 6-21-2025"'),
     ('https://sandiego.gov/sites/default/files/2025-04/automated-rent-price-fixing-prohibition-ordinance-materials.pdf', '2026-10-01T22:37Z', 'organisers corpus copy D076 (official staff report + draft ordinance O-2025-107): effective 30th day after final passage')),
  'The organisers\' corpus has only the pre-adoption draft (D076); the adopted code text with dates is in the team capture D074, so quoted_span_in_corpus is false for the exact span. Draft text in D076 uses the same operative sentence split across lines.')

# ------------------------------------------------------------------ BERKELEY
R('BERK-RENT-01','Berkeley, CA','city','rent_increase_limits','in_force',
  'Rent Stabilization Ordinance annual general adjustment – BMC § 13.76.110',
  'For fully covered units (generally multifamily buildings built before 1980), rent ceilings may rise each January by the Annual General Adjustment of 65% of CPI, never above 5%: 1.0% for 2026.',
  '1.0% for 2026 (65% of CPI; 5% cap)',
  cov(coo='1980-06-30', other='Fully covered units: multifamily units with a certificate of occupancy on or before 1980-06-30 (new construction after June 1980 is only partially covered: no rent control)'),
  'New construction (COO after June 1980) – partially covered, no rent ceiling; single-family homes with tenancies from 1996 onward; most condominiums; golden duplexes; owner-shared units; ADUs with owner occupancy; nonprofit cooperatives; dormitories',
  None, None, None, 'Berkeley Mun. Code § 13.76.110(A)',
  ['S-BK-01','S-BK-02','S-BK-03'], ['D008','D009','D006'], [],
  'adopted the Annual General Adjustment (AGA) Order for Year 2026 which will allow \neligible landlords to increase the 2025 permanent rent ceilings by 1.0% no earlier than \nJanuary 1, 2026.',
  'D008', inter(overrides=['CA-RENT-01'], note='Stricter local rent control; state cap superseded at fully covered addresses'),
  False, None, False, None, 0.85,
  va(('https://rentboard.berkeleyca.gov/sites/default/files/documents/AGA%20Public%20Notice.pdf', '2026-10-01T22:35Z', 'organisers corpus copy D008 (official Rent Board notice)'),
     ('https://rentboard.berkeleyca.gov/sites/default/files/documents/Rent%20Ordinance%20Coverage%20by%20Unit%20Type.pdf', '2026-10-01T22:35Z', 'organisers corpus copy D009: coverage table (built before 1980 fully covered)'),
     ('https://berkeley.municipal.codes/BMC/13.76.110', '2026-10-03T20:16Z', 'official code publisher: 65% of CPI-U, never below 0% or above 5%; history Ord. 7950-NS (2024) back to Ord. 5261-NS (1980)')),
  'Berkeley rows have no year_built or units → coverage unknown for every sample address (missing facts: COO/year_built). effective_date null (1980 ordinance, amended by Measure BB 2024).')

R('BERK-JUST-01','Berkeley, CA','city','just_cause_eviction','in_force',
  'Rent Stabilization and Eviction for Just Cause Ordinance – BMC § 13.76.130',
  'Tenants in fully or partially covered units may be evicted only for a just cause listed in the ordinance; Measure BB (2024) bars non-payment evictions for debt under one month of HUD Fair Market Rent and removed the failure-to-sign-a-new-lease ground.',
  'enumerated just causes; non-payment eviction only if debt ≥ 1 month FMR',
  cov(other='All units fully or partially covered by the Rent Ordinance (including new construction and single-family homes)'),
  'Exempt units: golden duplex; owner-shared kitchen/bath where owner lived there first; owner-occupied ADU properties (tenancies after 2018-11-07); dormitories; nonprofit cooperatives',
  None, None, None, 'Berkeley Mun. Code § 13.76.130',
  ['S-BK-02','S-BK-03'], ['D006','D009'], [],
  'In Berkeley, tenants in units that are fully or partially covered by the Rent Ordinance cannot be evicted unless there is "just cause” (previously called “good cause”).',
  'D006', inter(overrides=['CA-JUST-01'], note='Local just-cause ordinance adopted before 2019-09-01 → applies instead of Civ. Code § 1946.2'),
  False, None, False, None, 0.85,
  va(('https://rentboard.berkeleyca.gov/laws-regulations/measure-bb-changes-berkeleys-rent-ordinance', '2026-10-01T22:35Z', 'organisers corpus copy D006 (official Rent Board)'),
     ('https://rentboard.berkeleyca.gov/sites/default/files/documents/Rent%20Ordinance%20Coverage%20by%20Unit%20Type.pdf', '2026-10-01T22:35Z', 'organisers corpus copy D009: just cause applies to fully and partially covered units')),
  'Partially covered units (post-1980 construction) still get just cause, so most Berkeley multifamily addresses → applies even without year_built; exempt categories cannot be excluded from the data (owner-occupancy) → Hamza to decide applies vs unknown.')

R('BERK-DEP-01','Berkeley, CA','city','security_deposits','in_force',
  'Interest on security deposits – Berkeley Rent Ordinance (BMC § 13.76.070)',
  'Landlords of units fully or partially covered by the Rent Ordinance must pay tenants interest on security deposits at the end of each year (prorated on move-out).',
  'annual interest on deposits (covered units)',
  cov(other='Units fully or partially covered by the Rent Ordinance'),
  'Exempt units (see BERK-JUST-01)',
  None, None, None, 'Berkeley Mun. Code § 13.76.070',
  ['S-BK-04','S-BK-02'], ['D007','D009'], [],
  'landlords must pay tenants interest on their security deposit at the end of each year and a prorated amount if the tenant moves out before the end of the year.',
  'D007', inter(note='Adds to the state one-month cap (CA-DEP-01)'),
  False, None, False, None, 0.75,
  va(('https://rentboard.berkeleyca.gov/rights-responsibilities/security-deposits', '2026-10-01T22:35Z', 'organisers corpus copy D007 (official Rent Board)'),
     ('https://rentboard.berkeleyca.gov/sites/default/files/documents/Rent%20Ordinance%20Coverage%20by%20Unit%20Type.pdf', '2026-10-01T22:35Z', 'organisers corpus copy D009: security deposit interest column')),
  'Section number 13.76.070 from general knowledge – Hamza to confirm. Category fit (interest duty) flagged like LA-DEP-01/SF-DEP-01.')

R('BERK-FEE-01','Berkeley, CA','city','application_screening_fees','in_force',
  'Tenant screening fee disclosure and renewal-fee ban – BMC ch. 13.78',
  'An owner charging a screening fee must give the applicant a clear tenant-screening-fee rights statement and state the maximum fee permitted under Cal. Civ. Code § 1950.6(b) (BMC 13.78.010); non-refundable fees to existing tenants for renewals or roommate changes are prohibited (BMC 13.78.016).',
  'disclosure of state fee cap required; no non-refundable renewal/roommate fees',
  cov(other='All residential rental agreements in Berkeley'),
  None, None, None, None, 'Berkeley Mun. Code §§ 13.78.010, 13.78.016',
  ['S-BK-05'], ['D005'], [],
  'cannot charge a non-refundable fee to any existing tenant for the purpose of renewing a tenancy, in whole or in part, including any fee associated with the departure of a roommate or to request to add or replace a roommate in a pre-existing household.',
  'D005', inter(note='Does not change the state cap (CA-FEE-01); both apply'),
  True, 'Borderline categorisation: BMC 13.78 is a disclosure/notice duty plus a renewal-fee ban, not a fee cap. Alternative is a negative finding (BERK-FEE-00) with the state cap governing. Decision reserved for Hamza (open_questions.md).',
  False, None, 0.6,
  va(('https://rentboard.berkeleyca.gov/laws-regulations/city-berkeley-ordinances-affecting-rental-properties/tenant-screening-and', '2026-10-01T22:35Z', 'organisers corpus copy D005 (official Rent Board): BMC 13.78.010/.016/.018; 2026 maximum screening fee $68.96')),
  'effective_date null (ordinance date not verified). The Rent Board page publishes a 2026 maximum screening fee of $68.96 – a local computation of the state CPI-adjusted cap.')

R('BERK-SCRN-01','Berkeley, CA','city','screening_restrictions','in_force',
  'Ronald V. Dellums Fair Chance Access to Housing Ordinance – BMC ch. 13.106',
  'Rental housing providers in Berkeley may not ask about or use criminal history or criminal background checks in advertising, applications, tenant selection or decisions, with limited exceptions (lifetime sex-offender registrants, certain federally assisted housing, small owner-occupied properties).',
  'ban on criminal-history inquiry and use in housing decisions',
  cov(other='All rental housing providers in Berkeley'),
  'Lifetime sex-offender registrants; public housing/Section 8 limited exemptions; owner-occupied properties of 1–3 units where an owner of record lives; owner move-back tenancies (BMC 13.76.130 A.9); existing tenants subletting/adding roommates',
  '2020', '2020-04-14', None, 'Berkeley Mun. Code § 13.106.040 (Ord. 7692-NS)',
  ['S-BK-06','S-BK-07'], ['D003'], [],
  'The Fair Chance Access to Housing Ordinance prohibits rental housing providers in Berkeley from asking about and using criminal history and/or criminal background checks in their rental housing advertising, applications, tenant selection process, or decision-making.',
  'D003', inter(note='Stricter than CA state law (CRD regulations) and operates alongside Cal. Gov. Code § 12955'),
  False, None, False, None, 0.75,
  va(('https://rentboard.berkeleyca.gov/Fair_Chance', '2026-10-01T22:35Z', 'organisers corpus copy D003 (official Rent Board): "On April 14, 2020, Berkeley City Council passed the Fair Chance Access to Housing Ordinance (BMC 13.106)"'),
     ('https://berkeley.municipal.codes/enactments/Ord7692-NS', '2026-10-03T20:17Z', 'official code publisher: Ord. 7692-NS adds Ch. 13.106 (2020); exact effective date not shown')),
  'effective_date given at year precision (2020): adoption 2020-04-14 verified; the 30-day effective date was not shown by the code publisher. Owner-occupancy exemption (1–3 units) cannot be resolved from the data (no units for Berkeley) → unknown.')

R('BERK-ALG-01','Berkeley, CA','city','algorithmic_rent_setting','in_force',
  'Prohibition on coordinated pricing algorithms – BMC ch. 13.63 (Ord. 7992-NS)',
  'It is unlawful to sell or provide to Berkeley landlords, or for a landlord to use, a coordinated pricing algorithm that uses nonpublic competitor data to set or recommend rents or occupancy levels; each unit and month is a separate violation (up to $1,000 each).',
  'ban on sale/use of coordinated pricing algorithms',
  cov(other='All residential dwelling units in the City of Berkeley'),
  'Aggregated anonymous reports; affordable-housing rent-limit tools; market research, appraisal and software testing uses',
  '2026-01-01', '2025-12-02', None, 'Berkeley Mun. Code § 13.63.030 (Ord. 7992-NS)',
  ['S-BK-08','S-BK-09'], ['D001'], ['D002'],
  'B. It shall be unlawful for a landlord to use a coordinated pricing algorithm described \nin subsection A when setting rents or occupancy levels for residential dwelling units in \nthe City of Berkeley.',
  'D001', inter(note='Additional to state AB 325 (CA-ALG-01)'),
  True, 'Organisers\' README: two published effective dates — 2026-03-01 (ordinance text) vs January 2026 (Aug-2026 law-firm alert). Verified history: Ord. 7956-NS added ch. 13.63 (adopted 2025-03-25, eff. 2025-04-24); Ord. 7974-NS (adopted 2025-07-08, eff. 2025-08-07) inserted "The provisions of this Chapter shall not take effect until March 1, 2026"; Ord. 7992-NS (adopted 2025-12-02, eff. 2026-01-01 per berkeley.municipal.codes) re-enacted the chapter without that clause. Not resolved unilaterally; evidence favours 2026-01-01.',
  False, None, 0.7,
  va(('https://berkeleyca.gov/sites/default/files/documents/2025-12-02%20Item%2001%20Ordinance%207992.pdf', '2026-10-01T22:44Z', 'organisers corpus copy D001 (official): Ord. 7,992-N.S. text, passed to print 2025-11-18'),
     ('https://berkeley.municipal.codes/enactments/Ord7992-NS', '2026-10-03T20:12Z', 'official code publisher: adopted December 2, 2025; effective January 1, 2026'),
     ('https://berkeleyca.gov/sites/default/files/documents/2025-07-08%20Item%2001%20Amendments%20to%20Ordinance%20Prohibiting.pdf', '2026-10-03T20:13Z', 'official council item for Ord. 7974-NS: "The provisions of this Chapter shall not take effect until March 1, 2026."'),
     ('https://morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws', '2026-10-03T18:49Z', 'team supplementary D002 (secondary): "Berkeley Mun. Code ch. 13.63 (effective January 2026)"')),
  'RealPage v. City of Berkeley (N.D. Cal.) voluntarily dismissed with prejudice 2026-01-14 per D002.')

# ------------------------------------------------------------------ SANTA ANA (extraction only)
R('SA-RENT-01','Santa Ana, CA','city','rent_increase_limits','in_force',
  'Rent Stabilization Ordinance – Santa Ana Mun. Code ch. 8, art. XIX',
  'Annual rent increases for covered units are limited to the lesser of 3% or 80% of the CPI change (2.87% for 2026-09-01 to 2027-08-31); no increase if CPI is negative. Buildings constructed after 1995-02-01 are not covered.',
  'lesser of 3% or 80% of CPI; 2.87% for Sep 2026–Aug 2027',
  cov(ybmax=1995, other='Residential rental buildings constructed on or before 1995-02-01 (and mobile home spaces first rented before 1990-01-01)'),
  'Residential buildings constructed after 1995-02-01; mobile home spaces offered for rent after 1990-01-01; owner petitions for fair return',
  '2021-11-19', '2021-10-19', None, 'Santa Ana Mun. Code § 8-1998 et seq. (Rent Stabilization Ordinance)',
  ['S-SA-01','S-SA-02'], ['D084','D085'], [],
  'The increase cannot be more than 3% of your current rent or 80% of the Consumer Price Index (CPI) change, whichever is less.',
  'D084', inter(overrides=['CA-RENT-01'], note='Stricter local rent control; state cap superseded at covered units'),
  False, None, False, None, 0.8,
  va(('https://santa-ana.gov/departments/rent-stabilization', '2026-10-03T20:11Z', 'official city page (also corpus D084): 2.87% for September 1, 2026 through August 31, 2027'),
     ('https://santa-ana.gov/santa-ana-city-council-adopts-rent-stabilization-and-just-cause-eviction-ordinances-effective-nov-19', '2026-10-01T22:37Z', 'organisers corpus copy D085 (official): adopted Tuesday [2021-10-19]; "not effective until November 19, 2021"; post-1995-02-01 buildings excluded')),
  'Section citation (§ 8-1998 et seq.) from general knowledge – Hamza to confirm. No Santa Ana addresses in the sample (extraction only). enacted_date 2021-10-19 inferred from the press-release date ("Tuesday night") – low confidence.')

R('SA-JUST-01','Santa Ana, CA','city','just_cause_eviction','in_force',
  'Just Cause Eviction Ordinance – Santa Ana Mun. Code ch. 8, art. XIX-A',
  'After 30 days of tenancy an owner may not terminate without a stated at-fault or no-fault just cause; no-fault terminations require three months of relocation assistance or rent waiver.',
  'just cause after 30 days; 3 months relocation for no-fault',
  cov(other='Residential rental property in Santa Ana other than housing produced in the last 15 years and other listed exemptions'),
  'Housing produced in the last 15 years; deed-restricted affordable housing; hotels/transient occupancy; hospitals/care facilities; dormitories; shared living quarters',
  '2021-11-19', '2021-10-19', None, 'Santa Ana Mun. Code (Just Cause Eviction Ordinance, 2021)',
  ['S-SA-02'], ['D085'], [],
  'After 30 days, an owner shall not terminate a tenancy without just cause, which shall be stated in a written notice.',
  'D085', inter(overrides=['CA-JUST-01'], note='More protective local just-cause ordinance adopted after 2019-09-01; state rule superseded at covered units'),
  False, None, False, None, 0.8,
  va(('https://santa-ana.gov/santa-ana-city-council-adopts-rent-stabilization-and-just-cause-eviction-ordinances-effective-nov-19', '2026-10-01T22:37Z', 'organisers corpus copy D085 (official city press release)')),
  'Code section number not verified (ordinance text not retrieved). Extraction only – no addresses.')

NEG('SA-DEP-00','Santa Ana, CA','city','security_deposits',
    'No Santa Ana ordinance regulates security deposits; Cal. Civ. Code § 1950.5 governs.',
    'none (state Civ. Code § 1950.5 governs)', ['S-SA-01'], ['D084'], [], None, None, 0.65,
    va(('https://santa-ana.gov/departments/rent-stabilization', '2026-10-01T22:37Z', 'organisers corpus copy D084: no deposit provisions')),
    'Absence finding based on the organisers\' Santa Ana corpus only.')
NEG('SA-FEE-00','Santa Ana, CA','city','application_screening_fees',
    'No Santa Ana ordinance caps application screening fees; Cal. Civ. Code § 1950.6 governs.',
    'none (state Civ. Code § 1950.6 governs)', ['S-SA-01'], ['D084'], [], None, None, 0.65,
    va(('https://santa-ana.gov/departments/rent-stabilization', '2026-10-01T22:37Z', 'organisers corpus copy D084: no fee provisions')),
    'Absence finding based on the organisers\' Santa Ana corpus only.')
NEG('SA-SCRN-00','Santa Ana, CA','city','screening_restrictions',
    'No Santa Ana screening-restriction ordinance identified; Cal. Gov. Code § 12955 (CA-SCRN-01) governs.',
    'none (state Gov. Code § 12955 governs)', ['S-SA-01'], ['D084'], [], None, None, 0.6,
    va(('https://santa-ana.gov/departments/rent-stabilization', '2026-10-01T22:37Z', 'organisers corpus copy D084: no screening provisions')),
    'Absence finding; Santa Ana\'s full municipal code was not searched.')

R('SA-ALG-01','Santa Ana, CA','city','algorithmic_rent_setting','in_force',
  'Prohibition on anticompetitive rent-setting software – Santa Ana Ordinance No. NS-3090 (2026)',
  'Santa Ana prohibits the sale, licensing, provision and use of algorithmic rent-setting software that relies on nonpublic competitor data to set residential rents; violations carry civil penalties of up to $1,000 each.',
  'ban on sale/use of algorithmic rent-setting software',
  cov(other='Residential rental properties in Santa Ana'),
  'Software relying only on public data',
  None, '2026-03-03', None, 'Santa Ana Ordinance No. NS-3090 (code section not verified)',
  ['S-SA-03','S-SA-04','S-SA-05'], [], ['D086','D087','D002'],
  None, None, inter(note='Additional to state AB 325 (CA-ALG-01)'),
  True, 'Only secondary sources reached: PublicCEO (first reading 2026-02-17, final vote set for 2026-03-03), Voice of OC (6-0-1 vote), OCBJ, and Morgan Lewis ("Santa Ana Ordinance No. NS-3090 (effective April 2, 2026)"). Official ordinance text/city page not retrievable (Laserfiche portal requires cookies). Status in_force rests on secondary reporting.',
  False, None, 0.5,
  va(('https://www.publicceo.com/2026/02/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/', '2026-10-03T18:54Z', 'team supplementary D087 (secondary): approved 2026-02-17 first reading; final vote 2026-03-03'),
     ('https://voiceofoc.org/2026/02/santa-ana-bans-automated-rent-price-fixing/', '2026-10-03T20:11Z', 'secondary news: vote 6-0-1; up to $1,000 civil penalty per violation'),
     ('https://morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws', '2026-10-03T18:49Z', 'team supplementary D002 (secondary): "Santa Ana Ordinance No. NS-3090 (effective April 2, 2026)"'),
     ('https://publicdocs.santa-ana.org/weblink/1/doc/549791/Page1.aspx', '2026-10-03T20:11Z', 'official document portal – fetch failed (cookie wall)')),
  'effective_date null per rule 5.1/5.2 (no primary source); secondary sources give 2026-04-02. enacted_date 2026-03-03 (second reading) from PublicCEO scheduling plus OCBJ 2026-03-09 report – secondary only. quoted_span null: no official text saved.')

# ------------------------------------------------------------------ JERSEY CITY
R('JC-RENT-01','Jersey City, NJ','city','rent_increase_limits','in_force',
  'Rent Control Ordinance – Jersey City Code ch. 260 (§ 260-3)',
  'For rent-controlled dwellings, a landlord may not raise rent at lease expiry by more than the lesser of 4% or the CPI change over the lease term; buildings of one to four units are exempt, as is new construction for the statutory exemption period.',
  'lesser of 4% or CPI',
  cov(minu=5, other='Rent-controlled dwellings as defined in § 260-1; properties with 1–4 units are exempt'),
  '1–4 unit properties (per the Office of Landlord/Tenant Relations); newly constructed multiple dwellings for the N.J.S.A. 2A:42-84.1 exemption period; owner-occupied and other § 260 exemptions (not quoted)',
  None, None, None, 'Jersey City Code § 260-3',
  ['S-JC-01','S-JC-02'], ['D036'], [],
  'All 1-4 Unit Properties are exempt from rent control',
  'D036', inter(note='No state cap; nothing to supersede'),
  False, None, False, None, 0.7,
  va(('https://www.jerseycitynj.gov/landlordtenant', '2026-10-01T22:36Z', 'organisers corpus copy D036 (official): "(Please Note: All 1-4 Unit Properties are exempt from rent control)"'),
     ('https://cdnsm5-hosted.civiclive.com/UserFiles/Servers/Server_6189660/File/City%20Hall/Housing%20Economic%20Development/Tenant%20Landlord%20Relations/4.10.2024%20-%20June%202024%20CPI.pdf', '2026-10-03T20:15Z', 'official city CPI notice quoting § 260-3: "greater than four percent or the percentage difference between the consumer price index ... whichever is less"')),
  'Jersey City and Newark rows have no unit counts → the 1–4 unit exemption cannot be tested → expected result unknown for every Jersey City address (missing fact: units). The code text itself (ecode360/Municode) was not captured; the § 260-3 quote comes from an official city notice.')

NEG('JC-JUST-00','Jersey City, NJ','city','just_cause_eviction',
    'Jersey City has no local just-cause ordinance; the state Anti-Eviction Act (NJ-JUST-01) governs.',
    'none (N.J.S.A. 2A:18-61.1 governs)', ['S-JC-01'], ['D036'], [], None, None, 0.7,
    va(('https://www.jerseycitynj.gov/landlordtenant', '2026-10-01T22:36Z', 'organisers corpus copy D036: no just-cause ordinance referenced')),
    'Absence finding based on the organisers\' Jersey City corpus.')
NEG('JC-DEP-00','Jersey City, NJ','city','security_deposits',
    'No Jersey City deposit ordinance; N.J.S.A. 46:8-21.2 (NJ-DEP-01) governs.',
    'none (N.J.S.A. 46:8-21.2 governs)', ['S-JC-01'], ['D036'], [], None, None, 0.7,
    va(('https://www.jerseycitynj.gov/landlordtenant', '2026-10-01T22:36Z', 'organisers corpus copy D036')), 'Absence finding.')
NEG('JC-FEE-00','Jersey City, NJ','city','application_screening_fees',
    'No Jersey City application-fee ordinance; N.J.S.A. 46:8-18.1 (NJ-FEE-01) governs.',
    'none (N.J.S.A. 46:8-18.1 governs)', ['S-JC-01'], ['D036'], [], None, None, 0.7,
    va(('https://www.jerseycitynj.gov/landlordtenant', '2026-10-01T22:36Z', 'organisers corpus copy D036')), 'Absence finding.')
NEG('JC-SCRN-00','Jersey City, NJ','city','screening_restrictions',
    'No Jersey City screening-restriction ordinance identified; the NJ Fair Chance in Housing Act and LAD (NJ-SCRN-01/02) govern.',
    'none (N.J.S.A. 46:8-52 et seq.; 10:5-12 govern)', ['S-JC-01'], ['D036'], [], None, None, 0.6,
    va(('https://www.jerseycitynj.gov/landlordtenant', '2026-10-01T22:36Z', 'organisers corpus copy D036')), 'Absence finding; Jersey City code not searched exhaustively.')

R('JC-ALG-01','Jersey City, NJ','city','algorithmic_rent_setting','in_force',
  'Ban on algorithmic rent-setting using nonpublic competitor data – Jersey City Code § 218-12 (Ord. 25-057)',
  'Landlords in Jersey City may not use rent-setting software or algorithms that process nonpublic competitor information to set or recommend rents; single owners coordinating only their own properties and licensed real-estate agents are excluded.',
  'ban on landlord use of algorithmic rent-setting with nonpublic competitor data',
  cov(other='Residential rental properties in Jersey City'),
  'Pricing across multiple properties under a single owner; licensed real estate agents',
  '2025-06', '2025-05-21', None, 'Jersey City Code § 218-12 (Ord. 25-057)',
  ['S-JC-03','S-JC-04','S-JC-05'], [], ['D035','D037'],
  None, None, inter(yields_to=[], note='Possible preemption by the NJ FAIR Act from 2027-07-01 (P.L.2026 c.43 § 6(b)) – conflict_flag per organisers (T3); FAIR Act not yet effective'),
  True, 'NJ FAIR Act may preempt this ordinance once effective (2027-07-01); organisers list this as an open question (README § 9) and require conflict flags on Jersey City addresses in T3. Effective date only at month precision (NJ ordinances take effect 20 days after final passage/publication; Morgan Lewis: "effective June 2025").',
  False, None, 0.6,
  va(('https://hudsoncountyview.com/jersey-city-council-approves-realpage-ban-and-increasing-benefits-for-laborers/', '2026-10-03T18:51Z', 'team supplementary D035 (secondary news, 2025-05-22): council passed 9-0 on 2025-05-21'),
     ('https://www.insidernj.com/press-release/jersey-city-council-advances-ordinances-that-ban-ai-powered-rent-fixing-algorithms/', '2026-10-03T20:14Z', 'secondary press release: Ordinance 25-057; first reading 2025-05-08'),
     ('https://www.morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws', '2026-10-03T18:51Z', 'team supplementary D037 (secondary): "Jersey City Code § 218-12 (effective June 2025)"'),
     ('https://cityofjerseycity.civicweb.net/document/436629/Ordinance%20Amending%20Chapter%20218%20Section%2012.pdf', '2026-10-03T20:15Z', 'official ordinance PDF ("Ordinance Amending Chapter 218 Section 12") – robots.txt disallowed fetch; title corroborates § 218-12')),
  'quoted_span null: no official text saved (civicweb PDF blocked). Change test T2: applies only to Jersey City addresses; never to Newark or Hoboken.')

# ------------------------------------------------------------------ HOBOKEN
R('HOB-RENT-01','Hoboken, NJ','city','rent_increase_limits','in_force',
  'Rent Control – Hoboken Code ch. 155 (§ 155-5)',
  'At lease expiry a Hoboken landlord may not raise rent by more than the lesser of 5% or the CPI change over the lease term; one increase per 12 months. Hotels, new construction (post-1987 multiple dwellings for the statutory exemption period) and a few other categories are exempt; there is no small-building or owner-occupancy exemption.',
  'lesser of 5% or CPI per 12 months',
  cov(other='All dwellings rented in Hoboken except § 155-2 exemptions (no unit-count or owner-occupancy exemption)'),
  'Motels/hotels; newly constructed dwellings on first rental (registered); industrial/commercial property; institutional student housing; government-owned housing; buildings vacant since 1984-01-01; multiple dwellings constructed after 1987-06-25 for the mortgage-amortisation/30-year period under N.J.S.A. 2A:42-84.1 et seq.',
  None, '1984-01-16', None, 'Hoboken Code § 155-5',
  ['S-HOB-01','S-HOB-02','S-HOB-03'], [], ['D032','D033'],
  'no landlord may request or receive a percentage increase in rent which is greater than 5% or the percentage difference between the consumer price index three months prior to the expiration or termination of the lease and three months prior to the commencement of the lease term, whichever is less.',
  'D033', inter(note='No state cap; nothing to supersede. Ch. 158 (Ord. B-750, 2025-04-02) adds disclosure duties for increases over 10% – see open_questions'),
  False, None, False, None, 0.8,
  va(('https://ecode360.com/15252470', '2026-10-03T18:51Z', 'team supplementary capture D033 (code publisher, Article II): § 155-5 text'),
     ('https://ecode360.com/15252438', '2026-10-03T19:02Z', 'team supplementary D032: chapter history "Adopted ... 1-16-1984 by Ord. No. C329"'),
     ('https://ecode360.com/15252441', '2026-10-03T20:16Z', 'code publisher § 155-2 exemptions (single page read): hotels, new construction, post-1987-06-25 multiple dwellings, etc.')),
  'NJ construction years are mostly missing and 39/40 Hoboken rows lack units → new-construction exemption untestable → unknown unless year_built shows pre-1987 construction (then applies). ecode360 Terms of Use acknowledged; single pages only.')

NEG('HOB-JUST-00','Hoboken, NJ','city','just_cause_eviction',
    'Hoboken has no local just-cause ordinance; the state Anti-Eviction Act (NJ-JUST-01) governs.',
    'none (N.J.S.A. 2A:18-61.1 governs)', ['S-HOB-01'], [], ['D032'], None, None, 0.7,
    va(('https://ecode360.com/15252438', '2026-10-03T19:02Z', 'team supplementary D032: ch. 155 index shows rent-control provisions only')), 'Absence finding.')
NEG('HOB-DEP-00','Hoboken, NJ','city','security_deposits',
    'No Hoboken deposit ordinance; N.J.S.A. 46:8-21.2 (NJ-DEP-01) governs.',
    'none (N.J.S.A. 46:8-21.2 governs)', ['S-HOB-01'], [], ['D032'], None, None, 0.7,
    va(('https://ecode360.com/15252438', '2026-10-03T19:02Z', 'team supplementary D032')), 'Absence finding.')
NEG('HOB-FEE-00','Hoboken, NJ','city','application_screening_fees',
    'No Hoboken application-fee ordinance; N.J.S.A. 46:8-18.1 (NJ-FEE-01) governs.',
    'none (N.J.S.A. 46:8-18.1 governs)', ['S-HOB-01'], [], ['D032'], None, None, 0.7,
    va(('https://ecode360.com/15252438', '2026-10-03T19:02Z', 'team supplementary D032')), 'Absence finding.')
NEG('HOB-SCRN-00','Hoboken, NJ','city','screening_restrictions',
    'No Hoboken screening-restriction ordinance identified; NJ Fair Chance in Housing Act and LAD govern.',
    'none (N.J.S.A. 46:8-52 et seq.; 10:5-12 govern)', ['S-HOB-01'], [], ['D032'], None, None, 0.6,
    va(('https://ecode360.com/15252438', '2026-10-03T19:02Z', 'team supplementary D032')), 'Absence finding; Hoboken code not searched exhaustively.')

R('HOB-ALG-01','Hoboken, NJ','city','algorithmic_rent_setting','in_force',
  'Prohibition on price fixing using algorithmic pricing – Hoboken Code ch. 158 (Ord. B-781)',
  'Landlords renting any residential dwelling unit in Hoboken may not use software, algorithms or data-sharing platforms that analyse nonpublic competitor information (less than 365 days old) to coordinate, recommend or implement rents, lease terms or occupancy levels; penalties include fines up to $2,000 and community service.',
  'ban on algorithmic price fixing using nonpublic competitor information',
  cov(other='All residential dwelling units in Hoboken (primary residences)'),
  'Medical/long-term care and detention facilities; information more than 365 days old or publicly available at no cost',
  '2025-07', '2025-07-09', None, 'Hoboken Code ch. 158 (Ord. No. B-781, adopted 2025-07-09)',
  ['S-HOB-04','S-HOB-05'], [], ['D034','D002'],
  'Landlords who rent any residential dwelling unit (defined as any primary residence excluding medical/long-term care or detention facilities) in the City of Hoboken are prohibited from price fixing using algorithmic pricing.',
  'D034', inter(note='Possible preemption by the NJ FAIR Act from 2027-07-01 (P.L.2026 c.43 § 6(b)) – conflict_flag per organisers (T3)'),
  True, 'NJ FAIR Act may preempt this ordinance once effective (organisers\' open question; T3 conflict flags for Hoboken addresses). Effective date at month precision: adopted 2025-07-09; NJ ordinances take effect ~20 days after final passage and publication; Morgan Lewis gives "effective July 2025".',
  False, None, 0.75,
  va(('https://ecode360.com/46833413', '2026-10-03T18:51Z', 'team supplementary capture D034 (code publisher): "[Adopted 7-9-2025 by Ord. No. B-781]" and prohibition text'),
     ('https://www.morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws', '2026-10-03T18:49Z', 'team supplementary D002 (secondary): "Hoboken City Code, ch. 158-2 (effective July 2025)"'),
     ('https://www.hobokengirl.com/hbooken-rent-setting-algorithm-prohibit/', '2026-10-03T20:16Z', 'secondary news: council vote 2025-07-09')),
  'Change test T2: applies only to Hoboken addresses; never to Jersey City or Newark.')

# ------------------------------------------------------------------ NEWARK
R('NWK-RENT-01','Newark, NJ','city','rent_increase_limits','in_force',
  'Rent Control – Newark Code Title XIX, § 19:2-3.1',
  'For multiple dwellings subject to Newark rent control, the annual rent increase at lease expiry may not exceed the CPI change (15 months to 3 months before the increase) and in no case 4%; increases require substantial code compliance and registration.',
  'CPI change, capped at 4% per 12 months',
  cov(minu=1, other='All multiple dwellings (buildings with one or more rented apartments) except the listed exemptions'),
  'Public housing; transient hotels/motels; commercial space; newly constructed multiple dwellings (exempt for the initial-mortgage amortisation period or 30 years, whichever less) and vacant dwellings under §§ 19:2-18.1/18.2; federally/state rehabilitated Section 8 units; units under government rent regulation contracts',
  None, '2017-09-05', None, 'Newark Code § 19:2-3.1 (Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord. No. 6PSF-I)',
  ['S-NWK-01'], [], ['D070'],
  'In no case shall the allowable rent increase exceed 4%.',
  'D070', inter(note='No state cap; nothing to supersede'),
  False, None, False, None, 0.8,
  va(('https://ecode360.com/36623772', '2026-10-03T18:53Z', 'team supplementary capture D070 (code publisher): § 19:2-3.1 text and history; § 19:2-2.1 applicability; EXEMPTIONS definition; § 19:2-18.1 new construction')),
  'Newark rows have no units and few construction years → new-construction exemption untestable → unknown unless year_built shows older construction (then applies). effective_date null: chapter re-enacted 2017-09-05 and amended 2024-09-18 (dates of the current text); original rent control is older.')

NEG('NWK-JUST-00','Newark, NJ','city','just_cause_eviction',
    'Newark has no local just-cause ordinance; the state Anti-Eviction Act (NJ-JUST-01) governs.',
    'none (N.J.S.A. 2A:18-61.1 governs)', ['S-NWK-01'], [], ['D070'], None, None, 0.7,
    va(('https://ecode360.com/36623772', '2026-10-03T18:53Z', 'team supplementary D070: rent control chapter only')), 'Absence finding.')
NEG('NWK-DEP-00','Newark, NJ','city','security_deposits',
    'No Newark deposit ordinance; N.J.S.A. 46:8-21.2 (NJ-DEP-01) governs.',
    'none (N.J.S.A. 46:8-21.2 governs)', ['S-NWK-01'], [], ['D070'], None, None, 0.7,
    va(('https://ecode360.com/36623772', '2026-10-03T18:53Z', 'team supplementary D070')), 'Absence finding.')
NEG('NWK-FEE-00','Newark, NJ','city','application_screening_fees',
    'No Newark application-fee ordinance; N.J.S.A. 46:8-18.1 (NJ-FEE-01) governs.',
    'none (N.J.S.A. 46:8-18.1 governs)', ['S-NWK-01'], [], ['D070'], None, None, 0.7,
    va(('https://ecode360.com/36623772', '2026-10-03T18:53Z', 'team supplementary D070')), 'Absence finding.')

R('NWK-SCRN-01','Newark, NJ','city','screening_restrictions','in_force',
  'Ban the Box – housing (criminal record check practices) – Newark Code Title II, ch. 2:31, art. 1',
  'In connection with any rental, a Newark landlord or broker may not inquire into criminal history before determining the applicant otherwise qualified, may consider only limited recent records, and must give notice and an opportunity to present rehabilitation evidence before denying housing on that basis.',
  'criminal-record inquiry limited to post-qualification stage; individualised review',
  cov(other='Rentals of real property in Newark except owner-occupied two-family dwellings and rooms in owner-occupied one-family homes'),
  'A single apartment in an owner-occupied two-family dwelling; rooms rented by the owner-occupant of a one-family dwelling; properties in government programmes for individuals with criminal histories',
  None, '2015-04-15', None, 'Newark Code § 2:31-2 (Ord. 6 PSF-B, 4-15-2015)',
  ['S-NWK-02'], [], ['D072'],
  'A landlord or real estate broker may hold a housing unit open until an applicant provides information about rehabilitation, but a landlord or real estate broker is not required to hold a housing unit after making an initial determination of an applicant\'s eligibility.',
  'D072', inter(note='Operates alongside the NJ Fair Chance in Housing Act (NJ-SCRN-01), which is stricter on timing'),
  False, None, False, None, 0.7,
  va(('https://ecode360.com/36642000', '2026-10-03T18:53Z', 'team supplementary capture D072 (code publisher): Article 1 Housing, Ord. 6 PSF-B, 4-15-2015')),
  'effective_date null (adoption 2015-04-15 known; effective date not stated). Owner-occupancy exemptions cannot be resolved from the data.')

NEG('NWK-ALG-00','Newark, NJ','city','algorithmic_rent_setting',
    'Newark has no local algorithmic rent-setting ordinance; the state FAIR Act (NJ-ALG-01, not yet effective) is the only rule. Change test T2 requires that neither the Hoboken nor the Jersey City ban applies to Newark addresses.',
    'none (NJ FAIR Act P.L.2026 c.43 from 2027-07-01)', ['S-NWK-01'], [], ['D070','D002'], None, None, 0.75,
    va(('https://www.morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws', '2026-10-03T18:49Z', 'team supplementary D002 (secondary, Aug 2026 survey) lists Jersey City and Hoboken but no Newark ordinance'),
       ('https://ecode360.com/36623772', '2026-10-03T18:53Z', 'team supplementary D070: no algorithmic provision in the rent control chapter')),
    'Absence finding consistent with organisers\' T2 expected behaviour.')

# ------------------------------------------------------------------ BOSTON
NEG('BOS-RENT-00','Boston, MA','city','rent_increase_limits',
    'Boston may not enact rent control (M.G.L. c.40P, § 4); its 2023 home-rule petition H.3744 was sent to study on 2024-09-09 (see BOS-RENT-P1). No rent cap applies to Boston addresses.',
    'M.G.L. c.40P, § 4; Mass. H.3744 (193rd) – study order', ['S-MA-01','S-BOS-01'], ['D048','D011'], [],
    'that the city of Boston be authorized to implement rent stabilization and tenant eviction protections', 'D011', 0.9,
    va(('https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40P/Section4', '2026-10-01T22:36Z', 'organisers corpus copy D048 (official)'),
       ('https://malegislature.gov/Bills/193/H3744', '2026-10-01T22:35Z', 'organisers corpus copy D011 (official): "9/9/2024 House Accompanied a study order, see H5035"')),
    'Change test T5: never report a rent cap in Boston.')

R('BOS-RENT-P1','Boston, MA','city','rent_increase_limits','failed',
  'H.3744 – Boston home-rule petition for rent stabilization and eviction protections (died in study)',
  'Boston\'s 2023 home-rule petition asking the Legislature to authorise rent stabilization and tenant eviction protections was accompanied by a study order on 2024-09-09 at the end of the 193rd General Court and never became law.',
  None, cov(other='Would have applied to Boston if enacted; never in force'),
  None, None, '2023-04-10', None, 'Mass. H.3744 (193rd General Court) – study order H.5035 (2024-09-09)',
  ['S-BOS-01'], ['D011'], [],
  'An Act petition for a special law authorizing the city of Boston to implement rent stabilization and tenant eviction protections',
  'D011', inter(),
  False, None, False, None, 0.8,
  va(('https://malegislature.gov/Bills/193/H3744', '2026-10-01T22:35Z', 'organisers corpus copy D011 (official bill history)')),
  'Status "failed" because a study order at the close of the session ends the bill; Hamza may prefer "pending" if a refiled petition exists in the 194th General Court (not checked).')

R('BOS-JUST-01','Boston, MA','city','just_cause_eviction','in_force',
  'Housing Stability Notification Act (notice of tenants\' rights on termination) – Boston Ordinance (2020)',
  'Any landlord ending a Boston tenancy (notice to quit or non-renewal) must give the tenant the City\'s Notice of Tenants\' Rights and Resources at the same time and file a copy with the Office of Housing Stability; it does not itself require just cause.',
  'notice-of-rights duty on termination (no just-cause requirement)',
  cov(other='All landlords in Boston ending a tenancy; foreclosing owners'),
  None, '2020-11-06', '2020-10', None, 'Boston Code of Ordinances ch. 9, § 9-20 (Housing Stability Notification Act)',
  ['S-BOS-02','S-BOS-03'], ['D013','D014'], [],
  'The Housing Stability Notification Act requires any landlord to provide renters with a Notice of Tenant’s Rights and Resources when planning to end a tenancy agreement.',
  'D013', inter(note='Does not displace state notice rules (M.G.L. c.186 §§ 11, 12); MA has no just-cause statute'),
  True, 'Borderline categorisation: a notice-of-rights duty, not a just-cause rule. Alternative is a negative finding (BOS-JUST-00: no just-cause rule at city level). Decision reserved for Hamza (open_questions.md).',
  False, None, 0.6,
  va(('https://www.boston.gov/housing-stability-notification-act', '2026-10-01T22:35Z', 'organisers corpus copy D013 (official)'),
     ('https://www.boston.gov/sites/default/files/file/2020/11/Housing%20Stability%20Notification%20Act%20Tenant%20FAQs.pdf', '2026-10-01T22:35Z', 'organisers corpus copy D014 (official FAQ): "The HSNA becomes effective on November 6, 2020"; passed October 2020')),
  'Code section (ch. 9, § 9-20) from general knowledge – Hamza to confirm.')

NEG('BOS-DEP-00','Boston, MA','city','security_deposits',
    'No Boston deposit ordinance; M.G.L. c.186, § 15B (MA-DEP-01) governs.',
    'none (M.G.L. c.186 § 15B governs)', ['S-BOS-02'], ['D013'], [], None, None, 0.75,
    va(('https://www.boston.gov/housing-stability-notification-act', '2026-10-01T22:35Z', 'organisers corpus copy D013 – no deposit provisions in the Boston corpus')), 'Absence finding.')
NEG('BOS-FEE-00','Boston, MA','city','application_screening_fees',
    'No Boston application-fee ordinance; M.G.L. c.186, § 15B (MA-FEE-01) governs.',
    'none (M.G.L. c.186 § 15B governs)', ['S-BOS-02'], ['D013'], [], None, None, 0.75,
    va(('https://www.boston.gov/housing-stability-notification-act', '2026-10-01T22:35Z', 'organisers corpus copy D013')), 'Absence finding.')

R('BOS-SCRN-01','Boston, MA','city','screening_restrictions','in_force',
  'Boston Fair Chance Tenant Selection Policy (DND-funded and IDP housing) – Feb 2017',
  'Housing providers that receive Department of Neighborhood Development funding or land, or have income-restricted units under the BPDA Inclusionary Development Policy, may not impose blanket criminal-history bans and must disregard non-convictions, sealed/expunged records, juvenile records and convictions over five years old, assessing applicants case by case.',
  'no blanket criminal-history denials; 5-year look-back (city-funded/IDP housing)',
  cov(other='Housing providers receiving DND funding/land or with BPDA Inclusionary Development Policy units; not market-rate private landlords generally'),
  'Market-rate housing without DND funding or IDP units; where federal/state law imposes a conflicting criminal-history requirement',
  '2017-02', None, None, 'Boston Fair Chance Tenant Selection Policy (DND, February 2017) – policy, not ordinance',
  ['S-BOS-04','S-BOS-05'], ['D010','D012'], [],
  'Housing providers receiving Department of Neighborhood Development (DND) funding and/or \nland, or that have income restricted units created under the Boston Planning and Development \nAgency (BPDA) Inclusionary Development Policy will not impose a blanket policy that denies \nhousing to anyone with arrests and or convictions.',
  'D010', inter(note='Boston Fair Housing Commission also enforces local/state fair housing law (D012); M.G.L. c.151B § 4(10) applies statewide'),
  True, 'Borderline: a funding-conditioned policy, not legislation; coverage (DND funding/IDP units) is not in the address data → unknown. Alternative is a negative finding. Decision reserved for Hamza.',
  False, None, 0.55,
  va(('https://drive.google.com/file/d/1j4U3fDtmnYuwcUWhx5BMUcXc1bnKT8Ku/view?usp=sharing', '2026-10-01T22:44Z', 'organisers corpus copy D010 (official city-linked policy document, Feb 2017)'),
     ('https://www.boston.gov/departments/fair-housing-and-equity/boston-fair-housing-regulations', '2026-10-01T22:35Z', 'organisers corpus copy D012 (official Fair Housing Commission page)')),
  'effective_date at month precision from the document header "(February 2017)".')

NEG('BOS-ALG-00','Boston, MA','city','algorithmic_rent_setting',
    'Boston has no local algorithmic rent-setting ordinance; the only Massachusetts measures are the pending state bills S.2983/H.5222 (MA-ALG-P1/P2).',
    'none (MA bills S.2983/H.5222 pending)', ['S-MA-08','S-MA-09'], ['D046','D045'], [], None, None, 0.75,
    va(('https://malegislature.gov/Bills/194/S2983', '2026-10-01T22:36Z', 'organisers corpus copy D046: state bill pending; no Boston ordinance in the corpus')), 'Absence finding; Boston Code not searched exhaustively.')

# ------------------------------------------------------------------ CAMBRIDGE
NEG('CAM-RENT-00','Cambridge, MA','city','rent_increase_limits',
    'Cambridge may not enact rent control (M.G.L. c.40P, § 4); no rent cap applies to Cambridge addresses (T5).',
    'M.G.L. c.40P, § 4', ['S-MA-01'], ['D048'], [],
    'No city or town may enact, maintain or enforce rent control of any kind', 'D048', 0.9,
    va(('https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40P/Section4', '2026-10-01T22:36Z', 'organisers corpus copy D048 (official)')),
    'Change test T5: never report a rent cap in Cambridge.')

R('CAM-JUST-01','Cambridge, MA','city','just_cause_eviction','in_force',
  'Tenants\' Rights and Resources Notification Ordinance – Cambridge Mun. Code ch. 8.71',
  'Cambridge landlords must give every tenant the City\'s Tenants\' Rights and Resources guide at the start of a tenancy and again when taking legal steps to terminate it (e.g., notice to quit); it does not itself require just cause. Violations: $300 per day.',
  'notice-of-rights duty at tenancy start and termination (no just-cause requirement)',
  cov(other='All residential rental agreements in Cambridge, including single units'),
  'Rental units in hospitals, skilled nursing or health facilities, short-term substance-abuse treatment facilities; short-term rental units under Zoning § 4.60',
  None, None, None, 'Cambridge Mun. Code ch. 8.71',
  ['S-CAM-01'], ['D031'], [],
  'The Ordinance requires owners, landlords, and management companies to provide you with information at the start of your lease or tenancy as well as when your tenancy is being terminated.',
  'D031', inter(note='MA has no just-cause statute; state notice rules (c.186 §§ 11, 12) continue to apply'),
  True, 'Borderline categorisation (notice duty, not just cause) – same issue as BOS-JUST-01; alternative is a negative finding CAM-JUST-00. Decision reserved for Hamza.',
  False, None, 0.6,
  va(('https://www.cambridgema.gov/tenantrights', '2026-10-01T22:36Z', 'organisers corpus copy D031 (official city page)')),
  'effective_date null (ordinance date not verified).')

NEG('CAM-DEP-00','Cambridge, MA','city','security_deposits',
    'No Cambridge deposit ordinance; M.G.L. c.186, § 15B (MA-DEP-01) governs.',
    'none (M.G.L. c.186 § 15B governs)', ['S-CAM-01'], ['D031'], [], None, None, 0.75,
    va(('https://www.cambridgema.gov/tenantrights', '2026-10-01T22:36Z', 'organisers corpus copy D031')), 'Absence finding.')
NEG('CAM-FEE-00','Cambridge, MA','city','application_screening_fees',
    'No Cambridge application-fee ordinance; M.G.L. c.186, § 15B (MA-FEE-01) governs.',
    'none (M.G.L. c.186 § 15B governs)', ['S-CAM-01'], ['D031'], [], None, None, 0.75,
    va(('https://www.cambridgema.gov/tenantrights', '2026-10-01T22:36Z', 'organisers corpus copy D031')), 'Absence finding.')

R('CAM-SCRN-01','Cambridge, MA','city','screening_restrictions','in_force',
  'Cambridge Fair Housing Ordinance – source of income protection – Cambridge Mun. Code ch. 14.04',
  'The Cambridge Fair Housing Ordinance, enforced by the Cambridge Human Rights Commission, prohibits housing discrimination based on protected categories including source of income (Section 8 and public benefits).',
  'source of income (incl. Section 8) protected locally',
  cov(other='Real estate transactions in Cambridge'),
  None, None, None, None, 'Cambridge Mun. Code ch. 14.04',
  ['S-CAM-02'], ['D029'], [],
  'Source of Income, includes Section 8 and public benefits',
  'D029', inter(note='Operates alongside M.G.L. c.151B § 4(10) (MA-SCRN-01)'),
  False, None, False, None, 0.7,
  va(('https://www.cambridgema.gov/departments/humanrightscommission', '2026-10-01T22:36Z', 'organisers corpus copy D029 (official city page): protected categories list')),
  'effective_date null (1984 commission; ordinance dates not verified).')

NEG('CAM-ALG-00','Cambridge, MA','city','algorithmic_rent_setting',
    'Cambridge has no algorithmic rent-setting ordinance; on 2026-06-22 the City Council passed only a policy order asking the City Manager to draft options. The pending state bills (MA-ALG-P1/P2) are the only measures.',
    'none (policy order June 2026; MA bills pending)', ['S-CAM-03'], [], ['D030'],
    'City council also unanimously passed a policy order initiating steps to ban residential property management companies from contracting companies that use algorithmic and AI-driven models to recommend what they should charge for rent.', 'D030', 0.7,
    va(('https://www.cambridgeday.com/?p=158097', '2026-10-03T18:50Z', 'team supplementary D030 (secondary news, 2026-06-25): policy order only; "draft policy options or ordinance language ... later this term"')),
    'A policy order is not a bill/proposal with text, so status is recorded as a negative finding rather than pending; Hamza may prefer CAM-ALG-P1 pending.',
    conflict_flag=True, conflict_note='Negative finding vs pending: Cambridge policy order (June 2026) directs drafting of an ordinance; no ordinance text exists.')

# ------------------------------------------------------------------ verification
def verify():
    bad = []
    for r in RULES:
        span = r['quoted_span']; doc = r.pop('_span_doc')
        if span is None:
            r['quoted_span_in_corpus'] = False
            continue
        t, where = text(doc)
        if t is None or span not in t:
            bad.append((r['gold_id'], doc, span[:60])); continue
        # in organisers corpus?
        ct, cw = text(doc) if where == 'corpus' else (None, None)
        in_corpus = False
        for d in r['corpus_doc_ids']:
            tt, _ = text(d)
            if tt and span in tt: in_corpus = True
        r['quoted_span_in_corpus'] = in_corpus
        if len(span) < 20: bad.append((r['gold_id'], doc, 'span <20 chars'))
    return bad

if __name__ == '__main__':
    bad = verify()
    if bad:
        print('SPAN FAILURES:'); [print(' ', b) for b in bad]; sys.exit(1)
    ids = [r['gold_id'] for r in RULES]
    assert len(ids) == len(set(ids)), 'duplicate gold_id'
    import jsonschema
    schema = json.load(open(f'{OUT}/gold/schema/gold_rule.schema.json'))
    for r in RULES:
        jsonschema.validate(r, schema)
    os.makedirs(f'{OUT}/gold/rules', exist_ok=True)
    json.dump(RULES, open(f'{OUT}/gold/rules/all.json', 'w'), indent=1, ensure_ascii=False)
    print('rules:', len(RULES), 'negative:', sum(r['negative_finding'] for r in RULES),
          'spans in corpus:', sum(r['quoted_span_in_corpus'] for r in RULES),
          'null spans:', sum(r['quoted_span'] is None for r in RULES))
    from collections import Counter
    print(Counter(r['status'] for r in RULES))
    print(Counter((r['jurisdiction'] if r['level']=='state' else r['jurisdiction'].split(',')[1].strip()) for r in RULES))
