#!/usr/bin/env python3
"""Independent address key (seed20) – expected results computed from the gold rules' coverage logic."""
import csv, json, os
from collections import OrderedDict
ROOT='/home/claude/ss'; OUT='/mnt/user-data/outputs/navigator'
QY=2026  # query year (2026-10-01)
rows={r['address_id']:r for r in csv.DictReader(open(f'{ROOT}/sample_addresses.csv'))}
RULES={r['gold_id']:r for r in json.load(open(f'{OUT}/gold/rules/all.json'))}
PICK=['A0016','A0050','A0106','A0107','A0022','A0001','A0235','A0322','A0019','A0005',
      'A0227','A0040','A0012','A0008','A0331','A0003','A0065','A0036','A0015','A0048']
COUNTY={'Los Angeles':'Los Angeles County','San Francisco':'San Francisco County','San Diego':'San Diego County','Berkeley':'Alameda County',
        'Hoboken':'Hudson County','Jersey City':'Hudson County','Newark':'Essex County','Boston':'Suffolk County','Cambridge':'Middlesex County'}
BOSTON={'Dorchester','Roxbury','East Boston','Brighton','Allston','South Boston','Jamaica Plain','Hyde Park','Mattapan','Boston'}
def legal_city(r):
    pc=r['postal_city']
    if r['state']=='MA': return 'Cambridge' if pc=='Cambridge' else 'Boston'
    if r['state']=='CA':
        if r['source_dataset'].startswith('LA County'): return 'Los Angeles'
        if r['source_dataset'].startswith('SANDAG'): return 'San Diego'
        return pc
    return pc
PFX={'Los Angeles':'LA','San Francisco':'SF','San Diego':'SD','Berkeley':'BERK','Hoboken':'HOB','Jersey City':'JC','Newark':'NWK','Boston':'BOS','Cambridge':'CAM'}

def units_hint(r):
    """units from the units column, else a range implied by use_description (recorded as an inference)."""
    if r['units']: return int(r['units']), 'units column'
    d=r['use_description']
    if '5+' in d or '5 or more' in d or 'Five or more' in d: return 5,'use_description implies 5+ units'
    if 'APT 7-30 UNITS' in d: return 7,'use_description implies 7-30 units'
    if 'APT 4-6 UNITS' in d: return 4,'use_description implies 4-6 units'
    return None,None

