# Rulings 09 — owner-type exceptions follow organisers' README §4 (Hamza, 4 Oct)

No API calls. Organisers' README §4: owner names are excluded, so owner-type exceptions must be answered "unknown" unless we can explain why the exception cannot apply.

1. Split the niche_exemption class:
   - **owner_type** (identity or status of the owner: nonprofit / resident-controlled cooperative, government-owned units, natural-person owner, small-landlord exceptions, owner-occupancy): data silent → `unknown`, explanation names the missing fact. If the use code makes the exception impossible (e.g. owner-occupied 1–4 unit exception vs a 5+ unit building) → `applies` with that reason.
   - **use_or_funding** (vacation/transient lets, hotels, dormitories, hospitals, care facilities, public housing / government-contract units, deed-restricted or subsidised housing, software used under affordable programmes): unchanged — `applies` + "Applies unless …" assumption. (Pending an organiser answer in Discord on the funding cases; keep a flag `--strict-unknown` that turns these to `unknown` too, so we can switch in one run.)
2. Rebuild lookups and changes. Report: how many rows moved applies → unknown, new whole-sample unknown rate, presumption count, and seed60/seed20/holdout20 agreement (expect drops where our keys used the old presumption — list them; do NOT change gold files, the gold session will re-adjudicate).
3. README "Exemptions and presumptions": add the owner_type rule with the README §4 citation.
4. Commit by name, push, stop.
