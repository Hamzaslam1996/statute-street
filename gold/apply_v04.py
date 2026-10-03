#!/usr/bin/env python3
"""v0.4 — apply instructions/lawyer_review_01..04.md (Hamza, 2026-10-04)."""
import json, csv, os, re, hashlib, random, collections, copy
from collections import OrderedDict
OUT='/mnt/user-data/outputs/navigator'; ROOT='/home/claude/ss'
NOW='2026-10-03T22:45Z'; DEC='Lawyer review (Hamza, 2026-10-04)'
def norm(s): return re.sub(r'\s+',' ',s).strip()
def rd(p): return open(p,encoding='utf-8').read()
def text(doc):
    for fo in ('corpus','supp'):
        p=f'{ROOT}/{fo}/{doc}.txt'
        if os.path.exists(p): return rd(p)
MAN={os.path.basename(p):rd(p) for p in __import__('glob').glob(f'{ROOT}/manual/*.txt')}
def raw_span(t,target):
    """exact raw substring of t whose whitespace-normalised form equals norm(target)."""
    if target in t: return target
    k=norm(target); words=[re.escape(w) for w in k.split(' ')]
    m=re.search(r'\s+'.join(words),t)
    assert m, 'span not found: '+k[:60]
    return m.group(0)
R=json.load(open(f'{OUT}/gold/rules/all.json')); I={r['gold_id']:r for r in R}
LOG=[]; n0=len(list(csv.DictReader(open(f'{OUT}/gold/adjudication_log.csv'))))
def log(gid,field,old,new,src,why):
    LOG.append(OrderedDict(log_id=f'L{n0+len(LOG)+1:03d}',gold_id=gid,field=field,independent_value=str(new)[:300],silver_value=f'previous: {str(old)[:200]}',primary_source_url=src,recommendation='apply',reason=why,decided_by='Hamza',decision='applied per lawyer_review (2026-10-04)',decided_at=NOW))
def setf(r,field,val,src,why):
    old=r.get(field)
    if old!=val: r[field]=val; log(r['gold_id'],field,old,val,src,why)
def addsrc(r,*sids):
    for s in sids:
        if s not in r['source_ids']: r['source_ids'].append(s)
def addsupp(r,*d):
    for x in d:
        if x not in r['supplementary_doc_ids']: r['supplementary_doc_ids'].append(x)
def va(r,url,chk,res):
    if not any(v['url']==url for v in r['verified_against']): r['verified_against'].append(OrderedDict(url=url,checked_at_utc=chk,result=res))
def span(r,file_text,target,src,why,doc_label):
    s=raw_span(file_text,target); setf(r,'quoted_span',s,src,why+f' [span from {doc_label}]'); r['quote_verified']=True
def note(r,s): r['notes']=((r['notes'] or '').rstrip()+' '+s).strip()
def ver(r): r['verifier']='Hamza'

# ---- manual sources register ids
MS={'bos':'S-MAN-01','bbj':'S-MAN-02','cori':'S-MAN-03','c6':'S-MAN-04','jc':'S-MAN-05','jcad':'S-MAN-06','hob':'S-MAN-07','ca':'S-MAN-08','cella':'S-MAN-09','fee':'S-MAN-10','aga':'S-MAN-11','gov':'S-MAN-12','njpl':'S-MAN-13','lamc':'S-MAN-14'}
NEWS={'D088':'S-SA-06','D089':'S-SA-07','D090':'S-BOS-06','D091':'S-BK-10','D092':'S-BK-11','D093':'S-CA-09','D095':'S-HOB-06','D075':'S-SD-06'}
LR='instructions/lawyer_review_0{n}.md'

# ================= batch 1
r=I['BOS-SCRN-02']; f=LR.format(n=1)
setf(r,'citation','Boston Fair Chance Tenant Selection Policy (Department of Neighborhood Development, February 2017)',MS['bos'],f)
r['coverage']['other']='Housing providers receiving DND funding and/or land, or with income-restricted units created under the BPDA Inclusionary Development Policy; per Boston Bar Journal (Aug 2023) applies to all units in such a development incl. market-rate. Funding status not in the address data → Module B result unknown.'
log('BOS-SCRN-02','coverage','DND-funded only (brief)',r['coverage']['other'],MS['bbj'],f)
setf(r,'key_value','No blanket denial for arrests/convictions; may not consider arrests without conviction, sealed/expunged/relieved convictions, juvenile records, or convictions more than 5 years old (case-by-case review required)',MS['bos'],f)
span(r,MAN['BOS-SCRN-02_boston_fair_chance_policy_2017.txt'],"Housing providers receiving Department of Neighborhood Development (DND) funding and/or land, or that have income restricted units created under the Boston Planning and Development Agency (BPDA) Inclusionary Development Policy will not impose a blanket policy that denies housing to anyone with arrests and or convictions.",MS['bos'],f,'sources/manual/BOS-SCRN-02_boston_fair_chance_policy_2017.txt')
setf(r,'effective_date',None,MS['bos'],f); setf(r,'status','in_force',MS['bos'],f); r['conflict_flag']=True
r['conflict_note']='City POLICY adopted by agreement, not a codified ordinance; scope depends on DND funding / IDP status (not in data). '+DEC
setf(r,'confidence',0.7,MS['bos'],f); addsrc(r,MS['bos'],MS['bbj']); ver(r)
note(r,'Policy document dated February 2017; no effective date stated. '+DEC+' batch 1 row 1.')
va(r,'sources/manual/BOS-SCRN-02_boston_fair_chance_policy_2017.pdf','2026-10-04','manual download by Hamza (DND policy, 3 pp., footer "February 2017"); span verified against the pdftotext copy')
va(r,'sources/manual/BOS-SCRN-02_secondary_BBJ_2023.pdf','2026-10-04','secondary: Boston Bar Journal 31 Aug 2023 fn. 23 – scope incl. market-rate units in covered developments')