def build(aid):
    r=rows[aid]; city=legal_city(r); st=r['state']; pfx=PFX[city]
    yb=int(r['year_built']) if r['year_built'] else None
    units,usrc=units_hint(r)
    exp=[]; unknown=set(); notc=[]; neg=[]; notes=[]
    def E(g,res,reason,cf=False):
        exp.append(OrderedDict(gold_id=g,result=res,reason=reason,conflict_flag=cf))
    def U(fact): unknown.add(fact)
    if r['postal_city']!=city: notes.append(f'postal_city "{r["postal_city"]}" resolved to legal city {city}')
    if usrc and usrc!='units column': notes.append(f'units inferred from use_description ("{r["use_description"]}") – inference, not a data field; results relying on it are marked')
    stack=[st,COUNTY[city],city]
    # gather rules in stack
    inscope=[g for g,x in RULES.items() if (x['level']=='state' and x['jurisdiction']==st) or (x['level']=='city' and x['jurisdiction']==f'{city}, {st}')]
    for g in inscope:
        x=RULES[g]
        if x['negative_finding']: neg.append(g); continue
        if x['status']=='failed': neg.append(g); continue
        if x['status']=='pending': E(g,'pending','bill not enacted; reported as pending for every address in the state'); continue
        if x['status']=='not_yet_effective': E(g,'not_yet_effective',f'enacted, effective {x["effective_date"]} > 2026-10-01'); continue
    # ---------------- CA
    if st=='CA':
        # local rent control status
        local_rc=None  # True/False/None(unknown)
        if city=='Los Angeles':
            if yb is None: local_rc=None; U('year_built (RSO certificate-of-occupancy cutoff 1978-10-01)')
            elif yb==1978: local_rc=None; U('certificate-of-occupancy date (year_built equals the 1978 cutoff year)')
            elif yb<1978: local_rc=True if (units is None or units>=2) else False
            else: local_rc=False
            if units is None and local_rc: U('units (RSO excludes single-family dwellings)')
        elif city=='San Francisco':
            if yb is None: local_rc=None; U('year_built (Rent Ordinance certificate-of-occupancy cutoff 1979-06-13)')
            elif yb==1979: local_rc=None; U('certificate-of-occupancy date (year_built equals the 1979 cutoff year)')
            elif yb<1979: local_rc=True
            else: local_rc=False
        elif city=='Berkeley':
            local_rc=None; U('year_built / certificate of occupancy (Berkeley full coverage requires COO on or before 1980-06-30)')
        elif city=='San Diego':
            local_rc=False
        # 15-year COO exemption for AB 1482 (cutoff 2011-10-01)
        if yb is None: new15=None; U('year_built (AB 1482 15-year certificate-of-occupancy exemption)')
        elif yb>=2012: new15=True
        elif yb==2011: new15=None; U('certificate-of-occupancy date (year_built 2011 straddles the 15-year cutoff)')
        else: new15=False
        # CA-RENT-01
        if local_rc is True: E('CA-RENT-01','superseded',f'{city} local rent control covers this unit (Civ. Code § 1947.12(d)(3)); stricter local cap governs')
        elif local_rc is None: E('CA-RENT-01','unknown','state cap applies only if the unit is outside local rent control and older than 15 years; local coverage and/or COO age cannot be determined from the data')
        else:
            if new15 is True: notc.append(OrderedDict(gold_id='CA-RENT-01',reason=f'year_built {yb}: certificate of occupancy necessarily within the previous 15 years → exempt (§ 1947.12(d)(4))'))
            elif new15 is None: E('CA-RENT-01','unknown','year_built straddles the 15-year COO cutoff')
            else: E('CA-RENT-01','applies',f'no local rent control for this unit; year_built {yb} is more than 15 years old so the COO exemption cannot apply')
        # CA-JUST-01 – every CA sample city has a local just-cause ordinance
        if city in ('Los Angeles','San Francisco','Berkeley'):
            E('CA-JUST-01','superseded',f'{city} just-cause ordinance governs instead (Civ. Code § 1946.2(i))')
        elif city=='San Diego':
            E('CA-JUST-01','superseded','San Diego TPO (more protective, adopted 2023) governs where either applies; both share the 15-year COO exemption, which cannot be tested without year_built')
        # CA-DEP-01
        if units is not None and units>4: E('CA-DEP-01','applies',f'{units} units{" ("+usrc+")" if usrc!="units column" else ""} > 4 defeats the small-landlord two-month exception; one-month cap applies')
        else: E('CA-DEP-01','unknown','owner type and portfolio size (small-landlord two-month exception) not in the data'); U('owner type / portfolio size (Civ. Code § 1950.5(c)(5))')
        E('CA-FEE-01','applies','statewide; no coverage condition')
        E('CA-SCRN-01','applies','statewide; no coverage condition')
        E('CA-ALG-01','applies','statewide; effective 2026-01-01 (T1)')
        if city=='Los Angeles':
            if local_rc is True:
                E('LA-RENT-01','applies',f'year_built {yb} < 1978 and ≥2 units → RSO unit (COO on or before 1978-10-01 inferred from year_built)')
                E('LA-JUST-02','applies','RSO unit → RSO eviction grounds and relocation rules')
                E('LA-DEP-01','applies','RSO unit → deposit interest duty')
                notc.append(OrderedDict(gold_id='LA-JUST-01',reason='RSO unit; JCO covers only non-RSO units'))
            elif local_rc is None:
                for g in ('LA-RENT-01','LA-JUST-02','LA-DEP-01'): E(g,'unknown','RSO coverage depends on the certificate-of-occupancy date, which cannot be fixed from year_built')
                E('LA-JUST-01','unknown','JCO covers non-RSO units; RSO status unknown')
            else:
                for g in ('LA-RENT-01','LA-JUST-02','LA-DEP-01'): notc.append(OrderedDict(gold_id=g,reason=f'year_built {yb} after 1978 → not an RSO unit'))
                E('LA-JUST-01','applies',f'non-RSO residential unit (year_built {yb}); tenancy length (6 months) not in data but the rule attaches to the unit')
            E('LA-SCRN-01','applies','citywide; no coverage condition')
        if city=='San Francisco':
            if local_rc is True: E('SF-RENT-01','applies',f'year_built {yb} before 1979 → COO on or before 1979-06-13 inferred')
            elif local_rc is None: E('SF-RENT-01','unknown','COO cutoff 1979-06-13 cannot be tested')
            else: notc.append(OrderedDict(gold_id='SF-RENT-01',reason=f'year_built {yb} after 1979 → exempt from rent limits (just cause still applies)'))
            E('SF-JUST-01','applies','just cause covers Rent Ordinance units including post-1979 construction')
            E('SF-DEP-01','applies','citywide deposit-interest duty')
            E('SF-SCRN-01','unknown','Fair Chance housing provisions cover affordable housing only; affordability status not in the data'); U('affordable-housing status (SF Fair Chance Ordinance coverage)')
            E('SF-ALG-01','applies','citywide; effective 2024-10-14')
        if city=='San Diego':
            E('SD-JUST-01','unknown','TPO exempts housing with a COO within the previous 15 years; San Diego rows have no year_built');
            E('SD-SCRN-01','applies','citywide; no coverage condition')
            E('SD-ALG-01','applies','citywide; effective 2025-06-21')
        if city=='Berkeley':
            E('BERK-RENT-01','unknown','rent ceiling applies only to fully covered units (COO on or before 1980-06-30); Berkeley rows have no year_built')
            E('BERK-JUST-01','applies' if units else 'unknown','just cause covers fully and partially covered units; multifamily (5+ units per use code) cannot fall in the exempt categories' if units else 'exempt categories (owner-shared, ADU) cannot be excluded')
            E('BERK-DEP-01','applies' if units else 'unknown','deposit interest covers fully and partially covered units' if units else 'coverage status unknown')
            E('BERK-FEE-01','applies','applies to all residential rental agreements in Berkeley',cf=True)
            if units is not None and units>=4: E('BERK-SCRN-01','applies','owner-occupied 1–3 unit exemption impossible for a 5+ unit building (use code)')
            else: E('BERK-SCRN-01','unknown','owner-occupied 1–3 unit exemption cannot be excluded'); U('owner occupancy / units (BMC 13.106 exemption)')
            E('BERK-ALG-01','applies','citywide; effective 2026-01-01 (date conflict flagged on the rule)',cf=True)
    # ---------------- NJ
    if st=='NJ':
        if units is not None and units>=3:
            E('NJ-JUST-01','applies',f'{units} units > 2 defeats the owner-occupied two-unit exemption')
            E('NJ-DEP-01','applies',f'{units} units > 2 defeats the owner-occupied two-unit exclusion (N.J.S.A. 46:8-26)')
            E('NJ-FEE-01','applies',f'{units} units → not a one- or two-family dwelling')
        else:
            E('NJ-JUST-01','unknown','owner-occupied ≤2-unit exemption cannot be excluded (units and owner occupancy not in data)'); U('units / owner occupancy (Anti-Eviction Act owner-occupied two-unit exemption)')
            E('NJ-DEP-01','unknown','owner-occupied ≤2-unit exclusion cannot be excluded'); U('units / owner occupancy (N.J.S.A. 46:8-26)')
            E('NJ-FEE-01','unknown','one- or two-family dwelling exemption cannot be excluded'); U('units (one-/two-family dwelling exemption, N.J.S.A. 46:8-18.1(c))')
        if units is not None and units>4: E('NJ-SCRN-01','applies',f'{units} units > 4 defeats any small owner-occupied exemption')
        else: E('NJ-SCRN-01','unknown','small owner-occupied building exemption cannot be excluded'); U('units / owner occupancy (Fair Chance in Housing Act exemptions)')
        if units is not None and units>=3: E('NJ-SCRN-02','applies','LAD owner-occupied two-family exemption impossible')
        else: E('NJ-SCRN-02','unknown','LAD owner-occupied small-building exemption cannot be excluded'); U('units / owner occupancy (LAD exemptions)')
        # NJ-ALG-01 already not_yet_effective; add conflict flag for JC/Hoboken
        for e in exp:
            if e['gold_id']=='NJ-ALG-01' and city in ('Jersey City','Hoboken'):
                e['conflict_flag']=True; e['reason']+='; possible preemption of the local ordinance (T3 conflict flag)'
        if city=='Jersey City':
            E('JC-RENT-01','unknown','1–4 unit properties are exempt; Jersey City rows have no unit counts'); U('units (Jersey City 1–4 unit exemption)')
            E('JC-ALG-01','applies','citywide; conflict flag for possible FAIR Act preemption from 2027-07-01',cf=True)
        if city=='Hoboken':
            # rulings_05 §4a (Hamza): § 155-2 has NO unit-count test. Built ≤ 1987-06-25 → covered; built after and completion
            # < 30 years before the query date (2026-10-01) → unknown (N.J.S.A. 2A:42-84.1 exemption depends on mortgage term and
            # compliance filings not in the data); built after and ≥ 30 years ago → covered; year missing → unknown.
            # Year granularity: ≤1995 is certainly ≥30 years before 2026-10-01; 1996 could be either side → unknown.
            if yb is None: E('HOB-RENT-01','unknown','ordinance covers all dwelling units with no unit-count test, but the post-1987-06-25 new-construction exemption (§ 155-2(H)) cannot be tested without year_built'); U('year_built (Hoboken § 155-2(H) new-construction exemption)')
            elif yb<=1987: E('HOB-RENT-01','applies',f'year_built {yb} → built on/before 1987-06-25 (or, if later in 1987, completion ≥ 30 years before 2026-10-01) → § 155-2(H) exemption cannot apply; no unit-count or owner-occupancy exemption in § 155-2')
            elif yb<=1995: E('HOB-RENT-01','applies',f'year_built {yb} → post-1987-06-25 construction but completion ≥ 30 years before 2026-10-01 → § 155-2(H) exemption (lesser of mortgage term or 30 years) has expired; no unit-count test')
            else: E('HOB-RENT-01','unknown',f'year_built {yb} → post-1987-06-25 multiple dwelling less than 30 years old at 2026-10-01 → § 155-2(H) exemption depends on the initial-mortgage amortisation period and N.J.S.A. 2A:42-84.1 compliance filings, not in the data'); U('§ 155-2(H) new-construction exemption: mortgage amortisation period / statutory compliance')
            E('HOB-ALG-01','applies','citywide; conflict flag for possible FAIR Act preemption from 2027-07-01',cf=True)
            E('HOB-RENT-02','applies','disclosure duty for renewal increases >10% applies to all residential landlords in Hoboken (categorisation flagged)',cf=True)
        if city=='Newark':
            if yb is None: E('NWK-RENT-01','unknown','new-construction exemption (30 years / mortgage amortisation) cannot be tested without year_built'); U('year_built (Newark new-construction exemption)')
            elif yb<1990: E('NWK-RENT-01','applies',f'year_built {yb} → outside any 30-year new-construction exemption; multiple dwelling with no small-building exemption')
            else: E('NWK-RENT-01','unknown',f'year_built {yb} may fall within the new-construction exemption period'); U('new-construction exemption period')
            if units is not None and units>=3: E('NWK-SCRN-01','applies','owner-occupied two-family exemption impossible')
            else: E('NWK-SCRN-01','unknown','owner-occupied two-family exemption cannot be excluded'); U('units / owner occupancy (Newark § 2:31-1 exemptions)')
    # ---------------- MA
    if st=='MA':
        E('MA-DEP-01','applies','statewide; no coverage condition')
        E('MA-FEE-01','applies','statewide; no coverage condition')
        # Adjudicated after comparison (Hamza, 2026-10-04): MA-SCRN-01 is c.151B § 4(10), which has no owner-occupied two-family
        # exemption (that proviso is in § 4(7) and § 4(11)(3) only, official text D049) → applies to every MA rental regardless of units.
        E('MA-SCRN-01','applies','c.151B § 4(10) (public assistance / housing subsidy) has no owner-occupied two-family exemption; applies to all rental accommodations')
        E('MA-FEE-02','applies','statewide; attaches to any brokered rental')
        E('MA-SCRN-02','applies','statewide regulation of CORI use by housing providers (text not captured; low confidence)')
        if city=='Boston':
            E('BOS-JUST-01','applies','applies to all Boston landlords ending a tenancy (notice-only; categorisation flagged)',cf=True)
            E('BOS-SCRN-01','applies','Boston Fair Housing Commission protections apply to all Boston rentals')
            E('BOS-SCRN-02','unknown','Fair Chance policy applies only to DND-funded / IDP housing providers; funding status not in data',cf=True); U('DND funding / Inclusionary Development Policy status (Boston Fair Chance policy coverage)')
        if city=='Cambridge':
            E('CAM-JUST-01','applies','applies to all residential rental agreements in Cambridge (notice-only; categorisation flagged)',cf=True)
            E('CAM-SCRN-01','applies','citywide; no coverage condition')
    # order expected by gold_id
    exp.sort(key=lambda e:e['gold_id'])
    return OrderedDict(address_id=aid, raw=OrderedDict((k,r[k]) for k in r), jurisdiction_stack=stack,
                       legal_city=city, units_used=units, units_source=usrc, expected=exp,
                       not_covered=notc, negative_or_failed_in_stack=sorted(neg),
                       unknown_facts=sorted(unknown), notes='; '.join(notes) if notes else None)

