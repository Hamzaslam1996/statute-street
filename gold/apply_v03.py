#!/usr/bin/env python3
"""Apply Hamza's 2026-10-04 decisions (L009..L097), bump to v0.3, re-split, re-validate."""
import json, csv, os, random, collections, copy
from collections import OrderedDict
OUT='/mnt/user-data/outputs/navigator'; ROOT='/home/claude/ss'
NOW='2026-10-03T20:50Z'; DEC='Decided by Hamza 2026-10-04'
def text(doc):
    for fo in ('corpus','supp'):
        p=f'{ROOT}/{fo}/{doc}.txt'
        if os.path.exists(p): return open(p,encoding='utf-8').read()
R=json.load(open(f'{OUT}/gold/rules/all.json')); I={r['gold_id']:r for r in R}
def note(r,s): r['notes']=((r['notes'] or '').rstrip()+' '+s).strip()
def va(url,chk,res): return OrderedDict(url=url,checked_at_utc=chk,result=res)

# L009
r=I['SF-RENT-01']; r['effective_date']='2026-03-01'; note(r,f'{DEC} (L009): effective_date = start of the current rate period 2026-03-01; the Rent Ordinance itself dates from 1979.')
# L025
r=I['BERK-SCRN-01']; r['effective_date']='2020-04'; r['enacted_date']='2020-04-14'; note(r,f'{DEC} (L025): effective_date 2020-04 (month precision); adoption_date (enacted_date) 2020-04-14 per D003.')
# L033
r=I['SD-SCRN-01']; r['effective_date']='2019-08-01'; r['conflict_flag']=True; r['confidence']=min(r['confidence'],0.7)
r['conflict_note']='Two published dates: code history note "O–20986 N.S.; effective 10-18-2018" vs operative/applicable date 2019-08-01 reported by the San Diego Association of Realtors. '+DEC+' (L033): record 2019-08-01, conflict_flag true, confidence ≤ 0.7.'
note(r,f'{DEC} (L033): effective_date 2019-08-01 (code history 2018-10-18 noted).')
# L042
r=I['SA-ALG-01']; r['effective_date']=None; note(r,f'{DEC} (L042): effective_date null; news reports April 2026 (Morgan Lewis: 2026-04-02).')
# L046 / Q17
r=I['NJ-JUST-01']; r['effective_date']=None; note(r,f'{DEC} (L046, Q17 rule): long-standing statutes carry null unless the source text states an effective date.')
# L059
r=I['HOB-ALG-01']; r['effective_date']='2025-07'; r['enacted_date']='2025-07-09'; note(r,f'{DEC} (L059): effective_date 2025-07 (month precision); adoption_date (enacted_date) 2025-07-09 per D034.')
# L082
r=I['BOS-JUST-01']; r['effective_date']='2020-11-06'; note(r,f'{DEC} (L082): adopt 2020-11-06 (official FAQ D014).')
# L085 / L088: rewrite BOS-SCRN-01 as Fair Housing Commission regs; add BOS-SCRN-02 = Fair Chance policy
old=copy.deepcopy(I['BOS-SCRN-01'])
r=I['BOS-SCRN-01']
r.update(OrderedDict(title='Boston Fair Housing Commission – rental assistance / Section 8 protection (Boston Fair Housing Ordinance and regulations)',
  requirement='In the City of Boston it is illegal to discriminate in renting housing on the basis of protected classes that include rental assistance (e.g., renters using Section 8 vouchers); the Boston Fair Housing Commission enforces these local, state and federal protections.',
  key_value='rental assistance / Section 8 voucher use is a protected class locally',
  coverage=OrderedDict(coo_cutoff=None,year_built_max=None,min_units=None,max_units=None,owner_type=None,tenancy_months=None,other='Rental housing in the City of Boston'),
  exemptions=None, effective_date=None, enacted_date=None, sunset_date=None,
  citation='Boston Fair Housing Commission regulations (Boston Code ch. 10, § 10-3 Fair Housing Ordinance – section not verified)',
  source_ids=['S-BOS-05'], corpus_doc_ids=['D012'], supplementary_doc_ids=[],
  quoted_span='In the City of Boston, it’s illegal to discriminate when renting, buying, selling, or securing financing for any housing.',
  quoted_span_in_corpus=True, quote_verified=True,
  interaction=OrderedDict(overrides=[],yields_to=[],note='Operates alongside M.G.L. c.151B § 4(10) (MA-SCRN-01)'),
  conflict_flag=False, conflict_note=None, negative_finding=False, negative_reason=None, confidence=0.6,
  verified_against=[va('https://www.boston.gov/departments/fair-housing-and-equity/boston-fair-housing-regulations','2026-10-01T22:35Z','organisers corpus copy D012 (official): protected classes list includes "Rental Assistance" with example "renters using Section 8 voucher"')],
  verifier='AI-draft',
  notes=f'{DEC} (L085/L088): BOS-SCRN-01 kept as the Fair Housing Commission rule (silver\'s identification); effective_date null. The D012 page is a summary; the ordinance/regulation section number is unverified. Fair Chance policy moved to BOS-SCRN-02.'))
