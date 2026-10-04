# Agent guardrail demo: three questions through the MCP tools

Server: `mcp_server.py` (stdio, no network, no model calls, no writes). Registered locally with
`claude mcp add statute-street -- <repo>/.venv/bin/python <repo>/mcp_server.py`.
The answers below were produced on 4 Oct 2026 by calling the tools over stdio with the official MCP client
(engine commit f132902, rules version 1.0). Every tool answer ends with the standing notice:
"Legal information, not legal advice. Determinations are computed by the Statute Street engine; quote them, do not reinterpret them."

## Question 1: "Can I raise rent 6% at 3515 Fillmore St, San Francisco?"

Agent calls: `find_address("3515 Fillmore St San Francisco")` then `check_action("A0016", "raise_rent", "2026-10-01")`.

find_address: one match, A0016, 3515 FILLMORE ST, legal city San Francisco, CA, built 1926, 21 units, "Apartment 15 Units or more".

check_action:
- verdict: **restricted**; needs_human_review: false
- binding_rules: r-0059 San Francisco annual allowable rent increase (3/1/2026 to 2/28/2027) (S.F. Admin. Code ch. 37 (Rent Ordinance), § 37.3)
- row r-0059: result applies; explanation "Applies: built 1926, before the 13 Jun 1979 certificate of occupancy cutoff."; key_value_short "Cap: 1.6% per year (1 Mar 2026 to 28 Feb 2027)"; quoted_span "For rent-controlled units, the annual allowable increase amount effective March 1, 2026 through February 28, 2027 is 1.6%."; source https://www.sf.gov/news--annual-rent-increase-3126-22827-announced (retrieved 2026-10-01)
- row r-0016 (Cal. Civ. Code § 1947.12, statewide cap): result superseded, governed_by r-0059; "Governed instead by San Francisco annual allowable rent increase (3/1/2026 to 2/28/2027); the stricter local rule applies here."

What the agent should say: a 6% increase is above the 1.6% annual allowable increase for this rent-controlled building (S.F. Admin. Code § 37.3, quoted); the state cap is superseded here by the stricter local rule. Then it quotes the rule; it does not compute the lawful amount or decide the case.

## Question 2: "Can we run our pricing software at 1031 Clinton St, Hoboken, and does that change next year?"

Agent calls: `find_address("1031 Clinton St Hoboken")`, `check_action("A0002", "use_pricing_software", "2026-10-01")`, `check_action("A0002", "use_pricing_software", "2027-07-02")`, `upcoming_changes("A0002", "2026-10-01")`.

find_address: A0002, 1031-1035 CLINTON ST, legal city Hoboken, NJ, built 2001, units not in data (MOD-IV code 6B-20U-G).

check_action on 2026-10-01:
- verdict: **restricted**; needs_human_review: **true**
- binding_rules: r-0023 Algorithmic rent fixing in rental housing market prohibited (Hoboken Code § 158-2 (Ord. No. B-781))
- future_rules: r-0044 Forbidding the Algorithmic Inflation of Rent (FAIR) Act from 2027-07-01
- row r-0023 explanation: "Applies unless the property is a medical, long-term care or detention facility. Possible preemption: from 1 July 2027 the NJ FAIR Act may preempt the Hoboken and Jersey City algorithmic rent ordinances. Flagged for human review; not decided here."
- row r-0044: result not_yet_effective; "Not yet in force: takes effect 1 Jul 2027." plus the same preemption note.

check_action on 2027-07-02:
- verdict: **restricted**; needs_human_review: true
- binding_rules: r-0023 (Hoboken Code § 158-2) and r-0044 FAIR Act (P.L. 2026, c.43 (C.56:9-20 to 56:9-26))

upcoming_changes for A0002 after 2026-10-01: change register rows T2 (Hoboken and Jersey City algorithm bans, in force) and T3 (New Jersey FAIR Act, enacted 2026-07-20, effective 2027-07-01, not yet in force); rules_not_yet_in_force: r-0044 FAIR Act, effective 2027-07-01.

What the agent should say: restricted today by the Hoboken ordinance (quoted); from 1 July 2027 the state FAIR Act also applies, and whether it preempts the Hoboken ordinance is an open question flagged for human review, so the agent stops and asks a human before relying on either answer.

## Question 3: "Is there a rent cap at 134 Oxford St, Cambridge?"

Agent calls: `find_address("134 Oxford St Cambridge")`, `check_action("A0010", "raise_rent", "2026-10-01")`, `reliance_record("A0010", "raise_rent", "2026-10-01")`.

find_address: A0010, 134 Oxford St, legal city Cambridge, MA, built 1915, 6 units, "4-8-UNIT-APT".

check_action:
- verdict: **no_rule_found**; needs_human_review: false; binding_rules: none
- no_restriction_rules: r-0038 No rent cap: state law bars local rent control (M.G.L. c. 40P, § 4; MA); r-0039 No rent cap: state law bars rent control (M.G.L. c. 40P, §§ 2-3; MA); n-0027 No city rule; state law applies (M.G.L. c. 40P, § 4; Cambridge, MA)
- pending_or_failed_measures: failed: r-0037 Initiative Petition 25-21 (statewide rent increase limit) barred from ballot (Cella v. Attorney General, SJC-13893 (2026)); failed: r-0040 2026 statewide rent control ballot question (struck by SJC)

reliance_record (markdown, abridged):

```
# Reliance record: raise rent at 134 Oxford St, Cambridge, MA
Address id A0010. As of 2026-10-01. Verdict: no_rule_found.

## Relied on
- None.
## Not applicable on this date
- None.
## Unresolved
- None.
## Checked and found no restriction
- r-0038 No rent cap: state law bars local rent control (M.G.L. c. 40P, § 4; MA)
- r-0039 No rent cap: state law bars rent control (M.G.L. c. 40P, §§ 2-3; MA)
- n-0027 No city rule; state law applies (M.G.L. c. 40P, § 4; Cambridge, MA)
- failed: r-0037 Initiative Petition 25-21 (statewide rent increase limit) barred from ballot (...)
- failed: r-0040 2026 statewide rent control ballot question (struck by SJC) (...)

Statute Street rules version 1.0, engine commit f132902. Legal information, not legal advice. Determinations are
computed by the Statute Street engine; quote them, do not reinterpret them.
```

What the agent should say: no rent cap applies at this address on 1 October 2026; Massachusetts law (M.G.L. c. 40P) bars local rent control and the 2026 statewide ballot question was struck from the ballot. The reliance record is kept with the lease.

## Script notes for the video

1. Ask the question in plain words; show the agent calling `find_address` then `check_action`.
2. Read the verdict line and one quoted span aloud; point at the citation and retrieval date.
3. For Hoboken, show the second date and the "needs human review" stop.
4. For Cambridge, show the reliance record: what was checked and found absent, with the engine commit.
