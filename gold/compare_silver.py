#!/usr/bin/env python3
import json, csv, re
from collections import OrderedDict
OUT='/mnt/user-data/outputs/navigator'
IND={r['gold_id']:r for r in json.load(open(f'{OUT}/gold/rules/all.json'))}
SIL={r['gold_id']:r for r in json.load(open('/home/claude/ss/silver_rules.json'))['rules']}
def norm(sid):
    s=sid.replace('-JC-','-JUST-').replace('-SCR-','-SCRN-')
    if s.startswith('BK-'): s='BERK'+s[2:]
    return s
MAP={}  # silver -> independent
for s in SIL:
    n=norm(s)
    if n in IND: MAP[s]=n
# special: silver BOS-SCR-01 is a different rule in the same cell as BOS-SCRN-01; silver HOB-FEE-01 (rent disclosure) has no counterpart
MAP['BOS-SCR-01']='BOS-SCRN-01'
only_silver=[s for s in SIL if s not in MAP]
only_ind=[i for i in IND if i not in MAP.values()]

# field-level evidence notes (independent value basis). Keyed by (silver_id, field)
EV={
('CA-ALG-01','citation'):'Corpus D022 shows AB 325 adds Bus. & Prof. Code §§ 16729 and 16756.1; § 16729 is the operative prohibition. Recommend independent (specific section).',
('CA-JC-01','key_value'):'Wording only; both describe the 12-month trigger. No change needed.',
('SF-RENT-01','effective_date'):'Silver uses the rate-period start (2026-03-01, D080); independent leaves null because the Rent Ordinance dates from 1979 and the rate is annual. Decision for Hamza: rate-period date vs null.',
('SF-RENT-01','citation'):'Independent cites § 37.3(a) (allowable increases); silver cites ch. 37 generally. Equivalent; prefer the section.',
('SF-JC-01','citation'):'Equivalent (§ 37.9 vs § 37.9(a)).',
('LA-RENT-01','citation'):'Independent adds Ord. No. 188795 and § 151.06 (City Clerk CF 23-1134); silver cites the RSO generally. Prefer independent.',
('LA-RENT-01','key_value'):'Independent records 3% (Jul 2025–Jun 2026) and the 90%-of-CPI / 1% floor / 4% cap formula (AAGLA, secondary; LAHD page confirms 2026-02-02 changes). Silver has the formula description without numbers. Prefer independent; numbers for Jul 2026–Jun 2027 not confirmed on an official page.',
('LA-JC-01','citation'):'Equivalent (§ 165.00 et seq. vs § 165.03 / Ord. 187737, verified against the City Clerk PDF).',
('LA-DEP-01','source'):'Independent additionally cites official LAHD RSO overview (D041 lists "Interest Payments on Security Deposits"); silver relied on AAGLA only.',
('BK-RENT-01','key_value'):'Independent gives 1.0% for 2026 (D008 official notice) and the 65%-of-CPI / 5% cap formula (berkeley.municipal.codes 13.76.110); silver has no number. Prefer independent.',
('BK-SCR-01','effective_date'):'Silver 2020-03-12 (unsourced). Independent: adopted 2020-04-14 per Rent Board page D003 ("On April 14, 2020, Berkeley City Council passed..."); exact effective date not shown by the code publisher → year precision 2020. Neither value is primary-verified to the day; recommend 2020 (or verify Ord. 7692-NS second reading/effective date).',
('BK-ALG-01','effective_date'):'Silver 2026-03-01 (README text date). Independent 2026-01-01: berkeley.municipal.codes records Ord. 7992-NS adopted 2025-12-02, effective 2026-01-01, and the corpus text D001 has no delayed-effect clause; the 2026-03-01 clause belonged to the superseded Ord. 7974-NS. Organisers list this as an open question — Hamza decides (open_questions Q1).',
('BK-ALG-01','citation'):'Equivalent; independent cites § 13.63.030 (prohibition) + Ord. 7992-NS.',
('SD-SCR-01','effective_date'):'Silver null; independent 2018-10-18 from the SDMC history note "O–20986 N.S.; effective 10-18-2018" (NHLP mirror of the code). Operative date 2019-08-01 reported by SDAR (secondary) – flagged.',
('SD-SCR-01','citation'):'Equivalent; independent cites § 98.0803 specifically.',
('SA-RENT-01','citation'):'Silver cites Ord. NS-3011; independent could not verify an ordinance/section number (press release D085 only). If NS-3011/NS-3012 can be confirmed from the Santa Ana code, adopt silver\'s numbers.',
('SA-JC-01','citation'):'As above (silver NS-3012 unverified by independent).',
('SA-ALG-01','effective_date'):'Silver 2026-04 (from news/Morgan Lewis). Independent null: no primary source reached (rule 5.1/5.2); secondary sources say 2026-04-02. Decision: accept month precision from secondary sources or keep null.',
('NJ-FEE-01','citation'):'Silver "46:8-?"; independent N.J.S.A. 46:8-18.1 — verified in corpus D066 ("C.46:8-18.1 Residential rental property application fee not to exceed $50"). Adopt independent.',
('NJ-FEE-01','key_value'):'Independent adds CPI adjustment from January 2027 (D066 § 1(d)). Compatible.',
('NJ-ALG-01','citation'):'Silver "56:9-?"; independent N.J.S.A. 56:9-20 to 56:9-26 — from the chapter header of D069 ("C.56:9-20 to 56:9-26"). Adopt independent.',
('HOB-ALG-01','effective_date'):'Silver 2025-07-09 is the adoption date (D034 "[Adopted 7-9-2025 by Ord. No. B-781]"); independent uses month precision 2025-07 because NJ ordinances take effect after publication (~20 days). Decision for Hamza.',
('HOB-RENT-01','key_value'):'Equivalent (lesser of 5% or CPI).',
('HOB-RENT-01','coverage'):'Independent adds § 155-2 exemptions (hotels, post-1987-06-25 new construction, etc.) read from ecode360; silver left coverage to verify.',
('JC-RENT-01','key_value'):'Silver "(verify)"; independent verified the lesser-of-4%-or-CPI formula from the official Jersey City CPI notice quoting § 260-3, and the 1–4 unit exemption from D036. Adopt independent and remove "(verify)".',
('JC-RENT-01','citation'):'Independent § 260-3 (official notice). Adopt.',
('NWK-RENT-01','key_value'):'Silver "(verify)"; independent verified "In no case shall the allowable rent increase exceed 4%" (CPI 15→3 months) from D070 § 19:2-3.1. Adopt independent.',
('NWK-RENT-01','citation'):'Independent § 19:2-3.1 (Ord. 6 PSF-A(S) 2017; amended 2024). Adopt.',
('MA-RENT-00','effective_date'):'Silver 1994-12-08 (c.40P enactment, unsourced in corpus); independent null (negative finding). Harmless either way; prefer null for negative findings.',
('MA-RENT-P1','negative_finding'):'Silver marks the failed initiative as negative_finding=true; independent records it as a failed measure (status failed, negative_finding=false) and keeps a separate MA-RENT-00 negative finding. Representational; keep both rows.',
('BOS-JC-01','effective_date'):'Silver 2021-01-01 (unsourced); independent 2020-11-06 from the official FAQ D014 ("The HSNA becomes effective on November 6, 2020"). Adopt independent.',
('BOS-JC-01','citation'):'Silver "Boston Code ch. 10, § 10-14"; independent "ch. 9, § 9-20" — BOTH from memory, neither verified. Hamza to check the Boston Code (ordinance of October 2020).',
('BOS-JC-01','category'):'Both flag the categorisation (notice duty vs just cause) – open_questions Q5.',
('BOS-SCR-01','rule_identity'):'Different rules in the same cell: silver = Boston Fair Housing Commission regulations (source of income), independent = Boston Fair Chance Tenant Selection Policy (criminal history, DND-funded housing; D010 content). D012 (corpus) is only the Commission landing page and does not state a source-of-income rule. Options: keep independent; add silver\'s as BOS-SCRN-02 if the Commission regulation text can be sourced.',
('CAM-SCR-01','citation'):'Silver ch. 2.76 (Human Rights Ordinance); independent ch. 14.04 (Fair Housing Ordinance). D029 says the Commission enforces both and that housing discrimination is covered by the Fair Housing Ordinance ch. 14.04. Adopt independent.',
('LA-ALG-00','source'):'Both negative. Independent adds the Aug-2026 Morgan Lewis survey (no LA ordinance listed) and a 2026-10-03 web search; conflict_flag=true because absence is inferred.',
('NJ-RENT-00','status'):'Representational: silver gives negative findings status in_force; independent uses n/a. Scorer should treat both as "no rule".',
}