r=I['MA-SCRN-02']
setf(r,'citation','803 CMR 5.00 (CORI – Housing), esp. 5.04, 5.10; M.G.L. c.6, § 172(a)(3)',MS['cori'],f)
setf(r,'key_value','CORI may be requested only as the final step of the application; before asking about criminal history or making an adverse decision the landlord must give the applicant a copy of the CORI and disclose its source; look-back limited to felonies 10 years / misdemeanours 5 years after disposition (c.6 § 172(a)(3))',MS['cori'],f)
span(r,MAN['MA-SCRN-02_803_CMR_5.txt'],"Each landlord, property management company, real estate agent, or public housing authority shall provide a copy of a housing applicant's CORI or other criminal history information, and shall disclose the source of the information, to him or her: (a) before asking the applicant any questions about the criminal history; and (b) before making an adverse housing decision based on the housing applicant's CORI or other criminal history information.",MS['cori'],f,'sources/manual/MA-SCRN-02_803_CMR_5.txt')
r['coverage']['other']='Landlords, property management companies, real estate agents and public housing authorities that request CORI (803 CMR 5.01(2))'
setf(r,'effective_date',None,MS['cori'],f); setf(r,'confidence',0.8,MS['cori'],f); addsrc(r,MS['cori'],MS['c6']); ver(r)
note(r,'Regulation compiled 6/11/21; no effective date stated in the captured pages. Official malegislature.gov c.6 § 172 page could not be captured (connection timed out twice on 2026-10-03; FindLaw mirror saved instead). '+DEC+' batch 1 row 2.')
va(r,'sources/manual/MA-SCRN-02_803_CMR_5.pdf','2026-10-04','manual download by Hamza: 803 CMR 5.00 (pages dated 6/11/21); span verified against the pdftotext copy')
va(r,'https://codes.findlaw.com/ma/part-i-administration-of-the-government-ch-1-182/ma-gen-laws-ch-6-sect-172/','2026-10-04','secondary mirror of M.G.L. c.6 § 172 (manual download); look-back periods 10y felony / 5y misdemeanour')

# ================= batch 2 + batch 4 addendum (SA-ALG-01), BERK-FEE-01, BOS-JUST-01
r=I['SA-ALG-01']; f=LR.format(n=2)+' + lawyer_review_04 addendum'
setf(r,'citation','Santa Ana Ordinance No. NS-3090 (uncodified; number per challenge brief and OCBJ, not yet seen on an official page)','D088',f)
setf(r,'key_value',"Ban on sale, licensing, provision and use of algorithmic rent-setting software that uses nonpublic competitor data; tenant civil action, up to $1,000 per violation plus attorney's fees",'D088',f)
setf(r,'exemptions','Software relying solely on publicly available data, aggregate historical data, or tools used to comply with affordable-housing programme requirements','D088',f)
span(r,text('D088'),"The ordinance, which was approved on March 3, 2026 for a second reading and final vote, prohibits the sale, licensing, provision and use of certain algorithmic rent-setting software for residential rental properties.",'D088',f,'D088 (santa-ana.gov news)')
setf(r,'enacted_date','2026-03-03','D088',f); setf(r,'effective_date','2026-04','D088',f+' (addendum)'); setf(r,'status','in_force','D088',f)
r['conflict_flag']=True; r['conflict_note']='Ordinance number NS-3090 and the exact effective date have not been seen on an official page. '+DEC+' addendum: if an official agenda/ordinance PDF showing NS-3090 is supplied, raise confidence to 0.9 and clear this note.'
setf(r,'confidence',0.7,'D088',f); addsupp(r,'D088','D089'); addsrc(r,NEWS['D088'],NEWS['D089']); ver(r)
r['notes']=('Adopted 2026-03-03 per santa-ana.gov (D088/D089; D088 describes the 2026-03-03 approval as "for a second reading and final vote", so final adoption may be later in March); Santa Ana ordinances take effect 30 days after adoption (City Charter; cf. Cal. Gov. Code § 36937) → on or about 2026-04-02; the challenge brief lists "Santa Ana Ord. NS-3090 (Apr 2026)". Effective date computed from the adoption date, not stated in a saved document. '+DEC+' batch 2 row 3 + batch 4 addendum.')
va(r,'https://santa-ana.gov/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/','2026-10-03T22:34Z','official city news (team capture D088): "approved on March 3, 2026 for a second reading and final vote"; up to $1,000 per violation')
va(r,'https://santa-ana.gov/rent-stabilization-newsletter-march-2026/','2026-10-03T22:34Z','official city newsletter (team capture D089): "Approved on March 3, 2026"')

r=I['BERK-FEE-01']; f=LR.format(n=2)
setf(r,'citation','Berkeley Mun. Code §§ 13.78.010 (fee-cap disclosure duty), 13.78.016 (ban on non-refundable renewal/roommate fees) (Ord. 7697-NS § 1, 2020)','D091',f)
setf(r,'key_value','No separate local fee cap: landlord must give a written Tenant Screening Fee Rights Statement and disclose the current Cal. Civ. Code § 1950.6(b) cap; non-refundable fees to existing tenants for renewal or adding/replacing a roommate are unlawful','D091',f)
span(r,text('D091'),"It is unlawful for an owner of residential rental property or the owner's agent to charge a non-refundable fee to any existing tenant for the purpose of renewing a tenancy, in whole or in part, including any fee associated with the departure of a roommate or to request to add or replace a roommate in a pre-existing household.",'D091',f,'D091 (berkeley.municipal.codes § 13.78.016, verbatim section excerpt)')
setf(r,'effective_date','2020','D091',f); setf(r,'confidence',0.85,'D091',f); addsupp(r,'D091','D092'); addsrc(r,NEWS['D091'],NEWS['D092']); ver(r)
note(r,'Current text of §§ 13.78.010/.016 enacted by Ord. 7697-NS § 1 (2020) (code history). berkeley.municipal.codes returned HTTP 403 to the shell; section text obtained verbatim by a single-page WebFetch read and saved as D091/D092 (excerpts); Hamza supplied the identical span. '+DEC+' batch 2 row 4.')
va(r,'https://berkeley.municipal.codes/BMC/13.78.016','2026-10-03T22:36Z','code publisher (team capture D091, verbatim section): history "(Ord. 7697-NS § 1, 2020)"')
va(r,'https://berkeley.municipal.codes/BMC/13.78.010','2026-10-03T22:36Z','code publisher (team capture D092, verbatim section): history "(Ord. 7697-NS § 1, 2020; Ord. 7379-NS § 1, 2014; Ord. 7171-NS § 1 (part), 2011)"')