new=copy.deepcopy(old); new['gold_id']='BOS-SCRN-02'; new['effective_date']='2017-02'; new['conflict_flag']=True; new['confidence']=0.5
new['coverage']['other']='City-funded housing only: providers receiving DND funding/land or with BPDA Inclusionary Development Policy units'
new['conflict_note']='Policy (not legislation) with city-funded scope; '+DEC+' (L088): recorded as BOS-SCRN-02, scope city-funded only, conflict_flag true, low confidence.'
new['notes']=(old['notes'] or '')+f' {DEC} (L088): added as a second Boston screening row.'
# L095 HOB-RENT-02
hob=OrderedDict(gold_id='HOB-RENT-02',jurisdiction='Hoboken, NJ',level='city',category='rent_increase_limits',status='in_force',
  title='Disclosure duties for renewal rent increases above 10% – Hoboken Code ch. 158 (Ord. B-750)',
  requirement='A Hoboken landlord seeking a renewal rent increase of more than 10% year over year must first give the tenant an itemisation of the costs behind the increase, a statement whether a rent algorithm was used, notice of the right to challenge an unconscionable increase, and the Division of Housing\'s contact details; fines up to $1,000 per incident.',
  key_value='disclosures required for renewal increases > 10% (not a cap)',
  coverage=OrderedDict(coo_cutoff=None,year_built_max=None,min_units=None,max_units=None,owner_type=None,tenancy_months=None,other='All residential landlords in Hoboken renewing a lease with a current tenant'),
  exemptions=None, effective_date='2025-04', enacted_date='2025-04-02', sunset_date=None,
  citation='Hoboken Code ch. 158, art. I (Ord. No. B-750, adopted 2025-04-02)',
  source_ids=['S-HOB-04'], corpus_doc_ids=[], supplementary_doc_ids=['D034'],
  quoted_span='All residential landlords seeking to increase rent by more than 10% upon a renewal of a lease with a current tenant year over year shall be required to make the following disclosures to existing tenants',
  quoted_span_in_corpus=False, quote_verified=True,
  interaction=OrderedDict(overrides=[],yields_to=[],note='Supplements the ch. 155 rent-control cap (HOB-RENT-01), which still governs rent-controlled dwellings; this duty applies to all renewals above 10% (e.g., exempt new construction)'),
  conflict_flag=True, conflict_note='Categorisation: a disclosure duty recorded under rent_increase_limits. '+DEC+' (L095, Q15): added with conflict_flag true.',
  negative_finding=False, negative_reason=None, confidence=0.7,
  verified_against=[va('https://ecode360.com/46833413','2026-10-03T18:51Z','team supplementary capture D034 (code publisher): "[Adopted 4-2-2025 by Ord. No. B-750]" and disclosure text')],
  verifier='AI-draft', notes='effective_date month precision (NJ ordinances take effect ~20 days after final passage/publication); adoption 2025-04-02.')
