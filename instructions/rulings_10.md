# Rulings 10 — citation metric counts only the supplied corpus (Hamza, 4 Oct)

Organiser ruling (Harish, Discord, 4 Oct 03:20 PKT): self-saved link-only texts may be used for research but DO NOT count toward the citation metric; the metric is based on supplied, verifiable corpus text (the starter pack's corpus/text/D###.txt). No hour-16 release; T1–T5 only. score.py and the dev key will never be shared; videos show our own output and validation.

No API calls. Apply after rulings_08 and rulings_09.

1. **Primary evidence = supplied corpus whenever possible.** For every kept rule in rules.json:
   - If any starter-pack corpus/text document supports it (the rule itself or a folded duplicate was extracted from it, or its quote is an exact substring of a corpus text), make that the primary evidence: source_url = that doc's manifest URL, citation as in that doc, quoted_span = the verified span from that corpus text.
   - Supplementary / manual texts (corpus_supplementary/, sources/manual/, D088–D095) become supporting documents only in rules_full.json and the audit trail.
   - Check the rulings_07 folds in particular (JC r-0027 vs r-0028, Hoboken r-0023, Santa Ana r-0066): if the folded-away record was the corpus-backed one, swap which evidence is primary — keep the merged rule, but cite the corpus doc.
2. **Rules with no supplied-corpus text** (link-only or our own captures only): keep them (the law is real and verified), with source_url = the official manifest URL where one exists. Add an audit-log field `evidence_basis: "supplied_corpus" | "link_only_capture" | "manual_primary"` in rules_full.json (not in rules.json if the schema forbids extra fields — check `additionalProperties`).
3. Report a table: rules by evidence_basis; how many primaries switched to corpus; any rule whose only verified quote is non-corpus.
4. README: one paragraph "Evidence basis" quoting the organiser ruling, and the counts.
5. Re-run Module A eval (39/39 expected), rebuild lookups/changes (results should not change — evidence only), commit by name, push, stop.
