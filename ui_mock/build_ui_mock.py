"""Build UI mock data (contract-shaped) from the gold set. Run from navigator/: python3 ui_mock/build_ui_mock.py"""
import json, csv, os
here = os.path.dirname(os.path.abspath(__file__)); nav = os.path.dirname(here)
P = lambda *p: os.path.join(nav, *p)
rules = json.load(open(P('gold','rules','all.json')))
reg = {r['source_id']: r for r in csv.DictReader(open(P('sources','source_register.csv'), encoding='utf-8'))}
seed = json.load(open(P('gold','addresses','seed20.json')))
chg = json.load(open(P('gold','changes','T1-T5.json')))

def cov(c):
    if not c: return None
    parts=[]
    for k,lab in [('coo_cutoff','Certificate of occupancy on/before'),('year_built_max','Built in or before'),('min_units','Minimum units'),('max_units','Maximum units'),('owner_type','Owner type'),('tenancy_months','Tenancy months')]:
        if c.get(k) not in (None,''): parts.append(f"{lab}: {c[k]}")
    if c.get('other'): parts.append(c['other'])
    return '; '.join(parts) or None

out=[]
for r in rules:
    if r['jurisdiction'].startswith('Santa Ana'): continue  # out of challenge scope
    sid = (r.get('source_ids') or [None])[0]
    src = reg.get(sid, {})
    neg = bool(r.get('negative_finding'))
    status = r['status'] if r['status'] in ('in_force','not_yet_effective','pending','failed') else 'in_force'
    out.append({
      'team_rule_id': r['gold_id'], 'jurisdiction': r['jurisdiction'], 'level': r['level'], 'category': r['category'],
      'status': status,
      'title': (f"No {r['category'].replace('_',' ')} rule at {r['level']} level" if neg else r['title']),
      'requirement': (r.get('negative_reason') or r.get('requirement')) if neg else r.get('requirement'),
      'key_value': r.get('key_value'), 'coverage_conditions': cov(r.get('coverage')), 'exemptions': r.get('exemptions'),
      'effective_date': r.get('effective_date'), 'citation': r.get('citation'),
      'source_doc_id': (r.get('corpus_doc_ids') or r.get('supplementary_doc_ids') or [sid])[0],
      'source_url': src.get('url') or ((r.get('verified_against') or [{}])[0].get('url')),
      'quoted_span': r.get('quoted_span'), 'confidence': r.get('confidence'),
      'conflict_flag': bool(r.get('conflict_flag')), 'conflict_note': r.get('conflict_note'),
      'negative_finding': neg,
    })
json.dump({'rules': out}, open(os.path.join(here,'rules.json'),'w'), indent=1, ensure_ascii=False)

look={}; addrs=[]
for a in seed['addresses']:
    raw=a['raw']
    addrs.append({k: raw.get(k) for k in ['address_id','street_address','postal_city','state','zip','year_built','units']})
    look[a['address_id']]=[{'team_rule_id':e['gold_id'],'result':e['result'],'explanation':e['reason'],'conflict_flag':bool(e['conflict_flag'])} for e in a['expected']]
json.dump({'as_of': seed.get('as_of','2026-10-01'), 'lookups': look}, open(os.path.join(here,'lookups.json'),'w'), indent=1, ensure_ascii=False)
json.dump({'addresses': addrs}, open(os.path.join(here,'addresses.json'),'w'), indent=1, ensure_ascii=False)

ids={a['address_id'] for a in addrs}
ch={}
for t in chg['tests']:
    ch[t['test_id']]={'affected_address_ids':[x for x in t.get('expected_affected_address_ids',[]) if x in ids],
                      'conflict_flag_address_ids':[x for x in t.get('conflict_flag_address_ids',[]) if x in ids],
                      'notes': t['title'] + (' — ' + t['method_note'] if t.get('method_note') else '')}
json.dump(ch, open(os.path.join(here,'changes.json'),'w'), indent=1, ensure_ascii=False)

src=[{'source_id':s['source_id'],'jurisdiction':s['jurisdiction'],'title':s['title'],'citation':s['citation'],'url':s['url'],'publisher':s['publisher'],'retrieved_at':s['retrieved_at'],'sha256':s['sha256']} for s in reg.values()]
json.dump({'sources':src}, open(os.path.join(here,'sources.json'),'w'), indent=1, ensure_ascii=False)
print(len(out), len(addrs), len(ch), len(src))