# L096 MA-FEE-02
mafee=OrderedDict(gold_id='MA-FEE-02',jurisdiction='MA',level='state',category='application_screening_fees',status='in_force',
  title='Broker fee reform – M.G.L. c.112, § 87DDD½ (as amended by St. 2025, c.9, § 43)',
  requirement='A rental broker\'s fee may be charged only to the party (landlord or tenant) who engaged and contracted with the broker; a tenant who did not engage the broker cannot be made to pay the broker fee.',
  key_value='broker fee payable only by the party who engaged the broker',
  coverage=OrderedDict(coo_cutoff=None,year_built_max=None,min_units=None,max_units=None,owner_type=None,tenancy_months=None,other='All residential rentals in Massachusetts arranged through a licensed broker or salesperson'),
  exemptions=None, effective_date='2025-08-01', enacted_date=None, sunset_date=None,
  citation='M.G.L. c.112, § 87DDD½ (St. 2025, c.9, § 43, eff. 2025-08-01)',
  source_ids=['S-MA-10'], corpus_doc_ids=['D057'], supplementary_doc_ids=[],
  quoted_span='Any fee shall only be paid by the party, lessor or tenant who originally engaged and entered into a contract with the licensed broker or salesperson.',
  quoted_span_in_corpus=True, quote_verified=True,
  interaction=OrderedDict(overrides=[],yields_to=[],note='Complements MA-FEE-01 (landlords may charge no application fee); category fit (broker fee vs application fee) is debatable'),
  conflict_flag=False, conflict_note=None, negative_finding=False, negative_reason=None, confidence=0.85,
  verified_against=[va('https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVI/Chapter112/Section87DDD%201~2','2026-10-01T22:56Z','organisers corpus copy D057 (official): "Text of section as amended by 2025, 9, Sec. 43 effective August 1, 2025"')],
  verifier='AI-draft', notes=f'{DEC} (L096): added; effective date 2025-08-01 stated in the official annotation (listed in the brief).')
# L097 MA-SCRN-02
mascr=OrderedDict(gold_id='MA-SCRN-02',jurisdiction='MA',level='state',category='screening_restrictions',status='in_force',
  title='CORI in housing – 803 CMR 5.00 (Criminal Offender Record Information: housing)',
  requirement='Housing providers that obtain Criminal Offender Record Information must follow DCJIS regulations limiting how CORI is requested, used and shared in housing decisions.',
  key_value='regulated access to and use of CORI by housing providers',
  coverage=OrderedDict(coo_cutoff=None,year_built_max=None,min_units=None,max_units=None,owner_type=None,tenancy_months=None,other='Housing providers in Massachusetts that use CORI'),
  exemptions=None, effective_date=None, enacted_date=None, sunset_date=None,
  citation='803 CMR 5.00',
  source_ids=['S-MA-11'], corpus_doc_ids=['D056'], supplementary_doc_ids=[],
  quoted_span=None, quoted_span_in_corpus=False, quote_verified=False,
  interaction=OrderedDict(overrides=[],yields_to=[],note='Operates alongside M.G.L. c.151B § 4(10) (MA-SCRN-01); Boston and Berkeley-style fair-chance rules are stricter'),
  conflict_flag=False, conflict_note=None, negative_finding=False, negative_reason=None, confidence=0.5,
  verified_against=[va('https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download','2026-10-03T19:03Z','organisers manifest D056: capture failed (403 Forbidden); team capture also failed (0 bytes). Text not seen.')],
  verifier='AI-draft', notes=f'{DEC} (L097): added with null span, quote_verified false, confidence 0.5; source text never retrieved — requirement wording is a general description, not quoted.')