PICK40=['A0257','A0030','A0105','A0283',            # SF: no year; 1908 flat&store 5u; 2019 (15-yr COO); 1986 51u
        'A0445','A0267','A0037',                      # LA: 1977 (year before cutoff); no year/no units; 2001 47u
        'A0114','A0219','A0273','A0275','A0346',      # SD: 5 fillers = random.Random(20261004).sample(remaining SD ids sorted, 5); all no year
        'A0018','A0430','A0103','A0193','A0263',      # Berkeley: use-code edge cases 7200 and 7800, then 3 fillers = random.Random(20261004).sample(remaining, 3)
        'A0002','A0168','A0489','A0049',              # Hoboken: 2001/2007/2000 (post-1987 new-construction exemption); no year 'AFFORDABL'
        'A0026','A0042','A0017','A0032',              # Jersey City: 1901/1912 (pre-exemption); two no year
        'A0352','A0011','A0013','A0020',              # Newark: 1900; three no year
        'A0052','A0093','A0123','A0083','A0144',      # Boston: Allston 1965; Jamaica Plain 2004 A/118; East Boston 2013 A/125; Roxbury 1890 A/125; Roxbury 1910 A/112
        'A0009','A0034','A0039','A0046','A0043','A0064']  # Cambridge: 1915/1886/1920 6u; 1910 32u; 1975 44u; 1890 84u
