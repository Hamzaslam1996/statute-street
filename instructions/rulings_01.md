# Rulings from Hamza — after the 3-document test

1. effective_date = the date the specific extracted requirement first took effect. If a later amendment changed the key value itself, use the amendment date instead. Record last-amended info in notes (e.g. "as amended by SB 567, eff. 2024-04-01"). For D024 use 2020-01-01. (Example of the exception: CA deposit cap one month under AB 12 -> 2024-07-01.)

2. Never infer an effective date from amendment history or citations at the end of a statute. If the text does not state when the requirement took effect, return null and explain in notes.

3. Agreed: no cross-document conflict flags at extraction time. Keep capturing preemption/savings clauses in `interaction`. Add a TODO for a cross-rule conflict pass after extraction (state rule with preemption language + local rule in same category -> flag both).

4. Tighten quoted_span: it must be the operative sentence stating the duty, cap or prohibition (shall / shall not / may not / unlawful / prohibited), not a definition, penalty cross-reference or purpose clause. Verify by re-running D069.

5. Commit CLAUDE.md and this instructions/ folder now. Do not commit gold/ yet (another session is still writing it).

## Next
Run a second batch of these 11 docs and show me the same table plus the eval:
D001 D025 D026 D034 D041 D046 D048 D059 D066 D081 D083

Do not run --all yet.