for x in (new,hob,mafee,mascr):
    assert x['gold_id'] not in I; R.append(x); I[x['gold_id']]=x
# span re-verify
for r in R:
    if r['quoted_span'] is not None:
        ok=any(r['quoted_span'] in (text(d) or '') for d in r['corpus_doc_ids']+r['supplementary_doc_ids'])
        assert ok, ('span fail',r['gold_id'])
        r['quote_verified']=True
        r['quoted_span_in_corpus']=any(r['quoted_span'] in (text(d) or '') for d in r['corpus_doc_ids'])
    else:
        r['quote_verified']=False
import jsonschema
S=json.load(open(f'{OUT}/gold/schema/gold_rule.schema.json'))
for r in R: jsonschema.validate(r,S)
R.sort(key=lambda r:[ 'CA','NJ','MA','Los Angeles, CA','San Francisco, CA','San Diego, CA','Berkeley, CA','Santa Ana, CA','Jersey City, NJ','Hoboken, NJ','Newark, NJ','Boston, MA','Cambridge, MA'].index(r['jurisdiction']))
json.dump(R,open(f'{OUT}/gold/rules/all.json','w'),indent=1,ensure_ascii=False)

# source register additions
reg=f'{OUT}/sources/source_register.csv'; rows=list(csv.DictReader(open(reg)))
fn=list(rows[0].keys())
rows.append(dict(zip(fn,['S-MA-10','MA','state','application_screening_fees','M.G.L. c.112, § 87DDD½','M.G.L. c.112, § 87DDD½','https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVI/Chapter112/Section87DDD%201~2','Massachusetts General Court','official','D057','none','2026-10-01T22:56Z','','yes','corpus copy; added v0.3 (L096)'])))
rows.append(dict(zip(fn,['S-MA-11','MA','state','screening_restrictions','803 CMR 5.00 CORI – housing (NOT CAPTURED)','803 CMR 5.00','https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download','Mass. DCJIS (mass.gov)','official','D056','none','','','yes','403 on organisers and team capture; no text saved; added v0.3 (L097)'])))
import hashlib
for sid,body,src in [('S-MA-10',open(f'{ROOT}/corpus/D057.txt','rb').read(),'organisers corpus copy D057'),('S-MA-11',b'(no text saved: mass.gov returned 403 to organisers and team captures)','no text saved')]:
    h=hashlib.sha256(body).hexdigest()
    for r in rows:
        if r['source_id']==sid: r['sha256']=h
    rr=[r for r in rows if r['source_id']==sid][0]
    open(f'{OUT}/sources/official/{sid}.txt','wb').write((f"SOURCE: {rr['url']}\nRETRIEVED: {rr['retrieved_at']}\nVERIFIED_BY: AI-draft (v0.3, 2026-10-04)\nSHA256: {h}\nNOTE: {src}. {rr['notes']}\n---- BEGIN TEXT ----\n").encode()+body+b'\n---- END TEXT ----\n')
with open(reg,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)

# adjudication log
lp=f'{OUT}/gold/adjudication_log.csv'; log=list(csv.DictReader(open(lp)))
decisions={'L009':'2026-03-01 (rate period start; ordinance since 1979)','L025':'2020-04 + adoption_date 2020-04-14','L033':'2019-08-01, conflict_flag true, note code history 2018-10-18, confidence ≤0.7','L042':'null; note news reports April 2026','L046':'null (Q17: long-standing statutes null unless source text states an effective date)','L059':'2025-07 + adoption_date 2025-07-09','L082':'adopt independent 2020-11-06','L085':'null','L088':'keep BOS-SCRN-01 as Fair Housing Commission regs; add BOS-SCRN-02 Fair Chance policy (city-funded only, conflict_flag, low confidence)','L095':'add HOB-RENT-02, conflict_flag true','L096':'add MA-FEE-02, eff 2025-08-01','L097':'add MA-SCRN-02, null span, quote_verified false, confidence 0.5'}
for r in log:
    if r['log_id'] in decisions: r['decided_by']='Hamza'; r['decision']=decisions[r['log_id']]; r['decided_at']=NOW