def fields(si, ii):
    s=SIL[si]; i=IND[ii]; diffs=[]
    def add(f,sv,iv,ev=None): diffs.append((f,sv,iv,ev or EV.get((si,f),'')))
    # status
    sst=s['status']; ist=i['status']
    if s.get('negative_finding') and i['negative_finding']:
        pass  # both negative; status representational
    elif sst!=ist: add('status',sst,ist)
    if bool(s.get('negative_finding'))!=i['negative_finding']: add('negative_finding',s.get('negative_finding',False),i['negative_finding'])
    if s['category']!=i['category']: add('category',s['category'],i['category'])
    if (s.get('effective_date') or None)!=(i['effective_date'] or None): add('effective_date',s.get('effective_date'),i['effective_date'])
    if s['citation']!=i['citation']: add('citation',s['citation'],i['citation'])
    if (s.get('key_value') or None)!=(i['key_value'] or None) and not (s.get('negative_finding') and i['negative_finding']): add('key_value',s.get('key_value'),i['key_value'])
    for k in [('coverage',None),('source',None),('rule_identity',None)]:
        if (si,k[0]) in EV: add(k[0],'(see note)','(see note)')
    return diffs

rows=[]; log=[]; agrees=[]
n=1
for si,ii in MAP.items():
    d=fields(si,ii)
    if not d: agrees.append((si,ii)); continue
    for f,sv,iv,ev in d:
        rec_map={'citation':'adopt independent','effective_date':'Hamza decides','key_value':'adopt independent','status':'Hamza decides','negative_finding':'keep both rows','category':'Hamza decides','coverage':'adopt independent','source':'adopt independent','rule_identity':'Hamza decides'}
        rec=rec_map.get(f,'Hamza decides')
        SUB_KV={'CA-FEE-01','LA-RENT-01','BK-RENT-01','JC-RENT-01','NWK-RENT-01','SA-RENT-01','NJ-FEE-01','BOS-SCR-01','MA-RENT-P1'}
        SUB_CIT={'CA-ALG-01','NJ-FEE-01','NJ-ALG-01','SA-RENT-01','SA-JC-01','CAM-SCR-01','BOS-JC-01','JC-RENT-01','NWK-RENT-01','LA-RENT-01','SD-SCR-01','BK-SCR-01','BOS-SCR-01','BOS-RENT-00'}
        if f=='key_value' and si not in SUB_KV: rec='no change (wording only)'; ev=ev or 'Wording differs; substance equivalent.'
        if f=='citation' and si not in SUB_CIT: rec='no change (independent cite is more specific)'; ev=ev or 'Same provision; independent cites the operative section.'
        if (si,f) in EV and ('Equivalent' in EV[(si,f)] or 'Compatible' in EV[(si,f)] or 'No change' in EV[(si,f)] or 'Representational' in EV[(si,f)] or 'Harmless' in EV[(si,f)]): rec='no change (equivalent)'
        if (si,f) in EV and 'adopt silver' in EV[(si,f)].lower(): rec='adopt silver if verified'
        rows.append((si,ii,f,sv,iv,ev,rec))
        src=IND[ii]['verified_against'][0]['url'] if IND[ii]['verified_against'] else ''
        log.append(OrderedDict(log_id=f'L{n:03d}',gold_id=ii,field=f,independent_value=iv,silver_value=sv,primary_source_url=src,recommendation=rec,reason=ev,decided_by='',decision='',decided_at='')); n+=1
