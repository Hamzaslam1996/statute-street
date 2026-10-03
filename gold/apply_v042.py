#!/usr/bin/env python3
"""v0.4.2 — MA-SCRN-02: official M.G.L. c.6 § 172 text (D094) as the quoted span. Approved by Hamza in chat, 2026-10-04 04:02 PKT."""
import json, csv, hashlib, collections, re, os
from collections import OrderedDict
OUT='/mnt/user-data/outputs/navigator'; ROOT='/home/claude/ss'
NOW='2026-10-03T23:05Z'; DEC='approved by Hamza in chat (2026-10-04, v0.4.2)'; WHY='official malegislature.gov c.6 § 172 page captured as D094 (re-capture from the cloud workspace after TLS failures from the Mac VM)'
def norm(s): return re.sub(r'\s+',' ',s).strip()
def rd(p): return open(p,encoding='utf-8').read()
def text(doc):
    for fo in ('corpus','supp'):
        p=f'{ROOT}/{fo}/{doc}.txt'
        if os.path.exists(p): return rd(p)
MAN={os.path.basename(p):rd(p) for p in __import__('glob').glob(f'{ROOT}/manual/*.txt')}
R=json.load(open(f'{OUT}/gold/rules/all.json')); I={r['gold_id']:r for r in R}
LOG=[]; n0=len(list(csv.DictReader(open(f'{OUT}/gold/adjudication_log.csv'))))
def log(gid,field,old,new,src,why):
    LOG.append(OrderedDict(log_id=f'L{n0+len(LOG)+1:03d}',gold_id=gid,field=field,independent_value=str(new)[:300],silver_value=f'previous: {str(old)[:200]}',primary_source_url=src,recommendation='apply',reason=why,decided_by='Hamza',decision=DEC,decided_at=NOW))
def setf(r,field,val,src,why):
    old=r.get(field)
    if old!=val: r[field]=val; log(r['gold_id'],field,old,val,src,why)

D=text('D094'); SID='S-MA-12'; URL='https://malegislature.gov/Laws/GeneralLaws/PartI/TitleII/Chapter6/Section172'
i=D.find('(3) A requestor or the requestor'); j=D.find('treated as a felony for purposes of this section.')+len('treated as a felony for purposes of this section.')
SPAN=D[i:j]; assert i>0 and SPAN in D and 'to evaluate applicants for rental or lease of housing' in SPAN and '10 years' in SPAN and '5 years' in SPAN
r=I['MA-SCRN-02']
old_span=r['quoted_span']
setf(r,'quoted_span',SPAN,URL,WHY+' [span from D094, § 172(a)(3): housing-applicant purpose + 10-year felony / 5-year misdemeanour look-back]')
r['quote_verified']=True
setf(r,'confidence',0.8,URL,WHY)
if 'D094' not in r['supplementary_doc_ids']: r['supplementary_doc_ids'].append('D094'); log('MA-SCRN-02','supplementary_doc_ids','(without D094)',r['supplementary_doc_ids'],URL,WHY)
if SID not in r['source_ids']: r['source_ids'].append(SID); log('MA-SCRN-02','source_ids','(without S-MA-12)',r['source_ids'],URL,WHY)
setf(r,'citation','M.G.L. c.6, § 172(a)(3); 803 CMR 5.00 (CORI – Housing), esp. 5.04, 5.10',URL,'citation re-ordered: statutory look-back provision (now quoted) first; regulation second')
# verified_against: official page added; FindLaw kept as secondary
r['verified_against'].insert(0,OrderedDict(url=URL,checked_at_utc='2026-10-03T22:58Z',result='official page captured as D094 (HTTP 200, whole-page text); § 172(a)(3) quoted verbatim; FindLaw mirror now secondary only'))
for v in r['verified_against']:
    if 'findlaw' in v['url']: v['result']='SECONDARY (mirror) — superseded as basis by the official page D094; kept for the record: '+v['result']
r['verifier']='Hamza'
new_notes=('v0.4.2 (Hamza, 2026-10-04): quoted_span = M.G.L. c.6 § 172(a)(3) from the official malegislature.gov page (D094); the 803 CMR 5.10 copy-before-questioning passage previously used as the span (verified against sources/manual/MA-SCRN-02_803_CMR_5.txt, pages dated 6/11/21) is retained here: "'
   +norm(old_span)+'". History: added by L097 (null span, confidence 0.5); lawyer review batch 1 row 2 supplied the 803 CMR 5 manual text; D094 captured 2026-10-03 22:58 UTC after two TLS failures from the Mac VM. No effective date stated in either text (Q17 rule).')
