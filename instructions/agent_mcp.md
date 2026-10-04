# Agent guardrail: Statute Street as an MCP server (Hamza, 4 Oct)

Goal: any AI agent (a leasing or operations agent, Claude, a pricing engine's assistant) can ask Statute Street before acting. The agent never decides the law; our deterministic engine does, and the agent quotes it.
No API calls in the server. Python, stdio transport, official `mcp` Python SDK (pip install mcp into the venv; add to requirements.txt). Run after rulings_12 and integration.md.

## Tools (read-only, deterministic, all answers carry as_of, citation, quoted_span, source_url)
1. `find_address(query)` → up to 5 matches from data/sample_addresses + out/jurisdictions.json (address_id, street, legal city, state).
2. `get_determinations(address_id, as_of="2026-10-01", category=None)` → rows from the engine (re-run engine.py logic in-process for any as_of, or read out/lookups.json for the default date), each with result, explanation, assumptions, conflict_flag, key_value_short, citation, quoted_span, source_url, retrieved_at.
3. `check_action(address_id, action, as_of)` with action in {raise_rent, use_pricing_software, screen_applicant, charge_fee, take_deposit, end_tenancy} → verdict in {restricted, permitted_now_restricted_from:<date>, unknown_needs:<fact>, no_rule_found, needs_human_review} plus the binding rows. Same mapping as the UI Action check.
4. `upcoming_changes(address_id=None, after=as_of)` → change register rows (T1 to T5 and any not_yet_effective rules) affecting the address.
5. `reliance_record(address_id, action, as_of)` → markdown text of a reliance record (Relied on / Not applicable on this date / Unresolved), with engine commit and rules version.

## Server rules
- Every tool response ends with: "Legal information, not legal advice. Determinations are computed by the Statute Street engine; quote them, do not reinterpret them."
- Server instructions (MCP `instructions` field) tell the agent: call check_action before any rent, fee, screening or termination step; never state a rule without its citation; if verdict is unknown or needs_human_review, stop and ask a human.
- No network, no model calls, no writes.

## Deliverables
- `mcp_server.py`, `tests/test_mcp_tools.py` (each tool on A0016, A0002 at 2026-10-01 and 2027-07-02, A0010; assert verdicts: A0002 use_pricing_software 2026-10-01 → restricted by Hoboken ch. 158 with needs_human_review; A0010 raise_rent → no rent cap rule, pending bills listed).
- README section "Agent guardrail (MCP)": what it is, the five tools, the config snippet to add it to an MCP client (command: <venv python> mcp_server.py), and an example transcript of a question answered through the tools.
- `docs/agent_demo.md`: a 3-question script for the video: (1) "Can I raise rent 6% at 3515 Fillmore St, San Francisco?" (2) "Can we run our pricing software at 1031 Clinton St, Hoboken, and does that change next year?" (3) "Is there a rent cap at 134 Oxford St, Cambridge?"
- Register it for local use with Claude Code (`claude mcp add statute-street -- <venv python> <abs path>/mcp_server.py`) and run the 3 questions once yourself to confirm; paste the answers into docs/agent_demo.md.
Commit by name, push, report.