with open(lp,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(log[0].keys())); w.writeheader(); w.writerows(log)
print('open log rows:',sum(1 for r in log if not r['decided_by']))

# re-split
T=['CA-ALG-01','HOB-ALG-01','JC-ALG-01','NJ-ALG-01','MA-ALG-P1','MA-ALG-P2','MA-RENT-P1','NWK-ALG-00']
def state(r): return r['jurisdiction'] if r['level']=='state' else r['jurisdiction'].split(', ')[1]
random.seed(20261003)
dev=[r for r in R if r['gold_id'] in T]; rest=[r for r in R if r['gold_id'] not in T]
groups=collections.defaultdict(list)
for r in rest: groups[(state(r),r['category'])].append(r)
test=[]
for k,g in sorted(groups.items()):
    g.sort(key=lambda r:r['gold_id']); random.shuffle(g); n=len(g); nt=max(1,round(0.3*n)) if n>=2 else 0
    test+=g[:nt]; dev+=g[nt:]
for key in ['state','category']:
    f=(lambda r:state(r)) if key=='state' else (lambda r:r['category'])
    for v in set(map(f,R)):
        if not any(f(r)==v for r in test):
            cand=[r for r in dev if f(r)==v and r['gold_id'] not in T]; test.append(cand[-1]); dev.remove(cand[-1])
        if not any(f(r)==v for r in dev):
            cand=[r for r in test if f(r)==v]; dev.append(cand[-1]); test.remove(cand[-1])
dev.sort(key=lambda r:r['gold_id']); test.sort(key=lambda r:r['gold_id'])
for r in dev+test: jsonschema.validate(r,S)
json.dump(dev,open(f'{OUT}/gold/rules/dev.json','w'),indent=1,ensure_ascii=False)
json.dump(test,open(f'{OUT}/gold/rules/test.json','w'),indent=1,ensure_ascii=False)
tab=collections.defaultdict(lambda:[0,0])
for r in dev: tab[('state',state(r))][0]+=1; tab[('category',r['category'])][0]+=1
for r in test: tab[('state',state(r))][1]+=1; tab[('category',r['category'])][1]+=1
lines=['| stratum | value | dev | test |','|---|---|---|---|']+[f'| {k[0]} | {k[1]} | {v[0]} | {v[1]} |' for k,v in sorted(tab.items())]
open(f'{ROOT}/split_table.md','w').write('\n'.join(lines))
C=collections.Counter
print('rules total',len(R),'negative',sum(r['negative_finding'] for r in R),'rules/pending/failed',sum(not r['negative_finding'] for r in R))
print('status',C(r['status'] for r in R)); print('state',C(state(r) for r in R))
print('quote_verified true',sum(r['quote_verified'] for r in R),'false',sum(not r['quote_verified'] for r in R),'in_corpus',sum(r['quoted_span_in_corpus'] for r in R))
print('conflict_flag',sum(r['conflict_flag'] for r in R),'confidence<0.7',sum(r['confidence']<0.7 for r in R))
print('dev',len(dev),'test',len(test)); print('\n'.join(lines))
J=['CA','NJ','MA','Los Angeles, CA','San Francisco, CA','San Diego, CA','Berkeley, CA','Santa Ana, CA','Jersey City, NJ','Hoboken, NJ','Newark, NJ','Boston, MA','Cambridge, MA']
CAT=['rent_increase_limits','just_cause_eviction','security_deposits','application_screening_fees','screening_restrictions','algorithmic_rent_setting']
print('cells',sum(1 for j in J for c in CAT if any(r['jurisdiction']==j and r['category']==c for r in R)))