r=I['BOS-JUST-01']
setf(r,'citation','Boston Code of Ordinances ch. X, § 10-11 (Housing Stability Notification Act), Ord. 2020 (Docket filed 2020-10-21)','D090',f+' (corrects ch. 9 § 9-20)')
setf(r,'key_value','[notice-only] With any notice to quit or notice of lease non-renewal, landlord must serve a copy on the Office of Housing Stability and give the tenant a notice of basic housing rights and resources; no just-cause requirement','D090',f)
t90=text('D090'); i=t90.find('When a landlord or foreclosing owner serves'); j=t90.find('which shall be attached thereto.')+len('which shall be attached thereto.')
setf(r,'quoted_span',t90[i:j],'D090',f+' [span from D090 (official ordinance PDF, § 10-11.4)]'); r['quote_verified']=True
setf(r,'effective_date','2020-11-06','D090',f); setf(r,'confidence',0.8,'D090',f); addsupp(r,'D090'); addsrc(r,NEWS['D090']); ver(r)
note(r,'Ordinance text (D090): "The provisions of this ordinance shall become effective immediately."; city FAQ (D014) gives 2020-11-06. '+DEC+' batch 2 row 5.')
va(r,'https://www.boston.gov/sites/default/files/file/2021/03/Housing%20Stability%20Notification%20Act.pdf','2026-10-03T22:34Z','official ordinance PDF (team capture D090): inserts § 10-11 after § 10-10; § 10-11.4 Required Notice; "shall become effective immediately"')
va(r,'https://codelibrary.amlegal.com/codes/boston/latest/boston_ma/0-0-0-7149','2026-10-04','code publisher location of ch. X § 10-11 (per Hamza; not fetched)')

# ================= batch 3
r=I['JC-ALG-01']; f=LR.format(n=3)
setf(r,'citation','Jersey City Code § 218-12 (Preventing Algorithmic Rent Fixing in the Rental Housing Market), added by Ord. 25-057',MS['jc'],f)
setf(r,'title','Ban on contracting with algorithmic rent-coordination service providers',MS['jc'],f)
setf(r,'key_value','Unlawful for any real estate lessor (or agent/subcontractor) to subscribe to, contract with, or exchange anything of value for the services of a service provider that coordinates using nonpublic competitor information; service providers may not facilitate non-compete agreements among lessors. First violation per § 1-25; subsequent violations $100–$2,000; each day a separate violation. Private right of action; attorney\'s fees to prevailing plaintiff.',MS['jc'],f)
r['coverage']['other']='Residential dwelling units in Jersey City (primary residences; excludes inpatient medical, long-term care, detention facilities)'
setf(r,'exemptions','Owners of multiple properties acting only across their own properties; licensed real-estate agents acting within state regulations',MS['jc'],f)
span(r,MAN['JC-ALG-01_Ord_25-057_adopted.txt'],"It is unlawful for any real estate lessor, agent, or subcontractor thereof, to subscribe to, contract with, or otherwise exchange anything of value in return for the services of a Service Provider.",MS['jc'],f,'sources/manual/JC-ALG-01_Ord_25-057_adopted.txt (§ 218-12(2)(a))')
setf(r,'enacted_date','2025-05-21',MS['jc'],f); setf(r,'effective_date','2025-06',MS['jc'],f); setf(r,'confidence',0.9,MS['jc'],f); addsrc(r,MS['jc'],MS['jcad']); ver(r)
r['conflict_flag']=True; r['conflict_note']='Possible preemption by the NJ FAIR Act from 2027-07-01 (T3 conflict flag). '+DEC
note(r,'Final passage 2025-05-21; Mayor approved 2025-05-22. Ordinance states no effective date; under N.J.S.A. 40:49-2 municipal ordinances take effect 20 days after final passage and approval unless otherwise provided (≈ 2025-06-11); challenge brief lists "Jun 2025". '+DEC+' batch 3 row 8.')
va(r,'sources/manual/JC-ALG-01_Ord_25-057_adopted.pdf','2026-10-04','manual download by Hamza: city clerk\'s adopted copy of Ord. 25-057 (5 pp.); span verified against the pdftotext copy')

NJ20='Effective date at month precision: ordinance states no effective date; under N.J.S.A. 40:49-2 municipal ordinances take effect 20 days after final passage and approval unless otherwise provided.'
r=I['HOB-ALG-01']
setf(r,'citation','Hoboken Code § 158-2 (Art. II, adopted 7-9-2025 by Ord. No. B-781)',MS['hob'],f)
setf(r,'key_value','Landlords of residential dwelling units in Hoboken prohibited from price fixing using algorithmic pricing (software/algorithms/data-sharing platforms using nonpublic competitor information to coordinate, recommend or implement rents, lease terms or occupancy); enforcement by Division of Housing or any aggrieved private citizen in Municipal Court; penalties per N.J.S.A. 40:49-5, fine up to $2,000, or up to 90 days community service',MS['hob'],f)
setf(r,'enacted_date','2025-07-09',MS['hob'],f); setf(r,'effective_date','2025-07',MS['hob'],f); setf(r,'confidence',0.9,MS['hob'],f); addsrc(r,MS['hob'],NEWS['D095']); addsupp(r,'D095'); ver(r)
note(r,NJ20+' Introduction announced 2025-05-30 for the 2025-06-04 council meeting (hobokennj.gov, D095). '+DEC+' batch 3 row 7.')
va(r,'sources/manual/HOB-ALG-01_Hoboken_ch158_ecode360.pdf','2026-10-04','manual download by Hamza: full ch. 158 (ecode360 PDF dated 2026-10-03); § 158-2.A text matches D034')
va(r,'https://www.hobokennj.gov/news/city-of-hoboken-to-introduce-ordinance-prohibiting-algorithmic-rent-fixing','2026-10-03T22:34Z','official city news (team capture D095): introduction at the 2025-06-04 meeting')
r=I['HOB-RENT-02']
setf(r,'citation','Hoboken Code § 158-1 (Art. I, adopted 4-2-2025 by Ord. No. B-750)',MS['hob'],f)
setf(r,'key_value',"For renewal rent increases over 10% year over year, landlord must disclose: itemised costs; whether a rent algorithm was used; tenant's right to sue if the increase is unconscionable; Division of Housing contact details. Fine up to $1,000 per incident.",MS['hob'],f)
setf(r,'enacted_date','2025-04-02',MS['hob'],f); setf(r,'effective_date','2025-04',MS['hob'],f); setf(r,'confidence',0.9,MS['hob'],f); addsrc(r,MS['hob']); ver(r)
r['notes']=NJ20+' '+DEC+' batch 3 row 7.'
va(r,'sources/manual/HOB-ALG-01_Hoboken_ch158_ecode360.pdf','2026-10-04','manual download by Hamza: full ch. 158; § 158-1.A text matches D034')