for s in only_silver:
    log.append(OrderedDict(log_id=f'L{n:03d}',gold_id=f'(silver {s})',field='row',independent_value='absent',silver_value=f"{SIL[s]['category']} {SIL[s]['status']} {SIL[s]['citation']}",primary_source_url='',recommendation='Hamza decides',reason={'HOB-FEE-01':'Disclosure duty for >10% increases (Ord. B-750) – independent treats as not a rent cap; see open_questions Q15.','MA-FEE-02':'Broker-fee reform (c.112 § 87DDD½, eff. 2025-08-01) – independent folded into MA-FEE-01 notes; a separate row is defensible (category fit debatable: broker fee ≠ application fee).','MA-SCR-02':'803 CMR 5.00 (CORI) – source not captured (403); independent omitted because no text could be quoted; mentioned in MA-SCRN-01 interaction note.'}.get(s,''),decided_by='',decision='',decided_at='')); n+=1
for i in only_ind:
    r=IND[i]
    log.append(OrderedDict(log_id=f'L{n:03d}',gold_id=i,field='row',independent_value=f"{r['category']} {r['status']} {r['citation']}",silver_value='absent',primary_source_url=(r['verified_against'][0]['url'] if r['verified_against'] else ''),recommendation='keep (independent)' if not r['negative_finding'] else 'keep (negative finding fills the matrix cell)',reason=r['negative_reason'] or r['title'],decided_by='',decision='',decided_at='')); n+=1

