## 3. Submission format check

- rules.json: 65 records, schema errors: 0
- rules.json: duplicate team_rule_ids: 0
- lookups.json: as_of='2026-10-01'; addresses 500 (sample 500; missing 0, extra 0); invalid result values 0; rows citing unknown rules 0
- changes.json: tests ['T1', 'T2', 'T3', 'T4', 'T5']; required keys present: True; address ids not in sample: 0
- template rules.json keys missing from ours: none; extra keys in ours (allowed, schema has no additionalProperties): ['adoption_date', 'date_source_doc_id', 'evidence_basis', 'negative_finding', 'notes', 'record_role', 'requirement_es', 'retrieved_at', 'supporting_doc_ids']
- template lookups.json: top-level keys ['as_of', 'lookups'] vs ours ['as_of', 'lookups']; row keys missing: none; extra row keys: ['assumptions']
- template changes.json entry keys ['affected_address_ids', 'notes'] vs ours ['affected_address_ids', 'conflict_flag_address_ids', 'notes']

**Format check: PASS**