r=I['CA-ALG-01']
setf(r,'citation','Cal. Bus. & Prof. Code § 16729 (added by Stats. 2025, ch. 338, § 1 (AB 325))','D093',f)
setf(r,'key_value',"Unlawful to use or distribute a common pricing algorithm (a) as part of a contract, combination or conspiracy in restraint of trade, or (b) to coerce another person to adopt its recommended price or commercial term; 'common pricing algorithm' = methodology used by two or more persons that uses competitor data to recommend, align, stabilize, set or otherwise influence a price or commercial term",'D093',f)
setf(r,'confidence',0.95,'D093',f); addsupp(r,'D093'); addsrc(r,NEWS['D093'],MS['ca']); ver(r)
note(r,'Official section page captured 2026-10-03 (D093) carries the history note "(Added by Stats. 2025, Ch. 338, Sec. 1. (AB 325) Effective January 1, 2026.)" — an explicitly stated effective date (rulings_04 §2B). '+DEC+' batch 3 row 6.')
va(r,'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=BPC&sectionNum=16729','2026-10-03T22:34Z','OFFICIAL leginfo section page (team capture D093; direct fetch succeeded): § 16729 text identical to the span; history note "Effective January 1, 2026."')
va(r,'sources/manual/CA-ALG-01_BPC_16729_justia.pdf','2026-10-04','manual download by Hamza (Justia mirror) – same text')

# ================= batch 4
r=I['MA-RENT-P1']; f=LR.format(n=4)
setf(r,'citation',"Cella v. Attorney General, SJC-13893 (Mass. June 23, 2026) (Initiative Petition 25-21, 'An Initiative Petition to Protect Tenants by Limiting Rent Increases')",MS['cella'],f)
setf(r,'key_value','NO RULE: petition barred from the November 2026 ballot (art. 48 excluded matter — relates to religion); no statewide rent cap exists; M.G.L. c.40P continues to prohibit rent control',MS['cella'],f)
span(r,MAN['MA-RENT-P1_Cella_v_AG_SJC-13893.txt'],"Accordingly, art. 48 bars placement of the petition on the November 2026 Statewide election ballot.",MS['cella'],f,'sources/manual/MA-RENT-P1_Cella_v_AG_SJC-13893.txt (slip op. p. 2)')
setf(r,'status','failed',MS['cella'],f); setf(r,'confidence',0.95,MS['cella'],f); addsrc(r,MS['cella']); ver(r)
note(r,'SJC-13893 argued 2026-05-06, decided 2026-06-23 (official slip opinion saved in sources/manual). '+DEC+' batch 4 row 11.')
va(r,'sources/manual/MA-RENT-P1_Cella_v_AG_SJC-13893.pdf','2026-10-04','manual download by Hamza: official SJC slip opinion; span verified against the pdftotext copy')
r=I['MA-RENT-00']; addsrc(r,MS['cella'])
note(r,'Supporting restatement in Cella v. Attorney General, SJC-13893, slip op. p. 3: General Laws c. 40P, § 2, "broadly prohibits any regulatory scheme based upon or implementing rent control." (secondary restatement; D048 remains primary). '+DEC+' batch 4 row 11.')
va(r,'sources/manual/MA-RENT-P1_Cella_v_AG_SJC-13893.pdf','2026-10-04','SJC slip opinion p. 3 restates c.40P § 2 prohibition'); log('MA-RENT-00','notes','—','added Cella v. AG supporting quote',MS['cella'],f)

r=I['MA-FEE-02']
setf(r,'confidence',0.9,MS['fee'],f); addsrc(r,MS['fee']); ver(r)
note(r,'Effective date 2025-08-01 confirmed by the stated line in the Trial Court Law Libraries text: "Amended by St. 2025, c. 9, § 43, effective August 1, 2025" (explicitly stated date; D057 official annotation agrees). '+DEC+' batch 4 row 15.')
va(r,'sources/manual/MA-FEE-02_c112_87DDD-half_masslaw.pdf','2026-10-04','manual download by Hamza (mass.gov Trial Court Law Libraries text): "effective August 1, 2025"; operative sentence identical to D057')

r=I['BERK-RENT-01']
setf(r,'key_value','AGA for 2026 is 1.0% (65% of Bay Area CPI July–June, capped at 5% under Measure BB); applies to units fully covered by the Rent Ordinance; no increase in the year the tenancy began plus one further calendar year',MS['aga'],f)
span(r,MAN['BERK-RENT-01_AGA_page.txt'],"On January 1, the rent ceilings for most units fully covered by the Rent Ordinance increase by the AGA, which allows landlords to raise rents (with proper notice) up to the new rent ceiling.",MS['aga'],f,'sources/manual/BERK-RENT-01_AGA_page.txt (official Rent Board page)')
setf(r,'effective_date','2026-01-01',MS['aga'],f+' (current key-value date, same treatment as SF-RENT-01)'); setf(r,'confidence',0.9,MS['aga'],f); addsrc(r,MS['aga']); ver(r)
note(r,'Notice: 30-day written notice for increases ≤10%, 90-day for >10% (state law). effective_date = date the 2026 AGA took effect ("On January 1, the rent ceilings ... increase by the AGA"); the ordinance itself dates from 1980. '+DEC+' batch 4 row 13.')
va(r,'sources/manual/BERK-RENT-01_AGA_page.pdf','2026-10-04','manual download by Hamza: official Rent Board AGA page: "The AGA for 2026 is 1.0%"; span verified against the pdftotext copy')

