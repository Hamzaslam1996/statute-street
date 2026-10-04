# Unit counts as a PMS proxy: engine --use-derived-units on the 500 sample addresses

Before = out/lookups.json (unit counts only where the county supplied them). After = out/lookups_derived.json (New Jersey unit counts parsed from the MOD-IV building code, standing in for counts a property management system would supply). Results for CA and MA rows cannot change because their counts were already present.

| Legal city | Addresses | Rows | Unknown before | Unknown after | Presumption rows before | Presumption rows after |
|---|---|---|---|---|---|---|
| Berkeley, CA | 40 | 560 | 80 (14.3%) | 80 (14.3%) | 320 | 320 |
| Boston, MA | 60 | 600 | 60 (10.0%) | 60 (10.0%) | 0 | 0 |
| Cambridge, MA | 50 | 500 | 0 (0.0%) | 0 (0.0%) | 0 | 0 |
| Hoboken, NJ | 40 | 400 | 280 (70.0%) | 90 (22.5%) | 240 | 240 |
| Jersey City, NJ | 50 | 450 | 350 (77.8%) | 50 (11.1%) | 250 | 250 |
| Los Angeles, CA | 80 | 885 | 91 (10.3%) | 91 (10.3%) | 485 | 485 |
| Newark, NJ | 50 | 450 | 398 (88.4%) | 367 (81.6%) | 294 | 294 |
| San Diego, CA | 50 | 500 | 100 (20.0%) | 100 (20.0%) | 250 | 250 |
| San Francisco, CA | 80 | 953 | 85 (8.9%) | 85 (8.9%) | 240 | 240 |
| **All** | 500 | 5298 | 1444 (27.3%) | 923 (17.4%) | 2079 | 2079 |

Reading: a supplied unit count settles the unit-threshold tests (Jersey City rent control's 1 to 4 unit exemption, the small-building carve-outs in the state screening and deposit laws) in Hoboken and Jersey City; what remains unknown there is owner identity (never in the data) and, in Hoboken, the year built for the 1987 rent control cutoff. Newark moves least: many of its MOD-IV codes carry no unit count, only 2 of 50 rows have a year built, and owner identity decides the remaining exemptions. Presumption counts do not move: they come from use or funding exemptions (hotels, subsidised housing) that a unit count cannot settle.
