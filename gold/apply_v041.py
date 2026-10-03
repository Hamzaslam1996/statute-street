#!/usr/bin/env python3
"""v0.4.1 — apply instructions/rulings_05.md §4a to HOB-RENT-01 (Hamza, 2026-10-04)."""
import json, csv, os, re, hashlib, collections
from collections import OrderedDict
OUT='/mnt/user-data/outputs/navigator'; ROOT='/home/claude/ss'
NOW='2026-10-04T00:30Z'; DEC='applied per rulings_05 §4a (Hamza, 2026-10-04)'; SRCF='instructions/rulings_05.md §4a'
def norm(s): return re.sub(r'\s+',' ',s).strip()
def rd(p): return open(p,encoding='utf-8').read()
def text(doc):
    for fo in ('corpus','supp'):
        p=f'{ROOT}/{fo}/{doc}.txt'
        if os.path.exists(p): return rd(p)
MAN={os.path.basename(p):rd(p) for p in __import__('glob').glob(f'{ROOT}/manual/*.txt')}
def raw_span(t,target):
    if target in t: return target
    words=[re.escape(w) for w in norm(target).split(' ')]
    m=re.search(r'\s+'.join(words),t); assert m,'span not found: '+norm(target)[:60]; return m.group(0)
R=json.load(open(f'{OUT}/gold/rules/all.json')); I={r['gold_id']:r for r in R}
LOG=[]; n0=len(list(csv.DictReader(open(f'{OUT}/gold/adjudication_log.csv'))))
def log(gid,field,old,new,src,why):
    LOG.append(OrderedDict(log_id=f'L{n0+len(LOG)+1:03d}',gold_id=gid,field=field,independent_value=str(new)[:300],silver_value=f'previous: {str(old)[:200]}',primary_source_url=src,recommendation='apply',reason=why,decided_by='Hamza',decision=DEC,decided_at=NOW))
def setf(r,field,val,src,why):
    old=r.get(field)
    if old!=val: r[field]=val; log(r['gold_id'],field,old,val,src,why)

MANF='HOB-RENT-01_Hoboken_ch155_ecode360.txt'; SID='S-MAN-15'; T=MAN[MANF]
r=I['HOB-RENT-01']
# citation / key_value (Hamza's wording)
setf(r,'citation','Hoboken Code § 155-5; applicability § 155-2',SID,SRCF)
setf(r,'key_value','lesser of 5% or CPI change, once per 12 months',SID,SRCF)
# headline span = full § 155-5 first sentence from the manual full-chapter text
s=raw_span(T,"At the expiration of a lease or at the termination of a lease of a periodic tenant, no landlord may request or receive a percentage increase in rent which is greater than 5% or the percentage difference between the consumer price index three months prior to the expiration or termination of the lease and three months prior to the commencement of the lease term, whichever is less.")
setf(r,'quoted_span',s,SID,SRCF+f' [span from sources/manual/{MANF} (§ 155-5, full chapter)]'); r['quote_verified']=True
# coverage: no unit-count test; § 155-2 exemptions (A)–(H)
cov=r['coverage']; old=dict(cov)
cov['min_units']=None; cov['max_units']=None; cov['coo_cutoff']=None; cov['year_built_max']=None; cov['owner_type']=None; cov['tenancy_months']=None
cov['other']=('§ 155-2: all dwelling units (as defined in § 155-1) except exemptions (A)–(H). No minimum unit count and no owner-occupancy exemption (unlike Jersey City/Newark). '
 'Coverage test (rulings_05 §4a): building type not hotel/motel/commercial/industrial/institutional/government; built on or before 1987-06-25 → covered; built after 1987-06-25 and completion < 30 years before the query date → unknown (N.J.S.A. 2A:42-84.1 exemption depends on mortgage term and statutory compliance filings not in the data); built after 1987-06-25 and ≥ 30 years before the query date → covered; year missing → unknown.')
if old!=cov: log('HOB-RENT-01','coverage',old['other'],cov['other'],SID,SRCF+' — no unit-count test; post-1987 new construction → unknown')
setf(r,'exemptions',('§ 155-2(A) motels and hotels; (B) newly constructed dwellings for their first rental only (registered with the Rent Regulation Officer); (C) industrial property; (D) nonresidential/commercial property (apartment units in mixed buildings remain covered); '
 '(E) housing provided to students by a school/college that owns or controls it; (F) housing owned and operated by other government agencies; (G) buildings completely vacant on or before and since 1984-01-01 (first rental only, registered); '
 '(H) per N.J.S.A. 2A:42-84.1 et seq., multiple dwellings constructed after 1987-06-25, for the lesser of the initial-mortgage amortisation period or 30 years after completion (30 years if no initial mortgage), only where the landlord complied with the statute\'s notice requirements.'),SID,SRCF)
setf(r,'requirement',('At the expiration or termination of a lease a Hoboken landlord may not request or receive a percentage rent increase greater than the lesser of 5% or the CPI change over the lease term; no more than one such cost-of-living increase in any twelve-month period (§ 155-5). '
 'Applies to all dwelling units except the § 155-2 exemptions; there is no minimum unit count and no owner-occupancy exemption.'),SID,SRCF)