r=I['CA-SCRN-01']
setf(r,'key_value',"'Source of income' includes federal, state or local housing subsidies incl. Section 8 vouchers; discrimination based on source of income is unlawful",'D027',f)
t27=text('D027'); i=t27.find('For the purposes of this section, “source of income” means lawful, verifiable'); j=t27.find('(42 U.S.C. Sec. 1437f).',i)+len('(42 U.S.C. Sec. 1437f).')
setf(r,'quoted_span',t27[i:j],'D027',f+' [span from D027 § 12955(p)(1)]'); r['quote_verified']=True
r['conflict_flag']=False; r['conflict_note']=None; setf(r,'confidence',0.85,'D027',f); addsrc(r,MS['gov']); ver(r)
note(r,"History note in current text states only the latest amendment: 'Amended by Stats. 2023, Ch. 776, Sec. 1. (SB 267) Effective January 1, 2024.' SB 329's 2020-01-01 date is the standard 1 January effective date for a non-urgency statute chaptered 2019-10-08 (Cal. Const. art. IV, § 8(c)); not stated in the saved text. The extractor will likely return 2024-01-01 or null — accept that mismatch. "+DEC+' batch 4 row 12.')
va(r,'sources/manual/CA-SCRN-01_Gov_12955_justia.pdf','2026-10-04','manual download by Hamza (Justia mirror) – same (p)(1) text as D027')

r=I['NJ-ALG-01']; addsrc(r,MS['njpl']); ver(r)
note(r,'Corroborated by NJ State Policy Lab (27 Jul 2026): signed 20 Jul 2026 as P.L.2026, c.43; effective 1 Jul 2027. No field changes. '+DEC+' batch 4 row 9.')
va(r,'sources/manual/NJ-ALG-01_secondary_NJ_State_Policy_Lab_2026-07-27.pdf','2026-10-04','secondary (NJ State Policy Lab): signed 2026-07-20, effective 2027-07-01'); log('NJ-ALG-01','sources','—','added NJ State Policy Lab secondary',MS['njpl'],f)

r=I['LA-JUST-02']; la=MAN['LA-JUST-02_LAMC_ch15_art1_151.txt']
setf(r,'citation','L.A. Mun. Code § 151.09 (Evictions)',MS['lamc'],f)
setf(r,'key_value','Landlord may not evict from an RSO unit except on the legal grounds listed in § 151.09.A (e.g. non-payment, lease violation, nuisance, owner/family occupancy, demolition/withdrawal); relocation assistance due for no-fault evictions (§ 151.09.G)',MS['lamc'],f)
span(r,la,"A landlord may bring an action to recover possession of a rental unit only upon one of the following grounds:",MS['lamc'],f,'sources/manual/LA-JUST-02_LAMC_ch15_art1_151.txt (§ 151.09.A lead-in)')
setf(r,'effective_date',None,MS['lamc'],f); setf(r,'confidence',0.85,MS['lamc'],f); addsrc(r,MS['lamc']); ver(r)
note(r,'Ordinance history in the code text gives amendment dates only (e.g. § 151.09 "Amended by Ord. No. 154,237, Eff. 8/30/80, Oper. 9/1/80"; A.9 "Added by Ord. No. 165,251, Eff. 11/20/89") — recorded here, not as the rule\'s date. '+DEC+' batch 4 row 14.')
va(r,'sources/manual/LA-JUST-02_LAMC_ch15_art1_151.txt','2026-10-04','manual capture by Hamza of LAMC ch. XV art. 1 (American Legal); § 151.09 text; span verified')
# LA-RENT-01 / LA-DEP-01 tightened from the same official text (AI-draft; Hamza said "if clearer")
r=I['LA-RENT-01']
span(r,la,"Housing accommodations, located in a structure for which the first Certificate of Occupancy was issued after October 1, 1978, are exempt from the provisions of this chapter. If the structure was issued a Certificate of Occupancy, including a Temporary Certificate of Occupancy, on or before October 1, 1978, the housing accommodation(s) shall be subject to the provisions of this chapter.",MS['lamc'],f+' (LA-RENT-01 coverage span tightened from official LAMC § 151.02 "Rental Units" ¶6; AI-draft)','sources/manual/LA-JUST-02_LAMC_ch15_art1_151.txt (§ 151.02 Rental Units ¶6)')
addsrc(r,MS['lamc']); note(r,'Coverage span now from the official LAMC text (§ 151.02 definition of "Rental Units", exemption 6: first COO after 1978-10-01 exempt). The same text shows § 151.06 "(Amended by Ord. No. 188,795, Eff. 2/2/26.)", confirming the 2026-02-02 effective date in primary code text. Lawyer review batch 4 (row 14 note); verifier unchanged (AI-draft).')
va(r,'sources/manual/LA-JUST-02_LAMC_ch15_art1_151.txt','2026-10-04','official LAMC text (manual capture): § 151.02 Rental Units ¶6 COO cutoff; § 151.06 history "Amended by Ord. No. 188,795, Eff. 2/2/26."')
r=I['LA-DEP-01']
setf(r,'citation','L.A. Mun. Code § 151.06.02 (Payment of Interest on Security Deposits; added by Ord. No. 166,368, eff. 1990-12-06)',MS['lamc'],'LAMC official text (manual capture); AI-draft tightening')
span(r,la,"A landlord who is subject to the provisions of Section 1950.5 of the California Civil Code shall pay annually interest on all security deposits held for at",MS['lamc'],'LAMC § 151.06.02.B official text; AI-draft tightening','sources/manual/LA-JUST-02_LAMC_ch15_art1_151.txt (§ 151.06.02.B)')
setf(r,'effective_date',None,MS['lamc'],'section added by Ord. 166,368 eff. 1990-12-06; current B amended by Ord. 174,017 eff. 2001-07-16 — long-standing, Q17 null'); setf(r,'confidence',0.8,MS['lamc'],'official code text now in hand'); addsrc(r,MS['lamc'])
va(r,'sources/manual/LA-JUST-02_LAMC_ch15_art1_151.txt','2026-10-04','official LAMC text (manual capture): § 151.06.02 added by Ord. No. 166,368, Eff. 12/6/90; B amended by Ord. No. 174,017, Eff. 7/16/01')
# SD-SCRN-01: official Div. 8 PDF now captured as D075 (team re-capture 2026-10-03 21:16 UTC) — standing instruction from Hamza (2026-10-04 01:52) to add the span if present
r=I['SD-SCRN-01']; d75=text('D075')
span(r,d75,"It is unlawful for any person to do any of the following acts, wholly or in part, based on a person’s source of income",'D075','D075 re-captured from the official SDMC Division 8 PDF (docs.sandiego.gov) by the team on 2026-10-03 21:16 UTC; span added per Hamza\'s standing instruction (2026-10-04 01:52); AI-draft','D075 (official SDMC ch. 9 art. 8 div. 8 PDF, § 98.0803(a))')
va(r,'https://docs.sandiego.gov/municode/municodechapter09/ch09art08division08.pdf','2026-10-03T21:16Z','OFFICIAL SDMC Division 8 PDF (team re-capture D075): § 98.0803(a) text')
addsrc(r,NEWS['D075']); note(r,'Update 2026-10-04: D075 was re-captured by the team from the official SDMC Division 8 PDF (6,849 chars); quoted_span now taken from § 98.0803(a). The 2018-10-18 / 2019-08-01 date question is unchanged.')