with open(f'{OUT}/gold/adjudication_log.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(log[0].keys())); w.writeheader(); w.writerows(log)

# report
L=[]
L.append('# Silver vs independent key — comparison (Step 7)\n')
L.append(f'Opened `gold/gold_rules.json` (53 rows: 44 rules + 9 negatives) and `gold/GOLD_REVIEW.md` **after** freezing the independent key (see `FREEZE_before_step7.sha256`). Independent key: {len(IND)} rows ({sum(1 for r in IND.values() if not r["negative_finding"])} rules/pending/failed + {sum(1 for r in IND.values() if r["negative_finding"])} negative findings). Neither key was edited. Every disagreement below is also a row in `adjudication_log.csv` with `decided_by` blank.\n')
L.append(f'**Accounting of silver rows:** matched {len(MAP)} (agree {len(agrees)}, field-level disagreements {len(set(r[0] for r in rows))}), silver-only {len(only_silver)}. Independent-only rows: {len(only_ind)}.\n')
L.append('## (a) Rules in independent but not in silver\n')
L.append('| gold_id | category | status | citation | why it exists |'); L.append('|---|---|---|---|---|')
for i in only_ind:
    r=IND[i]; L.append(f"| {i} | {r['category']} | {r['status']} | {r['citation']} | {(r['negative_reason'] or r['title'])[:160]} |")
L.append('\nMost of these are **negative findings** that fill the remaining cells of the 13 × 6 matrix (the judges\' key has 19 such findings; silver has 9). Substantive additions: SF-DEP-01 (deposit interest, S.F. Admin. Code ch. 49), LA-SCRN-01 (LAMC § 45.67 source of income — silver noted "check D038" but did not add it), LA-JUST-02 (RSO eviction grounds), BERK-JUST-01, BERK-DEP-01, BERK-FEE-01, NWK-SCRN-01 (Ban the Box housing, 2015), CAM-JUST-01, BOS-RENT-P1.\n')
L.append('## (b) Rules in silver but not in independent\n')
L.append('| silver_id | category | status | citation | independent position |'); L.append('|---|---|---|---|---|')
for s in only_silver:
    r=SIL[s]; L.append(f"| {s} | {r['category']} | {r['status']} | {r['citation']} | {[x for x in log if x['gold_id']==f'(silver {s})'][0]['reason']} |")
L.append('\n## (c) Field-level disagreements (matched rows)\n')
L.append('Substantive rows first; wording-only differences are listed afterwards for completeness.\n')
L.append('| silver_id | gold_id | field | silver | independent | evidence | recommendation |'); L.append('|---|---|---|---|---|---|---|')
rows.sort(key=lambda r:(r[6].startswith('no change'),r[0]))
for si,ii,f,sv,iv,ev,rec in rows:
    esc=lambda x:str(x).replace('|','\\|')
    L.append(f"| {si} | {ii} | {f} | {esc(sv)} | {esc(iv)} | {esc(ev)} | {rec} |")
L.append('\n## (d) Rows that agree on all compared fields\n')
L.append(', '.join(f'{s}→{i}' for s,i in agrees) or '(none)')
L.append('\n## Representational differences (not logged per row)\n- Silver gives negative findings `status: in_force`; independent uses `n/a`. Silver id prefixes differ (JC→JUST, SCR→SCRN, BK→BERK).\n- Independent carries structured `coverage`, `quoted_span` (substring-verified), `quoted_span_in_corpus`, `verified_against` and `source_ids`; silver has free-text `coverage_conditions` and a `verify` hint.\n- Silver T-test ids (CA-ALG-01, HOB-ALG-01, JC-ALG-01, NJ-ALG-01, MA-ALG-P1/P2, MA-RENT-P1) match the organisers\' change_tests and the independent key.\n')
L.append('\n## Recommendation summary\n1. Adopt independent values where the silver row says "verify" or "?" and the independent key has a verified source (NJ-FEE-01, NJ-ALG-01 citations; JC-RENT-01 and NWK-RENT-01 caps; BOS-JC-01 effective date; CAM-SCR-01 citation; CA-ALG-01 section).\n2. Hamza decides the dated conflicts the organisers flagged (Berkeley 13.63; LA RSO formula date — both keys already agree on 2026-02-02 for LA) and the categorisation questions (notice-of-rights ordinances; Hoboken B-750 disclosure; broker-fee reform).\n3. Where neither key is primary-verified (Boston HSNA code section; Berkeley 13.106 effective day; Santa Ana ordinance numbers), verify before upgrading `verifier`.\n')
open(f'{OUT}/gold/silver_vs_independent.md','w').write('\n'.join(L))
print('matched',len(MAP),'agree',len(agrees),'diff rows',len(rows),'silver-only',only_silver,'ind-only',len(only_ind),'log rows',len(log))
