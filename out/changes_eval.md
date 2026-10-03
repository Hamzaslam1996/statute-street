# Module C evaluation vs gold/changes/T1-T5.json

verifier: AI-draft; as_of default 2026-10-01

| Test | Expected affected | Ours | Missing | Extra | Exact | Expected conflicts | Ours | Exact |
|---|---|---|---|---|---|---|---|---|
| T1 | 250 | 250 | 0 | 0 | yes | 0 | 0 | yes |
| T2 | 90 | 90 | 0 | 0 | yes | 90 | 90 | yes |
| T3 | 140 | 140 | 0 | 0 | yes | 90 | 90 | yes |
| T4 | 110 | 110 | 0 | 0 | yes | 0 | 0 | yes |
| T5 | 0 | 0 | 0 | 0 | yes | 0 | 0 | yes |

## Mismatching addresses and status checks

OK | T1 status on 2025-12-31 | expected not_yet_effective | ours {'not_yet_effective': 250} |
OK | T1 status on 2026-01-02 | expected applies | ours {'applies': 250} |
OK | T3 status on 2026-10-01 | expected not_yet_effective | ours {'not_yet_effective': 140} |
OK | T3 status on 2027-07-02 | expected applies | ours {'applies': 140} |
OK | T4 status on 2026-10-01 | expected pending | ours {'pending': 220} |
OK | T5 status on 2026-10-01 | expected failed | ours not reported (failed measures are never listed) |