# ---- re-verify every span; quoted_span_in_corpus by whitespace-normalised match
bad=[]
for r in R:
    s=r['quoted_span']
    if s is None: r['quote_verified']=False; r['quoted_span_in_corpus']=False; continue
    srcs=[text(d) for d in r['corpus_doc_ids']+r['supplementary_doc_ids']]+[MAN[m] for m in MAN if any(x in r['source_ids'] for x in MS.values()) ]
    ok=any(t and s in t for t in srcs)
    if not ok: bad.append(r['gold_id'])
    r['quote_verified']=ok
    r['quoted_span_in_corpus']=any(norm(s) in norm(text(d) or '') for d in r['corpus_doc_ids'])
assert not bad, bad
# ---- schema: quote_verified description; validate
S=json.load(open(f'{OUT}/gold/schema/gold_rule.schema.json'))
S['properties']['quote_verified']['description']='true only if quoted_span is an exact substring of a saved full source text (organisers corpus, team supplementary capture, or sources/manual pdftotext copy); false when quoted_span is null. quoted_span_in_corpus is a whitespace-normalised match against the organisers corpus/text.'
json.dump(S,open(f'{OUT}/gold/schema/gold_rule.schema.json','w'),indent=2)
import jsonschema
for r in R: jsonschema.validate(r,S)
json.dump(R,open(f'{OUT}/gold/rules/all.json','w'),indent=1,ensure_ascii=False)

# ---- adjudication log append
lp=f'{OUT}/gold/adjudication_log.csv'; rows=list(csv.DictReader(open(lp))); fn=list(rows[0].keys())
with open(lp,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows+LOG)