if SID not in r['source_ids']: r['source_ids'].append(SID)
r['verified_against'].append(OrderedDict(url='sources/manual/HOB-RENT-01_Hoboken_ch155_ecode360.pdf',checked_at_utc='2026-10-04',result='full ch. 155 PDF downloaded by Hamza from https://ecode360.com/HO0741 (dated 2026-10-03), 25 pp.; § 155-2 exemptions (A)–(H) and § 155-5 cap verified against the pdftotext copy; § 155-5 history "[Amended 2-1-2023 by Ord. No. B-532]"'))
setf(r,'confidence',0.9,SID,'full official chapter text verified by Hamza')
r['verifier']='Hamza'; log('HOB-RENT-01','verifier','AI-draft','Hamza',SID,SRCF)
r['notes']=('Coverage test per rulings_05 §4a; Hoboken rows in the data: 36/40 lack year_built (→ unknown) and the four with a year (2000, 2001, 2007, 2010) are post-1987 and < 30 years old at the 2026-10-01 query date (→ unknown). '
 'Building-type exemptions (hotel/commercial/institutional/government) are not testable from the MOD-IV building codes in the data and are rare in a rental sample. Earlier § 155-5 span (team capture D033) is identical to the full-chapter text. ecode360 Terms of Use acknowledged.')
log('HOB-RENT-01','notes','(previous notes)',r['notes'],SID,SRCF)

# ---- re-verify spans (manual copies included for rows citing S-MAN-*)
bad=[]
for x in R:
    sp=x['quoted_span']
    if sp is None: x['quote_verified']=False; x['quoted_span_in_corpus']=False; continue
    srcs=[text(d) for d in x['corpus_doc_ids']+x['supplementary_doc_ids']]+([MAN[m] for m in MAN] if any(s.startswith('S-MAN-') for s in x['source_ids']) else [])
    ok=any(t and sp in t for t in srcs); x['quote_verified']=ok
    if not ok: bad.append(x['gold_id'])
    x['quoted_span_in_corpus']=any(norm(sp) in norm(text(d) or '') for d in x['corpus_doc_ids'])
assert not bad, bad
import jsonschema
S=json.load(open(f'{OUT}/gold/schema/gold_rule.schema.json'))
for x in R: jsonschema.validate(x,S)
json.dump(R,open(f'{OUT}/gold/rules/all.json','w'),indent=1,ensure_ascii=False)
# dev/test: row set unchanged → patch in place, keep ids
for part in ('dev','test'):
    p=f'{OUT}/gold/rules/{part}.json'; L=json.load(open(p))
    L=[I[x['gold_id']] for x in L]; json.dump(L,open(p,'w'),indent=1,ensure_ascii=False); print(part,len(L),'HOB-RENT-01' in [x['gold_id'] for x in L])

# ---- adjudication log
lp=f'{OUT}/gold/adjudication_log.csv'; rows=list(csv.DictReader(open(lp))); fn=list(rows[0].keys())
with open(lp,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows+LOG)

# ---- source register + official copy
reg=f'{OUT}/sources/source_register.csv'; rows=list(csv.DictReader(open(reg))); fn=list(rows[0].keys())
if SID not in {x['source_id'] for x in rows}:
    body=open(f'{ROOT}/manual/{MANF}','rb').read(); h=hashlib.sha256(body).hexdigest()
    with open(f'{OUT}/sources/official/{SID}.txt','wb') as f:
        f.write((f'SOURCE: https://ecode360.com/HO0741 (Hoboken Code ch. 155 Rent Control, chapter PDF download dated 2026-10-03)\nRETRIEVED: 2026-10-04\nVERIFIED_BY: Hamza (rulings_05 §4a, 2026-10-04)\nSHA256: {h}\nNOTE: copy of sources/manual/{MANF} (pdftotext of the manual PDF, 25 pp.). Source type: official. Publisher: General Code (ecode360). Manual download by Hamza; includes § 155-2 Limitation of applicability (A)–(H) and § 155-5 increase cap.\n---- BEGIN TEXT ----\n').encode()); f.write(body); f.write(b'\n---- END TEXT ----\n')
    rows.append(dict(zip(fn,[SID,'Hoboken, NJ','city','rent_increase_limits','Hoboken Code ch. 155 Rent Control – full chapter (ecode360 PDF) – manual','Hoboken Code §§ 155-2, 155-5','sources/manual/HOB-RENT-01_Hoboken_ch155_ecode360.pdf','General Code (ecode360)','official','none','D032,D033','2026-10-04',h,'yes','manual download by Hamza (PDF dated 2026-10-03); pdftotext .txt alongside; supersedes the TOC-only D032 and the Article II page D033 as the primary text for HOB-RENT-01'])))
    with open(reg,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)
used=set(s for x in R for s in x['source_ids']); assert used<={x['source_id'] for x in rows}
C=collections.Counter
print('log rows added',len(LOG),'->',n0+len(LOG)); print('rules',len(R),'neg',sum(x['negative_finding'] for x in R))
print('verifier Hamza:',sum(x['verifier']=='Hamza' for x in R),'quote_verified',sum(x['quote_verified'] for x in R),'in_corpus',sum(x['quoted_span_in_corpus'] for x in R),'null spans',sum(x['quoted_span'] is None for x in R),'cf',sum(x['conflict_flag'] for x in R),'conf<0.7',sum(x['confidence']<0.7 for x in R),'sources',len(rows))