assert len(PICK40)==40 and not set(PICK)&set(PICK40)
import sys, random
MODE=sys.argv[1] if len(sys.argv)>1 else 'seed20'
# ---- holdout20: mechanical, seeded selection (no hand-picking) from rows NOT in seed20/seed60.
# Quota: 2 per legal city (18) + 1 extra each to the two cities with the most remaining rows (ties broken by city name).
# Per city (fixed order): 1 edge case drawn from that city's edge-case pool (if any), the rest drawn from all remaining rows of the city.
# Edge-case pool (same traps as seed60): year_built missing; CA year_built ≥ 2011 (AB 1482 15-year COO rolling exemption);
# LA 1977–1979, SF 1978–1980, Berkeley 1979–1980 (cutoff neighbours); NJ year_built > 1987 (new-construction exemptions);
# Boston postal_city ≠ 'Boston' (neighbourhood names). RNG: random.Random(20261005) over sorted ids.
def holdout_picks():
    used=set(PICK)|set(PICK40); rng=random.Random(20261005)
    order=['San Francisco','Los Angeles','San Diego','Berkeley','Hoboken','Jersey City','Newark','Boston','Cambridge']
    rem={c:sorted(a for a,r in rows.items() if a not in used and legal_city(r)==c) for c in order}
    quota={c:2 for c in order}
    for c in sorted(order,key=lambda c:(-len(rem[c]),c))[:2]: quota[c]+=1
    def edge(r,c):
        yb=int(r['year_built']) if r['year_built'] else None
        if yb is None: return True
        if r['state']=='CA' and yb>=2011: return True
        if c=='Los Angeles' and 1977<=yb<=1979: return True
        if c=='San Francisco' and 1978<=yb<=1980: return True
        if c=='Berkeley' and 1979<=yb<=1980: return True
        if r['state']=='NJ' and yb>1987: return True
        if c=='Boston' and r['postal_city']!='Boston': return True
        return False
    out=[]
    for c in order:
        pool=[a for a in rem[c] if edge(rows[a],c)]; got=[]
        if pool: got.append(rng.choice(pool))
        rest=[a for a in rem[c] if a not in got]; got+=rng.sample(rest,quota[c]-len(got))
        out+=got
    assert len(out)==20 and not set(out)&used and len(set(out))==20
    return out