# ---- source register
reg=f'{OUT}/sources/source_register.csv'; rows=list(csv.DictReader(open(reg))); fn=list(rows[0].keys()); have={r['source_id'] for r in rows}
def sha_file(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest() if os.path.exists(p) else ''
ADD=[
 (MS['bos'],'Boston, MA','city','screening_restrictions','Boston Fair Chance Tenant Selection Policy (DND, Feb 2017) – manual PDF/txt','Boston Fair Chance Tenant Selection Policy (DND, February 2017)','sources/manual/BOS-SCRN-02_boston_fair_chance_policy_2017.pdf','City of Boston DND','official-agency','D010','none','2026-10-04','manual download by Hamza; pdftotext .txt alongside','BOS-SCRN-02_boston_fair_chance_policy_2017.txt'),
 (MS['bbj'],'Boston, MA','city','screening_restrictions','Boston Bar Journal (31 Aug 2023) – scope of Boston Fair Chance policy','secondary','sources/manual/BOS-SCRN-02_secondary_BBJ_2023.pdf','Boston Bar Journal','secondary-news','none','none','2026-10-04','manual download by Hamza; PDF only',''),
 (MS['cori'],'MA','state','screening_restrictions','803 CMR 5.00 CORI – Housing (manual PDF/txt)','803 CMR 5.00','sources/manual/MA-SCRN-02_803_CMR_5.pdf','Mass. DCJIS','official','D056','none','2026-10-04','manual download by Hamza (mass.gov blocked captures); pages dated 6/11/21','MA-SCRN-02_803_CMR_5.txt'),
 (MS['c6'],'MA','state','screening_restrictions','M.G.L. c.6 § 172 (FindLaw mirror; manual)','M.G.L. c.6, § 172(a)(3)','https://codes.findlaw.com/ma/part-i-administration-of-the-government-ch-1-182/ma-gen-laws-ch-6-sect-172/','FindLaw (mirror)','secondary-news','none','none','2026-10-04','official malegislature.gov page timed out twice on 2026-10-03','MA-SCRN-02_MGL_c6_s172_findlaw.txt'),
 (MS['jc'],'Jersey City, NJ','city','algorithmic_rent_setting','Jersey City Ord. 25-057 adopted copy (city clerk) – manual PDF/txt','Jersey City Code § 218-12 (Ord. 25-057)','sources/manual/JC-ALG-01_Ord_25-057_adopted.pdf','City of Jersey City (City Clerk)','official','none','none','2026-10-04','manual download by Hamza; adopted 2025-05-21, Mayor 2025-05-22','JC-ALG-01_Ord_25-057_adopted.txt'),
 (MS['jcad'],'Jersey City, NJ','city','algorithmic_rent_setting','Jersey City Ord. 25-057 first-reading legal advertisement','Ord. 25-057 (first reading)','sources/manual/JC-ALG-01_Ord_25-057_first_reading_ad.pdf','City of Jersey City','official','none','none','2026-10-04','manual download by Hamza; PDF only',''),
 (MS['hob'],'Hoboken, NJ','city','algorithmic_rent_setting','Hoboken Code ch. 158 full chapter (ecode360 PDF) – manual','Hoboken Code §§ 158-1, 158-2','sources/manual/HOB-ALG-01_Hoboken_ch158_ecode360.pdf','General Code (ecode360)','official','none','D034','2026-10-04','manual download by Hamza (PDF dated 2026-10-03)','HOB-ALG-01_Hoboken_ch158_ecode360.txt'),
 (MS['ca'],'CA','state','algorithmic_rent_setting','Cal. Bus. & Prof. Code § 16729 (Justia mirror) – manual','Cal. Bus. & Prof. Code § 16729','sources/manual/CA-ALG-01_BPC_16729_justia.pdf','Justia (mirror)','secondary-news','D022','D093','2026-10-04','manual download by Hamza; official page captured as D093','CA-ALG-01_BPC_16729_justia.txt'),
 (MS['cella'],'MA','state','rent_increase_limits','Cella v. Attorney General, SJC-13893 slip opinion – manual','Cella v. Attorney General, SJC-13893 (Mass. 2026-06-23)','sources/manual/MA-RENT-P1_Cella_v_AG_SJC-13893.pdf','Supreme Judicial Court of Massachusetts','official','none','D059','2026-10-04','manual download by Hamza','MA-RENT-P1_Cella_v_AG_SJC-13893.txt'),
 (MS['fee'],'MA','state','application_screening_fees','M.G.L. c.112 § 87DDD½ (Trial Court Law Libraries text) – manual','M.G.L. c.112, § 87DDD½','sources/manual/MA-FEE-02_c112_87DDD-half_masslaw.pdf','Mass. Trial Court Law Libraries','official-agency','D057','none','2026-10-04','manual download by Hamza; "effective August 1, 2025"','MA-FEE-02_c112_87DDD-half_masslaw.txt'),
 (MS['aga'],'Berkeley, CA','city','rent_increase_limits','Berkeley Rent Board – Annual General Adjustment page – manual','Berkeley Mun. Code § 13.76.110','sources/manual/BERK-RENT-01_AGA_page.pdf','Berkeley Rent Stabilization Board','official-agency','D008','none','2026-10-04','manual download by Hamza; "The AGA for 2026 is 1.0%"','BERK-RENT-01_AGA_page.txt'),
 (MS['gov'],'CA','state','screening_restrictions','Cal. Gov. Code § 12955 (Justia mirror) – manual','Cal. Gov. Code § 12955','sources/manual/CA-SCRN-01_Gov_12955_justia.pdf','Justia (mirror)','secondary-news','D027','D021','2026-10-04','manual download by Hamza','CA-SCRN-01_Gov_12955_justia.txt'),
 (MS['njpl'],'NJ','state','algorithmic_rent_setting','NJ State Policy Lab note on the FAIR Act (27 Jul 2026)','P.L.2026, c.43 (secondary)','sources/manual/NJ-ALG-01_secondary_NJ_State_Policy_Lab_2026-07-27.pdf','NJ State Policy Lab','secondary-news','D069','none','2026-10-04','manual download by Hamza; PDF only',''),
 (MS['lamc'],'Los Angeles, CA','city','just_cause_eviction','LAMC ch. XV art. 1 (RSO) full text incl. §§ 151.02, 151.06, 151.06.02, 151.09 – manual','L.A. Mun. Code §§ 151.02, 151.06, 151.06.02, 151.09','sources/manual/LA-JUST-02_LAMC_ch15_art1_151.txt','American Legal Publishing (via Hamza)','official','none','D038','2026-10-04','manual capture by Hamza (text only)','LA-JUST-02_LAMC_ch15_art1_151.txt'),
 (NEWS['D088'],'Santa Ana, CA','city','algorithmic_rent_setting','santa-ana.gov news: council bans anticompetitive rent-setting software','Santa Ana Ord. NS-3090 (uncodified)','https://santa-ana.gov/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/','City of Santa Ana','official','none','D088','2026-10-03T22:34Z','team capture (curl single page)','supp:D088'),
 (NEWS['D089'],'Santa Ana, CA','city','algorithmic_rent_setting','santa-ana.gov Rent Stabilization Newsletter March 2026','Santa Ana Ord. NS-3090 (uncodified)','https://santa-ana.gov/rent-stabilization-newsletter-march-2026/','City of Santa Ana','official','none','D089','2026-10-03T22:34Z','team capture: "Approved on March 3, 2026"','supp:D089'),
 (NEWS['D090'],'Boston, MA','city','just_cause_eviction','Boston HSNA ordinance text (PDF)','Boston Code ch. X, § 10-11','https://www.boston.gov/sites/default/files/file/2021/03/Housing%20Stability%20Notification%20Act.pdf','City of Boston','official','none','D090','2026-10-03T22:34Z','team capture (curl + pdftotext)','supp:D090'),
 (NEWS['D091'],'Berkeley, CA','city','application_screening_fees','BMC 13.78.016 (code publisher; verbatim section excerpt)','Berkeley Mun. Code § 13.78.016','https://berkeley.municipal.codes/BMC/13.78.016','City of Berkeley (code publisher)','official','none','D091','2026-10-03T22:36Z','curl 403; WebFetch verbatim section saved (excerpt)','supp:D091'),
 (NEWS['D092'],'Berkeley, CA','city','application_screening_fees','BMC 13.78.010 (code publisher; verbatim section excerpt)','Berkeley Mun. Code § 13.78.010','https://berkeley.municipal.codes/BMC/13.78.010','City of Berkeley (code publisher)','official','none','D092','2026-10-03T22:36Z','curl 403; WebFetch verbatim section saved (excerpt)','supp:D092'),
 (NEWS['D093'],'CA','state','algorithmic_rent_setting','Cal. Bus. & Prof. Code § 16729 (official leginfo section page)','Cal. Bus. & Prof. Code § 16729','https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=BPC&sectionNum=16729','California Legislative Information','official','none','D093','2026-10-03T22:34Z','team capture (curl single page succeeded): history note "Effective January 1, 2026."','supp:D093'),
 (NEWS['D095'],'Hoboken, NJ','city','algorithmic_rent_setting','hobokennj.gov news: city to introduce algorithmic rent-fixing ordinance (2025-05-30)','Hoboken Ord. B-781 (introduction)','https://www.hobokennj.gov/news/city-of-hoboken-to-introduce-ordinance-prohibiting-algorithmic-rent-fixing','City of Hoboken','official','none','D095','2026-10-03T22:34Z','team capture (curl single page)','supp:D095'),
 (NEWS['D075'],'San Diego, CA','city','screening_restrictions','SDMC ch. 9 art. 8 div. 8 (official PDF) – team re-capture as D075','San Diego Mun. Code §§ 98.0801–98.0803','https://docs.sandiego.gov/municode/municodechapter09/ch09art08division08.pdf','City of San Diego','official','none','D075','2026-10-03T21:16Z','team re-capture (replaces the TOC-only gocodebook capture)','supp:D075'),
]
os.makedirs(f'{OUT}/sources/official',exist_ok=True)
for sid,jur,lvl,cat,title,cite,url,pub,st,inc,ins,ret,notes,txt in ADD:
    if sid in have: continue
    if txt.startswith('supp:'): body=open(f"{ROOT}/supp/{txt[5:]}.txt",'rb').read(); origin=f'team supplementary capture {txt[5:]}'
    elif txt: body=open(f'{ROOT}/manual/{txt}','rb').read(); origin=f'copy of sources/manual/{txt} (pdftotext of the manual PDF)'
    else: body=b'(PDF only; no text extracted)'; origin='PDF in sources/manual; no text copy'
    h=hashlib.sha256(body).hexdigest()
    with open(f'{OUT}/sources/official/{sid}.txt','wb') as f:
        f.write((f'SOURCE: {url}\nRETRIEVED: {ret}\nVERIFIED_BY: Hamza (lawyer review 2026-10-04) / AI-draft registration\nSHA256: {h}\nNOTE: {origin}. Source type: {st}. Publisher: {pub}. {notes}\n---- BEGIN TEXT ----\n').encode()); f.write(body); f.write(b'\n---- END TEXT ----\n')
    rows.append(dict(zip(fn,[sid,jur,lvl,cat,title,cite,url,pub,st,inc,ins,ret,h,'yes',notes])))
with open(reg,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)
used=set(x for r in R for x in r['source_ids']); have={r['source_id'] for r in rows}
assert not used-have, used-have

# ---- re-split (same seed/method)
T=['CA-ALG-01','HOB-ALG-01','JC-ALG-01','NJ-ALG-01','MA-ALG-P1','MA-ALG-P2','MA-RENT-P1','NWK-ALG-00']
def state(r): return r['jurisdiction'] if r['level']=='state' else r['jurisdiction'].split(', ')[1]
random.seed(20261003)
dev=[r for r in R if r['gold_id'] in T]; rest=[r for r in R if r['gold_id'] not in T]
groups=collections.defaultdict(list)
for r in rest: groups[(state(r),r['category'])].append(r)
test=[]
for k,g in sorted(groups.items()):
    g.sort(key=lambda r:r['gold_id']); random.shuffle(g); nn=len(g); nt=max(1,round(0.3*nn)) if nn>=2 else 0
    test+=g[:nt]; dev+=g[nt:]
for key in ['state','category']:
    fk=(lambda r:state(r)) if key=='state' else (lambda r:r['category'])
    for v in set(map(fk,R)):
        if not any(fk(r)==v for r in test):
            cand=[r for r in dev if fk(r)==v and r['gold_id'] not in T]; test.append(cand[-1]); dev.remove(cand[-1])
        if not any(fk(r)==v for r in dev):
            cand=[r for r in test if fk(r)==v]; dev.append(cand[-1]); test.remove(cand[-1])
dev.sort(key=lambda r:r['gold_id']); test.sort(key=lambda r:r['gold_id'])
for r in dev+test: jsonschema.validate(r,S)
json.dump(dev,open(f'{OUT}/gold/rules/dev.json','w'),indent=1,ensure_ascii=False); json.dump(test,open(f'{OUT}/gold/rules/test.json','w'),indent=1,ensure_ascii=False)
tab=collections.defaultdict(lambda:[0,0])
for r in dev: tab[('state',state(r))][0]+=1; tab[('category',r['category'])][0]+=1
for r in test: tab[('state',state(r))][1]+=1; tab[('category',r['category'])][1]+=1
open(f'{ROOT}/split_table.md','w').write('\n'.join(['| stratum | value | dev | test |','|---|---|---|---|']+[f'| {k[0]} | {k[1]} | {v[0]} | {v[1]} |' for k,v in sorted(tab.items())]))
C=collections.Counter
print('log rows added',len(LOG)); print('rules',len(R),'neg',sum(r['negative_finding'] for r in R),C(r['status'] for r in R))
print('verifier Hamza:',sum(r['verifier']=='Hamza' for r in R),'quote_verified',sum(r['quote_verified'] for r in R),'in_corpus',sum(r['quoted_span_in_corpus'] for r in R),'null spans',sum(r['quoted_span'] is None for r in R),'cf',sum(r['conflict_flag'] for r in R),'conf<0.7',sum(r['confidence']<0.7 for r in R))
print('dev',len(dev),'test',len(test),'| test ids changed? see diff'); print('sources',len(rows))