setf(r,'notes',r['notes'],URL,'notes rewritten (stale "null span / 0.5 / page could not be captured" wording removed)') if False else None
log('MA-SCRN-02','notes','(stale: null span / 0.5 / official page not captured)',new_notes,URL,'notes rewritten'); r['notes']=new_notes

# re-verify all spans (unchanged method)
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
for part in ('dev','test'):
    p=f'{OUT}/gold/rules/{part}.json'; L=json.load(open(p)); L=[I[x['gold_id']] for x in L]; json.dump(L,open(p,'w'),indent=1,ensure_ascii=False); print(part,len(L),'MA-SCRN-02' in [x['gold_id'] for x in L])
lp=f'{OUT}/gold/adjudication_log.csv'; rows=list(csv.DictReader(open(lp))); fn=list(rows[0].keys())
with open(lp,'w',newline='') as f: w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows+LOG)
# source register + official copy
reg=f'{OUT}/sources/source_register.csv'; rows=list(csv.DictReader(open(reg))); fn=list(rows[0].keys())
if SID not in {x['source_id'] for x in rows}:
    body=open(f'{ROOT}/supp/D094.txt','rb').read(); h=hashlib.sha256(body).hexdigest()
    with open(f'{OUT}/sources/official/{SID}.txt','wb') as f:
        f.write((f'SOURCE: {URL}\nRETRIEVED: 2026-10-03T22:58Z\nVERIFIED_BY: Hamza (chat approval 2026-10-04, v0.4.2)\nSHA256: {h}\nNOTE: team supplementary capture D094 (official malegislature.gov page, whole-page text). Source type: official. Publisher: Massachusetts General Court. Re-captured from the cloud workspace after two TLS failures from the Mac VM (2026-10-03 22:34/22:35 UTC).\n---- BEGIN TEXT ----\n').encode()); f.write(body); f.write(b'\n---- END TEXT ----\n')
    rows.append(dict(zip(fn,[SID,'MA','state','screening_restrictions','M.G.L. c.6, § 172 (official malegislature.gov page)','M.G.L. c.6, § 172(a)(3)',URL,'Massachusetts General Court','official','none','D094','2026-10-03T22:58Z',h,'yes','team capture D094 (cloud-workspace curl, single page) after TLS failures from the Mac VM; supersedes the FindLaw mirror S-MAN-04 as the basis for MA-SCRN-02'])))
    with open(reg,'w',newline='') as f: w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)
assert set(s for x in R for s in x['source_ids'])<={x['source_id'] for x in rows}
# README
p=f'{OUT}/gold/README.md'; t=open(p).read()
st=t.split('\n')[2]; t=t.replace(st,st.replace('**Status:** v0.4.1 (2026-10-04):','**Status:** v0.4.2 (2026-10-04): MA-SCRN-02 re-based on the official M.G.L. c.6 § 172 page (D094 = S-MA-12). v0.4.1:',1),1)
v=('v0.4.2 — MA-SCRN-02 (approved by Hamza in chat): quoted_span replaced by the § 172(a)(3) paragraph (housing-applicant purpose + 10-year felony / 5-year misdemeanour look-back) from the official malegislature.gov page, captured as D094 after the earlier TLS failures and registered as S-MA-12 (sources/official/S-MA-12.txt). '
   'quote_verified true, confidence 0.8, verifier Hamza; FindLaw mirror (S-MAN-04) kept in verified_against as secondary; the former 803 CMR 5.10 span is preserved in notes. Citation re-ordered to put § 172(a)(3) first. Log L203–L208. No address results changed; dev/test ids unchanged. '
   'Known stale text not changed this round: the MA-SCRN-02 reason string in build_addresses.py still says "text not captured; low confidence".')
t=t.rstrip('\n'); k=t.rfind('\nv0.4.1 — '); e=t.find('\n',k+1); e=len(t) if e==-1 else e; t=t[:e]+'\n'+v+t[e:]+'\n'
open(p,'w').write(t)
print('log rows added',len(LOG),'->',n0+len(LOG),'| Hamza',sum(x['verifier']=='Hamza' for x in R),'quote_verified',sum(x['quote_verified'] for x in R),'conf<0.7',sum(x['confidence']<0.7 for x in R),'sources',len(rows))
print('SPAN=',repr(SPAN))