PICKS=PICK if MODE=='seed20' else (holdout_picks() if MODE=='holdout20' else PICK+PICK40)
recs=[build(a) for a in PICKS]
import jsonschema
schema=json.load(open(f'{OUT}/gold/schema/gold_address.schema.json'))
schema['properties']['expected']['items']['properties']['result']['enum']=['applies','unknown','superseded','not_yet_effective','pending']
for x in recs: jsonschema.validate(x,schema)
out=OrderedDict(as_of='2026-10-01',verifier='AI-draft',method='Expected results derived from gold/rules/all.json coverage logic; see gold/README.md. Rules that do not cover the address are listed in not_covered (the submission format omits them). Negative findings and failed measures are listed for completeness and are never reported as applying.',
                selection_method=('seed20: hand-picked to exercise the README traps (see README). seed60 = seed20 + 40 rows chosen so every legal city has ≥5 (SF 7, LA 7, SD 7, Berkeley 6, Hoboken 6, Jersey City 6, Newark 6, Boston 8, Cambridge 7): per city, first every available edge case (cutoff-year neighbours 1977/1986, rows missing year_built or units, postal_city ≠ legal city, post-1987 NJ new construction, 2019/2013 recent construction), then fillers drawn with random.Random(20261004) from the remaining rows of that city. Expected results computed by the same coverage logic as seed20 (build_addresses.py).' if MODE=='seed60' else ('holdout20: 20 rows from sample_addresses.csv not in seed20/seed60, selected mechanically by build_addresses.py holdout_picks() — quota 2 per legal city + 1 extra to each of the two cities with most remaining rows; per city one edge case (missing year_built, CA ≥2011, cutoff-year neighbours, NJ post-1987, Boston neighbourhood postal_city) drawn first, then fillers; random.Random(20261005) over sorted ids. Not hand-picked; frozen by holdout20.sha256 before any engine scoring.' if MODE=='holdout20' else 'hand-picked to exercise the README traps')),
                sample_gaps=['No San Francisco row has year_built 1979 (two SF rows lack year_built and are used instead for the cutoff trap).','No Los Angeles row has a postal_city other than "Los Angeles" (Van Nuys etc. absent); the postal_city trap is exercised with Boston neighbourhoods and San Ysidro.'],
                addresses=recs)
json.dump(out,open(f'{OUT}/gold/addresses/{MODE}.json','w'),indent=1,ensure_ascii=False)
print(len(recs),'addresses;',sum(len(x['expected']) for x in recs),'expected entries;',sum(1 for x in recs for e in x['expected'] if e['result']=='unknown'),'unknowns')
for x in recs: print(x['address_id'],x['legal_city'],x['raw']['year_built'] or '-',x['units_used'],[ (e['gold_id'],e['result'][:4]) for e in x['expected']][:6],'...')